"""Exact full-shell transfer with bounded width for fixed arm differences.

See WORD_FRONTIER.md. A resource refusal is never a nonexistence result.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class System:
    lengths: tuple[int, int, int]
    vertices: list[tuple[int, int]]
    layers: list[int]
    rows: dict[int, dict[int, int]]
    last: list[int]
    ending: list[list[dict[int, int]]]


def lengths_checked(lengths):
    if (not isinstance(lengths, (list, tuple)) or len(lengths) != 3
            or any(type(n) is not int for n in lengths)):
        raise ValueError("three integer lengths required")
    a, b, c = lengths
    if not a > b > c >= 1:
        raise ValueError("require a > b > c >= 1")
    return a, b, c


def build_system(lengths):
    """Compile E=0, including balance, without using the completion module."""
    a, b, c = lengths_checked(lengths)

    def layer(vertex):
        _, depth = vertex
        return min(depth, c - depth) if 0 < depth < c else 0

    vertices = [(0, 0)] + [(arm, depth)
        for arm, length in enumerate((a, b, c), 1)
        for depth in range(2 if arm < 3 else 1, length + 1)]
    vertices.sort(key=lambda v: (layer(v), v))
    rows = {}

    def add(degree, index, coefficient):
        row = rows.setdefault(degree, {})
        row[index] = row.get(index, 0) + coefficient
        if not row[index]:
            del row[index]

    for index, (arm, depth) in enumerate(vertices):
        if arm == 0:
            for degree, value in ((0, -1), (1, 2), (a, -1), (b, -1), (c, -1)):
                add(degree, index, value)
            continue
        local = ((1, 1), (-1, 1), (-2, -1)) if arm < 3 else ((1, 2), (0, -1))
        for shift, value in local:
            add(depth + shift, index, value)
        add(lengths[arm - 1] - depth, index, -1)
        for other, length in enumerate(lengths, 1):
            if other != arm:
                add(depth + length, index, -1)
    rows = {degree: row for degree, row in sorted(rows.items()) if row}
    last = list(range(len(vertices)))
    ending = [[] for _ in vertices]
    for row in rows.values():
        end = max(row)
        ending[end].append(row)
        for index in row:
            last[index] = max(last[index], end)
    return System((a, b, c), vertices, [layer(v) for v in vertices], rows, last, ending)


def schedule(system):
    """Yield deterministic separators before and after each assigned sign."""
    active = []
    for index, last in enumerate(system.last):
        after = [old for old in active if system.last[old] > index]
        if last > index:
            after.append(index)
        yield index, active, after
        active = after


def describe(system):
    a, b, c = system.lengths
    radius = max(a + b - 2 * c, a - c + 1, 2)
    tail = a + b - 2 * c + 4  # three tails including depth c, plus centre
    bound = tail + 6 * (2 * radius + 1)
    width = max((len(before) + 1 for _, before, _ in schedule(system)), default=0)
    span = max((max(system.layers[i] for i in row)
                - min(system.layers[i] for i in row) for row in system.rows.values()), default=0)
    if span > 2 * radius or width > bound:
        raise AssertionError("folded separator bound violated")
    return {"lengths": list(system.lengths), "variables": len(system.vertices),
            "equations": len(system.rows), "radius_bound": radius,
            "maximum_equation_layer_span": span, "assignment_width": width,
            "uniform_width_bound": bound, "all_distance_equations": True,
            "existence_decided": False}


def solve(system, *, max_width=20, max_states=100000):
    """Exact decision/count transfer. Centre +1 removes global reversal.

    Keys are assignments on the current separator; values are path counts.
    No states or equations are discarded to satisfy a resource limit.
    """
    if type(max_width) is not int or max_width < 0 or type(max_states) is not int or max_states < 1:
        raise ValueError("nonnegative width and positive state limits required")
    report = describe(system)
    if report["assignment_width"] > max_width:
        return {**report, "status": "resource_limit", "reason": "width", "existence_decided": False}
    states = {0: 1}
    peak = 1
    for index, before, after in schedule(system):
        positions = {old: bit for bit, old in enumerate(before)}
        closing = system.ending[index]
        next_states = {}
        for mask, count in states.items():
            for sign in ((1,) if system.vertices[index] == (0, 0) else (-1, 1)):
                def value(old):
                    return sign if old == index else (1 if mask >> positions[old] & 1 else -1)
                if any(sum(coefficient * value(old) for old, coefficient in row.items())
                       for row in closing):
                    continue
                next_mask = sum((value(old) == 1) << bit for bit, old in enumerate(after))
                next_states[next_mask] = next_states.get(next_mask, 0) + count
                if len(next_states) > max_states:
                    return {**report, "status": "resource_limit", "reason": "states",
                            "stopped_after_variables": index + 1, "existence_decided": False}
        states = next_states
        peak = max(peak, len(states))
        if not states:
            break
    count = states.get(0, 0)
    return {**report, "status": "exact", "existence_decided": True,
            "exists": bool(count), "colourings_up_to_reversal": count, "peak_states": peak}


def verify(saved, *, audit_graph=False):
    """Check every coefficient of a literal signed-word certificate."""
    keys = {"format", "lengths", "centre", "arm1", "arm2", "arm3"}
    if type(saved) is not dict or set(saved) != keys:
        raise ValueError("certificate requires the exact word-completion fields")
    if saved["format"] != "tripod-word-completion-v1":
        raise ValueError("unsupported word-completion certificate format")
    system = build_system(saved["lengths"])
    centre = saved["centre"]
    if type(centre) is not int or centre not in (-1, 1):
        raise ValueError("centre must be integer +1 or -1")
    signs = {(0, 0): centre}
    for arm, length in enumerate(system.lengths, 1):
        word = saved[f"arm{arm}"]
        first = 2 if arm < 3 else 1
        if type(word) is not str or len(word) != length - first + 1 or set(word) - {"+", "-"}:
            raise ValueError("literal sign word has wrong length or alphabet")
        signs.update({(arm, depth): 1 if char == "+" else -1
                      for depth, char in enumerate(word, first)})
    values = [signs[v] for v in system.vertices]
    if any(sum(coefficient * values[i] for i, coefficient in row.items()) for row in system.rows.values()):
        raise ValueError("nonzero full distance-shell coefficient")
    report = {"valid": True, "lengths": list(system.lengths),
              "size": len(values) // 2, "all_distance_equations": True}
    if audit_graph:
        # Existing independent BFS implementation; no graph is contracted at a hole.
        import word_realizability
        report["graph_audit"] = word_realizability.graph_audit(saved)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--lengths", nargs=3, type=int)
    mode.add_argument("--affine", type=int, metavar="T")
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--max-width", type=int, default=20)
    parser.add_argument("--max-states", type=int, default=100000)
    parser.add_argument("--audit-graph", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.verify:
            if args.solve:
                raise ValueError("--solve requires lengths")
            result = verify(json.loads(args.verify.read_text()), audit_graph=args.audit_graph)
        else:
            if args.audit_graph:
                raise ValueError("--audit-graph requires --verify")
            if args.affine is not None:
                if args.affine < 1:
                    raise ValueError("affine parameter must be at least 1")
                lengths = [227 + 7560 * args.affine, 67 + 7560 * args.affine, 11 + 7560 * args.affine]
            else:
                lengths = args.lengths
            system = build_system(lengths)
            result = solve(system, max_width=args.max_width, max_states=args.max_states) if args.solve else describe(system)
        print(json.dumps(result, sort_keys=True))
        return 2 if result.get("status") == "resource_limit" else 0
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(json.dumps({"valid": False, "reason": str(error)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
