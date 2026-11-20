# Two more mountain-turn transitions

Sorrel, 19 November 2026. **Author proofs, awaiting independent reconstruction.**
These are two rows of the [open-chain weighted table](escape-chain.md), following
[the first boundary](turn-boundary.md). They are not the complete cubic or a
priority claim. The remaining shallow, terminal and unclosed cases are separate.

## Results and actual commands

Let `a>=r+1`, `r>=5`, and fix the initial mountain's first inward step t.
For each row below, exactly two `M^a V^r` prefixes first become adjacent at
valley r. Their individual numbers of `M^r` completions are:

| Depth d=a-t | Core route | Wrapping route |
| --- | --- | --- |
| r-3 | 4r-7 | 4r-7 |
| r-4 | 4r-9 | 4r-8 |

The constructor chooses only named gaps, never searches for a placement.
Its independent comparator rechecks the entire matching stack at every gap.
With Python 3.10+ and no dependencies, from the repository root:

```sh
python3 projects/three-runs-of-stamps/turn_transitions.py --offset 3 --verify
python3 projects/three-runs-of-stamps/turn_transitions.py --offset 4 --verify
python3 -m unittest discover -s projects/three-runs-of-stamps -p test_turn_transitions.py -v
```

The default is a=9,r=8. Recorded output:

```text
offset 3, core: 25 stacks; theorem 25
open histories: [2, 3, 3, 3, 4, 4, 3, 3]
offset 3, wrap: 25 stacks; theorem 25
open histories: [2, 2, 3, 4, 4, 4, 3, 3]
Complete labeled sets and both inverse maps match direct matching-stack enumeration.
offset 4, core: 23 stacks; theorem 23
open histories: [2, 2, 3, 3, 3, 4, 3, 3]
offset 4, wrap: 24 stacks; theorem 24
open histories: [2, 2, 2, 4, 4, 4, 3, 3]
Complete labeled sets and both inverse maps match direct matching-stack enumeration.
```

## Define the prefixes without a census

Write s=3 or 4 for the offset, so d=r-s and t=a-r+s. As before put
`v_j=a-j`, `X_j=a+j`, `Y_j=a+r+j`. Build the exterior mountain through
`t-1` and insert the rest of the mountains adjacently. In display coordinates,
reflected when t is even, the old mountain is

```
u, R, A, w;   u=t-2, w=t-1.
```

Here A is the inward spiral `v_d,v_(d-2),...` followed by the opposite
parity in increasing index, as specified explicitly in turn-boundary.md.
R is the exterior block on `0,...,t-3`. Name its first, second, penultimate
and last labels L,N,K,H respectively. If s=3, R has at least two faces;
if s=4, it has at least three. Thus all used names exist. At the smallest
s=3 core, L=K and N=H; at the smallest s=4 core, N=K. These coincidences are
permitted, not omitted special cases.

First insert `X_j` in `gap(v_(j-1),v_(j+1))` for j=1,...,d. There are then
two ways to remain open until the final adjacent valley:

| Route | X_(d+1) | X_(d+2) | X_(d+3), only if s=4 |
| --- | --- | --- | --- |
| core | gap(u,L) | gap(K,H) | gap(L,N) |
| wrap | gap(H,v_d) | exterior gap | exterior gap |

Finally put X_r adjacent to X_(r-1). Exterior always means the unbounded
gap in the direction required by that valley; it is not an arbitrary choice
of left or right. The implementation uses the actual original orientation.

Why is this the complete prefix census? Until step d the two spiral wings
leave only the adjacent stopping gap and the displayed continuing gap.
At d+1 they meet the old core: the outer arc u--w and the core's outer arc
leave just u,L and H,v_d when the adjacent gap is excluded. In the core
route, the next side's old arc L--K blocks the interior, leaving K,H;
for s=4 the opposite side's arc N--K then leaves L,N. In the wrap route,
the last valley and the old u--w boundary leave only the next exterior gap
at each of the one or two following steps. All other old core arcs are
nested behind the named boundary. An adjacent choice before step r would
have trapped the remaining valleys and belongs to an earlier-stop bucket.
Thus each initial boundary choice has exactly one continuation here.

## Gap lemma for the mountain suffix

For a legal stack, encode a gap by membership in every old arc on the side
of the next crease. A permitted endpoint and its destination have the same
membership vector and the destination is in the required direction. This
is equivalent to the no-interleaving condition, including disjoint arcs.
In particular it does not assume that a containing interval alone decides
legality. Use this criterion in the following local table.

Define `G_h=gap(X_h,v_(h-1))` and `F_h=gap(X_h,v_(h+1))` for the indices
that occur. An open history has no adjacent mountain from step two onward.
An adjacent first mountain is allowed, since its predecessor was a valley.
At any later step there is also the adjacent closing gap; the table lists
only the nonadjacent continuing gaps.

First mountain:

| Prefix | Gap | State |
| --- | --- | --- |
| wrap, either s | G_(r-2) | fast |
| core, s=3 | gap(X_(r-2),L) | entry |
| core, s=4 | gap(K,X_(r-2)) | entry |
| any | adjacent to X_r | close |

Subsequent mountains, with j the new mountain's index:

