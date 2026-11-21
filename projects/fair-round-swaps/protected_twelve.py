"""Exact paths and distance checks for the unresolved five-final protected core."""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import reduce
from itertools import permutations
import json
from math import lcm
from pathlib import Path

from swaps import ef1, exchange, validate_profile

START = (5, 0, 1, 2, 3, 4, 0, 6, 1, 2, 3, 4)
TARGET = (6, 0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4)


class BudgetExhausted(Exception):
    pass


class Graph:
    def __init__(self, u):
        validate_profile(u)
        if len(u) != 7 or len(u[0]) != 12:
            raise ValueError("need seven agents and twelve goods")
        if any(u[i][0] < v for i in (5, 6) for v in u[i]):
            raise ValueError("shared favorite must maximize both carrier rows")
        if any(u[i][i+1] < u[i][g] for i in range(5) for g in range(i+2, 12)):
            raise ValueError("common anchors must be greedy in order")
        if any(u[5][6] < u[5][g] or u[6][7] < u[6][g] for g in range(6, 12)):
            raise ValueError("carrier alternatives must maximize the tail pool")
        self.u = u
        self.totals, self.burdens = [], []
        for row in u:
            scale = reduce(lcm, (Fraction(v).denominator for v in row), 1)
            values = [int(Fraction(v)*scale) for v in row]
            total, largest = [0]*4096, [0]*4096
            for mask in range(1, 4096):
                bit = mask & -mask
                g, rest = bit.bit_length()-1, mask ^ bit
                total[mask] = total[rest]+values[g]
                largest[mask] = max(largest[rest], values[g])
            self.totals.append(total)
            self.burdens.append([a-b for a, b in zip(total, largest)])
        self.cache = {}

    def fair(self, state, limit=None):
        if state not in self.cache:
            if limit is not None and len(self.cache) >= limit:
                raise BudgetExhausted
            masks = [0]*7
            for g, i in enumerate(state):
                masks[i] |= 1 << g
            self.cache[state] = all(self.totals[i][masks[i]] >= self.burdens[i][masks[j]]
                                    for i in range(7) for j in range(5) if i != j)
        return self.cache[state]

    @staticmethod
    def neighbors(state):
        for x in range(12):
            for y in range(x+1, 12):
                if state[x] == state[y] or (x == 0 and state[y] < 5):
                    continue
                b = list(state)
                b[x], b[y] = b[y], b[x]
                yield tuple(b)

    def search(self, max_checks=200000):
        """Bidirectional BFS; only exhausted components justify separation."""
        if max_checks is not None and (type(max_checks) is not int or max_checks < 2):
            raise ValueError("check budget must be at least two, or None")
        if not self.fair(START, max_checks) or not self.fair(TARGET, max_checks):
            raise AssertionError("canonical endpoints should be fair")
        parents = [{START: None}, {TARGET: None}]
        frontiers = [[START], [TARGET]]

        def result(status, path=None):
            return {"status": status, "path": path, "checked": len(self.cache),
                    "reached": [len(p) for p in parents], "max_checks": max_checks}

        try:
            while frontiers[0] and frontiers[1]:
                side = 0 if len(frontiers[0]) <= len(frontiers[1]) else 1
                own, other = parents[side], parents[1-side]
                following = []
                for a in frontiers[side]:
                    for b in self.neighbors(a):
                        if b in own or not self.fair(b, max_checks):
                            continue
                        own[b] = a
                        if b in other:
                            left, right = [b], []
                            while parents[0][left[-1]] is not None:
                                left.append(parents[0][left[-1]])
                            node = b
                            while parents[1][node] is not None:
                                node = parents[1][node]
                                right.append(node)
                            path = left[::-1]+right
                            assert all(ef1(self.u, a) for a in path)
                            assert all(exchange(a, b) for a, b in zip(path, path[1:]))
                            return result("connected", path)
                        following.append(b)
                frontiers[side] = following
        except BudgetExhausted:
            return result("budget_exhausted")
        return result("separated")


