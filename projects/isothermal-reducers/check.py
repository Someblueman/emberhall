"""Check one exact five-vertex counterexample; no solver or external packages."""
from __future__ import annotations

import argparse
from fractions import Fraction as F


WEIGHTS = (
    (0, 2, 1, 1, 2),
    (2, 0, 2, 1, 1),
    (1, 2, 0, 2, 1),
    (1, 1, 2, 0, 2),
    (2, 1, 1, 2, 0),
)
DENOMINATOR = 29356625545
# E, S, A, B, C, D, Q, F as defined in proof.md.
NUMERATORS = (0, 1443761, 22268370, 40951670, 369124295, 743986795,
              6922659920, DENOMINATOR)
FITNESS = F(1, 25)


def orbit(state):
    vertices = [i for i in range(5) if state & (1 << i)]
    k = len(vertices)
    if k in (0, 1, 4, 5):
        return {0: 0, 1: 1, 4: 6, 5: 7}[k]
    if k == 3:
        vertices = [i for i in range(5) if i not in vertices]
    adjacent = (vertices[0] - vertices[1]) % 5 in (1, 4)
    return (2 if adjacent else 3) if k == 2 else (4 if adjacent else 5)


def check_harmonic(weights, values, fitness):
    """Verify every labelled state through elementary death/parent events."""
    n = len(weights)
    if n != 5 or len(values) != 32 or any(len(row) != 5 for row in weights):
        raise ValueError("expected five vertices and all 32 state values")
    if fitness <= 0:
        raise ValueError("fitness must be positive")
    for i, row in enumerate(weights):
        if sum(row) != 1 or row[i] != 0:
            raise ValueError("row sum or diagonal is wrong")
        if any(w < 0 or w != weights[j][i] for j, w in enumerate(row)):
            raise ValueError("negative or asymmetric weight")
    reached, pending = {0}, [0]
    while pending:
        i = pending.pop()
        for j, w in enumerate(weights[i]):
            if w and j not in reached:
                reached.add(j)
                pending.append(j)
    if len(reached) != 5:
        raise ValueError("disconnected graph")
    if values[0] != 0 or values[31] != 1 or any(v < 0 or v > 1 for v in values):
        raise ValueError("invalid boundary or probability")
    for state in range(1, 31):
        expectation, mass = F(0), F(0)
        for dead in range(5):
            # The diagonal is zero: the dead individual never competes.
            rates = [weights[dead][parent] * (fitness if state & (1 << parent) else 1)
                     for parent in range(5)]
            denominator = sum(rates)
            if denominator <= 0:
                raise ValueError("nonpositive parent normalization")
            for parent, rate in enumerate(rates):
                target = state & ~(1 << dead)
                if state & (1 << parent):
                    target |= 1 << dead
                chance = rate / (5 * denominator)
                mass += chance
                expectation += chance * values[target]
        if mass != 1 or expectation != values[state]:
            raise ValueError(f"harmonic equation failed at state {state}: "
                             f"residual {values[state] - expectation}")
    return sum(values[1 << i] for i in range(5)) / 5


def complete_values(fitness):
    # Count-chain downward/upward ratios telescope; see proof.md.
    increments = [F(1)]
    for k in range(1, 5):
        ratio = (4 + (fitness - 1) * k) / (fitness * (4 + (fitness - 1) * (k - 1)))
        increments.append(increments[-1] * ratio)
    total = sum(increments)
    profile = [sum(increments[:k]) / total for k in range(6)]
    return [profile[state.bit_count()] for state in range(32)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mutate-certificate", action="store_true",
                        help="deliberately damage one value; must exit with failure")
    parser.add_argument("--mutate-model", action="store_true",
                        help="check the same values at the wrong fitness; must fail")
    args = parser.parse_args()
    values = [F(NUMERATORS[orbit(state)], DENOMINATOR) for state in range(32)]
    if args.mutate_certificate:
        values[1] += F(1, DENOMINATOR)
    fitness = F(1, 24) if args.mutate_model else FITNESS
    weights = [[F(x, 6) for x in row] for row in WEIGHTS]
    try:
        rho = check_harmonic(weights, values, fitness)
        complete = [[F(i != j, 4) for j in range(5)] for i in range(5)]
        baseline = check_harmonic(complete, complete_values(FITNESS), FITNESS)
        if rho != F(1443761, 29356625545) or baseline != F(1, 20345):
            raise ValueError("unexpected exact fixation probability")
        gap = rho - baseline
        if gap != F(51360, 1837724759117) or gap <= 0:
            raise ValueError("strict counterexample inequality failed")
    except ValueError as exc:
        parser.exit(1, f"FAIL: {exc}\n")
    print("PASS connected symmetric loop-free graph; every row sums to one")
    print("PASS all 30 transient equations and both absorbing boundaries")
    print("PASS all 30 complete-graph equations and both absorbing boundaries")
    print(f"fitness = {FITNESS}")
    print(f"counterexample fixation = {rho}")
    print(f"complete-graph fixation = {baseline}")
    print(f"strict positive difference = {gap}")
    print("PASS exact counterexample; independent review and priority remain separate")


if __name__ == "__main__":
    main()
