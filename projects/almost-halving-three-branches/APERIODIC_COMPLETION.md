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

**Theorem (all hole placements, all t).** Fix H with |H|<=2, the centre
sign (zero if omitted), and every sign on the second and third arms.
There is **at most one** balanced homometric completion of the entire
first arm. No periodicity, retained seed, residue counts or insertion
word is assumed. The algorithm either recovers that completion or rejects
this particular retained assignment.

Every hole placement therefore reduces to at most **102t+1 literal sign
parameters**, or at most 102t after global reversal. More precisely the
retained count is 102t+1 minus the number of holes outside the first arm.
At t=2661 the maximum is 271,423 parameters, versus 324,642 in the earlier
upper-transfer-only reduction for holes {(1,19),(1,A)}. The latter kept the
centre, 102t shorter-arm signs, and 20t-1 proximal signs. This remains an
exponential problem; these counts imply neither feasible exhaustive search
nor an admissible parameter list. The hole choices must still be considered.

**A wider cone.** The same entire-first-arm uniqueness holds for any
A>B>C and a fixed H with |H|<=2 whenever, with delta and m as below,

    C>2,  C>m,  B-C-m-delta>m,  B-m-delta>2m.

These are sufficient conditions, not a characterization. In particular,
the hole-independent bounds C>A-B+2, 3B>2A+C+6, and 4B>3A+8 imply them
for every H. They hold for the project family and for many other unequal
triples. The checker accepts parameter inputs throughout this proved cone;
its convenient `--reduce t` command specializes to the project family.

For an odd target scale, the tree has 201t+1 vertices and target size
(201t-1)/2. Every target-or-larger pair has at most two omissions. Thus the
quantifiers of the theorem include all candidate target pairs, rather than
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

## Proof of full proximal injectivity

Compare two completions with the same retained signs. Upper transfer
makes their difference vanish above m=A-B+delta. Let X be the remaining
first-arm difference polynomial, and suppose it is nonzero with least
and greatest nonzero depths p and q. Thus 1<=p<=q<=m<C; in the project family m<=20t+2. For this
difference, (1) is

    zX-z^(C+1)X-z^(B+1)X-z^(A+1)X*
       -(1-z) sum_h T_h(X) = 0.                            (3)

Put w=q-p+1<=m. A hole not strictly between p and q on the first arm has
T_h(X) equal to a monomial times X or X*: before the support it is z^-h X;
after it, z^h X*; on another arm it is z^h X; at the centre it is X.
Its entire correction (1-z)T_h has a containing interval of span at most w.
Span means endpoint difference, not number of integer coordinates.

**Case 1: no hole lies strictly between p and q on the first arm.**
All hole operators have that monomial/reflection form. Place the base
terms in three containing intervals:

    L = [2,m+1],
    M = [C+2,C+m+1],
    U = [B+1-delta,A+1+delta].

The last interval contains both large-end terms. These disjoint intervals
satisfy

    gap(L,M) = C-m+1 > 0,
    gap(M,U) = B-C-m-delta > m,
    gap(L,U) = B-m-delta > 2m.                               (4)

On (99t,79t,23t), these gaps are at least 3t-1, 36t-4 and 59t-4.
Join overlapping containing intervals, adding the at most two
hole intervals. The component containing L cannot contain U: a direct
bridge needs total hole span >2m; a bridge through M requires one hole
to reach L and two more to cross its right-hand gap. Indeed a hole
reaching L ends before the right endpoint of M because C>m, and one
further interval cannot cross gap(M,U)>m. There are only two holes.

Collect the entire polynomial terms in the L component; separated support
components cannot cancel one another. If it excludes M, its equation is

    zX = (1-z) sum_(h in J) z^e X^(epsilon_h),              (5)

where epsilon means identity or star. Let r be the finite vanishing order
of X at z=1. The left side has order r, while every right-hand term has
order at least r+1, a contradiction. If the component includes M, cancel
1-z in the integral Laurent polynomial ring to get

    z(1+z+...+z^(C-1)) X = sum_(h in J) z^e X^(epsilon_h). (6)

Divide by (z-1)^r and evaluate at 1. If the first nonzero coefficient of
X is a, that of X* is (-1)^r a. Thus C must equal a sum of at most two
numbers each +1 or -1, impossible since C>2 (and C=23t>=23 in the project family).