def profile(seed=0):
    import random
    rng = random.Random(seed)
    u = [[rng.randrange(10) for _ in range(12)] for _ in range(7)]
    for i in range(5):
        u[i][i+1] = max(u[i][i+1:])
    for i, alternative in ((5, 6), (6, 7)):
        u[i][alternative] = max(u[i][6:])
        u[i][0] = max(u[i])
    return tuple(map(tuple, u))


def load_frontier():
    """Load retained search data, which is not a mathematical certificate."""
    import base64
    import zlib

    text = Path(__file__).with_name("PROTECTED_TWELVE.md").read_text()
    def block(name):
        begin, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
        if text.count(begin) != 1 or text.count(end) != 1:
            raise ValueError("missing retained frontier data")
        encoded = "".join(text.split(begin)[1].split(end)[0].split())
        decoder = zlib.decompressobj()
        raw = decoder.decompress(base64.b64decode(encoded, validate=True), 16*1024*1024)
        if not decoder.eof or decoder.unused_data:
            raise ValueError("invalid or oversized retained data")
        data = json.loads(raw)
        if data.get("version") != 1:
            raise ValueError("unknown retained-data version")
        return data

    data = block("twelve-data")
    if "<!-- splice-data:" in text:
        data["splice_search"] = block("splice-data")
    return data


def candidate_cut(u, states):
    """Check the retained finite subgraph only, not the whole allocation graph."""
    graph = Graph(u)
    domain = {tuple(a) for a in states}
    if (START not in domain or TARGET not in domain
            or any(len(a) != 12 or a[0] not in (5, 6)
                   or tuple(a.count(i) for i in range(7)) != (2,)*5+(1, 1)
                   for a in domain)):
        raise ValueError("invalid retained subgraph")
    fair = {a for a in domain if graph.fair(a)}
    if START not in fair or TARGET not in fair:
        raise ValueError("the retained endpoints must be fair")
    seen, pending = {START}, [START]
    while pending:
        a = pending.pop()
        for b in graph.neighbors(a):
            if b in fair and b not in seen:
                seen.add(b)
                pending.append(b)
    return {"candidate_vertices": len(domain), "fair_vertices": len(fair),
            "start_component": len(seen), "target_reached": TARGET in seen,
            "scope": "retained subgraph only"}


def cover_vertices(paths):
    """Validate path shapes and return their union in first-seen order."""
    vertices = {}
    for path in paths:
        if (len(path) < 2 or tuple(path[0]) != START or tuple(path[-1]) != TARGET
                or any(len(a) != 12 or any(type(i) is not int for i in a)
                       or a[0] not in (5, 6)
                       or tuple(a.count(i) for i in range(7)) != (2,)*5+(1, 1)
                       for a in path)
                or any(not exchange(a, b) for a, b in zip(path, path[1:]))):
            raise ValueError("cover contains an invalid protected exchange path")
        for a in path:
            vertices.setdefault(tuple(a), None)
    return tuple(vertices)


def check_cover(u, paths):
    """Check only these proposed paths; zero fair paths is not separation."""
    Graph(u)  # Validate the exact canonical braid domain.
    cover_vertices(paths)
    fair_paths = [index for index, path in enumerate(paths)
                  if all(ef1(u, tuple(a)) for a in path)]
    return {"paths": len(paths), "fair_paths": len(fair_paths),
            "first_fair_path": fair_paths[0] if fair_paths else None,
            "scope": "listed paths only; not a separation of the full graph"}


def common_pair_orbit(path):
    """Relabel the four common pairs into every valid endpoint-fixed path.

    Only allocation labels are transformed. This does not assert symmetry of
    the utilities or their greedy order; each resulting path still needs its
    own EF1 checks in the original profile.
    """
    cover_vertices([path])
    variants = {}
    for order in permutations(range(1, 5)):
        agents = (0,) + order + (5, 6)
        goods = list(range(12))
        for old in range(1, 5):
            goods[old+1], goods[old+7] = agents[old]+1, agents[old]+7
        route = []
        for state in path:
            renamed = [0]*12
            for g, owner in enumerate(state):
                renamed[goods[g]] = agents[owner]
            route.append(tuple(renamed))
        variants.setdefault(tuple(route), None)
    return tuple(variants)


