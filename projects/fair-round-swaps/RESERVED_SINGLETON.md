# Reserved singletons: a normalization and its boundary

Rook, 20 November 2026. **A conditional normalization, a local improvement
and two exact boundaries; independent reconstruction pending.** No general
normalization, protected-braid attachment, multi-round theorem or project
milestone is claimed.

The task is to attach a useful class of fair states to greedy endpoints.
There are r>=1 double recipients and one singleton S, on 2r+1 goods. S holds z.
Choose one good a_D (an **anchor**) from each double bundle. Suppose the
anchors can be selected greedily in some order from the market with z removed;
the other good of each pair is its **tail**. The resulting allocation must
also be EF1, including S's comparisons. This is a checkable hypothesis, not
an assumption that arbitrary EF1 allocations admit such an order.

The underlying model is the project's [frozen model](proof.md): nonnegative
additive real utilities, arbitrary maximizing ties, fixed labeled bundle
sizes, and one exchange between distinct owners per move. The whole proposed
attachment remains open. The subclass where S dominates every tail does
normalize. Outside it, the two-exchange improvement below does not justify
repeating itself. The counterexample is positive and strict as well as
available with small integer ties.

## 1. Normalize when the singleton dominates all tails

**Theorem.** Under the stated serial-anchor hypothesis, add the condition
`u_S(z) >= u_S(t)` for every original tail t. The allocation connects to an
actual greedy endpoint in at most 2r EF1 exchanges, with its size vector
unchanged. The input need not itself be greedy.

This extends the input contract of Aster's provisional-anchor mechanism
at frozen `f45ab98`: the argument below reconstructs the mechanism for an
anchor order that omitted z, rather than assuming an original greedy round.

If z is already a global favorite, put S:z first, then use the supplied
anchor order. Each of these picks is greedy by deletion of the alternative
z. Permute the final tails to the greedy assignment. Every double has an
anchor dominating every tail, and S has a favorite, so all these swaps
remain EF1.

Otherwise S has a global favorite f among the anchors. Let D own f. Give
D its favorite original tail q, then exchange f,z, as in Section 2 below.
Keep S:f and D:q fixed. D's other good, initially z, is provisional.
Process every other original anchor p in its original order. Its owner
takes the better of p and the provisional good, retaining p on a tie;
exchange them if needed and pass the unchosen good back to D.

Every processed agent weakly improves its anchor and keeps its original
tail. Every other agent retains its original anchor. D always owns q,
which dominates every original tail in D's valuation. Therefore D can
delete the other pair's anchor and pay its tail with q. Other doubles
delete D's provisional good and pay q with their retained or improved
anchor. S holds a global favorite. These comparisons prove every swap EF1.

The chosen good at each processed position is greedy. Apart from the one
provisional good, the remaining pool consists of unprocessed original
anchors and original tails. The current original anchor dominated all
later original anchors and every tail in its owner's valuation. Removing
D's f early introduces no new alternative. Thus only the provisional good
can improve that choice. After all other agents have picked, D takes its
preferred of the provisional good and q; q dominates all other remaining
original tails. This completes a genuine greedy first round beginning S:f.

Finally assign the residual r goods greedily to the r double recipients,
using tail swaps with the first-round picks fixed. The usual deletion of
another pair's first-round good proves all these states EF1. There are at
most two preparatory swaps, r-1 provisional swaps and r-1 final-tail swaps,
giving 2r. Ties and labels do not change the argument.

For a nongreedy input example take utilities `(2,3,1)` and `(3,2,1)`, with
bundles `{0}` and `{1,2}`. Neither agent owns a global favorite, so no greedy
first pick can realize it. Good 0 dominates tail 2 for the singleton, and
anchor 1 is greedy with 0 removed. Swapping 0,1 gives the greedy witness
`0:1,1:0 | 1:2`. This extends beyond greedy starting states.

## 2. A strict improvement in at most two exchanges

**Lemma.** From any allocation satisfying the stated hypothesis, either S
already holds a global favorite or at most two EF1 exchanges strictly
increase S's utility. Intermediate utility for S never decreases.

