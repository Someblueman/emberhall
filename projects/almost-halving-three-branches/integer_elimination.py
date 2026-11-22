"""Exact coordinate elimination for the full repeated-word shell equations.

This is an equivalent, smaller sign problem, not an existence decision.
No floating point, external solver, or search budget enters the reduction.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from math import gcd
from pathlib import Path

import coupled_word_completion as coupled

FORMAT = "tripod-integer-elimination-v1"
PERIOD = 320
BASE = (427, 267, 211)
CUTS = (213, 133, 105)
SHAPES = [[("literal", cut), ("repeat", PERIOD),
           ("literal", length - (arm < 2) - cut)]
          for arm, (length, cut) in enumerate(zip(BASE, CUTS))]


def primitive(row):
    """Divide a nonzero integer row by its signed coefficient gcd."""
    row = {i: a for i, a in row.items() if a}
    if not row:
        return row
    divisor = gcd(*row.values()) * (1 if row[min(row)] > 0 else -1)
    return {i: a // divisor for i, a in row.items()}


def cancel(row, other, pivot):
    """Eliminate one coefficient by a reversible rational row operation."""
    a, b = row[pivot], other[pivot]
    divisor = gcd(a, b)
    a, b = a // divisor, b // divisor
    result = {i: c * b for i, c in row.items()}
    for i, c in other.items():
        result[i] = result.get(i, 0) - a * c
    return primitive(result)


class Reduction:
    """A rational kernel parametrization with exact sign-domain recovery."""

    def __init__(self, rows, variables):
        self.original = [dict(row) for row in rows]
        self.variables = variables
        self.parents = list(range(variables))
        self.orientations = [1] * variables

        # A two-term row a*x+b*y=0 with |a|=|b| identifies literal signs.
        # These are also reversible substitutions over the rationals.
        while True:
            changed = False
            for row in self.original:
                reduced = self.substitute(row)
                if len(reduced) != 2:
                    continue
                (i, a), (j, b) = reduced.items()
                if abs(a) == abs(b):
                    self.parents[j] = i
                    self.orientations[j] = -a // b
                    changed = True
            if not changed:
                break
        self.links = [self.find(i) for i in range(variables)]
        self.roots = sorted({root for root, _ in self.links})
        active = {j: primitive(self.substitute(row))
                  for j, row in enumerate(self.original)}
        active = {j: row for j, row in active.items() if row}
        basis = []
        while active:
            number = min(active, key=lambda j: (len(active[j]), j))
            row = active.pop(number)
            incidence = Counter(i for other in active.values() for i in other)
            pivot = min(row, key=lambda i: (incidence[i], i))
            basis.append((pivot, row))
            for j, other in list(active.items()):
                if pivot not in other:
                    continue
                reduced = cancel(other, row, pivot)
                if reduced:
                    active[j] = reduced
                else:
                    del active[j]

        self.equations = {}
        for pivot, row in reversed(basis):
            for other in list(row):
                if other in self.equations:
                    row = cancel(row, self.equations[other], other)
            self.equations[pivot] = row
        self.free = [i for i in self.roots if i not in self.equations]
        self.rank = variables - len(self.free)
        self.parity, self.parity_inconsistent, self.parity_sources = self.free_parity()
        self.parameters = [i for j, i in enumerate(self.free) if j not in self.parity]
        self.congruence = self.sign_congruence()
        if self.congruence is not None:
            self.parameters.remove(self.congruence[1])

    def sign_congruence(self):
        """A modulo-five row may determine a sign absent from all parity rows."""
        occupied = {self.free[j] for mask, _ in self.parity.values()
                    for j in range(len(self.free)) if (mask >> j) & 1}
        candidates = [i for i in self.parameters if i not in occupied]
        for pivot, row in sorted(self.equations.items()):
            if row[pivot] % 5:
                continue
            for variable in candidates:
                if row.get(variable, 0) % 5:
                    return pivot, variable, 5
        return None

    def free_parity(self):
        """Necessary GF(2) equations after exact rational elimination.

        An even pivot coefficient vanishes modulo two in the bit equation
        sum(a_i*b_i) = sum(a_i)/2. This leaves only free coordinates.
        """
        positions = {i: j for j, i in enumerate(self.free)}
        basis, inconsistent, sources = {}, False, {}
        for pivot, row in self.equations.items():
            if sum(row.values()) % 2:
                inconsistent = True
                continue
            if row[pivot] % 2:
                continue
            mask = sum(1 << positions[i] for i, a in row.items()
                       if i != pivot and a % 2)
            rhs = (sum(row.values()) // 2) % 2
            witness = 1 << pivot
            while mask:
                bit = mask.bit_length() - 1
                if bit not in basis:
                    basis[bit] = (mask, rhs)
                    sources[bit] = witness
                    break
                old, value = basis[bit]
                mask, rhs = mask ^ old, rhs ^ value
                witness ^= sources[bit]
            else:
                inconsistent |= bool(rhs)
        return basis, inconsistent, sources

    def find(self, i):
        if self.parents[i] != i:
            parent, sign = self.find(self.parents[i])
            self.orientations[i] *= sign
            self.parents[i] = parent
        return self.parents[i], self.orientations[i]

    def substitute(self, row):
        result = defaultdict(int)
        for i, a in row.items():
            root, sign = self.find(i)
            result[root] += a * sign
        return {i: a for i, a in result.items() if a}

    def validate(self):
        """Check the parametrization against every original equation."""
        free = set(self.free)
        if len(self.roots) != len(self.equations) + len(free):
            raise ValueError("wrong partition of root coordinates")
        for pivot, row in self.equations.items():
            if not row.get(pivot) or set(row) - {pivot} - free:
                raise ValueError("equation is not solved in free coordinates")
        for original in self.original:
            row = self.substitute(original)
            for pivot in list(row):
                if pivot in self.equations:
                    row = cancel(row, self.equations[pivot], pivot)
            if row:
                raise ValueError("reduction does not imply an original equation")
        positions = {i: j for j, i in enumerate(self.free)}
        for bit, (expected_mask, expected_rhs) in self.parity.items():
            mask = rhs = 0
            for pivot, row in self.equations.items():
                if not (self.parity_sources[bit] >> pivot) & 1:
                    continue
                if row[pivot] % 2 or sum(row.values()) % 2:
                    raise ValueError("invalid source for a free parity equation")
                mask ^= sum(1 << positions[i] for i, a in row.items()
                            if i != pivot and a % 2)
                rhs ^= (sum(row.values()) // 2) % 2
            if (mask, rhs) != (expected_mask, expected_rhs):
                raise ValueError("parity equation differs from its exact row sources")
        if self.congruence is not None:
            pivot, variable, modulus = self.congruence
            row = self.equations[pivot]
            if row[pivot] % modulus or gcd(row[variable], modulus) != 1:
                raise ValueError("invalid modular sign recovery")
            position = self.free.index(variable)
            if any((mask >> position) & 1 for mask, _ in self.parity.values()):
                raise ValueError("modular recovery must follow independent parity recovery")
        return True

    def lift(self, values):
        """Return the unique full sign vector, or reject a free assignment."""
        if (type(values) is not list or len(values) != len(self.free)
                or any(type(a) is not int or a not in (-1, 1) for a in values)):
            raise ValueError("expected one literal integer sign per free coordinate")
        signs = dict(zip(self.free, values))
        for pivot, row in self.equations.items():
            numerator = -sum(a * signs[i] for i, a in row.items() if i != pivot)
            denominator = row[pivot]
            value, remainder = divmod(numerator, denominator)
            if remainder or value not in (-1, 1):
                raise ValueError(f"free assignment does not recover a sign at {pivot}")
            signs[pivot] = value
        full = [sign * signs[root] for root, sign in self.links]
        if any(sum(a * full[i] for i, a in row.items()) for row in self.original):
            raise ValueError("recovered signs violate an original equation")
        return full

    def lift_parameters(self, values):
        """Recover the free signs from the smaller parity parametrization."""
        if (type(values) is not list or len(values) != len(self.parameters)
                or any(type(a) is not int or a not in (-1, 1) for a in values)):
            raise ValueError("expected one literal integer sign per parameter")
        if self.parity_inconsistent:
            raise ValueError("odd-sign parity conditions are contradictory")
        supplied = dict(zip(self.parameters, values))
        bits = {j: (1 - supplied[i]) // 2 for j, i in enumerate(self.free)
                if i in supplied}
        for pivot, (mask, rhs) in sorted(self.parity.items()):
            bits[pivot] = rhs ^ (sum(bits[j] for j in bits
                                    if j != pivot and (mask >> j) & 1) % 2)
        if self.congruence is not None:
            pivot, variable, modulus = self.congruence
            row = self.equations[pivot]
            position = {i: j for j, i in enumerate(self.free)}
            residual = sum(a * (1 - 2 * bits[position[i]]) for i, a in row.items()
                           if i not in (pivot, variable))
            value = (-residual * pow(row[variable], -1, modulus)) % modulus
            if value not in (1, modulus - 1):
                raise ValueError("modular recovery is not a literal sign")
            bits[position[variable]] = 0 if value == 1 else 1
        return self.lift([1 - 2 * bits[j] for j in range(len(self.free))])

    def export(self):
        return {"free": self.free, "parameters": self.parameters, "links": self.links,
                "parity": [[p, [j for j in range(len(self.free)) if (mask >> j) & 1], rhs,
                            [i for i in self.equations if (self.parity_sources[p] >> i) & 1]]
                           for p, (mask, rhs) in sorted(self.parity.items())],
                "parity_inconsistent": self.parity_inconsistent,
                "sign_congruence": self.congruence,
                "equations": [[p, sorted(r.items())]
                              for p, r in sorted(self.equations.items())]}


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":"),
                                     sort_keys=True).encode()).hexdigest()


def build(control=False):
    if control:
        rows, variables, base, growth, _ = coupled.parse_word(coupled.control())
        period = 4
    else:
        rows, variables, base, growth = coupled.compile_shape(PERIOD, SHAPES)
        period = PERIOD
    reduction = Reduction(list(rows.values()), len(variables))
    reduction.validate()
    report = {"format": FORMAT, "template": "control" if control else "target-320",
              "period": period, "base_lengths": base, "growth": growth,
              "sign_variables": len(variables), "coefficient_rows": len(rows),
              "pair_identifications": len(variables) - len(reduction.roots),
              "rational_rank": reduction.rank, "free_signs": reduction.free,
              "parameter_signs": reduction.parameters, "free_parity_rank": len(reduction.parity),
              "sign_congruence": reduction.congruence,
              "equations_sha256": digest(reduction.export()),
              "input_sha256": digest([[list(k), sorted(r.items())] for k, r in rows.items()]),
              "template_existence_decided": False, "general_target_decided": False}
    return reduction, report


def verify(saved):
    if type(saved) is not dict or saved.get("template") not in ("control", "target-320"):
        raise ValueError("unknown reduction template")
    _, expected = build(saved["template"] == "control")
    if json.dumps(saved, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError("altered elimination receipt")
    return {"valid": True, "rational_rank": expected["rational_rank"],
            "free_sign_count": len(expected["free_signs"]),
            "parameter_sign_count": len(expected["parameter_signs"]),
            "template_existence_decided": False, "general_target_decided": False}


def word_from_signs(signs, control=False):
    if control:
        word = coupled.control()
        _, variables, _, _, _ = coupled.parse_word(word)
    else:
        _, variables, _, _ = coupled.compile_shape(PERIOD, SHAPES)
        word = {"format": coupled.FORMAT, "centre": signs[0], "period": PERIOD,
                "arms": [[{kind: "+" * size} for kind, size in arm] for arm in SHAPES]}
    word["centre"] = signs[0]
    for i, (arm, segment, letter) in enumerate(variables[1:], 1):
        item = word["arms"][arm - 1][segment]
        kind, text = next(iter(item.items()))
        item[kind] = text[:letter] + ("+" if signs[i] == 1 else "-") + text[letter + 1:]
    coupled.verify_word(word)
    return word


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--reduce", action="store_true")
    mode.add_argument("--verify", type=Path)
    mode.add_argument("--lift", type=Path, help="JSON list in the reported parameter-coordinate order")
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--write", type=Path)
    parser.add_argument("--equations", type=Path, help="write the complete exact reduced equations")
    parser.add_argument("--audit-repeat", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        if args.verify:
            result = verify(json.loads(args.verify.read_text()))
        else:
            reduction, result = build(args.control)
            if args.equations:
                args.equations.write_text(json.dumps(reduction.export()) + "\n")
            if args.lift:
                signs = reduction.lift_parameters(json.loads(args.lift.read_text()))
                word = word_from_signs(signs, args.control)
                audit = coupled.audit_word(word, args.audit_repeat)
                result = {"word": word, "audit": audit, "all_nonnegative_repetitions": True}
        if args.write:
            args.write.write_text(json.dumps(result, indent=2) + "\n")
        summary = {k: v for k, v in result.items()
                   if k not in ("free_signs", "parameter_signs", "word")}
        if "free_signs" in result:
            summary["free_sign_count"] = len(result["free_signs"])
            summary["parameter_sign_count"] = len(result["parameter_signs"])
        print(json.dumps(summary, sort_keys=True))
        return 0
    except (ValueError, TypeError, OSError, json.JSONDecodeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
