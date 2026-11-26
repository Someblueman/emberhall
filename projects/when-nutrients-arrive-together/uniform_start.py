"""Uniform deterministic starting-box bounds for a Gaussian linear model."""
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
from transient_law import gaussian_bounds


def box_norm(center, matrix, radii):
    """Upper envelope of max_{|z|<=r} ||center+matrix*z||, plus feasible corners."""
    c=np.asarray(center,float);a=np.asarray(matrix,float);r=np.asarray(radii,float)
    if (c.ndim!=1 or a.ndim!=2 or a.shape[0]!=len(c) or r.shape!=(a.shape[1],)
        or not all(np.isfinite(v).all() for v in (c,a,r)) or np.any(r<0)):
        raise ValueError('finite compatible center/map and nonnegative radii required')
    a=a[:,r>0]*r[r>0]
    if not np.isfinite(a).all():raise ValueError("nonfinite scaled box map")
    if not a.shape[1]:
        value=float(np.linalg.norm(c))
        if not np.isfinite(value):raise ValueError("nonfinite point norm")
        return dict(upper=value,lower=value,triangle=value,spectral=value,coordinate=value,gram=value)
    norm=float(np.linalg.norm(c))
    gram=a.T@a;cross=a.T@c
    bounds=dict(triangle=norm+float(np.linalg.norm(a,axis=0).sum()),
                spectral=norm+float(np.sqrt(a.shape[1])*np.linalg.norm(a,2)),
                coordinate=float(np.linalg.norm(abs(c)+abs(a).sum(axis=1))),
                gram=float(np.sqrt(c@c+2*abs(cross).sum()+abs(gram).sum())))
    if not np.isfinite(list(bounds.values())).all():raise ValueError("nonfinite computed box envelope")
    lower=0.
    starts=[np.ones(a.shape[1]),-np.ones(a.shape[1]),np.where(cross<0,-1.,1.)]
    for z in starts:
        for _ in range(20):
            changed=False
            for j in range(len(z)):
                field=cross[j]+gram[j]@z-gram[j,j]*z[j]
                new=1. if field>0 else -1. if field<0 else z[j]
                changed|=new!=z[j];z[j]=new
            if not changed:break
        lower=max(lower,float(np.linalg.norm(c+a@z)))
    upper=min(bounds.values())
    if lower>upper+1e-11*max(1.,upper):raise ValueError('feasible corner exceeds computed envelope')
    return dict(upper=upper,lower=lower,**bounds)


def box_gaussian_bounds(p,d,center,matrix,radii):
    """Uniform Gaussian TV upper bounds over this deterministic mean box.

    Every mean shares covariance P+D. Positive definiteness is required.
    This is a numerical evaluation of exact-matrix formulas, not interval arithmetic.
    """
    p=np.asarray(p,float);d=np.asarray(d,float)
    covariance=gaussian_bounds(p,np.zeros(len(p)),d)
    factor=np.linalg.cholesky((p+p.T)/2)
    c=solve_triangular(factor,np.asarray(center,float),lower=True)
    a=solve_triangular(factor,np.asarray(matrix,float),lower=True)
    envelope=box_norm(c,a,radii)
    left=solve_triangular(factor,d,lower=True)
    e=solve_triangular(factor,left.T,lower=True).T
    values,vectors=np.linalg.eigh((e+e.T)/2)
    transform=vectors.T/np.sqrt(1+values[:,None]/2)
    affinity_envelope=box_norm(transform@c,transform@a,radii)
    kl=covariance['kl']+.5*envelope['upper']**2
    affinity=covariance['negative_log_affinity']+.125*affinity_envelope['upper']**2
    pinsker=min(1.,float(np.sqrt(kl/2)))
    hellinger=float(np.sqrt(-np.expm1(-2*affinity)))
    return dict(tv_upper=min(pinsker,hellinger),kl_upper=kl,negative_log_affinity_upper=affinity,
                pinsker_upper=pinsker,affinity_upper=hellinger,
                mean_norm_upper=envelope['upper'],mean_norm_lower=envelope['lower'],
                affinity_mean_norm_upper=affinity_envelope['upper'],
                **{'mean_'+k:v for k,v in envelope.items() if k not in ('upper','lower')})


