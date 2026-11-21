# Removing the two middle-arm tips

Hawthorn, 21 November 2026. **The general conjecture remains open.** This
document proves a subfamily and records an exact finite search. Neither a
construction for every odd `(b,d)` nor a counterexample has been obtained.
The project milestone is not complete. Priority remains provisional under
[PRIORITY_REFRESH.md](PRIORITY_REFRESH.md); this work does not resolve its
unread sources or make a novelty claim. Independent review is still required.

## A proved infinite subfamily

For every positive odd integer `d`, the retained tree

`T(3d+3, 2d+1, d+3)`

has a full homometric partition into sets of size `3d+4`. Thus the original
tree `T(3d+3, 2d+3, d+3)` attains the project's target, with exactly the two
middle-arm tips omitted. In the conjecture's notation this is `b=2d+3`.
For odd `d>=5` the size is optimal: neither `d | (2d+3)` nor
`2d | (2d+4)`, so the full-partition obstruction in
[PROGRESSION_PARTITIONS.md](PROGRESSION_PARTITIONS.md) gives this upper bound.
For `d=1,3`, only the stated target attainment is claimed here.

From a repository checkout, with Python 3.10+ and its standard library:

```sh
python3 projects/almost-halving-three-branches/middle_prefix.py --family 37
python3 projects/almost-halving-three-branches/middle_prefix.py --prove
```

The first command prints the sets and complete distance profiles in the
existing checker's format. Pipe it to `published_cases.py --check -` to
check the original tree. `--summary` suppresses those larger fields.
Recorded family run: original lengths `(114,77,40)`, retained lengths
`(114,75,40)`, both sets of size 115, omitted vertices `(2,76),(2,77)`.
The proof command checks four Laurent identities, four size identities
and five small base cases. Source publication awaits independent integration;
a private source-room run is not evidence of public delivery.

## Explicit construction

Write `d=2h+1`, so the retained lengths are `(6h+6,4h+3,2h+4)`.
For `0<=h<5`, the three arm sign strings are `SMALL_SIGNS[h]` in
[middle_prefix.py](middle_prefix.py). The centre has sign `+`.
These five finite pairs are checked directly by `--prove`.

For `h>=5`, let `m=h mod 4`. The table below gives each arm's interior
words `W` and boundary words `B`. Arm 1 has six blocks, arm 2 four,
and arm 3 two. All block and boundary indices start at zero.

* In block `j`, repeat its four-character word at depths `jh+p`,
  `3<=p<=h-3`, starting with its first character at `p=3`.
* Boundary word `j` starts at depth `jh-2` and proceeds one depth per
  character. A dot denotes an out-of-tree position and assigns no sign.
  The final boundary is longer because the arm ends beyond its last `jh`.

The interiors and boundaries are disjoint and cover every retained vertex.
In particular, at `h=5` the interiors are empty; neighboring five-position
boundaries remain disjoint. Take all positive vertices as one set and all
negative vertices as the other.

| m | Arm | W | B |
|---|---|---|---|
| 0 | 1 | `-+-+ -+-+ -+++ -+++ -+-+ -+-+` | `...++ +-+-+ +-+-+ +-+++ +-+++ +-+-+ +-+-+-++-` |
| 0 | 2 | `+-+- +-+- -+-+ -+-+` | `...-- -+-+- -+-++ +-+-+ +-+--+` |
| 0 | 3 | `-+-- -+--` | `...-- --+-- --+---+` |
| 1 | 1 | `++++ ++++ +-++ -+++ ++++ ++++` | `...++ +++++ +++++ +-+++ -+++- +++++ ++++++++-` |
| 1 | 2 | `---- ---- ---- ----` | `...-- ----- ----- ----- -----+` |
| 1 | 3 | `--+- -+--` | `...-- --+-- -+----+` |
| 2 | 1 | `-+-+ -+-+ -+++ ++-+ -+-+ -+-+` | `...++ +-+-+ +-+-+ +++-+ +-+++ +-+-+ +-+-+-++-` |
| 2 | 2 | `+-+- +-+- -+-+ -+-+` | `...-- -+-+- -+-++ +-+-+ +-+--+` |
| 2 | 3 | `-+-- ---+` | `...-- +---+ --+---+` |
| 3 | 1 | `++++ ++++ +-++ ++-+ ++++ ++++` | `...++ +++++ +++++ +++-+ -+++- +++++ ++++++++-` |
| 3 | 2 | `---- ---- ---- ----` | `...-- ----- ----- ----- -----+` |
| 3 | 3 | `--+- ---+` | `...-- +---+ -+----+` |

