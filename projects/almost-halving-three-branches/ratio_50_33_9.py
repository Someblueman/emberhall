"""Terminal-shell reconstruction for arbitrary near-partitions of a tripod.

See RATIO_50_33_9.md. The universal target remains open. Only t=1 and t=2
have witnesses here; the necessary tail recurrence applies at every scale.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from published_cases import check_pair, validate_lengths, validate_vertices


def _parameter(t: int) -> int:
    if type(t) is not int or t < 1:
        raise ValueError("t must be a positive integer")
    return t


def family_bound(t: int) -> dict:
    """Uniform analytic bound, without allocating a tree or claiming existence."""
    t = _parameter(t)
    return {"t": t, "lengths": [50*t, 33*t, 9*t], "target": 46*t-1,
            "maximum_omissions": 3, "minimum_reconstructed_tip_levels": 24*t-3,
            "scope": "every target-or-larger homometric pair, with arbitrary omissions",
            "existence_proved_here": t in (1, 2), "universal_target_proved": False}


def reconstruct_tail(long_signs: list[int], long_holes: list[int],
                     middle_holes: list[int]) -> list[int]:
    """Solve S+Q=(1-z)(S*H_middle+Q*H_long) below the given cutoff.

    Depths are offsets from retained tips, so holes must have positive offsets.
    This algebraic operation also accepts integer words that are not signs.
    """
    cutoff = len(long_signs)
    for holes in (long_holes, middle_holes):
        if (len(holes) != len(set(holes))
                or any(type(h) is not int or not 1 <= h < cutoff for h in holes)):
            raise ValueError("holes must be distinct positive offsets below the cutoff")
    if any(type(s) is not int for s in long_signs):
        raise ValueError("the long word must contain integers")
    result = []
    for k, sign in enumerate(long_signs):
        value = -sign
        for h in middle_holes:
            if k >= h:
                value += long_signs[k-h]
            if k > h:
                value -= long_signs[k-h-1]
        for h in long_holes:
            if k >= h:
                value += result[k-h]
            if k > h:
                value -= result[k-h-1]
        result.append(value)
    return result


def terminal_certificate(lengths: object, left: object, right: object) -> dict:
    """Necessary high-distance equations for a literal pair; not a full check."""
    lengths = validate_lengths(lengths)
    left = validate_vertices(lengths, left)
    right = validate_vertices(lengths, right)
    if set(left) & set(right):
        raise ValueError("the two sets overlap")
    if len(left) != len(right):
        raise ValueError("the two sets have different sizes")
    signs = dict.fromkeys(left, 1) | dict.fromkeys(right, -1)
    tips = [max((d for (i, d) in signs if i == arm), default=0)
            for arm in range(1, 4)]
    if any(tip == 0 for tip in tips):
        raise ValueError("each arm must have a retained vertex")
    arms = sorted(range(1, 4), key=lambda i: (-tips[i-1], i))
    a, b, c = (tips[i-1] for i in arms)
    cutoff = b-c
    if cutoff <= 0:
        raise ValueError("the second retained arm must exceed the third")
    long_word = [signs.get((arms[0], a-k), 0) for k in range(cutoff)]
    middle_word = [signs.get((arms[1], b-k), 0) for k in range(cutoff)]
    long_holes = [k for k, sign in enumerate(long_word) if not sign]
    middle_holes = [k for k, sign in enumerate(middle_word) if not sign]
    predicted = reconstruct_tail(long_word, long_holes, middle_holes)
    failures = [k for k, (actual, forced) in enumerate(zip(middle_word, predicted))
                if actual != forced]
    return {"arms_long_middle_short": arms, "retained_tips": [a, b, c],
            "cutoff": cutoff, "long_holes": long_holes, "middle_holes": middle_holes,
            "predicted_middle_signs": predicted, "failure_offsets": failures,
            "necessary_condition_passes": not failures,
            "sufficient_for_homometry": False}


def finite_witness(t: int) -> dict:
    """Two exact controls, not an extrapolation to unproved scales."""
    t = _parameter(t)
    if t == 1:
        # Recovered by solving the full signed-shell equations, without reflection.
        words = (
            "+--+-++++-+--+-0+----++++++----++----++++++----++0",
            "-++++------++++--++++------++++--",
            "--++++--0",
        )
        left, right = [], [(0, 0)]
        for arm, word in enumerate(words, 1):
            for depth, sign in enumerate(word, 1):
                if sign != "0":
                    (left if sign == "+" else right).append((arm, depth))
    elif t == 2:
        # Rook's already-proved r|b construction; copied as an explicit control.
        r, b, c = 33, 66, 18
        retained_c = c-(r+c) % 2
        length = r+retained_c
        p = [1 if ((j-length//2-1)//r) % 2 == 0 else -1
             for j in range(1, length+1)]
        left, right = [], []
        for j, sign in enumerate(p, 1):
            vertex = ((1, r-j) if j < r else (0, 0) if j == r else (3, j-r))
            (left if sign == 1 else right).append(vertex)
        for j in range(1, b+1):
            sign = p[r-1-(j-1) % r]
            (left if sign == 1 else right).append((1, r+j))
            (right if sign == 1 else left).append((2, j))
    else:
        raise ValueError("this module has witnesses only for t=1 and t=2; other scales remain open")
    lengths = [50*t, 33*t, 9*t]
    checked = check_pair(lengths, left, right)
    if not checked["homometric"] or checked["size"] != 46*t-1:
        raise ArithmeticError("stored control failed its original-tree check")
    return {"t": t, "lengths": lengths, "left": left, "right": right, **checked}


def check_document(document: object) -> dict:
    if not isinstance(document, dict):
        raise ValueError("a witness must be a JSON object")
    lengths, left, right = (document.get(k) for k in ("lengths", "left", "right"))
    checked = check_pair(lengths, left, right)
    return {**checked, "terminal": terminal_certificate(lengths, left, right)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--lemma", type=int, metavar="T")
    mode.add_argument("--witness", type=int, metavar="T")
    mode.add_argument("--check", metavar="FILE", help="JSON witness; '-' reads stdin")
    args = parser.parse_args()
    try:
        if args.lemma is not None:
            result = family_bound(args.lemma)
        elif args.witness is not None:
            result = finite_witness(args.witness)
        else:
            data = sys.stdin.read() if args.check == "-" else Path(args.check).read_text()
            result = check_document(json.loads(data))
        print(json.dumps(result, sort_keys=True))
        return 0 if result.get("homometric", True) else 1
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
