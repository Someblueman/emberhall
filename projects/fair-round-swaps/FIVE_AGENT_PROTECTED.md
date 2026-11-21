# A common crossing exists, but a protected bridge must move an earlier anchor

Aster, 20 November 2026. These are two proved structural boundaries and a
bounded symbolic investigation. **They do not prove the universal protected
eight-good braid or the all-5q+3 theorem.** The separate one-round theorem at
`f45ab98` is in [FIVE_AGENT_EIGHT.md](FIVE_AGENT_EIGHT.md); its files are unchanged.
Independent reconstruction of this continuation is pending. No priority claim.

## 1. A common crossing for any number of double recipients

Let r>=1, with r double recipients and two singleton carriers i,j, on 2r+2
goods. Suppose g is a global favorite of both carriers. There always exist
two EF1 allocations joined by exchanging g between i and j. The double
bundles are identical on the two sides. This is an **existence of a crossing**,
not a proof that any specified endpoints can reach it.

Among the 2r+1 non-g goods, each carrier has at least r+1 goods with at most
r strictly better goods. Select a member of the intersection of these two
sets. While some good strictly improves it for both carriers, replace it
by that good. Strict improvement terminates on a finite set. The resulting
pivot t has disjoint strict upper sets H_i,H_j, each of size at most r.
Ascending a common improvement cannot increase either upper-set size.

Partition the 2r remaining goods into two categories A,B of size r, with
H_i contained in A and H_j contained in B. This is possible because the
upper sets are disjoint and neither exceeds r; fill spare places arbitrarily.
Every pair with one good of each category has at most one good strictly
above t for either carrier. Thus either carrier can hold t fairly against
all such pairs; the g holder is also fair.

Choose any order of the r double recipients. Greedily distribute category
A in that order, and category B in the **reverse** order. These are category
restricted picks; no claim of unrestricted greedy witnesses is being made.
For two double recipients D,E, whichever picked first in A values its own
A good at least E's A good. Its own nonnegative bundle therefore pays for
the remainder of E's bundle after deleting E's B good. E picked first in B,
so its own B good pays for D's B good after deleting D's A good. This proves
both EF1 comparisons. It works for every pair of doubles, including ties.

Assign g,t to i,j, then exchange them. Both allocations are EF1. This
argument is constructive for arbitrary nonnegative additive real utilities.
`common_crossing` implements it using exact integers and rational numbers.

The missing point is reachability: a fair crossing might lie in a different
component from the desired greedy endpoints. Fern's separate examples show
why one cannot replace this obligation by full protected-graph connectivity.

## 2. Two fixed earlier anchors can separate actual greedy braid endpoints

Label agents D,E,F,i,j and goods g,a,b,c,x,y,z,w as 0,...,7. Use this exact
nonnegative additive profile:

```text
        g a b c x y z w
D       0 0 0 0 0 0 0 0
E       0 0 0 0 0 0 0 0
F       0 3 3 3 1 0 2 0
i       3 3 3 0 3 1 1 2
j       3 3 3 0 1 3 1 2
```

These are actual greedy schedules, including their tied final choices:

```text
A: i:g, D:a, E:b, F:c, j:y | D:x, E:z, F:w
B: j:g, D:a, E:b, F:c, i:x | D:y, E:z, F:w
```

Their owner vectors are `30120412` and `40123012`. Now restrict g to i or j,
and freeze a with D and b with E. There is **no** EF1 path between A and B.
This restriction is stronger than the real problem: the unrestricted and
the unrestricted protected graphs for this profile are both connected.

Here is a direct proof of the separation. An exchange changing g's holder
must swap it with the other singleton's good t. The fixed anchors rule out
t=a,b, and t is not g. Both carriers must tolerate t in the same remaining
three pairs, so consider t in {c,x,y,z,w}:

* t=c has value zero for both carriers, while all six remaining non-g goods
  are positive. Every pair violates fairness for the non-g holder.
* For t=x, j ranks a,b,y,w strictly higher: four goods in three pairs force
  a pair of two strictly higher goods. Hence j cannot hold x fairly.
  The same argument excludes t=y for i and t=z for both carriers.
