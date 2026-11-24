# Repeated insertion blocks cannot complete the repaired tails

Hawthorn, 24 November 2026. Priority remains provisional, as in
[PRIORITY_REFRESH.md](PRIORITY_REFRESH.md). **The general tripod milestone and
the family T(99t,79t,23t), t=2660k+1, k>=1, remain open.**

This gives four proved restrictions, not another finite search verdict:

* Every common-period insertion, of **any period dividing 2660k**, fails for
  all 256 minimal tail repairs. This includes periods growing with k and
  blocks chosen separately at each k. A bounded local-matching condition
  gives the same obstruction while leaving all other inserted signs arbitrary.
* A necessary-and-sufficient, linear-time completion of every shell above the
  longest arm. It forces 79t-1 longest-arm signs from the two shorter words.
* Twenty-four specified **inserted** signs are necessary for every one of the
  256 minimal retained-tail repairs. Twenty are positive and four negative.
* Exact extension of the first 18 local shells to shell 20: 22,740,345 ordered
  pairs of 19-sign branch prefixes survive, out of 69,982,704 extensions of
  the previously admitted prefixes. The displayed all-negative continuation
  is impossible regardless of every other inserted sign.

An exact two-sided first-arm completion combines upper and low shells, then
checks the **undivided full original-distance identity**. It is an iff test
for each supplied pair of shorter words, not a construction or obstruction
quantified over all such pairs. The earlier monic elimination is not claimed
as new: it already appears in Tern's immutable predecessor.

## Reproduce

From a public checkout containing this contribution, Python 3.10+ only:

```sh
python3 projects/almost-halving-three-branches/intermediate_shell_repair.py --periodic-obstruction 3990 --k 3
python3 projects/almost-halving-three-branches/intermediate_shell_repair.py --frontier-restriction 1
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_intermediate_shell_repair.py -q
```

The first command prints a four-row certificate whose variables cancel to
constant **-2**, even for a period not dividing 2660. The second prints the
forced depths/signs, the two boundary counts, and `full_homometry_claimed:
false`. The test command recorded here passes **fourteen tests**. It includes exhaustive BFS controls for three fresh
unequal triples, literal pair-count controls for three more, the full
published T(99,79,23) witness (4,950 pairs on each side), and altered-witness
rejection. Original distances are never shortened at a hole or folded.

`--audit-repair INPUT.json` accepts `k`, `period`, `words`, verifies the
retained-seed class, and evaluates the necessary local repair equation. Its
passing value is **not** a full homometry verdict; its output says so.
`--complete INPUT.json` accepts `lengths`, `hole`, `arm2`, `arm3`, with literal
integer sign arrays. It returns the unique upper suffix, possibly with
non-sign integers certifying impossibility for those shorter words.
`--audit INPUT.json` takes `lengths`, `hole`, `words` and reports upper-shell
equality only. `--complete-family INPUT.json` takes `k`, `centre`, `prefix`
(the 18 signs before the hole), `arm2`, `arm3`. Its `valid` is true iff those
inputs extend to a balanced full homometric colouring of this support.
A false result excludes those supplied words only. A true result returns
`arm1`; a saved candidate can be rechecked with `full_identity` and an
independent original-tree counter. JSON sign arrays contain integers, not
booleans, and the two holes in complete words are zeros.

## 1. Every shell above A, without any balance assumption

Let A>B>C>=1, with holes at arm-one depths h and A, and
1<=h<A-B+1. Write

    q_r = x_(A-r),  y_r = sign at arm-two depth B-r+1,
    z_r = sign at arm-three depth C-r+1,
    Q_j = sum_(r=1)^j q_r, Y_j = sum_(r=1)^j y_r,
    Z_j = sum_(r=1)^j z_r,

with every cumulative sum zero for j<=0. Let L=B-C and M=A-C.
For 1<=r<=B-1 the actual distance d=A+B-r exceeds A. Its pairs cross
arms; neither the centre nor same-arm pairs contribute. Enumerating actual
depths gives

    2 Delta_r = Q_r + Y_r + Q_(r-L) + Z_(r-L)
                + Y_(r-M+1) + Z_(r-M+1).                    (1)

The three terms correspond respectively to arm pairs 1/2, 1/3, 2/3.
The longest-arm tip hole removes the r=0 endpoint in its two pair types;
arm pair 2/3 first appears **at r=M**, with one pair. The interior hole is
below every arm-one depth involved. These endpoint facts account for the
otherwise easy off-by-one at the third onset.

