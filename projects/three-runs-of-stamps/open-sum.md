# The entire unclosed middle run

For equal run lengths $k\ge2$, consider all labeled $M^kV^kM^k$ stacks
in which none of valley steps 2 through $k$ enters the gap immediately
beside the preceding face. There are exactly

$$U(k,k)=(9k^2-19k+12)/2.$$

For example, at $k=13$ there are 24 eligible middle prefixes and 643
completed stacks. This proves the unclosed term of the
[three-run decomposition](escape-chain.md). Its stopped terms still have
to be counted separately.

## The two possible endings of a valley

Write $q_i=k-i$, $x_j=k+j$ and $z_s=2k+s$ for the initial mountain,
valley and final mountain faces. Thus $x_0=q_0$. A gap written as an
unordered pair consists of two neighbors at the moment of insertion.
An exterior gap always means the one in the required direction.
The position of the final valley face distinguishes the two prefix
families in the table. The initial mountain turn $t$ is the first mountain
that was inserted inward. Its stack is an exterior spiral through $t-1$,
followed by adjacent mountains. A dash means that all mountains stayed
exterior.

| Initial turn | Outside ending | Inside ending |
|---|---:|---:|
| None | $2k-2$ | $k$ if $k\ge3$ |
| $2\le t\le k$ | $3k-t-1$ | $k+2(k-t)+2$ if $t\ge4$ |

Each occupied cell for a given $k,t$ represents exactly **one prefix**.
The numbers are its completion weights.

Here are the constructions. For a finite turn put $d=k-t$. The inner
mountain spiral consists of the contiguous labels $q_0$ through
$q_{d+1}$, arranged on alternating wings in increasing distance from
$q_0$. Next to $q_d$ on its outer side is $q_{d+3}$ if that face exists,
otherwise $q_{d+2}$. On that side the remaining old block runs through
$q_{d+3},q_{d+5},\ldots$ and returns on the other parity to $q_{d+2}$.
This is the exterior stack through $t-1$ with its nested last $d+1$
mountains inserted beside $t-1$.

* Put $x_j$ in $(q_{j-1},q_{j+1})$ for $1\le j\le d$.
  The first gap is adjacent. At later steps, looking back through the
  fold crosses the matched pair $q_{j-2},q_{j-1}$ to reach the other wing.
  At $j=d+1$ use the gap $(q_d,q_{\min(k,d+3)})$ instead. For $d>0$
  the skipped arc is $q_{d-1},q_d$. For $d=0$ this is the adjacent
  first valley. Its neighbor is given by the end of the inner spiral above.
* For the **outside** prefix put all subsequent valleys at alternating
  exterior ends. The next two steps, when present, jump respectively
  $q_d,q_{d+1}$ and $q_{d+1},q_{d+2}$. At $j=d+4$ jump both
  $q_{d+2},q_{d+3}$ and $x_{d+1},x_{d+2}$. Subsequent steps jump the
  previous opposite-wing valley pair to the exterior.
* The **inside** path shares the first two exterior steps. At $j=d+4$
  jump just the first pair, placing $x_j$ between $q_{d+3}$ and $x_{d+1}$.
  For each later step put $x_j$ in $(q_{j-3},q_{j-1})$ by jumping
  $q_{j-2},q_{j-1}$. Earlier valleys occupy the old gaps with smaller
  indices. This path exists precisely when $t\ge4$.
* With **no** mountain turn, put all valleys outward for the outside
  prefix. For the inside prefix place the first two outward, then place
  $x_j$ in $(q_{j-3},q_{j-1})$ from $j=3$ onward. At step three the
  walk jumps $q_1,q_2$ and can stop in $(q_2,q_0)$ before jumping
  $q_0,x_1$ to the exterior. Each later jump crosses $q_{j-2},q_{j-1}$.

In these instructions an arc jump goes across both matched ends on the
new crease's half-plane. Direction alternates, and the gap immediately
after a complete jump has the same interval memberships as the starting
endpoint. This verifies legality and nonadjacency at every required step.
Distinct initial turns and the final inside/outside position distinguish
all the prefixes.

