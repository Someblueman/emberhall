"""Reconstruct one entire sign word from the other two, with exact arithmetic.

Holes are (1,1),(2,1), and a>b>c>=1. See WORD_REALIZABILITY.md.
This is a necessary-and-sufficient reduction, not an infinite-family solver.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from itertools import product
import json
from pathlib import Path


FORMAT = "tripod-word-completion-v1"


def _add(target, source, factor=1, shift=0):
    for degree, value in source.items():
        key = degree + shift
        target[key] = target.get(key, 0) + factor * value
        if not target[key]:
            del target[key]


def _multiply(left, right):
    result = {}
    for degree, value in left.items():
        _add(result, right, value, degree)
    return result


def _reverse(poly):
    return {-degree: value for degree, value in poly.items()}


def _lengths(lengths):
    if (not isinstance(lengths, (list, tuple)) or len(lengths) != 3
            or any(type(n) is not int for n in lengths)):
        raise ValueError("three integer arm lengths are required")
    a, b, c = lengths
    if not a > b > c >= 1:
        raise ValueError("this reduction requires a > b > c >= 1")
    return a, b, c


def _word(word, size):
    if type(word) is not str or len(word) != size or set(word) - {"+", "-"}:
        raise ValueError(f"a literal +/- word of length {size} is required")
    return [1 if char == "+" else -1 for char in word]


def shell_polynomial(lengths, centre, words):
    """Full normalized shell polynomial; zero entries allow a missing arm.

    This direct coefficient construction is separate from elimination.
    It is an internal arithmetic function; complete/verify validate words.
    """
    a, b, c = lengths
    result = {}
    for degree, coefficient in ((0, -1), (1, 2), (a, -1), (b, -1), (c, -1)):
        _add(result, {degree: coefficient * centre})
    for arm, (length, signs) in enumerate(zip(lengths, words), 1):
        first = 1 if arm == 3 else 2
        for depth, sign in enumerate(signs, first):
            if arm < 3:
                terms = ((depth + 1, 1), (depth - 1, 1), (depth - 2, -1))
            else:
                terms = ((depth + 1, 2), (depth, -1))
            for degree, coefficient in terms:
                _add(result, {degree: coefficient * sign})
            _add(result, {length - depth: -sign})
            for other, other_length in enumerate(lengths, 1):
                if other != arm:
                    _add(result, {depth + other_length: -sign})
    return result


def reduction(lengths, centre, arm2, arm3):
    """Return D,M for the polynomial identity D*S1=M (D[0]=1)."""
    a, b, c = _lengths(lengths)
    if type(centre) is not int or centre not in (-1, 1):
        raise ValueError("centre must be the integer +1 or -1")
    signs2, signs3 = _word(arm2, b - 1), _word(arm3, c)
    coefficient = {}
    for degree, value in ((1, 1), (-1, 1), (-2, -1), (b, -1), (c, -1)):
        _add(coefficient, {degree: value})
    reflected = _reverse(coefficient)
    determinant = _multiply(coefficient, reflected)
    _add(determinant, {0: -1})
    denominator = {}
    _add(denominator, determinant, shift=b + 2)
    rest = shell_polynomial(lengths, centre, ([0] * (a - 1), signs2, signs3))
    numerator = _multiply(reflected, rest)
    _add(numerator, _reverse(rest), shift=a)
    shifted = {}
    _add(shifted, numerator, factor=-1, shift=b + 2)
    assert denominator.get(0) == 1 and min(shifted, default=0) >= 0
    return denominator, shifted


def boundary_obstruction(lengths, arm3):
    """Necessary seven-sign test, quantifying over every other sign.

    Passing means only that the first four forced coefficients can be
    signs for some centre and arm-2 prefix; it does not assert completion.
    """
    a, b, c = _lengths(lengths)
    if c < 7 or b - c < 4:
        raise ValueError("boundary theorem requires c >= 7 and b-c >= 4")
    signs = _word(arm3, c)
    y1, y2, y3 = signs[:3]
    z0, z1, z2, z3 = reversed(signs[-4:])
    u = y1 + y2 - y3 - 2 * z0 - z1 - z2 - z3
    w = -y1 + y2 + z0 + z1 + z2
    return {"U": u, "W": w, "excluded": abs(u) > 2 or abs(w) > 3}


def boundary_table():
    excluded = 0
    for pattern in product("+-", repeat=7):
        # With c=7 the first three and last four are disjoint.
        excluded += boundary_obstruction((13, 11, 7), "".join(pattern))["excluded"]
    return {"boundary_patterns": 128, "excluded_patterns": excluded,
            "patterns_not_excluded": 128 - excluded,
            "scope": "a>b>c>=7, b-c>=4; holes (1,1),(2,1)",
            "longer_transfer": transfer_count(),
            "all_other_signs_unrestricted": True,
            "infinite_frontier_solved": False}


def prefix_transfer(arm3, centre, shells=56):
    """Exact feasibility of the paired low/high shell subsystem only.

    The caller must supply c>=2*shells-1 and b-c>=shells. Input boundaries
    and the two long-arm prefix/tip regions are then disjoint.
    """
    if type(shells) is not int or not 1 <= shells <= 56:
        raise ValueError("shell count must be between 1 and 56")
    if type(centre) is not int or centre not in (-1, 1):
        raise ValueError("centre must be the integer +1 or -1")
    if type(arm3) is not str:
        raise ValueError("shortest arm must be a literal sign word")
    signs = _word(arm3, len(arm3))
    if len(signs) < 2 * shells - 1:
        raise ValueError("shortest-arm prefix and tip must be disjoint")
    return all(value in (-2, 0, 2) for value in _end_sums(signs, centre, shells))


def _end_sums(signs, centre, shells):
    """Compulsory sums of the long arms when the top shells cancel."""
    c = len(signs)
    def value_at(depth):
        return centre if depth == 0 else signs[depth-1] if 1 <= depth <= c else 0
    sums = [0, 0]
    for n in range(2, shells + 2):
        value = sums[n - 1] + (sums[n - 3] if n >= 3 else 0)
        value -= sums[n-c-2] if n >= c+2 else 0
        value += 2*value_at(n-3) - value_at(n-2) - centre*(n == c+2)
        value -= signs[c-n+1] if 2 <= n <= c+1 else 0
        sums.append(value)
        yield value


def short_arm_certificate():
    """Exclude every colouring at c=11, b>=32, a>b, on these two holes."""
    failures = Counter()
    survivors = 0
    for signs in product((-1, 1), repeat=11):
        for depth, value in enumerate(_end_sums(signs, 1, 21), 2):
            if value not in (-2, 0, 2):
                failures[depth] += 1
                break
        else:
            survivors += 1
    return {"format": "tripod-short-arm-obstruction-v1", "shortest_length": 11,
            "minimum_middle_length": 32, "longest_greater_than_middle": True,
            "holes": [[1, 1], [2, 1]], "centre_normalized": 1,
            "shortest_words_checked": 2048, "surviving_words": survivors,
            "first_failure_histogram": [list(item) for item in sorted(failures.items())],
            "all_colourings_of_this_support_excluded": survivors == 0,
            "all_hole_supports_excluded": False}


def large_gap_bound(shortest):
    """Uniform analytic obstruction, for an arbitrary odd shortest length."""
    if type(shortest) is not int or shortest < 3 or shortest % 2 == 0:
        raise ValueError("shortest length must be an odd integer at least three")
    gap = shortest + 2 + 3 ** (shortest + 2)
    return {"shortest_length": shortest, "minimum_middle_length": shortest + gap,
            "longest_greater_than_middle": True, "holes": [[1, 1], [2, 1]],
            "all_colourings_of_this_support_excluded": True,
            "all_hole_supports_excluded": False}


def verify_short_arm_certificate(saved):
    rebuilt = short_arm_certificate()
    if json.dumps(saved, sort_keys=True) != json.dumps(rebuilt, sort_keys=True):
        raise ValueError("short-arm certificate differs from exact reconstruction")
    return rebuilt


def transfer_count(shells=56):
    """Count the disjoint boundary words admitted by the local transfer.

    For shells>=8, opposite centres cannot both pass: their ninth sums
    differ by six. The output still concerns only a shell subsystem.
    """
    if type(shells) is not int or not 8 <= shells <= 56:
        raise ValueError("counted shell length must be between 8 and 56")
    states = Counter({(-1 - tip, 0, 0, 1): 1 for tip in (-1, 1)})
    for _ in range(1, shells):
        following = Counter()
        for (u, v, w, previous), count in states.items():
            for current, tip in product((-1, 1), repeat=2):
                value = u + w + 2 * previous - current - tip
                if value in (-2, 0, 2):
                    following[value, u, v, current] += count
        states = following
    return {"shells_per_end": shells, "boundary_bits": 2 * shells - 1,
            "patterns_not_excluded": 2 * sum(states.values()),
            "total_patterns": 2 ** (2 * shells - 1), "live_states_per_centre": len(states),
            "scope": f"a>b>c>={2*shells-1}, b-c>={shells}; only the paired end shells"}


def complete(lengths, centre, arm2, arm3):
    """Unique completion, or ValueError proving these exact inputs fail.

    No branch is chosen for arm 1. A failed input is not a proof that all
    inputs, all supports, or a parameter family fail.
    """
    a, b, c = _lengths(lengths)
    if c >= 7 and b - c >= 4 and boundary_obstruction(lengths, arm3)["excluded"]:
        raise ValueError("shortest-arm boundary violates the four-coefficient sign condition")
    if c >= 111 and b - c >= 56 and not prefix_transfer(arm3, centre):
        raise ValueError("shortest-arm boundary violates the 56-shell transfer condition")
    denominator, numerator = reduction(lengths, centre, arm2, arm3)
    positive_terms = [(degree, value) for degree, value in denominator.items() if degree]
    coefficients = {}
    for depth in range(a + 1):
        value = numerator.get(depth, 0) - sum(
            coefficient * coefficients.get(depth - delay, 0)
            for delay, coefficient in positive_terms if delay <= depth)
        if depth < 2:
            if value:
                raise ValueError(f"forbidden coefficient at depth {depth}: {value}")
        elif value not in (-1, 1):
            raise ValueError(f"forced coefficient at depth {depth} is {value}, not a sign")
        if value:
            coefficients[depth] = value
    remainder = dict(numerator)
    _add(remainder, _multiply(denominator, coefficients), factor=-1)
    if remainder:
        raise ValueError(f"nonzero polynomial remainder at degree {min(remainder)}")
    arm1 = "".join("+" if coefficients[d] == 1 else "-" for d in range(2, a + 1))
    result = {"format": FORMAT, "lengths": [a, b, c], "centre": centre,
              "arm1": arm1, "arm2": arm2, "arm3": arm3}
    signs = [_word(result[f"arm{i}"], n - (i < 3))
             for i, n in enumerate(lengths, 1)]
    assert not shell_polynomial(lengths, centre, signs)
    assert centre + sum(map(sum, signs)) == 0
    return result


def verify_certificate(saved):
    """Reconstruct all output; reject altered signs and extra saved claims."""
    if type(saved) is not dict or set(saved) != {
            "format", "lengths", "centre", "arm1", "arm2", "arm3"}:
        raise ValueError("unexpected certificate fields")
    rebuilt = complete(saved["lengths"], saved["centre"], saved["arm2"], saved["arm3"])
    if saved != rebuilt:
        raise ValueError("certificate differs from its unique reconstructed word")
    return rebuilt


def graph_audit(saved, max_vertices=512):
    """Independent BFS distances in the original tree, including both holes."""
    saved = verify_certificate(saved)
    lengths = saved["lengths"]
    if type(max_vertices) is not int or max_vertices < 1:
        raise ValueError("audit limit must be a positive integer")
    if 1 + sum(lengths) > max_vertices:
        raise ValueError("original-tree graph audit exceeds the vertex limit")
    graph = {(0, 0): []}
    for arm, length in enumerate(lengths, 1):
        previous = (0, 0)
        for depth in range(1, length + 1):
            vertex = (arm, depth)
            graph[vertex] = [previous]
            graph[previous].append(vertex)
            previous = vertex
    signs = {(0, 0): saved["centre"]}
    for arm, length in enumerate(lengths, 1):
        first = 1 if arm == 3 else 2
        signs.update({(arm, depth): sign for depth, sign in enumerate(
            _word(saved[f"arm{arm}"], length - (arm < 3)), first)})
    left, right = [{v for v, s in signs.items() if s == sign} for sign in (1, -1)]
    profiles = [Counter(), Counter()]
    for source in signs:
        distances = {source: 0}
        queue = deque([source])
        while queue:
            vertex = queue.popleft()
            for neighbor in graph[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex] + 1
                    queue.append(neighbor)
        for group, profile in zip((left, right), profiles):
            if source in group:
                for target in group:
                    if source < target:
                        profile[distances[target]] += 1
    target = len(graph) // 2 - 1
    if left & right or len(left) != len(right) or len(left) < target or profiles[0] != profiles[1]:
        raise ValueError("original-tree audit failed")
    return {"original_vertices": len(graph), "size": len(left), "target": target,
            "pairs_per_set": sum(profiles[0].values()), "distance_multiplicities_equal": True}


def control(parameter):
    if type(parameter) is not int or parameter < 0:
        raise ValueError("control parameter must be a nonnegative integer")
    return complete((5 + 4 * parameter, 4, 2), 1, "---", "++")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--control", type=int, metavar="K")
    source.add_argument("--complete", type=Path, metavar="INPUT_JSON")
    source.add_argument("--check", type=Path, metavar="CERTIFICATE_JSON")
    source.add_argument("--boundary-table", action="store_true")
    source.add_argument("--short-arm-obstruction", action="store_true")
    source.add_argument("--check-obstruction", type=Path)
    source.add_argument("--large-gap", type=int, metavar="ODD_C")
    parser.add_argument("--write", type=Path, metavar="CERTIFICATE_JSON")
    parser.add_argument("--audit-graph", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.large_gap is not None:
            if args.audit_graph or args.write:
                raise ValueError("large-gap output is a theorem bound, not a word certificate")
            print(json.dumps(large_gap_bound(args.large_gap), sort_keys=True))
            return 0
        if args.short_arm_obstruction or args.check_obstruction:
            if args.audit_graph:
                raise ValueError("an infinite obstruction is not a pair to audit")
            result = (verify_short_arm_certificate(json.loads(args.check_obstruction.read_text()))
                      if args.check_obstruction else short_arm_certificate())
            if args.write:
                args.write.write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps(result, sort_keys=True))
            return 0 if result["all_colourings_of_this_support_excluded"] else 1
        if args.boundary_table:
            if args.write or args.audit_graph:
                raise ValueError("boundary table is not a completed word certificate")
            print(json.dumps(boundary_table(), sort_keys=True))
            return 0
        if args.control is not None:
            result = control(args.control)
        elif args.complete:
            seed = json.loads(args.complete.read_text())
            if type(seed) is not dict or set(seed) != {"lengths", "centre", "arm2", "arm3"}:
                raise ValueError("completion input needs lengths, centre, arm2 and arm3")
            result = complete(seed["lengths"], seed["centre"], seed["arm2"], seed["arm3"])
        else:
            result = verify_certificate(json.loads(args.check.read_text()))
        report = {"valid": True, "lengths": result["lengths"],
                  "size": (sum(result["lengths"]) - 1) // 2,
                  "unique_longest_arm_completion": True,
                  "infinite_frontier_solved": False}
        if args.audit_graph:
            report["graph_audit"] = graph_audit(result)
        if args.write:
            args.write.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(report, sort_keys=True))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(json.dumps({"valid": False, "reason": str(error)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
