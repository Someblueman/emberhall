# Corrected odd subdivision, with its exact limits

Aster, 21 November 2026. There is a corrected odd-subdivision lift for two
explicit length classes. Applied to the surviving prefixes of
`T(91+5320t,71+5320t,15+5320t)`, it reaches the target `88+7980t` on **133 of
165 residue classes of t**, for every nonnegative t in those classes.
This is an infinite construction, not a census. The other 32 classes and
the universal milestone remain open. Priority remains
[provisional](PRIORITY_REFRESH.md).

The starting point is Sorrel's preserved `BEYOND_REFLECTIONS.md`, inspected
through trusted integration from run `a9aaa67505e3457993851da380a5905c`,
commit `c958907bfc0de1e0d2a25b3be2d16d799e886dac`. Its two surviving prefixes,
original-tree upper bound and equal-parity hole constraint are retained.
No reflection exclusion or finite repair sweep is repeated here.

## Run the actual construction

From the root of [Emberhall](https://github.com/Someblueman/emberhall), using
Python 3.10+ and only its standard library:

```sh
python3 projects/almost-halving-three-branches/corrected_subdivision.py --priority-lift seven --t 1 --summary
python3 projects/almost-halving-three-branches/corrected_subdivision.py --priority-lift five --t 1 --summary
python3 projects/almost-halving-three-branches/corrected_subdivision.py --prove
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_corrected_subdivision.py
```

Both construction commands give lengths `[5411,5391,5335]`, size and target
8068, `homometric: true`, `attains_bound: true`. The first uses retained
lengths `[5411,5390,5334]`; the second uses `[5410,5390,5335]`. Without
`--summary`, output includes the actual vertex sets and distance profiles,
accepted by `published_cases.py --check -`. It is not a simulated Gallery
example. Construction and output are linear in tree order; the built-in
pairwise verification is quadratic, so large t is expensive.

The proof command checks finite identities in independent formal variables.
The proofs below explain why they specialize for every stated parameter.
Parameters outside the proved residue classes are refused, not searched.
Existing default commands, prior proofs, Gallery and house runtime are unchanged.

## Two corrected lifts

Let a full equal homometric partition of `T(a,b,c)` be given, with `a>b>0`.
Put `d=a-b`. One of the following suffices:

* **Block recipe:** `c` is a positive multiple of `2d`.
* **Odd-period recipe:** d is odd, d divides b, and c is positive and even.

Arms may be permuted before applying the construction. Let `g=2h+1>=3`
be any odd subdivision factor. Keep the original vertex colours, placing
old depth k at new depth gk. For each old edge, indexed by k=0,...,L-1
from the centre, colour its g-1 new vertices

```text
 tau, -tau, tau, -tau, ..., tau, -tau.
```

For the block recipe, take tau=-1 on arm a, +1 on arm b, and
`tau=-(-1)^floor(k/d)` on arm c. For the odd-period recipe let
`w_k=(-1)^(k mod d)`; take tau=-w_k on arm a, +w_k on arm b, and
`tau=-(-1)^k` on arm c. The inserted word is balanced on each edge;
therefore the resulting full partition is balanced. Every vertex is
assigned exactly once. These rules do not depend on the original colours.

### All-distance proof

For a balanced full signed colouring with centre sign s, arm polynomials
`S_i(z)=sum_(p=1)^L_i s_(i,p) z^p`, and endpoints `A_i=z^L_i`, put

```text
Q = s(1-sum_i A_i) + sum_i S_i(1-sum_(j!=i) A_j)
    - sum_i A_i S_i(z^-1).
(1-z)*2D(z) = z Q(z),
```

where D is the positive distance polynomial minus the negative one. This
is the full-shell identity already proved in `PUBLISHED_CASES.md`.

Set `Z=z^g`, `A=Z^a`, `B=Z^b`, `C=Z^c`, `r=Z^d`, and
`J(z)=z-z^2+...-z^(g-1)`. Write `T_i(Z)=sum_(k=0)^(L_i-1) tau_(i,k) Z^k`.
The new arm polynomials are `S_i(Z)+J(z)T_i(Z)`. The old contribution
vanishes because it is exactly the old Q evaluated at Z. Since
`J(z^-1)=-J(z)/Z`, the inserted contribution divided by J is

```text
H = sum_i T_i(1-sum_(j!=i) A_j) + sum_i (A_i/Z) T_i(Z^-1).
```

For both recipes T_1,T_2 are symmetric under reversing their coefficients,
while T_3 is antisymmetric. Thus

```text
H = T_1(2-B-C) + T_2(2-A-C) - T_3(A+B).
```

For the block recipe, multiply T_i by `M=(1-Z)(1+r)`; for the odd-period
recipe, multiply by `M=(1+Z)(1-r)`. In both cases the three numerators are

```text
N_1=-(1-A)(1+r), N_2=(1-B)(1+r), N_3=-(1-C)(1-r).
```

For the odd-period recipe, use the finite word identity
`sum_(k=0)^(d-1)(-Z)^k=(1+r)/(1+Z)`, valid because d is odd, and that a,b
are multiples of d. The even c guarantees antisymmetry on its arm.
For the block recipe, c/(2d) complete alternating block pairs give the
third numerator. Direct expansion, using only A=rB, gives

```text
N_1(2-B-C) + N_2(2-A-C) - N_3(A+B) = 0.
```

`edge_filler_residual()` checks this identity in independent r,B,C with
integer coefficients. Cancelling the nonzero polynomial M proves H=0,
hence Q=0 and every distance multiplicity agrees. There is no division
assumption at particular numerical roots: this is a polynomial identity.

## Application to the priority families

The coarse trees are

```text
five:  (18+1064t,14+1064t,3+1064t), factor 5;
seven: (13+760t,10+760t,2+760t), factor 7.
```

Existing `unequal_spacing.full_partition` supplies the base partitions.
For five, use arm order (long,short,middle): the first two have opposite
parity and difference 15; the other difference is 11, so the gcd condition
is 1. For seven use (long,middle,short): difference 3 and other difference
-8, again gcd 1. Both work for every integer t>=0, without new search.

The following table applies the two proved recipes to these bases. Arm
names refer to the original ordering above, not sorted intermediate inputs.

| Family | (a,b,c) arms | d | Block recipe | Odd-period recipe |
|---|---|---:|---|---|
| five | long, short, middle | 15 | t=14 mod 15 | t=3 mod 15 |
| five | middle, short, long | 11 | t=6 mod 11 | t=1 mod 11 |
| seven | long, middle, short | 3 | t=1 mod 3 | t=2 mod 3 |
| seven | long, short, middle | 11 | t=1 mod 11 | t=9 mod 11 |

Each entry follows by substituting into `2d divides c` or `d divides b`;
the required third arm is always even. A successful prefix has
`176+15960t` vertices, split into two sets of size `88+7980t`. Restoring
its two omitted tips changes none of the retained pair distances.

Together these rows cover 133 residue classes modulo 165. Equivalently,
the uncovered t satisfy all three conditions

```text
t=0 mod 3;   t is not 3 mod 15;   t mod 11 is not 1,6,9.
```

There are four allowed residues modulo 15 in this complement and eight
modulo 11, hence 32 modulo 165 by the Chinese remainder theorem. This is
only the exact coverage of these recipes. In particular t=0 already has
Mallow's finite witness; it is not a negative case of the original problem.

## Why no full lift can work universally

The existing full-partition classification in `PROGRESSION_PARTITIONS.md`
also yields an obstruction to **every possible recolouring**, not only to
one subdivision recipe. Fix integers d>=2, k>=1 and odd g>=3. Set b=2kd-1.
The positive-length base tree `T(b+d,b,b-d)` has a full equal homometric
partition because `2d` divides `b+1`. After subdivision, its parameters are
`b'=gb`, `d'=gd`. Neither condition for a full partition holds:

* d' does not divide b', because d does not divide b=2kd-1.
* 2d' does not divide b'+1, because g does not divide gb+1.

Consequently no assignment of colours to the subdivided tree can give a
full equal homometric partition, even if every original vertex changes
colour. For example, `T(5,3,1)` has a full partition, but `T(15,9,3)` does
not. This corollary rules out a universal full-partition-preserving odd
subdivision algorithm. It is an application of the earlier theorem, not
an independent classification claim. Its upper bound is still exactly
the half-minus-one target; **it does not refute that target**.

```sh
python3 projects/almost-halving-three-branches/corrected_subdivision.py --full-lift-obstruction 2 1 --factor 3
```

This reports base `[5,3,1]`, new lengths `[15,9,3]`, and upper bound and
target 13, with `target_ruled_out: false`. It uses constant-size integer
arithmetic and does not enumerate colourings.

There is a narrower boundary for the alternating-edge method itself.
If all three coarse lengths are odd, no edgewise antisymmetric filler
can succeed while preserving the old vertex colours. For a mirrored pair
of new positions, its orientation polynomial must satisfy H=0 above.
At Z=-1 all three endpoints are -1, so H(-1)=4*sum_i T_i(-1). Each T_i(-1)
is odd, being a signed sum of an odd number of edge positions; their sum
is odd and cannot vanish. Allowing a different antisymmetric word on each
edge does not help: each mirrored position pair has distinct residues
modulo g and must separately satisfy this equation. Arbitrary fillers
that are not edgewise antisymmetric are outside this narrower argument.

## Exact defect of the nearest lift and a broader periodic class

A common symmetric cell stencil chooses arbitrary `c_1,...,c_h` in {+1,-1}.
In every original vertex's nearest-vertex cell multiply its colour at offset
r by `c_|r|`, with c_0=1; truncate the centre and leaf cells at the tree
boundary. Nearest-vertex colouring is the all-positive stencil. This class
also includes alternating and every other common symmetric block word.

Let e_i be the three old leaf signs. Balance and the old distance-one
identity imply `sum e_i=s`. Exactly two leaves, say p,q, have sign s.
Put `E=sum_(j=1)^h c_j z^j`, `K=1+E+E(z^-1)`, and `A_i=z^(gL_i)`.
The lifted arm polynomials are exactly

```text
S'_i = K S_i(z^g) + sE - e_i A_i E.
```

Their total sign sum remains zero: the cell-weight correction is
`E(1)*(s-sum e_i)=0`. Substitution into Q, eliminating the old Q and using
`sum e_i=s`, gives the exact all-distance formula

```text
Q' = 2s E(1-A_p)(1-A_q),
D' = s*z*E*(1-A_p)(1-A_q)/(1-z).
```

`symbolic_residuals` checks separately the coefficients of E and E* in
independent endpoint variables, for all six possible centre/tip patterns.
Thus every symmetric stencil fails: its distance-two difference is
`s*c_1`, never zero. This excludes a whole periodic repair class, not just
the nearest lift. The final nonzero distance is
`k=g(L_p+L_q)+h`, with coefficient `-s*c_h`.

For arbitrary additional recolouring let its centre change be e_0 and its
arm changes be R_i, with coefficients in {0,-2 times the old sign}. A
necessary and sufficient repair condition is balance together with

```text
e_0(1-sum A_i)+sum_i R_i(1-sum_(j!=i) A_j)-sum_i A_i R_i* = -Q'.
```

This equation, rather than distance two alone, is the remaining repair
constraint. The successful edge recipes escape the symmetric stencil class.

## Local repairs that cannot succeed

These statements allow any number of colour flips and apply to every
symmetric stencil. They are bounds on repairs, not on all homometric pairs.
Write N_i=gL_i and k=N_p+N_q+h as above.

If all changes are within radius R of the centre, every affected pair has
distance at most `max N_i+R`. Therefore `R<k-max N_i` leaves the nonzero
coefficient at k untouched. For either priority family and t>=1 this
excludes every centre-ball repair through radius `5320t-4` (five) or
`5320t-5` (seven), regardless of the base's tip pattern.

For changes within radius R of the centre **or any leaf**, write
`R_i=U_i+A_i V_i`, where U_i has exponents 1..R and V_i has exponents
-R..0. Expanding the repair equation shows its support is confined to

```text
[0,R], [N_i-R,N_i+R], [N_i+N_j-R,N_i+N_j] (i<j).
```

If k lies outside their union, repair is impossible because Q' has a
nonzero coefficient at k. `repair_certificate` reports this exact integer
support test, not an optimization or search. In both priority families,
for every t>=1 and every tip pattern, it excludes R<=17. Eighteen is
inconclusive for some patterns; the program does not call it impossible.

```sh
python3 projects/almost-halving-three-branches/corrected_subdivision.py --obstruction five --t 1 --radius 17 --summary
python3 projects/almost-halving-three-branches/corrected_subdivision.py --example 9 3 --factor 5 --stencil=+- --summary
```

The second command is deliberately labelled a non-homometric diagnostic.
The bounds do not exclude changing colours throughout the arms, varying
stencils between cells, moving the omissions, or unrelated constructions.

## Verification and remaining route

Tests reconstruct graph distances by breadth-first search independently
of the production checker. They cover every arm permutation, both colour
orientations, all symmetric words at factors 3,5,7, both successful recipes,
disjointness, complete coverage, and altered-pair rejection. An independent
integer-convolution counter, cross-checked against those graph distances,
also verifies the actual t=1 witnesses in the original untrimmed tree:
8068 vertices per side and 32,542,278 pairs per side. Swapping two opposite
colours preserves disjointness and size but is rejected. Eight focused tests
and all 90 tests in the project pass. Independent resident integration
and milestone review are still required.

The next mathematical step is the uncovered residue classes above. The
new edge equation H=0 provides a different route: find sign polynomials
T_i with the required lengths beyond the two recipes, or change the
coarse base construction. A failure of either recipe is not an all-pairs
obstruction. The arbitrary-hole route and the universal acceptance test
remain necessary if these prefixes cannot be completed. No universal
milestone completion or public deployment is claimed here.
