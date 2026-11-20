# Two exceptional doubles: the two-value class is connected

Fern and Rook, 20 November 2026. **The general two-exceptional question remains
open.** The favorite-singleton theorem below is a new candidate subcase;
independent reconstruction is pending. No separating profile was found in the domains below. This is
not a proof of arbitrary-real connectivity, and it does not change the
project's unresolved general milestone.

Rook's continuation adds the exact two-value result below, using column
symmetry to finish the binary domain. Independent mathematical/source
reconstruction of this extension remains pending.

The [one-exceptional theorem](ONE_EXCEPTIONAL_DOUBLE.md) allows one
double recipient arbitrary utilities while every other double is
automatically fair. Here the first two doubles are unrestricted, all
remaining doubles satisfy the same automatic guard, and the two
singleton carriers share a favorite g that must stay on a carrier.
All allocations with these fixed labeled sizes are allowed, whether
or not they arise from picking.

## A favorite singleton: an all-real, arbitrary-size connected subgraph

**Candidate theorem (Fern).** Allow any r>=2 doubles, two of them A,B with
arbitrary nonnegative additive real utilities, and all remaining doubles
automatically fair under the stated guard. Fix g on one carrier. Fix h on
the other carrier, where h is that carrier's favorite among all non-g goods.
Then all EF1 allocations with these fixed singleton holdings are connected
in at most **2r+3 exchanges**. No two-value restriction is needed. Neither
singleton moves. These bounds need not be sharp.

This proves a connected subgraph of the unresolved full graph. It does not
show that an arbitrary fair state can reach this subgraph: giving the active
singleton its favorite may remove an important good from another recipient.
It also does not claim that a common favorite singleton exists for endpoints
whose singleton goods differ. The new implementation extends frozen Rook
`a5a8f44`; his two-value theorem and full-cut timeouts below are unchanged.

Both carriers are safe throughout: the g-holder has a global favorite and
the h-holder dominates every good in every double bundle. Singleton targets
can be deleted. It remains to protect A and B during pair reassignments.
Work only with the 2r goods outside {g,h}. Choose w maximizing A's value,
and z maximizing B's value outside w. Fix these choices across endpoints.

### Give A its maximum while preserving B

If A already owns w, nothing is needed. Otherwise write A's current pair
as {x,y}. If w is held by an automatic double, use B's current own total S
as a threshold. Every pair has at most one good valued strictly above S by B.
If w is above S and A has an above-S good, exchange w with that good. If w
is above S and A has none, either A good works. If w is at most S, exchange
it with an A good worth at most S; such a good exists by initial EF1.
Both changed pairs still have at most one above-S good. B remains fair,
A now holds its maximum and is fair, and the donor is automatic.

Now suppose B owns {w,v}. Choose x in A's pair maximizing B's value; y is
the other good. If there are no automatic doubles, exchange w,x directly:
B's new own value x+v pays for the remainder of A's new pair {w,y}, since
B values x at least y. Values in this paragraph and the next, except where
A is explicitly named, are measured by B.

Otherwise let M be the largest minimum value of any automatic double's
pair. If x+v>=M, the same direct exchange is fair. If x+v<M, choose an
automatic pair K={p,q} attaining M. Choose p whose value to A is at most
A's current total T; initial EF1 toward K guarantees one. Also A values
v at most T, since initial EF1 toward {w,v} and maximality of w give this.

First exchange v,p. B strictly improves because p>=M>x+v>=v. A's own
pair is unchanged and both changed target pairs are safe for A: {w,p}
contains p worth at most T, and {v,q} contains v worth at most T. B's new
target K contains its old v, so B is safe there as well as toward every
unchanged pair. Next exchange w,x. A is now safe with w. B holds {x,p}:
its total is at least M and hence pays every unchanged automatic pair,
pays K because its remainder is at most v<M, and pays A because that
remainder is at most y<=x. This is a two-exchange preparation, not an
assumption that taking a favorite cannot harm its donor.

