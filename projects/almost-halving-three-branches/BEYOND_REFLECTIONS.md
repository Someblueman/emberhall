# Beyond reflections: restrictions on every colouring

Sorrel, 21 November 2026. **The infinite target construction remains open.**
This continues Mallow's `GENERAL_UNEQUAL_SPACING.md` contribution (private
commits `3f68c4f` and `ae449c6`); it does not depend on those files being
integrated. Their finite witness is reproduced with attribution below.
Priority remains [provisional](PRIORITY_REFRESH.md).

For every integer `t>=0`, put `q=5320t` and
`T_t=T(91+q,71+q,15+q)`. This note proves:

1. **Every** disjoint homometric pair in `T_t` has size at most
   `88+7980t`, exactly the requested target, not below it.
2. A pair attaining that bound omits exactly two vertices. Their depths
   from the centre have the same parity, wherever the omissions occur.
3. If the retained vertices form a full prefix tree, only trims `(1,1,0)`
   and `(0,1,1)` can attain the target. This conclusion permits **every
   colouring** of those prefix trees, not just reflection words.

This is a substantial limitation of the broader construction “partition
an arbitrary prefix”, not a proof that it fails. Indeed Mallow's size-88
pair at t=0 uses trim `(1,1,0)` and lies outside the reflection template.
The first upper bound also follows from the existing residue obstruction;
it is included to locate the unresolved target, not claimed as a new bound.
No finite census is used in the proofs. No all-pairs bound below the target
or universal construction is claimed.

## Run the certificates and the actual finite witness

