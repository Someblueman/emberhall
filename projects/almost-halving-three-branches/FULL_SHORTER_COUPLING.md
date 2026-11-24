# A short middle seed determines both missing arms

Tern, 24 November 2026. Continuation of SHORTER_ARM_ELIMINATION.md.
**Strongest reduction:** for 0<=h<=2t-2, the second arm and a contiguous
block of **2h+2** third-arm signs determine at most one full completion.
For h=19 and every resistant scale t=2660k+1, k>=1, this leaves **79t+41**
retained signs. The wider shallow-hole family first reduces to 5t third-arm
signs; a sparse recurrence then proves the short-seed result. Full operator
invertibility is not assumed and is false for some other scales.
The universal tripod milestone remains open; priority remains provisional.

## Hole and sign quantifiers

For every integer t>=1 let A=99t, B=79t, C=23t. Fix exactly the holes
H={(1,h),(1,A)} with **1<=h<=20t-1**, also allowing **h=0** to mean
H={(0,0),(1,A)}. Distances use the original tree. All occupied signs are
literal +/-1; the centre sign sigma is zero exactly when omitted. There
is no periodicity assumption. No other hole placement is covered here.
Use x,y,w and K=(1-z)F-2zS as in the predecessor. Indices outside an arm
or at a hole have value zero. Balanced homometric signings have S=K=0.

For each integer **1<=r<=3t+1**, put e=43t+r. Using the predecessor's B_r,

    w_r + w_(20t+r-1) + B_r(y) + y_(76t+r-1) = 0.          (1)

Every index displayed is within its arm: 20t<=20t+r-1<=23t and
76t<=76t+r-1<=79t. These equations fill the low band omitted previously.

**Reduction theorem.** Fix sigma, the entire second arm, and third-arm
signs at **13t+1 through 18t**, inclusive. First use the predecessor's
equations to force depths 3t+2..13t and the reflected partners
18t+1..23t. Then (1) forces all remaining depths 1..3t+1, since its
other third-arm index lies in the already forced interval 20t..23t.
Every forced value must be a literal sign. Check every unused equation
and apply the predecessor's unique first-arm recovery and full shell check.
There is at most one full completion of these retained signs. This leaves
79t+5t+1=84t+1 signs, or 84t when h=0; global reversal removes another.
At t=2661 and h=19, the retained count is **223,525**, versus the earlier
271,423. This still leaves exponentially many assignments, not solutions.

## Exact proof of the additional low band

As before write E_j=K_(99t+j). For 1<=j<=3t+1, the high row now retains
the two extra cross terms which were absent in the predecessor:

    E_j-E_(56t+j) = -x_(20t+j-1)+y_(56t+j)-y_j-w_j
                   -y_(76t+j-1)-w_(20t+j-1).             (2)

At j=1, e=A+1 deserves care: the original centre contribution -sigma
cancels the tip-hole contribution +sigma. The endpoint x_A is absent.
The shallow-hole cross corrections end at B+h+1<=99t, below this row;
its same-arm corrections end at A-h+1<=A+1. For h=0 the centre is absent
and the first-arm correction ends at A, since x_A is a hole. Thus no
unlisted term survives, including at j=1. The other long sign is removed
by the predecessor's high singleton row E_(56t+j).

The low row (6) in SHORTER_ARM_ELIMINATION.md remains valid for
43t+1<=e<=46t+1 here. Its smallest first-arm coordinate is 20t>h.
Third-arm shallow-hole corrections end at C+h+1<=43t; all centre
and third-arm terms in that low row are therefore absent. Substitute
(2) and the same high singleton rows used previously. The exact identity,
valid even for unbalanced arbitrary integer signings, is

    w_r+w_(20t+r-1)+B_r(y)+y_(76t+r-1)
      = K_e + E_(e-20t)-E_r+E_(56t+r)
            -E_(36t-r+1)-E_(e+h-20t+1)+E_(e+h-20t).       (3)

Each singleton index is in [23t+1,79t]. This proves (1) for every stated
integer, not by interpolation from finite cases. Together with the earlier
proof it proves the reconstruction and its retained-sign count.

The new rows are strictly stronger than the predecessor's rows: on the
actual t=1, h=19 size-100 pair, exchange signs w_1 and w_2. Balance and
all earlier coupling rows survive, since none uses these two depths.
Equation (1) fails and independent BFS rejects the altered pair. At every
scale, all-positive shorter words pass the earlier rows; flipping w_1
changes only the new low constraints. No existence conclusion follows.

## What remains on the middle block: a proved operator

