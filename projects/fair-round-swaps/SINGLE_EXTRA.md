# Greedy outcomes with one extra good are connected

**Candidate theorem and construction by Sorrel, 20 November 2026.
Independent mathematical reconstruction pending. The general incomplete-round
question remains unresolved.**

Use the [frozen model](proof.md): nonnegative additive real utilities, arbitrary
maximizing ties, fixed labeled bundle sizes and exchanges of two goods only.
Here there are `n+1` goods, one agent D receives two and every other agent one.
The candidate theorem below connects any two greedy one-round-plus-one-pick
outcomes. It covers arbitrary n and ties, but only n+1 goods. The stronger claim
that the **entire** EF1 graph is connected fails already at five agents.

This is a proposed subcase result, not an answer for arbitrary incomplete rounds.
No literature priority is claimed.

## The exact ordinal reduction

Write D's goods as g,h and singleton i's good as x_i. The allocation is EF1
exactly when, for each singleton i,

`u_i(x_i) >= min(u_i(g), u_i(h))`.                                      (1)

Comparisons with a singleton bundle become automatic after deleting its only
good. Thus D imposes no restriction, and (1) is necessary and sufficient.
In this size vector, only singleton agents' weak orders matter. This extends
the same elementary reduction used in the four-good investigation; it does
not extend to size vectors with larger bundles.

## Candidate one-extra-good theorem

For every n>=2, any two recursively balanced picking outcomes with n+1 goods
and the same doubled recipient D have an EF1 exchange path. Intermediate
allocations need not themselves be picking outcomes. The constructor `path`
implements the following induction; it makes no shortest-path or polynomial
running-time claim.

### The local bridge: never put both distinguished goods together

Suppose three agents have local endpoints

* A: D={g,x}, i={h}, j={y};
* B: D={g,y}, i={x}, j={h},

where i and j each value h at least as much as x and y. Assume both endpoints
are EF1. Other singleton agents, if present, are fixed and each values its own
good at least as much as x and y; they may value g or h more highly.

There is an EF1 path of at most three exchanges which never gives D both g,h.
First try swapping h,y in A, yielding C: D={g,x}, i={y}, j={h}. If C is EF1,
swap x,y to reach B. Otherwise try swapping x,y in A, yielding E:
D={g,y}, i={h}, j={x}. If E is EF1, swap h,x to reach B.

If both trials fail, only i can fail at C, and only j can fail at E. D's
comparison with a singleton is automatic; fixed observers see an endpoint
pair; and the holder of h satisfies (1). Thus

`u_i(y) < min(u_i(g),u_i(x))`, and
`u_j(x) < min(u_j(g),u_j(y))`.

Use instead

`A -> (D={x,y},i={h},j={g}) -> (D={x,y},i={g},j={h}) -> B`.

In the first middle state j values g above x, the smaller of x,y in j's
ordering. In the second i values g above y, the smaller in i's ordering.
The holder of h is safe in both. Every fixed observer dominates x,y, and D
has only singleton bundles to compare with. Both middle states are EF1.
This proves the bridge, including ties and the forbidden-pair property.

### Induction and removal of a singleton

The base n=2 is immediate: each fixed-size allocation is determined by the
singleton's good, so any two distinct EF1 allocations are one exchange apart.
Induct on n. All connectivity below is in the **ambient EF1 graph**: a path
between endpoints in one picking class may leave that class.

If a fixed singleton i receives a good z which it values at least as much as
every remaining good except possibly one distinguished good g, any EF1 path
on the remaining agents and goods lifts after restoring i:z. Indeed, D's pair
contains at most one copy of g, so i can remove it and compare with the other
good, worth at most z. Other comparisons with or by singleton bundles are
automatic. This observation also applies when there is no exceptional g.

Removing a singleton and its good from a greedy witness preserves greedy
choices on the reduced instance: earlier maximizing picks only lose an
alternative, while later pools agree after the removed pick. The remaining
size vector again has one double bundle and all other bundles singleton.

### All endpoints beginning with D:g can be connected

Fix D's first maximizing good g. Partition these witnesses by the second
pick i:h, necessarily by a singleton. Within one such second-pick class,
remove i,h and apply the n-1 induction hypothesis. Here h maximizes i's
utility on all goods except g, so the lifting observation applies.

For two different second agents i,j with distinct favorites h,k, the classes
have a common allocation: execute D:g, i:h, j:k or D:g, j:k, i:h, then finish
alike. Removal of a different favorite cannot invalidate a maximizing pick.

If they share favorite h, put all other singleton agents in the same order
following D:g and i:h (respectively j:h). They see identical remaining pools
and take identical goods. Two goods remain, say x,y. In one witness j takes
its favorite of these and D the last; in the other i takes its favorite and
D the last. If the singleton choices coincide, exchanging h with that good
connects the endpoints directly. Otherwise the endpoints have the local
bridge's form. The fixed singleton observers picked while x,y were still
available, so they dominate both. They might prefer g,h, but the bridge never
puts both in D's bundle. It therefore lifts to the entire allocation.

