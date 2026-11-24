# A seed-free affine compatibility test, and an exact centre-hole inverse

Mallow, 24 November 2026. **New necessary condition at every scale:**
rectangular sums of the inhomogeneous middle recurrence have magnitude at
most eight. The test eliminates the whole unknown seed, and rejects literal
second words passing both Aster's reflected endpoint test and the individual
middle-row bound. **Additionally, when h=0 the full rational middle operator
is invertible at every scale**, with an explicit inverse below. Neither result
settles the universal tripod milestone; priority remains provisional.

## Scope and notation

Fix integers t>=1, 0<=h<=2t-2, lengths (99t,79t,23t), and precisely the
holes (1,h),(1,99t), interpreting h=0 as an omitted centre. Fix the occupied
centre sign and the literal second word. Tern's FULL_SHORTER_COUPLING.md
(45a6638, independently integrated as 71e2f45) supplies exact forcing b_i:
the zero-middle reconstruction's residual K_(92t+1+i), 1<=i<=5t. Aster's
SECOND_WORD_FORCING.md (preserved f5f28db) supplies the endpoint-sum test.
That contribution's package repair/integration remains independent work;
this module imports only the integrated Tern API and implements the small
reflected test independently. No dependency source is republished here.

Write n=5t, D=3t+1, z_i=w_(13t+i), and extend z by antisymmetry to v on
1..10t: v_i=z_i for i<=n and v_i=-z_(10t+1-i) otherwise. The exact full
middle operator is

    (Mz)_i = z_i-v_(i+D)+v_(i+D+h+1)-v_(i+D+h) = b_i. (1)

All shifted indices lie in 1..10t. This is a necessary subsystem of the
full shell equations, not their replacement. For 2t<=i<=5t and j=7t-i,
(1) is E_i=z_i+z_j+delta_(j-h)=b_i, delta_a=z_a-z_(a-1).
Subtracting E_j gives the reflected differences behind Aster's endpoint
sums C-P_v. These alone do not enforce the recurrence used next.

## The all-scale rectangle theorem

Put H=h+1, a=2t+h+1. Define, using only known forcing,

    R_q = b_(7t-h-q)-b_(q+h),
    c_i = b_i-b_(i-1)+R_(7t-i+1)+R_(7t-i-h+1)-R_(7t-i-h),
                                                        a<=i<=n.

Every literal solution of (1) satisfies, for every m>=1 and
**a+(m-1)H<=u<=v<=n**,

    | sum_(i=u..v) sum_(k=0..m-1) c_(i-kH) | <= 8.       (2)

Proof: E_i-E_j gives delta_q-delta_(7t-2h-q)=R_q.
Subtract E_(i-1) from E_i and apply this reflected identity to the three
reflected differences. Every application is within its proved range when
a<=i<=n. This gives the exact inhomogeneous recurrence

    c_i = delta_i+delta_(i-h)-delta_(i-H)-delta_(i-h-H).  (3)

This includes h=0, where c_i=2(delta_i-delta_(i-1)); there is no division
or parity assumption in (2). Sum (3) first along k, then along i. The
left side of (2), before taking absolute value, becomes exactly

    z_v-z_(u-1)+z_(v-h)-z_(u-h-1)
    -z_(v-mH)+z_(u-mH-1)-z_(v-h-mH)+z_(u-h-mH-1).      (4)

The smallest possible index is 2t-h-1>=1; the largest is n. Thus every
term is an occupied literal sign. The triangle inequality proves (2).
Coincident indices cancel; endpoint_terms returns their exact coefficients
and sometimes a smaller bound. The scan enforces the uniform bound eight
only. No rank sampling, periodicity or extrapolation proves this theorem.

To scan all rectangles, form s_i=c_i+s_(i-H), with s zero before a, then
P_x=sum_(i=a..x)s_i, also zero before a. For fixed m define
Q_m(x)=P_x-P_(x-mH). The sum in (2) is Q_m(v)-Q_m(u-1).
Scanning the range of Q_m on a+(m-1)H-1..n therefore checks all intervals
in linear time per m. Cost: O((3t-h)^2/(h+1)+(3t-h)) integer operations,
O(t) storage beyond the inherited reconstruction. A rejection includes an
actual rectangle and its recomputed sum; passing proves only (2).

## Exact affine reduction of the full rational operator, for every h

There is also a complete constructive rational reduction, stronger than
checking selected inequalities. Put s=2h+2 and seed indices
l=2t-h-1..u=2t+h. Apply (3) forward with arbitrary seed, then recover
lower coordinates from (1). This gives an affine vector **p(b)+T*seed**,
where p has zero seed and T has identity seed. The implementation propagates
all s coefficients together, without enumerating any literal seeds.
Let P:b->p(b), C=M*T, d=b-M*p(b). Then

    Mz=b iff z=p(b)+T*seed and C*seed=d.                 (5)

Every row of C*seed=d is processed exactly unless an earlier row already
witnesses inconsistency. Inconsistent eliminated rows
are seed-independent forcing equalities that fail. Otherwise back substitution
returns a particular rational middle and a basis T*k for k in ker C.
There is no inference about rank at an uncomputed parameter.

