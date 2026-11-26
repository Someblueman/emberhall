"""Hash-bound replay and compact export of the selected full-tail solver control."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
import scipy

from reference import community, score
from tail_solver import baseline, digest, write


def export(old, study, output):
    previous = baseline(old)
    config = json.loads((study/'protocol.json').read_text())
    receipt = json.loads((study/'receipt.json').read_text())
    if (receipt['protocol_sha256'] != digest(study/'protocol.json') or
        config['baseline_receipt_sha256'] != digest(old/'receipt.json') or
        config['baseline_protocol_sha256'] != digest(old/'protocol.json')):
        raise ValueError('changed protocol or baseline identity')
    if config['numpy'] != np.__version__ or config['scipy'] != scipy.__version__:
        raise ValueError('replay library versions changed')
    for name, expected in config['sources'].items():
        if digest(Path(__file__).with_name(name)) != expected:
            raise ValueError('changed numerical source: '+name)
    output.mkdir(parents=True, exist_ok=True)
    write(output/'tail-solver-protocol.json', config)
    summary = dict(status=receipt['status'], protocol_sha256=digest(study/'protocol.json'),
                   receipt_sha256=digest(study/'receipt.json'),
                   exporter_sha256=digest(Path(__file__)), scope=config['scope'])
    if receipt['status'] == 'failure':
        summary['error'] = receipt['error']
    else:
        if digest(study/'trajectory.npz') != receipt['trajectory_sha256']:
            raise ValueError('changed refined trajectory')
        with np.load(study/'trajectory.npz', allow_pickle=False) as arrays:
            x = arrays['log_abundance']
        if x.shape != previous.shape or not np.isfinite(x).all():
            raise ValueError('invalid refined trajectory')
        _, gain, labels = community(config['community'])
        rows, maximum_delta = [], 0.
        for n in config['lengths']:
            before, after = score(previous[:n], gain, labels), score(x[:n], gain, labels)
            recorded = receipt['windows'][str(n)]
            for metric in before:
                row = dict(observations=n, metric=metric)
                for target in before[metric]:
                    a, b = before[metric][target], after[metric][target]
                    delta = abs(b-a)
                    for key, value in [('baseline', a), ('refined', b), ('absolute_delta', delta)]:
                        if not np.isclose(value, recorded[key][metric][target], rtol=1e-12, atol=1e-12):
                            raise ValueError('score replay discrepancy')
                        row[key+'_'+target] = value
                    maximum_delta = max(maximum_delta, delta)
                rows.append(row)
            maximum_error = float(np.abs(x[:n]-previous[:n]).max())
            rms_error = float(np.sqrt(np.mean((x[:n]-previous[:n])**2)))
            if (maximum_error != recorded['maximum_log_error'] or
                rms_error != recorded['rms_log_error']):
                raise ValueError('trajectory-error replay discrepancy')
            inside = all(abs(after[m][t]-before[m][t]) <= config['solver_margin']
                         for m in before for t in before[m])
            if inside != recorded['inside_original_solver_margin']:
                raise ValueError('solver-margin replay discrepancy')
        with (output/'tail-solver-scores.csv').open('w') as stream:
            writer = csv.DictWriter(stream, list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
        summary.update(trajectory_sha256=receipt['trajectory_sha256'],
                       elapsed_seconds=receipt['elapsed_seconds'],
                       maximum_log_error=maximum_error, rms_log_error=rms_error,
                       maximum_absolute_score_delta=maximum_delta,
                       all_scores_inside_original_solver_margin=maximum_delta <= config['solver_margin'],
                       replayed_score_values=3*sum(len(v) for v in before.values())*len(config['lengths']),
                       scores_sha256=digest(output/'tail-solver-scores.csv'))
    write(output/'tail-solver-summary.json', summary)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--study', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.baseline, args.study, args.output)))
