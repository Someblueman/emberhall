# Same-parity omissions: modular counts do not settle the open scale

Linnet, 23 November 2026. Task `halving-t2661-same-parity-study-20261124`,
project `small-after-sum-20261120`. [Priority remains provisional](PRIORITY_REFRESH.md).

**Result:** for every `t=2660k+1`, `k>=1`, there are disjoint sets of the
required size on `T(99t,79t,23t)`, omitting two odd-depth vertices, whose
complete distance histograms agree **modulo 1330** (and hence modulo 2, 5,
7 and 19). This means histogram bins collect distances by their remainder;
it does not mean the two full histograms agree or their counts agree only
up to a numerical congruence. The construction below fails full equality.
Thus these modular invariants, even jointly, cannot exclude all same-parity
hole pairs. This is a limitation theorem for that route, not a solution of
the tripod problem or an infinite obstruction family.

A mod-4 parity argument excludes every paired-half insertion that keeps the
original colours, for odd k, when the long insertion separates the holes.
A further exact result excludes a specified two-phase repeated-block
construction at `t=2661`, allowing all 4,190 of its sign choices. Arbitrary
colourings, even-even omissions, other hole locations, and unrestricted
non-periodic blocks with recoloured original vertices remain open. The default witness command is unchanged.

## Reproduce from the repository root

Python 3.10+; standard library only; no downloaded dependencies:

```sh
python3 projects/almost-halving-three-branches/t2661_same_parity.py --sweep --hensel
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_t2661_same_parity.py -v
```

`--k K` changes the scale to `2660K+1`. Output deliberately labels the
modular construction `homometric: false`. No large witness bundle is needed:
the short rule below regenerates every sign.

## Modular lifting lemma (arbitrary half-words)

Start with a balanced signed colouring of a tripod: `+1` and `-1` label the
two sets, and zero labels omitted vertices. On arm i choose a cut `c_i`
between original vertices and insert `2H_i` occupied vertices. Choose **any**
word `W_i` of length `H_i`; colour the insertion `W_i,-W_i`. Original signs
and order are preserved. Let p divide every `H_i`.

For an occupied vertex v write `A_r(v)` for the number of other occupied
vertices at distance congruent to r modulo p. For any colouring,

```
2 (left_pairs_r - right_pairs_r) = sum_v sign(v) A_r(v).
```

For an original vertex, distances to original vertices keep their residues:
every insertion has length divisible by p, and an original vertex lies
outside each inserted interval. The inserted vertices contribute exactly
`C=2 sum_i H_i/p` to each residue shell, independently of v and r. Hence
`A_new,r(v)=A_old,r(v)+C`. The extra signed contribution is zero because
the old signs sum to zero.

Pair the new vertex at offset j with offset `j+H_i`. Their residues and
positions relative to all old vertices agree modulo p. On another arm,
all distances shift by `H_i`. On their own arm, moving by `H_i` transfers
`H_i` possible neighbours from the upper interval to the lower interval;
each such interval contains exactly `H_i/p` of each residue. Self-distance
zero is excluded at both vertices. Thus their occupied distance shells
are equal, while their signs are opposite. All new contributions cancel.
This proves preservation of every modular distance count, without imposing
periodicity on W, and with each set gaining exactly `sum_i H_i` vertices.

Apply the lemma to the existing exact `t=1` witness in
[RESIDUE_2660.md](RESIDUE_2660.md), imported as `FRONTIER` and independently
recounted in the tests. It has 100 vertices per side, centre sign -1,
and holes `(1,19),(1,99)`. Take

```
H = 1330k * (99,79,23),    cuts = (19,0,0).
```

