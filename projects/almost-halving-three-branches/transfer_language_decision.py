"""Two-ended affine pruning of the full integer tripod transfer.

The affine spaces are necessary conditions, never integer-existence answers.
See TRANSFER_LANGUAGE_DECISION.md. Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import word_frontier as frontier
import word_transfer_compression as compression

FORMAT = "tripod-two-ended-parity-v1"


def copy_space(space):
    result = compression.Parity()
    result.rows = space.rows.copy()
    return result


def projections(system, cuts):
    """Project ALL necessary parity equations onto selected separators.

    At cut i the separator contains j<i with last[j]>=i. Past rows close
    before i; future rows close at or after i. Their eliminated variables
    are disjoint, so intersecting their projections is exact over F2.
    """
    size = len(system.vertices)
    cuts = set(cuts)
    if any(type(i) is not int or not 0 <= i <= size for i in cuts):
        raise ValueError("cuts must be variable positions in the system")
    if not cuts:
        return {}
    future = {}
    space = compression.Parity()
    if size in cuts:
        future[size] = copy_space(space)
    for index in range(size - 1, min(cuts) - 1, -1):
        for row in system.ending[index]:
            space.add(*compression.parity_row(row))
        if system.vertices[index] == (0, 0):
            space.add(1 << index, 0)
        space.forget(index)
        if index in cuts:
            future[index] = copy_space(space)
    result = {}
    for index, before, after, past, following in compression.steps(system):
        if index in cuts:
            both = copy_space(past)
            for mask, rhs in future[index].rows.values():
                both.add(mask, rhs)
            active_mask = sum(1 << i for i in before)
            if any(mask & ~active_mask for mask, _ in both.rows.values()):
                raise AssertionError("projected row escaped the separator")
            result[index] = (tuple(before), past, future[index], both)
        if index + 1 == size and size in cuts:
            result[size] = (tuple(after), copy_space(following), future[size],
                            copy_space(following))
        if index >= max(cuts):
            break
    return result


def folded_layer(system, index):
    arm, depth = system.vertices[index]
    if not arm:
        return -1
    c = system.lengths[2]
    residue = (2 * depth - (system.lengths[arm - 1] - c)) % (2 * c)
    return min(residue, 2 * c - residue) // 2


def normalized(system, active, space, layer):
    """Canonical affine equations on geometrically labelled live signs."""
    c = system.lengths[2]
    labelled = []
    for index in active:
        arm, depth = system.vertices[index]
        if not arm:
            raise ValueError("normalization requires an interior separator")
        q = 2 * depth - (system.lengths[arm - 1] - c)
        winding, residue = divmod(q, 2 * c)
        label = (arm, winding, int(residue > c), folded_layer(system, index) - layer)
        labelled.append((label, index))
    labelled.sort()
    labels = tuple(label for label, _ in labelled)
    if len(set(labels)) != len(labels):
        raise AssertionError("separator labels are not injective")
    canonical = compression.Parity()
    for mask, rhs in space.rows.values():
        canonical.add(sum(1 << position for position, (_, index) in enumerate(labelled)
                          if mask >> index & 1), rhs)
    return labels, tuple(sorted(canonical.rows.items()))


def interface_report(parameter=1, layers=(1024, 1040)):
    if type(parameter) is not int or parameter < 1:
        raise ValueError("parameter must be a positive integer")
    if not layers or any(type(layer) is not int or layer < 1 for layer in layers):
        raise ValueError("positive interior layers required")
    lengths = tuple(base + 7560 * parameter for base in (227, 67, 11))
    system, ordering = compression.order_system(frontier.build_system(lengths))
    positions = {}
    for index in range(len(system.vertices)):
        layer = folded_layer(system, index)
        if layer in layers and layer not in positions:
            positions[layer] = index
    if set(positions) != set(layers):
        raise ValueError("requested layer is outside the tree")
    spaces = projections(system, positions.values())
    records, canonical = [], []
    for layer in layers:
        index = positions[layer]
        active, past, future, both = spaces[index]
        states = [normalized(system, active, p, layer) for p in (past, future, both)]
        canonical.append(states)
        records.append({"layer": layer, "position": index, "stored_signs": len(active),
                        "past_rank": len(past.rows), "future_rank": len(future.rows),
                        "combined_rank": len(both.rows),
                        "past_free_bits": len(active) - len(past.rows),
                        "combined_free_bits": len(active) - len(both.rows),
                        "space_sha256": [hashlib.sha256(repr(p).encode()).hexdigest()
                                         for p in states]})
    return {"format": FORMAT, "parameter": parameter, "layers": list(layers),
            "lengths": list(lengths), "ordering": ordering, "interfaces": records,
            "spaces_equal_to_first": [[state == canonical[0][j]
                                        for j, state in enumerate(states)]
                                       for states in canonical],
            "existence_decided": False,
            "scope": "all parity equations; holes (1,1),(2,1); not integer reachability"}


def branch_certificate():
    """Replay the two affine boundary phases, not integer accepting paths.

    The documented homogeneous stencil proves the extension from these
    exact returns to arbitrary parameters. No hash is used for equality.
    """
    reports, snapshots = [], []
    for parameter, layers in ((1, (1024, 1040, 1104, 1184)), (5, (1024,))):
        lengths = tuple(base + 7560 * parameter for base in (227, 67, 11))
        system, ordering = compression.order_system(frontier.build_system(lengths))
        if ordering != "half-offset":
            raise AssertionError("the branch requires the half-offset order")
        cuts = {}
        for index in range(len(system.vertices)):
            layer = folded_layer(system, index)
            if layer in layers and layer not in cuts:
                cuts[layer] = index
        projected = projections(system, cuts.values())
        normalized_states = {}
        counts = {}
        for layer, index in cuts.items():
            active, past, future, both = projected[index]
            normalized_states[layer] = tuple(normalized(system, active, p, layer)
                                             for p in (past, future, both))
            counts[layer] = [len(active), len(past.rows), len(future.rows), len(both.rows)]
        snapshots.append(normalized_states)
        reports.append({"parameter": parameter, "ranks_by_layer": counts})
    base, later = snapshots
    if not (base[1024][0] == base[1040][0] == base[1104][0] == base[1184][0]
            and base[1024][1:] == base[1184][1:]
            and base[1024][1:] != base[1040][1:]
            and later[1024] == base[1104]):
        raise AssertionError("two-ended affine branch return failed")
    if any(values != [1080, 117, 86, 201]
           for report in reports for values in report["ranks_by_layer"].values()):
        raise AssertionError("unexpected branch interface rank")
    return {"format": "tripod-two-ended-branch-v1", "reports": reports,
            "branch": "t=1+4u, u>=0", "future_period_layers": 160,
            "inserted_layers_per_u": 15120, "boundary_phases": 2,
            "two_ended_interface_bits": 879,
            "parity_feasible_for_every_u": True, "existence_decided": False,
            "scope": "parity relaxation only; integer accepting paths remain unknown"}


def binary_basis(vectors):
    basis = {}
    for vector in vectors:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot in basis:
                vector ^= basis[pivot]
            else:
                basis[pivot] = vector
                break
    return tuple(basis.values())


def row_hull(space, row):
    """Compare a row's current affine image with its exact integer solutions."""
    variables = tuple(row)
    offset, influences = 0, {}
    for position, variable in enumerate(variables):
        if variable in space.rows:
            mask, rhs = space.rows[variable]
            offset |= rhs << position
            mask ^= 1 << variable
        else:
            mask = 1 << variable
        while mask:
            bit = mask & -mask
            influences[bit] = influences.get(bit, 0) ^ (1 << position)
            mask ^= bit
    basis = binary_basis(influences.values())
    patterns = [offset]
    for vector in basis:
        patterns += [pattern ^ vector for pattern in patterns]
    good = [pattern for pattern in patterns
            if sum(row[v] * (1 - 2 * (pattern >> i & 1))
                   for i, v in enumerate(variables)) == 0]
    dimension = len(binary_basis(pattern ^ good[0] for pattern in good)) if good else -1
    return len(basis), dimension, len(patterns), len(good)


