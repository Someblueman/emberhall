"""Paired clean-reference convergence experiment; see CONVERGENCE.md."""
import argparse
import json
from pathlib import Path
import numpy as np
import scipy
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


def run(output, communities=12, drives=2, duration=4096, burn=1024,
        finest=.0625, segments=(16, 30, 60), resume=False, max_attempts=None):
    if communities < 2 or drives < 1 or duration - burn < 480 or burn < 0:
        raise ValueError('need two communities, one drive, nonnegative burn and 480 samples')
    if finest <= 0 or not np.isclose(duration / (4 * finest), round(duration / (4 * finest))):
        raise ValueError('duration must divide the coarsest mesh exactly')
    if max_attempts is not None and max_attempts < 1:
        raise ValueError('max_attempts must be positive')
    if output.exists() and not resume:
        raise ValueError('use a new output directory or explicitly resume')
    if resume and not output.exists():
        raise ValueError('cannot resume a missing experiment')
    output.mkdir(parents=True, exist_ok=resume)
    config = dict(communities=communities, drives=drives, duration=duration,
                  burn=burn, finest=finest, segments=list(segments),
                  numpy=np.__version__, scipy=scipy.__version__)
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
    remaining = [(s, d) for s in range(communities) for d in range(drives)
                 if (s, d) not in completed]
    scheduled = set(remaining if max_attempts is None else remaining[:max_attempts])
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
                  summaries={field: aggregate(complete, field) for field in fields} if complete else {})
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
    parser.add_argument('--max-attempts', type=int)
    args = parser.parse_args()
    run(**vars(args))
