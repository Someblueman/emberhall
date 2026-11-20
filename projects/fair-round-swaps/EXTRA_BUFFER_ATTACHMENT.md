# A better greedy division can require a temporary loss

Fern, 20 November 2026. **Candidate theorem; independent reconstruction pending.**

There are positive, strict preferences and two actual greedy picking outcomes
such that **everyone weakly prefers the target**, but every exchange path to
it temporarily makes someone worse off. The example extends to arbitrarily
many automatically fair pairs. An explicit EF1 path attains the exact minimum
loss, both in absolute units and as a fraction of starting utility.

This rules out a Pareto-monotone strengthening of the project's desired
connectivity theorem. It does **not** refute connectivity: the endpoints have
an explicit fair path. The [frozen model](proof.md) is unchanged. No literature
priority is claimed.

## The phenomenon already occurs with two agents

Give A values (11,10,9,1) and B values (21,10,9,1). Initially A owns goods
{0,3}, and B owns {1,2}. The target exchanges their entire bundles.

Both are recursively balanced greedy outcomes: use A,B | B,A for the source
and B,A | A,B for the target. Values rise from (12,19) to (19,22). But the
four possible first exchanges lower one recipient's utility by 1,2,9 or 8.
Thus no value-preserving exchange path exists, even through unfair states.

Exchanging goods 0,1 and then 2,3 is an EF1 path, with values
(12,19) -> (11,30) -> (19,22). Its largest temporary loss is exactly one.
The construction below also allows an incomplete final round, positive strict
buffer rows and arbitrarily many agents.

## A uniform family

For every r>=2, let A=0 and B=1 be two exceptional double recipients. There
are r-2 automatic double recipients, numbered 2,...,r-1, and singleton
recipients I=r and J=r+1. There are m=2r+2 goods. Choose an integer L>m.

The first six goods are g,h,a,b,c,d, numbered 0,...,5. A and B have these
base values, and base zero on every additional good:

| Observer | g | h | a | b | c | d |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 0 | 0 | 3 | 2 | 2 | 0 |
| B | 0 | 0 | 5 | 2 | 2 | 0 |

Multiply a base value by L and add its one-based good index. Interchange
the offsets of b,c in these two rows, so their values for b and c are
2L+5 and 2L+4 respectively. Thus the rows are positive and strict.

Both carriers value g at 30L+1, h at 20L+2, and every other good at its
one-based index. They share the unique global favorite g.

Automatic recipient i owns goods 2i+2 and 2i+3. Give its first good value
2m, its second value 2m-1, and d value 2m-2. Assign the remaining goods
the distinct values m+1,...,2m-3 in increasing good order. Every row is
positive and strict. The sum of its two smallest values exceeds its largest
value, so this recipient is EF1 under **every** allocation of the fixed sizes,
including allocations that put g in a pair.

The endpoints are

| | A | B | I | J | Each automatic recipient |
| --- | --- | --- | --- | --- | --- |
| Source | a,d | b,c | g | h | Its own two goods |
| Target | b,c | a,d | g | h | The same two goods |

A's utility rises from 3L+9 to 4L+9; B's rises from 4L+9 to 5L+9.
Everyone else keeps exactly the same goods. This is an all-recipient Pareto
improvement, not a target that asks the buffer recipient to accept a loss.

### Both endpoints are actual greedy outcomes

Write C,D,... for automatic recipients in increasing index order. Their
first and second goods are denoted C0,C1, D0,D1,... .

```
source: A:a, I:g, J:h, B:b, C:C0, D:D0,... | B:c, C:C1, D:D1,..., A:d
target: B:a, I:g, J:h, A:b, C:C0, D:D0,... | A:c, C:C1, D:D1,..., B:d
```

Every first-round agent appears once; the final round gives exactly one
additional good to each double recipient. A and B take their best remaining
core goods. The automatic recipients choose their unique best, then their
unique second-best goods. All these tails are removed before the last pick
of d, so a larger-index low good cannot defeat that pick. Each carrier
maximizes when it picks. `witnesses` produces the full sequences for any r,
and the checker validates every pick, including strict offset comparisons.

## The exact unavoidable loss

For an allocation x, let

```
d(x) = max over all recipients i of max(0, initial_i - u_i(x_i)).
```

A path's cost is its largest d(x). This uses the stated utility units.
Define delta=L+4-m, which is positive since L>m.

**Theorem.** The least possible cost of any exchange path from source to
target is exactly delta, even when unfair intermediate allocations are allowed.
An EF1 path attains it. Goods may move freely; protecting g is not assumed.

**Lower bound.** Look at the first exchange that changes an owner among the
five goods g,h,a,b,c. Before it, I has g, J has h, A has a plus one low good,
and B has b,c. A low good means d or an additional good; its value to A or
B is at most m. Earlier trades among low goods are unrestricted.

