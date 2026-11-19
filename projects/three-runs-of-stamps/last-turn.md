# When the last mountain is the first inward turn

For a strip with $a$ initial mountain creases, take the unique mountain
stack whose first inward step is its last one. Let the first adjacent valley
after valley one occur at step $r$. For $a>r\ge5$ there are three stopped
prefixes. Their numbers of labeled completions with $r$ final mountains are

```text
direct entry into the old stack       2r
entry on the fourth valley            2r
stay outside until the valley stop    3r - 2
```

At $a=r\ge5$ only the last two prefixes survive, with the same weights.
Thus the last-turn contribution is $7r-2$ in the interior stop and
$5r-2$ in the terminal stop. This establishes one row of the
[weighted decomposition](escape-chain.md). Independent review and the
general cubic remain open.

## Read the gaps by walking across matched arcs

Use the fixed face orientation of the [layer model](first-family.md).
Write q_i for face a-i, x_j for valley a+j, and z_k for mountain a+r+k.
Here x_0=q_0. Reflect the drawing, if needed, to put q_1 on the left.
Before any valley the complete stack is

```text
q_1 q_0   q_3 q_5 q_7 ... [q_a] ... q_6 q_4 q_2
```

The odd indices from 3 increase and the even indices from 2 decrease.
The largest index occurs once. This follows by placing each mountain
outward except the last, which goes next to q_1.

At an endpoint, walk along the stack in the new crease's direction, using
only the matching on its half-plane. The immediate gap is always legal.
Upon encountering the near end of an arc, jump to its partner. The gap
just beyond that partner is legal. An unmatched face zero is a singleton
one can step across. On encountering an end whose partner lies *behind*
the walker, stop before it. Stop also at the exterior. This lists all legal
gaps. Entering a jumped arc or leaving the enclosing arc changes the
inside/outside test. Every other arc within a jumped arc has both ends
there, by noncrossing. A same-side partner of label i is i+1 if i has the
new crease's parity and i-1 otherwise. A missing partner of zero is the
singleton just described.

The tables give the directional walk as pairs followed by its stopping
face, or * for the exterior. For example, `x2>x1 q3>q2 | x3` means that
the first two gaps after adjacency are (x1,q3) and (q2,x3). These tables
specify actual inverses as well as counts. At any step the order on the
smaller labels shows which gap the new label occupied.

## Classifying the valleys

The first step sees `q3>q4 | q2`. Choosing the gap after the jump gives
**direct**. Its subsequent open steps j see
`q_(j+2)>q_(j+3) | q_(j+1)`. To stay open, jump and insert x_j in
(q_(j+3),q_(j+1)). Indeed x_(j-1) is between q_j and q_(j+2), and the
other wing still has q_(j+3) next to q_(j+1). Older valley insertions
occupy gaps with smaller indices. This proves the repeating walk by
induction and the displayed mountain order gives the first step. When
j=a-2 the jump reduces to the singleton q_a and the next step sees only
the barrier q_a. Thus direct survives through the adjacent stop if
a>=r+1, including a=r+1 where the last open jump was the singleton. For
a=r the compulsory adjacency is one valley too early.

If x_1 takes the immediate gap, it lies between q_0 and q_3. The second
and third valleys see `q0>q1 | *` and `q1>q2 | *`. Staying open places
them at opposite exterior gaps. At step four the walk is
`q2>q3 x1>x2 | *`. The first jump gives **return**, in (q_3,x_1).
From step five the return walk is `q_(j-2)>q_(j-1) | q_(j-3)`.
Here the two mountain wings are the same as for direct, four indices
earlier. At j=5 the adjacent x_4 is on the q_3 wing pointing back to q_3.
After each jump the insertion lies between q_(j-1) and q_(j-3), giving
the next step with opposite wing and parity. There is sufficient depth
through j=r-1. The second jump at step four instead gives **outer**.
Thereafter the walk is `x_(j-3)>x_(j-2) | *` on alternating wings. The
last exterior face and the previous wing's exterior face are partners,
so the only jump continues outward. These are all open prefixes.
In each choose adjacency at r.

## Direct and returning mountain suffixes

At the first mountain keep the adjacent branch (**near**) as well as every
jump (**far**). Adjacency closes a history only from mountain step two.
Once closed, all remaining mountains are forced by the same-symbol
trapping argument in [the deep-turn proof](deep-turn.md). Consequently
each open order through one or more mountains corresponds to exactly one
full completion. Close at the next mountain if any remain.

Here is the walk for direct. The letters in a pair are faces, not arc
numbers. In the two regular rows put j=r-k.

| State | Step k | Jumps in order | Barrier |
|---|---|---|---|
| Both starts | 1 | q_(r+2) > q_(r+1) | x_(r-2) |
| Near | 2 through r | x_(j+2) > x_(j+1) | q_(j+2) |
| Far | 2 through r-2 | q_(j+3) > q_(j+2) | x_(j-1) |
| Far | r-1 | q_4 > q_3 | q_0 |
| Far | r | q_3 > q_2 | * |

