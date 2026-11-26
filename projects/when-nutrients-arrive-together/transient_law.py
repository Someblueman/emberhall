"""Gaussian starting-law bounds, propagated to every future record by a kernel."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import solve_triangular

from linear_calibration import setup
from linear_reference import equilibrium
from reference import community


def _log_gap(values):
    """x-log1p(x), avoiding loss of relative accuracy near zero."""
    values=np.asarray(values,float)
    result=values-np.log1p(values)
    near=abs(values)<.01
    x=values[near]
    result[near]=sum((-1.)**k*x**k/k for k in range(2,12))
    return result


def _affinity_gap(values):
    """.5 log1p(x/2)-.25 log1p(x), nonnegative and stable near zero."""
    values=np.asarray(values,float)
    result=.5*np.log1p(values/2)-.25*np.log1p(values)
    near=abs(values)<.01
    x=values[near]
    result[near]=sum((-1.)**(k+1)*(.5/2**k-.25)*x**k/k for k in range(2,12))
    return result


def gaussian_bounds(stationary_covariance, mean, covariance_difference):
    """Bounds on TV(N(mean,P+D), N(0,P)); require both covariances PD.

    D is supplied separately so tiny transient corrections are not erased by
    first adding them to P. This is floating arithmetic, not interval arithmetic.
    """
    p=np.asarray(stationary_covariance,float)
    d=np.asarray(covariance_difference,float)
    m=np.asarray(mean,float)
    if (p.ndim!=2 or p.shape[0]!=p.shape[1] or d.shape!=p.shape or m.shape!=(len(p),)
        or not all(np.isfinite(a).all() for a in (p,d,m))
        or not np.allclose(p,p.T,rtol=1e-12,atol=1e-14)
        or not np.allclose(d,d.T,rtol=1e-12,atol=1e-14)):
        raise ValueError('finite symmetric covariance matrices and compatible mean required')
    factor=np.linalg.cholesky((p+p.T)/2)
    h=solve_triangular(factor,m,lower=True)
    left=solve_triangular(factor,d,lower=True)
    e=solve_triangular(factor,left.T,lower=True).T
    values,vectors=np.linalg.eigh((e+e.T)/2)
    if np.min(values)<=-1:
        raise ValueError('transient covariance not numerically positive definite')
    covariance_kl=float(np.sum(_log_gap(values)))
    norm=float(h@h)
    kl=.5*(covariance_kl+norm)
    rotated=vectors.T@h
    negative_log_affinity=float(np.sum(_affinity_gap(values))+.125*np.sum(rotated**2/(1+values/2)))
    if min(kl,negative_log_affinity)<0:
        raise ValueError('negative Gaussian divergence from numerical cancellation')
    pinsker=min(1.,float(np.sqrt(kl/2)))
    hellinger=float(np.sqrt(-np.expm1(-2*negative_log_affinity)))
    return dict(tv_upper=min(pinsker,hellinger),pinsker_upper=pinsker,
                affinity_upper=hellinger,kl=kl,negative_log_affinity=negative_log_affinity,
                whitened_mean_norm=float(np.sqrt(norm)),
                relative_covariance_min=float(values.min()),relative_covariance_max=float(values.max()))


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    config=dict(seeds=list(range(4,16)),burns=[0,16,32,64,128,512],
                starts=['equilibrium','baseline-tangent'],
                scope='full-state Gaussian starting-law distance; covers every finite future statistic in the supplied linear model',
                numpy=np.__version__,scipy=scipy.__version__,
                code_sha256={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                             for name in ['transient_law.py','TRANSIENT_LAW.md','linear_calibration.py','linear_reference.py','reference.py']})
    encoded=json.dumps(config,indent=2,sort_keys=True)+'\n'
    target=output/'protocol.json'
    if target.exists() and target.read_text()!=encoded:raise ValueError('different frozen protocol')
    target.write_text(encoded)
    rows=[]
    for seed in config['seeds']:
        f,p,_,_=setup(seed)
        r,g,_=community(seed)
        x,resources=equilibrium(r,g,np.r_[np.ones(24),np.full(6,3.)])
        initial=np.zeros_like(p);initial[36:,36:]=.005*np.eye(30)
        for start in config['starts']:
            m=np.zeros(len(f))
            if start=='baseline-tangent':m[:6]=-np.log(x);m[6:36]=1-resources
            for burn in config['burns']:
                row=dict(seed=seed,start=start,burn=burn,status='success',reason='')
                if burn==0:
                    row.update(status='singular',reason='deterministic ecological state versus full Gaussian density',
                               **{k:None for k in ['pinsker_upper','affinity_upper','kl','negative_log_affinity','whitened_mean_norm','relative_covariance_min','relative_covariance_max']},tv_upper=1.)
                else:
                    power=np.linalg.matrix_power(f,burn)
                    try:row.update(gaussian_bounds(p,power@m,power@(initial-p)@power.T))
                    except (ValueError,np.linalg.LinAlgError) as error:
                        row.update(status='failure',reason=str(error),tv_upper=1.)
                rows.append(row)
        print('starting law',seed,flush=True)
    fields=list(dict.fromkeys(k for row in rows for k in row))
    target=output/'summary.csv'
    with target.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    print('cases',len(rows),'summary sha256',hashlib.sha256(target.read_bytes()).hexdigest())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
