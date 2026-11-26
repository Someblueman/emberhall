"""Audit the unchanged frozen burn runner with an explicit 1e-12 replay tolerance.

The original exporter used exact equality on floating reductions of arrays with
different memory layouts. Its witnessed rejection is retained in BURN_COUPLING.md.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

from burn_coupling import config, diagnostics, digest
from reference import community


def compare(actual, expected):
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            raise ValueError('replay keys differ')
        return max((compare(actual[k], expected[k]) for k in expected), default=0.)
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ValueError('replay shape differs')
        return max((compare(a, b) for a, b in zip(actual, expected)), default=0.)
    a, b = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
    if a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('replay shape or finite-value failure')
    error = float(np.max(np.abs(a-b))) if a.size else 0.
    if error > 1e-12:
        raise ValueError('diagnostic differs beyond declared replay tolerance')
    return error


def audit(study, output):
    protocol = study/'protocol.json'
    settings = json.loads(protocol.read_text())
    if settings != config():
        raise ValueError('frozen runner source or settings differ')
    records, errors, solver_log_errors = [], [], []
    for seed in settings['seeds']:
        path = study/f'seed-{seed}.json'
        record = json.loads(path.read_text())
        if record['seed'] != seed or record['protocol_sha256'] != digest(protocol):
            raise ValueError('receipt identity mismatch')
        if record['status'] not in ('success', 'failure'):
            raise ValueError('unknown receipt status')
        if record['status'] == 'success':
            arrays_path = study/f'seed-{seed}.npz'
            if digest(arrays_path) != record['arrays_sha256']:
                raise ValueError('changed trajectory')
            _, gain, labels = community(seed)
            with np.load(arrays_path, allow_pickle=False) as arrays:
                states = arrays['states']
                if states.shape != (settings['duration'], 2, 36) or not np.isfinite(states).all():
                    raise ValueError('invalid trajectory')
                replay = diagnostics(states, gain, labels, settings['burn'])
                errors.append(compare({k: record[k] for k in replay}, replay))
                if seed == settings['solver_control_seed']:
                    tight = arrays['tighter_states']
                    if tight.shape != states.shape or not np.isfinite(tight).all():
                        raise ValueError('invalid tighter trajectory')
                    errors.append(compare(record['solver_control'], dict(
                        maximum_state_difference=float(np.abs(tight-states).max()),
                        diagnostics=diagnostics(tight, gain, labels, settings['burn']))))
                    solver_log_errors.append(float(np.abs(
                        tight[settings['burn']:, :, :6]-states[settings['burn']:, :, :6]).max()))
        records.append(record)
    summary = dict(planned=len(settings['seeds']), attempted=len(records),
                   successful=sum(r['status'] == 'success' for r in records),
                   failures=[r for r in records if r['status'] == 'failure'],
                   complete=True, records=records,
                   maximum_replay_discrepancy=max(errors, default=0.),
                   replay_absolute_tolerance=1e-12, auditor_sha256=digest(Path(__file__)),
                   protocol_sha256=digest(protocol),
                   receipt_sha256={str(s): digest(study/f'seed-{s}.json') for s in settings['seeds']},
                   scope=settings['scope'])
    output.mkdir(parents=True, exist_ok=True)
    (output/'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    good = [r for r in records if r['status'] == 'success']
    compact = {k: v for k, v in summary.items() if k != 'records'}
    if good:
        compact.update(
            maximum_checkpoint_log_difference={str(t): max(r['checkpoint_log_differences'][str(t)] for r in good)
                                               for t in settings['checkpoints']},
            linear_relaxation_time_range=[min(r['linear_relaxation_time'] for r in good),
                                          max(r['linear_relaxation_time'] for r in good)],
            maximum_equilibrium_residual=max(r['equilibrium_residual'] for r in good),
            maximum_post_burn_log_difference=max(r['maximum_post_burn_log_difference'] for r in good),
            maximum_post_burn_standardized_difference=max(r['maximum_post_burn_standardized_difference'] for r in good),
            maximum_post_burn_resource_difference=max(r['maximum_post_burn_resource_difference'] for r in good),
            maximum_absolute_score_difference=max(abs(v) for r in good for m in r['score_differences'].values() for v in m.values()),
            maximum_solver_control_post_burn_log_difference=max(solver_log_errors, default=None),
            maximum_solver_control_state_difference=max((r['solver_control']['maximum_state_difference'] for r in good
                                                         if 'solver_control' in r), default=None))
    (output/'compact-summary.json').write_text(json.dumps(compact, indent=2, allow_nan=False)+'\n')
    fields = ['seed', 'linear_relaxation_time', 'maximum_post_burn_log_difference',
              'maximum_post_burn_standardized_difference', 'maximum_post_burn_resource_difference']
    with (output/'scores.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fields, extrasaction='ignore')
        writer.writeheader(); writer.writerows(r for r in records if r['status'] == 'success')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.study, args.output)
    print('complete', result['complete'], 'success', result['successful'],
          'maximum replay discrepancy', result['maximum_replay_discrepancy'])
