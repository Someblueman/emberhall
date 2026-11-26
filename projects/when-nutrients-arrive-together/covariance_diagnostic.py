"""Separate within-half covariance and differing sample means, without a stationarity claim."""
import argparse
import csv
import hashlib
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from reference import PAIRS
from summarize_length import load


def decompose(x):
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or len(x) < 4 or not np.isfinite(x).all():
        raise ValueError('finite matrix with at least four observations required')
    a, b = np.array_split(x, 2)
    p = len(a) / len(x)
    centered = x - x.mean(axis=0)
    ca, cb = a - a.mean(axis=0), b - b.mean(axis=0)
    full = centered.T @ centered / len(x)
    within = p * (ca.T @ ca / len(a)) + (1-p) * (cb.T @ cb / len(b))
    delta = a.mean(axis=0) - b.mean(axis=0)
    between = p * (1-p) * np.outer(delta, delta)
    return full, within, between, delta


def rank(covariance, overlap):
    if not np.isfinite(covariance).all() or not np.isfinite(overlap).all():
        raise ValueError('finite covariance and overlap required')
    deviations = np.sqrt(np.diag(covariance))
    if np.any(deviations <= 0):
        raise ValueError('positive consumer variances required')
    correlations = covariance / np.outer(deviations, deviations)
    if np.ptp(correlations[PAIRS]) == 0 or np.ptp(overlap) == 0:
        raise ValueError('rank comparison needs nonconstant pair values')
    return float(spearmanr(correlations[PAIRS], overlap).statistic)


def diagnose(partitions, output):
    receipts, _ = load(partitions)
    rows = []
    for directory in partitions:
        for path in sorted(directory.glob('seed-*.npz')):
            seed = int(path.stem.split('-')[1])
            with np.load(path) as data:
                x, gain = data['log_x'], data['gain']
            if x.shape != (20000, 6) or gain.shape != (6, 30) or not np.isfinite(gain).all():
                raise ValueError('unexpected development trajectory shape')
            full, within, between, delta = decompose(x)
            error = float(np.max(np.abs(full - within - between)))
            relative_error = error / float(np.max(np.abs(full)))
            if relative_error > 1e-10:
                raise ValueError('covariance decomposition failed')
            overlap = (gain @ gain.T)[PAIRS]
            a = x[:len(x)//2]
            centered = a - a.mean(axis=0)
            first = centered.T @ centered / len(a)
            full_rank, within_rank = rank(full, overlap), rank(within, overlap)
            first_rank = rank(first, overlap)
            scores = receipts[seed]['scores']
            if (abs(full_rank-scores['20000']['correlation']['overlap_spearman']) > 1e-12
                    or abs(first_rank-scores['10000']['correlation']['overlap_spearman']) > 1e-12):
                raise ValueError('trajectory and score receipt disagree')
            rows.append(dict(seed=seed, observations=len(x),
                log_abundance_sha256=hashlib.sha256(x.tobytes()).hexdigest(),
                covariance_relative_residual=relative_error,
                first_half_rank=first_rank, full_rank=full_rank,
                within_half_rank=within_rank,
                full_minus_within_rank=full_rank-within_rank,
                mean_between_variance_fraction=float(np.mean(np.diag(between)/np.diag(full))),
                maximum_standardized_mean_shift=float(np.max(np.abs(delta)/np.sqrt(np.diag(full))))))
    if sorted(r['seed'] for r in rows) != list(range(8, 16)):
        raise ValueError('exactly communities 8–15 are required; no duplicates or omissions')
    with output.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: r['seed']))
    print(f'Wrote {len(rows)} exact covariance diagnostics.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('partitions', nargs='+', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    diagnose(args.partitions, args.output)