At a=r+1 the first jump is the singleton q_(r+1). The initial adjacent
gap is the one between x_r and the first face encountered. The table then
gives exactly one continuing jump on each path at each later step,
hence 2r completions. To check the regular rows directly, the near path
has the previous face in (q_(j+3),x_(j+2)) after its first jump, and
points toward x_(j+2). Past its paired x_(j+1), the next older face is
q_(j+2). At k=2 the first face ahead is the stopped x_r, paired with
x_(r-1). The far path has the previous face between q_(j+3) and x_j
and points toward q_(j+3). Its partner q_(j+2) neighbors x_(j-1).
Each jump moves the two indices down one, changing wings. Earlier
mountains lie in previously crossed outer gaps. At the last two steps
the original tail is q_1,q_0,q_3 and the opposite exterior is just past
q_2. This gives the two special rows without assuming the two paths agree.

For return, the same indexing argument shifts the q indices four earlier,
until it reaches q_0. The valley faces x_1,x_2,x_3 now sit beside q_0
and outside the two wings. Following the actual matches there gives

| State | Step k | Jumps in order | Barrier |
|---|---|---|---|
| Both starts | 1 | q_(r-2) > q_(r-3) | x_(r-2) |
| Near | 2 through r-4 | x_(j+2) > x_(j+1) | q_(j-2) |
| Far | 2 through r-2 | q_(j-1) > q_(j-2) | x_(j-1) |
| Far | r-1 | none | q_0 |
| Near | r-3 | x_5 > x_4, x_1 > q_0 | q_1 |
| After both jumps | r-2 | none | q_0 |
| After the first jump | r-2 | x_4 > x_3 | * |
| Continuing outward | r-1 | x_3 > x_2 | * |
| Continuing outward | r | x_2 > x_1, z_(r-3) > z_(r-2) | * |

At the near fork the old labels q_1,q_0,x_1,x_4,q_3 occur in that
order. The walker jumps from x_5 to x_4 and then from x_1 to q_0. The gap after both jumps lies inside the short
q_1--q_0 arc. From the gap after just one jump the opposite exterior
is available. Two outward insertions place z_(r-2) and z_(r-1) on opposite
ends. The final walk reaches x_1 and then these newer outer layers as
listed. The far path has r-2 open orders in total. The near path has one
at each step through r-4, then 2, 1, 1 and 2. The sum is 2r, including
r=5 where the regular near continuation range is empty.

## The outer suffix

After the adjacent valley stop the exterior valleys alternate around the
original stack, with x_r just inside x_(r-1). The initial adjacent
mountain enters between x_r and x_(r-3). Call this path **outside**.
Every jumping first mountain instead starts a **descent**. At its local
step i put h=r-i-1. Walking toward the center on a descent gives

| Local step i | Jumps in order | Barrier |
|---|---|---|
| 1 through r-5 | x_(h-1) > x_(h-2) | x_h |
| r-4 | x_2 > x_1, q_3 > q_2 | x_3 |
| r-3, after first jump | x_1 > q_0 | q_1 |
| r-3, after both jumps | q_2 > q_1 | x_2 |
| r-2, first branch | none | q_0 |
| r-2, second branch | q_1 > q_0 | x_1 |
| r-1, surviving branch | none | q_0 |

The regular jump lands between x_(h-2) and x_h. These are consecutive
same-wing valleys. On the next step x_(h-2) is first in the walking
direction and its opposite-wing partner neighbors x_(h-1). This is the
induction down the outer valley spiral. At its foot the entire interval
between q_3 and q_2 can be jumped because they are partners. The only
remaining boundary faces on the x_2 wing are x_2,q_1,q_0,x_1,q_3.
This gives the two terminal branches in the table. Together the open
orders of the early descent count (r-5)+2+2+1=r. At r=5 its initial
walking row is already the two-jump row.

The outside branch sees `x_r>x_(r-1) | *` at step two,
`x_(r-1)>x_(r-2) | *` at three, and
`x_(r-2)>x_(r-3) z_1>z_2 | *` at four. These follow by placing z_1
beside x_r, then z_2 and z_3 beyond opposite ends. At four, staying
exterior and thereafter jumping z_(k-3)--z_(k-2) produces one open order
at every step through r. Alternatively the first jump at four enters
(x_(r-3),z_1). Its next walking direction encounters x_(r-3), exactly
the entrance to the descent above. The four earlier mountain arcs are
outside the remaining gaps or surround them, and the subsequent descent
moves inward. Thus it uses the same old-face walks with local i=k-4.
Only its fork is reached at k=r. This delayed branch counts
1+(r-5)+2=r-2 open orders. Altogether the outer prefix has
r+r+(r-2)=3r-2 completions.

To invert any construction, remove the largest labels in order. The first
and fourth valley gaps distinguish the prefixes. The first mountain's gap,
all later nonadjacent jumps and the first adjacent step after it recover the
open order and its forced closing tail. Distinct walks count distinct
labeled stacks, including walks with equal weights.

## Check from a clone

```sh
python3 projects/three-runs-of-stamps/last_turn.py 12 9 --verify
```

Recorded output:

```text
outer: 25 labeled completions
return: 18 labeled completions
direct: 18 labeled completions
All constructed sets agree with the independent matching checker.
```

Tests also reconstruct the entire prefix set by unpruned single-valley
extensions. They compare every labeled final order in the three families
for r=5 through 15 and a in {r,r+1,r+2,r+5}. At a=7 the short stops
r=2,3,4 yield respectively {3,4}, {5,6}, {8,8}. Ending at r=4 takes
the adjacent fourth valley before the outer/return fork. The displayed
three-family theorem begins at r=5.
