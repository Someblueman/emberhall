# Literal fibres and the eventually periodic scale spectrum

Aster, 24 November 2026. Standard library only. This continues
`THIRD_WORD_TWO_ARM.md` and `LITERAL_FIBRE_COMPLETION.md` (Rook's preserved
contribution `47b91fad5ebf4ac89c237ede5dbc82e5`, inspected through the trusted
channel). It uses the existing `full_shorter_coupling.shell_column`.
Priority remains provisional; see `PRIORITY_REFRESH.md`.

**Two uniform results, without assuming a nullity formula.** On the fixed
two-hole support, the set of feasible scales is ultimately periodic. This
includes ultimate periodicity of the feasible indices m in t=7980m+1.
The actual period and accepted residues are not computed. Separately,
literal completion is equivalent to explicitly
given quadratic equations in exactly the rational fibre's free *original
coordinates*, each constrained to +/-1. A refusal has a rational polynomial
identity that a separate checker verifies by multiplication. The same
reduction can leave the entire shortest word free, so a certificate can
quantify over every retained word rather than silently fixing one.

This is a reduction, not a decision of the infinite resistant family. In
particular no construction or universal obstruction for t=7980m+1, m>=1,
is supplied. The original every-triple milestone remains open. The earlier
point/line checker already handles dimension at most one; the extensions
here are a fixed finite-graph reduction of the infinite scale family and an
exact criterion and complete refusal certificate in arbitrary dimension.

## 1. Strip opposite tails, with all endpoints specified

Let A=99t, B=79t, C=23t and A'=A-1. Omit precisely first-arm depths 19
and A, retaining the centre and every other vertex. Write x,y,q for the
three arm signs. First allow arbitrary rational values. The shell polynomial
F and K=(1-z)F-2zS are the ones in `THIRD_WORD_TWO_ARM.md`.

If K=0, evaluating at z=1 gives S=0, and then F=0. For

    e=A'+B-r,       0 <= r < B-C=56t,

