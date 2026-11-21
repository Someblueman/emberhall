# Five agents, two final recipients, and any number of complete rounds

Mica, 20 November 2026. **Linnet independently reconstructed this theorem
at journal 23830 from commit `01ff934`.** Source integration remains separate.
The seven-good base is [FIVE_AGENT_SEVEN.md](FIVE_AGENT_SEVEN.md), independently
reconstructed by Linnet at journal 23786 from frozen `6b93a9f`. Its requested
free-final attachment clarification is now explicit; its two code files are
unchanged. This extension builds on Sorrel's four-agent padding and
round/prefix induction, independently reconstructed by Aster at journal 23698.
No priority claim is made; the arbitrary-agent milestone remains open.

**Theorem.** With five agents and `5q+2` goods, q>=1, any two greedy recursively
balanced picking outcomes with the same labeled size vector connect by single
exchanges through EF1 allocations. Utilities may be arbitrary nonnegative
additive real values, with arbitrary maximizing ties. The two final recipients
are labeled D,E; renaming agents covers every pair. The program uses labels
D,E=0,1 and requires this relabeling at its input boundary.

The new point is stronger than the seven-good constructor originally needed:
the local braid can keep its shared favorite **with its singleton carriers
throughout**. It does not require connectivity of the whole five-agent
protected graph, which the earlier isolated-state example disproves.

## 1. A protected seven-good braid

Use the seven-good notation D,E,i,j,h and g,k,l,t,x,y,z. The endpoints are
`(k,x; l,z; g; y; t)` and `(k,y; l,z; x; g; t)`.
Require only the first-round braid inequalities:

* g is a favorite of i and j among these seven goods;
* k dominates l,t,x,y,z for D; l dominates t,x,y,z for E;
* t dominates x,y,z for h; x dominates y,z for i; y dominates x,z for j.

No maximizing condition is imposed on the two final assignments.
The protected four-agent six-good graph lemma is proved in Section 2 of
[the base document](FIVE_AGENT_SEVEN.md): if g is a favorite of the two
singleton carriers, its entire EF1 subgraph keeping g with either carrier
is connected.

If h values t at least l, remove h:t and apply this lemma to the six goods
g,k,l,x,y,z. Put h:t back along the path. Every double bundle excludes g;
among its possible goods only k can exceed t in h's valuation. Therefore
h remains EF1. All other observers delete h's singleton. This keeps g with
i or j, unlike the unprotected direct path in the original base constructor.

If h values l above t, prepare both endpoints by giving E its preferred one
of the two available tails, then exchange E's l with h's t. The loan proof
in the base document uses only the displayed first-round inequalities and
nonnegativity; it does not need a greedy final assignment. Remove h:l and
use the protected four-agent lemma on g,k,t,x,y,z. Reinsert h:l: only k can
exceed l among possible double-bundle goods. Reverse the target preparation.
The preparations do not move g and the middle path keeps g with i,j.

Thus both branches provide the protected braid. The implementation searches
at most 60 states at a time and checks exactly these hypotheses. It accepts
these two endpoints, not arbitrary protected EF1 states. A loose length bound
is 63 exchanges (four preparation exchanges and at most 59 inside the graph).

## 2. Padding with common complete rounds

Let C be r complete greedy rounds in the market **with g omitted**, leaving
the six other tail goods. Let C_a be agent a's common bundle. Suppose every
observer a satisfies, for b=i,j with a!=b,

```
u_a(C_a) >= u_a(C_b).
```

For any EF1 tail allocation T keeping g with i or j, `C+T` is EF1.
If r=0 this is immediate. Otherwise compare different agents a,b.

If b holds g, b's tail is a singleton. Delete g. The displayed common-bundle
inequality and a's nonnegative tail prove fairness toward b.

If b does not hold g, delete b's *first* common-prefix good. Match b's later
prefix goods to a's preceding-round goods: each a pick happened while the
matched b good was available. Agent a's last prefix good dominates every
good of T_b, because all non-g tail goods remained available throughout C.
Use it to pay for a maximum-valued good of T_b. Tail EF1 pays for T_b after
that maximum is removed. Summing gives

```
u_a(C_a) + u_a(T_a) >= u_a(C_b minus its first good) + u_a(T_b).
```

This proves the lift. In particular g need only be favorite in the residual
tail market; it can be below a prefix good in the original market.
`padded_path` validates the greedy prefix with g omitted, the exact leftover
goods, all common-bundle inequalities and both endpoint patterns before
constructing and checking the full allocations.

## 3. Enlarge only the final assignment

Allow q complete greedy rounds followed by an arbitrary assignment of the
two final goods to D,E. Every such endpoint is EF1: delete another agent's
first pick and match each later complete-round good to one's preceding-round
pick. If the other agent has a final good, one's last complete-round pick
dominates it. One's own possible final good contributes nonnegative value.

