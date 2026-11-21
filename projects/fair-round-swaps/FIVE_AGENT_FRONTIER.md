# Five agents: where the four-agent proof cannot simply continue

Sorrel, 20 November 2026. This is a proved obstruction to a proposed proof
method, **not** a counterexample between greedy endpoints. The five-agent
seven-good greedy-endpoint question remains unresolved here. No priority
claim is made.

The four-agent argument used connectivity of the **entire** three-agent
five-good EF1 graph after removing a protected singleton. Removing a
singleton from the next case leaves four agents and six goods. That entire
graph can already be disconnected. The construction below goes further:
with five agents, the graph keeping a common favorite with two singleton
carriers can itself contain an isolated state. Thus the unconditional
protected-favorite lemma also cannot be copied to five agents.

## Exact obstruction

Use seven goods numbered 0 through 6 and the following additive utilities:

| Agent | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| D | 0 | 8 | 10 | 6 | 2 | 3 | 0 |
| E | 0 | 1 | 6 | 2 | 0 | 4 | 0 |
| i | 4 | 0 | 3 | 4 | 2 | 1 | 5 |
| j | 3 | 1 | 4 | 2 | 0 | 4 | 0 |
| h | 1 | 1 | 1 | 1 | 0 | 1 | 2 |

The state is `3110204`: D={3,5}, E={1,2}, i={4}, j={0}, h={6}.
Its size vector is (2,2,1,1,1). It is EF1. Its first six goods form the
isolated four-agent example in [FOUR_AGENTS.md](FOUR_AGENTS.md); adding h's
singleton does not change any of those comparisons. Any of the thirteen
exchanges between old goods therefore still fails.

There are six new possible exchanges involving good 6. The following table
gives one violated EF1 comparison for each, after the best deletion:

| Exchange 6 with | Observer | Observed bundle | Own value | Remainder |
| --- | --- | --- | ---: | ---: |
| 0 | j | D | 0 | 2 |
| 1 | i | E | 2 | 3 |
| 2 | E | D | 1 | 2 |
| 3 | D | E | 3 | 8 |
| 4 | h | D | 0 | 1 |
| 5 | D | E | 6 | 8 |

Thus all nineteen exchanges fail. The full EF1 graph has an isolated state,
so its subgraph keeping good 6 with i or h also has that isolated state.
Good 6 is a strict favorite of both i and h. There are other fair allocations
in the same protected subgraph. This disproves the proposed extension of the
four-agent *all-EF1 protected-subgraph* lemma, with no numerical approximation.

The state is not a greedy endpoint. A first-round singleton must dominate
every good reserved for the final round. There is no possible final D good:
i values D's good 3 at 4, above its own 2, so i requires D's good 5 to be
final; j values good 5 at 4, above its own 3, so j requires good 3 instead.
This contradiction holds whichever final E good is chosen.

The complete computation has 1,260 fixed-size states, 228 EF1 states, and
components of sizes 1 and 227. Exactly 50 greedy outcomes all lie in the
large component. The protected subgraph has 90 fair states and components
of sizes 1 and 89. These counts describe this one profile, not every profile.

### Discarding isolated states is not enough

Even the four-agent six-good side graph need not have just one nontrivial
component. Use utility rows

```text
6 2 1 7 12 4
2 7 1 12 4 6
3 1 1 2  0 4
0 1 2 1  3 4
```

Its 43 EF1 states have components of sizes 2 and 41. The two-state component
is `102310 <-> 103210`; each state's only fair neighbor is the other. Neither
state is isolated, and neither is greedy. All seven greedy outcomes belong
to the 41-state component. The independent neighbor test verifies the closed
two-state component directly. A proposed repair that merely excludes isolated
states would therefore still be false.

## Recognize the correct endpoints without enumerating all orders

`greedy_witness` handles n agents and n+r goods with 0<=r<n, sizes one or two.
For each of the 2^r choices of one final good from each doubled bundle, let
p_i be agent i's first-round good and t_i its final good when present.
The allocation is a greedy outcome exactly when some choice passes all of:

1. Every agent values p_i at least every proposed final good. Those goods
   remain available throughout the complete first round.
2. The first-round precedence graph is acyclic. Add j -> i whenever agent i
   strictly prefers p_j to its own p_i.
3. The final-round precedence graph is acyclic. Among final recipients,
   add j -> i whenever agent i strictly prefers t_j to its own t_i.

Necessity is immediate from an actual greedy execution: every strictly
preferred assigned good must already have been removed at the relevant pick.
For sufficiency, execute a topological order of the first graph. All strictly
preferred first-round goods have gone, and condition 1 handles every final
good, so each pick maximizes. Then execute a topological order of the second
graph. Its precedence edges eliminate every strictly preferred remaining
good. These two orders provide the witness. Ties create no edge and need no
special tie-breaking assumption.

The final-round graph matters: two doubled agents may each prefer the other's
proposed final good. Checking only the first-round graph would accept that
impossible final assignment. The search over final-good choices also matters:
failure of one such assignment does not establish failure of the allocation.

The direct implementation is bounded by 2^r choices and polynomial graph
work per choice (at most O(n^3) here); it does not enumerate n! first-round
orders or r! final-round orders. It generalizes the single-extra-good
recognizer to multiple final recipients. It does not recognize multi-round
instances or certify a path between two endpoints.

## Reproduce and continue

```sh
python3 projects/fair-round-swaps/five_agent_frontier.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_five_agent_frontier.py -v
```

The checker prints the complete graph counts and rejection of all nineteen
neighbors. Tests use an independent all-deletions predicate, compare the
recognizer to exhaustive greedy outcomes on fresh profiles, check exact
rational gaps and ties, and reject deliberate first- and final-round cycles.

An installed symbolic solver helped investigate candidate graphs; none is
needed by this artifact. An unsatisfiable solver search for one chosen braid
shape is not presented as a universal mathematical proof. What survives is
the exact isolated-state certificate and the independently checkable endpoint
characterization above.

The next proof needs more than connectivity of arbitrary EF1 states after
removing a singleton. It could connect the greedy-containing components,
establish a smaller reachable family with a common crossing, or allow the
protected favorite to visit other recipients with a proved padding guard.
The isolated state rules out only the unconditional shortcut; its absence
from greedy outcomes prevents it from settling the actual question.
