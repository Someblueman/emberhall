"""Long-period hunt for a legal periodic packing that beats b/(5b+4).

Run: python3 projects/five-marks/longperiod.py

Re-uses the exact maximum-independent-set solver from counterexample.py.
For odd b with n=5b+4, computes exact periodic maxima for L=3n and L=4n
(running a separate search per period), restricted to the circulated graph
where conflicts are circular differences in M or -M modulo L. Any density
above b/n would be a legal periodic counterexample to tightness and is
reported with its residues. The published lower construction is checked
for legality at these periods as well.

Finite computation supports the argument only; no third-party code.
"""
from itertools import combinations

from counterexample import differences, max_independent_set, shape


def circulated_adjacency(period: int, forbidden: set[int]) -> list[int]:
    vertices = list(range(period))
    pos = {v: i for i, v in enumerate(vertices)}
    adj = [0] * period
    for x in vertices:
        mask = 0
        for d in forbidden:
            for y in ((x + d) % period, (x - d) % period):
                j = pos[y]
                if j != pos[x]:
                    mask |= 1 << j
        adj[pos[x]] = mask
    return adj


def periodic_maximum_at(period: int, forbidden: set[int]) -> tuple[int, tuple[int, ...]]:
    """Exact maximum periodic-set size modulo period.

    If some forbidden distance is a multiple of period, every start
    conflicts with its own period-translate, so only the empty set is
    legal. Return that empty maximum explicitly rather than searching
    a conflict graph that drops the self-loop.
    """
    if any(d % period == 0 for d in forbidden):
        return 0, ()
    adj = circulated_adjacency(period, forbidden)
    chosen = max_independent_set(adj, period)
    residues = tuple(sorted(chosen))
    residue_set = set(residues)
    for x in residues:
        for d in forbidden:
            assert (x + d) % period not in residue_set
    return len(residues), residues


def lower_construction_legal(b: int, period: int) -> bool:
    """Check R + nZ residues remain legal modulo any multiple L of n."""
    n = 5 * b + 4
    if period % n != 0:
        raise ValueError(f'period {period} is not a multiple of n={n}')
    residues = tuple(range(0, 2 * b, 2))
    m = differences(shape(b))
    residue_set = set(residues)
    # lifts: residue r appears as r, r+n, ... in [0, L)
    lifts: set[int] = set()
    k = 0
    while k * n < period:
        for r in residues:
            if r + k * n < period:
                lifts.add(r + k * n)
        k += 1
    for x in lifts:
        for y in lifts:
            if x != y and (y - x) % period in {d % period for d in m}:
                return False
    assert residue_set <= lifts
    return True


def run_range() -> None:
    for parameter in (1, 3, 5, 7, 9, 11):
        m = differences(shape(parameter))
        n = 5 * parameter + 4
        for multiple in (3, 4):
            period = multiple * n
            size, residues = periodic_maximum_at(period, m)
            flag = 'BEATS BOUND' if size * n > parameter * period else 'at/below bound'
            print(f'long b={parameter} L={period} ({multiple}n): '
                  f'{size}/{period} = {size / period:.6f} vs {parameter / n:.6f} ({flag})')
            assert size * n <= parameter * period, (parameter, period, size, residues)
            assert lower_construction_legal(parameter, period)
    print('Long-period search: no density beats b/(5b+4) for 3n, 4n through b=11')
    print('Lower construction remains legal at all searched periods.')
    print('Finite search passed; read PROOF.md for the all-parameter argument.')


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O: this research check requires assertions')
    run_range()
