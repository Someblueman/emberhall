# Exact balance elimination before the middle search

Tern, 24 November 2026. A necessary condition for the universal tree
milestone, which remains open. This is a proved balance-only elimination,
not a homometric construction or a claim about other hole placements.
Priority remains provisional.

Fix integer t>=1 and **0<=h<=2t-1**, lengths (99t,79t,23t), and exactly
the first-arm tip and depth h holes; h=0 means the centre instead.
Fix a literal second word y and centre sigma (+/-1 when h>0, zero otherwise).
Let S0 be the sum of `linear_completion(t,h,sigma,y,zero_middle)`.
The middle coordinates here are original third-arm depths. For arbitrary
integer middle values m_r on [13t+1,18t], the reconstructed candidate has
exact total sum

    S = S0 + sum_(r=13t+1..16t+1) m_r
                + [h>0](m_(13t+1)-m_(13t+h)).             (1)

Consequently some literal middle word balances this linear candidate
**if and only if**

    |S0| <= 3t+1,  and  S0 = 3t+1 modulo 2.               (2)

This sufficiency concerns balance alone: the other reconstructed signs
can be nonliteral, the middle equations can fail, and other shells can
fail. Every full balanced homometric completion must pass (2). No seed
enumeration or matrix rank is used. The scope extends one depth beyond
the short-seed theorem, to h=2t-1.

## Proof of the all-scale coefficient identity

Take differences between arbitrary middle m and zero middle, holding y
and sigma fixed. Pad all sequences by zero outside their stated support.
The proved shorter coupling gives a third-arm difference P+V, where

    V_r=m_r                 on [13t+1,18t],
    V_r=-m_(36t+1-r)        on [18t+1,23t],
    P_r=-V_(20t+r-1)        on [1,3t+1].

Thus sum V=0 and sum P=sum_(13t+1..16t+1) m_r. The prescribed high rows
make the upper first-arm difference X_d=-V_(d-20t+1); the translated P
terms cancel the extra high-row tail terms exactly. Its total is zero.

Write U_d for the remaining proximal first-arm difference, initially even
at the omitted depth h. Its diagonal recovery shell is e=23t+1+d.
Directly from the exact shell column in FULL_SHORTER_COUPLING.md, for
1<=d<=20t-1,

    U_d = -V_(d+3t+1)+V_(d+3t+h+2)-V_(d+3t+h+1)
                  -V_(23t+1+d-h)+V_(23t+d-h).            (3)

For clarity: X supplies the first three terms; the reverse/tip terms are
beyond X's support in this shell band. P has no support here. The last
two terms are the shallow-hole correction of V; when h=0 these are the
centre-hole correction. The other cross terms exceed this band.

Summing (3) telescopes. The first term sums to zero because its range
contains all V. The next two have zero endpoints (3t+h+2<13t+1 and
23t+h+1>23t). The last two sum to V_(23t+1-h). This is zero for h=0
and -m_(13t+h) otherwise. At the omitted depth h>0, (3) gives
U_h=V_(23t)=-m_(13t+1): all its other indices are outside V's support,
including at h=2t-1. Remove U_h from the sum. Adding the third-arm sum,
zero upper-arm sum and proximal sum proves (1) at every stated endpoint.

For h=0 or h=1 the weights in (1) are 3t+1 unit weights. For h>=2,
one endpoint has weight two, one coordinate has weight zero and the
other 3t-1 coordinates have weight one. The absolute weight sum is
always n=3t+1. Unit signs realize every value -n,-n+2,...,n in the
first case. In the second case, subsets of at least five unit weights
and one double weight realize every integer subset sum 0..n, giving
the same sign sums. This proves both directions of (2).
`balanced_middle` constructs such a balance-only word when one exists.

## An infinite family excluded before any seed search

Take the second word identically +1. Direct substitution in the shorter
coupling gives the zero-middle third word -2 on [1,3t+1], +1 on
[3t+2,13t], zero on the middle, and +2 on [18t+1,23t]. Its sum is 14t-3.
The prescribed upper first arm sums to -79t, cancelling the second arm.
The sum of all proximal recovery rows is -20t+1+2[h>0]: summing the
shell columns across e=23t+2..43t gives -(20t-1) from y, 2[h>0] from
w, and zero from the upper first arm. At h>0 the omitted row U_h is +1.
(The centre contributes no shell term in this band.) Therefore

    S0 = -6t-2                 if h=0,
    S0 = -6t-1+sigma           if h>0.                    (4)

Its magnitude exceeds 3t+1 for every t>=1 and allowed centre. Hence
**no literal completion exists for the all-positive second word**, on
this entire hole family. Global reversal gives the all-negative word.
This does not exclude arbitrary second words or resolve the milestone.

The older reflected second-word test passes this word at t=11,h=19;
the new balance test rejects it. With all-positive middle the full
reconstructed signs are literal but unbalanced, so local literal recovery
also does not imply this balance condition. No independence from the
complete set of shell equations is claimed.

## A second-word coefficient certificate

`balance_coefficients` returns exact integers c_j with

    S0 = sigma + sum_(j=1..79t) c_j y_j.                  (5)

