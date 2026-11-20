# The first boundary of an inward mountain turn

Sorrel, 19 November 2026. **Author result, awaiting independent review.**
This counts the `d=r-2` row of [the open-chain table](escape-chain.md),
separately from the deeper-turn work. It does not prove the full cubic or
settle priority. The model and literature limitations remain those in
[the project README](README.md) and [reconstruction](RECONSTRUCTION.md).

## Result and runnable check

Fix `a>=r+1`, and let the first inward mountain insertion be at
`t=a-r+2`; thus `d=a-t=r-2`. Among the `M^a V^r` prefixes whose first adjacent
valley after valley one is valley `r`, there are exactly two with this
mountain order. Call them **inside** and **outside**, as constructed below.
Their numbers of `M^r` completions are respectively

```
inside:  4r-5
outside: 4r-6.
```

The requested range is `r>=5`; the proof also covers `r=3,4`. The family
has a growing number of faces, two precisely specified prefixes for each
mountain length, and an explicit parameter for every completion. No count
or candidate placement in its constructor comes from a legality search.

From the repository root, Python 3.10+ with no third-party packages:

```sh
python3 projects/three-runs-of-stamps/turn_boundary.py --mountains 8 --stop 7 --verify
python3 -m unittest discover -s projects/three-runs-of-stamps -p test_turn_boundary.py -v
```

Recorded output:

```text
inside: 23 stacks; theorem 23
open histories: [3, 3, 3, 4, 4, 3, 3]
outside: 22 stacks; theorem 22
open histories: [2, 3, 3, 4, 4, 3, 3]
Both complete labeled sets and their inverses match direct matching-stack enumeration.
```

`--list` prints each `(route, index)` parameter and the actual labeled stack.
The comparison uses the separately written push/pop matching predicate in
`reconstruction.py`, checking a complete stack at each insertion. The
constructor uses only named gaps. Neither one consults the stated formula
to choose a stack.

## Coordinates and the two valley prefixes

Write `v_j=a-j`, `X_j=a+j`, and `Y_j=a+r+j`. A named gap is between two
neighboring labels, in either order. An adjacent insertion means the unique
gap next to the current endpoint in the direction required by the crease.

The mountain order is determined by `t`: extend the exterior mountain spiral
through face `t-1`, then insert every remaining mountain adjacently. Reflect
our *display coordinates* if `t` is even. The actual constructor retains the
original labeled orientation. In these coordinates the order has the form

```
u, R, A, w
u=t-2=v_r; w=t-1=v_(r-1)
A=(v_(r-2), v_(r-4), ..., then the opposite parity in increasing index)
```

More explicitly, if `n=r-2`, A first lists indices `n,n-2,...,n mod 2`,
then `1-(n mod 2),3-(n mod 2),...,n-1`. R is the nonempty old exterior
spiral block with labels `0,...,t-3`. Write L,H for its first and last labels.
For the minimal case `a=r+1`, `t=3`, R is the single face zero.

The two stopped valley prefixes are constructed as follows:

1. For `j=1,...,r-2`, insert `X_j` in `gap(v_(j-1),v_(j+1))`.
2. Insert `X_(r-1)` either in `gap(u,L)` (**inside**) or in
   `gap(H,v_(r-2))` (**outside**).
3. Insert `X_r` adjacently to `X_(r-1)`.

These names describe the position beside the old exterior core, not a
quotient by reflection. The two labeled stacks are distinct.

**Why these are all the prefixes.** Two same-symbol adjacent insertions
trap all further insertions of that symbol in the newly nested pocket.
Consequently a mountain order has one first inward step and is forced
thereafter. Until valley `r-2`, the old mountain arcs bound an annulus with
one gap on each wing. The first valley has only the displayed gap; at each
later step the gap on the endpoint's wing is the adjacent stopping gap and
the other is `gap(v_(j-1),v_(j+1))`. Selecting any earlier stopping gap
would not belong to this stop-r bucket.

