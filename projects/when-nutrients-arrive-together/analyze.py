"""Make compact, inspectable tables from every planned clean-study receipt."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from convergence import METRICS, TARGETS, summarize
from reference import interval


def analyze(directory, output):
    config = json.loads((directory/'protocol.json').read_text())
    records = [json.loads((directory/f'seed-{seed}.json').read_text())
               for seed in config['seeds']]
    if [r['seed'] for r in records] != config['seeds']:
        raise ValueError('receipt identities do not match the planned seeds')
    good = [r for r in records if r['status'] == 'success']
    for r in good:
        for mesh in config['meshes']:
            for segment in config['segments']:
                for metric in METRICS:
                    for target in TARGETS:
                        value = r['scores'][str(mesh)][str(segment)][metric][target]
                        if not np.isfinite(value) or not (-1 if target == TARGETS[0] else 0) <= value <= 1:
                            raise ValueError('invalid score in receipt')
    result = summarize(records, config)
    result['protocol_sha256'] = hashlib.sha256((directory/'protocol.json').read_bytes()).hexdigest()
    result['receipt_sha256'] = {str(seed): hashlib.sha256((directory/f'seed-{seed}.json').read_bytes()).hexdigest()
                                for seed in config['seeds']}
    result['paired_coherence_advantage'] = {
        other: {k: interval([r['scores']['0.0625']['30']['coherence'][k]
                            - r['scores']['0.0625']['30'][other][k] for r in good])
                for k in TARGETS}
        for other in METRICS if other != 'coherence'} if good else {}
    result['maximum_absolute_deltas'] = {
        field: {m: {k: max(abs(r[field][m][k]) for r in good) for k in TARGETS} for m in METRICS}
        for field in ('coarse_forcing_delta', 'finest_forcing_delta', 'solver_delta', 'length_delta')
    } if good else {}
    result['maximum_segment_sensitivity'] = {
        m: {k: max(abs(r['scores']['0.0625'][str(segment)][m][k]
                       -r['scores']['0.0625']['30'][m][k])
                   for r in good for segment in (16, 60)) for k in TARGETS}
        for m in METRICS} if good else {}
    output.mkdir(parents=True, exist_ok=True)
    (output/'study-summary.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    fields = ['seed', 'metric']
    for prefix in ('score', 'forcing', 'length', 'solver'):
        fields.extend(f'{prefix}_{k}' for k in TARGETS)
    rows = []
    for r in good:
        for m in METRICS:
            row = dict(seed=r['seed'], metric=m)
            for prefix, values in [('score', r['scores']['0.0625']['30']),
                                   ('forcing', r['finest_forcing_delta']),
                                   ('length', r['length_delta']), ('solver', r['solver_delta'])]:
                row.update({f'{prefix}_{k}': values[m][k] for k in TARGETS})
            rows.append(row)
    with (output/'community-scores.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    print('planned', len(records), 'success', len(good), 'gates', result['gates'])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    analyze(args.directory, args.output)
