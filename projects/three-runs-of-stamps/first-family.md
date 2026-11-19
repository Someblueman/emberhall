# Counting tightly nested valley prefixes

**Status:** author proofs for a specified family and its enlargement, awaiting
independent reconstruction. It does not classify all two-run prefixes or prove the cubic.
The exact enumerator supports the argument on finite inputs; it is not the
proof of the statement for arbitrary length. No novelty claim is made.

## Geometric definition

Label the faces consecutively from zero, keep face zero facing right, and
use the [README convention](README.md#the-model). Let `k >= 2`.

1. Fold `M^k` into its single outward spiral: each new face is exterior,
   and each new crease encloses the whole previous stack on its side.
   Thus the last face, `k`, is exterior.
2. The first valley crease goes outward from `k`. Every later valley
   crease turns inward, placing its new face immediately beside the current
   endpoint on the required side. Do this for `k` valley creases.

Call the resulting prefix `P_k`. This is one specified prefix at each length,
not every prefix whose drawing resembles two spirals.

An explicit definition removes any ambiguity about “inward”. The mountain
stack in the actual fixed orientation is the descending odd labels, then
zero, then the ascending positive even labels, up to `k`.
Reflect the whole drawing *temporarily* if necessary so `k` is on the right.
Write its earlier faces as `B`, so the stack is `(B, k)`. Set `x_j = k+j`.
The valley part gives the following normalized order:

```
B, x_0, x_2, x_4, ..., x_(largest even <= k),
                     x_(largest odd <= k), ..., x_3, x_1
```

Undo the temporary reflection. It is only a coordinate change in this proof,
not identification of different labeled stacks. `family_prefix(k)` implements
this explicit construction. Examples in the actual orientation:

| k | P_k, left to right |
|---|---|
| 2 | 1 0 2 4 3 |
| 3 | 4 6 5 3 1 0 2 |
| 4 | 3 1 0 2 4 6 8 7 5 |
| 5 | 6 8 10 9 7 5 3 1 0 2 4 |

## Proposition and scope

For `1 <= c <= k`, exactly **c** legal completions of `P_k` append `M^c`.
In particular, exactly **k** stacks of `M^k V^k M^k` restrict to `P_k`.
The restriction deletes every face with label greater than `2k`.

This is not a lower bound obtained by exhibiting c examples: the gap argument
below rules out other insertions. It does not apply when `c > k`, when the
continuing path can encounter the earlier mountain spiral.

## Gap argument

Draw an edge as an arc between its two endpoints in the appropriate
half-plane. There is a useful exact test for a possible new endpoint `y`.
For **each existing arc `(u,v)` on the new arc's side**, the current endpoint
and `y` must either both be inside its open interval or both be outside.
Exactly one inside would interleave the endpoints and force a crossing.
Neither endpoint of a proposed new arc is an endpoint of an old arc on this
side: the immediately previous crease is on the other side.
Combine this membership test with the required left/right direction.
It is necessary and sufficient for a gap to be available.

Put `b=k` and write the valley faces as `x_0,...,x_b` in the normalized
order above. Third-run face `z_t` means label `2k+t`.
Define the following gaps in that normalized drawing:

- For `1 <= t < b`, `G_t` lies between `x_(b-t+1)` and `x_(b-t-1)`.
- `G_b` is the unbounded gap beyond `x_1`, away from all of `B`.
- After continuing through `G_1,...,G_(t-1)`, `S_t` is between
  `z_(t-1)` and `x_(b-t+2)`, for `2 <= t <= b`.

The two endpoints named for each gap are adjacent at the moment it is used.
Insertion changes adjacency but does not change any old endpoint's order.
Here is the complete transition table:

| State before insertion | Available gaps | State afterward |
|---|---|---|
| Before z_1 | G_1 only | continuing |
| Continuing, inserting z_t, 2 <= t <= b | G_t and S_t | G_t continues; S_t stops |
| Already stopped, inserting another face | between the two most recently inserted faces | stopped |

For the last row, at the first subsequent insertion “two most recently
inserted” refers to `z_(t-1),z_t`, where the stop was at step t.

**Why the table is exhaustive.** The original valley arcs connect successive
`x` labels and form alternating nested barriers. From `x_b`, the arc on the
new crease's side joins `x_(b-2)` to `x_(b-1)`. The current face is inside it;
the direction condition leaves only `G_1`. On a continuing step, apply the
interval-membership test to those nested arcs and to the earlier `z` arcs.
On the required side of the current face, their matching membership regions
are exactly the small gap `S_t` and the next gap on the opposite wing of the
nest, `G_t`. All intermediate gaps lie inside a separating arc whose interval
does not contain the current face, or outside an enclosing arc which does.
The two wings alternate because successive creases use opposite half-planes.
At `t=b` the next opposite-wing gap is beyond `x_1`. All faces of `B` lie
beyond `x_0` on the other wing, so no gap of `B` is reached in these b steps.
These observations also verify that both listed gaps satisfy every old
interval test and the direction condition.

If `S_t` is chosen, the new endpoint lies directly beside the preceding one.
The new short arc and the old enclosing valley arc bound a pocket on
alternating sides. At the next step the direction points into that pocket;
the same membership test leaves only the gap between those last two faces.
Inserting there repeats the pocket with opposite parity. Induction forces
all later insertions. This proves the last row without any assumption about
how many further faces will be inserted.

For an explicit check of the middle row, at k=4 the normalized prefix is
`B,4,6,8,7,5`. Its continuing gaps are `(6,8)`, `(7,5)`, `(4,6)` and
`(5,+infinity)`. With `z_1=9,z_2=10,z_3=11`, the stop gaps are `(9,8)`,
`(7,10)` and `(11,6)`. These alternate as the table predicts. They should be
reconstructed directly from the arc membership test by the next reader.

**Counting and inverse.** The first insertion is forced. At each of steps
`2,...,c`, choose to stop or continue; after stopping no choice remains.
There is one completion whose first stop is each `t in {2,...,c}`, plus one
which never stops in these c steps. That is `(c-1)+1=c` completions.
They are distinct: their first different gap gives a different relative
order of two labels, which later insertions preserve. Conversely delete
`z_c,...,z_1` from any full stack, in that order, and inspect the gaps in
reverse. The table recovers either its unique first stop or the never-stop
case. There are no duplicates and no omitted legal stacks of this prefix.

## A growing family: all tightly nested second runs

There is a larger family with **k distinct prefixes** and exactly **k²+1**
completions. Start with *any* legal mountain stack Q for `M^k` and put all k
valley faces in the gap immediately beside its endpoint on the required side,
always turning inward. Call the result N(Q,k). Its explicit construction
replaces label k in Q by the `x` block in the displayed order above when k is
even, and by the reversed block when k is odd. All other faces retain their
order. `nested_prefix` and `nested_family` implement this definition.

The original P_k is the member with an exterior endpoint. For all members,
a third run of length `c < k` has exactly c completions: before the final
escape, it stays inside the original gap, so the previous table applies.
At length k the original backing can be reached. We now count that event.

### Escape-gap lemma

Give the faces of Q integer positions. Put a test point h half a position
from face k in the direction **away from face k-1**. For each old crease
whose index has the parity of k-1, record whether h lies inside its interval.
Let g(Q) be the number of gaps of Q in that same direction from face k whose
half-integer test point has exactly that membership vector. Include the
unbounded gap, and include the original gap containing h.

Then the number of length-k completions of N(Q,k) is

```
k - 1 + g(Q).
```

To see this, use the earlier transition table until step k-1. There are k-2
already stopped paths, each forced thereafter. For the one continuing path,
step k can stop in S_k (one option), or leave the valley nest. The latter
arc is on the same side as old crease `(k-1,k)`. Its current endpoint lies
beside x_0 on the side away from k-1, so its memberships in old intervals
are exactly those of h. The M direction requires its new endpoint to lie
farther in that same direction. Within the nest, the only such matching
pocket is S_k; outside the nest, the membership test is precisely the
definition of g(Q). Collapsing the nest back to the original gap pairs these
external possibilities one-to-one with those gaps of Q, including the
original gap's outer remainder. No old endpoint or relative order changes
under that collapse. Thus there are `(k-2)+1+g(Q)` possibilities.

### Evaluating g without enumeration

Recall the elementary one-run spiral classification, also used in the
published paper's proof of `c(M^k)=k`. At every step there is one outward
continuation. There is also one inward choice from step two onward; after
the first inward choice all subsequent steps are forced. Hence the k
mountain stacks are indexed by first inward step `t=2,...,k`, or no inward
step. This can also be reconstructed by deleting higher labels and finding
the first endpoint that is not exterior; `first_inward` does that.

- **No inward step.** The last face k is exterior. On its outward side there
  is just the unbounded gap, so g=1.
- **First inward step t<k.** In the nested terminal spiral, k lies between
  k-1 and k-2, and the side away from k-1 points toward k-2. The two last
  same-side arcs `(k-3,k-2)` and `(k-1,k)` bound the annular region containing
  h. On the required side of k that region has only the single gap up to
  k-2. Crossing either boundary changes its membership vector; the other
  wing of the annulus is on the wrong side. Thus g=1.
- **First inward step t=k.** Before this insertion the stack was entirely
  outward. The new arc `(k-1,k)` lies outside the older nested chain of
  same-side arcs. The intervening gap has the empty membership vector.
  Looking away from k-1, exactly two gaps have that vector: the intervening
  gap itself, and the unbounded gap beyond the older chain. All intervening
  gaps are inside that chain. Thus g=2. For k=2 the older chain is just the
  isolated face zero; the two gaps on either side of zero give the same
  result directly from Q=`1 2 0`.

Only one Q first turns inward at its last step. It contributes k+1, while
the other k-1 stacks contribute k each. Their prefix restrictions are
pairwise distinct, and deleting the valley labels recovers Q uniquely.
Therefore this family's disjoint total is `(k-1)k+(k+1)=k²+1`.

The k=3 exception is explicit: Q=`1 0 3 2` first turns inward at step three;
N(Q,3)=`1 0 4 6 5 3 2` has four completions. The new face can escape to
either of the two old empty-membership gaps. Calling every member a
three-completion member would lose a legal stack.

### Unequal lengths: a corollary

The mountain length and the valley nest length need not be equal. For any
`a >= 2, b >= 2`, start with all a legal mountain stacks for `M^a`, nest
`V^b` in the endpoint gap, and append `M^b`. Their disjoint total is **ab+1**.
In the escape lemma replace the old endpoint label k by a and the nest depth
k by b: the final new arc has index `a+2b-1`, of the same parity as `a-1`.
The proof of g depends only on the old mountain stack. Hence the one stack
that first turns inward at step a has b+1 completions and the other a-1
have b each. This is a direct consequence of the same classification,
not an extrapolation from samples. Four unequal-length pairs are exercised
in the tests, including both orders of a and b.

## Allowing the first valley crease to skip faces

Enlarge the family by allowing the **first** valley face in any legal gap
of Q, then placing every subsequent valley face immediately beside its
predecessor on the required side. For k>=3 there are k+1 prefixes, with
exactly **k²+k+3** completions. At k=2 there are just two prefixes and five
completions. These are still restricted families, not all two-run prefixes.

The following local bijection reduces the arbitrary-length claim to an
explicit two-valley case, rather than to interpolation.

### Local insertion lemma

Let P be any legal prefix whose last crease is V and whose last two faces
are adjacent in the layer order. Write these last labels as A=n-2 and
B=n-1, where P has n faces. Let T(P) insert a new valley face C=n immediately
beside B on the required side. If F(P,r) counts extensions by r mountains,
then for every r>=1,

```
F(T(P), r+1) = F(P,r) + 1.
```

Normalize the drawing so the local order in P is `B,A`. In T(P) it is
`B,C,A`. On the side containing the old V arc A--B, subsequent mountain
arcs point right; on the other side they point left. The first mountain
face D=n+1 is forced into the gap C,A: A--B encloses C, and the direction
selects that half of the interval. Now the local order is `B,C,D,A`.

The next mountain face E=n+2 points left from D. It can go between C,D,
or somewhere left of B. It cannot go between B,C: the new arc D--E would
interleave the V arc B--C. The first choice begins a trapped inward spiral,
with exactly one completion of any remaining length.

In the second case delete C and D, and subtract two from all larger labels.
This replaces the detour B--C--D--E by B--E and leaves a completion counted
by F(P,r). Here is why this deletion and its inverse lose nothing:

- After E is left of B, B,C,D remain consecutive forever. A future rightward
  arc cannot enter B,C or C,D from the left, since A--B would then be crossed;
  from the right it points away. A future leftward arc from the right cannot
  enter B,C because of B--C, or C,D because of D--E; from the left it points
  away. This proves the consecutive-block invariant by induction.
- Outside this block, the intervals B--E and D--E have identical membership
  for every other endpoint. The two extra short arcs B--C and C--D have no
  endpoint inside them. All crossing tests for remaining arcs therefore
  agree before and after deletion.
- The inverse simply inserts C,D beside B toward A, and adds two to the
  mountain labels. Since the first mountain endpoint in a completion of P
  points left from B, the inverse enters the second case. Parities and all
  M/V inequalities are preserved by the even label shift. Later faces in
  the old gap B,A lie beyond D, as the same direction and interval argument
  forces. Thus the two maps are inverse on complete labeled stacks.

This gives one stopped completion and a bijection for all the others.
The assumption that A,B are adjacent is essential; the first added face is
not generally forced without it. The tests compare the actual deletion map,
not only its cardinality, on several prefixes and mountain-run lengths.

### Which first valley placements are possible?

Use the first-inward-step classification of Q again. If the mountain run
never turned inward, its endpoint is exterior and the first V has one gap.
If it turned inward before its last step, alternating enclosing arcs trap
the first V in the gap immediately beside the endpoint. These are the
adjacent placements already counted above.

If the first inward step is its final step a, normalize its layer order as

```
u, a, R, v       where u=a-1 and v=a-2.
```

Here R contains labels 0 through a-3 in their outward-spiral order. The first
V points right from a. The old arc u--v contains it; same-side arcs within
R are nested and fill R's span. Consequently the only possible gaps are
immediately before R and immediately after R (before v). If R is empty,
these are one gap. This is the a=2 exception. If a>=3, they are different:
one is adjacent to a, and the other skips every face of R. There are no
other gaps with the necessary interval memberships.

Thus exactly one additional first-valley placement exists for a>=3. After
that first valley, all further V faces are specified, so there is exactly
one extra prefix in the enlarged family.

### The extra prefix contributes b+2

Allow a>=3 mountains and b>=2 valleys. For the extra first-valley placement,
write X=a+1 and Y=a+2. At b=2, after the specified adjacent second valley,
the normalized prefix is

```
u, a, R, Y, X, v.
```

The first mountain face Z can enter exactly two gaps: between a and the
first face of R, or between the last face of R and Y. Its direction is left.
The arc a--X requires Z inside its interval, and the old nested arcs filling
R forbid R's internal gaps. Even when R is a singleton, its two sides are
distinct. No further gap satisfies these tests.

For the next mountain face W, the direction is right. If Z was before R,
the only options are immediately after Z or beyond v. The old same-side
chain spanning from the first face of R to v forbids everything between
those two regions. If Z was after R, W can be immediately after Z (before Y)
or between X and v; the arc X--Y excludes the intervening region. All four
options satisfy the remaining interval tests. They are distinct by Z or W's
relative order, so the base count is exactly four.

From b=2 onward the last valley crease is adjacent. Each increase of b adds
one tightly nested V and one final M, so the local insertion lemma adds one
completion. The extra prefix therefore has `4+(b-2)=b+2` completions.
Together with the previous family's ab+1 this gives **(a+1)b+3**, and setting
a=b=k gives k²+k+3. For a=2 the extra prefix does not exist, leaving 2b+1.

Example: at k=3 the extra prefix is `1 4 6 5 0 3 2` and contributes five
stacks. Alongside the earlier ten this gives fifteen of the 48 total stacks.
`--first-valley-family` reconstructs the enlarged family from legal insertions;
it does not use the formula to decide which stacks to emit.

## What was checked, and what remains

The tests reconstruct P_k for `2 <= k <= 12`, check its legality, and enumerate
every third-run length `1 <= c <= k`. Each count equals c and every resulting
stack passes the separate direct permutation predicate. The full seven-face
universe independently gives ten stacks at k=2. These are finite checks only.

The other two-run prefixes are substantial unfinished work. There are
`2k^2-3k+2` in total by the published two-block result. The growing family
selects k of these, contributing k²+1 full stacks. At k=2 it contributes
five of ten; at k=3 it contributes ten of 48. The remaining prefixes are
not covered by either proposition. The tests check all k family members
through k=10, including the unique k+1 exception and disjoint restrictions.

Next useful pieces, in order:

1. Independently reconstruct the gap table and inverse, especially both
   parities, the escape-gap lemma, and the unique k+1 exception. This author
   argument is not an independently accepted milestone.
2. Classify prefixes whose second or later valley face does not use the
   adjacent gap, including those with internal mountain endpoints. Record explicit gap
   conditions for each class; a fitted count is not a classification.
3. Prove those classes disjoint and exhaustive, then sum their counts. Do not
   subtract k²+k+3 from the conjectured cubic and call the remainder
   a theorem. Keep the 2026 prior-art lead in the README unresolved until read.