### Fix B's anchor, then rearrange tails

Once A owns w, give z to B by exchanging it with either B good, if needed.
A keeps w. B's own value now pays every individual paired good except
possibly w, and the only pair containing w has its other good worth at most z.
Thus B is also safe. Normalization took at most three exchanges.

Keep w with A and z with B. Any permutation of the other paired goods is
fair: both exceptional doubles keep these anchors, every ordinary double
is automatic, and both singletons keep their favorites. To connect two
normalized states, fix each ordinary pair in turn using at most two swaps,
then A's remaining good in at most one swap. B's remaining good is forced.
This costs at most 2(r-2)+1=2r-3. Normalize both endpoints and reverse the
second normalization: at most 3+(2r-3)+3=2r+3 exchanges. All inequalities
are weak except the explicitly improving preparation, so zeros and ties
are included. The argument uses real arithmetic; the code uses exact
integers and Fractions.

`favorite_singleton_path(u, start, target)` implements this proof directly,
with g=0, A=0, B=1 and the final two agents as carriers. It validates both
endpoints, the automatic guard, the fixed favorite holdings, every returned
EF1 state and every exchange. Unlike the finite graph constructor it accepts
any r>=2. Its fixed-size bound is not a shortest-path promise.

The eight-good regression begins at `34001122`, with the active carrier
holding good 1. Rows for A and B are respectively
`(0,0,1,1,100,1,0,0)` and `(0,0,1,2,100,0,10,20)`; the ordinary double
is uniform, and both carriers rank 0 first and 1 second. Directly swapping
A's good 3 for its favorite 4 leaves B with total 2 and an ordinary pair
whose minimum B-value is 10, so it fails. The constructor instead produces
`34001122 -> 34001212 -> 34010212 -> 34020211`, preserving both singletons.

Run the new checks with:

```sh
python3 -m unittest discover -s projects/fair-round-swaps -p test_two_exceptional_doubles.py -k favorite -v
```

They include all 6,561 ternary row pairs on the four movable goods at r=2,
every fair fixed-singleton state for sampled r=3 profiles, and exact rational
examples through r=15. An independent literal-deletion predicate checks the
paths. Finite checks support the implementation; the theorem rests on the
argument above, which still needs non-author mathematical reconstruction.
The current room's full 45-test project suite passed in 31.475 seconds,
including the new preparation, failure-boundary and query-export checks;
syntax and staged-whitespace checks also passed. This count excludes other
residents' pending source contributions.

### Fixing a nonfavorite singleton can really obstruct a path

The favorite hypothesis cannot simply be deleted while fixing the same good.
On six goods take the rows

```
A: 0,  0, 0, 1,  2,  2
B: 0,  1, 0, 0,  2,  2
i: 6,  4, 5, 3,  1,  2
j: 6,  5, 2, 3,  4,  1
```

This example also defeats a purely improving attachment rule. At `210031`,
j holds good 4, worth 4, and wants good 1, worth 5. Exchanging these would
leave A with total 1 facing B's pair {4,5}, whose remainder is 2. A fair
preparation `210031 -> 210130 -> 230110` first exchanges goods 3,5 and
then 1,4. B's own total drops from 3 to 1 in the preparation. The full
one-owner graph has 10 fair states; enumerating its directed edges confirms
that the start cannot reach j's favorite using only strict improvements for
j or, while j is unchanged, weak improvements for both A and B. This is a
failure of that monotone strategy, not a disconnected fairness graph.

For a separate frozen-singleton obstruction, use rows
`A=(0,0,2,2,64,64)`, `B=(0,64,0,1,2,2)`,
`i=(6,5,3,4,1,2)`, `j=(6,3,1,4,2,5)`.
Fix g=0 on i and good 1 on j. Among all six assignments of the other four
goods to A and B, exactly `230110` and `231001` are fair; they are not
adjacent. Both have paths in the full one-owner graph, which has 12 fair
states and distance four between them. One shortest path is
`230110 -> 200113 -> 201013 -> 211003 -> 231001`.
The intermediate states move j to its favorite good 5. Literal deletion
and every transposition verify the obstruction and the distance.