Every anchor is worth at least every tail to its owner, because all tails
were available when the anchors were chosen. An earlier anchor is also
worth at least a later anchor to the earlier picker. Thus, after any tail
permutation, double observers remain EF1: delete the other pair's anchor
and pay for its tail with one's own anchor. S remains EF1 exactly when
no pair has both goods strictly better than z in S's valuation.

If all tails are no better than z to S, take a global favorite f of S.
If S is not already satisfied, f is an anchor held by a double D. First
give D its favorite tail q by at most one tail exchange, then exchange f,z.
S now has f. D keeps q, which pays for every other pair after deleting its
anchor. Every other double deletes z from D's pair and pays for q with its
own anchor. S was safe throughout the tail preparation because all tails
were no better than z. This proves the first case.

Otherwise let h be a tail strictly better than z to S. Choose the **last**
double E in the anchor order whose anchor p is no better than z to S.
Such an E exists: the pair containing h must have a low anchor, by S's EF1
condition. Give h to E by a tail exchange. Both the old holder of h and E
have low anchors, so S stays fair. The double observers remain fair by
the fixed-anchor argument.

Try exchanging z,h. S improves and E retains its anchor p, which pays for
every other tail. All pairs except E's are unchanged. If this is unfair,
some other double D must satisfy

```
u_D(own pair) < min(u_D(p), u_D(z)).
```

D cannot be earlier than E: its anchor would dominate p. Therefore D is
later than E. By E's choice as the last low anchor, a_D is strictly better
than z to S. The displayed inequality also implies that z is strictly
better than a_D to D, using nonnegativity of D's other good.

Instead exchange z,a_D. Both S and D strictly improve. Every other double
deletes z from D's pair and pays for its unchanged tail with its own anchor.
S's previous comparisons persist after its improvement; against D it can
delete the tail and tolerate its own former z. These are all possible
comparisons. At most the tail preparation and this last swap were needed.

The construction uses only weak comparisons except where strict improvement
is needed. It covers arbitrary ties and arbitrary labels. It does not ask
whether an entire allocation graph is connected.

## 3. The improvement can destroy every anchor certificate

Columns are goods 0,...,6; the last row is singleton S. All entries below
are positive, and each row has distinct values.

| Agent | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 11 | 1 | 31 | 41 | 2 | 3 | 4 |
| B | 23 | 11 | 1 | 12 | 41 | 2 | 22 |
| C | 11 | 41 | 12 | 13 | 1 | 42 | 31 |
| S | 21 | 11 | 22 | 23 | 31 | 30 | 41 |

Start with `A={1,3}, B={0,2}, C={5,6}, S={4}`, owner vector `1010322`.
With good 4 withheld, the anchor order A:3, B:0, C:5 is greedy. Each pair
is EF1 by anchor dominance, and S can tolerate its smaller member. The
lemma chooses E=C and h=6. The single fair exchange 4,6 produces

```
1010322 -> 1010223
```

S's value rises from 31 to its global maximum 41. But the new allocation
has **no** serial-anchor certificate with 6 withheld. B strictly prefers
good 4 to either of its own goods, so C would have to pick 4 before B.
C cannot pick 4: its own good 5 is strictly better and cannot be removed by
any other anchor picker. This exhausts possible orders, not just the old
order. The same argument also rules out a greedy full-round witness for
the new allocation: C cannot take 4 until its final pick, after B's first.

This is not a disconnected endpoint example. Two further fair swaps reach
an actual greedy allocation while S keeps 6:

```
1010223 -> 1100223 -> 1200123
```

The terminal maximizing witness is
`S:6,C:5,B:4,A:3 | C:1,B:0,A:2`. The program also retains a smaller
integer example with ties having exactly the same owners, orders and moves.
Both versions are checked by explicit deletion and exhaustive anchor-order
tests. Thus the failed inference is precisely: “strict improvement lets
us reapply the reserved-anchor lemma.” The lemma's input premise has gone.

## 4. Full pair-only connectivity cannot supply the missing step

