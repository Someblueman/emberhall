"""Conditional midpoint refinement of an already sampled stationary OU path."""
import argparse
import json
from pathlib import Path
import numpy as np
from reference import ou, simulate, score
from paired_crosscheck import compare


def bridge(supply, spacing, seed, amplitude=.1, omega=1.):
    if spacing <= 0 or amplitude <= 0 or omega <= 0:
        raise ValueError('positive spacing, amplitude and rate required')
    base = np.r_[np.ones(24), np.full(6, 3.)]
    if supply.ndim != 2 or supply.shape[1] != 30 or len(supply) < 2:
        raise ValueError('need at least two thirty-resource endpoints')
    a = np.exp(-omega * spacing / 2)
    q = supply - base
    variance = amplitude**2 / 2 * (1-a*a)/(1+a*a)
    refined = np.empty((2*len(supply)-1, 30))
    refined[::2] = supply
    refined[1::2] = (base + a/(1+a*a)*(q[:-1]+q[1:])
                     + np.sqrt(variance)*np.random.default_rng(seed).normal(size=(len(supply)-1,30)))
    return refined


def check(experiment, seed=6, drive=0, bridge_seed=600006):
    config = json.loads((experiment/'config.json').read_text())
    import hashlib
    if config['model_sha256'] != hashlib.sha256(Path(__file__).with_name('reference.py').read_bytes()).hexdigest():
        raise ValueError('model/estimator hash differs')
    supply = ou(200000 + 1000*seed + drive, config['duration'], config['finest'])
    refined_supply = bridge(supply, config['finest'], bridge_seed)
    if refined_supply.min() <= 0:
        raise ValueError('nonpositive bridge supply; no repair')
    with np.load(experiment/f'community-{seed}-drive-{drive}.npz') as data:
        old, uptake, gain, labels = data['log_abundance'], data['uptake'], data['gain'], data['labels']
    new, minimum = simulate(uptake,gain,refined_supply,config['finest']/2,
                            config['duration'],config['burn'],config['finest']/4,1e-10)
    result = dict(community=seed,drive=drive,bridge_seed=bridge_seed,
                  duration=config['duration'],burn=config['burn'],model_sha256=config['model_sha256'],
                  rtol=1e-10,max_step=config['finest']/4,
                  original_mesh=config['finest'],refined_mesh=config['finest']/2,
                  endpoints_exact=bool(np.array_equal(refined_supply[::2],supply)),
                  minimum_supply=float(refined_supply.min()),minimum_abundance=minimum,
                  log_rms=float(np.sqrt(np.mean((new-old)**2))),
                  score_differences=compare(score(old,gain,labels),score(new,gain,labels)),
                  limitation='post-hoc single-path diagnostic; not a continuum or population bound')
    (experiment/f'bridge-check-{seed}-{drive}.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment',type=Path)
    args=parser.parse_args()
    check(args.experiment)
