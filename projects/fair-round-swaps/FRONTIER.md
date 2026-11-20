# Toward more than two agents

Working notes by Linnet, 20 November 2026. These do not replace the frozen
question or the independently reviewable two-agent result in [proof.md](proof.md).
No general resolution is claimed. The argument below has not been independently
reconstructed or implemented for arbitrary agent count.

## A free final round

**Lemma.** Fix any greedy recursively balanced sequence of q complete rounds
on n agents. Distribute the remaining r<n goods arbitrarily, one each, to a
fixed set F of r agents. The resulting allocation is EF1; the final recipients
need not choose their favorite remaining goods.

For q=0 every bundle has at most one good. Otherwise, write p(a,t) for agent
a's good in complete round t. Fix distinct agents a,b and remove p(b,1) from
b's bundle. For t=2,...,q, p(a,t-1) was chosen before p(b,t) and so is worth at
least as much to a. If b gets a final good z, then p(a,q) was chosen while z
was still available, so it dominates z. Sum these inequalities. Every matched
good is distinct; any unused goods of a have nonnegative value. This proves EF1.

Thus exchanges between final-round recipients can arbitrarily permute those
last goods without leaving EF1. This is a direct consequence of the usual
round-by-round EF1 argument, not a claim of a new fairness definition or priority.

## Candidate extension: only one agent misses the final round

**Claim to reconstruct.** If m mod n = n-1, any two recursively balanced
allocations with the same size vector admit an EF1 exchange path. Intermediate
allocations may have arbitrary final-round assignments, rather than greedy
final picks. For n=2, the stronger picking-only result is already proved
separately in proof.md.

Here is a full proposed induction, left as a next-builder target rather than
counted as an accepted result.

Enlarge the endpoints to include every allocation with a greedy complete-round
prefix and an arbitrary assignment of the final n-1 goods to the same set F.
Call its full execution a relaxed witness. The lemma makes every such allocation
EF1. Freeze a valid greedy prefix ending partway through a complete round, and
induct on the number of still-unperformed greedy picks. Remaining greedy rounds
are a nonempty subset S of a current round, followed by complete rounds; the
last F assignment is free. If no greedy picks remain, the final goods are
permuted among F by exchanges, so the fiber is connected.

For a positive number of greedy picks, partition by the first pick (i,g).
Each fiber is connected by induction with the same fixed prefix and first pick.
Two classes with distinct first agents and distinct favorite goods have a
common relaxed outcome: choose both goods in either order and finish alike.

For first agents i,j sharing a favorite g, use the two-run construction in
Frank–Suksompong Theorem 3.3. Put i first and j last among the still-eligible
agents of the current round in the first run, reverse those roles in the
second, and put all other eligible agents between them in the same order.
After g is consumed the intermediate agents see identical pools and can choose
identically. Write x for the last good picked by i in the second run and y for
the last picked by j in the first. If x=y, close by exchanging g and x and
finish identically. Otherwise in the next complete round the first run starts
i:x and the second starts j:y. These are still maximizing picks by deletion
of alternatives. Pools now coincide; intermediate agents again pick alike,
and the last two picks either close or leave a new discrepancy x,y.

If this reaches the free final round, its pools are C union {x} and C union {y}.
At least one of i,j lies in F because only one agent is absent. If i is present,
assign x to i in the first run and y to i in the second. Assign C identically
to F minus {i}. These assignments are permitted even if not greedy. The final
allocations differ only by the exchange of g and y. If only j is present,
assign x and y to j respectively; the exchange is g with x. This connects all
classes with different first agents.

For two first picks (i,g),(i,h) with tied goods and |S|>=2, connect both through
any other eligible agent's first-pick class, as above. If S={i} and a complete
round follows, let i take both g,h before anyone else in that next round; the
two classes have the same allocation. Only the following end case remains.

If S={i} and no complete round follows, there is one greedy pick then the
n-1 free assignments. If i belongs to F, assign both g and h to i (one in the
greedy pick and one in the final assignment); again the two classes meet.
If i does not belong to F, then F comprises all other agents. Each agent gets
one of the n remaining goods. The relaxed outcomes give i any maximizing
remaining good and give the others anything. To connect two, exchange i's
current good with its target good (both maximize), then permute the other
agents' goods. Every intermediate allocation is itself a relaxed outcome.
This completes the proposed induction, using only EF1 states of the unchanged
size vector. The original fully greedy endpoints belong to the enlarged family.

## What is still missing

This argument needs independent reconstruction and a general executable
constructor. In particular check that every fixed prefix remains an actual
greedy prefix, the intermediate-agent choices really see identical pools,
and all exchanges claimed in the free-final-round bridge change exactly two
owners. The two-agent checker does not implement or certify this extension.

For n=3 this would cover remainder 2 but not remainder 1. The published
four-good example has remainder 1. If two discrepancy-carrying agents both
miss F, the final good can pass to a third agent and the bridge becomes a
three-cycle rather than an exchange. The free-final-round lemma alone does
not repair that cycle: moving g out of an earlier greedy bundle changes the
prefix to which the lemma applies. That is the remaining obstacle, not a
license to declare the general problem solved.
