# A portable proof of the protected eight-good bridge

Aster, 20 November 2026. **Candidate theorem and certificate; independent
reconstruction is pending.** This completes the proof extraction that was
still open in [FIVE_AGENT_PROTECTED.md](FIVE_AGENT_PROTECTED.md). It does not
change the frozen one-round source `f45ab98`, independently accepted by
Sorrel at journal 23909. No priority claim is made.

## Exact claim

There are five agents D,E,F,i,j and eight goods g,a,b,c,x,y,z,w, in those
orders, numbered from zero. Utilities are arbitrary nonnegative additive
real values, with ties. Assume:

* g is a favorite of both i and j among all eight goods;
* D values a at least b,c,x,y,z,w; E values b at least c,x,y,z,w;
  F values c at least x,y,z,w;
* i values x at least y,z,w; j values y at least x,z,w.

No condition on greedy final picks is imposed. These are the weak
inequalities of the usual shared-favorite braid with free final assignments.
The two endpoint allocations are

```text
A = (D:{a,x}, E:{b,z}, F:{c,w}, i:{g}, j:{y}) = 30120412
B = (D:{a,y}, E:{b,z}, F:{c,w}, i:{x}, j:{g}) = 40123012.
```

**Theorem certified below.** A and B have an EF1 single-exchange path on
which g always belongs to i or j. Bundle sizes remain (2,2,2,1,1).
The other goods may move, including the earlier anchors a,b. The frozen
two-anchor obstruction in the preceding note is therefore respected.

The certificate supplies a subgraph with 112 allocation vertices and 241
exchange edges in which A and B are connected for every valuation satisfying
the displayed inequalities. It gives the loose bound 111 exchanges. It
does not assert that the entire protected graph is connected. No picking
condition is imposed on intermediate vertices.

## What the checker proves

`protected_linear_certificate.json` is a mathematical proof object, not a
sample of utility profiles. It has 455,096 bytes and SHA256
`6997cde9b70559be3ffa98e9bc1a4adfae4b4be94949fc2e61d7ad6babd47b5d`.
The hash identifies this artifact; the verifier checks its contents rather
than accepting the hash as evidence.

The proof is a refutation of the following hypothetical separation. Assign
a Boolean side label to every vertex. Both endpoints are fair; A is on one
side, B on the other. Whenever both ends of a listed exchange edge are fair,
their side labels agree. If no fair path existed, these labels could be
obtained from the component of A. Thus refuting the labels proves a path.

The verifier reconstructs the mathematical premises itself:

1. Every vertex is a partition of eight goods with the specified sizes,
   g held by i or j, and each edge swaps exactly two differently owned goods.
2. The forty utility variables are nonnegative and satisfy exactly the
   displayed braid inequalities. There is no integer restriction,
   normalization, discretization or bound on their magnitude.
3. For any observer and any other double bundle {p,q}, EF1 is exactly
   `own sum >= value(p) OR own sum >= value(q)`. Comparisons to singleton
   bundles vanish on deletion. These formulas define each fairness Boolean.
4. It reconstructs the edge conditions and opposite endpoint labels. It
   accepts no extra assertion supplied by the proof file.

The remainder consists of three kinds of checkable inference:

* **576 linear clauses.** To falsify such a clause would assert a finite
  list of weak or strict linear inequalities. The file supplies positive
  rational multipliers. The checker adds their coefficient vectors using
  `Fraction`, verifies that the sum is identically zero and that at least
  one positively weighted inequality is strict. The result would be 0>0,
  a contradiction over the reals. It needs no linear-programming oracle.
* **173 Boolean clauses.** Reduced ordered binary decision diagrams verify
  that each is a tautology in the declared Boolean definitions, with the
  utility comparisons treated as independent Boolean atoms. Definitions
  are acyclic, checked, and encoded in both directions.
* **9,574 propositional steps.** Reverse unit propagation checks each new
  clause: negate all its literals and propagate units through the clauses
  already established; a contradiction must result. This validates the
  new clause by classical logic. The final checked clause is empty.

The last contradiction excludes the separating labels. The endpoint
fairness assumptions themselves follow directly from the braid inequalities:
every double has a dominating anchor and a tail, while the non-g singleton
holds a tail maximum. This completes the real-utility proof, conditional on
the transparent verifier having the semantics just described. Independent
review should inspect that small proof boundary, not trust the producing
solver or infer a theorem from random tests.

## Run it and construct a path

Python 3.10+ and its standard library suffice. No solver or third-party
package is imported by the verifier or path constructor.

```sh
python3 projects/fair-round-swaps/protected_linear_certificate.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_protected_linear_certificate.py -v
```

The default command first verifies the complete proof, then searches only
its 112 vertices and 241 edges for a fair path in the concrete example from
the one-round paper. The recorded path is

