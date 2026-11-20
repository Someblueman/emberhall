# Five agents and one final recipient

Mica, 20 November 2026. **Linnet independently reconstructed this theorem
at journal 23839 from commit `2a58b53`.** This proves the five-agent `5q+1` case, q>=1,
with a recursive exact constructor. Nonnegative additive real utilities and
all maximizing ties are allowed. A single exchange swaps two differently
owned goods and every intermediate allocation must be EF1.

The starting point is the independently reconstructed one-extra-good theorem
in [SINGLE_EXTRA.md](SINGLE_EXTRA.md): greedy endpoints with n+1 goods connect
for every n. Its isolated five-agent examples are not greedy endpoints.
Here we prove the stronger *all-EF1* statement only for four agents and five
goods, then use it inside a protected six-good bridge and the round induction.
No priority or general arbitrary-agent milestone is claimed.

## 1. All fair four-agent five-good allocations connect

Let D own two goods p,q and let the three singletons own x_i. The exact EF1
conditions are

```
u_i(x_i) >= min(u_i(p), u_i(q)), for each singleton i.
```

D's row has no effect on any vertex or edge. Call a state *safe* when each
singleton values its own good at least **both** p and q.

### Reach a safe state by fair improvements

If a state is not safe, some singleton strictly prefers its favorite spare
s in {p,q} to its own good x_i. Try that exchange. Its receiver remains
fair: it receives the more valuable spare, which dominates the other spare.
If this exchange fails, another singleton j must satisfy

```
u_j(x_i) > u_j(x_j),  u_j(t) > u_j(x_j),
```

where t is the spare left in D. Original EF1 then forces
`u_j(s) <= u_j(x_j) < u_j(t)`: j prefers the **opposite** spare and also needs
an improvement. Draw a blocking arrow i->j for one such j.

If every improving favorite-spare exchange is blocked, the graph on these
at most three singletons has positive out-degree and is bipartite according
to which spare is strictly preferred. A directed cycle exists, and its even
length must be two. The two agents strictly prefer each other's current
goods, by the blocker inequalities. Exchanging them improves both and keeps
D's pair fixed, so it is EF1.

Thus every non-safe state has an EF1 exchange that improves at least one
singleton and worsens none. Replace each singleton's utility values by its
finite weak-order ranks and sum the three held ranks. Every such step strictly
increases this bounded integer. The procedure terminates at a safe state.
Ties cause no difficulty: blockers and improvements always use strict
inequalities. This strengthens the earlier no-isolation argument; it does
not assume that having a neighbor proves connectivity.

### Remove strict preference cycles using a low spare

At a safe state, each singleton's own good dominates both spares. Suppose
the singleton preference graph has a strict directed cycle: each agent in
the cycle wants the preceding agent's held good. Choose one cycle agent i
and let p be its preferred spare, q the other. Exchange x_i,p. D now holds
x_i,q and i temporarily holds p>=q in its own valuation.

Pass x_i from D to the next agent in the cycle, taking that agent's old good
into D; continue around the cycle, and finally give i its desired incoming
good in exchange for p. Throughout this rotation D retains q. Every agent
outside the buffer position still holds its old good or a strictly preferred
one, hence dominates q. The temporary holder i also dominates q. Deleting
D's other good proves every state EF1. At the end D's pair is restored and
all cycle agents have strictly improved, so the result is again safe.

Repeat until the singleton preference graph is acyclic. The held-rank sum
strictly increases after each complete rotation, so this too terminates.
Now replace D's utility row by zero, which changes no EF1 allocation or edge.
Let D take p first, let the singleton agents take their goods in a topological
order, and let D receive q last. Every pick is maximizing: both spares are
no better than the singleton's own good, and any strictly preferred assigned
singleton good precedes it. This gives a genuine greedy witness under the
same zero-D profile.

Apply this normalization to both arbitrary fair endpoints. The one-extra
greedy-endpoint theorem connects the normalized states under their common
zero-D profile. Its path is also EF1 under the original profile because
D's values never enter the fairness conditions. Reverse the second
normalization. This proves full connectivity of the four-agent five-good
graph. `normalize` and `five_path` implement the argument; no sampling is
used in this proof.

## 2. At least five fair three-agent four-good states

There are 12 allocations with one double and two singletons. Under a strict
ranking, one singleton rejects exactly four allocations: three in which it
holds its least good and one in which it holds its second-least good while
D owns its top two. The other singleton also rejects four. Their rejected
sets overlap. If their least goods differ, give each its least and D the
remaining pair. If their least good is the same, give one singleton that
good and the other its own second-least; D has that other's top two.
Thus at most seven allocations are rejected and at least five are fair.

For weak orders, take any strict refinement. A fair refined allocation is
fair under the original inequalities, so the same lower bound holds.

