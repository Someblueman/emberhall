# Fewest possible tail swaps with the anchors fixed

Linnet, 20 November 2026. **Constructive candidate theorem; independent
reconstruction pending.** This removes a local matching choice from the
[serial-anchor crossing](COMMON_CROSSING.md). It does not attach that crossing
to prescribed greedy endpoints or settle arbitrary-round connectivity.

## The matching theorem

There are r>=1 labeled anchors and r labeled tails. Give each good a subset
of {I,J}; the empty set and {I,J} are allowed. A tail may be assigned to an
anchor exactly when their subsets are disjoint. Any two legal bijections
connect by the **fewest possible exchanges of two tails**, through legal
bijections: exactly r-c exchanges, where c is the number of cycles in their
relative permutation, counting already correct positions as one-cycles.
The two upper sets need not be disjoint, and no assumption about the existence
of a matching is required beyond the two given endpoints.

The implementation encodes the subsets as two-bit masks: 0 means neither,
1 first only, 2 second only, and 3 both. A pair is legal precisely when its
bitwise intersection is zero. Labels distinguish goods even when masks or
utilities tie.

## Constructive proof

Fix anchors successively, without ever changing one already fixed. Process
them in the order **both, first only, second only, neither**. At an anchor a,
let s be its current tail, t its target tail, and c the current owner of t.
If s=t there is nothing to do. Otherwise c is not already fixed, since the
target bijection assigns t to a alone.

If c can accept s, exchange s,t and fix a. The following cases show that only
one kind of failure is possible, and give its repair.

**Both.** An anchor marked both can hold only an empty tail. Thus both s,t
are empty, and c accepts s regardless of its type. The direct exchange works.

**First only.** All both anchors are fixed. If the direct exchange fails,
c must be second only and s second only. Since t is legal at both a and c,
t is empty. Follow the relative permutation from a: each anchor points to
the current owner of its target tail. Its cycle C includes c and contains
no fixed anchor. The current and target tail sets within C coincide.
Let U be the first-only and empty anchors of C; let V be its second-only
anchors. There is an anchor d in U holding a tail
that is empty or first only. To prove this, suppose otherwise. Every current
tail in U would then be second only or both. None can go to V. Their number
equals |U|, so all target slots of U would be needed for them. But a's target
tail t is empty, a contradiction.

Exchange c's tail t with d's tail u. This is legal: u is empty or first only,
so c accepts it; t is empty, so d accepts it. Then exchange a's s with the
tail t now at d. This is legal: a receives its target t; d is first only or
empty, so it accepts the second-only s. Two exchanges fix a, and neither
touches any fixed anchor. All other assignments remain legal.

**Second only.** Both and first-only anchors are fixed. The owner c of t is
now second only or empty. Tail s is empty or first only, so c accepts it.
The direct exchange works.

**Neither.** Only empty anchors remain, so the direct exchange works.

Each processed anchor needs at most two exchanges, so the procedure terminates.
More strongly, every exchange splits a cycle of the relative permutation.
For a direct swap, a and c are in the same cycle by definition. In the repair,
c,d are in C, so their exchange splits that cycle. Tail t is then at d,
meaning a points directly to d in the new relative permutation; the second
exchange also splits a cycle. No exchange ever merges two cycles.

A transposition increases the cycle count by at most one. Any path from c
initial cycles to the r singleton cycles of the target needs at least r-c
swaps. Our procedure increases that count by exactly one at each step,
so it attains this lower bound. In particular it takes at most r-1 swaps.
The implementation uses no allocation graph enumeration, recursion or
external solver.

## Apply it to both sides of a fair crossing

Use r double recipients D and two singleton carriers i,j. Fix distinct goods
g,t and an anchor a_D for each double. The remaining r goods are tails.
Assume:

* g is a global favorite of both carriers;
* each double values its own anchor at least as much as every tail;
* the initial and target tail assignments are fair for a carrier holding t:
  neither carrier sees a pair whose two goods are both strictly better than t.

Mark a good with I when i values it strictly above t, and with J when j does.
The last condition is exactly the matching theorem's legality condition.
It also allows goods in both upper sets. At every step place g,t at i,j in
either order, using the same double bundles for both sides.

Every intermediate allocation is EF1. The t holder can delete the member of
any pair strictly above t, if there is one; legality forbids two such members.
The g holder is safe because g is a favorite. Each double comparing with
another double can delete the other's anchor: its own fixed anchor pays for
the other's tail. Every comparison against a singleton is safe on deletion
of that singleton. This exhausts all comparisons and uses nonnegativity when
adding a double's own tail.

