# The exact boundary for unrestricted central-path transfer

Hawthorn, 21 November 2026. Let r,b,c be positive integers, put
c′=c-((r+c) mod 2), and M=r+c′. Consider the transfer on
T(b+r+1,b,c) from [INTERIOR_TRANSFER.md](INTERIOR_TRANSFER.md): omit
long-arm depth r and its tip; omit the short tip too if c′=c-1. Colour
all M central vertices by any reflection-antisymmetric sign word, and
attach arbitrary opposite sign words of length b at coordinates 0 and r.

**Theorem. A homometric pair of this form exists if and only if**

```
r divides b, OR
r divides c′ and (c′/r is odd OR b is even).
```

No anti-periodicity is assumed. Thus allowing unrestricted central words
adds **no triples** to the predecessor's admission domain, although it
can add different words. The obstruction covers every central and tail
word of the stated form, for every parameter outside that domain.
It is not an obstruction to arbitrary pairs with different omissions or
a different construction, and does not refute the general tripod target.

For example, T(b+4,b,1) admits this transfer exactly when 3 divides b.
The unchanged default command already attains the target on T(9,5,1),
where this transfer is impossible. This illustrates the scope distinction.

## Existing work and what changes

The predecessor is Rook's completed private 772580f, whose final proof
was inspected in preserved run 4683b6fb12fa4f789a8398657a1c4e44. It proves
sufficiency and an exact boundary **assuming** p[j+r]=-p[j]. The new
necessity argument below removes that assumption and closes the stated
path-transfer problem; it supplies no new positive tripod coverage.

The earlier bipartite parity observation in
[UNRESTRICTED_ODD_FIELDS.md](UNRESTRICTED_ODD_FIELDS.md#interior-omissions-a-necessary-parity-filter)
is background, not a new result. The completed 94f9a35 affine construction
is unchanged and is not reopened as missing. External priority remains
provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md); this is not
a claim of first publication or a universal three-arm theorem.

The new module imports only the existing published-case checker. It runs
from the current repository without the pending transfer module or its
pending prerequisites. No old file or default selector changes. The
predecessor links become local when its contribution is integrated.

## Coordinates and the complete distance equation

Coordinates 1,...,M follow the central path from just after the omitted
long-arm vertex to the retained short tip. For j<r the vertex is long-arm
depth r-j; j=r is the centre; j>r is short-arm depth j-r. Coordinate 0
is an omitted vertex, not a contracted edge. Its distance to j is j;
the centre's distance is |j-r|, including distance zero at j=r.

For p_j in {+1,-1} with p_j=-p_(M+1-j), write

```
P = sum_(j=1)^M p_j z^j,       I = sum_(j=1)^r p_j z^j,
A = U_0-U_r = sum_(j=1)^M [z^j-z^|j-r|]
  = (z^(c′+1)-1)(1-z^r)/(1-z),
H = F_0+F_r = sum_(j=1)^M p_j [z^j+z^|j-r|],
X = sum_(j=1)^b x_j z^j,       G = z+...+z^b.
```

The two tails receive x_j and -x_j. Reflection makes the base pair
balanced and homometric. Old-old distance differences vanish; each
tail's internal pairs cancel against the other tail; cross-tail terms
cancel on exchanging the two depths. Twice the remaining old-new
profile difference is exactly

```
E = X A + G H.                                           (1)
```

Thus E=0 is necessary and sufficient for every original-tree distance
multiplicity. It is not just a moment condition. Each set has b+M/2
vertices, the half-minus-one target. The listed coordinates and signs
ensure disjointness; the actual tip omissions do not change distances.

## Eliminate the unrestricted tail using reflection

For any Laurent polynomial Q let Q*=Q(z^-1), and put R=z^r. Splitting
H at the centre, with I including the sign at j=r, gives

```
R H = (1+R)P + R^2 I* - I.
```

Its reciprocal gives R H*=(R^2+R)P*+I-R^2 I*. Adding, then using
reflection P*=-z^(-(M+1))P, yields

```
H+H* = (1+R) z^(-(M+1)) (z^(c′+1)-1) P.
```

Also A*=-z^(-M)A and G*=z^(-(b+1))G. Put Y=z^(b+1)X*, the reversed
tail polynomial. Applying these identities to E/G+E*/G*, clearing
denominators and cancelling the nonzero polynomial z^(c′+1)-1 gives

```
(1+z^r)(1-z^b)P = (1-z^r)(Y-z^M X).                    (2)
```

The cancellation is in the Laurent polynomial integral domain, before
any specialization at roots. In particular, it remains valid when r
and c′+1 have common factors. No symmetry or periodicity of X was used.

There is a direct check avoiding rational division. With
K=(1+z^r)(1-z^b)P+(1-z^r)(z^M X-Y), the exact identity is

```
(1-z)[z^(M+1) E + z^(M+b+2) E*] = z(z^(c′+1)-1) K.
```

`elimination_identity()` verifies it over integer Laurent polynomials in
nine independent variables z,R,C,B,P,I,I*,X,Y, with C=z^c′ and B=z^b.
It rejects a changed reflection sign. `reflection_transfer_identity()`
also checks the identity on literal words, including nonhomometric ones.
The nonzero factors on the right prove that E=0 implies K=0 and (2).
The converse is not asserted or used.

## Residue sums give the full obstruction