def splice_cover(u, paths):
    """Find a fair path in the induced union, allowing joins between paths.

    Every actual exchange between two union vertices is allowed, even if it
    was absent from the listed paths. An uncovered union is not a full cut.
    """
    vertices = cover_vertices(paths)
    graph = Graph(u)
    fair = {a for a in vertices if graph.fair(a)}
    if START not in fair or TARGET not in fair:
        raise ValueError("the cover must contain both fair canonical endpoints")
    previous, queue = {START: None}, [START]
    route = None
    for a in queue:
        if a == TARGET:
            route = [a]
            while previous[route[-1]] is not None:
                route.append(previous[route[-1]])
            route.reverse()
            break
        for b in graph.neighbors(a):
            if b in fair and b not in previous:
                previous[b] = a
                queue.append(b)
    return {"status": "connected" if route else "uncovered", "path": route,
            "vertices": len(vertices), "fair_vertices": len(fair),
            "reached": len(previous),
            "scope": "induced path union only; uncovered is not full separation"}


def verify_ten_step_distance(u, path):
    """Certify ten as the distance by complete radius-four balls and a path.

    Disjoint balls with no edge between them exclude every path of length at
    most nine. This visits the full protected graph, not a retained subgraph.
    """
    graph = Graph(u)
    path = tuple(map(tuple, path))
    if (len(path) != 11 or path[0] != START or path[-1] != TARGET
            or any(len(a) != 12 or a[0] not in (5, 6)
                   or tuple(a.count(i) for i in range(7)) != (2,)*5+(1, 1)
                   or not graph.fair(a) for a in path)
            or any(not exchange(a, b) for a, b in zip(path, path[1:]))):
        raise ValueError("need a fair ten-exchange protected path between canonical endpoints")

    def ball(root, opposite):
        seen, frontier, layers = {root}, {root}, [1]
        for _ in range(4):
            following = {b for a in frontier for b in graph.neighbors(a)
                         if b not in seen and graph.fair(b)}
            seen.update(following)
            if opposite in seen:
                raise ValueError("a path shorter than ten exists")
            frontier = following
            layers.append(len(frontier))
        return seen, layers

    left, left_layers = ball(START, TARGET)
    right, right_layers = ball(TARGET, START)
    if left & right or any(b in right for a in left for b in graph.neighbors(a)):
        raise ValueError("a path of at most nine exists")
    return {"distance": 10, "radius": 4, "start_layers": left_layers,
            "target_layers": right_layers, "ball_sizes": [len(left), len(right)],
            "intersection": 0, "cross_edges": 0, "checked": len(graph.cache),
            "scope": "this canonical protected pair; no universal distance bound"}


def frontier_vertices(data):
    """Reconstruct the latest pool without replacing any earlier archive."""
    continuation = data.get("splice_search", {})
    vertices = cover_vertices(data["paths"] + continuation.get("added_paths", []))
    if continuation.get("include_original_states"):
        vertices = tuple(map(tuple, data["states"])) + vertices
    return tuple(dict.fromkeys(vertices))


def repaired_frontier(data):
    """Include the saved full-graph repair, after checking its original utilities.

    The default frontier deliberately retains its last witnessed failure.
    This separate entry point prepares the next search without rewriting that
    earlier result or assuming that a solver's proposed path is fair.
    """
    case = data["splice_search"]["final_counterexample"]
    result = case["search"]
    if result["status"] != "connected" or result["path"] is None:
        raise ValueError("resumption needs a completed full-graph repair")
    path = cover_vertices([result["path"]])
    u = tuple(tuple(Fraction(v) for v in row) for row in case["utilities"])
    Graph(u)
    if not all(ef1(u, state) for state in path):
        raise ValueError("saved repair is not fair in its original utilities")
    return tuple(dict.fromkeys(frontier_vertices(data) + path))


def _implied_by_rankings(observer, own, target):
    """Nonnegativity plus one stated rank can settle a whole EF1 comparison."""
    for held in own:
        for remaining_good in target:
            if observer < 5:
                if held == observer+1 and remaining_good > observer+1:
                    return True
            elif held == 0 or (held == observer+1 and remaining_good >= 6):
                return True
    return False


