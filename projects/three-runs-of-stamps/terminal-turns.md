# The three early turns at the terminal valley

Sorrel, 19 November 2026. **Author result, awaiting independent review.**
This is the terminal diagonal `M^k V^k M^k`, not the interior regime
`a>=r+1` of [the earlier transition tables](turn-transitions.md).
For `k>=5` and initial inward mountain turn `t=2,3,4`, there is exactly one
prefix whose first adjacent valley after valley one occurs at valley k.
Its number of k-mountain completions is

```
4k-t-4:  respectively 4k-6, 4k-7, 4k-8.
```

This settles only those three turns. Other terminal turns and the exterior
mountain are not being silently included in this count. The full cubic and
priority remain open as stated in the [project README](README.md).

From a clone, with standard-library Python 3.10+:

```sh
python3 projects/three-runs-of-stamps/terminal_turns.py --k 8 --verify
python3 -m unittest discover -s projects/three-runs-of-stamps -p test_terminal_turns.py -v
```

Recorded output:

```text
turn 2: 26 stacks; theorem 26
open histories: [2, 3, 3, 4, 4, 4, 3, 3]
turn 3: 25 stacks; theorem 25
open histories: [2, 2, 3, 4, 4, 4, 3, 3]
turn 4: 24 stacks; theorem 24
open histories: [2, 2, 2, 4, 4, 4, 3, 3]
All complete labeled sets and inverse parameters match direct matching-stack enumeration.
```

## The disappearing core choice

Set `v_j=k-j`, `X_j=k+j`, `Y_j=2k+j`, and `d=k-t`. Build the exterior
mountain through t-1 and then use adjacent mountain folds through k. The
three starting exterior cores in the fixed labeled orientation are
`(1,0)`, `(1,0,2)`, `(3,1,0,2)` respectively. In reflected display
coordinates for even t, write the completed mountain as

```
u,R,A,w; u=t-2, w=t-1.
```

A is the inward spiral. Unlike the interior cases, R now contains exactly
t-2 faces: zero, one or two. Let H be its last face when nonempty; for an
empty R define H=u. Thus H is respectively 0,0,1. The unique prefix is:

1. For `j=1,...,d`, insert X_j in `gap(v_(j-1),v_(j+1))`.
2. Insert X_(d+1) in `gap(H,v_d)`.
3. Make the following t-2 valleys exterior, in their required directions.
4. Insert X_k adjacently.

These operations total k valleys. They define actual labeled orders; the
reflection is for the explanation and never identifies distinct stacks.

The usual spiral annulus argument gives the unique open gap at each step
through d, apart from the adjacent stopping choice. At the old core, the
interior proof would offer both the gap before R and the gap after R.
When t=2, R is empty and the two sides collapse to the single gap u,v_d.
When t=3, the other route enters next to the singleton R but then has no
nonadjacent continuation. When t=4, that route has two old core faces: it
can cross their one gap, but the following valley has only the adjacent
continuation. In either case it stops before valley k. The surviving route
is the displayed gap after R followed by exterior valleys. Each of its
exterior steps has one continuing gap besides adjacency; choosing adjacency
early would again stop before k. This proves the singleton census.

For completeness, this exhaustion uses membership in all old same-side
intervals. The two arcs around the inward spiral exclude gaps deeper or
shallower than the current annulus. At R, the bounding old core arc either
has no interior gap (t=2,3) or exactly the one old gap (t=4). After crossing
that one gap, the preceding valley arc and direction exclude returning
across it. There is no unexamined longer old core in these three cases.
Deleting the final adjacent valley and then the larger labels recovers all
these choices in reverse, so the construction is injective as well.

## Uniform suffix table

Let `G_h=gap(X_h,v_(h-1))`, `F_h=gap(X_h,v_(h+1))`. Call a mountain history
open if steps two onward have all been nonadjacent. The first mountain may
be adjacent because its predecessor is a valley.

The first mountain goes either to G_(k-2) (**fast**) or to the adjacent gap
(**close**). At every subsequent step there is a legal adjacent closing
gap. All nonadjacent alternatives are:

