# Five agents and eight goods: a constructive bridge

Aster, 20 November 2026. **Candidate theorem; independent reconstruction is
pending.** The proof actually covers one complete round for any number of
agents when exactly two agents miss the final round. It does not prove the
arbitrary-round extension or the general project milestone. No priority is
claimed. All earlier frozen contributions remain unchanged.

## Statement and plan

Let n>=3, with 2n-2 labelled goods and nonnegative additive real utilities,
including arbitrary maximizing ties. Fix the n-2 final recipients. Any two
greedy recursively balanced allocations with this labelled size vector are
connected by single exchanges through EF1 allocations of the same sizes.
For n=5 the vector is (2,2,2,1,1), up to relabelling.

The proof has three pieces:

1. Move any greedy endpoint to a greedy endpoint whose first picker is a
   singleton. The new reduction works with any nonempty incomplete final round.
2. Connect each fixed singleton/favorite class by the existing near-complete
   theorem after removing that singleton.
3. Join the two singleton classes by a new anchor bridge. Its last double
   recipient may temporarily hold the common favorite. No assumption about
   connectivity of the **entire** four-agent seven-good graph is used.

The program implements these pieces. Its only imported constructor is
`near_complete.path`; it does not search the full fixed-size graph. The
near-complete constructor and its proof are in [FRONTIER.md](FRONTIER.md).
The endpoint and EF1 model remain exactly those in [proof.md](proof.md).

## 1. A general singleton-first reduction

Consider n agents, n+r goods, 1<=r<n, and one greedy complete round followed
by r greedy final picks. Call the first-round goods anchors and the final
goods tails. Every anchor is worth at least every tail to its owner, and
each singleton's good dominates all tails in that singleton's valuation.

Permuting the tails among double recipients is EF1: every pair still has
its anchor and one tail. Any observer can delete the other pair's anchor,
leaving a tail that its own anchor or singleton dominates. This also proves
EF1 for arbitrary final assignments after a fixed greedy complete round.

Take the earliest singleton i, holding b. If b is a global favorite, move
its pick to the front; all other picks remain greedy by deletion of an
alternative. Otherwise choose a global favorite g of i. It was picked before
i, hence by a double recipient D. Give D its favorite among **all r tails**,
denoted q, by at most one tail exchange. Exchange D's g with i's b.

This is EF1. Singleton i now holds a favorite. Every other singleton still
dominates all tails, and every other double retains its anchor. Those
observers delete the provisional anchor b from D's pair {b,q}. D can delete
each other double's anchor and pay for its tail with q. Comparisons with
singleton bundles vanish after deletion.

Now retain i:g and process, in their original first-round order, all agents
except i,D. Keep one provisional good a in D's pair, initially b, and keep
q there throughout. For the next agent k with its original good p, give k
whichever of p,a it weakly prefers, retaining p on a tie. If a is better,
exchange p,a. Pass the unchosen good on as D's new provisional good.

Every such exchange is EF1 by the same tail payments. A receiving singleton
improves its good. A receiving double improves its anchor and keeps a tail.
D still owns q, which dominates all other tails in D's valuation. All other
pairs still contain a tail affordable to every unchanged observer.

The processed good is a maximizing pick in the new order beginning i:g.
Indeed, after removing the already processed goods, the remaining pool is
the unprocessed original first-round goods, all original tails, and the
one provisional good a. The next original p dominated every later original
first good and every tail. Earlier processed picks removed one of their p
and the previous a and passed only the other onward. Thus only the current
a can beat p. This invariant also covers agents originally before D or i.

After all others, D holds {a,q}; these are D's two best possible remaining
choices in the sense that q dominates every remaining original tail. Let D
pick max_D(a,q) last in the new complete round. The allocation now has a
greedy complete-round witness and arbitrary final assignments. Greedily
permute the remaining r goods to their final recipients, using at most r-1
exchanges. The first-round anchors are fixed, so this is EF1. We have reached
an actual greedy endpoint beginning with singleton i and its favorite g.

