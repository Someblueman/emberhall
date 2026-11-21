# Two deleted middle tips always suffice

Hawthorn, 21 November 2026. **The two-middle-tip conjecture is true.**

For every odd `b>=3` and odd `1<=d<b`, the retained tree

`T(b+d, b-2, b-d)`

has a full homometric partition. Its two parts have `(3b-1)/2` vertices.
Viewed inside `T(b+d,b,b-d)`, they omit precisely the last two middle-arm
vertices and attain the project's half-minus-one target. This is a result
about equal multisets of distances, including multiplicities, not isometry.
It does not settle arbitrary three-arm lengths or change the full-partition
classification for the original, untrimmed arithmetic progression.

Priority remains **provisional**, subject to the unread sources in
[PRIORITY_REFRESH.md](PRIORITY_REFRESH.md). A non-author still needs to
reconstruct this proof and verify the source contribution before integration
and any wider milestone acceptance. No claim of public delivery follows from
a private source-room run.

## Run it

Python 3.10+ and the standard library suffice. From a repository checkout:

```sh
python3 projects/almost-halving-three-branches/middle_prefix.py 87 33
python3 projects/almost-halving-three-branches/middle_prefix.py --prove
```

The first command constructs the sets without search and checks their full
profiles in the original tree. It uses the existing checker format, so its
output can be piped into `published_cases.py --check -`. Add `--summary` to
suppress sets and profiles. The second command expands the universal Laurent
identity below in nine independent symbols; it does not substitute a finite
list of b,d values. The existence argument for the signs is the signed-path
proof below, not a finite computation.

Recorded runs:

| b,d | Original lengths | Retained lengths | Each part |
|---|---|---|---|
| 47,7 | 54,47,40 | 54,45,40 | 70 |
| 57,9 | 66,57,48 | 66,55,48 | 85 |
| 87,13 | 100,87,74 | 100,85,74 | 130 |
| 87,33 | 120,87,54 | 120,85,54 | 130 |
| 121,51 | 172,121,70 | 172,119,70 | 181 |
| 151,99 | 250,151,52 | 250,149,52 | 226 |

The implementation tests build the graphs and count distances by breadth-first
search, independently of the production distance formula. They cover small
odd parameters, fresh large cases, the shortest short arm, and reject a
size-preserving alteration of a valid pair.

## 1. A signed path supplies the periodic word

Put

`ell=d+2`, `m=b-2`, `c=b-d`, `a=b+d=m+ell`.

Thus ell and m are odd, c is positive and even, and `c-m=4-ell`.
All residue indices below lie in `0,...,ell-1`. Consider two reflections:

* `alpha(j) = (m-j) mod ell`, with edge sign +1;
* `beta(j) = (c-j) mod ell`, with edge sign
  `epsilon(j)=(-1)^floor((c-j)/ell)`.

The beta edge has the same sign in both directions. Indeed, writing
`c-j=q*ell+k`, with `0<=k<ell`, gives `c-k=q*ell+j` as well.
Each reflection has exactly one fixed point because ell is odd. Alpha's
loop is positive. At beta's fixed point, `c-2j=q*ell`; c and 2j are even
and ell is odd, so q is even and this loop is positive too.

Moreover, `beta(alpha(j)) = j+4 mod ell`. Since `gcd(4,ell)=1`, the graph
formed by the two reflections is connected. Removing its two positive
loops leaves a path: the two distinct fixed points have degree one and
every other vertex has degree two. Equivalently, its ell vertices have
ell-1 non-loop edges. There are no nontrivial cycles to cause a sign conflict.

Set `u_0=-1` and propagate signs along the path. This assigns every u_j a
sign, uniquely, satisfying

```text
u_(m-j mod ell) = u_j,
u_(c-j mod ell) = (-1)^floor((c-j)/ell) * u_j.       (1)
```

Extend u periodically to every integer index. In particular,
`u_m=u_0=-1` and `u_(m+j)=u_(-j)`.
The implementation traverses these two labelled edges from each visited
residue; it never searches over colourings.

## 2. Colour the retained tree

For every integer p, write `p=q*ell+j`, `0<=j<ell`, and define

`h_p = -(-1)^q * u_j`.

