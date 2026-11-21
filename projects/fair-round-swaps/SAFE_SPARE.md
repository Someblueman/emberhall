# A safe spare reaches the greedy component

Fern, 20 November 2026. **Candidate constructive theorem; independent
reconstruction pending.** This concerns one double bundle and singleton
bundles, for arbitrarily many agents. It does not assert connectivity of
the whole EF1 graph or resolve the general incomplete-round question.

The [one-extra theorem](SINGLE_EXTRA.md) connects greedy endpoints with
`n+1` goods. Its separate safe-spare observation proves a fair neighbor
exists. Here a safe spare gives a path all the way to a greedy endpoint,
including from nongreedy allocations. Mica's four-agent normalization in
`FIVE_AGENT_ONE_FINAL.md` uses the same preference-cycle rotation after
reaching a stronger safe state. The new initial condition below lets the
normalization work for every n, without the at-most-three-singleton
blocking-cycle argument. The implementation depends only on the existing
one-extra constructor and common model; no new dependency is needed.

## Statement

Use the [frozen model](proof.md): nonnegative additive real utilities,
arbitrary ties, fixed labeled bundle sizes, and one-for-one exchanges.
Let n>=2, let there be n+1 goods, and let D be the only double recipient.
Write its pair as `{h,p}` and singleton i's good as x_i. Call h a **safe
spare** when

```
u_i(x_i) >= u_i(h)  for every singleton i.
```

Such a state is automatically EF1: delete p when a singleton compares
with D, and delete the entire good from any other singleton. D has only
singleton bundles to compare with. All utilities are nonnegative.

**Theorem.** From any allocation with a safe spare there is an EF1 exchange
path of length at most `2n(n-1)` to an actual greedy one-round-plus-one-pick
outcome for the original utility profile. Consequently all safe-spare
allocations with the same doubled recipient lie in the ambient EF1
component containing every greedy endpoint.

The bound concerns each normalization, not the subsequent path connecting
two normalized endpoints. The latter uses the existing one-extra theorem.
Neither statement requires every intermediate state of that connector to
have a safe spare.

## First make both spares safe

Keep h in D. If some singleton i strictly prefers the other spare p to x_i,
exchange p and x_i. The recipient improves, so it still dominates h; every
other singleton retains its good and also dominates h. Delete D's other
good in every singleton comparison. Thus the exchange is EF1 and h stays
safe. The new variable spare is x_i.

Repeat while any singleton wants the variable spare. Each exchange
strictly improves one singleton, without worsening another. The procedure
therefore terminates: replace each singleton's finitely many distinct
utility values by their ordered ranks and sum the ranks of the held goods.
That sum strictly increases and is bounded by `n(n-1)`.
At termination every singleton dominates both h and the variable spare p.
No property of D's utility has been assumed.

## Resolve preference cycles with a spare as a buffer

Draw i->j when singleton i strictly prefers x_j to x_i. If there is a cycle
`i_0 -> i_1 -> ... -> i_(k-1) -> i_0`, choose the spare p that i_0 values
at least as much as the other spare q. First exchange p and x_(i_0).
The temporary singleton i_0 holds p, which dominates q for that observer.

Now pass the good carried by D to i_(k-1), taking that agent's old good;
continue in reverse cyclic order through i_1. Finally give i_0 its desired
x_(i_1), returning p to D. This uses k+1 exchanges and restores D's
original pair. Every cycle agent has strictly improved at the end.

Throughout the rotation D retains q. Outside the temporary buffer position,
every singleton holds its original good or a strictly better one; each
dominates q. The temporary position also dominates q by the choice of p.
Deleting D's non-q good therefore proves EF1 at every step. Comparisons
with singleton bundles remain automatic. At the end both original spares
are still safe, since no singleton has worsened.

Repeat until the strict preference graph is acyclic. The rank sum strictly
increases after every complete rotation, so this terminates. Each singleton
rank can increase at most n times across both stages. A one-person
improvement costs one exchange; a cycle improving k>=2 people costs
k+1<=2k exchanges. Charging at most two exchanges to each strict rank
increase gives the bound `2n(n-1)`.

## Produce a greedy witness

Repeatedly choose a singleton that does not prefer any remaining singleton's
good to its own. Such an agent exists in an acyclic directed graph. It
maximizes among all remaining goods: already removed goods are unavailable,
and both spares are no better than its own good. Let the chosen singleton
take its good and continue.

After all n-1 singletons have picked, let D take its preferred spare as the
last pick of the first full round, then the other spare as its final pick.
This is an actual greedy witness under D's original utility row. No neutral
utility replacement, sum comparison approximation, or fixed tie rule is
needed. Ties do not create preference edges and may be chosen in any order
consistent with the construction.

Normalize both input allocations. The already-established one-extra
theorem connects the resulting greedy endpoints. Reverse the second
normalization to obtain the claimed ambient component connection.

## Scope boundaries

The condition is sufficient, not necessary. With rows

```
D: 0 0 0 0
B: 4 1 2 0
C: 1 4 0 2
```

the state `0012` has no safe spare: B rejects good 0 as a spare, and C
rejects good 1. Yet exchanging goods 0 and 2 reaches the EF1 state `1002`,
where good 2 is a safe spare. It therefore joins the greedy component.
The program rejects normalization of `0012` as an unsupported premise;
it does not report that this state is disconnected.

Conversely, the known isolated family in `SINGLE_EXTRA.md`, for n>=5,
has no safe spare and cannot reach the greedy component. There is no
contradiction with this theorem. More than one double recipient invalidates
the deletion-of-the-only-double-bundle argument; that case is not covered.

## Run the construction

Python 3.10+ and the standard library, from the repository root:

```sh
python3 projects/fair-round-swaps/safe_spare.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_safe_spare.py -v
```

The real command normalizes a six-agent state with a strict five-singleton
preference cycle. Owner vectors, with goods and agents numbered from zero:

```
0012345 -> 1002345 -> 1052340 -> 1052304
        -> 1052034 -> 1050234 -> 0051234
```

It prints the resulting greedy witness as well as all six exchanges.
`normalize(utilities, allocation)` returns both; `path(utilities, start,
target)` joins two eligible allocations through the existing greedy
constructor. Arbitrary labeled doubled recipients are supported.

The six tests check all 2,256 eligible allocations from 256 binary singleton
profiles on four goods, a 29-singleton cycle, an eight-transfer improvement
chain, arbitrary doubled labels, and 225 exact-rational instances through
ten agents. Deletions, maximizing picks, bundle sizes and changed owners are
checked independently. Tests also exercise the known isolated family,
the sufficient-but-not-necessary example, and the real command. These are
implementation checks; the argument above carries the real-utility and
arbitrary-agent quantifiers. No literature priority is claimed.
