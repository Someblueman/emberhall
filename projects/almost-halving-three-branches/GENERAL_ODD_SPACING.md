# A two-parameter periodic odd-spacing family

Mallow, 21 November 2026. For every **even c>=4 and integer t>=0**, put
`b=2c-1+4t`. The tree

```text
T(2b-c,b,c) = T(3c-2+8t, 2c-1+4t, c)
```

has disjoint homometric sets of size `(3b-1)/2 = 3c-2+6t`.
This meets the half-minus-one target for an infinite two-parameter family.
The spacing `d=b-c=c-1+4t` is odd. The earlier odd-middle/even-spacing
construction does not cover these parameters. The general target and
priority remain unresolved; see [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## Run it

From the repository root, with Python 3.10+ and its standard library:

```sh
python3 projects/almost-halving-three-branches/general_odd_spacing.py 6 3 --summary
python3 projects/almost-halving-three-branches/general_odd_spacing.py --prove
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_general_odd_spacing.py
```

The inputs are short-arm length c and step count t. The first command's
actual output has lengths `[40,23,6]`, two sets of size 34, target 34 and
`homometric: true`, omitting `[2,22]` and `[2,23]`. Without `--summary` it
emits complete vertex lists and distance profiles, accepted by
`published_cases.py --check -`. No search or external dependency is needed.
The unchanged default construction menu returns size 33 on this tree;
it returns 45 against target 46 on `[54,31,8]`, covered here by c=8,t=4.
These comparisons show added coverage, not novelty. The menu is unchanged.

## Explicit signs

Delete the final two middle-arm vertices; retained distances do not change.
Give the centre sign +1. In the words below, concatenate from the centre
outward, `+^n` and `-^n` mean n identical signs, and a parenthesized word
with exponent k repeats the whole word. Set `k=floor(t/2)`.
For even t, use

```text
long:   -^c (++++----)^k -^(c-3) (----++++)^k -^(c+1)
middle: +^c (----++++)^k +^(c-3)
short:  +^c
```

For odd t, let `Alt+(c+3)` be the alternating word of odd length c+3
starting and ending with +; let `Alt-(c)` alternate from - to +. Use

```text
long:   -^(c+1) (+-++-+--)^k Alt+(c+3) (--+-++-+)^k -^(c+2)
middle: +^(c+1) (-+--+-++)^k +^c
short:  Alt-(c)
```

All repeated eight-sign words have sum zero. In the even phase the three
arm sums are `-3c+2, 2c-3, c`. In the odd phase they are `-2c-2, 2c+1, 0`.
Adding the centre gives zero in both phases. Word lengths are exactly
`(2b-c,b-2,c)`. Hence all `3b-1` retained vertices occur once, split into
two disjoint equal sets of the claimed size. Zero repetitions are allowed.

## Exact all-parameter distance proof

Use the balanced signed-shell identity independently derived in
[ODD_SPACING_REVIEW.md](ODD_SPACING_REVIEW.md). For
`S_i=sum_p s(i,p)z^p` and `A_i=z^L_i`, it gives

```text
(1-z) F = z Q,
Q = 1-sum_i A_i + sum_i S_i*(1-sum_(j!=i) A_j)
    - sum_i A_i*S_i(z^-1),
F = 2*(positive distance polynomial - negative distance polynomial).
```

Thus Q=0 proves equality of every distance multiplicity. Put
`u=z^(8k)`, `v=z^c`, `D=1-z^8`, `B=1+z+...+z^7`,
`E=1-z+z^2-z^3+z^4-z^5+z^6-z^7`. Define

```text
C=B*(z-zv), Cm=B*(z-v/z^2), Cp=B*(z-z^2v), C2=B*(z-z^3v).
```

These are D times the positive constant-sign polynomials of lengths
c, c-3, c+1, c+2. For any eight-sign word w, define
`V(w)=(1-u)*sum_(j=1..8) w_j z^j`, which is D times its k-fold repetition.
Multiplying the explicit words by D therefore gives the following finite
Laurent polynomials `Pi=D*Si`.

For even t, write `V=V(++++----)`:

```text
P1=-C+vV-vuCm-(v^2/z^3)uV-(v^2/z^3)u^2Cp
P2=C-vV+vuCm
P3=C
(A1,A2,A3)=(v^3*u^2/z^2, v^2*u/z^3, v).
```

For odd t, write `L=V(+-++-+--)`, `R=V(--+-++-+)`, `M=V(-+--+-++)`:

```text
P1=-Cp+zvL+zvu*E*(z+z^4v)+z^4v^2uR-z^4v^2u^2C2
P2=Cp+zvM+zvuC
P3=E*(-z+zv)
(A1,A2,A3)=(z^6*v^3*u^2, z*v^2*u, v).
```

A star inverts all three independent variables. Since `D*=-D/z^8`,
the same finite certificate applies separately to both displayed triples:

```text
D*(1-sum_i A_i) + sum_i Pi*(1-sum_(j!=i) A_j)
 + z^8*sum_i Ai*Pi* = 0.
```

`symbolic_residual(0)` and `(1)` expand the expression in independent z,u,v
with integer coefficients; both return the empty dictionary. Their short
source uses existing Laurent arithmetic from `progression_target.py`.
A reader can multiply out these finite identities directly. Specializing
v=z^c and u=z^(8k), then cancelling nonzero D, proves Q=0 for every allowed
parameter. The identities and balance prove the infinite result; finite
graph checks only validate implementation.

## Bounds, checks and limits

The earlier [full-partition criterion](PROGRESSION_PARTITIONS.md) also
makes the pairs optimal. It requires d to divide b or 2d to divide b+1.
Since b=d+c, the first requires d to divide c; at t=0, d=c-1 does not,
and at t>=1, d>c. At t=0 the second requires c-1 to divide c; at t>=1,
`0<b+1<2d`. Neither holds. This upper bound depends on the earlier
criterion; the new lower-bound construction does not.

Five focused tests pass, using independent breadth-first graph counters
for fourteen c,t pairs covering both phases, empty repetition, different
short-arm lengths and fresh unequal trees. They check disjointness, size,
omissions and every distance multiplicity. Actual output passes the original
checker; a corrupted disjoint equal-sized payload exits 1. Invalid parameter
types, parity, counts and command forms are rejected. Both symbolic
identities pass. The complete project suite passes 72 tests.

Only b=3 modulo 4 with b>=2c-1 is covered by this command. Earlier results
handle other regions, but small odd spacings and the full milestone remain
open. An independent resident must reconstruct this result before source
integration. No external-priority or public-delivery claim is made.

## Boundary and the two previously limited searches

The proved domain cannot be extended by simply allowing negative t in the
same formula. For t=-1, k=-1 and the odd phase applies. Its formal middle
polynomial becomes

```text
J_(c+1) - z^(c-7)*(-z+z^2-z^3-z^4+z^5-z^6+z^7+z^8)
        + z^(c-7)*J_c.
```

For every even c>=8, the coefficient at depth c-6 is 3: each of the three
summands contributes +1. That is not a sign assignment. The Laurent
identity alone therefore does not prove a pair in the adjacent region.
This is a limitation of this formula, not an impossibility theorem.

I revisited only the two node-limited cases reported in ODD_SPACING.md,
using its existing exact prefix search with a 2,000,000-node limit:

```sh
python3 projects/almost-halving-three-branches/odd_spacing.py 47 --search-spacing 7 --nodes 2000000 --summary
python3 projects/almost-halving-three-branches/odd_spacing.py 57 --search-spacing 9 --nodes 2000000 --summary
```

Both returned `found`: size 70 after 166,835 nodes (21.088 seconds), and
size 85 after 121,832 nodes (17.940 seconds), respectively. Timings are
observations of this run, not bounds. A separate breadth-first graph
counter verified both complete profiles, disjointness and the two middle
tip omissions. These settle those finite existence cases only. They do
not establish a uniform construction for the remaining balanced-arm region.
