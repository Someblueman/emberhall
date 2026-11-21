# Any number of agents, with one final recipient

Fern, 20 November 2026. **Candidate theorem with an exact constructor;
independent mathematical reconstruction pending.** This addresses one
remainder class for arbitrary agent counts, not the whole project question.

**Theorem.** For every n>=2 and q>=1, any two greedy recursively balanced
allocations of nq+1 goods, with the same final recipient D, are connected
by single exchanges through EF1 allocations of the same labeled size vector.
Utilities may be any nonnegative additive real values, with arbitrary ties.
Intermediate allocations need not be greedy outcomes.

The [frozen model](proof.md) is unchanged. Dependencies are the established
arbitrary-n one-extra theorem in [SINGLE_EXTRA.md](SINGLE_EXTRA.md), and the
new [safe-spare normalization](SAFE_SPARE.md) in this contribution. The
round/prefix construction follows Mica's five-agent proof at `2a58b53`;
the new ingredient replaces its full-fiber connectivity argument with a
connection between specified components. No priority claim is made.

## 1. Connect the relevant components while protecting a favorite

First work with n+1 goods. D has two goods and everyone else one. Two
singleton agents i,j have a shared favorite g. Consider two greedy endpoints
that hold g at i or j. We will keep g with one of these two agents throughout.
For n=2 there cannot be two singleton carriers; this lemma is needed only
for n>=3.

Fix g with one carrier and remove that agent and g. The remaining instance
has n-1 agents, n goods and one double bundle. Removing a singleton from a
greedy witness preserves its greediness: earlier picks only lose an
alternative and later pools agree. Its final good in D is a safe spare,
since every remaining singleton picked while that good was available.

By the safe-spare theorem, every safe-spare state in this smaller instance
joins the component containing its greedy endpoints. Restore the removed
carrier and g after every step. That carrier is fair because g is its
favorite; everyone can delete that singleton's entire bundle. Thus each
reduced safe-spare component lifts to the fixed-g fiber.

It remains to cross between the two fibers. With g removed, let the n-3
other singleton agents pick greedily, in any fixed order, excluding D,i,j.
Exactly three goods remain. There is a good z that is in the top two of
these three for both i and j: two subsets of size two in a three-element
set intersect. Ties only enlarge the available choices. Give the other
two goods p,h to D and z to the carrier not holding g.

Every other singleton dominates both p,h because it chose while they
were available. The holder of z dominates at least one of p,h by the
top-two choice. Consequently, after removing the g holder, that allocation
has a safe spare. This holds whether z belongs to i or j; the safe spare
need not be the same good on the two sides. These states are EF1, and
exchanging g,z joins them.

Connect the first endpoint to its constructed crossing state inside its
safe-spare component, exchange g,z, then connect to the second endpoint.
This proves the **protected greedy-endpoint bridge for every n**.
The program also accepts non-greedy endpoints when their fixed-g reductions
have safe spares. It deliberately rejects other endpoints as unsupported.

It would be false to say that every fixed-g fiber is connected: the known
isolated one-extra states survive in such fibers for sufficiently many
agents. Likewise the [three-final side obstruction](FIVE_AGENT_THREE_FINAL.md)
still holds. No full-graph connectivity assumption is used here.

## 2. A padding lemma independent of the number of agents

Let C be k common complete greedy rounds with g omitted from their pool.
Let each agent retain its C bundle while an EF1 path acts on a disjoint
n+1-good tail. Assume g remains with i or j, each a tail singleton, and
for every observer a and either carrier b,

```
u_a(C_a) >= u_a(C_b).
```

Then every protected tail allocation lifts to a full EF1 allocation.
If the compared bundle holds g, delete g. It leaves exactly C_b, which
the observer can afford by the displayed inequality and nonnegativity.

For any other compared bundle, delete its first common-prefix good.
Match its common picks in rounds 2,...,k to the observer's picks in
rounds 1,...,k-1: each observer pick occurred earlier and dominates its
matched good. The observer's last common pick dominates every non-g tail
good, because those goods remained available throughout C. Use that pick
to pay for the largest good of the compared tail bundle, and use tail EF1
to pay for the rest. The sum proves the required deletion inequality.
With k=0 this is just tail EF1.

`padded_path` checks the actual greedy prefix, the disjoint tail and the
common-bundle dominance inequalities. It also checks every lifted state
with the general EF1 definition. Those checks implement the lemma; they
do not replace its proof or silently weaken the original endpoint question.

## 3. Round induction, and the role of fixed first picks

Induct on the number q of complete rounds. The q=1 base is the established
one-extra theorem. **That base is ambient:** its paths need not preserve a
specified first-pick prefix. We do not assume otherwise.

