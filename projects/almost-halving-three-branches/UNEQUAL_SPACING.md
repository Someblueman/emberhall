# Signed reflections beyond equal arm spacings

Fern, 21 November 2026. This extends the construction in
[MIDDLE_PREFIX.md](MIDDLE_PREFIX.md) to unequal spacings and disconnected
reflection graphs. It proves a sufficient condition for full partitions,
an exact existence criterion **within this sign template**, and the project's
target for every `T(50t,33t,9t)`, `t>=1`. It does not settle arbitrary triples.
Priority remains [provisional](PRIORITY_REFRESH.md); this is a result beyond
the current construction menu, not a claim of novelty in the literature.
Independent mathematical reconstruction and source integration remain required.

## Run the actual construction

From the repository root, with Python 3.10+ and its standard library:

```sh
python3 projects/almost-halving-three-branches/unequal_spacing.py 50 33 9
python3 projects/almost-halving-three-branches/unequal_spacing.py --prove
```

The first command emits both vertex sets and complete distance profiles in
the existing checker format. Its recorded result is size **46**, target 45,
upper bound 46, with only vertex `[3,9]` omitted. The ordinary command gives
size 43 on this input. This module does not change that command. Add `--summary`
for compact output; pipe a complete result into `published_cases.py --check -`
for separate input validation. The second command expands the universal
Laurent reduction reused from `middle_prefix.py`; the graph existence proof
below is mathematical, not established by finite substitution.

`full_partition(a,m,c)` is importable. The CLI's `prefix_witness(lengths)`
tries the 20 positive prefix shapes obtained by deleting at most three tips,
and their six arm orders. It returns the largest supported full-prefix pair,
using original arm labels and original-tree distances. It never searches
vertex subsets. Exit 2 with "no supported reflection prefix" is a constructor
limitation, not an upper bound on other pairs.

## The full-partition theorem

Let `a>m>=1` have opposite parity, and let `c>=2` be even. Put

```text
ell = a-m   (odd),       g = gcd(ell,c-m)   (positive and odd).
```

If **g divides m+1**, `T(a,m,c)` has a full homometric partition, with
`(1+a+m+c)/2` vertices in each set. Neither a nor m individually needs to
be odd. The condition is also necessary for the following reflection word
to exist; necessity is asserted only for that word, not all partitions.

For residues `0<=j<ell`, seek signs `u_j` with `u_0=-1` and

```text
u_((m-j) mod ell) = u_j,
u_((c-j) mod ell) = (-1)^floor((c-j)/ell) * u_j.       (1)
```

Extend u periodically. For every integer p, including negative p, define
`h_p=-(-1)^floor(p/ell)*u_(p mod ell)`. Colour the centre +; use `u_p` on
the a arm, `-u_p` on the m arm, and `h_p` on the c arm.

### Exactly when the word exists

Write `alpha(j)=(m-j) mod ell`, `beta(j)=(c-j) mod ell`. Alpha edges have
sign +; beta edges have the sign in (1), equal in both directions. Both
involutions have one fixed point. Both fixed loops are positive: for beta,
`c-2j=q*ell`, and c even and ell odd force q even.

Their product is translation by `c-m` modulo ell. Its orbits have length
`L=ell/g` and are the residue classes modulo g. Alpha pairs class r with
`r'=(m-r) mod g`. A paired pair of distinct classes gives an alternating
cycle of length 2L. The unique class with r=r' gives a path with the two
positive fixed loops (a single vertex if L=1).

Multiplying the signs around the cycle for classes r,r' gives

```text
(-1)^E,   E=(c-r-r')/g-(L-1).                       (2)
```

Indeed, over an orbit the canonical representatives sum to
`L*r+g*L*(L-1)/2`; their alpha images have the same sum with r replaced by
r'. Summing the beta quotients gives (2). Since c is even and g,L are odd,
the sign is positive exactly when r+r' is even.

Put `s=m mod g`. If `s=g-1`, every pair has `r+r'=g-1`, which is even;
all cycles are consistent. Choose a sign in each connected component and
propagate, choosing - at residue zero. If `s<g-1` is odd, the pair 0,s
has odd sum. If s is even, the distinct pair s+1,g-1 has odd sum. Either
gives an inconsistent negative cycle. The self-paired class always has
positive loops. Thus (1) is solvable exactly when `s=g-1`, equivalently
`g | m+1`. This handles disconnected graphs; assuming connectivity alone
would discard valid cases such as `(a,m,c)=(14,5,8)` with g=3.

### Balance and all distance multiplicities

Let a star substitute z^-1. Put