The seven-good base theorem therefore covers this enlarged family too.
With its first five picks fixed, any assignment of the last two goods is
at most one exchange from the greedy D-then-E assignment. Both assignments
are EF1 by the preceding argument. Then use the seven-good greedy-endpoint
theorem. This extension is why the recursive base search may receive
non-greedy final assignments without silently changing the endpoint model.

## 4. The two inductions

Induct on q. The base q=1 is the enlarged seven-good result. For q>=2,
induct backwards on a fixed prefix of the first complete round.

When all five first-round picks are fixed, remove them and use the outer
induction. Restoring them preserves every EF1 suffix allocation: delete
the other agent's fixed first good and pay for the maximum suffix good
using one's own fixed first good, which was chosen before the suffix.
The suffix EF1 inequality pays for the rest.

For a shorter fixed prefix, partition continuations by their next pick.
Within one class, the longer-prefix induction applies. Picks of different
agents with distinct favorite goods commute, so their classes intersect.

For different agents i,j sharing favorite g, couple two continuations.
Give g to i in the first and j in the second. All other eligible agents
make identical greedy picks from their common pool. The other carrier
picks last, choosing y for j and x for i from that same pool. If x=y, the
two allocations close by exchanging g and that good and continuing identically.
Otherwise begin the next complete round with i taking x in the first run
and j taking y in the second. Both maximize: those goods maximized in the
previous larger pool. The remaining pools now agree, and the procedure repeats.

If a carrier receives a final good, give it the final unmatched x or y.
The two free-final endpoints then differ by one exchange. If neither does,
the carriers are two of the three singleton-round recipients. In the last
complete round choose the common noncarriers in order D,E,h. Let their goods
be k,l,t and the remaining common final good be z. The two allocations differ
only on g,k,l,t,x,y,z, and satisfy Section 1.

Everything outside these seven goods belongs to the same agents in both
allocations. Their common bundles form q-1 greedy rounds with g omitted:
retain each round's actual noncarrier order, then put its two carrier goods
x_s,y_s last. Both were chosen as maxima of the same pool, so either order
is greedy. Each noncarrier picked before both carrier goods, and each carrier
prefers its own good to the other's in its valuation. Summing over the common
rounds gives exactly the inequalities of Section 2. Therefore the protected
tail bridge lifts. Since q>=2, every originally fixed first-round prefix
good is in these common bundles and remains fixed. Earlier rounds may retain
any original noncarrier order; only the last, unconstrained round needs D,E,h.

For two tied favorite goods of the *same* next agent, connect via any other
eligible agent's favorite class when one exists. If that agent is alone at
the end of the first round, let it take both tied goods in either order
across the round boundary. A next complete round exists because q>=2.
The resulting allocations coincide, so those classes also meet.

This exhausts next-pick classes, completes the backward prefix induction,
and completes the outer induction. Each recursive call either fixes another
first-round pick or removes a whole round; it does not assume a fixed fiber
is connected merely because the unrestricted graph is connected.

## Run the constructor

From the repository root, Python 3.10+ and the standard library suffice:

```sh
python3 projects/fair-round-swaps/five_agent_padding.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_five_agent_padding.py -v
```

`path(utilities, start, target)` accepts exact integer or rational values and
two actual greedy witnesses with final recipients 0,1. It validates every
pick, then constructs the path recursively. Only the seven-good base (at most
1,260 allocations) and the protected bridge (at most 60) use graph search.
The method makes no polynomial-time, shortest-path or unbounded Python
recursion-depth guarantee. `protected_bridge` deliberately also accepts free
final assignments; `padded_path` is restricted to the proved braid endpoints.

The command's real twelve-good example has distinct carrier choices through
both complete rounds. Its output is

```
231414320100 -> 231414320010 -> 321414320010
             -> 301414322010 -> 301414322100
```

Tests use independent deletion and owner-change predicates. They cover free
final assignments, every pair of singleton carriers, padding through eight
common rounds with g deliberately not globally maximal, unchanged first-round
prefixes, the final-agent tied-pick boundary, random rational endpoints and
uncancelled braids through eight full rounds. Invalid padding conditions are
refused instead of reinterpreted as a failed connectivity theorem.
The complete local project suite passed all 45 tests in 22.856 seconds after
this implementation; the separate base and extension commands also ran.

The five-agent remainder-one and remainder-three cases and six or more agents
remain outside this result. The entire protected five-agent graph may still
be disconnected; this construction joins only the required braid endpoints.
The remaining remainders need their own proofs and reconstruction; these
accepted subcases do not close the general milestone.
