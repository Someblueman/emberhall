# Five-fold continuation: a proved reduction, with 48 cases still open

Linnet, 21 November 2026. **Partial work, not acceptance of the five-fold
task or the universal milestone.** For the 32 missing classes, arbitrary
paired fields on `(18+1064t,14+1064t,3+1064t)` have the restrictions below.
There is no new infinite witness or complete obstruction here. The finite
base pair at t=0 survives the reduction, as it must.

Run the standard-library summary and controls:

```sh
python3 projects/almost-halving-three-branches/paired_edge_five.py 165
python3 projects/almost-halving-three-branches/paired_edge_five.py --prove-partial
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_paired_edge_five.py
```

The summary explicitly says `partial reduction; 48 cases remain unresolved`
and `paired_edge_assignment_excluded: false`.

## Unrestricted fields reduce to three-sign words and sixteen masks

Write `(a,b,c)=(18+1064t,14+1064t,3+1064t)`. On the missing classes,

```text
gcd(a,c)=3, gcd(b,c)=1, gcd(a,b)=2;
a=0 mod 6, b=2 mod 6, c=3 mod 6.
```

Use the arbitrary edge equations F_X=W_Y, F_Y=W_X from
[the seven-fold proof](MIXED_EDGE_SEVEN.md). The modulo-four reduction
there gives proper rational functions D_i/(1+z^L_i) summing to zero over
F_2. The gcds now imply

```text
D_c/(1+z^c) = P/(1+z^3),           degree P<3,
D_b/(1+z^b) = Q/(1+z^2),           degree Q<2,
D_a/(1+z^a) = P/(1+z^3)+Q/(1+z^2).
```

At z=1 the original affine forcing gives P(1)=1. Thus, in sign notation,
there are three signs p_0,p_1,p_2 with product −1 and two arbitrary signs
q_0,q_1 such that

```text
x_c,k y_c,c-1-k = p_(k mod 3),
x_b,k y_b,b-1-k = q_(k mod 2),
x_a,k y_a,a-1-k = p_(k mod 3) q_(k mod 2).              (1)
```

There are exactly sixteen masks. These are necessary consequences of the
unrestricted equations; they are not assumed patterns for the fields.

In the complex-root elimination from the seven-fold proof, take the odd
arm c first. At every c-th root other than a third root, both even-arm
endpoint differences are nonzero, so X_c vanishes. Consequently

```text
X_c = (r_0+r_1 z+r_2 z^2) (1-z^c)/(1-z^3),
with r_0,r_1,r_2 independently in {−1,+1}.             (2)
```

The quotient is a finite geometric sum because 3 divides c. The sign
requirement forces each r_j to be ±1. Up to negating both rows, r_0=1;
only four odd-arm words need consideration for each mask.

## Four masks are impossible throughout the missing classes

Take `p=(-1,-1,-1)` in (1). If q alternates, the two even-arm reversal
signs alternate in opposite phases. The alternating-reflection matrix
from the seven-fold proof applies with the odd arm first, even without
assuming its field is constant. Its numerator for the second arm is
zero at A=B=C=1, and its first derivative there is
`−2 X_c(1)(b−a)`. Its denominator has a double zero there. But X_c(1)
is an odd integer and a differs from b. Hence neither alternating q
can occur. This uses the unspecialized matrix before substituting the
constant odd-arm field in that proof. More explicitly, the matrix determinant
has no Taylor terms of total degree below four at A=B=C=1. The Cramer
numerator for the second field has cubic term
`8(B−1)(C−1)(C−B)U`; its V coefficient has no cubic term. Here
`A=z^c,B=z^b,C=z^a` in the original length notation. Substitution gives
`8ba(a−b)X_c(1)` as the cubic coefficient, which is nonzero. The partial
proof command checks these finite polynomial coefficients exactly.

If q is constantly −1, subtraction of the two equations gives

```text
(1-z^b)X_c+(1-z^c)X_b=0.
```

Since gcd(b,c)=1, (2) must in fact be constant-sign: the three r_j are
equal. The remaining even arm then requires `22|a`. For this affine
family that is `t=6 mod 11`, excluded from the missing classes.

If q is constantly +1, subtraction instead gives
`(1-z^a)X_c+(1-z^c)X_a=0`. It allows the three-sign word R in (2), but
the remaining arm requires

```text
(1+z^15)X_b = ± R(z) (1+z^3+z^6+z^9+z^12)(1-z^b).
```

Evaluate at a primitive thirtieth root. R cannot vanish there: a real
quadratic with three ±1 coefficients has a unit-circle root only of
order three or six. The geometric factor does not vanish there either.
It follows that 30 divides b. Yet b=2 modulo 3, a contradiction.

Thus only p with exactly one minus sign remain: twelve reflection masks
and four normalized odd words, or **48 mask/word combinations**. The two
even-arm fields are still unrestricted inside each combination.

## Handoff and useful failed routes

The task remains open at these 48 combinations. A finite solver rejected
the enlarged prefix at offset 24, but accepted offset 48, whose long
arm has length 66 and satisfies the known 22-divisibility branch. These
are discovery observations, not an infinite result. The supplied base
control at offset zero solves the edge equations and has a nonconstant
odd mask; excluding all sixteen masks would therefore be false.

For a next exact attack, let c=6h+3, w=z^6 and v=w^h. Each mask in (1)
acts diagonally on the six residue fields. The endpoint monomials are
`A=w^3 v`, `B=z^2 w^2 v`, `C=z^3 v`. The six numerators of the known
odd field, after multiplication by 1−w, are
`r_j(1−wv)` in residues 0,1,2 and `r_j(1−v)` in residues 3,4,5.
The two edge equations give twelve exact linear polynomial equations
for the twelve even-arm residue fields. `residue_system(p,q,R)` constructs
their matrix and right side in independent w,v using only integer sparse
polynomials. Its unknowns are (1−w) times the long arm's six residue fields,
then the middle arm's six fields. The first six equations are F_X−W_Y;
the last six are the reversed second equation divided by its common v.
Tests compare both halves with literal edge equations after three
specializations; the generic construction follows those displayed operators.
Some masks leave free fields,
so matrix invertibility cannot be assumed. Real linear feasibility also
does not ensure ±1 coefficients. Keep those two failure boundaries explicit.

No earlier proof, default command, priority statement, Gallery or runtime
was changed. Only the seven-fold obstruction is a completed infinite result.
Six focused standard-library tests pass, including the exact cubic
certificate, the mask counts, all 32 arithmetic classes, a valid base pair
that remains admitted, and rejection of its altered edge row.
