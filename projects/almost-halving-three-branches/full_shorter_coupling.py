"""Exact third-arm elimination; no periodicity or numerical rank tests."""
from collections import defaultdict
import argparse
import json
from math import gcd
from pathlib import Path
import shorter_arm_elimination as se


def validate(t,h):
    if type(t) is not int or t<1 or type(h) is not int or not 0<=h<=20*t-1:
        raise ValueError('require t>=1 and 0<=h<=20t-1; h=0 omits the centre')


def low_terms(t,h,r):
    validate(t,h)
    if type(r) is not int or not 1<=r<=3*t+1:
        raise ValueError('require 1<=r<=3t+1')
    out=defaultdict(int)
    for d,c in [(r,1),(r+23*t,-1),(r+56*t,-1),
                (r+23*t+h+1,1),(r+23*t+h,-1),
                (r+43*t-1,1),(r+20*t-1,-1),
                (r+43*t-h,-1),(r+43*t-h-1,1),
                (76*t+r-1,1)]:
        out[2,d]+=c
    out[3,r]+=1
    out[3,20*t+r-1]+=1
    return {v:c for v,c in out.items() if c}


def low_certificate(t,h,r):
    low_terms(t,h,r)
    e=43*t+r
    out=defaultdict(int,{e:1})
    for j,c in [(e-20*t,1),(r,-1),(56*t+r,1),
                (36*t-r+1,-1),(e+h-20*t+1,-1),(e+h-20*t,1)]:
        out[99*t+j]+=c
    return {e:c for e,c in out.items() if c}


def third_word(t,h,y,middle):
    """Linear recovery, allowing intermediate arbitrary integer values."""
    validate(t,h)
    if set(y)!=set(range(1,79*t+1)):
        raise ValueError('wrong second-arm coordinates')
    if set(middle)!=set(range(13*t+1,18*t+1)):
        raise ValueError('wrong middle third-arm coordinates')
    w=dict(middle)
    for r in range(3*t+2,18*t+1):
        terms=se.coupling_terms(t,h,r)
        target=(3,r if r<=13*t else 36*t-r+1)
        coefficient=terms.pop(target)
        assert coefficient==1
        w[target[1]]=-sum(c*(y[d] if i==2 else w[d]) for (i,d),c in terms.items())
    for r in range(1,3*t+2):
        terms=low_terms(t,h,r)
        assert terms.pop((3,r))==1
        w[r]=-sum(c*(y[d] if i==2 else w[d]) for (i,d),c in terms.items())
    return w


def geometry(t,h):
    validate(t,h)
    return [99*t,79*t,23*t],{(1,99*t),(1,h) if h else (0,0)}


def shell_column(L,H,v):
    """Exact (1-z)F-2zS column; same identity as APERIODIC_COMPLETION (1)."""
    i,d=v
    out=defaultdict(int)
    if i==0:
        out[1]+=1
        for n in L:out[n+1]-=1
    else:
        out[d+1]+=1
        out[L[i-1]+1-d]-=1
        for j,n in enumerate(L,1):
            if j!=i:out[d+n+1]-=1
    for j,a in H:
        distance=abs(d-a) if i==j else d+a
        out[distance]-=1
        out[distance+1]+=1
    return {e:c for e,c in out.items() if c}


def shell_rows(L,H,signs):
    out=defaultdict(int)
    for v,s in signs.items():
        if s:
            for e,c in shell_column(L,H,v).items():out[e]+=s*c
    return {e:c for e,c in out.items() if c}


def linear_completion(t,h,sigma,y,middle):
    """Prescribed rows only: remaining equations and literal signs still matter."""
    L,H=geometry(t,h)
    w=third_word(t,h,y,middle)
    signs={(2,d):s for d,s in y.items()}
    signs.update({(3,d):s for d,s in w.items()})
    if h:signs[0,0]=sigma
    for j in range(1,79*t+1):
        s=-y[j]
        if j<=23*t:
            s+=y[56*t+j]-w[j]
            if j<=3*t+1:s-=y[76*t+j-1]+w[20*t+j-1]
        signs[1,20*t+j-1]=s
    # For h<=2t-1 every remaining proximal column has the diagonal
    # coefficient -1 at C+1+d and no other contribution in this band.
    if h>2*t-1:
        raise ValueError('two-arm linear recovery requires h<=2t-1')
    known=shell_rows(L,H,signs)
    for d in range(1,20*t):
        if (1,d) not in H:signs[1,d]=known.get(23*t+1+d,0)
    return signs


