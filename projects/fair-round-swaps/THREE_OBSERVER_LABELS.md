# Which unlabelled pairing paths lift to named recipients?

Aster, 20 November 2026. Candidate mathematical result; independent
reconstruction is pending. No priority claim. This is a separate continuation
of the three-observer pairing task, whose three files belong to Linnet.

There is an exact answer **over any connected component of unlabelled
pairings**. It is not enough for the unlabelled pairings to be connected.
The relevant invariant is the connected components of the graph of goods
whose edges are pairs that actually occur in that unlabelled component.
Each named recipient must retain the component from which its goods come.
Subject to that condition, every assignment of pairs is reachable.

This supplies a constructive labelled-lift criterion, a sharp bound on the
number of labelled components for three observers, a six-exchange zero-buffer
operation, and an exact positive strict EF1 example separating a
fixed-observer obstruction from the unrestricted allocation graph. It does
not resolve the general incomplete-final-round question.

## Model and scope

There are `2r` distinct goods and `r` named recipients, each holding two goods.
An undirected compatibility graph `G` says which pairs are legal. A state is
a perfect matching of `G` together with a bijection from its edges to the
recipients. A move exchanges one good between two recipients, leaving both
new pairs legal. An **unlabelled switch** forgets the recipient names and
replaces two edges by a different perfect matching of the same four goods.

For three fixed observers, give good `g` a three-bit mark: bit `i` is present
exactly when observer `i` values `g` strictly above the value of its own fixed
bundle. A pair passes those observers' EF1 comparisons exactly when its
marks are disjoint. Equality is low, so ties cause no ambiguity. Other
comparisons must already be invariant or automatic: in particular, the
recipients' own EF1 conditions cannot depend on which legal pair they get.
Otherwise this compatibility model does not describe the full fair fiber.

The theorem below holds for any finite compatibility graph, not just graphs
from three-bit marks. The executable accepts arbitrary nonnegative bit masks.
More than three bits do not silently acquire unlabelled connectivity.

## Exact lift theorem

Fix a connected component `C` of the unlabelled switch graph. Define `U(C)`
on the goods by taking the union of all edges in all matchings in `C`. Write
its connected components as `B_1,...,B_s`, with `|B_j|=2k_j`. These sizes are
even because every matching in `C` covers each component internally.

**Theorem.** Two labelled states over `C` are connected by legal exchanges
if and only if, for every named recipient, its pair in both states belongs
to the same `B_j`.

Consequently the labelled graph above `C` has exactly

```
r! / (k_1! ... k_s!)
```

components. Each has exactly `|C| k_1! ... k_s!` vertices. In particular it is
connected, for `r>=1`, exactly when `U(C)` is connected (including the one-pair
case). These are all-size claims proved below; the finite checks test the
implementation rather than replace the proof.

### A two-exchange transposition

Suppose recipients `i,j` hold `ab,cd`, and a legal switch replaces these with
`bc,ad`. Exchange `a,c`, then exchange `b,d`. The resulting labelled pairs
are `cd,ab`: the original pairs have traded recipients in two legal moves.
The alternate cross matching gives the analogous operation.

This yields more than a path between two unlabelled states: it realizes a
transposition of their pair labels while returning to the same matching.

### Transport the transpositions to one root

Choose a root matching `M` and label its pairs `1,...,r`. For every `N` in
`C`, choose a switch path from `M` to `N` and lift it, choosing one of the two
labelled exchanges for every switch. Keep its resulting labelled state.

Build a graph `H` on the root pair indices. Join `i,j` whenever a switch is
possible between the pairs held by those recipients in any of the chosen
states. For that edge: follow the chosen path to the state, perform the
two-exchange transposition, then undo the path's good exchanges in reverse
order. This is a loop of unlabelled matchings that swaps exactly root pair
labels `i,j`.

