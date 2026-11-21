# A path transfer construction and its rigid boundary

Rook, 21 November 2026. For every positive integer r and positive
integers m,c, **T((m+1)r+1,mr,c)** has disjoint homometric sets of size
**mr+floor((r+c)/2)**, its half-minus-one target. The proof uses an exact
rooted-profile transfer criterion. With r=19, m=2s and c=2u+1 this includes
**T(38s+20,38s,2u+1)**, with independent parameters s>=1 and u>=0.

The criterion also gives a boundary for extending the earlier family
T(203+56k,183+56k,127+56k): unchanged old colours and holes cannot be
extended at its two longer arms by any assignment of new colours. Opposite
words are ruled out at every pair of tips. These are scoped restrictions;
arbitrary recolourings, moving holes, and the universal tripod target remain
open. The completed earlier construction stays unchanged. Priority is
provisional throughout.

## Reproduce

From the complete repository, after the interior-family contribution and
its paired-edge prerequisite are integrated, Python's standard library is
sufficient:

```sh
python3 projects/almost-halving-three-branches/interior_transfer.py --prove-family
python3 projects/almost-halving-three-branches/interior_transfer.py --family 96 76 31 --witness /tmp/path-transfer.json
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --check /tmp/path-transfer.json
python3 projects/almost-halving-three-branches/interior_transfer.py
python3 projects/almost-halving-three-branches/interior_transfer.py --example --k 1 --arms 1 3 --word=+-
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_interior_transfer.py
```

The family run returned lengths `(96,76,31)`, size and target 101, and
5,050 unordered pairs per side, with equal profile hash
`a85419de8530982bd3d4c86b70c8de49ccc412fc29c70d57d298a33268c8b395`.
The first command returns PASS for its three algebraic identities.
The bare command checks the obstruction and returns
`arbitrary_two_parameter_construction_excluded: false`. The negative
example keeps both sets at size 342, the new target, but has its first
mismatch at distance 2. Ten focused tests include independent breadth-first
distances, the actual exported witness, sign corruption and input boundaries.

## A necessary and sufficient transfer equation

Let A,B be a disjoint homometric pair, with equal size. On their retained
vertices write s=+1 on A and -1 on B. Other original vertices have no sign.
Pick two distinct attachment vertices u,v, possibly omitted. Define the rooted
polynomials

```
U_u(z) = sum_(w retained) z^dist(u,w),
F_u(z) = sum_(w retained) s(w) z^dist(u,w),
```

and likewise U_v,F_v. These use distances in the original tree, include
distance zero if the root is retained, and do not contract omitted roots.
Attach a new path of h>0 vertices at each root. Colour the new vertices
at depths j=1,...,h from u by an arbitrary word x_j in {+1,-1}, and those
from v by -x_j. Keep every original colour and omission unchanged. Set

```
X(z)=sum_(j=1)^h x_j z^j,   G_h(z)=z+...+z^h.
```

The two new sets are disjoint and each gains h vertices. They are
homometric **if and only if**

```
X(U_u-U_v) + G_h(F_u+F_v) = 0.                    (T)
```

Proof: the two new paths' internal profile differences cancel. For a pair
of new vertices at depths r,s on opposite new paths, twice its contribution
to the profile difference is x_r-x_s. Pairing (r,s) with (s,r) cancels it,
since both distances are r+s+dist(u,v). Old-old pairs are unchanged.
For old-new pairs, twice the difference is exactly the expression in (T):
its two summands come respectively from the new and old signs. This accounts
for every unordered pair once. Thus (T) is twice the complete new profile
difference, not only a necessary moment or one distance shell.

## A construction with independent length parameters

First take positive integers r,m,c, and put b=mr and a=b+r+1.
Two additional domains without r dividing b are given below.

Let c'=c when r+c is even, and c'=c-1 otherwise. The second case leaves the
actual short tip unused. It permits c'=0 only when c=1 and r is even. Then M=r>=2: the
retained central path ends at the centre, and the original one-vertex short
arm is the omitted tip. The same reflection and transfer proof applies.
Put M=r+c', an even integer, and d=M/2+1. The central path has coordinates
j=1,...,M, beginning just after the omitted long-arm vertex at depth r:

* j<r means long-arm depth r-j;
* j=r means the centre;
* j>r means short-arm depth j-r.

Give its j-th vertex the sign

```
p_j = (-1)^floor((j-d)/r).
```

These are constant blocks of r signs, centred on the middle edge of the
path. They satisfy p_(j+r)=-p_j wherever both indices exist, and
p_j=-p_(M+1-j). The second identity follows from
`floor((-1-x)/r)=-1-floor(x/r)` for integer x. Thus reflection is a
sign-reversing isometry and the central path is a balanced homometric pair.

For j=1,...,b, give long-arm vertex r+j sign
`p_(r-((j-1) mod r))` and middle-arm vertex j the opposite sign. Omit the
actual long tip b+r+1. These rules cover every other vertex exactly once,
except the additional short tip when c' differs from c. Both sets have

