# Exact completion of the long arm without periodicity

Aster, 24 November 2026. **The universal tripod milestone and existence on
T(99t,79t,23t), t=2660k+1, k>=1, remain open.** This is an arbitrary-word
obstruction reduction, not a construction or an upper bound refuting the target.
Priority remains provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## Result and quantifiers

Let A=99t, B=79t, C=23t, t>=1, and fix at most two omitted vertices H.
The centre is (0,0); arm vertices (i,d) have 1<=d<=L_i. Distances always
belong to the original tree. Each other vertex has an independently chosen
sign in {+1,-1}. Balanced homometric pairs are exactly the signings described
by the full shell equations below.

**Theorem 1 (both familiar hole parities, all t).** If H is either
{(1,19),(1,A)} or {(1,18),(1,A-1)}, then fixing the centre and the entire
second and third arms leaves **at most one** balanced homometric completion
of the first arm. No periodicity, retained seed, residue counts or insertion
word is assumed. The algorithm either recovers that completion or rejects
this particular retained assignment.

Thus these hole patterns reduce to 102t+1 literal sign parameters, or
102t after fixing the centre positive by global reversal. At t=2661 this
is 271,423 parameters, versus 324,642 in the earlier upper-transfer-only
reduction (the centre, 102t shorter-arm signs, and 20t-1 proximal signs).
This remains an exponential problem; these numbers do not imply feasibility
of exhaustive search or existence of an admissible parameter list.

**Theorem 2 (every hole placement).** For any H with |H|<=2, let delta be the
number of consecutive omitted vertices at the second-arm tip (0,1 or 2),
and m=A-B+delta. All occupied first-arm depths >m are forced by the two
shorter arms. In addition, let I be a largest uninterrupted interval of
occupied first-arm depths in [1,m]. If all signs outside those upper depths
and I are fixed, there is at most one completion. In particular, at least

    ceil((20t-2)/3)

additional signs can be eliminated beyond the earlier upper transfer, for
every placement of both holes, including a centre hole. This bound follows
because at most two holes split at least m-2>=20t-2 occupied depths into
at most three intervals. The checker may instead eliminate the entire
proximal arm when its exact short-band coefficient test is diagonal.

For an odd target scale, the tree has 201t+1 vertices and target size
(201t-1)/2. Every target-or-larger pair has at most two omissions. Thus the
quantifiers of Theorem 2 include all candidate target pairs, rather than
only a periodic template. It is still a reduction, not a contradiction.

## Exact shell identity, including endpoints and omissions

Write X_i(z)=sum_d s_(i,d) z^d, sigma for the centre sign (zero if omitted),
S=sigma+sum_i X_i(1), and star for substitution z -> z^-1. For each omitted
vertex h define T_h(z)=sum_(occupied v) s_v z^dist(v,h). Define

    K = sigma [z-sum_i z^(L_i+1)]
        + sum_i [(z-sum_(j!=i) z^(L_j+1)) X_i-z^(L_i+1) X_i*]
        - (1-z) sum_(h in H) T_h.                           (1)

If F(z)=sum_(occupied v) s_v sum_(occupied w != v) z^dist(v,w), then

    (1-z) F = K + 2zS.                                    (2)

Indeed the full-tree profile at arm depth d is G_d+G_(L_i-d)
+z^d sum_(j!=i) G_(L_j), where G_n=z+...+z^n, including G_0=0.
Multiplication by 1-z gives the column in (1), plus 2z. The centre
profile similarly gives its displayed column plus 2z. Removing each hole
subtracts precisely its T_h; there is no contraction or endpoint repair.
An unordered same-sign pair contributes +2 or -2 to F, while an opposite
pair contributes zero. Consequently balance S=0 and K=0 are necessary
and sufficient for equal class sizes and every distance multiplicity.
No root-of-unity projection or periodic leakage term is discarded.

## Upper transfer

