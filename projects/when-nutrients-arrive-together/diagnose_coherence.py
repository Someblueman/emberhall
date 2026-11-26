"""Post-hoc replay of the retained community-four coherence ranking gap."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from amplitude_limit import exact_linear_response,nonlinear_response
from reference import community,ou,measures,score,PAIRS
from linear_reference import equilibrium,linear_system


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    config=dict(seed=4,input_seed=70004,fraction=.125,duration=2048,burn=512,mesh=.0625,
                max_step=.03125,tolerance=1e-10,
                purpose='post-hoc diagnosis of already retained coherence rank gap; no new amplitude or baseline gate',
                code_sha256={n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
                             for n in ('diagnose_coherence.py','amplitude_limit.py','reference.py','linear_reference.py')})
    encoded=json.dumps(config,indent=2,sort_keys=True)+'\n'
    protocol=output/'protocol.json'
    if protocol.exists() and protocol.read_text()!=encoded:
        raise ValueError('different coherence diagnostic protocol')
    protocol.write_text(encoded)
    uptake,gain,labels=community(4)
    base=np.r_[np.ones(24),np.full(6,3.)]
    x,resources=equilibrium(uptake,gain,base)
    initial=np.r_[np.log(x),resources]
    j,b=linear_system(uptake,gain,x,resources)
    q=ou(70004,2048,.0625)-base
    times=np.arange(512,2048,1.)
    linear=exact_linear_response(j,b,q,.0625)[np.rint(times/.0625).astype(int),:6]
    nonlinear=nonlinear_response(uptake,gain,base,initial,q,.0625,.125,times,.03125,1e-10)
    a=measures(linear)['coherence'];c=measures(nonlinear)['coherence']
    inversions=[]
    for i in range(len(a)):
        for k in range(i+1,len(a)):
            if (a[i]-a[k])*(c[i]-c[k])<0:
                inversions.append(dict(first_edge=[int(PAIRS[0][i]),int(PAIRS[1][i])],
                    second_edge=[int(PAIRS[0][k]),int(PAIRS[1][k])],
                    linear_difference=float(a[i]-a[k]),nonlinear_difference=float(c[i]-c[k])))
    result=dict(linear_coherence=a.tolist(),nonlinear_coherence=c.tolist(),
                maximum_absolute_measure_difference=float(np.max(abs(a-c))),inversions=inversions,
                linear_scores=score(linear,gain,labels)['coherence'],
                nonlinear_scores=score(nonlinear,gain,labels)['coherence'])
    (output/'report.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
