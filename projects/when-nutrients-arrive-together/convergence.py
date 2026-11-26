"""Nested-path clean-reference study; protocol.json is written before simulation."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import t

from reference import community, ou, simulate, score, interval

METRICS = ('correlation', 'absolute_correlation', 'cpsd', 'coherence')
TARGETS = ('overlap_spearman', 'same_diet_pair_auc', 'single_linkage_guild_auc')


def protocol(seeds, duration, burn):
    return dict(version=1, seeds=list(seeds), input_seed_offset=20000,
                duration=duration, burn=burn, meshes=[.25, .125, .0625],
                rtol=1e-8, solver_check_rtol=1e-10,
                solver_check_max_step=.03125, segments=[16, 30, 60],
                primary_segment=30, sample_interval=1,
                thresholds=dict(solver_score=.005, forcing_overlap=.05,
                                forcing_auc=.03, length_overlap=.1, length_auc=.05,
                                mean_ci_half_width=.1),
                held_out=dict(community_seeds=[1000, 1031], input_seed_offset=30000,
                              correlations=[0, .25, .5, .75],
                              status='reserved; not executed; see PROTOCOL.md'))


def difference(a, b):
    return {m: {k: float(b[m][k] - a[m][k]) for k in TARGETS} for m in METRICS}


def stationarity(x):
    half = len(x) // 2
    return dict(half_mean_shift_in_sd=(np.abs(x[:half].mean(0) - x[half:].mean(0))
                                      / x.std(0)).tolist(),
                half_variance_ratio=(x[:half].var(0) / x[half:].var(0)).tolist())


def summarize(records, config):
    good = [r for r in records if r['status'] == 'success']
    summary = {}
    for m in METRICS:
        summary[m] = {}
        for k in TARGETS:
            values = [r['scores']['0.0625']['30'][m][k] for r in good]
            if not values:
                continue
            stat = interval(values)
            # Distribution-free marginal bound for the expected bounded score.
            # Remains nonzero when every observed community is perfect.
            width = 2 if k == 'overlap_spearman' else 1
            radius = width * np.sqrt(np.log(40) / (2 * len(values)))
            stat['hoeffding_ci95'] = [max(-1 if width == 2 else 0, stat['mean']-radius),
                                      min(1, stat['mean']+radius)]
            summary[m][k] = stat
    gates = dict(no_failures=len(good) == len(config['seeds']) == len(records))
    for name, field, overlap, auc_limit in [
            ('forcing', 'finest_forcing_delta', .05, .03),
            ('length', 'length_delta', .1, .05),
            ('solver', 'solver_delta', .005, .005)]:
        gates[name] = bool(good) and all(abs(r[field][m][k]) <=
                            (overlap if k == 'overlap_spearman' else auc_limit)
                            for r in good for m in METRICS for k in TARGETS)
    gates['precision'] = bool(summary) and all(
        s['ci95'] is not None and (s['ci95'][1]-s['ci95'][0])/2 <= .1
        and (s['hoeffding_ci95'][1]-s['hoeffding_ci95'][0])/2 <= .1
        for by_metric in summary.values() for s in by_metric.values())
    return dict(status='empirical diagnostics only; no milestone acceptance',
                attempted=len(records), planned=len(config['seeds']),
                failures=[r for r in records if r['status'] != 'success'],
                summaries=summary, gates=gates,
                caveat='Student-t intervals are approximate; Hoeffding intervals are marginal, not simultaneous. No stationarity proof or continuum error bound.')


def run(output, seeds, duration=4608, burn=512):
    if duration-burn < 480 or burn < 0 or duration % 1:
        raise ValueError('need nonnegative burn and at least 480 retained observations')
    output.mkdir(parents=True, exist_ok=True)
    config = protocol(seeds, duration, burn)
    config['versions'] = dict(numpy=np.__version__, scipy=scipy.__version__)
    config['code_sha256'] = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                             for name in ('reference.py', 'convergence.py')}
    encoded = json.dumps(config, indent=2, sort_keys=True) + '\n'
    path = output / 'protocol.json'
    if path.exists() and path.read_text() != encoded:
        raise ValueError('output already has a different protocol; use a new directory')
    path.write_text(encoded)
    records = []
    for seed in seeds:
        receipt = output / f'seed-{seed}.json'
        if receipt.exists():
            records.append(json.loads(receipt.read_text()))
            continue
        record = dict(seed=seed, status='failure')
        try:
            uptake, gain, labels = community(seed)
            supply = ou(20000+seed, duration, spacing=.0625)
            record['minimum_supply'] = float(supply.min())
            if supply.min() <= 0:
                raise ValueError('nonpositive supply; no repair')
            trajectories, scores = {}, {}
            for mesh, stride in ((.25, 4), (.125, 2), (.0625, 1)):
                x, minimum = simulate(uptake, gain, supply[::stride], mesh,
                                      duration, burn, mesh, 1e-8)
                trajectories[str(mesh)] = x
                scores[str(mesh)] = {str(segment): score(x, gain, labels, segment)
                                     for segment in (16, 30, 60)}
                print(f'seed {seed} mesh {mesh} recorded', flush=True)
            x = trajectories['0.0625']
            solver, _ = simulate(uptake, gain, supply, .0625, duration, burn, .03125, 1e-10)
            # Arrays are private; every score and failure survives in small JSON.
            np.savez_compressed(output / f'seed-{seed}.npz',
                                **{f'log_x_{k}': v for k,v in trajectories.items()},
                                solver=solver, uptake=uptake, gain=gain, labels=labels)
            record.update(status='success', scores=scores,
                stationarity=stationarity(x), minimum_abundance=minimum,
                finest_forcing_delta=difference(scores['0.125']['30'], scores['0.0625']['30']),
                coarse_forcing_delta=difference(scores['0.25']['30'], scores['0.125']['30']),
                solver_delta=difference(scores['0.0625']['30'], score(solver, gain, labels)),
                solver_log_rms=float(np.sqrt(np.mean((solver-x)**2))),
                forcing_log_rms=float(np.sqrt(np.mean((trajectories['0.125']-x)**2))),
                length_delta=difference(score(x[:len(x)//2], gain, labels), scores['0.0625']['30']),
                second_half_scores=score(x[len(x)//2:], gain, labels))
        except (ValueError, RuntimeError, FloatingPointError) as error:
            record['error'] = str(error)
        receipt.write_text(json.dumps(record, indent=2, allow_nan=False)+'\n')
        records.append(record)
        (output/'report.json').write_text(json.dumps(summarize(records, config), indent=2, allow_nan=False)+'\n')
        print(f'seed {seed}: {record["status"]}', flush=True)
    report = summarize(records, config)
    (output/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--start', type=int, default=4)
    parser.add_argument('--seeds', type=int, default=12)
    parser.add_argument('--duration', type=int, default=4608)
    parser.add_argument('--burn', type=int, default=512)
    args = parser.parse_args()
    if args.seeds < 2:
        parser.error('at least two communities required')
    run(args.output, range(args.start, args.start+args.seeds), args.duration, args.burn)