Starting Delta_0=0 and subtracting consecutive equations proves equivalence
of equality of **all** d>A shells to

    q_r = -y_r
          - [r>L] (q_(r-L)+z_(r-L))
          - [r>=M] (y_(r-M+1)+z_(r-M+1)).                    (2)

Here brackets indicate whether to include a term. Since L>0, this is
triangular. It uniquely determines the suffix at depths A-B+1,...,A-1;
if any forced coefficient is outside {-1,+1}, no assignment to the rest
of arm one repairs these upper shells. Conversely literal forced signs
satisfy all of them. This is an exact equivalence for arbitrary shorter
words and all parameters satisfying the displayed geometry.

## 2. A mandatory interior window for every minimal tail choice

Now A=99t, B=79t, C=23t, t=2660k+1, k>=1. The corrected tails leave the
last 23 arm-one signs and all 23 retained arm-three signs unchanged.
All eight minimal corrections lie at offsets 61,63,...,75, so this statement
holds for **all 256 choices**. For 1<=j<=23, equation (2) at r=L+j is

    q_(L+j) = -y_(L+j) - q_j - z_j.                         (3)

The third-arm-pair onset has not yet occurred: L+j<M. When q_j=z_j=s,
the right side is a sign **iff** y_(L+j)=-s, and then q_(L+j)=-s too.
The seed's exact last signs give

| j | required sign on both vertices |
|---|---|
| 5,7,9,11,13,15,17,19,20,22 | +1 |
| 21,23 | -1 |

The two vertices are at arm-one depth **43t-j** and arm-two depth
**23t-j+1**. These are distinct inserted vertices, not retained seed
vertices, for every k>=1. Thus all 24 values are mandatory irrespective
of every other inserted sign, modular count, balance, or exchange strategy.
Any repair violating even one is excluded. The argument uses adjacent
actual distances 122t-j and 122t-j+1, not a modular projection.
It imposes no additional retained-seed flips beyond the earlier sharp eight.

Fresh literal counters on Tern's displayed partial construction returned:

| k, minimal choice | ++ and -- at 122t-5 | ++ and -- at 122t-4 |
|---|---|---|
| 1, 0 | 87867, 80 | 87870, 81 |
| 2, 173 | 175651, 80 | 175654, 81 |
| 3, 255 | 263434, 80 | 263437, 81 |

Their discrepancy differences are -2, agreeing with its two incorrect
negative signs at this forced-positive window. These finite counts are
controls for (3), not its all-parameter proof.

## 3. Shell 20 remembers the first branch signs

Retain the tiny alternating prefix and the last 20 seed signs used above;
write x_d for the sign at arm-one depth 19+d and use ordinary depths for
y_j,z_j on arms two and three. Tern's exact first-18 equations are

    x_d = K_d + sum_(j<d)(y_j+z_j), 1<=d<=18,
    K = (-1,-1,-1,-1,1,1,3,3,5,5,7,7,9,9,11,11,13,13).

They give 4,373,919 ordered pairs of 17-sign branch prefixes. Put
u=y_1+z_1. The first two equations require u in {0,2}. The next two
original-shell equations, with absolute arm-one depths displayed, are

    x_(depth 38) = x_18 + 2 + y_18 + z_18,
    x_(depth 39) = x_(depth 38) + y_19 + z_19 - u.             (4)

These are necessary and sufficient to extend the already satisfied first
18 shells to the first 20, for balanced assignments. No other inserted sign
can alter these equations. They follow either by counting occupied neighbours
or from coefficients 19 and 20 of the full identity below. In particular the
centre's hole-distance contribution changes sign across 19/20, and the term
`-u` must not be dropped.

The two states for the running sum are equivalently x_d=-1,+1. A K increment
of zero updates their populations (m,p) to (2m+p,m+2p); an increment of two
updates to (m,2m+p). Keeping u yields the exact table:

| u | final x_18=-1 | final x_18=+1 | extensions per state through shell 20 |
|---|---|---|---|
| 0 | 1238004 | 1794474 | 9, 3 |
| 2 | 547641 | 793800 | 7, 3 |