def middle_operator(t,h,r):
    """Necessary homogeneous operator, NOT a proved invertible matrix."""
    validate(t,h)
    if h>2*t-1 or type(r) is not int or not 13*t+1<=r<=18*t:
        raise ValueError('require h<=2t-1 and 13t+1<=r<=18t')
    out=defaultdict(int)
    for j,c in [(r,1),(r+3*t+1,-1),(r+3*t+h+2,1),(r+3*t+h+1,-1)]:
        if 13*t+1<=j<=23*t:
            if j>18*t:j,c=36*t-j+1,-c
            out[j]+=c
    return {j:c for j,c in out.items() if c}


def periodic_middle_vector(t,h,residue):
    """One exact operator-kernel vector, not a homometric signing.

    Period g=gcd(3t,h+1); boundary-free range requires h<=2t-2.
    Distinct paired residues give floor(g/2) independent vectors.
    """
    validate(t,h)
    if h>2*t-2:
        raise ValueError('periodic operator kernel needs h<=2t-2')
    g=gcd(3*t,h+1)
    if type(residue) is not int or not 0<=residue<g:
        raise ValueError('residue outside the proved period')
    partner=(10*t+1-residue)%g
    if partner==residue:
        raise ValueError('fixed reflection residue gives only the zero vector')
    return {r:int((r-13*t)%g==residue)-int((r-13*t)%g==partner)
            for r in range(13*t+1,18*t+1)}


def recover_middle(t,h,forcing,seed):
    """Solve the necessary middle system from 2h+2 consecutive values.

    Coordinates here are relative 1..5t, not original third-arm depths.
    No rank, floating point, periodicity assumption or search is used.
    """
    validate(t,h)
    if h>2*t-2:raise ValueError('seed recovery requires h<=2t-2')
    if set(forcing)!=set(range(1,5*t+1)):
        raise ValueError('wrong forcing coordinates')
    lo,hi=2*t-h-1,2*t+h
    if set(seed)!=set(range(lo,hi+1)):
        raise ValueError('wrong consecutive middle seed coordinates')
    z=dict(seed)
    delta={i:z[i]-z[i-1] for i in range(lo+1,hi+1)}
    def reflection(a):
        return forcing[7*t-h-a]-forcing[a+h]
    for i in range(hi+1,5*t+1):
        j=7*t-i
        c=(forcing[i]-forcing[i-1]+reflection(j+1)
           +reflection(j-h+1)-reflection(j-h))
        if h:
            delta[i]=delta[i-2*h-1]+delta[i-h-1]-delta[i-h]+c
        else:
            if c%2:raise ValueError('inconsistent integer middle forcing')
            delta[i]=delta[i-1]+c//2
        z[i]=z[i-1]+delta[i]
    D=3*t+1
    for i in range(1,lo):
        z[i]=forcing[i]+z[i+D]-z[i+D+h+1]+z[i+D+h]
    for i in range(1,5*t+1):
        if sum(c*z[d-13*t] for d,c in middle_operator(t,h,13*t+i).items())!=forcing[i]:
            raise ValueError('remaining middle compatibility equation fails')
    return {13*t+i:s for i,s in z.items()}


