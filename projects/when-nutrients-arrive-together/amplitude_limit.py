"""Same-path nonlinear-to-linear amplitude check; not baseline acceptance."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from reference import community, ou, rhs, score
from linear_reference import equilibrium, linear_system


def exact_linear_response(j, b, forcing, spacing):
    """Zero-state response at mesh endpoints to piecewise-linear forcing.

    The augmented system has z'=Jz+Bq, q'=v, v'=0 on each interval.
    Reset q and v at each mesh boundary; z is continuous.
    """
    d,k=b.shape
    augmented=np.zeros((d+2*k,d+2*k))
    augmented[:d,:d]=j;augmented[:d,d:d+k]=b
    augmented[d:d+k,d+k:]=np.eye(k)
    step=expm(augmented*spacing)[:d]
    transition=step[:,:d];level=step[:,d:d+k];slope=step[:,d+k:]
    result=np.zeros((len(forcing),d))
    for index in range(len(forcing)-1):
        result[index+1]=(transition@result[index]+level@forcing[index]
                        +slope@(forcing[index+1]-forcing[index])/spacing)
    return result


def nonlinear_response(uptake,gain,base,initial,forcing,spacing,fraction,
                       observation_times,max_step,tolerance):
    duration=(len(forcing)-1)*spacing
    def derivative(time,state):
        position=min(time/spacing,len(forcing)-1)
        left=min(int(position),len(forcing)-2)
        weight=position-left
        drive=forcing[left]*(1-weight)+forcing[left+1]*weight
        return rhs(state,base+fraction*drive,uptake,gain)
    solve=solve_ivp(derivative,(0,duration),initial,t_eval=observation_times,
                    max_step=max_step,rtol=tolerance,atol=tolerance/100)
    if not solve.success or solve.y.shape[1]!=len(observation_times):
        raise RuntimeError(solve.message)
    if not np.isfinite(solve.y).all() or np.min(solve.y[6:])<=0:
        raise ValueError('nonfinite state or nonpositive resource; no repair')
    return solve.y[:6].T-initial[:6]


def evaluate(seed,config):
    uptake,gain,labels=community(seed)
    base=np.r_[np.ones(24),np.full(6,3.)]
    abundance,resources=equilibrium(uptake,gain,base)
    initial=np.r_[np.log(abundance),resources]
    j,b=linear_system(uptake,gain,abundance,resources)
    forcing=ou(70000+seed,config['duration'],config['mesh'])-base
    if np.min(base+forcing)<=0:
        raise ValueError('nonpositive supply; no repair')
    times=np.arange(config['burn'],config['duration'],1.)
    indices=np.rint(times/config['mesh']).astype(int)
    linear=exact_linear_response(j,b,forcing,config['mesh'])[indices,:6]
    denominator=np.linalg.norm(linear)
    if denominator<=1e-12:
        raise ValueError('degenerate linear response')
    linear_scores=score(linear,gain,labels)
    linear_cov=np.cov(linear.T,bias=True)
    records=[]
    for fraction in config['fractions']:
        nonlinear=nonlinear_response(uptake,gain,base,initial,forcing,config['mesh'],
            fraction,times,config['mesh']/2,1e-10)
        scaled=nonlinear/fraction
        scores=score(nonlinear,gain,labels)
        record=dict(fraction=fraction,relative_trajectory_error=float(np.linalg.norm(scaled-linear)/denominator),
                    relative_covariance_error=float(np.linalg.norm(np.cov(scaled.T,bias=True)-linear_cov)/np.linalg.norm(linear_cov)),
                    score_changes={metric:{target:scores[metric][target]-value
                        for target,value in targets.items()} for metric,targets in linear_scores.items()})
        if seed==config['seeds'][0] and fraction==config['fractions'][-1]:
            tighter=nonlinear_response(uptake,gain,base,initial,forcing,config['mesh'],
                fraction,times,config['mesh']/4,1e-11)
            record['tighter_solver_relative_difference']=float(np.linalg.norm(tighter-nonlinear)/(fraction*denominator))
        records.append(record)
        print('amplitude',seed,fraction,record['relative_trajectory_error'],flush=True)
    return dict(seed=seed,status='success',minimum_supply=float(np.min(base+forcing)),
                linear_scores=linear_scores,records=records)


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    config=dict(seeds=list(range(4,16)),input_seed='70000 + community',duration=2048,burn=512,
                mesh=.0625,fractions=[1.,.5,.25,.125],segment=30,
                initial='deterministic equilibrium for both linear and nonlinear systems',
                scope='same-path finite-amplitude diagnostic, not stationary population or baseline acceptance',
                numpy=np.__version__,scipy=scipy.__version__,
                code_sha256={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                             for name in ('amplitude_limit.py','reference.py','linear_reference.py')})
    encoded=json.dumps(config,indent=2,sort_keys=True)+'\n'
    protocol=output/'protocol.json'
    if protocol.exists() and protocol.read_text()!=encoded:
        raise ValueError('different amplitude protocol')
    protocol.write_text(encoded)
    results=[]
    for seed in config['seeds']:
        receipt=output/f'seed-{seed}.json'
        if receipt.exists():
            result=json.loads(receipt.read_text())
            if result.get('seed')!=seed or result.get('status') not in ('success','failure'):
                raise ValueError('invalid amplitude receipt')
        else:
            try:
                result=evaluate(seed,config)
            except (ValueError,RuntimeError,FloatingPointError) as error:
                result=dict(seed=seed,status='failure',error=str(error))
            receipt.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        results.append(result)
    summary=[]
    successful=[r for r in results if r['status']=='success']
    for index,fraction in enumerate(config['fractions']):
        records=[r['records'][index] for r in successful]
        if not records:continue
        summary.append(dict(fraction=fraction,communities=len(records),
            maximum_relative_trajectory_error=max(r['relative_trajectory_error'] for r in records),
            maximum_relative_covariance_error=max(r['relative_covariance_error'] for r in records),
            maximum_absolute_score_changes={metric:{target:max(abs(r['score_changes'][metric][target])
                for r in records) for target in records[0]['score_changes'][metric]}
                for metric in records[0]['score_changes']}))
    report=dict(planned=len(results),successful=len(successful),failures=[r for r in results if r['status']=='failure'],
                summary=summary,seed_errors={str(r['seed']):[x['relative_trajectory_error'] for x in r['records']]
                                           for r in successful},
                tighter_solver_checks=[dict(seed=r['seed'],fraction=x['fraction'],
                    relative_difference=x['tighter_solver_relative_difference']) for r in successful
                    for x in r['records'] if 'tighter_solver_relative_difference' in x])
    (output/'summary.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
