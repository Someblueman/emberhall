# One extra good: isolation is the wrong counterexample target

**Candidate boundary results by Sorrel, 20 November 2026. Independent
mathematical reconstruction pending. The greedy-endpoint question is unresolved.**

Use the [frozen model](proof.md): nonnegative additive real utilities, arbitrary
maximizing ties, fixed labeled bundle sizes and exchanges of two goods only.
Here there are `n+1` goods, one agent D receives two and every other agent one.
The question is whether two greedy one-round-plus-one-pick outcomes can be
connected through EF1 allocations. The attempted stronger lemma, that the
**entire** EF1 graph is connected, fails already at five agents.

The results below give a precise obstruction to that shortcut, not an answer
to the project's full question. No literature priority is claimed.

## The exact ordinal reduction

Write D's goods as g,h and singleton i's good as x_i. The allocation is EF1
exactly when, for each singleton i,

`u_i(x_i) >= min(u_i(g), u_i(h))`.                                      (1)

Comparisons with a singleton bundle become automatic after deleting its only
good. Thus D imposes no restriction, and (1) is necessary and sufficient.
In this size vector, only singleton agents' weak orders matter. This extends
the same elementary reduction used in the four-good investigation; it does
not extend to size vectors with larger bundles.

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
vector can itself supply the required greedy endpoint. A negative answer to
the original question here needs distinct **non-singleton components**, each
containing a verified greedy endpoint.

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
family checks: n=5,6,7,10,25, both tied and strict utilities
Scope: defeats all-EF1 connectivity; greedy-endpoint question remains open
```

Owner vectors use agent 0 for D. The test suite uses direct deletion tests for
fairness, independently walks the complete six-good graph, compares the
precedence recognizer with exhaustive picking outcomes, and exercises 22,155
fair binary profile cases up to four agents. The universal statements rest
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

The full arbitrary-agent question, even its one-extra-good restriction,
remains unresolved here. The next useful step is a path argument specifically
for greedy-containing components, or a separating example whose **both**
endpoints pass the precedence test. Enlarging the isolated family, counting
more profiles, or relabeling these non-greedy endpoints would not meet that
obligation. The provisional near-complete-round proof also still requires
its own independent mathematical reconstruction.
