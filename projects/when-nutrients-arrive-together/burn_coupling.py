"""Shared-drive initial-condition diagnostic, not a nonlinear stationarity proof."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from reference import community, ou, rhs, score
from linear_reference import equilibrium, linear_system
from ou_bridge import bridge
from convergence import stationarity


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config():
    names = ('burn_coupling.py', 'reference.py', 'linear_reference.py',
             'ou_bridge.py', 'convergence.py')
    return dict(seeds=list(range(4, 16)), duration=1024, burn=512,
                coarse_spacing=1/16, spacing=1/32, max_step=1/32,
                tolerance=1e-9, input_seed='80000 + 100*community',
                bridge_seed='90000 + 100*community',
                initial_conditions=['all amounts one', 'constant-mean-supply equilibrium'],
                checkpoints=[0, 32, 64, 128, 256, 512, 1023],
                solver_control_seed=4, solver_control_step=1/64,
                solver_control_tolerance=1e-11,
                numpy=np.__version__, scipy=scipy.__version__,
                sources={n: digest(Path(__file__).with_name(n)) for n in names},
                scope='fixed development cohort, one reused input prefix each; no population or stationarity certificate')


def coupled(uptake, gain, supply, spacing, duration, initial, max_step, tolerance):
    """Integrate independent ecological states together under identical forcing."""
    initial = np.asarray(initial, dtype=float)
    if initial.ndim != 2 or initial.shape[1] != 36 or not np.isfinite(initial).all():
        raise ValueError('need finite initial states in log-consumer/resource coordinates')
    if np.any(initial[:, 6:] <= 0) or np.min(supply) <= 0:
        raise ValueError('nonpositive resource or supply; no repair')
    if len(supply) != round(duration/spacing)+1:
        raise ValueError('supply does not cover duration')

    def derivative(time, flat):
        position = min(time/spacing, len(supply)-1)
        left = min(int(position), len(supply)-2)
        fraction = position-left
        drive = supply[left]*(1-fraction)+supply[left+1]*fraction
        return np.concatenate([rhs(state, drive, uptake, gain)
                               for state in flat.reshape(initial.shape)])

    solution = solve_ivp(derivative, (0, duration), initial.ravel(),
                         t_eval=np.arange(duration), rtol=tolerance,
                         atol=tolerance/100, max_step=max_step)
    if not solution.success or solution.y.shape[1] != duration:
        raise RuntimeError(solution.message)
    states = solution.y.T.reshape(duration, *initial.shape)
    if not np.isfinite(states).all() or states[:, :, 6:].min() <= 0:
        raise ValueError('nonfinite state or nonpositive resource; no repair')
    if states[:, :, :6].min() < np.log(1e-8):
        raise ValueError('near extinction; no replacement')
    return states


def diagnostics(states, gain, labels, burn=512):
    logs = states[:, :, :6]
    delta = np.abs(logs[:, 0]-logs[:, 1])
    retained = logs[burn:]
    scales = retained[:, 0].std(axis=0)
    if np.any(scales <= 1e-12):
        raise ValueError('constant retained abundance')
    scores = [score(retained[:, i], gain, labels) for i in range(2)]
    return dict(maximum_post_burn_log_difference=float(delta[burn:].max()),
                maximum_post_burn_standardized_difference=float((delta[burn:]/scales).max()),
                maximum_post_burn_resource_difference=float(np.abs(
                    states[burn:, 0, 6:]-states[burn:, 1, 6:]).max()),
                checkpoint_log_differences={str(t): float(delta[t].max())
                                           for t in (0, 32, 64, 128, 256, 512, len(states)-1)},
                score_differences={m: {k: scores[1][m][k]-scores[0][m][k]
                                      for k in scores[0][m]} for m in scores[0]},
                stationarity_descriptive=[stationarity(retained[:, i]) for i in range(2)])


def freeze(output):
    output.mkdir(parents=True, exist_ok=True)
    settings = config()
    encoded = json.dumps(settings, indent=2, sort_keys=True)+'\n'
    protocol = output/'protocol.json'
    if protocol.exists() and protocol.read_text() != encoded:
        raise ValueError('changed protocol or source; use a new output directory')
    protocol.write_text(encoded)
    return settings


def run_seed(output, seed, settings):
    receipt = output/f'seed-{seed}.json'
    identity = dict(seed=seed, protocol_sha256=digest(output/'protocol.json'))
    if receipt.exists():
        old = json.loads(receipt.read_text())
        if any(old.get(k) != v for k, v in identity.items()):
            raise ValueError('changed receipt identity')
        return old
    record = dict(**identity, status='failure')
    try:
        u, g, labels = community(seed)
        x, r = equilibrium(u, g, np.r_[np.ones(24), np.full(6, 3.)])
        j, _ = linear_system(u, g, x, r)
        decay = float(np.max(np.linalg.eigvals(j).real))
        if decay >= 0:
            raise ValueError('unstable constant-supply equilibrium')
        initial = np.array([np.r_[np.zeros(6), np.ones(30)], np.r_[np.log(x), r]])
        supply = bridge(ou(80000+100*seed, settings['duration'], 1/16),
                        1/16, 90000+100*seed)
        states = coupled(u, g, supply, settings['spacing'], settings['duration'],
                         initial, settings['max_step'], settings['tolerance'])
        record.update(diagnostics(states, g, labels, settings['burn']))
        record['linear_relaxation_time'] = -1/decay
        record['equilibrium_residual'] = float(np.abs(rhs(initial[1],
            np.r_[np.ones(24), np.full(6, 3.)], u, g)).max())
        arrays = output/f'seed-{seed}.npz'
        contents = dict(states=states)
        if seed == settings['solver_control_seed']:
            tighter = coupled(u, g, supply, settings['spacing'], settings['duration'],
                              initial, settings['solver_control_step'],
                              settings['solver_control_tolerance'])
            record['solver_control'] = dict(
                maximum_state_difference=float(np.abs(tighter-states).max()),
                diagnostics=diagnostics(tighter, g, labels, settings['burn']))
            contents['tighter_states'] = tighter
        np.savez_compressed(arrays, **contents)
        record.update(status='success', arrays_sha256=digest(arrays))
    except (ValueError, RuntimeError, FloatingPointError) as error:
        record['error'] = str(error)
    receipt.write_text(json.dumps(record, indent=2, allow_nan=False)+'\n')
    return record


def summarize(output, settings):
    records = []
    for seed in settings['seeds']:
        path = output/f'seed-{seed}.json'
        if not path.exists():
            continue
        record = json.loads(path.read_text())
        if record['seed'] != seed or record['protocol_sha256'] != digest(output/'protocol.json'):
            raise ValueError('receipt identity mismatch')
        if record['status'] == 'success':
            arrays = output/f'seed-{seed}.npz'
            if digest(arrays) != record['arrays_sha256']:
                raise ValueError('changed trajectory')
            with np.load(arrays, allow_pickle=False) as saved:
                _, g, labels = community(seed)
                replay = diagnostics(saved['states'], g, labels, settings['burn'])
                for key, value in replay.items():
                    if value != record[key]:
                        raise ValueError('diagnostic does not replay: '+key)
                if 'solver_control' in record:
                    tight = diagnostics(saved['tighter_states'], g, labels, settings['burn'])
                    error = float(np.abs(saved['tighter_states']-saved['states']).max())
                    if tight != record['solver_control']['diagnostics'] or error != record['solver_control']['maximum_state_difference']:
                        raise ValueError('solver control does not replay')
        records.append(record)
    good = [r for r in records if r['status'] == 'success']
    result = dict(planned=len(settings['seeds']), attempted=len(records), successful=len(good),
                  complete=len(records) == len(settings['seeds']),
                  failures=[r for r in records if r['status'] != 'success'],
                  records=records, scope=settings['scope'])
    (output/'summary.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    fields = ['seed', 'linear_relaxation_time', 'maximum_post_burn_log_difference',
              'maximum_post_burn_standardized_difference', 'maximum_post_burn_resource_difference']
    with (output/'scores.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fields, extrasaction='ignore')
        writer.writeheader(); writer.writerows(good)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--start', type=int, default=4)
    parser.add_argument('--stop', type=int, default=16)
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    settings = freeze(args.output)
    if not args.report_only:
        if not 4 <= args.start < args.stop <= 16:
            parser.error('range must be within development communities 4..15')
        for seed in range(args.start, args.stop):
            record = run_seed(args.output, seed, settings)
            print(seed, record['status'], flush=True)
    else:
        summary = summarize(args.output, settings)
        print('attempted', summary['attempted'], 'successful', summary['successful'],
              'complete', summary['complete'])
