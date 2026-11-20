# Completing reserved anchors: terminal buffers and two-value utilities

Linnet, 20 November 2026. **Candidate constructive theorem; independent
reconstruction pending.** This enlarges Rook's safe-tail normalization in
[RESERVED_SINGLETON.md](RESERVED_SINGLETON.md). It does not normalize every
reserved-anchor state or settle the arbitrary-agent endpoint conjecture.

## Statement

There are r>=1 double recipients and one singleton S on 2r+1 goods, with
nonnegative additive real utilities and arbitrary maximizing ties. S owns z.
Each double D owns an anchor a_D and a tail t_D. The supplied anchor order
is greedy with z withheld, and the initial allocation is EF1. Thus each
anchor dominates every original tail in its owner's valuation.

There is also an unconditional improvement within this reserved-anchor
domain: if S prefers any original tail to z, it can acquire a **maximizing
original tail** in at most r+1 fair exchanges. This stronger conclusion
does not require either terminal guard. It keeps S above its initial
value, but need not improve S at every intermediate step. The result and
its different invariant are proved below.

Call an anchor f=a_E **terminal** when every other double D weakly prefers
its own anchor to f. The supplied order need not put E last: deleting E
from its old position and putting it last is still a greedy anchor order.
An earlier agent already dominated f; a later agent does so by the stated
condition. E's f still dominates all tails. At least the original last
anchor is terminal, but it need not meet either additional guard below.

**Theorem.** The allocation has an EF1 single-exchange path to a genuine
recursively balanced greedy endpoint, preserving all bundle sizes and never
decreasing S's utility, if any of these holds:

1. **Safe tails:** z weakly dominates every original tail for S. This is
   Rook's existing theorem and its existing implementation, with bound 2r.
2. **Low terminal anchor:** some terminal f satisfies `u_S(f) <= u_S(z)`.
3. **High terminal anchor with a safe favorite tail:** some terminal f
   weakly dominates every original tail for S, and E has a maximizing
   original tail q with `u_S(q) <= u_S(z)`. Maximization here uses E's
   values over **all** original tails, not only E's own tail.

In either new case the path uses at most **2r+1** exchanges. The bound is
not claimed sharp. These are sufficient guards, not a characterization.
No automatic-fairness condition is imposed on any double row.

**Two-value consequence.** Every reserved-anchor EF1 state normalizes for
arbitrary r when each agent's utility row has at most two distinct values.
More generally, the double rows may each have their own two values, while
S may have arbitrary values provided no original anchor lies strictly
between S's original z-value and its greatest original tail-value.
The same 2r+1 bound holds. This consequence has no additional terminal
guard to check: the proof below shows that one necessarily exists.

## Preparation in the unsafe-tail case

Only the case where some original tail is strictly better than z for S
needs a new argument. Original anchors are kept on their owners while
preparing a buffer pair belonging to E.

In case 2, let h be S's favorite original tail. Give h to E by at most one
tail exchange, then exchange z,h. Let q=f be E's retained good. The old
holder of h had a low anchor: otherwise both its goods would have been
strictly above z for S, contradicting initial EF1. E also has a low anchor.
The tail exchange is therefore fair for S. All doubles remain fair because
each can delete a foreign anchor and pay the remaining original tail with
its own anchor. After z,h, every other double can delete z from E's pair
and pay q with its own anchor, by terminality. E pays every other pair's
tail with q. S pays every original tail with h and pays q because
`u_S(q) <= u_S(z) < u_S(h)`.

In case 3, retain q as the safe favorite tail specified in the guard and
put h=f. Give q to E by at most one tail exchange, then exchange z,f.
Here f is strictly above z for S: it dominates a tail strictly above z.
Consequently E's original tail is at most z for S, by initial EF1.
Both exchanged tails are at most z, so the preparation is fair for S.
The doubles remain fair by original anchor dominance. After exchanging
z,f, E pays every other tail with its retained favorite tail q; every
other double pays q with its original anchor. S's new h pays every
original tail by the guard, and pays q.

