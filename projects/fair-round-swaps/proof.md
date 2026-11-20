# Two agents can stay within picking outcomes

**Theorem, 20 November 2026. Author: Linnet. Independently reconstructed by
Hawthorn at source `aa358ec`; see the acceptance record below.**

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

The full question allows any number of agents. The theorem below resolves only
**two** agents, including an odd number of goods. It does not claim that the
three-or-more-agent question is settled, nor that arbitrary EF1 endpoints are
connected.

Source: [Frank and Suksompong, *Reconfiguration in Fair Division Revisited*,
arXiv:2609.15358v1](https://arxiv.org/html/2609.15358v1), read 20 November 2026,
section 2 and Theorems 3.2–3.3 through Proposition 3.4. Their complete-round
induction is the starting point here; the new step is the two-agent terminal
case below. Priority has not been established by an exhaustive literature search.

## Theorem

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
and its finite checks. The mathematical text above is unchanged from that
reviewed source.

The full contribution `ed36452` subsequently passed independent source review
and the project test suite: journal receipt 23395 integrates it as `70c1f6c`,
and receipt 23413 records remote equality. The first milestone is accepted on
the frozen model, this theorem and the published four-good reconstruction.
The separate extension in `FRONTIER.md` remains mathematically provisional;
the general three-or-more-agent EF1 question remains open here.
