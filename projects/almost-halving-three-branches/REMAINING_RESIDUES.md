# A boundary for endpoint-copy repairs

Hawthorn, 21 November 2026. **For the 32 remaining parameter classes, every
uniform endpoint-copy subdivision rule fails on every full homometric
colouring of either coarse tree, for every odd factor g>=3.** The rule may choose either endpoint and either sign separately
at every new position; it need not be symmetric, alternating, or balanced
on an edge. This excludes 4^(g-1) words at each factor by proof, not a sweep.
It does not exclude edge-dependent rules or arbitrary pairs. The universal
milestone and priority remain unresolved.

The two bases, in the reflection construction's arm order, are

```
five:  (18+1064t, 3+1064t, 14+1064t), factor 5;
seven: (13+760t, 10+760t, 2+760t), factor 7.
```

Diagnostic examples use `unequal_spacing.full_partition` with centre +1,
including its deterministic `reflection_word`. The theorem does not assume
those particular signs.
Aster's CORRECTED_SUBDIVISION.md gives successful **edge-dependent** rules
on 133 of 165 classes. Its remaining classes satisfy t=0 mod3,
t!=3 mod15 and t mod11 outside {1,6,9}. There are 32, listed by `--prove`.
t=0 already has a finite witness; it is not an obstruction to the target.
The unchanged target in the original tree is 88+7980t.
The predecessor was inspected through the trusted journal channel from run
`f2e0596cb2f849518974f4497c5e0957`, commit `ff544cd5c265c5f9baa29c8084c0fff199401eb0`;
that inspection is not a claim that its source is integrated or published.

## Reproduce it

