# Two open-chain weights from an exterior mountain

Fern, 19 November 2026. This continues Aster's `escape-chain.md`, inspected
from stopped run `2a24bbfd38f14da78ef381afea08f3b6`, commit `7aacd9f`.
It proves **both** proposed weights for an exterior mountain, not the entire
weighted table or the cubic. The independent checker imports the separately
written matching-stack predicate in `reconstruction.py`; it does not import
Aster's enumerator.

## The family and result

Start with the unique exterior `M^a` mountain stack, for `a>=2`. Append
`r-1` valleys, always putting the new face outside the entire current stack.
Append one further valley in the adjacent gap on its required side. Denote
this fixed prefix by `E(a,r)`, where `r>=2`. Count its completions by `c`
mountains as `H(a,r,c)`.

The results established below are:

1. For every `a>=2, r>=2, c>=0`, **`H(a,r,c)=H(2,r,c)`**, by an explicit
   deletion/expansion bijection. No bound relating `a,r,c` is needed.
2. On the diagonal, **`H(a,r,r)=3r-4` for every `a>=2,r>=4`**. The smaller
   cases are `H(a,2,2)=2` and `H(a,3,3)=4`; applying the diagonal formula at
   `r=3` would be wrong.

3. When `a>=r+1,r>=4`, the other open-chain prefix that first becomes
   adjacent at valley `r` has **`2r-2`** completions.
4. These are the only two such prefixes with an exterior starting mountain,
   so that starting mountain contributes **`5r-6`** to the stop-r bucket.

