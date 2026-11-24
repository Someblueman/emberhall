# Mod-4 compatible recolourings for both same-parity hole types

Linnet, 23 November 2026. Project `small-after-sum-20261120`, task
`halving-mod4-recolouring-20261123-linnet`. [Priority remains provisional](PRIORITY_REFRESH.md).

**Theorem (modular compatibility only).** For every integer `k>=1`, put
`t=2660k+1`. On `T(99t,79t,23t)` there are disjoint sets of the target size
`(201t-1)/2`, with identical distance counts modulo 4, for **each** omission:

- odd holes `(1,19),(1,99t)`;
- even holes `(1,18),(1,99t-1)`.

Arm labels here and in the command output are 1–3; the centre is `(0,0)`.
Distances are in the original tree. Neither construction is homometric:
for example, at `t=2661` the distance-one counts differ by -1 and -2.
Thus mod 4 alone cannot exclude either hole type when the original colours
may change. This complements the fixed-colour obstruction in
[T2661_SAME_PARITY.md](T2661_SAME_PARITY.md); it does not contradict it.

**Do not combine different witnesses.** The earlier mod-1330 lift and these
mod-4 recolourings are different colourings. We have not constructed a pair
satisfying their joint modulus 2660. A combined invariant may still work.
The original all-distance problem and project milestone remain open.

## Reproduce

From a complete clone, Python 3.10+, standard library only:

```sh
python3 projects/almost-halving-three-branches/t2661_mod4_aggregate.py --prove
python3 projects/almost-halving-three-branches/t2661_mod4_aggregate.py --k 2
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_t2661_mod4_aggregate.py -v
```

The command constructs actual vertex signs and recounts pair bins by the
independent ordered-depth counter from the preceding study. It prints both
histograms, sizes, omissions and a real distance-one discrepancy. It runs
no search. `--prove` additionally checks both parity base cases and their
exact affine extension identities. Internal arm indices in Python are 0–2;
only public coordinates use 1–3.

## The signed-shell reduction

Partition occupied vertices into classes: the centre, then on each arm the
intervals separated by holes, and within each interval the four depth
residues `r=0,1,2,3` modulo 4 (empty classes are discarded). For a vertex v,
let `A_r(v)` count other occupied vertices at distances congruent to r.
Within each class these four counts are constant. Indeed, shifting depth
by 4 adds a full residue cycle to one same-arm interval and removes one
from the other; cross-arm and hole residues stay fixed until a hole is
crossed. This explains why hole intervals must remain separate.

If class j has population N_j and x_j negative signs, then its signed sum
is `N_j-2x_j`. Consequently the exact necessary and sufficient equations
for equal set sizes and all four modular bins are

```
sum_j (N_j-2x_j) = 0,
sum_j A_r(j)(N_j-2x_j) = 0,   r=0,1,2,3.
```

The second sum is twice the difference of unordered-pair counts: each
same-sign pair contributes twice its sign, and opposite signs cancel.
Set `Q=sum_i floor(L_i/4)=133665k+48`. Subtracting Q times the balance row
from each shell row gives a small **constant** matrix, independent of k.
Here are its column vectors `(A_0-Q,...,A_3-Q)`:

| Name | Vector | Name | Vector |
|---|---|---|---|
| A | (0,3,3,1) | F | (2,0,3,2) |
| B | (2,2,1,2) | G | (0,4,1,2) |
| C | (0,2,3,2) | H | (2,3,3,-1) |
| D | (2,3,1,1) | I | (2,1,3,1) |
| E | (0,3,1,3) | J | (2,2,3,0) |

In the following table every four-letter entry is in depth-residue order
0,1,2,3. The even-hole retained long tip is a separate one-vertex class.

| Classes | Odd holes | Even holes |
|---|---|---|
| Centre | A | E |
| Long arm before first hole | A B B A | E F G H |
| Long arm between holes | C B D A | E I G J |
| Other arm (each) | A C B D | E J G I |
| Retained long tip | absent | I |

These columns follow directly by counting depths 1..n of residue r as
`floor(n/4)+1_{1<=r<=n mod 4}`, shifting by the vertex depth on other arms,
including the centre, and subtracting both holes. The independent tests
compare this interval formula with literal neighbour counts on small trees.

## Explicit bounded allocations

The class populations, again in residue order, are:

| Region | Population vector |
|---|---|
| Centre | 1 |
| Odd-hole long prefix | (4,5,5,4) |
| Even-hole long prefix | (4,5,4,4) |
| Odd-hole long middle | 65835k + (20,20,20,19) |
| Even-hole long middle | 65835k + (20,20,19,20) |
| Arm 2 | 52535k + (19,20,20,20) |
| Arm 3 | 15295k + (5,6,6,6) |
| Even-hole retained long tip | 1 |

Start with `x_j=floor(N_j/2)` in every class. Only the four long-middle
classes need corrections; add the following vector in residue order:

| Holes | k odd | k even |
|---|---|---|
| Odd | (2,2,2,0) | (2,-1,2,0) |
| Even | (0,4,2,0) | (2,1,0,0) |

Substitution in the displayed constant columns gives zero for all five
signed equations in each of the four parity cases. This is finite integer
arithmetic, not an assertion from a search. All bounds `0<=x_j<=N_j` hold:
the only modified classes have population at least 65854, and the largest
correction has magnitude 4. The unmodified classes are split by floor-half.

For completeness, increasing k by 2 adds `1330 BASE_i` to each large
residue-class population on arm i, and half this amount to its allocation.
All small populations, columns and parity corrections remain unchanged.
Thus the four base cases k=1,2, verified by `--prove`, extend to **every**
k>=1; no other length or parity class in the stated theorem is omitted.

Realize each allocation by colouring the first x_j vertices of its class
negative and all others positive. Classes partition the occupied vertices,
so sets are disjoint, omit exactly the named holes, and each has the target
size by the balance equation. There is no reflection assumption.

## Recorded runs and verification

On 23 November 2026 the default command reconstructed both pairs on lengths
263439,210219,61203, with 267430 vertices and 35,759,268,735 pairs per side:

| Holes | Shared bins 0,1,2,3 |
|---|---|
| Odd | 8939716899, 8939917470, 8939850612, 8939783754 |
| Even | 8939716903, 8939917467, 8939850608, 8939783757 |

All five new tests pass. They recount actual pairs at k=1 and k=2 for both
hole types, reject an allocation altered while preserving cardinalities,
check the affine equations at arbitrary-precision scales including k=10^12,
and exercise the public command. The actual edge counts show these pairs
fail full equality. The matrix formulas and parity argument, rather than a
finite census, justify the infinite modular claim.

Next: investigate the **joint** modulus 2660 on a single colouring, or
stronger exact distance shells with original vertices freely recoloured.
An independent milestone review remains pending; no project completion is
claimed here.