def smt2(states, paths=None):
    """Rebuild the finite real-linear separating-cut query without a solver.

    Writing this query or receiving a solver verdict is not a checked proof.
    """
    states = [tuple(a) for a in states]
    if (len(set(states)) != len(states) or START not in states or TARGET not in states
            or any(len(a) != 12 or any(type(i) is not int for i in a) or a[0] not in (5, 6)
                   or tuple(a.count(i) for i in range(7)) != (2,)*5+(1, 1)
                   for a in states)):
        raise ValueError("need distinct protected vertices and both endpoints")
    lines = ["(set-logic QF_LRA)"]
    for i in range(7):
        for g in range(12):
            lines += [f"(declare-fun u_{i}_{g} () Real)", f"(assert (>= u_{i}_{g} 0))"]
        lines.append(f"(assert (= (+ {' '.join(f'u_{i}_{g}' for g in range(12))}) 1))")
    for i in range(5):
        lines.extend(f"(assert (>= u_{i}_{i+1} u_{i}_{g}))" for g in range(i+2, 12))
    for i, best in ((5, 6), (6, 7)):
        lines.extend(f"(assert (>= u_{i}_0 u_{i}_{g}))" for g in range(12))
        lines.extend(f"(assert (>= u_{i}_{best} u_{i}_{g}))" for g in range(6, 12))
    where = {a: k for k, a in enumerate(states)}
    for k, a in enumerate(states):
        lines.extend((f"(declare-fun f{k} () Bool)", f"(declare-fun r{k} () Bool)"))
        bundles = [[g for g, owner in enumerate(a) if owner == i] for i in range(7)]
        terms = []
        for i in range(7):
            own = f"(+ {' '.join(f'u_{i}_{g}' for g in bundles[i])})"
            for j in range(5):
                if i != j and not _implied_by_rankings(i, bundles[i], bundles[j]):
                    terms.append(f"(or {' '.join(f'(>= {own} u_{i}_{g})' for g in bundles[j])})")
        formula = f"(and {' '.join(terms)})" if terms else "true"
        lines.append(f"(assert (= f{k} {formula}))")
    if paths is not None:
        for path in paths:
            path = [tuple(a) for a in path]
            if (len(path) < 2 or path[0] != START or path[-1] != TARGET
                    or any(a not in where for a in path)
                    or any(not exchange(a, b) for a, b in zip(path, path[1:]))):
                raise ValueError("every covering path must be a valid protected exchange path")
            lines.append(f"(assert (not (and {' '.join(f'f{where[a]}' for a in path)})))")
        lines.append("(check-sat)")
        return "\n".join(lines)+"\n"
    for a, k in where.items():
        for b in Graph.neighbors(a):
            if b in where and where[b] < k:
                j = where[b]
                lines.append(f"(assert (=> (and f{k} f{j}) (= r{k} r{j})))")
    a, b = where[START], where[TARGET]
    lines.extend((f"(assert f{a})", f"(assert f{b})", f"(assert r{a})",
                  f"(assert (not r{b}))", "(check-sat)"))
    return "\n".join(lines)+"\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--input", help="JSON utility rows, integers or rational strings")
    parser.add_argument("--max-checks", type=int, default=200000,
                        help="zero means no search limit")
    parser.add_argument("--frontier", action="store_true", help="replay the retained numeric case")
    parser.add_argument("--write-smt2", help="write the retained finite cut query")
    parser.add_argument("--cover", action="store_true", help="write the path-cover query instead")
    parser.add_argument("--candidate-cut", action="store_true", help="check the retained small graph")
    parser.add_argument("--cover-case", action="store_true",
                        help="replay the last exact counterexample to the retained path cover")
    parser.add_argument("--splice-cover", action="store_true",
                        help="join retained path segments, or export their induced cut query")
    parser.add_argument("--resume-frontier", action="store_true",
                        help="include the checked saved repair in a --splice-cover query export")
    parser.add_argument("--ten-step-case", action="store_true",
                        help="verify the retained exact ten-exchange distance")
    args = parser.parse_args()
    if args.resume_frontier and not (args.splice_cover and args.write_smt2):
        parser.error("--resume-frontier requires --splice-cover and --write-smt2")
    if args.ten_step_case:
        if (args.splice_cover or args.cover_case or args.cover or args.input
                or args.candidate_cut or args.frontier or args.write_smt2):
            parser.error("--ten-step-case cannot be combined with another mode")
        case = load_frontier()["splice_search"]["ten_step_case"]
        u = tuple(tuple(Fraction(x) for x in row) for row in case["utilities"])
        print(json.dumps({**verify_ten_step_distance(u, case["path"]),
                          "utilities": case["utilities"], "path": case["path"]}))
        return
    if args.splice_cover and (args.cover or args.cover_case or args.input
                              or args.candidate_cut or args.frontier):
        parser.error("--splice-cover cannot be combined with another retained mode or input")
    if args.splice_cover and not args.write_smt2:
        data = load_frontier()
        case = data["continuations"][-1]["final_counterexample"]
        u = tuple(tuple(Fraction(v) for v in row) for row in case["utilities"])
        report = {"listed": check_cover(u, data["paths"]),
                  "spliced": splice_cover(u, data["paths"]),
                  "scope": "retained path union; no universal verdict"}
        continuation = data.get("splice_search")
        if continuation and continuation.get("final_counterexample"):
            case = continuation["final_counterexample"]
            v = tuple(tuple(Fraction(x) for x in row) for row in case["utilities"])
            report["frontier"] = {
                "candidate": candidate_cut(v, frontier_vertices(data)),
                "full_graph": Graph(v).search(None if args.max_checks == 0 else args.max_checks)}
        print(json.dumps(report))
        return
    if args.cover_case and (args.input or args.write_smt2 or args.candidate_cut):
        parser.error("--cover-case cannot be combined with another input or retained query")
    if args.cover and not args.write_smt2:
        parser.error("--cover requires --write-smt2")
    if args.cover_case:
        data = load_frontier()
        phases = data.get("continuations", [])
        case = phases[-1].get("final_counterexample") if phases else None
        if case is None:
            parser.error("no exact final path-cover counterexample is retained")
        u = tuple(tuple(Fraction(v) for v in row) for row in case["utilities"])
        report = check_cover(u, data["paths"])
        if report["fair_paths"]:
            raise ValueError("retained valuation no longer defeats the path cover")
        search = Graph(u).search(None if args.max_checks == 0 else args.max_checks)
        print(json.dumps({"cover": report, "search": search, "utilities": case["utilities"],
                          "scope": "finite cover failure; full protected graph checked separately"}))
        return
    if args.write_smt2:
        data = load_frontier()
        paths = data["paths"] if args.cover else None
        states = data["states"] if paths is None else cover_vertices(paths)
        if args.splice_cover:
            states = repaired_frontier(data) if args.resume_frontier else frontier_vertices(data)
        text = smt2(states, paths)
        Path(args.write_smt2).write_text(text)
        print(json.dumps({"bytes": len(text.encode()), "vertices": len(states),
                          "includes_saved_repair": args.resume_frontier,
                          "status": "unverified_solver_input"}))
        return
    if args.candidate_cut:
        data = load_frontier()
        u = tuple(tuple(Fraction(v) for v in row) for row in data["last"]["utilities"])
        print(json.dumps(candidate_cut(u, data["states"])))
        return
    u = profile(args.seed)
    if args.frontier:
        u = tuple(tuple(Fraction(v) for v in row) for row in load_frontier()["last"]["utilities"])
    if args.input:
        with open(args.input) as stream:
            data = json.load(stream)
        if any(type(v) not in (int, str) for row in data for v in row):
            raise ValueError("utilities must be exact integers or rational strings")
        u = tuple(tuple(Fraction(v) for v in row) for row in data)
    result = Graph(u).search(None if args.max_checks == 0 else args.max_checks)
    result["utilities"] = [[str(v) for v in row] for row in u]
    result["scope"] = "one protected graph; universal five-final claim unresolved"
    print(json.dumps(result))


if __name__ == '__main__':
    main()