The lengths become `(99,79,23)(2660k+1)`, the holes are
`(1,19),(1,99(2660k+1))`, and each size is `(201t-1)/2`. Both holes are odd.
The lemma applies to **every divisor of 1330k**, including the joint modulus
1330. The recorded run chooses alternating W on all arms. Its independent
counter processes actual vertices: earlier depths on the same arm subtract,
depths on different arms add, and centre pairs are counted explicitly.
Packed integer histogram digits have more capacity than all possible pairs,
so no digit carry can corrupt counts. Random small tests compare every bin
with literal unordered-pair enumeration.

## A mod-4 obstruction for arbitrary half-words with the seed fixed

For **odd k**, keep every FRONTIER sign and the centre sign fixed, insert
`W_i,-W_i` with arbitrary half-words of lengths `H_i=1330k BASE_i`, and allow
any cuts `19<=c_1<99`, `0<=c_2<=79`, `0<=c_3<=23`. None of these lifts is
homometric: none even has equal distance counts modulo 4. This removes
periodicity entirely from this scoped negative result. It does not permit
recolouring the original vertices or moving the long insertion outside the
hole gap.

Here is a short proof. Every original vertex contributes its old mod-4
shell plus the same constant to each bin, because `2H_i` is divisible by 4.
The signed old contribution is therefore zero, as in the lifting lemma.
Write `C_r=2(left_pairs_r-right_pairs_r)` for the total new contribution and
`K=-2C_0-2C_1-C_2`. A first-half vertex at depth d, paired with its opposite
sign at depth `d+H_i`, contributes the difference of their occupied shells.
For the particular cuts `(19,0,0)`, these differences by offset modulo 4 are

| Offset | Bin 0 | Bin 1 | Bin 2 | Bin 3 | Contribution to K |
|---:|---:|---:|---:|---:|---:|
| 0 | -2 | -1 | 2 | 1 | 4 |
| 1 | 2 | -1 | -2 | 1 | 0 |
| 2 | 2 | 1 | -2 | -1 | -4 |
| 3 | -2 | 1 | 2 | -1 | 0 |

The same calculation for other allowed cuts rotates the last column.
This follows directly by counting distances 1..d-1 and 1..L_i-d on the
same arm, depths 1..L_j shifted by d on another arm, the centre, and
subtracting the holes. Explicitly, the number of depths 1..n congruent to r
modulo 4 is `floor(n/4)+1_{1<=r<=n mod 4}`. All final lengths are 3 modulo
4, the two holes are 3 modulo 4, and `H_i=2 modulo 4`; within an inserted
interval the relative side of each hole is fixed. These facts give a
rotation of `(4,0,-4,0)` on every arm, independent of k and word length.
`audit_mod4_cut_classes` checks all 64 residue classes of the three cuts;
these representatives exhaust the permitted geometry, not arbitrary trees.

Flipping a word sign changes K by a multiple of 8. Setting all signs in
one half-word to +1 gives K congruent to 4 modulo 8: its length is `4q+2`,
so full cycles cancel and the last two consecutive entries sum to +4 or -4.
There are three arms, hence total `K=4 modulo 8`, never zero. This proves
the obstruction for every half-word, without search. At `(19,0,0)` one can
also read the contradiction as `S0=S2, S1=S3`, although the respective
population differences are 3 and therefore odd.

For even k, all H_i are divisible by 4 and the lifting lemma preserves the
mod-4 histograms for **every** half-word. This explicitly prevents extending
the odd-k obstruction to all scales. The binary split is about this
construction, not the original question over all colourings.

## Exact two-phase template obstruction at t=2661

This separate result allows arbitrary signs on all 200 original occupied
vertices, including the centre. On each arm insert

```
B_i repeated H_i/P times, then (-B_i) repeated H_i/P times,
P=1330, H=(131670,105070,30590), cuts=(19,0,0).
```

Each B_i has P independent signs; the three words need not agree. This
includes different arm periods dividing 1330. Both omissions keep the same
locations as above. There are 3P+200=4190 free signs. Balance of the original
signs is necessary for equal sizes; no reflection assumption is made.