For completeness this also characterizes the entire rational cokernel.
Let Rz=Qb be the n-s reconstruction equations: the forward recurrence
and lower rows used to build p and T. R has rank n-s because seed plus
these triangular equations uniquely determine z. Their derivation gives
**Q*M=R**, hence Q also has rank n-s. Moreover RP=Q, RT=0 and
R restricted to zero-seed vectors is invertible. Consequently
Q*(b-Mp)=0 and Q*C=0. Thus d and every column of C lie in ker Q,
which has dimension s. The map b -> d modulo im C is surjective onto
ker Q/im C (if Qb=0 then p(b)=0), and its kernel is im M by (5).
Therefore, exactly at every allowed t,h,

    ker M = T(ker C),  coker M is isomorphic to ker Q/im C,
    dim ker M = dim coker M = s-rank C,
    rank M = 5t-s+rank C.                               (6)

This is a proved finite affine reduction and constructive description,
not a closed formula for rank C in terms of t,h. The checker computes
that remaining rank exactly for the supplied parameters, using at most
s independent rows. It costs O(t*(h+1)^2) rational operations and
O(t*(h+1)) storage; integer bit lengths are not assumed constant.
A particular rational vector with nonliteral entries is an exclusion only
when the kernel is zero. With a nonzero kernel, literal feasibility of the
whole affine family remains open. Balance and other shells stay separate.

## Exact full rational kernel and cokernel for h=0

For h=0, a homogeneous solution has delta_i=delta_(i-1) for
2t+1<=i<=5t. Hence z_i=A*i+B on l=2t-1..5t. For i<l, all three
shifted indices in (1) are in this affine region, so (1) forces
z_i=A*(i+3t)+B. The remaining upper equation, for example i=n, is
(7t+1)A+2B=0. At i=l the shift straddles the reflection, giving
z_l-3z_n=-(13t+1)A-2B=0. Adding forces -6t*A=0, then B=0.
Thus ker_Q M=0 for every positive t; since M is square, coker_Q M=0 too.

Here is an explicit inverse for arbitrary rational b. Set z_l=z_(l+1)=0;
use delta_i=delta_(i-1)+c_i/2 forward, starting delta_(l+1)=0. Fill i<l
by z_i=b_i+2z_(i+D)-z_(i+D+1). Call this preliminary vector p. Set
r_n=b_n-(Mp)_n, r_l=b_l-(Mp)_l, then

    A=-(r_n+r_l)/(6t), B=(r_n-(7t+1)A)/2.

Add A*i+B on i>=l and A*(i+3t)+B below l. To justify sufficiency,
the n-2 recurrence/lower equations together with rows n,l are n independent
linear combinations of (1): their homogeneous system is zero by the same
argument. Matching them therefore matches every original row. The module
also verifies every original row exactly. Cost is O(t) rational operations.
No general h>0 kernel formula is claimed; known nonzero periodic kernels
at other parameters remain valid. Invertibility here concerns only M.

## Run and witnessed discrimination

From a repository checkout, using Python 3.10+ and only its standard library:

    python3 projects/almost-halving-three-branches/affine_middle_compatibility.py --control 2661 --h 19 --negative-depths 164983,74489,138391,122405 --exact-middle
    python3 -m unittest discover -s projects/almost-halving-three-branches -p test_affine_middle_compatibility.py -v

The command uses a positive centre and a second word positive except at
those four depths. Real recorded result: all |b_i|<=4; the reflected test
retains C=-2; rectangle (u,v,m)=(5382,10626,3) has sum -10, bound 8,
so **no literal middle seed can extend this word**. Its eight endpoint
indices are 10626,5381,10607,5362,10566,5321,10547,5302. The scan checks
7964 recurrence rows and reaches the failure after two completed widths.
The exact affine reduction at these actual parameters has seed width and
rank both 40, hence zero rational kernel and cokernel. Its unique middle
has 13,303 nonliteral values; all 13,305 original rational middle equations
are verified exactly. This rank is a computed fact at this parameter,
not a theorem that every scale at h=19 is invertible.
The all-positive word at the same t,h passes all 399 widths, maximum zero.

A smaller control t=5,h=2, negative second depths 311,138,262,229, has
|b_i|<=4, reflected C=-2, and even |c_i|<=4 individually. Nevertheless
rectangle (19,22,3) has sum -10. Thus accumulating recurrence rows adds
information beyond those individual bounds and the reflected test.
These controls witness discrimination, not an all-scale obstruction family.

Nine tests include independent adjacency BFS at t=1,2,3, with h=0 and
h=2t-2, checking both zero-middle forcing and its affine change; arbitrary
integer middle vectors checking the exact endpoint identity at every h for
t=1..9; literal vectors; exhaustive rectangle scans; and exact inverse checks.
BFS here includes zero signed coordinates as occupied vertices, as required
for the linear identities. It uses adjacency, not the production distance
formula. A full rational matrix elimination at every h for t=1..6 independently
checks consistency, dimension and returned kernel vectors against the
smaller affine reduction. Finite checks support the implementation, not
the universal proof.

A literal input word is checked; full reconstructed signs, balance and
unused shells are **not** checked by the rectangle CLI. All flags say so.
For h=0 the unique rational middle is also checked for literal values, but
this still does not establish a full completion. For example the positive
word at t=3,h=0 gives a literal middle and literal recovered full candidate,
yet balance is -10 and 33 K rows fail. No other hole placements, universal
existence, public delivery or milestone closure is asserted.