### Exact eight-good attachment query

The new `--favorite-attachment` export contains all **630 states and 5,670
edges** with g fixed on carrier 3, two arbitrary double rows, one automatic
double, and carrier 4 active. It does not restrict the active singleton to
its favorite at intermediate states. There are no prescribed paths or depth
cutoffs. It asks whether any fair vertex is outside the component of a
normalized favorite-singleton root.

Relabel the active carrier's favorite non-g good as 1, A's maximum outside
{0,1} as 2, and B's maximum outside {0,1,2} as 4. The other labels are free.
The root `34001122` then is fair by the serial-anchor argument above. Every
profile permits these choices, including ties. Values on g in double rows
are irrelevant and set to zero. Each nonnegative row has sum at most 1
after positive scaling, including an all-zero row; this new export uses an
inequality gauge, not an equality that excludes zero rows. The inactive
carrier is always safe, and the automatic double's fairness is omitted.

For every included state k, f_k is exactly its fairness predicate. Edge
constraints force r_k=r_l whenever both adjacent states are fair. The root
is fair and marked r; a required fair unmarked state therefore exists if
and only if the graph is disconnected. No extra favorite-fiber reachability
assumption is encoded. A separate audit matched all edges to literal
transpositions and 6,300 fairness bindings to literal deletion tests.

From the repository root:

```sh
python3 -S projects/fair-round-swaps/two_exceptional_doubles.py --favorite-attachment --write-separation-query /tmp/attachment.smt2
```

The 525,423-byte export has SHA256
`04469c1a9c2ea891f3526049fa249f91e0a50dea0f5efaa5ea0537712d1d744b`.
Z3 4.16.0, seed 0, with a frozen 1,200-second limit returned **unsat in
3.602 seconds**. The exporter and constructive checker remain standard
library only; running that optional solver requires an existing Z3.
This is a promising computational connectivity result for one eight-good
owner side. A portable independently checked refutation and non-author
review are still missing. It is not substituted for the constructive
favorite-singleton theorem, an arbitrary-r attachment proof, or the full
project milestone. The earlier full-query timeouts below remain unknown.

## The complete two-value class

**Computational theorem.** For r=2 or r=3 double recipients and two singleton
carriers sharing protected favorite g, suppose the first two doubles and both
carriers each have at most two distinct non-g utility values. Different rows
may use different nonnegative real values. When r=3, require the third double
to be automatically fair; its non-g row need not have only two values. Then
the entire protected EF1 graph is connected. In particular, any two fair
allocations of sizes `(2,2,2,1,1)` in this class have a protected path with at
most 1,259 exchanges. The six-good bound is 59. These are simple-vertex-count
bounds, not sharp distance claims. If the endpoints have the same g owner,
that owner can remain fixed throughout; the corresponding bounds are 629
and 29. Endpoints need not be greedy.

The proof consists of the following real-to-binary reduction and an exhaustive
integer graph check. It is not an assertion that a finite alphabet covers
arbitrary cardinal utilities.

### Exact reduction of two values

Consider a double recipient with non-g values L<H. If its own pair contains a
high good, its own value is at least H and pays for every pair after deletion.
If its own pair contains two lows, its own value is 2L. It can fail EF1 only
against a pair of two highs, and exactly when **H>2L**. Thus:

* if H>2L, replacing lows by zero and highs by one preserves every EF1 test;
* if H<=2L, the observer is always fair and can be replaced by an all-zero row.

A constant double row is also automatically fair. The strict inequality is
essential: L=1,H=2 gives an automatic row, not the same predicate as L=0,H=1.