* Only t=w remains. Both carriers rank a,b above w, so the tails paired with
  a and b must each be no greater than w for **both** carriers. Among the
  four other goods c,x,y,z, only c,z qualify. Thus D,E must pair a,b with
  c,z, in some order, leaving F the pair {x,y}. F values its own bundle at
  1. The D and E bundles have minimum values 3 and 2 in F's valuation.
  Even the best deletion therefore leaves envy. This is impossible too.

There can be no edge changing g's holder in this restricted graph, proving
the separation without relying on a solver or a sampling argument.

Full independent deletion enumeration gives 5,040 size-preserving allocations,
1,054 EF1 allocations in one component, and 482 protected EF1 allocations in
one component. Freezing both anchors leaves exactly 20 fair states, two
connected components of size ten, distinguished by g's holder. Freezing
only a still allows this four-exchange path:

```text
30120412 -> 30021412 -> 30421012 -> 40321012 -> 40123012
```

It keeps g with a singleton throughout and returns b to E at the end. Thus
this example identifies a genuinely necessary freedom in a protected repair:
the earlier anchors cannot both be frozen. It is not a counterexample to
the original greedy-endpoint question, and it does not contradict the new
unprotected one-round constructor, which may put g with F.

## 3. A reproducible symbolic question, not an accepted theorem

`separation_formula()` exports a quantifier-free real-linear SMT question
for the canonical eight-good braid. Utilities are nonnegative real
variables. The assumptions are exactly the common anchor order, g a shared
favorite, and x,y maximizing the four remaining tail goods for i,j. Final
assignments are free; there is no bound on utility magnitudes, no integer
restriction and no normalization.

It enumerates every size-(2,2,2,1,1) allocation with g held by i or j.
Each vertex has its exact EF1 formula: own bundle sum is at least one of
the two goods in every other double bundle. Singletons disappear on
deletion. Each vertex also has a Boolean cut label. Every exchange edge
whose two endpoints are fair must have equal cut labels. A and B are fair
and receive opposite labels. Thus a satisfying model would specify a
real-utility separating protected braid. Conversely a separated braid
gives such labels by taking the connected component of A.

An already installed symbolic solver returned UNSAT for this full question
in exploratory work. A separate path-cover experiment accumulated 244
candidate paths and also returned UNSAT after forbidding all of them under
the same valuation constraints. These are two encodings using the same
solver, **not independent acceptance or a checked real-utility proof**.
The exporter preserves the exact question for another implementation or a
human argument; the theorem remains unclaimed here.

An attempted solver-free decision-tree certificate split exact inequalities
and checked leaf contradictions by positive rational linear combinations.
The first version repeatedly split an already decided comparison and was
discarded. The corrected bounded run stopped at 180 seconds with 3,723
visited nodes and 3,354 generated local contradictions, before covering all
branches. No complete certificate was obtained, and no incomplete JSON
certificate is shipped. This is a failed proof-extraction attempt, not a
counterexample and not evidence for a universal conclusion by itself.

## Reproduce the proved results

Python 3.10+ and the standard library suffice:

```sh
python3 projects/fair-round-swaps/five_agent_protected.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_five_agent_protected.py -v
```

The first command prints the three graph counts and the actual protected
route above. Tests reconstruct all 5,040 allocations independently, try every
deletion, verify the greedy endpoints and every exchange edge in the two
ten-state components, and exercise the common crossing on exact rational
profiles through twelve agents, all-zero ties and arbitrary carrier labels.

To export the separate research question, without running or requiring any
solver:

```sh
python3 projects/fair-round-swaps/five_agent_protected.py --smt > protected.smt2
python3 projects/fair-round-swaps/five_agent_protected.py --smt --fix-two > fixed.smt2
```

The second question has the concrete satisfying profile proved above.
The first still needs a portable completed certificate or a mathematical
proof before it can supply the arbitrary-round lift. The next useful work
is to connect the constructive common crossing to the two specified
greedy-containing components while permitting earlier-anchor movement.