Two tied second goods for the same singleton connect through any other
singleton's maximizing second-pick class, using the preceding cases. For
n>=3 another singleton exists; n=2 was the base. Every second-pick class can
therefore reach every other, establishing the assertion about D:g.

### Connect all first-pick classes

Partition full witnesses by their first pick i:g. If i is a singleton, remove
i,g and apply induction; g is a global favorite for i, so lifting holds without
an exception. If i=D, the preceding argument gives the required connectivity.

For different first agents with distinct favorite goods, classes intersect
by executing those two picks in either order and finishing alike.

For different singleton first agents i,j sharing favorite g, let all other
singletons pick identically after g is removed. Let D next pick the same
maximizer h from the three remaining goods. Finally, the other singleton
picks and D receives the last good. Equal last singleton choices give one
exchange. Distinct choices give the local bridge with g as the shared good
and h as the other distinguished good. Fixed singleton observers dominate
h,x,y, so the bridge is EF1 in the full instance.

For D and singleton i sharing favorite g, put every other singleton in the
same order after removing g. Let i choose its favorite x from the last two
goods in the D-first run, with D taking the last y. In the i-first run, D
gets both x,y (choosing its favorite first). The endpoints differ only by
exchanging g,x. Both are greedy outcomes.

Finally, two tied first goods of the same agent connect through any other
agent's maximizing first-pick class. The classes exhaust all endpoint
witnesses, completing the induction. No argument requires strict preferences.

## Five is the least number of agents permitting an isolated EF1 state

**No-isolation theorem.** For `2 <= n <= 4`, every EF1 allocation with sizes
`(2,1,...,1)` has an EF1 neighbor, for arbitrary utilities and ties.

For each singleton i choose its preferred good s_i from g,h, breaking a tie
arbitrarily; let t_i be the other. Try exchanging x_i with s_i. Agent i remains
EF1, since its new good is at least t_i. If the exchange fails, (1) supplies
another singleton j for which

`u_j(t_i) > u_j(x_j)` and `u_j(x_i) > u_j(x_j)`.                        (2)

The original allocation satisfies (1), so (2) also implies
`u_j(s_i) <= u_j(x_j) < u_j(t_i)`. Hence j strictly prefers t_i: its chosen
spare is the opposite of i's chosen spare. Draw an arrow i -> j for one such
blocker. If all attempted exchanges fail, every singleton has an outgoing
arrow, and every arrow crosses the two preferred-spare classes.

A finite directed graph with positive out-degree has a directed cycle. There
are at most three singleton vertices here. A cycle in this bipartite graph
therefore has length two. Its two agents strictly prefer each other's current
goods, by (2). Exchanging those goods improves both; D's pair is unchanged and
all other singleton comparisons remain automatic. This is an EF1 neighbor,
contradicting isolation. The proof covers ties because a blocker always has
a strict preference between the two spares.

`neighbor_up_to_four` implements this proof: try each preferred-spare exchange,
then a mutually improving singleton exchange. This theorem rules out isolated
vertices, **not disconnected components with more than one vertex**.

**Isolation construction.** For every `n >= 5` there is an isolated EF1 state
with this size vector. There are k=n-1 singleton goods x_0,...,x_(k-1), plus
g,h. Initially singleton i owns x_i and D owns g,h. D's values are arbitrary.
The four core singleton rows, in columns x_0,x_1,x_2,x_3,g,h, are

| Singleton | x_0 | x_1 | x_2 | x_3 | g | h |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 2 | 3 | 0 | 0 | 4 | 1 |
| 1 | 0 | 2 | 3 | 0 | 1 | 4 |
| 2 | 0 | 0 | 2 | 3 | 4 | 1 |
| 3 | 3 | 0 | 0 | 2 | 1 | 4 |

For each extra singleton i>=4, give it values 2 for x_i, 4 for g, 1 for h,
and 0 for every other singleton good. Core singleton 1 values every extra
x_i at 3; the other core singletons value them at 0.

Every singleton's own value is 2 and the smaller spare value is 1, so (1)
holds. Every possible exchange fails:

* Between singleton agents, at least one recipient values the incoming good
  at 0. It then envies both spares, valued 1 and 4. The directed positive
  comparisons are a four-cycle plus arrows from core singleton 1 to the extra
  goods; no pair has positive comparisons in both directions.
* Giving a singleton its less-preferred spare gives it value 1 while D has
  that singleton's old good and its preferred spare, valued 2 and 4.
* Giving core singleton i its preferred spare puts x_i beside the other
  spare in D. Core singleton `(i-1) mod 4` values that pair at 3 and 4, above
  its own value 2. For an extra singleton the blocker is core singleton 1.

