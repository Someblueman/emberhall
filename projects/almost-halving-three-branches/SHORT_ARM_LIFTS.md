# Uniform lift families and exact short-arm classifications

Linnet, 23 November 2026. For every even b>=2, integer k>=1 with
`a=2k(b-1)>b`, and odd g>=3, the tree `T(ag,bg,g)` has a full equal
homometric partition. This is a uniform three-parameter construction;
it does not enumerate boundary words and has no bound on b. A second
uniform family covers `T(2bg,bg,g)` for every even b>=4 and odd g>=3.

For even `a>b`, the two-row subdivision equations
`E1=E2=0` for `T(a,b,1)` admit sign words exactly as follows:

| b | Allowed a | Solutions up to global sign |
|---|---|---|
| 2 | Every even a>2 | Three at a=4; one thereafter |
| 4 | Multiples of 6, and a=8 | Three at 6; ten at 8; one at later multiples of 6 |
| 6 | Multiples of 10, and a=8 or 12 | Two at 8; forty at 12; one at every multiple of 10 |
| 8 | Multiples of 14, and a=10,12,16 | Two at 10; ten at 12; 160 at 16; one at every multiple of 14 |

These are **complete classifications of this lift template**, not
obstructions to arbitrary homometric partitions. For instance, the coarse
trees `T(6k+2,4,1)`, k>=2, have full partitions by the existing cell theorem,
but no two-row lift. Another subdivision construction may still work.
Priority remains provisional; the general tripod milestone stays open.

## Reproduce and construct

From the repository root, Python 3.10+ with its standard library:

```sh
python3 projects/almost-halving-three-branches/short_arm_lifts.py --prove-double
python3 projects/almost-halving-three-branches/short_arm_lifts.py --double 10 3 --summary
python3 projects/almost-halving-three-branches/short_arm_lifts.py --prove-uniform
python3 projects/almost-halving-three-branches/short_arm_lifts.py --uniform 10 2 3 --summary
python3 projects/almost-halving-three-branches/short_arm_lifts.py --prove --middle 4
python3 projects/almost-halving-three-branches/short_arm_lifts.py --prove --middle 6
python3 projects/almost-halving-three-branches/short_arm_lifts.py --prove --middle 8
python3 projects/almost-halving-three-branches/short_arm_lifts.py --construct 12 5 --summary
python3 projects/almost-halving-three-branches/short_arm_lifts.py --construct 20 3 --middle 6 --summary
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_short_arm_lifts.py -q
```

`--uniform B K G` constructs the uniform family for arbitrary even B.
`--solve A B` returns every sign-word solution for even B in {2,4,6,8}.
`--construct A G` uses the selected middle length, keeps a full coarse
partition, and inserts the two sign rows for every odd G>=3. Omit
`--summary` for explicit vertex sets. The emitted pairs are checked by
actual distance counting, rather than merely labelled valid by the theorem.
The coarse cell theorem applies to all admitted cases: the cell lengths
are `(a+1,b+1,2)`, have even total, and their difference gcd is one.

Recorded output: b=4 has 512 boundary choices, 503 invalid streams and nine
periodic streams; b=6 has 8192 choices, 8159 invalid and 33 periodic.
The first construction above returns `(60,20,5)`, size 43, target 42,
`homometric: true`, and an empty distance difference. The second returns `(60,18,3)`, size 41, target 40, also with an empty
distance difference. All thirteen focused tests pass, including the middle-eight certificate,
both uniform families beyond the enumerated lengths, and the stream bound.

## Uniform three-parameter proof

The words for a=2k(b-1) are

```text
X1 = (-^(b-1) +^(b-1))^k, X2 = -^b, X3 = +,
Y_i = -X_i.
```

Their combined inserted sign sum is zero. In independent z,R,A, put
`B=zR`, `D=(1-z)(1+R)` and

```text
DX1=-(1-R)(1-A), DX2=-(1-B)(1+R), DX3=D,
(A1,A2,A3)=(A,B,z).
```

Specialize R=z^(b-1), A=R^(2k) only after checking the identity.
Reflection gives `D*=-D/B`. Since Y=-X, E2=-E1, and exact expansion gives

```text
D E1 = sum_i [(DX_i)(1-A_j-A_l) - A_i R (DX_i)*] = 0.
```

The checker verifies this in the independent three-variable Laurent ring,
including the denominator reflection and a nonzero short-word corruption.
D is nonzero in an integral domain. Thus E1=E2=0 for every b,k in the
stated domain. Coarse cell differences have gcd
`gcd(a-b,b-1)=gcd(-1,b-1)=1` and their sum is even, so the existing cell
theorem gives a full coarse partition. The universal odd-subdivision
identity then proves every odd g. At B=10,K=2,G=3 the actual command
returns lengths `(108,30,3)`, size 71 and target 70, with empty distance
difference. This proof is separate from the fixed-b exhaustion below.

## Uniform doubling family

For every even b>=4 take

```text
X = (+^(b-1) -- +^(b-1), -^b, +),
Y = (+ -^(b-3) + -^(b-1) ++, - +^(b-3) --, +).
```

The X sign sum is b-3 and the Y sum is 3-b. In independent z,B with
D=1-z and arm ends `(B^2,B,z)`, their cleared polynomials are

```text
DX1=1-2B/z+2zB-B^2, DX2=-1+B, DX3=D,
DY1=1-2z+2B/z^2-2B/z+2B^2/z^2-B^2,
DY2=-1+2z-2B/z^2+B, DY3=D.
```