```text
K=z^ell, B=z^m, C=z^c, A=KB,
U=sum_(p=1)^a u_p z^p,  V=-sum_(p=1)^m u_p z^p,
W=sum_(p=1)^c h_p z^p, H=1+W,
P=sum_(j=1)^ell u_j z^j, R=sum_(j=1)^ell u_(m+j) z^j.
```

Periodicity gives `U+KV=P`, `U+V=BR`. Equation (1) gives `u_m=u_0=-1`,
`u_(m+j)=u_(-j)`, and `h_(c-p)=h_p`; hence `H=CH*`. The anti-periodic
h word gives `(1+K)H=-sum_(j=0)^(ell-1) u_j z^j-C R`. The endpoint
u_0=-1 and the reflected word give
`R-P-KP*=-sum_(j=0)^(ell-1) u_j z^j`. Thus

```text
P+(1-K)V-BR = 0,
(1-C)R-P-KP*-(1+K)H = 0.                            (3)
```

This is the same finite-word calculation as MIDDLE_PREFIX, sections 2–3;
it uses no relationship between c and a+m. It also holds when c<ell because
overlapping head and tail terms add as polynomial coefficients. At z=1,
`R(1)=P(1)`, (3) gives `H(1)=-P(1)`, and `U(1)+V(1)=P(1)`. Thus the
total sign sum is zero: the two sets have equal size and use every vertex.

The full signed-shell expression is

```text
Q=1-A-B-C + U(1-B-C)+V(1-A-C)+W(1-A-B)-AU*-BV*-CW*.
```

Substitute `A=KB`, `U=P-KV`, `CW*=H-C`. Exact expansion gives

```text
Q = B*((1-C)R-P-KP*-(1+K)H) + (1-C)*(P+(1-K)V-BR) = 0.
```

For balanced signs, the signed-shell identity gives
`(1-z)*sum_(k>=1) L_k z^k=zQ`, where `L_k` is twice the difference between
the two within-set distance multiplicities. Therefore every multiplicity
agrees. Balance, the complete colouring, and Q=0 prove the theorem.

The earlier middle-tip result has `a=b+d`, `m=b-2`, `c=b-d`, with b,d odd.
Here `g=gcd(d+2,2-d)=gcd(d+2,4)=1`, recovering that entire family.

## An infinite family outside equal spacing

For **every integer t>=1**, `T(50t,33t,9t)` has a pair of size at least
`46t-1`, meeting the project's target. Here are two possible retained
templates for each parity; entries are (a,m,c), not original arm labels:

| t | First template | Second template |
|---|---|---|
| odd | `(50t-2,9t,33t-1)` | `(50t,9t-2,33t-1)` |
| even | `(50t-2,33t-1,9t)` | `(50t,33t-1,9t-2)` |

Each deletes three terminal vertices, so a full retained partition has
size `46t-1`. Every displayed arm is positive and has the required parity.
In the first column g divides 7 and is 7 only when `t=5 mod7`. In the
second g divides 7 and is 7 only when `t=2 mod7`. (Subtract the appropriate
24- and 41-multiples, or 24- and 17-multiples, of the two gcd arguments.)
These two exceptional residues are distinct, so one template has g=1.
The full-partition theorem applies for every t. Restoring terminal vertices
does not change any retained distance.

Many scales attain the larger disjointness bound 46t by omitting only one
tip. At t=1 the CLI records precisely that, proving `h(T(50,33,9))=46`.
No optimality for every scale is claimed by the three-tip argument.

## An infinite limitation of this template

For odd `b>=9`, consider `T(b+50,b,b-6)`. Any supported prefix here must
omit exactly two vertices: the original three arms are odd, and supported
full prefixes have exactly one odd arm and an even total vertex count.
Thus one tip must be removed from each of two distinct arms. The three
choices give these exact criteria, independent of which admissible arm is
called a:

| Trimmed arms | g | Required condition |
|---|---|---|
| first and second | 5 | `b=0 mod5` |
| first and third | 7 | `b=6 mod7` |
| second and third | 3 | `b=0 mod3` |

Consequently **every `b=11+210k`, k>=0, is excluded by this prefix
template**. This is a proved limitation, not a solver timeout. It is not a
negative theorem about homometric sets: at k=1, `(271,221,215)`, the existing
ordinary command already constructs target-size sets of 353. At k=0 it
returns 37 versus target 38; that case remains a diagnostic gap here.

Tests independently count graph distances, enumerate all normalized sign
words for 112 small parameter triples, cover disconnected graphs and
negative-index h identities, validate relabelled prefixes in the original
metric, and reject a size-preserving changed witness through the actual CLI.
Finite tests support the implementation; the all-parameter claims rest on
the proofs above. The general target and unread-priority gaps remain open.
