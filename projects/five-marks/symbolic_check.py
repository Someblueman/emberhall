"""Symbolic re-derivation of the Five Marks candidate argument.

Cinder, 17 November 2026. Run: python3 projects/five-marks/symbolic_check.py

An independent re-check of PROOF.md's affine identities in odd b, using
stdlib-only arithmetic on linear forms p*b+q. No third-party code, no
network. The verifier proves the displayed identities hold as linear
forms in b; it does not prove the infinite-family density claim, which
rests on the interval-partition step recorded in SYMBOLIC.md.
"""
import sys

# Linear forms in b, written as (coefficient of b, constant).
Lin = tuple[int, int]


def add(x: Lin, y: Lin) -> Lin:
    return (x[0] + y[0], x[1] + y[1])


def sub(x: Lin, y: Lin) -> Lin:
    return (x[0] - y[0], x[1] - y[1])


def scale(c: int, x: Lin) -> Lin:
    return (c * x[0], c * x[1])


def ev(x: Lin, b: int) -> int:
    return x[0] * b + x[1]


B: Lin = (1, 0)
ZERO: Lin = (0, 0)
TWO: Lin = (0, 2)
FOUR: Lin = (0, 4)

# S_b = {0, b+2, 2b+4, 3b+4, 4b+4}
S = [ZERO, add(B, TWO), (2, 4), (3, 4), (4, 4)]
S_LABELS = ["s_0=0", "s_1=b+2", "s_2=2b+4", "s_3=3b+4", "s_4=4b+4"]

# M as published: {b, b+2, 2b, 2b+2, 2b+4, 3b+2, 3b+4, 4b+4}
M = [(1, 0), (1, 2), (2, 0), (2, 2), (2, 4), (3, 2), (3, 4), (4, 4)]
M_LABELS = ["b", "b+2", "2b", "2b+2", "2b+4", "3b+2", "3b+4", "4b+4"]

N: Lin = (5, 4)  # 5b+4


def check_distances() -> None:
    """All positive pair differences of S coincide with M as linear forms."""
    got = sorted({sub(S[j], S[i]) for i in range(5) for j in range(i + 1, 5)})
    want = sorted(set(M))
    assert got == want, (got, want)
    # Instances agree as sets for odd b.
    for b in range(1, 202, 2):
        assert {ev(d, b) for d in got} == {ev(d, b) for d in M}, b


def check_lower_bound() -> None:
    """Modular boundary argument for R={0,2,...,2b-2} mod n."""
    # |R differences| <= 2b-2 < n = 5b+4 for every b>=1.
    assert sub(N, (2, -2)) == (3, 6) and ev((3, 6), 1) > 0
    # Even forbidden distances, as linear forms: 2b, 2b+2, 2b+4, 4b+4.
    evens = [(2, 0), (2, 2), (2, 4), (4, 4)]
    # Each exceeds the largest even difference 2b-2 (coefficient gap 0..2).
    for e in evens:
        assert sub(e, (2, -2)) in {(0, 2), (0, 4), (0, 6), (2, 6)}, e
        # mod n, the other representative m-n is odd (n is odd for odd b),
        # so it can never equal an even difference of R elements.
        assert ev(N, 1) % 2 == 1  # n=9,19,... odd
    # Odd forbidden distances: n-m values are 4b+4, 4b+2, 2b+2, 2b.
    odds = [(1, 0), (1, 2), (3, 2), (3, 4)]
    assert sorted(sub(N, o) for o in odds) == sorted([(4, 4), (4, 2), (2, 2), (2, 0)])
    for v in [(4, 4), (4, 2), (2, 2), (2, 0)]:
        # each >= 2b > 2b-2, so it cannot be a difference of two R residues
        assert sub(v, (2, -2)) in {(2, 6), (2, 4), (0, 4), (0, 2)}, v
    # R has exactly b residues: 0,2,...,2b-2.
    for b in range(1, 202, 2):
        assert len(set(range(0, 2 * b, 2))) == b
        assert max(range(0, 2 * b, 2)) == 2 * b - 2 < 5 * b + 4


def check_partition() -> None:
    """Columns c+S for c=0,...,b-1 partition window except 4 extras."""
    intervals = [(0, "b-1"), (2, "2b+1"), (4, "3b+3"), (4, "4b+3"), (4, "5b+3")]
    # Row intervals as evaluated: [s_i, s_i+b-1].
    assert S[0] == ZERO and (S[0][0], S[0][1]) == (0, 0)
    lows = [ZERO, (1, 2), (2, 4), (3, 4), (4, 4)]
    assert lows == S
    highs = [add(s, (1, -1)) for s in S]
    assert highs == [(1, -1), (2, 1), (3, 3), (4, 3), (5, 3)], highs
    # Complement of the five strips in [0,5b+3] has exactly 4 points.
    for b in range(1, 202, 2):
        covered = set()
        for i, s in enumerate([ev(x, b) for x in S]):
            for c in range(b):
                covered.add(c + s)
        assert len(covered) == 5 * b, b
        complement = set(range(5 * b + 4)) - covered
        assert complement == {b, b + 1, 2 * b + 2, 2 * b + 3}, (b, complement)
    # Every difference inside one column lies in M (by construction).
    for i in range(5):
        for j in range(i + 1, 5):
            assert sub(S[j], S[i]) in M