**Case 2: a hole lies strictly between p and q on the first arm.**
Such a hole's T_h(X) has degree at most q-p-1, so its correction lies
entirely below q. All low terms, including zX and these internal-hole
corrections, lie in L'=[0,q+1]. The middle term lies in
M'=[C+p+1,C+q+1]. At most one remaining hole is outside the support;
its correction is a monomial/reflection of X times 1-z, with span at
most w. The gap from M' to U exceeds m, so this single interval cannot
connect M' to U. Internal-hole intervals stay in L' and cannot bridge
that gap or reach M'.

If the external interval connects M' to L', its right endpoint is at
most q+1+w<C+q+1, since w<C. But the coefficient at C+q+1 of the middle
term is -[z^q]X != 0, and no other term in that component reaches it.
That is impossible. Consequently the M' component excludes both L' and
U. Its equation is either a lone nonzero -z^(C+1)X, or

    -z^(C+1)X = (1-z) z^e X^(epsilon),

again impossible by vanishing order at 1. This also handles two internal
holes, when there is no external correction at all.

Both cases contradict X!=0, proving injectivity on **all proximal
coordinates simultaneously**, even when holes cut that support. Combined
with upper transfer this proves the stated entire-first-arm theorem.

## A particularly simple recovery band

For H={(1,19),(1,A)} or {(1,18),(1,A-1)}, delta=0 and m=20t. In (3),
consider exponents C+2 through C+m+1, namely 23t+2 through 43t+1.
The low term ends at m+1; both large-end terms start at least B+1.
The shallow hole contributes distances at most max(18,m-19), or
max(17,m-18), entirely below this band. The far hole contributes only
distances at least A-m, or A-1-m, beyond the band. Thus the only proximal
term there is -z^(C+1)X. Each remaining sign is recovered directly from
its own row. The general theorem above is stronger: it covers arbitrary
hole positions where this diagonal-band shortcut fails.

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

## An independent radial-polynomial certificate beyond the cone

There is also a sufficient injectivity test with no length-separation
assumption. Map the occupied first arm to coordinates q=d, the centre
to zero, and both other arms to q=-d, retaining their multiplicities.
For a vertex on the first arm, distance to every occupied vertex is
exactly |d-q|, even though the two shorter arms overlap in this coordinate.
Let

    M(z)=sum_(occupied vertices v) z^q(v).

For a first-arm perturbation X, put C(z)=X(z)M(z^-1). Its nonzero exponent
coefficients fold in opposite pairs to give exactly the signed shell
profile. Its constant coefficient is X(1), since each occupied first-arm
coordinate has multiplicity one. Therefore balanced all-shell vanishing
is equivalent to the exact Laurent identity

    X M* + X* M = 0.                                     (9)

This includes arbitrary first-arm hole cuts automatically.

Let a and b be the largest occupied first-arm and shorter-arm depths,
P=z^b M, N=a+b, and Y=z^b X. Then deg(P)=N, its constant coefficient is
one or two, its leading coefficient is one, and (9) becomes

    Y P^R + Y^R P = 0,                                  (10)

where both reversals use degree N, padding Y with zeros. Let
G=gcd(P,P^R) over the rationals, g=deg(G), and U=P/G. Coprimality of
P/G and P^R/G forces U to divide Y. If Y=UW, then deg(W)<=g.
Because U has nonzero constant coefficient and Y starts at degree at
least b+1, W must also start at degree at least b+1. Thus

    deg gcd(P,P^R) <= b  ==>  full first-arm injectivity.  (11)

This is sufficient, not necessary: additional support and hole conditions
on Y may force zero even when the degree test fails. It does not by itself
construct a sign completion. Equation (10) is an exact unrestricted kernel
reduction available for further work outside the geometric cone.

For further elimination, the same equation has an exact inhomogeneous
form. Let F_0 be the signed occupied-shell profile contributed only by
the retained centre and shorter arms, and let S_0 be their signed sum.
These are determined without any first-arm signs, since occupancy is
fixed. A first-arm candidate is a balanced homometric completion exactly
when its literal occupied signs satisfy

    Y P^R + Y^R P = R,
    R = -z^N [F_0(z)+F_0(z^-1)+2S_0].                   (12)