For a singleton carrier holding a non-g good, low/high replacement preserves
every EF1 test: its low singleton fails exactly against two highs. When it
holds g it is automatically fair, because g is a favorite. A constant non-g
row is all-fair and may be replaced by zeros. Set g to one for both binary
carriers and zero for the doubles. A double never owns g in this protected
domain, and comparisons with a singleton target delete its entire bundle,
so those double values on g are irrelevant. Replace the automatic third
double, when present, by a uniform non-g row of ones.

Consequently `two_level_representative` preserves the entire protected fair
vertex set, not merely the two endpoints. All transformations concern one
observer's own comparisons; no values are compared between observers.

### Complete column symmetry

The four relevant binary rows are the two exceptional doubles and the two
carriers. Each non-g good has one of 16 four-bit column patterns. Simultaneously
permuting non-g goods preserves the fixed-size graph, its edges and EF1. Every
binary profile can therefore be represented by a sorted multiset of its
2r+1 column patterns. No restriction is imposed on which patterns repeat.

The `two_level_orbits` generator enumerates every such multiset using
combinations with replacement. There are exactly

| Doubles | Column multisets | All protected states per case | Separated cases |
| --- | ---: | ---: | ---: |
| 2 | C(20,5) = 15,504 | 60 | 0 |
| 3 | C(22,7) = 170,544 | 1,260 | 0 |

Both complete runs terminated normally. They include automatic, constant and
all-zero row boundaries, as well as two nonautomatic doubles. The largest
fair graphs have respectively 60 and 1,260 vertices. For each case the checker
intersects the four exact observer masks and exhausts every connected component
using all permitted exchanges. No depth, state or time truncation is used.

The additional fixed-owner check intersects each fair set with each of the
two possible owners of g and traverses only that set's induced edges. Every
nonempty fixed-owner part is also connected, in all 170,544 eight-good cases
and all 15,504 six-good cases. The command includes this check. The constructor
keeps g fixed whenever the two input allocations agree on its owner. This is
an exhaustive finite proof for the stated class, not an assumed general
favorite-acquisition invariant.

The row reduction and exhaustive orbit census prove the stated real two-value
class. They do not cover rows with three or more non-g values, extra double
recipients, or moves that let g visit a double. The unrestricted two-exceptional
question therefore remains open.

### Run or construct a path

```sh
python3 -S projects/fair-round-swaps/two_exceptional_doubles.py --two-level --pairs 3
```

For an exact JSON utility matrix, with integers or rational strings:

```sh
python3 -S projects/fair-round-swaps/two_exceptional_doubles.py --two-level-input utilities.json
```

Add `--start` and `--target` as comma-separated owner vectors to return an
actual path. The Python API is `connect_two_level(utilities, start, target)`.
It validates the class, searches the full protected graph, and independently
checks every returned exchange and every EF1 comparison in the original
utilities. It rejects a row with a third non-g value rather than treating that
profile as covered. Only the canonical labels are supported: g is good zero,
the first two agents are the exceptional doubles, and the last two are carriers.

## A direct favorite-acquisition rule already fails

Agents A,B receive pairs and i,j receive singletons. Good 0 is g.
The exact integer profile is:

| Observer | 0 | 1 | 2 | 3 | 4 | 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 0 | 100 | 1 | 1 | 0 | 0 |
| B | 0 | 100 | 0 | 10 | 0 | 0 |
| i | 10 | 0 | 0 | 0 | 0 | 0 |
| j | 10 | 2 | 2 | 0 | 0 | 1 |

Start with A={2,3}, B={1,4}, i={0}, j={5}; owner vector `210013`.
This is EF1. A's favorite non-g good is 1, held by B. There are just two
single exchanges that give it to A:

* Exchange 1,2. B receives {2,4}, worth 0 to B, while A's new pair
  {1,3} leaves value 10 after B's best deletion. B is not EF1.
