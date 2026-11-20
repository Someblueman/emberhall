# Count every strip that first closes on its last valley

For three equal blocks of length $k$, let $S(k,k)$ count the labeled layer
orders in which the first adjacent valley after valley one is the last
valley. The count is $7k^2-23k+21$ for $k\ge3$, with five orders at $k=2$.
At $k=13$, 23 stopped prefixes give 905 full stacks. This note assembles
the terminal case and proves the later-turn terms. It uses the separate
early-turn result identified below.

| First inward mountain | Middle valley route | Weight at $k\ge5$ |
|---|---|---:|
| None | outside, inside | $3k-4$, $2k-2$ |
| 2, 3, 4 | one prefix each | $4k-6$, $4k-7$, $4k-8$ respectively |
| $5\le t\le k$, $d=k-t$ | outside, inside | $3k+2d-2$, $2k+2d$ |

## Where the prefixes come from

Keep the notation and directed matching walk of [the unclosed-sector
proof](open-sum.md). Its outside and inside routes are named by the
position of $x_k$ in the *unclosed* witness. Delete this face and add an
adjacent valley in its place. The turn and all earlier valley choices are
preserved. The two witnesses at $t=4$ had their fork at $x_k$, so their
stopped prefixes coincide. At $t\ge5$ the fork was earlier and the two
remain distinguishable. The no-turn prefixes forked at step three.

This constructs $k$ outside and $k-3$ inside prefixes for $k\ge4$.
They exhaust the $2k-3$ terminal stops, since each arises by an adjacent
extension of an open prefix of length $k-1$. The count of those open
prefixes is the difference of the two-block counts at valley lengths
$k-1$ and $k-2$, as in [the decomposition](escape-chain.md).
For $k=3$ there are three prefixes after the no-turn step-three histories
coalesce. The two at $k=2$ are separately enumerated.

## The inside route gains a second mountain start

For a finite $t\ge5$, or no turn with $k\ge4$, the last **unclosed**
valley $x_k$ is in $(q_{k-3},q_{k-1})$. The adjacent **stopped** valley
instead lies in $(q_{k-2},x_{k-1})$. Let $P$ be the common order after
deleting $x_k$. The two gaps of $P$ are distinct.

Start with the adjacent first mountain in the stopped prefix. The pair
$(z_1,x_k)$ is consecutive, as it was after the first mountain in the
unclosed inside prefix. Moving that pair from one of the named gaps of
$P$ to the other gives a bijection of their **open** suffix histories.
Here “open” starts monitoring adjacency at the second mountain.

To see this, at mountain two the next directional walk on either order
jumps $x_k$ to its partner $x_{k-1}$. On passing the partner it is in
the same old gap on both drawings. The rest of the walk agrees, including
the second jump if $t=5$. If the walk closes immediately, each order has
its one forced tail. Otherwise every continuing insertion at this step
is in an unaffected gap. From mountain three onward refer to the inside
walking table in [open-sum.md](open-sum.md): no walked gap has a
$q_{k-3},q_{k-2}$ or $q_{k-1}$ endpoint. In the regular run its largest
q index is $h-3\le k-5$; at the fork it is $d+1\le k-4$; in the
delayed run it is $h+1\le k-4$. The special no-turn run has the same
regular bound and ends outdoors. No later jump uses $x_k$ or $z_1$.
Thus neither gap is visited between paired ends, neither gets subdivided,
and removing and replacing the pair leaves each later walk unchanged.
Placing the pair back is the inverse. The code checks both the consecutive
pair and the vacant destination gap whenever it moves an open order.

The stopped prefix has **one additional first mountain gap**. Starting
from $x_k$, the walk jumps $q_{k-2}$ to $q_{k-3}$ before the barrier
$x_{k-2}$. After that jump, at each mountain $s$ put $h=k-s+1$.
The new gap is $(q_{h-3},x_{h-2})$ through $s=k-2$. The walk is
$q_{h-2}>q_{h-3}$ followed by barrier $x_{h-2}$. Indeed the preceding
inserted face neighbors $q_{h-2}$; on the opposite wing the partner
$q_{h-3}$ neighbors $x_{h-2}$. These statements follow down the two
wings of the inside prefix. Before meeting the bridge they use the gaps
$(q_{j-3},q_{j-1})$ occupied by the returning valleys. At the bridge
the arc $q_{d+3},q_{d+2}$ spans the older block, and jumps it in one
step. The neighboring valley on its far side is $x_{d+3}$, which was
the second exterior valley before the return. From there the original
inner spiral has $x_j$ in $(q_{j-1},q_{j+1})$ and the same walk
continues to $(q_0,x_1)$. Only the adjacent gap is possible at the next
step. With no mountain turn the old spiral is continuous and the bridge
step is absent.

Counting one completion for each open history as before, the extra start
contributes $k-2$. The transferred start contributes $k+2d+2$ for a
finite turn, and $k$ for no turn. This proves the inside weights.

## The outside route runs the same descent twice