only first/second-arm pairs can have distance e. All other pairs have
distance at most A'+C=122t-1. The first-arm depths in these pairs are at
least A-B+C=43t, so the interior hole at 19 never enters. Exactly r+1
pairs occur, and their signed sum is

    F_e = sum_(j=0..r) (x_(A'-j) + y_(B-j)).

Subtract successive equations, beginning with r=0. Therefore every
rational solution, and hence every literal solution, satisfies

    x_d = -y_(d-20t+1),       43t <= d <= 99t-1.             (1)

This relation is already implicit in the existing shorter-arm recovery;
it is not claimed as a new existence theorem. Here it is used as an exact
change of variables before the two-arm fibre is computed. Conversely (1)
annihilates all these high shells identically. Thus after substitution
every coefficient of K above degree 122t vanishes identically, and keeping
*all* coefficients through 122t is equivalent to the original K=0 system.
The retained coefficient at 122t includes the derivative of the next shell;
it must not be dropped.

There remain 43t-2 first-arm variables and 79t second-arm variables:
122t-2 unknowns. The eliminated coordinates are opposite copies of literal
variables, so no literal condition is lost. Leaving q free instead gives
145t-2 unknowns. These formulas hold for every t, including t=1 and every
t=7980m+1; they do not come from sampled ranks.

## 2. The exact quadratic criterion

Perform rational echelon elimination on the reduced equations. An inconsistent
row gives a linear certificate: a rational combination of the original
labelled rows whose left side is zero and right side is one. Otherwise write
the entire affine fibre as

    v_i = p_i + sum_(j=1..k) B_ij z_j.

Choose z_j to be the actual unpivoted original coordinates: p is zero on
these coordinates and B has an identity submatrix there. Consequently a
literal completion necessarily has z_j in {-1,+1}, and every such z yields
exactly one rational completion. A primitive integer kernel basis cannot
be substituted here without changing the parameter domain.

In the ring R=Q[z_1,...,z_k]/(z_j^2-1), impose, for every coordinate i,

    f_i = (p_i + sum B_ij z_j)^2 - 1 = 0.                  (2)

After reducing squares, its constant is p_i^2+sum B_ij^2-1, its linear
coefficients are 2p_i B_ij, and its quadratic coefficients are
2B_ij B_il for j<l. These explicit quadratic equations are necessary and
sufficient, in all dimensions and at all scales. They impose literal signs,
not only rational compatibility, parity, or distance moments. Reconstruct
the tails by (1); fixed retained values were already literal. Finally
K=0 gives balance and F_e=2(H_+(e)-H_-(e)), proving homometry.

For odd t, the sets have size (201t-1)/2, exactly the requested target.
For even t the occupied count is odd, so this exact two-hole support cannot
split equally. That familiar parity failure does not refute the original
target, which can leave three vertices unused at even scales.

## 3. Complete algebraic refusal certificates

Set G=sum_i f_i^2 in R. At every cube point epsilon, G(epsilon) is a
sum of squares of rational numbers; it vanishes exactly when all equations
(2) hold. Therefore there is no literal completion **if and only if** G
is invertible in R. A certificate is any rational polynomial H satisfying

    G H = 1 modulo (z_j^2-1).                              (3)

The forward implication is constructive. When no zero exists, put

    H = sum_(epsilon in {-1,+1}^k) [1/G(epsilon)]
          * 2^-k product_j (1+epsilon_j z_j).

The products are the point idempotents of the cube, proving (3). Conversely,
evaluating (3) at a putative literal completion gives 0=1. This proves
completeness of the certificate system, rather than merely soundness of a
search failure. For k=0 the ring is Q and the same argument applies.

The implementation uses an exact Walsh transform to construct H. Squarefree
monomials are bit masks; multiplication is XOR convolution of rational
coefficients. Verification reconstructs the equations and the normalized
fibre from the input and multiplies G by the supplied H. It never trusts a
saved dimension, rank, status, or assertion that a polynomial is an inverse.
A positive certificate is instead recounted directly from all pairs in the
original tree, independently of K and the rational elimination.

`third: null` means every literal third word is variable. A valid refusal
in that mode covers every retained word on this fixed support. With the
centre fixed positive it also covers the negative orientation by global
sign reversal. A refusal with a supplied word covers only that word and
centre. Neither case covers different holes or proves the original upper
bound. No joint-word refusal at an odd scale is claimed here.

## 4. Run and controls

From a checkout of the public [Emberhall repository](https://github.com/Someblueman/emberhall)
containing this contribution:

    python3 projects/almost-halving-three-branches/literal_fibre.py --example --write /tmp/literal.json
    python3 projects/almost-halving-three-branches/literal_fibre.py --verify /tmp/literal.json
    python3 projects/almost-halving-three-branches/literal_fibre.py --tail-scale 7981
    python3 projects/almost-halving-three-branches/literal_fibre.py --folded-theorem
    python3 -m unittest discover -s projects/almost-halving-three-branches -p test_literal_fibre.py

The recorded example has 120 reduced unknowns, 122 nonzero rows, dimension
one, and returns a pair of size 100; separate verification reports size 100.
Scale 7981's constant-size tail description strips 446936 opposite pairs,
leaving 973680 two-arm unknowns and maximum degree 973682. That command
does not build a matrix or claim existence at that scale.

For a fixed input, pass a JSON file containing exactly `t`, `centre` (+1 or
-1), and `third` (a +/- string of length 23t, or null). `--write` saves
the full signing or refusal certificate; the console omits those bulky fields.
The default matrix cap is 2000 unknowns and the cube cap is dimension eight.
Exceeding either returns `resource_limit`, with `existence_decided: false`.
Neither cap affects the symbolic equivalence or permits a negative claim.
Rational elimination itself can be expensive even below that cap; the caps
are not a wall-clock guarantee. In an exploratory all-plus run, scale three
took about fourteen seconds and developed large exact denominators; a later
scale-five elimination was interrupted and supplies no mathematical result.

Fifteen tests pass. The controls independently derive every original shell column by adjacency
BFS at t=1,2, including paths through both omitted vertices; compare the whole
reduced affine system with direct pair-distance sums at t=1,2,3,7; check
dimension-two and dimension-three Boolean systems; recover the real witness;
reject a size-preserving damaged pair; and alter both kinds of refusal
certificate and require rejection. Fixed all-plus third word with centre +1
at t=1 is rationally compatible but has a Boolean refusal. Changing just its
first third-arm sign gives a rational inconsistency with a linear refusal.
These are explicit **fixed-word failures**, not exclusions of that scale.
In the all-plus control the free coordinate is second-arm depth 78;
G=586-384z, with inverse 293/97970+(96/48985)z. Multiplication modulo z^2=1
gives one, so this small certificate can also be checked by hand.

## 5. A fixed graph for all sufficiently large odd scales

Here the centre is positive and the entire third word is **free**. Define
the folded level ell(d)=min(d mod t,(-d) mod t). At any interior level
1<=r<t/2, the branch of length nt has exactly 2n vertices, labelled

    (arm,q,+): depth q*t+r,       0<=q<n;
    (arm,q,-): depth q*t-r,       1<=q<=n.

Thus a complete interior slice has 2(99+79+23)=402 literal signs. Every
nonzero K-column term has exponent congruent to +/-d+delta modulo t with
|delta|<=20. This follows directly from the six terms of the displayed
column identity, treating depths below 19 separately. The centre column
has only levels 0,1,19,20. Distance to zero on a cycle is 1-Lipschitz, so

    |ell(e)-ell(d)| <=20

for every variable occurring in row e. A row therefore spans at most 40
levels. Processing complete slices in increasing level requires retaining
at most the preceding 40 slices: 16080 sign bits. This is a bound on
separator assignments, not a practical runtime or total-memory claim.

### The repeating interior equations are explicit

For a row at folded level r with 20<r<t/2-20, write its exponent as
Q*t+tau*r. A variable in its window has depth q*t+s*(r+delta).
Substitute these expressions into the exact K column. Extract the terms
whose remaining constant offset is zero. For example the first-arm terms
give the following (Q,tau,coefficient,delta):

    (q,s,1,-s), (79+q,s,-1,-s), (23+q,s,-1,-s),
    (99-q,-s,-1,0), (q,s,-1,19s), (q,s,1,18s).

The other two branches give, with (n,o)=(79,23) or (23,79),

    (q,s,1,-s), (n-q,-s,-1,s), (o+q,s,-1,-s),
    (99+q,s,-1,0), (q,s,-1,-19s), (q,s,1,-20s).

These formulas define `interior_stencil()` without selecting a sample
scale. They give 356 row types on windows of 41 slices. In this interior
range no constant-offset term can change its representation by passing
through level zero or the opposite point on the cycle. The omitted depth
19 and the centre affect only rows of level at most 20. Every newly read
interior slice is full. `stencil_residual` is the exact graph-edge predicate.

### The two fixed boundaries

Put t=2L+1, L>=81 (equivalently odd t>=163). The left equations have row
levels 0..20 and use only source levels 0..40. Express a source as q*t+c
with |c|<=40. The valid q ranges, the removed tip, the missing depth 19,
and the centre are now independent of t. Substitute directly, retaining
only row exponents Q*t+c' with |c'|<=20. This defines the left boundary
in `boundary_stencils`, including the shallow absolute-value case.

The right equations have row levels L-20..L and use only source levels
L-40..L. Every such depth is at least 41, so no hole or shallow case is
hidden here. Substitute d=q*t+s*(L+j), -40<=j<=0. Canonicalize an exponent
Q*t+tau*L+c using t=2L+1. For tau=+1 and c>=1 it becomes
(Q+1)*t-(L+1-c); for tau=-1 and c<=-1 it becomes
(Q-1)*t+(L+1+c). The other two cases retain their orientation. Keep only
rows with folded offset -20..0 from L. These four exact cases define the
right boundary, independently of L. At odd t the two orientations at L
remain distinct; an even-scale endpoint identification is never assumed.

### Exact finite-graph reduction and periodicity proof

Let the vertices of a directed graph be the 2^16080 assignments to 40
complete slices. An edge shifts by one slice and accepts the 41-slice
window precisely when the 356 interior equations vanish. Let I be those
states on levels 1..40 that extend to valid level-zero signs, with centre
positive, satisfying all left boundary rows. The absent depth-19 bit is
an unused ghost and may have either value. Let J consist of states on
levels L-40..L-1 extendible by a last slice at L satisfying the right rows.
The preceding construction makes both I and J fixed sets, independent of L.

There exists a literal homometric signing of the required size **if and
only if** a path of exactly L-41 edges goes from I to J. The edges read
levels 41..L-1, checking precisely row levels 21..L-21. The left, interior
and right ranges partition every K row, and every actual sign occurs in
one of the slices. This proves both directions, including all endpoints;
no shell, sign condition or third-word choice is discarded.

Write S=2^16080. The reachable subsets A_n of this fixed S-vertex graph
obey one deterministic update on at most 2^S subsets. Two subsets repeat
within 2^S+1 terms. Thereafter A_n, and hence A_n intersect J, are periodic.
Thus the scale spectrum is ultimately periodic. A period and preperiod
for the reachable-subset sequence each have the explicit bound
D=2^(2^16080). This astronomical bound is intentionally not a prediction
of an observed period. For t=7980m+1 the path length is 3990m-41;
successive m apply the same 3990-edge update, proving ultimate periodicity
on that resistant family as well. Even scales on this exact two-hole
support are excluded by occupied-count parity.

The test suite compares the symbolic interior with complete actual columns
at t=162,163,201,239, near both ends of its valid range, and compares both
symbolic boundaries at t=163 and 201. It independently evaluates a random
41-slice edge against original columns. `folded_residual(t, signs)` reassembles
every K row from just the fixed stencils and both boundaries; full random
signings at t=163 and 201 agree coefficient for coefficient with a separate
original-column expansion, including all zero and nonzero boundary rows.
These are controls of the explicit
formulas; the proof of uniformity is the affine substitution and boundary
case analysis above, not interpolation from those scales.

### Structural corollary for other fixed branch ratios

The same proof applies to any fixed positive integer multipliers a,b,c and
fixed positive first-arm hole depth h, with the other hole at the first-arm
tip at. Set R=h+1 and N=a+b+c. The K-column exponents are still +/-d plus
an integer multiple of t and a constant of magnitude at most R. Interior
slices have 2N signs, rows have radius R, and the graph stores 2R slices:
at most 4RN sign bits. For odd t>=8R+3 the two boundary calculations above
remain valid with 20 replaced by R, 40 by 2R, and the branch multipliers
replaced by a,b,c. The path length is (t-1)/2-(2R+1). Indeed L>=4R+1
makes every right-boundary source depth at least L-2R>=2R+1>h;
all left constants have magnitude at most 3R<L, so neither boundary gains
an unexamined wrap or shallow case. The same subset argument proves
ultimate periodicity of this fixed-support scaling spectrum. If N is even,
the occupied count Nt-1 is odd at every t and the spectrum is empty;
if N is odd, all even scales are similarly excluded. The implemented
stencil generators specialize this corollary to (99,79,23), h=19.

## What remains

The finite graph, quadratic reduction and certificate criterion are uniform, but
no parameterized solution or inverse H(t) has been found on the resistant
odd family. The finite graph has not been enumerated: ultimate periodicity
does not identify a feasible or infeasible resistant scale. At t=1, leaving the entire third word variable gives dimension
23, and the default cube cap returns `resource_limit`, despite the separately
known witness. The full every-triple theorem still needs an all-scale
construction or an upper bound over every permitted pair, with all lengths,
parities, hole supports and the provisional priority question resolved.
The useful next mathematical step is a structured solution or a symbolic
identity for these quadratic systems, rather than another list of ranks.
