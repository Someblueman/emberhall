"""Exact stationary sampled-linear calibration of fixed-segment predictions.

This samples Gaussian perturbations, not positive nonlinear populations.
No forcing interpolation, ODE stepping or burn-in is involved.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.linalg import expm, solve_continuous_lyapunov

from reference import community, score, interval
from linear_reference import equilibrium, linear_system
from linear_welch import predictions
from convergence import METRICS, TARGETS


def covariance_factor(matrix):
    symmetric=(matrix+matrix.T)/2
    values,vectors=np.linalg.eigh(symmetric)
    scale=max(float(np.max(np.abs(values))),1e-30)
    if values.min() < -1e-9*scale:
        raise ValueError('covariance is materially indefinite')
    # Report roundoff truncation explicitly; never repair an indefinite model.
    return vectors*np.sqrt(np.maximum(values,0)), float(values.min()/scale)


def stationary_sample(transition, covariance, seed, count):
    initial,minimum_initial=covariance_factor(covariance)
    noise=covariance-transition@covariance@transition.T
    factor,minimum_innovation=covariance_factor(noise)
    rng=np.random.default_rng(seed)
    state=initial@rng.normal(size=len(covariance))
    innovations=rng.normal(size=(count-1,len(covariance)))@factor.T
    samples=np.empty((count,6 if len(covariance)>=6 else len(covariance)))
    samples[0]=state[:samples.shape[1]]
    for index,innovation in enumerate(innovations,1):
        state=transition@state+innovation
        samples[index]=state[:samples.shape[1]]
    return samples,dict(initial_min_relative_eigenvalue=minimum_initial,
                        innovation_min_relative_eigenvalue=minimum_innovation,
                        transition_covariance_residual=float(np.max(np.abs(
                            transition@covariance@transition.T+factor@factor.T-covariance))))


def setup(seed):
    uptake,gain,labels=community(seed)
    x,resources=equilibrium(uptake,gain,np.r_[np.ones(24),np.full(6,3)])
    j,b=linear_system(uptake,gain,x,resources)
    a=np.block([[j,b],[np.zeros((30,36)),-np.eye(30)]])
    if np.max(np.linalg.eigvals(a).real)>=0:
        raise ValueError('unstable local linear system')
    diffusion=np.zeros_like(a); diffusion[36:,36:]=.01*np.eye(30)
    p=solve_continuous_lyapunov(a,-diffusion)
    return expm(a),p,gain,labels


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    config=dict(seeds=list(range(4,16)),paths=4,count=131072,
                windows=[2048,4096,20000,131072],input_seed='50000 + 100*community + path',
                segment=30, purpose='calibrate estimator finite-length effects in exact stationary linear samples; no nonlinear baseline acceptance',
                code_sha256={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                             for name in ('linear_calibration.py','linear_welch.py','linear_reference.py','reference.py')})
    encoded=json.dumps(config,indent=2,sort_keys=True)+'\n'
    protocol=output/'protocol.json'
    if protocol.exists() and protocol.read_text()!=encoded:
        raise ValueError('different calibration protocol')
    protocol.write_text(encoded)
    records=[]
    for seed in config['seeds']:
        receipt=output/f'seed-{seed}.json'
        if receipt.exists():
            records.append(json.loads(receipt.read_text())); continue
        record=dict(seed=seed,paths=[])
        transition,p,gain,labels=setup(seed)
        record['prediction']=predictions(seed)['scores']
        for path in range(4):
            entry=dict(path=path,status='failure')
            try:
                x,diagnostics=stationary_sample(transition,p,50000+100*seed+path,131072)
                entry.update(status='success',diagnostics=diagnostics,
                             scores={str(n):score(x[:n],gain,labels) for n in config['windows']},
                             maximum_covariance_error=float(np.max(np.abs(np.cov(x.T,bias=True)-p[:6,:6]))))
            except (ValueError,RuntimeError,FloatingPointError) as error:
                entry['error']=str(error)
            record['paths'].append(entry)
        receipt.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
        records.append(record)
        print('linear calibration',seed, 'paths',len(record['paths']),flush=True)
    summary=[]
    for n in config['windows']:
        for m in METRICS:
            for k in TARGETS:
                means=[]; errors=[]
                for r in records:
                    good=[p for p in r['paths'] if p['status']=='success']
                    if len(good)!=4:continue
                    means.append(float(np.mean([p['scores'][str(n)][m][k] for p in good])))
                    errors.append(float(np.mean([abs(p['scores'][str(n)][m][k]-r['prediction'][m][k]) for p in good])))
                if means:
                    summary.append(dict(observations=n,metric=m,target=k,**interval(means),
                                        mean_absolute_prediction_error=float(np.mean(errors))))
    result=dict(summary=summary,failures=[dict(seed=r['seed'],**p) for r in records for p in r['paths'] if p['status']!='success'])
    (output/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.output)
