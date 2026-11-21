# Fair exchange paths after any final round

**20 November 2026.** The general construction combines Mica and Mallow's
outer induction, Fern's all-remainder extension, and Linnet's one-anchor
bridge. Hawthorn independently reconstructed the complete endpoint theorem
at Fern's `9144cb5` (journal review 24697). Mallow prepared this consolidated
exposition. The stronger two-agent result by Linnet, independently reconstructed
at `aa358ec`, is retained in the appendix.

## Frozen question and scope

There are finitely many labelled indivisible goods and labelled agents. Each
agent has a nonnegative, real-valued additive utility. At a pick the agent may
choose **any** utility-maximizing remaining good; no common or fixed tie rule is
assumed. A recursively balanced schedule consists of complete rounds, each
permuting all agents, followed by at most one round containing distinct agents.

An allocation is a partition of all goods. The two specified endpoint
allocations must each have a recursively balanced picking witness and have the
same size **vector**, not merely the same sorted bundle sizes. A move exchanges
one good of one agent with one good of a different agent. Transfers, multiple
simultaneous exchanges and temporary changes of bundle size are forbidden.
Every intermediate allocation must be EF1: for each observer i and other agent
j, deleting at most one good from j's bundle removes i's envy.

The theorem concerns these **greedy endpoints**, not arbitrary EF1 endpoints.
Only in the two-agent special case do we require every intermediate allocation
to remain a picking outcome. Write u_i(B) for agent i's value of a bundle B.

