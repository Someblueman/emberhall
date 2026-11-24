#!/usr/bin/env python3
"""Exact shorter-arm coupling and radial forcing; standard library only."""
from collections import defaultdict
import argparse
import json
from pathlib import Path


def compile_forcing(payload):
    import aperiodic_completion as ac
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


def coupling_terms(t, h, r):
    """Integer shorter-only row; valid for 3t+2 <= r <= 23t."""
    if type(t) is not int or t < 1 or type(h) is not int or not 0 <= h <= 23*t:
        raise ValueError('require t>=1 and 0<=h<=23t')
    if type(r) is not int or not 3*t+2 <= r <= 23*t:
        raise ValueError('coupling row outside proved interval')
    out = defaultdict(int)
    for d, c in [(r,1),(r+23*t,-1),(r+56*t,-1),
                 (r+23*t+h+1,1),(r+23*t+h,-1),
                 (r+43*t-1,1),(r+20*t-1,-1),
                 (r+43*t-h,-1),(r+43*t-h-1,1)]:
        out[2,d] += c
    out[3,r] += 1
    u = 36*t-r+1
    if u <= 23*t:
        out[3,u] += 1
        out[2,56*t+u] -= 1
    return {v:c for v,c in out.items() if c}


def certificate_rows(t, h, r):
    """Exact identity L_r = sum c_e K_e, even for unbalanced signs."""
    coupling_terms(t,h,r)  # Validate the theorem's quantifiers.
    e = 43*t+r
    out = defaultdict(int)
    out[e] += 1
    # E_j denotes K_(99t+j).
    for j,c in [(e-20*t,1),(r,-1),(56*t+r,1),
                (79*t-e+1,-1),(e+h-20*t+1,-1),(e+h-20*t,1)]:
        out[99*t+j] += c
    u = 36*t-r+1
    if u <= 23*t:
        out[99*t+56*t+u] += 1
    return {e:c for e,c in out.items() if c}


def coupled_constraint(payload):
    """Necessary conditions only; does not assert a homometric completion."""
    lengths = payload['lengths']
    if (not isinstance(lengths,(list,tuple)) or len(lengths)!=3
            or any(type(n) is not int or n<1 for n in lengths)):
        raise ValueError('require three positive integer lengths')
    try:
        holes = set(map(tuple,payload['holes']))
    except TypeError as exc:
        raise ValueError('holes must be coordinate pairs') from exc
    if any(len(v)!=2 or any(type(c) is not int for c in v) for v in holes):
        raise ValueError('holes must be integer coordinate pairs')
    if lengths[0] % 99:
        raise ValueError('require lengths (99t,79t,23t)')
    t = lengths[0]//99
    if list(lengths) != [99*t,79*t,23*t]:
        raise ValueError('require lengths (99t,79t,23t)')
    candidates = [d for i,d in holes if i == 1 and d != 99*t]
    if (0,0) in holes:
        candidates.append(0)
    shallow = (0,0) if candidates == [0] else ((1,candidates[0]) if len(candidates)==1 else None)
    if len(candidates) != 1 or holes != {shallow,(1,99*t)}:
        raise ValueError('require exactly the two proved first-arm holes')
    h = candidates[0]
    coupling_terms(t,h,3*t+2)
    words = {}
    for i in (2,3):
        word = payload[f'arm{i}']
        if not isinstance(word,str) or len(word)!=lengths[i-1] or set(word)-set('+-'):
            raise ValueError('require literal occupied shorter words')
        words[i] = word
    if (type(payload['centre']) is not int
            or (payload['centre'] not in (-1,1) if h else payload['centre'] != 0)):
        raise ValueError('centre sign disagrees with the hole geometry')
    def value(v):
        i,d = v
        return 1 if words[i][d-1]=='+' else -1
    violations = []
    for r in range(3*t+2,23*t+1):
        residual = sum(c*value(v) for v,c in coupling_terms(t,h,r).items())
        if residual:
            violations.append((r,residual))
    return dict(t=t,h=h,checked_rows=20*t-1,violations=len(violations),
                first_violation=violations[0] if violations else None,
                excluded_by_necessary_constraint=bool(violations),
                free_retained_signs_bound=87*t+2-(h==0),
                all_scale_reduction_proved=True,
                existence_decided=False,all_hole_placements_covered=False,
                all_scale_family_proved=False)


