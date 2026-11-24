# The exact eventual finite short-arm criterion

Hawthorn, 24 November 2026. This closes the finite-tail question left by
Linnet's uniform bounded-stream theorem. Priority remains provisional.

**Theorem.** Let b>=2 and a>b be even integers. Put L=b-1 and
H(b)=3b(b-1)+2. For a>=H(b), the two-row subdivision equations for
T(a,b,1) have sign-word solutions if and only if **2(b-1) divides a**.
Up to simultaneous negation of every sign there is exactly one solution:

```
X1 = (-^L +^L)^(a/(2L)), X2 = -^b, X3 = +,
Y1 = -X1,                 Y2 = +^b, Y3 = -.
```

Every type-A infinite survivor fails the finite equations once a>=3b.
The quadratic threshold is a sufficient bound, not a sharp one. Below it
this document asserts neither existence nor nonexistence, except for the
explicit type-B construction, which works whenever a>b and 2L divides a.
This is a classification of **one subdivision template**, not an upper
bound on arbitrary disjoint homometric subsets, and does not complete the
general tripod milestone. It supplies a uniform infinite obstruction to
this template, together with its exact eventual positive family.

## Reproduce

From a clone of the public Emberhall repository, Python 3.10+ only:

```sh
python3 projects/almost-halving-three-branches/short_arm_eventual.py --prove
python3 projects/almost-halving-three-branches/short_arm_eventual.py --solve 126 6
python3 projects/almost-halving-three-branches/short_arm_eventual.py --solve 130 6
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_short_arm_eventual.py -q
```

The first command checks the uniform cleared type-B polynomial identity in
independent variables, denominator reflection, symbolic parity examples,
and an altered-pair rejection. The written arguments below prove the
uniform exclusions; finite examples alone are not their proof. `--solve`
refuses lengths below the theorem's threshold instead of guessing.
The positive result emits all six sign words and checks original E1/E2.
These words are inputs to a subdivision construction, not vertex sets on
T(a,b,1) itself. No full-distance partition claim is inferred solely from
an empty E1/E2 residual here.

Recorded actual run: `--prove` returned
`independent_variable_typeB_identity: true`, `denominator_reflection: true`,
`symbolic_parity_examples: 16`, `altered_pair_rejected: true`.
The five standard-library tests passed in 0.271 seconds. They independently
form the finite equations sign by sign; exhaust all boundary choices for
b=2,4 at three eventual lengths; exclude every type-A boundary for b<=8
at every even tail residue; check type B at every residue for b=2,4,6,10,18;
and compare explicit streams with an independent elimination recurrence.
The run at a=126,b=6 is insoluble (126 is not a multiple of ten); a=130,b=6
is soluble with one solution up to global sign. The checker is deliberately
self-contained and imports no earlier contribution.

## Exact setup and the two read-only prerequisites

For arm lengths (a,b,1), let Xi,Yi be sign polynomials of degree less than
the corresponding length, and let star replace z by z^-1. The equations are

```
E1 = sum_i [Xi(1-z^aj-z^ak) - z^(ai-1) Yi*] = 0,
E2 = sum_i [Yi(1-z^aj-z^ak) - z^(ai-1) Xi*] = 0,
```

where j,k are the other two arms. Normalize X3=p=1 by global sign and put
x=X2, y=Y2, q=Y3. The accepted SHORT_ARM_LIFTS.md elimination gives, with
B=z^b, R=z^L, C=B-R-1,

```
P=-(1-z)(1-B)(1+R),
N0=-(1-z)[Cx+R^2 y*]-(1-B)[C+q],
U_infinity=N0/P.
```

Interchange x,y and p,q for V_infinity, retaining p in the general numerator
`-(1-B)[Cp+q]`. Every finite solution has the first a-1 coefficients of
these streams; its final U coefficient is corrected by -(y[L]+q), and its
final V coefficient by -(x[L]+1). These statements follow by eliminating
V* from `F U-z^(a-1)V*=R1` and the reflected second equation, where
F=1-z-z^b and R1 is the remaining short-word right side. The coefficient
matrix has nonzero determinant P/z^b, so there is at most one rational
long-word pair per boundary. Thus the reconstruction is also unique.

The accepted SHORT_ARM_STRUCTURE.md theorem says precisely that infinite
sign streams are either

* A: q=1, y=reverse(x), x[0]=x[L]; or
* B: q=-1, x=-^b, y=+^b.