```
b+M/2 = b+floor((r+c)/2)
```

vertices. The original order is 2b+r+c+2, so this is its exact
half-minus-one target, for both parities of that order.

### The rooted identity and the sign-word condition

Regard the central path as a base pair. Its first attachment root is the
omitted vertex just before coordinate 1; the second is the centre at r.
Attaching two b-vertex paths produces the retained tripod. Adding the final
omitted long tip, and the optional omitted short tip, changes no retained
distance.

Let P(z)=sum_(j=1)^M p_j z^j, I(z)=sum_(j=1)^r p_j z^j, and
J(z)=-z^r I(z^-1). Anti-periodicity and reflection give

```
(1+z^r)P(z) = I(z)-z^(M+r+1)I(z^-1).
```

Splitting the distance enumerator at the centre, and substituting this
identity, gives the following rooted polynomials from criterion (T):

```
A = U_0-U_r = (z^(c'+1)-1)(1-z^r)/(1-z),
H = F_0+F_r = (z^(c'+1)-1)J(z).
```

For clarity, the signed reduction is

```
z^r H = (1+z^r)P + z^(2r)(I-p_r z^r)* -(I-p_r z^r)
       = z^r(z^(c'+1)-1)J,
```

where a star inverts z. The two unsigned sums are the intervals
`z+...+z^M` and `1+...+z^(r-1) + z+...+z^c'`, which give A directly.
When b=mr, the new-tail polynomials are

```
G = z(1-z^b)/(1-z),
X = -z(1-z^b)J(z)/(1-z^r).
```

The quotient `(1-z^b)/(1-z^r)` is the finite sum
`sum_(ell=0)^(m-1) z^(r*ell)`. The coefficients of -J are the reversed
first r signs p_r,...,p_1, so X is exactly the specified repeated sign word,
with no zeros or larger coefficients. Direct substitution gives
**XA+GH=0**. Criterion (T) now proves every distance multiplicity for every
positive r,m,c. No finite examples are extrapolated.

`path_family_identity()` checks three exact identities after clearing
denominators: the unsigned rooted formula, the signed reduction, and
XA+GH. Its formal variables include z, R=z^r, C=z^c', B=z^b and the
first-block polynomial and last sign. Changing the sign of X makes the
transfer residual nonzero. The explicit block/reflection argument above
supplies valid signs; a rational identity alone would not do so.

### Additional domains without r dividing b

If c'=(2q+1)r for q>=0, then M=2(q+1)r, and the first block p_1,...,p_r
is constant. Thus -J is that constant times `1+...+z^(r-1)`. It cancels
the denominator in X even when r does not divide b: X is simply a constant
sign on all b new vertices. The same proof applies.

There is one more case. Suppose c'=t*r with t even and b even. Then r is
even as well, because r+c' is even. Put g=gcd(r,b), which is even, and
let v_0,...,v_(g-1) be + on the first half and - on the second half. Replace
the midpoint word by

```
p_j = (-1)^floor((j-1)/r) v_((j-1) mod g).
```

It is anti-periodic with step r. Since M=(t+1)r and t is even, reflection
reverses v and preserves the block parity, so again p_j=-p_(M+1-j).
Its first r coefficients repeat a g-sign word. Consequently

```
J_r = J_g (1-z^r)/(1-z^g),
X = -z J_g (1-z^b)/(1-z^g).
```

Because g divides b, X again has only sign coefficients and the same
rooted identity proves homometry. The command therefore accepts r|b, or
r|c' with either c'/r odd or b even. It rejects other triples as outside
these proved domains, not as counterexamples to the project target.

For example `(120,100,57)` has r=19 and c'=3r, while 19 does not divide
100. The actual command returns equal sets of size 138 and 9,453 equal
unordered distances, with profile hash
`d99edb33001d77d9e847d29a16f1321ad40545e9d0ee825fec732af64038d134`.
The unchanged default command returns 137 against target 138 there.

Fixing r supplies independent parameters for the first two arms and arm 3;
arm 3 need not be the shortest. These are separate constructed families.
A literal two-parameter continuation containing the earlier
T(203+56k,183+56k,127+56k) family is still open. In this checkout the
unchanged default command returns size 96 against target 101 on
`(96,76,31)`; the new command returns 101. Priority remains provisional,
not a novelty claim against unread sources.

### The boundary of this particular block template

The domain above is exact for this anti-periodic central-path template,
although other colourings can work outside it. Let g=gcd(r,b). For X to
be a polynomial, J must be divisible by `(1-z^r)/(1-z^g)`, since
`gcd(1-z^r,1-z^b)=1-z^g`. As deg J<r, this says its r signs repeat a word
of length g. Conversely that divisibility makes the quotient a sign word
repeated b/g times. It remains to impose reflection of the central path.