The reverse path remains legal: a global permutation of recipient labels
commutes with exchanging any specified two goods, and legality depends only
on pairs, not their recipient labels. Thus the reverse path after the middle
transposition is the correspondingly relabelled reverse of the forward path.
If the chosen forward path has length `d`, this root loop has length `2d+2`.

Use paths from a spanning tree of `C`. Every prefix then reaches the chosen
state of its vertex. Along any such path, goods can move only between root
pair indices in the same component of `H`.

### Identify the components of H

Each component of `H` corresponds to exactly one component of `U(C)`:

* No move can exchange goods from different `U(C)` components. A new mixed
  pair would itself be an edge of `U(C)`, contradicting their separation.
  Root pairs are already edges of `U(C)`, so a recipient's goods stay in its
  original component along every chosen path. Each edge of `H` therefore
  joins root pairs in the same `U(C)` component.
* Conversely, during a chosen path, the two recipient indices at each switch
  are adjacent in `H`. By induction, every good remains among root pair
  indices in one `H` component. Each pair in its final matching consequently
  joins goods from one such component. Every edge of `U(C)` occurs in some
  final matching, so it cannot join different `H` components.

The partitions therefore agree, after expanding each root pair into its two
goods. Transpositions on the edges of a connected graph generate every
permutation of its vertices: along a path `v_0,...,v_t`, use its edges in
forward order and then all except the last in reverse order to transpose
the endpoints while restoring the internal vertices.

### Complete the construction and count

Lift a chosen path from `M` to the target's unlabelled matching. Its final
pair assignment differs from the desired assignment by a permutation of
recipient labels. The stated invariant says this permutation acts separately
inside the components of `H`. Perform it at the root using the transposition
loops, then follow the same good exchanges to the target. This proves
sufficiency. The first bullet above proves necessity.

For any matching in `C`, exactly `k_j` recipients must be assigned to `B_j`.
There are `r! / product(k_j!)` ways to choose those recipient sets. For any
fixed choice there are `product(k_j!)` assignments at each matching, all
connected by the construction. This proves both counts.

## Useful sufficient condition: a zero pair

If some matching in `C` contains two goods marked zero, `U(C)` is connected.
Indeed, let that pair be `xy` and any other pair be `ab`. The alternate pairs
`xa,yb` are legal, occur after one switch, and connect the other pair to the
zero goods in `U(C)`. Thus all labelled states above `C` connect.

There is also a short direct operation. When a zero pair occupies a spare
recipient `k`, transpose bundles at `i,j` by transposing `(i,k)`, then `(i,j)`,
then `(j,k)`. Each uses the two-exchange construction and one participating
pair is zero. This takes six good exchanges and restores the zero pair at
`k`. If `k` is one of `i,j`, two exchanges suffice.

`buffer_permute` gives a better bound by letting the zero pair move. Treat
each pair as one token. A permutation cycle of length `k` containing the
zero token uses `k-1` transpositions with that token. A nontrivial cycle not
containing it uses `k+1`: enter the cycle with the zero token, fix its tokens
in order, then leave. Each token transposition is two good exchanges. This
count is minimal among procedures restricted to transpositions with that
zero token. Each transposition either merges two permutation cycles or
splits one. Starting from the identity, every final nontrivial cycle not
containing zero must be split off from the zero cycle at least once. If
there are `c` final cycles (including fixed points) and `s` such nonzero
nontrivial cycles, at least `r-c+2s` transpositions are necessary. The counts
above attain this bound. This is not a shortest-path claim for unrestricted
good exchanges.

There are at most `floor(3(r-1)/2)` token transpositions in total. If the zero
cycle is trivial, at most `r-1` tokens move, in cycles of length at least
two; their total cost is their number plus at most half their number. If
the zero cycle has length `k>=2`, its cost is `k-1`; the other `r-k` tokens
cost at most `floor(3(r-k)/2)`, giving the same bound. It is attained by
transposing disjoint pairs of nonzero tokens when `r` is odd; for even
`r>=4` use one length-three nonzero cycle and length-two cycles, and for
`r=2` move the zero token once. Thus arbitrary pair permutations use at most
`2 floor(3(r-1)/2)` good exchanges. Given unlabelled paths of lengths
`d_1,d_2` to a matching with a zero pair, add these two lengths to that bound.

