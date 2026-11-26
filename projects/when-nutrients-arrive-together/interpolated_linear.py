"""Exact stationary linear model for linearly interpolated OU mesh inputs.

Isolates population forcing interpolation bias, not realized pathwise error.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import expm,solve_discrete_lyapunov
from scipy.stats import spearmanr

from linear_reference import equilibrium,linear_system
from linear_calibration import setup
from linear_welch import expected_spectra
from reference import community,PAIRS,auc,single_linkage_scores


def interpolated_system(j,b,spacing,rate=1.,variance=.005):
    """Mesh-endpoint dynamics driven by exact OU endpoints and linear bridges.

    This is a deterministic straight line between endpoints, not an OU bridge.
    Return its transition and stationary covariance including the input state.
    """
    if spacing<=0 or rate<=0 or variance<=0:
        raise ValueError('positive mesh, rate and stationary input variance required')
    d,k=b.shape
    augmented=np.zeros((d+2*k,d+2*k))
    augmented[:d,:d]=j;augmented[:d,d:d+k]=b
    augmented[d:d+k,d+k:]=np.eye(k)
    step=expm(augmented*spacing)
    p=step[:d,:d]
    right=step[:d,d+k:]/spacing
    left=step[:d,d:d+k]-right
    r=np.exp(-rate*spacing)
    transition=np.block([[p,left+r*right],[np.zeros((k,d)),r*np.eye(k)]])
    innovation=np.vstack((right,np.eye(k)))
    q=variance*(-np.expm1(-2*rate*spacing))*(innovation@innovation.T)
    if np.max(np.abs(np.linalg.eigvals(transition)))>=1:
        raise ValueError('unstable interpolated linear model')
    covariance=solve_discrete_lyapunov(transition,q)
    residual=float(np.linalg.norm(covariance-transition@covariance@transition.T-q)/np.linalg.norm(covariance))
    return transition,covariance,residual


def predictions(transition,covariance,gain,labels,segment=30):
    power=np.eye(len(transition))
    scales=np.sqrt(np.diag(covariance)[:6])
    lags=[]
    for k in range(segment):
        lags.append((power@covariance)[:6,:6]/scales[:,None]/scales[None,:])
        power=transition@power
    spectra=expected_spectra(lags,segment)
    auto=np.diagonal(spectra,axis1=1,axis2=2).real
    cross=spectra[:,PAIRS[0],PAIRS[1]]
    coherence=abs(cross)**2/(auto[:,PAIRS[0]]*auto[:,PAIRS[1]])
    correlation=lags[0][PAIRS]
    values=dict(correlation=correlation,absolute_correlation=abs(correlation),
                cpsd=abs(cross).sum(axis=0)/segment,coherence=coherence.sum(axis=0)/segment)
    overlap=(gain@gain.T)[PAIRS];same=(labels[:,None]==labels)[PAIRS]
    scores={metric:dict(overlap_spearman=float(spearmanr(value,overlap).statistic),
        same_diet_pair_auc=auc(same,value),
        single_linkage_guild_auc=auc(same,single_linkage_scores(value))) for metric,value in values.items()}
    return scores,values


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    config=dict(seeds=list(range(4,16)),meshes=[.25,.125,.0625,.03125],segment=30,
                observation_interval=1.,input_rate=1.,stationary_input_variance=.005,
                scope='stationary local-linear population interpolation bias; not same-path or nonlinear bounds',
                numpy=np.__version__,scipy=scipy.__version__,
                code_sha256={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                    for name in ('interpolated_linear.py','linear_reference.py','linear_calibration.py','linear_welch.py','reference.py')})
    encoded=json.dumps(config,indent=2,sort_keys=True)+'\n'
    protocol=output/'protocol.json'
    if protocol.exists() and protocol.read_text()!=encoded:
        raise ValueError('different interpolation protocol')
    protocol.write_text(encoded)
    records=[]
    for seed in config['seeds']:
        uptake,gain,labels=community(seed)
        x,resources=equilibrium(uptake,gain,np.r_[np.ones(24),np.full(6,3.)])
        j,b=linear_system(uptake,gain,x,resources)
        continuous_f,continuous_p,_,_=setup(seed)
        reference,reference_values=predictions(continuous_f,continuous_p,gain,labels)
        for mesh in config['meshes']:
            f,p,residual=interpolated_system(j,b,mesh)
            observation=np.linalg.matrix_power(f,int(round(1/mesh)))
            scores,values=predictions(observation,p,gain,labels)
            records.append(dict(seed=seed,mesh=mesh,lyapunov_relative_residual=residual,
                relative_covariance_error=float(np.linalg.norm(p[:6,:6]-continuous_p[:6,:6])/np.linalg.norm(continuous_p[:6,:6])),
                maximum_correlation_error=float(np.max(abs(values['correlation']-reference_values['correlation']))),
                score_changes={metric:{target:scores[metric][target]-value for target,value in targets.items()}
                               for metric,targets in reference.items()}))
    summary=[]
    for mesh in config['meshes']:
        group=[r for r in records if r['mesh']==mesh]
        summary.append(dict(mesh=mesh,communities=len(group),
            maximum_relative_covariance_error=max(r['relative_covariance_error'] for r in group),
            maximum_correlation_error=max(r['maximum_correlation_error'] for r in group),
            maximum_absolute_score_changes={metric:{target:max(abs(r['score_changes'][metric][target]) for r in group)
                for target in group[0]['score_changes'][metric]} for metric in group[0]['score_changes']}))
    report=dict(summary=summary,maximum_lyapunov_relative_residual=max(r['lyapunov_relative_residual'] for r in records))
    (output/'records.json').write_text(json.dumps(records,indent=2,allow_nan=False)+'\n')
    (output/'summary.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