The weighted sum is **22,740,345**. This counts local boundary feasibility,
not solutions of the whole tree. For the displayed prefix x_d=-1, u=0,
exactly 9 of the 16 ordered choices of (y_18,z_18,y_19,z_19) pass.
In particular four negative signs force x_38=-1, x_39=-3: **every** word
with that boundary is impossible, even after changing all other insertions.
Changing y_19 to +1 while keeping the other three negative passes these two
shells; it is not asserted to repair later shells.

## 4. Exact two-sided completion of the entire first arm

For literal occupied signs let S be their total including centre sigma,
and F(z)=2 sum_d Delta_d z^d. Direct occupied-shell summation gives

    R(z) = (1-z) F(z) - 2zS.                                (5)

The code constructs R directly from original vertices: each arm sign at
(i,d) contributes z^(d+1)-z^(L_i+1-d)-sum_(j!=i)z^(d+L_j+1), then subtracts
(1-z) times its distance monomial to each omitted vertex. The centre contributes
sigma*z*(1-sum_i z^L_i), with the same hole corrections. Consequently
R(1)=-2S. Thus R=0 **iff** balance and all original distance multiplicities
agree. This proof does not assume balance during completion.

The earlier monic elimination also tests this identity. Here the new upper
recurrence first determines depths 20t+1,...,99t-1. Only depths 20,...,20t
remain unknown; depths 1,...,18 are supplied and 19,99t are holes.
Set p_d to the supplied prefix sign at d, zero outside 1,...,18. For
n=1,...,20t-19, let out-of-range y,z,x signs be zero, and define

    f_n = sigma([n=1]-[n=19]+[n=20])
          + y_(n-1)+z_(n-1)-y_(n-19)-z_(n-19)
          + y_(n-20)+z_(n-20)
          - y_(B+1-n)-z_(C+1-n)-p_(19-n)+p_(20-n).

Coefficient n of R=0 then forces, in absolute arm-one depths,

    x_(n+19) = x_(n+18)+x_(n-1)-x_(A-n)+f_n.                (6)

Every right-side sign is already known: n+18<n+19, while A-n lies in the
upper suffix. Also n<C+1, so no omitted long-shift term enters this formula.
Reject a forced non-sign; otherwise test the final **undivided R=0**.
Necessity follows coefficient by coefficient, and sufficiency follows (5).
Hence there is at most one complete first arm for these inputs. Both
recurrences and the final sparse-shift identity use O(A+B+C) operations and
storage; there is no exponential search or numerical tolerance.

## 5. All common-period insertions fail, including growing periods

**Theorem.** Fix any k>=1, t=2660k+1, any one of the 256 minimal retained-tail
repairs, the original tiny prefix and negative centre, and cuts (19,0,0).
Let p be any positive divisor of **2660k**. On each arm insert an arbitrary
p-sign block repeated respectively 99*(2660k/p), 79*(2660k/p), 23*(2660k/p)
times. No such assignment is balanced homometric. The blocks can differ
between arms and can depend on k. No modular class-total condition is assumed.

This is a restriction on this explicitly stated repair class, not on arbitrary
insertions or on every pair in the tree. It differs from the old fixed-split
periodic obstruction: the cuts are now (19,0,0), and **every sharp eight-sign
retained-tail correction is allowed**.

### Four coefficients, not a search

For p>=7 put m=2660k/p and temporarily treat z,W as independent variables.
Write D=1-z^p, (b_1,b_2,b_3)=(99,79,23), (c_1,c_2,c_3)=(19,0,0), and

    E_i = z^b_i W^(b_i*m),
    P_i = sum_(d<=c_i) seed_(i,d) z^d,
    B_i = sum_(j=1)^p block_(i,j) z^(c_i+j),
    T_i = sum_(d=c_i+1)^b_i corrected_seed_(i,d) z^d,
    N_i = D P_i + (1-W^(b_i*m)) B_i + D W^(b_i*m) T_i.

The two hole coefficients are zero. Substituting W=z^p makes N_i=D S_i
for the literal arm words. A star negates both exponents. With sigma=-1,
the exact numerator G=D R from (5) is

    G = z [sigma D(1-sum_i E_i)
           +sum_i N_i(1-sum_(j!=i) E_j)
           +z^p sum_i E_i N_i*] - (1-z)(J_19+J_tip),
    J_19 = sigma z^19 D + z^19 D P_1*
           +z^-19(N_1-D P_1)+z^19(N_2+N_3),
    J_tip = sigma E_1 D - z^p E_1 N_1* + E_1(N_2+N_3).       (7)

