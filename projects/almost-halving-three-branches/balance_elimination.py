"""Exact balance-only elimination for the tip and shallow-hole family.

Passing this test does not solve the middle equations or prove homometry.
"""
import argparse
import json
import full_shorter_coupling as fc


def middle_balance_weights(t, h):
    fc.validate(t, h)
    if h > 2*t-1:
        raise ValueError('balance elimination requires h<=2t-1')
    a = 13*t+1
    weights = dict.fromkeys(range(a, 16*t+2), 1)
    if h:
        weights[a] += 1
        weights[a+h-1] -= 1
    return {r:c for r,c in weights.items() if c}


def balance_coefficients(t, h):
    """Transpose the prescribed recovery to S=sigma+dot(y,c)+dot(m,w).

    Exact integer elimination; linear time in the number of arm vertices.
    """
    middle_balance_weights(t,h)
    lengths,holes = fc.geometry(t,h)
    def weight(vertex):
        return 1 + sum(c for e,c in fc.shell_column(lengths,holes,vertex).items()
                       if 23*t+2 <= e <= 43*t and e != 23*t+1+h)
    y = {j:weight((2,j)) for j in range(1,79*t+1)}
    w = {r:weight((3,r)) for r in range(1,23*t+1)}
    for j in range(1,79*t+1):
        q = weight((1,20*t+j-1))
        y[j] -= q
        if j <= 23*t:
            y[56*t+j] += q
            w[j] -= q
        if j <= 3*t+1:
            y[76*t+j-1] -= q
            w[20*t+j-1] -= q
    # Reverse the triangular construction order, substituting each target
    # out of the balance functional rather than forming any candidate.
    for r in reversed(range(1,3*t+2)):
        q = w.pop(r)
        terms = fc.low_terms(t,h,r)
        terms.pop((3,r))
        for (arm,d),c in terms.items():
            (y if arm==2 else w)[d] -= q*c
    for r in reversed(range(3*t+2,18*t+1)):
        target = r if r <= 13*t else 36*t-r+1
        q = w.pop(target)
        terms = fc.se.coupling_terms(t,h,r)
        terms.pop((3,target))
        for (arm,d),c in terms.items():
            (y if arm==2 else w)[d] -= q*c
    if {r:c for r,c in w.items() if c} != middle_balance_weights(t,h):
        raise ArithmeticError('balance dual disagrees with proved middle identity')
    return y