Having a zero good, as opposed to a zero pair that occurs in a matching, is
not the assertion proved here. Nor may `U(C)` be replaced by the graph of
switches available at just the initial matching. In the executable example
with marks `(0,1,2,5,3,4)` and pairs `(03,12,45)`, the last pair initially
cannot switch with either other pair; all 18 labelled states nevertheless
connect through three unlabelled matchings.

## Three observers: a sharp all-size bound

For three-bit marks, `U(C)` has **at most four components**. This conclusion
holds for any unlabelled component `C`; it does not need an all-size
unlabelled-connectivity theorem.

First, all goods of any one mark type belong to the same `U(C)` component.
Take two such goods `a,b`. If they are already paired there is nothing to
show. Otherwise their pairs `ax,by` can be switched to `bx,ay`, because
`a,b` have identical marks. Both old and new edges belong to `U(C)` and join
the goods into one component.

A component containing just one mark type must therefore contain only
zero-marked goods: any nonzero type is incompatible with itself. If there
is no zero-only component, each component uses at least two of the eight
types, giving at most four. If there is a zero-only component, mark 7 cannot
occur, because every such good must pair with a zero and would join that
component. The six remaining types can form at most three more components.

Let `r=4q+t`, where `0<=t<4`. The lift theorem gives the sharp upper bound

```
number of labelled components above C <= r! / ((q+1)!^t q!^(4-t)).
```

To maximize the multinomial coefficient, allow four groups, some possibly
empty, and balance their sizes. If two sizes differ by at least two, moving
one unit from the larger to the smaller decreases the product of factorials
in the denominator. Repetition yields the displayed balanced partition.
For `r=0` the formula is 1, the single empty state.

**Sharp family.** For four nonnegative integers `k_0,...,k_3`, place `k_j`
goods of type `j` and `k_j` goods of type `7 xor j`. Thus the four possible
classes are `0/7`, `1/6`, `2/5`, and `3/4`. Write `r=sum(k_j)`. Each observer
bit occurs on exactly `r` goods. A legal matching of `r` pairs can place
at most one occurrence of a bit in each pair, so every pair must contain
every bit exactly once. Each pair therefore has complementary marks.
Conversely, every matching within these complementary classes is legal.

There are exactly `product(k_j!)` unlabelled matchings. They all connect:
within a class, exchanging two goods of the same type transposes their
partners, and such transpositions generate all bijections between its two
types. The nonempty complementary classes are exactly the goods blocks.
Hence this family has

```
r! / product(k_j!) labelled components,
each with product(k_j!)^2 labelled states.
```

Balanced `k_j` attain the upper bound for every `r`. For example, taking one
good of every mark `0,...,7` gives four compulsory complementary pairs and
24 isolated labelled assignments. This is a fixed-observer statement, not
a separation of the unrestricted EF1 graph.

Within one component of this family, `connect_complementary` fixes each
desired good by exchanging it with a good of the same mark currently held
by its intended recipient. Such a good exists because that recipient's
type class is invariant. Each exchange preserves the type of every bundle,
and fixes a target good without displacing an already correct one. At most
`2r` exchanges suffice; no matchings need be enumerated. Different recipient
type assignments are rejected by the proved invariant, not a search cutoff.

These families can be realized by **positive, strictly ranked additive
utilities**. Give each of three singleton observers its own good worth 10
and the other two singleton goods distinct values below 1. Give free good
`g` value `11+(g+1)/(2r+1)` when its bit is high, and `1+(g+1)/(2r+1)`
otherwise, with `g` numbered within the free goods. Give every automatic
recipient value `3+(h+1)/(2r+4)` for **every** good `h`, including observer
goods, numbered from zero in the complete allocation. Every automatic pair
has total value above 6; after removing one good from any other pair its
residual value is below 4. The observers' restrictions on free pairs
are exactly the marks. The fixed-observer EF1 fiber is therefore precisely
the classified labelled graph. `realize_fixed_observers` returns these
exact rational utilities. Allowing the observers' goods to move changes the
graph and is deliberately outside this count.