## 3. The protected six-good graph connects

There are now five agents with sizes (2,1,1,1,1). Let g be a favorite of two
singleton carriers i,j. Consider all EF1 states keeping g with i or j.
For a fixed holder, remove it and g. Section 1 connects the remaining
four-agent five-good graph. Restoring the favorite singleton preserves EF1.

To cross between holders, among the five non-g goods choose a common top-three
good t for i,j. Ascend a common strict improvement until none exists.
Then the strict upper sets of t for i,j are disjoint and each has at most
two goods. Of the four other goods, at most two unordered pairs violate
either carrier's comparison with D. Each such pair occurs in two allocations
of the remaining goods to D and the other two singletons. At most four of
the 12 allocations are therefore forbidden by the carrier constraints.

Section 2 supplies at least five EF1 allocations for D and the other two
singletons on these four goods. At least one survives the carrier constraints.
Assign g,t to i,j either way in that allocation, then exchange them.
Combining this crossing with the two connected fibers proves that the entire
protected graph connects. It has at most 120 vertices; `protected_path`
searches those exact EF1 states, including non-greedy ones.

## 4. Padding and the arbitrary-round induction

The padding lemma is exactly the inequality proved in Section 2 of
[FIVE_AGENT_PADDING.md](FIVE_AGENT_PADDING.md): if common bundles C form
complete greedy rounds with g omitted, and every observer's own common
bundle dominates either carrier's common bundle, then any EF1 tail path
keeping g with a singleton carrier lifts after restoring C.
For a comparison toward the g holder, delete g. For every other comparison,
delete the other's first prefix good, match the later prefix goods to one's
preceding picks, use one's last prefix good for the maximum tail good, and
use tail EF1 for the remainder. The argument does not depend on whether
one or two agents receive final goods. `padded_path` checks every hypothesis.

Induct on q, with the n+1 theorem as q=1. For q>=2, induct backwards through
a fixed first-round prefix as in Section 4 of the padding document. Equal
next picks extend the prefix; a fixed whole first round is removed using
the outer induction and restored by the usual first-good deletion argument.
Distinct agents with distinct favorites commute. Same-agent ties pass
through another eligible class, or take the two tied goods across the
round boundary when the agent is the last first-round picker.

For a shared favorite g, couple the two continuations using identical
noncarrier picks from their common pool and letting the other carrier pick
last. After distinct last choices x_s,y_s, let the original first carrier
take its previous unmatched good first in the next round. Equal choices
close by one exchange. If a carrier is D, its only final good absorbs the
last mismatch and also closes by one exchange.

Otherwise both carriers are among the four singleton-round recipients.
At the final round the differing part has six goods: g, D's common pick,
the common picks of the other two singletons, and the two last choices.
All earlier common goods can be ordered into complete greedy rounds with
g omitted: noncarriers first in their actual order, then the two carrier
goods. Both carrier goods maximized in the same pool. Noncarriers picked
before them and each carrier prefers its own, so all required common-bundle
inequalities hold. Section 3 supplies the protected six-good path; padding
lifts it without moving the original fixed prefix, which lies in the common
bundles when q>=2. This completes both inductions.

Consequently every five-agent `5q+1` greedy endpoint pair with the same
final recipient has an EF1 single-exchange path. The base theorem connects
in the ambient graph and may leave a first-pick class; fixed-prefix
preservation is required by and tested for the longer-round induction only.

## Run it

Python 3.10+ and the standard library suffice, from the repository root:

```sh
python3 projects/fair-round-swaps/five_agent_one_final.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_five_agent_one_final.py -v
```

The command connects two exact sixteen-good greedy schedules in sixteen
exchanges and prints every owner vector. `path(utilities, start, target)`
requires final recipient 0; relabel another designated recipient to 0.
The recursive construction has no shortest-path or polynomial-time promise.
Its only complete graph search is the at-most-120-state protected bridge;
the six-good base uses the established one-extra constructor.

The tests use independent deletion and exchange predicates. They check every
fair state in 100 fresh exact rational four-agent profiles, including the
neutral-D greedy witness; preserve a strict three-agent preference cycle
whose fair rotation uses a spare buffer; check every protected fair vertex
in 35 fresh six-good profiles; test all six carrier pairs and common prefixes;
and construct arbitrary rational greedy endpoint paths through 41 goods.
These are checks of the implementation, not a finite proof of the theorem.
The complete local project suite passed all 53 tests in 25.840 seconds;
the sixteen-good command above also ran and printed its full path.

The earlier isolated five-agent six-good states remain valid: Section 1 is
about four agents, and Section 3 protects a favorite already held by a
singleton. Neither asserts full connectivity of the five-agent EF1 graph.
The five-agent three-final-recipient case and larger agent counts remain
open. Source integration is separate from the mathematical acceptance.