For exhaustiveness use the established two-block counts. Deleting the
last valley gives exactly one adjacent child for each shorter prefix.
Any nonadjacent child is open, since an earlier adjacent valley after
step one would force the entire remaining tail. Hence the open population
is the difference of the counts for $(k,k)$ and $(k,k-1)$. The two-block
edge cases give $(2k^2-3k+2)-(2k^2-5k+4)=2k-2$. The second count uses
reversal and exchange of the two crease kinds. The $k=2$ case can also be
enumerated directly. We have exhibited exactly that many prefixes,
including $k$ outside and $k-2$ inside. [Hull et al., section 3.1](https://arxiv.org/html/2503.23661v2#S3.SS1).

## Count open mountain histories

At the first mountain keep every legal gap. At later steps keep only the
nonadjacent choices. For each such open order of length $s$ between one
and $k$, append $k-s$ adjacent mountains to obtain a complete stack.
After the first of those mountains, the same-symbol trapping lemma forces
the remainder. The inverse deletes largest labels until the first adjacent
mountain after step one has been located, or keeps the whole order if
there was none. Thus it suffices to count the open orders, at *all* steps.

The directional walks below also establish exhaustiveness of these
histories. As in the [last-turn proof](last-turn.md), start beside the
current endpoint. Jump across a same-side matched pair to reach the gap
beyond the pair. An unmatched face zero can be stepped across. Stop if
the next face has its partner behind the walker, or if there is no next
face. This lists every legal gap, including the initial adjacent gap.
We write a directional walk as the ordered jumps, followed after a bar
by the blocking face or the exterior (*).

### Outside ending

The initial mountain must go outside. There is one wholly exterior
mountain path **E** through all $k$ steps. It admits two possible
departures. **S** leaves at step three, enters the valley spiral and
runs to the horizon. For a finite $t$, **C** leaves at step $t$ and
also reaches the horizon. If $t>3$, C shares the beginning of S.
If $t\le3$, C leaves E directly. Here and below use $h=k-s+1$.

| Path and step | Directional walk after adjacency |
|---|---|
| E, step 1 | no jump, exterior |
| E, step 2 | x_k > x_(k-1), then exterior. At t=2 insert singleton q_k before exterior |
| E, step 3 | x_(k-1) > x_(k-2), x_k > z_1, then exterior. At t=3 insert q_k > q_(k-1) between the jumps. At t=2 replace the first jump by q_k > q_(k-1) |
| E, later | z_(s-3) > z_(s-2), then exterior |
| S before the turn, or no turn | x_(h+1) > x_h, then barrier x_(h+2) |
| S at s=t>3 | x_(h+1) > x_h, q_(h+2) > q_(h+1), then barrier x_(h+2) |
| S after the turn | q_(h+2) > q_(h+1), then barrier x_(h+2) |
| C after its entry | x_(h+1) > x_h, then barrier q_(h+1) |

For verification, E first adds $z_1$ beyond $x_k$ and $z_2$ on the
opposite wing. At step three a gap remains between the last two same-wing
valleys, before jumping $x_k,z_1$ to the outside. For $t=2$ the last valley
was the first exterior escape, so the other wing still ends in the
singleton $q_k$ at step two. For $t=3$ the old pair $q_k,q_{k-1}$ is
between the two jumped pairs at three. These are the only adjustments
to E. After step three the exterior mountain arcs wrap all older faces.

The S jump before the turn gives $(x_h,x_{h+2})$, initially after the
first jump at step three. Each such gap is on alternating wings of the
exterior valley spiral. Decreasing $h$ by one encounters the partner
of the inner gap face, whose opposite-wing neighbor is $x_{h+2}$ at
that next step. At $s=t$ the inner label $h=d+1$ marks the earlier
valley bridge. Immediately beyond $x_h$ there is the old block
$q_{d+3}$ through $q_{d+2}$. Its ends are partners, so one may either
stop between $x_h,q_{d+3}$ (C) or jump it and stop between
$q_{d+2},x_{h+2}$ (S). At $t=2$ the block is the singleton $q_k$.
At $t=3$ this same choice occurs inside the step-three E walk.
The separated paths now descend the two interleaved wings: C lands in
$(x_h,q_{h+1})$ at each later step, S lands in $(q_{h+1},x_{h+2})$.
The preceding gap puts the stated near face next in the reversed
direction. Its partner neighbors the listed barrier because $x_j$
was inserted between $q_{j-1},q_{j+1}$. Earlier descending faces are
in gaps of larger index. This verifies the repeating rows by induction
all the way to $h=1$.

E contributes $k$. S contributes $k-2$ (zero at $k=2$), and C contributes
$k-t+1$ when the turn exists. This gives the outside column of the table.

### Inside ending

First suppose $t\ge4$. Follow the gaps $(x_h,q_{h-3})$ for $s<t-3$.
After the initial adjacent step, the walk jumps $x_{h+1},x_h$ and ends
at $q_{h-3}$. Indeed the previous insertion is beside $x_{h+1}$, while
on the opposite wing $x_h$ neighbors the old face in the gap used at
valley step $h$. Earlier mountains lie farther down those wings. At
$s=t-3$, $h=d+4$ and the return-valley gap produces the fork. The walks
at the fork and thereafter are

| State | Step | Directional walk after adjacency |
|---|---|---|
| Fork | t-3 | x_(d+5) > x_(d+4), x_(d+1) > x_d, then barrier q_(d+1). Omit the first jump when t=4 |
| Cross both pairs, short descent | t-2 through k-3 | x_(h-3) > x_(h-4), then barrier q_(h-3) |
| Short descent | k-2 | no jump, barrier q_0 |
| Stop between the fork pairs | t-2 | x_(d+4) > x_(d+3), then exterior |
| Continue outward | t-1 | x_(d+3) > x_(d+2), then exterior |
| Continue outward | t | x_(d+2) > x_(d+1), z_(t-3) > z_(t-2), then exterior |
| Stay outside | later | z_(s-3) > z_(s-2), then exterior |
| Enter the gap at step t | later | x_(h+1) > x_h, then barrier q_(h+1) |

At the fork the two adjacent labels separating the jumped pairs are
$x_{d+4},x_{d+1}$: this is exactly where the valley turned back into the
old stack. The short descent starts in $(x_d,q_{d+1})$. Its gaps are
$(x_{h-4},q_{h-3})$, obtained from successively smaller interleaved
mountain/valley labels, down to $(q_0,q_1)$. This last gap is inside the
short old mountain arc, leaving only adjacency at $s=k-2$. For $d=0$
the first short gap is already the last one. For $t=4$ the gap between
the fork pairs is the first mountain's adjacent choice, so no $x_{k+1}$
is needed.

Taking the gap between the fork pairs instead leaves the outermost
$x_{d+3}$ and $x_{d+2}$ on opposite wings. The next two jumps therefore
go to exterior gaps. At $s=t$ a mountain can stay outside forever or
enter $(x_{d+1},z_{t-3})$. From that gap $x_{d+1}$ is next in the
walking direction, its partner $x_d$ neighbors $q_{d+1}$, and the same
interleaved descent repeats one index lower at each step. It is four steps
later than the short descent and only reaches $(x_1,q_2)$ by the horizon.
This proves the table and gives one spine through all $k$ steps, a short
branch at $t-3,\ldots,k-3$ and a delayed branch at $t,\ldots,k$.
Their sum is $k+2(d+1)$.

For no mountain turn there is no old bridge and no fork. The first
mountain is adjacent toward $q_{k-3}$. Through $s=k-2$ the continuing
gap is $(x_h,q_{h-3})$, with the same alternating jump and barrier as
above. At the last two steps, $x_3,x_2$ and $x_2,x_1$ are the only
jumped pairs and each leads outside. Thus exactly one history stays open
at every length, contributing $k$.

### Sum and check

For $k\ge3$ the sum is
$2k-2+k+\sum_{t=2}^k(3k-t-1)+\sum_{t=4}^k(3k-2t+2)$.
The two sums evaluate to $(5k^2-9k+4)/2$ and $(2k-2)(k-3)$.
With the no-turn terms these give $(9k^2-19k+12)/2$.
At $k=2$ the two outside prefixes contribute two and three.
The same expression gives five.

```sh
python3 projects/three-runs-of-stamps/open_sum.py 13 --verify
```

Recorded output:

```text
M^13 V^13 M^13, no adjacent valley from step two onward
24 prefixes, 643 labeled completions
Each constructed completion set agrees with whole-matching enumeration.
```

The comparison checks actual labeled stacks, not just the sum. The tests
also enumerate every two-run prefix through $k=12$, separately check the
seven-face permutation universe, and challenge the individual trajectory
sets at $k=13,16,21,24$. No priority or independent proof review is claimed.
