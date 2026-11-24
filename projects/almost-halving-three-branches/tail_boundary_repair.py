"""An exact partial-shell repair, not a homometric colouring.

Preserves the joint residue totals, changes eight retained seed signs,
and repairs the first eighteen and last seventy-nine distance shells.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json

from unrestricted_insertion_lift import BASE, FRONTIER, prefix_realization, distance_difference


CONFLICTS = (61, 63, 65, 67, 69, 71, 73, 75)


def local_constants():
    seed = [[0 if ch == '0' else 1 if ch == '+' else -1 for ch in w]
            for w in FRONTIER]
    return [-1+sum(seed[0][:d-1])-sum(seed[0][98-d:98])
            -sum(seed[1][-d:])-sum(seed[2][-d:])-seed[0][18-d]
            for d in range(1, 19)]


def start_words():
    """Exact solution of x_d=K_d+sum_(j<d)(y_j+z_j), 1<=d<=18."""
    constants = local_constants()
    assert constants[0] == -1
    first, second, third = [-1]*18, [], []
    for old, new in zip(constants, constants[1:]):
        difference = old-new
        assert difference in (0, -2)
        second.append(1 if difference == 0 else -1)
        third.append(-1)
    return first, second, third


def boundary_count(shells=18):
    """Count all branch-prefix choices; the first-arm prefix is then forced."""
    if type(shells) is not int or not 1 <= shells <= 18:
        raise ValueError('shells must be an integer in 1..18')
    states = {0: 1}
    for constant in local_constants()[1:shells]:
        following = Counter()
        for running, count in states.items():
            for step, multiplicity in ((-2, 1), (0, 2), (2, 1)):
                if constant+running+step in (-1, 1):
                    following[running+step] += count*multiplicity
        states = following
    return sum(states.values())


def class_totals(words):
    """Negative totals in each arm interval/residue, plus the tiny prefix."""
    result = Counter()
    for i, word in enumerate(words):
        for d, sign in enumerate(word, 1):
            if sign == -1:
                key = (i, 'tiny', d) if i == 0 and d < 19 else (i, 'large', d % 2660)
                result[key] += 1
    return result


def construct(k=1, choice=0):
    """choice's eight bits choose which endpoint to change in each conflict.

    Every change is paired with an opposite-sign inserted donor in the same
    interval/residue, away from every boundary used in the local proof.
    """
    if type(choice) is not int or not 0 <= choice < 256:
        raise ValueError('choice must be an integer in 0..255')
    words = prefix_realization(k)
    before = class_totals(words)
    changes, exchanges = [], []

    def exchange(arm, depth, desired, retained=False):
        word = words[arm]
        current = word[depth-1]
        if current == desired:
            return
        assert current == -desired
        cut = 19 if arm == 0 else 0
        insertion_end = cut+2660*k*BASE[arm]
        donor = cut+20+(depth-(cut+20)) % 2660
        while donor <= insertion_end-19:
            if word[donor-1] == desired:
                break
            donor += 2660
        else:
            raise ArithmeticError('no interior same-residue donor')
        word[depth-1], word[donor-1] = desired, current
        exchanges.append((arm+1, depth, donor))
        if retained:
            changes.append((arm+1, depth))

    for index, r in enumerate(CONFLICTS):
        arm = (choice >> index) & 1
        old_depth = 99-r if arm == 0 else 80-r
        exchange(arm, old_depth+2660*k*BASE[arm], -1, retained=True)
    x, y, z = start_words()
    for arm, cut, signs in ((0, 19, x), (1, 0, y), (2, 0, z)):
        for j, desired in enumerate(signs, 1):
            exchange(arm, cut+j, desired)
    assert class_totals(words) == before
    assert -1+sum(map(sum, words)) == 0
    return words, {'retained_seed_changes': changes, 'exchanges': exchanges,
                   'joint_class_totals_preserved': True}


def top_differences(words):
    """Directly enumerate the 3160 actual cross-arm pairs in the top shells."""
    a, b, _ = map(len, words)
    counts = Counter()
    for r in range(1, 80):
        for s in range(79):
            if r+s <= 79:
                depth1, depth2 = a-r, b-s
                counts[depth1+depth2] += (words[0][depth1-1]+words[1][depth2-1])//2
    return {d: n for d, n in counts.items() if n}


def report(k=1, choice=0, check_local=True):
    words, evidence = construct(k, choice)
    lengths = tuple(map(len, words))
    top = top_differences(words)
    local = {d: distance_difference(lengths, 19, -1, words, d) for d in range(1, 19)} if check_local else None
    # A remaining, genuinely untested-by-the-construction shell is reported.
    next_difference = distance_difference(lengths, 19, -1, words, 20)
    return {'k': k, 'choice': choice, 'lengths': lengths,
            'retained_seed_changes': len(evidence['retained_seed_changes']),
            'joint_class_totals_preserved': evidence['joint_class_totals_preserved'],
            'top_79_shells_equal': not top, 'first_18_differences': local,
            'distance_20_difference': next_difference,
            'admissible_local_prefix_pairs': boundary_count(),
            'full_homometry_claimed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--k', type=int, default=1)
    parser.add_argument('--choice', type=int, default=0)
    args = parser.parse_args()
    try:
        result = report(args.k, args.choice)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
