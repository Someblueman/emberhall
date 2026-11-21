# Reconstruction: exactly one agent misses the last round

Rook, 20 November 2026. Independent reconstruction of the candidate in
[FRONTIER.md](FRONTIER.md) and its [constructor](near_complete.py), as present
at source `70c1f6c`. This accepts that mathematical extension within the model
below. It does not resolve the other remainders, assert priority, or replace
independent source integration of this note.

## Statement and intermediate family

Let there be n >= 2 agents, m = qn + n - 1 labelled goods, and nonnegative
additive real utilities. Fix the n - 1 final recipients F. An execution has q
complete rounds, each using every agent once in any order, followed by one
pick per member of F. A greedy pick maximizes the agent's value among remaining
goods, with arbitrary ties. Any two greedy executions have allocations joined
by single exchanges through EF1 allocations with their original bundle sizes.

The proof actually connects a larger family: the complete rounds are greedy,
but the assignment of the remaining goods to F is arbitrary. These final picks
need not maximize anything. We call these executions relaxed. The endpoints
of the stated theorem are included in this family.

Every relaxed allocation is EF1. For agents a != b, remove b's first-round
good. Pair b's round-t good, for t = 2,...,q, with a's round-(t-1) good. Each
paired good of a was chosen while b's good was available and is at least as
valuable to a. If b is in F, pair its final good with a's round-q good.
Unused goods of a have nonnegative value. Summing proves the required
inequality. When q = 0 all bundles have size at most one, so EF1 is immediate.

## The induction is over fixed prefixes

Freeze any valid greedy prefix of the complete rounds. We prove connectivity
of the allocations of all relaxed continuations, retaining that prefix in
every witness. Induct on the number P of greedy picks still to make. A current
partial round has eligible set S, followed by zero or more full rounds and
the free assignment to F. Goods already in the prefix never move.

For P = 0, every member of F gets one remaining good. Any two assignments are
connected by transpositions between members of F. For P > 0, partition
continuations by their first pick (i,g). Each class is connected by induction,
because freezing that pick decreases P. It remains to connect these classes.

If i != j and their chosen goods g != h, both orders i:g,j:h and j:h,i:g are
legal. A maximizer stays a maximizer after another good is deleted. Finish the
two runs identically. Their allocations coincide, so these classes intersect.

## Shared-favorite bridge, with its allocation invariant

Suppose distinct i,j in S both start with g. Start one run with i:g and the
other with j:g. In the current round put S minus {i,j} next in identical order,
with identical tied choices; they see exactly the same remaining pool. Put j
last in the first run and i last in the second. From the common pool D, let
j choose y and i choose x, respectively.

If x = y, complete identically: only ownership of g and x differs. If x != y,
the first pool is C union {x} and the second C union {y}, where
C = D minus {x,y}. If another full round follows, start it with i:x in the
first run and j:y in the second. These picks are maximizing by deletion of
alternatives from D. The remaining pools are now both C, so all other agents
again pick identically, then j and i pick last. Repeat this procedure.

To check that these operations really end in **one exchange**, retain the
names x_0,y_0,...,x_t,y_t of the successive last choices. Just after the last
pair of picks, the varying parts of the two bundles are:

| Agent | First run | Second run |
| --- | --- | --- |
| i | g, x_0,...,x_(t-1) | x_0,...,x_t |
| j | y_0,...,y_t | g, y_0,...,y_(t-1) |

All other holdings agree, including the frozen prefix. If x_t = y_t, this
table differs only by exchanging g with that common good. All later picks can
be identical.

Otherwise, eventually only the free assignment to F remains. Its pools are
C union {x_t} and C union {y_t}. At least one of i,j is in F: its complement
has exactly one member. If i is in F, assign x_t to i in the first run and y_t
to i in the second, and assign C identically to F minus {i}. The table now
differs only by exchanging g and y_t. If i is absent, j is present: assign
x_t and y_t to j instead. The difference is the exchange of g and x_t.
There are exactly n-2 common goods for the n-2 other final recipients.

Thus every pair of distinct-agent first-pick classes is connected, even with
ties. Every step stays inside a class or crosses one of the single exchanges
above, and every witness keeps the original prefix greedy.

## Two tied choices by the same agent

Let the first picks be (i,g) and (i,h), with g != h tied as maximizers.

* If |S| >= 2, choose any other j in S and one of its maximizers. Both classes
  connect to that first-pick class by the distinct-agent argument.
* If S = {i} and a full round follows, put i first in that next round. The
  sequences i:g,i:h and i:h,i:g are legal and have the same allocation;
  complete them identically. They connect the two classes.
* If S = {i} and only the free final assignment follows, there are n goods
  left. If i is in F, give i both g and h, one as its greedy pick and one as
  its final good. Assign the other n-2 goods identically: again the classes
  share an allocation. If i is not in F, every agent gets one of the n goods.
  Exchange i's current good with its target good, which is also a maximizer,
  then permute the other goods among F. Every intervening witness remains
  relaxed and retains the prefix.

This exhausts the first-pick classes and completes the induction. Applying it
to the empty prefix proves the statement for all q, including zero.

## Constructor and independent checks

The code's `connect` implements the first-pick cases above; `bridge` implements
the displayed invariant. `permute` fixes recipients one at a time, so previously
fixed assignments stay fixed. Within a fixed prefix only suffix goods move.
Equal allocations can be discarded without changing an adjacent exchange.
Termination follows from decreasing P in the recursive same-pick calls;
the other recursive calls have the same first pick on each side. The detour
through a different agent is used only for a same-agent pair with |S| >= 2.
The bridge itself advances one complete round at a time.

[test_near_complete_reconstruction.py](test_near_complete_reconstruction.py)
generates fresh endpoints without the production witness helpers. It checks
each returned witness by partitioning it into rounds, each EF1 inequality by
trying all removals, and each exchange by explicit changed owners. Its exact
rational profiles include zeros and ties, every absent agent, zero through
three full rounds, and two through five agents. A changed unfair allocation
and a non-greedy prefix are rejected by these independent checks.

Run from the repository root:

```sh
python3 -m unittest discover -s projects/fair-round-swaps -p 'test_near_complete_reconstruction.py'
```

Recorded on 20 November 2026: two tests passed, checking 224 paths and
4,577 exchanges; 553 visited witnesses had non-greedy final picks.

The finite checks audit the executable construction; the induction above
supplies the universal claim. The broader problem remains open here: when two
discrepancy-carrying agents both miss the final round, the last bridge step has
no carrier in F. No claim about that case follows from this reconstruction.