def second_arm_terms(t,h,r):
    """A second-arm-only compatibility equation; no independence claim."""
    coupling_terms(t,h,r)
    if not 13*t+1 <= r <= 18*t:
        raise ValueError('require the lower half of the reflection band')
    out = defaultdict(int, coupling_terms(t,h,r))
    for v,c in coupling_terms(t,h,36*t-r+1).items():
        out[v] -= c
    out = {v:c for v,c in out.items() if c}
    assert all(i==2 for i,d in out)
    return out


def force_third_band(t,h,arm2,free_arm3):
    """Fill exactly 15t-1 forced positions; reject nonliteral forced values.

    free_arm3 is a depth->sign dictionary on [1,3t+1] U [13t+1,18t].
    The remaining second-arm compatibility rows are checked separately.
    """
    coupling_terms(t,h,3*t+2)
    if not isinstance(arm2,str) or len(arm2)!=79*t or set(arm2)-set('+-'):
        raise ValueError('require a literal second word')
    expected = set(range(1,3*t+2)) | set(range(13*t+1,18*t+1))
    if set(free_arm3)!=expected or any(type(s) is not int or s not in (-1,1) for s in free_arm3.values()):
        raise ValueError('wrong free third-arm coordinates or signs')
    w = dict(free_arm3)
    for r in list(range(3*t+2,13*t+1))+list(range(13*t+1,18*t+1)):
        terms = coupling_terms(t,h,r)
        target = r if r<=13*t else 36*t-r+1
        c = terms.pop((3,target))
        total = sum(k*((1 if arm2[d-1]=='+' else -1) if i==2 else w[d])
                    for (i,d),k in terms.items())
        sign = -total//c
        if total % c or sign not in (-1,1):
            raise ValueError('forced third-arm value is not a literal sign')
        w[target] = sign
    return ''.join('+' if w[d]==1 else '-' for d in range(1,23*t+1))


def reconstruct_third(payload):
    """Accept '?' exactly on forced coordinates, fill them and check all rows."""
    word = payload['arm3']
    if not isinstance(word,str) or set(word)-set('+-?'):
        raise ValueError('compressed third word needs +, - or ?')
    probe = dict(payload,arm3=word.replace('?','+'))
    geometry = coupled_constraint(probe)
    t,h = geometry['t'],geometry['h']
    free = set(range(1,3*t+2)) | set(range(13*t+1,18*t+1))
    if any((ch=='?') == (d in free) for d,ch in enumerate(word,1)):
        raise ValueError('use ? exactly on the forced third-arm coordinates')
    signs = {d:1 if word[d-1]=='+' else -1 for d in free}
    completed = dict(payload,arm3=force_third_band(t,h,payload['arm2'],signs))
    report = coupled_constraint(completed)
    if report['excluded_by_necessary_constraint']:
        raise ValueError('remaining shorter-arm compatibility rows fail')
    return dict(parameters=completed,report=report)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('parameters',type=Path)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--modulus',type=json.loads,help='constant-first coefficient list')
    g.add_argument('--coupled',action='store_true',help='check the proved all-scale shorter-arm rows')
    g.add_argument('--force-third',action='store_true',help='fill forced ? positions in the third word')
    args=p.parse_args()
    try:
        payload=json.loads(args.parameters.read_text())
        if args.force_third:
            result=reconstruct_third(payload)
        else:
            result=coupled_constraint(payload) if args.coupled else constraint(payload,args.modulus)
        print(json.dumps(result,sort_keys=True))
    except (ValueError,KeyError) as e:p.exit(1,str(e)+'\n')


if __name__=='__main__':main()