def check_exclusion_tables() -> None:
    """Both six-entry tables of the odd-column obstruction."""
    # Extra positions t_low = b+1, t_high = 2b+3, with t_high - t_low = b+2 in M.
    t_low = (1, 1)
    t_high = (2, 3)
    assert sub(t_high, t_low) == (1, 2) in M
    # Table 1: distances from t to C_1 rows 0,3,4 (C_1 has c=1).
    one = (0, 1)

    def dist(x: Lin, y: Lin) -> Lin:
        d = sub(x, y)
        return (-d[0], -d[1]) if d[0] < 0 or (d[0] == 0 and d[1] < 0) else d

    def row_dist(t: Lin, i: int) -> Lin:
        return dist(add(one, S[i]), t)

    table1 = {
        t_low: [row_dist(t_low, 0), row_dist(t_low, 3), row_dist(t_low, 4)],
        t_high: [row_dist(t_high, 0), row_dist(t_high, 3), row_dist(t_high, 4)],
    }
    expected1 = {
        t_low: [(1, 0), (2, 4), (3, 4)],
        t_high: [(2, 2), (1, 2), (2, 2)],
    }
    for t, row in expected1.items():
        got = table1[t] if t == t_low else table1[t_high]
        assert got == row, (t, got, row)
        assert all(x in M for x in row), (t, row)
    # Table 2: from odd column c (rows 1,2) to next odd column c+2 (rows 0,3,4).
    trans = {
        (1, 0): (1, 0), (1, 3): (2, 4), (1, 4): (3, 4),
        (2, 0): (2, 2), (2, 3): (1, 2), (2, 4): (2, 2),
    }
    for (i, j), want in trans.items():
        # distance from c+s_i to (c+2)+s_j, c cancels
        got = add(sub(S[j], S[i]), (0, 2))
        if got[0] < 0 or (got[0] == 0 and got[1] < 0):
            got = (-got[0], -got[1])
        assert got == want, (i, j, got, want)
        assert want in M, (i, j, want)
    # Rows 1,2 are the only candidates surviving t at C_1: each of 0,3,4 is
    # excluded above, so the survivor set is a subset of {1,2}. (For t_high,
    # row 1 is also excluded; the proof's closed set {1,2} still holds.)
    survivors = {}
    for t, name in ((t_low, "t_low"), (t_high, "t_high")):
        surv = [i for i in range(5) if row_dist(t, i) not in M]
        survivors[name] = surv
        assert set(surv) <= {1, 2}, (name, surv)
    assert survivors == {"t_low": [1, 2], "t_high": [2]}, survivors


def check_endpoint() -> None:
    """At final odd column c=b-2 (b>=3): positions 2b and 3b+2, both in M."""
    # c + s1 = (b-2)+(b+2) = 2b ; c+s2 = (b-2)+(2b+4) = 3b+2
    assert add((1, -2), (1, 2)) == (2, 0) in M
    assert add((1, -2), (2, 4)) == (3, 2) in M
    for b in (3, 5, 7, 11, 101):
        assert (b - 2) + (b + 2) == 2 * b
        assert (b - 2) + (2 * b + 4) == 3 * b + 2


def check_b1() -> None:
    """b=1 is separate: M={1,...,8}, so window [0,8] holds at most one start."""
    b = 1
    s = [ev(x, b) for x in S]
    assert s == [0, 3, 6, 7, 8], s
    m = {abs(s[j] - s[i]) for i in range(5) for j in range(i + 1, 5)}
    assert m == {1, 2, 3, 4, 5, 6, 7, 8}, m


def check_coloring_instances() -> None:
    """Finite-instance mirror of PROOF 'Equivalent graph answer' table."""
    for b in range(1, 202, 2):
        n = 5 * b + 4
        u = (n + 1) // 2
        assert u == (5 * (b + 1)) // 2
        even_r = sorted({(u * d) % n for d in (2 * b, 2 * b + 2, 2 * b + 4, 4 * b + 4)})
        odd_r = sorted({(u * d) % n for d in (b, b + 2, 3 * b + 2, 3 * b + 4)})
        assert even_r == [b, b + 1, b + 2, 2 * b + 2], (b, even_r)
        assert odd_r == [3 * b + 2, 3 * b + 3, 4 * b + 3, 4 * b + 4], (b, odd_r)
        assert all(b <= r <= n - b for r in even_r + odd_r), b


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Run without -O: this derivation check requires assertions")
    check_distances()
    check_lower_bound()
    check_partition()
    check_exclusion_tables()
    check_endpoint()
    check_b1()
    check_coloring_instances()
    print("Symbolic re-derivation: all affine identities in PROOF.md hold as linear forms in b")
    print("Finite instances (odd b=1..201) confirm distance sets, partitions and coloring table")
    print("Finite confirmation only; the infinite density step is in SYMBOLIC.md")
