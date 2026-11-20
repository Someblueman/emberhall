# Two paths through a deep stamp fold

Fix the initial mountain length $a$, its first inward step $t$, and the
first adjacent valley after the first valley at step $r$. Write $d=a-t$.
For **$t\ge2, r\ge2, d\ge r-1$** there is exactly one such stopped
prefix. With $c\ge1$ subsequent mountains its number of labeled
completions is

```text
min(c, r+1) + min(c, r-2).
```

The empty suffix has one completion. Thus the deep row in the
[open-chain table](escape-chain.md) contributes **$2r-2$** for each
initial turn at $c=r$, including the short stops $r=2,3,4$.
When $c\ge r+1$, the count stays at $2r-1$. This is an author proof for
one row. The other interior rows and the cubic remain open.

## The nested mountain and its stopped valley

Use face zero's fixed orientation and the [labeled layer model](first-family.md).
Restricting a stack to labels at most $i$ recovers its order at step $i$.
An insertion is adjacent when it lands immediately beside the preceding face
in that order. Once an adjacent step follows a crease of the same kind, the
next arc lies on the same side as the preceding outer arc, points back
into it, and has just the adjacent gap available. Repetition forces the tail.
The [one-run spiral classification](first-family.md) gives one initial order
for each turn $t$. Take exterior mountain steps through $t-1$, then use
adjacent mountain steps through $a$.

Write $q_i=a-i$, $x_i=a+i$ for mountain and valley faces, with $x_0=q_0$.
Reflect the drawing when necessary so $q_2$ is on the right. The labels
$q_0,\ldots,q_{d+1}$ form one consecutive interval, in the order of the
coordinates $(-1)^i i$ for face $q_i$. Indeed the first inward step puts $t$ beside
$t-1$. Each following adjacent step inserts its new face between the
previous two. This gives the asserted alternating order by induction. The
older $q_{d+2}=t-2$ is on the far side of $q_{d}$ from the center (before
the turn, $t-1$ and $t-2$ were opposite exterior endpoints). We need its
side only when $d=r-1$.

Let $Q_i$ denote arc $q_iq_{i-1}$, and $X_i$ arc $x_ix_{i+1}$.
A new arc can reach a gap exactly when it points toward that gap and crosses
no older arc on its own side. In particular, suppose the current face lies
inside a same-side parent. Looking in the required direction, if the next
face is the near end of a same-side child, and the face immediately beyond
the child's far end is the parent end, exactly two gaps are possible, the
adjacent one and the one just past the child. Any interior gap crosses the
child, and passing the parent crosses the parent. Jumping the whole child
is legal because every same-side arc internal to the child has both ends
inside it. If the parent end itself is next, only adjacency is possible.

At valley step one the next face in the required direction is $q_2$, the
end of $Q_2$. Put $x_1$ in that gap. For $2\le j<r$ the parent is
$Q_{j+1}$, the child $Q_{j-1}$. Looking forward from $x_{j-1}$, the
next face is $q_{j-2}$, the child's near end. Just past its far end
$q_{j-1}$ is $q_{j+1}$. The open continuation must jump the child,
putting $x_j$ between $q_{j-1}$ and $q_{j+1}$. The induction holds because older $x_i$ have radius at most $j-1$ and each occupies a
different old gap. Assign the new coordinate $(-1)^{j-1}j$ to $x_j$.
At step $r$ choose adjacency by definition. Thus $x_r$ lies between
$x_{r-1}$ and $q_{r-2}$, at radius $r-3/2$ on their wing. This
constructs the only prefix, also when $r=2$.

## All final mountains

At the first mountain, call the adjacent choice **near** and the other
choice **far**. From step two onward count a path as open until its first
adjacent mountain. Every such close has one forced completion. The table
lists the rest of the choices. A pair in the last column denotes an
unordered pair of neighboring labels around the open insertion gap.

| Path | Mountain step $k$ | Same-side parent | Child crossed | Open insertion gap |
|---|---|---|---|---|
| Near start | 1 | $X_{r-2}$ | none | adjacent to $x_r$, toward $q_{r-2}$ |
| Far, including its start | $1\le k\le r-2$, with $h=r-k-1$ | $X_h$ | $Q_h$ | $q_{h-1},x_h$ |
| Near | $k=2$ | $Q_{r+1}$ | $X_{r-1}$ | $x_{r-1},q_r$ |
| Near | $3\le k\le r+1$, with $h=r-k+1$ | $Q_{h+2}$ | $X_h$ | $x_h,q_{h+1}$ |

To verify the far row, the current endpoint lies between $x_{h+1}$ and
$q_h$. This holds initially by the position of $x_r$ and thereafter
by the preceding insertion. The direction is toward $q_h$. Past that
child's far end $q_{h-1}$, the next face is $x_h$, the parent end.
Their wing has radii $h-1,h$. Previous far insertions had larger radii.
These arcs have the parity of the new crease. The two-gap observation
gives exactly the displayed continuation and the adjacent alternative.
At $h=0$ the endpoint lies between $q_0,x_1$, with the end of $X_0$
next. Only adjacency is possible. For $r=2$ this is already the initial
state and there is no far start.

At near step two the direction turns back toward $x_r$, with the parent
end $q_r$ immediately past the far child end $x_{r-1}$. The enclosing
arc $Q_{r+1}$ reaches from the other wing to $q_r$. At the depth
boundary its other endpoint can lie beyond additional old faces, all behind
the current endpoint. The forward gap list is the same.

For subsequent near steps the preceding open insertion lies between
$q_{h+2}$ and $x_{h+1}$, pointing toward $x_{h+1}$. Immediately past
its partner $x_h$ is the parent end $q_{h+1}$. These have radii
$h,h+1$ on the opposite wing. Earlier open insertions were farther out
on that wing. In the first instance $k=3$, the stopped valley $x_r$
and the near-start mountain lie inside the child, so they create no
extra directional gap. The index parities give the same side for child,
parent and new mountain. The table follows, also at $h=0$ using
$x_0=q_0$. After $k=r+1$ the current endpoint lies in the gap
$q_0,q_1$ of $Q_1$. Only adjacency is possible on the next step.

Each open path ending at step $k<c$ yields one complete stack by closing
on step $k+1$. Each path still open at $c$ supplies one more. Near is
open through $\min(c,r+1)$ steps and far through $\min(c,r-2)$, giving
the claimed sum. To invert this construction, remove suffix labels in
descending order, read the first mountain's gap, then find the first adjacent
mountain at step two or later (or the end of the suffix). This recovers the
branch and its closing time uniquely. At $c=r$ there are $a-r$ eligible
turns $2\le t\le a-r+1$, hence this part of the weighted sum is
$(a-r)(2r-2)$.

## Reproduction and the boundary

Run from a clone with the standard library:

```sh
python3 projects/three-runs-of-stamps/deep_turn.py 12 4 7 --verify
```

Recorded output:

```text
M^12 V^7 M^7, first inward mountain 4, first adjacent valley after V1 at 7
Stopped prefix: 3 5 18 19 7 16 9 14 11 12 13 10 15 8 17 6 4 1 0 2
12 labeled completions
The independent matching checker returns the same full orders.
```

With `--suffix 11` it returns 13. The tests compare the labeled sets and
prefix uniqueness by whole-matching enumeration across both parities
through ten initial mountains. One layer short, $a=8,t=5,r=5$, there
are **two** stopped prefixes, of weights **14 and 15**. The deep formula
would give eight and cannot be extended to that row.
