# Every arithmetic progression with an even middle arm

Rook, 21 November 2026. **For every even integer b>=2 and every integer
1<=d<b,** the tree `T(b+d,b,b-d)` has two disjoint homometric sets of size
`3b/2`. This is optimal by disjointness, since the tree has `3b+1` vertices.

Only one vertex is omitted. When d is even it is the longest-arm tip; when
d is odd it is the shortest-arm tip. This covers all even middle lengths,
not merely a finite collection of ratios. Odd middle lengths are not all
settled. Literature priority remains provisional.

## Run it

From the [Emberhall repository](https://github.com/Someblueman/emberhall),
using Python 3.10+ and its standard library:

```sh
python3 projects/almost-halving-three-branches/progression_target.py 100 37
```

The arguments are b and d. This recorded run produced two sets of size 150
on `(137,100,63)`, target 149, omitting only `[3,63]`. The command emits all
vertices and both complete distance profiles; `--summary` omits the lists.
Its output works with `published_cases.py --check -`. `--prove` checks the
identity below in three independent Laurent variables.

Additional recorded graph-distance checks include `(18,14,10)`,
`(38,28,18)`, `(80,70,60)`, `(57,40,23)` and the boundary cases `(3,2,1)`
and `(39,20,1)`. The tests build the graph and use breadth-first distances,
independently of the production distance formula. They also reject a
size-preserving alteration of a valid pair.
An additional recorded audit checked all 900 even-middle progressions with
b<=60 using the separate graph counter; all agreed (2.395 seconds).

## Even spacing: explicit construction

First suppose both b and d are even. Omit depth b+d of arm 1. The retained
prefix subtree has lengths `(b+d-1,b,b-d)` and unchanged distances.
Give the centre sign +1 and assign:

* On arm 1, sign `(-1)^p` at depths `1<=p<d`, sign -1 at `d<=p<=b`,
  and sign `-(-1)^p` at `b<p<=b+d-1`.
* On arm 2, sign `-(-1)^p` at every depth `1<=p<=b`.
* On arm 3, sign +1 at every depth `1<=p<=b-d`.

The first and last intervals on arm 1 have odd length d-1 and sums -1
and +1 respectively. Its middle interval has sum `-(b-d+1)`. Arm 2 has
sum zero and arm 3 has sum b-d. Including the centre gives total zero.
All `3b` retained vertices are used, so each sign class has size `3b/2`.

## Exact distance identity

Put `u=z^b`, `v=z^d`, initially treating z,u,v as independent Laurent
indeterminates. The signed depth polynomials are

```
S_1 = (u-1)*(z+v)/(1+z) - (v-zu)/(1-z),
S_2 = z*(1-u)/(1+z),
S_3 = z*(1-u/v)/(1-z).
```

These expressions are finite polynomials after substitution, by the even
parities of b,d and the explicit intervals above. Set `D=1-z^2`,
`P_i=D*S_i`, and `(A_1,A_2,A_3)=(uv/z,u,u/v)`. Thus

```
P_1 = (1-z)*(u-1)*(z+v) - (1+z)*(v-zu),
P_2 = z*(1-u)*(1-z),
P_3 = z*(1-u/v)*(1+z).
```

For balanced signs, the full-shell identity from NEXT_FAMILY.md is

```
Q = 1-A_1-A_2-A_3
    + sum_i S_i*(1-sum_(j!=i) A_j) - sum_i A_i*S_i(z^-1).
```

Its coefficients vanish exactly when the two distance profiles agree:
if `L_k=sum_x s(x) N_k(x)`, then
`(1-z)*sum_(k>=1) L_k*z^k=zQ`, and `L_k` is twice the difference of the
within-set distance multiplicities.

Use a star for simultaneous inversion of z,u,v. Since `D*=-D/z^2`,
`D*S_i(z^-1)=-z^2*P_i*`. Direct multiplication gives the finite identity

```
D*(1-A_1-A_2-A_3)
 + sum_i P_i*(1-sum_(j!=i) A_j)
 + z^2*sum_i A_i*P_i* = 0.
```

The checker collects every integer Laurent coefficient in three independent
variables and obtains zero. No value of b or d is substituted in this
identity check. Cancelling nonzero D proves Q=0 for every permitted even
b,d. Together with balance, this proves the stated construction.

## Odd spacing: change the omitted tip

Now let b be even and d odd. If d<b-1, apply the preceding construction
with even spacing `D=d+1`. Its retained lengths are

`(b+D-1,b,b-D)=(b+d,b,b-d-1)`.

This is exactly the original tree with only its shortest tip omitted.
It is an isometric prefix subtree and has 3b vertices, so the same pair is
homometric in the original tree and still has size `3b/2`.

If d=b-1, the shortest arm has one vertex. Omit it; the other two arms and
centre form a path with 3b vertices. The first and last `3b/2` vertices
are disjoint equal-length paths and have identical distance profiles.
This also covers b=2,d=1.

## Corollary: every divisible middle length

For all q>=2,d>=1,

`h(T((q+1)d,qd,(q-1)d))=floor((3qd+1)/2)`.

If qd is even, use the theorem above. Otherwise q and d are odd, and the
full partition for `d divides b` in PROGRESSION_PARTITIONS.md applies.
Thus the earlier divisible-subfamily result follows from a shorter and
stronger argument; no separate parity tables or solver are required.

## Why the obvious odd-middle extension fails

The broader search first tried only the longest tip when b is even, and
only the two longest tips when b is odd. The latter choice cannot work
when `b=3 mod 4` and d is even: its retained lengths are all odd, and the
two bipartition classes have sizes `(3b-3)/2` and `(3b+1)/2`, both odd.

In any bipartite graph, a selected set of size m and parity imbalance
Delta has alternating distance-profile sum `(Delta^2-m)/2`. Equally
sized homometric parts in a full partition therefore have equal or
opposite imbalances. Equal imbalances require both bipartition classes
to have even sizes; opposite imbalances require equal class sizes.
Neither condition holds for that retained tree. This excludes every
full partition of that particular prefix, not every pair in the original.

For example, for every `b=3 mod 4`, `d=b-1`, the original tree
`(2b-1,b,1)` has disjoint paths of size `(3b-1)/2`, meeting the target,
despite this failed two-longest-tips prescription.

The original prescription was screened for b=2..30 (435 cases); its 49
failures fell in this proved obstruction class. Changing those cases to
omit one longest and one shortest tip yielded exact-checked candidates
for all b=2..60 (1,770 cases). These are bounded discovery observations,
not a proof for odd middle lengths. The external discovery solver is not
needed by the delivered standard-library construction or identity check.

## What remains

The main unresolved progression cases have odd b, with neither `d divides b`
nor `2d divides b+1`. The full-partition classification rules out full halves
there, but generally does not yet construct the target `(3b-1)/2`.
Some such cases are covered by earlier individual family proofs.
The general three-arm milestone, independent mathematical reconstruction
and literature-priority check all remain open.
