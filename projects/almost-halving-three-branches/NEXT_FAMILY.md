# An optimal pair for the next uncovered family

Rook, 21 November 2026. **The whole family `T(10t,7t,4t)` is now covered:**

> For every integer `t>=2`, there are disjoint homometric sets of size
> `floor(21t/2)`. This size is optimal. The general three-arm problem
> remains open here.

For even t this is one larger than the project target; for odd t it equals
the target. The construction omits one longest-arm tip when t is even,
and the two longest-arm tips when t is odd. The original tree has
`21t+1` vertices. The smaller case t=1 already has two disjoint ten-vertex
paths, and the upper bound below proves that ten is optimal there too.

This is a separate construction. It does not change or repair any published
formula in [PUBLISHED_CASES.md](PUBLISHED_CASES.md). Its literature priority
is **provisional**, with the same unread thesis chapter and other limits
recorded there. No general novelty claim or milestone completion follows.

## Run and check it

From a clone of [Emberhall](https://github.com/Someblueman/emberhall), at its
root, using Python 3.10+ and only its standard library:

```sh
python3 projects/almost-halving-three-branches/next_family.py 11
```

This prints the two vertex sets, omitted vertices and both full distance
profiles. Arm labels and centre `(0,0)` follow PUBLISHED_CASES.md. It can
be piped directly into the existing `published_cases.py --check -` command.
Add `--summary` to omit the sets and profiles. The exact algebra check is:

```sh
python3 projects/almost-halving-three-branches/next_family.py --prove
```

Recorded runs, 21 November 2026:

| t | Original lengths | Size of each set | Target | Certified maximum |
|---|---|---:|---:|---:|
| 11 | 110,77,44 | 115 | 115 | 115 |
| 12 | 120,84,48 | 126 | 125 | 126 |
| 17 | 170,119,68 | 178 | 178 | 178 |
| 23 | 230,161,92 | 241 | 241 | 241 |

The proof command reported `PASS: six Laurent identities, six size
identities, full-partition certificate`. Tests construct the graph and use
breadth-first distances independently of the production distance formula,
including all four odd-table cases, both even-table cases and the smallest
parameters. Moving the centre of either a t=14 or t=17 pair to an omitted
tip preserves its size and disjointness but is rejected as nonhomometric.
These are implementation checks; the identities below establish all t.

## Common proof mechanism

Delete the omitted tips to obtain a prefix subtree, with lengths `a,b,c`.
Its metric on retained vertices is identical to the original metric.
Assign each retained vertex a sign in `{+1,-1}`, with centre sign `+1`.
The positive and negative sets will be A and B. Let `S_i(z)` be the signed
depth polynomial of arm i, and let `A_i=z^(length_i)` (the capital `A_i`
here is a monomial, not the positive vertex set).

For balanced signs, the full-shell equation from PUBLISHED_CASES.md is

```
Q = 1-A_1-A_2-A_3
    + sum_i S_i*(1-sum_(j!=i) A_j) - sum_i A_i*S_i(z^-1).
```

Explicitly, if `L_d=sum_v s(v) N_d(v)`, then
`(1-z)*sum_(d>=1) L_d*z^d = z*Q`. Each retained unordered pair contributes
twice its common sign, or zero if its signs differ. Thus `L_d` equals twice
the difference of the two distance multiplicities. Consequently balanced
signs and `Q=0` prove homometry, including multiplicities.

Write `r=z^h`, temporarily treating z and r as independent Laurent
indeterminates. For `D=1-z^k`, put `P_i=D*S_i`. Inversion gives
`D*S_i(z^-1)=-z^k*P_i(z^-1,r^-1)`. The identity to verify is therefore

```
F = D*(1-A_1-A_2-A_3)
    + sum_i P_i*(1-sum_(j!=i) A_j)
    + z^k*sum_i A_i*P_i(z^-1,r^-1) = 0.                 (1)
```

The tables below completely specify the signs and finite Laurent
polynomials. Ordinary multiplication and integer coefficient collection
give zero in (1), separately for all six rows of parameter classes.
`--prove` performs precisely these operations, without substituting any
finite h and without a symbolic-algebra dependency. Since the Laurent
polynomial ring has no zero divisors, cancellation of nonzero D is valid.

## Even t: two tables

Put `t=2h`, `h>=1`. The retained lengths are `(20h-1,14h,8h)`, so
`(A_1,A_2,A_3)=(r^20/z,r^14,r^8)`. Split arm i into 20,14,8 blocks
respectively. Block j, numbered from zero, has interior depths
`jh+p`, `1<=p<h`. Boundary j has depth jh. Arm 1 has boundaries 1..19;
arms 2 and 3 have boundaries 1..14 and 1..8. The centre is separate.

In an interior word, `+` or `-` is constant; `a` means `(-1)^p`, and `b`
means `-(-1)^p`. Boundary strings list signs in increasing depth order.

| h parity | Arm | Interior words | Boundary signs |
|---|---:|---|---|
| even | 1 | `aaaaaabb----aabbbbbb` | `+++++------++------` |
| even | 2 | `bbbbbbbbbbbbbb` | `--------------` |
| even | 3 | `aa++++aa` | `++++++++` |
| odd | 1 | `ab++++ba++++ab++++ba` | `-++++-++++++-++++-+` |
| odd | 2 | `ba----ab----ba` | `+-----------+-` |
| odd | 3 | `ba----ba` | `+-----++` |

Set `k=2` and `epsilon=(-1)^h`. An interior word's contribution to P_i is
`r^j*(z-r)*(1+z)` for `+`, and
`r^j*(-z-epsilon*r)*(1-z)` for `a`; negate for `-` or `b`.
A boundary of sign s contributes `s*r^j*(1-z^2)`.
These formulas remain valid when h=1 and every interior is empty.

The sum of all signs, including the centre, is an affine expression in h.
For each of the two table classes its slope and intercept both collect to
zero. Hence each side has half the retained order, namely `21t/2`.
Substituting these P_i into (1) gives the two zero Laurent identities.

## Odd t: four tables

Put `t=2h+1`, `h>=1`, and `m=h mod 4`. The retained lengths are
`(20h+8,14h+7,8h+4)`, so the endpoint monomials are
`(z^8*r^20,z^7*r^14,z^4*r^8)`. Define `e_j=jh+floor(j/2)`.
Block j starts at e_j and has nominal length `h+(j mod 2)`.
Its interior is `e_j+p` for `1<=p<h+ell_j`, where
`ell_j=j mod 2`, except that **the last block of arm 1 has ell_j=0**.
This removes the penultimate tip as well as the final tip.
The boundary ranges are again 1..19, 1..14, 1..8, now at depths e_j.
These disjoint interiors, boundaries and centre exhaust the retained tree.

Every four-sign word below repeats starting with its first sign at p=1.
The words are in block order, starting at j=0; `B` lists boundary signs.

```text
m=0
1: ++-+ ++-+ ++++ ++++ ++++ ++++ --+- --+- ---- ---- ---- ---- ---+ ---+ ++++ ++++ ++++ ++++ +++- +++-
B: +++++------++++++--
2: --+- --+- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- -+-- -+--
B: --------------
3: ++++ ++++ ++++ ++++ ++++ ++++ ++++ ++++
B: ++++++++
m=1
1: +-++ -+-+ ---+ ---- ---- -+-- -+-- +-+- +-+- -+-+ -+-+ +-+- +-+- -+-- -+-- ---- ---- ---+ -+-+ +-++
B: ++------++------+++
2: -+-- +-+- +++- ++++ ++++ +-++ --+- --+- +++- ++++ ++++ +-++ +-+- ---+
B: --+++---+++-+-
3: ++-+ ++-+ -+-+ +-+- +-+- -+-+ ++-+ ++-+
B: ++--++++
m=2
1: ++-+ -+++ ++++ ++++ ++++ ++++ --+- +--- ---- ---- ---- ---- ---+ -+-- ++++ ++++ ++++ ++++ +++- +-++
B: +++++------+-++++-+
2: --+- +--- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- -+-- ---+
B: ------------+-
3: ++++ ++++ ++++ ++++ ++++ ++++ ++++ ++++
B: ++++++++
m=3
1: +--+ +-+- +-++ +-++ +-++ +-++ --+- +-++ +-+- -+-+ -+-+ +-+- +++- --+- +++- +++- +++- +++- +-+- ++--
B: -++++-+-++---------
2: -++- -+-+ -+-- -+-- -+-- -+-- -+-+ -+-+ -+-- -+-- -+-- -+-- -+-+ ++--
B: +-------------
3: +++- -+-- -+-+ +-+- +-+- -+-+ -+-- +++-
B: ++--++-+
```

Here set `k=4`. For a word `w_1,w_2,w_3,w_4`, extend w periodically to
all integer indices. Its contribution to P_i is the finite numerator

```
z^floor(j/2)*r^j *
  (sum_(p=1)^4 w_p*z^p - r*z^ell_j*sum_(q=0)^3 w_(m+ell_j+q)*z^q).
```

This follows by multiplying the finite periodic word by `1-z^4`:
all internal terms cancel, leaving its first period minus the period
beginning at the excluded endpoint. A boundary sign s contributes
`s*z^floor(j/2)*r^j*(1-z^4)`.

For balance write `h=4q+m`. An interior has sign sum
`q*sum_(p=1)^4 w_p + prefix_w(m+ell_j-1)`.
Here `prefix_w(n)=sum_(p=1)^n w_p` for n>=0, and
`prefix_w(-1)=-w_4`. Summing these expressions, boundaries and centre gives
zero q coefficient and zero constant in each table class. Both sets
therefore have `(21t-1)/2` vertices. Equation (1) collects to zero for each
of the four classes, proving homometry for every odd t>=3.

## Optimality, including the odd case

For even t, disjointness gives the matching bound `floor((21t+1)/2)`.
For odd t, it remains to rule out a full partition of the *original* tree.
Suppose such a partition existed, and form Q using its full lengths
`(10t,7t,4t)` and centre sign s0. The same formula holds with its initial
term multiplied by s0. Let `q_j=[z^j]Q`. Direct coefficient collection gives

```
sum_(j=0)^17 w_j*q_(jt) = 2*(s0+s(1:3t)+s(2:t)),
w = (1,1,0,-1,1,0,-1,-1,2,-1,-1,0,1,-1,0,1,-1,-2).
```

To reconstruct this short certificate, expand Q at scale t=1: all variables
cancel except the three displayed ones, each with coefficient 2. At any
scale, shifts and reflections by arm lengths preserve residues modulo t;
coefficients at multiples of t involve only depths at multiples of t.
Thus the same 22-variable cancellation proves the displayed identity for
arbitrary t, not just tested t. A full homometric partition would have Q=0,
forcing three signs in `{+1,-1}` to sum to zero. This is impossible.
Consequently its maximum size is at most `(21t-1)/2`, as constructed above.

This certificate **must not** be applied unchanged after omitting vertices:
then the shell correction from PUBLISHED_CASES.md is nonzero. The lower
bound here was instead proved on the complete retained prefix subtree.

## Scope and next step

The former limitation `10t+3` was a bound on the old construction menu.
It remains a correct statement about that menu, but no longer a limitation
on the results proved in this project. The new optimum is `floor(21t/2)`.
Finite solver experiments were used to discover the tables; neither those
experiments nor their solver statuses are premises of the proof.

A non-author still needs to reconstruct these six identities and the
three-sign certificate. The general milestone also needs arbitrary unequal
lengths beyond the covered families. This document does not claim either
acceptance has occurred. The next mathematical step is to look for a common
construction behind the periodic words or select the next uncovered ratio
family; another finite census alone will not close the milestone.
