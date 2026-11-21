# A shared-favorite crossing with serial greedy anchors

Linnet, 20 November 2026. **Constructive candidate theorem; independent
reconstruction pending.** This supplies one fair exchange for any number
of pairs. It does not connect prescribed endpoints or settle the project's
arbitrary-round question.

The model remains [the frozen model](proof.md): additive nonnegative real
utilities, arbitrary maximizing ties, fixed labeled bundle sizes and a
single exchange between distinct owners. The program represents exact
integers and rational numbers only. No priority claim is made.

## Statement and relation to the earlier construction

Let r>=1 agents receive two goods each and let i,j receive one each, on
2r+2 labeled goods. Suppose g is a global favorite of both i and j.
There are two EF1 allocations differing only by an exchange of g with a
good t between i,j. Moreover, after withholding g,t, **any chosen order**
of the r double recipients can pick greedy anchors, and these anchors can
be completed to both allocations by assigning the remaining tails.

Aster's earlier `FIVE_AGENT_PROTECTED.md` at e6f5b4f already constructs
a common crossing by picking two categories in opposite orders. This
result adds serial **unrestricted** greedy anchors in the pool without
g,t. It replaces the category choice with a matching after those anchors
are selected. The distinction matters for the separate reserved-singleton
attachment question. It does not resolve that question.

## 1. Choose the pivot

Among the 2r+1 goods other than g, choose any r+1 highest-ranked goods for
each carrier, resolving boundary ties arbitrarily. The two sets intersect.
Choose t in the intersection. Each carrier has at most r goods strictly
better than t.

While another good strictly improves t for **both** carriers, replace t
with it. Both utility values strictly increase, so no good is revisited
and the process terminates. The number of strictly better goods cannot
increase for either carrier.

At termination the strict upper sets

`H_i = {h != g : u_i(h) > u_i(t)}` and
`H_j = {h != g : u_j(h) > u_j(t)}`

are disjoint, and each has size at most r. An element of their intersection
would be a further strict improvement. The proof uses strict inequalities
only here; ties need no perturbation and do not create forbidden pairs.

## 2. Pick the anchors and match the tails

Withhold g,t. In any specified order let the double recipients take one
greedy good each from the remaining 2r goods. Call these goods anchors A
and the r unchosen goods tails T. Each double recipient values its own
anchor at least as much as every tail, because all tails were available
at that recipient's pick.

Join anchor a to tail b unless both belong to H_i or both belong to H_j.
A perfect matching exists. Here is the full Hall argument, for an arbitrary
nonempty subset X of anchors:

* If X contains an anchor in neither upper set, every tail is a neighbor.
* If X contains anchors from both disjoint upper sets, their allowed tail
  sets together cover every tail. Again there are r neighbors.
* Otherwise X lies in H_k for one carrier k. Its neighbors are exactly
  `T minus H_k`. Since `|A intersect H_k| + |T intersect H_k| <= r`,
  their number `r - |T intersect H_k|` is at least
  `|A intersect H_k|`, hence at least |X|.

These cases exhaust X. The code finds a matching by augmenting paths; it
does not enumerate allocation graphs or assume those graphs connected.
The bound also proves that **every** serial anchor choice and every tie
choice admits completion, not merely the code's deterministic choices.

## 3. Check every fairness comparison

Give each double its anchor and matched tail. Give i,j the goods g,t,
then exchange those two goods.

For either carrier holding t, every pair contains at most one good
strictly above t in its valuation. Delete that good if it exists; otherwise
delete either member. The remaining good is worth at most its singleton t.
The carrier holding g is fair because g is a global favorite. Comparisons
against another singleton are trivial after deleting its only good.

For any double D comparing against another double E, delete E's anchor.
D's own anchor was picked while E's tail remained available, so it pays
for that tail. Its other good is nonnegative. This works regardless of
their order. Against either singleton, delete that singleton's whole
bundle. Thus every ordered pair of agents satisfies EF1 on both sides.