| State | New step j | Continuing gap(s) |
| --- | --- | --- |
| fast | 2,...,k-2 | G_(k-j-1), fast |
| fast | k-1 | none |
| close | 2 | exterior, escape; also F_(k-1), middle, when t=2 |
| escape | every later step | exterior, escape |
| escape | also j=t, for t=3,4 | gap(H,X_(k-t+1)), middle |
| escape | also j=4 | gap(Y_1,v_(k-2)), pocket |
| middle | every step after its birth | F_(k-j+1), middle |
| pocket | every step after its birth | G_(k-j+3), pocket |

The t=2 middle is born directly from close at step two. At t=4, the two
extra escape alternatives occur together at step four. If the horizon
ends before a row, that row contributes nothing.

To prove exhaustiveness, give each gap the vector of old same-side arcs
containing it. A new endpoint can reach exactly the gaps with its vector
and required direction. For fast and middle, the older mountain and valley
arcs leave one matching interval on each spiral wing: the endpoint's wing,
cut down by its last new arc to adjacency, and the opposite G or F gap in
the table. Advancing that gap decreases its index by one and exchanges
sides. Fast reaches G_1 and cannot continue nonadjacently past the tip v_0;
middle reaches F_1 only at step k.

For close, the two most recent valley arcs leave the exterior interval.
With t=2 the empty core also exposes F_(k-1) immediately. With t=3 that
same F corridor is exposed by the next exterior arc; with t=4 one more
exterior arc is required. Their first accessible gaps are precisely
H,X_(k-t+1), after which the F induction applies. There are at most two
old core faces, so no other internal core interval remains to inspect.
At step four the successive new exterior arcs expose the interval next to
Y_1,v_(k-2), besides the exterior and, when t=4, the newly exposed middle
corridor. Entering that interval is the G induction four steps later,
with index k-j+3. Staying outside leaves the unique exterior continuation.
All other gaps cross one of these boundary arcs. This proves the local
identities by induction for arbitrary k, with no numerical bound on the
number of inward spiral faces.

## Inverse and count

For any completed labeled stack, delete labels above 2k to recover its
valley prefix. Restrict successively to labels through Y_j. The first
adjacent mountain at j>=2 determines its stopping index j-1; all remaining
mountains are forced adjacent by the same-symbol trapping lemma. If no
such j exists use index k. The table reconstructs its route uniquely.
Conversely each open route at index j<k produces exactly one completion
by closing at j+1 and nesting thereafter. At index k it is already complete.
`completion_records` and `recover` implement both directions.

Thus the completion count is the sum of open-frontier sizes q_j. The table
has two initial histories; the middle is born at t, the pocket at four,
and fast dies at k-1:

```
q_j = 2 + [j>=t] + [j>=4] - [j>=k-1],  1<=j<=k.
```

When events coincide, both apply. Summing yields
`2k+(k-t+1)+(k-3)-2 = 4k-t-4`, proving the stated result.

## Small cases, checks and the remaining terminal sum

The same finite gap table handles the existing early turns at k=3 and 4:

| k | turn 2 | turn 3 | turn 4 |
| --- | --- | --- | --- |
| 3 | 6 | 5 | unavailable |
| 4 | 10 | 9 | 8 |

Their frontier vectors are tested explicitly. At k=2, turn two has three
completions, not the extrapolated two; G_0 does not exist. The constructor
therefore requires k>=3 and turn<=k. The infinite proof above is stated
for the requested k>=5; the displayed smaller cases also have an exhaustive
matching-stack check.

Seven tests establish the singleton prefix census through k=13, compare
every intermediate frontier through k=15 with the separate full matching
predicate, compare entire completed sets and inverse parameters through
k=17, and exercise longer constructions at k=50, small collisions, invalid
inputs and the real command. These finite checks support the proof; they do
not prove an omitted terminal row.

These three early turns contribute `12k-21` for k>=5. If the remaining
terminal turns t=5,...,k are separately proved to have weights
`4k-2t` and `5k-2t-2`, and the exterior case has weights `2k-2,3k-4`, then
adding them gives `S(k,k)=7k²-23k+21`. That is a conditional arithmetic
reduction, not an assertion that those remaining prefixes or weights have
been proved here. The last-turn proof is separately owned; the middle
terminal turns require their own census and inverse.
