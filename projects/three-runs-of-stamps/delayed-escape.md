# A valley escape at the second fold

**Status: author result, awaiting independent reconstruction.** This is a
separate family from the first-valley family in `first-family.md`. It does
not classify every two-run prefix and does not prove the three-run cubic.
No novelty or priority claim is made. The older arguments remain pending
their own independent reconstruction; this note does not accept them.

From a clone, with Python 3.10 or newer and no dependencies:

```sh
python3 projects/three-runs-of-stamps/delayed_escape.py --k 4 --list
python3 -m unittest discover -s projects/three-runs-of-stamps -p 'test_delayed_escape.py' -v
```

The program is standalone. Its gap-signature sweep does not import the
earlier enumerator. The tests separately use full permutations for the
small controls. Counting uses the geometric definition, never the formula.

## Definition and result

Use the fixed face-zero orientation and noncrossing labeled layer model of
[Hull et al., Definition 2.1](https://dmtcs.episciences.org/en/articles/15454/download),
not a rigid-paper folding motion. An order lists faces from left to right;
positions, rather than labels, satisfy the inequalities. Crease i joins
i to i+1 and shares a half-plane with precisely the creases of its parity.
Even M creases point left, even V creases right; odd creases reverse these.

An **adjacent insertion** puts the next face in the gap immediately beside
the current last face, on the side required by its crease direction.
For a,b >= 2 define D(a,b) by:

1. Take any legal mountain-only order of faces 0,...,a.
2. Insert the first valley face adjacently.
3. Insert the second valley face in any legal **non-adjacent** gap.
4. Insert all remaining b-2 valley faces adjacently.

The family is specified before the final mountain run is appended. Different
insertion histories cannot give the same prefix: deleting successive largest
labels recovers every gap. It is disjoint from any family requiring every
valley after the first to be adjacent.

There are a prefixes for a=2,3 and a+1 prefixes for a>=4, independently of b.
Let C(a,b) count their completions by **b** more mountain creases. Then:

| Mountain length | b=2 | b>=3 |
|---|---:|---:|
| a=2 | 5 | 2b+3 |
| a=3 | 9 | 3b+6 |
| a>=4 | 2a+5 | (a+1)b+a+7 |

In particular C(2,2)=5, C(3,3)=15, and C(k,k)=k²+2k+7 for k>=4.
The equally natural family with its first non-adjacent valley at step
3 or later is **empty**, as proved next. This rules out a proposed avenue
of enlargement rather than filling it with fitted counts.

## Two local facts

For an old arc u--v on the new crease's side, a proposed new endpoint and
the current endpoint must have the same membership in its open interval.
Otherwise exactly one lies inside and the arcs interleave. The direction
condition together with these memberships is sufficient as well as necessary.
No old arc on this side shares the current endpoint. This proves the gap
test used below and in the sweep program.

**Adjacent same-symbol trapping.** Suppose the last crease is S (M or V)
and the next S insertion is adjacent. Reflect coordinates so the preceding
edge goes from u on the left to v on the right. The new endpoint w goes
left from v, hence u<w<v and w,v are adjacent. The following S edge goes
right from w on the same half-plane as u--v. Membership forces its endpoint
inside (u,v); direction and adjacency leave only (w,v). Applying the same
argument to the next two edges proves that every later S insertion is
forced and adjacent. In a valley run, choosing the second valley adjacent
therefore precludes a first non-adjacent valley at any later step.

**Collar removal.** Suppose a legal prefix P ends in a valley and its last
two faces A,B are adjacent. Let T(P) append an adjacent valley C. If F(P,r)
counts completions by r mountains, then, for r>=1,

    F(T(P),r+1) = 1 + F(P,r).

Here is the deletion and its inverse, included so the result does not depend
on accepting the earlier note's version of this lemma. Normalize P to local
order B,A. T(P) has B,C,A. The first mountain D must go in (C,A): it points
right from C and must stay inside A--B. The second mountain E points left.
It either goes in (C,D), after which the trapping fact forces the rest, or
goes to the left of B. The interval B--C forbids its intervening gap.

In the latter case delete C,D and lower every subsequent label by two.
The arc D--E becomes B--E. The block B,C,D stays consecutive: a future
rightward edge entering from its left crosses A--B, and from its right
points away; a future leftward edge entering from its right crosses B--C
or D--E, and from its left points away. These statements induct on the
next edge, so apply to every later insertion, not just the next one.
Outside the block, B--E and D--E have identical interval membership; the
removed short arcs contain no other endpoints. All remaining tests agree.

Conversely, in a completion of P, insert C,D immediately after B toward A,
in that order, and raise all subsequent labels by two. Its first mountain
goes left of B, exactly the second case above. The same non-entry argument
preserves the block. Orientations and half-planes survive the even label
shift. These constructions are inverse on labeled orders. The first case
is one additional completion, proving the identity.

For every member of D(a,b) with b>=3 the last valley is adjacent. Appending
an adjacent valley and a final mountain thus adds exactly one completion
per prefix. It remains to classify the prefixes and count at b=2 and b=3.

## All second-valley placements

The mountain-only classification has one exterior spiral, and one order
for each first inward step t=2,...,a. Before t each largest face is placed
exteriorly; at t it is placed adjacent toward the previous faces, after
which the trapping fact forces every later mountain. Deleting largest
labels gives the inverse. This is also the one-block argument in
[the paper, Theorem 2.1](https://dmtcs.episciences.org/en/articles/15454/download).

Normalize coordinates so the last mountain points right (reflect when a
is odd); this is a proof coordinate change, not a quotient of stack orders.
Write w=a-1, v=a-2, u=a-3. Let Xj=a+j be valley labels. The relevant
mountain orders and resulting three-valley prefixes are as follows.
Unshown faces retain their mountain order.

| Mountain type | Mountain order | Prefix after three valleys |
|---|---|---|
| Exterior | w,R,a | X2,X3,w,R,a,X1 |
| Deep: t<=a-2 | ...,u,w,a,v,... | ...,u,X2,X3,w,a,X1,v,... |
| Last: t=a | w,a,R,v | X2,X3,w,a,X1,R,v |
| Penultimate near: t=a-1 | u,R,w,a,v | u,R,X2,X3,w,a,X1,v |
| Penultimate far: t=a-1 | u,R,w,a,v | u,X2,X3,R,w,a,X1,v |

In each row X1 is adjacent to a, and X2 is non-adjacent to X1.
For the penultimate rows R consists of labels 0,...,a-4, in exterior-spiral
order. If R is nonempty, call its first and last faces L,H. For a=3 it is
empty: near and far coincide, and use H=u in the near row. For a=2 there
is no penultimate type; there are just exterior and last. The last row's R
in the last-step type instead contains 0,...,a-3; it is empty when a=2.

Why are there no other X2 gaps? Its direction is left; its half-plane is
that of the last mountain arc w--a. For the exterior order that arc spans
the old stack, so the only alternative to the adjacent gap is beyond w.
In the last-step order it is short, but all old faces are to its right:
again the only non-adjacent alternative is beyond w. In the deep order,
u--v encloses X1 while w--a does not; the matching left-hand region is
exactly (u,w). In the penultimate order u--v encloses X1, w--a excludes it,
and the same-side outer arc of R covers its entire interior. The two
remaining gaps are (u,L) and (H,w). For singleton R these are distinct;
for empty R they are the single gap (u,w). These observations also prove
that each listed placement is legal. Adjacent later valleys are legal
because no intervening old endpoint changes any interval membership.

Thus for a>=4 there are a-3 deep prefixes, one exterior, one last, and two
penultimate prefixes: a+1 altogether. The stated smaller counts follow.

## Exact base gap trees

These tables provide the finite arithmetic in the proof. They are symbolic
in a and t, not samples from the census. Let Z1,Z2,Z3 be the final mountain
labels, and let (x,y) denote the current adjacent gap between x and y.
The bounds -inf and +inf denote exterior gaps. Each row describes all its
branches; a vertical bar separates alternatives at the same step.

For b=3, the prefixes are those displayed above:

| Type | Z1 gap | Z2 gap | Z3 gap(s) |
|---|---|---|---|
| Deep | (X3,w) | (u,X2) | (Z2,X2) or (X1,v) |
| Deep | (X3,w) | (X3,Z1) | (Z2,Z1) |
| Deep | (a,X1) | (a,Z1) | (Z2,Z1) |
| Exterior | (X3,w) | (-inf,X2) | (Z2,X2) or (X1,+inf) |
| Exterior | (X3,w) | (X3,Z1) | (Z2,Z1) |
| Exterior | (a,X1) | (a,Z1) | (Z2,Z1) |
| Last | (X3,w) | (-inf,X2) | (Z2,X2), (X1,first R), or (v,+inf) |
| Last | (X3,w) | (X3,Z1) | (Z2,Z1) |
| Last | (a,X1) | (a,Z1) | (Z2,Z1) |
| Near | (X3,w) | (-inf,u) | (Z2,u) or (v,+inf) |
| Near | (X3,w) | (H,X2) | (Z2,X2) or (X1,v) |
| Near | (X3,w) | (X3,Z1) | (Z2,Z1) |
| Near | (a,X1) | (a,Z1) | (Z2,Z1) |
| Far | (X3,L) | (u,X2) | (Z2,X2) or (X1,v) |
| Far | (X3,L) | (X3,Z1) | (Z2,Z1) |
| Far | (H,w) | (-inf,u) | (Z2,u) or (v,+inf) |
| Far | (H,w) | (H,Z1) | (Z2,Z1) |
| Far | (a,X1) | (a,Z1) | (Z2,Z1) |

For the last type with empty R, read (X1,first R) as (X1,v).
The totals are deep 4, exterior 4, last 5, near 6, far 7.

For b=2, remove X3 from each prefix; the complete two-step trees are:

| Type | Z1 gap | Z2 gap(s) |
|---|---|---|
| Deep | (u,X2) | (Z1,X2) or (X1,v) |
| Exterior | (-inf,X2) | (Z1,X2) or (X1,+inf) |
| Last | (-inf,X2) | (Z1,X2), (X1,first R), or (v,+inf) |
| Near | (-inf,u) | (Z1,u) or (v,+inf) |
| Near | (H,X2) | (Z1,X2) or (X1,v) |
| Far | (u,X2) | (Z1,X2) or (X1,v) |

These give 2,2,3,4,2 respectively, with the same empty-R conventions.

To verify exhaustiveness of the tables, use interval membership, with the
two sides named A (parity a-1) and B (parity a). For the deep type the
relevant old A intervals are u--v and w--a; old B intervals are v--w and
(a-4)--u. The latter encloses the displayed local block. They exclude
every remote gap. In the exterior type A's w--a spans R; in the last type
the A interval spanning R is its exterior edge and B's v--w spans the old
stack. In the penultimate types the relevant A intervals are u--v, w--a,
and L--H (omit when R has fewer than two faces); B includes H--u and v--w.
All other old arcs nest within R, enclose the deep block, or are disjoint
from it. They cannot
split any listed gap, and the listed outer intervals already exclude
their interiors wherever a candidate could enter R.

Add the V intervals a--X1 on B, X1--X2 on A, and X2--X3 on B (b=3).
At each row add the preceding Z arc, flip side and direction, and retain
only gaps with the endpoint's membership vector. For example, deep Z1
lies inside u--v and X2--X1 but outside w--a; this leaves (X3,w) and
(a,X1). After the first choice, B allows (u,X2) and (X3,Z1); after the
second it allows only (a,Z1). This gives its three rows, including both
branches of the first row. The same interval lists give all other rows.
An internal R gap is rejected by its spanning interval before its smaller
nested arcs need inspection. This establishes the tables for arbitrary
mountain length, including both parities.

## Sum and limitations

Collar removal extends each b=3 row by one per extra valley/mountain pair.
Deep and exterior contribute b+1 each, last b+2, near b+3, far b+4.
For a>=4 the sum is

    (a-2)(b+1) + (b+2) + (b+3) + (b+4) = (a+1)b+a+7.

For a=3 omit deep and far: (b+1)+(b+2)+(b+3)=3b+6.
For a=2 keep exterior and last: 2b+3. At b=2 use its table separately.
Every sum is disjoint by the recovered mountain order and the second
valley's gap. Collar deletion is bijective, so it introduces no overlap.

Two failed shortcuts are retained: treating near and far as always
distinct predicts 22 at a=b=3, but the exact family has 15; starting the
collar recurrence at b=2 is invalid because the last valley is non-adjacent.
For instance a=4 has 13 completions at b=2, but 26 at b=3, not 13+5=18.
The order `1 4 3 2 6 5 0` is the a=b=3 merged prefix and has six completions.

Recorded run on 19 November 2026:

```
$ python3 projects/three-runs-of-stamps/delayed_escape.py --k 4
M^4 V^4 M^4; nonadjacent V at step 2
5 prefixes; 31 completions
by first internal mountain step: {2: 5, 4: 6, None: 5, 3: 15}
author formula: 31 (see delayed-escape.md; independent review pending)
```

The ten tests pass: full permutation controls through six faces, the
complete seven-face universe restricted by insertion history, local
trapping on all short legal prefixes, every delayed step 3 or later over
a=2..8/b=3..9, symbolic-class base counts for a=2..12, actual collar
deletion images, every symbolic three-step gap tree through a=12 (both
parities), unequal a,b=2..10, failed shortcuts, and the native CLI.
These are finite checks supporting the proof, not a substitute for it.

Next: independently reconstruct the symbolic gap trees and collar inverse
before any milestone verdict. Beyond this family, allow a second
non-adjacent valley after the step-two escape, or delay the first adjacent
valley itself. The trapping lemma restricts where choices can continue;
it does not make the one-escape families exhaustive. The general cubic,
and the unresolved prior-art comparison in the earlier README, remain open.