This argument does not assume b is valuable to D, does not assume a common
ranking, and does not discard ties. It provides a finite constructive
reduction, with no appeal to a smaller all-EF1 connectivity statement.

## 2. The shared-favorite anchor bridge

There are r=n-2 doubles D_1,...,D_r and two singleton carriers i,j. Their
common anchor order is a_1,...,a_r; write c=a_r and F=D_r. Let g be a global
favorite of both carriers. After the anchors are chosen from the pool with
g removed, the remaining r+1 goods are tails. Let x maximize this tail pool
for i and y maximize it for j. The x=y case closes immediately by swapping
g,x and assigning the identical remaining final goods alike.

For distinct x,y consider these relaxed greedy endpoints:

* A: i holds g, j holds y; the doubles hold their anchors and one tail each,
  with x assigned to any chosen double.
* B: i holds x, j holds g; replace that double's x by y and leave all other
  double tails the same.

Every double's anchor dominates all tails. Every earlier double's anchor
also dominates c. The final assignments need not be greedy.

### Case I: i values c at least x

By one tail exchange, give F its favorite q among the r tails currently
assigned to doubles. Exchange i:g with F:c, then F:g with j:y. The resulting
singletons are i:c and j:g, and F holds {q,y}.

During the temporary {g,q} state, earlier doubles delete g and pay for q
with their anchors. F pays for every other double's remaining tail with q.
Singleton i's c dominates **every** tail, since c>=_i x; singleton j's y
also dominates every tail. The next exchange replaces g in F by y, so the
same comparisons still suffice. In particular the proof does not require
g to be valuable to F.

Let t be F's favorite tail other than x, now including y. Use the same
fixed ordering of the tail labels to resolve both choices of a maximum.
Rearrange F's
pair {q,y} to {x,t} by at most one exchange with an earlier double. This
claim includes all ties: q was the selected maximum excluding y and t is a maximum
excluding x; the two pairs share a good. Either they already agree, q=x,
t=y, or q=t. Moreover both pairs contain an F-maximum of the entire tail
pool. Keeping that shared maximum while changing the other good therefore
keeps F fair. All other doubles retain anchors; i:c dominates all tails;
j:g is safe. Now exchange i:c with F:x. F regains c, and i gets its tail
maximum x. Permute double tails to their specified targets. All doubles
again have their anchors, and x dominates all tails for the sole non-g
singleton. Every step is EF1.

### Case II: j values c at least y

Apply Case I backwards from B, exchanging the roles i,j and x,y.

### Case III: x>_i c and y>_j c

Put x with F by at most one tail exchange, then exchange i:g with F:x.
F temporarily holds {c,g}, i holds x and j holds y. Both singletons can
delete g and tolerate c by this case's hypotheses. Every earlier double
can delete g and pay for c with its own earlier anchor. F retains c, which
dominates every other tail. Now exchange F:g with j:y and permute the
double tails to their targets. All anchors are restored.

These three cases exhaust the weak inequalities. They prove the shared
favorite bridge for any r>=1; with r=3 the implementation takes at most
eight exchanges (a loose bound). The first r-1 anchors never move. The
favorite can visit F, which matters for the limitation below.

## 3. Connect all greedy endpoints

First fix a singleton i and a global favorite g. Remove i:g. The residual
problem has n-1 agents, 2n-3 goods, and n-2 final recipients: exactly one
agent misses its final round. The near-complete theorem connects its greedy
endpoints through EF1 states with free final assignments. Restoring i:g is
safe: i holds a global favorite against pairs, and other agents delete i's
entire singleton bundle.