## Identity valid for every parameter

Use independent Laurent variables `z,r`, substituting `r=z^h` only after
the identity is established. Put `D=1-z^4` and let `P_i=D*S_i`, where
`S_i` is the signed depth polynomial of arm i. The endpoint monomials are

`(A_1,A_2,A_3)=(z^6*r^6, z^3*r^4, z^4*r^2)`.

If `w` is a block's four-sign word, indexed periodically so that `w(3)`
is its first sign, its contribution to `P_i` is exactly

```text
r^j * (sum_(p=3)^6 w(p)*z^p - r*sum_(q=-2)^1 w(m+q)*z^q).
```

Multiplying the finite repeated word by `1-z^4` cancels all interior
terms, leaving these four head and four tail terms. This remains valid
for the empty interior at `h=5`. A boundary sign `s` at `jh+p`
contributes `s*r^j*z^p*D`.

For each of the four table classes, integer coefficient collection gives

```text
D*(1-A_1-A_2-A_3)
 + sum_i P_i*(1-sum_(j!=i) A_j)
 + z^4*sum_i A_i*P_i(z^-1,r^-1) = 0.                 (1)
```

`symbolic_residual(m)` constructs precisely these finite expressions;
it does not fit numerical samples or substitute a finite value of h.
Because `D*S_i(z^-1)=-z^4*P_i(z^-1,r^-1)`, equation (1) is D times
the full-shell identity in [NEXT_FAMILY.md](NEXT_FAMILY.md). Cancellation
of nonzero D is valid in the Laurent polynomial ring.

For balance, write `h=4q+m`. A block contributes

`q*sum(w) + floor((m-5)/4)*sum(w) + prefix_w((m-5) mod 4)`.

Adding every block, boundary and centre gives coefficient zero for q and
constant zero, separately in all four classes. Thus the two signs occur
equally often. The full-shell identity then gives equal multiplicities
at every positive distance, not merely equal distance sums or isometry.
The retained order is `12h+14`, so each part has `6h+7=3d+4` vertices.
Deleting only terminal vertices preserves the original distances. This
proves the stated family.

## Exact search and its limits

```sh
python3 projects/almost-halving-three-branches/middle_prefix.py 47 7 --summary
python3 projects/almost-halving-three-branches/middle_prefix.py 57 9 --summary
```

Both formerly node-limited instances have positive witnesses: size 70 on
retained `(54,45,40)` and size 85 on retained `(66,55,48)`, respectively.
The tests reconstruct the original graphs and count distances by breadth-first
search, including these two cases, fresh family parameters and all small bases.
They reject an altered pair which still has disjoint, equal-sized parts.
These are finite checks, not a proof of the general conjecture.

For a fixed retained tree, assign one sign `s_v` to each vertex. The search
forms the exact integer equations

`sum_v s_v=0`, and `sum_v s_v*N_k(v)=0` for each positive distance k,

where `N_k(v)` counts retained vertices at distance k from v. Each pair
with equal signs contributes twice that sign to a shell equation; an
opposite-sign pair contributes zero. Hence these equations are equivalent
to a full homometric partition, including balance.

Exact rational row reduction expresses every pivot sign in terms of free
signs. Clearing denominators reduces the requirement that a pivot be a
sign to an equation `abs(sum c_i*s_i)=D`. The search branches on both signs,
pruning only when an exact integer reachable-sum calculation permits no
extension. Fixing the first free sign to + loses only the global colour
swap. Consequently a completed negative search would cover every colouring
of that retained tree. No negative instance is claimed here.

The command distinguishes `partition`, `node-limit` (exit 3), and an exhausted
`no-partition`; a limit never becomes a negative. Search is capped at 900
retained vertices and at the explicit node budget (`--nodes`, default 100000).
The proved family constructor does not have these search caps. Small randomly
generated sign systems are also compared with exhaustive enumeration, including
inconsistent equations and denominator-cleared targets.

The next task is still the original one: a construction for all remaining
odd `(b,d)`, or an independently reproducible exact counterexample. A proof
of this one family, finite positive witnesses, and failure of a restricted
colouring pattern do not meet that acceptance result.