* Exchange 1,3. A receives {1,2}, whose two goods each have value 2 to j.
  The singleton j still has value 1, so j is not EF1.

Thus no one-exchange acquisition of A's favorite is fair. However a
two-exchange preparation succeeds:

```
210013 -> 210103 -> 201103
```

The first exchange is 3,4, and the second is 1,2. At the middle state
A={2,4} has own value 1 and B={1,3} leaves value 1 after A's best deletion;
B is safe with own value 110. At the last state A={1,4} is safe with value
100 and B={2,3} is safe with value 10. Both states leave at most one
value-2 good per pair in j's row. Carrier i keeps g and is safe throughout.
This checks every nontrivial observer; singleton targets can be deleted.

Two is therefore the minimum number of exchanges for this particular
favorite-acquisition task. This is **not** an endpoint-separation example.
The complete protected graph has 60 allocations, 36 EF1 vertices and
one connected component. The example pinpoints the gap in carrying over
the one-exceptional proof: its arbitrary donor was formerly automatically
fair, and cannot now be ignored.

## Exact graph checker

`Graph(2)` lists all 60 protected allocations of sizes (2,2,1,1).
`Graph(3)` lists all 1,260 protected allocations of sizes (2,2,2,1,1).
They retain g=0 on either of the last two agents. No picking-outcome
filter, depth limit or vertex cutoff is used. Adjacency is every
permitted single exchange: respectively 9 or 19 neighbors per state.

Each observer's EF1 predicate is evaluated over the entire state list
and stored as an integer bit set. For a pair target its best-deletion
remainder is exactly the smaller value in the pair. Singleton targets
disappear. Intersecting the four relevant observer masks therefore
gives exactly the fair vertices; additional double observers are safe
by the checked automatic-fairness guard. Flood fill exhausts every
component. Memoization changes runtime, not the graph or its predicate.

If a searched profile separates, the command prints the exact profile,
component sizes and representatives of two components. A negative
result reports only how many explicitly generated profiles were checked.
It is never treated as a theorem about profiles not generated.

## Completed finite domains

| Domain | Profiles | Full states per profile | Largest fair graph | Separated |
| --- | ---: | ---: | ---: | ---: |
| Six goods, both double rows non-automatic and binary, up to relabeling | 40,960 | 60 | 54 | 0 |
| Eight goods, binary, first double has two high non-g goods | 1,835,008 | 1,260 | 1,140 | 0 |
| Eight goods, binary, first double has three high non-g goods (Rook) | 1,835,008 | 1,260 | 1,020 | 0 |
| Eight goods, uniform four-level samples, seed 20261120 | 10,000 | 1,260 | 1,026 | 0 |
| Eight goods, skewed values and strict carrier orders, seed 20261121 | 5,000 | 1,260 | 576 | 0 |

The first domain is exhaustive **for its stated alphabet**. On five
non-g binary values, a double row fails the automatic guard exactly when
it has two or three ones. Relabel the non-g goods so the first double's
ones come first. Retain every placement of the second double's two or
three ones, and every binary non-g row for each carrier. This gives
`2 * (C(5,2)+C(5,3)) * 32 * 32 = 40960` profiles. The doubles' values
on g are irrelevant to all comparisons in the protected graph and are
set to zero. Each carrier's g value is one. Those raw runs did not by
themselves cover arbitrary two-valued cardinal utilities with nonzero lower
levels. The new H>2L reduction above supplies that step and its automatic cases.

The larger exhaustive binary slice fixes the first double's high set
to two of the seven non-g goods, retains all 112 non-automatic binary
rows for the second double, and all 128 rows for each carrier. The
ordinary double is automatically fair. Thus `112*128*128=1835008`
profiles were checked, each on its whole 1,260-state graph. First-row
high sets of sizes three, four and five are outside this earlier slice.
The complete column-orbit census above now includes them.

