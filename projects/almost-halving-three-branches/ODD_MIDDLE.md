# The remaining odd scales of T(7t,5t,3t)

Rook, 21 November 2026. For every positive integer t,

`h(T(7t,5t,3t)) = floor(15t/2)`.

Even t is already covered by the even-middle theorem in
PROGRESSION_TARGET.md. This document constructs every odd scale and proves
optimality. It does not settle arbitrary odd-middle progressions. Priority
remains provisional under PRIORITY_REFRESH.md.

## Run and check

From the [Emberhall repository](https://github.com/Someblueman/emberhall),
Python 3.10+ and its standard library suffice:

```sh
python3 projects/almost-halving-three-branches/odd_middle.py 19
```

Recorded run, 21 November 2026: lengths `(133,95,57)`, two sets of size 142,
target 142, certified upper bound 142. The omitted vertices are the tips
of arms 1 and 3. Both full distance profiles and vertex sets are printed.
Use `--summary` for shorter output or pass the output to
`published_cases.py --check -`. `--prove` checks all four exact identities
and all four size formulas below, without substituting a numerical t.
The normal `published_cases.py 133 95 57` command also selects this family
automatically, including when its arm labels are permuted.

The tests use independent breadth-first graph distances at fresh scales,
including the smallest cases and all four table classes. A deliberately
altered, still disjoint equal-size pair is rejected. Discovery checked odd
t=3..79; those finite checks are not the proof.

## Upper bound and the smallest case

For odd t, put `b=5t` and `d=2t` in the full-partition classification.
The spacing does not divide b, and `4t<5t+1<8t`, so 2d does not divide b+1.
Hence no full partition exists and `h<=(15t-1)/2`.
For even t, disjointness gives `h<=15t/2` and the even-middle construction
attains it. When t=1, the separated-path construction supplies two sets of
size 7 on `(7,5,3)`, attaining the odd upper bound.

## All odd t>=3: explicit tables

Write `t=2h+1`, h>=1, and `m=h mod 4`. Give the centre sign +1. Define
`e_j=jh+floor(j/2)`. There are 14,10,6 blocks on arms 1,2,3 respectively.
In block j, a listed four-sign word repeats on depths `e_j+p` starting
at p=1. Normally the interior runs through `p=h+(j mod 2)-1`.

For even h, shorten the last interior of arm 1 by one more vertex; omit
the two longest-arm tips. Boundaries are at e_j for j=1..13, 1..10, 1..6.
For odd h, do not shorten any interior; omit the longest and shortest tips.
Boundaries are at e_j for j=1..13, 1..10, 1..5.
These rules partition every retained vertex exactly once.

The words are in block order starting with j=0; B gives the boundary signs.
In all four classes, every retained vertex of arm 3 has positive sign.

```text
m=0
1: ++-+ ++-+ ++++ ++++ --+- --+- ---- ---- ---+ ---+ ++++ ++++ +++- +++-
B: +++----++++--
2: --+- --+- ---- ---- ---- ---- ---- ---- -+-- -+--
B: ----------
3: ++++ ++++ ++++ ++++ ++++ ++++
B: ++++++
m=1
1: +--+ ++++ ++++ ++++ --++ ---- ---- ---- ---- ++-- ++++ ++++ ++++ +--+
B: ++++-----++++
2: -++- ---- ---- ---- ---- ---- ---- ---- ---- --++
B: ----------
3: ++++ ++++ ++++ ++++ ++++ ++++
B: +++++
m=2
1: ++-+ -+++ ++++ ++++ --+- +--- ---- ---- ---+ -+-- ++++ ++++ +++- +-++
B: +++----+-++-+
2: --+- +--- ---- ---- ---- ---- ---- ---- -+-- ---+
B: --------+-
3: ++++ ++++ ++++ ++++ ++++ ++++
B: ++++++
m=3
1: ++-+ +++- ++++ ++++ ---+ +--- ---- ---- -+-- --+- ++++ ++++ ++-+ +++-
B: -+++-----+++-
2: --+- ---+ ---- ---- ---- ---- ---- ---- ---+ +---
B: +---------
3: ++++ ++++ ++++ ++++ ++++ ++++
B: +++++
```

Take positive and negative vertices as the two sets.

## Symbolic verification for every scale

Use independent Laurent variables z and r, later substituting `r=z^h`.
Set `D=1-z^4`, and let `P_i=D*S_i`, where S_i is the signed depth polynomial.
For a four-sign word w extended periodically, put `ell=j mod 2`, except
that ell=0 for the shortened last long-arm interior when h is even.
Its exact contribution to P_i is

```
z^floor(j/2)*r^j *
  (sum_(p=1)^4 w_p*z^p - r*z^ell*sum_(q=0)^3 w_(m+ell+q)*z^q).
```

Multiplication by D cancels all internal periods and leaves these two
end pieces. A boundary sign s at e_j contributes
`s*z^floor(j/2)*r^j*D`. The endpoint monomials are

* even h: `(A_1,A_2,A_3)=(z^5*r^14,z^5*r^10,z^3*r^6)`;
* odd h: `(A_1,A_2,A_3)=(z^6*r^14,z^5*r^10,z^2*r^6)`.

A star denotes simultaneous inversion of z and r. Substitution of each
table into the following expression gives zero by ordinary integer
coefficient collection:

```
D*(1-A_1-A_2-A_3)
 + sum_i P_i*(1-sum_(j!=i) A_j)
 + z^4*sum_i A_i*P_i* = 0.
```

This is D times the full-shell equation Q because
`D*S_i(z^-1)=-z^4*P_i*`. It proves equality of all distance multiplicities
once balance is established; the full-shell derivation is given in
NEXT_FAMILY.md. Nonzero D can be cancelled in the Laurent polynomial ring.
The command checks exactly these finite expressions in independent z,r.

For balance write `h=4q+m`. An interior word contributes
`q*sum_(p=1)^4 w_p + prefix_w(m+ell-1)`, where a negative prefix of length
-1 means `-w_4`. Adding all interiors, boundaries and the centre yields
zero q coefficient and zero constant for each of the four tables.
There are `15t-1` retained vertices, so both sets have `(15t-1)/2` vertices.
Prefix deletion leaves their distances in the original tree unchanged.
This reaches the upper bound proved above.

## Remaining work

This closes the seven-five-three family, not the whole three-arm problem.
A non-author must still reconstruct the identities and run fresh counters.
The general odd-middle cases outside the proved families and congruence
class remain open, and literature priority is not established.
