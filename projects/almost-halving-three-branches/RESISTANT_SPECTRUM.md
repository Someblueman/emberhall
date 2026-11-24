# Periodic folded interiors and moving-hole words

Rook, 24 November 2026. **The task's acceptance result is not obtained.**
This contribution neither decides arbitrary hole choices nor closes the
infinite resistant family. Priority remains provisional.

The attempt leaves the first and last `w` folded levels independently
signed (`w>=40`). Between those patches, each independent coordinate
`(arm,q,orientation)` repeats with period `p` in folded level. The only
physical holes are first-arm depths 19 and 99t. The entire third word is
free subject to this explicitly stated repetition, rather than fixed in
advance. Opposite first/second tails are restored as in
[LITERAL_FIBRE.md](LITERAL_FIBRE.md).

## Why the finite system is exact for this attempt

Write t=2L+1. Require L>=2w+42+p. The left boundary rows cover levels
0..20; the right boundary rows cover L-20..L. Interior rows have radius
20. Those at levels 21..w+20 and L-w-20..L-21 can see an endpoint patch
and are retained separately. Every other row uses only periodic signs;
levels w+21..w+20+p represent all their residues. These ranges cover all
rows, with no omitted endpoint. Every independent sign is represented,
including signs whose coefficient happens to cancel.

Consequently the finite integer equations are equivalent to every
original distance-shell equation under this repetition constraint.
Their coefficients and literal-coordinate keys are identical when L is
increased by a multiple of p. Thus a verified signing would extend to
all such L; a verified parity refusal excludes just this ansatz on all
such L. Intersecting L congruent to 3990 modulo p with L=3990m gives an
infinite resistant subfamily (m congruent to 1 modulo p suffices).
This is a possible route to a construction, not evidence one exists.

I independently checked the predecessor's path count: edges append
levels 41..L-1, hence L-41 edges, checking row centres 21..L-21.
The boundary ranges 0..20 and L-20..L complete the partition.

## A refusal another mind can replay

For a row sum(c_i*s_i)=0, write s_i=2b_i-1. If sum(c_i) is odd no
literal signing is possible. Otherwise the necessary binary equation is

    sum((c_i mod 2)*b_i) = sum(c_i)/2 mod 2.

The checker reconstructs the shell system and XORs the indexed binary
rows. A refusal is accepted only when they sum to zero coefficients and
right side one. Search exhaustion is kept separate from this certificate.
A compatible binary system is not a literal solution. In particular the
period-128 system has 2,534 free binary coordinates at the recorded scale,
so it still leaves a substantial integer-sign problem.

From the repository root, standard library only:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --period 1 --write /tmp/folded-refusal.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/folded-refusal.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -v
```

The seconds budget applies to branching, not compilation or parity
elimination. Larger periods and patches can cost substantial memory;
there is no practical-time guarantee. Certificates are regenerated,
not committed as large evidence files.

## Observations and remaining obstacle

At t=7981, w=40, binary elimination refuses periods
1,2,3,4,5,6,7,8,9,10,11,13,16,17,19,23,29,31,32,61,64,127.
Period 128 is binary compatible. This is a finite list, not a theorem
about every period. Period one also fails with free patch widths
41,60,80,120,160,240. Increasing the patch therefore matters mathematically;
none of these failures licenses removing the patch restriction.

The five tests compare every compiled equation with direct original
physical shell columns at t=247,255,267 (including wider patches), check
unchanged equations after adding whole periods to L, compare binary
refusals with exhaustive literal solutions on small arbitrary systems,
reject damaged certificates, and compare the cached parity-assisted sign search
with exhaustive literal solutions on small arbitrary systems. These are controls on the compiler
and refusal checker, not milestone acceptance.

The sign-search setup caches truth tables by coefficient word. A measured
period-128 setup constructed all 60,878 row tables in 0.208 seconds; the
unchanged uncached method recomputed these tables separately. Its binary
echelon equations also remain active during branching.

An exploratory sparse elimination modulo three was stopped at its
120-second work limit (39,029 pivots, a remaining row of width 6,133).
It supplies no impossibility claim.

At period 128, a 600-second sign search ended unknown after 30,340
branch nodes. A separate parity-assisted 600-second run ended unknown
after 14,607 nodes. The cached natural-order 900-second run also ended
unknown, after 22,187 nodes. None of these timeouts is an impossibility
result. A final most-connected-first 300-second run ended unknown after
9,777 nodes. Replay that order with `--period 128 --seconds 300 --free-order connected`; no witness was found in any recorded run.

The remaining problem is to find a literal period-128 (or other)
assignment that satisfies the integer equations, or to reason about
unrestricted signs and all allowed hole placements. Binary compatibility
alone does not address that problem. No all-pairs obstruction is claimed.

A useful next mathematical step is to eliminate the periodic interior as
a block-circulant linear system before more sign branching, while retaining
original literal coordinates as parameters. The modulo-three probe above
shows why unrestricted sparse elimination is not yet that reduction.
The current script supports natural or most-connected free-coordinate
branching; changing that order does not change its equations or scope.

## Mica's continuation: verified modular kernels and moving holes

24 November 2026. The unrestricted target and this task's acceptance remain
unmet. The prior three files were recovered verbatim from Rook's stopped
contribution `1fad5a46080a4f3d8a772eacf9926750`, checked with its five tests,
and preserved separately in commit `eb372ee`. Aster's earlier moving-hole
room could not be inspected: the trusted reader reported that its source
repository could not resolve its head. The compiler below is independently
derived, not a recovered copy of that missing implementation.

### The period-128 linear diagnostic now completes

`ternary_analysis` first eliminates low-degree columns with sparse integer
rows modulo three, then compacts the remaining coordinates into pairs of
disjoint bitsets for coefficients one and two. It reverses both triangular
eliminations to express every coordinate in free **original coordinates**.
Every resulting kernel expression is substituted back into every untouched
input row. Free coordinates have an identity submatrix, so the verified
kernel has the claimed dimension; the pivot elimination gives the matching
rank bound. Timeouts report only a lower bound, with no kernel assertion.

At t=7981, period 128 and patch width 40, the completed computation reports
60,755 variables, 60,878 equations, rank 58,232 and nullity 2,523 over the
field of three elements. The original-row kernel check passes and no
coordinate is forced to zero. This is a full linear diagnostic, **not** a
nowhere-zero vector, a literal signing, or a decision of this ansatz.
Its elapsed time was 490 seconds during concurrent computations; this is
not a portable performance guarantee. The earlier 120-second bitset-only
probe reached 41,826 pivots; sparsity-first alone reached 42,789.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --ternary --period 128 --seconds 900
```

### Independently derived moving-hole compiler

Fix period p, put t=pk+1, and omit first-arm depths 19t and 99t. Keep
every other old vertex at a depth divisible by t independently signed,
including the centre. On each of the 201 old edges independently repeat
one p-sign word k times in its inserted vertices. There are 200+201p
literal variables; no shortest-arm word is prescribed.

Write Z=z^t. For position r=1..p on one edge, multiplication by 1-z^p
turns its forward and reflected geometric sums into exactly

    P_r = z^r - Z*z^(r-1),
    N_r = Z^(-1)*z^(p+1-r) - z^(p-r).

Substitute these sums in the original physical shell columns, using N_r
for a reflected endpoint or a hole beyond the edge and P_r otherwise.
Coarse columns are multiplied by 1-z^p. `moving_periodic_system` records
each coefficient of the resulting formal polynomial in Z and z, before
specialization. All z exponents lie in 0..p+1. Therefore a formal zero
gives K=0 for every k>=1 by geometric summation and cancellation of the
nonzero polynomial 1-z^p. Conversely, when t>p+1 these exponents cannot
collide under Z=z^t, so every physical zero under this word restriction
is a formal zero. In particular that converse holds for resistant scales
t=7980m+1, m>=1, at p=10. This is an exact criterion for these words and
these moving holes, not for arbitrary supports or inserted words.

For p=10 the compiler has 2,210 variables and 2,146 nonzero formal rows.
Its verified modular rank is 2,131 with 79 free coordinates, independently
matching Aster's recorded rational rank. Equality of those two ranks is
an observation; no general equality of rational and modular ranks is used.

### Nonzero-coordinate closure and exact search

Every free parameter in the modular kernel is an original sign, hence
nonzero modulo three. If a coordinate is ax with a nonzero coefficient,
it is a signed copy. If it is ax+by, all of x,y and the coordinate must
be nonzero, so ax=by and ax+by=-ax. These necessary equalities are literal
equalities or opposites for signs. Substitute them in the integer shell
equations and recompute. Each quotient retains a reversible signed alias
for every original coordinate. No arbitrary kernel-basis coefficients are
treated as signs.

At period ten this reaches a fixed point after thirteen modular analyses:
1,734 sign coordinates, 1,798 nonzero integer rows, modular rank 1,655,
and nullity 79. Its necessary binary system has rank 1,653, leaving 81
binary free coordinates. No forced zero or conflicting equality is found.
The equality closure simplifies representation; it has not reduced that
modular dimension or produced a literal solution.

The exact search retains short-row truth tables. On longer rows it uses
the necessary bound |assigned sum| <= sum of remaining absolute coefficients
and forces a sign when its alternative violates that bound. Long rows are
rechecked after every affected assignment, including complete assignments.
They have no mutable state to lose during rollback. This weak but sound
propagation avoids constructing exponential truth tables for wide rows.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --moving --period 10 --seconds 1200 --nodes 10000000 --free-order connected --write /tmp/moving10.json
```

The command's time budget includes the modular closure. A saved positive
assignment can be checked with `--verify`; verification rebuilds the original
formal equations and checks every literal value without trusting the closure,
rank, aliases or search status. Unknown output is not a certificate.

Tests compare the new formal compiler with **every** physical shell column
at four period/scale combinations, including the geometric endpoint where
formal monomials can coincide. Independent dense elimination and exhaustive
small modular solution sets check ranks, kernels and nonzero equalities.
Signed aliases are checked by substitution, including a deep chain; long-row
search is checked against exhaustive three-sign controls. The original five
tests still pass. These controls do not close the original milestone.

### Combining the two fields matters

`parity_sign_quotient` parameterizes the complete affine binary fibre in
free original binary coordinates, and checks that parameterization against
every untouched necessary binary row. Two sign coordinates with the same
parameter mask must agree or oppose according to their affine constants.
Merge those signed copies and substitute in the **integer** shell rows.
Every original literal solution projects to the quotient and every literal
quotient solution lifts to the original rows. No other binary dependencies
are discarded from a claimed witness: the lifted integer rows still test them.

On the period-128 folded system this yields 52,127 sign coordinates from
60,755; the necessary binary rank before quotienting is 58,221. The subsequent
modulo-three rank is 50,478 with nullity 1,649, and its kernel again verifies
against every quotient row. No coordinate is forced zero. There are 273
further necessary nonzero-coordinate equalities; they were not applied in
this recorded diagnostic. The binary stage took 75 seconds and the modular
stage 976 seconds during concurrent work. These times are observations only.

The drop from nullity 2,523 to 1,649 concerns a different, necessarily
restricted linear space: the added equalities hold for literal solutions,
not for every rational or ternary solution of the original equations.
It is not a correction to the earlier rank. This is a useful joint-field
reduction, not a literal witness or a refusal.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --ternary --parity-quotient --period 128 --seconds 1800
```