def conditioned_comparison(distance_upper, stationary_success_lower):
    """Common-event conditional TV bound, given an independently justified floor.

    The final division is rounded upward and success subtraction downward for
    supplied float inputs. This does not certify how those inputs were obtained.
    This does not estimate success probabilities or compare different filters.
    A zero transient success probability must not define a conditional score law.
    """
    delta,p=float(distance_upper),float(stationary_success_lower)
    if not np.isfinite([delta,p]).all() or not 0<=delta<=1 or not 0<=p<=1:
        raise ValueError('distance and success floor must lie in [0,1]')
    success=max(0.,float(np.nextafter(p-delta,-np.inf))) if delta else p
    upper=(min(1.,float(np.nextafter(delta/p,np.inf))) if delta else 0.) if p>delta else 1.
    return dict(tv_upper=upper,
                transient_success_lower=success,
                guarantees_positive_transient_success=p>delta)


def initial_box(consumer_equilibrium, resource_equilibrium):
    """Mean box for physical ecological starts [.5,2], stationary zero-mean OU.

    Consumers are LOG amounts, resources are unlogged amount differences.
    """
    x=np.asarray(consumer_equilibrium,float);resources=np.asarray(resource_equilibrium,float)
    if (x.ndim!=1 or resources.ndim!=1 or not len(x) or not len(resources)
        or not np.isfinite(x).all() or not np.isfinite(resources).all() or np.any(x<=0)):
        raise ValueError('finite equilibrium vectors and positive consumers required')
    center=np.r_[-np.log(x),1.25-resources,np.zeros(len(resources))]
    radii=np.r_[np.full(len(x),np.log(2.)),np.full(len(resources),.75)]
    return center,radii


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    config=dict(seeds=list(range(4,16)),burns=[0,16,32,64,128,512],initial_amount_bounds=[.5,2.],
                scope='uniform pointwise deterministic initial-mean family, supplied Gaussian linear model only',
                numpy=np.__version__,scipy=scipy.__version__,
                construction_sha256=hashlib.sha256(Path(__file__).with_name('UNIFORM_START.md').read_text().split('\n## Results\n')[0].encode()).hexdigest(),
                code_sha256={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                             for name in ['uniform_start.py','transient_law.py',
                                          'linear_calibration.py','linear_reference.py','reference.py']})
    encoded=json.dumps(config,indent=2,sort_keys=True)+'\n'
    target=output/'protocol.json'
    if target.exists() and target.read_text()!=encoded:raise ValueError('different frozen protocol')
    target.write_text(encoded)
    rows=[]
    for seed in config['seeds']:
        f,p,_,_=setup(seed)
        r,g,_=community(seed)
        x,resources=equilibrium(r,g,np.r_[np.ones(24),np.full(6,3.)])
        center,radii=initial_box(x,resources)
        initial=np.zeros_like(p);initial[36:,36:]=.005*np.eye(30)
        identity=hashlib.sha256(b''.join(a.astype('<f8').tobytes() for a in [f,p,center,radii])).hexdigest()
        for burn in config['burns']:
            row=dict(seed=seed,burn=burn,status='success',reason='',input_sha256=identity)
            if burn==0:row.update(status='singular',reason='deterministic ecological start',tv_upper=1.)
            else:
                power=np.linalg.matrix_power(f,burn)
                try:row.update(box_gaussian_bounds(p,power@(initial-p)@power.T,power@center,power[:,:36],radii))
                except (ValueError,np.linalg.LinAlgError) as error:
                    row.update(status='failure',reason=str(error),tv_upper=1.)
            rows.append(row)
        print('uniform start',seed,flush=True)
    fields=list(dict.fromkeys(k for row in rows for k in row))
    target=output/'summary.csv'
    with target.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    print('cases',len(rows),'sha256',hashlib.sha256(target.read_bytes()).hexdigest())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
