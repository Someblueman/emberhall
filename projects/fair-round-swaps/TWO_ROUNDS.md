# Three agents with one final good

**Candidate theorem by Sorrel, 20 November 2026. Independent mathematical
reconstruction pending. The arbitrary-agent question remains unresolved.**

The [one-extra-good theorem](SINGLE_EXTRA.md) leaves open how its local bridge
behaves when the agents already hold other goods. Keeping those goods changes
the EF1 inequalities. This note proves a sum-based bridge for a specific pair
of greedy witnesses: the shared-favorite braid used in the complete-round
argument of [Frank and Suksompong, Theorem 3.3](https://arxiv.org/html/2609.15358v1).
There are three agents and `3q+1` goods, q>=1. The final recipient D is distinct
from the two agents i,j who initially want the same good g.

The bridge connects specially chosen braid endpoints in at most three EF1
exchanges. A second induction below connects arbitrary endpoints to those
representatives. Together they give the candidate theorem: for three agents
and 3q+1 goods, every pair of recursively balanced outcomes with the same
size vector has an EF1 exchange path, for all q>=1 and all nonnegative real
additive utilities with arbitrary ties. No claim of literature priority is made.

## Two matched greedy runs

Start one run with i:g, and the other with j:g. In round t, let D choose the
same good k_t from their common remaining pool. Then j chooses y_t in the
first run and i chooses x_t in the second. If x_t=y_t, close the braid and
finish the runs identically; the resulting allocations differ only by an
exchange involving g.

Otherwise, begin the next round with i:x_t in the first run and j:y_t in the
second. These picks are valid by deletion of alternatives. Their pools again
coincide before D acts. Continue through q full rounds. If no equality occurs,
the final good is x_q in the first run and y_q in the second; give it to D.
Define

* I = {x_1,...,x_(q-1)}, J = {y_1,...,y_(q-1)};
* P = {k_1,...,k_(q-1)}, z=k_q, x=x_q, y=y_q.

The endpoints are

| | D | i | j |
| --- | --- | --- | --- |
| A | P + z + x | I + g | J + y |
| B | P + z + y | I + x | J + g |

Here a plus means disjoint union of goods. The bundles have sizes
(q+1,q,q). Both endpoints are greedy and hence EF1, with no tie rule needed.

## The bounds supplied by the braid

Write v(S) for one agent's additive value of S, and
`F_v(S) = v(S) - max_{s in S} v(s)`, with F(empty)=0. This is exactly the
value left after the best EF1 deletion.

The following bounds hold for the corresponding observer:

1. i values I at least J, and j values J at least I. At stage t each of x_t
   and y_t was available to both agents when they made their respective
   maximizing last picks from the same pool.
2. D values P at least I and at least J. At stage t, D picked k_t before
   either last pick x_t or y_t; sum this for t<q.
3. i values I at least F_i(P+x), and j values J at least F_j(P+y). For q=1
   both sides are zero. For q>=2, delete k_1. Match x_t to k_(t+1) for
   t=1,...,q-2: x_t was chosen while the later k_(t+1) was available. Match
   x_(q-1) to x_q. For j use the corresponding y goods. These are distinct
   matched goods, so additivity proves the bounds; the best deletion is no
   worse than deleting k_1.
4. Both i and j value g at least x and y, since g was their initial favorite.

All inequalities allow equality. None compares one agent's value with another
agent's value.

## Bridge lemma

The following proof needs only the displayed endpoint form, endpoint EF1,
and the four bounds above. It therefore applies to arbitrary nonnegative
real utilities, not just the numerical example or a finite sample.

First try C, obtained from A by exchanging g,y between i,j:

`C = (P+z+x, I+y, J+g)`.

If C is EF1, exchange x,y to reach B. Next try E, obtained from A by
exchanging x,y between D,j:

`E = (P+z+y, I+g, J+x)`.

If E is EF1, exchange g,x to reach B. Suppose both trials fail.

Only i's comparison with D can fail at C. Agent j replaces y by a weakly
better g. For i's comparison with j, delete g and use v_i(I)>=v_i(J).
For D's comparison with either carrier, delete the carrier's extra good and
use v_D(P)>=v_D(I),v_D(J). Likewise, only j's comparison with D can fail at E.
Consequently

`v_i(I)+v_i(y) < F_i(P+z+x)`, and
`v_j(J)+v_j(x) < F_j(P+z+y)`.

For any nonempty S and a distinct good t,

`F_v(S+t) = F_v(S) + min(v(t), max_{s in S} v(s))`.

Since v_i(I)>=F_i(P+x), the first failure implies v_i(z)>v_i(y).
It then follows that

`F_i(P+x+y) <= F_i(P+x)+v_i(y) <= v_i(I)+v_i(z)`.

Similarly, the second failure gives v_j(z)>v_j(x) and
`F_j(P+x+y) <= v_j(J)+v_j(z)`.

Now use three exchanges:

`A -> (P+x+y, I+g, J+z) -> (P+x+y, I+z, J+g) -> B`.

The carrier holding z satisfies its comparison with D by the inequality just
proved. The carrier holding g also satisfies it, because g is at least x,y
and the same bound with g in place of z holds. Between i,j, delete the extra
good and use their I/J dominance. For D, delete the extra good from either
carrier and use P's dominance. Thus both middle states are EF1. Every step
exchanges exactly two goods and leaves the fixed size vector unchanged.

The pivot is the **last** common D pick z=k_q. Earlier D goods do not in
general satisfy the required P-dominance bounds.

## From the bridge to arbitrary three-agent endpoints

### Removing a complete first round is safe

Fix a greedy first-round allocation, one good p_i per agent. Every p_i was
chosen while every good left after that round was still available, so each
agent values p_i at least as much as every remaining good. Suppose R is any
EF1 allocation of the remaining goods. For observers i,j, let h be a good
whose deletion from R_j witnesses EF1 (if R_j is empty, there is nothing to
prove). Then

`u_i(p_i)+u_i(R_i) >= u_i(h)+u_i(R_j minus h) = u_i(R_j)`.

Thus the full allocation is EF1 after deleting p_j from j's full bundle.
Consequently **every** EF1 path on the remaining goods lifts with this first
round fixed. This is stronger than lifting only greedy intermediate outcomes.

### Outer induction on q; inner induction on a first-round prefix

For q=1 use the [one-extra-good theorem](SINGLE_EXTRA.md), which covers three
agents in particular. For q>=2, fix any valid greedy prefix within the first
complete round. We prove, backwards in the number of remaining first-round
picks, that any two full greedy outcomes extending that exact prefix connect
while keeping the prefix goods with their owners.

When all three first-round picks are fixed, remove that round. The remaining
endpoints are recursively balanced outcomes on 3(q-1)+1 goods. Apply the
outer induction and the safe lifting result above. This is the base of the
inner induction.

Otherwise partition continuations by their next pick i:g. Within one such
class, the inner induction applies to the prefix extended by that pick. Join
the classes as follows, always using maximizers of the common remaining pool:

* Different next agents and different favorite goods have a common outcome:
  execute the two picks in either order, then finish identically.
* Different next agents with the same favorite g use matched braid runs
  beginning after the fixed prefix. Finish the first partial round by placing
  its other remaining agents between the two carriers. In each later complete
  round, place the first carrier first, the other last, and D between them
  when D is not a carrier. Early equality closes with one exchange.
* If D is one of the carriers and the braid reaches the final good, D absorbs
  its unmatched good. The two final allocations differ only by exchanging g
  with the other carrier's unmatched good. Both are greedy, hence EF1.
* If D is not a carrier, the two carriers are exactly the other two agents.
  There are only two possible prefixes at this point: empty, or D's first
  pick alone. With empty prefix, use the bridge proved above. With D already
  fixed, use its fixed first good as k_1; the later common D picks are
  k_2,...,k_q. All bridge bounds still hold. In particular D chose k_1 before
  either x_1 or y_1, and x_t was chosen while k_(t+1) was available. The
  pivot k_q lies in a later round since q>=2, so the bridge leaves the fixed
  first good k_1 untouched. There are no additional fixed singleton observers
  in this case. This exhausts non-carrier-D cases specifically because there
  are only three agents.
* For two tied next goods of the same agent, if another first-round agent is
  available, connect through any of that other agent's next-pick classes.
  Otherwise this is the last pick of the first round. Let that agent take g
  now and h first in the next round in one run, and h now then g first in the
  next round in the other. Both are maximizing picks; after them allocations
  and remaining pools agree. A complete next round exists because q>=2.

Thus all next-pick classes connect through common outcomes or an EF1 bridge,
and the inner induction closes. Applied to the empty prefix, it completes the
outer induction. This proves the stated three-agent 3q+1 claim.

The constructor `path(u, start_witness, target_witness)` implements these two
inductions. Inputs are complete maximizing-pick witnesses with extra recipient
0; relabel agents to handle either other recipient. It checks both inputs,
returns all allocations, and verifies every EF1 inequality and every exchange.
It is recursive, with no shortest-path or polynomial runtime guarantee. The
mathematical claim covers arbitrary real utilities; the executable represents
exact integers and rational numbers only.

## A seven-good example, including a failed earlier pivot

Number agents D=0,i=1,j=2 and goods g,k_1,y_1,x_1,z,y,x as 0,...,6.

| Observer | g | k_1 | y_1 | x_1 | z | y | x |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| D | 0 | 100 | 90 | 90 | 10 | 1 | 1 |
| i | 100 | 90 | 20 | 61 | 60 | 30 | 50 |
| j | 100 | 90 | 61 | 20 | 60 | 50 | 30 |

Both two-exchange trials fail. At C, i has value 91 while the best deletion
from D leaves value 110. At E, j has the same 91<110 failure. The three-step
bridge uses z, the last common pick, and passes every inequality.

Borrowing k_1 instead would first create D={z,x,y}, i={g,x_1}, j={y_1,k_1}.
D's own value is only 12, while deleting its most-valued good from j's bundle
still leaves 90. This is an exact failure of the earlier-pivot extension,
not a disconnected EF1 graph. `tail_bridge` refuses that pivot because its
claimed sum bounds are false.

Run from the repository root with Python 3.10+ and the standard library:

```sh
python3 projects/fair-round-swaps/two_rounds.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_two_rounds.py
```

Recorded output:

```text
three agents, seven goods: two complete greedy rounds and one final pick
left picks: 1:0 0:1 2:2 1:3 0:4 2:5 0:6
right picks: 2:0 0:1 1:3 2:2 0:4 1:6 0:5
0: 1021020
1: 1021200
2: 2021100
3: 2021001
Verified: 3 exchanges, all states EF1
Scope: candidate three-agent 3q+1 theorem; general agent count remains open
```

The tests check 1,500 exact rational braid examples through five full rounds,
including early closure, ties and both bridge lengths. They also check every
pair of outcomes for 24 seven-good profiles and 300 sampled pairs through six
full rounds, including all-zero ties. Their independent fairness predicate
tries every deletion directly. Finite checks support the construction; the
proof above supplies the arbitrary-length argument. Independent reconstruction
remains required before accepting this candidate theorem.

## What remains

The theorem covers three agents with remainder one; the separate near-complete
result covers remainder two. Neither this candidate nor those other results
resolve the arbitrary-agent problem. In particular, this inner induction uses
that if D is absent from a first-round suffix containing two different next
agents, the fixed prefix consists only of D. With four or more agents, extra
fixed observers need a further lifting argument; with several final recipients,
the braid can also leave more unmatched final goods.

The new path theorem and its dependence on the one-extra base need independent
mathematical reconstruction. A passing test suite, the isolated-state family,
or the failed earlier pivot cannot substitute for that review or close the
full second milestone.