### Exact rational recovery for the smaller moving system

`rational_recovery` uses exact fractions and low-degree pivots, then checks
every kernel expression against every original integer row. The free
parameters remain original coordinates. Clearing denominators yields exact
integer recovery equations that may strengthen both bound propagation and
the necessary binary system. Rank equality across fields is never presumed.

On the 1,734-coordinate moving-period-ten quotient, recovery completes with
rational rank 1,655 and 79 free coordinates. Adding its 1,655 denominator-cleared
equations raises the necessary binary rank from 1,653 to 1,655. It supplies
two further binary constraints, not an impossibility result. Reproduce the
augmented search with:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --moving --rational --period 10 --seconds 700 --nodes 10000000 --free-order connected --write /tmp/moving10-rational.json
```

Thirteen targeted tests pass, including exhaustive preservation of every
literal solution under the binary quotient, exact rational recovery and
denominator clearing, exceptional prime rank, resource limits and moving
driver rejection of a forged positive assignment.

### Bounded searches and the remaining obstacle

After the thirteen-step moving-word closure, a connected-order search with
the exact integer shell rows and binary echelon constraints ended **unknown**
after 1,200 seconds and 290,636 branch nodes. Adding the denominator-cleared
rational recovery rows produced a separate **unknown** after 600 seconds
and 68,964 nodes. The latter setup uses 3,453 integer rows rather than 1,798.
Neither search found a signing or exhausted its search tree. These are
witnessed resource limits, not refusal certificates.

The precise missing step is the cube intersection: the 79 free original
coordinates must make every recovered coordinate a literal sign at once.
Compatible rational, binary and ternary fibres do not establish that.
An obstruction for either word ansatz would still leave unrestricted inserted
words and other hole placements open. No all-pairs obstruction or parametric
construction for the resistant family is claimed, and the task remains open.

Rook's baseline was independently accepted and delivered as `bba771d` during
this run. Its complete source tree matches recovered commit `eb372ee` exactly;
the content-preserving merge `60fec49` records that accepted ancestry for the
coordinator. All new implementation changes remain in the three task-owned files.

## Linnet's continuation: alternating the exact reductions

24 November 2026. **Acceptance remains unmet.** I retrieved the three complete
files of Mica's contribution `aeabc8810e0048358fd3d81a401bc8bd`, commit
`c960918`, through the trusted inspector, preserved that implementation, and
ran its thirteen tests before extending it. No all-pairs claim follows below.

### Why alternating fields can remove more literal candidates

`joint_sign_closure` alternates exact rational recovery, the full affine binary
sign quotient, and verified ternary recovery with necessary nonzero-coordinate
relations. It adds the denominator-cleared rational equations before computing
the binary fibre. Every signed alias is composed back to the original signs.
Repeated homogeneous rows are divided by their integer greatest common divisor,
with a fixed sign convention, and deduplicated; their zero sets do not change.

The rational recovery equations are exact consequences of the current integer
rows. Binary equalities hold for every literal solution; substituting them in
those integer rows therefore preserves precisely the literal solution set.
The same argument applies to the ternary nonzero equalities. Two complete
ternary kernel expressions that coincide, or oppose, also give a literal signed
copy, regardless of their support size: reduction modulo three is injective on
{-1,+1}. The new detector includes these copies. It found none beyond the sparse
relations in the final moving-word diagnostic.

Consequently every original literal solution descends through these quotients,
and every literal solution of the final quotient lifts to the original rows.
The intervening rational spaces need not coincide: necessary *literal*
equalities can cut their dimensions. In particular a dimension drop below 79
is not a correction to the earlier rational or modular rank.

An exploratory cycle starting with the 1,734-coordinate moving-period-ten
system and its recovery rows gave successive sign counts
1,410, 1,406, 1,405, 1,405. The corresponding ternary dimensions were
75, 74, 74, 74; exact rational recovery independently returned 75, 74, 74
after the first three rounds. All recovered kernels passed their untouched-row
checks. No forced zero or conflicting alias appeared. A stop with no new signed
merges is not a completeness theorem for these inference rules.

Reproduce the integrated reduction and bounded search from the repository root:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --moving --joint-fields --reduced-xor --period 10 --seconds 300 --nodes 10000000 --write /tmp/moving10-joint.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -q
```

The family remains the explicit moving holes 19t and 99t and one independent
period-ten inserted word on each old edge. Since 10 divides 7980, its formal
criterion applies to every resistant scale t=7980m+1, m>=1. It does **not**
quantify over arbitrary inserted words or other hole placements. A positive
saved assignment is still checked against every untouched formal shell row.
Unknown output is not a certificate. The new diagnostic refusal statuses are
not accepted by the standalone saved-certificate verifier.

### Two tested routes that did not strengthen this fibre

`affine_shell_closure` parameterizes the necessary binary fibre, enumerates each
short shell's locally independent binary characters, and adds the equations of
the affine hull of its valid sign patterns. A local hull contains every valid
pattern, so this is a necessary relaxation, never an existence test. Enumeration
is capped at twelve independent local characters by default; skipped rows stay
in the final integer search. The control 3x+y+z+w=0 forces three binary relations
where elementary parity gives one. At folded period 128 no new relation was
obtained. On the rationally augmented moving-period-ten system it likewise
added none, retained 79 free binary coordinates, and skipped 2,442 wider rows.
A 600-second requested search then ended unknown after 73,728 nodes (617 seconds
including setup), with no signing.

`quadratic_sign_lift` squares each verified ternary kernel expression, substitutes
free-coordinate squares equal to one, and treats each distinct pair product as
a new coordinate. It preserves the necessary square equations over the field
of three elements. The constant coordinate represents one; every product is
nonzero. A forced-zero product would therefore refuse this word ansatz. A
compatible product vector need not factor into original signs. Here the lift
had 3,082 coordinates including the constant, 1,734 rows, rank 1,336 and nullity
1,746, with its kernel verified against every lifted row. It forced no zero and
its sparse nonzero rule supplied no product equality. The later diagnostic for
dense product copies timed out, so no conclusion is recorded about those copies.

### Search representation and controls

`--reduced-xor` removes other pivots from each binary equation before branching;
this preserves its exact binary solution set. On the exploratory final quotient,
nonzero occurrences fell from 156,220 to 46,994. A separate sixty-second search
still ended unknown after 4,083 nodes. Short integer-row truth tables are now
built by meet-in-the-middle signed sums and packed into the same exact bitset
format, avoiding a full 2^width scan for each coefficient word.

Twenty targeted tests pass. Added controls exhaust every small literal fibre
before and after joint quotienting, check every local-hull consequence on all
small solutions, compare the quadratic lift with every nonzero modular solution,
compare reduced binary equations on every small bit assignment, and compare the
new truth tables with independent full enumeration through width sixteen.
Resource limits remain unknown; none of these controls is milestone acceptance.

### Recorded integrated runs and a wider hole parameter

The integrated `--joint-fields --reduced-xor --period 10 --seconds 300` run
stopped unknown after 3,248 branch nodes and 304 seconds including setup. It
retained 1,405 variables and 5,334 integer rows. Its three joint stages had
sign counts 1,407, 1,405, 1,405 and ternary dimensions 75, 74, 74; deduplication
and the dense-copy detector explain the different intermediate counts from the
exploratory cycle above. The final dimension is the same. Applying the quadratic
lift to that exploratory final fibre gave 2,702 product coordinates, 1,331
nonzero rows, verified rank 1,331 and nullity 1,371. No forced zero or signed
product relation, including dense copies, appeared, and no binary row was added.

`--moving --hole h` now permits every old first-arm interior vertex h=1..98;
the physical holes are ht and 99t. Default h=19 and old saved assignments retain
their meaning. The formal column derivation is unchanged: each hole contributes
its original-tree distance from every retained vertex. Tests additionally compare
all physical shell columns for h=1,43,98, including holes beyond the old shallow
range; that comparison uses explicit geometry rather than the shallow-recovery
helper, whose domain deliberately ends at 20t-1.

**Odd periods are impossible for this word ansatz, for every such h.** A formal
solution extends to every k>=1. For odd p, take k=1, so t=p+1 is even. The
retained support has 201t-1 vertices, an odd number. It cannot carry equally many
plus and minus signs. The identity K=0 forces balance by evaluation at z=1,
contradicting this count. Moreover at t>p+1 the formal/physical equivalence proved
above means that even a solution at one sufficiently large scale would extend
to this impossible scale. This excludes odd periods in this restricted ansatz,
not arbitrary signings or hole placements. The finite period-one probe over all
98 old hole positions independently encountered modular forced zeros; the
parity argument, rather than that census, explains their uniform failure.

The remaining obstacle is still the literal cube intersection, now with 74 free
original coordinates for the period-ten attempt. A refusal there would still
leave unrestricted inserted words and other supports open. No parametric
construction or all-pairs obstruction has been delivered.

A bounded additional support probe covered all 98 old holes at periods two
through six: all 490 cases encountered a verified modular forced zero. This
finite list does not prove a period-divisibility theorem. At period ten, a
150-second sweep reached h=1..76: h=2,4 were refused by modular nonzero constraints,
and the other 74 returned unknown under their two-second setup/search budgets.
Holes 77..98 were not reached. No existence or universal support claim follows.

The earlier 1,200-second requested joint search, before dense-copy grouping and
the table-construction optimization, ended unknown after 163,875 nodes and
1,229 seconds including setup. Its final 1,405-variable representation had
6,472 rows and dimension 74. It used the triangular binary basis, so its node
count is not a speed comparison with the later reduced-basis run. A final
`--moving --joint-fields --reduced-xor --hole 1 --period 10 --seconds 120` run
also ended unknown: 1,432 variables, 4,067 rows, dimension 79, 126 branch nodes,
124 seconds including setup. Neither run supplied an assignment or exhausted
its search tree. The deeper-hole compiler extension passes the same twenty-test
suite. No scientific or task-completion claim is inferred from a timeout.