def local_hull_report(lengths=(7787, 7627, 7571), batch_size=128):
    """Complete finite test of single-row affine strengthening, in batches.

    A zero strengthening count is a fixed point for this particular rule:
    replace a row's current affine image by the hull of its integer solutions.
    It is not a fixed point for arbitrary multi-row reasoning.
    """
    if type(batch_size) is not int or not 1 <= batch_size <= 512:
        raise ValueError("batch size must be between 1 and 512")
    system, _ = compression.order_system(frontier.build_system(lengths))
    if len(system.vertices) > 24000:
        raise ValueError("local hull replay is limited to 24000 variables")
    indices = [i for i, rows in enumerate(system.ending) if rows]
    examined = strengthened = empty = 0
    for offset in range(0, len(indices), batch_size):
        batch = indices[offset:offset + batch_size]
        snapshots = projections(system, set(batch) | {i + 1 for i in batch})
        for index in batch:
            _, past, _, _ = snapshots[index]
            _, _, future, _ = snapshots[index + 1]
            middle = copy_space(past)
            if system.vertices[index] == (0, 0):
                middle.add(1 << index, 0)
            for row in system.ending[index]:
                middle.add(*compression.parity_row(row))
            for mask, rhs in future.rows.values():
                middle.add(mask, rhs)
            for row in system.ending[index]:
                before, after, _, _ = row_hull(middle, row)
                examined += 1
                empty += after == -1
                strengthened += 0 <= after < before
    if examined != len(system.rows):
        raise AssertionError("not every integer row was examined")
    return {"format": "tripod-local-affine-hulls-v1", "lengths": list(system.lengths),
            "rows_examined": examined, "empty_row_domains": empty,
            "affine_strengthenings": strengthened, "complete": True,
            "existence_decided": False,
            "scope": "finite single-row affine closure, not multi-row integer feasibility"}