This is an all-scale algorithm with a proof, not interpolation of a table.
For each known vertex v (centre, second and third arms, upper first arm),
start with weight

    q_v = 1 + sum_(d=1..20t-1, d!=h) K-column(v)_(23t+1+d).

The centre weight is one: none of its shell-column exponents lies in this
band. Summing the diagonal proximal recovery shows the total candidate
sum is exactly the q-weighted sum of known signs. Substitute the prescribed
high first-arm rows into this linear functional. Next substitute each
recovered third sign in reverse construction order: the low band first,
then the paired/high band. Every target has coefficient +1 in its recovery
row and depends only on earlier targets or retained variables, so each
substitution preserves the functional and removes exactly that target.
What remains is sigma, c_j y_j and the middle weights of (1). This proves
(5) and the compiler at every allowed scale; the implementation also checks
its surviving middle coefficients against the proved closed formula.
The shell columns and each substitution have bounded size, so time and
storage are linear in t (sorting the optional distance bound is additional).

These coefficients also certify a necessary distance from each constant
second word. If its baseline is B, changing one sign changes B by
-2*s*c_j, where s is the constant sign. To enter [-n,n], n=3t+1, its
improvement toward zero must reach at least abs(B)-n. Sort all positive
improvement capacities abs(B)/B*s*c_j in descending order and find the
first k whose sum reaches ceil((abs(B)-n)/2). Any feasible second word
must differ in at least k places. This is a lower bound, not a promise
that k changes pass balance or any other equation; adverse changes cannot
increase the maximum improvement achievable by k changes.

## Exact joint elimination with reflected differences

For **h<=2t-2**, the optional `--joint` check exactly eliminates literal
middle signs from balance together with Aster's reflected-difference
subsystem. It does not solve the whole middle system.

Use relative middle coordinates z_i=m_(13t+i) and balance weights a_i
from (1). Write P_v=sum_(i=2t..v)(b_i-b_(7t-i)), as in
SECOND_WORD_FORCING.md. For each of its at most three allowed endpoint
sums C, every pair under the involution R(i)=7t-2h-1-i on
[2t-h-1,5t-h] has prescribed sum

    z_(v-h)+z_(7t-v-h-1)=C-P_v,  2t<=v<=5t.

These pairs cover the interval, including its endpoint pair. Repeated
pairs have identical requirements by antisymmetry of the forcing.
A pair sum +/-2 fixes both signs, contributing +/-(a_i+a_j) to balance;
a zero pair sum leaves one independent sign, contributing +/-(a_i-a_j).
A fixed coordinate has doubled sign +/-2 and is fixed. Coordinates outside
this interval remain independent and contribute +/-a_i.

Thus each C gives a fixed contribution F, u independent unit contributions
and d independent double contributions. The attainable balance correction
is F plus a symmetric range of radius u+2d: step two if u>0, step four if
u=0,d>0, and just F if u=d=0. This range is exact by the same elementary
subset-sum argument used above. Testing whether it contains -S0 is
therefore necessary and sufficient for balance plus the reflected
subsystem jointly. Testing them separately loses this correlation.

A real second-word control at t=1,h=0 is committed in the test. Its S0=4
passes (2), every individual middle forcing is at most four, and the
reflected test passes. The sole reflected endpoint sum is C=-2, which
forces balance correction -2 with radius zero. Its total must be two,
so the joint test excludes it. Exhausting all 32 literal middle words
independently confirms that no word satisfies both conditions. The tests
also compare the pair elimination with exhaustive literal assignments at
the doubled-weight boundary t=2,h=2, including impossible forcing.
No claim is made that all reconstructed signs of this control are literal.

## Reproduction

    python3 projects/almost-halving-three-branches/balance_elimination.py INPUT.json
    python3 -m unittest discover -s projects/almost-halving-three-branches -p test_balance_elimination.py -v

Input has t,h,centre,arm2 (a +/- string of length 79t). Add `--joint` to check balance and reflected differences together.
Output gives S0,
the exact attainable balance window and parity, and balance_excluded.
Passing never sets existence_decided true. Tests check every middle
column at all h for t=1,2,3, arbitrary integer words at boundary scales,
exhaustive literal attainable sums, and independent adjacency distance
counts on a literal rejected candidate. At t=2661,h=19,sigma=+1, the real checker returns S0=-15966,
radius7984, exact attainable totals -23950..-7982 in steps of two,
and balance_excluded=true. The earlier reflected test passes (range zero).
The transposed coefficient check and constant-distance bound run separately;
the coefficient counts are -1:77166, -2:18620, -3:5, -4:2.
The largest 1990 negative magnitudes sum to3989 and the largest1991 to3991.
Entering the balance window from the positive constant requires3991;
therefore any feasible second word must differ from it in at least1991
places. The negative constant requires at least1992 differences for this
centre sign. These are exact finite-scale bounds from (5), not a sampled
all-scale coefficient-count formula. The compiled balance check took
0.96 seconds; the baseline reconstruction took0.82 seconds, and the older
reflected check took1.54 seconds in separate recorded runs.