## Mallow's continuation: desubdivision and a completed period-ten refusal

24 November 2026. **The task acceptance is still unmet.** This continuation
carries forward Linnet's preserved three-file contribution from private head
`302f4e8`; the source room started from an older integrated version. The
unrestricted support and word problem remains open. Priority is provisional.

### A necessary condition that does apply to arbitrary words

Colour a vertex black when its depth from the centre is even. Let a pair of
size k have a black vertices in its first set and b in its second. Every odd
distance joins opposite colours, so equality of the odd-distance counts gives

    a(k-a) = b(k-b),  hence  (a-b)(k-a-b) = 0.

Thus its retained black count a+b is even or equals k. This argument uses
all odd distance shells together and makes no word or hole-location assumption.
The helper `bipartition_support_obstruction` implements precisely this one
necessary condition; passing it does not assert homometry.

For t=7980m+1, put k=(201t-1)/2. Here k is even. The full tripod has k black
and k+2 white vertices. A pair of size k leaves two holes. Those holes must
have the same colour: removing one of each would leave the odd black count
k-1, which is not k. Consequently the moving support ht,99t is impossible
for even h, for **arbitrary signs**, not merely repeated words. This does
not rule out the other same-colour supports, or a larger full partition.

### Desubdivision lemma for the formal moving-word system

Specialize Z=z in the formal equations, even though the earlier geometric
argument stated only k>=1. Then every inserted column vanishes identically:

    P_r = z^r - z*z^(r-1) = 0,
    N_r = z^(-1)*z^(p+1-r) - z^(p-r) = 0.

What remains is (1-z^p) times the physical old-tripod shell polynomial on
T(99,79,23), with holes h and 99 and the old signs unchanged. The integral
polynomial ring has no zero divisors, so those old signs must themselves
form a homometric partition of the retained old support. This is necessary
for **every period p** in the formal ansatz. It is not a desubdivision
principle for unrestricted signings of a subdivided tree.

`coarse_projection_audit` substitutes Z=z coefficient by coefficient, retaining
every original formal column, and compares the result with independently
constructed physical columns multiplied by 1-z^p. It checks exact equality,
including cancellation of every inserted coordinate. At p=10, h=19 the audit
cancels 2,010 inserted columns and leaves 200 old coordinates and 178 nonzero
old physical rows. The earlier finite-graph path convention remains unchanged:
L-41 appended levels check centres 21..L-21; endpoint rows complete 0..L.

### An exhaustive four-way split, rather than another bounded branch run

For h=19, exact rational/binary/ternary signed-copy reduction of the old support
leaves 136 literal coordinates with a verified rational kernel of dimension
20. Free coordinates are original signs. Fixing the first free sign positive
leaves exactly 2^19 assignments. `kernel_sign_patterns` checks every one,
using two half-sum tables for each denominator-cleared kernel expression.
Only expressions equal to +1 or -1 survive. The verified kernel and reversible
signed aliases give both directions: every old signing occurs, and every
retained assignment lifts to an old signing. Normalizing the centre positive
therefore removes exactly complementation, with no duplicate or missing pair.

The recorded complete catalog has **four** centre-positive signings, each
splitting the old support into two sets of size 100. Direct pairwise distance
counters, independent of the shell equations, verify each of the four.
`verify_saved` accepts a saved positive coarse assignment only with this direct
check and explicitly calls its scope the original support, not an inflation.
A two-sign alteration preserving size is rejected in each of the four controls.
The catalog command completed in 0.94 seconds in this run; this is an observation,
not a runtime guarantee. Dimension/time caps return incomplete, never refusal.

Conditioning the original period-ten formal equations on each catalog entry
now closes all four branches. Each branch's joint reduction reaches 1,187
literal coordinates and a verified ternary forced zero. The integrated replay
completed in 125.84 seconds, with no sign branching or search timeout. A separate
branch-zero diagnostic found rational rank 2,154, then binary quotient size
1,187 and ternary rank 1,179. Its one forced-zero quotient class contains the
original coordinates (arm 1, edge 41, position 2) and the opposite of
(arm 3, edge 0, position 10). A literal sign cannot be zero modulo three.
This is a replayable computational refusal of this word ansatz, not a small
standalone negative certificate; the saved verifier deliberately rejects it.

For t=10k+1 with k>=2, formal and physical exponents do not collide, so this
refusal excludes **all period-ten moving-word signings** with holes 19t,99t,
including every resistant scale. It closes the 74-free-coordinate search left
by the previous continuation, but only by disjoining all old-support signings.
It does not cover other periods, independently free endpoint patches, arbitrary
inserted words, other first-arm holes, holes on different arms, or full partitions.

From the repository root, standard library only:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --audit-coarse --period 10 --hole 19
python3 projects/almost-halving-three-branches/resistant_spectrum.py --coarse-catalog --hole 19 --seconds 30 --write /tmp/old-catalog.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --coarse --hole 19 --seconds 120 --nodes 1000000 --write /tmp/old-pair.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/old-pair.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --condition-coarse --period 10 --hole 19 --seconds 240
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -q
```

The remaining mathematical obstacle is to decide unrestricted words and every
same-colour pair of holes (and larger full partitions), or to find a genuinely
extendable alternative word period and then verify every original distance
shell. No all-pairs upper bound or infinite positive family has been delivered.


### Uniform endpoint proof: every period, not a longer census

The old-support census is now complete for all h=1..98. Forty-nine even h
are excluded by the odd-distance shell above. Exact rational-cube enumeration
completes for the other 49. Only h=19 has any old signing: its four already
verified entries. The integrated `--coarse-supports --seconds 300` run completed
in 68.54 seconds, with no unknown support. This is a finite classification of
old supports; the desubdivision lemma makes it a necessary condition for
**every** formal word period, not just those tried in the earlier probes.
The cube filter skips one-coordinate tautologies before enumeration and starts
from a range rather than allocating all patterns first; a 24-free-coordinate
cap suffices for this census. Exhaustion, rather than timeout, decides each case.

It remains to exclude h=19 for all periods. This does not require any interior
transfer, periodicity inference from a census, or increasing search budgets.
Every term in an inserted column is a coarse monomial times z^u P_r or z^u N_r,
where u is 0 or 1. In formal row c, the possible positions are therefore

    from z^u P_r:  r=c-u or c-u+1;
    from z^u N_r:  r=p+1+u-c or p+u-c.

Keeping only c=0,1,p,p+1 sees positions 1,2,p-1,p. Relabel the first two as
left endpoints and the last two by offsets -1,0 from p. Coarse columns have
z exponents 0,1,p,p+1 as well. The powers of Z and all coefficients are then
independent of p. For p>=4 these endpoints are distinct. At p=2,3 some signs
are identified, which only restricts the same universal model. The row labels
remain distinct for every p>=2. Period one is impossible separately: the
specialization k=1 leaves 401 retained vertices, an odd support to partition.

`moving_boundary_system` constructs this one universal endpoint relaxation:
200 old signs, 804 independent endpoint signs, and 714 formal boundary rows.
It extracts exponents symbolically as beta*p+offset, without choosing a
representative period or assuming stabilization from examples.
`moving_boundary_audit` checks the exact coefficient map into any requested
p>=2, aggregating the identified signs at p=2,3 rather than silently dropping
them. Controls cover p=2,3,4,5,6,10,20,37 and other holes, and reject a changed
coefficient. These finite controls check the implementation; the displayed
index formulas establish why the model is uniform for unbounded p.

Conditioning these rows on each old catalog entry adds 199 homogeneous
signed-copy equations to the centre. All four relaxations are inconsistent:
branches 0,2,3 yield a verified ternary forced zero after the binary quotient
(373 coordinates); branch 1 yields a binary contradiction (259 coordinates).
The complete replay took 0.88 seconds including the old catalog. No short
ternary lift, interior row, literal branching or timeout was needed. In the
ternary cases the kernel is substituted back into every input row; a forced
zero cannot represent a sign. The binary step is the necessary parity system
of the integer equations. Thus these are exact algebraic refusals, not failed
search branches.

**Computer-assisted conclusion within this ansatz.** For every h=1..98 and
every positive integer p there is no formal moving-word signing with holes
ht,99t. For an actual scale t=pk+1 with k>=2, all formal exponents are distinct
under Z=z^t, so this rules out the corresponding physical repeated-word pair.
Consequently any actual target-size pair on those supports must have **no
common proper period dividing t-1 across all 201 inserted edge words**. The
four old signings exist, but none admits this uniform inflation.

This does not apply to arbitrary words by taking p=t-1: then k=1 and c=t
collides with c=0 in the next coarse row. The formal converse used above
fails exactly there. Nor does it apply to the earlier folded ansatz, whose
shallow hole is 19 rather than 19t. Other hole placements and larger full
partitions remain outside this particular refusal; the next subsection handles
full partitions by a different argument. The task's all-pairs acceptance is
still unmet. Further moving-period searches in this rejected method are
unnecessary; the remaining work must change the method or support.

Fast replay of the universal h=19 refusal, plus the whole old-support census:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --audit-boundary --period 2
python3 projects/almost-halving-three-branches/resistant_spectrum.py --boundary-refusal --hole 19 --seconds 30
python3 projects/almost-halving-three-branches/resistant_spectrum.py --coarse-supports --seconds 300
```

These negative reports are fresh-replay diagnostics, not portable standalone
certificates; saved-certificate verification rejects them. The positive old
assignments remain independently checkable with direct distance counters.
The period-eight and period-twelve full conditioned runs also refused all four
branches (67.48 and 300.60 seconds respectively), but the uniform proof makes
those runs logically redundant. The larger period-twenty run was intentionally
interrupted after the uniform refusal appeared; it supplies no search result.

An ancillary exact sign rule is available as `ternary_short_sign_rows`. If a
verified modular recovery expresses a sign as three signed free signs, their
sum cannot be +/-3 modulo three, so it must be +/-1 and equals the recovered
sign over the integers. For two terms the corresponding integer equation is
2x_i+sum=0. These rows may optionally augment `joint_sign_closure`; exhaustive
small modular-sign and integer-cube controls preserve every solution. Width
four is deliberately excluded, since sums +/-2 and +/-4 have different integer
lifts. This rule was not needed for the uniform endpoint refusal.