def recover_from_seed(payload):
    """Unique full candidate from second arm plus a short middle seed."""
    t,h=payload['t'],payload['h']
    validate(t,h)
    if h>2*t-2:raise ValueError('seed recovery requires h<=2t-2')
    sigma=payload['centre']
    if type(sigma) is not int or (sigma not in (-1,1) if h else sigma!=0):
        raise ValueError('centre sign disagrees with omissions')
    word,seedword=payload['arm2'],payload['middle_seed']
    if not isinstance(word,str) or len(word)!=79*t or set(word)-set('+-'):
        raise ValueError('require a literal second word')
    if not isinstance(seedword,str) or len(seedword)!=2*h+2 or set(seedword)-set('+-'):
        raise ValueError('require exactly 2h+2 consecutive literal seed signs')
    y={d:1 if ch=='+' else -1 for d,ch in enumerate(word,1)}
    zero={r:0 for r in range(13*t+1,18*t+1)}
    L,H=geometry(t,h)
    baseline=linear_completion(t,h,sigma,y,zero)
    rows=shell_rows(L,H,baseline)
    forcing={i:rows.get(92*t+1+i,0) for i in range(1,5*t+1)}
    seed={i:1 if ch=='+' else -1 for i,ch in enumerate(seedword,2*t-h-1)}
    middle=recover_middle(t,h,forcing,seed)
    signs=linear_completion(t,h,sigma,y,middle)
    rows=shell_rows(L,H,signs)
    nonliteral=sum(s not in (-1,1) for s in signs.values())
    balance=sum(signs.values())
    accepted=not nonliteral and not balance and not rows
    result=dict(accepted=accepted,nonliteral_values=nonliteral,balance=balance,
                failed_shell_rows=len(rows),retained_signs=79*t+2*h+2+(h!=0),
                universal_existence_proved=False,all_hole_placements_covered=False)
    if accepted:
        result['pair']=dict(lengths=L,holes=sorted(H),
            left=[list(v) for v,s in signs.items() if s==1],
            right=[list(v) for v,s in signs.items() if s==-1])
    return result


def reconstruct_third(payload):
    """Fill every third-arm sign from its 5t middle signs; check necessary rows."""
    t,h=payload['t'],payload['h']
    validate(t,h)
    sigma=payload['centre']
    if type(sigma) is not int or (sigma not in (-1,1) if h else sigma!=0):
        raise ValueError('centre sign disagrees with omissions')
    word,mid=payload['arm2'],payload['middle_third']
    if not isinstance(word,str) or len(word)!=79*t or set(word)-set('+-'):
        raise ValueError('require a literal second word')
    if not isinstance(mid,str) or len(mid)!=5*t or set(mid)-set('+-'):
        raise ValueError('require exactly 5t literal middle third-arm signs')
    y={d:1 if ch=='+' else -1 for d,ch in enumerate(word,1)}
    middle={d:1 if ch=='+' else -1 for d,ch in enumerate(mid,13*t+1)}
    w=third_word(t,h,y,middle)
    if any(s not in (-1,1) for s in w.values()):
        raise ValueError('forced third-arm value is not a literal sign')
    L,H=geometry(t,h)
    q=dict(lengths=L,holes=sorted(H),centre=sigma,arm2=word,
           arm3=''.join('+' if w[d]==1 else '-' for d in range(1,23*t+1)))
    report=se.coupled_constraint(q)
    low_failures=sum(bool(sum(c*(y[d] if i==2 else w[d])
                             for (i,d),c in low_terms(t,h,r).items()))
                     for r in range(1,3*t+2))
    if report['violations'] or low_failures:
        raise ValueError('remaining shorter-arm compatibility rows fail')
    report.update(free_retained_signs_bound=84*t+1-(h==0),
                  checked_rows=23*t,first_arm_completion_proved=False)
    return dict(parameters=q,report=report)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parameters',type=Path,help='JSON: t,h,centre,arm2,middle_third')
    parser.add_argument('--seed',action='store_true',help='use 2h+2 middle_seed signs and verify the full pair')
    args=parser.parse_args()
    try:
        payload=json.loads(args.parameters.read_text())
        result=recover_from_seed(payload) if args.seed else reconstruct_third(payload)
        print(json.dumps(result,sort_keys=True))
    except (ValueError,KeyError) as exc:parser.exit(1,str(exc)+'\n')


if __name__=='__main__':main()