Source: [Frank and Suksompong, *Reconfiguration in Fair Division Revisited*,
arXiv:2609.15358v1](https://arxiv.org/html/2609.15358v1), read 20 November 2026,
section 2 and Theorems 3.2–3.3 through Proposition 3.4. Their complete-round
induction is the starting point for this investigation. Priority has not been
established by an exhaustive literature search.

## General endpoint theorem

For n>=2 agents and m>=1 goods, any two recursively balanced greedy picking
outcomes with the same labelled size vector connect by a finite sequence of
single exchanges through EF1 allocations with that same vector. Utilities may
be arbitrary nonnegative real numbers, including zeros and ties. The one-agent
and zero-good cases are trivial as well.

Write m=nq+r, 0<=r<n, and let F be the r agents receiving an extra good.
The proof actually connects a larger family: q greedy complete rounds followed
by an **arbitrary** assignment of the remaining r goods to F, one each. Call
these relaxed outcomes. Intermediate states of the constructed paths need not
belong to this family; their fairness is proved separately.

### 1. Free final assignments

Every relaxed outcome is EF1. For q=0 each bundle has at most one good.
Otherwise, against target j delete j's first-round good. Observer i's pick in
round t-1 precedes j's pick in round t, so it dominates that later good.
If j has a final good, i's last complete-round pick dominates it too. Summing
these disjoint comparisons proves EF1. Extra goods held by i are nonnegative.

Consequently, after a fixed greedy complete-round history, any permutation
of the final goods among F remains fair. In particular an arbitrary final
assignment can be changed to a greedy final completion by exchanges.

### 2. A protected crossing for any number of pairs

There are r>=1 double recipients D_1,...,D_r and two singleton carriers I,J.
Both carriers have the same global favorite g. Double D_d owns an original
anchor a_d that it values at least as much as every good in a tail pool T of
size r+1. Apart from g and the r anchors, all goods are in T.

Consider endpoints retaining every original anchor, with g on opposite
carriers. At each endpoint the carrier without g holds one of its favorite
goods in T; the doubles have the other tails in any assignment. These endpoints
connect in at most 2r+3 EF1 exchanges, always keeping g on a carrier and moving
at most one original anchor away from its double. Here is the construction.

**Find a common crossing.** Among the 2r+1 non-g goods, each carrier has a top
r+1 set, with ties ordered arbitrarily. Their intersection is nonempty. Choose
t in it, then improve t strictly for both carriers while possible. Such an
improvement remains in both top sets. At termination the strict upper sets

    H_I = {h : u_I(h) > u_I(t)},   H_J = {h : u_J(h) > u_J(t)}

are disjoint and have size at most r each. If t is a tail, keep all original
anchors as slot goods. If t=a_D, replace only D's slot by its favorite q in
the entire original pool T. Withhold g and t; match the r slots to the r
remaining goods, forbidding any pair wholly in H_I or wholly in H_J.

Hall's condition holds. A subset of slots containing a good outside both
upper sets sees every partner. So does a subset meeting both disjoint upper
sets. A subset contained in H_K sees at least r minus the number of partner
goods in H_K; because |H_K|<=r, this is at least the total number of slots in
H_K, and hence at least the subset's size. A perfect matching therefore exists.

Give each double its slot and its matched partner. These pairs, with carriers
holding g and t, are fair in **either** carrier orientation. A carrier holding
t tolerates every pair by the forbidden-pair rule. A carrier holding g has
a global favorite. Each ordinary double can delete a foreign anchor and pay
the remaining tail with its own anchor. If D lost a_D, its new favorite tail
q pays every foreign tail; the other doubles also tolerate D's two-tail pair.
Thus exchanging g,t joins two fair crossing states with the same double pairs.

**Attach an endpoint.** Fix the g-holder and call the other carrier S, holding
its original tail maximum z. With S:z and all anchors retained, any permutation
of the double tails is fair and needs at most r-1 exchanges.

If t is a tail, prepare the crossing assignment with z and t interchanged,
then swap them, or just permute tails if t=z. If t=a_D and z lies in D's
crossing pair {q,p}, prepare that pair with t substituted for z, then swap z,t.
These cases use at most r exchanges. Otherwise z lies in a different double
B's crossing pair {a_B,z}. There are two cases:

- If u_S(q)>=u_S(t), prepare S:z, D:{t,p}, B:{a_B,q}, with every other pair
  as in the crossing. Swap z,q, then q,t. At S:q, pairs already in their
  crossing positions are affordable because q>=_S t, while D's pair contains
  t. Every double still has its anchor. The last swap reaches the proved crossing.
- If u_S(q)<u_S(t), prepare S:z, D:{t,q}, B:{a_B,p}. Swap z,t, then z,p.
  At S:t, D's pair {q,z} is affordable because q<_S t. The pair {a_B,p} is
  affordable because the crossing pair {a_B,z} is, and p<=_S z. Double D
  retains its favorite original tail q; all other doubles retain anchors.

Preparations retain all anchors and S:z, so their fairness follows from the
tail-permutation observation. Each attachment takes at most r+1 exchanges.
Attach both endpoints to their respective crossing orientations and reverse
the second attachment: the total is at most (r+1)+1+(r+1)=2r+3. Equality cases
are included by the weak inequalities. This is Linnet's one-anchor lemma;
no solver or finite-census conclusion is used.

### 3. The one-complete-round base

We first recall the near-complete case: if |F|=n-1, relaxed outcomes connect
for any number of complete rounds. Induct backwards over a fixed greedy
prefix. With no greedy picks left, permute the free final goods. Distinct next
agents with distinct favorites commute. For a shared favorite g, run the two
carriers first and last among the eligible agents, with identical other picks.
If their alternative favorites x,y coincide, exchange g,x and finish alike.
Otherwise start the next complete round by giving each carrier its outstanding
alternative, and repeat. Maximization survives deletion of alternatives.
If this reaches the free final round, at least one carrier belongs to F.
Assign the outstanding alternative to that carrier in both runs; the resulting
allocations differ by one exchange with g.

Two tied favorites of one next agent connect through another eligible agent.
If it is alone and another complete round follows, let it take both tied goods
across the boundary in opposite orders. If no complete round follows, there
is one greedy pick and the n-1 free assignments left: when this agent is in F,
assign both tied goods to it; otherwise the remaining n goods give one to each
agent, and exchange its two tied favorites before permuting the others. This exhausts
the prefix cases, proving the near-complete lemma within relaxed outcomes.

Now suppose q=1 and 1<=r<n. Greedify free final assignments using Section 1.
For a greedy endpoint, take the earliest singleton i in its first round. If
its good b is already a global favorite, move its pick first. Otherwise a
global favorite g was taken earlier, necessarily by a double D. Give D its
favorite tail t_D, then exchange D:g with i:b.
This is fair: D can pay every other pair's tail with t_D, while every other
observer can delete b from D's pair and pay t_D with its original anchor or
singleton. Agent i now holds a global favorite.

Keep i:g fixed. Process the other original first-round picks, except D, in
their original order. D retains t_D and a provisional good a, initially b.
At each step give the next agent the better of its original good p and a,
returning the other to D. Receivers only improve, D keeps t_D, and the same
tail payments establish EF1. These are greedy picks in the new order:
the remaining goods are the unprocessed original first goods, the original
tails, and a; p dominated every later original good and every tail, so only
a can beat it. Finally D takes its preferred remaining good, and greedify
the final assignment. This reaches a genuine greedy endpoint beginning with
a singleton's global favorite. This is Aster's singleton-first reduction.

Fix r and induct on n. The base n=r+1 is the near-complete lemma. Otherwise
there are at least two singletons. Inside a fixed first singleton/favorite
class remove that singleton and its good and apply the n-1 induction. Restoring
its global favorite is safe against pairs, and others delete its whole bundle.
Different singleton agents with different favorites commute. Tied favorites
of the same singleton connect through a second singleton's favorite class.

For two singleton carriers sharing g, first let all other singletons pick with
g omitted and freeze their goods. Then let the r doubles choose anchors in a
common greedy order. The remaining r+1 goods are tails; the carriers' choices
x,y maximize their own values there. If x=y the classes join by one exchange.
Otherwise apply Section 2, choosing free final assignments to fit its endpoints.
Every frozen singleton values its own good at least as much as every non-g
core good. Each core pair therefore becomes affordable after one deletion;
comparisons in the other direction delete the spectator's entire singleton.
The whole core path lifts. Its endpoints have greedy complete-round histories
and free final assignments; greedify those assignments and join inside the
connected first-pick classes. This proves the q=1 base, including arbitrary
free finals. If r=0, all bundles are singletons and permutations suffice.

### 4. A lemma for restoring common rounds

Suppose a local EF1 path keeps g alone on one of two carriers I,J. Restore
p common complete greedy rounds executed with g omitted and all the other
local goods still available but unpicked. Write C_a for
agent a's common bundle. Assume that every observer values its own C_a at
least as much as either carrier's common bundle, except comparisons with itself.
Then every full allocation on the restored path is EF1.

For p=0 this is local EF1. If the target holds g, delete g; its local bundle
was just {g}, and the assumed common-bundle comparison pays everything left.
Otherwise delete the target's first common good. Match its later common goods
to the observer's preceding-round picks. Match a largest-valued target-local
good, if any, to the observer's last common pick: that non-g good was still
available then. Finally use local EF1 to pay for all other target-local goods
with the observer's local bundle. These payments use disjoint observer goods.
The maximum local good is paid for, not deleted a second time. This proves
the full EF1 inequality with exactly the one stated deletion.

This lemma requires g to remain a singleton. A bridge lending g to a double
does not in general lift: the concrete thirteen-good failure in
[FIVE_AGENT_EIGHT.md](FIVE_AGENT_EIGHT.md) explains why that older shortcut fails.

### 5. Induction over all complete rounds

For q=0, relaxed outcomes have only singleton bundles. Section 3 settles q=1.
For q>=2 induct on q, and within this step backwards over a fixed prefix of
the first complete round. Once that whole round is fixed, remove it and use
the q-1 induction. Restoring this round preserves EF1: delete the target's
first-round good, pay its most valuable suffix good with the observer's
first-round pick, and pay its remaining suffix using suffix EF1.

For a shorter fixed prefix, split witnesses by their next pick. Each class
is connected by the prefix induction. Different next agents with different
favorites commute. Two tied favorites of the same next agent connect through
another eligible agent; if there is none, let that agent take both tied goods
across the next complete-round boundary. This next round exists because q>=2.

It remains to join distinct carriers I,J sharing a favorite g. Put I first
and J last among current eligible agents in one run, and reverse those roles
in the other, using the same intervening picks. After g is consumed those
intervening agents see the same pool. Let x,y be I's and J's alternative
maximizers there. If x=y, exchange g,x and finish identically. Otherwise the
two remaining pools differ only by x,y. Begin the next complete round with
I:x on the first side and J:y on the second. Both are still maximizing picks
after deletion of alternatives. Repeat with identical noncarrier picks.

If r=0, the last complete round leaves only one common good after the
noncarriers pick. Thus x=y there and closure is unavoidable. If r>0 and a
carrier is in F, the free final assignment absorbs the two outstanding
alternatives into that carrier, closing by one exchange with g.

Otherwise both carriers miss F. In the last complete round put all other
singleton recipients first, then the r doubles in F. Their common picks
with g omitted produce exactly the spectators, anchors and tails of Section 3.
Use the one-anchor crossing, which keeps g alone on a carrier, and restore
the spectators as before.

Number the alternative pairs (x_t,y_t), one per complete round, from t=1 to q.
The local carrier holdings are (g,y_q) and (x_q,g). Their common goods are
C_I={x_1,...,x_(q-1)} and C_J={y_1,...,y_(q-1)}; every other agent's common
goods are its first q-1 picks, identical in the two runs. For each t<q, retain
the noncarriers' actual order, then pick I:x_t and J:y_t, with g omitted.
This is a greedy common history: noncarriers chose before either carrier
alternative, and each carrier chose its own favorite in their common pool.
In each such round a noncarrier's pick dominates both carrier picks in that
noncarrier's valuation; each carrier prefers its own pick to the other's.
Summing gives exactly the common-bundle hypotheses of Section 4. That lemma
lifts the local bridge. Every initially fixed prefix good belongs to this
common history and remains with its owner.

The bridge endpoints lie in their respective next-pick classes with permitted
free final assignments. Joining inside the classes completes the prefix
induction, and hence the q induction. The original greedy endpoints are
members of this larger family, proving the general theorem.

## Construction, scope and verification

The constructions are finite: singleton reduction processes a finite list;
the core uses a finite matching and permutations; one-round recursion removes
an agent; the outer recursion fixes a first-round pick or removes a whole
round. Same-agent tie detours immediately reduce to distinct-agent classes.
No shortest-path or polynomial-time bound for the complete construction is
claimed. The bound 2r+3 applies only to the isolated one-anchor core.

The detailed component documents are [ONE_ANCHOR_CERTIFICATE.md](ONE_ANCHOR_CERTIFICATE.md),
[ARBITRARY_SINGLE_ROUND.md](ARBITRARY_SINGLE_ROUND.md),
[ARBITRARY_FEW_FINAL.md](ARBITRARY_FEW_FINAL.md), and the
[near-complete reconstruction](NEAR_COMPLETE_RECONSTRUCTION.md).
The outer constructor's exact source is Fern `9144cb5`; its one-round
prerequisites were recovered together by Hawthorn at `c471b9c8` from Fern
`4bcf3a4` and Aster `f45ab98`. Linnet's core is `580ebf5`.

`arbitrary_few_final.py:path` takes actual greedy endpoint witnesses and returns
owner vectors. [GENERAL_INPUT.md](GENERAL_INPUT.md) describes the supplied-input
command and saved-path rechecking. Integers and rational strings are represented
exactly; real-valued universality belongs to the proof. Finite tests falsify
implementation mistakes but do not establish the universal quantifiers.
Its one-round base uses Aster's earlier, also proved last-anchor bridge; the
existence proof in Section 3 instead reuses the protected core of Section 2.
Both establish the same one-round endpoint contract. The outer multi-round
implementation uses the protected core and the common-round lemma above.

Hawthorn's independent reconstruction at journal 24697 accepted the general
theorem at the frozen source, including the spectator and common-round lifts,
q=0, r=0, r=1, all ties and nonnegative real rows. This consolidated presentation
and its updated public entry point are a new source contribution for independent
review; that earlier acceptance does not by itself publish these files or
complete the project's final delivery milestone.

## Appendix: two agents can stay within picking outcomes

The following stronger theorem and its proof are Linnet's independently
reconstructed two-agent result. Unlike the general construction, every vertex
here is a recursively balanced greedy outcome.

### Two-agent theorem

For two agents, any two recursively balanced allocations with the same size
vector are connected by pairwise exchanges **through recursively balanced
allocations with that same size vector**. In particular the path is EF1.

This holds for every finite number of goods, every pair of nonnegative additive
real utility functions, and arbitrary tie choices, which may differ between the
endpoint witnesses and between intermediate witnesses.

### Induction family

Write the agents as i and j. Freeze an arbitrary already allocated prefix.
The remaining schedule has:

1. an optional first partial round containing a nonempty subset S of {i,j};
2. zero or more complete two-agent rounds;
3. optionally a fixed final singleton L.

We omit empty rounds. A singleton followed directly by L is permitted even when
its agent equals L. Consider all allocations obtainable on the remaining goods
by varying every permitted order and every maximizing tie choice, while leaving
the prefix fixed. We prove that their exchange graph is connected. This larger
family is closed under removing a first pick. At zero, one or two remaining
goods the claim is immediate: there is either just one allocation or two goods
assigned one each, and any distinct outcomes are related by their one exchange.

Induct on the number of remaining goods. Partition witnesses by first pick
(a,g), where a belongs to S and g maximizes a's utility among remaining goods.
Inside each such class connectivity follows from induction after fixing that
pick. It remains to connect these classes.

### Different agents and different favorite goods

Suppose the first classes are (i,g) and (j,h), with g != h. They have a common
allocation: let i take g and j take h in either order, then finish identically.
Each remains a maximizer after the other's good is removed. Both picks are in
the same first round, since S contains both agents. Thus these two classes meet.

### Different agents and a shared favorite: the terminal step

Suppose both first picks take the same good g. Make two runs R and T, starting
with i:g and j:g respectively. Finish that first round with j:y in R and i:x
in T, choosing any respective maximizers after removing g.

If x=y, both runs now have the same remaining goods; finish identically.
Their allocations differ just by exchanging g and x.

If x!=y, after this round R's remaining pool is C union {x}, while T's is
C union {y}. At the next complete round, let R start with i:x and T with j:y.
These picks are valid: x and y were respective maximizers in the earlier larger
pool C union {x,y}. Both pools are now C. Finish the round with j:y' in R and
i:x' in T. If x'=y', close and finish identically. Otherwise repeat with the
new common pool and the new pair x',y'. This process consumes a complete round
each time, so it cannot continue indefinitely.

All paired x-goods are assigned to i in both runs; all paired y-goods are
assigned to j in both runs. Until closure the exceptions are g and the currently
unpaired last goods x,y. If a complete round consumes the last two goods, the
second pick in both runs must be the same good, so closure is unavoidable.

The other possibility is reaching the fixed final singleton L without closure.
Exactly one good then remains in each run: x in R, y in T. There is no common
pool left. If L=i, after the final picks the entire allocations differ only by
exchanging **g and y**. If L=j they differ only by exchanging **g and x**.
In either case both allocations have valid recursively balanced witnesses and
are one exchange apart. This is the step that uses having only two agents:
the final recipient must be one of the two agents carrying the discrepancy.

Thus classes (i,g) and (j,g) are connected whether or not the final round is
complete. No comparison between sums of utilities, or strict preferences, was
used in this construction.

### One agent, two tied first goods

Suppose the classes are (i,g) and (i,h), g!=h. Both goods are maximizers for i.
If S contains j, choose any maximizing good x for j. The preceding two cases
connect (i,g) to (j,x), and (j,x) to (i,h).

If S={i} and a complete round follows, the two classes meet. In one run i takes
g in the singleton then h first in the next complete round. In the other, i
takes h then g. These are maximizing picks because g and h tie at the top.
The pools and allocation agree after those picks; finish identically, starting
with the other agent's remaining pick in that complete round.

If no complete round follows, at most two goods remain, which is the base case.
These cases cover all first-pick classes. Their internal connectivity and their
connecting edges or intersections complete the induction.

Start with S={i,j}, followed by the required complete rounds and final singleton
if any. With an odd number of goods, equality of the endpoint size vectors fixes
that final recipient. With an even number there is no final singleton. This
proves the claimed connectivity in both cases.

### Why every intermediate allocation is EF1

In a full recursively balanced witness, observer i's (t-1)st pick precedes
agent j's t-th pick for every t>=2. The good eventually chosen in the latter
pick was still available in the former. Maximization therefore gives a
termwise utility domination. Delete j's first good and sum these inequalities;
i's remaining unmatched goods have nonnegative value. Hence i does not envy
j after that deletion. This argument applies to both observers, including when
one receives the final extra good. All paths above retain full picking witnesses,
so every vertex is EF1. Exchanges preserve the size vector by definition.

## Four-good calibration: the restriction to two agents matters

Number agents and goods from 1. Use strict utility rankings
1: g1 > g2 > g3 > g4; 2: g4 > g1 > g3 > g2;
3: g4 > g2 > g1 > g3. The size vector is (2,1,1).

Writing an allocation as the four owners of g1,g2,g3,g4, its picking outcomes
are 1312, 1123 and 2113. The first is isolated in the picking-only graph. But
the exchange path 1312 -> **3112** -> 2113 -> 1123 is EF1. Its first internal
vertex is not a picking outcome. For each singleton owner along the path, that
owner's good outranks at least one of the two goods in agent 1's bundle; this
proves EF1 for all utility magnitudes consistent with the rankings. Agent 1's
comparisons are automatic after deleting a singleton. The checker verifies
these ordinal inequalities as well as the complete finite graph for one exact
representative. This is a reconstruction of the published example, not a new
obstruction to the full EF1 question.

## Executable correspondence and acceptance

`two_agents.py:path` implements the induction, returning a maximizing-pick
witness for every output vertex. `bridge` implements the shared-favorite runs;
the singleton-tie branch takes both tied goods before the other agent acts.
Every recursive invocation either fixes a first pick or immediately routes a
same-agent tie through a different first agent and then fixes one. Thus the
construction terminates. It need not be shortest or polynomial in length.

`swaps.py` independently checks maximizing picks, EF1 inequalities and single
exchanges. Its finite state generator includes **all** allocations of a size
vector. `check.py` checks the published calibration, invalid inputs, exact
fractions and finite samples of the constructive path. Integers and Fractions
are exact; the proof, rather than a floating-point approximation or finite
census, covers arbitrary real utilities and arbitrary size.

Hawthorn independently reconstructed the induction at source `aa358ec`,
including the suffix family, arbitrary ties, both final-singleton cases and the
termwise EF1 argument. The journal lesson
`hawthorn-two-agent-suffix-reconstruction` records that mathematical acceptance
and its finite checks. This appendix retains the two-agent argument from that
reviewed source.

The full contribution `ed36452` subsequently passed independent source review
and the project test suite: journal receipt 23395 integrates it as `70c1f6c`,
and receipt 23413 records remote equality. The first milestone is accepted on
the frozen model, this theorem and the published four-good reconstruction.
Those receipts concern the first milestone. The later general endpoint result
and its separate mathematical acceptance are recorded above; they do not
promote the stronger picking-only property to three or more agents.
