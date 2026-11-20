# Four agents, any number of rounds, and two final recipients

Theorem by Sorrel, 20 November 2026. **Aster independently reconstructed the
mathematical argument at journal 23698.** Source integration of this run remains
separate. No priority claim is made. The arbitrary-agent problem remains open.

**Theorem.** For four agents and `4q+2` goods, q>=1, any two greedy recursively
balanced outcomes with the same size vector have a single-exchange EF1 path.
Utilities are arbitrary nonnegative additive reals and all maximizing ties are
allowed. Intermediate allocations need not be picking outcomes.

Relabel the two final recipients D,E as 0,1 and the singleton-round recipients
i,j as 2,3. This note builds on the six-good base case in
[TWO_FINAL_EXTENSION.md](TWO_FINAL_EXTENSION.md). It proves the missing lift;
it does not change that document's recorded scope or review status.

## Why the naive lift fails

A fair six-good path does not automatically stay fair when earlier goods are
put back. In the exact ten-good example in `four_agent_lift.py`, the common
prefix goods belong to D,E,i,j respectively as 3,1,5,7. The six remaining
goods, in the order g,k,l,x,y,z, are 4,8,9,6,2,0.

Both complete endpoint witnesses are greedy, including their final picks:

```
A: 2:4 0:3 1:1 3:7 | 2:5 0:8 1:9 3:2 | 0:6 1:0
B: 3:4 0:3 1:1 2:5 | 3:7 0:8 1:9 2:6 | 0:2 1:0
```

The six-good loan path first puts g into E's double bundle. Its locally fair
state lifts to agent i holding goods 5,9, worth 20+5=25. E holds 0,1,4, worth
0+100+100 to i. Even the best deletion leaves 100. This is an exact failure
of that lift, not a separating counterexample to the connectivity question.

The repair is to keep g with i or j throughout the local path. The following
two lemmas show that this restriction is always possible, not merely possible
in this example.

## 1. Every three-agent five-good EF1 graph is connected

Fix sizes (2,2,1), with double recipients D,E and singleton C. A singleton
good is *safe* if at most one of the five goods is strictly more valuable to
C. There are at least two safe goods, counting labels even when values tie.
A safe singleton never envies either pair after deleting one good.

### Reach a safe singleton in at most two exchanges

Suppose C's good b is not safe. EF1 prevents either pair from containing two
goods strictly above b. Therefore exactly two goods are above b: write the
allocation as D={f,e}, E={h,t}, C={b}, where f,h are above b and e,t are no
better than b in C's valuation. Both f and h are safe.

Try the two direct upgrades b,f and b,h. In the first trial D may fail its
comparison with E (call this U_D), or E may fail with D (U_E). In the second
trial E may fail (V_E), or D may fail (V_D). The failure inequalities are:

| Failure | Strict inequality, in the indicated observer's valuation |
| --- | --- |
| U_D | b+e < min(h,t), for D |
| U_E | h+t < min(b,e), for E |
| V_E | b+t < min(f,e), for E |
| V_D | f+e < min(b,t), for D |

C is safe in either trial, so these exhaust failures. U_D and V_D cannot
both hold: U_D and original fairness imply `f+e>=min(h,t)>b+e`, hence f>b,
contradicting V_D. Likewise U_E and V_E cannot both hold, using original
fairness of E. If both trials fail, the failures must therefore include
either (U_D,V_E) or (U_E,V_D).

In either case D values t strictly above e, and E values e strictly above
both b and t. Exchange the low goods e,t between D,E. Both double recipients
remain fair: D now has t>e, the smaller possible remainder in E's pair;
E has e>t, the smaller possible remainder in D's pair. C remains EF1 against
both pairs because each contains only one of f,h, although b is not yet
top-two safe. Now exchange b,f.
D={b,t} is fair against E={h,e} because t>e in D's valuation. E is fair
against D because e>b in E's valuation. C now holds safe f. This proves
the two-exchange bound.