At step `r-1`, the annulus reaches R. On this side the old arcs `u--w` and
`L--H` require the endpoint to remain inside the former and outside the
latter. In the required direction this leaves `u,L` and `H,v_(r-2)`, plus
the adjacent stopping gap. When R is a singleton there is no `L--H` arc,
but there is also no internal R gap. All other old arcs are nested inside
R or are the two wings already passed. This gives exactly the two
nonadjacent choices above. The adjacent step `r` is unique and legal.

## The old core can be removed for every suffix length

On one side, called A here, the old arc `u--H` encloses R except its last
endpoint H. On side B, when R has at least two faces, `L--H` encloses R.
In the displayed coordinates every new mountain on A points left and
on B points right. These facts give a useful no-entry argument:

- An A endpoint to the right of R cannot enter it without crossing `u--H`.
  An A endpoint to its left points away from R.
- A B endpoint to the left cannot enter R without crossing `L--H`.
  A B endpoint to its right points away from R.

There is no internal gap when R is a singleton. Both stopped prefixes have
no new face inside R; induction therefore keeps R consecutive for an
arbitrarily long mountain suffix, not just the diagonal of length r.

Put `delta=t-3`. Delete all labels less than delta, subtract delta from the
remaining labels, and reverse the order if t is even. R becomes face zero,
u becomes one, and w becomes two. This maps either prefix and any legal
mountain suffix to the same kind at `a'=r+1,t'=3`.

Deleting a consecutive block preserves interleaving of surviving arcs.
Every deleted arc lies inside R or ends at its boundary, so none could
be crossed by a new endpoint. The common parity shift and the indicated
reflection preserve the M/V directions. Conversely restore the exterior
spiral R in place of face zero and undo the reflection and shift. No new
endpoint lies within that replacement block, so every restored arc is
legal. The two maps are inverse. `compress_core` and `expand_core` implement
this actual labeled bijection, with an explicit intact-block check.

Thus it is enough to give the gap table with R a singleton. The same table
also works in the original larger stack; the no-entry argument rules out
hidden internal R gaps.

## Exhaustive mountain gap table

Define two wings of gaps, wherever their indices occur in the table:

```
G_h = gap(X_h, v_(h-1))
F_h = gap(X_h, v_(h+1)).
```

An *open history through j mountains* has no adjacent insertion at mountain
steps `2,...,j`. Adjacency at step one is allowed: the previous crease was
a valley, so it does not yet trap the mountain tail. Every later adjacent
choice closes the history and forces all remaining mountains adjacently.

The first mountain has these choices:

| Prefix | First gap | Route |
| --- | --- | --- |
| Either | G_(r-2) | fast |
| Either | adjacent to X_r | close |
| Inside only | gap(H,v_(r-2)) | escape |

At every later step the adjacent closing gap is legal. The following table
lists **all additional, nonadjacent gaps**. Empty entries mean none.

| Route before step j | j | Nonadjacent gap and resulting route |
| --- | --- | --- |
| fast | 2 through r-2 | G_(r-j-1), still fast |
| fast | r-1 | none |
| close, inside | 2 | gap(u,X_(r-1)), middle |
| close, outside | 2 | gap(H,X_(r-1)), middle; or exterior, escape |
| middle | 3 through r | F_(r-j+1), still middle |
| escape | 2,3 | exterior, still escape |
| escape | 4 | exterior, still escape; or gap(Y_1,v_(r-2)), pocket |
| escape | 5 through r | exterior, still escape |
| pocket | 5 through r | G_(r-j+3), still pocket |

For outside, escape is born at step two, so its step-two row is already
accounted for by close. For `r=3,4`, rows beyond the horizon are simply absent;
no overlapping events are silently added.

Here is an interval check of the table. For any fixed side, mark a gap by
the set of old arcs whose interiors contain it. A new arc is legal exactly
when its endpoint and destination gap have the same set, and the direction
is correct. This criterion also handles disjoint arcs; checking only the
nearest enclosing arc would not suffice.

