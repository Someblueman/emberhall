"""Symbolic balance coefficients with certified affine breakpoint ordering.

Certifies h=19 and the cone h>=3, t>=h+2. No rank sampling.
"""
from collections import defaultdict
from dataclasses import dataclass
from functools import total_ordering
import argparse
import json


def plus(a,b):
    return (a[0]+b[0],a[1]+b[1])


def minus(a,b):
    return (a[0]-b[0],a[1]-b[1])


def value(a,t):
    return a[0]*t+a[1]


class OrderProof:
    """Each operation records sufficient integer t for its affine ordering."""
    def __init__(self):
        self.minimum_t = 1
        self.inequalities = set()

    def require(self,left,right,margin=0):
        # Prove right(t)-left(t)>=margin for every t>=minimum_t.
        a,b = minus(right,left)
        if a < 0 or (a == 0 and b < margin):
            raise ArithmeticError('requested order is not eventually true')
        if a:
            self.minimum_t = max(self.minimum_t,(margin-b+a-1)//a)
        self.inequalities.add((left,right,margin))

    def intersect(self,left,right):
        lo = max(left[0],right[0])
        hi = min(left[1],right[1])
        self.require(min(left[0],right[0]),lo)
        self.require(hi,max(left[1],right[1]))
        if lo > hi:
            # Dropping an integer interval requires strict separation.
            self.require(hi,lo,1)
            return None
        self.require(lo,hi)
        return lo,hi

    def verify(self):
        # Nonnegative slope plus a checked endpoint proves the whole ray.
        return all((minus(r,l)[0]>=0 and
                    value(minus(r,l),self.minimum_t)>=margin)
                   for l,r,margin in self.inequalities)


@total_ordering
@dataclass(frozen=True)
class AffineH:
    """Exact intercept b*h+c for a two-parameter endpoint a*t+b*h+c."""
    slope: int = 0
    intercept: int = 0

    @staticmethod
    def lift(other):
        return other if isinstance(other,AffineH) else AffineH(0,other)

    def __add__(self,other):
        other = self.lift(other)
        return AffineH(self.slope+other.slope,self.intercept+other.intercept)

    __radd__ = __add__

    def __neg__(self):
        return AffineH(-self.slope,-self.intercept)

    def __sub__(self,other):
        return self+-self.lift(other)

    def __rsub__(self,other):
        return self.lift(other)+-self

    def __lt__(self,other):
        other = self.lift(other)
        return (self.slope,self.intercept)<(other.slope,other.intercept)

    def __eq__(self,other):
        other = self.lift(other)
        return (self.slope,self.intercept)==(other.slope,other.intercept)

    def __hash__(self):
        # Equal constant AffineH and integer objects need equal hashes.
        return hash(self.intercept) if not self.slope else hash((self.slope,self.intercept))


class ConeProof(OrderProof):
    """Certify orders on h>=3, t>=h+2 by nonnegative cone coordinates."""
    def require(self,left,right,margin=0):
        a,b = minus(right,left)
        b = AffineH.lift(b)
        # t=u+v+5, h=v+3, with u,v>=0.
        coefficients = (a,a+b.slope,5*a+3*b.slope+b.intercept-margin)
        if min(coefficients)<0:
            raise ArithmeticError(f'order not proved on cone: {left} <= {right}, margin {margin}')
        self.inequalities.add((left,right,margin))

    def verify(self):
        for left,right,margin in self.inequalities:
            a,b = minus(right,left)
            b = AffineH.lift(b)
            if min(a,a+b.slope,5*a+3*b.slope+b.intercept-margin)<0:
                return False
        return True


def add(*sequences):
    terms = defaultdict(int)
    for sequence in sequences:
        for lo,hi,c in sequence:
            terms[lo,hi] += c
    return [(lo,hi,c) for (lo,hi),c in terms.items() if c]


def scale(sequence,c):
    return [(lo,hi,q*c) for lo,hi,q in sequence if q*c]


def shift(sequence,offset):
    return [(plus(lo,offset),plus(hi,offset),c) for lo,hi,c in sequence]


def reflect(sequence,axis):
    return [(minus(axis,hi),minus(axis,lo),c) for lo,hi,c in sequence]


def restrict(sequence,domain,proof):
    result = []
    for lo,hi,c in sequence:
        interval = proof.intersect((lo,hi),domain)
        if interval is not None:
            result.append((*interval,c))
    return add(result)


def segments(sequence,domain,proof):
    sequence = restrict(sequence,domain,proof)
    events = defaultdict(int)
    events[domain[0]] += 0
    events[plus(domain[1],(0,1))] += 0
    for lo,hi,c in sequence:
        events[lo] += c
        events[plus(hi,(0,1))] -= c
    points = sorted(events)
    out = []
    total = 0
    for left,right in zip(points,points[1:]):
        proof.require(left,right)
        total += events[left]
        out.append((left,plus(right,(0,-1)),total))
    total += events[points[-1]]
    if total:
        raise ArithmeticError('finite interval sweep did not close')
    return out


def shell_weight(arm,domain,proof,h=19):
    """1 plus the proximal recovery-band sum of a symbolic shell column.

    Exponent tuples (s,a,b,c) mean c at e=s*d+a*t+b.
    The first-arm domain is above the shallow hole and below the tip.
    """
    lengths = (99,79,23)
    n = lengths[arm-1]
    exponents = [(1,0,1,1),(-1,n,1,-1)]
    exponents += [(1,m,1,-1) for j,m in enumerate(lengths,1) if j!=arm]
    if arm == 1:
        exponents += [(-1,99,0,-1),(-1,99,1,1),
                      (1,0,-h,-1),(1,0,1-h,1)]
    else:
        exponents += [(1,99,0,-1),(1,99,1,1),
                      (1,0,h,-1),(1,0,h+1,1)]
    terms = [(*domain,1)]
    # Recovery exponents E=[23t+2,43t] minus {23t+1+h}.
    for sign,a,b,c in exponents:
        if sign == 1:
            lo,hi,point = (23-a,2-b),(43-a,-b),(23-a,1+h-b)
        else:
            lo,hi,point = (a-43,b),(a-23,b-2),(a-23,b-1-h)
        terms += [(lo,hi,c),(point,point,-c)]
    return restrict(terms,domain,proof)


def substitute_b(y,q,h=19):
    offsets = [((0,0),1),((23,0),-1),((56,0),-1),
               ((23,h+1),1),((23,h),-1),((43,-1),1),
               ((20,-1),-1),((43,-h),-1),((43,-h-1),1)]
    return add(y,*(shift(scale(q,-c),offset) for offset,c in offsets))


def symbolic_coefficients(h=19, proof=None):
    if isinstance(h,int) and (type(h) is not int or h < 3):
        raise ValueError('symbolic coefficient compiler requires h>=3')
    proof = proof if proof is not None else OrderProof()
    # First-arm shell formula assumes this domain is above the shallow hole.
    proof.require((0,h+1),(20,0))
    y = shell_weight(2,((0,1),(79,0)),proof,h)
    w = shell_weight(3,((0,1),(23,0)),proof,h)
    upper = shell_weight(1,((20,0),(99,-1)),proof,h)
    q = shift(upper,(-20,1))
    y = add(y,scale(q,-1))
    q23 = restrict(q,((0,1),(23,0)),proof)
    y = add(y,shift(q23,(56,0)))
    w = add(w,scale(q23,-1))
    qlow = restrict(q,((0,1),(3,1)),proof)
    y = add(y,shift(scale(qlow,-1),(76,-1)))
    w = add(w,shift(scale(qlow,-1),(20,-1)))
    # Reverse low third-arm recovery: -B_r-y_(76t+r-1)-w_(20t+r-1).
    low = restrict(w,((0,1),(3,1)),proof)
    w = add(w,scale(low,-1),shift(scale(low,-1),(20,-1)))
    y = add(substitute_b(y,low,h),shift(scale(low,-1),(76,-1)))
    # The upper paired target u=36t+1-r is solved using a retained r.
    paired = restrict(w,((18,1),(23,0)),proof)
    q = reflect(paired,(36,1))
    w = add(w,scale(paired,-1),scale(q,-1))
    y = add(substitute_b(y,q,h),shift(paired,(56,0)))
    # Remaining forced third depths3t+2..13t have w_r=-B_r.
    lower = restrict(w,((3,2),(13,0)),proof)
    w = add(w,scale(lower,-1))
    y = substitute_b(y,lower,h)
    expected = [((13,1),(16,1),1),((13,1),(13,1),1),
                ((13,h),(13,h),-1)]
    difference = segments(add(w,scale(expected,-1)),((0,1),(23,0)),proof)
    if any(c for lo,hi,c in difference):
        raise ArithmeticError('symbolic middle balance identity failed')
    result = segments(y,((0,1),(79,0)),proof)
    counts = defaultdict(lambda:(0,0))
    for lo,hi,c in result:
        length = plus(minus(hi,lo),(0,1))
        counts[c] = plus(counts[c],length)
    if not proof.verify():
        raise ArithmeticError('affine order proof failed')
    return proof,result,dict(counts)


def certificate():
    proof,_,counts = symbolic_coefficients()
    cone,_,cone_counts = symbolic_coefficients(AffineH(1,0),ConeProof())
    if any(b.slope or (a,b.intercept)!=counts[c] for c,(a,b) in cone_counts.items()):
        raise ArithmeticError('cone counts differ from fixed-hole counts')
    return dict(h=19,minimum_t=proof.minimum_t,
                two_parameter_domain='h>=3 and t>=h+2',
                cone_order_proof_verified=cone.verify(),
                cone_order_inequalities=len(cone.inequalities),
                coefficient_multiplicities={str(c):dict(slope=a,intercept=b)
                                             for c,(a,b) in sorted(counts.items())},
                affine_order_inequalities=len(proof.inequalities),
                order_proof_verified=proof.verify(),
                existence_decided=False)


def distance_bounds(t, sigma, h=19):
    if (type(t) is not int or t < 17 or type(h) is not int or not 3<=h<=t-2
            or type(sigma) is not int or sigma not in (-1,1)):
        raise ValueError('require t>=17, 3<=h<=t-2 and centre +/-1')
    return dict(all_positive=(3*t-18-sigma+3)//4,
                all_negative=(3*t-18+sigma+3)//4)


def balance_tight_word(t, sigma, constant, h=19):
    """Attain the distance bound for balance alone at odd t>=21.

    Neither other signs' literalness nor homometry is asserted.
    """
    import balance_elimination as be
    bounds = distance_bounds(t,sigma,h)
    if t % 2 != 1 or type(constant) is not int or constant not in (-1,1):
        raise ValueError('tight construction requires odd t and constant +/-1')
    coefficients = be.balance_coefficients(t,h)
    k = bounds['all_positive' if constant==1 else 'all_negative']
    changed = set(sorted(coefficients,key=lambda j:(coefficients[j],j))[:k])
    y = {j:-constant if j in changed else constant for j in coefficients}
    baseline = sigma+sum(c*y[j] for j,c in coefficients.items())
    middle = be.balanced_middle(t,h,baseline)
    if middle is None:
        raise ArithmeticError('closed distance bound is not balance-attainable')
    total = baseline+sum(c*middle[r] for r,c in be.middle_balance_weights(t,h).items())
    if total:
        raise ArithmeticError('constructed middle does not balance')
    return y,middle


def resistant_check(k):
    if type(k) is not int or k < 1:
        raise ValueError('require integer k>=1')
    import balance_elimination as be
    t = 2660*k+1
    records = []
    for sigma in (-1,1):
        for constant in (-1,1):
            y,middle = balance_tight_word(t,sigma,constant)
            coefficients = be.balance_coefficients(t,19)
            baseline = sigma+sum(c*y[j] for j,c in coefficients.items())
            import full_shorter_coupling as fc
            actual = fc.linear_completion(t,19,sigma,y,middle)
            records.append(dict(centre=sigma,constant=constant,
                                changed=sum(s!=constant for s in y.values()),
                                baseline=baseline,
                                balanced_total=sum(actual.values()),
                                nonliteral_forced_signs=sum(s not in (-1,1) for s in actual.values())))
    return dict(k=k,t=t,balance_only_tight_controls=records,
                full_middle_equations_checked=False,existence_decided=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-scale',type=int,metavar='K',
                        help='also construct balance-only tight controls at t=2660K+1')
    args = parser.parse_args()
    result = certificate()
    if args.check_scale is not None:
        result['resistant_check'] = resistant_check(args.check_scale)
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