### Connect safe singleton states

With C's safe good fixed, only the comparisons between D and E matter. On
four remaining goods, a double recipient can exclude at most one of the six
labeled 2+2 allocations: an unfair pair can contain neither of its two
highest-valued remaining goods, so only the pair of the other two can fail.
The six allocations form an octahedron exchange graph. Distinct vertices
are adjacent unless their D bundles are complements. Such opposite vertices
have four common neighbors. Deleting at most two unfair vertices therefore
leaves a connected graph of diameter at most two.

Now take two different safe singleton goods b,c. The six allocations of the
remaining four goods with C holding b correspond bijectively to the six with
C holding c: replace c by b in its double bundle and exchange b,c. Each
double recipient rules out at most one allocation before this exchange and
at most one after it. At most four of the six possibilities fail, so a fair
crossing exists. Both singleton holdings are safe. Combined with the fixed
singleton fibers, this connects the safe states in at most five exchanges.
Together with the two endpoint upgrades, the whole graph has diameter at
most nine. The bound is only an upper bound, not a claim of sharpness.

## 2. A six-good bridge that keeps the favorite with a singleton

There are now four agents with sizes (2,2,1,1). Suppose g is a favorite of
both singleton agents i,j. The subgraph in which g remains with either i or j
is connected, for **all its EF1 vertices**.

With its holder fixed, remove that holder and g. The remaining graph has
three agents and five goods with sizes (2,2,1), and is connected by Section 1.
Adding g back preserves fairness because its holder has a global favorite
and everyone else can delete that singleton bundle.

To cross between the two holders, consider the other five goods. Each
singleton has at least three goods with at most two strictly better labels.
Their two sets intersect. Choose a member t that has no good strictly better
for **both** agents: starting at any member of the intersection and ascending
a common strict improvement must terminate there, still inside the intersection.
The strict upper sets H_i,H_j of t are disjoint and each has size at most two.

Give t to the singleton not holding g and partition the other four goods
between D,E. A singleton can object only if its two strictly better goods
form one of those pairs. If both upper sets have size two, disjointness makes
them complementary; they forbid the same two labeled allocations. If one
set has fewer than two goods, it forbids nothing. Hence at most two of the
six pair allocations fail either singleton's constraint.

Each double recipient excludes at most one more allocation, as in Section 1.
At least two of the six allocations therefore satisfy all constraints with
either assignment of g,t to i,j. Exchanging g,t gives the crossing. This
proves the connectedness assertion and supplies a finite construction: search
the at most sixty EF1 vertices that keep g with i,j. `carrier_path` does this.

## 3. Padding while protecting the favorite

Let C be r complete greedy rounds on the goods **with g omitted**, leaving
five other goods besides g. Let C_a denote agent a's common prefix bundle.
Assume, for b=i or j and a!=b,

`u_a(C_a) >= u_a(C_b)`.

Take any EF1 allocation T of the six tail goods in which g belongs to i or j.
Then `C+T` is EF1. To prove this, compare a with b.

* If b holds g, delete g. Its tail bundle was a singleton. The assumed common
  bundle inequality, plus nonnegativity of a's tail, settles the comparison.
* Otherwise b's tail contains no g. If r=0, use tail EF1 directly. If r>0,
  delete b's first prefix good. Match b's subsequent prefix goods to a's
  preceding-round prefix goods. The last prefix good of a dominates every
  good in b's tail, since all five non-g tail goods were still available.
  Tail EF1 pays for the rest after its largest good is removed. Summing
  these inequalities proves the full comparison.

This proves every state of a protected local path lifts. It also explains
the failure above: if g enters E's tail, E is no longer an allowed protected
holder, and the displayed common-bundle inequality need not hold toward E.
`padded_path` checks both hypotheses and every resulting full allocation.

## 4. The arbitrary-round induction