Let `S_i(z)` be the signed arm polynomial, `L_i` the final arm length,
`D=1-z^P`, and `N_i=D S_i`. The insertion has sparse numerator
`z^(c_i+1) B_i(z)(1-z^H_i)^2`; original vertices contribute `D sign(v) z^d`.
Let `C(z)=2(profile_left-profile_right)`. Counting all occupied neighbours,
then subtracting the two holes, gives the exact polynomial
`R(z)=(1-z)D C(z)` computed by `exact_numerator`. For an arm vertex at depth d,
the full-tree shell before hole subtraction satisfies

```
(1-z) shell_v(z) = 2z + z^(d+1)(1-sum_{j!=i} z^L_j) - z^(L_i-d+1).
```

The centre shell is `z(3-sum_i z^L_i)/(1-z)`. These formulas account for
all distances in the original tree. The implementation also handles
unbalanced signs, adding their explicit balance term rather than silently
using equality of sizes. Small random tests compare its entire numerator
with literal pair counting, including a missing centre and equal arm lengths.

For **every** sign assignment in the stated template,

```
[z^30592] R(z) = C_30592-C_30591-C_29262+C_29261 = 2 (mod 4).
```

The certificate is independently verified without polynomial multiplication
or elimination. At each of the four distances, enumerate a vertex's possible
neighbours (two on its arm, the centre, one on either other arm), subtract
holes, and accumulate coefficients of each of the 4190 sign variables.
Every variable coefficient is even; setting every variable to +1 gives
residue 2 modulo 4. Flipping any sign changes the sum by a multiple of 4.
Therefore R cannot vanish. The graph-shell certificate is valid even before
imposing balance, so it excludes every equal-size pair of this template.

This free-base obstruction does **not** extend automatically to arbitrary
half-words. Removing the period constraint while also freeing the original
colours leaves 24 variable coefficients odd in that same shell certificate. `unrestricted_half_word_escape` reports this failed
extension: it is a concrete remaining freedom, not an existence result.
When the original FRONTIER signs are fixed instead, the mod-4 argument
above already excludes all half-words at odd k.

## Recorded run and scope

The command above on 23 November 2026 returned lengths 263439, 210219, 61203;
size 267430 per side; holes `(1,19),(1,263439)`; and 35,759,268,735 pairs
per side in each of the mod-2, 5, 7, 19 and 1330 recounts. Every modular
profile agreed exactly. The alternating lift first differs at distance 1,
with left-minus-right count -1.

The finite menu separately checks all four period-two words independently
on each arm, and cuts `{0,floor(BASE_i/2),BASE_i}`: 64*27=1728 exact
polynomial tests, zero homometric hits. This is an exhaustive result about
that explicitly finite menu only. Fixed base signs at cuts `(19,0,0)` also
fail the necessary mod-4 equations for periods 2,5,7,10,14,19,38,70,1330.
For period 1330, freeing the original signs gives the stronger 4190-variable
certificate above. No finite search here is promoted to an unrestricted
upper bound. An independent milestone review is still required.

A continued bounded attempt (`--refine 20`) also freed individual paired
positions from their periodic residue groups while allowing all original
colours to change. It still excluded 856 such free positions (5046 variables
total). Its 1831-equation certificate is regenerated and independently checked
by occupied graph-shell range sums; only its count and SHA-256 are printed:
`3c7882602b056aa5b8b76bea043b6aecb86156e11bd83831e417f859420f50ba`.
The run stops when the next escape would require more than 2048 new positions,
not because arbitrary half-words were exhausted. All 15 tests pass (19 including the preceding mod-2 module); they include
independent modular-shell counts and both sides of the odd/even-scale boundary.

Next useful route: recolour the original vertices together with non-periodic
half-word defects, move the long insertion outside the hole gap, or change
the holes. Merely adding more mod-5/7/19 distance counts
to these odd-hole candidates cannot settle the general problem.