For completeness, the near-complete proof uses backward induction over a
fixed greedy prefix. Distinct maximizing goods of different next agents
commute. A common favorite creates two coupled greedy runs with identical
noncarrier picks and one unmatched good per carrier. When these runs reach
the free final assignments, at least one of the two carriers is a final
recipient; assign the unmatched good to it and close by one exchange. The
single-agent tied-pick end case either takes both tied goods across a round
boundary or permutes the remaining one-good-per-agent suffix. Free final
assignments are EF1 by the ordinary round-shift deletion comparison. This
is the same argument implemented in `near_complete.py`, not a full-EF1
connectivity assumption.

There are only two possible first-singleton agents. Their classes with
different favorite goods meet: choose both goods first in either order,
then finish alike. Classes sharing g join using Section 2, putting all
doubles between the first and last singleton. Attach each relaxed endpoint
to a genuine greedy member of its class by permuting final tails while
keeping its complete round fixed. Two favorite classes of the same singleton
connect through any favorite class of the other singleton. Section 1 brings
every original endpoint into one of these connected classes. This completes
the theorem.

## 4. Why this does not yet prove 5q+3 for every q

The bridge temporarily gives g to a double recipient. The established
common-prefix padding lemma requires g to stay with a singleton carrier.
This is a real obstruction to copying this particular path, not just a
missing assertion.

An exact regression in `test_no_automatic_common_prefix_lift` appends five
common first-round goods to the example below. For each double, its own
new good is worth 2000 and the other new goods zero. For each singleton,
the new F good and g are both worth 1000, both new singleton goods are worth
90, and the other new goods are worth zero. Other values are those below.
Both thirteen-good endpoint schedules are genuinely greedy. The common
prefix with g omitted is also greedy and satisfies all the old carrier
dominance inequalities. Nevertheless the loan gives i value 90+70=160
while F holds values 1000+1000+60 to i. Even deleting its best good leaves
1060. Thus this **path** fails after padding. It is not a counterexample
between the thirteen-good endpoints.

Fern's separately owned investigation of the full four-agent seven-good
side graph is not a dependency of the proof above. A protected braid with
g always held by i or j, or a different validated way to lift the new base,
is still needed for arbitrary earlier rounds. General agent counts and
other remainder classes remain outside this theorem.

## Run and check

Python 3.10+ and the standard library suffice, from the repository root:

```sh
python3 projects/fair-round-swaps/five_agent_eight.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_five_agent_eight.py -v
```

The example utility rows, in order D,E,F,i,j, are:

```text
  0 100  90  80 70 60 50 40
  0   0 100  90 80 70 60 50
  0   0   0 100 80 70 60 50
100  90  80  70 60  0 20 10
100  90  80  70  0 60 20 10
```

The two witnesses are `i:g,D:1,E:2,F:3,j:5,D:4,E:6,F:7` and
`j:g,D:1,E:2,F:3,i:4,D:5,E:6,F:7`, with g=0. The actual command returns:

```text
30120412 -> 30122410 -> 20132410 -> 40132210 -> 40123210 -> 40123012
```

Every arrow exchanges exactly two owners; all six allocations are EF1.
The tests use separate deletion, maximizing-pick and owner-change predicates,
fresh exact rational profiles, arbitrary final-recipient labels, all-zero
ties, all three bridge branches, and the failed thirteen-good lift. The
reduction is exercised for all incomplete remainders through seven agents;
the whole theorem constructor is exercised through seven agents. Finite
tests support the implementation; the arguments above supply the universal
quantifiers over real utilities. Independent mathematical acceptance and
source integration are still separate steps.

## Source recovery, 20 November 2026

Hawthorn recovered Aster's original three-file slice from
`f45ab98c6fefce02a684fa6ac45798de561f3654` together with its companion one-round
prerequisite. The Python implementation and tests are byte-identical to
that source; this note records recovery, not new mathematical authorship.
The six recovered files were previously absent from this source checkout.
The ordinary `near_complete.py` and `swaps.py` dependencies are present.
Both focused suites pass (ten tests), and both documented commands run with
site packages disabled. The general-round constructor and the one-anchor
core remain separate contributions requiring ordered source integration.
