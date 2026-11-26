"""Exact Gaussian finite-record covariance moments and conservative score envelopes.

These are stationary local-linear model bounds, not nonlinear ecological bounds.
No normal approximation, independent-time assumption, or new sampled path is used.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import linear_sum_assignment
from scipy.stats import rankdata

from linear_calibration import setup
from reference import PAIRS, community, single_linkage_scores


def lag_covariances(transition, covariance, count, observed=6):
    """Return L[k] = Cov(Y(t+k), Y(t)); compute every requested lag."""
    if type(count) is not int or count < 2 or not 1 <= observed <= len(covariance):
        raise ValueError('need at least two observations and valid observed dimension')
    rows = np.eye(len(covariance))[:observed]
    lags = np.empty((count, observed, observed))
    for k in range(count):
        lags[k] = rows @ covariance[:, :observed]
        rows = rows @ transition
    return lags


def centered_moments(lags):
    """Mean and entrywise variance of S = Y.T H Y / N for zero-mean Gaussian Y.

    Accepts nonsymmetric positive-lag covariance matrices. Does not assume
    time reversibility. Storage is O(N*d*d), not a dense Nd by Nd matrix.
    """
    lags = np.asarray(lags, dtype=float)
    n, d, other = lags.shape
    if n < 2 or d != other or not np.isfinite(lags).all():
        raise ValueError('need finite square lag matrices and at least two times')
    if not np.allclose(lags[0], lags[0].T, rtol=1e-12, atol=1e-14):
        raise ValueError('zero-lag covariance must be symmetric')
    # Row sums of the time covariance block T_ij, with its two lag orientations.
    cumulative = np.cumsum(lags[1:], axis=0)
    before = np.concatenate((np.zeros((1,d,d)), cumulative))
    row_sums = lags[0] + before + before[::-1].transpose(0,2,1)
    totals = row_sums.sum(axis=0)
    mean = lags[0] - totals / n**2
    weights = (n - np.arange(n))[1:]
    variance = np.empty((d,d))
    for i in range(d):
        for j in range(d):
            # Wick: Var(S_ij) = [tr(H T_ii H T_jj) + tr(H T_ij H T_ij)] / N².
            first = n*lags[0,i,i]*lags[0,j,j]
            first += 2*np.dot(weights, lags[1:,i,i]*lags[1:,j,j])
            first -= 2*np.dot(row_sums[:,i,i], row_sums[:,j,j])/n
            first += totals[i,i]*totals[j,j]/n**2
            second = n*lags[0,i,j]**2
            second += 2*np.dot(weights, lags[1:,i,j]*lags[1:,j,i])
            second -= 2*np.dot(row_sums[:,i,j], row_sums[:,j,i])/n
            second += totals[i,j]**2/n**2
            variance[i,j] = (first+second)/n**2
    scale = max(float(np.max(np.abs(variance))), np.finfo(float).tiny)
    if variance.min() < -1e-10*scale:
        raise ValueError('negative covariance variance beyond roundoff')
    return mean, np.maximum(variance, 0)


def quadratic_operator_bounds(lags):
    """Upper bounds on ||Sigma^(1/2) A_ij Sigma^(1/2)|| for S_ij.

    Use only the one- or two-species marginal needed by each entry. The
    symmetric temporal covariance operator norm is at most its maximum
    absolute row sum; ||H||=1, and the off-diagonal quadratic weight has
    norm 1/(2N), versus 1/N for a diagonal entry.
    """
    n,d,_=lags.shape
    absolute=np.abs(lags)
    before=np.concatenate((np.zeros((1,d,d)),np.cumsum(absolute[1:],axis=0)))
    row_sums=absolute[0]+before+before[::-1].transpose(0,2,1)
    bounds=np.empty((d,d))
    for i in range(d):
        bounds[i,i]=np.max(row_sums[:,i,i])/n
        for j in range(i+1,d):
            norm=max(np.max(row_sums[:,i,i]+row_sums[:,i,j]),
                     np.max(row_sums[:,j,i]+row_sums[:,j,j]))
            bounds[i,j]=bounds[j,i]=norm/(2*n)
    return bounds


def correlation_envelope(population, mean, variance, alpha=.05, operator_bounds=None):
    """Fixed envelope containing all sample correlations with probability >=1-alpha.

    Chebyshev, or Gaussian quadratic concentration when an operator bound
    is supplied, plus union bound over d(d+1)/2 centered covariance entries.
    Inflate by the exact mean-centering bias to center on population covariance.
    A nonpositive variance lower bound returns the full correlation range.
    """
    if not 0 < alpha < 1:
        raise ValueError('alpha must lie strictly between zero and one')
    d = len(population)
    entries = d*(d+1)//2
    if operator_bounds is None:
        radius = np.sqrt(entries*variance/alpha)
    else:
        # Gaussian quadratic-form Bernstein bound; see FINITE_COVARIANCE.md.
        t=np.log(2*entries/alpha)
        radius=np.sqrt(2*variance*t)+2*operator_bounds*t
    radius += np.abs(mean-population)
    lo, hi = population-radius, population+radius
    lower, upper = [], []
    for i,j in zip(*np.triu_indices(d,1)):
        if lo[i,i] <= 0 or lo[j,j] <= 0:
            lower.append(-1.); upper.append(1.); continue
        denominators = np.sqrt([lo[i,i]*lo[j,j], hi[i,i]*hi[j,j]])
        candidates = np.array([lo[i,j],hi[i,j]])[:,None]/denominators
        lower.append(max(-1.,float(candidates.min())))
        upper.append(min(1.,float(candidates.max())))
    return np.array(lower),np.array(upper),radius


def absolute_envelope(lower, upper):
    return np.where((lower<=0)&(upper>=0),0,np.minimum(abs(lower),abs(upper))), np.maximum(abs(lower),abs(upper))


def auc_envelope(labels, lower, upper):
    """Enclose every Mann-Whitney AUC attainable inside the score intervals."""
    labels = np.asarray(labels,dtype=bool)
    if not labels.any() or labels.all():
        raise ValueError('AUC needs both classes')
    low = lower[labels,None] - upper[None,~labels]
    high = upper[labels,None] - lower[None,~labels]
    return [float(np.mean((low>0)+.5*(low==0))),
            float(np.mean((high>0)+.5*(high==0)))]


def spearman_envelope(target, lower, upper):
    """Bound no-tie score ranks by a relaxed minimum/maximum assignment.

    Gaussian sample correlations/absolute correlations have no exact ties
    almost surely for the nonsingular six-species model with N>=6. Target
    ties are allowed. This helper is not for the tied single-linkage closure.
    """
    m=len(lower)
    target=rankdata(target)-.5*(m+1)
    denominator=np.linalg.norm(target)*np.sqrt(m*(m*m-1)/12)
    if denominator==0:
        raise ValueError('constant rank target')
    lowest=1+np.sum(upper[None,:]<lower[:,None],axis=1)
    highest=m-np.sum(lower[None,:]>upper[:,None],axis=1)
    ranks=np.arange(1,m+1)
    allowed=(ranks[None,:]>=lowest[:,None])&(ranks[None,:]<=highest[:,None])
    cost=target[:,None]*ranks[None,:]
    bounds=[]
    for direction in (1,-1):
        rows,cols=linear_sum_assignment(np.where(allowed,direction*cost,np.inf))
        bounds.append(float(cost[rows,cols].sum()/denominator))
    return bounds


def score_envelopes(labels, lower, upper, overlap=None):
    same = (labels[:,None]==labels)[PAIRS]
    a,b = np.triu_indices(len(lower),1)
    ordered = (lower[a]>upper[b]) | (lower[b]>upper[a])
    result=dict(certified_pair_orders=int(ordered.sum()),total_pair_orders=len(a),
                same_diet_pair_auc=auc_envelope(same,lower,upper),
                single_linkage_guild_auc=auc_envelope(same,single_linkage_scores(lower),single_linkage_scores(upper)))
    if overlap is not None:
        result['overlap_spearman']=spearman_envelope(overlap,lower,upper)
    return result


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    config = dict(seeds=list(range(4,16)),windows=[4096,20000,65536,131072],alpha=.05,
                  bounds=['chebyshev','gaussian-quadratic','gaussian-studywise'],
                  scope='first two marginal per community/window; last joint over 12 communities and four windows; all joint over covariance entries and derived correlation scores',
                  model='exact stationary local-linear Gaussian; no nonlinear or source-replication guarantee',
                  numpy=np.__version__,scipy=scipy.__version__,
                  code_sha256={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                               for name in ('finite_covariance.py','linear_calibration.py','linear_reference.py','reference.py')})
    encoded=json.dumps(config,indent=2,sort_keys=True)+'\n'
    protocol=output/'protocol.json'
    if protocol.exists() and protocol.read_text()!=encoded:
        raise ValueError('different finite-covariance protocol')
    protocol.write_text(encoded)
    records=[]
    for seed in config['seeds']:
        receipt=output/f'seed-{seed}.json'
        if receipt.exists():
            saved=json.loads(receipt.read_text())
            if saved['seed']!=seed or saved['status']!='success':
                raise ValueError('failed or mismatched receipt retained; inspect before continuing')
            records.extend(saved['records']);continue
        transition,p,_,labels=setup(seed)
        _,gain,_=community(seed)
        overlap=(gain@gain.T)[PAIRS]
        # Normalize before moment arithmetic; correlations are invariant to this.
        lags=lag_covariances(transition,p,max(config['windows']))
        scales=np.sqrt(np.diag(lags[0]))
        lags/=scales[None,:,None]*scales[None,None,:]
        community_records=[]
        for n in config['windows']:
            mean,var=centered_moments(lags[:n])
            operators=quadratic_operator_bounds(lags[:n])
            for bound in config['bounds']:
                alpha=config['alpha']
                if bound=='gaussian-studywise':
                    alpha/=len(config['seeds'])*len(config['windows'])
                lower,upper,radius=correlation_envelope(lags[0],mean,var,alpha,
                    operators if bound!='chebyshev' else None)
                for metric,(lo,hi) in dict(correlation=(lower,upper),absolute_correlation=absolute_envelope(lower,upper)).items():
                    community_records.append(dict(seed=seed,observations=n,metric=metric,bound=bound,
                        maximum_covariance_bias=float(np.max(np.abs(mean-lags[0]))),
                        maximum_covariance_sd=float(np.sqrt(var.max())),
                        maximum_correlation_width=float(np.max(hi-lo)),
                        **score_envelopes(labels,lo,hi,overlap)))
        receipt.write_text(json.dumps(dict(seed=seed,status='success',records=community_records),indent=2,allow_nan=False)+'\n')
        records.extend(community_records)
        print('finite covariance',seed,flush=True)
    rows=[]
    for n in config['windows']:
        for bound in config['bounds']:
          for metric in ('correlation','absolute_correlation'):
            group=[r for r in records if r['observations']==n and r['metric']==metric and r['bound']==bound]
            rows.append(dict(observations=n,metric=metric,bound=bound,communities=len(group),
                mean_certified_pair_orders=float(np.mean([r['certified_pair_orders'] for r in group])),
                minimum_certified_pair_orders=min(r['certified_pair_orders'] for r in group),
                maximum_covariance_bias=max(r['maximum_covariance_bias'] for r in group),
                maximum_covariance_sd=max(r['maximum_covariance_sd'] for r in group),
                mean_rank_lower=float(np.mean([r['overlap_spearman'][0] for r in group])),
                mean_rank_upper=float(np.mean([r['overlap_spearman'][1] for r in group])),
                mean_pair_auc_lower=float(np.mean([r['same_diet_pair_auc'][0] for r in group])),
                mean_guild_auc_lower=float(np.mean([r['single_linkage_guild_auc'][0] for r in group]))))
    with (output/'summary.csv').open('w') as stream:
        writer=csv.DictWriter(stream,list(rows[0]));writer.writeheader();writer.writerows(rows)
    return records


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