Indeed folding X M* gives the missing shell profile, while its constant
coefficient is X(1). Conversely, evaluating the Laurent equation at 1
forces X(1)=-S_0: F_0(1)=S_0(M(1)-1). The other coefficients then give
every missing shell equation. Thus balance is not silently omitted.
In particular G must divide R; reduction modulo any prime gives a
necessary shorter-word constraint even if the modular gcd has additional
factors. Passing such a divisibility test is not sufficient for the
support and literal-sign requirements on Y. This is an exact next route
to constraints on the shorter arms, rather than an assumption that they
or the recovered first arm must be periodic.

`--radial-bound GEOMETRY.json`, taking `lengths` and `holes`, computes the
gcd modulo the fixed prime 1,000,003. Full leading degrees survive this
reduction; hence the rational gcd degree is at most the modular gcd degree.
A modular degree <=b is an exact sufficient certificate for (11), rather
than a numerical estimate. A larger degree means inconclusive. The diagnostic
refuses polynomial degree above 10,000 to avoid costly dense divisions;
the all-scale geometric proof and primary recovery checker have no such cap.
For T(99,79,23) with holes (1,19),(1,99), it returns rational gcd degree
at most 3<=79, independently certifying first-arm uniqueness. Outside the
cone it also certifies examples such as T(9,7,3) with no holes.

The limitation is real: on T(8,4,1), omitting its only third-arm vertex
leaves an occupied path. First-arm depths 1 and 3 have identical shell
profiles by reflection in that path. The degree diagnostic is inconclusive
there, and the tests explicitly verify this nonzero first-arm kernel.
No general injectivity assertion is made for all tripods outside the cone.

## Exact recovery and rejection

`aperiodic_completion.py` forms the integer sparse columns of (1) and
balance. It first checks (8) when applicable, substitutes the descending
upper pivots, then solves for the omitted proximal coordinates directly
from the clear short band, or by singleton substitutions followed,
if necessary, by exact rational Gaussian elimination. Sparse residual updates
avoid building a matrix for all upper-arm variables. The full injectivity theorem
ensures full column rank for the selected recovery coordinates. Every
substitution is reversible. Acceptance requires every recovered coordinate
to be exactly +1 or -1 and every original shell row and balance to vanish.
This gives a bijection between accepted retained sign lists and actual
homometric completions for the specified H. A rational kernel solution
or a partial shell solution is never accepted as a signing.

The `--complete PARAMETERS.json` command takes only `lengths`, `holes`,
`centre` (-1, +1, or zero exactly when omitted), and `arm2` / `arm3` strings
using '+', '-', and '0' at omitted vertices. It accepts no first-arm signs.
On success `--output WITNESS.json` writes the complete left/right sets;
the printed receipt gives their size and exact full-shell verification.
`--recover WITNESS.json` is a reconstruction test that hides the entire
first arm of an existing witness and rejects if reconstruction differs.

The fast `--reduce` command computes a homogeneous rank certificate for
the proximal coordinates and reports the number of parameters; it does
**not** search their assignments. `--recover` rejects an altered witness
even if its retained shorter-arm signs admit a different homometric
completion. The tests independently build tree adjacency
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
`universal_milestone_decided` were both false. The test run passed thirteen
tests, including independent BFS reconstruction on t=1,3,7, an altered
pair, random signed shell identities on unequal lengths [8,5,3], random
hole placements including the centre, exact fractional pivots, and the
first open scale's proximal rank, every-column audits of (7), and an
actual rejection using the prior first-open-scale shorter words. Fresh
unequal triples (101,81,25), (105,85,29), and (119,99,43) were reconstructed
and independently BFS-recounted as well. A non-diagonal first-open-scale
case with holes (1,19),(2,61203) returned full proximal rank 53219 and
271422 retained signs, using the general recovery strategy. An independent BFS shell matrix on
T(17,16,6) had full first-arm column rank modulo a prime for all 821
hole sets of cardinality zero, one or two; this is a finite audit of the
proof, not its justification. The radial gcd criterion and reflected-path
negative control were also checked. An independent BFS audit of (12)
checks both reversal padding and the essential balance constant. No witness at t=2661 is produced.

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
search at the first open scale. All hole placements are covered by the completion reduction, but none
is excluded by that reduction alone.