Thus both cases reach precisely this state:

* S holds h, strictly better than its original z.
* E holds `{q,z}`, with `u_S(q) <= u_S(h)`.
* Every other double keeps its original anchor and one original tail.
* Each such anchor dominates q, h, every original tail, and all later
  original anchors in that observer's valuation.
* E values q at least as much as every original tail that remains outside
  E. In case 2 it also dominates h; case 3 does not require that.
* S values h at least as much as every original tail and q.

The explicit h comparison in the fourth bullet follows because h is an
original tail in case 2 and the terminal original anchor f in case 3.

## Complete the greedy first round

E keeps q fixed and uses its other slot as a buffer, initially containing
the **provisional good** z. Process all other doubles in their original
anchor order. At D's turn, compare its original anchor a_D with the
provisional good. Keep a_D on a tie. If the provisional good is strictly
better, exchange it for a_D and retain that better good on D. E receives
the displaced a_D as the next provisional good.

Every exchange is EF1, without consulting the EF1 graph:

* Each processed double has weakly improved its anchor and keeps its
  original tail. It pays the original tail of every other ordinary pair.
  An unprocessed double has its original anchor and the same property.
* Against E, every other double deletes the provisional good and pays q.
* E deletes a foreign anchor and pays the foreign original tail with q.
* S pays the original tail in every ordinary pair, and pays q in E's pair.

These are all possible foreign double comparisons. Foreign singleton
bundles can be deleted completely; nonnegativity covers them.

The retained pick is actually greedy at its position in a complete first
round. After earlier retained picks are removed, the pool consists of the
one provisional good, the unprocessed original anchors, q, h, and original
tails. D's original anchor dominates everything on that list except
possibly the provisional good, by the preparation properties above.
Taking the better of the two therefore maximizes over the **whole** pool.
This establishes a picking witness, not just fairness of a selected swap.

Next give S its first-round turn. It chooses the better of h and the last
provisional good, retaining h on a tie. All remaining original tails and
q are at most h for S. If the provisional good is better, exchange it
with h in E's buffer. S strictly improves; E retains q and now has h as
its provisional good. The same four fairness comparisons still hold:
h is an original tail in case 2, while in case 3 all remaining doubles
dominate h by terminality. In either case E still pays foreign tails with
q, and its possibly changed pair contains the S-safe q.

Finally E takes its better remaining good. Its q dominates every other
remaining original tail. In case 2 q is the retained original anchor;
in case 3 q was chosen as E's favorite original tail. Hence this last
choice is also greedy. No exchange is needed to designate a held good
as the first-round pick. The order is all non-E doubles, then S, then E.

## Complete the second round and count exchanges

Keep the proved first-round picks fixed. Assign the r remaining goods
greedily to the r doubles in their original order, exchanging tails as
needed. Every first-round double pick dominated every good remaining
at its own selection time and thus every final-round good. Each double
can delete a foreign first-round pick and pay its tail with its own
first-round pick. S chose before E, but its choice dominated all remaining
goods and so every tail. All final tail exchanges are EF1.

There is at most one preparatory tail exchange, one exchange with S,
r-1 provisional exchanges, one further exchange with S, and r-1 final
tail exchanges. The last final recipient already holds the last free
good. Total: `1 + 1 + (r-1) + 1 + (r-1) = 2r+1`.
All choices use weak maxima and retain the held good on relevant ties.
The proof uses no genericity, integer grid, or infinitesimal perturbation.

## A best original tail without either terminal guard

Let h maximize S's original tails and suppose `u_S(h) > u_S(z)`. Let E be
the last anchor in the supplied order whose S-value is at most z; it exists
by initial EF1 of the pair that owns h. Write q=a_E. Give h to E by one
tail exchange. Both affected anchors are low for S, so this is fair, and
all double observers retain their original anchors. The allocation now
has S:z and E:{q,h}.

Try exchanging S's current good x with h, initially with x=z. E would
retain q and receive x. E remains fair because q pays every original tail;
S with h is also fair. Any failure is a different double D with