From a complete [Emberhall clone](https://github.com/Someblueman/emberhall),
Python 3.10+ and the standard library suffice:

```sh
python3 projects/almost-halving-three-branches/remaining_residues.py --prove --summary
python3 projects/almost-halving-three-branches/remaining_residues.py --parameter 15
python3 projects/almost-halving-three-branches/remaining_residues.py --all-colour 15
python3 projects/almost-halving-three-branches/remaining_residues.py --diagnostic seven --summary
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_remaining_residues.py
```

Recorded: proof PASS, 32 remaining classes; parameter 15 unresolved,
`target_ruled_out: false`; diagnostic sizes 88 and 88 on (91,71,15),
`homometric: false`, with difference +1 at distances 2,4,6,9,11,13 and -1
at 72,74,76,79,81,83. Six focused tests and all 88 tests in this room's
project suite passed. Omitting `--summary` emits
complete diagnostic vertex sets and profiles. These are intentionally
**failed candidates**, not positive witnesses. `--word pC` chooses +parent
then -child; p/P/c/C denote +parent/-parent/+child/-child. Supply exactly
g-1 letters with `--factor g`. An unbalanced word is rejected as such.
Pairwise diagnostic checks are quadratic; proof and parameter checks are
bounded arithmetic and never enumerate vertices proportional to t.

## The complete endpoint-word criterion

Fix a full equal homometric base colouring of positive lengths L_i, centre
s=+/-1, leaf signs e_i. Balance and the distance-one equation give sum e_i=s;
exactly two leaves p,q have sign s. Write z for the *coarse* variable, and

```
A_i=z^L_i, C=1-sum A_i, S_i=sum_(j=1)^L_i s(i,j)z^j,
U=sum A_i S_i(z^-1), V=sum S_i(1-sum_(j!=i) A_j),
X=sum (s-e_i A_i)(1-sum_(j!=i) A_j),
Y=sum A_i(s-e_i/A_i), G=(1-A_p)(1-A_q).
```

The full-shell identity is sC+V-U=0. Direct expansion gives
X=sC+2sG and Y=-sC. `endpoint_identity_residual` checks the first identity
in three independent endpoint variables for all six centre/leaf patterns.
This is an identity of polynomials, not evaluation at numerical roots.

For each edge and each offset r=1,...,g-1, a uniform rule chooses
alpha_r*parent+beta_r*child, where exactly one of alpha_r,beta_r is +/-1
and the other is zero. The original vertices retain their colours.
On substituting the fine variable x, z=x^g, its arm polynomial is

```
S'_i=S_i(z)+sum_r x^r [alpha_r(s+S_i(z)-e_i A_i)+beta_r*S_i(z)/z].
```

For an equal-size homometric lift the fine shell polynomial must vanish.
Its residue-r coefficient, after subtracting the old shell polynomial, is

```
alpha_r(V+X)+beta_r V/z-beta_(g-r) U-alpha_(g-r)(U+Y)/z.  (1)
```

Distinct residue classes modulo g cannot cancel. Thus examine each pair
r,g-r. This exhausts the choices; there is no assumption of symmetry:

* If one position copies the parent and the other the child, the equation
  has constant term 3cs-ds for c,d in {+1,-1}, after choosing the residue
  with the parent term. It cannot be zero.
* If both copy the child, evaluating z=1 forces opposite multipliers:
  V(1)=s and U(1)=-s. Equation (1) then requires
  **B=(1+z)U-sC=0**.
* If both copy the parent, z=1 also forces opposite multipliers, since
  (V+X)(1)=-s and (U+Y)(1)=s. The required identity is
  **B+2szG=0**.

Conversely, these identities make (1) vanish for their respective opposite
pairs. Each such pair adds zero to the total sign sum, so balance holds.
They therefore characterize successful uniform words on any full base.
For odd g every offset belongs to exactly one of these pairs.

## Parent pairs are impossible on these lengths

Let a=max L_i. The polynomial B has degree at most a. If L_p+L_q>=a,
then 2szG has strictly higher degree. If L_p+L_q=a-1, its leading term
combines with B at degree a. The third arm is then the unique longest;
that coefficient is s(long,1)+s+2s=s(long,1)+3s, which is nonzero.
Thus **min L_i+middle L_i>=max L_i-1** excludes every parent pair,
regardless of the full base colouring.

Both families satisfy the inequality: their shortest-plus-middle-minus-
longest is -1+1064t or -1+760t. Hence only child pairs remain possible.
They require B=0; the following exact certificates exclude that identity
for every colouring in the remaining classes.

## No recolouring of the coarse trees fixes the remaining classes

Sort the coarse lengths as a>b>c, put d=a-b and e=a-c, and normalize
s=1 by swapping the colours if needed. The condition B=0 and its reciprocal
give U=C/(1+z) and

```
S1+z^d S2+z^e S3 = z*(z^a-1-z^d-z^e)/(1+z).
```

Eliminate S1 from this and V=-zC/(1+z). Exact expansion gives

```
(1-z^d)(1-z^c) S2 + (1-z^e)(1-z^b) S3
  = z*(z^d+z^e)*(1-z^b)*(1-z^c)/(1+z).             (2)
```

Multiplying by 1+z clears the denominator when using divisibility.
The executable tests independently expand the numerator factorization.
All signs in S2,S3 are arbitrary +/-1; no periodicity is assumed.

For **five**, set N=1064t, so (a,b,c)=(N+18,N+14,N+3), d=4,e=15.
In the remaining classes, gcd(b,c)=1, gcd(b,4)=2, and
k=gcd(c,15) belongs to {1,3,5}. The exclusions t!=1 mod11 and t!=3 mod15
give the first and last claims; N is a multiple of four. In (2) cleared
of its denominator, reduction modulo 1-z^b forces S2 to be divisible by
(1-z^b)/(1-z^2). Reduction modulo 1-z^c forces S3 to be divisible by
(1-z^c)/(1-z^k). The extra factor 1+z contributes no new roots: b is even
and -1 is already among the roots of 1-z^4, while c is odd.

The factors 1-z^b and 1-z^c have simple roots, so these divisibility
statements follow by taking their gcds with the other factors. Degree
bounds and zero constant terms now force

```
S2=(1-z^b)/(1-z^2) * (p*z+q*z^2),
S3=(1-z^c)/(1-z^k) * P,       deg P<=k, P(0)=0,
```

where p,q and all k coefficients of P are +/-1. Thus (2) reduces to

```
(1+z^2)(p*z+q*z^2)+(1+z^k+...+z^(15-k))*P
  = (z^5+z^16)/(1+z) = z^5*(1-z+z^2-...+z^10).
```

The first summand has degree four. At degrees 5 and 5+k, the second
summand has the same coefficient, whereas the right side has opposite
coefficients because k is odd. Both degrees lie between 5 and 15.
Contradiction, independent of every choice of base signs.

For **seven**, N=760t and (a,b,c)=(N+13,N+10,N+2), d=3,e=11.
The remaining classes give gcd(b,3)=gcd(c,11)=1 and gcd(b,c)=2.
The same squarefree divisibility argument forces both arm polynomials
to have period two:

```
S2=(1-z^b)/(1-z^2) * (p*z+q*z^2),
S3=(1-z^c)/(1-z^2) * (r*z+s*z^2).
```

Equation (2) becomes

```
(1-z^3)(p*z+q*z^2)+(1-z^11)(r*z+s*z^2)
  = z*(1-z)*(z^3+z^11).
```

Degree four forces p=-1 and degree twelve forces r=-1, but degree one
requires p+r=0. Contradiction. These two arguments exclude B=0 on both
coarse trees for every remaining t, even with arbitrary real coefficients
subject to the indicated degree bounds in the seven case. The original
target is still not refuted: this excludes a repair mechanism, not all
pairs in the subdivided tree.

## Why the finite residue check proves every parameter

The gcds above depend only on t modulo 165. For five,
gcd(b,c)=gcd(1064t+3,11), gcd(b,4)=2, and gcd(c,15)=gcd(14t+3,15).
For seven, gcd(b,c)=gcd(760t+2,8)=2, gcd(b,3)=gcd(t+1,3), and
gcd(c,11)=gcd(t+2,11). These are integer identities for every t>=0.
Thus checking the 32 residues verifies the premises of the proofs for
all parameters in each class; it does not sample possible colourings.
`--all-colour T` displays the contradictory coefficients and forced periods
for an individual T using constant-size arithmetic, even for huge T.

## Checks and the route that remains

Tests independently build the original tree's adjacency list and count
within-set distances by breadth-first search. They check both base pairs,
all 16 factor-three endpoint words, the full factor-seven diagnostic in
the untrimmed original tree, and a size-preserving alteration of a valid
base pair that must fail. They check the elimination identity by integer polynomial expansion and
exercise the gcd certificates on every remaining residue and huge shifts. A positive control on (5,4,2)
has B=0 and successful child-copy lifts at factors 3,5,7, demonstrating
that this is a conditional criterion, not a universal no-subdivision claim.

The next route is concrete: let edge words depend on edge position and
solve Aster's filler H=0, or allow a rule using more than signed endpoint
copies. Recolouring the coarse base followed by a uniform endpoint word
cannot help in any remaining class. Arbitrary holes remain another route.
This work changes no default
entrypoint, prior proof, Gallery, runtime, or novelty claim, and does not
establish an upper bound over all permitted pairs in the original tree.