def solve(lengths, *, max_variables=128, max_width=20, max_states=100000):
    """Small exact integer transfer with future-aware coordinate spaces."""
    for value, minimum in ((max_variables, 1), (max_width, 0), (max_states, 1)):
        if type(value) is not int or value < minimum:
            raise ValueError("invalid resource limit")
    system, _ = compression.order_system(frontier.build_system(lengths))
    report = {"lengths": list(system.lengths), "existence_decided": False}
    size = len(system.vertices)
    # Storing every suffix projection is quadratic; refuse before doing it.
    if size > max_variables:
        return {**report, "status": "resource_limit", "reason": "variables"}
    try:
        spaces = projections(system, range(size + 1))
    except compression.InconsistentParity:
        return {**report, "status": "exact", "existence_decided": True,
                "exists": False, "colourings_up_to_reversal": 0}
    width = max(len(space.free(active)) + (system.vertices[i] != (0, 0))
                for i, (active, _, _, space) in spaces.items() if i < size)
    report["assignment_width"] = width
    if width > max_width:
        return {**report, "status": "resource_limit", "reason": "width"}
    states, peak = {0: 1}, 1
    for index in range(size):
        active, _, _, before = spaces[index]
        after_active, _, _, after = spaces[index + 1]
        free_before, free_after = before.free(active), after.free(after_active)
        following = {}
        for code, count in states.items():
            old = before.decode(code, free_before)
            for bit in ((0,) if system.vertices[index] == (0, 0) else (0, 1)):
                bits = old | bit << index
                if any(sum(a * (1 - 2 * (bits >> i & 1)) for i, a in row.items())
                       for row in system.ending[index]):
                    continue
                if any((mask & bits).bit_count() % 2 != rhs
                       for mask, rhs in after.rows.values()):
                    continue
                next_code = sum((bits >> i & 1) << k for k, i in enumerate(free_after))
                following[next_code] = following.get(next_code, 0) + count
                if len(following) > max_states:
                    return {**report, "status": "resource_limit", "reason": "states"}
        states = following
        peak = max(peak, len(states))
        if not states:
            break
    count = states.get(0, 0)
    return {**report, "status": "exact", "existence_decided": True,
            "exists": bool(count), "colourings_up_to_reversal": count, "peak_states": peak}


def verify(saved):
    if type(saved) is not dict:
        raise ValueError("expected a two-ended parity certificate")
    if saved.get("format") == FORMAT:
        expected = interface_report(saved.get("parameter"), saved.get("layers"))
    elif saved.get("format") == "tripod-two-ended-branch-v1":
        expected = branch_certificate()
    elif saved.get("format") == "tripod-local-affine-hulls-v1":
        expected = local_hull_report(saved.get("lengths"))
    else:
        raise ValueError("expected a two-ended parity certificate")
    # JSON roundtrips turn the branch report's integer layer keys into strings.
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError("certificate differs from exact replay")
    return {"valid": True, **expected}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--affine", type=int)
    mode.add_argument("--lengths", type=int, nargs=3)
    mode.add_argument("--verify", type=Path)
    mode.add_argument("--branch", action="store_true")
    mode.add_argument("--local-hulls", action="store_true")
    parser.add_argument("--layers", type=int, nargs="+", default=[1024, 1040])
    parser.add_argument("--write", type=Path)
    parser.add_argument("--max-variables", type=int, default=128)
    parser.add_argument("--max-width", type=int, default=20)
    parser.add_argument("--max-states", type=int, default=100000)
    args = parser.parse_args(argv)
    try:
        if args.verify:
            if args.write:
                raise ValueError("verify cannot write a certificate")
            result = verify(json.loads(args.verify.read_text()))
        elif args.affine is not None:
            result = interface_report(args.affine, args.layers)
        elif args.branch:
            result = branch_certificate()
        elif args.local_hulls:
            result = local_hull_report()
        else:
            if args.write:
                raise ValueError("write is for interface reports")
            result = solve(args.lengths, max_variables=args.max_variables,
                           max_width=args.max_width, max_states=args.max_states)
        if args.write:
            args.write.write_text(json.dumps(result, sort_keys=True) + "\n")
        print(json.dumps(result, sort_keys=True))
        return 2 if result.get("status") == "resource_limit" else 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({"valid": False, "reason": str(error)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