Since D*=-D/z, exact expansion of `D E1` and `D E2` gives zero using
the reversed terms `+A_i(DY_i)*` and `+A_i(DX_i)*`. The checker also
rejects a short-word corruption. Specialize B=z^b only afterward.
The coarse cell difference gcd is `gcd(b,b-1)=1`, so full coarse
partitions exist. The same odd-subdivision identity proves every odd g.
The command `--double 10 3 --summary` returns `(60,30,3)`, size 47,
target 46, homometric with empty distance difference.

## Eliminate the long words exactly

Use the definitions of E1/E2 in [TWO_PARAM_LIFTS.md](TWO_PARAM_LIFTS.md).
Write the short words as `x=X2`, `y=Y2`, `p=X3`, `q=Y3`, and fix p=+1
by global sign. There are exactly `2^(2b+1)` boundary choices. Set

```text
A=z^a, B=z^b, F=1-z-B, G=1-z-A,
R1=-Gx+z^(b-1)y*-(1-A-B)p+q,
R2=-Gy+z^(b-1)x*-(1-A-B)q+p.
```

The original equations are `F X1-(A/z)Y1*=R1` and its X/Y interchange.
Reflect the latter and eliminate Y1* to get

```text
P X1 = z^b F*R1 + z^(b-1) A R2* = N0(z)+A N1(z),
P = z^b(F F*-1) = -(1-z)(1-z^b)(1+z^(b-1)).
```

Interchanging X/Y gives the second recurrence. All arithmetic is integer
Laurent polynomial arithmetic, an exact elimination over the rational
function field. P has constant coefficient -1 and degree 2b. Both N0
polynomials have nonnegative exponents; N1 has minimum exponent -1.
Consequently coefficients through degree a-2 are forced by N0 alone.
**The final coefficients require corrections** `-(y[b-1]+q)` for X1 and
`-(x[b-1]+p)` for Y1. Ignoring these incorrectly rejects known solutions;
a dedicated regression test preserves the witness at a=6,b=4.

Generate both forced infinite streams from P. Once the N0 coefficients
are exhausted, the previous 2b coefficients of each word determine the
next pair. If either stream first leaves {+1,-1} at index k, that boundary
choice is impossible for every a>=k+2. Otherwise a repeated joint state
proves periodicity forever. There are at most `2^(4b)` binary joint states,
so this procedure always terminates. The implementation uses the sharper
quadratic bound proved next. No empirical periodicity assumption
or floating point rank calculation is used.

## A uniform quadratic stream bound

For even b put T=b(b-1). The polynomial `(1-z^T)^2` is divisible by P:
one copy supplies the factor `1-z^b`, and the other supplies both
`1-z` and `1+z^(b-1)` (b is even). Exact integer long division checks
this identity for each enumerated b; the factor argument proves it for
every even b. Because deg N0<=2b=deg P, the coefficient streams satisfy

```text
s_(n+2T) - 2s_(n+T) + s_n = 0,  n>=1.
```

Each residue subsequence is affine. Three consecutive affine values
cannot all belong to {+1,-1} unless their slope is zero. Therefore
checking indices through 3T either finds an invalid sign or proves
period T from index one onward. Adding a full 2b-state window gives the
conservative bound `3T+2b+2` used by the implementation. This replaces
an exponential stream-state search; boundary enumeration remains
exponential in b. It is a general algebraic bound, not an extrapolation
of the four observed periods.

## A finite certificate for all lengths

The complete boundary exhaustion produces:

| b | Invalid streams | Latest invalid index | Periodic streams | Their period | Tail starts at |
|---|---|---|---|---|---|
| 2 | 29 | 4 | 3 | 2 | 6 |
| 4 | 503 | 13 | 9 | 6 | 16 |
| 6 | 8159 | 30 | 33 | 10 | 32 |
| 8 | 130943 | 56 | 129 | 14 | 58 |

Check all smaller even a directly, retaining the final-coefficient
correction. Each candidate is substituted into the **original** E1/E2,
so eliminating equations cannot accidentally admit spurious solutions.

For the remaining periodic streams, first check the corrected last signs
(their values depend only on the length residue). Choose one anchor a0 in each even
residue class modulo its period t, beyond the displayed threshold.
Encode the length a=a0+tn word with independent U=z^(tn):

```text
X1 = prefix(a0) + z^a0 block(t)(1-U)/(1-z^t)
     - (y[b-1]+q) z^(a0-1) U,
```

and similarly for Y1. Clear `D=1-z^t` in E1/E2; reflection uses
`D*=-z^-t D`. Each resulting residual is exactly `C0(z)+U C1(z)`.
If both vanish in the independent-variable ring, that boundary gives
solutions for every n>=0. Otherwise all possible cancellations after
U=z^(tn) are decided exactly: nonzero C0 and C1 must be negatives of one
another shifted by a nonnegative multiple of t. Compare their minimum
exponents and every coefficient. There are no exceptional tail indices
for these four b values. Exactly one boundary survives in residue zero,
and none in the other even residues. This proves the table, including
all excluded sign words and all lengths, not just a bounded census.

## Checks and scope

The tests compare finite solution counts with independent exact rational
row reduction of the separately built full E1/E2 coefficient matrix.
They check coefficient corruption, the final-boundary correction, tail
cancellation, and two actual lifted partitions by breadth-first distances
on an independently built adjacency graph, including coverage and balance.

The universal reflection identity from TWO_PARAM_LIFTS.md then proves every
odd subdivision factor for each admitted coarse tree. Neither finite BFS
nor a successful recurrence prefix is used as an infinite-family proof.
Boundary enumeration is exponential in b; the enumerating command deliberately
limits b to 2,4,6,8. Middle-eight enumeration takes roughly half a minute
on this machine; the default middle-four proof takes well under a second. It is linear in a after that fixed boundary enumeration,
apart from the quadratic distance recount when constructing a real pair.
