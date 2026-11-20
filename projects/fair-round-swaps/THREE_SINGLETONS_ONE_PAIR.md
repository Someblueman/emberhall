# Four agents, five goods: the entire EF1 graph has diameter at most five

Aster, 20 November 2026. Complete finite computational proof with an independent
checker; non-author mathematical acceptance is pending. No priority claim.

**Theorem.** Four agents divide five indivisible goods with fixed bundle sizes
`(1,1,1,2)` and arbitrary nonnegative additive real utilities. Every EF1
allocation connects to every other by at most **five** exchanges of two goods.
The bound is sharp, even when every utility is positive and every agent's
ranking is strict. Intermediate allocations need not be picking outcomes.

The result strengthens the four-agent **no-isolation** result in
[SINGLE_EXTRA.md](SINGLE_EXTRA.md): it excludes disconnected components of
every size, not just isolated vertices. It is confined to this size vector.
That earlier document already gives isolated EF1 allocations with five
agents and six goods, so the number of singleton observers matters. The
general incomplete-final-round question remains open.

## Why a finite ordinal proof covers arbitrary real utilities

Let singleton observers `0,1,2` hold `x_0,x_1,x_2`, and let agent `3` hold
the remaining pair `{a,b}`. A singleton's only possibly nontrivial EF1
condition is

```
u_i(x_i) >= min(u_i(a), u_i(b)).
```

Comparisons with any singleton vanish on deleting its only good. Agent 3
is automatically EF1 for any nonnegative utility row: every other bundle
is a singleton. Its comparisons with its own bundle are automatic too.
Thus its values impose **no additional assumption** on the theorem.

The displayed condition depends only on the three observers' weak orders
of individual goods. Replace each row's distinct values by consecutive
integer ranks starting at zero, retaining all ties. Every fair state and
every allowed exchange remains exactly the same. This is not a numerical
approximation or a restriction to equally spaced utility values.

There are 541 weak orders on five labelled goods. One generator enumerates
the five-entry tuples over `{0,...,4}` that use every integer from zero
through their maximum. An independent generator permutes the five goods,
cuts the resulting sequence into nonempty ordered blocks, and gives each
block its rank. Both produce exactly the same 541 tuples.

Simultaneously relabel the goods to put the first observer's row in
nondecreasing order. Its canonical rank tuple starts with zero and each
subsequent entry either stays equal or rises by one: exactly `2^4=16`
possibilities. Ties can be ordered arbitrarily within their block. The
second and third observer still range over **all** 541 weak orders, so
every original profile is represented after this common good relabelling.
No permutation of agent labels or other symmetry is assumed.

The exhaustive domain therefore has

```
16 * 541 * 541 = 4,682,896 ordinal profile representatives.
```

It contains duplicates under further symmetries; duplicates do not omit
any case. The construction does not break ties into strict preferences.

## The full allocation and exchange graph

Choose the three singleton goods as an ordered triple of distinct goods.
The other two belong to agent 3. This enumerates all `5*4*3=60` allocations,
including every allocation outside picking outcomes. Each has nine
exchanges: of the ten pairs of goods, only the pair already held by agent 3
fails to change the allocation. There are 270 undirected edges.

For each ordinal profile retain exactly the states satisfying the three
displayed inequalities, and keep every edge with both endpoints retained.
The implementation uses one bit per state. Intersecting the first two
observer masks gives 1,194 distinct masks; their multiplicities sum to
`16*541=8,656`. Each is intersected with every third-observer mask. This
aggregation changes neither the third-observer cases nor their graphs.
It counts all 4,682,896 profile representatives exactly once with weight.

The completed census found:

| Quantity | Exact result |
| --- | ---: |
| Profile representatives | 4,682,896 |
| Distinct induced EF1 graphs | 135,191 |
| Empty fair graphs | 0 |
| Disconnected fair graphs | 0 |
| Minimum number of EF1 vertices | 14 |
| Maximum number of EF1 vertices | 60 |
| Maximum diameter | 5 |

The primary checker computes connected components by bit-set traversal and
diameters by breadth-first layers from every fair vertex. Every diameter
measurement is over the full induced graph, not a selected collection of
paths or a sampled endpoint pair.

The independent checker uses a different ordering of the 60 allocations,
the ordered-block weak-order generator, and literal deletion comparisons.
It enumerates the **unaggregated** 16-by-541-by-541 profile domain, obtaining
the same weighted histogram and 135,191 distinct graphs. Its adjacency
test compares the two changed owner entries rather than generating swaps.
For every distinct graph, it checks the five-step upper bound by Boolean
relation products: from the reflexive one-step relation `R`, form `R^2`,
then `R^4`, then `R^5`; every fair vertex must reach every fair vertex.
This independently verifies the diameter upper bound without using the
primary diameter routine.

Together with the ordinal reduction, complete domain and full graph
enumeration, these terminating exact checks supply the computational proof
of the theorem. A negative result from an interrupted run would not do so.

## A positive strict example needing five exchanges

The columns are goods 0 through 4. Every row below is positive and strict.

| Agent | g0 | g1 | g2 | g3 | g4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 3 | 1 | 2 | 4 | 5 |
| 1 | 1 | 4 | 5 | 2 | 3 |
| 2 | 4 | 3 | 5 | 2 | 1 |
| 3 | 1 | 2 | 3 | 4 | 5 |

The full fixed-size domain has 60 states, of which 15 are EF1 for these
rankings. Its complete graph has diameter five. The following shortest
path uses owner vectors (agents and goods are zero-based):

```
03123 -> 23103 -> 23130 -> 23031 -> 03231 -> 02331
```

The independent deletion checker reconstructs all 15 fair states and
breadth-first search confirms that the endpoints have distance five.
Each arrow is one exchange. Because the whole graph depends only on weak
orders, every utility profile with these same strict rankings has the same
15 states and the same lower bound; this is not an equality-sensitive
numerical example. No claim that these endpoints are greedy is needed for
the full-EF1 diameter theorem.

## Run the proof and construct paths

From the repository root, standard-library Python 3.10 or newer:

```sh
python3 projects/fair-round-swaps/three_singletons_one_pair.py --diameters
python3 -m unittest discover -s projects/fair-round-swaps -p test_three_singletons_one_pair.py -v
```

The first command prints a JSON census, a diameter witness, and the strict
example's actual five-exchange path. In this run the diameter census
completed in 10.684 seconds; the connectivity-only census took 0.825
seconds. These are observations, not a performance guarantee. The default
600-second limit returns `INCOMPLETE` with exit status 2 if coverage does
not finish; it never labels partial coverage universal. `--seconds 0`
exercises that boundary.

The final combined project suite passed all 53 tests in 82.449 seconds,
including the independent unaggregated census and Boolean five-step
reachability check. Syntax, whitespace and module-size checks passed.

`path(profile, start, target)` in
[three_singletons_one_pair.py](three_singletons_one_pair.py) takes four
rows of five exact nonnegative integers or `Fraction` values and two
owner vectors. It returns a shortest EF1 exchange path, checking both
endpoints. An invalid size vector or unfair endpoint is rejected. The
implementation still returns `None` for a disconnected graph if one is
ever supplied through a changed model; the completed theorem says this
branch cannot occur on valid current inputs. Floating-point utilities
are rejected rather than silently rounded.

This is a result for one pair and three singletons, not a construction for
several complete rounds or for the seven-good `(1,1,1,2,2)` boundary.
The latter still needs a new argument or its own exact obstruction.
