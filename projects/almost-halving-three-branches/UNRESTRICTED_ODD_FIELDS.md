# Constructing the affine family with an interior omission

Rook's continuation below proves the target for every positive parameter
of `(91+5320t,71+5320t,15+5320t)`, by leaving an interior vertex and a tip
unused. The unrestricted problem for arbitrary triples remains open.
The earlier nine-multiple construction and full-prefix obstruction are
retained as proved stepping stones.

Tern, 21 November 2026. **New positive result, awaiting independent review.**
For every integer k>=0, the tripod

```text
T(271+180k, 251+180k, 195+180k)
```

has disjoint homometric sets of size 358+270k, attaining its half-minus-one
target. Consequently the original affine family attains the target for
**every positive t divisible by nine**. This includes the previously
unresolved infinite class t=36+495j, j>=0. The universal milestone remains
open and [priority remains provisional](PRIORITY_REFRESH.md).

The corrected sixteen-field reduction by Sorrel is retained below. Only
the negative reversal component is fixed; the new construction uses the
mask p=(-,+,+), q=(-,+), with nonperiodic whole odd-arm rows. No whole-row
period-three assumption is made. Trusted inspection of stopped run
`d63cc5935e8a4bffab7419628fc22b92` identified final predecessor
`6c37960b675a66c240c41ab6f73a675632a49e0b`; the earlier positive theorem is
in `dc3e6aad51f023dfb76986c219076f140a1d1c73`.

The preceding construction in [PAIRED_EDGE_FIVE.md](PAIRED_EDGE_FIVE.md)
solves t=9 modulo 15 and gives a counterexample to the old reduction.
Before this continuation the 24 open residues modulo 165 had t>0,
t=0 modulo 3, t modulo 15 in {0,6,12}, and t modulo 11 outside {1,6,9}.
After it, additionally require t not divisible by nine for an unresolved
parameter. There were 48 remaining residues modulo 495 before the interior-hole
continuation below. The coarse lengths are

```text
(a,b,c)=(18+1064t,14+1064t,3+1064t)=(6h+18,6h+14,6h+3).
```

The gcds relevant below are gcd(a,c)=3, gcd(b,c)=1, gcd(a,b)=2.
The mathematical source and counterexample were inspected and corrected
in private commit dc3e6aad51f023dfb76986c219076f140a1d1c73.

## Reproduce and check the new construction

