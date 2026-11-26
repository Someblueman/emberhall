"""Exact finite-horizon initialization corrections for the local-linear model."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.signal import get_window

from finite_covariance import lag_covariances
from linear_calibration import setup
from linear_reference import equilibrium
from linear_welch import expected_spectra
from reference import community


def finite_sums(f, k, count):
    """Return F**count, sum F**t, sum F**t K (F**t).T for 0<=t<count.

    Binary concatenation; no stability or invertibility condition is needed.
    """
    f, k = np.asarray(f, float), np.asarray(k, float)
    if (type(count) is not int or count < 0 or f.ndim != 2 or
            f.shape[0] != f.shape[1] or k.shape != f.shape or
            not np.isfinite(f).all() or not np.isfinite(k).all() or
            not np.allclose(k,k.T,rtol=1e-12,atol=1e-14)):
        raise ValueError('finite square transition, symmetric correction and nonnegative integer count required')
    size = len(f)
    power, total, gram = np.eye(size), np.zeros_like(f), np.zeros_like(f)
    block_power, block_total, block_gram = f.copy(), np.eye(size), k.copy()
    while count:
        if count & 1:
            gram += power @ block_gram @ power.T
            total += power @ block_total
            power = power @ block_power
        count >>= 1
        if count:
            block_gram = block_gram + block_power @ block_gram @ block_power.T
            block_total = block_total + block_power @ block_total
            block_power = block_power @ block_power
    return power, total, (gram + gram.T)/2


def fourier_filters(f, observation, segment):
    if type(segment) is not int or segment < 3:
        raise ValueError('segment must be at least three')
    window = get_window('hann', segment, fftbins=True)
    vectors = np.exp(-2j*np.pi*np.arange(segment//2+1)[:, None]
                     *np.arange(segment)[None, :]/segment)*window
    vectors -= vectors.mean(axis=1, keepdims=True)
    powers = []
    rows = np.asarray(observation, float)
    for _ in range(segment):
        powers.append(rows)
        rows = rows @ f
    filters = np.einsum('ft,tij->fij', vectors, np.asarray(powers))
    factors = np.full(len(vectors), 2/np.sum(window**2))
    factors[0] /= 2
    if segment % 2 == 0:
        factors[-1] /= 2
    return filters, factors


def corrections(f, k, observation, count, burn=0, segment=30, hop=None):
    """Differences from stationary expected raw Welch and centered covariance.

    K=P0-P+m*m.T at time zero; innovations have stationary covariance.
    No coherence or sample-correlation expectation is returned.
    """
    if (type(count) is not int or count < segment or type(burn) is not int or burn < 0):
        raise ValueError('nonnegative integer burn and a full record required')
    hop = segment-segment//2 if hop is None else hop
    if type(hop) is not int or not 1 <= hop <= segment:
        raise ValueError('hop must be between one and segment')
    f, k, observation = np.asarray(f, float), np.asarray(k, float), np.asarray(observation, float)
    if observation.ndim != 2 or observation.shape[1] != len(f) or not np.isfinite(observation).all():
        raise ValueError('finite observation matrix required')
    # finite_sums validates transition, initial correction and integer exponent.
    fb = finite_sums(f, k, burn)[0]
    kb = fb @ k @ fb.T
    segments = 1+(count-segment)//hop
    fh = np.linalg.matrix_power(f, hop)
    average = finite_sums(fh, kb, segments)[2]/segments
    filters, factors = fourier_filters(f, observation, segment)
    spectra = np.einsum('fip,pq,fjq->fij', filters.conj(), average, filters)
    spectra *= factors[:, None, None]
    _, total, gram = finite_sums(f, kb, count)
    covariance = observation @ (gram/count-total@kb@total.T/count**2) @ observation.T
    return spectra, (covariance+covariance.T)/2, segments


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    config = dict(seeds=list(range(4,16)), burns=[0,128,512,2048], lengths=[4096,65536],
                  starts=['equilibrium','baseline-tangent'],segment=30,hop=15,
                  scope='exact finite-horizon linear expected raw spectra and centered covariance; no nonlinear or expected coherence guarantee',
                  numpy=np.__version__, scipy=scipy.__version__,
                  code_sha256={name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                               for name in ['transient_welch.py','TRANSIENT_WELCH.md','linear_calibration.py',
                                            'linear_reference.py','linear_welch.py','finite_covariance.py','reference.py']})
    protocol = json.dumps(config, indent=2, sort_keys=True)+'\n'
    target = output/'protocol.json'
    if target.exists() and target.read_text() != protocol:
        raise ValueError('different frozen protocol')
    target.write_text(protocol)
    rows = []
    for seed in config['seeds']:
        f, p, _, _ = setup(seed)
        observation = np.eye(len(f))[:6]
        r,g,_ = community(seed)
        x,resources = equilibrium(r,g,np.r_[np.ones(24),np.full(6,3.)])
        initial = np.zeros_like(p); initial[36:,36:] = .005*np.eye(30)
        covariance_k = initial-p
        lags = lag_covariances(f,p,config['segment'])
        stationary = expected_spectra(lags,config['segment'])
        autos = np.diagonal(stationary,axis1=1,axis2=2).real
        scales = np.sqrt(autos[:,:,None]*autos[:,None,:])
        if np.any(autos<=0):
            raise ValueError('nonpositive stationary auto spectrum')
        covariance_scales = np.sqrt(np.outer(np.diag(p)[:6],np.diag(p)[:6]))
        for start in config['starts']:
            m = np.zeros(len(f))
            if start == 'baseline-tangent':
                m[:6] = -np.log(x); m[6:36] = 1-resources
            for burn in config['burns']:
                for count in config['lengths']:
                    parts = {}
                    for name,k in [('mean',np.outer(m,m)),('covariance',covariance_k)]:
                        spectra,cov,_ = corrections(f,k,observation,count,burn,config['segment'],config['hop'])
                        parts[name]=(spectra,cov)
                    total_s = parts['mean'][0]+parts['covariance'][0]
                    total_c = parts['mean'][1]+parts['covariance'][1]
                    row = dict(seed=seed,start=start,burn=burn,count=count,
                               spectral_relative_max=float(np.max(abs(total_s)/scales)),
                               centered_covariance_relative_max=float(np.max(abs(total_c)/covariance_scales)),
                               minimum_relative_auto_correction=float(np.min(np.diagonal(total_s,axis1=1,axis2=2).real/autos)),
                               maximum_relative_auto_correction=float(np.max(np.diagonal(total_s,axis1=1,axis2=2).real/autos)))
                    for name,(s,c) in parts.items():
                        row[name+'_spectral_relative_max']=float(np.max(abs(s)/scales))
                        row[name+'_covariance_relative_max']=float(np.max(abs(c)/covariance_scales))
                    rows.append(row)
        print('transient model',seed,flush=True)
    path=output/'summary.csv'
    with path.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print('cases',len(rows),'summary sha256',hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
