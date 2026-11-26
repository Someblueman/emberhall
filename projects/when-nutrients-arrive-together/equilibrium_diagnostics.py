"""Local-linear diagnostics, not a stationary-law certificate for the nonlinear model."""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from reference import PAIRS, auc, community, single_linkage_scores, simulate
from linear_reference import equilibrium, linear_system, stationary, spectrum


def diagnose(seed, transient=False):
    uptake, gain, labels = community(seed)
    base = np.r_[np.ones(24), np.full(6, 3)]
    x, resources = equilibrium(uptake, gain, base)
    j, b = linear_system(uptake, gain, x, resources)
    covariance, residual = stationary(j, b)
    correlation = covariance / np.sqrt(np.outer(np.diag(covariance), np.diag(covariance)))
    overlap = (gain @ gain.T)[PAIRS]
    same = (labels[:, None] == labels)[PAIRS]
    scores = {}
    for name, values in [('correlation', correlation[PAIRS]),
                         ('absolute_correlation', np.abs(correlation[PAIRS]))]:
        scores[name] = dict(overlap_spearman=float(spearmanr(values, overlap).statistic),
                           same_diet_pair_auc=auc(same, values),
                           single_linkage_guild_auc=auc(same, single_linkage_scores(values)))
    result = dict(community=seed, slowest_linear_relaxation_time=float(-1/np.max(np.linalg.eigvals(j).real)),
                  integrated_linear_correlation_times=(np.diag(spectrum(0,j,b)).real
                                                       / (2*np.diag(covariance))).tolist(),
                  lyapunov_residual=residual, population_linear_scores=scores)
    if transient:
        trajectory, _ = simulate(uptake, gain, np.repeat(base[None,:], 4097, axis=0),
                                 .25, 1024, 512, .25, 1e-9)
        result['constant_supply_max_log_distance_after_512'] = float(
            np.max(np.abs(trajectory - np.log(x))))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--communities', type=int, default=12)
    parser.add_argument('--transient', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.communities < 1:
        parser.error('need at least one community')
    records = []
    for seed in range(args.communities):
        try:
            records.append(diagnose(seed, args.transient))
        except (ValueError, RuntimeError, FloatingPointError) as error:
            records.append(dict(community=seed, failure=str(error)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(status=__doc__, records=records), indent=2, allow_nan=False)+'\n')