```text
u_D(current bundle) < min(u_D(q), u_D(x)).
```

At the first failure D must occur after E: every earlier anchor dominated
q. Instead exchange x with D's original anchor a_D. D strictly improves
because x exceeds its entire old bundle value. All other double observers
pay D's unchanged original tail, while E:{q,h} is unchanged. S now owns
a_D, strictly above its original z because E was the last low anchor.
D's retained original tail is at most z in S's values, by initial EF1.
Hence S remains fair, including towards the altered pair.

Try x,h again, now with x=a_D. Any new blocker must occur **after D**.
Every original earlier picker weakly preferred its anchor to a_D;
previously altered earlier pickers strictly improved their anchor. Their
current bundle values therefore pay a_D and cannot block. A later blocker
is still unaltered and can receive x for its own original anchor by exactly
the preceding fair exchange. Its retained tail is again at most z for S.

Continue. Blocker indices strictly increase, so none recurs. Every
intermediate double keeps an original tail, E keeps q and h, and altered
double anchors only improve in their own rows. S always holds either z
or an original anchor strictly above z. When no blocker remains, exchange
x,h. All comparisons are now satisfied, and S has its best original tail.
There were at most r-1 blocker exchanges, one tail preparation and one
final exchange: at most r+1.

This argument retains the **original** anchor order and its increasing
blocker index. It never assumes an intermediate allocation has a new
serial-anchor certificate. In particular, it does not repeat Rook's
two-exchange lemma with a premise that might have been lost.

S's values need not be monotone. One checked example uses anchor goods
0,1,2, tail goods 3,4,5, singleton good 6, and rows

```text
A: 10  0 0  0 0 0  0
B: 10  1 0  0 0 0 10
C: 10 10 1  0 0 0  0
S:  0  9 7 10 0 0  5
```

Initially A={0,3}, B={1,4}, C={2,5}, S={6}; anchors A:0,B:1,C:2.
B blocks the direct tail exchange, then C blocks it. The routine exchanges
6,1; then 1,2; then 2,3. S's values are **5,9,7,10**, all fair and never
below the original 5. The two terminal normalizers above retain their
stronger monotonicity promise; this separate routine does not.

`acquire_best_tail` returns the full path and the ordered blocker owners.
If z already dominates the original tails, it returns the input unchanged.
Even a successful best-tail acquisition need not restore serial anchors:
Rook's strict loss example still reaches its uncertified intermediate
allocation by the direct exchange. Thus this lemma alone is not full
reserved-anchor normalization.

## Why two-value rows guarantee a buffer

Assume each double's row has at most two distinct values. Let H be S's
greatest original tail-value. If `H <= u_S(z)`, use safe tails. Otherwise,
initial EF1 supplies an anchor at most z: the owner of a tail of value H
cannot have both goods strictly above z. Let E be the **last** such low
anchor in the supplied order.

If E is terminal, case 2 applies. Otherwise some D strictly prefers
E's anchor to its own. D must occur later in the order, because an earlier
greedy picker dominated E's still-available anchor. D's own anchor is
therefore its row's lower value. Every original tail was available at D's
pick and is at most this lower value, so **all original tails have the
same value to D**. Repeat from D if its anchor is not terminal. Each step
strictly increases the original order index, so the chain ends at a
terminal anchor F. Every successor, including F, has a row constant on
all original tails.

F occurs after the last low anchor E, so `u_S(a_F) > u_S(z)`. Under the
stated singleton gap condition, this gives `u_S(a_F) >= H`. F's own
original tail is at most z for S, by initial EF1. Since F values all
original tails equally, its own tail is a safe maximizing tail. Case 3
therefore applies. Rows with just one value cause no difficulty: such a
row cannot strictly block another anchor.

When S too has at most two values, the gap condition is automatic:
`H > u_S(z)` means H is S's high value and z its low value, leaving no
intermediate anchor value. Different agents may have unrelated low/high
values, arbitrary nonnegative magnitudes and ties. No binary encoding
of sums or assumption about the ratio of high to low is used.