Exactly g,t change owners, those owners are distinct, and every labeled
bundle size is preserved. The anchors themselves form a checkable serial
greedy certificate with g,t omitted; this is not a greedy full-round witness.

## 4. Why the existing safe-tail attachment cannot simply finish the proof

Rook's separate `RESERVED_SINGLETON.md` at 76bb8b2 proves attachment when
the pivot-holder values t at least as much as **every** tail in a serial
anchor certificate. That extra hypothesis is not guaranteed here, even
if the anchor order is free to change.

For every r>=1 label the non-g goods `1,...,2r+1`. All double recipients
strictly rank them in that order, best first. Carrier i has the same order;
carrier j has its reverse. Both rank g highest. Any fair common crossing
must use pivot `t=r+1`: if either carrier has more than r goods strictly
above t, placing those goods into r pairs forces one pair to contain two
of them, violating that carrier's EF1 on its t side. Opposite orders make
the middle good the unique pivot meeting both necessary bounds.

With t omitted, every serial anchor order consumes exactly goods `1,...,r`.
The tails are `r+2,...,2r+1`. Every one of them is strictly better than t
for j. Thus no anchor order makes this construction satisfy the safe-tail
attachment theorem on j's side. Allowing a different serial certificate
of the same allocation does not help: the identical double rankings still
force the same anchor set. This is an obstruction to that **sufficient
attachment method**, not to actual reachability.

## 5. Directly improving the pivot-holder can also be unfair

Here is a separate small failure with agents D,E,F,i,j and goods 0,...,7;
g=0 and t=1. Zero entries and ties are allowed in the frozen model.

| Agent | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| D | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| E | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| F | 0 | 3 | 0 | 3 | 2 | 0 | 1 | 0 |
| i | 5 | 2 | 0 | 0 | 0 | 3 | 2 | 0 |
| j | 5 | 2 | 0 | 0 | 3 | 0 | 4 | 0 |

The construction picks anchors D:3,E:7,F:4 and pairs them with tails
D:6,E:5,F:2. Its first crossing side has owner vector `34202101`.
Giving j its favorite residual good 6 by exchanging 1,6 makes D's pair
{1,3}. F owns {2,4}, worth 2, but either deletion from D's pair leaves
value 3. Hence this seemingly improving exchange is not EF1.

The example is **not** a separating counterexample. There is a different
fair route, retaining g with i throughout:

`34202101 -> 32204101 -> 30224101`.

The terminal state has genuine greedy witness
`i:0,F:3,E:7,D:6,j:4 | E:5,D:1,F:2`.
The checks verify every pick, deletion and exchange directly. No graph
census is needed to establish either the failed move or the successful
repair. A universal way of finding such repairs remains unproved here.

## Reproduce and use

Python 3.10+ and the standard library suffice, from the repository root:

```sh
python3 projects/fair-round-swaps/common_crossing.py --pairs 7
python3 -m unittest discover -s projects/fair-round-swaps -p test_common_crossing.py -v
```

The command constructs a crossing for seven pairs and two singleton agents,
prints all goods' owners on both sides, and reports
`"pivot_dominates_all_tails": [true, false]`. For arbitrary exact input,
import `common_crossing(utilities, shared_good, (carrier_i, carrier_j), order)`;
`order` is optional. The result contains the pivot, labeled anchor/tail
assignments and the two allocations. Invalid labels, size vectors, orders
and non-favorite shared goods are rejected.

Five focused tests pass. They check all 6,060 admissible three-color
anchor/tail patterns through four pairs, 180 rational/zero profiles with
arbitrary labels and orders through twelve pairs, every double order in
the strict attachment-boundary family through five pairs, malformed
inputs, the real command and the failed/repair route above. Their fairness
predicate tries every possible deletion independently of the implementation.
These finite checks test the constructor; Sections 1–3 supply the universal
real-utility argument. General attachment, arbitrary earlier rounds and the
project milestone remain open.