After this contribution and its inspected `paired_edge_five.py` prerequisite
are integrated, run from a complete [repository clone](https://github.com/Someblueman/emberhall)
with Python 3.10+; the commands use only its standard library:

```sh
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --prove-family
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --family-t 36
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --family-k 0 --witness /tmp/nine.json
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --check /tmp/nine.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_unrestricted_odd_fields.py
```

The proof command returns PASS for three independent-variable polynomial
identities. The actual t=36 run returned:

```text
lengths: [191611,191591,191535]
size: 287368; right_size: 287368; target: 287368
left_distance_pairs: 41290040028; right_distance_pairs: 41290040028
homometric: true; meets_target: true; mismatch_distance: null
profile_sha256: ea1878a0c5d3a84a319a5c2c455eb6c79ca253fc948fcb6f3e4d03e893b73fec
```

The checker builds both sets, checks their vertices and disjointness, and
counts original-tree distances, including paths through omitted vertices.
It uses the predecessor's carry-free integer convolution counter. Tests
compare that counter with graph breadth-first search at fresh unequal
triples, check every paired-edge equation directly, and reject an actual
size-preserving altered pair (move the centre to an omitted tip). The base
k=0 run has size 358 and 63,903 unordered pairs on each side. Independent
source review is still required; local checks are not publication.

## Words, endpoints and size

Let n=(36k+54,36k+50,36k+39). A word means its literal sequence of signs.
For coarse vertices at depths 1 through n_i, use `block^k tail` from
`FAMILY_COARSE` in the executable; put + at the centre. For edges indexed
0 through n_i-1, use `prefix block^k tail` from `FAMILY_EDGES`. The exact
words, with no search or solver in the delivered construction, are:

```text
coarse 1 block: +++-----------++++++++++++++++++++++
coarse 1 tail:  +++-----------+++++++++++++++++++++++++-----------++++
coarse 2 block: ---+++++++-------------+-+----------
coarse 2 tail:  ---+++++++-------------+-+-------------+++++++----
coarse 3 block: +++++++----+-+--+-++-+--+-+----+++++
coarse 3 tail:  +++++++----+-+--+-++-+--+-+----++++++++

edge 1 prefix: --+-+--++-++--+-+-
edge 1 block:  --+-+-+++-++--+-+---+-+-+++-++--+-+-
edge 1 tail:   --+-+-+++-++--+-+---+-+-+++-+++++-++
edge 2 prefix: -+---+-----+-+-+-+
edge 2 block:  -+---+-----+---+---+---+-----+---+--
edge 2 tail:   -+---+-----+-----------+-----+--
edge 3 prefix: ++++--+++++-++-++-
edge 3 block:  ++++--+++++-++-+++++++--+++++-++-+++
edge 3 tail:   +++++-+++++-++-+++++-
```

Every block has length 36; the coarse tails have lengths 54,50,39;
the edge prefixes have length 18 and tails have lengths 36,32,21.
Call the edge words X_i. Set p=(-,+,+), q=(-,+) and

```text
epsilon_1(j)=p[j mod3]q[j mod2],
epsilon_2(j)=q[j mod2], epsilon_3(j)=p[j mod3],
Y_i = reverse(epsilon_i * X_i).
```

Reverse within each arm, including both indexed ends. Subdivide every
coarse edge into five edges. At positions 5j+1,...,5j+5 on arm i, put
`X_i[j], X_i[j], Y_i[j], Y_i[j], coarse_i[j]`. Keep the centre +. Finally
append one **omitted** terminal vertex to each of the first two arms.
Positive and negative vertices give the two sets. No interior distance is
shortened by omitting these tips.

The proof below implies balance. The retained vertex count is
1+5(sum n_i)=716+540k, so each set has 358+270k vertices. The original tree
has 718+540k vertices; this is exactly floor(|V|/2)-1.
For the assigned family set k=266(t/9)-1. For positive t divisible by nine,
k>=0 and 36(k+1)=1064t. The original lengths become
(91+5320t,71+5320t,15+5320t), as required.

## Proof for all parameters

Write z for the distance variable and let V be independent. Put
D=1-z^36, E_i=z^(54,50,39)_i V, K_i=1-E_j-E_l. For any word W let
[W]_s=sum W[j] z^(s+j), with signs interpreted as integers. Define

```text
C_i = [coarse block_i]_1 (1-V) + V D [coarse tail_i]_1,
Xbar_i = D [edge prefix_i]_0 + z^18 [edge block_i]_0 (1-V)
         + V D z^18 [edge tail_i]_0.
```

Let Ebar_i be the same numerator as Xbar_i with each coefficient multiplied
by epsilon_i at its actual index. Both mask periods divide 36, so this is
valid before and after repeating a block. A star inverts **both** z and V.
The executable collects integer coefficients and verifies these three
identities in the Laurent ring Z[z,z^-1,V,V^-1]:

```text
D(1-E_1-E_2-E_3) + sum C_i K_i + z^36 sum E_i C_i* = 0,
sum Xbar_i K_i - sum Ebar_i = 0,
sum (Ebar_i-Xbar_i) E_j E_l - sum Ebar_i(E_j+E_l) = 0.
```

Substitute V=z^(36k). The displayed numerators divided by D are exactly
the finite words above, including k=0. Since D is nonzero, cancellation
is valid. The first identity is the full coarse shell equation, with
centre sign +1. Evaluating that shell at z=1 gives minus twice the total
sign sum, hence the colouring is balanced. For a balanced full colouring,
summing each vertex's distance enumerator with its sign gives twice the
difference of the two within-set distance profiles; multiplication by
1-z gives z times the shell. Thus the first identity proves coarse homometry.

For edge polynomials beginning at index zero, let
F_X=sum X_i K_i and W_Y=sum z^(n_i-1)Y_i(z^-1). The second identity is
F_X=W_Y, because reverse(Y_i)=epsilon_i X_i. Reversing F_Y=W_X and
multiplying by z^(sum n_i-1) gives exactly the third identity. Therefore
both edge equations hold. In the five-fold subdivision the nonzero
residues of the shell are precisely F_X-W_Y and F_Y-W_X, each used twice;
the zero residue is the coarse shell. All vanish. The same shell argument
then proves balance and equality of **all** distance multiplicities in the
retained tree, and hence in the original tree with its two omitted tips.

This proves every k, not a finite census. Discovery used an already
installed constraint solver to choose literal words; no solver result is
trusted by the proof or required by the command. Among the formerly open
72 residues modulo 495, this covers exactly the 24 divisible by nine;
the other 48 remain open. In particular the result does not claim the
entire 24-class problem modulo 165 is solved.

## The root argument actually fixes one component

Let E_i=reverse(Y_i), with reversal taken within arm i. The paired equations
are F_X=sum E_i and F_Y=sum reverse(X_i), where
F_X=sum_i X_i(1-sum_(j!=i) z^L_j). Reverse the second equation and multiply
by z^(a+b+c-1). At z^c=1, subtracting the first equation leaves

```text
(z^a-1)(z^b-1)(E_c-X_c)=0.                       (1)
```

`root_identity()` checks all six coefficients of this elimination in
independent formal A=z^a and B=z^b. The conclusion is E_c=X_c at those
roots, not X_c=0.

The necessary modulo-four masks from the prior derivation have p of length
three, product(p)=-1, and q of length two:

```text
E_c=p X_c,  E_b=q X_b,  E_a=(p q)X_a,
```

with periodic coefficientwise multiplication. This continuation treats
p with exactly one negative sign, at phase r. The p=(-,-,-) sector is treated separately by the complete constant-mask
argument below.

Now E_c-X_c=-2 sum_(j=r mod3) x_c,j z^j. At every c-th root except a
third root, both factors in (1) are nonzero by the gcd hypotheses. Writing
that selected component as z^r R(z^3), R vanishes at every nontrivial
(2h+1)-st root. Its degree is at most 2h and its coefficients are signs.
Therefore

```text
R(w)=s(1+w+...+w^(2h)),  s in {+1,-1}.
```

Only this one phase is constant. The other two phases are unrestricted.
The known counterexample at t=24 has different signs at odd-arm indices
zero and three while satisfying both complete edge equations.

## Twelve equations, sixteen unknown fields

Set w=z^6, V=w^h. Split every arm polynomial into six residue fields
P_i,r(w), and use Z_i,r=(1-w)P_i,r. The endpoint monomials are
A=w^3V, B=z^2w^2V and C=z^3V.
The first equation and the reversed second equation are

```text
sum_i [(1-epsilon_i)-A_j-A_l]X_i=0,
sum_i [(epsilon_i-1)A_j A_l-epsilon_i(A_j+A_l)]X_i=0.
```

Collect six residues of each and cancel the second equation's common V.
This gives twelve integer-polynomial equations. Of the eighteen Z fields,
only two are fixed by the valid root argument:

```text
Z_c,r   = s(1-wV),
Z_c,r+3 = s(1-V).
```

`corrected_system(p,q,s)` returns the other sixteen column names, the
12-by-16 matrix, and its right side. Columns use zero-based arm and residue
numbers. All six long-arm fields, all six middle-arm fields, and four
odd-arm fields remain free. A simultaneous sign negation permits s=1,
but the implementation supports both signs for explicit checks.

The equations are equivalent to the two original paired equations once
actual finite sign polynomials are substituted. They are not an existence
certificate for a rational or real solution. Degree and coefficient bounds
still matter: the P fields, not the Z fields, have coefficients +/-1.
Their lengths are h+3 on the long arm; h+3 in middle residues 0,1 and h+2
in its other residues; h+1 in odd residues 0,1,2 and h in residues 3,4,5.
Do not discard these constraints after linear elimination.

## Seven excluded masks, with all sixteen fields retained

Under the stated root hypotheses and h>=100, seven of the twelve
nonconstant masks are impossible. This does not exclude any whole
parameter class or original-tree pair. The five survivors are
(p,q)=((-++),(-+)), ((-++),(++)), ((+-+),(++)), ((++-),(+-)),
and ((++-),(++)).
In particular it does not contradict the nonperiodic q=(+1,+1) control.

Use M P=b/(1-w), since Z=(1-w)P. Keep coefficients at
w^(alpha*h+beta), alpha=0,1,2 and -6<=beta<=6. For a monomial w^a V^b
in a matrix entry, the unknown sign's index is
(alpha-b)h+beta-a. Every a is between zero and eight. For h>=100 that
index is inside a residue field precisely if

```text
alpha-b=0 and beta-a>=0, or
alpha-b=1 and beta-a<n,
```

where n is 3,2,1 or 0 according to the field lengths stated above.
All head indices are at most six; all tail offsets are at least -14.
They cannot overlap at h>=100. Every other index is outside the field.
The RHS coefficient after division by 1-w is the sum of monomials with
b<alpha, or b=alpha and a<=beta. Thus these are the same finite necessary
equations for every allowed h, not equations sampled at one h.

Exact integer elimination first adds linear consequences of the endpoint
rows. Every derived row carries rational weights;
`verify_linear_consequences` independently reconstructs its coefficients
and right side from the original rows. No unverified elimination step
is accepted. Then `endpoint_certificate` forces a sign only when its opposite leaves an
absolute residual greater than the sum of the remaining coefficient
magnitudes. It ends with a violated magnitude bound, a parity
contradiction, or both signs of one variable excluded. It never branches.
`verify_endpoint_certificate` independently replays the recorded
inferences and the terminal contradiction. All seven excluded masks have
such certificates. The tests compare the finite endpoint rows directly
to the original paired equations at h=100 and h=131, including arbitrary
nonperiodic values in the four free odd fields, and reject an altered proof.

These finite equations are necessary, so their contradiction excludes all
sign assignments for those masks. Failure to derive a contradiction for
another mask is not evidence that it is feasible. The constant-odd
sector and the five surviving nonconstant masks must not be conflated.
Swapping X and Y sends (p,q) to (reverse(p),reverse(q)); a global sign
change restores the chosen normalization. Thus the five surviving masks
form three exchange orbits, represented by the first three listed above.

## Parity certificates for the five surviving nonconstant masks

There is a second new result. For the three exchange-orbit representatives,
**every** solution of the corrected sixteen-field system must satisfy:

| Mask index | p | q | Necessary condition |
|---|---|---|---|
| 1 | -++ | -+ | h=0 modulo 3 |
| 3 | -++ | ++ | impossible |
| 7 | +-+ | ++ | h=1 modulo 5 |

Indices refer to `masks()`. Exchange carries the other two surviving masks
to indices 1 and 3. This is an unrestricted coefficient obstruction within
these masks: the four free odd fields remain arbitrary sign words.
On the remaining 48 residues modulo 495, neither numerical condition holds.
Together with the seven earlier exclusions, this excludes **all twelve
nonconstant masks** there. The four constant masks p=(---) are treated in the next section.
Neither this parity calculation nor the completed obstruction below
refutes arbitrary omissions in the original tree.

Here is a reproducible algebraic certificate. In this section write
A_r=P_(long,r), B_r=P_(middle,r), C_r=P_(odd,r), before multiplication by
1-w. The twelve equations imply the following three rows, respectively:

```text
(1-w^3)A_0 + 2w^2 C_1 - 2w^4 C_2 - 2w^5 C_4 + 2w^2 C_5
    = -V(w^5+w^4-w^3) - (1+w+w^2),

(w^5-1)(B_0-w^2 B_1+w^4 B_2)
 + (w^5+1)(-w^2 C_1+w^4 C_2) + 2w^5 C_4 - 2w^7 C_5
    = (Vw^6-1)(w^4+w^3-w^2-w-1),

(w^5-1)(w^3 A_0+w^6 B_3-B_4+w^2 B_5)
 + (w^5+1)(-w^3 C_0+w^6 C_3+w^2 C_5) - 2w^4 C_2
    = V(w^12+w^11-w^10-w^9-w^8) + w^4+w^3+w^2-w-1.
```

`PARITY_CERTIFICATES` stores explicit polynomial row multipliers. The
checker multiplies the original 12-by-16 matrix and right side, and checks
**every column** against each displayed row, after restoring the factor
1-w relating P to Z. Their common denominators are, respectively,
2 V^2 w (Vw^3-1)(V^2w-1), 2 V(V^2w-1), and
2 V^2 w^3(V^2w-1). Substituting V=w^h never makes these the zero polynomial
for h>=0, so clearing them loses no implication. Neither a symbolic solver
nor a floating-point calculation is used by the verifier.

To read the parity contradiction, call the left coefficients d_i(w),
the right side R(w,V), and let n_i=h+offset_i be the actual field lengths.
Put G_n=1+w+...+w^(n-1). Every sign field has P_i=G_(n_i)+2Q_i with integer
coefficients Q_i. Thus, necessarily,

```text
sum d_i Q_i = K_h,
K_h = (R(w,w^h)-sum d_i G_(h+offset_i))/2.
```

All d_i are divisible by 1-w^m modulo two, with m=3 for the first row and
m=5 for the other rows. Therefore K_h must also be divisible by 1-w^m
modulo two. This retains all the free Q_i; none are set to zero.
The verifier checks K_h has integer coefficients for each base residue
0<=h<m. It also checks the following **polynomial** increment identities,
not a finite extrapolation:

```text
K_(h+m)-K_h = w^h(1-w^m)L,
L_1 = -w^2-3w^3-2w^4,
L_3 = w^8+w^7-w^5+w^4+w^3,
L_7 = 2w^10+2w^9+2w^8+w^7+w^6+w^5-w^3-w^2.
```

Hence its m exact remainder computations exhaust every h. They yield
zero remainder only at h=0 modulo 3 for mask 1, nowhere for mask 3, and
at h=1 modulo 5 for mask 7. This proves the table. In the affine family,
h=532(t/3): these conditions are respectively nine divides t and
t=9 modulo 15, exactly the two now constructed branches.

Run the certificate with:

```sh
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --prove-parity
```

Tests reject altered row multipliers and an altered increment identity.
A successful parity proof alone does not address the constant masks.
The following argument supplies that missing part; the original universal
milestone remains open.

## Why these sixteen masks exhaust arbitrary paired rows

This also reconstructs the mask reduction without a whole-row periodicity
assumption. Write A=z^a, B=z^b, C=z^c and E_i=reverse(Y_i). Set
D_i=(X_i-E_i)/2; its coefficients are 0 or +/-1. Subtract the first edge
equation from the reversed second one after substituting E_i=X_i-2D_i.
The X terms cancel, giving

```text
(1-B)(1-C)D_a + (1-A)(1-C)D_b + (1-A)(1-B)D_c = 0.       (2)
```

At the b-th roots, only 1 and -1 can annihilate (1-A)(1-C), since the
pairwise gcds are 2,3,1. The roots are simple and deg D_b<b, so
D_b=(1-B)/(1-z^2) times a word u of length two. Likewise
D_c=(1-C)/(1-z^3) times a word v of length three. Their coefficients
u_j,v_j belong to {0,+1,-1}. Dividing (2) by (1-A)(1-B)(1-C) shows that
D_a repeats -(u_j+v_j) with periods two and three. Because every D_a
coefficient also belongs to {0,+1,-1}, nonzero u_j and v_j must have
opposite signs. Consequently the reversal masks are q on arm b, p on
arm c, and pq on arm a, with a minus exactly where D is nonzero.

At z=1 the paired equations give sum X=sum D. The former is odd because
there are a+b+c odd edges. But the latter is

```text
(b-a)/2 * sum u + (c-a)/3 * sum v = -2 sum u - 5 sum v.
```

Thus v has an odd number of nonzero entries. The mask p therefore has
one or three minuses. These are exactly the twelve nonconstant and four
constant masks, not a restriction to periodic X. Moreover where a D
coefficient is nonzero it equals the X coefficient. This proves the valid
negative-component constraint used above.

## The four constant masks and the full-prefix obstruction

If p=(---), all entries of v are nonzero. If q has any minus, the bound
|u_j+v_r|<=1 forces every v_r to have the same sign. Negate both rows to
make that sign +. Then X_c=G_c=(1-C)/(1-z), and every nonzero u_j is -1.
There are only the following cases.

* **q=(--).** X_b=-G_b and E_a=X_a. The first edge equation reduces to
  X_a=(B-C)(1-A)/((B+C)(1-z)). Since b-c=11, a primitive 22nd root makes
  B+C=0 but B-C nonzero, forcing 22 to divide a. On the affine family this
  means t=6 modulo 11, excluded from the remaining classes.
* **q=(++).** Here u=0, X_a=-P(1-A)/(1-z^3) and
  X_c=P(1-C)/(1-z^3), for a three-sign polynomial P. The first equation
  gives X_b=P(z^15-1)(1-B)/((z^15+1)(1-z^3)). At
  z=exp(pi*i/15), the denominator's first factor vanishes and all other
  factors are nonzero: b=2 modulo 3 so 30 does not divide b. Hence P(z)=0.
  This is impossible for three signs: writing P=s0+s1*z+s2*z^2, its
  imaginary part after division by z forces s0=s2, and then its real part
  requires cos(pi/15)=+/-1/2.
* **q=(-+).** The odd-indexed part of X_a is
  -z(1-A)/(1-z^2), the even-indexed part of X_b is
  -(1-B)/(1-z^2), and X_c=G_c. Call the unknown remaining parts a_e,b_o.
  Splitting the first edge equation by parity gives a two-by-two system
  with left matrix [[B,C],[C,A]]. At z=exp(2*pi*i/13),
  AB=C^2 because a+b-2c=26. Its compatibility condition, after multiplying
  by the nonzero 1-z^2, is
  C*z + 1+z+z^2=0. The executable verifies this exact polynomial reduction
  modulo z^13-1. But it implies C=-(1+2 cos(2*pi/13)), whose absolute value
  exceeds one, while |C|=1. This is a contradiction.
* **q=(+-).** Exchange X and Y. Since a and b are even, reversing their
  parity masks interchanges -+ and +-, reducing to the previous case.

For the compatibility calculation in the third case, set
alpha=-z(1-A), beta=-(1-B), gamma=1-zC, delta=z-C. The two right sides,
multiplied by 1-z^2, are

```text
R1=-C alpha+(2-A)beta+(2-A-B)gamma,
R2=(2-B)alpha-C beta+(2-A-B)delta.
```

The exact identity checked by `constant_mask_proof()` is

```text
z^2(C R1-B R2) = 2 C^2(1-z)(Cz+1+z+z^2)  modulo z^13-1,
```

after A=Cz^15 and B=Cz^11. This records the signs and endpoints needed
to reconstruct the analytic contradiction without trusting a search.
The same function checks (2) and the constant-row quotient algebra.

Therefore on every remaining positive affine parameter, **no arbitrary
paired edge rows exist**. The hypotheses repeat modulo 495 because their
gcds use only the fixed differences 4,11,15; h mod3, h mod5, and t mod11
also repeat there. `--prove-obstruction` verifies the 48 representatives,
all earlier mask certificates and these exact polynomial identities.

An arbitrary full colouring of the prefix with lengths (5a,5b,5c) splits
by depth modulo five into a coarse colouring and two pairs of edge rows.
Its shell equation forces the same paired equations. Thus no full equal
homometric partition of that prefix exists on the 48 remaining classes.
This excludes the **specific** choice of omitted vertices at the longest
and middle tips, even with arbitrary recolouring of every retained vertex.
It does not bound all pairs on the original tree: another pair of omitted
vertices is still allowed and may succeed.

```sh
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --prove-obstruction
```

## Interior omissions: a necessary parity filter

The continuation starts with an obstruction applying to **all** pairs,
not only periodic words. The earlier [full-partition bound](PUBLISHED_CASES.md#a-full-partition-obstruction-and-a-sharp-case)
applies here with gcd(L_i+1)=4 and odd quotient sum 45+3990t. Thus a pair
meeting the target omits exactly two vertices. In a bipartite tree, let x and y count even-depth
vertices in two sets of equal size k. The numbers of odd-distance pairs
are x(k-x) and y(k-y). Homometry therefore implies

```text
(x-y)(k-x-y)=0.
```

Consequently the retained bipartition classes must either have equal
sizes, or both have even sizes. This is only a necessary condition; it
does not certify the other distance multiplicities.

In the original affine tripod, the even-depth class has
E=88+7980t vertices and the odd-depth class has E+2. Both are even.
Omitting one vertex from each leaves unequal odd class sizes, violating
the condition. Thus **the two omitted vertices must have the same depth
parity**, for every permitted homometric pair attaining the target.
In particular omitting the centre and any terminal tip cannot work.
If both omitted vertices have even depth, each set must contain
(E-2)/2 even-depth and (E+2)/2 odd-depth vertices. If both have odd depth,
the two retained classes have equal size and this extra restriction vanishes.

When searching a repeated-word family with two even-depth omissions, an
increment of two modulo four in all three arms changes the bipartition
parity and makes alternate parameters impossible. Split that phase or
use a common increment divisible by four. This explains some failed
unrestricted-period templates without excluding their compatible phases.

## An interior-hole construction for the entire affine family

Rook, 21 November 2026. For every integer k>=0,

```
T(203+56k, 183+56k, 127+56k)
```

has disjoint homometric sets of size **256+84k**, exactly its
half-minus-one target. The omitted vertices are both on the longest arm:
its vertex at depth 19 and its terminal tip. Distances pass through the
interior omitted vertex in the original tree.

For every positive integer t, put **k=95t-2**, which is nonnegative. Then
these lengths are exactly `(91+5320t,71+5320t,15+5320t)`. Thus the entire
positive affine family now attains the target, including all 48 previously
unresolved classes modulo 495. The earlier finite witness handles t=0.
This resolves the assigned continuation; it does not prove the target for
arbitrary triples. Priority remains provisional, and independent review
of this contribution and its prerequisite is still required.

### Reproduce the identity and original-tree witness

After the stated predecessor dependencies and this contribution are
integrated, run from the complete repository using only Python's standard
library:

```sh
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --prove-interior
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --interior-k 2 --witness /tmp/interior.json
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --check /tmp/interior.json
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --interior-t 15
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_unrestricted_odd_fields.py
```

Recorded k=2 run: lengths `(315,295,239)`, size 424 on each side, target 424,
89,676 unordered pairs on each side, identical distance profiles with hash
`3a3fd75c8fb49995aae73213f92e0be9787ac0900120456f24628f512412c498`.
The actual t=15 run (a formerly missing class) returned lengths
`(79891,79871,79815)`, equal sizes 119788, and 7174522578 unordered pairs on
each side, with profile hash
`0c78d232587f613a9cbe7bb6326b80896321daa51490edff79b6a507ed4c7d82`.
The proof command returns PASS for the exact two-variable identity below.
The tests use independent breadth-first distances at fresh parameters and
reject a changed sign in the identity and a changed, still equal-sized
and disjoint, actual witness.

### Literal words, with both holes explicit

The centre has sign +. Each row is `prefix block^k tail`. A zero is an
omitted vertex, not a contracted edge. Every block has length 56; prefix
lengths are 101,91,63 and tail lengths are 102,92,64. These are the exact
`INTERIOR_FAMILY` words in the executable:

```text
1 prefix -+-+-+-+-+-+-+-+-+0-+-+----+-+++++-++-+-+-+-+-+-+-+-+-+--+-+-+-+++++++++-+-+-+-+++++++-+-++--++++++++
1 block  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
1 tail   ++++++++--++-+-+++++++-+-+-+-+++++++++-+-+-+--+-+-+-+-+-+-+-+-+-++-+++++-+----+-+-+-+-+-+-+-+-+-+-+-+0
2 prefix -+-+-+-+-+-+-+-+-+-+-+-++++-+-----+--+-+-+-+-+-+-+-+-+-+-+-+-------+-+--++-+-+-+-+---------
2 block  +---------+-+-+-+-----------------------+-+-+-+---------
2 tail   +---------+-+-+-+-++--+-+-------+-+-+-+-+-+-+-+-+-+-+-+--+-----+-++++-+-+-+-+-+-+-+-+-+-+-+-
3 prefix +-+-++++-+-----+--+-+-+----+-+++++-+++-+-+-+---------+-+-+-+-+-
3 block  +-+-+-+-+-+---------+-+-+-+---+-+-+-+---------+-+-+-+-+-
3 tail   +-+-+-+-+-+---------+-+-+-+++-+++++-+----+-+-+--+-----+-++++-+-+
```

Take the positive and negative vertices as the two sets. This assigns a
sign to every vertex except the two displayed zeros, exactly once.

### Proof for every k, including zero

Work in the Laurent ring Z[z,z^-1,V,V^-1], before substituting V=z^(56k).
For a word W starting at depth s, let `[W]_s=sum_j W_j z^(s+j)`, interpreting
+,-,0 as 1,-1,0. Put D=1-z^56, H=(101,91,63), n=(203,183,127), and define

```
P_i = [prefix_i]_1,  B_i = [block_i]_(H_i+1),
T_i = [tail_i]_(H_i+1),  E_i = z^n_i V,
N_i = D P_i + (1-V) B_i + D V T_i,
K_i = 1-sum_(j!=i) E_j.
```

After substitution, N_i/D is exactly the signed depth polynomial S_i of
the finite row, including k=0. A star inverts both z and V. Since
D(z^-1)=-z^-56 D, the full-shell numerator is

```
Qbar = D(1-E_1-E_2-E_3) + sum_i N_i K_i
       + z^56 sum_i E_i N_i*.
```

Let F_h be the signed distance enumerator from the omitted vertex at depth
19, and F_l that from the omitted long tip. Their exact numerators are

```
D F_h = D z^19 + D sum_p (P_1)_p z^|p-19|
        + z^-19(N_1-D P_1) + z^19(N_2+N_3),
D F_l = D E_1 - z^56 E_1 N_1* + E_1(N_2+N_3).
```

The first formula splits the long arm at the interior hole. Everything
outside its fixed prefix lies farther out than depth 19. The second uses
that every retained long-arm vertex lies before its omitted tip. Both use
original-tree distances, also between opposite sides of the interior hole.

Substitution of the literal words gives the exact coefficient identity

```
z Qbar - (1-z)(D F_h + D F_l) = 0.                  (I)
```

`interior_proof()` collects integer coefficients in independent z,V and
returns an empty residual. It checks the words' lengths and the two zero
positions before doing this calculation; no search or solver is used.
After V=z^(56k), cancel the nonzero polynomial D. At z=1, the resulting
full shell is minus twice the total sign sum, while the omitted-vertex
correction vanishes. Thus the two sets have equal size. The retained count
is 512+168k, so that size is 256+84k. For a balanced colouring, the left
side of (I) after cancellation is `(1-z)` times twice the difference of
the two complete unordered distance profiles, by the arbitrary-hole
shell identity in EDGE_DEPENDENT.md. Polynomial cancellation proves
homometry at every distance. No finite witness or experiment is used to
extrapolate to other k.

## Different omissions: the depth-parity construction is exhausted

Rook, 21 November 2026. This continuation proves a **restricted** negative
result for every parameter, not the task's requested upper bound over all
pairs. Colour every even-depth vertex positive, every odd-depth vertex
negative, and omit two negative vertices. On the larger family
`T(91+q,71+q,15+q)`, q any nonnegative even integer, this construction is
homometric **exactly** in the following five cases (arm labels are fixed):

| q | First omitted vertex | Second omitted vertex |
|---|---|---|
| 18 | middle tip, depth 89 | long arm, depth 55 |
| 22 | long tip, depth 113 | short arm, depth 19 |
| 40 | middle tip, depth 111 | middle arm, depth 55 |
| 60 | long tip, depth 151 | long arm, depth 75 |
| 78 | long tip, depth 169 | middle arm, depth 75 |

Thus none has q=5320t, even at t=0. Reversing both colours changes nothing.
This does **not** restrict an arbitrary two-colouring: the successful
nine-multiple construction above already uses different signs.

Run `unrestricted_odd_fields.py --prove-bipartition-holes`. The recorded
standard-library run returned `proof: PASS`, the five offsets above,
`affine_parity_colouring_excluded: true`, and
`original_target_ruled_out: false`. Tests independently count original-tree
breadth-first distances in all five cases, including the cases with two
holes on the same arm. They reject a size-preserving move of an omitted
odd vertex in each case. The original tree is never contracted at a hole.

### Exact classification, without searching parameter or depth ranges

Put q=2r and A=(r+46,r+36,r+8), so arm i has length 2A_i-1.
Let w count distance two. Before removing holes, the positive and negative
within-arm distance profiles are equal: even vertices on an arm including
the centre form a path of A_i vertices, just like its odd vertices.
For each pair of different arms i,j, the negative profile exceeds the
positive profile by `w+w^2+...+w^(A_i+A_j-1)`. This follows by subtracting
`(w+...+w^(A_i-1))(w+...+w^(A_j-1))` from
`w(1+...+w^(A_i-1))(1+...+w^(A_j-1))`.

Call the sum of these three intervals F. An odd vertex at depth 2x-1 on
arm j has distance enumerator S to the other odd vertices, where

```
(1-w) S = 2w+w^x-w^(A_j+1-x)-sum_(k!=j) w^(x+A_k).
```

This includes boundary values x=1 and x=A_j by cancellation. If the two
holes are h,g, their removal deletes `S_h+S_g-w^D` from the negative
profile, where 2D is their original-tree distance. The pair is therefore
homometric iff this polynomial equals F.

The two longest odd tips form the unique pair at distance
`2(A_1+A_2-1)`, beyond every positive-positive distance. At least one of
these tips must be a hole. Fix its arm i in {1,2}, and let the other hole
lie on arm j at depth 2x-1. Multiplying the preceding equality by 1-w and
cancelling gives equality of the following **multisets of three exponents**:

```
j=i: {x, A_i, A_j'+A_k'} = {A_i-x, x+A_j', x+A_k'},
      where j',k' are the other two arms;
j!=i: {x, A_i, A_j+A_k} = {A_j+1-x, x+A_k, A_i+x-1},
      where k is the remaining arm.
```

Conversely either multiset equality implies the original profile equality,
because multiplication by 1-w is injective on integer polynomials.
Each exponent is affine in r,x. There are two choices of i, three of j,
and six matchings of the exponent multisets: **36 linear systems**.
`bipartition_hole_cases()` solves each using exact rational two-by-two
elimination and checks the third equation. Rank-deficient systems are
checked for inconsistency; the verifier fails if any unexamined affine
branch survives. It then enforces integer r>=0, 1<=x<=A_j, and distinct
holes. The five rows in the table are the complete output. This is a
finite enumeration of symbolic identities, not a finite census of trees.

### Scope of this restriction

The depth-parity classification does not supply an upper bound for arbitrary
colourings. The interior-hole construction above is such a different
colouring. Exploratory search failures and time limits supply no additional
obstruction. Priority and independent predecessor integration requirements
are unchanged.

## Reproduction and useful limits

Run from the repository root, using only Python's standard library:

```sh
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --counterexample-k 850
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --prove-seven-masks
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_unrestricted_odd_fields.py
```

The first command reports lengths [25554,25550,25539], gcds [3,1,2],
12 masks, matrix shape [12,16], and four free odd fields. The second reports
zero residual coefficients and `whole_odd_row_has_period_three: false`.
Both explicitly report `remaining_24_classes_solved: false`.
Eight tests check the root elimination, every mask and both signs against
literal original edge equations at three different lengths, invalid fixed
components, the actual t=24 counterexample, and the real CLI.

An exploratory fixed-period-five insertion search tried 36 configurations
at h=10,13,14, three nonconstant p masks with q=(+,+), and four insertion
positions. Seven restricted-template searches exhausted; 29 hit their
short time limit. A separate period-eleven screen of 72 configurations hit
its short limits without a witness; no source acceptance rests on it. No witness resulted. These are discovery failures only;
they neither exhaust the corrected coefficient model nor prove anything
about any infinite class. The search code was not added as a second solver
or a default fallback.

The interior-hole continuation above supplies a different pair for every
positive t of this affine family. Triples outside the known constructions
still need a witness or an upper bound over all permitted pairs. All paired-row sectors and the specific five-fold full
prefix remain excluded on the 48 baseline classes; this is consistent with
the new interior-hole construction and does not refute the original target. Independent review and the unread priority sources
remain necessary before larger claims.