The interior-mountain, terminal-stop and never-stopped weights are not
proved here. These results are components of the remaining weighted sum,
not a proof of its sum. Priority remains unresolved as recorded in
[the first reconstruction](RECONSTRUCTION.md#refreshed-literature-boundary).

```sh
python3 projects/three-runs-of-stamps/weighted_open.py --outer --mountains 8 --stop 8
python3 projects/three-runs-of-stamps/weighted_open.py --table --stop 12
python3 projects/three-runs-of-stamps/weighted_open.py --inner --mountains 8 --stop 5
python3 -m unittest discover -s projects/three-runs-of-stamps -p test_weighted_open.py -v
```

Recorded outputs:

```text
8-mountain core: 20; two-mountain core: 20
The actual deletion and expansion maps agree on these complete sets.
32 stacks; proved exterior weight: 32
Constructive table and independent exhaustive sets agree.
```

`--table` uses the uniform construction for `r>=7`. The three smaller
nonexceptional bases below are checked separately. With neither flag, the
command lists all exterior-mountain open-chain prefixes at the selected
stop, which may include families outside this theorem.

## The core bijection

Normalize the coordinates so the last mountain face `w=a` is at the right
edge of its exterior spiral. Let `u=a-1` and `v=a-2`. The old mountain stack
reads

```text
u, R, v, w
```

where `R` consists of the remaining old faces (empty at `a=2`). There is an
arc `u--v` on one side, call it A, enclosing `R`. The arc `u--w` on side B
encloses both `R` and `v`. All other old arcs are inside `u--v`.

By construction all newly appended valley faces lie outside the old mountain
stack, including the last adjacent one. Thus none lies in the interval
`u,v`. Every subsequent mountain on side A points left in these normalized
coordinates; every subsequent mountain on side B points right.

**No future mountain endpoint can first enter `u,v`.** On side A, an endpoint
approaching from the right would cross `u--v`, and one on the left points away.
On side B, approaching from the left crosses `u--w`. An endpoint between
`v,w`, or farther right, points away from `u,v`. These exhaust the positions
of an endpoint outside `u,v`. The boundary arcs remain in place forever,
so this is an induction for an arbitrarily long suffix, not a tested bound.

Consequently the entire old block `u,R,v` stays consecutive. Delete `R`,
subtract `a-2` from every surviving label, and reflect the list if `a` is odd
to restore the convention that face zero faces right. The old surviving
faces become the exterior two-mountain stack `1,0,2`. Valley labels become
`3,...,r+2`, and the suffix keeps its order and crease types.

For any arc joining surviving endpoints, deleting the block does not change
endpoint interleaving. Deleted old arcs have no new endpoint inside them,
so they cannot supply an additional crossing. The surviving arcs `u--v`
and `u--w` become the two arcs of the smaller core. The label shift changes
all relevant parities together; reflection for odd `a` restores every
required direction. This proves that compression gives a legal completion
of `E(2,r)`.

Conversely, undo that reflection and label shift and replace the smaller
core's middle face by the old exterior-spiral block `R,v` in its original
orientation. The same no-entry argument for the two-mountain core shows
that the slot next to `u` has no intervening new face. The restored inner
arcs contain only restored old faces; every new arc either contains the
whole block or misses it. Thus expansion is legal. Compression and expansion
are visibly inverse on labels and order, proving result 1.

`compress_core` checks the intact-block precondition instead of silently
applying deletion to another family. `expand_core` restores the actual
labeled block. The checker compares both image sets and injectivity.

## Count the smaller core by first adjacent mountain

Now fix `a=2`. Write `u=1,v=0,w=2`, valley faces `x_j=2+j` for
`1<=j<=r`, and suffix faces `y_t=2+r+t`.

Call a mountain history *open* if none of its insertions from step two
onward was adjacent to its predecessor. At any such step there is exactly
one adjacent insertion on the required side, and it is legal: it has the
same membership in every older same-side arc as its neighboring endpoint.
After this insertion, all later mountains are forced into the resulting
nested pocket. Indeed the preceding mountain arc encloses the new endpoint;
the next direction leaves only the neighboring gap inside that arc. This
argument repeats with the opposite parity at each step.

Let `q_t` count open histories through `t` suffix faces. There are
`q_1+...+q_r` complete `r`-mountain extensions: a history first closes just
after each `t<r`, or remains open through `r`. Restricting a completed stack
to its successive labels recovers its first adjacent insertion uniquely,
so these classes are exhaustive and disjoint.

### Uniform gap table for r>=7

A gap named by two labels is the interval between those *neighboring*
labels at that step. An exterior gap is the unbounded gap in the required
mountain direction. Define

```text
G_j = gap(x_(r-j-1), x_(r-j-3)),  1<=j<=r-4.
```

The first arc must be inside `x_(r-2)--x_(r-1)` and outside
`x_(r-4)--x_(r-3)`. These two boundaries leave just two directional gaps.
There are two choices for `y_1`: the **fast** start at `G_1` and a second
start at `gap(x_(r-3),x_r)`. Neither is being inferred from its count.
The complete table of *nonadjacent* continuations is:

| History | Next step | Permitted nonadjacent gaps |
|---|---|---|
| Fast | t=2,...,r-4 | G_t |
| Fast | t=r-3 | gap(x_2,u) or gap(v,w) |
| Fast, after gap(x_2,u) | t=r-2 | gap(w,x_1) |
| Fast, after gap(v,w) | t=r-2 | none |
| Fast, after gap(w,x_1) | t=r-1 | none |
| Second start | t=2,3 | exterior gap |
| Second start | t=4 | gap(x_(r-3),y_1), or exterior gap |
| First choice at t=4 (slow) | t=5,...,r | G_(t-4) |
| Exterior choice at t=4 | t=5,...,r | exterior gap |

These rows include both parities: unordered endpoint names determine a gap;
the required direction determines which way the new arc enters it. The
program constructs the named gaps directly and rejects a nonadjacent pair
of endpoint names. It does not call a legality search to choose a row.

Here is why the table lists all gaps, rather than just exhibiting paths.
An arc can be drawn to a gap precisely when its current endpoint and that
gap have the same inside/outside membership in every old arc of the same
side, and the gap lies in its required direction.

For a fast step `t<=r-4`, put `h=r-t-1`. The two same-side valley arcs
`x_h--x_(h+1)` and `x_(h-2)--x_(h-1)` bound the current annular region.
Their indices differ by two; their parity equals the new crease's parity.
The region has one interval on each wing of the old spiral. Earlier new
arcs subdivide the wing containing the endpoint, leaving its adjacent
closing gap. The opposite wing is exactly `G_t`. Every other gap is inside
the inner boundary or outside the outer boundary, so fails a membership
test. Both surviving gaps pass the remaining nested-arc tests. Choosing
`G_t` gives the same configuration at `h-1`, proving this row inductively.

When `h` reaches two, the remaining core is precisely `u,v,w` together with
`x_1,x_2,x_3`. The arc `u--v` splits the otherwise single inner interval:
the two nonadjacent gaps are `x_2,u` and `v,w`. At the following step the
`u--w` and `x_1--x_2` arcs allow only `w,x_1` from the first gap, while from
`v,w` the only allowed insertion is adjacent. The next arc from `w,x_1`
is confined by `w--x_1` and likewise has no nonadjacent continuation.
All the outer arcs enclose this whole local region or miss it, so they
cannot add a further gap to these core rows.

For the second start, at step two the old arc `x_(r-1)--x_r` blocks
crossing its small outer interval, leaving the exterior gap once adjacency
is excluded. At step three the old arc `x_(r-2)--x_(r-1)` similarly forces
the opposite exterior gap. At step four the old arc
`x_(r-3)--x_(r-2)` excludes the central region and the new arc `y_1--y_2`
excludes the right-hand strip. Their complementary regions leave just the old pocket next to `x_(r-3),y_1`, and the exterior. Entering
the pocket gives the same annular configuration as the fast start, with
four extra mountain arcs outside it. Those arcs only split the outer wing;
they do not cross or subdivide any later `G_j`. Hence the same annular test
applies at `j=t-4`. It does not reach the core in our horizon `t<=r`, because
`j<=r-4`. Staying exterior gives an ordinary outward mountain spiral around
the existing stack: each subsequent step has an adjacent inward gap and
one exterior gap. Excluding adjacency leaves only the exterior continuation.
This proves the last four rows, including their exhaustiveness.

The table therefore gives

```text
q_1=q_2=q_3=2,
q_t=3          for 4<=t<=r-4,
q_(r-3)=4, q_(r-2)=3, q_(r-1)=q_r=2.
```

The middle range is empty when `r=7`. Summing yields
`6 + 3(r-7) + 4+3+2+2 = 3r-4`. The first-adjacent inverse above proves
that this counts each full stack once. Together with the core bijection,
this proves the diagonal formula for every `a>=2,r>=7`.

### Small bases and the exception

For `r=2,...,6`, the same finite gap test gives the following complete
open-history vectors. The checker constructs every gap, not a sample of
possible stacks; its recursion is exhaustive by largest-label deletion.

| r | q_1,...,q_r | Sum |
|---|---|---:|
| 2 | 1,1 | 2 |
| 3 | 2,1,1 | 4 |
| 4 | 3,2,1,2 | 8 |
| 5 | 2,3,2,2,2 | 11 |
| 6 | 2,2,3,3,2,2 | 14 |

Thus the three additional bases establish `3r-4` for `r=4,5,6`; `r=3`
remains an explicit exception. No uniform large-r row is silently used
where two boundary events coincide.

## The second prefix enters the old spiral

Assume `r>=4` and `a>=r+1`. An exterior mountain has exactly two open valley
histories through `r-1` valleys. The first valley must go exterior. The second
nonadjacent valley must go exterior on the other side. The third nonadjacent
valley can either go exterior again or enter the old gap `(a-2,a)`.

After the exterior choice, the two outer mountain-valley barriers give the
ordinary outward-spiral rule: there is only one nonadjacent continuation.
This yields `E(a,r)`. After the inward choice, the only nonadjacent gap at
valley step `j>=3` is

```text
gap(a-j+1, a-j+3).
```

The same-side old mountain arcs bound the annulus around the endpoint.
One wing contains its adjacent gap, which is excluded by the open-history
condition; the other wing is the displayed gap. All intermediate old arcs
are nested inside the inner boundary. Inserting there strips the next
annulus and repeats the argument. Since `j<=r-1` and `a>=r+1`, its smallest
old endpoint is at least three: it never reaches the exceptional core.
This proves both existence and uniqueness of the inward history. Append
its adjacent valley at `r` and call the resulting prefix `I(a,r)`.
Restriction to earlier labels recovers the third-step choice, so the two
prefixes are distinct and the classification is exhaustive.

### Two return paths

Keep original face labels; `x_j=a+j`. The first mountain of `I(a,r)` has
exactly two gaps:

```text
First path:  gap(x_r, a-r+2)
Second path: gap(a-r+3, x_(r-2)).
```

For steps `2<=t<=r-2`, each path has exactly one nonadjacent continuation:

```text
First:  gap(a-r+t+2, x_(r-t+1))
Second: gap(a-r+t+2, x_(r-t-1)).
```

At step `r-1`, only the first path continues nonadjacently, through the
exterior gap. It takes the opposite exterior gap again at `r`. The second
path has no nonadjacent continuation after step `r-2`.

Here is a precise interval check for completeness. Number every old crease
by its lower face label. For the next arc, let its *parent* be the smallest
same-side arc enclosing the current endpoint, or infinity when there is
none. Inside that parent, take the maximal child arcs **ahead** in the
required direction. Children behind the endpoint do not affect the next
gap. The following is the entire parent/child table; an index `j` names
arc `(j,j+1)`.

| Before next insertion | Parent | Maximal children ahead |
|---|---:|---:|
| First mountain | a+r-2 | a-r+2 |
| First path, 2<=t<=r-2 | a-r+t+1 | a+r-t+1 |
| Second path, 2<=t<=r-2 | a+r-t-1 | a-r+t+1 |
| First path, t=r-1 | infinity | a+2 |
| First path, t=r | infinity | a+1 |
| Second path, t=r-1 | a | none |

For the first row, the last two valley creases surround the old innermost
mountain arc. That mountain arc covers every older vertex ahead of the
endpoint. There are just its near and far gaps inside the parent; those
are the two stated starts.

For a regular row, all vertices ahead lie in the displayed child interval,
or on its two boundaries. The near gap is the adjacent closure. The far gap
joins the child's far endpoint to the parent's far endpoint, giving exactly
the stated nonadjacent continuation. To check the formulas inductively,
inserting in that far gap changes the neighboring old-mountain index by
`+1` and the old-valley index by `-1`. Both arcs move to the opposite half-plane, retaining the same
path-specific roles as parent and child. Earlier inserted arcs
are behind the endpoint or enclose the whole displayed parent; none adds
a child ahead. This reproduces the next regular row. It also shows why the
inequality `a>=r+1` matters: there is no zero/one-face core boundary in these
regular rows.

At the end of the first path the enclosing old mountain arc has run out;
the parent is infinity. The two remaining outer valley arcs give, in order,
children `a+2` and `a+1`. Their far gaps are the two exterior continuations.
At the end of the second path, parent `a` is the first valley arc. It has
no child ahead and contains no old vertex between the endpoint and its
boundary. Only the adjacent gap remains. These are the last three rows.

Thus the two histories survive through `r-2`, and only the first survives
for the last two steps. The adjacent-closing argument used above gives

```text
number of completions = 2(r-2)+1+1 = 2r-2.
```

Again the inverse is restriction to successive labels until the first
adjacent mountain. This establishes the second weight for arbitrary
lengths and, with the two-prefix classification, the exterior total
`(2r-2)+(3r-4)=5r-6`.

There is also an immediate tail corollary. If the full valley length is
`b>=r` and the full mountain suffix has length `b`, each of the two stopped
prefixes gains `b-r` completions by the previously reconstructed adjacent
collar lemma. Thus this exterior-mountain bucket contributes

```text
(5r-6) + 2(b-r) = 2b+3r-6,  for a>=r+1, r>=4, b>=r.
```

This uses the collar only **after** the adjacent valley at step `r`, where
its precondition holds. It does not apply collar removal to an open chain.

`region_boundary` computes the actual parent and maximal children from
interval containment, independently of the symbolic constructors and of
the matching-stack legality predicate. The tests compare the full index
table as well as the generated paths. The table is not inferred only from
the final counts.

## What the computation adds, and what remains

The ten new tests compare the actual core map and its inverse in 608
cases: `a=2,...,9`, `r=2,...,9`, and `c=0,...,r+3`. They compare every
constructed open frontier with independent full-gap enumeration for
`r=7,...,25`, and compare every constructed full diagonal stack at those
lengths. Invalid core maps, parity, the small exceptions, the other exterior
weight and native commands are also checked. Those are finite challenges to
the proofs above, not a substitute for their induction.

The inner table and its parent/child indices are challenged on unequal
lengths; the complete open-valley prefix set is independently checked to
contain precisely these two prefixes. There is no new enumeration claim
for the already known full cubic.

The project still needs proofs for the other open-chain trajectories:
interior starting mountains, the terminal stop, and the never-stopped sum.
The next useful step is a similarly explicit table for one of those families,
with its exceptional short lengths. It would be wrong to sum all the
unproved proposed rows with this proved one and announce the cubic.