### An unrestricted full-partition upper bound by subdivision inheritance

The remaining larger-pair case can be closed without any word assumption.
For a full signing on T(a,b,c), the no-hole physical column of an arm vertex
(i,d) has exponents

    d+1,  L_i+1-d,  d+L_j+1 (j != i),

with coefficients +1,-1,-1,-1; the centre column is z-sum(z^(L_i+1)).
Let L_i=t*l_i. In shell rows e congruent to 1 modulo t, the first and last
exponents require d congruent to 0, and so does the reflected exponent.
No nongrid vertex can contribute. The old vertices d=t*q give exactly the
base columns after relabelling e=t*(E-1)+1. Hence a zero full signed shell
system on the subdivided tree induces a zero full signed shell system on
T(l_1,l_2,l_3), with every induced coordinate still a sign. Evaluating the
base identity at z=1 gives balance, so it really is a full homometric pair.

Thus **nonexistence of a full partition is inherited by uniform subdivision**.
This is a necessary reduction for arbitrary signs, not a periodic-word claim.
For the base T(99,79,23), the established fourth-root argument applies:
99+1,79+1,23+1 are 4*(25,20,6), whose quotient sum is 51, odd. Its signed
total polynomial would have to vanish at every fourth root, including 1.
Every depth-residue sum would then be zero, impossible because the four
residue classes contain 49,51,51,51 vertices. This reconstructs the relevant
case of [the full-partition obstruction](PUBLISHED_CASES.md#a-full-partition-obstruction-and-a-sharp-case).

For every odd t the scaled tree has N=201t+1 even vertices, and therefore

    h(T(99t,79t,23t)) <= N/2-1 = (201t-1)/2.

The earlier root-of-unity test applied directly at the scaled lengths does
not always give this bound. The inheritance proof does: it uses the fixed
base obstruction. At t=7981 the command below reports upper bound 802090.
This is exactly the project's lower target, so it does **not** refute or
establish its attainment. It does eliminate every larger full partition,
leaving exactly the two-hole case for every resistant scale.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --full-partition-bound 7981
```

`full_partition_subdivision_audit` independently reconstructs every finite
scaled column at several small unequal bases and scales, checking both that
all nongrid columns miss the chosen residue and that every coarse column
matches the base. The returned upper bound is strengthened only when the
base root obstruction applies and the scaled total is even. On odd totals
it retains the ordinary floor(N/2) bound, since a one-hole pair is a different
case. Twenty-eight focused tests now cover the new bounds, uniform boundary
maps and refusals, cube enumeration, direct distance witnesses, and all prior
spectrum controls.

The precise open target is now a two-hole pair of the required size, with
holes of the same colour, without a common proper period dividing t-1 on
the moving coarse-hole supports. Arbitrary inserted words, other hole depths
and holes on different arms have not been excluded. No all-pairs upper bound
strictly below the target, and no infinite positive family, has been obtained.

### Linnet: unrestricted even-hole refusals from exact fourth-root rows

24 November 2026. **The all-pairs acceptance is still unmet.** This step
excludes two classes of supports without prescribing any word or period.
For t=1 modulo 4, let the two holes have even depths (the centre has depth
zero). Then no target pair on that support exists in either case:

* t=1 modulo 8 and both hole depths are zero modulo 4;
* t=5 modulo 8 and one hole depth is zero modulo 4, the other two modulo 4.

The holes may be on any arms, at any permitted depths, including the centre.
Thus for the resistant t=7980m+1 family, even m excludes the first class and
odd m excludes the second. This is a support obstruction, **not an all-pairs
obstruction**: for example the previously studied odd-depth holes are untouched.

Here is a short algebraic proof. Reduce the exact physical shell polynomial
modulo z^4-1, over the rationals. Its four coefficients must all vanish. Since
all three L_i+1 are divisible by four, the full column of a depth-d vertex is

    (z-2) z^d - z^(-d).

This formula also holds for the centre. Each removed hole adds
(z-1) z^distance to every retained column. Write coefficient vectors in order
z^0,z^1,z^2,z^3. For even holes every odd-depth vertex has one of these columns:

    (0,-4,3,-1), (1,-3,2,-2), (2,-2,1,-3), (3,-1,0,-4).

The choice depends on the arms and order of the holes, but both weight vectors
below annihilate **all four** possibilities. Even-depth columns do not depend
on those choices, because negating an even residue preserves it modulo four:

| Hole residues | Depth-zero column | Depth-two column | Row weights |
| --- | --- | --- | --- |
| 0,0 | (-5,3,0,0) | (0,0,-5,3) | (-7,-1,-3,-5) |
| 0,2 | (-4,2,-1,1) | (-1,1,-4,2) | (-9,1,-1,-7) |

Each listed weight vector has dot product 32 with its depth-zero column and
zero with every other possible column. Therefore the sum of signs on retained
vertices at depth zero modulo four must be zero. Before removing holes that
class has 1+sum floor(L_i/4)=(201t-5)/4 vertices. Its retained size is
(201t-13)/4 in the first row, or (201t-9)/4 in the second. That size is odd
in exactly the two cases stated above. A sum of an odd number of signs cannot
be zero. No search, repeated-word assumption or large-scale limit enters this
proof.

The implementation returns integer row-combination certificates for any odd
column group isolated by rational elimination. A separate checker verifies
every column dot product and its odd multiplicity; it does not trust the
elimination. `residue_shell_groups` compiles arbitrary supports in time
independent of arm length: between successive holes the distance exponents
are affine with slope plus or minus one, so their residue columns repeat
every four depths. Tests compare this compilation with every original column
for all two-hole supports of several small unequal trees, check certificates
against exhaustive literal assignments, reject altered certificates and verify
the displayed weights at ordinary and resistant scales.

A broader finite classification is also replayable:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --fourth-root-census
python3 projects/almost-halving-three-branches/resistant_spectrum.py --residue-zero 7981 --holes 1:4 2:2 --period 4 --write /tmp/support-refusal.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/support-refusal.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -q
```

This replay covers **all hole placements**, t>=9 and t=1 modulo 4, using finite
representatives. On an arm with k holes, split the retained depths into k+1
nonnegative gaps. Reducing any gap g>=12 to 12+(g-12) modulo 32 preserves all
column vectors, their multiplicities modulo eight, and each group's available
signed sums modulo eight: each residue occurs at least three times, and adding
32 adds eight copies of each column. Every reduced gap lies in 0..43. Conversely,
a reduced tuple lifts to the desired length by adding the remaining multiple
of 32 to a gap at least 12. With at most two holes, reduced total length is at
most 131. All actual arms here exceed it. Thus the representative types depend
only on arm lengths modulo 32, covered by the eight t residues 1,5,...,29.
The program includes same-arm, different-arm and centre-hole supports.

Recorded replay: 139,200 representatives, 20,706 congruence signatures.
The modulo-eight version of the four residue equations refuses 69,600, exactly
those already refused by the odd-distance shell. **Congruence compatibility
misses an exact obstruction:** rational row combinations refuse another 13,260
representatives, leaving 56,340 undecided by this method. These numbers count
representatives, not actual supports or proportions of pairs. The proof above
is independent of the census. The remaining obstacle is construction or an
obstruction for all surviving supports; neither rational compatibility nor a
finite support census decides unrestricted homometry.

The portable example at t=7981 isolates 401,043 retained depth-zero vertices
with row weights (-9,1,-1,-7), coefficient 32. Its verifier rebuilds the exact
support before checking the certificate. Unknown searches are not accepted as
certificates. The 35 focused tests pass, including JSON-shaped hole coordinates
and saved-certificate mutations. The census and certificate checks use only the
standard library and take seconds, independently of the physical scale.

#### A further unrestricted refusal at eighth roots

The same checker yields another infinite support obstruction. On
T(99t,79t,23t), **holes (1,2),(1,4) cannot attain the target when t=1 modulo
16**, with arbitrary signs on every retained vertex. In the resistant family
this covers m=0 modulo 4. The fourth-root mixed-hole proof above leaves these
scales open, so this is an additional refusal, not a repeat of that result.

For t=1 modulo 8 the arm lengths have residues 3,7,7. Reducing their physical
columns modulo z^8-1 gives exactly these nine vectors:

```text
(-2, 1,-1, 1,-2, 1, 0, 0)  target
(-2, 1, 0, 0,-2, 1,-1, 1)
(-1, 1,-3, 1, 0, 0,-1, 1)
( 0,-3, 2,-2, 1, 0, 0, 0)
( 0,-1, 1,-1, 1,-2, 1,-1)
( 0, 0,-1, 1,-1, 1,-3, 1)
( 1,-2, 1,-2, 1, 0, 0,-1)
( 1,-2, 1,-1, 0,-1, 1,-1)
( 1, 0, 0,-1, 1,-2, 1,-2)
```

This is a bounded symbolic calculation: substitute the length residues into
the physical column formula, treating the centre, first-arm depths 1 and 3,
first-arm depths at least 5 in eight residue classes, and the eight classes
on each other arm. Those classes exhaust the vertices; beyond depth 4 both
hole distances are affine, so adding eight changes no column.

Weights (-25,-15,-1,25,7,17,-1,-39) have dot product 64 with the target and
zero with all eight other columns. The target group consists of the centre,
long-arm depths 4 modulo 8 except the removed depth 4, and depths 0 modulo 8
on the other arms. Its size is

    1 + (99t-11)/8 + (79t-7)/8 + (23t-7)/8 = (201t-17)/8.

It is odd exactly when t=1 modulo 16. Its forced zero sign sum is impossible.
This proof is independent of larger-root searches and assumes no word period.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --residue-zero 31921 --holes 1:2 1:4 --period 8 --write /tmp/eighth-root-refusal.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/eighth-root-refusal.json
```

The additional test checks every symbolic column class, its multiplicity and
all dot products at both parities of t=1 modulo 8, rejects the even-count
certificate, and verifies a portable refusal on a resistant scale. No surviving
support is thereby constructed or ruled out; the global task remains open.

Both contributions pass all 36 focused tests. An exploratory integer-lattice
probe at 32nd roots was interrupted before its first scale phase completed;
it supplies no classification or impossibility result and is not part of the
shipped checker. Increasing the root order alone has not resolved the remaining
odd-hole supports, including the original shallow-hole and long-tip support.

#### Complete integer-parity relaxation with bounded arithmetic

The checker now separates three questions: a zero group; an integer aggregate
solution with the required parities; and a literal physical signing. Only the
last would construct a pair. The new integer relaxation deliberately omits
|S_j|<=n_j, where S_j is the sum of signs in a column group of multiplicity n_j.
For example S_1+3S_2=0 admits odd aggregates (-3,1), but two singleton groups
cannot realize them. Every output retains `all_pairs_decided: false`.

For a residue-column matrix C, ask C*S=0 with S congruent to n modulo two.
Integer Euclidean row and column operations give U*C*V=D with U,V unimodular
and D diagonal (ordering the diagonal divisors is unnecessary). For pivot d,
the original row combination U_i*C has gcd |d|. Its primitive coefficients
must have even dot product with n. This is also sufficient for **unbounded**
aggregates: the pivot coordinates of V^-1*n are even, so they can be changed
to zero by adding twice an integer vector. Free coordinates impose no equation.
`residue_integer_parity` checks this exact criterion. Large coefficients or an
expired work budget yield unknown, never compatibility or refusal by exhaustion.

`residue_dyadic_parity` computes the same criterion with bounded arithmetic.
Let H be the largest squared column norm, r=min(number of rows,number of
columns), and B=1+r*ceil(bit_length(H)/2). Hadamard bounds every nonzero minor
strictly below 2^B. Consequently every nonzero Smith divisor has two-adic
valuation below B. Elimination modulo 2^B chooses an entry of least valuation,
normalizes its odd factor by modular inversion, and clears its row and column.
No hidden nonzero divisor can be lost modulo this modulus. Every visible pivot
forces its transformed aggregate coordinate even; these parity conditions are
therefore exactly the integer conditions above, not merely a small-modulus
probe. The all-zero matrix is harmless. Required B exceeding the bit budget,
or time exhaustion, still returns unknown.

A refusal in either algorithm consists only of integer row weights w and a
positive divisor d. The independent verifier checks d divides **every exact**
column dot product w*C_j, then checks sum((w*C_j/d)*n_j) is odd. This proves
the contradiction without trusting either elimination, its rank or its modulus.
Weights are reduced into [-d,d) modulo 2d; this preserves divisibility and the
primitive parity, and keeps the portable proof short even when elimination
used large integers.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --residue-parity 31921 --holes 1:2 1:4 --period 16 --dyadic --seconds 30 --write /tmp/integer-refusal.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/integer-refusal.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --residue-parity 7981 --holes 1:19 1:790119 --period 256 --dyadic --seconds 30
```

The finer period-sixteen grouping has no individually forced odd zero group,
but the integer checker recovers the eighth-root parity contradiction. On the
original odd-hole support at t=7981, the Euclidean version with a 256-bit limit
returns unknown at orders 64,128,256. The bounded modular version completes
all three, including order 256 in about 3.4 seconds in the recorded probe, and
reports compatible **unbounded aggregates**. This is a limitation result for
that relaxation, not a physical signing.

Controls compare both algorithms with complete tiny integer-lattice enumeration,
compare them on larger random integer matrices, independently verify every
refusal, reject altered divisors and weights, and check resource-limit results.
A deliberately scaled equation invisible modulo 2^30 still refuses after the
Hadamard-sized saturation, guarding against treating a fixed small modulus as
complete. The full physical shell equations and literal bounds remain necessary.

Compatibility can now be independently checked as well. With
`--retain-residue-witness --write FILE`, the dyadic solver records a vector
of aggregate residues modulo 2^B. The small verifier recomputes the Hadamard
bound, checks every aggregate parity and every modular row, and never runs
elimination. This is sufficient for an exact **unbounded integer** solution:
in integral Smith coordinates, d_i*y_i=0 modulo 2^B and v_2(d_i)<B force
every constrained y_i even. Set those coordinates to zero and retain the free
coordinate parities; the inverse unimodular change of coordinates gives an
exact integer kernel vector with the required original parities. This argument
asserts no bounds on its coordinates and does not round it to literal signs.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --residue-parity 7981 --holes 1:19 1:790119 --period 256 --dyadic --seconds 30 --retain-residue-witness --write /tmp/unbounded-aggregates.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/unbounded-aggregates.json
```

Recorded: 513-bit modulus, 784 aggregate residues, independent verification
passes. The CLI prints a short summary and keeps the vector in the requested
file. All 41 focused tests pass, including compatibility-witness mutations and
saved status/scope checks. No large certificate or transcript is added to Git.

The bounded family audit runs the same relaxation for both named supports,
(1,19),(1,99t) and (1,19t),(1,99t), across every resistant scale phase:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --audit-resistant-residues --period 256 --seconds 900 --max-bits 1024 --write /tmp/resistant-residue-audit.json
```

For each listed root order p, the scale phases are exactly
2p/gcd(7980,2p), represented by t=7980m+1 with m from one through that count.
Increasing t by 2p preserves all physical column exponents modulo p. For the
fixed shallow hole, its short patch is unchanged and the long interval grows
by 198p. For the moving hole, the long-arm intervals grow by 38p and 160p;
the other two arms grow by 158p and 46p in either case. Thus each residue
column gains an even number of copies. All varying intervals already exceed
p in these representatives (p<=256), so no new column type appears. Both the
column set and its multiplicities modulo two are invariant. This is an exact
finite covering of the integer relaxation for every m>=1, not an inference
from a list of consecutive scales. It excludes neither support by itself.

Each order's expected case count is twice its scale-phase count. A full order
with every case compatible establishes only the failure of this particular
integer relaxation to refute those two supports. Unknown cases or a work-limit
exit leave that order undecided. No finite list of orders is a theorem about
all orders, and no compatible aggregate vector is a homometric pair.

Recorded 900-second family audit, 24 November 2026:

| Root order | Expected cases | Compatible | Unknown | Not run |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 4 | 4 | 0 | 0 |
| 8 | 8 | 8 | 0 | 0 |
| 16 | 16 | 16 | 0 | 0 |
| 32 | 32 | 32 | 0 | 0 |
| 64 | 64 | 64 | 0 | 0 |
| 128 | 128 | 128 | 0 | 0 |
| 256 | 256 | 188 | 1 | 67 |

No refusal was found. The complete first six rows establish that **neither
named odd-hole support can be excluded by the unbounded integer residue
relaxations at orders 4,8,16,32,64,128, for any resistant m>=1**. This is a
method limitation, not existence. The order-256 row is incomplete; its timeout
and unrun cases have no mathematical outcome. It should not be repeated merely
to turn this partial table into a larger census. The original all-pairs target
requires a literal construction or an obstruction stronger than these completed
relaxations. No project or task acceptance is claimed.

### Rook: retaining the aggregate bounds still leaves the low orders open

24 November 2026. Recovered Linnet's exact three-file continuation from the
trusted stopped-contribution inspection, preserving it separately in `e04ffd8`.
**The task acceptance remains unmet.** This continuation changes the relaxation,
not the target: it retains both integer parity and the physical bounds
`|S_j| <= n_j` on each residue-column group's sign sum.

`residue_bounded_search` records reversible integer column operations during
Euclidean diagonalization. Starting with zero pivot coordinates and small free
coordinates of the required parity, it reverses those operations to obtain an
exact integer kernel vector. Large groups are preferred as pivots. This is a
witness search: a missed witness, coefficient limit or timeout is unknown.
The separate `verify_bounded_residue_witness` checks every original residue
row, every parity and every physical bound using integer arithmetic alone.
It trusts neither diagonalization nor the search. The distinction matters:
`S_1+3S_2=0` with singleton groups passes the unbounded test but fails the
bounded test; the new verifier rejects the unbounded witness `(-3,1)`.

For both named supports, **the bounded residue relaxation is feasible at root
orders 4, 8 and 16 for every resistant t=7980m+1, m>=1**. The audit checks
4, 8 and 16 representative cases respectively, all with independently checked
bounded witnesses and no unknown case. This is not a claim about other orders.
For each order p the phase count is `2p/gcd(7980,2p)`. Within a phase, increasing
t by that many increments of 7980 preserves the column set and its parities.
Every growing interval gains an even number of copies of each column; the
shallow fixed patch is unchanged. Counts therefore never decrease. The same
bounded witness from the first scale stays within every later bound. This
monotonicity, not sampling successive scales, extends the finite audit.

Each accepted group sum is physically realizable: choose `(n_j+S_j)/2` of
that group's vertices positive and the rest negative. The residue equations
also force total sign sum zero, since every column sums to -2. Thus these
are genuine equal-size sign partitions satisfying the *projected* equations.
They need not satisfy the original individual distance shells. The saved
verifier explicitly preserves that distinction and never claims homometry.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --audit-resistant-residues --period 16 --bounded --seconds 30
python3 projects/almost-halving-three-branches/resistant_spectrum.py --residue-parity 7981 --holes 1:19 1:790119 --period 16 --bounded --write /tmp/bounded-residues.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/bounded-residues.json
```

The first command completed in under a second in this room. The second saved
58 exact sums, verified independently. Controls compare kernel reconstruction
and accepted witnesses with exhaustive tiny bounded cubes, reject altered sums,
wrong parity and excessive magnitudes, and reuse each phase witness at much
larger scales. Larger-root probes were unknown for the shallow-hole support at
orders 32 and 64; these are failed witness searches, not obstructions. The
remaining obstacle is still a literal solution to every original distance shell
or an all-pairs obstruction. Merely adding group bounds at orders through 16
cannot provide that obstruction on either named support.

All 43 focused tests pass; the saved bounded witness and the full bounded
phase audit also pass through the command-line interface.

### Tern: every fixed finite collection of residue tests has false positives

24 November 2026. **The target remains open.** This is a method limitation
with explicit literal colourings, not another proposed homometric family.
The preceding continuation was recovered from Rook's inspected stopped run
`a6c249aa8e1f4cf4b9eba981a5a68724`, including its complete test file; its
43 focused tests passed before this extension. No publication is asserted.

**Theorem.** Fix any finite nonempty collection of positive integers
p_1,...,p_s. Put P=lcm(p_1,...,p_s), D=lcm(7980,2P). For every j>=1, set
t=Dj+1. On T(99t,79t,23t) there are disjoint sets A,B, each of target size
(201t-1)/2, whose pair-distance multiplicities agree after grouping distances
modulo every p_i. Nevertheless A has exactly **one fewer pair at distance
one** than B. In particular these are not homometric sets. Thus no fixed
finite collection of root-of-unity/residue equations, even with literal signs,
exact support, balance and group bounds enforced jointly, can rule out the
entire resistant family. This does not assert compatibility for arbitrary
scale-dependent orders, all orders together, or individual distance shells.

There is also a growing-order corollary: **at every resistant scale**
t=7980m+1, take P=3990m. The same construction passes the entire distance
profile modulo P and hence modulo every divisor of P, yet still fails at
distance one. Here the interior word on each old edge is just P plus signs
followed by P minus signs. Thus even a residue order growing linearly with
the scale can miss the defect. This covers these particular growing orders;
it makes no claim about other scale-dependent tests or all orders together.

**Construction.** Use the recorded, directly recounted t=1 pair from
`residue_2660.t1_witness`: centre negative, holes 1:19 and 1:99, 100 vertices
of each sign. Its two other leaves are positive. Multiply all old depths by
t and keep their signs. On each of the 201 old edges, give its t-1 inserted
vertices the word

    (+ repeated P times, - repeated P times) repeated (t-1)/(2P) times.

The only holes are 1:19t and 1:99t. Every inserted block is balanced, so
both sets have 100+201(t-1)/2=(201t-1)/2 vertices. This specifies every
vertex, with no free word, search, asymptotic assertion or omitted endpoint.
`residue_lift_sign(P,t,(arm,depth))` evaluates any coordinate directly.

**Proof of all modular profiles.** Let K be the exact signed shell polynomial
used above and let Delta(z) be the difference of the two unordered
pair-distance polynomials. Balance gives K=2(1-z)Delta. Work modulo z^P-1.
Since t=1 modulo P, every old vertex column, including its hole-distance
terms, is identical to its original t=1 column after reduction. Their signed
sum is therefore zero. In each old edge, match an inserted vertex in a plus
block to the vertex P depths later in the following minus block. Both are
strictly inside the same old edge. All hole positions are old vertices, so
each distance to a hole changes by either +P or -P, without crossing a hole.
The no-hole column exponents also change by +/-P. The two complete columns
are identical modulo z^P-1, and their opposite signs cancel. This covers
every inserted vertex, proving K=0 in the quotient.

Multiplication by 1-z has a one-dimensional kernel in Q[z]/(z^P-1):
a reduced polynomial in that kernel has all P coefficients equal. Hence
Delta modulo z^P-1 is a multiple of 1+z+...+z^(P-1). But Delta(1)=0,
since the sets have equal sizes, so that multiple is zero. This balance
step is essential; cancelling 1-z directly in this quotient would be invalid.
Reduction modulo each z^p_i-1 follows because p_i divides P.

**Proof of the exact failure.** In the induced retained tree, every vertex
has degree two except the centre (degree three), the two retained leaves,
and the three neighbours of the two holes (each degree one). Balance yields

    2 Delta_1 = sum_v (degree(v)-2)*sign(v).

The centre contributes -1, the two leaves contribute -2, the neighbours of
1:19t have signs -,+ and contribute +1,-1, and the neighbour 1:(99t-1)
has sign - and contributes +1. Thus 2 Delta_1=-2 for every index. This is
a witnessed failure at an individual shell, despite exact compatibility of
all the requested modular profiles. It supplies no upper bound on other pairs.

**General tree form.** The modular construction also works on any finite
base tree with a balanced homometric signing and any set of old holes. For a
vertex v of a hole-free tree, let F_v(z) count the other vertices by distance.
The sphere recurrence gives the exact identity

    (1-z) F_v(z) - 2z = sum_u (degree(u)-2) z^(distance(v,u)+1).

Indeed, beyond radius zero each vertex has one parent, so the next sphere
minus the current sphere has size sum(degree(u)-2) over the current sphere;
the radius-one coefficient is degree(v). Removing a hole h adds
(z-1)z^distance(v,h) to the right side. Under uniform subdivision the new
vertices have degree two and disappear from that sum. Only old vertices and
old holes remain, all distances to which are affine with slope +/-1 inside
an old edge. The same cancellation proof therefore applies unchanged.
The new equal sizes are k+|E|(t-1)/2 when the old sizes were k. This is a
statement about distance profiles modulo P; the distance-one failure proved
above belongs to the particular tripod colouring, not to every base tree.
A separate test builds a branched tree, subdivides its adjacency graph, and
uses breadth-first distances for several base pairs and moduli to check this
general form, including paths through old holes.

A real compact run, from the repository root, standard library only:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --residue-lift 3 16 19 --write /tmp/residue-lift.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/residue-lift.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -q
```

Recorded output: t=63841, P=912, each set has 6,416,020 vertices, with
6,415,920 inserted opposite pairs. Verification reports modular profile
equality and one fewer positive distance-one pair. All 46 focused tests pass.

The checker directly recounts the small base pair, compares all 200 old
columns after specialization, and checks the six exceptional degrees without
expanding the large scale. Tests separately materialize the construction at
eight smaller period/scale combinations and count **every unordered pair**;
all modular profiles agree and every distance-one difference is -1. They also
check huge periods and indices with bounded-size arithmetic data and reject
altered saved claims. This proof replaces further fixed-order probes as a
route to excluding the whole family. The remaining obstacle is an exact-shell
construction, or an obstruction covering all pairs on all surviving supports;
this run obtains neither, and priority remains provisional.

### A construction attempt with independent patches at every old edge end

The uniform-word refusal does not apply if finite patches at **all 402 old
edge ends** are independent. `moving_periodic_system(p,h,w)` now compiles
that larger ansatz; the default w=0 preserves the previous compiler exactly.
Holes remain ht,99t, but every other old sign is free. In each old edge the
first and last w inserted signs are independent, and its middle repeats one
independent p-sign word. Require p|2w and t=1 modulo p, t>=2w+p+1.
This is a possible positive construction method, not an unrestricted reduction.

For word position r=1..p, multiplying its geometric sum by 1-z^p gives

    P_r = z^(w+r) - Z*z^(-w+r-1),
    N_r = Z^(-1)*z^(p+1+w-r) - z^(p-w-r),   Z=z^t.

Here P_r is the forward sum and N_r the reflected sum. Patch signs use
individual physical columns, also multiplied by 1-z^p. All formal coefficients
are retained, including negative constant offsets in the Laurent representation.
A formal zero specializes to (1-z^p)K=0 at every admissible t. Cancelling that
nonzero polynomial in Q[z] proves every shell vanishes; K(1)=-2 sum(signs)
then gives balance and the target size. No converse or observed rank pattern
is needed for this implication. Saved positive assignments rebuild and check
all formal equations, and report the admissible minimum scale. Unknown search
results are rejected by the verifier.

The new column test compares every formal column, specialized at two scales,
with the sum of all corresponding original physical columns times 1-z^p.
It covers (p,w,h)=(1,1,19),(2,4,19),(3,3,7),(4,4,19),(8,8,19), including
every old coordinate, both patches, each geometric endpoint and every word
position. It rejects a fabricated positive assignment and keeps a zero-node
search unknown. These checks control the compiler, not the target theorem.

A bounded exact attempt (its budget includes reductions) is replayable as:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --moving --period 2 --edge-patch 4 --joint-fields --affine-shells --seconds 900 --nodes 10000000 --free-order connected --write /tmp/patched-moving.json
```

This patch mechanism differs from the earlier folded-level endpoint patches:
it applies at every coarse edge, with the shallow hole moving to 19t. A
refusal of this ansatz would still leave other words and other supports open.

Recorded first run: p=2,w=4 compiles 2,210 signs and 2,138 formal rows.
The ternary and joint-field quotients reached 1,358 signs and 69 binary free
coordinates. Local shell closure added no binary rows. The command above
returned **unknown** after 35,590 nodes and 906.47 seconds, including reductions.
No refusal or positive certificate resulted. The existing `--short-recovery`
option now also reaches moving-word joint closure; it had previously been
passed only to the conditioned coarse-word route. Its exhaustive small-sign
controls pass, as do all 47 focused tests after this wiring change.

For discovery only, the already-installed CP-SAT solver was also given the
exact quotient with short recovery rows: it reported infeasible after 19,357
branches (222 seconds including quotient setup). This is **not a shipped
portable refusal proof**, and concerns only p=2,w=4. Direct unreduced CP-SAT
and Z3 attempts on the same ansatz each returned unknown at 600 seconds.
Neither installed solver is a dependency of the delivered checker. No package
was installed. A positive discovery would have to pass the standard-library
verifier against every untouched formal shell before being used as a result.

The standard-library replay with `--short-recovery` and a 600-second budget
also returned unknown: 21,247 nodes, 606.09 seconds including reductions.
The different budgets and ordering do not support a speed comparison. No
positive assignment or portable refusal was obtained from either replay.

Rook independently reviewed the immutable modular-colouring proof at journal
41883: rebuilt four small signings, counted every unordered pair, and checked
the specialization, balanced quotient kernel and exceptional-degree argument.
No error was found. That review certifies neither this room's checker source
nor the project's unresolved milestone; independent source integration remains
separate.

Further experimental ordering used binary and ternary signed quotients,
including short recovery rows, before 600-second standard-library branching
budgets. It returned unknown at (p,w)=(4,4),(8,8),(16,16), after respectively
39,074, 10,487 and 6,669 nodes. These are scoped search failures, not proofs of
infeasibility, and no exact-shell witness was produced.

The final direct installed-solver attempts at (p,w)=(4,4) and (8,8) also
returned unknown at their 600-second budgets. All discovery processes ended
without a positive assignment. No all-pairs upper bound below the target has
been obtained. The task remains open: the next useful advance needs a genuine
formal-shell solution, a different exact construction, or an obstruction that
covers every permitted pair; further fixed-order root probes cannot by
themselves exclude the whole resistant family proved compatible above.

### Sorrel: reconcile the stopped continuation

24 November 2026. Reconstructed the three complete per-path diffs for stopped
run `66ee535d9a86472d96059c8f3909b1fd`, contribution `fe33972`, against
its recorded base `aa045c1`; every removed/context line matched that base.
The candidate source retains every current function and all current tests;
its changes add bounded aggregates, modular-colouring lifts and independent
edge patches. Retained the later shared 900-second residue audit and its
incomplete order-256 row alongside the candidate's new sections. No recorded
failure was replaced. All 47 focused tests pass (26.826 seconds); the shared
baseline's 41 tests had passed separately. This resolves source overlap only;
the all-pairs acceptance and provisional priority remain unchanged.

### Sorrel: flat pieces fail uniformly, even without a repeated word

24 November 2026. **The all-pairs target remains open.** A different attempt
lets every old edge have independently signed long constant pieces. This
allows a word with just one change on an entire edge, so it is not the
previous common-period ansatz. It too has an exact obstruction.

**Scoped theorem.** Let p>=2 and L>=179 with pL even, and put t=pL+1. Omit first-arm
vertices 19t and 99t. Subdivide each old edge's inserted vertices into p
successive pieces of L vertices each. There is no target pair whose sign is
constant within every such piece. Each old retained vertex and each piece
can otherwise have its own independent sign, including every third-arm piece.
For resistant t=7980m+1 this applies to every divisor p>=2 of 7980m for which
L=7980m/p>=179. In particular two flat halves cannot attain the target for
any m>=1. Arbitrary words, unaligned changes and other supports are untouched.

**Exact equations.** Write a monomial as (q,c), meaning z^(qL+c).
For an edge numbered e from zero, piece r=0,...,p-1 has depth interval

    [(pe+r)L+e+1, (pe+r+1)L+e].

Use the original physical K column, not an assumed transfer or rank formula.
For a term a*z^(d+B*p*L+C), summing over this interval and multiplying by
1-z leaves a at (p(e+B)+r,e+1+C) and -a at
(p(e+B)+r+1,e+1+C). For a reflected term a*z^(-d+B*p*L+C),
the two endpoints are a at (p(B-e)-r-1,C-e) and -a at
(p(B-e)-r,C-e). The hole terms are of exactly these forms, because no old
hole lies strictly inside an old edge. Old vertices use their single physical
columns multiplied by 1-z; the centre is retained explicitly.
`split_edge_system` implements these endpoint sums symbolically. It also
allows independent patches at both ends of each piece, as a separate search
method; the uniform theorem here uses patch width zero only.

For the unpatched equations every constant offset lies in [1,179],
independently of p. If L>178, distinct (q,c) cannot specialize to the same
exponent: |c-c'|<=178<L. Consequently an actual zero shell polynomial in
this ansatz must satisfy every separate formal coefficient equation. This
converse is why the lower bound L>=179 matters; small-scale column tests
alone would not establish it. Conversely any formal zero specializes to
(1-z)K=0; cancellation in the polynomial ring gives K=0, including balance.

**One fixed necessary system for every p.** Retain only formal rows with
q divisible by p. The displayed endpoint formulas show that only r=0 and
r=p-1 enter these rows. Rename those pieces first and last, and divide q
by p. All their coefficients, every old sign and every retained row are now
independent of p. The first/last pieces are distinct even at p=2. Thus the
p=2 extraction in `split_endpoint_system` gives precisely the same necessary
system for every integer p>=2: 602 signs and 535 nonzero rows.

For each integer row sum(c_i*s_i)=0, set s_i=2b_i-1. An odd sum(c_i) is
already a refusal; otherwise the necessary binary equation is
sum((c_i mod 2)*b_i)=sum(c_i)/2 mod 2. The generated endpoint certificate
XORs indexed binary rows to zero on every coordinate and one on the right.
The independent verifier checks that contradiction using the untouched
integer rows. It does not trust a rank, kernel, branch search or time limit.
The endpoint formulas establish the unbounded-p identification; finite tests
merely control its implementation.

From the repository root, standard library only:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --split-endpoints --write /tmp/flat-refusal.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/flat-refusal.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -q
```

The real run generated and independently accepted the parity refusal. All
49 focused tests pass (27.169 seconds). New controls specialize every compiled
column against sums of original physical columns at six piece/patch/hole
configurations and two endpoint scales each, including coincident monomials.
They compare the entire normalized endpoint system at p=2,3,4,7,10,31;
reject an empty refusal and fabricated positive assignment; and retain all
47 predecessor tests. No large certificate is committed.

The two-piece attempt with one independent vertex at every piece end also
has a directly verified formal parity refusal (1,406 variables, 1,603 rows).
That extra observation is scoped to that patch width; it is not a theorem
for arbitrary patches. The remaining mathematical obstacle is to make
nonconstant words satisfy the exact shells, or to exclude all surviving
supports without assuming flat pieces. Neither a project finish nor the
main task's acceptance is claimed here.

### Independent repeating words inside the pieces

The flat-piece refusal does not exclude nonconstant words. The same compiler
now accepts `word_period=q`: each piece has its own q-sign word, with L a
multiple of q; first/last w vertices of every piece remain independent.
Require q|2w and L>=2w+q. For word position j=1,...,q in piece r, put
A=(pe+r)L+e+w+j. Its depths are

    A, A+q, ..., A+L-2w-q.

Multiplication by 1-z^q changes the forward geometric sum into
z^A-z^(A+L-2w), and the reflected sum into
z^(-A-L+2w+q)-z^(-A+q). Each independent patch or old sign uses its
individual physical column multiplied by 1-z^q. These formulas specify all
coefficients without sampling L. A formal literal zero therefore proves
K=0 at every admissible L, by cancellation in Q[z]. The positive verifier
rebuilds all original formal rows; it trusts neither the quotient nor the
search status. The earlier flat-piece theorem is still only q=1,w=0.

An exploratory q=2,p=2,w=4 run had 4,220 literal coordinates. Joint exact
reductions, with short recovery rows, reached 2,682 coordinates, rational
nullity 132 and 133 binary free coordinates. No further signed merge was
found. The 600-second attempt ended unknown after 1,047 search nodes and
609.505 seconds including reductions and search. It found neither a literal
assignment nor a refusal. The compiler's columns were independently checked
against every physical shell at w=0,2,4 and two admissible scales each before
that search. This method, including its replay command, is retained rather
than relying on the temporary discovery script:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --split-edge --edge-pieces 2 --piece-period 2 --edge-patch 4 --seconds 600 --nodes 10000000 --write /tmp/segmented-word.json
```

A positive result would cover the resistant family, since L=3990m is even
and exceeds the minimum L=10. An unknown file is not a witness. A later
builder still needs an exact-shell signing or a genuinely unrestricted
obstruction; the remaining 132-dimensional literal problem is not solved
by the verified rational dimension.
The retained implementation passes all 49 focused tests (31.199 seconds),
with the physical-column controls extended to q=2 and q=3, and invalid
period/patch combinations rejected. No solver dependency was added.

The separate enlarged original moving-word attempt also finished without a
witness: period two, edge patch width eight, joint fields, short recovery and
local affine closure, with an 1,800-second budget. Joint closure took 1,630.266
seconds and settled at 2,518 signs, rational nullity 253 and 254 binary free
coordinates. Local affine closure added no rows. The whole attempt ended
**unknown**, after 4,112 branch nodes and 1,808.726 seconds. No refusal or
positive assignment resulted. Replay with `--moving --period 2 --edge-patch 8
--joint-fields --short-recovery --affine-shells --seconds 1800 --nodes 10000000
--free-order connected`. This is a witnessed failure of this attempt, not an
upper bound; increasing patches or budgets has supplied no theorem here.

Tern independently checked the frozen flat-piece proof and its refusal at
journal 42041, including the endpoint map, injective specialization and an
independent binary replay. That review covers the scoped obstruction, not the
later repeating-word extension or the unresolved project milestone. The
current continuation leaves the main task open. The next useful step is an
exact literal solution or stronger reasoning about the surviving sign fibre
(the segmented attempt has rational nullity 132), or a different support;
more fixed-order residue censuses cannot exclude the whole resistant family.

A final boundary audit covers the allowed case q|2w but q does not divide w:
(q,w,p,h)=(2,1,2,19),(4,2,3,7),(6,3,2,19). An independent direct-column
recount passed at six scales, checking 23,712 complete columns; the permanent
column test now includes these three cases as well. This closes a test gap in
the geometric endpoint handling, without changing the compiler or its scope.

### The growing-block lift is far from an exact pair on its support

Sorrel, 24 November 2026. This is a limitation of a construction, **not an
all-pairs obstruction**. For every odd t>=3, put P=(t-1)/2 and use the
recorded old signs and the inserted word +^P -^P on each old edge. Its
physical holes are 1:19t and 1:99t. Let K be its exact signed shell
polynomial. Then

    ||K||_1 = 500t-256.

Consequently every exact target-size pair on this same retained support
must differ from this lift at at least ceil((500t-256)/16) vertex signs.
Global complementation of the lift gives the same bound. At t=7981 this
is 249,391 sign changes out of 1,604,180 retained vertices. In particular
this modularly compatible construction cannot be repaired by changing a
bounded number of signs as t increases. The statement permits arbitrary
new signs and words on that support; it assumes no repetition in the
candidate exact pair. It makes no claim about moving either hole.

Here is a finite symbolic calculation proving the norm for every scale,
rather than extrapolating from samples. Write t=2P+1. Each old sign is
an interval of length one. Each inserted edge has intervals

    [e*t+1, e*t+P] with sign +1,
    [e*t+P+1, (e+1)*t-1] with sign -1.

For a signed interval [l,r] on arm a, its no-hole physical shell columns
sum to constant coefficient intervals [l+1,r+1] with sign s,
[n_a*t+1-r,n_a*t+1-l] with sign -s, and
[n_b*t+l+1,n_b*t+r+1] with sign -s for each other arm b.
For each hole, the distance image is an interval [u,v]; add coefficient
-s on [u,v] and +s on [u+1,v+1]. Distances to a same-arm hole have a
constant slope on the interval because holes are old endpoints; an old
hole itself has no sign. The centre is handled by its four no-hole
monomials and four hole monomials, with centre sign -1.

Represent an interval by a positive coefficient jump at its left endpoint
and the negative jump at one past its right endpoint. Every jump exponent
is affine aP+b. `growing_lift_shell_events` compiles these rules into 745
nonzero affine jumps. Sort by (2a+b,a). For each adjacent pair, the checker
verifies that their exponent difference AP+B has A>=0 and 2A+B>=0.
This proves that this order holds for every integer P>=2, including ties
at P=2. Between jumps the shell coefficient is the cumulative jump sum.
Multiplying the absolute value of that sum by the affine interval length
and summing gives exactly 1000P+244. The final cumulative sum is zero.
P=1 is checked separately by coincident-event aggregation and gives 1244,
the same formula. Thus the norm identity holds at every odd t>=3.

Finally, every retained physical vertex column has norm at most eight:
four no-hole monomials and two monomials per hole. Collisions only lower
this bound. Flipping h signs therefore changes K by norm at most 16h,
by the triangle inequality. A balanced exact homometric pair has K=0
(the signed shell identity is K=2(1-z)Delta), proving the stated Hamming
bound. This also explains why equality of modular profiles and a defect
of only one at distance one do not mean that the full error is small.

Replay from the repository root, without constructing the large tree:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --lift-repair-bound 7981 --write /tmp/lift-repair.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/lift-repair.json
```

The recorded output has shell_l1=3990244 and minimum_sign_changes=249391.
All 52 focused tests pass (28.127 seconds). New controls reconstruct all
shell coefficients from physical vertex columns at t=3,5,7,11,101 and
independently from unordered pair distances at t=3,5; check the column
norm bound at every retained vertex in those five trees; and reject
altered saved bounds. A scale exceeding 10^80 is checked symbolically.
The main resistant-family acceptance remains unmet.

### Flat interiors fail even with arbitrary finite endpoint patches

Sorrel, continuation. The earlier unpatched flat-piece refusal can be
strengthened without a sign search or a larger patch census.

**Scoped theorem.** Let p>=2,w>=0,L>=179+2w and t=pL+1. In each old
edge, divide the t-1 inserted vertices into p successive pieces of L
vertices. Allow arbitrary independent signs on all retained old vertices
and on the first and last w vertices of each piece. Require only that
each remaining piece interior is constant, with its own independent sign.
No such signing gives balanced homometric sets. This holds with the named
holes 19t and 99t; in fact it holds for any choice of holes among the old
vertices. It excludes neither holes inside inserted pieces nor nonconstant
interiors such as the surviving period-two attempt.

**Proof.** Compile (1-z)K with affine exponents qL+c as above. Every offset
lies in [1-w,179+w]. Thus L>=179+2w makes specialization injective on
these formal exponents. A true zero therefore makes every formal row zero.
Retain the rows with q divisible by p, divide q by p, then sum all offsets
c. Any individual old or patch column cancels, because multiplying a
monomial by 1-z gives opposite coefficients with the same slope q.
Every hole correction also cancels in this sum: its two terms differ by
one in c. This is independent of the old hole's position. Constant
interiors have only their two geometric endpoints. Among pieces r=0..p-1,
only the first and last endpoints can have slope divisible by p.

Write f_(a,e),l_(a,e) for those first and last interior signs, on old edge
e=0..n_a-1, where (n_1,n_2,n_3)=(99,79,23). Their necessary aggregate
columns, now polynomials in a formal Y, are explicitly

    f_(a,e): Y^e + Y^(n_a-e) - sum_(b!=a) Y^(e+n_b),
    l_(a,e): -Y^(e+1) - Y^(n_a-e-1) + sum_(b!=a) Y^(e+n_b+1).

No old sign, patch sign, hole choice, p, w or L remains. These formulas
also provide an independent construction of `split_bulk_system`, rather
than relying on extraction from the full compiler.

Sum the necessary coefficient equations at slopes q with q mod 8 in
{4,5,6,7}. This fixed square wave selects 88 of the 179 rows. The resulting
integer equation has exactly 24 coefficients +2 and 25 coefficients -2;
all other coefficients vanish. These counts follow just by evaluating the
two displayed columns at the square-wave indicator for e=0..n_a-1, a
finite integer calculation retained in `split_bulk_refusal`. For a direct hand calculation, let f(q) be one when q mod 8 is in
{4,5,6,7} and zero otherwise. The selected coefficient of a first sign is
f(e)+f(n_a-e)-sum_(b!=a)f(e+n_b); for a last sign it is
-f(e+1)-f(n_a-e-1)+sum_(b!=a)f(e+n_b+1). Both coefficients vanish
identically on arms two and three. On arm one, the first coefficient is
-2 for e=0 mod 8, +2 for e=4 mod 8 and zero otherwise; the last is
-2 for e=3 mod 8, +2 for e=7 mod 8 and zero otherwise. Among e=0..98
these give 13+12 negative and 12+12 positive terms. Dividing by
two gives a sum of 49 signed odd integers equal to zero, which is
impossible. Equivalently the selected binary rows XOR to 0=1. The
portable verifier rebuilds the independent columns and checks that XOR;
it uses no search, rank estimate, sampled scale or time limit.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --split-bulk --write /tmp/flat-bulk.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/flat-bulk.json
```

For the named two holes this rules out *every fixed finite patch width*
on sufficiently long flat pieces, strengthening the earlier width-zero
and width-one results. It also tells a builder exactly why merely making
such patches wider cannot produce an infinite flat-interior family.
The period-two repeating interiors have zero-mean possibilities and are
not covered by this argument. The task's unrestricted acceptance remains
unmet; no new all-pairs upper bound is asserted.

### Moving the two holes cannot rescue two flat halves

The bulk obstruction also yields a deliberately conservative bound covering
**any two physical holes**, including holes inside a piece or at the centre.
It remains a theorem about flat interiors, not arbitrary third words.

Let p>=2,w>=0,L>=2w+1,t=pL+1, with the same aligned pieces as above.
If

    L >= 804p + 3216pw + 1007,

no balanced homometric signing can be constant on the piece interiors,
even with arbitrary old signs, arbitrary endpoint patches of width w,
and arbitrary positions of the two holes. In particular p=2,w=0 requires
only L>=2615. Every resistant t=7980m+1 has L=3990m, so **two flat
halves per old edge fail for every resistant scale and every two-hole
support**. This strengthens the aligned-hole theorem in a different
direction; it is not the unrestricted all-pairs acceptance result.

To prove the bound, extend a proposed signing to a baseline full-support
signing: keep arbitrary signs at every old vertex, make each entire piece
constant with its interior sign, and assign a sign to any old hole. The
full-support no-hole polynomial K_0 has derivative (1-z)K_0 with offsets
in [1,179]. The independent bulk columns and square-wave contradiction
above apply unchanged, since all individual old columns and hole columns
had cancelled in the aggregate.

Consequently at least one slope cluster has a nonzero total jump. If all
cumulative jumps between clusters were zero, every cluster total would
be zero, contradicting the bulk certificate. Thus K_0 is nonzero on a
whole interval between consecutive slope clusters. That interval contains
at least L-178 coefficient positions: a cluster's largest possible
exponent is qL+179 and the next cluster's smallest possible exponent is
(q+1)L+1. This argument requires L>178, which the stated threshold ensures.

Now count how many coefficient positions can change. The baseline source
signs consist of 201p constant intervals and 202 individual old vertices.
For one arbitrary hole h its correction to K is

    -(1-z) sum_v s_0(v) z^dist(v,h).

The distance map is affine with slope +1 or -1 on each interval, except
that at most one interval must split at a same-arm hole. The image sum
of each resulting constant interval is geometric; multiplication by
1-z leaves at most two coefficient positions. Each old point also gives
at most two. Thus this correction has support size at most
2(201p+202+1)=402p+406, independently of the hole's location. For two
holes the union has size at most 804p+812. Overlaps and cancellations
can only reduce it.

The actual source differs from the baseline at at most 402pw endpoint
patch vertices and two holes. In the shell operator with those holes,
each changed source vertex affects at most eight coefficient positions:
four no-hole terms plus two terms per hole. Hence these source changes
add at most 8(402pw+2) positions. Altogether K-K_0 is supported at at
most

    804p + 3216pw + 828

positions. It cannot cancel a nonzero interval of length L-178 exceeding
that number. A balanced homometric pair requires K=0, giving the bound.
This proof counts support, not coefficient magnitudes, so it permits
arbitrary signs and accidental collisions at the moving holes.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --flat-any-holes 3990 --write /tmp/flat-any-holes.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/flat-any-holes.json
```

Recorded output: t=7981, unavoidable nonzero support at least 3812,
possible correction support at most 2436, status flat_ansatz_refused.
At or below the threshold the checker returns not_decided_by_bound,
never an exhaustive search conclusion. It also accepts enormous integer
scales without expanding the tree. New finite controls independently
compare the support-count decomposition with physical columns, including
an interior hole and a missing centre, and check both sides of the exact
strict-inequality threshold. Saved altered bounds are rejected.


The same hand calculation gives a structural extension: replace the old
arm lengths by A=8u+3, B=8v+7, C=8r+7, for nonnegative integers u,v,r,
in any arm order. The other two arms still vanish, and the distinguished
arm contributes 4u+1 nonzero coefficients, all +/-2. Thus the same
flat-interior obstruction holds. Put N=A+B+C and
M=max(A+B,A+C,B+C). The aligned-old-hole threshold becomes L>=M+1+2w;
the support-count argument for any two holes becomes

    L >= M + 4Np + 16Npw + 4N + 25.

Indeed there are Np intervals, N+1 old points, and at most one split per
hole; the unavoidable plateau has length L-M. These are scoped theorems
about the same aligned constant interiors. The command-line checker in
this contribution deliberately reports only the original (99,79,23)
case. This extension asserts no unrestricted homometric upper bound.

### The nonconstant sign fibre remains unresolved

The same building stretch pursued the surviving p=2, word-period-two,
patch-width-four system. Joint closure again retained 2,682 signs, rational
nullity 132 and 133 binary free coordinates; it completed in 435.379
seconds. A separately recovered rational kernel and a second representation
inferred from the retained recovery rows were both checked against the
untouched formal equations. No numerical rank assumption was used.

A temporary numerical local search chose 132 original coordinates as signs
and penalized each recovered coordinate by (abs(value)-1)^2. A floating
change of basis reduced its largest recovery coefficient from roughly
70,000 to 1.287. Its final observed report, at 630 seconds, had visited
31,930,344 sign flips over 639 restarts without finding a zero penalty;
the attempt was then stopped. Those figures describe a heuristic attempt,
not an exact minimum, an exhaustive refusal or evidence against other
words. A numerical candidate would still have had to pass the untouched
integer shell equations. No such candidate was produced.

All 56 permanent focused tests pass (28.470 seconds). The temporary discovery
programs add no dependency to the standard-library checker. The remaining
obstacle is still a literal exact-shell signing of an infinite resistant
family, or an obstruction allowing arbitrary nonconstant words and every
permitted hole support. Wider flat patches and relocating the holes within
the flat ansatz are now excluded under the stated bounds; that does not
close the nonlinear periodic fibre or the main task.

A separate discovery attempt used the already installed constraint solver on
2,682 Boolean signs, 2,558 distinct untouched integer shell rows after the
verified signed quotient, and 2,549 necessary binary echelon rows. It fixed
the retained centre positive to remove global complementation. With two
workers and a 1,050-second solve limit it returned **UNKNOWN**, after
1,051.790 seconds overall, 18,680 branches and 258 conflicts. It produced
neither a witness nor an exhaustive refusal. The solver was used only for
temporary discovery; no solver dependency or solver status is accepted by
the portable checker as a mathematical certificate. Neither this timeout
nor the numerical search decides the surviving fibre. No further increase
of their budgets is proposed here.