There is a further exact constraint for **0<=h<=2t-1**. It describes
homogeneous differences of completions having the same second arm and
centre; it does not treat the original literal signs as zero or antisymmetric.
Write V for their third-arm difference restricted to [13t+1,23t], padded
by zero elsewhere. The already proved coupling gives

    V_j = -V_(36t-j+1) on this interval.                   (4)

Its lower half z_j=V_j, 13t+1<=j<=18t, contains the remaining 5t variables.
For each r in that lower half a necessary homogeneous equation is

    V_r - V_(r+3t+1) + V_(r+3t+h+2)
                         - V_(r+3t+h+1) = 0.             (5)

Thus (5), folded by (4), has at most four integer terms per row on 5t
variables. `middle_operator` returns those coefficients. It does **not**
claim their independence or invertibility, and no smaller retained-sign
bound is inferred from it.

Here is an all-scale derivation. Put P=W restricted to [1,3t+1]. All other
third-arm differences outside P and V vanish. The high transfer and (1)
force the first-arm difference to have the form

    X = U - z^(20t-1)V,   supp(U) subset [1,20t-1], U_h=0. (6)

In the clear middle recovery band, the low term from the upper first-arm
block contributes to U; it must not be discarded. For d in that band,
its contribution is exactly

    -V_(d+3t+1)+V_(d+3t+h+2)-V_(d+3t+h+1).              (7)

The only other contribution comes from the shallow-hole correction of W,
and is supported at depths <=h. Therefore

    supp(U) subset [1,h] union [10t-h-1,20t-1].            (8)

For 13t+1<=r<=18t, the reflected depth 20t-r-1 lies in [2t-1,7t-2].
It misses (8); if its lower end equals h, U_h=0 because it is a hole.
The same proof applies when h=0. At shell exponent B+1+r, the terms
-z^(B+1)X_upper and -z^A V cancel identically. Other possible terms are
outside this exponent band, leaving exactly -U_r-V_r. Since r>h,
substitute (7) to obtain (5).

For nonhomogeneous second-arm data, `linear_completion` implements the
prescribed high and middle rows with arbitrary integer middle values.
If c_r is K_(B+1+r) for zero middle values, the true residual at middle
vector z is **c_r - (middle_operator z)_r**. This supplies exact forcing
for future work, without asserting that every prescribed row already solves
all shells or that an integer candidate is a literal-sign completion.

A tempting stronger singleton assertion was tested and rejected: at t=1,
h=0, middle difference z_14=1 and all others zero gives K_98=1, although
-z_18=0. The missing term is a proximal first-arm contribution. A regression
control preserves this failure; neither a two-arm uniqueness theorem nor
a 79t+1 retained-sign claim is made.

## A constant-size middle seed: an all-scale theorem

**Theorem.** Suppose **0<=h<=2t-2**. Fix the second arm, the occupied
centre sign, and the consecutive third-arm signs at depths
**15t-h-1 through 15t+h**, inclusive. There is at most one balanced
homometric completion of both missing arms. The interval contains 2h+2
signs and lies within the free middle block. The retained count is
**79t+2h+3** when h>0, and **79t+2** when h=0. This is a literal-sign
parameter bound, not a claim that the parameters extend to a solution.
For h=19 the condition is t>=11, hence includes every remaining resistant
scale t=2660k+1, k>=1. At t=2661 the bound is **210,260** signs, versus
the predecessor's 271,423. All other hole placements remain unresolved.

Here is the complete proof. It suffices to show that two completions
with these same retained signs have zero difference. Use relative middle
coordinates i=1..5t, so z_i=V_(13t+i), and extend to i=1..10t by
v_i=z_i on the lower half and v_i=-z_(10t+1-i) on the upper half.
Equation (5) becomes, with D=3t+1,

    z_i-v_(i+D)+v_(i+D+h+1)-v_(i+D+h)=0.                (9)

For **2t<=i<=5t**, every shifted index is in the upper half, except
possibly the last index 10t+1, which cannot occur because h<=2t-2.
Writing j=7t-i, this says exactly

    E_i := z_i+z_j+z_(j-h)-z_(j-h-1)=0.                 (10)

Both i and j lie in [2t,5t]. Subtract E_j from E_i. If
delta_a=z_a-z_(a-1), the result is the reflection symmetry

    delta_a=delta_(7t-2h-a),  2t-h<=a<=5t-h.            (11)

Subtract E_(i-1) from E_i and apply (11) to each reflected difference.
For **2t+h+1<=i<=5t**, all three applications stay in that exact interval:

    delta_i-delta_(i-2h-1)-delta_(i-h-1)
                                      +delta_(i-h)=0.  (12)