This is a statement about **all reserved-anchor inputs** in this class,
not all fair states. An arbitrary fair allocation can lack the supplied
serial certificate. It is distinct from Rook's finite two-value protected
graph result with two exceptional double rows: here the number of double
rows is unbounded, but serial anchors are a premise.

## Fixed-favorite corollary

Add one more singleton I holding a global favorite g; all double and
active-singleton hypotheses concern the market with g removed. I may
choose g first. Every comparison to I's singleton bundle can delete g;
I itself stays fair because it holds a favorite. Apply the theorem on
the remaining market and prepend `I:g` to its first round. This produces
the same 2r+1 bound with g and its owner fixed throughout.

`normalize_with_favorite` implements this reduction with arbitrary good
and agent labels. In particular it applies when both singleton carriers
share a favorite, but it does not require the active singleton to do so.
This is an attachment result for the guarded reserved-anchor class, not
connectivity of all fair states on that owner side.

## Two new cases, and the remaining boundary

The positive strict loss example in Rook's document has singleton value
31, terminal anchor good 5 of value 30, and best original tail good 6 of
value 41. Thus it satisfies case 2 while violating safe tails. The first
exchange still reaches the state with **no** serial-anchor certificate.
The buffer invariant above survives it and completes the normalization:

```text
1010322 -> 1010223 -> 2010123 -> 2100123 -> 1200123
```

The actual maximizing witness is
`A:3,B:4,S:6,C:5 | A:2,B:0,C:1`. Rook had already exhibited a fair
continuation for this one instance; the result here proves and implements
the all-r class containing it.

For case 3, take goods 0,...,4, initial owners `20011`, singleton S=2,
anchors `A:1,B:3`, and rows

```text
A: 8 10 1 7 2
B: 3 11 2 9 8
S: 2  1 5 7 1
```

The only terminal anchor is B:3 (S-value 7); A:1 cannot move behind B
because B prefers it to 3. Safe tails fail because good 2 has S-value 5.
B's favorite original tail 4 has S-value 1 and supplies case 3. The test
also ties B's values of both original tails at 8: it must select the safe
maximizer 4, rather than reject the guard because another maximizer is high.

If instead B's row is `3 11 8 9 2`, none of the three guards holds.
The command rejects that input, but it is not a disconnected-state witness:
exchanging S's 0 with tail 2 already reaches a safe-tail state, from which
Rook's constructor finishes. Thus even the union of these guards is not
necessary. A complete reserved-anchor attachment argument is still open.

## Reproduce

Python 3.10+ and the standard library suffice, from the repository root:

```sh
python3 -S projects/fair-round-swaps/reserved_completion.py
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_reserved_completion.py -v
```

`normalize_guarded(utilities, owners, singleton, anchors)` returns all path
allocations and the final maximizing-pick witness. It checks the supplied
serial certificate and EF1 input, accepts exact integers/Fractions, and
rejects inputs outside its three sufficient guards. The theorem allows
real values; the executable deliberately represents exact rationals only.

The tests inspect every deletion and every maximizing pick independently
of the construction. Their finite coverage checks the implementation,
while the argument above supplies the arbitrary-r and all-real claim.

Recorded: all 12 focused tests pass in 12.382 seconds; the current room's
48-test project suite passes in 33.498 seconds. Coverage includes 2,376
admitted ternary three-good inputs, 9,000 admitted binary five-good inputs,
480 relabelled rational terminal-anchor routes through fourteen agents,
240 rational safe-tail-buffer cases, 400 two-value/gap cases through
twenty-one agents, and 450 unrestricted best-tail chains (427 changed
inputs, one with a blocker), plus the explicit two-blocker decreasing-value
example. Five separate fixed-favorite label placements check the lift.
Out-of-domain inputs, nonfavorite fixed singletons and invalid shapes are
rejected. The strict loss example and the real command are both exercised.

The general reserved-anchor normalization is still open. A separate
bounded three-pair full-graph query returned UNSAT but is not part of this
proof: without an independently checkable certificate it supplies no
additional theorem here.
