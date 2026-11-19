# The count for three equal runs of stamps

For every integer $k\ge2$, the number of legal labeled stacks with crease
assignment $M^kV^kM^k$ in [the fixed face-zero orientation](README.md#the-model) is

$$C(k)=\frac{9k^3-25k^2+30k-12}{2}.$$

This is our author proof of the formula interpolated in
[Hull, Ibrahim, Paltrowitz, Ter-Saakov and Wang, §5.2, Table 2](https://arxiv.org/html/2503.23661v2#S5.SS2).
It joins Aster's decomposition, Fern's exterior weights, Sorrel's boundary
proofs, Mallow's shallow-turn proof and Rook's remaining sectors. The first
family has an independent reconstruction. Independent reconstruction of the
whole argument and comparison with Sakai's 2026 full text remain open.

## Recover one sector from each stack

Restrict the layer order successively to labels through $k+r$. Call valley
$r$ adjacent when its new face sits next to the preceding label in that
restriction. Let $r$ be the first such step **after valley one**, or record
“never.” Monitoring starts at two even when the very first valley was adjacent.
Each full stack has exactly one sector. The [chain and inverse](escape-chain.md)
show that after the stop every subsequent valley is forced. If a prefix stops
at $r$, deleting one of these forced valley collars together with the first
mountain removes exactly one completion. The [collar bijection](delayed-escape.md)
requires an already adjacent pair before the collar. It is used only *after*
the stop and never on an open chain.

Let $S(k,r)$ sum the weights at the stop with just $r$ final mountains,
$N(k,r)$ count these stopped prefixes, and $U(k,k)$ count the never-stopped
sector with all $k$ mountains. Repeating the bijection gives

$$C(k)=U(k,k)+\sum_{r=2}^{k}\big[S(k,r)+(k-r)N(k,r)\big].$$

For $k\ge3$, $N(k,2)=k+1$, $N(k,r)=k+2r-4$ for $3\le r<k$, and
$N(k,k)=2k-3$. These follow by taking the first difference of the proved
two-block prefix counts in [Hull et al., §3.1](https://arxiv.org/html/2503.23661v2#S3.SS1),
with the separate equal-length boundary as detailed in the chain proof.

## Weights for an interior stop

The stop-two sector, including its collars, is $k^2+k+3$ for $k\ge3$ by the
[first-valley proof](first-family.md) and its [reconstruction](RECONSTRUCTION.md).
The [stop-three gap table](escape-chain.md#a-fully-counted-next-bucket)
gives $S(k,3)=4k+16$ for $k\ge4$.

For $5\le r<k$, split the mountain prefix by its first inward step $t$,
with $d=k-t$. The all-exterior prefix and the turns $2\le t\le k$ are
disjoint and exhaustive by the [mountain classification](first-family.md).
Each number in the table is the weight of one stopped prefix for a mountain
of the indicated type.

| Mountain type | Individual weights | Construction and proof |
|---|---|---|
| Exterior | $2r-2,3r-4$ | [Fern's two routes](WEIGHTED_OPEN.md) |
| $d\ge r-1$ | $2r-2$ for each of $k-r$ types | [Deep turn](deep-turn.md) |
| $d=r-2$ | $4r-6,4r-5$ | [First boundary](turn-boundary.md) |
| $d=r-3$ | $4r-7,4r-7$ | [Two transitions](turn-transitions.md) |
| $d=r-4$ | $4r-9,4r-8$ | [Two transitions](turn-transitions.md) |
| $1\le d\le r-5$ | $2r+2d-1,2r+2d,3r+2d-2$ | [Shallow turns](shallow-turns.md) |
| $d=0$ | $2r,2r,3r-2$ | [Last turn](last-turn.md) |

The three transition rows sum to $24r-42$. Exterior and last turn give
$12r-8$. Summing $7r+6d-3$ over the shallow band gives $(r-5)(10r-15)$,
also valid when the band is empty. Add $(k-r)(2r-2)$ for the deep turns:

$$S(k,r)=2(r-1)k+8r^2-27r+25.$$

At $r=3$ this agrees with the separately established $4k+16$. At $r=4$,
$k\ge5$, the exterior weights are 6 and 8, the $k-4$ deep types contribute
6 each, and the $d=2$ boundary gives 10 and 11. The two remaining types
$d=1,0$ give respectively 9 and 9, and 8 and 8, by the following lemma.
Consequently $S(k,4)=6k+45$, again the displayed interior formula.

### Why the fourth-stop count holds at every mountain length

Fix $d=0$ or 1. Build the exterior mountain through $k-d-1$ and insert
the remaining $d+1$ mountains adjacently. From this one prefix take every
first valley, only nonadjacent second and third valleys, the adjacent fourth
valley, then every sequence of four mountains.

Here is the entire local rule for generating those gaps. Start beside the
current endpoint in the required direction. Emit this gap. When the next
face is unmatched, cross it and emit the following gap. When its same-side
partner is ahead, jump to the partner and emit the next gap. When the
partner is behind, stop. At the exterior stop as well. On this half-plane
the pairs start with labels of the parity of the current last face, and
only zero can lack a partner. Noncrossing makes every forward pair a whole
interval: gaps within it differ in membership from the starting face, and
the gap just beyond it has the same memberships. A backward partner is the
boundary of a containing interval. This proves that the walk emits precisely
the legal gaps, in order starting with the adjacent one.

The following finite certificate uses that rule. For each of the two
mountain types it lists the weights of *all* stopped prefixes and the
smallest label inspected anywhere in the eight-crease tree. An inspection
includes every jump endpoint, barrier and both available neighbors of
every emitted gap, even a valley gap discarded by the stop condition.

| $k$ | $d=0$ weights | $d=1$ weights | Smallest inspected, both trees |
|---:|---|---|---:|
| 5 | 8, 8 | 9, 9 | 0 |
| 6 | 8, 8 | 9, 9 | 0 |
| 7 | 8, 8 | 9, 9 | 0 |
| 8 | 8, 8 | 9, 9 | 1 |
| 9 | 8, 8 | 9, 9 | 2 |

The finite part can be repeated with the short walk and tree in
[cubic.py](cubic.py) and the [certificate test](test_cubic.py). The test also
compares the weights with the separate gap-signature enumeration.

To increase $k$ by two, add two to each old label except zero, and replace
old zero in place by the consecutive block $(1,0,2)$. The exterior mountain
has descending odd labels, zero, then ascending even labels. The substitution
therefore makes exactly the exterior mountain two faces longer. The $d+1$
adjacent insertions at the high end commute with it, proving the same assertion
for the initial turned mountain. Parities, prescribed directions and
partnerships between old nonzero faces are preserved. A partnership involving
old zero could change a walk only if it inspected zero.

At each seed, 8 and 9, no walk inspects zero. In the enlarged order every
step that encounters an endpoint, jumps to its partner, or stops at a
barrier encounters the corresponding old label plus two. A jump across
the replaced block crosses the entire block. No emitted gap touches the
block, since neither neighbor of its preimage was zero. Thus *the entire
list* of children agrees after substitution, and inserting a child commutes
with it. Induct over the eight creases to obtain a bijection of the trees.
All corresponding walks still avoid the new zero, so the same enlargement
can be iterated. The two seed parities cover every $k\ge8$ and the first
three certificate rows cover the smaller lengths. This induction is the
reason a finite computation suffices.

### Recovering a construction from the labeled order

First delete the suffix in decreasing label order to read the exact mountain
turn and the history of valley gaps. This selects a unique table row and
prefix, including at the boundary where two routes have equal weight.
Starting from the full order, invert each forced collar by its deletion map.
If the order is the one exceptional completion added by this collar, its
depth identifies it and the inversion ends. Otherwise the reduced order is
the input to the preceding collar. For a base order, deleting the final
mountains in reverse gives their actual insertion gaps; the row constructions
identify the route and closing time from these gaps. At the finite fourth
stop this is exactly the path in the walk tree. Beyond a seed contract the
untouched central block to its old zero before reading that path. Conversely,
build the specified prefix and suffix, then reinsert the collars with the
forward map, using the distinguished completion at its recorded depth if
needed. This explains how to distinguish equal-weight paths and invert
the construction on individual orders as well as sum their counts.

## Terminal stop, never stopped and summation

At the terminal stop the boundary is $k=r$, outside the interior theorem.
The [terminal proof](terminal-stop.md), including Sorrel's
[three early turns](terminal-turns.md), gives $S(k,k)=7k^2-23k+21$ for
$k\ge3$. The [open-sector proof](open-sum.md) gives
$U(k,k)=(9k^2-19k+12)/2$ for $k\ge2$. These cases have no collar bonus.

An interior sector with its collars contributes
$k^2+(3r-6)k+6r^2-23r+25$. Summing over $3\le r<k$ uses
$\sum r=k(k-1)/2-3$ and $\sum r^2=k(k-1)(2k-1)/6-5$.
Twice that interior sum is $9k^3-50k^2+93k-72$. Add twice the stop-two,
terminal and never-stopped contributions to get $9k^3-25k^2+30k-12$.
The interior sum is empty at $k=3$. At $k=2$ the separate seven-face
permutation check in [the model and controls](README.md#exactness-and-controls)
gives five stopped and five never-stopped stacks, also the claimed value.
