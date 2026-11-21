"""Check a finite real-linear proof of the protected eight-good braid.

The proof file is untrusted data. No symbolic solver is imported or executed.
See PROTECTED_LINEAR_CERTIFICATE.md for the exact mathematical statement.
"""

from __future__ import annotations

import argparse
from collections import deque
from fractions import Fraction
from functools import lru_cache
import json
from math import gcd
from pathlib import Path

from five_agent_protected import START, TARGET
from swaps import allocation, ef1, exchange, validate_profile


def need(condition, message):
    if not condition:
        raise ValueError(message)


def literal(value, size):
    need(type(value) is int and 0 < abs(value) <= size, "invalid propositional literal")
    return value


class Formulas:
    """Acyclic Boolean definitions and independently rebuilt mathematical premises."""

    def __init__(self, variables, states, edges):
        self.variables = variables
        self.size = len(variables)
        self.atoms, self.names, self.ops, self.defs = {}, {}, {}, {}
        self.clauses = [(1,)]
        need(variables and variables[0] == ["true"], "variable one must be true")
        for k, spec in enumerate(variables[1:], 2):
            need(isinstance(spec, list) and spec, "invalid variable definition")
            kind = spec[0]
            if kind == "linear":
                need(len(spec) == 3 and type(spec[1]) is int and spec[1] in range(5), "invalid utility row")
                c = spec[2]
                need(len(c) == 8 and all(type(v) is int for v in c) and any(c), "invalid linear form")
                need(gcd(*c) == 1, "linear form is not primitive")
                key = spec[1], tuple(c)
                need(key not in self.atoms, "duplicate linear atom")
                self.atoms[key] = k
            elif kind in ("fair", "reach"):
                need(len(spec) == 2 and type(spec[1]) is int and spec[1] in range(len(states)), "invalid vertex variable")
                need(tuple(spec) not in self.names, "duplicate vertex variable")
                self.names[tuple(spec)] = k
            else:
                need(kind in ("and", "or", "iff") and len(spec) == 2, "unknown Boolean definition")
                args = tuple(literal(v, k - 1) for v in spec[1])
                need(len(args) >= 2 and (kind != "iff" or len(args) == 2), "invalid Boolean arity")
                key = kind, args
                need(key not in self.ops, "duplicate Boolean definition")
                self.ops[key], self.defs[k] = k, key
                if kind == "and":
                    self.clauses.extend((-k, v) for v in args)
                    self.clauses.append((k,) + tuple(-v for v in args))
                elif kind == "or":
                    self.clauses.extend((k, -v) for v in args)
                    self.clauses.append((-k,) + args)
                else:
                    a, b = args
                    self.clauses.extend(((-k, -a, b), (-k, a, -b), (k, a, b), (k, -a, -b)))
        self._premises(states, edges)

    def combine(self, kind, args):
        args = tuple(args)
        if kind == "iff":
            a, b = args
            if a == b:
                return 1
            if a == -b:
                return -1
            args = tuple(sorted(args))
        else:
            args = set(args)
            if (kind == "and" and -1 in args) or (kind == "or" and 1 in args):
                return -1 if kind == "and" else 1
            args.discard(1 if kind == "and" else -1)
            if any(-a in args for a in args):
                return -1 if kind == "and" else 1
            args = tuple(sorted(args))
            if not args:
                return 1 if kind == "and" else -1
            if len(args) == 1:
                return args[0]
        need((kind, args) in self.ops, "missing definition of a mathematical premise")
        return self.ops[kind, args]

    def comparison(self, row, owned, good):
        c = tuple(owned.count(g) - int(g == good) for g in range(8))
        if not any(c):
            return 1
        divisor = gcd(*c)
        key = row, tuple(v // divisor for v in c)
        need(key in self.atoms, "missing utility comparison")
        return self.atoms[key]

    def _premises(self, states, edges):
        def require_true(v):
            self.clauses.append((v,))
        for i in range(5):
            for g in range(8):
                require_true(self.comparison(i, [g], -1))  # u_i(g) >= 0
        for i, anchor in enumerate((1, 2, 3)):
            for g in range(anchor + 1, 8):
                require_true(self.comparison(i, [anchor], g))
        for i, best in ((3, 4), (4, 5)):
            for g in range(8):
                require_true(self.comparison(i, [0], g))
            for g in (4, 5, 6, 7):
                require_true(self.comparison(i, [best], g))
        for k, a in enumerate(states):
            clauses = []
            for i in range(5):
                own = [g for g in range(8) if a[g] == i]
                for j in range(3):
                    if i != j:
                        clauses.append(self.combine("or", (self.comparison(i, own, g)
                                                            for g in range(8) if a[g] == j)))
            fair = self.names["fair", k]
            require_true(self.combine("iff", (fair, self.combine("and", clauses))))
        for a, b in edges:
            same = self.combine("iff", (self.names["reach", a], self.names["reach", b]))
            require_true(self.combine("or", (-self.names["fair", a], -self.names["fair", b], same)))
        a, b = states.index(list(START)), states.index(list(TARGET))
        for v in (self.names["fair", a], self.names["fair", b],
                  self.names["reach", a], -self.names["reach", b]):
            require_true(v)


class BooleanDiagrams:
    """Reduced ordered decision diagrams certify Boolean tautologies exactly."""

    def __init__(self, definitions):
        self.definitions = definitions
        self.nodes, self.unique, self.values = [None, None], {}, {}
        self.negated, self.applied = {0: 1, 1: 0}, {}

    def node(self, v, low, high):
        if low == high:
            return low
        key = v, low, high
        if key not in self.unique:
            self.unique[key] = len(self.nodes)
            self.nodes.append(key)
        return self.unique[key]

    def negate(self, a):
        if a not in self.negated:
            v, low, high = self.nodes[a]
            self.negated[a] = self.node(v, self.negate(low), self.negate(high))
        return self.negated[a]

    def apply(self, op, a, b):
        a, b = sorted((a, b))
        key = op, a, b
        if key in self.applied:
            return self.applied[key]
        if op == "and" and a == 0:
            result = 0
        elif op == "or" and (a == 1 or b == 1):
            result = 1
        elif a == b:
            result = a
        elif (op == "and" and a == 1) or (op == "or" and a == 0):
            result = b
        else:
            av, al, ah = self.nodes[a]
            bv, bl, bh = self.nodes[b]
            v = min(av, bv)
            al, ah = (al, ah) if av == v else (a, a)
            bl, bh = (bl, bh) if bv == v else (b, b)
            result = self.node(v, self.apply(op, al, bl), self.apply(op, ah, bh))
        self.applied[key] = result
        return result

    def value(self, lit):
        if lit < 0:
            return self.negate(self.value(-lit))
        if lit == 1:
            return 1
        if lit not in self.values:
            if lit not in self.definitions:
                result = self.node(lit, 0, 1)
            else:
                op, args = self.definitions[lit]
                xs = [self.value(v) for v in args]
                if op == "iff":
                    a, b = xs
                    result = self.apply("or", self.apply("and", a, b),
                                        self.apply("and", self.negate(a), self.negate(b)))
                else:
                    result = 1 if op == "and" else 0
                    for v in xs:
                        result = self.apply(op, result, v)
            self.values[lit] = result
        return self.values[lit]

    def tautology(self, clause):
        result = 0
        for v in clause:
            result = self.apply("or", result, self.value(v))
        return result == 1


class Propagation:
    """Two watched literals implement reverse unit propagation (RUP)."""

    def __init__(self):
        self.clauses, self.positions, self.units, self.watch = [], [], [], {}
        self.empty = False

    def add(self, clause):
        clause = tuple(sorted(set(clause)))
        if any(-v in clause for v in clause):
            return
        k = len(self.clauses)
        self.clauses.append(clause)
        if not clause:
            self.empty = True
        if len(clause) < 2:
            self.units.extend(clause)
            self.positions.append(None)
        else:
            self.positions.append([0, 1])
            for v in clause[:2]:
                self.watch.setdefault(v, set()).add(k)

    def contradiction(self, assumed_clause):
        if self.empty:
            return True
        assigned = set()
        queue = self.units + [-v for v in assumed_clause]
        while queue:
            v = queue.pop()
            if v in assigned:
                continue
            if -v in assigned:
                return True
            assigned.add(v)
            for k in list(self.watch.get(-v, ())):
                clause, positions = self.clauses[k], self.positions[k]
                slot = 0 if clause[positions[0]] == -v else 1
                other = clause[positions[1 - slot]]
                if other in assigned:
                    continue
                replacement = next((j for j, x in enumerate(clause)
                                    if j not in positions and -x not in assigned), None)
                if replacement is not None:
                    self.watch[-v].remove(k)
                    self.watch.setdefault(clause[replacement], set()).add(k)
                    positions[slot] = replacement
                elif -other in assigned:
                    return True
                else:
                    queue.append(other)
        return False


def verify_certificate(data):
    """Prove that no fair cut separates the two canonical protected endpoints."""
    need(data.get("format") == "protected-eight-rup-v1", "unknown proof format")
    states, edges = data["states"], data["edges"]
    need(states and len({tuple(a) for a in states}) == len(states), "duplicate vertices")
    for a in states:
        need(len(a) == 8 and all(type(i) is int and i in range(5) for i in a)
             and tuple(a.count(i) for i in range(5)) == (2, 2, 2, 1, 1)
             and a[0] in (3, 4), "invalid protected allocation")
    need(list(START) in states and list(TARGET) in states, "missing endpoints")
    for a, b in edges:
        need(type(a) is int and type(b) is int and a in range(len(states))
             and b in range(len(states)) and exchange(tuple(states[a]), tuple(states[b])), "invalid exchange edge")
    formulas = Formulas(data["variables"], states, edges)
    propagation = Propagation()
    for clause in formulas.clauses:
        propagation.add(clause)
    def checked_clause(clause):
        need(isinstance(clause, list), "proof clauses must be lists")
        return tuple(literal(v, formulas.size) for v in clause)
    for clause, weights in data["theory"]:
        clause = checked_clause(clause)
        need(all(abs(v) in {value for value in formulas.atoms.values()} for v in clause), "nonlinear theory clause")
        total = [[Fraction(0) for _ in range(8)] for _ in range(5)]
        strict = False
        for index, numerator, denominator in weights:
            need(type(index) is int and index in range(len(clause)) and type(numerator) is int
                 and type(denominator) is int and numerator > 0 and denominator > 0, "invalid positive multiplier")
            v = clause[index]
            _, row, coefficients = formulas.variables[abs(v) - 1]
            factor = Fraction(numerator, denominator) * (-1 if v > 0 else 1)
            for g, coefficient in enumerate(coefficients):
                total[row][g] += factor * coefficient
            strict |= v > 0
        need(strict and not any(value for row in total for value in row), "linear contradiction does not sum to zero")
        propagation.add(clause)
    diagrams = BooleanDiagrams(formulas.defs)
    for clause in data["tautologies"]:
        clause = checked_clause(clause)
        need(diagrams.tautology(clause), "claimed Boolean tautology is false")
        propagation.add(clause)
    proof = data["proof"]
    need(proof and proof[-1] == [], "proof must conclude with the empty clause")
    for k, clause in enumerate(proof):
        clause = checked_clause(clause)
        need(propagation.contradiction(clause), f"RUP step {k} is not justified")
        propagation.add(clause)
    return {"vertices": len(states), "edges": len(edges), "variables": formulas.size,
            "linear_lemmas": len(data["theory"]), "Boolean_lemmas": len(data["tautologies"]),
            "RUP_steps": len(proof)}


@lru_cache(maxsize=1)
def _verified_data():
    file = Path(__file__).with_name("protected_linear_certificate.json")
    data = json.loads(file.read_text())
    return data, verify_certificate(data)


def verified_proof():
    return _verified_data()[1]


def protected_bridge(u):
    """Construct the canonical braid while keeping g with a singleton."""
    validate_profile(u)
    need(len(u) == 5 and len(u[0]) == 8, "need five agents and eight goods")
    need(all(u[i][h] >= u[i][g] for i, h in enumerate((1, 2, 3)) for g in range(h + 1, 8))
         and all(u[i][0] >= value for i in (3, 4) for value in u[i])
         and all(u[i][h] >= u[i][g] for i, h in ((3, 4), (4, 5)) for g in (4, 5, 6, 7)),
         "braid hypotheses fail")
    data, _ = _verified_data()
    states = [tuple(a) for a in data["states"]]
    neighbors = [[] for _ in states]
    for a, b in data["edges"]:
        neighbors[a].append(b)
        neighbors[b].append(a)
    fair = {k for k, a in enumerate(states) if ef1(u, a)}
    first, last = states.index(START), states.index(TARGET)
    previous = {first: None}
    queue = deque([first])
    while queue:
        a = queue.popleft()
        if a == last:
            route = [a]
            while previous[route[-1]] is not None:
                route.append(previous[route[-1]])
            return [states[k] for k in reversed(route)]
        for b in neighbors[a]:
            if b in fair and b not in previous:
                previous[b] = a
                queue.append(b)
    raise AssertionError("certified protected endpoints disconnected")


def padded_bridge(u, prefix, tail):
    """Lift the certified local bridge through common greedy complete rounds."""
    validate_profile(u)
    m = len(u[0])
    need(len(u) == 5 and m >= 8 and m % 5 == 3
         and len(tail) == 8 and len(set(tail)) == 8
         and all(type(g) is int and g in range(m) for g in tail)
         and len(prefix) == m - 8, "invalid padded braid shape")
    remaining = set(range(m)) - {tail[0]}
    common = [[] for _ in range(5)]
    for offset in range(0, len(prefix), 5):
        round_picks = prefix[offset:offset + 5]
        need({i for i, _ in round_picks} == set(range(5)), "prefix round is incomplete")
        for i, g in round_picks:
            need(g in remaining and u[i][g] == max(u[i][h] for h in remaining), "prefix is not greedy with g omitted")
            common[i].append(g)
            remaining.remove(g)
    need(remaining == set(tail[1:]), "prefix leaves the wrong tail goods")
    need(all(sum(row[g] for g in common[a]) >= sum(row[g] for g in common[b])
             for a, row in enumerate(u) for b in (3, 4) if a != b), "missing carrier dominance")
    local = tuple(tuple(row[g] for g in tail) for row in u)
    result = []
    for a in protected_bridge(local):
        full = list(allocation(tuple(prefix), m))
        for g, owner in zip(tail, a):
            full[g] = owner
        result.append(tuple(full))
    need(all(ef1(u, a) for a in result) and all(exchange(a, b) for a, b in zip(result, result[1:])), "padding lost EF1")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, help="check a different proof file")
    args = parser.parse_args()
    if args.certificate:
        print(json.dumps(verify_certificate(json.loads(args.certificate.read_text())), indent=2))
    else:
        from five_agent_eight import EXAMPLE
        print(json.dumps({"proof": verified_proof(),
                          "path": ["".join(map(str, a)) for a in protected_bridge(EXAMPLE)]}, indent=2))