For q>=2, prove by backward induction on the number of unfixed first-round
picks that each class with a fixed actual greedy first-round prefix is
connected while retaining its allocated goods. A fixed complete first
round reduces to q-1 rounds. Restore it after applying the outer induction:
delete the compared agent's first-round good and use one's own first-round
good to pay for the largest residual tail good, with residual EF1 paying
for the remainder. All first-round goods dominate every remaining good.

Inside a shorter fixed prefix, partition witnesses by their next pick.
Classes with an identical next pick connect by the inner induction.
Different agents choosing different favorites commute: both picks can be
performed in either order and followed by a common greedy completion.
Different tied favorites for the same agent connect through another
eligible agent's first-pick class when one exists. If it is the last
eligible agent, let it take both tied goods consecutively, as the last pick
of the current round and the first of the next complete round. The two
orders yield the same allocation. The next complete round exists because
this inner argument is used only for q>=2.

Only different agents i,j sharing favorite g remain. Use the paired greedy
executions of the complete-round argument. Let i start one with g and j
the other. All other currently eligible agents pick identically from the
common pool, in a fixed order; let j finish one round with its favorite y
and i finish the other with its favorite x. If x=y, swap g,x and finish
identically. Otherwise start the next complete round with i:x in the
first execution and j:y in the second. These picks still maximize, since
x,y were chosen in a larger pool. Repeat with the remaining agents in a
common order, then the respective last carrier. Each repetition consumes
a complete round.

If equality eventually closes the discrepancy, the executions differ by
one exchange. If the discrepancy reaches the single final pick and D is
one of i,j, assigning that last good again makes the allocations differ
by one exchange. This is the usual two-carrier cancellation.

## 4. The unresolved-carrier case becomes the protected bridge

Suppose neither carrier is D when the final pick is reached. All assigned
goods agree between the two executions except g and the two last carrier
choices x,y. Form a tail from g, x,y and the last-round common good of
each of the n-2 noncarriers. It has n+1 goods and one double recipient D.

Each endpoint restricted to this tail has a greedy one-extra witness:
choose g first, then the common noncarrier goods in their original order,
then the other carrier's chosen x or y, and finally D's remaining good.
The common picks maximize on that restricted pool because it is a subset
of the pool in which they were chosen. Both i and j value g at least every
tail good, since it was their shared favorite while all those goods were
available. Section 1 therefore supplies a protected tail path.

The goods outside this tail form q-1 complete common rounds with g omitted.
To see this, place each round's common noncarrier choices first, preserving
their relative order, then that round's paired i and j goods. The latter
were both maximizers in the same common pool, so either order is greedy.
Deleting g and moving these paired choices before the next round leaves
exactly the pool that the next common noncarrier choices originally saw.
This proves by successive rounds that the reordered prefix is greedy.
Already fixed picks preceding the discrepancy remain allocated to the same
agents; no tail good belongs to that fixed first-round prefix when q>=2.

Every noncarrier's common pick precedes both carrier picks in its round,
so it dominates either carrier's good for that observer. Each carrier's
own common pick also dominates the other's, since they maximize on the
same pool. Summing over the q-1 common rounds gives exactly the dominance
condition in Section 2. The protected tail path thus lifts while retaining
the initially fixed prefix's allocation. This joins the last two first-pick
classes and completes both inductions.

All recursion terminates: fixing an equal first pick reduces the inner
number of unfixed picks; fixing a whole first round reduces q. The explicit
commutation, tie and paired-execution constructions connect their classes
through these smaller calls. No search over the full nq+1 allocation graph
is needed. No shortest-path or polynomial-time bound is claimed for the
complete recursive constructor.

## Run and inspect

Python 3.10+ and the standard library, from the repository root:

```sh
python3 projects/fair-round-swaps/arbitrary_one_final.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_arbitrary_one_final.py -v
```

The real command uses six agents, nineteen goods and a discrepancy that
does not cancel before the final pick. It returns three EF1 exchanges:

```
4012345012345012305
4012345012345512300
5012345012345412300
5012345012345012340
```

`path(utilities, start_witness, target_witness, final_agent=0)` supports any
labeled final recipient and validates both complete greedy witnesses.
Integer and exact rational utilities are supported in code; the theorem
allows arbitrary nonnegative real values. Recursion depth and output size
can limit large computations.

The tests independently check all deletions, all maximizing picks, sizes,
each two-owner exchange and retained first-round prefixes. They include
51 forced uncancelled braids through twelve agents and forty-nine goods,
126 rational or all-zero cases through eight agents, opposed carrier
rankings, a last-agent tie across a round boundary, missing padding
dominance, and a protected fiber outside the supported component. The
q=1 cases deliberately check the ambient contract rather than falsely
requiring their input prefixes to stay fixed.

**Remaining:** independent reconstruction of this argument and its safe-spare
dependency; source integration; and all other remainder classes beyond
their existing separately scoped results. The arbitrary-agent project
milestone is not complete merely because this one class has a constructor.
