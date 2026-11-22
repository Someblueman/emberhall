"""Exact family-wide coupling of literal and repeated tripod sign words.

A polynomial identity checks every repetition count, including both endpoints.
The target template probe is a restricted obstruction, not an existence answer.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path

FORMAT = "tripod-coupled-words-v1"
PROBE_FORMAT = "tripod-coupled-template-obstruction-v1"


def compile_shape(period, arms):
    """Return all coefficient rows of (1-z**period) E(z, v).

    Each arm is a list of (kind, length), where kind is literal or repeat.
    v represents z**(period*n); each letter gets its own sign variable.
    """
    if type(period) is not int or period < 1:
        raise ValueError("period must be a positive integer")
    if len(arms) != 3:
        raise ValueError("three arm shapes required")
    rows = defaultdict(dict)
    numerators, lengths, growth = [], [], []
    variables = [(0, 0, 0)]  # centre

    def add(poly, degree, index, value):
        row = poly.setdefault(degree, {})
        row[index] = row.get(index, 0) + value
        if not row[index]:
            del row[index]

    for arm, segments in enumerate(arms, 1):
        numerator = {}
        offset, repeats = (2 if arm < 3 else 1), 0
        for segment, (kind, size) in enumerate(segments):
            if kind not in ("literal", "repeat") or type(size) is not int or size < 0:
                raise ValueError("invalid segment shape")
            if kind == "repeat" and size != period:
                raise ValueError("all repeated blocks must have the stated period")
            for letter in range(size):
                index = len(variables)
                variables.append((arm, segment, letter))
                degree = (offset + letter, repeats)
                add(numerator, degree, index, 1)
                other = ((degree[0] + period, repeats) if kind == "literal"
                         else (degree[0], repeats + 1))
                add(numerator, other, index, -1)
            if kind == "literal":
                offset += size
            else:
                repeats += 1
        lengths.append(offset - 1)
        growth.append(repeats)
        numerators.append(numerator)
    a, b, c = lengths
    if not a > b > c >= 1 or not growth[0] >= growth[1] >= growth[2]:
        raise ValueError("lengths must remain strictly decreasing for every repetition count")

    def shifted(poly, dz, dv, factor):
        for (z, v), row in poly.items():
            for index, value in row.items():
                add(rows, (z + dz, v + dv), index, factor * value)

    centre = {(0, 0): {0: 1}, (period, 0): {0: -1}}
    shifted(centre, 1, 0, 2)
    shifted(centre, 0, 0, -1)
    for length, count in zip(lengths, growth):
        shifted(centre, length, count, -1)
    for arm, numerator in enumerate(numerators):
        local = ((1, 1), (-1, 1), (-2, -1)) if arm < 2 else ((1, 2), (0, -1))
        for dz, factor in local:
            shifted(numerator, dz, 0, factor)
        for other in range(3):
            if other != arm:
                shifted(numerator, lengths[other], growth[other], -1)
        # D(z^-1) = -z^-period D(z); this cancels the minus on the reversal.
        for (z, v), row in numerator.items():
            for index, value in row.items():
                add(rows, (lengths[arm] + period - z, growth[arm] - v), index, value)
    return {degree: row for degree, row in sorted(rows.items()) if row}, variables, lengths, growth


def parse_word(saved):
    if type(saved) is not dict or set(saved) != {"format", "centre", "period", "arms"}:
        raise ValueError("unexpected word certificate fields")
    if saved["format"] != FORMAT or type(saved["centre"]) is not int or saved["centre"] not in (-1, 1):
        raise ValueError("invalid word format or centre sign")
    arms = saved["arms"]
    if type(arms) is not list or len(arms) != 3:
        raise ValueError("three arm segment lists required")
    shapes, values = [], [saved["centre"]]
    for segments in arms:
        if type(segments) is not list:
            raise ValueError("arm must be a segment list")
        shape = []
        for segment in segments:
            if type(segment) is not dict or len(segment) != 1:
                raise ValueError("segment must contain exactly literal or repeat")
            kind, word = next(iter(segment.items()))
            if kind not in ("literal", "repeat") or type(word) is not str or set(word) - {"+", "-"}:
                raise ValueError("segment must be a literal sign word")
            shape.append((kind, len(word)))
            values.extend(1 if ch == "+" else -1 for ch in word)
        shapes.append(shape)
    rows, variables, lengths, growth = compile_shape(saved["period"], shapes)
    return rows, variables, lengths, growth, values


def verify_word(saved):
    rows, variables, lengths, growth, values = parse_word(saved)
    for degree, row in rows.items():
        value = sum(coefficient * values[index] for index, coefficient in row.items())
        if value:
            raise ValueError(f"family coefficient {degree} is {value}, not zero")
    # For n above this bound, different powers of v cannot overlap in z.
    z_values = [z for z, _ in rows]
    span = max(z_values, default=0) - min(z_values, default=0)
    return {"valid": True, "base_lengths": lengths,
            "growth_per_repeat": [saved["period"] * r for r in growth],
            "sign_variables": len(variables), "coefficient_rows": len(rows),
            "separating_repeat_count": span // saved["period"] + 1,
            "all_nonnegative_repetitions": True, "scope": "fixed holes (1,1),(2,1)"}


def expand_word(saved, count):
    if type(count) is not int or count < 0:
        raise ValueError("repetition count must be a nonnegative integer")
    parse_word(saved)
    words = ["".join(word * (count if kind == "repeat" else 1)
                     for segment in segments for kind, word in segment.items())
             for segments in saved["arms"]]
    return words


def audit_word(saved, count, max_vertices=1024):
    """Count unordered original-tree distances, independently of shell rows."""
    if type(count) is not int or count < 0:
        raise ValueError("repetition count must be a nonnegative integer")
    _, _, base, growth, _ = parse_word(saved)
    lengths = [a + saved["period"] * r * count for a, r in zip(base, growth)]
    if 1 + sum(lengths) > max_vertices:
        raise ValueError("direct distance audit exceeds the vertex limit")
    words = expand_word(saved, count)
    groups = {1: [(0, 0)] if saved["centre"] == 1 else [],
              -1: [(0, 0)] if saved["centre"] == -1 else []}
    for arm, word in enumerate(words, 1):
        for depth, sign in enumerate(word, 2 if arm < 3 else 1):
            groups[1 if sign == "+" else -1].append((arm, depth))
    profiles = []
    for signs in (1, -1):
        profile = Counter()
        for (arm, depth), (other, distance) in combinations(groups[signs], 2):
            profile[abs(depth - distance) if arm == other else depth + distance] += 1
        profiles.append(profile)
    target = (1 + sum(lengths)) // 2 - 1
    if (set(groups[1]) & set(groups[-1]) or len(groups[1]) != len(groups[-1])
            or len(groups[1]) < target or profiles[0] != profiles[1]):
        raise ValueError("original-tree balance, size or distance audit failed")
    return {"lengths": lengths, "size": len(groups[1]), "target": target,
            "pairs_per_set": sum(profiles[0].values()), "equal_distance_multisets": True}


def parity_obstruction(rows):
    """Return an XOR certificate, or None; feasible parity does not solve signs."""
    basis = {}
    for number, row in enumerate(rows.values()):
        total = sum(row.values())
        if total % 2:
            return {"odd_row": number}
        mask = sum(1 << i for i, a in row.items() if a % 2)
        rhs, used = (total // 2) % 2, 1 << number
        while mask:
            pivot = (mask & -mask).bit_length() - 1
            if pivot not in basis:
                basis[pivot] = mask, rhs, used
                break
            old, value, indices = basis[pivot]
            mask, rhs, used = mask ^ old, rhs ^ value, used ^ indices
        else:
            if rhs:
                return {"xor_rows": [i for i in range(len(rows)) if used >> i & 1]}
    return None


def target_probe():
    """One exact global template obstruction; no search and no cutoff."""
    lengths, period, cuts = (347, 187, 131), 24, (173, 93, 65)
    shapes = [[("literal", cut), ("repeat", period),
               ("literal", length - (arm < 2) - cut)]
              for arm, (length, cut) in enumerate(zip(lengths, cuts))]
    rows, variables, _, _ = compile_shape(period, shapes)
    contradiction = parity_obstruction(rows)
    if contradiction is None:
        raise AssertionError("expected target-template parity obstruction disappeared")
    # Independently replay the selected rows instead of trusting elimination.
    selected = (contradiction.get("xor_rows") or [contradiction["odd_row"]])
    if "xor_rows" in contradiction:
        mask, rhs = 0, 0
        ordered = list(rows.values())
        for number in selected:
            row = ordered[number]
            mask ^= sum(1 << i for i, a in row.items() if a % 2)
            rhs ^= (sum(row.values()) // 2) % 2
        if mask or rhs != 1:
            raise AssertionError("invalid global XOR contradiction")
    return {"format": PROBE_FORMAT, "base_lengths": list(lengths),
            "period": period, "prefix_lengths": list(cuts),
            "sign_variables": len(variables), "coefficient_rows": len(rows),
            "contradiction": contradiction, "template_family_impossible": True,
            "target_existence_decided": False, "all_hole_supports_excluded": False}


def control():
    # Previously known (5+4n,4,2) family, credited in the accompanying note.
    return {"format": FORMAT, "centre": 1, "period": 4,
            "arms": [[{"repeat": "--++"}, {"literal": "--++"}],
                     [{"literal": "---"}], [{"literal": "++"}]]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--control", action="store_true")
    mode.add_argument("--target-template", action="store_true")
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--audit-repeat", type=int)
    args = parser.parse_args(argv)
    try:
        saved = (json.loads(args.verify.read_text()) if args.verify else
                 target_probe() if args.target_template else control())
        if saved.get("format") == PROBE_FORMAT:
            if args.audit_repeat is not None:
                raise ValueError("a template obstruction is not a literal word")
            if saved != target_probe():
                raise ValueError("altered template obstruction")
            report = {k: v for k, v in saved.items() if k != "contradiction"}
            report["contradiction_rows"] = len(saved["contradiction"].get("xor_rows", [0]))
        else:
            report = verify_word(saved)
            if args.audit_repeat is not None:
                report["original_tree_audit"] = audit_word(saved, args.audit_repeat)
        if args.write:
            args.write.write_text(json.dumps(saved, indent=2) + "\n")
        print(json.dumps(report, sort_keys=True))
        return 0
    except (ValueError, OSError, TypeError, AttributeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