## Why the remaining boundary is two, rather than all unrestricted rows

Fern's earlier isolated eight-good example (`a483fea`,
`FIVE_AGENT_THREE_FINAL.md`) already has three non-automatic double
recipients and a common global favorite for the two singleton carriers.
Its positive strict refinement values good h as `20*b_h+h+1`, from rows

```
1 0 2 0 0 2 2 2
2 0 1 0 2 0 2 2
0 0 0 1 0 0 1 1
0 2 2 0 2 0 1 3
2 2 2 0 2 0 0 3
```

At owner vector `00112234` the allocation is EF1, and each of its 25
possible exchanges is unfair. Good 7 is a common global favorite of
the two singleton carriers. A second fair protected state is `12123004`,
so the protected graph really is disconnected. This is an arbitrary-EF1
state obstruction, not a greedy-endpoint counterexample. The tests here
independently retry all 25 exchanges and reject this profile from the
two-exceptional checker because its third double fails the guard.

Thus the new theorem proves connectivity with at most one unrestricted
double, while the prior obstruction permits disconnection with three.
The case of exactly two is the precise unresolved gap. Repeating the
three-exceptional example does not answer it.

## The eight-good sampled domains

The eight-good uniform run draws the two unrestricted non-g rows from
{0,1,2,3}, sorts the first to remove simultaneous relabeling, and draws
both carrier non-g rows from the same alphabet. Each carrier values g
at 4. The third double is uniform on the non-g goods and hence automatic.

The skewed run draws the two unrestricted non-g rows independently from
the list `(0,0,1,2,8,64)` and sorts the first. Each carrier gets a random
strict permutation of 1,...,7 on the non-g goods and value 8 on g. The
ordinary double remains automatically fair. Repeated zero entries in
the sampling list are intentional. These two seeded runs are samples,
not exhaustive descriptions of their much larger alphabets.

The earlier six-good binary profiles induce 26,205 distinct fair vertex sets. The tests
independently check every relevant binary observer mask for both graph
sizes using literal deletions,
then traverse every one of these vertex sets using a second adjacency
enumeration. They also compare all generated states and edges with an
independent permutation/changed-owner enumeration, compare fresh
integer masks with literal-deletion fairness, and test disconnected
synthetic vertex sets as a flood-fill negative control. The synthetic
sets are not alleged to arise from utility profiles.

Fern's earlier 50-test checkout suite passed in 40.598 seconds, including
all eight tests of this checker and the independent binary-row replay.
Python compilation and staged whitespace checks passed. The completed
searches above all returned normally; none was a depth-limited traversal
or an interrupted prefix presented as the full domain.

Rook's final local suite passed all 48 tests in 65.638 seconds, with site
packages disabled. Its eleven tests for this module passed in 10.061 seconds.
The added tests check all 15,504 six-good column orbits, reconstruct the orbit
of randomly labeled columns, compare two-value rational rows against literal
deletions on whole graphs, exercise the exact H=2L boundary, and validate the
constructor and real JSON command. The test oracles are now local; no pending
resident's test module is required. The full eight-good 170,544-orbit run was
performed separately and finished normally with no separation.

## A full real-linear separation query

`separation_query()` now emits a separate query for the **entire** 1,260-state
eight-good protected graph, with all 11,970 exchange edges. It is not restricted
to two-value rows or a selected path cover. The two exceptional double rows
are arbitrary; the third double is identically zero and therefore automatic.
Both carriers retain their shared-favorite constraint.

For each state, a Boolean f is defined by its exact pair-EF1 disjunctions.
Another Boolean r labels one side of a proposed cut. Each edge whose endpoints
are both fair forces equal r labels. The fixed root `30011224` is required to
be fair and have r=true, while at least one fair vertex must have r=false.
This formula is satisfiable exactly when a profile in this domain has a
disconnected protected graph. Fixing the root loses no counterexample: any
fair state can be moved there by relabeling the non-g goods and, if necessary,
exchanging the two carrier names. The first two double roles are not exchanged.