Every possible first change falls into one of the following cases:

| Change | Recipient forced to lose | Lower bound on that loss |
| --- | --- | ---: |
| g leaves I | I | 10L-1 |
| h leaves J without receiving g | J | 20L+2-m |
| B gives b or c and receives a low good | B | 2L+4-m |
| A gives a and receives a low good | A | 3L+9-2m |
| A gives a and receives b or c | A | L+4-m |

A swap of g,h is covered by the first row. A swap between two B-owned goods
is not an exchange. The remaining possibilities involving a carrier have
already been covered. In the last row A ends with a value at most 2L+5+m;
in the third row B has value at most 2L+5+m. These explain the only bounds
that depend on possible prior preparations. All five bounds are at least
delta, for every L>m. Any path to the target must make a first change of
these owners, so its cost is at least delta. This argument does not use EF1.

**Matching upper bound.** If r=2, exchange a,b and then c,d. A's middle value
is 2L+11, a loss of L-2=delta. B improves immediately. Both states are fair.

If r>=3, take t to be the largest-index good, m-1. It is the second good
of the last automatic recipient C. Use these four exchanges:

```
A:d <-> C:t
A:a <-> B:b
A:t <-> B:c
B:t <-> C:d
```

A's successive values are

```
3L+9 -> 3L+3+m -> 2L+5+m -> 4L+9 -> 4L+9.
```

Its only loss below the source is delta. B never falls below its starting
value. C loses exactly one unit while it holds d in place of t, then gets
its original good back. Every other recipient is unchanged. Since delta>=5,
this path's cost is exactly delta.

For EF1, the only intermediate pair with two large goods from A's viewpoint
is B's {a,c} after the second exchange. Its smaller A-value is 2L+4, below
A's current 2L+5+m. Before that, A owns its maximum a; afterwards its two
core goods pay every remaining comparison. B keeps b,c initially and then
holds a; its comparisons are safe by the same direct bounds. Every automatic
pair has only low goods in A's and B's rows throughout. I and J retain their
favorites among the paired goods, and automatic recipients are always fair.
These are all the possible EF1 comparisons.

## The exact proportional loss, approaching one third

Replace d(x) by the largest fraction of initial utility lost by any recipient.
The exact optimum for this family is

```
gamma = (L+4-m)/(3L+9).
```

Divide the five lower bounds above by the respective initial values
30L+1, 20L+2, 4L+9, 3L+9, 3L+9. The smallest ratio is gamma when L>m>=6.
For example, comparing B's ratio with gamma leaves the positive numerator
`2L^2+(m+5)L`; comparing I's leaves `(30m-34)L+m-13`. The low-good A case
is larger by `2L+5-m` before division, and J loses over 19/20 of its value.

The same explicit path attains gamma. A loses exactly this fraction; the
only other loss is C's one unit out of 4m-1. The latter is smaller: gamma
increases with L, and already at L=m+1 it is `5/(3m+12)>1/(4m-1)`.
For fixed r and increasing L, gamma tends to one third. Thus greedy outcomes
that everyone weakly prefers can require almost one third of someone's
starting utility to be given up temporarily. This fraction is invariant
under independent positive rescaling of utility rows.

## Run and inspect

Python 3.10+ and the standard library suffice, from the repository root:

```sh
python3 -S projects/fair-round-swaps/extra_buffer_attachment.py
python3 -S projects/fair-round-swaps/extra_buffer_attachment.py --pairs 3 --audit
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_extra_buffer_attachment.py -v
```

The default r=4,L=100 example has A,B values (309,409) at the source and
(409,509) at the target; all other final holdings are unchanged. The four
fair exchanges attain absolute loss **94** and proportional loss **94/309**.
The complete eight-good audit has 5,040 unrestricted states and 900 fair
states. It independently finds absolute optimum 96 and proportional optimum
32/103. The source is alone in its zero-loss component, although the target
is fair, greedy, and better for both A and B.

Tests independently enumerate all fixed-size states on six and eight goods,
try every literal deletion for EF1, and check reachability both strictly
below and at the claimed absolute and proportional bounds. They permit g
to move to any agent. Other tests check actual maximizing picks, the bare
two-agent example, strict profiles through twenty doubles, small rational
perturbations, invalid domains and the actual command. The all-size theorem
rests on the five-case argument and explicit paths, not sampled graphs.

The earlier c8fcfe9 contribution retained two weaker constructions. This
continuation replaces them in place with the single stronger family. Their
frozen source remains available in that commit. Independent mathematical
acceptance, source integration and the general connectivity milestone are
separate outstanding matters.