After freezing a favorite singleton, one might instead appeal to connectivity
of all EF1 states of the remaining pairs. This premise is false already
for three pairs. Use A={a,b}, B={c,d}, C={e,f} and

| Agent | a | b | c | d | e | f |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 1 | 2 | 0 | 0 | 3 | 6 |
| B | 6 | 3 | 2 | 1 | 0 | 0 |
| C | 0 | 0 | 3 | 6 | 1 | 2 |

Each own value is 3. The better foreign pair has minimum 3 and the other
foreign pair has minimum zero, so the state is EF1. Every exchange between
A and B makes A lose a positive good and receive a zero. Its own value
falls below 3 while C's pair stays unchanged, violating EF1. Exchanges
between B,C fail for B; exchanges between C,A fail for C. These three
cases exhaust all twelve possible exchanges. The state is isolated.

An actual greedy allocation is obtained by
`A:f,B:a,C:d | A:e,B:b,C:c`, so the graph is genuinely disconnected.
The isolated allocation is not greedy: nobody owns a global favorite.

The construction extends to every n>=3 when all n bundles have size two.
Core agents assign zero to every added good. Each added agent values its
own two goods at 1 and 2, every core good at 3, and other added goods at
zero. Initial own values are again 3, and all EF1 inequalities hold.
Core-core swaps fail as before. A core-added swap fails for the core agent
that loses a positive good while its valued core pair is untouched.
An added-added swap leaves a participant below 3 while a core pair still
has both goods worth 3. Thus every distinct-owner exchange fails.

It is robust to positive strict preferences. With m=2n, replace entry v
in column g (zero-based) by `10*m*v + m + g + 1`. Initial own value is
at least `30m + 2m + 3`; every foreign-pair minimum is at most `30m + 2m`.
Each blocking inequality had an integer gap of at least one. After scaling,
its gap is at least 10m, while the added own offsets sum to at most 4m
and the foreign minimum gains a positive amount. The strict failure
survives. Each row is positive and has distinct entries.

This threshold is sharp for equal pairs. For n=2 there are six allocations,
forming the octahedron exchange graph. For either observer, any own bundle
containing a top-two good is EF1: the smaller of the two opposing goods
cannot exceed that good. So at most one of the six states is excluded by
each observer. After deleting at most two vertices, any surviving
nonadjacent pair still has at least two of its four common neighbors.
The EF1 graph is connected with diameter at most two. For n=1 it has one
vertex. The argument allows ties and does not assume strict preferences.

This equal-pair obstruction does not refute normalization of the smaller
reserved-anchor class, or the original greedy-endpoint conjecture. It says
exactly why arbitrary EF1 pair states cannot be substituted in the proof.

## Reproduce and continue

Python 3.10+ and the standard library suffice, from the repository root:

```sh
python3 projects/fair-round-swaps/reserved_singleton.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_reserved_singleton.py -v
```

Recorded: six tests pass. The seeded exact-rational test checks 732 valid
inputs through twelve agents, with branches favorite 292, best-anchor 136,
best-tail 303 and blocking-anchor 1. Independent predicates try every
deletion and explicitly inspect changed owners. The two invariant-loss
profiles, all anchor orders, their actual greedy continuation, all exchanges
in the obstruction family at n=3,4,6,12 (tied and strict), invalid inputs,
and the real command are checked. A separate 330 exact-rational cases through
twelve agents check the safe-tail normalization, its 2r bound and every pick
of its final greedy witness; the unsafe domain is rejected. Finite examples
audit the code; the proofs above supply the stated conditional normalization,
local lemma and isolation family.

The initial research also screened 30,000 seeded four-agent integer profiles
for failure of monotone reachability from this reserved class to any greedy
endpoint. No failure was found. That temporary exploratory computation is
not a universal claim or a shipped acceptance test. It did not establish a
normalization or repair the lost invariant.

Next useful work is a preserved hypothesis larger than serial anchors, or a
new attachment argument that can traverse the resulting non-serial states.
A local improvement, a fair crossing, and a full normalization are different
conclusions. The normalization here requires the safe-tail condition.
