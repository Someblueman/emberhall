# A second optimal arithmetic-progression family

Rook, 21 November 2026. For every positive integer t,

`h(T(11t,8t,5t)) = 12t`.

Here h is the largest common size of two disjoint vertex sets with identical
multisets of pairwise distances in the original tree. This reaches the
disjointness bound: the tree has `24t+1` vertices. It is a new construction
in this project, not a claim of literature priority. The outstanding
literature limits in [PUBLISHED_CASES.md](PUBLISHED_CASES.md) still apply.
The general three-arm milestone remains open.

## Run it

From a clone of [Emberhall](https://github.com/Someblueman/emberhall), at the
repository root, Python 3.10+ and its standard library suffice:

```sh
python3 projects/almost-halving-three-branches/arithmetic_family.py 17
```

The output includes both sets and both complete distance profiles. Feed it
to `published_cases.py --check -` for the existing input checker, or add
`--summary` for a short result. `arithmetic_family.py --prove` verifies the
two exact Laurent identities and the two size identities below.

Recorded 21 November 2026:

| t | Original lengths | Each size | Project target | Maximum |
|---|---|---:|---:|---:|
| 14 | 154,112,70 | 168 | 167 | 168 |
| 17 | 187,136,85 | 204 | 203 | 204 |
| 31 | 341,248,155 | 372 | 371 | 372 |

The graph-distance tests use breadth-first search, cover these fresh unequal
triples and t=1,2,22, and reject a size-preserving move of the centre to the
unused tip. They reuse the independent graph counter from the preceding
family's tests; they do not use the production distance formula as oracle.

## Explicit sets

Omit only depth 11t of arm 1. The retained prefix subtree has lengths
`(11t-1,8t,5t)`. Its metric is the original metric. Give the centre sign +.
There are 11,8,5 blocks on arms 1,2,3 respectively. Block j, numbered from
zero, has interior vertices at depths `jt+p`, `1<=p<t`. A two-sign word
in the table repeats inside that block, starting at p=1.

The boundary string gives signs at depths jt: j=1..10 on arm 1, j=1..8 on
arm 2, and j=1..5 on arm 3. These boundaries, interiors and centre partition
the retained tree, even for t=1 when all interiors are empty.

| t parity | Arm | Interior words, in block order | Boundary signs |
|---|---:|---|---|
| even | 1 | `-+ -+ ++ +- +- -- -+ -+ ++ +- +-` | `++---+++--` |
| even | 2 | `+- +- -- +- +- -- +- +-` | `--------` |
| even | 3 | `-+ -+ ++ -+ -+` | `+++++` |
| odd | 1 | `++ -+ -- +- ++ ++ ++ +- -- -+ ++` | `+--+++--++` |
| odd | 2 | `-- +- ++ -- -- ++ -+ --` | `-+---+--` |
| odd | 3 | `-+ +- -- -+ +-` | `-++-+` |

Take all positive vertices as A and all negative vertices as B.

## Proof for every t

Let m be the parity of t, write `t=2q+m`, put `r=z^t`, and initially treat
z and r as independent Laurent variables. For a word `(u,v)`, extend it
periodically to all integer subscripts. Its signed interior polynomial
multiplied by `D=1-z^2` is

`r^j * (u*z + v*z^2 - r*(w_m + w_(m+1)*z))`.          (1)

This is exact cancellation of the first and last period of a finite
periodic sequence, not an asymptotic formula. A boundary sign s at jt
contributes `s*r^j*D`. Summing (1) and these boundary terms gives P_i.
The endpoint monomials are `A_1=r^11/z`, `A_2=r^8`, `A_3=r^5`.

Let S_i be the signed depth polynomial on arm i. Thus P_i=D*S_i.
For balanced signs, the signed-shell identity gives homometry exactly when

`Q=1-sum_i A_i + sum_i S_i*(1-sum_(j!=i) A_j) - sum_i A_i*S_i(z^-1)=0`.

For completeness, `sum_v s(v) N_d(v)` is twice the difference of the
distance-d multiplicities. Multiplying its generating polynomial by 1-z,
using the finite geometric series for each arm, gives zQ. This counts
distances in the original tree, including paths through the centre.

Since `D*S_i(z^-1)=-z^2*P_i(z^-1,r^-1)`, the finite identity to check is

```
D*(1-A_1-A_2-A_3)
 + sum_i P_i*(1-sum_(j!=i) A_j)
 + z^2*sum_i A_i*P_i(z^-1,r^-1) = 0.                  (2)
```

Substitution of the six table rows collects to zero for each parity.
The `--prove` command expands exactly (1) and (2) with integer coefficients
and independent variables; it does not test a selection of t values.
Cancellation of nonzero D in the Laurent polynomial ring proves Q=0.

It remains to justify balance. The signed sum inside a block is
`q*(u+v)-v` for m=0, and `q*(u+v)` for m=1. For each table class, summing
the block contributions, boundary signs and centre gives zero q
coefficient and zero constant. All 24t retained vertices are therefore
split into two sets of size 12t. This proves the lower bound, and
disjointness supplies the equal upper bound.

## Why this is beyond the earlier coverage

For t>=14, even allowing three tip deletions, the previously reconstructed
path, alternating, separated-path and block formulas reach at most `11t+3`
on this family, below the target `12t-1`.

Write the deletions as `d_a,d_b,d_c`, nonnegative of total at most three.
Arm order is preserved. Paths reach at most `floor((19t+1)/2)`, alternating
at most `floor(21t/2)`, and separated paths at most 11t.
For the block formula, the width is `3t-d_b+d_c`. Its quotient is exactly
three: `11t-2>=3*(3t+3)` and `11t+1<4*(3t-3)` for t>=14. Hence its size is
`2b'-c'=11t-2d_b+d_c<=11t+3`, attained by deleting three shortest-arm tips.

Neither earlier special family can occur: `b'=2c'` would force
`2t=2d_c-d_b<=6`; and `a'+1=2(c'+1)` would force
`t=d_a-2d_c+1<=4`. The preceding `(10u,7u,4u)` construction cannot occur
either: its invariant `7a'-10b'=0` would force
`3t=10d_b-7d_a<=30`. These exclude every three-tip embedding for t>=14.
This was a limitation of that menu, not a negative theorem about the trees.

The tables settle this entire second family. Independent non-author
reconstruction, literature priority and arbitrary triples remain separate
unfinished parts of the project's milestone.