Each matching exchange swaps tails owned by two distinct double recipients,
so it is an actual one-for-one exchange with unchanged labeled bundle sizes.
All anchors, g and t remain fixed on each side. Moreover, at every matching
the two sides are still joined by the single exchange of g,t. The program
returns the two synchronized paths and checks their full EF1 inequalities.

Serial greedy anchors with g,t omitted satisfy the anchor-dominance premise.
Thus the theorem applies to the output of `common_crossing` at frozen
`ac90057`. It also applies to some non-serial anchor systems with the same
explicit dominance bound. The code checks that bound rather than inventing
a greedy witness for such an input.

## A direct swap really can need the repair

Take three anchor masks `(I,J,empty)`, with tail labels 5,6,7 having masks
`(I,J,empty)`. The initial tail tuple is `(6,7,5)`, the target `(7,5,6)`.
Giving the first anchor its target by a direct exchange would leave the
second anchor holding tail 6, a forbidden J–J pair. Instead:

```
(6,7,5) -> (6,5,7) -> (7,5,6).
```

The module's five-agent, eight-good example realizes these masks as exact
utilities, with greedy anchors. Its left-side owner vectors are

```
34012201 -> 34012102 -> 34012120
```

and the right side performs the same tail exchanges with the singleton
goods reversed. Independent tests verify both paths, the actual direct-swap
failure, and every unchanged anchor and singleton good.

## What this does and does not remove

An attachment argument for a fixed crossing may choose **any** legal tail
matching: this theorem connects that choice to the constructor's matching
without losing fairness or moving an anchor. It is unnecessary to analyze
every possible matching as a separate component.

The matching still has to exist, the anchor system is still fixed, and an
attachment to a greedy endpoint still needs proof. This theorem does not
repair the safe-tail hypothesis failure or the direct singleton-improvement
failure in `COMMON_CROSSING.md`. It does not imply connectivity when anchors
also move, or connectivity of the full fixed-size EF1 allocation graph.

## Three fixed observers already break tail-only connectivity

The number of independent upper-set constraints matters. With three anchors
a,b,c and tails x,y,z, forbid just a–x, b–y, c–z. The only legal bijections
are `(y,z,x)` and `(z,x,y)`. Each transposition of either creates a forbidden
pair. These are two isolated vertices of the complete tail-matching graph.

This has an exact EF1 realization with three double recipients D0,D1,D2 and
three fixed singleton observers S0,S1,S2. Give Dk value 3 for its fixed anchor
and zero for everything else. Give Sk value 1 for its own fixed singleton
good, value 2 for anchor k and tail k, and zero for every other good. Then
all double comparisons are safe, and Sk fails EF1 exactly at forbidden pair k.
The function `three_observer_boundary` supplies the full 6-by-9 utility table
and the two fair owner vectors. The independent test checks all six possible
tail assignments and every possible tail exchange from the first fair one.

Thus an arbitrary third observer cannot be added to the matching theorem.
This does **not** separate the endpoints in the full EF1 graph: changing an
anchor or singleton good is outside this fixed slice. In a larger-agent lift,
the additional singleton observers therefore need an explicit dominance
argument, such as the earlier greedy-pick bound, rather than this lemma alone.

## Run and inspect

Python 3.10+ and the standard library, from the repository root:

```sh
python3 projects/fair-round-swaps/tail_matchings.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_tail_matchings.py -v
```

`reconfigure(anchor_masks, tail_masks, start, target)` returns the combinatorial
matching path. `start` and `target` contain one distinct integer tail label
per anchor; the dictionary supplies each tail's mask. It rejects incomplete
bijections, illegal endpoints and values outside the two-bit mask domain.

`crossing_paths(utilities, shared, carriers, crossing, target_tails)` applies
the theorem to a `Crossing` certificate from `common_crossing`, or an explicitly
constructed certificate satisfying the stated dominance bounds. It checks
labels, the size vector, both singleton favorites, the certificate's actual
owners and the two endpoint matchings before constructing the paths.

The exhaustive test includes every assignment of the four masks through four
pairs, and all 162,009 legal initial matchings, joined to a fixed legal target
for each mask assignment. Every path length is checked against an independent
relative-cycle count, not merely against an upper bound. The total also follows from
`sum(r! * 9**r for r=1,...,4)`: each matched anchor/tail pair has nine legal
mask combinations. Further tests use 120 exact rational instances through
fifteen pairs with arbitrary labels and overlapping upper sets, the explicit
two-swap repair, malformed inputs and the real command. Each mathematical
step rests on the constructive proof above; these finite checks test its code.
The separate three-observer test checks the complete restricted slice of its
boundary example, not an entire allocation graph.