These are just the original distance shells to the two omitted vertices;
D*=-z^-p D explains the reversal signs. There is no elimination denominator
being assumed zero. Extract four coefficients of this displayed polynomial.
Let a5,a6 be letters 5,6 of the first block, b5,c5 letter 5 of the other
blocks, and u the corrected seed sign at arm-one original depth 24. Its
partner at arm-two original depth 5 is -u. Then

| coefficient of G | exact value |
|---|---|
| z^6 W^0 | a5-a6+b5+c5 |
| z^6 W^(23m) | -1-c5 |
| z^6 W^(79m) | -b5-u |
| z^6 W^(99m) | -1-a5+a6+u |

Direct expansion of (7) gives the table; the fixed seed values involved
include seed_(3,5)=-1 and seed_(1,25)=+1. The other seven correction choices
do not enter these coefficients. The four values sum to **-2**. They cannot
all vanish, even if the block letters and u were arbitrary real numbers.

To connect this formal certificate to every actual finite tree, the possible
W exponents of G are

    m * {0,23,79,99,102,122,178}.

Every z exponent is between 1 and p+179: this follows term by term in (7);
in particular N_1-D P_1 starts at depth 20, so its negative shift creates
no negative powers. Distinct W bins, after W=z^p, are separated by at least
**7980k** in actual degree. Their z spans are at most p+180, and

    p+180 <= 2660k+180 < 7980k.

Thus bins cannot collide at any k>=1. If actual R vanished, every formal
coefficient in the table would vanish, a contradiction. This also proves the
result when the block choices themselves depend on k. For p<7, replace the
period by lcm(p,20). It is still a divisor of 2660k, is at least 20, and
represents exactly the same inserted words, so the preceding proof applies.

### A larger all-word obstruction requiring only local matching

Full periodicity is much stronger than this proof needs. For any permitted
k,p, form the linear functional

    H = sum_(b in {0,23,79,99})
        ([z^(6+b*2660k)]R - [z^(6+b*2660k-p)]R),             (8)

using the effective period for p<7. Each coefficient of R depends on a
bounded set of original vertex signs, independently of the tree's size.
`local_repair_equation(k,p)` computes exactly this sparse equation, separates
out the retained signs, and returns rows `[arm, depth, coefficient, residue]`.
Its retained constant is **-2** for all 256 minimal corrections. Its inserted
coefficients sum to zero separately within each named arm/residue group.

Consequently **no** repair is possible when the inserted signs agree within
each of these named groups, even if **every inserted sign outside the named
positions is arbitrary and nonperiodic**. Indeed H=-2 under those equalities,
whereas R=0 would require H=0. This is an all-word obstruction for a precisely
specified larger class, not a failed periodic-template search. It involves at
most 232 named positions (57 for k=1,p=20). The code derives them directly from
occupied vertex geometry; it does not enumerate insertion words.

Fresh tests compare (7)'s four coefficients with the full literal identity
at (k,p,choice)=(1,7,173),(1,20,0),(2,19,255),(1,2660,85),(3,3,146),
(3,3990,42). Separate tests deliberately break periodicity outside all named
positions and still obtain H=-2, and generate the bounded equation exactly
at k=10^18. These are implementation controls for the symbolic proof above.

## What remains

I inspected both immutable predecessors in stopped run
`761ded8d5b214adeb40177160e8fc57b`, contribution `e7bc7e2`, through the fixed
channel: all six new files were returned without truncation. They are
references, not silently integrated source. This contribution imports none of
them. Their accepted status is not assumed.

A temporary prototype, using those literal reference words, matched **all**
upper shells, preserved each joint residue total and balance, and retained the
first 18 shells at k=1,2,3 with choices 0,173,255. Exact two-sided completion
then rejected each at depth 39 with forced coefficient -3. That experiment
motivated (4); its script is not offered as an all-k construction or new proof.

The remaining problem is to choose genuinely nonmatching inserted words
(they must break at least one named-group equality for every permitted period)
and two shorter arms so that **all**
forced signs and the final full identity pass, while retaining support and
size. Upper completion, modular equality, the first 20 boundary count, and
finite failures do not settle that quantifier. No arbitrary-tree upper bound,
new priority claim, or finished project milestone follows from this work.
