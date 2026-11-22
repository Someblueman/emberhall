"""Exact parity-coordinate compression of the full integer shell transfer.

Signs are 1-2*b. Parity reduces state coordinates, never the integer checks.
See WORD_TRANSFER_COMPRESSION.md. Requires the accepted word_frontier module.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import word_frontier as frontier

FORMAT = "tripod-parity-compression-v1"


class InconsistentParity(ValueError):
    """The integer shell system has an inconsistent necessary parity system."""


class Parity:
    """Affine equations over F2, with an identity submatrix on pivot columns."""

    def __init__(self):
        self.rows = {}

    def add(self, mask, rhs):
        for pivot, (row, value) in self.rows.items():
            if mask >> pivot & 1:
                mask ^= row
                rhs ^= value
        if not mask:
            if rhs:
                raise InconsistentParity("inconsistent parity equations")
            return
        pivot = (mask & -mask).bit_length() - 1
        for old, (row, value) in list(self.rows.items()):
            if row >> pivot & 1:
                self.rows[old] = (row ^ mask, value ^ rhs)
        self.rows[pivot] = (mask, rhs)

    def forget(self, variable):
        """Existentially eliminate a column; no constraint on survivors is lost."""
        if variable in self.rows:
            del self.rows[variable]
            return
        selected = min((p for p, (row, _) in self.rows.items()
                        if row >> variable & 1), default=None)
        if selected is None:
            return
        mask, rhs = self.rows.pop(selected)
        for pivot, (row, value) in list(self.rows.items()):
            if row >> variable & 1:
                self.rows[pivot] = (row ^ mask, value ^ rhs)

    def free(self, active):
        return tuple(i for i in active if i not in self.rows)

    def decode(self, code, free):
        bits = sum(((code >> k) & 1) << i for k, i in enumerate(free))
        for pivot, (mask, rhs) in self.rows.items():
            bits |= (rhs ^ ((mask & bits).bit_count() & 1)) << pivot
        return bits


def parity_row(row):
    total = sum(row.values())
    if total % 2:
        raise InconsistentParity("odd coefficient sum cannot vanish on signs")
    return sum(1 << i for i, a in row.items() if a % 2), (total // 2) % 2


def steps(system):
    """Yield exact before/after coordinate systems without saving a large plan."""
    parity = Parity()
    for index, before, after in frontier.schedule(system):
        previous = Parity()
        previous.rows = parity.rows.copy()
        if system.vertices[index] == (0, 0):
            parity.add(1 << index, 0)  # centre sign +1
        for row in system.ending[index]:
            parity.add(*parity_row(row))
        after_set = set(after)
        for old in (*before, index):
            if old not in after_set:
                parity.forget(old)
        yield index, before, after, previous, parity


def assignment_width(system):
    changes = [0] * (len(system.vertices) + 1)
    for index, last in enumerate(system.last):
        if last > index:
            changes[index + 1] += 1
            changes[last + 1] -= 1
    active = maximum = 0
    for change in changes:
        active += change
        maximum = max(maximum, active + 1)
    return maximum


def order_system(system):
    """Try a half-arm-offset fold; retain the old order if its width is smaller."""
    c = system.lengths[2]

    def folded(index):
        arm, depth = system.vertices[index]
        if arm == 0:
            return -1
        residue = (2 * depth - (system.lengths[arm - 1] - c)) % (2 * c)
        return min(residue, 2 * c - residue)

    order = sorted(range(len(system.vertices)),
                   key=lambda i: (folded(i), system.vertices[i]))
    position = {old: new for new, old in enumerate(order)}
    rows = {degree: {position[i]: value for i, value in row.items()}
            for degree, row in system.rows.items()}
    last = list(range(len(order)))
    ending = [[] for _ in order]
    for row in rows.values():
        end = max(row)
        ending[end].append(row)
        for i in row:
            last[i] = max(last[i], end)
    candidate = frontier.System(system.lengths,
        [system.vertices[i] for i in order], [system.layers[i] for i in order],
        rows, last, ending)
    if assignment_width(candidate) < assignment_width(system):
        return candidate, "half-offset"
    return system, "original"


def describe(system):
    original = frontier.describe(system)
    system, ordering = order_system(system)
    ordered_width = assignment_width(system)
    width = state_bits = max_rank = 0
    try:
        for index, before, after, previous, parity in steps(system):
            width = max(width, len(previous.free(before))
                        + (system.vertices[index] != (0, 0)))
            state_bits = max(state_bits, len(parity.free(after)))
            max_rank = max(max_rank, len(parity.rows))
    except InconsistentParity:
        return {"format": FORMAT, "lengths": list(system.lengths),
                "status": "parity_obstruction", "existence_decided": True,
                "exists": False, "all_distance_equations": True}
    return {"format": FORMAT, "lengths": list(system.lengths),
            "status": "compressed", "existence_decided": False,
            "all_distance_equations": True,
            "variables": original["variables"], "equations": original["equations"],
            "original_assignment_width": original["assignment_width"],
            "ordering": ordering, "ordered_assignment_width": ordered_width,
            "compressed_assignment_width": width,
            "original_maximum_stored_bits": original["assignment_width"] - 1,
            "maximum_stored_bits": state_bits, "maximum_parity_rank": max_rank}


def solve(system, *, max_width=20, max_states=100000):
    if type(max_width) is not int or max_width < 0 or type(max_states) is not int or max_states < 1:
        raise ValueError("nonnegative width and positive state limits required")
    report = describe(system)
    if report["existence_decided"]:
        return {**report, "colourings_up_to_reversal": 0}
    if report["compressed_assignment_width"] > max_width:
        return {**report, "status": "resource_limit", "reason": "width"}
    system, _ = order_system(system)
    states, peak = {0: 1}, 1
    for index, before, after, previous, parity in steps(system):
        free_before, free_after = previous.free(before), parity.free(after)
        next_states = {}
        for code, count in states.items():
            old_bits = previous.decode(code, free_before)
            for bit in ((0,) if system.vertices[index] == (0, 0) else (0, 1)):
                bits = old_bits | (bit << index)
                if any(sum(a * (1 - 2 * ((bits >> i) & 1)) for i, a in row.items())
                       for row in system.ending[index]):
                    continue
                new_code = sum(((bits >> i) & 1) << k for k, i in enumerate(free_after))
                next_states[new_code] = next_states.get(new_code, 0) + count
                if len(next_states) > max_states:
                    return {**report, "status": "resource_limit", "reason": "states",
                            "stopped_after_variables": index + 1}
        states = next_states
        peak = max(peak, len(states))
        if not states:
            break
    count = states.get(0, 0)
    return {**report, "status": "exact", "existence_decided": True,
            "exists": bool(count), "colourings_up_to_reversal": count, "peak_states": peak}


def cycle_certificate():
    """Replay finite hypotheses of the branch repetition proof in the document."""
    base = frontier.build_system((7787, 7627, 7571))
    system, ordering = order_system(base)
    if ordering != "half-offset":
        raise AssertionError("branch proof requires the half-offset order")
    c, start, period = system.lengths[2], 1024, 16

    def label(index, layer):
        arm, depth = system.vertices[index]
        if arm == 0:
            raise AssertionError("centre survived into the middle loop")
        e = system.lengths[arm - 1] - c
        residue = 2 * depth - e
        if not 0 <= residue < 2 * c:
            raise AssertionError("wrapped tail entered the middle loop")
        return (arm, int(residue > c), min(residue, 2 * c - residue) // 2 - layer)

    def snapshot(active, parity, layer):
        labels = {i: label(i, layer) for i in active}
        if len(set(labels.values())) != len(labels):
            raise AssertionError("middle labels are not injective")
        rows = tuple(sorted((labels[pivot],
            tuple(sorted(labels[i] for i in active if mask >> i & 1)), rhs)
            for pivot, (mask, rhs) in parity.rows.items()))
        return tuple(labels.values()), rows

    frames, initial, final = {}, None, None
    for index, before, after, previous, parity in steps(system):
        arm, depth = system.vertices[index]
        if not arm:
            continue
        e = system.lengths[arm - 1] - c
        residue = (2 * depth - e) % (2 * c)
        layer = min(residue, 2 * c - residue) // 2
        if layer < start:
            continue
        if layer >= start + period:
            break
        if initial is None:
            initial = snapshot(before, previous, start - 1)
        rows = tuple(sorted(tuple(sorted((label(i, layer), coefficient)
            for i, coefficient in row.items())) for row in system.ending[index]))
        frames.setdefault(layer, []).append((label(index, layer), rows,
            tuple(label(i, layer) for i in before),
            tuple(label(i, layer) for i in after)))
        final = snapshot(after, parity, layer)
    if initial != final or len(frames) != period:
        raise AssertionError("projected middle state did not repeat")
    first_frame = frames[start]
    if any(frame != first_frame for frame in frames.values()):
        raise AssertionError("full integer transition stencil is not homogeneous")

    def digest(value):
        return hashlib.sha256(repr(value).encode()).hexdigest()

    witness = next(len(before) + 1 for i, before, _ in frontier.schedule(base)
                   if base.vertices[i] == (2, 1000))
    return {"format": "tripod-middle-cycle-v1", "base_lengths": list(base.lengths),
            "parameter_branch": "t = 1 + 4u, u >= 0", "loop_start_layer": start,
            "loop_period": period, "extra_cycles_per_branch_step": 945,
            "loop_state_bits": len(initial[0]) - len(initial[1]),
            "boundary_guard": 1024, "integer_frame_sha256": digest(first_frame),
            "original_width_witness": witness, "ordered_width": assignment_width(system),
            "projected_state_sha256": digest(initial),
            "maximum_assignment_bits": describe(base)["compressed_assignment_width"],
            "all_distance_equations": True, "existence_decided": False}


def verify(saved):
    if type(saved) is not dict:
        raise ValueError("expected a compression certificate")
    if saved.get("format") == "tripod-middle-cycle-v1":
        expected = cycle_certificate()
    elif saved.get("format") == FORMAT:
        expected = describe(frontier.build_system(saved.get("lengths")))
    else:
        raise ValueError("expected a compression certificate")
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError("compression certificate differs from exact replay")
    return {"valid": True, **expected}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--lengths", nargs=3, type=int)
    mode.add_argument("--affine", type=int, metavar="T")
    mode.add_argument("--verify", type=Path)
    mode.add_argument("--cycle", action="store_true")
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--max-width", type=int, default=20)
    parser.add_argument("--max-states", type=int, default=100000)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.verify:
            if args.solve or args.write:
                raise ValueError("verify cannot be combined with solve or write")
            result = verify(json.loads(args.verify.read_text()))
        elif args.cycle:
            if args.solve:
                raise ValueError("cycle is a reduction certificate, not a solved branch")
            result = cycle_certificate()
            if args.write:
                args.write.write_text(json.dumps(result, sort_keys=True) + "\n")
        else:
            if args.affine is not None:
                if args.affine < 1:
                    raise ValueError("affine parameter must be at least 1")
                lengths = tuple(n + 7560 * args.affine for n in (227, 67, 11))
            else:
                lengths = args.lengths
            system = frontier.build_system(lengths)
            if args.solve and args.write:
                raise ValueError("write records compression certificates, not partial searches")
            result = solve(system, max_width=args.max_width, max_states=args.max_states) if args.solve else describe(system)
            if args.write:
                args.write.write_text(json.dumps(result, sort_keys=True) + "\n")
        print(json.dumps(result, sort_keys=True))
        return 2 if result.get("status") == "resource_limit" else 0
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(json.dumps({"valid": False, "reason": str(error)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