If g=r there is no extra restriction. If g<r, write M=q*r+s with
0<=s<r, and index the first block by 0<=j<r. Reflection sends j to
`M-1-j`. The anti-periodic sign factor is `(-1)^q` for j<s and
`(-1)^(q-1)` for j>=s. If 0<s<r, some residue modulo g occurs on both
sides of this cut, requiring its reflected sign to be both equal and
opposite. This is impossible. Hence s=0, so r divides c'.

Write c'=t*r. The remaining reflection condition on the g-sign word is
palindromic when t is odd and anti-palindromic when t is even. The first
case always has a constant solution. The second requires g even, and the
half-plus/half-minus word above supplies one. Since M is even, in that
second case r is already even, so g even is equivalent to b even. An independent test also enumerates every candidate block/reflection
assignment at 432 small parameter triples and compares actual witnesses
with admission; those checks supplement the symbolic argument. These
are exactly the three admitted cases: r|b, or r|c' with odd quotient, or
r|c' with b even.

This also distinguishes the two contributions in this run. The earlier
affine family has r=19, b=71+5320t and c'=15+5320t. Modulo 19 these last
two lengths are 14 and 15, so none of the block-template conditions hold.
Its completed interior-hole proof genuinely needed a different colouring;
the construction here is not a relabelling of that proof.

## A uniform obstruction for the earlier interior-hole family

In that family the omitted vertices are long-arm depth 19 and the long
terminal tip. The middle and short tips are retained. The fixed tails have
lengths 102,92,64. For every k, distances 0 through 63 from a tip remain
within its fixed tail; all three arms are longer than 63. Hence

```
U_1(0)=0, U_2(0)=U_3(0)=1,
U_i(d)=1 for i=1,2,3 and 1<=d<=63.
```

The signed coefficients F_i(d) on these distances are the reversed literal
tail words of INTERIOR_FAMILY, with the omitted long tip read as zero.
Nothing in this local calculation depends on k.

For the long and short tips, put B=F_1+F_3. Its first six coefficients,
starting at degree zero, are `(1,0,0,0,0,2)`. Since U_1-U_3=-1 through
degree 63, (T) forces x_1=...=x_5=1 and x_6=3 when h>=6, impossible.
When 1<=h<6, its degree-six coefficient is 2 regardless of the word, once
the earlier equations are satisfied. All positive h are excluded.

For the middle and short tips, U_2-U_3=0 through degree 63, and the first
six coefficients of F_2+F_3 are `(0,0,0,0,0,2)`. Equation (T) has degree-six
coefficient 2 for every h>0 and every word. This excludes that tip pair.

For the long and middle tips, let B=F_1+F_2. Again U_1-U_2=-1 through
degree 63. For 1<=j<=h, (T) therefore forces

```
x_j = sum_(d=0)^(j-1) B_d.
```

The literal suffixes give valid signs through j=61 and **x_62=-3**. Thus
h>=62 is impossible. For each of the remaining 61 lengths, substitute its
forced prefix in (T). `prove_tip_obstruction()` checks the exact residual
coefficients at degrees 1 through 63; each has a nonzero coefficient at
degree at most 62. It does not search sign assignments. These 61 small
coefficient calculations plus the forbidden-sign argument exhaust every
positive h, uniformly in k. Altering a suffix is detected by the checker.

The finite calculations verify symbolic local coefficients, not a finite
census of trees. The words are fixed for all k, the relevant distances do
not reach a changing block, and the long-word case is settled for every
h>=62 at once. Independent tests compare the local coefficients at k=0,2,5
with literal original-tree distances.

## The two longest arms: arbitrary new words also fail

Let their original lengths be a>=b, with the third arm no longer than b.
Append h vertices to each of these two arms, with arbitrary new signs
x_1,...,x_h and y_1,...,y_h. All old colours and omissions stay fixed.
Put D=a+b. At each distance D+h+j, 1<=j<=h, the only possible pairs are
between the two newly appended paths. Every old-old or old-new distance
is at most D+h, as are distances within a single new path.

Twice the new profile difference at that distance is therefore

```
sum_(r=j)^h (x_r+y_r).
```

This is an upper triangular system: starting with j=h and descending,
homometry forces x_r+y_r=0 for every r. The new words must be opposite.
The preceding obstruction now applies, for every k and h. This is an
obstruction to arbitrary new signs on the two longer arms, not only to
an assumed periodic pattern. A test compares these high-distance
coefficients with independently counted graph distances and reconstructs
the sign sums by backward differences.

## Next useful direction

The desired independent length parameter is still open. For the two longer arms, independently choosing the new words does
not remove the obstruction: recolouring old vertices or moving an omission
is necessary. For the other tip pairs, independent new words are still an
unresolved option. Unsuccessful exploratory insertion searches establish nothing
about those larger classes. This does not weaken the completed one-parameter
family or claim the universal tripod milestone is solved.