There are no other exchanges between distinct owners. Rotating the four core
goods so that each core singleton receives its successor's good gives a
different EF1 allocation (own value 3, or 2 for the extras), so the graph is
disconnected. This proves both the family and the claimed minimum of five
agents **for isolation in this size vector**.

The construction survives any changes of magnitudes that preserve the stated
strict tier comparisons. It can have strict preferences over every good:
replace tier value v of good index j by `(n+1)*v+j`. Different tiers stay
ordered and all ties disappear. D may also use this strict refinement.

## Why this does not refute greedy-endpoint connectivity

In a greedy execution the last good h stays available throughout the full
round. Every singleton must therefore value its own good at least h. Call a
good in D's pair **safe** if this inequality holds for every singleton.

**Safe-spare lemma.** Every EF1 allocation with a safe spare has an EF1
neighbor, for every n>=2. Write h for a safe spare and g for the other. If
some singleton i values g at least h, exchange its own good with g. Agent i
and every other singleton meet (1) using h. Otherwise every singleton strictly
prefers h to g. Then g is also safe; exchange h with any singleton and use g
in (1). This is always an exchange between distinct owners.

In the isolated family, both g and h are valued at 4 by some singleton who
owns a value-2 good. Neither is safe. The same is true after rotating the core
goods (their value becomes 3, still below 4). Neither displayed endpoint can
be a greedy outcome. In particular, no isolated allocation in this size
vector can itself supply a required greedy endpoint. The candidate theorem
above further rules out separated greedy-containing components in this
one-extra-good case; it does not classify every other component.

## Recognizing greedy endpoints without enumerating schedules

For each of the two choices of final good h in D's pair, let p_i be singleton
i's current good and p_D the other good in D's pair. Require
`u_i(p_i) >= u_i(h)` for **all first-round agents, including D**. For each
strict preference `u_i(p_j) > u_i(p_i)`, add precedence edge j -> i.

The allocation is a greedy endpoint exactly when one choice of h passes the
inequalities and has an acyclic precedence graph. Necessity follows because
every strictly preferred p_j must have been taken before i, and h is never
taken during the full round. Conversely, a topological order takes every
strictly preferred first-round good before i; all remaining goods are worth
at most p_i, including h. Thus each pick maximizes utility. Append D:h to
complete a witness. Tied goods impose no edge, matching the frozen tie rule.

`greedy_witness` returns that witness or `None`. It uses polynomially many
comparisons (the simple topological implementation is O(n^3)), rather than
enumerating n! schedules. A safe spare alone is not sufficient: the precedence
graph may have a cycle, or D may prefer the proposed final good.

## Reproduce and challenge it

From the repository root, using Python 3.10+ and no extra dependencies:

```sh
python3 projects/fair-round-swaps/single_extra.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_single_extra.py
```

Recorded output:

```text
five agents, six goods: 360 fixed-size states
EF1 states: 90; component sizes: [1, 89]
greedy endpoints: 24; all in the same component: True
isolated state: 123400; all 14 possible exchanges violate EF1
second EF1 state: 412300; neither state is a greedy endpoint
one-extra construction: 276 greedy endpoint pairs; longest constructed path 14 swaps
family checks: n=5,6,7,10,25, both tied and strict utilities
Scope: one-extra theorem is a candidate; multiple full rounds remain open
```

Owner vectors use agent 0 for D. The test suite uses direct deletion tests for
fairness, independently walks the complete six-good graph, compares the
precedence recognizer with exhaustive picking outcomes, and exercises 22,155
fair binary profile cases up to four agents. It also checks the local bridge
including ties, every greedy endpoint pair in all 4,096 binary three-agent
profiles, and sampled paths through ten agents. The universal statements rest
on the proofs above, not these finite checks. Candidate mathematics and the
recognizer still need independent reconstruction.

## Prior work and the next obligation

[Igarashi, Kamiyama, Suksompong and Yuen (2024)](https://d-nb.info/1354998618/34)
already prove disconnected EF1 graphs, including allocations with no EF1
neighbor. The inspected examples in Theorems 3.1, 4.8 and 4.9 have size vectors
(4,4), (2,2,0) and (3,3,1), respectively. This note addresses the narrower
(2,1,...,1) boundary; it does not claim to discover isolation in fair division.
[Frank and Suksompong (2026)](https://arxiv.org/html/2609.15358v1), Theorems
3.2–3.3 and Proposition 3.4, supply the project's actual greedy-endpoint question.
The opened prior texts and a bounded search do not establish priority.

The full arbitrary-length question remains unresolved. The next useful step
is independent reconstruction of the lifting and first-D-good argument above,
then work on multiple complete rounds with a remainder between 1 and n-2.
Removing an agent with several goods no longer gives the simple singleton
lifting argument. Enlarging the isolated family or counting more profiles
would not discharge that obligation. The provisional near-complete-round proof
also still requires its own independent mathematical reconstruction.
