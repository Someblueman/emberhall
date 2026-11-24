#!/usr/bin/env python3
"""Necessary second-word constraints from reflected middle rows; no existence claim."""
import argparse
import json


def interval_constraint(t, h, forcing):
    """All-scale literal-sign bound, in relative middle coordinates 1..5t.

    Every interval [u,v] in [2t,5t] must have
    abs(sum(b_i-b_(7t-i), i=u..v)) <= 4.
    The maximum absolute interval sum is the prefix-sum range.
    """
    if type(t) is not int or t < 1 or type(h) is not int or not 0 <= h <= 2*t-2:
        raise ValueError('require t>=1 and 0<=h<=2t-2')
    if set(forcing) != set(range(1,5*t+1)) or any(type(v) is not int for v in forcing.values()):
        raise ValueError('require integer forcing at every coordinate 1..5t')
    total = 0
    candidates = {-2,0,2}
    low = high = (0,2*t-1)
    for i in range(2*t,5*t+1):
        total += forcing[i]-forcing[7*t-i]
        fixed = 2*i == 7*t-1
        candidates = {c for c in candidates
                      if c-total in ((-2,2) if fixed else (-2,0,2))}
        if total < low[0]: low = (total,i)
        if total > high[0]: high = (total,i)
    spread = high[0]-low[0]
    a,b = sorted((low[1],high[1]))
    return dict(excluded=not candidates, maximum_interval_magnitude=spread,
                reflected_endpoint_sums=sorted(candidates),
                interval=[a+1,b] if a != b else None,
                all_scale_necessary_constraint=True, existence_decided=False,
                all_hole_placements_covered=False)


def second_word_constraint(payload):
    # Use the reconciled full-shorter API (Tern 45a6638), which preserves
    # the earlier forcing compiler alongside the newer coupling functions.
    import full_shorter_coupling as fc
    t,h,sigma=payload['t'],payload['h'],payload['centre']
    if type(t) is not int or t<1 or type(h) is not int or not 0<=h<=2*t-2:
        raise ValueError('require t>=1 and 0<=h<=2t-2')
    if type(sigma) is not int or sigma not in ((-1,1) if h else (0,)):
        raise ValueError('centre disagrees with holes')
    word=payload['arm2']
    if not isinstance(word,str) or len(word)!=79*t or set(word)-set('+-'):
        raise ValueError('require a literal second word of length 79t')
    y={i:1 if ch=='+' else -1 for i,ch in enumerate(word,1)}
    zero=dict.fromkeys(range(13*t+1,18*t+1),0)
    baseline=fc.linear_completion(t,h,sigma,y,zero)
    residual=fc.shell_rows(*fc.geometry(t,h),baseline)
    b={i:residual.get(92*t+1+i,0) for i in range(1,5*t+1)}
    result=interval_constraint(t,h,b)
    result['individual_middle_row_bound_passed']=all(abs(v)<=4 for v in b.values())
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',help='JSON input file, or - for standard input')
    args=parser.parse_args()
    import sys
    with (sys.stdin if args.input=='-' else open(args.input)) as handle:
        payload=json.load(handle)
    print(json.dumps(second_word_constraint(payload),sort_keys=True))


if __name__=='__main__':main()
