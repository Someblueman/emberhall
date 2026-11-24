#!/usr/bin/env python3
"""Partial follow-on: compile exact shorter-word forcing, with no long signs."""
from collections import defaultdict
import argparse
import json
from pathlib import Path
import aperiodic_completion as ac


def compile_forcing(payload):
    lengths = payload['lengths']
    holes = ac.validate(lengths,payload['holes'])
    ac.interval_plan(lengths,holes)  # Published separation bounds, not a guess.
    known = {} if payload['centre']==0 else {(0,0):payload['centre']}
    if type(payload['centre']) is not int or payload['centre'] not in (-1,0,1):
        raise ValueError('invalid centre sign')
    for i in (2,3):
        word=payload[f'arm{i}']
        if not isinstance(word,str) or len(word)!=lengths[i-1] or set(word)-set('+-0'):
            raise ValueError('invalid shorter word')
        known.update({(i,d):1 if ch=='+' else -1 for d,ch in enumerate(word,1) if ch!='0'})
    expected={v for v in ac.vertices(lengths) if v[0]!=1 and v not in holes}
    if set(known)!=expected:
        raise ValueError('retained signs disagree with omissions')
    ends=list(lengths)
    for i in range(3):
        while ends[i] and (i+1,ends[i]) in holes:
            ends[i]-=1
    a,b=ends[0],max(ends[1:]);N=a+b
    P=defaultdict(int)
    for i,d in ac.vertices(lengths):
        if (i,d) not in holes:
            P[b+(d if i==1 else -d)]+=1
    S0=sum(known.values())
    derivative=defaultdict(int)
    derivative[1]=2*S0
    for v,s in known.items():
        for e,c in ac.column(lengths,holes,v).items():
            derivative[e]+=s*c
    D=max(ends[i]+ends[j] for i in range(3) for j in range(i+1,3))
    F0={};running=0
    for e in range(D+2):
        running+=derivative[e]
        if e<=D and running:
            F0[e]=running
    if running or any(v for e,v in derivative.items() if e>D+1):
        raise AssertionError('shell derivative did not integrate to a polynomial')
    R=defaultdict(int)
    R[N]=-2*S0
    for e,c in F0.items():
        R[N+e]-=c
        R[N-e]-=c
    return {'P':dict(P),'R':{e:c for e,c in R.items() if c},'N':N,
            'S0':S0,'F0':F0,'retained':len(known)}


def remainder(poly, modulus, prime=1000003):
    """Laurent remainder; require a nonzero constant for negative powers."""
    q={i:c%prime for i,c in enumerate(modulus) if c%prime}
    if not q or max(q)<1 or 0 not in q:
        raise ValueError('modulus needs positive degree and nonzero constant')
    degree=max(q);out={e:c%prime for e,c in poly.items() if c%prime}
    while out and min(out)<0:
        e=min(out);factor=out[e]*pow(q[0],-1,prime)%prime
        for j,c in q.items():
            k=e+j;out[k]=(out.get(k,0)-factor*c)%prime
            if not out[k]:out.pop(k,None)
    while out and max(out)>=degree:
        shift=max(out)-degree;factor=out[shift+degree]*pow(q[degree],-1,prime)%prime
        for j,c in q.items():
            k=shift+j;out[k]=(out.get(k,0)-factor*c)%prime
            if not out[k]:out.pop(k,None)
    return out


def constraint(payload,modulus):
    data=compile_forcing(payload)
    P,N=data['P'],data['N']
    if remainder(P,modulus) or remainder({N-e:c for e,c in P.items()},modulus):
        raise ValueError('modulus is not a certified common radial factor')
    residue=remainder(data['R'],modulus)
    return dict(retained_signs=data['retained'],radial_degree=N,
                forcing_residue=residue,excluded_by_necessary_constraint=bool(residue),
                existence_decided=False,all_scale_family_proved=False)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('parameters',type=Path)
    p.add_argument('--modulus',type=json.loads,required=True,help='constant-first coefficient list')
    args=p.parse_args()
    try:print(json.dumps(constraint(json.loads(args.parameters.read_text()),args.modulus),sort_keys=True))
    except (ValueError,KeyError) as e:p.exit(1,str(e)+'\n')


if __name__=='__main__':main()