def constant_word_distance_bounds(t, h, sigma, coefficients):
    """Necessary Hamming distances from the two constant second words.

    The largest available improvements bound what any given number of
    flips can achieve. Reaching that bound need not pass other equations.
    """
    n = 3*t+1
    result = {}
    for sign,label in ((1,'all_positive'),(-1,'all_negative')):
        baseline = sigma + sign*sum(coefficients.values())
        direction = 1 if baseline >= 0 else -1
        needed = max(0,(abs(baseline)-n+1)//2)
        capacities = sorted((direction*sign*c for c in coefficients.values()
                             if direction*sign*c > 0),reverse=True)
        total = count = 0
        for capacity in capacities:
            if total >= needed:
                break
            total += capacity
            count += 1
        result[label] = count if total >= needed else None
    return result


def balance_window(t, h, baseline):
    """Exact attainable total sums for independently literal middle values."""
    weights = middle_balance_weights(t, h)
    if type(baseline) is not int:
        raise ValueError('baseline must be an integer')
    radius = sum(weights.values())
    return dict(baseline=baseline, radius=radius,
                minimum_total=baseline-radius, maximum_total=baseline+radius,
                total_parity=(baseline+radius) % 2,
                balance_excluded=abs(baseline)>radius or (baseline+radius)%2 != 0,
                middle_equations_checked=False, existence_decided=False,
                all_hole_placements_covered=False)


def balanced_middle(t, h, baseline):
    """Construct literal middle values balancing the linear candidate only.

    Its other forced signs may be nonliteral and shell equations may fail.
    """
    result = balance_window(t, h, baseline)
    if result['balance_excluded']:
        return None
    weights = middle_balance_weights(t, h)
    middle = dict.fromkeys(range(13*t+1, 18*t+1), -1)
    # From all minus, flipping weight c adds 2c. At most one weight is 2;
    # at least two unit weights bridge all possible subset sums.
    required = (result['radius']-baseline)//2
    double = next((r for r,c in weights.items() if c == 2), None)
    units = [r for r,c in weights.items() if c == 1]
    if required > len(units):
        middle[double] = 1
        required -= 2
    for r in units[:required]:
        middle[r] = 1
    return middle


def joint_reflected_balance(t, h, baseline, forcing):
    """Exactly eliminate literal middle signs from balance and differences.

    Covers only the reflected-difference subsystem, not all middle rows.
    """
    balance_window(t,h,baseline)
    import second_word_forcing as sw
    reflected = sw.interval_constraint(t,h,forcing)
    weights = {r-13*t:c for r,c in middle_balance_weights(t,h).items()}
    outcomes = []
    reflection = 7*t-2*h-1
    for endpoint_sum in reflected['reflected_endpoint_sums']:
        pairs = {}
        prefix = 0
        for v in range(2*t,5*t+1):
            prefix += forcing[v]-forcing[7*t-v]
            a = v-h
            pair = tuple(sorted((a,reflection-a)))
            required = endpoint_sum-prefix
            if pair in pairs and pairs[pair] != required:
                raise ArithmeticError('inconsistent reflected pair requirements')
            pairs[pair] = required
        fixed = 0
        free_weights = []
        covered = set()
        for (a,b),required in pairs.items():
            covered.update((a,b))
            if a == b:
                fixed += weights.get(a,0)*(required//2)
            elif required:
                fixed += (weights.get(a,0)+weights.get(b,0))*(required//2)
            else:
                free_weights.append(abs(weights.get(a,0)-weights.get(b,0)))
        free_weights.extend(c for a,c in weights.items() if a not in covered)
        units = free_weights.count(1)
        doubles = free_weights.count(2)
        radius = units+2*doubles
        step = 2 if units else (4 if doubles else 0)
        offset = baseline+fixed
        feasible = (abs(offset)<=radius and
                    ((offset+radius)%step==0 if step else offset==0))
        outcomes.append(dict(endpoint_sum=endpoint_sum, fixed_contribution=fixed,
                             radius=radius, step=step, balance_feasible=feasible))
    return dict(joint_excluded=not any(o['balance_feasible'] for o in outcomes),
                endpoint_cases=outcomes, full_middle_equations_checked=False,
                existence_decided=False)


def second_word_balance(payload, joint=False):
    t,h,sigma = payload['t'],payload['h'],payload['centre']
    middle_balance_weights(t,h)
    if type(sigma) is not int or sigma not in ((-1,1) if h else (0,)):
        raise ValueError('centre disagrees with holes')
    word = payload['arm2']
    if not isinstance(word,str) or len(word)!=79*t or set(word)-set('+-'):
        raise ValueError('require a literal second word of length 79t')
    y = {i:1 if s=='+' else -1 for i,s in enumerate(word,1)}
    coefficients = balance_coefficients(t,h)
    baseline = sigma + sum(c*y[r] for r,c in coefficients.items())
    result = balance_window(t,h,baseline)
    result['necessary_distance_from_constant_words'] = constant_word_distance_bounds(
        t,h,sigma,coefficients)
    if joint:
        if h > 2*t-2:
            raise ValueError('joint reflected check requires h<=2t-2')
        zero = dict.fromkeys(range(13*t+1,18*t+1),0)
        residual = fc.shell_rows(*fc.geometry(t,h),
                                fc.linear_completion(t,h,sigma,y,zero))
        forcing = {i:residual.get(92*t+1+i,0) for i in range(1,5*t+1)}
        result['joint_reflected_balance'] = joint_reflected_balance(t,h,baseline,forcing)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='JSON input file, or - for standard input')
    parser.add_argument('--joint', action='store_true',
                        help='also eliminate the reflected-difference subsystem')
    args = parser.parse_args()
    import sys
    with (sys.stdin if args.input=='-' else open(args.input)) as handle:
        payload = json.load(handle)
    print(json.dumps(second_word_balance(payload,joint=args.joint),sort_keys=True))


if __name__ == '__main__':
    main()
