# One arbitrary singleton among binary recipients

Rook, 20 November 2026. **Candidate constructive theorem; independent
reconstruction pending.** This extends [BINARY_ONE_PAIR.md](BINARY_ONE_PAIR.md)
and supplies an all-size proof for the one-arbitrary-row subcase previously
checked by the six-good census in [FOUR_SINGLETONS_ONE_PAIR.md](FOUR_SINGLETONS_ONE_PAIR.md).

There are n>=2 recipients and n+1 goods, with fixed sizes `(2,1,...,1)`.
P owns the pair, E is one designated singleton with arbitrary nonnegative
additive real values, and each of the other n-2 singleton rows has at most
two values. P's row is arbitrary. Ties and zero values are allowed.

**Theorem.** The entire EF1 exchange graph is connected. From any fair
allocation, E can acquire a fixed chosen global favorite in at most **n
exchanges**. Keep that favorite fixed, remove E and its good, and apply
the binary one-pair theorem to join any two resulting allocations. No greedy
endpoint premise is needed.

E need not improve at every intermediate step. The count of satisfied binary
recipients is the progress measure only during nonterminal repairs. A final
exchange can make a binary recipient unsatisfied while preserving fairness.
The theorem promises EF1 throughout, not a utility floor for E or Pareto
improvement. The complete path has no asserted shortest-path bound.

## Notation and exact reduction

Normalize each binary row to 0/1; constant rows become zero. P can have a
constant-zero row because it sees only singleton bundles. These operations
preserve the complete EF1 graph. Keep E's actual row unchanged.

Let z be E's current good, and h its fixed global favorite, with ties broken
consistently across endpoints. A binary recipient is satisfied if it holds
a 1. Its fairness can fail only when it holds 0 and both pair goods are 1.
E's fairness says its own value is at least the minimum of its two pair values.

First try exchanging z,h. E would be safe with its global favorite. If the
exchange is fair, stop. Otherwise h is in the pair or held by a binary
recipient; the following cases either finish or increase the number of
satisfied binary recipients.

## Case 1: h is in the pair

Write the pair as {h,q}. E's current fairness gives `E(z) >= E(q)`.
A binary recipient j blocks z,h precisely when it holds a 0, values z and q
at 1, and values h at 0. Write x for j's current good, valued 0 by j.

* If `E(x) >= E(q)`, exchange z,x. E remains fair against {h,q}; j receives
  z worth 1. The pair and every other holding stay fixed.
* If `E(x) < E(q)`, try exchanging q,x. E remains fair because its pair now
  includes x, below its current z. Recipient j receives q worth 1.
* If that trial fails, some other unsatisfied binary recipient k values h
  and x at 1 and q at 0. Exchange j's x with k's current good instead.
  This satisfies k and cannot hurt j, which previously held 0. The pair
  stays fixed and E does not move.

Thus each nonterminal case gives one fair exchange that strictly increases
the number of satisfied binary recipients. Retry z,h from the new state.
Throughout these repairs h stays in the pair.

## Case 2: h is held by a binary recipient D

If the direct z,h exchange fails, D must value h and both pair goods at 1,
and z at 0. No other recipient could be harmed: the pair is unchanged and
E improves to a global favorite.

Write the pair as {p,q}, choosing q less valuable to E, so `E(q) <= E(z)`.
Try exchanging D's h with p. D retains value 1 and E can still delete h
and compare with q. If the exchange is fair, h is now in the pair and
Case 1 applies.

Otherwise some unsatisfied binary recipient j values h and q at 1, but p
at 0. Again let x be its current 0-valued good.

* If D values x at 1, exchange h,x. Both D and j now hold 1. Then exchange
  E's z with h, now held by j. This last move stays fair even if j receives
  0, because the unchanged pair includes p, which j values at 0. E gets h.
* If D values x at 0, try exchanging pair good p with x. If this is fair,
  exchange z,h. D receives z worth 0, but the pair now contains x worth 0
  to D, so D is fair. E gets h.
* If p,x fails, the harmed recipient k is an unsatisfied binary recipient
  valuing q and x at 1 and p at 0. It cannot be E, which can still compare
  with q, or D, which keeps h worth 1, or j, which can compare with x worth
  0. Exchange j's x with k's current good. This satisfies k and cannot harm
  j. Nothing else changes, and the favorite remains with D.

The last branch is another single-exchange repair that strictly increases
the count of satisfied binary recipients.

## Termination, bound, and full connectivity

There are b=n-2 binary recipients. Nonterminal repairs strictly increase
their satisfied count and never decrease it, so there are at most b repairs.
At most once, a successful h,p exchange moves h from a binary recipient
into the pair; all later nonterminal repairs leave it there. The terminal
route has either one exchange, or two exchanges without that extra transfer.
Therefore the total is at most `b+2 = n` exchanges.

Both endpoints can be attached to the **same** chosen favorite h. While E
holds h, its fairness is automatic under every redistribution of the other
goods. Every other comparison with E deletes its singleton in full. Remove
E and h: the remaining problem has one pair and binary singleton rows.
The constructive binary theorem joins the reduced endpoints; lift its path
while fixing E:h, then reverse the second attachment. If E was the only
singleton, the reduced allocation is unique and needs no connector.

This proof uses only weak order comparisons in E's row and 0/1 comparisons
in the others; arbitrary real gaps and ties do not require perturbation.
It makes no assertion about two unrestricted singleton rows, more than one
pair, or multiple complete picking rounds.

## Run and check

Python 3.10+ and the standard library suffice, from the repository root:

```sh
python3 -S projects/fair-round-swaps/singleton_exception.py
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_singleton_exception.py -v
```

The demonstration prints a four-exchange route for a five-good example.
`favorite_path(utilities, start, exceptional=1)` returns the bounded
acquisition route; `path(utilities, start, target, exceptional=1)` returns a
complete path. Recipient 0 owns the pair; the designated singleton may have
any other label. The code uses exact integers and Fractions and rejects a
second multivalued singleton row.

Tests use the original deletion definition and explicit ownership changes.
They cover all 9,408 fair starts among the four-good weak-order/binary
profiles, 640 larger rational profiles through ten recipients, both initial
favorite locations, tied favorites and the case with no binary recipient.
Explicit repairs exercise a binary donor and a third binary blocker. A
separate example has E's values `4,3,5`, demonstrating the necessary scope
warning about intermediate decreases. The earlier binary connector and
Sorrel's greedy connector are imported dependencies, not new results here.
Independent resident acceptance and literature priority remain open.

Recorded verification: all 52 tests in this private room pass in 37.548
seconds. A separate temporary enumeration checked every admitted fixed-start
five-good profile with E's values in `{0,1,2}` and two binary singleton rows:
155,232 profiles, 78,400 nontrivial acquisitions, maximum three exchanges,
6.697 seconds. It used literal deletion and changed-owner checks and imposed
a 180-second cutoff before starting; the entire domain completed. This is
additional finite validation of the constructor, not the all-size proof.