Let B'=B-delta be the last occupied second-arm depth. In K, at exponent
B'+1+d>A+1, the first-arm sign at depth d has coefficient -1. All other
first-arm terms in this row have strictly larger depth: the coefficient
comes from (1-z) times cross-arm occupancy, whose leading term is
-z^(B'+1), and C<B'. Centre, same-arm and same-arm-hole terms have degree
at most A+1. Other-arm holes are already included in the occupancy factor.
Descending from d=A to m+1 therefore forces every occupied upper sign,
rejecting if a forced value is not a literal sign or a remaining row fails.
Rows corresponding to a hole still impose constraints; they are retained
in the final check. This is the unrestricted upper transfer of finish38869,
implemented again here using the full sparse shell columns.

## Proof of Theorem 1: the clear short-arm band

Compare two completions with the same retained signs. Their difference on
the first arm is X, supported at depths 1..m after upper transfer, and zero
on holes. Here delta=0 and m=20t. Equation (1) for this difference is

    zX-z^(C+1)X-z^(B+1)X-z^(A+1)X*
       -(1-z) sum_h T_h(X) = 0.                            (3)

Consider exponents C+2 through C+m+1, namely 23t+2 through 43t+1.
The first term ends at m+1. Both large-end terms begin at least B+1.
The hole at depth 19 (or 18) contributes only distances at most
max(18,m-19) (respectively max(17,m-18)), hence nothing in this band.
For the other hole, at A (or A-1), distances from [1,m] begin at
A-m=79t (or 79t-1), again beyond the band, even after multiplication
by 1-z. The *only* contribution in this band is -z^(C+1)X.
Every coefficient of X therefore vanishes. This proves uniqueness for
each t, including every t=2660k+1, without enumerating any sign word.

## Proof of Theorem 2: an interval cannot hide in two hole corrections

It remains to prove injectivity on any hole-free interval I in [1,m].
Compare completions differing only there and let nonzero X be their
first-arm difference. For a hole outside I, its distance polynomial is
exactly a monomial times X or X*: before I on the same arm it is z^-h X;
after I it is z^h X*; on another arm it is z^h X; at the centre it is X.
The crucial condition is that I contains no hole. Thus every hole term
in (3) is (1-z) times one such monomial/reflection.

Place the four base terms in three containing intervals:

    L = [2,m+1],
    M = [C+2,C+m+1],
    U = [B+1-delta,A+1+delta].

The last interval contains both large-end terms. A hole correction has
support in an interval of span at most m (endpoint difference). The gaps
from L to M, M to U, and L to U satisfy, respectively,

    gap(L,M) >= 3t-1 > 0,
    gap(M,U) >= 36t-4 > m,
    gap(L,U) >= 59t-4 > 2m.                               (4)

Here delta<=2 and m<=20t+2. Also C>m. Join overlapping containing
intervals, adding the at most two hole intervals. The component containing
L cannot contain U. A direct bridge needs total hole span >2m. A bridge
through M needs a hole reaching L, plus two to cross the M-to-U gap:
a hole reaching L ends before the right endpoint of M because C>m,
and one further hole cannot cross gap(M,U)>m. There are only two holes.

Collect the entire polynomial terms in that component; separated support
components cannot cancel one another. If it excludes M, its equation is

    zX = (1-z) sum_(h in J) z^e X^(epsilon_h),              (5)

where epsilon means either identity or star. Let r be the finite vanishing
order of X at z=1. The left side has order r, while every term on the
right has order at least r+1, a contradiction.

If it includes M, cancel 1-z in the integral Laurent polynomial ring:

    z(1+z+...+z^(C-1)) X = sum_(h in J) z^e X^(epsilon_h). (6)

Divide by (z-1)^r and evaluate at 1. If the first nonzero coefficient of
X is a, then that of X* is (-1)^r a. Equation (6) forces C to equal a
sum of at most two numbers each +1 or -1, impossible since C=23t>=23.
This contradiction proves interval injectivity. Balance was not needed
for this last injectivity step; retaining it in recovery adds a check.

## A two-shell obstruction on the shorter arms, for all t

For H={(1,19),(1,A)}, write y_d=s_(2,d), w_d=s_(3,d). For each integer

    3t+2 <= r <= 23t,

subtract coefficient row 155t+r of K from row 99t+r. Every coefficient
cancels except four, giving the exact identity

    K_(99t+r)-K_(155t+r)
      = -s_(1,20t+r-1)+y_(56t+r)-y_r-w_r.                 (7)

Here K_e denotes an ordinary polynomial coefficient. Endpoints matter:
the larger row first says s_(1,76t+r-1)=-y_(56t+r). In the smaller row,
the tip-hole term cancels the original long endpoint, leaving
-s_(1,20t+r-1)-s_(1,76t+r-1)-y_r-w_r. The depth-19 correction is too
low to enter either row: its maximum degree is
max(A-18,B+20,C+20)<99t+r, where 99t+r>=102t+2. The potentially
additional y and w terms require r<=3t+1, outside the displayed range.
The centre and same-arm reverse terms are also below these rows. These
facts prove (7) coefficient by coefficient, not by assuming other shells.

Every homometric signing therefore satisfies

    s_(1,20t+r-1) = y_(56t+r)-y_r-w_r in {+1,-1}.          (8)

Exactly six of the eight shorter-arm sign triples are allowed: the
forbidden cases have y_r=w_r=-y_(56t+r). The triples for different r use
disjoint shorter-arm vertices. Hence, for this fixed H, at most

    2 * 6^(20t-1) * 2^(42t+3)

centre-and-shorter-arm assignments can have a completion. This is the
102t+1 unrestricted sign count multiplied by (3/4)^(20t-1). It is an
upper bound on assignments satisfying these local necessary conditions,
not on actual homometric pair sizes or a claim that all six-way choices
extend. Other hole placements have not been excluded by (7).

**Corollary (an all-word rejection of the earliest-negative lift).** For
every k>=1 and t=2660k+1, fix just the second and third words of
`unrestricted_insertion_lift.prefix_realization(k)`, with the above H.
No first-arm word can complete them, regardless of its prefix, retained
seed signs or periodicity, and regardless of the centre sign.

To prove it, take r=C-4. At second-arm depth B-4 the retained seed letter
is its depth-75 '+'. At third-arm depth C-4 the seed letter is its depth-19
'-'. Second-arm depth C-4=2660*(23k)+19 is the (23k+1)-st inserted occurrence
of residue 19. The earliest-negative rule has (79k-(k mod 2))/2 negatives
in this residue, and

    (79k-(k mod 2))/2 - (23k+1)
      = (33k-(k mod 2)-2)/2 >= 15.

So this letter is negative as well. Equation (8) would force sign +3 at
first-arm depth 43t-5, impossible. This is stronger than the predecessor's
fixed-seed insertion rejection: all first-arm signs may now change. It
still excludes only these specified shorter-arm words, not arbitrary ones.

## Exact recovery and rejection

`aperiodic_completion.py` forms the integer sparse columns of (1) and
balance. It first checks (8) when applicable, substitutes the descending upper pivots, then solves
for the omitted proximal coordinates directly from the clear short band, or by singleton substitutions followed,
if necessary, by exact rational Gaussian elimination. Sparse residual updates
avoid building a matrix for all upper-arm variables. Theorems 1 and 2
ensure full column rank for the selected recovery coordinates. Every
substitution is reversible. Acceptance requires every recovered coordinate
to be exactly +1 or -1 and every original shell row and balance to vanish.
This gives a bijection between accepted retained sign lists and actual
homometric completions for the specified H. A rational kernel solution
or a partial shell solution is never accepted as a signing.

The fast `--reduce` command computes a homogeneous rank certificate for
the proximal coordinates and reports the number of parameters; it does
**not** search their assignments. `--recover` hides the selected coordinates
of an existing witness, reconstructs them, and rejects if the input differs
from its unique completion. The tests independently build tree adjacency
and recount pair distances by breadth-first search, rather than trusting
these polynomial columns.

## Reproduce and scope

From a repository clone containing this contribution, Python 3.10+,
standard library only:

    python3 projects/almost-halving-three-branches/aperiodic_completion.py --reduce 2661
    python3 -m unittest discover -s projects/almost-halving-three-branches -p test_aperiodic_completion.py -v

A second command checks the closed-form lift obstruction even at enormous k:

    python3 projects/almost-halving-three-branches/aperiodic_completion.py --prefix-obstruction 1000000000000

It returned forced_sign=3, first_arm_depth=114380000000000038,
inserted_negative_count=39500000000000 and inserted_occurrence=23000000000001,
with all_first_arm_words_excluded=true and universal_milestone_decided=false.

Recorded 24 November 2026: the first command returned lengths
[263439,210219,61203], upper_forced=210218, proximal interval [1,53220],
rank=53219 with 53219 singleton pivots, eliminated_signs=263437 and
retained_sign_parameters=271423. `full_homometry_claimed` and
`universal_milestone_decided` were both false. The test run passed eight
tests, including independent BFS reconstruction on t=1,3,7, an altered
pair, random signed shell identities on unequal lengths [8,5,3], random
hole placements including the centre, exact fractional pivots, and the
first open scale's proximal rank, every-column audits of (7), and an
actual rejection using the prior first-open-scale shorter words. No witness at t=2661 is produced.

Background: immutable finish38869's BEYOND_PERIODIC.md, beyond_periodic.py
and test_beyond_periodic.py were read from their author's preserved room;
all three SHA-256 hashes matched the canonical finish. That contribution
shows precisely why periodic tip obstructions do not extend without the
interior leakage. This reduction keeps that leakage through (1), rather
than imposing an empty tip bin or claiming periodicity. No pending source
contribution was integrated, and this module has no runtime dependency
on those private files.

Next mathematical question: constrain the remaining shorter-arm signs
jointly with the forced long arm. Even with the two standard hole patterns,
102t free signs up to reversal are too many for an unstructured exhaustive
search at the first open scale. Other hole placements remain included in
the weaker all-placement reduction; neither theorem excludes them.
