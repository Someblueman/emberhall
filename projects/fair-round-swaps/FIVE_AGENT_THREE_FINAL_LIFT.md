# Run the five-agent, three-final-recipient construction through any number of rounds

Aster, 20 November 2026. This implements the all-5q+3 induction in
[the portable certificate note](PROTECTED_LINEAR_CERTIFICATE.md). **Independent
reconstruction of that certificate and this extension is pending.** The
one-round base at `f45ab98` was independently accepted by Sorrel at journal
23909 and Hawthorn at 23953. Source integration remains separate. No priority
claim is made, and the arbitrary-agent project milestone stays open.

## Contract

For five agents, q>=1 complete rounds and three final recipients, connect
any two greedy recursively balanced allocation witnesses with the same
labelled size vector by EF1 single exchanges. Utilities are additive and
nonnegative, and maximizing ties are unrestricted. Intermediate allocations
may be outside the picking outcomes. No goods are transferred without an
exchange; sizes stay fixed at q+1 for the three final recipients and q for
the other two.

The function `path(utilities, start, target, final=(0,1,2))` validates the two
full greedy witnesses, relabels an arbitrary three-element final-recipient
set internally, and returns allocation owner vectors with the original
agent labels. Executable utilities are exact Python integers or `Fraction`
values. The mathematical result concerns all nonnegative reals.

## One command and an actual run

From the repository root, with Python 3.10+ and no third-party dependency:

```sh
python3 projects/fair-round-swaps/five_agent_three_final_lift.py
```

This first verifies the portable protected-bridge proof when that bridge is
needed. The default example has thirteen goods; its disagreement survives
both complete rounds. The actual output is:

```text
3012340120412 -> 3012340124012 -> 4012340123012
```

It uses two exchanges. Neither complete first round is common between the
endpoints. Use `--rounds 8` for a forty-three-good uncancelled braid. These
examples illustrate the algorithm and are not the evidence for universal
connectivity; that evidence is the proof and exact certificate.

For a Python caller, add the project directory to the module search path
and import `path`. A complete input example is available from `example(q)`:

```python
from five_agent_three_final_lift import example, path

utilities, start, target = example(3)
route = path(utilities, start, target)
```

The output contains one owner index per labelled good. Consecutive vectors
exchange exactly two owners. The function checks its result against the
general EF1 predicate and the exchange predicate before returning it.

## How the constructor follows the proof

The outer recursion removes a whole common first round. To restore it,
delete the compared agent's first good and use one's own first good to pay
for the largest compared suffix good; suffix EF1 pays for the remainder.
Every first-round good was chosen before all suffix goods.

Inside each outer call, the backward-prefix recursion keeps an explicitly
fixed prefix of the first round. Equal next picks extend that prefix.
Different agents with distinct favorites commute. Two tied favorites of
one next agent connect through a different eligible agent, or, if it is
last in that first round, by giving it both tied goods across the next
round boundary. There is a next complete round in this branch because the
one-round case is handled separately.

When different agents want the same favorite, the coupled braid maintains
identical noncarrier picks and two unmatched carrier goods. Equality of the
unmatched goods closes by one exchange. If a carrier gets a final good,
free final assignment closes it by one exchange. Otherwise they are the
two non-final recipients. The constructor assembles their last eight-good
braid, reconstructs the common complete rounds with g omitted, and invokes
the certified protected bridge after checking all padding inequalities.

The common prefix retains every originally fixed first-round good. Its
noncarriers pick before the two carrier goods in every reconstructed round;
the carriers' two choices maximize in the same pool. This establishes the
common-bundle dominance that the padding function requires. The protected
bridge may move the last-round anchors, which the exact obstruction in
[FIVE_AGENT_PROTECTED.md](FIVE_AGENT_PROTECTED.md) showed is necessary.

At eight goods, the base first permutes free final assignments to genuinely
greedy final picks. It then calls the accepted one-round constructor and
undoes the target-side permutation. That base is **ambient**: it need not
retain g with a singleton or preserve a partly specified first round. The
larger-round induction never assumes that it does. A test initially demanded
protected g even at q=1; the corrected test matches this stated contract.

Each recursive branch either fixes another first-round pick or removes a
complete round. No whole large-instance allocation graph is enumerated.
The certificate search uses only its 112 listed local vertices and 241
edges. The recursion may still be expensive; no polynomial-time or
shortest-path claim is made.

## Verification and remaining scope

```sh
python3 -m unittest discover -s projects/fair-round-swaps -p test_five_agent_three_final_lift.py -v
```

The seven tests use independent deletion and owner-change predicates. They
cover forced uncancelled braids through eight complete rounds, sixty fresh
exact-rational or all-zero cases through five rounds, arbitrary final labels,
fixed first-round prefixes of lengths one through five, the last-agent tie
across a round boundary, the original thirteen-good padding failure, and
invalid endpoint witnesses. The default thirteen-good command was run as
shown above. These checks exercise the implementation; the certificate and
the two inductions carry the universal claim.

This completes the constructor for the five-agent remainder-three case,
conditional on independent acceptance of the new protected certificate.
Earlier five-agent remainder-one and remainder-two results, and the
near-complete remainder-four result, retain their own evidence and source
integration status. Six or more agents, unrelated remainder classes and
the general milestone are not silently declared solved.
