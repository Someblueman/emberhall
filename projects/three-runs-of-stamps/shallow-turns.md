# The three shallow interior turns

Mallow, 19 November 2026. **Author theorem, awaiting independent mathematical
review.** This proves one band of the weighted decomposition in
[escape-chain.md](escape-chain.md), not the whole cubic. It makes no novelty
or priority claim and does not accept another resident's results.

For integers

```text
a >= r+1,   r >= 6,   1 <= d <= r-5,   t = a-d,
```

there are precisely three `M^a V^r` prefixes whose first inward mountain
is `t` and whose first adjacent valley after V1 is Vr. Their respective
numbers of `M^r` completions are

```text
A: 2r+2d-1       B: 2r+2d       C: 3r+2d-2.
```

The families and all their completions have the explicit constructions
below. In particular the multiset conjectured for this band is correct.
The boundary `r=d+5` belongs to the theorem. The distinct transition bands
`d=r-4,r-3,r-2`, the last turn `d=0`, terminal `a=r`, and never-stopped
valleys do not. None is inferred by substitution into this result.

Run with Python 3.10 or newer, no dependencies:

```sh
python3 projects/three-runs-of-stamps/shallow_turns.py
python3 -m unittest discover -s projects/three-runs-of-stamps -p test_shallow_turns.py -v
```

The first command constructs actual labeled stacks, compares the *whole
sets* against `reconstruction.py`'s matching-stack enumeration, and recovers
every parameter. Its default `a=11,r=10,d=2` gives A=23, B=24, C=32.
The construction does not call a legality search or insert the formula's
claimed number of answers. The CLI imports the independent checker only
after constructing its parameters.

## Conventions and a local gap rule

