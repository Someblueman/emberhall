# Every bounded short-arm lift stream

Linnet, 23 November 2026. The survivor pattern previously checked only at
b=2,4,6,8 holds for **every even b>=2**. Fix X3=p=+1 by global sign and
write x=X2, y=Y2, q=Y3. The two infinite forced coefficient streams stay
in {+1,-1} exactly for these boundaries:

* **A:** q=+1, y=reverse(x), and x[0]=x[b-1].
* **B:** q=-1, x is all minus and y is all plus.

There are exactly `2^(b-1)+1` such boundaries. This is a theorem about
infinite forced streams in the two-row subdivision template. A finite
word can end before its forced stream fails; its final coefficient also
has a correction. This is **not** a classification of all finite lifts,
and is not an obstruction to arbitrary homometric partitions.
Priority remains provisional and the general tripod milestone stays open.

## Reproduce

Python 3.10+ with only its standard library:

```sh
python3 projects/almost-halving-three-branches/short_arm_structure.py --prove
python3 projects/almost-halving-three-branches/short_arm_structure.py --classify -- ++ -1
python3 projects/almost-halving-three-branches/short_arm_structure.py --classify +--+ +--+ 1
python3 projects/almost-halving-three-branches/short_arm_structure.py --classify ++++ ++++ -1
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_short_arm_structure.py -q
```

The first command checks the formal survivor identities and all 32
b=2 boundaries. It directs the reader to the spectral argument below;
it is not a claim that a proof assistant checked that argument. The
second command accepts the literal all-minus word and reports type B.
The third reports type A with period six from index one; the fourth
returns a concrete invalid coefficient. The standalone module
depends on no other project file. Tests also compare it with the earlier,
independently structured two-variable elimination implementation.

## Exact setup and sufficiency

Put L=b-1, R=z^L, B=z^b, C=B-R-1 and

```text
P=-(1-z)(1-B)(1+R),
N0=-(1-z)[C x+R^2 y*]-(1-B)[C p+q],
X_infinity=N0/P.
```

Interchange x/y and p/q for Y_infinity. A star substitutes z^-1.
These are the forced low coefficients from eliminating the long arm in
E1/E2. The omitted high numerator affects a finite word only at its final
coefficient and beyond; see SHORT_ARM_LIFTS.md for that boundary.

For type A, y*=x/R and p=q=1 give

```text
X_infinity=-(x+R)/(1+R), Y_infinity=-(y+R)/(1+R).
```

Write n=jL+k with 0<=k<L. The coefficient at n=0 is -x[0]; at a positive
multiple jL it is (-1)^j; elsewhere it is `-(-1)^j x[k]`.
The endpoint condition makes these formulas agree. Thus all are signs,
and each stream has period 2L from index one. The checker verifies the
rational identity with independent z,R and a formal placeholder for x.

For type B, x=-(1-B)/(1-z) and y=-x give

```text
X_infinity=-(1-R)/((1-z)(1+R)), Y_infinity=-X_infinity.
```

These are alternating constant-sign blocks of length L, hence signs
forever with period 2L from index zero. Their cleared identity is also
checked in independent z,R. A sign-corrupted identity is nonzero.

## Necessity when q=-1

For b>=4, the coefficients at n=0,...,b-2 are `-x[n]-2` and `-y[n]+2`.
Validity therefore forces x[n]=-1 and y[n]=+1 throughout those prefixes.
Put u=x[b-1], v=y[b-1]. Expanding the displayed generating functions
through n=2b-1 now gives `X[2b-1]=v-2`, `Y[2b-1]=u+2`.
Both can be signs only when v=+1 and u=-1, exactly type B.

More explicitly, relative to the proved type-B streams, the changes are

```text
Delta X = R[(u+1)C+(v-1)]/((1-zR)(1+R)),
Delta Y = R[(v-1)C+(u+1)]/((1-zR)(1+R)).
```

Their R^2 z coefficients are v-1 and u+1. Adding the base signs gives
the two stated forced coefficients. These identities follow by expanding
`1/((1-zR)(1+R))` through R^2; terms R^3 begin later than 2b-1 for b>=4.
The b=2 case is included in the exact 32-boundary base check.

## Two coprime periods force rigidity

Assume q=+1 and both streams are signs forever. P has only roots of
unity, with repeated roots only at +1 and -1. A nonzero repeated-pole
term grows linearly along a residue class, so boundedness cancels it.
The polynomial part of N0/P affects only index zero. Each stream, from
index one, is therefore a sum of real sequences f+g where

```text
f[n+b]=f[n],   g[n+L]=-g[n].
```

This also follows by grouping the simple Fourier modes of the remaining
denominator into b-th roots and roots of z^L=-1, assigning their common
root -1 to either group. Conjugate roots pair to give real sequences.

On either depth parity, f has period b/2 and g has period L. Those periods
are coprime. The Chinese remainder theorem means every pair of their
values occurs together. If both varied, fixing one value of g shows two
distinct f values differ by 2; fixing f gives the same conclusion for g.
Their combined range would then be at least 4, impossible for signs.
So one component is constant on that parity. Anti-periodicity of g,
with odd L, makes its two parity value sets negatives of one another.
Thus either g is constant on both parities, or f is constant on both.
Consequently **each stream has period b or period 2L**, from index one.
Periods need not be minimal.

## Both streams cannot have period b

Initial coefficients for q=1 are X[n]=-x[n], Y[n]=-y[n] for n<b-1,
and `X[b-1]=-x[b-1]+y[b-1]-1`, with X/Y interchanged for Y.
Both latter values being signs forces x[b-1]=y[b-1]=r and
X[b-1]=Y[b-1]=-1. Two further exact coefficients are

```text
X[2b-1]=-x[0]-y[b-2]+r,
Y[2b-2]= x[0]-r+1.
```

For clarity, all these local formulas come from the exact truncation

```text
X_infinity = -x + R(y_rev-1)
             + R^2[-z x+(z-1)y_rev+1] + O(R^3).
```

The checker verifies the cleared truncation with independent placeholders
for x and y_rev. Their degrees are at most L, and 3L>2L+1 for b>=4,
so the omitted terms cannot affect any displayed coefficient.

If both streams had period b from index one, the first would equal -1,
so x[0]+y[b-2]=r+1. The second would equal -y[b-2], so the same sum would
be r-1: a contradiction. These indices are positive for b>=4.
At least one stream must therefore have period 2L.

## Period 2L forces type A

Suppose X has that period; interchange x/y if it is Y instead.
At every b-th root xi except +/-1, its generating function has no pole,
because gcd(b,2L)=2. Evaluating the numerator there gives
`y*(xi)=xi x(xi)`. With `y_rev=z^(b-1)y*`, this says

```text
y_rev-x=(alpha+beta z) Qb,  Qb=(z^b-1)/(z^2-1).
```

The polynomial on the left has degree at most b-1; Qb has degree b-2
and exactly the required simple roots. Boundedness also cancels the
double pole at -1: N0(-1)=-2(x(-1)+y(-1))=0. Hence the left side above
vanishes at -1. As Qb(-1)=b/2, alpha=beta.
Its constant and last coefficients give alpha=r-x[0] and beta=y[0]-r.
Equality says x[0]+y[0]=2r, forcing x[0]=y[0]=r and alpha=beta=0.
Thus y_rev=x and both endpoints of x agree: exactly type A.
The b=2 base check closes the remaining case. Together with sufficiency,
this proves the claimed exact count for all even b, without extrapolating
from a finite census.
