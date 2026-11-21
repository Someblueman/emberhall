# Exactly when evenly spaced arms admit a full partition

Rook, 21 November 2026. Let `1<=d<b` be integers. There is a partition of
**all** vertices of `T(b+d,b,b-d)` into two equal homometric sets if and only if

`b is odd, and either d divides b or 2d divides b+1`.       (1)

This classifies full partitions, not all maximum homometric pairs. When
b is odd and neither divisibility holds, it proves only the upper bound
`h(T)<=(3b-1)/2`, exactly the project's half-minus-one target. It does
**not** refute that target. Literature priority remains provisional under
the unresolved checks in [PUBLISHED_CASES.md](PUBLISHED_CASES.md).

## Run it

From the [Emberhall repository](https://github.com/Someblueman/emberhall),
Python 3.10+ and its standard library suffice:

```sh
python3 projects/almost-halving-three-branches/progression_partitions.py 21 6
```

This records lengths `(27,21,15)`, target and upper bound 31, and a residue
parity certificate: residues 1 and 4 must have equal sign sums but contain
12 and 9 vertices respectively. It says `target_ruled_out: false`.

For a positive example, `.../progression_partitions.py 9 3 --witness`
prints a full partition of `(12,9,6)` into two sets of size 14, with both
complete distance profiles. `--prove` checks the exact algebraic identities
used below. The graph tests count distances independently and enumerate
every balanced partition of the trees with middle arm at most five.
An additional recorded audit tested b=7 with every d=1..6 and agreed in
all six cases. For each negative case d=3,5,6 it checked all 352,716
partitions with the centre fixed on one side; the complementary labelling
adds no distinct pair. The audit took 10.246 seconds. This is a bounded
implementation check, not the proof of the infinite classification.

## Necessity: a root-of-unity obstruction

If b is even, the order `3b+1` is odd, so a full equal partition is impossible.
Hence suppose b is odd and a full partition exists. Assign signs +1 and -1
to its two parts, including centre sign s0. Let `S_i(z)` be each arm's
signed depth polynomial and `F=s0+S_1+S_2+S_3`. Balance gives `F(1)=0`.
The full-shell identity in [NEXT_FAMILY.md](NEXT_FAMILY.md) gives

```
Q = s0*(1-A_1-A_2-A_3)
    + sum_i S_i*(1-sum_(j!=i) A_j) - sum_i A_i*S_i(z^-1) = 0,
A_i = z^(length_i).
```

Take any d-th root of unity z. All three A_i equal `y=z^b`. Write
`S=S_1+S_2+S_3`, and use a star for evaluation at z^-1. Then

```
Q = (1-3y)*s0 + (1-2y)*S - y*S* = 0,
y*Q* = (y-3)*s0 - S + (y-2)*S* = 0.
```

Multiply the first equation by y-2 and the second by y, then add. Direct
expansion gives `-2*(y-1)^2*(s0+S)=0`. Thus F vanishes at every d-th root
where y is not 1. This elimination is checked coefficient by coefficient
by `root_elimination_residuals`; no floating-point root evaluation is used.

Put `g=gcd(b,d)`. The common roots of `z^b=1` and `z^d=1` are precisely
the g-th roots. Reduce F modulo `z^d-1` to R, of degree less than d.
All roots of `(z^d-1)/(z^g-1)` are distinct and annihilate R, so

`R=(1+z^g+...+z^(d-g))*P`, with `degree(P)<g`.

Consequently the coefficients of R are constant within each residue
class modulo g. Each coefficient is a sum of signs on vertices at that
depth residue modulo d; its parity is the number of those vertices.

If d divides b, this gives no obstruction; that branch is constructed below.
Otherwise write `b=qd+r`, `0<r<d`. Let N_j count original vertices whose
depth is j modulo d, including the centre in N_0. Direct counting on the
three arms gives

```
N_0 = 3q+1,
N_j = 3q+3 for 1<=j<=r,
N_j = 3q   for r<j<d.
```

If g>1, r is a positive multiple of g and r<=d-g. Residues 1 and d-g+1
are congruent modulo g, but their counts are 3q+3 and 3q, of opposite
parity. Their sign sums cannot be equal, a contradiction.

If g=1, every coefficient of R is equal. Their sum is `R(1)=F(1)=0`, so
every coefficient is zero and every N_j must be even. If r<d-1, N_0 and
N_(r+1) differ by one, impossible. Thus r=d-1. Now N_0=3q+1 is even only
if q is odd, which says `b+1=(q+1)d` is divisible by 2d. This proves the
necessity in (1) over every full partition, without restricting its shape.

## Sufficiency when 2d divides b+1

Use the already reconstructed block construction on `(b+d,b,b-d)`. Its
block width is d and its quotient is `(b+d+1)/d=(b+1)/d+1`, an odd integer;
the remainder is zero. Therefore the valid published formula uses every
vertex and gives two sets of size `(3b+1)/2`. No even-quotient endpoint is
repaired or extended here.

## Sufficiency when d divides b

Write `b=qd`. Both q and d are odd; `q>=3`. Give the centre sign +1.
On arm 1, of length `(q+1)d`, give depth p sign `(-1)^p`.
On arm 2, divide the path into q consecutive blocks of length d. Within
each block give positions 1..d the signs `-,+,-,+,...,-`.
On arm 3, use q-1 blocks with all those signs reversed.

Arm 1 has even length and sign sum zero. Each arm-2 block has sum -1 and
each arm-3 block sum +1. Together with the centre the total is
`0-q+(q-1)+1=0`. Thus both parts have `(3b+1)/2` vertices.

To check all distances, put `r=z^d`, `x=r^(q-1)`. The endpoint monomials
are `A=r^2*x`, `B=r*x`, `C=x`. Finite geometric series give

```
S_1 = -z*(1-r^2*x)/(1+z),
S_2 = -z*(1+r)*(1-r*x)/((1+z)*(1-r)),
S_3 =  z*(1+r)*(1-x)/((1+z)*(1-r)).
```

These expressions are finite polynomials at the stated odd q,d. In
particular a length-d block has polynomial `-z*(1+r)/(1+z)` because d
is odd. Set `D=(1+z)*(1-r)`, `N_i=D*S_i/z`, and `K=1-A-B-C`. Then

```
N_1=-(1-r)*(1-A),  N_2=-(1+r)*(1-B),  N_3=(1+r)*(1-C).
```

Let a star now invert r and x. Since `D*= -D/(zr)`, the constant and
z coefficients of DQ are respectively

```
(1-r)*K + r*(A*N_1* + B*N_2* + C*N_3*),
(1-r)*K + N_1*(1-B-C) + N_2*(1-A-C) + N_3*(1-A-B).
```

Both are identically zero in the independent Laurent variables r,x, by
direct multiplication. `multiple_construction_residuals` checks these
two identities with exact integers. Hence Q=0, proving homometry for
every odd q,d, not just the examples that led to this construction.

## What has and has not been established

The two positive branches supply full partitions and therefore exact
maxima. The negative branch only excludes full partitions. It leaves
the half-minus-one target open unless another construction covers it.
For example it explains the upper bound on every odd-t member of
`T(10t,7t,4t)`; the separate six-table construction supplies the lower bound.

The finite audit and implementation tests support the code. The root
argument and the displayed polynomial identities prove (1) for all
parameters. A non-author's reconstruction is still outstanding, as is
the general project's target for arbitrary three-arm lengths.