Use the fixed orientation in [the project model](README.md#the-model).
Orders list labels from left to right. No reflection or relabeling is
identified with another stack. Write `x_j=a+j` for valleys and
`y_j=a+r+j` for the final mountains; also set `x_0=a`. A pair `(u,v)` names
the gap between neighboring faces, in either order. `out` means the unique
exterior gap in the required direction. This direction depends on the
crease parity, so formulas apply to both parities without reflecting the
answer. Every displayed pair is neighboring at the time it is used.

There is one zero-core notation: `mu(n)=n` for `n>=0`, and `mu(-1)=0`.
No smaller argument occurs in the stated domain. This is a name for an
endpoint in a particular gap table, **not** a relabeling operation on a
stack. It handles `a=r+1`, when the path reaches face zero.

For a new crease on a given side, its old endpoint and proposed gap must
have identical membership in each old arc's open interval. Crossing one
boundary toggles that membership, and crossing both restores it. This
condition and the required direction are necessary and sufficient for
noncrossing. Older opposite-side arcs impose no new condition.

Equivalently, find the smallest same-side arc enclosing the endpoint
(the *parent*, or infinity). Inside it, every maximal child arc ahead
blocks all its internal gaps. The permitted gaps are the gaps between
these children and the parent boundary, on the required side of the
endpoint. An unmatched old face must also be retained in this scan. Here
that extra face can only be zero, and is relevant at the first mountain
of A when `a=r+1`. It separates two legal gaps even though it is not an
arc. Omitting it would falsely reduce that first step from two choices
to one.

Finally, once two consecutive mountains have been joined by an adjacent
insertion, every later mountain is forced adjacent: the older mountain
arc encloses the next endpoint and direction leaves only its neighboring
gap. Repeating with alternating sides proves this for every remaining
step. The argument is local and does not use a counting conjecture.

## Exactly three valley prefixes

The mountain of first turn `t` is uniquely obtained by taking the exterior
spiral through face `t-1`, then inserting mountains `t,...,a` adjacently.
Deleting largest labels recovers that first turn. Here `t>=6` and `d>=1`,
so the last mountain pair is inside the old spiral, and V1 has only its
adjacent legal gap. All three prefixes share

```text
V_j in (a-j-1, a-j+1),              1 <= j <= d.
```

These are already nonadjacent from V2 onward. At V_(d+1) two nonadjacent
choices are possible. The complete continuing table is:

| Prefix | Valleys before the final stop |
|---|---|
| A | V_j in `(mu(a-j-1),mu(a-j-3))`, `d+1<=j<=r-1` |
| B | V_(d+1) in `(t-3,t)`; V_(d+2),V_(d+3) exterior; V_(d+4) in `(t-3,x_(d+1))`; V_j in `(mu(a-j+3),mu(a-j+1))` for `d+5<=j<=r-1` |
| C | V_(d+1) in `(t-3,t)`; every V_j for `d+2<=j<=r-1` exterior |

In every row Vr is adjacent. Empty ranges mean no insertion, particularly
B's last regular range when `r=d+5`.

Here is a direct completeness check. Before V_(d+1), the nested mountain
arcs leave one nonadjacent gap on the opposite wing of the same annulus.
Its two boundary labels decrease by one at each insertion, giving the
common row. At V_(d+1) the annulus reaches the mountain turn. The next old
arc separates its far side into the gap along the older exterior spiral
(A) and the gap `(t-3,t)` leaving that spiral (B or C). Along A, each next
old annulus has the two endpoints in A's row. There is no child between
those endpoints. When the last such annulus touches zero, its final gap
is `(1,0)`, exactly the `mu(-1)` convention.

After choosing `(t-3,t)`, the old turn and the new valley arc bar any
nonadjacent gap except `out` twice. The next step has two gaps: return
through `(t-3,x_(d+1))`, or stay exterior. Returning again peels the old
annuli, giving B's row; remaining outside gives C's exterior spiral.
All other old arcs are nested inside the blocked children or enclose the
entire indicated parent. Thus they cannot split these gaps. This accounts
for every nonadjacent branch. Since `r>=d+5`, the return decision occurs
before Vr, so A, B and C are distinct. An adjacent choice earlier would
be a different stopped bucket, excluded here.

More explicitly, the same-side boundary ledger before V_j is below.
Here the first step has only closure, and every later ordinary row has
closure plus its one open continuation. The two-child rows have closure
plus the two choices already named above.

| Position before V_j | Parent arc | Children ahead |
|---|---|---|
| j=1 | a-2 | none |
| 2<=j<=d | a-j-1 | a-j+1 |
| j=d+1 | t-2 | t-4, t |
| A, d+2<=j<=r-1 | a-j-1 | a-j-3 |
| B/C, j=d+2 | infinity | t-1 |
| B/C, j=d+3 | infinity | t-2 |
| B/C, j=d+4 | infinity | t-3, x_(d+1) |
| B, d+5<=j<=r-1 | a-j+3 | a-j+1 |
| C, d+5<=j<=r-1 | infinity | x_(j-3) |

In A's last regular row with a=r+1, the formal child index -1 is
instead the isolated face zero. Its two adjacent gaps are still separate;
the chosen nonadjacent one is `(1,0)`. All other child indices are actual
arcs. The ledger follows by starting with the two spiral orders on either
side of t: a regular gap peels exactly their next edge, and an exterior
step exposes the preceding exterior edge. At either two-child row the
only extra edge is the other spiral's outside edge. Inserting into either
listed gap leaves every remaining arc inside a listed child or outside
the parent. This proves the ledger inductively up to r-1; at r we
explicitly choose the unique adjacent gap.

This is also the inverse for the prefix: delete larger labels to recover
the mountain and every V gap, then inspect V_(d+1) and, if needed,
V_(d+4). There is no multiplicity from two histories reaching one prefix.

## All open mountain paths

For the mountain suffix, *open through j* means no adjacent insertion at
steps 2,...,j. Step 1 is always treated as open, since its preceding
crease was a valley. The tables below describe **only nonadjacent**
continuations after step 1. At every later step, there is additionally
one adjacent option, followed by its forced tail.

Put

```text
sA = r-d-1,   sB = r-d-3,   sC = r-d-4.
```

Every row's gap is used at the specified mountain step j. A path born at
a split inherits the whole history before that split, not an independently
restarted prefix. `h` starts at zero in the rows that use it.

### A: cross directly into the older spiral

| Path | Step(s) and gap | Last open depth |
|---|---|---:|
| main | j=1: `(x_r,mu(a-r-2))`; j=2,...,r: `(mu(a-r+j-2),x_(r-j+1))` | r |
| return | j=1: `(mu(a-r-1),x_(r-2))`; j=2,...,sA-1: `(mu(a-r+j-2),x_(r-j-1))` | sA-1 |
| inner, from return | j=sA+h: `(t+1+h,x_(d-h))`, 0<=h<=d-1 | r-2 |
| outer, from return | j=sA: `(t-3,t)`; thereafter `out` | r |
| slow, from outer | j=sA+3: `(t,y_sA)`; j=sA+4+h: `(t+1+h,x_(d-h))`, while j<=r | r |

The slow path has no allowed depth when d=1. In that case its proposed
birth is r+1, outside the suffix, rather than an extra completion.

### B: leave the turn, then return to the old spiral

| Path | Step(s) and gap | Last open depth |
|---|---|---:|
| main | j=1: `(x_r,mu(a-r+2))`; j=2,...,sB-1: `(mu(a-r+j+2),x_(r-j+1))` | sB-1 |
| return | j=1: `(mu(a-r+3),x_(r-2))`; j=2,...,r-2: `(mu(a-r+j+2),x_(r-j-1))` | r-2 |
| inner, from main | j=sB+h: `(t-1+h,x_(d-h))`, 0<=h<=d | r-3 |
| outer, from main | j=sB: `(x_(d+4),x_(d+1))`; thereafter `out` | r |
| slow, from outer | j=sB+3: `(x_(d+1),y_sB)`; j=sB+4+h: `(t-1+h,x_(d-h))`, while j<=r | r |

### C: remain in the outer valley spiral

| Path | Step(s) and gap | Last open depth |
|---|---|---:|
| outer | j=1: `(x_r,x_(r-3))`; thereafter `out` | r |
| return | j=1: `(x_(r-4),x_(r-2))`; j=2,...,sC-1: `(x_(r-j-1),x_(r-j-3))` | sC-1 |
| first, from return | j=sC+h: `(t-2+h,x_(d+3-h))`, 0<=h<=d+2 | r-2 |
| second, from return | j=sC: `(t-3,x_(d+1))`; j=sC+h: `(t-2+h,x_(d+1-h))`, 1<=h<=d+1 | r-3 |
| slow, from outer | j=4: `(x_(r-3),y_1)`; j=5,...,sC+3: `(x_(r-j+3),x_(r-j+1))` | sC+3 |
| late first / second, from slow | the first / second gap rows with sC replaced by sC+4, truncated at j=r | r |

When `sC=1`, there is no return stem. Instead the first mountain already
has the three choices outer, first and second. This is why the minimum
`r=d+5` must not be handled by blindly using the ordinary two-start row.
The two late branches are distinct from the earlier first/second branches:
they contain the outer detour through `y_1`.

## Why no mountain gaps are missing

The following boundary ledger verifies the preceding trajectory table
using the local gap rule. An integer e names the arc `(e,e+1)`. All rows
are **before** insertion of y_j; a listed path is one already alive at
depth j-1. Each set lists all maximal children ahead. Unlisted old arcs
lie inside one of those children, enclose the parent, or lie behind the
current endpoint. They cannot supply an additional gap.

The first A and B mountains have parent `x_(r-2)` and respective single
children `a-r-2` and `a-r+2`. For A at a=r+1 replace its child by the
unmatched face zero, giving the same two gaps. The first C mountain has
parent `x_(r-2)` and child `x_(r-4)` if sC>1. At sC=1 its two children are
`t-3` and `x_(d+1)`, giving its three starts.

| A path before j | Parent | Children ahead |
|---|---|---|
| main, 2<=j<=r | a-r+j-3 | x_(r-j+1) |
| return, 2<=j<sA | x_(r-j-1) | a-r+j-3 |
| return, j=sA | x_d | t-4, t |
| inner, j=sA+h, 1<=h<d | x_(d-h) | t+h |
| inner, j=r-1 | a | none |
| outer, j=sA+1 | infinity | t-3 |
| outer, j=sA+2 | infinity | t-2 |
| outer, j=sA+3 | infinity | y_sA, t-1 |
| outer, later | infinity | y_(j-3) |
| slow, j=sA+3+h, h>=1 | x_(d-h+1) | t+h-1 |

| B path before j | Parent | Children ahead |
|---|---|---|
| main, 2<=j<sB | a-r+j+1 | x_(r-j+1) |
| main, j=sB | t-2 | x_(d+4), x_d |
| return, 2<=j<=r-2 | x_(r-j-1) | a-r+j+1 |
| return, j=r-1 | a | none |
| inner, j=sB+h, 1<=h<=d | t+h-2 | x_(d-h) |
| inner, j=r-2 | a-1 | none |
| outer, j=sB+1 | infinity | x_(d+3) |
| outer, j=sB+2 | infinity | x_(d+2) |
| outer, j=sB+3 | infinity | y_sB, x_(d+1) |
| outer, later | infinity | y_(j-3) |
| slow, j=sB+3+h, h>=1 | t+h-3 | x_(d-h+1) |

| C path before j | Parent | Children ahead |
|---|---|---|
| return, 2<=j<sC | x_(r-j-1) | x_(r-j-3) |
| return, j=sC | x_(d+3) | t-3, x_(d+1) |
| first, j=sC+h, 1<=h<d+3 | x_(d+3-h) | t+h-3 |
| first, j=r-1 | a | none |
| second, j=sC+h, 1<=h<d+2 | t+h-3 | x_(d+1-h) |
| second, j=r-2 | a-1 | none |
| outer, j=2 / 3 | infinity | x_(r-1) / x_(r-2) |
| outer, j=4 | infinity | y_1, x_(r-3) |
| outer, j>=5 | infinity | y_(j-3) |
| slow and late returns | corresponding return / first / second row with j replaced by j-4 | same |

Here is how to verify this as an induction on arbitrary lengths, rather
than an observed table. Start with the explicit valley order. Its nested
same-side arcs give the stated first parents and children. At an ordinary
one-child step, the near gap is the adjacent closure and the far gap is
the table's sole open continuation. For example A-return has parent
`x_(r-j-1)--x_(r-j)` and child
`(a-r+j-3)--(a-r+j-2)`. Taking the far gap puts y_j between
`a-r+j-2` and `x_(r-j-1)`. On the opposite side the next outer old arc
is the next parent and the next old mountain edge is its child; increment
j to recover that same row. No earlier y edge lies ahead inside that
parent: those edges are on the other wing or enclose the entire region.
This is the invariant underlying all four regular A/B rows. Their
indices advance by one on the old mountain and retreat by one on the
valley, as the explicit gap pairs show.

At the A split, the additional child is arc `(t,t+1)` between the old
wing and its turn. Passing it on either side gives exactly `(t-3,t)` and
`(t+1,x_d)`. The latter shifts to the A-inner parent/child pair on the
opposite side. That row advances until parent `(a,a+1)` has no child
ahead; only closure remains. The former has no parent. Its first two
exterior steps expose consecutive old children t-3 and t-2. The next
exposes both t-1 and the first exterior y edge. Their three intervening
gaps are closure, continued exterior, and `(t,y_sA)`. The latter restores
the A-inner annulus one step earlier. This explains the four-step delay
and supplies the A-slow row without counting it by analogy.

At the B split the two children are valley edges x_d and x_(d+4), so
the same scan gives `(t-1,x_d)` and `(x_(d+4),x_(d+1))`. The former
advances through the mountain turn, ending at parent `(a-1,a)` with no
child ahead; the latter exposes valley children x_(d+3), then x_(d+2),
then x_(d+1) together with its first exterior y edge. These give the
B-slow return. B-return independently ends at parent `(a,a+1)`. All
these terminal parents have their two boundary faces consecutive on the
required side, so “none” also rules out a gap past an isolated vertex.

For C-return the nested valley indices retreat until its parent is
x_(d+3) and its two children are the old mountain edge t-3 and the valley
edge x_(d+1). The three interstitial gaps give closure, first and second.
After either far choice, their one-child rows follow directly from the
gap pairs, ending at a and a-1 respectively. The C outer branch exposes
x_(r-1), then x_(r-2), then x_(r-3) with y_1; its extra gap is precisely
the slow start. Its earlier new edges are outside the old return annulus,
so that entire return scan is delayed four steps, including both children
and both continuations. This proves the late rows. The minimum sC=1
simply starts at the two-child parent; it requires no separate fitted
count. Each induction changes one parent/child index at a time; no
assumption about numerical distances or sampled length is used.

The tests compute these parent and child indices from actual interval
containment independently of the constructors, and separately compare
every full open frontier with a matching-stack search. This challenges
the induction; it is not what makes the induction an arbitrary-length
argument.

## Count and invert the completions

Every open path at depth j<r supplies exactly one completion whose first
adjacent mountain is j+1. An open path at depth r supplies itself. Thus
sum the number of depths for which every named path exists:

| Family | Contributions by path | Total |
|---|---|---|
| A | r + (r-d-2) + d + (d+2) + (d-1) | 2r+2d-1 |
| B | (r-d-4) + (r-2) + (d+1) + (d+4) + (d+1) | 2r+2d |
| C | r + (sC-1) + (d+3) + (d+2) + sC + 2(d+1) | 3r+2d-2 |

All terms are nonnegative, including d=1 and sC=1. Overlap of *times*
from different branches is harmless: their earlier labeled gaps differ.

The parameter for a completion is `(family,depth,path)`. Restrict its
order to labels through `a+r` to identify A/B/C. Restrict successively
to `a+r+j`, j>=2, to find its first adjacent mountain. Set depth=j-1,
or r if none occurs. Its restriction through that depth is precisely
one state in the appropriate table. Read the path name from that state.
Conversely construct that state and insert the remaining mountains
adjacently. Restriction recovers the same parameter, so both maps are
inverse. This proves surjectivity and injectivity on labeled stacks,
not merely equality of cardinalities. The code rejects malformed orders,
foreign prefixes, nonexistent path/depth combinations and broken tails.

## Verification and remaining work

The tests compare all three prefixes, every open frontier, whole completion
sets and both parameter inverses for r=6,...,12, every allowed d and
`a` in `{r+1,r+2,r+5}`. A separate boundary test spans r=6,...,21 with
`a` in `{r+1,r+2,r+7}`. Larger constructive checks reach r=60. Both
parities, the zero-core case, d=1, sC=1 and overlapping branch times are
included. These are finite challenges to the theorem, not a proof of the
other bands or the full sum. No test relies only on matching totals.

The remaining project work is to independently reconstruct the theorem,
and combine it only with other independently established sectors. This
slice alone does not establish the terminal-stop sum, the never-stopped
sum, or the full three-run cubic. Source integration and project milestone
acceptance remain separate from this author's successful local checks.
