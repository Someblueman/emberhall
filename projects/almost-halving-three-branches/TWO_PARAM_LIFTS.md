# Two two-parameter full homometric subdivision families

Recovered by Linnet, 23 November 2026, from the interrupted two-parameter
contribution. This completes that contribution's proof and documentation.
The general almost-halving milestone and literature priority remain open.

For every odd `g>=3`, full equal homometric partitions exist on

1. `T(2mg,(2m-2)g,g)`, for every integer `m>=2`;
2. `T((4m+3)g,4g,2g)`, for every integer `m>=1`.

A full partition uses every vertex. Its two parts each have
`(1+sum(lengths))/2` vertices, so these families exceed the project's
half-minus-one target by one. These are exact infinite families, not a
claim about arbitrary tripods or every possible subdivision stencil.

## Run from the repository root

Python 3.10+ and its standard library suffice:

```sh
python3 projects/almost-halving-three-branches/two_param_lifts.py --prove
python3 projects/almost-halving-three-branches/two_param_lifts.py --family1 3 5 --summary
python3 projects/almost-halving-three-branches/two_param_lifts.py --family2 2 3 --summary
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_two_param_lifts.py -q
```

Recorded on 23 November 2026: the proof command reports PASS for both
families (zero E1/E2 terms), both subdivision reflection residuals have
zero terms, and every deliberate corruption has a nonzero residual.
The two example commands above respectively report `(30,20,5)`, size 28,
target 27, and `(33,12,6)`, size 26, target 25; both are homometric with
empty distance differences. All six focused tests pass.

Omit `--summary` for explicit vertex lists and distance profiles. The
result can be piped to the same command with `--check -`; altered pairs
are checked afresh rather than trusting their reported profiles.

## Coarse partition and inserted words

Start with a full partition of the coarse tree, provided by
`ratio_51_33_10.original_tree`. Its palindromic-cell theorem applies without
trimming: the cell lengths are the arm lengths plus one. For family 1,
the differences of `(2m+1,2m-1,2)` have greatest common divisor one and
its sum is even. For family 2, the same holds for `(4m+4,5,3)`.
This is the existing theorem in [RATIO_51_33_10.md](RATIO_51_33_10.md),
not an assumption inferred from finitely many coarse examples.

Write `g=2h+1`. Keep each coarse vertex's sign at depth `gk`.
For coarse edge `k=0,...,L_i-1`, insert h copies of `X_i[k]`, followed
by h copies of `Y_i[k]`. The words, ordered from the centre outward, are

```text
family 1:
X = (-^(2m), +^(2m-2), +)
Y = ((+-)^m, (-+)^(m-1), +)

family 2:
X = (--+ (+--+)^m, +-+-, -+)
Y = ((+--+)^m +--, ++++, --)
```

Each word has exactly its coarse arm's length. In both families the
three X words have total sign sum -1, and the Y words total +1.
The inserted signs therefore have total zero; the coarse partition is
balanced, so the new partition is balanced too. All vertices occur once.

## Exact parameter identities

Put `A_i=Z^L_i`, and encode the edge words as
`X_i(Z)=sum_k X_i[k] Z^k` and similarly for Y. A star inverts every
independent variable. Set

```text
E1 = sum_i [X_i(1-A_j-A_l) - (A_i/Z)Y_i*]
E2 = sum_i [Y_i(1-A_j-A_l) - (A_i/Z)X_i*],  {i,j,l}={1,2,3}.
```

For family 1 work in the Laurent ring with independent Z,M, then
specialize `M=Z^(2m)`. With `D=1-Z^2`, the exact numerators are

```text
A  = (M, M/Z^2, Z)
DX = (-(1+Z)(1-M), (1+Z)(1-M/Z^2), D)
DY = ((1-Z)(1-M), -(1-Z)(1-M/Z^2), D).
```

For family 2 specialize `M=Z^(4m)`. Put `D=1-Z^4` and
`B=1-Z-Z^2+Z^3`; then

```text
A  = (Z^3 M, Z^4, Z^2)
DX = (D(-1-Z+Z^2)+Z^3 B(1-M),
      D(1-Z+Z^2-Z^3), D(-1+Z))
DY = (B(1-M)+MD(1-Z-Z^2),
      D(1+Z+Z^2+Z^3), D(-1-Z)).
```

The checker expands `D E1` and `D E2` exactly as Laurent polynomials.
Since `D*=-Z^-d D` for `D=1-Z^d`, each reversed term becomes
`+A_i Z^(d-1)(DY_i)*` or `+A_i Z^(d-1)(DX_i)*`.
Both residuals vanish in the independent-variable ring in each family.
The ring is an integral domain and D is nonzero, hence E1=E2=0.
The displayed numerators follow directly from finite geometric sums of
the words; tests also compare every coefficient after specialization.
Changing X on the shortest arm gives a nonzero residual in both cases.

## Why this proves every odd subdivision factor

For any balanced full signed tripod, with arm sign polynomials S_i,
centre sign s0 and A_i=z^L_i, the signed shell identity is

```text
Q = s0(1-A1-A2-A3) + sum_i[S_i(1-A_j-A_l)-A_i S_i*],
(1-z) sum_(d>=1) 2(H_plus(d)-H_minus(d)) z^d = z Q.
```

Now use independent z,H, specializing `H=z^h` only at the end. Set
`W=z H^2`, `J1=z(1-H)/(1-z)` and `J2=H J1`.
The inserted arm polynomial is `J1 X_i(W)+J2 Y_i(W)`.
Reflection gives `W J1*=J2` and `W J2*=J1`, so its entire contribution is

```text
Q_inserted = J1 E1(W) + J2 E2(W) = 0.
```

The retained coarse vertices contribute `Q_coarse(W)=0`. Thus the full
lift has Q=0, and every distance multiplicity agrees. The checker verifies
both reflection identities after clearing `1-z`, in the Laurent ring
with independent z,H, and rejects a deliberate sign corruption.
This universal identity applies to both exact parameter certificates;
it does not sample h or claim that sampling proves an infinite family.

## Verification and limits

Tests independently build the original tripod adjacency graph and use
breadth-first search to recount all within-part distances. They cover
both parameter boundaries, multiple odd factors, full coverage and balance,
coefficient specialization, invalid parameters, and altered-pair rejection.
The constructor also recounts each emitted witness using the existing
independent arithmetic-distance checker. This finite verification is a
cross-check of the formulas; the Laurent identities prove the infinite claim.

The construction's recount costs quadratic time in the number of vertices.
No search or third-party dependency is required. The general project remains
open; see [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md) for priority limits.