Put g=gcd(r,b). In Q[z], 1-z^r and 1+z^r are coprime, and

```
gcd(1-z^r,1-z^b)=1-z^g.
```

These facts follow either by Euclidean division of binomials or by their
simple roots of unity. Equation (2) therefore implies

```
B_r,g = (1-z^r)/(1-z^g) = 1+z^g+...+z^(r-g) divides P.   (3)
```

Reduce P modulo z^r-1. Its coefficient in residue j is
S_j=sum_(1<=k<=M, k=j mod r) p_k. Since z^g B_r,g=B_r,g modulo z^r-1,
(3) says that the r coefficients S_j repeat a word of length g. This
statement is integral: the divisor is monic, so its quotient in P has
integer coefficients. Also sum S_j=P(1)=0 by reflection.

If g=r there is no restriction, and this is exactly the first admitted
case r|b. Suppose g<r. Write M=qr+s, 0<=s<r. Each S_j has the same
parity as its number of signs. The first s residues contain q+1 signs,
and the other r-s contain q signs. If 0<s<r, this parity word consists
of two nonempty constant intervals with different values; it cannot
repeat with proper divisor period g. Indeed if s>=g its first full
period is constant, which would force the whole word constant; if s<g,
the next repetition of its first s values already contradicts the
constant suffix. Therefore s=0: r divides M and hence c′.

Now every S_j is a sum of q signs. The equality sum S_j=0 and their
period g imply sum_(j=1)^g S_j=0. If q is odd, all g summands are odd,
so g must be even. If q is even there is no additional obstruction.
Since q=c′/r+1, these are precisely c′/r odd, or g even. In the latter
case q odd and M even force r even, so g even is equivalent to b even.
This proves necessity of the displayed admission domain for all words.
It includes c′=0, which can occur when c=1 and r is even.

## Sufficiency supplies actual sign words

For completeness, the predecessor's formulas attain all three cases:

* If r|b, use p_j=(-1)^floor((j-M/2-1)/r). It is anti-periodic with
  step r and reflection-antisymmetric for every even M.
* If c′/r is odd, the same word has a constant first r-block. No
  divisibility restriction on b is then needed.
* If c′/r is even and b is even, r and g=gcd(r,b) are even. Let v be
  g/2 plus signs followed by g/2 minus signs, and put
  p_j=(-1)^floor((j-1)/r) v_((j-1) mod g). Reflection reverses v while
  preserving the r-block parity, so again it negates every sign.

In all cases, give the first tail the reversed first r signs, repeated
as needed to length b, and the second tail their negatives. This is the
actual word used by `construct_pair`, without a search.

Here is the common algebra. Put J=-z^r I*. Anti-periodicity and
reflection give (1+z^r)P=I-z^(M+r+1)I*, hence
H=(z^(c′+1)-1)J. Take

```
X = -z J (1-z^b)/(1-z^r).
```

The quotient is a sign polynomial: when r|b it repeats the r-sign
block; when the block is constant its geometric factor cancels; in the
third case the first r signs repeat a g-sign block and g divides b.
Substitution into (1) gives zero exactly. Thus each admitted case
produces disjoint sets with the target size and identical profiles.
`constant_tail_identity()` independently checks that special case after
clearing denominators, and rejects the opposite tail orientation.

## Real commands, boundaries, and controls

From a clone of [Emberhall](https://github.com/Someblueman/emberhall), run
at the repository root with Python 3.10+ and its standard library:

```sh
python3 projects/almost-halving-three-branches/unrestricted_path_transfer.py --prove
python3 projects/almost-halving-three-branches/unrestricted_path_transfer.py 3 5 1
python3 projects/almost-halving-three-branches/unrestricted_path_transfer.py 3 7 9 --witness /tmp/central-pair.json
python3 projects/almost-halving-three-branches/published_cases.py --check /tmp/central-pair.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_unrestricted_path_transfer.py
```

Recorded 21 November: both exact identities pass and their changed signs
are rejected. The negative command returns `status: obstructed` on
T(9,5,1), with `universal_tripod_obstruction: false`. The positive
command exports disjoint sets of size 13 on T(11,7,9), exactly its
target, with 78 distances on each side; the existing input checker
accepts that file. A size-preserving changed vertex is rejected by that
checker in the tests. All eight focused tests pass.

Different central words can work without adding coverage:

```sh
python3 projects/almost-halving-three-branches/unrestricted_path_transfer.py 2 7 6 --central=+--+-++- --tail=-+--+-+ --witness /tmp/nonperiodic-pair.json
```

This real run gives size 11 and identical 55-distance profiles on
T(10,7,6), with `anti_periodic: false`. The triple itself was already
covered by Rook's constant-tail construction. Changing the first tail
sign and its opposite mate preserves disjointness and size but gives
a nonzero full distance residual. As an additional rigidity corollary,
when gcd(b,r)=gcd(b,c′+1)=1, A and G are coprime; (1) forces H=±A by
degree and leading coefficient, so X=∓G is constant. The displayed
nonconstant tail has gcd(b,c′+1)=7 and does not contradict that corollary.

The tests independently count original-tree distances by breadth-first
search, exhaust 2,940 central/tail assignments at 72 small parameter triples,
and check fresh larger parameters in all admitted branches, including
an omitted short tip. Enumeration corroborates implementation; the
polynomial and residue arguments prove the infinite statement. A
non-author's reconstruction and independent integration are still due.
