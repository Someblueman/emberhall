"""Independent-input ECRM pilot; see MODEL.md for source and departures."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.signal import csd, welch
from scipy.stats import rankdata, spearmanr, t

PAIRS = np.triu_indices(6, 1)


def community(seed, bias=0.4):
    rng = np.random.default_rng(seed)
    labels = np.repeat([0, 1], 3)
    resource_labels = np.repeat([0, 1], 12)
    p = np.where(labels[:, None] == resource_labels, 0.5 + bias, 0.5 - bias)
    uptake = 0.1 * np.column_stack((rng.random((6, 24)) < p, np.eye(6)))
    yields = rng.normal(1, 1 / 6, uptake.shape)
    while np.any(yields < 0):
        bad = yields < 0
        yields[bad] = rng.normal(1, 1 / 6, bad.sum())
    return uptake, uptake * yields, labels


def ou(seed, duration, spacing=0.25, amplitude=0.1, omega=1.0):
    """Stationary OU, exact transitions; no clipping or rejection of paths."""
    rng = np.random.default_rng(seed)
    count = int(round(duration / spacing))
    if not np.isclose(count * spacing, duration):
        raise ValueError('duration must be a multiple of drive spacing')
    q = np.empty((count + 1, 30))
    q[0] = rng.normal(size=30) * amplitude / np.sqrt(2)
    decay = np.exp(-omega * spacing)
    innovation = amplitude * np.sqrt((1 - decay**2) / 2)
    for i in range(count):
        q[i + 1] = decay * q[i] + innovation * rng.normal(size=30)
    base = np.r_[np.ones(24), np.full(6, 3.0)]
    return base + q


def rhs(state, supply, uptake, gain):
    x, resources = np.exp(state[:6]), state[6:]
    return np.r_[gain @ resources - 0.3,
                 supply - (0.5 + uptake.T @ x) * resources]


def simulate(uptake, gain, supply, spacing, duration, burn, max_step, tolerance):
    def derivative(time, state):
        position = min(time / spacing, len(supply) - 1)
        left = min(int(position), len(supply) - 2)
        fraction = position - left
        k = supply[left] * (1 - fraction) + supply[left + 1] * fraction
        return rhs(state, k, uptake, gain)
    times = np.arange(burn, duration, 1.0)
    result = solve_ivp(derivative, (0, duration), np.r_[np.zeros(6), np.ones(30)],
                       t_eval=times, rtol=tolerance, atol=tolerance / 100,
                       max_step=max_step)
    if not result.success or result.y.shape[1] != len(times):
        raise RuntimeError(result.message)
    if not np.isfinite(result.y).all() or np.min(result.y[6:]) <= 0:
        raise ValueError('nonfinite state or nonpositive resource; not repaired')
    if np.min(result.y[:6]) < np.log(1e-8):
        raise ValueError('near extinction; not silently removed')
    return result.y[:6].T, float(np.exp(result.y[:6]).min())


def measures(log_x, nperseg=30):
    if len(log_x) < 4 * nperseg:
        raise ValueError('at least four Welch segments required')
    scales = log_x.std(axis=0)
    if np.any(scales < 1e-12):
        raise ValueError('constant abundance')
    z = (log_x - log_x.mean(axis=0)) / scales
    correlation = np.corrcoef(z.T)[PAIRS]
    freq, auto = welch(z, fs=1, window='hann', nperseg=nperseg,
                       noverlap=nperseg // 2, axis=0, detrend='constant')
    magnitude, coherence = [], []
    for i, j in zip(*PAIRS):
        _, cross = csd(z[:, i], z[:, j], fs=1, window='hann', nperseg=nperseg,
                       noverlap=nperseg // 2, detrend='constant')
        magnitude.append(np.abs(cross).sum() * (freq[1] - freq[0]))
        coherence.append((np.abs(cross)**2 / (auto[:, i] * auto[:, j])).sum()
                         * (freq[1] - freq[0]))
    return dict(correlation=correlation, absolute_correlation=np.abs(correlation),
                cpsd=np.array(magnitude), coherence=np.array(coherence))


def auc(target, scores):
    """Mann-Whitney AUC with half credit for ties; pairs are not replicates."""
    target = np.asarray(target, dtype=bool)
    n = target.sum()
    if not 0 < n < len(target):
        raise ValueError('AUC needs both classes')
    return float((rankdata(scores)[target].sum() - n * (n + 1) / 2)
                 / (n * (len(target) - n)))


def single_linkage_scores(pair_scores):
    """Connection threshold of each pair under single-linkage closure.

    Maximin path weight: connected at threshold h iff this value >= h.
    Labels never enter this operation.
    """
    links = np.full((6, 6), -np.inf)
    links[PAIRS] = pair_scores
    links[(PAIRS[1], PAIRS[0])] = pair_scores
    np.fill_diagonal(links, np.inf)
    for via in range(6):
        links = np.maximum(links, np.minimum(links[:, via, None], links[None, via, :]))
    return links[PAIRS]


def score(log_x, gain, labels, nperseg=30):
    overlap = (gain @ gain.T)[PAIRS]
    same = (labels[:, None] == labels)[PAIRS]
    return {name: {'overlap_spearman': float(spearmanr(values, overlap).statistic),
                   'same_diet_pair_auc': auc(same, values),
                   'single_linkage_guild_auc': auc(same, single_linkage_scores(values))}
            for name, values in measures(log_x, nperseg).items()}


def interval(values):
    values = np.asarray(values)
    mean = float(values.mean())
    if len(values) < 2:
        return dict(mean=mean, ci95=None, n=len(values))
    radius = float(t.ppf(0.975, len(values) - 1) * values.std(ddof=1) / np.sqrt(len(values)))
    return dict(mean=mean, ci95=[mean - radius, mean + radius], n=len(values))


def run(output, seeds=range(4), duration=1536, burn=512, drive_spacing=.25):
    if burn < 0 or duration - burn < 240 or drive_spacing <= 0:
        raise ValueError("need nonnegative burn, at least 240 observations, positive mesh")
    output.mkdir(parents=True, exist_ok=True)
    rows, failures, convergence, diagnostics = [], [], [], []
    for seed in seeds:
        uptake, gain, labels = community(seed)
        supply = ou(10000 + seed, duration, spacing=drive_spacing / 2)
        diagnostics.append(dict(seed=seed, minimum_supply=float(supply.min()),
                                supply_variance=float((supply - supply.mean(0)).var(0).mean())))
        try:
            if supply.min() <= 0:
                raise ValueError('negative OU supply; no clipping allowed')
            # Same fine OU path: refine solver separately from the drive mesh.
            coarse, _ = simulate(uptake, gain, supply[::2], drive_spacing, duration, burn, drive_spacing, 1e-6)
            fine, minimum = simulate(uptake, gain, supply[::2], drive_spacing, duration, burn, drive_spacing / 2, 1e-8)
            drive_fine, _ = simulate(uptake, gain, supply, drive_spacing / 2, duration, burn, drive_spacing / 2, 1e-8)
            s_coarse, s_fine, s_drive = [score(x, gain, labels) for x in (coarse, fine, drive_fine)]
            convergence.append(dict(seed=seed,
                solver_log_rms=float(np.sqrt(np.mean((fine - coarse)**2))),
                drive_log_rms=float(np.sqrt(np.mean((drive_fine - fine)**2))),
                minimum_abundance=minimum,
                half_mean_shift_in_sd=float(np.max(np.abs(
                    fine[:len(fine)//2].mean(0) - fine[len(fine)//2:].mean(0)) / fine.std(0))),
                half_variance_ratio=(fine[:len(fine)//2].var(0) / fine[len(fine)//2:].var(0)).tolist(),
                solver_max_score_change=max(abs(s_fine[m][k] - s_coarse[m][k]) for m in s_fine for k in s_fine[m]),
                drive_max_score_change=max(abs(s_drive[m][k] - s_fine[m][k]) for m in s_fine for k in s_fine[m])))
            np.savez_compressed(output / f'seed-{seed}.npz', log_abundance=fine,
                                fine_drive_log_abundance=drive_fine, supply=supply,
                                uptake=uptake, gain=gain, labels=labels,
                                observation_time=np.arange(burn, duration, 1.0),
                                supply_time=np.arange(len(supply)) * drive_spacing / 2)
            seed_rows = []
            for segment in (16, 30, 60):
                for name, scores in score(fine, gain, labels, segment).items():
                    seed_rows.append(dict(seed=seed, segment=segment, metric=name, **scores))
            rows.extend(seed_rows)
        except (ValueError, RuntimeError, FloatingPointError) as error:
            failures.append(dict(seed=seed, error=str(error)))
        print(f'seed {seed}: {"failed" if failures and failures[-1]["seed"] == seed else "recorded"}', flush=True)
    with (output / 'scores.csv').open('w') as stream:
        writer = csv.DictWriter(stream, ['seed', 'segment', 'metric', 'overlap_spearman', 'same_diet_pair_auc', 'single_linkage_guild_auc'])
        writer.writeheader(); writer.writerows(rows)
    summaries = {}
    for metric in ('correlation', 'absolute_correlation', 'cpsd', 'coherence'):
        subset = [r for r in rows if r['metric'] == metric and r['segment'] == 30]
        if subset:
            summaries[metric] = {key: interval([r[key] for r in subset])
                                for key in ('overlap_spearman', 'same_diet_pair_auc', 'single_linkage_guild_auc')}
    report = dict(status='pilot; not a paper-figure reproduction or milestone acceptance',
                  versions=dict(numpy=np.__version__, scipy=scipy.__version__),
                  attempted_seeds=list(seeds), failures=failures, duration=duration, burn=burn, drive_spacing=drive_spacing, sample_interval=1.0,
                  summaries=summaries, convergence=convergence, input_diagnostics=diagnostics)
    (output / 'report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('/tmp/nutrient-reference'))
    parser.add_argument('--seeds', type=int, default=4)
    parser.add_argument('--duration', type=int, default=1536)
    parser.add_argument('--burn', type=int, default=512)
    parser.add_argument('--drive-spacing', type=float, default=.25)
    args = parser.parse_args()
    if args.seeds < 1:
        parser.error('--seeds must be positive')
    run(args.output, range(args.seeds), args.duration, args.burn, args.drive_spacing)
    from linear_reference import verify
    linear = [verify(seed) for seed in range(args.seeds)]
    (args.output / 'linear.json').write_text(json.dumps(linear, indent=2) + '\n')