This definition includes negative p; the quotient is the floor quotient.
It immediately gives `h_0=1` and `h_(p+ell)=-h_p`. The second relation in
(1) gives the reflection identity `h_(c-p)=h_p` for every integer p:
if `c-j=q'*ell+k`, then

`h_(c-p)=-(-1)^(q'-q)*u_k=-(-1)^(2q'-q)*u_j=h_p`.

Assign these signs:

* centre: +1;
* long arm, depths `1,...,a`: `u_p`;
* middle arm, depths `1,...,m`: `-u_p`;
* short arm, depths `1,...,c`: `h_p`.

Every retained vertex is assigned exactly once. Positive and negative
vertices will be the required sets. We prove balance and homometry next.

## 3. Word identities, without numerical parameters

Let a star mean replacing z by z^-1. Define the finite polynomials

```text
K=z^ell, B=z^m, C=z^c, A=z^a=K*B,
U=sum_(p=1)^a u_p*z^p,
V=-sum_(p=1)^m u_p*z^p,
W=sum_(p=1)^c h_p*z^p, H=1+W,
P=sum_(j=1)^ell u_j*z^j,
R=sum_(j=1)^ell u_(m+j)*z^j.
```

Periodicity of u and cancellation of the two prefixes give

`U+K*V=P`, `U+V=B*R`, hence `P+(1-K)*V-B*R=0`.       (2)

The reflection of h gives `H=C*H*`, or `C*W*=H-C`. Also,
`u_(m+j)=u_(-j)` and `u_m=u_0=-1` imply

`R-P-K*P* = -sum_(j=0)^(ell-1) u_j*z^j`.             (3)

For clarity, the constant coefficient in (3) is -u_0; at depths
1 through ell-1 the reflected terms cancel; at ell the coefficient
is `u_m-u_0=0`.

The h sequence is anti-periodic with period ell. Multiplication of its
finite prefix H by `1+K` leaves its first ell coefficients and the negative
of the next ell coefficients after depth c. Since
`h_(c+j)=h_(-j)=u_(-j)=u_(m+j)` for `1<=j<=ell`, equation (3) yields

`(1+K)*H = (1-C)*R-P-K*P*`.                          (4)

This cancellation remains valid when `c<ell`: the head and tail terms
then overlap and are added as polynomial coefficients. No length ordering
beyond the stated hypotheses was used.

Evaluating (4) at z=1, and noting `R(1)=P(1)`, gives
`H(1)=-P(1)`. Equation (2) gives `U(1)+V(1)=P(1)`. Thus the sum of all
vertex signs, `H(1)+U(1)+V(1)`, is zero. The colouring is balanced.

## 4. Full distance multiplicities

Use the full-shell identity from [NEXT_FAMILY.md](NEXT_FAMILY.md):

```text
Q = 1-A-B-C
    + U*(1-B-C) + V*(1-A-C) + W*(1-A-B)
    - A*U* - B*V* - C*W*.
```

Here `A*U*` means A times the starred polynomial U, and similarly for
the other products. Substituting `A=K*B`, `U=P-K*V`,
`U*=P*-K^-1*V*`, and `C*W*=H-C` gives the exact factorization

```text
Q = B * ((1-C)*R-P-K*P*-(1+K)*H)
    + (1-C) * (P+(1-K)*V-B*R).
```

Both parentheses vanish by (2) and (4), so Q=0. `--prove` checks precisely
this factorization in a free Laurent ring, treating K,B,C,P,V,P*,V*,H,R
as independent symbols. It is separate from graph-distance testing.

For balanced signs, the full-shell identity states
`(1-z)*sum_(k>=1) L_k*z^k = z*Q`, where
`L_k=sum_v s_v*N_k(v)` and N_k(v) counts retained vertices at distance k.
Every pair of equal signs contributes twice its sign to L_k, while an
opposite-sign pair contributes zero. Therefore Q=0 proves equality of
all distance multiplicities. The retained tree has `3b-1` vertices, so
each set has `(3b-1)/2` vertices. Restoring the two terminal middle-arm
vertices does not change distances between retained vertices. This proves
the conjecture.

The earlier partial `b=2d+3` tables and bounded sign search were discovery
tools; the implementation replaces them with this all-parameter construction.
No timeout, failed restricted template, or finite census is used as proof.