Its characteristic polynomial is (q^h+1)(q^(h+1)-1). For h>=1 this is
a forward recurrence of order 2h+1. For h=0 it is
2 delta_i=2 delta_(i-1), with the same uniqueness over the rationals.
Thus the consecutive z values at **2t-h-1..2t+h** determine all z
from 2t-h-1 through 5t. Every lower coordinate
1<=i<=2t-h-2 is then forced by (9), whose three shifted indices are
inside this already determined upper region. If the seed difference
vanishes, every coordinate vanishes. The low-band theorem and full
first-arm uniqueness finish the proof. No matrix rank was used.

The implementation also carries exact inhomogeneous forcing. If the right
side of (9) is b_i, define R_a=b_(7t-h-a)-b_(a+h). Then the right side
of (12) is

    c_i=b_i-b_(i-1)+R_(j+1)+R_(j-h+1)-R_(j-h).

`recover_middle` uses this recurrence, fills the lower coordinates using
(9), and checks **every** original middle equation afterward. A failed
integer division or compatibility row rejects the seed. For known second
arm and centre, `linear_completion` with zero middle values supplies b_i
as its shell residual K_(92t+1+i); the affine identity proved above
justifies this forcing. `recover_from_seed` then reconstructs both arms
and checks literal signs, balance and every K coefficient before accepting.
This is a complete candidate verifier, not acceptance from selected rows.

## A genuine operator kernel, without a full-completion claim

The middle operator need not be invertible. If h<=2t-2 and
g=gcd(3t,h+1), it has at least **floor(g/2)** independent integer kernel
vectors. In relative coordinates take any g-periodic v_i satisfying
v_i=-v_(10t+1-i). Each paired residue class supplies one vector;
fixed reflection residues supply none. There are floor(g/2) pairs because
10t+1 is odd, and the lower 5t coordinates contain all residues.
Every shifted argument in (9) stays within 1..10t, while D=1 modulo g
and h+1=0 modulo g. Its four terms therefore cancel identically.
For h=19 and every t>=11 divisible by five this gives two independent
operator-kernel vectors. They are not homometric completions: other shells
can fail, and these difference vectors are not literal signings. The
resistant t=2660k+1 has gcd(3t,20)=1, so this particular lower bound is
zero there. No converse or complete kernel characterization is claimed.
`periodic_middle_vector` generates these exact controls without a search.

## Runnable reconstruction and recorded checks

The new module uses only the standard library and the preceding shorter-arm
module. Input JSON contains `t`, `h`, `centre`, the full `arm2` word, and
`middle_third`, the 5t signs in increasing depth order from 13t+1 to 18t:

    python3 projects/almost-halving-three-branches/full_shorter_coupling.py INPUT.json
    python3 -m unittest discover -s projects/almost-halving-three-branches -p test_full_shorter_coupling.py -v

The default CLI fills the full third word, rejects nonliteral forced values, and
checks every old and new shorter-only row. It returns the original parameter
format for the predecessor's first-arm checker. Passing this default mode does not establish a first-arm completion, balance
or existence; these flags remain false. For h<=2t-2 replace `middle_third`
with `middle_seed`, the 2h+2 signs in the theorem's interval, and add
`--seed`. This mode checks the entire candidate and returns a pair only
when literal signs, balance and all shells pass.

Recorded: eight tests pass. Independent adjacency BFS verifies every low
certificate row at t=1,2,3, h=0,1,20t-1 and verifies the affine middle
operator on random integer assignments at h=0,1,2t-1. Coefficient controls
also reach t=7. The actual size-100 witness reconstructs its full third
word from five signs, and the balanced w_1/w_2 alteration is rejected by
BFS and the new rows while all predecessor coupling rows pass. At t=2661,
h=19, all-positive inputs fill 61,203 necessary rows and report 223,525
retained signs; they are not homometric solutions. As before, tests use
immutable predecessor dependencies149fbe7 from a temporary module path;
independent integration d7c7ffff was observed in the journal during this run.
Exact affine seed reconstruction is checked at t=1,2,3,11,15,31,2661.
A real `--seed` CLI run at t=2661,h=19 with all-positive second word
and forty positive seed signs finished in 3.08 seconds. It returned
accepted=false, balance=-7982, 23,955 failed shell rows, zero nonliteral
values, and retained_signs=210260. This is an exact rejected candidate,
not a scientific success inferred from a passing necessary subsystem.
A periodic operator-kernel control at t=15,h=19 passes the selected
middle rows under independent BFS but fails other shells, preserving the
distinction between the necessary operator and a full completion.

Next: determine the exact kernel and forcing compatibility of (5),
including exceptional small scales and h=19 at the resistant scales.
Even invertibility would leave literal signs, support, balance, other shell
rows, and all other hole placements to settle. No finite matrix census is
an all-scale proof, and no local-hole theorem is a universal obstruction.