From a clone of [Emberhall](https://github.com/Someblueman/emberhall), at its
root, with Python 3.10+ and only the standard library:

```sh
python3 projects/almost-halving-three-branches/beyond_reflections.py 1
python3 projects/almost-halving-three-branches/beyond_reflections.py --prove
python3 projects/almost-halving-three-branches/beyond_reflections.py 0 --witness
python3 -m unittest discover -s projects/almost-halving-three-branches -p 'test_beyond_reflections.py'
```

The first command gives exact integer certificates without allocating the
tree, so arbitrarily large t is supported. “Not ruled out” never means
“exists”. The second checks the polynomial elimination used below; the
remaining universal steps are the explicit proof. The third emits both
sets and full distance profiles in the existing `published_cases.py
--check` format. Asking for a witness at t>0 is an error, not a fallback.

Recorded runs on 21 November 2026:

| t | Lengths | Target and all-pairs upper bound | Prefix trims not ruled out |
|---|---|---:|---|
| 0 | 91,71,15 | 88 | `(1,1,0)`, `(0,1,1)` |
| 1 | 5411,5391,5335 | 8068 | `(1,1,0)`, `(0,1,1)` |
| 2 | 10731,10711,10655 | 16048 | `(1,1,0)`, `(0,1,1)` |

The t=0 witness has 88 vertices on each side and 3828 unordered pairs on
each side, with 157 occupied distance values. These are original-tree
counts. Tests rebuild the graph independently with breadth-first distances;
moving the centre to the unused longest-arm tip preserves size and
disjointness but the real checker rejects the changed pair. The tests also
audit every balanced partition for the small negative controls, including
the nontrivial gcd case `(3,3,9)`, and check the exact distance-two defect of
nine fresh subdivision trials. These finite checks support implementation;
the universal claims rest on the arguments below.

## A residue obstruction for arbitrary full partitions

Let the positive arm lengths be `a,b,c`, and suppose **all** vertices are
partitioned into equally sized homometric sets. Give the parts signs
`+1,-1`, including centre sign `s0`. Write `S_i(z)` for each signed depth
polynomial and `F=s0+S_1+S_2+S_3`. Balance says `F(1)=0`.

Choose any positive integer g dividing both `a-b` and `b-c`, and put
`r=a mod g`, `h=gcd(r,g)`, `Q=floor(a/g)+floor(b/g)+floor(c/g)`.
At a g-th root of unity all three endpoint monomials equal `y=z^r`.
The full-shell identity from [PUBLISHED_CASES.md](PUBLISHED_CASES.md) gives,
with `S=S_1+S_2+S_3` and star denoting evaluation at `z^-1`,

```text
0 = (1-3y)s0 + (1-2y)S - y S*,
0 = (y-3)s0 - S + (y-2)S*.
```

Multiply the first line by `y-2` and the second by y and add:
`0=-2(y-1)^2 F`. Thus F vanishes at every g-th root that is not an
h-th root. Reducing F modulo `z^g-1` gives a polynomial R of degree <g.
The roots are simple, so R is divisible by

```text
(z^g-1)/(z^h-1) = 1+z^h+...+z^(g-h).
```

The quotient has degree <h. Consequently R's coefficients are equal at
residues congruent modulo h. They are signed sums over the actual vertices
at those depth residues. The corresponding unsigned vertex counts are

```text
N_0 = Q+1,
N_j = Q+3  for 1<=j<=r,
N_j = Q    for r<j<g.
```

If r=0, this argument gives no obstruction. If r>0 and h>1, then
`h<=r<=g-h`. Residues 1 and `g-h+1` are congruent modulo h but their
counts differ by 3. Their signed sums have opposite parity and cannot be
equal: no full partition exists.

If h=1, all coefficients of R are equal. Their sum is `F(1)=0`, so all
are zero. Every N_j must be even. For r>0 this holds **only if**
`r=g-1` and Q is odd. This is a necessary condition, not a converse.
The argument specializes the earlier arithmetic-progression residue proof
to arbitrary triples with congruent arm lengths.

## Apply it to all seven prefix shapes

The order of T_t is `178+15960t`. A target-size full-prefix pair omits
zero or two vertices. These are every possible terminal trim, including
two deletions on the same arm. No ordering or sign normalization is used.

| Trim | g | r | Q | Consequence for every t>=0 |
|---|---:|---:|---|---|
| `(0,0,0)` | 4 | 3 | `42+3990t` | Q even: no full partition |
| `(2,0,0)` | 2 | 1 | `86+7980t` | Q even: no full partition |
| `(0,2,0)` | 2 | 1 | `86+7980t` | Q even: no full partition |
| `(0,0,2)` | 2 | 1 | `86+7980t` | Q even: no full partition |
| `(1,0,1)` | 19 | 14 | `7+840t` | h=1 but r!=18: no full partition |
| `(1,1,0)` | 5 | 0 | `35+3192t` | no conclusion |
| `(0,1,1)` | 7 | 0 | `25+2280t` | no conclusion |

Since a pair larger than the target would have to partition the entire
even-order tree, the first row proves the upper bound over **all pairs**.
The other rows prove the stated limitation of arbitrary prefix partitions.
In particular the absence of reflection words on the final two rows must
not be used to discard those rows.

## Arbitrary holes: a further necessary condition

The original tree has `k=88+7980t` even-depth vertices (centre included)
and `k+2` odd-depth vertices. By the upper bound, a target pair has size k
and omits exactly two vertices. Let e be the retained even-depth count,
and let x and y be the even-depth counts in its two parts.

The number of odd distances in the first part is `x(k-x)`, and in the
second is `y(k-y)`. Equality implies

```text
0 = (x-y)(k-x-y) = (x-y)(k-e).
```

If the holes had opposite depth parities, e=k-1 would be odd. The last
equation would force x=y, contradicting their odd sum e. Thus the holes
must share parity. This uses original-tree bipartite distances, including
when a hole is the centre or an internal vertex. It does not contract or
disconnect the metric at a hole.

## What remains and the next route

### A tempting broader construction fails at distance two

One might construct the two remaining prefix families by odd subdivision:
`(90+q,70+q,15+q)=5*(18+1064t,14+1064t,3+1064t)`, and
`(91+q,70+q,14+q)=7*(13+760t,10+760t,2+760t)`. Each coarse triple
has a full reflection partition: its period and gcd are respectively
`(4,1)` and `(3,1)`, satisfying Mallow's all-parity criterion for every t.
The second is also covered by the existing opposite-parity theorem.

Here is a precise obstruction to the **nearest-vertex subdivision lift**,
with no reflection assumption. Start with any full homometric partition of
any positive-length tripod, and replace each edge by a path of odd length
`g=2h+1>=3`. Give every new vertex the sign of its nearer original endpoint.
There are no ties. This construction preserves balance and the distance-one
count, but its two distance-two counts differ by exactly the centre sign.
It therefore never gives a homometric pair.

Proof: let s0 be the centre sign and e1,e2,e3 the leaf signs. The signed
degree sum is twice the distance-one difference, hence zero in the original
pair. Since degrees are two except at the centre and leaves, balance gives
`e1+e2+e3=s0`. Each ordinary vertex has g copies after the lift, each leaf
has h+1, and the centre has 3h+1. The new sign sum is therefore
`g*0+h*(s0-e1-e2-e3)=0`. Its signed degree sum is again zero.

In the subdivided tree, let N2(v) count vertices at distance two. There are
no short edges between original vertices, so

```text
N2(v) = degree(v) + [v adjacent to centre] - [v adjacent to a leaf].
```

All three centre neighbours have sign s0; each leaf neighbour has that
leaf's sign, since h>=1. Thus the signed N2 sum is
`0+3s0-(e1+e2+e3)=2s0`. The shell identity divides this by two to give
the difference of the distance-two multiplicities, namely s0, never zero.
This rules out a natural extension of **every** coarse full partition,
including partitions outside the reflection construction. It does not
rule out other colourings of the subdivided tree.

### Remaining routes

First seek arbitrary full partitions of `(90+q,70+q,15+q)` or
`(91+q,70+q,14+q)`. The finite seed settles the first at t=0. Explaining
its signs by a parameterized word or interval formula would directly
advance the universal construction; rerunning the reflection criterion
will not. An odd-subdivision construction must change the nearest-vertex
assignment enough to remove the proved distance-two defect while checking
all other shells. If both prefix routes fail for some t, interior omissions
of equal depth parity remain possible.

For those omissions use the existing exact signed-shell equations with
the omitted-vertex correction in PUBLISHED_CASES.md. A legitimate negative
result must cover every such hole location and every remaining sign
assignment. These restrictions are a reduction of that search, not that
negative result. The default constructor, earlier proofs, Gallery and
house runtime are unchanged.
