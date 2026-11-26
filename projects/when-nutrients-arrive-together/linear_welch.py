"""Infinite-record expected Welch spectra for the stationary local-linear model.

Fixed segment length, window and detrending match reference.measures. Ratio of
expected spectra is NOT expectation of finite-record sample coherence.
"""
import json
from pathlib import Path
import numpy as np
from scipy.linalg import expm, solve_continuous_lyapunov
from scipy.signal import get_window
from scipy.stats import spearmanr

from reference import community, PAIRS, auc, single_linkage_scores
from linear_reference import equilibrium, linear_system


def expected_spectra(lags, segment):
    """lags[l] = Cov(Y(t+l),Y(t)); unit sampling and stationary Y."""
    if len(lags) < segment:
        raise ValueError('need every lag within one segment')
    covariance = np.array([[lags[t-u] if t >= u else lags[u-t].T
                            for u in range(segment)] for t in range(segment)])
    window = get_window('hann', segment, fftbins=True)
    vector = np.exp(-2j*np.pi*np.arange(segment//2+1)[:, None]
                    *np.arange(segment)[None, :]/segment)*window
    vector -= vector.mean(axis=1, keepdims=True)  # constant detrend before window
    spectrum = np.einsum('ft,fu,tuij->fij', vector.conj(), vector, covariance,
                         optimize=True)/np.sum(window**2)
    spectrum[1:-1 if segment % 2 == 0 else None] *= 2
    return spectrum


def predictions(seed, segment=30):
    uptake, gain, labels = community(seed)
    x, resources = equilibrium(uptake, gain, np.r_[np.ones(24), np.full(6, 3)])
    j,b = linear_system(uptake, gain, x, resources)
    a = np.block([[j,b],[np.zeros((30,36)), -np.eye(30)]])
    if np.max(np.linalg.eigvals(a).real) >= 0:
        raise ValueError('unstable equilibrium')
    diffusion = np.zeros_like(a)
    diffusion[36:,36:] = .01*np.eye(30)
    p = solve_continuous_lyapunov(a, -diffusion)
    transition = expm(a)
    lags, power = [], np.eye(len(a))
    scales = np.sqrt(np.diag(p)[:6])
    for lag in range(segment):
        lags.append((power@p)[:6,:6]/scales[:,None]/scales[None,:])
        power = transition@power
    spectra = expected_spectra(lags, segment)
    autos = np.diagonal(spectra, axis1=1, axis2=2).real
    cross = spectra[:, PAIRS[0], PAIRS[1]]
    coherence = np.abs(cross)**2/(autos[:,PAIRS[0]]*autos[:,PAIRS[1]])
    correlation = lags[0][PAIRS]
    values = dict(correlation=correlation, absolute_correlation=np.abs(correlation),
                  cpsd=np.abs(cross).sum(0)/segment,
                  coherence=coherence.sum(0)/segment)
    same = (labels[:,None] == labels)[PAIRS]
    overlap = (gain@gain.T)[PAIRS]
    scores = {m: dict(overlap_spearman=float(spearmanr(v,overlap).statistic),
                      same_diet_pair_auc=auc(same,v),
                      single_linkage_guild_auc=auc(same,single_linkage_scores(v)))
              for m,v in values.items()}
    return dict(seed=seed, segment=segment, scores=scores,
                pair_measures={m:v.tolist() for m,v in values.items()},
                caveat='Stationary local linear process, infinite number of fixed-size Welch segments; not finite-record expected coherence, nonlinear law, or a source-figure reproduction.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    records=[predictions(seed) for seed in range(4,16)]
    args.output.write_text(json.dumps(records,indent=2,allow_nan=False)+'\n')
    for metric in ('correlation','absolute_correlation','cpsd','coherence'):
        print(metric, {k:round(float(np.mean([r['scores'][metric][k] for r in records])),5)
                       for k in records[0]['scores'][metric]})
