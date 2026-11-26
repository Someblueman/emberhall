"""Audit all frozen refinement receipts against arrays before exporting results."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

from paired_refinement import configuration, digest, summarize, validate, write_json
from reference import community, score
from convergence import METRICS, TARGETS, difference, stationarity


def check_table(actual, expected):
    if set(actual) != set(expected):
        raise ValueError('score table keys differ')
    for key in expected:
        if isinstance(expected[key], dict):
            check_table(actual[key], expected[key])
        elif not np.allclose(actual[key], expected[key], rtol=0, atol=1e-12):
            raise ValueError('receipt scores/diagnostics differ from trajectories')


def audit(study):
    protocol = study/'protocol.json'
    config = json.loads(protocol.read_text())
    if config != configuration():
        raise ValueError('frozen source or configuration differs')
    protocol_hash = digest(protocol)
    rows, hashes = [], {}
    for seed in config['communities']:
        for drive in config['drives']:
            path = study/f'community-{seed}-drive-{drive}.json'
            row = validate(json.loads(path.read_text()), seed, drive, protocol_hash)
            hashes[f'{seed}:{drive}'] = digest(path)
            if row['status'] == 'success':
                array_path = path.with_suffix('.npz')
                if digest(array_path) != row['trajectory_sha256']:
                    raise ValueError('trajectory hash mismatch')
                with np.load(array_path, allow_pickle=False) as arrays:
                    coarse, fine = arrays['coarse'], arrays['fine']
                for x in (coarse, fine):
                    if x.shape != (config['duration']-config['burn'], 6) or not np.isfinite(x).all():
                        raise ValueError('trajectory shape or finite-value failure')
                _, gain, labels = community(seed)
                full = score(fine, gain, labels)
                short = score(fine[:config['lengths'][0]], gain, labels)
                old = score(coarse, gain, labels)
                for field, expected in dict(scores=full, coarse_scores=old, short_scores=short,
                        second_half_scores=score(fine[config['lengths'][0]:], gain, labels),
                        forcing_delta=difference(old, full), length_delta=difference(short, full),
                        stationarity=stationarity(fine),
                        segment_delta={str(n): difference(full, score(fine, gain, labels, n))
                                       for n in (16, 60)}).items():
                    check_table(row[field], expected)
                if not np.isclose(row['log_rms'], np.sqrt(np.mean((fine-coarse)**2)), rtol=0, atol=1e-12):
                    raise ValueError('trajectory discrepancy differs')
            rows.append(row)
    return config, rows, hashes


def export(study, output):
    config, rows, hashes = audit(study)
    report = summarize(rows, config)
    good = [r for r in rows if r['status'] == 'success']
    report.update(protocol_sha256=digest(study/'protocol.json'), receipt_sha256=hashes,
                  exporter_sha256=digest(Path(__file__)),
                  audited='all stored scores, segment changes, stationarity and mesh RMS replayed from hash-bound trajectories',
                  total_solve_seconds=sum(r['elapsed_seconds'] for r in rows))
    if good:
        report.update(maximum_log_rms=max(r['log_rms'] for r in good),
            minimum_supply=min(r['minimum_supply'] for r in good),
            minimum_observed_abundance=min(min(r['minimum_abundance']) for r in good),
            maximum_half_mean_shift_in_sd=max(max(r['stationarity']['half_mean_shift_in_sd']) for r in good),
            half_variance_ratio_range=[min(min(r['stationarity']['half_variance_ratio']) for r in good),
                                       max(max(r['stationarity']['half_variance_ratio']) for r in good)],
            maximum_segment_changes={m: {k: max(abs(r['segment_delta'][str(n)][m][k])
                for r in good for n in (16, 60)) for k in TARGETS} for m in METRICS},
            solver_checks=[dict(community=r['community'], drive=r['drive'], checks=r['solver_checks'])
                           for r in good if 'solver_checks' in r])
    output.mkdir(parents=True, exist_ok=True)
    write_json(output/'summary.json', report)
    (output/'protocol.json').write_bytes((study/'protocol.json').read_bytes())
    fields = ['community', 'drive', 'metric'] + [f'{field}_{target}'
        for field in ('scores', 'forcing_delta', 'length_delta') for target in TARGETS]
    with (output/'scores.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        for row in good:
            for metric in METRICS:
                writer.writerow(dict(community=row['community'], drive=row['drive'], metric=metric,
                    **{f'{field}_{target}': row[field][metric][target]
                       for field in ('scores', 'forcing_delta', 'length_delta') for target in TARGETS}))
    print(json.dumps({k: report[k] for k in ('planned', 'attempted', 'complete', 'complete_communities')}))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    export(args.study, args.output)