## An observer loan reconnects the sharp examples

The distinction above can be demonstrated constructively, for arbitrarily
many goods, rather than left as a warning.

**Loan lemma.** Suppose three singleton observers hold `x_0,x_1,x_2` and the
other recipients are automatically EF1 for every possible pair of goods.
Assume `x_i` is no higher than the present threshold of each other observer.
Let a legal free matching contain a zero-marked good `z` paired with `h`,
where `h` is strictly above observer `i`'s threshold. Any permutation of the
matching's pairs among the named recipients admits an EF1 path of at most
`2+2 floor(3(r-1)/2) <= 3r-1` exchanges (`r>=2`). Only observer `i` needs to
move its good.

Exchange `x_i` with `h`. Observer `i`'s own utility increases; its threshold
therefore relaxes. Other observers keep their thresholds and goods. The
new free pair is `x_i,z`. Both goods are low for every observer: `z` was
already low, `x_i` is low for the other observers by hypothesis, and its
value for `i` is smaller than the new own value of `h`. All other free pairs
remain legal. Automatic recipients remain fair by hypothesis, and singleton
bundles leave zero after their one good is removed. The whole state is EF1.

Hold these new observer goods fixed. The free pair `x_i,z` is now a zero
buffer, so permute all pairs to their desired recipient labels in at most
`2 floor(3(r-1)/2)` exchanges. Finally exchange `x_i` back for `h`. The free matching
is now exactly its original legal matching with the desired labels, and
the observers have exactly their original goods. This last state is EF1
under the original thresholds, even though observer `i`'s threshold falls
on the last step. The two loan exchanges give the bound.

If a zero good is already paired with another zero, no observer loan is
needed. If its partner has a nonzero mark, choose one of that mark's bits
as `i`. Thus, under the other hypotheses, any zero good suffices to remove
the label obstruction when an observer may lend a good. This statement is
about moving outside the fixed-observer fiber, not about its connectivity.

The exact realization above satisfies the hypotheses: each observer's good
is below the other observers' thresholds, and every automatic pair, even
one containing a former observer good, is fair. In a complementary family
with a nonempty `0/7` class, the zero's partner is high for all three
observers. `loan_label_permutation` returns every allocation along the
resulting path. Its internal conservative marks set the borrowed observer
good to zero and leave the other old marks unchanged; actual relaxation of
one threshold can only allow more pairs.

**Full endpoint consequence for this family.** If the `0/7` class is
nonempty, any two fixed-observer endpoints of the realized complementary
family, including different unlabelled matchings and different label
classes, connect in at most `5r-1` exchanges. First
assign each target pair to some current recipient of the same complementary
type, obtaining an intermediate labelled target. Reach it by at most `2r`
same-type good exchanges. Then use the loan lemma to correct the remaining
recipient labels in at most `3r-1` exchanges. The other two observers stay
fixed throughout. `connect_realized_family` implements this composition.

For the balanced 100-pair example the fixed-observer graph has
`1612207508215775948685323966297082670959348818240567745024` components.
Reversing the canonical pair labels crosses those components, yet the
executable constructs an actual 298-exchange EF1 loan path between them.
It also constructs a 192-exchange path within a single label class. These
are exact constructed paths; no enumeration of the enormous full graph
or assertion about unrelated valuation profiles is involved.

## Exact EF1 failure of an unconditional labelled lift

Five agents divide seven goods. Agents 0,1,2 hold goods 0,1,2 respectively;
agents 3,4 each hold two of goods 3,4,5,6. Their additive values are:

| Agent | g0 | g1 | g2 | g3 | g4 | g5 | g6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 10 | 1 | 2 | 14 | 3 | 4 | 15 |
| 1 | 1 | 10 | 2 | 3 | 14 | 15 | 4 |
| 2 | 1 | 2 | 10 | 3 | 14 | 4 | 15 |
| 3 | 1 | 2 | 3 | 11 | 12 | 13 | 14 |
| 4 | 3 | 2 | 1 | 14 | 13 | 12 | 11 |

Every row is positive and strictly ranked. The four free goods have marks
`(1,6,2,5)`. Agents 3,4 are automatic throughout this fixed-observer fiber:
their own pair totals are at least 23, while the residual value of any
other pair after deleting its larger good is at most 14. Singleton bundles
impose no restriction on them.

The only unlabelled matching is `{{g3,g4},{g5,g6}}`. Although `g3,g5` have
disjoint marks, their complementary pair `g4,g6` does not. The union graph
therefore has two components of two goods, giving two isolated labelled
states, owner vectors `0123344` and `0124433`.

**This is not a counterexample to the project's endpoint question.** Enumerate
all 1,260 allocations of size `(1,1,1,2,2)`, allowing the observers to change
their goods: exactly 156 are EF1, and all 156 lie in one component. A shortest
escape route is

```
0123344 -> 3120344 -> 3124340 -> 3124430 -> 0124433
```

Each arrow exchanges exactly two goods. The route temporarily moves an
observer's good, precisely the permission the restricted fiber forbids.
The example establishes only a failed fixed-observer lift; no greedy
endpoint claim is needed or made.

## Run and inspect

From the repository root, with standard-library Python 3.10 or newer:

```sh
python3 projects/fair-round-swaps/three_observer_labels.py
python3 projects/fair-round-swaps/three_observer_labels.py --family-pairs 100
python3 -m unittest discover -s projects/fair-round-swaps -p test_three_observer_labels.py -v
```

`explore(marks, start)` exhausts one unlabelled component and stores a spanning
tree plus its transposition loops. `connect(component, target)` returns every
labelled state in an exact path, or `None` when the invariant or unlabelled
component prevents it. It has no search cutoff. Interrupting it does not
produce a negative result. `buffer_transpose` does not enumerate matchings
and works directly for arbitrarily many pairs.

Recorded checks: the full three-bit mark census through eight
goods includes 1,809 feasible multisets, 850,705 labelled states and 825,531
constructed root-to-state paths. The test oracle independently enumerates
the **entire labelled exchange graph**, rather than using the proof's
transposition graph. Seed `20261120516` additionally generates 40 eight-good
profiles (infeasible profiles are skipped), checks all labelled components
for feasible profiles, and samples target paths. Every census entry also
checks the four-block upper bound. Balanced sharp families through six pairs
are enumerated, and a 100-pair family constructs a 192-exchange route without
enumeration. Exact positive strict realizations are checked against literal
EF1 for every pair partition in three small profiles. Zero-buffer operations
are checked through 100 goods. A chordless six-cycle encoded with more observer
bits verifies rejection of targets in a different unlabelled component.
Literal EF1 deletion comparisons independently reproduce the full 156-state
boundary census. The CLI prints its actual route.

All 32,768 compatibility graphs on six goods are also checked, using one
observer bit for each forbidden edge. Among them, 24,823 have a perfect
matching; their 26,488 unlabelled components and 368,640 labelled states
verify the theorem beyond the three-observer specialization, including
disconnected unlabelled graphs. The loan test checks all 24 pair-label
permutations of a four-pair sharp example with each of the three possible
borrowers. Thirty further constructed paths change both the matching and
its label class, with exact positive rational EF1 checked at every step
through twelve pairs.

The construction and tests are self-contained except for the CLI census's
use of the existing `swaps.py` finite model. They need no unmerged pairing
constructor, solver, or large certificate. A later accepted all-size
unlabelled-connectivity theorem can apply the criterion to the union of
**all** legal matchings; until then the theorem here is stated over `C`.