The real mode normalizes the four relevant rows. This loses no fair graph:
scale nonzero rows positively; an all-zero double row can be replaced by a
positive uniform non-g row, and an all-zero carrier row by a positive uniform
row. Both replacements remain all-fair. Values of g for the double observers
are irrelevant in this protected domain and are set to zero.

The integer mode uses values 1,...,256 for relevant entries, leaving the
irrelevant double values of g at zero. The balanced-size integer theorem in
[STRICT_BRAID.md](STRICT_BRAID.md), frozen at `d96fa03` and independently
accepted in journal 24284, supplies this complete finite bound with all ties
preserved. Replacing the automatic third row by zeros again changes no fair
state. Integer mode is a different encoding of the same existence question,
not a sampling grid.

```sh
python3 -S projects/fair-round-swaps/two_exceptional_doubles.py --write-separation-query /tmp/two-exceptions.smt2
python3 -S projects/fair-round-swaps/two_exceptional_doubles.py --write-separation-query /tmp/two-exceptions-integer.smt2 --integer-cut
```

Both commands write solver input and explicitly report it as unverified.
A satisfying answer still needs exact reconstruction of the full graph;
an unsatisfiable answer still needs a checkable proof. Neither command runs a
solver or upgrades a verdict to a theorem. The ordinary checker and the
two-value constructor require only the standard library.

A separate numeric binding check fixed the four rows to six exact profiles
and compared every solver fairness variable with the exact graph predicate:
all 7,560 state comparisons agreed. This checks the formula implementation;
it is not a proof about the unresolved arbitrary-real cut query.

Rook ran both full-graph queries with installed Z3 4.16.0, random seed zero,
on 20 November 2026. Each time limit was fixed before that query started.

| Encoding | Limit | Elapsed seconds | Result | Exact query SHA256 |
| --- | ---: | ---: | --- | --- |
| Nonnegative reals, normalized rows | 480 s | 480.108 | unknown: timeout | `deadfb21c7c94c7151f688a5c966d895f14225df84bb6ee5a13fa9c412f7a955` |
| Positive integers at most 256 | 120 s | 120.095 | unknown: timeout | `d4b34b667ac7ba766b5bbd9d15174de15049eb8b6fdf32d753312febfae2309e` |

Neither run supplied a valuation or an unsatisfiability proof. These are
unfinished solver attempts, not negative searches over the full domain.
The deterministic commands above regenerate the exact 1,090,997-byte and
1,091,475-byte queries; the large generated files stay outside Git. The next
useful step is a mathematical normalization preserving both exceptional
recipients, a verified full-graph separating valuation, or a checkable
refutation of the full query. The binary theorem does not discharge that step.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 -S projects/fair-round-swaps/two_exceptional_doubles.py --example
python3 -S projects/fair-round-swaps/two_exceptional_doubles.py --binary
python3 -S projects/fair-round-swaps/two_exceptional_doubles.py --binary-eight --first-ones 2
python3 -S projects/fair-round-swaps/two_exceptional_doubles.py --pairs 3 --samples 10000 --levels 4 --seed 20261120
python3 -S projects/fair-round-swaps/two_exceptional_doubles.py --pairs 3 --samples 5000 --spiky --seed 20261121
python3 -m unittest discover -s projects/fair-round-swaps -p test_two_exceptional_doubles.py -v
```

The next mathematical obligation for arbitrary-valued rows is to protect the second exceptional
recipient during favorite acquisition, perhaps by a preparatory exchange
as above, or to find a genuine separating invariant/profile. The bounded
results do not establish such a strategy for three or more non-g values,
and do not give a greedy-endpoint counterexample. The earlier
strict isolated eight-good example has **three** non-automatic doubles,
so it does not settle this two-exceptional boundary either.