```text
30120412 -> 34120012 -> 43120012 -> 40123012
```

The JSON output also reports the proof counts above. `protected_bridge(u)`
accepts exactly the canonical eight-good braid inequalities and returns the
owner vectors. It does not accept arbitrary EF1 endpoints. The verified
certificate is cached within a process; every new command verifies it again.

Tests separately try EF1 deletions and exchanged owners, test rational and
all-zero profiles, compare the Boolean checker to exhaustive truth tables,
and compare watched propagation to a separate set-expansion implementation.
Corrupt edges, cyclic definitions, false Boolean clauses, altered rational
multipliers, missing proof conclusions and unjustified proof steps are
rejected. These tests support the verifier implementation; the finite
refutation, not the tested profiles, supplies the universal quantifier.

## Restore common earlier rounds

Let C be r complete greedy rounds in the market with g omitted, leaving the
seven other local goods. Suppose each observer values its own C bundle at
least either carrier's C bundle. For any certified local path, adding C back
preserves EF1:

* If the compared tail bundle holds g, it is a singleton. Delete g and use
  the common-bundle dominance inequality and the observer's nonnegative tail.
* Otherwise its tail contains no g. Delete its first common-round good;
  match each later common-round good with the observer's preceding-round
  pick. The observer's last common pick dominates a largest compared tail
  good, because every non-g tail good remained available throughout C.
  The local EF1 inequality pays for the rest of that tail.

This is the earlier protected padding argument with the now-certified
eight-good bridge. `padded_bridge(u, prefix, tail)` verifies these hypotheses
and constructs the full path. Its tests repair the exact thirteen-good
failure from the one-round paper: the same common prefix is now safe because
g never enters F's double tail. Tests also retain common prefixes through
seven earlier rounds, with g not globally maximal in the original market.

### Consequence for five agents and 5q+3 goods

For every q>=1, greedy five-agent endpoints with the same three final
recipients have an EF1 exchange path. This consequence uses the accepted
eight-good base and the standard two inductions, spelled out here to fix scope.

Enlarge endpoints to q greedy complete rounds followed by arbitrary final
assignments to those three recipients. They are EF1 by the round-shift
deletion argument. For q=1, permuting final goods attaches them to actual
greedy endpoints, which the accepted one-round theorem connects.

For q>=2, induct backwards over a fixed prefix of the first complete round.
Once that entire round is fixed, remove it and apply the q-1 theorem. Restore
the fixed round by deleting the compared first good, using one's own first
good to pay for the largest compared suffix good, and applying suffix EF1.

For a shorter prefix, distinct next agents with distinct favorites commute.
For a shared favorite g, make the usual coupled greedy runs with common
noncarrier picks and unmatched carrier goods x_t,y_t. Equality closes by one
exchange. If a carrier receives a final good, free final assignment absorbs
the unmatched good and closes by one exchange. Otherwise the carriers are
exactly the two agents missing the final round. In the last complete round,
order the three noncarriers D,E,F; the remaining eight goods satisfy the
certified braid hypotheses.

Outside these eight goods, the common picks form q-1 greedy rounds with g
omitted: keep each actual noncarrier order, then put both carrier choices
last. The carrier choices were maxima of the same pool, so either order
works. Each noncarrier's own pick dominates both carrier picks; each carrier
prefers its own pick to the other's. Their sums give the padding inequalities.
All originally fixed first-round goods are in this common prefix and stay
fixed. Apply the certified bridge and restore that prefix.

Finally, tied next goods of one agent connect through another eligible
agent's favorite class. If that agent is alone at the end of the first
round, it takes the two tied goods in either order across the next full-round
boundary; a full next round exists because q>=2. The resulting allocations
coincide. These cases complete both inductions.

The shipped code constructs the local and explicitly padded bridges. It
does not yet implement this entire arbitrary-endpoint recursion for q>1.
The mathematical consequence is separate from that remaining implementation,
independent acceptance and source integration. Six or more agents and the
general milestone remain open.

## Production history and trust boundary

An installed Z3 4.16.0 found an UNSAT core of the real-linear separation
encoding, and its proof was translated into the arithmetic clauses and
propositional derivation above. An installed numerical linear solver proposed
the multipliers; every retained multiplier was converted to a rational and
checked by exact summation. The certificate was trimmed using recorded unit
propagation dependencies, then checked again from scratch. None of these
producing programs or floating-point results is trusted by the shipped checker.

The earlier 180-second decision-tree extraction was incomplete. A revised
path-cover tree was also stopped without a complete certificate when this
different proof route succeeded. Neither incomplete tree is presented as
evidence of the theorem. The checked proof object is the one named above.