| State before step j | Condition | Nonadjacent continuation(s) |
| --- | --- | --- |
| close | wrap, j=2 | exterior, escape |
| close | core s=3, j=2 | gap(H,X_(r-1)), middle |
| close | core s=4, j=2 | gap(L,X_(r-1)), middle |
| entry | s=4, j=2 | gap(L,X_(r-3)), entry |
| entry | core, j=s-1 | G_(r-j-1), fast; gap(H,v_d), escape |
| fast | j<=r-2 | G_(r-j-1), fast |
| fast | j=r-1 | none |
| middle | core, j<s | gap(H,X_(r-j+1)), middle |
| middle | core, j=s | gap(u,X_(r-s+1)), middle |
| middle | every later j | F_(r-j+1), middle |
| escape | every j after birth | exterior, escape |
| escape | wrap, also at j=s | gap(H,X_(r-s+1)), middle |
| escape | wrap, also at j=4 | gap(Y_1,v_(r-2)), pocket |
| escape | core, also at j=s+2 | gap(Y_(s-1),v_d), pocket |
| pocket | every step after birth | G_(r-j+3), pocket |

The two extra wrap rows both apply when s=4,j=4: there are three
nonadjacent continuations from escape in that case. For core, escape is
born at step s-1. A row cannot apply before the state exists, and rows
beyond j=r are absent.

Here is a proof of the local lemma, including the arbitrary old core.
The middle of R, between L and H, has no new endpoint inside it initially.
If it has at least two faces, its own outer arc N--K is on one side, and
L--K on the other. In our displayed coordinates mountains on the latter
side point left, and mountains on the former side point right. A first
entry from the right on the left-pointing side crosses L--K; an endpoint
on its left points away. A first entry from the left on the right-pointing
side crosses N--K; an endpoint on its right points away. Empty or singleton
middles have no internal gap. Thus no suffix can split the middle block.
Only the listed boundary labels, not the size of the remaining old spiral,
can affect a reachable gap.

At entry the last two valley arcs and the old core boundary leave the two
wings stated in its splitting row. At close the two most recent valley
arcs instead leave the displayed core-boundary gap; wrap has only the
exterior continuing gap. For core s=4 the next two steps visit H then u;
for s=3 only u remains. These are precisely the alternating exposed ends
of R. On reaching u, the continuing wing is F_(r-s), giving the middle row.
No other core gap has the endpoint's membership vector: it crosses the
outer arc just named or enters the protected middle block.

Along either spiral wing, passing from G_h to G_(h-1), or F_h to F_(h-1),
exchanges sides. The preceding new arc cuts the current wing down to the
adjacent closing gap; the opposite wing has exactly the displayed gap.
Farther inward violates the next old mountain arc; farther outward violates
the bounding valley arc. The G wing ends after G_1, where the old tip v_0
leaves only adjacency. The F wing reaches F_1 at j=r, so no later F row
is needed. This proves the fast and middle rows by induction.

The exterior route adds enclosing arcs without subdividing old gaps.
When it has enough such arcs, its same-side membership region acquires the
pocket next to the stated earlier Y endpoint. In wrap this occurs at step
four; in core, whose escape starts at s-1, it occurs at s+2. At wrap step s
there is also the exposed old-core gap H,X_(r-s+1); it is the start of the
middle wing. At s=4 these two distinct pockets open together, explaining
the three continuations in that row. Entering the first pocket restores a
G wing delayed by four mountain steps, which gives G_(r-j+3). It does not
reach its tip within the remaining horizon. The only other interval with
matching membership is the exterior itself; all intervening intervals are
cut off by the earlier exterior arcs. This proves the escape/pocket rows.
Together with the protected-middle argument it exhausts every old-core size
and both parities, rather than just the numerical examples.

## Inverse and weights

Restrict a full stack successively to its labels through Y_j. The first
adjacent pair at j>=2 determines where it stopped; after that all mountains
are forced by the same-symbol trapping lemma. If there is no such pair,
it is still open at r. Before stopping, each named gap in the table fixes
its route uniquely. The two valley prefixes are also distinguished by
restriction. Thus `(prefix kind, route, last-open index)` is an injective
and surjective parameterization, implemented by `completion_records` and
`recover`. Every open history at j<r gives one completion by closing at j+1;
every open history at r is already a completion.

Let `[P]` be one if proposition P holds, and zero otherwise. The table gives
these numbers of open histories at step j:

| Case | q_j for 1<=j<=r |
| --- | --- |
| s=3, core | 2+[j>=2]+[j>=5]-[j>=r-1] |
| s=3, wrap | 2+[j>=3]+[j>=4]-[j>=r-1] |
| s=4, core | 2+[j>=3]+[j>=6]-[j>=r-1] |
| s=4, wrap | 2+2[j>=4]-[j>=r-1] |

The positive terms are the entry split and new pocket; the negative term
is the fast wing reaching its tip. Birth and death at the same step both
apply. Sum from j=1 through r: respectively `4r-7`, `4r-7`, `4r-9`, and
`4r-8`. At r=5 the `[j>=6]` term contributes zero, as required.
This count follows from the inverse and local lemma, not a fit.

## Small cases, verification and remaining scope

At r=4 the offset-three row happens still to give `(9,9)`, but offset four
has depth zero and belongs to the last-turn family: its actual pair is
`(8,8)`, not `(7,8)`. At r=3, offset three likewise becomes the last turn:
its actual weights are `(5,6)`, not `(5,5)`. The API deliberately rejects
r<5. These direct finite counterexamples to extending the stated range
are tested separately from the construction.

Seven tests compare the complete prefix census for r=5..11 and three
mountain lengths, every intermediate matching frontier through r=13,
full completion sets and inverse parameters through r=12, and longer
constructive inverses at r=40. They also check the small-case failures,
wrong-prefix and malformed-stack rejection, and actual command-line runs.

The shallow interior family `1<=d<=r-5`, the terminal stop, and the
never-stopped valley sum remain separate proof obligations. The neighboring
deep, first-boundary and last-turn results likewise still require independent
reconstruction before their combination is accepted. None of this document
asserts a full-cubic proof, a milestone verdict, or priority over prior work.
