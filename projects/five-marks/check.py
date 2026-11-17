"""Check the candidate proof's arithmetic and small windows; no third party code.

Run: python3 projects/five-marks/check.py
Finite computation is supporting evidence, never an infinite-family proof.
"""
from itertools import combinations


def shape(b: int) -> tuple[int, ...]:
    a = b + 2
    return (0, a, 2 * a, 2 * a + b, 2 * a + 2 * b)


def distances(s: tuple[int, ...]) -> set[int]:
    return {y - x for x, y in combinations(s, 2)}


def legal(points: tuple[int, ...], forbidden: set[int]) -> bool:
    return len(points) == len(set(points)) and all(
        abs(x - y) not in forbidden for x, y in combinations(points, 2)
    )


def check_affine_identities() -> None:
    """Check the exclusion identities as coefficients of b, not sample values."""
    offsets = ((0, 0), (1, 2), (2, 4), (3, 4), (4, 4))
    positive = {(y[0] - x[0], y[1] - x[1])
                for x, y in combinations(offsets, 2)}
    signed = positive | {(-c, -d) for c, d in positive}
    for t in ((1, 1), (2, 3)):
        for j in (0, 3, 4):
            assert (offsets[j][0] - t[0], offsets[j][1] + 1 - t[1]) in signed
    for i in (1, 2):
        for j in (0, 3, 4):
            assert (offsets[j][0] - offsets[i][0],
                    offsets[j][1] + 2 - offsets[i][1]) in signed
        assert (offsets[i][0] + 1, offsets[i][1] - 2) in positive


def check_arithmetic(b: int) -> None:
    s = shape(b)
    m = distances(s)
    n = 5 * b + 4
    assert m == {b, b + 2, 2 * b, 2 * b + 2, 2 * b + 4,
                 3 * b + 2, 3 * b + 4, 4 * b + 4}
    residues = tuple(range(0, 2 * b, 2))
    # All ordered residue pairs and every forbidden distance, including a
    # residue with itself, check both signs and period-boundary conflicts.
    for x in residues:
        for y in residues:
            assert all((x - y - d) % n != 0 for d in m)
    inverse_two = (n + 1) // 2
    assert (2 * inverse_two) % n == 1
    assert all(b <= (inverse_two * d) % n <= n - b for d in m)
    if b == 1:
        assert m == set(range(1, 9))
        return
    columns = [{c + v for v in s} for c in range(b)]
    assert sum(map(len, columns)) == len(set.union(*columns)) == 5 * b
    extras = {b, b + 1, 2 * b + 2, 2 * b + 3}
    assert set(range(n)) - set.union(*columns) == extras
    for t in (b + 1, 2 * b + 3):
        assert all(abs(1 + s[j] - t) in m for j in (0, 3, 4))
    for i in (1, 2):
        assert all(abs(2 + s[j] - s[i]) in m for j in (0, 3, 4))
        assert b - 2 + s[i] in m
    assert (2 * b + 3) - (b + 1) in m


def check_all_windows(b: int) -> tuple[int, int]:
    """Enumerate every legal subset of [0,n-1] containing 0, not just maximal ones.

    This include/exclude search uses only pair distances. It does not prune
    using the claimed bound, column argument, or residue construction.
    """
    s = shape(b)
    m = distances(s)
    n = 5 * b + 4
    points = tuple(x for x in range(1, n) if x not in m)
    conflicts = [sum(1 << j for j, y in enumerate(points)
                     if x == y or abs(x - y) in m) for x in points]
    count, maximum = 0, 0

    def visit(available: int, chosen: tuple[int, ...]) -> None:
        nonlocal count, maximum
        if not available:
            count += 1
            maximum = max(maximum, len(chosen))
            assert legal(chosen, m)
            assert len(chosen) <= b, (b, chosen)
            extras = {b + 1, 2 * b + 3}.intersection(chosen)
            if extras and b > 1:
                assert any(not {c + v for v in s}.intersection(chosen)
                           for c in range(1, b, 2)), (b, chosen)
            return
        bit = available & -available
        index = bit.bit_length() - 1
        visit(available ^ bit, chosen)
        visit(available & ~conflicts[index], chosen + (points[index],))

    visit((1 << len(points)) - 1, (0,))
    assert maximum == b
    return count, maximum


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O: this research check requires assertions')
    check_affine_identities()
    print('Symbolic coefficient check: both exclusion tables and endpoint')
    for parameter in range(1, 102, 2):
        check_arithmetic(parameter)
    print('Arithmetic/period checks: 51 positive odd parameters through 101')
    for parameter in (1, 3, 5, 7):
        total, largest = check_all_windows(parameter)
        print(f'b={parameter}: {total} legal anchored windows; maximum {largest}')
    print('Finite checks passed; read PROOF.md for the all-parameter argument.')