In the fast and middle rows, the two old mountain wings and the alternating
valley arcs give two intervals with the endpoint's membership: its current
wing, cut down by the last new arc to the adjacent closing gap, and the
opposite wing. For fast that opposite wing is G_(h-1) after G_h; for middle
it is F_(h-1) after F_h. The change h to h-1 exchanges sides. Every gap
farther toward the tip crosses the next old mountain arc; every gap farther
toward R crosses the previous valley arc. Thus the named opposite gap and
the adjacent gap exhaust the possibilities. At G_1 the two wings meet at
the old tip v_0; there is no G_0 wing and only adjacency remains. Middle
reaches F_1 only at the last step, so no continuation there is asserted.

For close at step two, `X_(r-1)--X_r` and `X_(r-2)--X_(r-1)` leave the
core boundary gap displayed in the table. The outside prefix has an
additional interval outside the whole old stack, while the inside prefix's
old `u--w` boundary excludes it. For the initial inside escape, and the
outside escape born at step two, the next two exterior arcs enclose the
whole old stack. At step four, the arc `Y_1--Y_2` leaves precisely the pocket
next to `Y_1,v_(r-2)` and the exterior interval, besides adjacency. No gap
inside R is possible by the preceding lemma. Entering this pocket puts the
endpoint on the fast pair of wings, four steps later; hence at j=5 it
enters G_(r-2), and subsequently follows G_(r-j+3). Staying exterior keeps
one exterior gap at every subsequent step. The pocket cannot reach G_1
within the r-step horizon. These membership tests prove the table
inductively, including both parities and the exclusion of other gaps.

## Inverse and count

A full stack first determines its prefix by deleting labels greater than
a+r. Its first adjacent mountain step j>=2, if present, is recovered by
restricting the stack to labels through Y_j and inspecting those two
endpoints. Everything after that insertion is forced. Before it, the
unique gaps in the table recover the route. If there is no adjacent step,
use index r. Thus a completion has exactly one parameter `(route,index)`:
its open history through `index`, followed by forced adjacent mountains.
The prefixes, routes and parameters are not counted modulo symmetry.

For the inside prefix the number q_j of open histories through j is

```
q_j = 3 + [j>=4] - [j>=r-1],  1<=j<=r.
```

The outside prefix subtracts one more at j=1, and has the same q_j later.
There are initially fast, close and (inside only) escape. Close is replaced
by middle at step two, with an extra escape for outside. Escape gives birth
to pocket at step four; fast disappears at step r-1. These are precisely
the terms in q_j. When their indices coincide, both changes occur.

Each open history at j<r gives one full completion by first closing at j+1;
each open history at r already is a full completion. The inverse proves
that these are exhaustive and disjoint. Therefore

```
inside  = sum(q_j) = 3r + (r-3) - 2 = 4r-5
outside = inside - 1 = 4r-6.
```

This holds at r=3 as well: the vectors are `(3,2,2)` and `(2,2,2)`.
At r=4 they are `(3,3,2,3)` and `(2,3,2,3)`. We do not extend the construction
to r=2, where its first named gap would require X_0.

## Boundaries and what remains

The proof needs `a>=r+1` so that t>=3 and R is nonempty. It must not be
applied to the exterior mountain or to the last possible inward turn. Its
depth condition is exact, `d=r-2`. A direct independent-matching check one
step shallower, `d=r-3`, gives two weights `4r-7,4r-7` at r=5,6,7, rather
than either weight here. This failed extension is retained as a regression.

Nine tests check all stopped prefixes for r=3..10 and six mountain lengths
per r; every intermediate gap frontier for r=3..13 and three lengths;
complete-set equality and the parameter inverse for r=3..11; actual core
compression/expansion; larger constructions through r=50; the small-stop
vectors, neighboring-depth rejection and the native command. Additional
full matching-set comparisons at r=20,35 passed for three lengths each.
Finite checks support the proof; they do not replace its induction.

The next weighted rows are `d=r-3`, `d=r-4`, the shallow interior turns,
and the last turn, followed by the terminal-stop and never-stopped cases.
The deeper `d>=r-1` task has another owner. Do not infer any of these rows,
a milestone verdict, or the proposed full cubic from this result.