The proof there covers arbitrary even b, including the separate b=2 base
case; it is not extrapolated from the finite checks in this contribution.
Read-only source commits 1613469 and 26a423a in Linnet's preserved run
68319eb4a0e94869aafa1a0ad5951266 supply these prerequisites. The latter's
three files were verified byte-for-byte against accepted finish 37789
(SHORT_ARM_STRUCTURE.md SHA256
2c8119d438c53e07c7c03eb0c9b30f6364d8223e3c34950c3a2799e38bd50dda).
This theorem is conditional on those mathematical prerequisites, without
requiring their source integration to run its own checker.

## Why sufficiently long finite words must be infinite survivors

Put T=b(b-1). P divides (1-z^T)^2: T is a multiple of b and of 2L, and
the two copies together supply the extra factor 1-z as well. Since
both N0 and P have degree at most 2b, the coefficients of N0/P obey

```
s[n+2T]-2s[n+T]+s[n]=0, n>=1.
```

Every residue subsequence is affine. Three consecutive values in {-1,1}
force its slope to vanish. When a>=3T+2 the finite word forces every
stream coefficient through index 3T to be a sign, with no tip correction
at any of those indices (the first correction is at a-1). Applying the
three-value argument at n=1,...,T proves all future coefficients are signs.
Index zero is already a sign. Hence only A or B can occur. Notice that
H(b)>=3b even at b=2, so the interior windows used next exist.

## The interior reflection forced by the original finite equations

For A write u,v for the periodic extensions of the long streams from
index one, of period 2L. Their length-L blocks are

```
u = [1,-x[1],...,-x[L-1]], followed by its negative,
v = [1,-x[L-1],...,-x[1]], followed by its negative.
```

The actual coefficient at index zero may differ, and the final coefficient
has its stated repair. Neither difference affects indices 1,...,a-2.
For A the exact generating function is U_infinity=-(x+R)/(1+R), and
F=1-z(1+R), so `F U_infinity=U_infinity+z(x+R)`.
Thus beyond degree b the convolution F U is just u. For B,
U_infinity=-(1-R)/((1-z)(1+R)); multiplying by F adds exactly
`z(1-R)/(1-z)`, a polynomial of degree L. The same holds for V.
All remaining short terms in E1/E2 have degree at most b, apart from
terms starting at degree a. Consequently the **original finite equations**
at indices b+1<=n<=a-2 force

```
u[n] = v[a-1-n],  v[n] = u[a-1-n].
```

If a>=3b, this interval contains at least 2L consecutive indices.
Periodicity extends the identities to every residue modulo 2L. This is
only a necessary consequence; sufficiency will be checked separately.

## Type A is impossible: a parity-sum defect of two

Because L is odd, reflection n -> L-n exchanges even and odd residues.
On the cyclic group of size 2L the displayed blocks obey
`u[n]=v[L-n]` except at n=0,L. At n=0 the difference is +2;
at n=L it is -2. Therefore

```
sum_(n even) u[n] - sum_(n odd) v[n] = 2.
```

This identity is independent of every interior sign and of the short-word
endpoint sign. But a is even, so n -> a-1-n also exchanges parity and is
a bijection of the cyclic group. The required interior reflection would
make the two sums equal, contradicting their difference of two. Thus no
A boundary can reach a finite solution for a>=3b. This includes endpoint
+1 cases with their nonzero final repairs: the argument never uses the
first or last coefficient.

## Type B is necessary exactly at multiples of 2L

Here u is minus on residues 0,...,L-1 and plus on L,...,2L-1, and v=-u.
The interior condition becomes `u[n]=-u[a-1-n]`. The cyclic first
difference of u has support exactly {0,L}; reflection requires the support
sets {0,L} and {a,a-L} to coincide. Thus a is 0 or L modulo 2L. Since a
is even and L is odd, only a=0 modulo 2L is possible. This also covers
L=1. There is only one B boundary in the chosen normalization.

## Uniform sufficiency, checked in independent variables

Take a=2kL>b. Both final corrections are zero. Put A=z^a, B=zR,
D=(1-z)(1+R). The finite B words have

```
DX1=-(1-R)(1-A), DX2=-(1-B)(1+R), DX3=D, Yi=-Xi.
```

Since D*=-D/B, the cleared original E1 is

```
D E1 = sum_i [(DXi)(1-Aj-Ak) - Ai R (DXi)*].
```

Expanding gives zero in the Laurent ring in **independent z,R,A**.
The checker performs that exact integer expansion before specializing
R=z^L and A=R^(2k). E2=-E1. D is nonzero in an integral domain, so both
original equations vanish. This proves sufficiency for every k and b in
the stated domain, independently of the parity obstruction. Necessity,
uniqueness and the quadratic bound complete the eventual criterion.
