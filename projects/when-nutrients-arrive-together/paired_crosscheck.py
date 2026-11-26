"""Paired clean-reference convergence experiment; see CROSSCHECK.md."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import scipy
from scipy.stats import beta
from reference import community, ou, simulate, score, interval

METRICS = ('correlation', 'absolute_correlation', 'cpsd', 'coherence')
KEYS = ('overlap_spearman', 'same_diet_pair_auc', 'single_linkage_guild_auc')


def compare(first, second):
    return {m: {k: second[m][k] - first[m][k] for k in KEYS} for m in METRICS}


def stationarity(x):
    """Descriptive diagnostics only: halves are dependent, not replicates."""
    halves = np.array_split(x, 2)
    return dict(half_mean_shift_in_sd=(np.abs(halves[0].mean(0) - halves[1].mean(0))
                                     / x.std(0)).tolist(),
                half_variance_ratio=(halves[0].var(0) / halves[1].var(0)).tolist())


def aggregate(records, field):
    """Each independent community contributes once, after averaging its drives."""
    groups = {}
    for row in records:
        groups.setdefault(row['community'], []).append(row[field])
    return {m: {k: interval([np.mean([v[m][k] for v in group])
                            for group in groups.values()]) for k in KEYS} for m in METRICS}


def perfect_recovery(records):
    """A community succeeds only when every drive has perfect guild AUC.

    The binomial interval describes community-level perfect recovery in this
    experiment, not a confidence interval for mean AUC or a zero-error promise.
    """
    groups = {}
    for row in records:
        groups.setdefault(row['community'], []).append(row['scores'])
    result = {}
    for metric in METRICS:
        count = sum(all(v[metric]['single_linkage_guild_auc'] >= 1 - 1e-12
                        for v in group) for group in groups.values())
        n = len(groups)
        result[metric] = dict(successes=count, communities=n,
            exact_ci95=([float(beta.ppf(.025, count, n-count+1)) if count else 0.,
                         float(beta.ppf(.975, count+1, n-count)) if count < n else 1.]
                        if n else None))
    return result


def run(output, communities=12, drives=2, duration=4096, burn=1024,
        finest=.0625, segments=(16, 30, 60), resume=False, max_attempts=None, report_only=False):
    if communities < 2 or drives < 1 or duration - burn < 480 or burn < 0:
        raise ValueError('need two communities, one drive, nonnegative burn and 480 samples')
    if finest <= 0 or not np.isclose(duration / (4 * finest), round(duration / (4 * finest))):
        raise ValueError('duration must divide the coarsest mesh exactly')
    if report_only and not resume:
        raise ValueError('report-only requires an existing experiment and --resume')
    if max_attempts is not None and max_attempts < 1:
        raise ValueError('max_attempts must be positive')
    if output.exists() and not resume:
        raise ValueError('use a new output directory or explicitly resume')
    if resume and not output.exists():
        raise ValueError('cannot resume a missing experiment')
    output.mkdir(parents=True, exist_ok=resume)
    config = dict(communities=communities, drives=drives, duration=duration,
                  burn=burn, finest=finest, segments=list(segments),
                  numpy=np.__version__, scipy=scipy.__version__,
                  model_sha256=hashlib.sha256(Path(__file__).with_name('reference.py').read_bytes()).hexdigest())
    if resume:
        if json.loads((output / 'config.json').read_text()) != config:
            raise ValueError('resume configuration differs from frozen experiment')
    else:
        (output / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
    records = ([json.loads(line) for line in (output / 'records.jsonl').read_text().splitlines()]
               if (output / 'records.jsonl').exists() else [])
    failures = (json.loads((output / 'failures.json').read_text())
                if (output / 'failures.json').exists() else [])
    completed = {(r['community'], r['drive']) for r in records + failures}
    if len(completed) != len(records) + len(failures):
        raise ValueError('duplicate attempt identities in checkpoint')
    planned = {(s, d) for s in range(communities) for d in range(drives)}
    if not completed <= planned or any(r['input_seed'] != 200000 + 1000*r['community'] + r['drive']
                                       for r in records + failures):
        raise ValueError('checkpoint identities differ from frozen seed schedule')
    remaining = [(s, d) for s in range(communities) for d in range(drives)
                 if (s, d) not in completed]
    scheduled = set() if report_only else set(remaining if max_attempts is None else remaining[:max_attempts])
    for seed in range(communities):
        uptake, gain, labels = community(seed)
        for drive in range(drives):
            if (seed, drive) not in scheduled:
                continue
            # Disjoint seeds from the pilot, fixed before inspecting any scores.
            input_seed = 200000 + 1000 * seed + drive
            identity = dict(community=seed, drive=drive, input_seed=input_seed)
            failed = False
            try:
                supply = ou(input_seed, duration, finest)
                if supply.min() <= 0:
                    raise ValueError('nonpositive supply; no repair')
                trajectories = []
                for stride in (4, 2, 1):
                    spacing = finest * stride
                    x, minimum = simulate(uptake, gain, supply[::stride], spacing,
                                          duration, burn, spacing / 2, 1e-8)
                    trajectories.append(x)
                scores = [score(x, gain, labels) for x in trajectories]
                x = trajectories[-1]
                # First half and full window share the same realization and burn.
                short = score(x[:len(x)//2], gain, labels)
                late = score(x[len(x)//2:], gain, labels)
                row = dict(**identity, minimum_supply=float(supply.min()),
                           minimum_abundance=minimum, scores=scores[-1],
                           coarse_to_middle=compare(scores[0], scores[1]),
                           middle_to_fine=compare(scores[1], scores[2]),
                           short_to_full=compare(short, scores[-1]),
                           early_to_late=compare(short, late),
                           stationarity=stationarity(x),
                           log_rms=[float(np.sqrt(np.mean((b-a)**2)))
                                    for a,b in zip(trajectories, trajectories[1:])],
                           segment_scores={str(n):score(x, gain, labels, n) for n in segments})
                # Preserve the fine trajectory for new estimators without rerunning dynamics.
                np.savez_compressed(output / f'community-{seed}-drive-{drive}.npz',
                                    log_abundance=x, uptake=uptake, gain=gain, labels=labels)
                encoded = json.dumps(row, allow_nan=False)
                records.append(row)
                with (output / 'records.jsonl').open('a') as stream:
                    stream.write(encoded + '\n')
            except (ValueError, RuntimeError, FloatingPointError) as error:
                failed = True
                failures.append(dict(**identity, error=str(error)))
                (output / 'failures.json').write_text(json.dumps(failures, indent=2) + '\n')
            print(f'community {seed} drive {drive}: {"failed" if failed else "recorded"}', flush=True)
    # Never average communities with missing drives into a clean population summary.
    complete = [r for r in records if sum(s['community'] == r['community'] for s in records) == drives]
    fields = ('scores', 'coarse_to_middle', 'middle_to_fine', 'short_to_full', 'early_to_late')
    report = dict(config=config, attempted=communities * drives, successful=len(records), completed_attempts=len(records)+len(failures),
                  complete=len(records)+len(failures) == communities*drives,
                  failures=failures, complete_communities=len({r['community'] for r in complete}),
                  status='diagnostic; conditional on success if any failure; not milestone acceptance',
                  perfect_guild_recovery=perfect_recovery(complete),
                  summaries={field: aggregate(complete, field) for field in fields} if complete else {})
    gates = {}
    for field in ('middle_to_fine', 'short_to_full'):
        gates[field] = {}
        for metric in METRICS:
            gates[field][metric] = {}
            for key in KEYS:
                ci = report['summaries'].get(field, {}).get(metric, {}).get(key, {}).get('ci95')
                worst = max((abs(r[field][metric][key]) for r in records), default=None)
                gates[field][metric][key] = dict(ci95=ci, worst_absolute_change=worst,
                    inside_margins=bool(ci is not None and ci[0] >= -.03 and ci[1] <= .03
                                        and worst is not None and worst <= .10))
    report['exploratory_gates'] = gates
    report['candidate_stable'] = bool(report['complete'] and not failures and all(
        v['inside_margins'] for field in gates.values() for metric in field.values() for v in metric.values()))
    (output / 'report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--communities', type=int, default=12)
    parser.add_argument('--drives', type=int, default=2)
    parser.add_argument('--duration', type=int, default=4096)
    parser.add_argument('--burn', type=int, default=1024)
    parser.add_argument('--finest', type=float, default=.0625)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--report-only', action='store_true')
    parser.add_argument('--max-attempts', type=int)
    args = parser.parse_args()
    run(**vars(args))
