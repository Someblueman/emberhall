"""Exact integer search for a fixed repeated-word tripod template.

Every original two-variable coefficient is retained. A search limit is not
a negative answer. See INTEGER_TEMPLATE_DECISION.md for the scope and proof.
"""
from __future__ import annotations

import argparse
from collections import deque
from functools import lru_cache
import heapq
import json
from pathlib import Path

import coupled_word_completion as coupled

FORMAT = "tripod-integer-template-v1"
PERIOD = 320
BASE = (427, 267, 211)
CUTS = (213, 133, 105)
SHAPES = [[("literal", cut), ("repeat", PERIOD),
           ("literal", length - (arm < 2) - cut)]
          for arm, (length, cut) in enumerate(zip(BASE, CUTS))]


@lru_cache(maxsize=65536)
def subset_sums(counts):
    """Bit t is set iff the multiset of positive weights has a subset of sum t."""
    possible = 1
    for weight, count in enumerate(counts):
        for _ in range(count):
            possible |= possible << weight
    return possible


class IntegerSearch:
    """Integer-row propagation and resolution learning on the original bits.

    Bit b means sign 1-2b. Negative row coefficients use the complemented
    bit. Thus each row becomes a positive weighted sum equal to half its
    total weight. Reasons are Boolean clauses implied by that exact row;
    learned clauses follow by resolution, not by relaxing the integer rows.
    """

    def __init__(self, rows, variables):
        self.rows = list(rows.values())
        self.n = variables
        self.width = max((abs(a) for r in self.rows for a in r.values()), default=0)
        self.incidents = [[] for _ in range(variables + 1)]
        self.counts, self.targets = [], []
        self.impossible_row = False
        for number, row in enumerate(self.rows):
            counts = [0] * (self.width + 1)
            total = sum(abs(a) for a in row.values())
            self.impossible_row |= bool(total % 2)
            self.targets.append(total // 2)
            for index, coefficient in row.items():
                self.incidents[index + 1].append((number, coefficient))
                counts[abs(coefficient)] += 1
            self.counts.append(counts)
        self.values = [0] * (variables + 1)
        self.levels = [0] * (variables + 1)
        self.reasons = [None] * (variables + 1)
        self.phase = [-1] * (variables + 1)
        self.activity = [float(len(a)) for a in self.incidents]
        self.heap = [(-self.activity[v], v) for v in range(1, variables + 1)]
        heapq.heapify(self.heap)
        self.trail, self.limits = [], []
        self.queue, self.pending = deque(), set()
        self.qhead = 0
        self.clauses = []
        self.watches = [[] for _ in range(2 * variables + 1)]
        self.increment = 1.0
        self.conflicts = self.decisions = self.maximum_depth = 0
        self.integer_reasons = 0
        for number in range(len(self.rows)):
            self.schedule(number)
        # Global sign reversal preserves every homogeneous equation.
        self.enqueue(-1, [-1])

    def schedule(self, number):
        if number not in self.pending:
            self.pending.add(number)
            self.queue.append(number)

    def literal_value(self, literal):
        return self.values[abs(literal)] * (1 if literal > 0 else -1)

    def enqueue(self, literal, reason):
        variable = abs(literal)
        value = 1 if literal > 0 else -1
        if self.values[variable]:
            return self.values[variable] == value
        self.values[variable] = self.phase[variable] = value
        self.levels[variable] = len(self.limits)
        self.reasons[variable] = reason
        self.trail.append(literal)
        for number, coefficient in self.incidents[variable]:
            weight = abs(coefficient)
            self.counts[number][weight] -= 1
            self.targets[number] -= weight * (value * coefficient > 0)
            self.schedule(number)
        return True

    def integer_reason(self, number, forced=None):
        # Negating a forced literal, or the current conflicting assignments,
        # leaves no subset of the remaining weights with the required sum.
        # Relax irrelevant assignments one at a time. Each retained reason
        # still has an exact subset-sum contradiction, even after relaxation.
        counts = list(self.counts[number])
        target = self.targets[number]
        if forced is not None:
            coefficient = self.rows[number][abs(forced) - 1]
            weight = abs(coefficient)
            counts[weight] -= 1
            opposite = forced < 0 if coefficient > 0 else forced > 0
            target -= weight * opposite
        result = [] if forced is None else [forced]
        for index, coefficient in self.rows[number].items():
            variable = index + 1
            if not self.values[variable] or (forced is not None and variable == abs(forced)):
                continue
            weight = abs(coefficient)
            bit = self.values[variable] * coefficient > 0
            counts[weight] += 1
            target += weight * bit
            if target >= 0 and (subset_sums(tuple(counts)) >> target) & 1:
                counts[weight] -= 1
                target -= weight * bit
                result.append(-variable * self.values[variable])
        self.integer_reasons += 1
        return result

    def propagate(self):
        while True:
            while self.qhead < len(self.trail):
                false = -self.trail[self.qhead]
                self.qhead += 1
                watched = self.watches[false]
                position = 0
                while position < len(watched):
                    number = watched[position]
                    clause = self.clauses[number]
                    if not clause:  # retired, redundant learned clause
                        watched[position] = watched[-1]
                        watched.pop()
                        continue
                    if clause[0] == false:
                        clause[0], clause[1] = clause[1], clause[0]
                    first = clause[0]
                    if self.literal_value(first) > 0:
                        position += 1
                        continue
                    for replacement in range(2, len(clause)):
                        if self.literal_value(clause[replacement]) >= 0:
                            clause[1], clause[replacement] = clause[replacement], clause[1]
                            watched[position] = watched[-1]
                            watched.pop()
                            self.watches[clause[1]].append(number)
                            break
                    else:
                        if self.literal_value(first) < 0:
                            return clause
                        self.enqueue(first, clause)
                        position += 1
            if not self.queue:
                return None
            number = self.queue.popleft()
            self.pending.remove(number)
            counts, target = self.counts[number], self.targets[number]
            if target < 0 or not (subset_sums(tuple(counts)) >> target) & 1:
                return self.integer_reason(number)
            forced = {}
            for weight in range(1, self.width + 1):
                if not counts[weight]:
                    continue
                counts[weight] -= 1
                possible = subset_sums(tuple(counts))
                counts[weight] += 1
                zero = bool((possible >> target) & 1)
                one = target >= weight and bool((possible >> (target - weight)) & 1)
                if not zero:
                    forced[weight] = 1
                elif not one:
                    forced[weight] = 0
            for index, coefficient in self.rows[number].items():
                variable = index + 1
                if not self.values[variable] and abs(coefficient) in forced:
                    bit = forced[abs(coefficient)]
                    if coefficient < 0:
                        bit = 1 - bit
                    literal = variable if bit else -variable
                    self.enqueue(literal, self.integer_reason(number, literal))

    def backtrack(self, level):
        if len(self.limits) <= level:
            return
        cut = self.limits[level]
        for literal in self.trail[cut:]:
            variable = abs(literal)
            for number, coefficient in self.incidents[variable]:
                self.counts[number][abs(coefficient)] += 1
                self.targets[number] += abs(coefficient) * (literal * coefficient > 0)
            self.values[variable] = 0
            self.reasons[variable] = None
            heapq.heappush(self.heap, (-self.activity[variable], variable))
        del self.trail[cut:]
        del self.limits[level:]
        self.qhead = len(self.trail)
        self.queue.clear()
        self.pending.clear()

    def analyze(self, conflict):
        """Resolve reasons to the first unique implication point."""
        seen, learned = set(), [0]
        paths, position, pivot = 0, len(self.trail) - 1, 0
        while True:
            for literal in conflict:
                variable = abs(literal)
                if variable == abs(pivot) or variable in seen or not self.levels[variable]:
                    continue
                seen.add(variable)
                self.activity[variable] += self.increment
                heapq.heappush(self.heap, (-self.activity[variable], variable))
                if self.levels[variable] == len(self.limits):
                    paths += 1
                else:
                    learned.append(literal)
            while abs(self.trail[position]) not in seen:
                position -= 1
            pivot = self.trail[position]
            position -= 1
            seen.remove(abs(pivot))
            paths -= 1
            if not paths:
                break
            conflict = self.reasons[abs(pivot)]
            if conflict is None:
                raise AssertionError("resolution reached a second decision")
        learned[0] = -pivot
        members = set(learned)
        for literal in learned[1:]:
            reason = self.reasons[abs(literal)]
            if reason is not None and all(
                    abs(q) == abs(literal) or not self.levels[abs(q)] or q in members
                    for q in reason):
                members.discard(literal)
        learned = [q for q in learned if q in members]
        back = 0
        if len(learned) > 1:
            second = max(range(1, len(learned)), key=lambda i: self.levels[abs(learned[i])])
            learned[1], learned[second] = learned[second], learned[1]
            back = self.levels[abs(learned[1])]
        return learned, back

    def retire_clauses(self):
        # Dropping a learned consequence cannot drop an original equation.
        locked = {id(r) for v, r in enumerate(self.reasons) if self.values[v]}
        for number in range(max(0, len(self.clauses) - 10000)):
            clause = self.clauses[number]
            if len(clause) > 4 and id(clause) not in locked:
                self.clauses[number] = []
        self.heap = [(-self.activity[v], v) for v in range(1, self.n + 1)
                     if not self.values[v]]
        heapq.heapify(self.heap)

    def solve(self, max_conflicts):
        if type(max_conflicts) is not int or not 1 <= max_conflicts <= 1000000:
            raise ValueError("max_conflicts must be between 1 and 1000000")
        restart, next_restart = 100, 100
        if self.impossible_row:
            return False
        while True:
            conflict = self.propagate()
            if conflict is not None:
                self.conflicts += 1
                if not self.limits:
                    return False
                if self.conflicts >= max_conflicts:
                    return None
                learned, back = self.analyze(conflict)
                self.backtrack(back)
                number = len(self.clauses)
                self.clauses.append(learned)
                if len(learned) > 1:
                    self.watches[learned[0]].append(number)
                    self.watches[learned[1]].append(number)
                self.enqueue(learned[0], learned)
                self.increment /= 0.95
                if self.increment > 1e100:
                    self.activity = [a * 1e-100 for a in self.activity]
                    self.increment *= 1e-100
                    self.retire_clauses()
                if self.conflicts % 5000 == 0:
                    self.retire_clauses()
            else:
                if self.conflicts >= next_restart:
                    self.backtrack(0)
                    restart = int(restart * 1.5)
                    next_restart = self.conflicts + restart
                while self.heap:
                    activity, variable = heapq.heappop(self.heap)
                    if not self.values[variable] and activity == -self.activity[variable]:
                        break
                else:
                    # Do not rely on the propagation engine to certify a word.
                    if any(sum(a * -self.values[i + 1] for i, a in row.items())
                           for row in self.rows):
                        raise AssertionError("candidate violates an original integer coefficient")
                    return True
                self.decisions += 1
                self.limits.append(len(self.trail))
                self.maximum_depth = max(self.maximum_depth, len(self.limits))
                self.enqueue(variable * self.phase[variable], None)


def solve(max_conflicts=100000):
    rows, variables, base, growth = coupled.compile_shape(PERIOD, SHAPES)
    engine = IntegerSearch(rows, len(variables))
    exists = engine.solve(max_conflicts)
    result = {"format": FORMAT, "period": PERIOD, "base_lengths": base,
              "prefix_lengths": list(CUTS), "growth": growth,
              "max_conflicts": max_conflicts, "sign_variables": len(variables),
              "coefficient_rows": len(rows), "conflicts": engine.conflicts,
              "decisions": engine.decisions, "maximum_depth": engine.maximum_depth,
              "integer_reasons": engine.integer_reasons,
              "status": "resource_limit" if exists is None else "exact",
              "template_existence_decided": exists is not None,
              "general_target_decided": False, "all_hole_supports_excluded": False}
    if exists is not None:
        result["exists"] = exists
    if exists:
        signs = {(a, s, k): "+" if engine.values[i + 1] < 0 else "-"
                 for i, (a, s, k) in enumerate(variables)}
        word = {"format": coupled.FORMAT, "centre": 1, "period": PERIOD,
                "arms": [[{kind: "".join(signs[a, s, k] for k in range(size))}
                          for s, (kind, size) in enumerate(arm)]
                         for a, arm in enumerate(SHAPES, 1)]}
        coupled.verify_word(word)
        result["word"] = word
    return result


def known_obstruction():
    """Strengthen the accepted 24-letter certificate to individual targets.

    This does not decide the surviving 320-letter template. The inherited
    parity contradiction is replayed, then the finite separation bound is
    computed from every row of that exact shape.
    """
    saved = coupled.target_probe()
    period = saved["period"]
    shapes = [[("literal", cut), ("repeat", period),
               ("literal", length - (arm < 2) - cut)]
              for arm, (length, cut) in enumerate(zip(
                  saved["base_lengths"], saved["prefix_lengths"]))]
    rows, _, _, _ = coupled.compile_shape(period, shapes)
    degrees = [z for z, _ in rows]
    span = max(degrees) - min(degrees)
    cutoff = span // period + 1
    # 347+24(315t-5)=227+7560t, and likewise for the other arms.
    for base, target_base in zip(saved["base_lengths"], (227, 67, 11)):
        if base - 5 * period != target_base or 315 * period != 7560:
            raise AssertionError("target embedding changed")
    if 315 - 5 < cutoff:
        raise AssertionError("first target does not exceed the separation bound")
    return {"format": "tripod-pointwise-template-obstruction-v1",
            "period": period, "base_lengths": saved["base_lengths"],
            "prefix_lengths": saved["prefix_lengths"], "z_span": span,
            "separating_repeat_count": cutoff,
            "every_individual_target_t_at_least": 1,
            "signs_may_depend_on_repetition": True,
            "contradiction": saved["contradiction"],
            "general_target_decided": False, "all_hole_supports_excluded": False}


def verify(saved):
    if type(saved) is dict and saved.get("format") == "tripod-pointwise-template-obstruction-v1":
        if json.dumps(saved, sort_keys=True) != json.dumps(known_obstruction(), sort_keys=True):
            raise ValueError("altered pointwise obstruction")
        return {"valid": True, "status": "exact", "general_target_decided": False}
    if type(saved) is not dict or saved.get("format") != FORMAT:
        raise ValueError("expected an integer-template receipt")
    expected = solve(saved.get("max_conflicts"))
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError("receipt differs from exact deterministic replay")
    return {"valid": True, "status": expected["status"],
            "template_existence_decided": expected["template_existence_decided"],
            "general_target_decided": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--solve", action="store_true")
    mode.add_argument("--known-obstruction", action="store_true")
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--max-conflicts", type=int, default=100000)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args(argv)
    try:
        result = (verify(json.loads(args.verify.read_text())) if args.verify
                  else known_obstruction() if args.known_obstruction
                  else solve(args.max_conflicts))
        if args.write:
            args.write.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({k: v for k, v in result.items() if k not in ("word", "contradiction")},
                         sort_keys=True))
        return 2 if result.get("status") == "resource_limit" else 0
    except (ValueError, OSError, TypeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