Take $t\ge5$. The $k-1$ valleys before the stop reached the exterior
on the [outside witness](open-sum.md). The adjacent $x_k$ is between
$x_{k-1}$ and $x_{k-3}$. A first mountain placed beside $x_k$ starts
the outer path. At steps two and three its walks jump $x_k>x_{k-1}$
and $x_{k-1}>x_{k-2}$ to the opposite exterior ends. At four the
walk is $x_{k-2}>x_{k-3},z_1>z_2$ followed by the exterior. These are
the outer wing neighbors left by the stopped valley and the first
three mountains. Choosing both jumps gives the continuing exterior
spiral, with one open order at every length. Choosing just the first
jump enters $(x_{k-3},z_1)$ and begins a delayed descent. All the
nonadjacent first-mountain gaps begin the early descent instead.

Index both descents by a virtual step $j$, starting at five. For the
early descent $j=s+4$, where $s$ is the actual mountain step. For the
delayed descent $j=s$ after the entry at step four. Put $h=k-j+1$.
The common walk is

| Stage | Jumps in order | Barrier |
|---|---|---|
| $j<t$ | $x_{h+1}>x_h$ | $x_{h+2}$ |
| $j=t$ | $x_{h+1}>x_h$, then $q_{h+2}>q_{h+1}$ | $x_{h+2}$ |
| Continue beyond the second jump | $q_{h+2}>q_{h+1}$ | $x_{h+2}$ |
| Continue beyond the first jump | $x_{h+1}>x_h$ | $q_{h+1}$ |

At the first entry $h=k-4$, and the first face in the walking direction
is $x_{k-3}$ on both drawings. Its mate is $x_{k-4}$. Extra exterior
mountains from the delayed entry are beyond the listed barriers or
enclose the walking interval. Once the first jump has been taken,
the two drawings have the same next current gap against all the
remaining old faces. Until $j=t$ the jump lands in $(x_h,x_{h+2})$.
The next direction reverses and the next pair lies one valley inward.
At $j=t$, $h=d+1$ exactly reaches the old valley bridge. The block from
$q_{d+3}$ to $q_{d+2}$ intervenes between $x_{d+1}$ and $x_{d+3}$.
Its endpoints are partners. The two open gaps after these jumps are
$(x_h,q_{h+2})$ and $(q_{h+1},x_{h+2})$. Subsequently the first
trajectory follows $(x_h,q_{h+1})$ and the second
$(q_{h+1},x_{h+2})$. They are the same interleaved trajectories as
in the unclosed-sector proof. The larger indices have already been
passed, so the named gap's neighbors and the paired arc on the other
wing give the entire forward walk. This proves the table by induction.

The early descent has four more steps available after the common
entry. On the first trajectory the $h=0$ jump is $x_1>q_0$, ending
in $(q_0,q_1)$. The next mountain is trapped. On the second, the $h=0$
jump is $q_2>q_1$, ending in $(q_1,x_2)$; at $h=-1$ the jump is
$q_1>q_0$ ending in $(q_0,x_1)$, where the next step is trapped.
Thus the early descent has one spine through $s=k-2$, plus the branch
from $s=t-4$ through $s=k-3$, giving $(k-2)+(d+2)$ open orders.
The delayed descent has its entry at $s=4$, then one spine to $k$ and
another branch from $t$ to $k$, giving $(k-3)+(d+1)$. Adding the $k$
exterior orders gives $3k+2d-2$. Largest-label deletion recovers the
first-mountain gap, optional step-four departure, and the choice at the
bridge. Closing at the next adjacent mountain recovers exactly one
full order from each open history.

With no initial mountain turn the outside case is precisely the
exterior-spiral family. Its core bijection and gap table give $3k-4$
for every $k\ge4$. [Exterior proof](WEIGHTED_OPEN.md).

## Early turns and the sum

The early-turn component supplies the three exceptional weights
$4k-6,4k-7,4k-8$ for $k\ge5$. Its named-gap argument is separately
owned in [the early-turn proof](terminal-turns.md). The runnable
checker counts these three rows by legal insertion and never uses their
formulas to produce a stack.

For the remaining $k-4$ ordinary turns the sum of both weights is
$5k-2+4d$, with $d=0,\ldots,k-5$. The no-turn row contributes $5k-6$
and the three early turns contribute $12k-21$. Adding gives

$$5k-6+12k-21+(k-4)(5k-2)+2(k-5)(k-4)=7k^2-23k+21.$$

Full matching enumeration gives respectively 5, 15 and 41 at $k=2,3,4$.
The seven-face permutation universe independently checks the first value.
At $k=3,4$ the quadratic gives 15 and 41. At $k=2$ it gives 3 and the
separate count is necessary.

```sh
python3 projects/three-runs-of-stamps/terminal_stop.py 13 --verify
```

Recorded output:

```text
M^13 V^13 M^13, first adjacent valley after V1 at step 13
23 prefixes, 905 labeled completions
Each terminal prefix has the same endings under whole-matching enumeration.
```

The tests compare the full prefix inventory and all labeled orders through
$k=13$ and challenge each later-turn set separately at $k=15,16,22,25$.
This is the terminal contribution. Completing the cubic also requires
the open and interior stopped sectors and an independent mathematical review.