Enlarge the endpoints to greedy complete rounds followed by arbitrary final
assignments to D,E. The free-final-round lemma makes every such endpoint EF1.
Induct on q. The q=1 case is [the six-good theorem](TWO_FINAL_EXTENSION.md).

For q>=2, also induct backwards over a fixed prefix of the first complete
round. Once that whole round is fixed, remove it, apply the q-1 theorem, and
put it back. This is safe for any EF1 suffix path: delete the other agent's
fixed first good and use one's own first good to pay for the good deleted
by suffix EF1. That own first good was chosen before every suffix good.

Partition continuations by their next greedy pick. Within each class the
first-round prefix grows, so the inner induction applies. Distinct agents
with distinct maximizing goods commute. For distinct agents sharing g,
use the ordinary two-run braid: other eligible agents make identical picks
from their common pool, the other carrier picks last, and in each subsequent
round the first carrier picks its previous unmatched good before the common
picks. Equality of the last choices closes the braid in one exchange. If
one carrier is a final recipient, it absorbs the unmatched final good and
again closes in one exchange, using the free final assignments.

The remaining case has exactly the two singleton carriers i,j. In every
round t write k_t,l_t for D,E's common picks and x_t,y_t for the two last
choices from the same common pool. They differ until the final round;
otherwise use the early closure just described. Their allocations agree
outside the six goods

`g, k_q, l_q, x_q, y_q, z`.

The common bundles contain k_t,l_t,x_t,y_t for t<q. They form q-1 complete
greedy rounds with g omitted: keep the original D,E order, then choose x_t
and y_t in either order. Both are maximizing in the pool before either is
removed. This also verifies that the next common round sees the right pool.
D and E pick before x_t,y_t, so each values its common good at least each
carrier's common good. Each carrier values its own last choice at least
the other's, since both choices maximize on that same pool. Sum over t<q
to obtain exactly the common-bundle inequalities in Section 3.

Apply Section 2 to the six tail goods, protecting g, then Section 3 to put
the common bundles back. Since q>=2, every originally fixed first-round
prefix good is in those common bundles and never moves. Only D,E could
have appeared before the two singleton carriers; their original prefix order
is retained when constructing the first common round.

Finally, two tied next goods of the same agent connect through another eligible
agent's class. If that agent is alone at the end of the first round, let it
take both tied goods across the round boundary in either order. A full next
round exists because q>=2, and the resulting allocations coincide. This
exhausts next-pick classes, completing both inductions.

## Computation and limits

```sh
python3 projects/fair-round-swaps/four_agent_lift.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_four_agent_lift.py -v
```

The exact ten-good repair printed by the first command is

```
1130220301 -> 1100220331 -> 1100320321 -> 1100322301
```

All three exchanges are EF1 after padding, and g stays with i or j.
`five_path` searches the full 30-vertex size graph, `carrier_path` the
protected 60-vertex graph, and `padded_path` checks the actual lifting
hypotheses. `path` accepts fully greedy four-agent witnesses with 4q+2 goods
and fixed final recipients 0,1. It implements the outer round induction,
inner first-round-prefix induction, and shared-favorite braid above. Only
the six-good base case and protected bridge use graph search (at most 180
and 60 states respectively); larger prefixes are retained and lifted. The
recursion makes no shortest-path or polynomial-complexity guarantee. The
proof supplies existence independently of any finite numerical screen.

All comparisons in code use exact integers or rational numbers. The theorem
itself permits arbitrary real nonnegative values. The tests independently
try EF1 deletions, exercise the failed lift and its repair, test protected
padding through seven complete rounds, retain each possible fixed first-round
prefix in the ten-good braid, and construct fresh rational and all-zero paths
through six complete rounds. An installed symbolic solver
was used in exploratory work; none is required by the delivered command,
tests, or mathematical proof.

Four-agent remainder one, larger agent counts and the full project milestone
are still unresolved. Do not generalize the two-carrier argument to a third
singleton observer without a new proof of its padding comparisons.
