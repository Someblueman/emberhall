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

### Shifted holes and an endpoint refusal for every piece count

Fern, 24 November 2026. The split-edge compiler now allows the shallow
hole to be `1:(ht+delta)` instead of requiring it to be an old vertex.
The other hole remains `1:99t`. Require integer `|delta|<=w`, where w is
the independent patch width at each end of each piece. Every old sign is
free except an old vertex that actually is a hole; a shifted hole removes
its own patch sign instead. This is a larger construction ansatz, **not
an unrestricted all-pairs reduction**.

Here t=pL+1, p>=2, the independent interior word length q divides L and
2w, and L>=2w+q. The formulas above still compile `(1-z^q)K` exactly.
An interval's distance to the shifted hole has one slope: all non-singleton
intervals lie beyond its endpoint patch. The compiler proves this ordering
for every L>=2w+q by checking that the affine distance difference AL+B
has A>=0 and A(2w+q)+B>0. It omits the hole before forming its column.
The direct tests also establish that the coordinate groups partition all
201t-1 retained physical vertices, with no duplicate or missing vertex.

**Uniform endpoint obstruction.** For h=19, q=2, w=4 and either
`delta=-2` or `delta=2`, no such signing exists for **any** p>=2 and any
even L>=190. In particular this excludes the ansatz at every resistant
scale t=7980m+1 for which p divides 7980m and L=7980m/p is even and
at least 190. It excludes neither larger patches nor other supports.

Here is why a single finite certificate covers all piece counts. Retain
only formal rows whose coefficient of L is divisible by p, and divide
that coefficient by p. An interior piece with index r=0,...,p-1 has forward
endpoint slopes congruent to r and r+1 modulo p; reflected endpoints
have slopes -r and -r-1. Single patch signs have the corresponding one
endpoint slope. Thus only the first piece's outer patch and first word
endpoint, and the last piece's outer patch and last word endpoint, can
enter a retained row. Old vertices and both holes have slope divisible
by p, including the fixed offset delta. Relabel these two pieces as
first/last. Their entire retained row system is exactly the p=2 system,
including constants and coefficients; the middle pieces contribute nothing.
No assumption about their independent words has been added.

For the two shifts the necessary binary rows have a verified contradiction:
substituting s_i=2b_i-1 and summing the named rows gives 0=1 modulo two.
To pass from formal coefficients to physical shells, collect the raw
constant exponents *before cancellation*. Their set is independent of p
by the column formulas above, and its span is 189. For L>=190, distinct
integer pairs (A,B) cannot specialize to the same exponent AL+B: a nonzero
slope difference has magnitude at least L, larger than every constant
difference. Physical K=0 therefore forces every formal coefficient of
`(1-z^q)K` to vanish. Its endpoint subsystem contradicts the certificate.
The threshold is rounded upward to a multiple of q by the portable checker;
tampering with it is rejected.

Replay either sign of the shift using standard-library Python:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --split-endpoints --edge-patch 4 --piece-period 2 --hole-offset -2 --write /tmp/shifted-endpoints.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/shifted-endpoints.json
```

The negative-shift run has 2,494 endpoint rows on 4,220 coordinate slots,
with raw constant span 189 and minimum even L=190. The positive-shift
run has the same threshold. Tests compare the whole normalized endpoint
system at p=2,3,7 for four word/patch/hole configurations, including odd
shifts and q not dividing w, and compare the raw constant sets. Independent
physical-column controls cover eight shifted-hole configurations at two
scales each, including both patch extremes and h=1,98. Invalid offsets,
empty refusals, incorrect specialization thresholds and unknown saved
results are rejected.

This refusal does not persist under arbitrary patch enlargement: q=2,
w=8, delta=-2 is binary compatible (104 free binary coordinates before
joint-field reductions). A full exact search of that case is recorded below; compatibility alone
is no witness. The main task's
infinite-family acceptance and the arbitrary-triple milestone remain open.

### Holes at internal piece boundaries; exact small-fibre exhaustion

The compiler also accepts `--hole-piece r`, 0<=r<p. Its shallow hole is
`1:(ht+rL+delta)`. This genuinely adds supports inside a subdivided old
edge. At r>0 require w>=1 and 1-w<=delta<=w: the previous piece ends at
ht+rL, so its last w vertices start at ht+rL-w+1. This differs by one
from the patch next to an old singleton. A direct-column test caught the
invalid delta=-w case; it is now rejected rather than silently grouping a
hole with retained interior vertices. The old-boundary convention at r=0
remains -w<=delta<=w. The uniform-p endpoint theorem above concerns r=0;
internal holes do not have its divisible-by-p slope and are not covered.

For h=19, r=1, p=2, q=2, w=2, delta=0, the necessary binary system has
exactly ten free coordinates. Enumerating all 1,024 assignments and checking
every recovered signing against the original integer rows leaves zero
solutions. The portable refusal therefore excludes this ansatz at every
even L>=186, including the resistant scales with L=3990m. It is another
scoped obstruction, not an all-pairs obstruction. The raw constant span is
185; the injective-specialization requirement is essential for a negative
formal result. Positive formal zeroes still specialize at the smaller
geometric threshold L>=2w+q.

`enumerate_binary_fibre` recovers pivot bits in increasing pivot order:
each pivot is the greatest index in its echelon equation, so only already
recovered pivots and chosen free bits occur on its right. This enumerates
the whole necessary binary fibre exactly once. Literal signs are then
checked in every untouched integer equation. Search uses this route for
at most 16 free coordinates before expensive rational reduction. A time
limit produces **unknown**, never a refusal. Verification rebuilds the
system and repeats the full enumeration; it rejects changed counts or
specialization thresholds.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --split-edge --edge-pieces 2 --piece-period 2 --edge-patch 2 --hole-piece 1 --write /tmp/internal-hole.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/internal-hole.json
```

The exact run takes about half a second on this room, compared with the
previous joint-field refusal in 108.560 seconds. It has 2,612 sign slots
and 2,850 integer rows. Exhaustion is also compared with full literal
enumeration on 72 random small integer systems and 72 separate systems
with planted solutions. The original random seed produced no positive cases;
the planted controls close that verification gap. Direct
physical-column and complete-support tests now include four internal-hole
configurations at two scales each; they retain the original shifted-hole
and uniform-endpoint controls. The main task's acceptance remains unmet.

The wider shifted-hole attempt also produced no construction. The q=2,
w=8, delta=-2, p=2, h=19 run reported
`ansatz_refused_by_joint_fields` after 1,554.373 seconds, before branching.
Its first joint round reduced 7,436 signs to 2,020, with rational nullity
100, binary free dimension 100, ternary nullity 18 and 2,244 ternary signed
relations. A later reduction found a conflict. This is the exact-field
solver's diagnostic refusal, **not a standalone portable refusal file**;
`--verify` intentionally does not accept this status. Do not confuse it
with either independently replayable certificate above. Any physical
negative claim for this formal ansatz also requires even L>=198 (raw
constant span 197), rather than just its geometric minimum L=18.

Replay the computation, allowing the full reduction budget:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --split-edge --edge-pieces 2 --piece-period 2 --edge-patch 8 --hole-offset -2 --seconds 1800 --nodes 10000000 --write /tmp/wide-shifted-hole.json
```

The final retained implementation passed all 53 focused tests (36.252s);
the strengthened positive/negative fibre control also passed separately
(1.616s). No large solver output is committed. The remaining obstacle is
still an exact construction with freer signs/supports, or a genuinely
unrestricted obstruction. Neither the scoped refusals nor their enlarged
compiler decide all pairs on the resistant family, so the main task stays
open and priority stays provisional.

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

A final physical-column audit checks the generalized aggregate on fresh
old triples (3,7,15), (11,15,23), (19,7,31), at (p,w)=(2,0),(3,1),
with old holes on arms two and three. All 655 complete piece columns
agree with the displayed first/last formulas; all middle pieces cancel.
Here L=M+4. The temporary audit initially decoded affine exponents with
an origin of one, incorrectly assigning a valid c=0 patch endpoint to
the preceding slope. Using q=floor((exponent-(1-w))/L) corrects that
auditor error and covers c in [1-w,179+w] (or [1-w,M+1+w] generally).
The project compiler was unchanged. These controls support the endpoint
conventions; the finite controls alone are not the generalized proof.

## Mica: an all-word moving-hole strip and the next dyadic layer

24 November 2026. **The task acceptance and global milestone remain unmet.**
Priority remains provisional. Commit `0f2b68e` reconciles Fern's inspected
`f2c5c2a` changes with Sorrel's later flat-interior work. The trusted integration
attempt reported a conflict; this private reconciliation is not publication.
The combined predecessor suite passed all 60 tests before the additions below.

### Radius one for moving holes, with endpoints stated explicitly

Fix h in 1..98, odd t=2L+1>=9, and holes (1,ht),(1,99t). No word is fixed.
After cancelling the long-tip hole against its endpoint term, the physical
shell columns are, writing d for depth and j for the other short arm:

    C_1(d) = z^(d+1) - z^(79t+d+1) - z^(23t+d+1) - z^(99t-d)
             + (z-1) z^|d-ht|,
    C_i(d) = z^(d+1) - z^(n_i*t+1-d) - z^(n_j*t+d+1) - z^(99t+d)
             + (z-1) z^(ht+d),                 i=2,3,
    C_0    = z - z^(79t+1) - z^(23t+1) - z^(99t) + (z-1)z^(ht).

These follow directly from the original physical column formula; in particular
the cancelled term on arms two and three must not be retained a second time.
An initial temporary compiler did retain it. The independent matrix comparison
caught that error before any result from the compiler was accepted.

Every nongrid depth is uniquely q*t+s*r, s=+/-1, 1<=r<=L. There are 402
signs per folded level, and 200 retained old-grid signs including the centre.
An interior column term is z^(Q*t+u*r+c), where u=+/-1 and c is zero or one.
Thus a row at Q*t+u*r uses source level r-u*c: its radius is exactly one.
`moving_folded_stencils` retains these integer equations without prescribing
any of the 402 signs, including every third-arm sign.

The exact partition of shell rows is: left levels 0 and 1; interior centres
2..L-1; right level L. The left rows see old-grid signs and levels 1,2.
The right rows see levels L-1,L. At the odd midpoint use exactly

    Q*t+L+1 = (Q+1)*t-L,    Q*t-L-1 = (Q-1)*t+L.

Consequently an unrestricted signing on this **named support** is equivalent
to a path in a fixed graph on two consecutive 402-sign levels. Initial states
admit some assignment to the 200 old-grid signs satisfying the left rows;
terminal states satisfy the right rows. Starting with levels 1,2, append levels
3..L: there are **L-2 edges**, checking centres 2..L-1. The state bound is
2^804. This graph has not been enumerated or its accepted lengths decided.
This statement concerns moving holes ht,99t; it does not replace the earlier
fixed-depth-hole strip or cover other hole supports.

The new periodic-interior compiler keeps levels 1..w and L-w..L independent,
with w>=2, and keeps all old-grid signs. For L>=2w+4+p, interface centres 2..w+1 and L-w-1..L-1 are retained literally;
one complete period of centres w+2..w+p+1 covers all remaining rows. Its
integer equations are unchanged when L increases by p. An exact positive
signing would therefore prove an infinite half-length phase. A parity refusal
excludes only this periodic ansatz. Unlike the earlier split-piece compiler,
it does not require p to divide L. The explored p=4, L=3990 phase intersects
the resistant family at every odd m. No such positive signing is reported.

A standard-library command checks the **entire matrix**, not a random signing:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --moving-strip-audit 17
```

Recorded result: 3,416 physical columns and 3,026 shell rows match, radius one,
804 stored slice signs, six path edges. Additional tests check complete matrices
at t=9,11,15, arbitrary integer sign coordinates at five scales, and direct
unordered-pair distance counts of a balanced signing. Four periodic compiler
controls compare every physical column and verify whole-period extension.
A deliberately changed sign and damaged certificates are rejected by the
witness/refusal checks; planted positive checker controls are explicitly
synthetic and are not tripod witnesses.

### Exact mod-eight equations on the complete binary fibre

Parameterize all necessary mod-four shell solutions by free original binary
coordinates x. Write s_i=sigma_i*product_(j in M_i)(1-2x_j), sigma_i=+/-1.
For an integer shell row R=sum c_i*s_i, its constant term C is divisible by
four and A_j=sum_(i:j in M_i)c_i*sigma_i is even. Expanding modulo eight gives

    R/4 = C/4 + sum_j (A_j/2)*x_j
          + sum_(j<k) sum_(i:j,k in M_i)c_i*sigma_i*x_j*x_k   (mod 2).

The sign of the linear term disappears modulo two; terms of degree three or
more vanish. `binary_shell_quadratics` checks the whole affine fibre against
every input parity row before constructing these exact quadratic equations.
XOR elimination temporarily treats pair products as independent coordinates.
Each resulting linear consequence carries a replayable XOR trace of original
quadratic rows. Compatibility of that relaxation is not a quadratic solution
or a literal signing. Small exhaustive controls verify the displayed identity
on **every** free binary choice and independently verify fibre completeness.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --split-dyadic --edge-patch 4 --piece-period 2 --seconds 120 --write /tmp/split-dyadic.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/split-dyadic.json
```

Recorded result: 138 free binary coordinates, 9,453 pair-product coordinates,
quadratic rank 2,547 and three independent necessary linear relations, with
no contradiction. Applying those relations and repeating the calculation
leaves 135 binary coordinates and rank 2,544, with no further linear relation.
Separately the existing joint-field quotient has 2,682 signs and 133 binary
coordinates; its mod-eight equations have rank 2,550 and one new linear
relation. Repeating after that relation leaves 132 coordinates and rank 2,549,
with no further linear relation. These are necessary reductions only.

### Forced tails reduce the all-word graph to 580 stored signs

For 1<=h<=42 the same moving-hole strip has a smaller exact representation.
In every shell row e>122t, the displayed columns contribute only

    -x_(e-79t-1) - y_(e-99t).

Indeed all third-arm and short-endpoint exponents are at most 122t, and the
shallow-hole terms are at most (h+79)t+1<=122t. Thus for every full literal
solution, without a word restriction,

    x_(d+20t-1) = -y_d,          23t+1<=d<=79t.

There are 56t pairs. Eliminate first-arm depths 43t..99t-1, keeping depths
1..43t-1 except ht, and both other arms. A second-arm source in that tail
now has column C_2(d)-C_1(d+20t-1). Its affine constants are still only
-1,0,1. The reduced strip therefore retains radius one, the same row
partition, and the same **L-2** edge convention. It has 290 signs per level,
144 retained old-grid coordinates and a graph-state bound **2^580**.
Balance concerns the restored full signing; the reduced coordinates alone
must not be required to have zero sum. This reduction is asserted only for
h<=42; it is not extended to h=43 or arbitrary holes.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --moving-strip-audit 17 --moving-reduced
```

Recorded result: all 3,416 original retained columns are accounted for in
2,464 reduced source columns; 2,074 shell rows match, with 290 signs per
slice and 580 stored signs. Tests independently inspect every high-distance
row at (t,h)=(9,1),(11,19),(15,42), verify the complete reduced matrices,
and expand arbitrary reduced signs back into every original physical shell.
This is an exact all-word reduction on the named supports, **not** an accepted
path, an infinite construction, or an all-pairs obstruction.

### Recorded failures and independent reconciliation checks

For the new period-four interior with w=2, h=19 and L=3990, compilation has
3,818 signs and 4,094 nonzero rows. Its raw binary system has 93 free
coordinates. Joint exact reduction completes with 2,392 signs, rational and
ternary nullity 86, and 86 binary free coordinates (335.559 seconds observed).
The following 600-second exact sign search ends **unknown**, after 55,251
nodes; total observed elapsed time was 936.177 seconds. The untouched original
rows are still required for a positive result. The shipped command counts its
budget across both reduction and search, so allow both stages when replaying:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --moving-folded --period 4 --folded-patch 2 --seconds 1000 --nodes 10000000 --write /tmp/moving-folded.json
```

The same quotient's mod-eight product relaxation has rank 2,306 and no new
linear relation. Its separate ternary sign-square lift completes: 86 free
signs, 3,656 product coordinates, 2,306 rows, rank 2,306, nullity 1,350, original
kernel checks passed, no forced-zero coordinate and no signed-copy relation.
The observed elapsed time is 546.441 seconds. Equality of the two ranks is
an observation, not an assumption or a sign solution.

A temporary exact-parity-fibre energy search on the earlier two-piece,
period-two, width-four system used the exact integer objective sum R^2.
Every reported improvement was checked against untouched integer rows.
After 900.172 seconds, 368 accepted flips and 143 restarts, its best objective
was 29,728, not zero. A binary change of basis did not make its dense sign
influences local. The temporary numerical search is discovery only, adds no
runtime dependency and supplies no lower bound, witness or refusal.

For Fern's internal-hole contribution I independently used **lowest** pivots,
then recovered them in descending order, rather than calling the supplied
highest-pivot fibre enumerator. All 1,024 assignments of its ten free bits
were tested against untouched integer rows: zero literal solutions. Independent
XOR replay of each shifted endpoint trace (offset -2 and +2) gives 0=1;
both systems have 2,494 rows, raw constant span 189, and minimum even L=190.
These checks support exactly the scoped claims retained in the reconciliation.

All **68 focused tests pass** (51.227 seconds observed), including complete
matrix reconstruction, direct distance multiplicities, whole-period extension,
small exhaustive dyadic identities, CLI round trips and damaged certificates.
No larger test suite was repeated. The precise remaining obstacle is a literal
accepted strip path in a resistant half-length phase, or a rigorous obstruction
allowing every word and every permitted two-hole support. Neither the product
relaxations, the smaller graph, the failed searches nor this reconciliation
constitutes the task's infinite-family acceptance or the milestone audit.

The second moving-folded attempt used h=1 with the same L=3990, p=4 and w=2.
Joint reduction retained 2,428 signs and 86 rational, binary and ternary free
coordinates. The shipped 600-second whole-run command ended **unknown** after
28,241 nodes and 600.515 seconds; no literal signing was produced. Both this
phase and the h=19 phase still require a new exact construction or obstruction,
not a claim inferred from the exhausted time budgets.

### Rook: simultaneous local shell hulls

**Preserved pairing reconciled (Tern, 25 November).** The older recovery task
`preserve-paired-spectrum-hulls` names run `bf68757ba40e4fd2bb803a8c3e355868`
and `paired_shell_rows`. Canonical source inspection fails at that room's
`git rev-parse HEAD`; its cited commit `881f6c3` is absent here, and lesson
`fern-paired-shell-hulls-20261124` has no attached artifacts. This is not a
recovery or independent verification of those missing files or their large
diagnostics.

The useful mathematical method is already covered by the accepted simultaneous
blocks below. For integer residuals R and S on signs, let
B=1+sum(abs(c) for c in coefficients(S)). Then abs(S)<B, so B*R+S=0
holds exactly when R=S=0: a nonzero integer R has abs(B*R)>=B.
Enumerating a two-row block therefore enumerates precisely the solutions of
the encoded row, without introducing its larger coefficients. The statement
concerns the same local parameterization; bounded searches may inspect different
blocks or stop early and need not report the same rank.

I independently enumerated all 64 sign assignments for the lesson's rows
`(2,-2,-2,-1,-1,2)` and `(-1,2,-2,-2,-1,2)`. With B=11, their conjunction
and the encoded row have the identical four solutions. Current
`affine_shell_closure` returns rank 3 separately and rank 4 both with
`blocks=[(0,1)]` and with the encoded row appended. Every returned equation
holds on all four solutions. Existing exhaustive joint-block controls below
also cover infeasible systems and rank-limit skips. Thus no restoration of
the missing helper is needed to retain this method; its old large-run counts
remain historical reports, not newly checked evidence. The infinite-family
acceptance remains unmet.

The infinite-family acceptance remains unmet. `affine_shell_closure` now accepts
explicit blocks of row indices. It expresses every sign in the same original
binary parameters, enumerates assignments satisfying **all** rows of a block,
and adds only equations of their affine hull. This preserves every literal
solution. A block above the chosen rank bound is skipped, never declared
inconsistent. A compatible hull is still only a necessary condition.

This retains correlations that separate row hulls lose. For example,
`a+b+c+d=0` and `a+b-c-d=0` separately give just the same four-bit parity;
together they force `a=-b` and `c=-d`. Exhaustive controls compare complete
blocks with every literal assignment on 61 small systems, including empty
solution sets, and check every returned binary equation on every solution.

The deterministic folded diagnostic pairs each row with its two neighbors
sharing the most literal coordinates, breaking ties by row index and removing
duplicate pairs. It does not inspect every row pair. Reproduce it with:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --folded-hulls --period 4 --seconds 600
```

For h=19, L=3990, p=4 and w=2 there are 3,818 signs, 4,094 rows and 7,047
selected pairs. Single-row closure leaves 93 binary parameters. Pair closure
at local rank twelve leaves the same 93 (2,860 skipped blocks; 3.67 seconds
observed). Raising the bound to sixteen still leaves 93 (561 skipped blocks;
65.83 seconds). Neither run finds a contradiction or a literal signing.
The fixed-point flag concerns the inspected hulls, including the reported
skips; it does not certify closure under larger blocks or all row pairs.

`--joint-fields` applies the existing exact rational/binary/ternary reduction
before selecting pairs. Its time budget includes that reduction, compilation
and block selection. The diagnostic deliberately reports `all_pairs_decided`
as false and saves only a compact summary, not a new claimed certificate.

The joint-field run completes in 419.00 seconds observed. The existing
reduction retains 2,392 signs, 6,963 rows and 86 binary parameters. Its
13,202 selected pairs add no affine relation: the final binary rank is
2,306. There are 14,089 skipped **blocks** (single rows and selected pairs
together) above rank sixteen; 5,691 distinct local systems were enumerated.
The hull stage alone takes 58.27 seconds. Replay with:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --folded-hulls --period 4 --joint-fields --seconds 1200
```

All 69 focused tests pass (39.71 seconds observed); the period-one diagnostic
also reproduces its existing initial-parity conflict without claiming an
all-support result. The remaining obstacle is nonlinear compatibility of
the 86 parameters, or an unrestricted argument for all permitted supports.
These inspected affine hulls supply neither. Further repetition of the same
rank-limited pair check cannot advance this fixed point; a larger or more
structured joint constraint, an actual literal solution, or a new invariant
is needed. The ready task and its acceptance are left open.

### Hawthorn: retain nonlinear local relations instead of their affine hulls

The task's infinite-family acceptance remains **unmet**. The previous paired
hull fixed point does not mean that exact local relations carry no further
information. `relational_shell_consistency` keeps every valid local assignment,
then semijoins selected pairs on their entire shared binary linear-form space.
It does not replace a relation by its affine hull.

Here is the soundness argument. Write each original sign as
`(-1)^(a_i.x+b_i)` using the original shell parity equations. For each row,
choose independent generators for the span of its `a_i`, and enumerate exactly
those generator assignments for which the **integer**, rather than modular,
row sum vanishes. Every full literal solution projects into this relation.
For two rows, tagged binary elimination computes a basis of the intersection
of their generator spans: each returned pair of coefficient words denotes
exactly the same linear form in the two coordinate systems. An assignment
whose intersection projection occurs nowhere in the other relation cannot
extend to a full solution. Deleting it is therefore sound, including after
previous deletions. An empty relation or empty intersection projection refuses
this compiled system; nonempty pairwise-consistent relations need not have
any simultaneous global assignment. Skipping an oversized row only weakens
the relaxation, and budget expiry returns incomplete, never refusal.

This is genuinely stronger than the existing separate-row affine closure on
a small nine-sign control included in the tests: the latter is compatible,
but exact relational propagation detects an empty overlap. Exhaustive tests
inspect every literal assignment of that control and sixty small integer-row
systems; every genuine solution survives every retained relation. Another
sixty independently generated pairs of binary spans verify that the tagged
intersection is the entire shared space, by enumerating both spans directly.

The resistant quotient uses the same deterministic 7,047 selected neighbor
pairs as the preceding hull diagnostic, not all row pairs. Replay:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --folded-relations --period 4 --hull-rank 12 --seconds 30
```

At h=19, L=3990, p=4, w=2, all 4,094 row relations fit rank twelve: **no row
is skipped**. The first semijoin sweep deletes 246 local assignments; the next
deletes zero. There are 546,304 surviving local assignments in total, not
546,304 full solutions. The observed whole diagnostic takes 2.86 seconds.
Taking the affine hull of each resulting relation in a separate diagnostic
still gives binary rank 3,725 on the original 3,818 signs, hence 93 free
parameters. The deletions are information that this affine projection loses.
No contradiction or literal signing follows from that fact.

`make_relational_engine` can retain these exact relations during the existing
untouched-row search. Each generator gets an auxiliary bit linked by an exact
binary equation to the original free coordinates. The convention matters:
the local generator is parity of **negative** sign bits, while the search
engine represents a positive sign by bit one. Thus for generator mask g,
`aux XOR parity(positive & g) = popcount(g) mod 2`. Tests fix every original
sign assignment of three small systems and check both generator parity offsets,
also checking the rank-zero skipped-row fallback against the original rows.
An explicit original-sign seed uses global reversal without assuming that
all auxiliary bits reverse. Any returned signing is restored (including
joint-field aliases when requested) and checked against untouched input rows.
Replay a bounded search with:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --folded-relations --relation-search --period 4 --hull-rank 12 --seconds 600 --nodes 1000000
```

This is a finite ansatz search, not an unrestricted all-support decision.
The relations remain usable without the search and add no dependency.

A direct helper run, after compiling the relations, gave the search 600
seconds and one million nodes. It returned **unknown** after 8,377 nodes;
engine construction plus search took 600.68 seconds. It added 11,570 auxiliary
bits to the 3,818 original signs. The CLI above charges preparation against
its single time budget, so its node count need not match this helper run.
This is no speedup claim: the auxiliary state has substantial overhead.
All 72 focused tests pass (61.05 seconds observed while the bounded search
also ran), and `git diff --check` is clean. The remaining obstacle is global
compatibility of the surviving nonlinear relations, or an unrestricted
argument across every permitted support. No infinite family has been decided.

### Tern: Boolean cubic consequences on the complete parity fibre

24 November 2026. **Infinite-family acceptance remains unmet.** I advanced
this private room to the already accepted `44db365` before extending the
three owned files. The new method retains Boolean product compatibility
that the independent-product relaxation discards; it does not decide every
hole placement or remove the periodic-word restriction.

For clarity about scope, `compile_moving_folded` uses t=2L+1, holes 19t and
99t, independent end patches of width two and a periodic folded interior.
I checked its row partition directly: left rows cover folded levels zero
and one, interior rows cover 2..L-1, and right rows cover L. The compiler
keeps the two patch interfaces separately and one full period of wholly
periodic rows. Increasing L by whole periods preserves the literal system.
Thus L=3990, p=4 represents resistant indices m odd, since L=3990m;
it does not automatically represent the other half-length phase.

The existing checked mod-eight identity gives quadratic zero-polynomials
q(x) in free original negative-sign bits. `boolean_cubic_lift` adds every
x_j*q(x), reducing x_j squared to x_j, then eliminates the resulting
constant, linear, quadratic and cubic monomials over the binary field.
Every actual shell signing satisfies every such polynomial. This is stronger
than treating all pair products independently: xy=1, xz=0, yz=1 has compatible
independent products but its cubic lift yields the contradiction 1=0.

Whenever elimination derives linear equations, `boolean_linear_substitution`
parameterizes their complete affine solution set in free original bits.
`substitute_boolean_quadratics` substitutes this parameterization into every
untouched quadratic and composes recovery of the initial parameters. It
checks every linear recovery identity. The next lift therefore concerns
exactly the remaining candidates of the previous necessary relaxation.
This can repeat even after a bounded partial elimination: every polynomial
already derived is sound, while absence of further consequences is unknown.
Both time and stored-pivot bounds stop with `unknown`, never refusal.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --folded-cubic --period 4 --seconds 900 --cubic-pivots 50000 --write /tmp/folded-cubic.json
```

Recorded at L=3990, h=19, p=4, w=2: the 4,094 input rows on 3,818 signs
have 93 free parity parameters and quadratic rank 2,304. A 20,000-pivot
lift obtains five independent linear constraints, leaving 88 parameters;
the next lift reaches that cap without another linear constraint. A separate
50,000-pivot run likewise reduces 93 to 88 and then stops at its cap:
47,708 products in the first lift and 47,713 in the second, 207.20 seconds
observed in total. These are necessary equations, not a literal signing,
and are not claimed stronger than the earlier joint-field reduction.

`--joint-fields` first applies the existing exact rational/binary/ternary
quotient. `--cubic-search` reserves half the post-quotient budget for the
lift and gives the remaining time to exact **integer** shell search. The
cubic recovery equations remain active in that search. They are expressed
in negative-sign bits, whereas the literal engine uses positive-sign bits;
the right side is therefore adjusted by the equation mask's parity.
Any positive assignment is restored through all aliases and checked against
every untouched input shell row, then saved in the existing `moving_folded`
witness format for independent `--verify`. A resource stop is not a refusal
certificate; an explicit identity chain from `--cubic-proof` is checked as below.

Controls independently construct the full cubic monomial space for sixty
small systems, compare its rank and contradiction result, exhaustively
check every affine substitution on small cubes, and check the bit-convention
conversion in exact search. A driver control verifies a positive signing
against untouched rows and rejects an altered sign. No large proof bundle
or extra dependency is committed.

With `--joint-fields --seconds 1200 --cubic-pivots 30000`, the existing
joint reduction retains 86 binary parameters. Its cubic lift reaches
30,000 pivots after 27,699 products and derives no additional linear
constraint. Total observed time is 545.14 seconds, including 18.51 seconds
for the lift. It remains `unknown`; this bounded probe gives no improvement
on that joint-field fibre.

#### Checked cubic identities give a scoped infinite refusal

`--cubic-proof` records XOR dependencies during elimination and extracts
explicit identities of the form sum(q_i*l_i)=p, with affine binary
multipliers l_i. The small quadratic source basis is rebuilt from the original
rows. The verifier adds the indicated source polynomials and their multiplied
combinations, reducing repeated variables by x_i squared=x_i, and checks the
claimed polynomial coefficient by coefficient. It does not repeat cubic
elimination, trust a reported rank, or trust an alias from the generator.
It checks each linear reduction in order and requires the final identity
p=1. Grouping products by their multiplier variable keeps verification small.
Proof generation currently uses the original shell system, without
`--joint-fields`; this avoids trusting a prior quotient in the certificate.

For moving holes **97t and 99t**, L=3990, p=4 and w=2, the first bounded
lift gives nine linear constraints, reducing 90 parameters to 81. The next
lift obtains the constant contradiction at rank 9,547 after 6,322 products.
A fresh process reproduces this result. Explicit proof generation takes
23.91 seconds observed, and the separate identity verifier accepts it:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --folded-cubic --cubic-proof --hole 97 --period 4 --seconds 300 --cubic-pivots 20000 --write /tmp/cubic97-proof.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/cubic97-proof.json
```

The exact conclusion is nonexistence **within this periodic-interior word
model**, for these holes and every resistant index m odd. This follows from
the checked polynomial contradiction and the unchanged compiled system under
L increasing by whole periods. It excludes neither arbitrary words on that
support nor any other support. It is not the task's all-pairs obstruction.

The original-support integer search using the five cubic constraints ends
unknown after 600.01 seconds and 155,820 nodes, leaving 88 free bits. Eight
further bounded probes at h=5,13,29,41,57,73,85,93 also stop unknown with
88 parameters; these probes select possible searches, not a support theorem.

All **80 focused tests pass** (57.07 seconds observed), including fifty
independent small polynomial-identity controls, damaged proof rejection,
scope rejection, and the existing physical shell and direct-distance controls.
Certificates are regenerated outside Git; no large evidence file is added.
The complete physical-column comparison was also extended to h=19 and h=97
at L=18, p=4, w=2 (the resistant half-length phase), followed by the
whole-period extension check at L=22; both pass.

#### Larger diagnostic and the proof-extraction boundary

At h=19, a 120,000-pivot diagnostic reduces 93 parameters to 88 and then
reports a constant contradiction at rank 95,908 after 93,632 products.
Observed total time is 965.64 seconds (633.06 for the first lift and 329.09
for the second). **This larger refusal has not received standalone certificate
verification in this run.** A separate proof-generating replay exceeded its
1,200-second budget inside extraction, which still attempted to extract
every final linear consequence. I interrupted that process after about
1,436 seconds; it saved no completed certificate. That is a witnessed
resource failure, not another verified refusal.

The shipped generator now extracts only the final constant identity after
a contradiction and checks the time budget during extraction too. An
unfinished extraction returns `unknown`, `proof_time_limit`, an empty proof,
and a separate `algebra_status`; it cannot masquerade as a checked certificate.
A clock-boundary control exercises deadlines throughout a small proof run.
The h=97 certificate above remains independently checkable and accepted.
The large h=19 certificate can be attempted with the same command, replacing
`--hole 97` by `--hole 19`, the pivot cap by 120000 and the budget by 1200;
completion is not promised.

The task remains open. Neither the verified period-four h=97 refusal nor
the larger diagnostic excludes unrestricted inserted words or every permitted
two-hole support. The next mathematical step must allow those possibilities
or produce an actual signing in another model; repeating the capped small
hull or unsuccessful literal searches is not acceptance. Priority remains
provisional, and no project or milestone completion is claimed.
After the extraction repair, all **81 focused tests pass** (43.72 seconds
observed), and `git diff --check` is clean.

## Fern: unrestricted interior rank and the third word as a rational driver

25 November 2026. **The task acceptance remains unmet.** This result concerns
all words in the moving-hole interior, without periodic identifications. It
neither supplies signs nor excludes a support. The separate endpoint equations
and the condition that every coordinate is a sign remain essential.

For every integer h in 1..98, form the 356 by 402 Laurent matrix M_h(z)
from `moving_folded_stencils(h)[1]`: the coefficient of coordinate (a,q,s)
in row (Q,u) is the sum of c*z^d over that row's entries (a,q,s,d).
The recurrence on folded levels is exactly M_h(S)x=0, with S the shift
x_r -> x_(r+1). The previously checked radius-one physical-column derivation
and row partition apply unchanged.

**Result.** Over Q(z), M_h has rank 356. More specifically its square minor
on all 198 first-arm and 158 second-arm coordinates is invertible. Hence
its rational-function kernel has dimension 46, and projection onto the
46 third-arm coordinates is an isomorphism. The entire third word is an
arbitrary rational-function driver at this level of relaxation; the other
two words are uniquely recovered over Q(z). This is not a statement that
arbitrary third-arm *signs* extend to signs, or that the endpoints can be met.

**Checkable proof.** Specialize z=2 in a small prime field. For each of the 98 h values
the specified 356 by 356 minor has a nonzero determinant for a certified
prime from the fixed list 5,7,11,13,17,19. A prime is tried only until the
minor is nonsingular; a singular specialization is not a rank refusal.
This proves its Laurent determinant is not the zero polynomial over Q:
an identically zero integer Laurent polynomial would evaluate to zero here.
There are only 356 rows, so the rank is exactly 356. Writing M=[A B],
the kernel is precisely {(-A^-1 B y,y): y in Q(z)^46}, proving the driver
statement. The finite enumeration is over the complete parameter range h,
not over scales or sign words; the field argument handles arbitrary levels.

A further consequence gives the exact size of the unclosed interior problem.
For W>=3 independent levels, retain the equations centred at 1..W-2.
They have rank 356(W-2) over Q and nullity **46W+712**. Any finite rational
linear dependence among these rows would, after collecting shifts, give a
Laurent-polynomial left dependence on M_h, which full row rank excludes.
The row count gives equality. The 712 term is the two unclosed endpoint
levels; this formula includes neither physical endpoint constraints.

There are also nonzero finitely supported rational interior solutions:
choose a nonzero vector in the Q(z) kernel and clear its denominators.
A nonzero finite sequence cannot be periodic on the full integer line.
Thus linear interior equations alone cannot imply a fixed period for all
*rational* solutions. They might still imply strong restrictions after the
sign and physical boundary conditions are imposed. A periodic refusal cannot
be promoted to an unrestricted refusal by citing this rank calculation.

The selector uses sparse elimination. A separate verifier reconstructs the
physical stencil specialization, selects exactly the two-arm minor, and uses
row swaps to check its determinant. It rejects changed scope and malformed
minors. Certificates are small and generated outside Git:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --interior-rank --hole 19 --write /tmp/interior-rank.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/interior-rank.json
```

The full h=1..98 census verifies every two-arm minor (36.44 seconds
observed after the repair). An initial fixed
modulo-five run certified full row rank for all h but needed third-arm
columns at 24 positions. It therefore did not prove the stronger driver
claim; selecting a nonsingular specialization for the *fixed* two-arm
minor repairs that gap.
Independent finite-window modular controls at h=1,19,98 and W=3,4,7
reproduce the proved rank and nullity; specialization controls clear the
negative Laurent exponent before reducing modulo five. The pre-existing
81 tests plus two new certificate tests passed together (83 tests, 52.91
seconds); all three new tests, including the later finite-window control,
were then run separately. No large certificate bundle is committed.

A separate bounded exploratory prefix attempt retained physical left rows
and all interior centres before width 2,4,8, without repetition, at h=19,97.
Joint rational/binary/ternary closure found no contradiction at widths 2,4;
width 8 stopped at its 45-second budget during rational recovery. These
are witnessed failed attempts, not feasibility certificates. They add no
unrestricted obstruction and are not shipped as a second search mode.

The remaining mathematical obstacle is to meet both endpoints with *sign*
values in the rationally driven system, or to exclude all allowed supports.
The new result removes a tempting linear shortcut; it does not close the
infinite resistant family, and no project completion is claimed.

### Independent preservation — Hawthorn, 25 November 2026

Reconciled Fern's preserved commit `0938ac8` through trusted source inspection;
all three file changes apply cleanly to the preceding source. Re-ran the full
98-support certificate census: 74 minors certified modulo five, 23 modulo seven,
and one modulo eleven (38.79 seconds). All 84 focused tests pass (48.40 seconds),
and the command-line certificate write/read round trip verifies. The argument
uses a nonzero specialized two-arm determinant to prove full row rank over
Q(z); it does not decide sign feasibility, physical endpoints, or arbitrary
hole placements. This preserves the interior result only; the resistant-family
task and the project's global milestone remain unresolved.

## Rook: an absolute parity phase for unrestricted moving-hole words

25 November 2026. **The resistant-family acceptance is still unmet.** This
identity applies to every literal word on the support with holes `ht,99t`,
for every `1<=h<=98`, odd `t=2L+1>=9`. There is no periodicity assumption
and the third word remains free. Other hole placements are outside its scope.

Use the existing 402 slice labels `i=(arm,q,orientation)` and write
`x[i,r]=1-2*b[i,r]`, with bits b. For each of the 356 interior shell rows,
let `c[j,i,d]` be its integer coefficient at shift `d=-1,0,1`. Its necessary
binary equation at level r is

    sum_(i,d) (c[j,i,d] mod 2)*b[i,r+d] = sum_(i,d)c[j,i,d]/2 mod 2.

The coefficient sums are even. Select precisely the 176 shell rows whose
coarse shell index Q is `4,5,6,7 modulo 8`, using both orientations. XOR
their left sides as a Laurent polynomial vector P(z) over the binary field.
For every h, the XOR of their right sides is one, and

    P_i(-1)+P_i(0)+P_i(1) = 0,
    P_i(z) = (1+z) * (P_i(-1)*z^-1 + P_i(1)).

Here P_i(d) means a coefficient, rather than evaluation at d. Define the
explicit two-level parity observable

    J_r = sum_i [P_i(-1)*b[i,r-1] + P_i(1)*b[i,r]] mod 2.

The coefficients have a short closed description. Let `f(q)=1` for
`q mod 8` in 4..7, otherwise zero; additions below are modulo two. For a
first-arm label, say it is before the hole when `q<h` or `q=h,s=-1`.
Before the hole put `D=f(q), R=f(h-q)`; after it put
`D=f(q)+f(q-h), R=0`. On either other arm put
`D=f(q)+f(q+7)+f(q+h), R=f(7-q)`. For orientation +, the coefficients
`(P_i(-1),P_i(1))` are `(D,R)`; for orientation -, they are `(R,D)`.
This follows by selecting the physical column exponents; the cross lengths
79 and 23 agree modulo eight. An independent formula control matches every
coefficient of all 98 generated observables.

Then **J_r + J_(r+1) = 1** at every interior centre `2<=r<=L-1`.
There is also an absolute starting phase. XOR the 264 left boundary shell
rows with the same coarse index selection, now using offsets -1,0,1.
Their left side is exactly J_2 and their right side is one. Consequently

    J_r = (r-1) mod 2,             2<=r<=L.

For resistant `L=3990m`, the right endpoint must in particular have J_L=1.
This is a necessary condition, not evidence that the endpoint can be met.
XORing the recurrence over any putative odd-period bi-infinite interior
gives `0=1`. Thus **no odd-period literal interior exists**, for any of the
98 supports. The result also excludes an eventually odd-period interior
when its repeating portion contains all the required translated equations.
Even-period interiors, unrestricted nonperiodic words, and other supports
are not excluded.

The certificate records the actual observable and both fixed lists of source
rows. The separate verifier checks each polynomial coefficient directly,
including the left boundary phase; it performs no rank inference, parity
elimination or sign search. All 98 values of h are checked, the entire finite
parameter domain of this identity. Tests additionally reconstruct columns
by direct distance counts on retained physical vertices, independently of
the shell-column and folded compilers. They check the selected integer row
sums modulo four as well as every vertex coefficient modulo two. Damaged
observables, row lists, phases and scope claims are rejected.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --interior-cocycle --hole 19 --write /tmp/interior-phase.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/interior-phase.json
```

The recorded generation and separate verification both return `verified:true`,
`initial_phase:1`, and `all_pairs_decided:false`. At h=19 the observable has
356 terms; neither its size nor its phase is a count of literal solutions.
The earlier unrestricted rank contribution is preserved without alteration.

### What the unrestricted-window attempt did not decide

I next retained independent levels, with no repetition and no physical endpoint
identifications. For width W the rows are the integer interior stencil at each
centre 1 through W-2, and coordinate `(i,r+d)` has index `(r+d)*402+i`.
`joint_sign_closure` was given 180 seconds per window, with short recovery
active. Observed outcomes were:

| Width | h=19 | h=97 |
| --- | --- | --- |
| 4 | stable relaxation, 1.66 s | stable relaxation, 3.89 s |
| 8 | stable relaxation, 87.85 s | budget stop during ternary reduction |
| 16 | budget stop during rational reduction | budget stop during ternary reduction |

A stable relaxation is not a literal signing. No window produced a
contradiction. Two exact period-two *interior-only* searches also returned
unknown at 300 seconds, after 62,215 and 84,055 nodes respectively. These
measurements neither certify compatible signs nor refuse a support.

The exact remaining obstacle is the simultaneous literal cube and physical
endpoints, with the shortest word unrestricted; the alternating parity phase
handles only a necessary affine consequence. Even resolving all 98 moving
supports would still leave arbitrary hole positions, including holes on
different arms. No all-pairs upper bound below the target, infinite target
construction, project completion or milestone completion is claimed.

A final constructive probe used h=1, L=3990, period six, patch width two,
and the proved opposite-tail elimination before recovering a rational kernel.
Exact recovery took 578.51 seconds and left 178 original free signs; it checked
its basis against every input row. A seeded numerical search on that literal
free cube then ran for 600 seconds (776,000 proposed flips), without obtaining
zero residual or an exact candidate. Total observed time was 1,179.00 seconds.
The numerical prototype is not shipped and supplies no refusal certificate.
An attempted modular reconstruction shortcut also did not produce a verified
rational basis and was not used. These are witnessed failed attempts, not a
claim about the nonexistence of a target pair. The retained deliverable is the
exact parity law and its checker; the broader task remains open.

Validation for the retained deliverable: all 87 focused tests passed in
53.27 seconds. After adding the independent closed-formula control, that
changed test passed separately in 6.35 seconds. The final documentation-only
addition passes `git diff --check`; no unchanged suite was repeated.

### Applying the law before sign search

The moving-folded driver now returns a checked interior refusal on odd periods,
before entering joint-field or literal search. Its existing bound
`L>=2w+4+p` leaves fully periodic centres `w+2..L-w-2`, at least p centres.
XORing the alternating identities over one complete odd period gives 0=1.
The separate verifier rebuilds the model's length and phase constraints,
requires the same hole parameter in the identity, and rejects an even period,
a damaged identity, or a model too short for the argument. Even periods retain
the existing search behavior. This still refuses only the named periodic model.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --moving-folded --period 3 --half 11 --folded-patch 2 --hole 19 --write /tmp/odd-interior.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/odd-interior.json
```

The recorded driver run returns `ansatz_refused_by_interior_cocycle` in
0.024 seconds; separate verification returns `verified:true` and keeps
`all_pairs_decided:false`. All 88 focused tests pass in 54.14 seconds,
including bypass, even-period preservation and damaged-scope controls.

### Reconciled contribution — Linnet, 25 November 2026

Restored Rook's parity theorem and odd-period shortcut from trusted inspection
of stopped run `63271a9219f640318dd7f6ef0c9b1c70`, commit `61f5eb7`, onto
installed base `2939d1b`. The three pre-existing rank functions and their
controls are unchanged; their duplicate additions caused the earlier conflict.
The resulting Python source and test blobs exactly match the preserved
candidate (`e2844e1` and `b82b9ba`). All 88 focused tests pass (53.08 seconds),
both documented certificate round trips verify, and `git diff --check` passes.
This is a source reconciliation, not another mathematical result. Independent
trusted integration remains the delivery gate; no wider acceptance is claimed.

### Resubmitted after an access-only refusal — Fern, 25 November 2026

The prior contribution received a terminal review refusal because bounded test
and documentation inspection was unavailable, not because a defect was found.
This submission restores its complete trusted, untruncated diff from stopped
run `b6ecc3931e8647a4a944d0f37bc1037b`, commit `ef4fd68`, onto the same base.
Both Python blobs retain the hashes recorded above. A fresh independent review
is required; the earlier refusal remains part of the record.
Fresh local validation: all 88 focused tests pass in 49.14 seconds, both
documented certificate round trips verify, and `git diff --check` passes.

## Fern: all constant-row parity traces, and complete mod-four completions

25 November 2026. **The resistant-family acceptance remains unmet.** Both
results below concern holes `ht,99t` on the first arm, with the third word
unrestricted. Neither decides integer signings or other hole placements.

### Five traces, with phases fixed by both physical endpoints

For every `1<=h<=98`, the 356-by-402 interior binary matrix evaluated at
shift one has rank 351. The following five independent shell selectors
span its complete left kernel. In the table, `+` and `-` are shell-row
orientations, and every listed residue is selected.

| Law | Positive row indices | Negative row indices |
| --- | --- | --- |
| 1 | 4,5,6,7 modulo 8 | 4,5,6,7 modulo 8 |
| 2 | 3,4,5,6 modulo 8 | 0,5,6,7 modulo 8 |
| 3 | 0 modulo 4 | 3 modulo 4 |
| 4 | 2 modulo 4 | 1 modulo 4 |
| 5 | 1 modulo 4 | 2 modulo 4 |

For each selector, XOR its integer shell rows modulo two to obtain
`P_i(-1),P_i(0),P_i(1)` as in Rook's notation. Define

    J^j_r = sum_i [P^j_i(-1)*b[i,r-1] + P^j_i(1)*b[i,r]] mod 2.

Every selected vector has `P(-1)+P(0)+P(1)=0`. Direct substitution gives
`J^j_r+J^j_(r+1)=d_j`, where `d=(1,1,1,1,0)`.
The five resulting observables are independent. Rank 351 and these five
independent dependencies prove completeness **for constant combinations
of the 356 row types whose sum is a two-level first difference**. This
makes no completeness claim for shifted combinations, longer recurrences,
nonlinear consequences, or the whole shell system.

The left physical rows imply, at level 2,

    J1=1,  J2+J3=1,  J4+J5=0.

The right physical rows imply, at level L,

    J1+J2=0,  J3+J4=0,  J5=0.

These are exactly the three-dimensional spaces of endpoint-determined
combinations on each side: the verifier tests every one of the 31
nonzero combinations. Their common space has dimension one and fixes
`J1+J2+J3+J4+J5=0` on both sides. The union has rank five. Propagating
the recurrences therefore forces, for **every** level `2<=r<=L`,

    (J1,J2,J3,J4,J5) = (r-1,r-1,r,r,0) mod 2.

There is no inconsistency between these endpoint traces for either parity
of L. This strengthens the necessary conditions without refusing a support.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --parity-traces --hole 19 --write /tmp/parity-traces.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/parity-traces.json
```

### The entire linear binary relaxation has an infinite completion

For every **odd** `h` from 1 through 97 and every `L>=18`, there is an
explicit sign assignment to the entire physical support for which every
integer shell row is divisible by four. Thus the full necessary linear
binary system, not merely the five traces, is compatible on all these
supports and lengths. In particular this covers every resistant scale
`t=7980m+1`, `m>=1`, for these holes. Even h is outside this construction
and is already excluded at resistant scales by the odd-distance obstruction.

The certificate has a period-two folded interior, six independently signed
levels at each endpoint, and independent old vertices. For each of the 49
odd h and each parity of L, exact binary elimination produces one witness
at L=18 or 19. The separate verifier does **no elimination**: it substitutes
all recovered signs into every untouched integer quotient row and checks
zero modulo four, including the physical endpoints and a positive centre.

This is an infinite extension, rather than an extrapolation from two lengths.
For patch width six, left-touching centres are 2..7, right-touching centres
are L-7..L-1, and the two interior residue representatives are 8 and 9.
At L>=18 these ranges do not overlap; every omitted centre sees only the
period-two interior. Its row equals one of the two representative rows.
The right-coordinate names depend only on L modulo two. These facts make
the quotient identical for all larger L of the same parity; the verifier
also guards its implementation by comparing L with L+2.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --parity-completion --hole 89 --half 3990 --write /tmp/mod-four-completion.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/mod-four-completion.json
```

The first attempt with three free endpoint levels worked on 48 odd supports
but failed at h=89 for both length parities. Widths four and five also failed
there; six succeeded. A period-two interior with only two free endpoint
levels failed even at h=19. These failures concern the restricted quotient,
not unrestricted words. No large certificate files are committed.

The precise remaining obstacle is to raise these modular signings to exact
integer zero in every shell while meeting both endpoints, or to find an
obstruction using more than this linear binary relaxation. A modulo-four
completion is neither a literal solution nor a target pair. It does not
exclude stronger congruences or nonlinear binary consequences.

Validation: all 92 focused tests pass in 91.43 seconds. They regenerate the
five-law classification for all 98 h, all 98 completions for odd h and both
length parities, reject damaged certificates, and check expanded assignments
against independently generated physical shell columns at several lengths.
Both documented certificate round trips verify; `git diff --check` passes.

### A replayable obstruction to period two with the physical phases

For **h=19**, the period-two interior equations and the five endpoint-forced
trace phases have no literal signing. Unlike the earlier interior-only
searches, this statement retains the absolute phases inherited from the
physical endpoints. It excludes a period-two block containing both complete
translated row parities, with neighbouring levels inside the repeating
block, in any full solution on this support. In particular widening the
free endpoint patches cannot rescue a sufficiently long period-two interior.
Other even periods, other h, unrestricted nonperiodic interiors and arbitrary
hole placements are not decided by this certificate.

The finite system has 804 original signs and 712 interior row instances.
The ten trace conditions (five at each level parity), together with the
original shell parity equations, leave 94 free binary coordinates. No
rational or ternary quotient is used in the retained proof. A Boolean cubic lift gives 15 checked linear consequences;
a second lift on 79 coordinates gives 41 more; on the remaining 38
coordinates a final explicit polynomial combination is the identity `1=0`.
The first lift hit its 40,000-pivot limit, but the 15 retained consequences
have explicit identities; completeness of that lift is unnecessary.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --period-two-phase-refusal --hole 19 --seconds 300 --cubic-pivots 40000 --write /tmp/period-two-phase.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/period-two-phase.json
```

Generation can return unknown on a slower machine. The separate verifier
first checks the five trace laws and endpoint identities. It rebuilds the
original period-two shell rows and their affine binary fibre, includes the
ten checked phase equations, and verifies the saved Boolean identities by
multiplication. It performs binary elimination but no rational or ternary
quotient, external solving, or cubic search. The generic
quadratic compiler now accepts explicit additional binary conditions, while
this scoped wrapper establishes why its conditions are necessary. No external
solver or new dependency is used by the shipped generation or replay path.
The roughly 470-kilobyte generated certificate is not committed.

The path to this certificate included a temporary probe with already installed
OR-Tools 9.15.6755. The original phase-constrained interior model returned
unknown after 300 seconds. Its exact reduced equations (580 signed coordinates, rational nullity 95)
returned infeasible in 85.33 seconds. This solver report motivated proof extraction; it is not
the proof accepted by the checker. A 20,000-pivot Boolean pass left 91
parameters without a contradiction. An independent temporary Z3 probe stopped
unknown. A direct handwritten interior search stopped unknown after 900.07
seconds and 122,303 nodes. These limits are not impossibility results.

The full period-two model with six free endpoint levels, h=19 and L=3990
also stopped unknown after 602.22 seconds without completing a joint-closure
round. The new phase certificate explains why further sign branching in
this particular period-two model cannot produce a solution. The broader
resistant-family acceptance and the every-triple milestone remain unmet.

Further temporary exact probes found no witness: the raw period-two endpoint
model stopped unknown at 1,200.32 seconds (35,908 branches); its analytically
opposite-tail-reduced version stopped unknown at 900.10 seconds (35,984
branches); the period-four model stopped unknown at 900.48 seconds (40,215
branches). These installed-solver probes add no dependency and supply no
refusal claim. The retained period-two obstruction instead comes from the
original-row polynomial certificate described above.

Final validation: all 93 focused tests pass in 130.37 seconds; the expanded
additional-condition test also passes separately. The public original-row
proof command regenerates a verified refusal in 178.04 seconds, and a fresh
process separately verifies its saved certificate. Changing a proof bit, the
hole parameter, the claim scope, or removing the proof is rejected. The
original-row path uses no rational or ternary quotient. `git diff --check`
passes. No all-pairs or project acceptance is claimed.

## Mica: replayed phase refusals at further holes (25 November)

Using the accepted original-row compiler unchanged at source `c500500`,
I generated and replayed the period-two phase refusal at further holes:

| h | Generation plus first replay, seconds | Proof rounds | Separate CLI replay |
| --- | ---: | ---: | --- |
| 1 | 128.38 | 2 | accepted |
| 3 | 118.49 | 2 | accepted |
| 21 | 110.29 | 2 | accepted |
| 49 | 60.31 | 2 | accepted |
| 97 | 14.05 | 1 | accepted |

For each row, reproduce with the existing commands, substituting its h:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --period-two-phase-refusal --hole 1 --seconds 300 --cubic-pivots 40000 --write /tmp/phase-refusal.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/phase-refusal.json
```

These are polynomial identities on the original integer shell parity fibre,
with all five physically forced trace phases. The same necessity argument as
for h=19 applies: a sufficiently long period-two block in a full signing
would satisfy the rebuilt finite system and hence the checked identity
`1=0`. Free endpoint patches cannot repair that block. No large certificates
are committed; the commands regenerate them. This extends the scoped theorem,
not the task's all-pairs acceptance. There is no new implementation behavior,
and unchanged test suites were not repeated.

A separate exact compilation at h=19 exposes the next resource boundary.
With the trace phases, periods 2, 4, 6 and 8 have respectively 94, 188, 278
and 373 free binary coordinates. The original-row cubic engine accepts at
most 128; increasing the period therefore does not just repeat the successful
proof command. Period four's 188-coordinate mod-eight compilation succeeds,
but it is not a contradiction or a literal signing. Periods six and eight
stop at the quadratic compiler's 256-coordinate dimension guard.

The remaining mathematical obstacle is unchanged: decide literal signings
with longer even or nonperiodic interiors and their physical endpoints, then
allow arbitrary hole positions. The present identities do not exclude those
possibilities and give no all-pairs obstruction or infinite target
construction. The broader task and every-triple milestone remain open.


## Hawthorn: original-row phase proofs beyond period two (25 November)

The all-pairs acceptance is still open. The phase proof entry point now accepts
an explicitly named even period. It retains every original sign and every
interior row, plus all five independently checked absolute endpoint phases at
each residue. Odd periods are rejected because they identify opposite absolute
trace phases. A refusal concerns a repeating interior block containing every
row residue and its two neighbouring levels; it does not impose or exclude
unrestricted nonperiodic words or other physical hole placements.

The Boolean engine now admits up to 192 free binary coordinates, enough for
the 188-coordinate period-four fibre at h=19. A larger model still reports a
dimension limit. Its multiplier map stores monomial positions rather than
one-bit integers. For 188 variables and multiplier 187, those positions occupy
651,228 bytes on this interpreter; the former one-bit representation would
occupy an estimated 2,549,643,788 bytes from Python integer digit sizes. This
estimate describes the map alone, not total search memory. The verifier also
computes triple indices directly rather than materializing every triple.
Elimination storage remains bounded by the requested pivot count and can
still be substantial; resource exhaustion is unknown, never a refusal.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --periodic-phase-refusal --period 4 --hole 19 --seconds 600 --cubic-pivots 12000 --write /tmp/phase-four.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/phase-four.json
```

Only a generated refusal can pass the second command. As a positive control
for the proof machinery, the general entry point at period two, h=97 and
40,000 pivots regenerated the known refusal in 13.07 seconds; a fresh process
accepted it. Changing its period, hole, scope flags or proof is rejected.
The old period-two command and certificate format remain supported.

The first h=19 period-four run stopped unknown after 442.42 seconds:
the first 12,000-pivot pass supplied three explicitly verified linear
consequences, reducing 188 parameters to 185; the second pass hit the same
pivot limit without another consequence. Each saved identity was checked by
polynomial multiplication against its original-round inputs. These three
constraints are not a contradiction or a literal witness.

A continuation need not rediscover those consequences. `--resume-phase`
accepts an unknown certificate for the same hole, period and checked trace,
rebuilds the original shell parity fibre, and verifies every retained identity
before applying its affine substitution. A final refusal retains the entire
proof chain for independent replay. For example:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --periodic-phase-refusal --period 4 --hole 19 --seconds 1200 --cubic-pivots 24000 --resume-phase /tmp/phase-four.json --write /tmp/phase-four-next.json
```

Replaying the initial partial result restored 185 parameters. The time budget
is checked between algebraic stages; verification of a retained proof may
run beyond a very short budget. A six-period request reports unknown with
`dimension_limit` and 278 free coordinates; it is not silently treated as a
refusal. Large generated proof files remain outside Git.

Validation: all 98 focused tests pass (145.64 seconds). They include the
general certificate round trip and damaged scopes, and period-four and
period-six rows compared coefficient by coefficient with independently folded
original physical shell columns. Wide polynomial controls cover 188 and 192
variables, check explicit identities, and reject damaged identities. Resume
controls reject altered identities and mismatched scopes, preserve exact
recovery, and replay an independently checked final contradiction after a
resumed reduction. The expanded final resume control also passes separately.


The deeper h=19 run, with 24,000 pivots per pass and a 1,200-second
budget, stopped unknown after 1,044.14 seconds. It again reduced 188 to 185
parameters and obtained no further consequence before the next pivot limit.
Doubling this cap did not strengthen the retained reduction. At h=97 the
initial period-four run stopped unknown after 900.05 seconds: 187 parameters
became 184, then certificate extraction reached its time limit. Only the
first checked reduction was retained for a subsequent resume attempt.


A real h=97 resume used the retained three consequences, rechecked them,
and found three more: 184 parameters became 181 before the 600-second budget
expired. Independent replay by polynomial multiplication verified both
reduction rounds, 187 to 184 to 181. The next unfinished pass hit its time
limit at 11,297 pivots; it supplies no refusal. To reproduce this sequence,
use h=97 and period four with 24,000 pivots, first for 900 seconds, then
resume its saved unknown certificate for 600 seconds. Timing affects how
many consequences a run retains; every retained identity remains checked.


The final h=97 continuation rechecked that entire chain, then stopped at its
24,000-pivot cap after 360.04 seconds without another consequence. The
retained result is six checked necessary constraints and 181 parameters,
not a contradiction. Repeating the same cap on the same reduced system has
no demonstrated benefit. The next substantive step needs a stronger bounded
algebraic strategy or a new mathematical argument about literal words;
all permitted holes and unrestricted nonperiodic interiors remain open.
No literal witness, all-pairs obstruction, task acceptance or project
completion is claimed.

## Rook: a bounded sweep and cheaper replay (25 November)

The latest predecessor commit was absent from this assigned clone. The trusted
integration inspection supplied an untruncated patch against its exact base
`26c74e5`; applying it restored the three advertised blob hashes. Recovery
commit `704b05e` preserves that contribution separately. Its 98 tests passed
before further changes. Nothing was published from this private room.

At h=97, period four, the unchanged proof generator with only 3,000 pivots per
pass reproduced six checked necessary constraints in 100.23 seconds, leaving
187 -> 184 -> 181 binary parameters. Separate replay rebuilt the original
shell parity fibre and checked all six polynomial identities. This is the
same retained reduction as the predecessor's 24,000-pivot attempts, not six
additional constraints and not a contradiction.

The optional `--cubic-sweep` keeps examining products after its pivot store
fills. It discards new nonlinear pivots at that bound but allows at most n+1
additional linear pivots, where n is the current number of parameters.
Each retained row still has an identity using the original quadratic basis:
discarded rows are never premises. The unchanged independent polynomial
checker verifies these identities. If any row was discarded, finishing the
sweep reports unknown rather than compatibility; a checked identity 1=0 can
still prove a refusal. A proof-producing sweep reserves one fifth of its
remaining time for extraction, since stopping precisely at the search
deadline otherwise loses identities that cannot be extracted in time.

A small exact control has quadratics [33,70,124] in the documented Boolean
monomial encoding. A four-pivot ordinary pass stops unknown. The sweep
discards two rows and later produces the independently checked identity
1=0. Exhaustive controls on 100 small systems check every retained
consequence against every actual Boolean solution, validate the explicit
identities, and enforce the pivot bound.

Dense product construction now toggles a byte buffer before making its wide
integer. Sparse products keep the direct path. This changes neither the
monomials nor their cancellation. An illustrative dense 188-variable local
control took 0.0299 seconds with repeated wide-integer XORs and 0.0070 seconds
with packing; this is not a general timing guarantee. Tests cover monomial
sets, the packing threshold, collisions, and wide 188/192-variable maps.

The full unchanged-order packed baseline reproduced exactly the same six
identities in 44.00 seconds, versus the earlier 100.23-second observation.
Inspection then showed that **every multiplier in all six identities is
zero**: these are linear consequences of the quadratic input span, not
consequences requiring cubic products. The engine now applies input-span
linear rows before multiplication. A 1,400-pivot run reproduced both
reductions in 18.24 seconds; the first two passes used zero products and
had ranks 1,400 and 1,397. Its final unreduced pass examined seven products
before its cap. Timing varies; the checked equations do not.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --periodic-phase-refusal --period 4 --hole 97 --seconds 120 --cubic-pivots 1400 --write /tmp/phase-linear.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --periodic-phase-refusal --period 4 --hole 97 --seconds 240 --cubic-pivots 12000 --retain-quadratics --write /tmp/phase-quadratic.json
```

The second command retains **four additional independent quadratic
consequences**, beyond the reduced input span on 181 parameters. Its first
cubic pass found them; the next pass, using all four as premises, found
nothing more at the same cap. This observed run took 128.78 seconds.
Each quadratic round is stored as `{"quadratics": [identities...]}` amid
the existing affine-reduction rounds. Replay checks every identity against
the preceding premises, requires new quadratic rows, then explicitly adds
them to the next round. Modified, duplicate and malformed rounds are
rejected. A partial chain is never accepted as a refusal: a final checked
constant contradiction is still required. Resume rechecks both kinds of
round. Up to sixteen new quadratic rows are retained per pass; their proof
extraction also receives the reserved time. Large certificates stay out of Git.
A fresh process replayed the six linear and four quadratic identities in
16.59 seconds, preserving the entire chain exactly, using `--resume-phase`
with the second saved file and a one-pivot cap for the subsequent search.

The bounded sweeps did not strengthen the six linear constraints. The
packed natural-order continuation examined 97,251 products; reverse and
sparse-row-order probes examined 47,696 and 47,831. All stopped unknown
with 181 parameters. An earlier sweep without extraction time reached its
deadline and retained no proof, which motivated the explicit reservation.
These are witnessed limits of the strategies, not impossibility results.

Validation: all 104 focused tests passed in 118.08 seconds; six selected
quadratic controls also passed after the final replay guards. They include
checked quadratic reuse and resume, rejection of damaged or redundant
premises, and an explicit quadratic round followed by a separately checked
contradiction. The task's all-pairs acceptance remains unmet.

The h=97 continuation at 24,000 pivots rechecked the full chain and then
found no further linear or quadratic consequence (126.12 seconds total).
At h=19, the input-span prepass gives the known three linear consequences,
188 -> 185 parameters. A subsequent 12,000-pivot pass found no new quadratic
row (64.66 seconds total). These differences concern the stated periodic
models; neither result licenses excluding unrestricted interiors.
Flipping one bit of an actual retained quadratic identity was rejected by a
fresh CLI resume with `Boolean cubic polynomial identity failed`.

The final h=19 continuation combined quadratic reuse with a 12,000-pivot
sweep. It checked 97,680 products, discarded 86,647 new nonlinear rows, and
stopped unknown after 481.19 seconds with the same 185 parameters and no
additional consequence. The earlier three checked identities were preserved.
The remaining obstacle is literal solvability with unrestricted interiors
and physical endpoints, followed by all permitted supports. These bounded
degree-three strategies supply neither a literal construction nor an
all-pairs obstruction; repeating the same caps has no demonstrated benefit.

Finally the legacy `--period-two-phase-refusal --hole 19 --seconds 180
--cubic-pivots 40000` path regenerated its scoped refusal in 85.56 seconds.
A fresh process accepted the saved certificate with `--verify`. Both retained
the period-two-only scope and false literal-existence/all-pairs flags. This
checks the actual older CLI format after the new quadratic-round support;
it adds no broader mathematical claim.


## Hawthorn: source recovery and independent replay (25 November)

Recovered Rook's stopped contribution `48530606` from the complete trusted
inspection patch, without publishing its rejected integration. All three
reconstructed blobs match the patch's recorded hashes; private commit
`5c40898` preserves them exactly. Lesson
`hawthorn-rook-source-recovery-20261125` stores immutable copies of the
source, tests and preceding record, so later readers need not recover a room.

All 104 focused tests passed in 93.94 seconds. A fresh period-four, h=97
run with 1,400 pivots reproduced the two checked input-span reductions
187 -> 184 -> 181 in 13.95 seconds. A separate one-pivot resume replayed
both proof rounds unchanged. Both runs report unknown; neither the
unrestricted-sign problem nor the all-pairs acceptance is settled. This
recovery supplies reviewable source and replay evidence, not a new theorem.


## Hawthorn: actual open interior windows, without periodic identification

The next model leaves both ends free and every folded level distinct. For
centres `first..first+length-1` it retains all 356 original integer shell
rows at each centre and all five endpoint-derived trace phases. Coordinates
run from `first-1` through `first+length`. These are necessary equations for
any physical solution with `L>=first+length+1`; they omit other centres and
the physical endpoint equations. No periodicity is imposed.

At both `first=3` and `first=4`, h=19 and h=97 admit literal signings for the
**specified two-centre window**. Each example supplies all 1,608 signs and passes all
712 integer rows and ten trace equations. The installed OR-Tools solver
found the odd-start examples in 9.21 and 5.54 seconds, and the even-start
examples in 546.68 and 8.05 seconds, after explicitly adding the checked
binary echelon equations; neither the shipped checker nor
the example command imports that solver. This is finite local compatibility,
not a physical endpoint completion, an infinite construction or all-pairs
acceptance. In particular it does not rule out a contradiction at other
centres outside a chosen window or on a larger window. Translation by two
preserves both integer coefficients and trace phases, so these four words
supply checked local signings at every starting level at least three.
Different windows need not agree on shared coordinates.

The following standard-library command emits and checks the recorded h=97
example; h=19 and `--first-level 4` (or any level at least three) are also
available. The saved file can be checked independently.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --open-phase-example --hole 97 --write /tmp/open-window.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/open-window.json
```

The recorded run reports `verified: true`, `length: 2`, `first: 3`, and
both existence and all-pairs decision flags false. For a fresh search use
`--open-phase-window 1 --hole 19 --seconds 30 --nodes 100000`; the
standard-library engine found and checked a one-centre signing. A two-centre
h=19 search exhausted one million nodes in 126.09 seconds and stayed unknown.
A resource stop never turns into a negative mathematical conclusion.

The two examples starting at 3 **cannot simply be continued with their signs
fixed**. At the next centre, 5, row `(0,+)` uses only their already supplied
coordinates and sums to -2 for each. This is an exact check of these two
words, not a claim that every two-centre signing fails to extend. The
regression tests retain this failure to prevent mistaking local compatibility
for a construction. Other tests compare every open-window coefficient with
direct physical distance-shell columns, keep both end levels distinct, and
reject altered signs, scope and dimensions.

The unrestricted interior and arbitrary-support problems remain open.


Continuation limits (installed OR-Tools 9.15.6755, one search worker):

| Necessary model | Holes h | Seconds per case | Outcome |
| --- | --- | --- | --- |
| Three consecutive unwrapped centres | 19, 97 | 600 | unknown |
| Two centres plus every contained neighbouring shell row | 19, 97 | 300 | unknown |
| Period four, with checked affine consequences | 19, 97 | 600 | unknown |
| Period six, with the complete binary echelon constraints | 19 | 1200 | unknown |

The guarded model retains 1,068 integer rows on the same four sign levels:
712 original window rows and 356 neighbouring rows whose entire support is
already present. These searches add no dependency to generation or replay.
Their unknown outcomes are resource limits, not impossibility certificates.
Joint rational, binary and ternary closure on those guarded integer rows
made only the existing binary identifications; neither hole gained a new
ternary copy or short recovery row. Repeating these caps has no demonstrated
benefit. What is missing is a compatible overlapping extension, followed by
physical endpoint completion and arbitrary supports.

Validation: the 106-test suite passed in 107.21 seconds before the final
example data, then five focused window controls passed in 2.95 seconds,
including both parities and translations. The physical-column comparison
also passed at the advertised minimum half-length. A separate command-line
process verified the h=97 example translated to first level 20. The main
task and the arbitrary-triple milestone remain unfinished.

Mallow independently restored the attached source, passed the four new
window controls, and replayed a translated witness in a fresh process
(lesson review 45803). That review confirms the stated local compatibility
result, not global existence.

## Hawthorn: a period-four sign-flip obstruction (25 November)

For each `h=4j+1`, `0<=j<=24`, and also `h=91`, the all-word interior
has no literal signing obeying `s(a,q,orientation,k+2)=-s(a,q,orientation,k)`
at every level of a sufficiently long interior block. This excludes that
specific sign-flip period-four pattern, even without endpoint phase
conditions. It does not exclude general period-four words, decide endpoint
completion, or meet the task's infinite-family/all-pairs acceptance.

The finite system retains all 1,424 original integer rows at four residues,
with 1,608 independent sign positions before imposing the named sign flips.
The 804 additional binary equations say precisely that each position and
its translate by two have opposite signs. No endpoint trace equations are
used. Original shell parity plus these relations has 98 free binary
coordinates at h=97. On that complete affine fibre, each untouched integer
row is identically divisible by four. Divide by four and reduce modulo two:
its remainder is a Boolean polynomial of degree at most two. An explicit
XOR of those input polynomials is the constant one. Thus simultaneous
integer zeroes would give `0=1`. There are no multiplied polynomials,
external solvers, rational quotients or search assumptions in this proof.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --antiperiod-two-refusal --hole 97 --write /tmp/sign-flip-refusal.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/sign-flip-refusal.json
```

A fresh command emitted `status: refused`; a separate process returned
`verified: true`, `period: 4`, `sign_shift: 2`, with both global decision
flags false. Generation and replay of all 26 named hole certificates passed
in 14.88 seconds while other exploratory processes were running. The
certificates are small and regenerated rather than committed.

The proof generator deliberately checks only the input span. At the other
23 odd holes from 1 to 97, it returns unknown. That is not a compatible
signing or a complete polynomial-ideal result. In particular h=19 remains
open under this restriction. Tests reject damaged identities, altered hole
and scope, an unknown result passed as a proof, and removal of the sign-flip
hypothesis. They also check the relation's exact sign convention and the
negation of original integer rows under translation by two.

Validation of this addition: four focused sign-flip controls pass, all 112
spectrum tests pass in 107.89 seconds, and a fresh command-line process
replays the saved h=97 identity. The inherited direct physical-column test
covers four unwrapped centres at first level 3 and minimum half-length 8;
those four residues are exactly the rows used here after period-four
identification. `git diff --check` passes.

A different encoding of the unrestricted three-centre h=97 window, using
all exact allowed short-row sign patterns and the fully reduced complete
binary basis, stopped unknown after 600.02 seconds, 24,742,784 branches and
1,694,391 conflicts. It used installed OR-Tools 9.15.6755 only for exploratory
search. This is a resource limit, not a local obstruction. The shipped
sign-flip certificate generator and checker use the standard library only.

### Stronger linear obstruction for all odd integer values

For all 25 holes `h=4j+1`, `0<=j<=24`, there is a simpler, stronger
certificate. After substituting `s(k+2)=-s(k)`, let A be the original integer
matrix on the two independent levels (804 coordinates, 1,424 rows).
The certificate supplies row weights `w_r` in `{0,1,2,3}` such that

    C = sum_r w_r A_r,       every C_j is divisible by 4,
    sum_j (C_j/4) is odd.

If A*s=0, then `(C/4)*s=0`. When every s_j is an odd integer, its left side
is odd modulo two, a contradiction. Thus these holes exclude even arbitrary
odd integer values under the stated sign-flip constraint, not just values
+1 and -1. No endpoint phases are needed. This still says nothing about
unrestricted interiors, endpoint completion or arbitrary support choices.

Generation solves `A*b=A*1/2` modulo four, necessary for `s=1-2b`.
Unit row operations and divisions by two retain the row weights in two bit
planes. The independent verifier does none of that elimination: it rebuilds
A, forms the weighted sum with ordinary integers, and checks divisibility
and the odd sum. It uses no Boolean compilation, rational elimination,
endpoint phase calculation, external solver or bounded search. All 25
certificates regenerated and replayed in 13.61 seconds. At h=97 the
582-byte certificate selects 534 rows; C/4 has 652 nonzero coefficients,
with histogram `{-3:100, -2:49, -1:354, 1:149}` and sum -603.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --antiperiod-two-odd-refusal --hole 97 --write /tmp/odd-sign-flip.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/odd-sign-flip.json
```

The separate replay prints `verified: true` and the precise claim: no odd
integer interior values reversing after two levels. The two sign-flip
compilers are checked against the pre-existing four-residue shell compiler;
its unwrapped rows are covered by the direct physical-column control at
half-length 8. A six-level unwrapped block, with centres 3 through 6, supplies
all four residues and their radius-one neighbours. Consequently a longer
sign-flip interior cannot evade the identity through distant endpoint
patches. Sign reversals remain a hypothesis, not a forced property of a
physical pair.

Hole 91 retains only the Boolean sign obstruction above: this linear
checker returns unknown there. Hole 19 also returns unknown. Regression
controls keep those scopes separate, check a damaged bit in the row weights,
and reject altered divisors, holes, dimensions and global decision claims.
They replay successfully with the Boolean, rational and endpoint-phase
routines disabled.

### Why that linear obstruction cannot settle the unrestricted interior

For **every odd hole h from 1 to 97**, every finite unwrapped window of the
bare integer shell rows has an odd-integer solution. This theorem includes
no endpoint trace equations, no sign bounds and no physical endpoint rows.
It is not a literal signing or an infinite compatible word. It explains a
precise limit of the preceding linear congruence method.

Let M(z) be the 356-by-402 Laurent matrix whose `(row,label)` coefficient
is `sum_d c(row,label,d)*z^d`, with the radius-one shifts `d=-1,0,1`.
Reduce coefficients modulo two. Evaluate at the nonzero element alpha of
`F4=F2[alpha]/(alpha^2+alpha+1)`. The retained certificate selects a square
356-column minor that is nonsingular over F4. Its determinant therefore is
not the zero Laurent polynomial. Hence M(z) has full row rank over F2(z).
All 49 hole certificates regenerated and independently replayed in 8.98
seconds. The verifier uses a different row-pivot algorithm from selection;
tests check its field arithmetic against polynomial multiplication.

Any binary dependence between finitely many shifted shell rows would give
a polynomial row vector f(z) with `f(z)*M(z)=0`. Full row rank forces f=0.
Thus the integer matrix A_N on N consecutive unwrapped centres has binary
row rank exactly `356*N`; there are `402*(N+2)` coordinates. Direct finite
binary compilations at N=1,3,7 independently confirm the implication at
holes19/97. The theorem itself is for every positive N, not a rank census
bounded by those controls.

Here is the integer existence argument. Choose a square column minor B of
A_N with odd determinant D, and write F for its other columns. Every shell
row has even coefficient sum, so `B*1+F*1=0` modulo two. Set

    s_free = D*1,       s_pivot = -adj(B)*F*1.

These are integers and `A_N*s=0`, since `B*adj(B)=D*I`. The free coordinates
are odd. Modulo two, `adj(B)*F*1=adj(B)*B*1=D*1`, so every pivot coordinate
is odd too. No bounds on those odd integers are asserted. This proves that
no linear congruence of the bare interior rows can exclude all odd values;
the actual unit-sign restrictions or additional endpoint conditions matter.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --interior-binary-rank --hole 19 --write /tmp/binary-interior-rank.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/binary-interior-rank.json
```

The separate replay reports rank356 and explicitly excludes endpoint
traces from its odd-integer claim. Tests reject the singular first-356-column
minor, duplicate columns, wrong field conventions, altered dimensions and
broader existence flags. All source remains standard-library only.

Further exploratory limits in this stretch: at h=19 the sign-flip model
with physical endpoint phases was reported infeasible by installed OR-Tools
in439.30s, but the original-row Boolean proof is still unknown. Its first
38.75s pass retained three verified linear consequences, then hit the
40,000-pivot limit. Resuming those consequences with a600s sweep retained
seven proof rounds but stopped at proof extraction's time limit with91
parameters remaining; no refusal is claimed. The same sign-flip model
without endpoint phases stopped unknown after300.01s. These solver and
resource reports do not strengthen either theorem above.

Final validation for the linear and binary-rank additions: all116 spectrum
tests passed in107.94s. Fresh separate command-line processes replayed both
the h=97 odd-integer obstruction and unrestricted binary-rank certificate.
`git diff --check` passed. The h=19 unrestricted three-centre exact-table
search stopped unknown after1200.02s,29,073,078 branches and1,897,417
conflicts. Thus neither longer-window search supplies a local obstruction
or signing. The actual unit-sign problem with endpoint traces, then
physical endpoint completion and arbitrary supports, remains the next
mathematical obstacle; enlarging a bare linear congruence test cannot
remove it. Main task acceptance and the global milestone remain open.

Aster independently replayed the earlier26 Boolean sign-flip refusals and
four focused controls (canonical review46008). That review predates the
stronger odd-integer identity and binary-rank theorem, which have not yet
received independent review. No acceptance or publication is inferred from
that earlier review.

## Mallow: endpoint traces do not obstruct finite odd-integer interiors

For every odd hole h=1,3,...,97, every positive number N of consecutive
interior centres, and either starting parity (first centre at least 3),
there are **odd integer values** satisfying all 356N exact shell rows and
all five endpoint-derived parity traces at every centre. This strengthens
Hawthorn's bare-window result by retaining the traces. It does not bound
values by one, include physical endpoint rows, produce mutually compatible
windows or decide a target pair. The task's acceptance remains unmet.

Proof. The checked Laurent minor over F4 gives full binary row rank to
A_N, as in Hawthorn's shifted-row argument above. Independently, the
period-two shell system has a binary solution with the absolute trace
phases at every odd h. The new certificate records that word and checks
all its original integer rows modulo four and every trace by substitution.
Repeating the word, then restricting to a window, gives a vector r of
unit residues with A_N r divisible by four and the prescribed traces.
Absolute levels, including odd starting levels, select the residues;
no unwrapped coordinates are identified in the exact equation system.

Choose an odd-determinant square column minor B of A_N. Set free correction
coordinates to zero and solve

    B y_pivot = -A_N r / 4,       x = r + 4y.

The right side is integral. Every denominator in y divides the odd
integer det(B). Thus A_N x=0 over the rationals and x has the same residues
as r in the rationals with odd denominator. Let D be the least common
multiple of the denominators of x. Choose k=D or -D so that k=1 modulo
four. Then kx is integral, has A_N(kx)=0, and is congruent to r modulo four.
In particular its coordinates are odd, and (1-kx)/2 retains every binary
trace of (1-r)/2. This is an existence proof for every finite N, rather
than an extrapolation from the examples below. It gives no uniform bound,
so no infinite-word compactness conclusion follows.

The standard-library generator uses odd-pivot rational elimination. Its
separate example verifier performs only exact integer shell substitution
and trace checks; it does not call that elimination or the rank selector.
The all-length certificate separately verifies the Laurent minor and the
period-two residue word, without searching for a unit signing.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --phase-odd-rank --hole 19 --write /tmp/phase-rank.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/phase-rank.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --open-phase-odd 3 --hole 97 --write /tmp/odd-window.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/odd-window.json
```

A recorded three-centre h=97 example has 2,010 odd values, maximum absolute
value 25,912,933,113,985,897,955, and no unit values. That is a witnessed
failure to meet the actual sign restriction, not a signing or a refusal.
The h=19 example at first centre 4 also verifies. Tests regenerate all 49
all-length certificates, check denominator clearing on small independent
matrices, and reject changed dimensions, values, rank witnesses and scope.
The remaining obstacle is an actual compatible unit-sign extension, then
physical endpoint completion and unrestricted hole supports. Further bare
linear odd-integer congruences, even with these traces, cannot supply the
missing finite-interior obstruction.

Validation: all 119 spectrum tests passed, including the three new controls;
fresh command-line processes replayed the all-length certificate and both
three-centre examples. The new tests disable elimination during certificate
replay. No solver dependency was added. Whitespace checks passed.

## Hawthorn: one compatible bounded odd word for the entire interior

For **each of the 49 odd holes `h=1,3,...,97`**, the exact checker now
constructs a single period-two odd-integer word on all 402 folded labels.
Repeating that word supplies every overlapping interior window at once,
including all five endpoint-derived parity traces at every absolute level.
All 49 words have absolute values below `10^51`, a uniform bound
**independent of the window length**. This strengthens finite-window odd-integer existence: the
windows are restrictions of one compatible infinite word, rather than
separate solutions whose values might grow with their length.

This is an interior relaxation theorem. The values are not unit signs;
none of the 49 generated words has even one unit coordinate. It supplies
neither the physical endpoint shell rows nor actual subsets of a tripod.
The arbitrary-pair task and arbitrary-triple milestone remain unfinished,
and priority remains provisional. Existing period-two Boolean refusals are
consistent with this result: the unit-value condition does real work.

### Exact construction and why the finite check proves all lengths

Write A for the untouched period-two integer shell matrix and E for a
rational kernel parametrization, so `A E=0`. The implementation reuses exact
rational recovery and checks that identity against every original row. Let
Q be the largest power of two dividing any denominator in E. Thus every
coefficient of `Q E` has odd denominator. Such denominators are invertible
modulo `M=4Q`; all following modular computations use these exact inverses.
Choose integer free parameters f satisfying these linear congruences:

* For every coordinate i, `2 Q (E f)_i = 2Q (mod 4Q)`.
* For each trace with support S and required bit r,
  `Q sum_{i in S}(E f)_i = Q (|S|-2r) (mod 4Q)`.

The first congruence says that each rational coordinate of `E f` is an odd
integer in the ring of rationals with odd denominator. The second says
`sum_{i in S}(1-(E f)_i)/2 = r (mod 2)`, exactly the required trace.
A unit-pivot elimination solves these congruences over a power of two.
When no odd pivot remains, either an odd right side proves inconsistency,
or every coefficient and right side is divided by two and the modulus is
halved. Each saved pivot retains its own modulus during back substitution.
The candidate parameters are substituted into the initial congruences
before use; incompatible congruences never become a physical refusal.

All denominators of `v=E f` are now odd. Clear their common denominator with
a multiplier d chosen to satisfy `d=1 (mod 4)` (use D or -D). The integer
word `s=d v` remains odd, has `A s=0` exactly, and preserves every trace.
The portable verifier independently substitutes s into the original
periodic integer rows and traces, without using the kernel, parameters,
modular solver, or a rank claim. Exact generation and replay succeeded for
all 49 holes. This finite collection of checked integer words is the
computational lemma; there is no inference from solver infeasibility.

Finally, assign label i at absolute level k the value `s[i,k mod 2]`.
Every unwrapped interior row is precisely its corresponding periodic row
under this substitution, and every trace phase is two-periodic. Consequently
all centres, arbitrarily long windows, and their overlaps satisfy the same
original equations. The maximum of the 804 absolute word values is the
claimed length-independent bound. No limiting argument or endpoint repair
is used. An argument requiring every compatible odd interior word to grow without
bound therefore cannot work. The actual unit bound, or the missing physical
endpoint equations, must matter.

### Reproduction and observed limits

The generator and verifier use only the Python standard library:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --periodic-phase-odd --hole 97 --write /tmp/periodic-odd.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/periodic-odd.json
```

A real run returned `verified: true`, `period: 2`, and both decision flags
false in each separate process. The h=97 word has 804 coordinates, maximum
absolute value `81200807355445727931196536007292526841450371294017`, and no
unit coordinate. Across all 49 generated words the largest power Q was
`4194304` and the largest absolute value had 51 decimal digits. No generated
word data or solver dependency is added to the repository.

New controls compare the power-of-two solver to exhaustive enumeration on
small systems, replay all 49 words with the generator's two main oracles
disabled, restrict h=19 and h=97 to overlapping windows starting at levels
3, 4 and 99, and reject altered values, dimensions, periods and scope flags.
An additional direct check expands the h=19 and h=97 words onto all
4,622 retained physical columns at t=23, putting zero on old-grid vertices.
Every interior physical shell residual vanishes; 533 and 529 boundary
residuals respectively remain nonzero. This uses the original physical
column routine rather than the periodic compiler, and explicitly witnesses
why interior compatibility must not be read as a physical completion.
A kernel resource stop reports unknown and cannot emit a verified word.

Separate exploratory attempts retained the *actual* small bounds. Integer
searches for period-two odd values bounded by three at h=19 and h=97 stayed
unknown after 120 seconds each. Three-centre unwrapped odd searches with
that bound stayed unknown after 300 seconds each; an independent integer
programming engine also stayed unknown for h=97 after 120 seconds. A further h=97 three-centre run with explicit binary parity channels and
all binary echelon constraints stayed unknown after 600 seconds. These
are witnessed search limits, not lower bounds on the necessary amplitudes.

Final validation: all 122 spectrum tests passed in 394.780 seconds. The
additional original-physical-column control passed separately in 5.308
seconds; the strengthened all-49 bound and non-unit control passed in
108.944 seconds. Both fresh command-line processes verified h=97.
`py_compile` and `git diff --check` passed. Exact-kernel attempts to include
six independent endpoint levels at both ends, period two, half-length 18,
h=19 and h=97, reached 300-second resource limits and stayed unknown. No
endpoint solution or refusal is claimed from those attempts. The finished
slice is the compatible bounded odd interior theorem, not the main task.

### Integration reconciliation (Hawthorn, 25 November)

Reconciled preserved candidate `d036bbe` against accepted source `1b068be`
from common ancestor `4e6b6b9`. All six overlapping insertion points had
empty current and ancestor sides; retaining the candidate additions produces
no deletions from accepted source in any of the three owned files. No other
paths were changed. The reconciled full spectrum suite passes **123 tests
in 259.022 seconds**, including all 49 odd holes, independent direct
substitution, translated overlapping windows and original physical-column
controls. The hole-97 command-line construction also verifies; Python
compilation and whitespace checks pass. This repairs source coexistence,
not the unresolved unit-sign or physical-endpoint problem. Independent
integration and publication are not claimed here.

## Mallow: exact finite-bit searches at the unit-value boundary

25 November 2026. This attempt changes neither the resistant-family decision
nor the arbitrary-triple milestone. It tests a different solver representation,
not a further relaxation of the shell equations. No solver dependency is added
to the shipped generator or verifier.

For odd bound B=2^b-1, give each coordinate an unsigned b-bit value x and put
s=B-2x. This enumerates exactly the odd integers in [-B,B]. A shell row becomes
`sum(c*x)=B*sum(c)/2`; an odd coefficient sum immediately refuses odd values.
Choose width w with `2^w > B*sum(abs(c))/2` for every row and w>=b. Then
bit-vector equality is equivalent to integer equality: the absolute difference
between its two sides is at most B*sum(abs(c))/2, strictly less than 2^w.
Negative coefficients are reduced modulo 2^w. A trace on S becomes XOR of
the low bits of x, with right side adjusted by `|S|*(1-B)/2 modulo two`.
This retains the absolute physical trace phases, including the odd-bound case.

The following reproduces the necessary models with the already installed
Z3 4.16.0, from a Python process whose import path includes this directory.
It is an optional research experiment; a returned model must still be converted
to signs and replayed against the original integer rows. An `unsat` answer here
is not a portable refusal certificate, and `unknown` decides nothing.

```python
import z3
import resistant_spectrum as rs

def experiment(hole, centres, bound_bits, seconds):
    if centres:
        keys, rows, phases = rs.open_phase_system(hole, centres, 3)
        size = len(keys)
    else:
        size, rows, phases = rs._period_two_phase_system(hole)
    B = (1 << bound_bits)-1
    w = max(bound_bits, max((B*sum(abs(c) for c in row.values())//2).bit_length()
                           for row in rows))
    x = [z3.BitVec('x'+str(i), bound_bits) for i in range(size)]
    solver = z3.SolverFor('QF_BV')
    solver.set(timeout=1000*seconds)
    for row in rows:
        assert sum(row.values()) % 2 == 0
        lhs = sum((c*z3.ZeroExt(w-bound_bits, x[i]) for i,c in row.items()),
                  z3.BitVecVal(0,w))
        solver.add(lhs == z3.BitVecVal(B*sum(row.values())//2,w))
    for mask,rhs in phases:
        lhs = z3.BitVecVal(mask.bit_count()*((1-B)//2)%2,1)
        for i in range(size):
            if mask>>i&1:
                lhs ^= z3.Extract(0,0,x[i])
        solver.add(lhs == rhs)
    return solver, x
```

The three-centre unit run additionally imposed the complete reduced binary
basis of the integer rows and traces; its encoding was otherwise the same.
The period-two bound-three run used just the original rows and traces.
Independent instantiated bit-vector evaluation agreed with exact integer
substitution on 904 exhaustive small assignments (signed coefficients),
including all eight trace masks per assignment and both bounds. Both recorded
h=19 and h=97 two-centre unit witnesses also passed every encoded row and
the existing independent integer verifier. No solver result was used as an
oracle for these controls.

The three-centre unit bit-vector run (h=97, 2,010 variables, 1,068 integer
rows, five-bit sums) returned unknown/timeout after 300.149 seconds.
The period-two bound-three run (h=97, 804 two-bit coordinates, seven-bit
sums) returned unknown/timeout after 600.513 seconds. Neither supplies a
word, a lower amplitude bound, or a contradiction. The code above uses the tighter difference bound (three and four bits
respectively); the first recorded runs used the conservative widths just
listed, which change no satisfying assignments.

A second exact unit encoding replaces each negative-weight Boolean term
`c*x` by `abs(c)*(1-x)-abs(c)`, then uses weighted Boolean equality with
target `sum(c)/2 + sum(abs(c) for c<0)`. Its independent controls passed
320 exhaustive small assignments and all 712 integer rows of the recorded
h=97 two-centre witness. This is an arithmetic control, not evidence of
three-centre compatibility.
The direct Boolean-cardinality run used QF_FD, all original trace phases,
and the 12 reduced binary consequences having at most six coordinates.
It returned unknown/timeout after 900.074 seconds. The tighter three-bit
encoding separately passed the same 904 exhaustive assignments and all
712 rows of each recorded two-centre witness before its new search.
Three bits are also necessary for this row-wise encoding at h=97: in row
zero of the three-centre window, set x=1 at coordinates 976,986,1775,2005
and zero at the other six coordinates. The true shell residual is 8;
the transformed equality falsely passes modulo four and fails modulo eight.
This is a single-row overflow control, not a model of the complete system.
The three-bit h=97 three-centre run returned unknown/timeout after 600.211
seconds, with the same complete reduced binary consequences as the five-bit
run. Reducing the representation therefore did not produce a new word at
this cap; no performance ordering between the engines is established.
Finally, installed CP-SAT used the original integer rows, the 15 original
traces and 30 reduced binary consequences of width at most 32, encoded as
`sum(bits)=2*k+rhs`. The recorded h=97 two-centre word supplied hints for
its four levels, with repair enabled and a hint-conflict cap of 100,000;
no hint was a fixed sign. One worker, a 1,200-second cap, returned UNKNOWN
after 1200.012 seconds (3,590 branches, zero reported conflicts). No extended
word was emitted. This is a witnessed failure of the hinted attempt, not
proof that the recorded word, or every two-centre word, cannot be repaired.

All five searches remained unknown. The next useful advance requires a new
compatible unit-sign extension or a replayable obstruction, followed by the
physical endpoints and unrestricted supports. These experiments do not justify
repeating the same caps or marking the main task complete. Only this concise
record changes; the existing generator, tests and milestone status are unchanged.


## Rook: direct sign repair does not yet extend the open window

25 November 2026. A different constructive attempt worked directly on the
2,010 unit signs of the h=97 three-centre window (first centre 3), with
1,068 untouched integer shell rows and 15 absolute trace equations. For
bits x, its unweighted repair cost was the sum of squared shell residuals
divided by four, plus the number of failed traces. Thus zero, and only
zero, would pass the local equations. This still omits physical endpoints.

The scratch search chose a violated row, scored its incident single-bit
flips with positive adaptive row weights, occasionally chose a random
incident flip, and increased weights when no improving flip was available.
It restarted after 200,000 iterations. All 8,240 incident flip updates on
the independently verified two-centre h=97 word agreed with direct exact
integer and trace recomputation. This checks the incremental arithmetic,
not search completeness.

Two seeds each ran to a 600-second cap without a zero-cost word. Their
best costs were 100 and 97 after 264,660,000 and 291,940,000 iterations,
respectively. These are search observations, not lower bounds.

A full three-centre assignment from this attempt, failing 117 shell rows
and two traces, was passed as a changeable hint to installed CP-SAT. With
all original equations and reduced binary consequences of width at most
32, one worker and hint repair enabled, it returned UNKNOWN after 240.006
seconds (3,590 branches, no reported conflicts). It emitted no word.
This is a failed constructive attempt, not an obstruction or a comparison
of solver performance. Scratch assignments and search logs are not added
to Git. The acceptance result remains unmet: find a compatible exact
unit-sign extension, then satisfy physical endpoints and unrestricted
hole supports. Repeating this cap is not the next mathematical step.

## Rook: forced opposite tails for every moving hole

25 November 2026. The exact radius-one reduction now covers **every**
`1<=h<=98`, rather than only `h<=42`. This is a representation theorem
on the named support `(1,ht),(1,99t)`, not a construction, an obstruction,
or the task's acceptance result. The arbitrary-pair milestone stays open.

For `43<=h<=98`, odd `t=2L+1>=9`, put `E=(h+79)t+1`.
Above E the only nonzero physical shell columns are

    -x_(e-79t-1) - y_(e-99t),       E<e<=178t.

To check the cutoff directly in the displayed physical columns, all
third-arm terms are at most `max(122t,(h+23)t+1)`, first-arm hole terms
at most `max(h,99-h)t+1`, and second-arm hole terms at most E.
All are at most E. The first-arm/23t cross terms end at 122t;
only the first-arm/79t and second-arm/99t cross terms remain above E.
The long-tip vertices are holes or cancel against their endpoint terms.
Thus every literal solution necessarily has

    x_(d+20t-1) = -y_d,       (h-20)t+2<=d<=79t.

This removes exactly `(99-h)t-1` first-arm signs, at depths
`ht+1..99t-1`. Keep first-arm depths `1..ht-1` and both other arms.
At the immediately preceding row, e=E, the first-arm coordinate would be
**the hole ht**. That row instead says

    y_((h-20)t+1) = y_(79t).

The exceptional second-arm sign is retained, and its unchanged row stays
in the reduced left boundary system. Pairing it with a first-arm sign
would silently invent a vertex at the hole. It must not be substituted.
For h<=42 the earlier 56t-pair argument and reduction are unchanged.

For all h, substitute the removed first-arm sign into each corresponding
second-arm column, `C_2(d)-C_1(d+20t-1)`. Every affine shift is still -1,
0 or 1. Therefore the complete reduced strip has the same left levels
0,1, interior centres `2..L-1`, right level L, and **L-2** appended edges.
Its slice width is `2(max(43,h)+102)` signs. Deep holes have `(h+102)t`
retained sources including the centre, rather than the shallow case's
`145t-1`. The graph-state bound is `2^(4(max(43,h)+102))`; for example
h=43 uses 580 stored signs, h=97 uses 796, and h=98 uses 800.
These bounds do not enumerate a graph or decide its accepted lengths.

The existing audit command now accepts reduced mode for all holes:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --moving-strip-audit 9 --moving-reduced --hole 97
```

New tests compare **every coefficient of every reduced physical column**
for all 98 holes at t=9. Separate t=9,11,15 deep-hole controls reconstruct
all high rows, check the exceptional row, and compare complete restored
random-sign shell residuals at h=43,44,97,98. In particular they check the
boundary h=43 and the almost-empty tail h=98; no sign is assigned to a hole.

### A common smaller core, with explicit nonlinear sign conditions

There is a stronger exact elimination if unit conditions are kept separately.
For all h, every original row with `122t<e<=178t` is

    -x_(e-79t-1) - y_(e-99t) + y_(e-ht-1) - y_(e-ht) = 0,

where out-of-arm y coordinates and the missing x coordinate are omitted.
The same cutoff bounds above prove that these are the entire high rows.
Thus, for `43t<=a<=99t-1`, `a!=ht`, recover

    x_a = -y_(a-20t+1) + y_(a+(79-h)t) - y_(a+(79-h)t+1).

The only high row without a recovered x is the exceptional equality already
stated. This leaves a common first-arm core `1..43t-1` for **all** holes.
Unlike the opposite-tail substitution, this requires extra unit conditions:
for `a<ht`, all three y coordinates exist, and `-A+B-C` is a sign exactly
when `A=B or C=B`. Its only forbidden patterns are `A=C=-B`, which would
restore a value of magnitude three. For `a>ht`, the last two terms are
outside the arm, so the restored sign is automatically `-A`.

Consequently the full physical problem is exactly equivalent to: choose
signs on the centre, first-arm core and both other arms; satisfy all original
low shell rows after this linear recovery; impose the exceptional equality
when present; and exclude those two three-sign patterns at every removed
coordinate below the hole. Forward implication follows from the high rows;
reverse implication follows by substitution into every original row and the
explicit unit conditions. Balance, if separately required, is evaluated on
the restored full word. This equivalence does not solve its smaller core.
It retains `145t-1` sources for h<=42, or `145t` for h>=43, before the
additional constraints; it makes no radius-one claim for this stronger model.

`moving_high_arm_relations(t,h)` returns every integer recovery expression
and the exceptional high row. Its new test independently reconstructs every
original high coefficient for all 98 holes at t=9, checks the exact number
of removed coordinates, and exhausts all eight three-sign assignments.
The preceding radius-one change passed all 125 existing/new tests; the
additional recovery test passed separately after this additive helper.

The broader three-centre experiment used the untouched 1,068 shell rows,
15 traces, and reduced binary consequences of width at most 32. Installed
CP-SAT, one worker, presolve disabled, returned UNKNOWN at 120 seconds each
for h=1,49,3,47,95,25 (18,162; 18,147; 18,047; 28,542; 19,126; 24,725
branches respectively). No candidate was emitted. This is a witnessed
failed search, not a lower bound or a reason to repeat those caps.

### A positive three-centre window at h=43

The reduced representation did find a new local signing. At h=43, centres
3,4,5 admit **2,010 original unit signs**, satisfying all 1,068 untouched
integer shell rows and all 15 absolute parity traces. Translation by two
supplies the same local witness at every odd first centre >=3, for
`L>=first+4`. It is not an extension of the earlier h=19/97 words and
makes no assertion at an even first centre for h=43.

The research model substituted the forced opposite tails, leaving 1,562
variables, 732 nonzero integer rows and the mapped traces. Before search,
its entire row set was compared with the transformed original rows and
eight random assignments checked the trace transformation. Installed
CP-SAT, one worker, symmetry detection disabled, used exact allowed-sign
row tables and returned a candidate in 6.571 seconds (1,658,024 branches,
25,988 conflicts). The original integer verifier then accepted the full
2,010-sign word. Replay uses only the standard library, not that solver:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --open-phase-example --hole 43 --write /tmp/three-centres.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/three-centres.json
```

The recorded example is embedded in the existing generator. Focused tests
check all its original rows and traces at starts 3 and 11, reject unsupported
even starts and a changed active sign, and compare all coefficients with
physical shell columns at the advertised minimum half-length. Separate
command-line generation and replay both report verified=true with both
existence-decision flags false. Physical endpoints, arbitrary hole supports,
and a compatible arbitrarily long word remain unresolved.

The stored three-centre word cannot be extended with its supplied signs
fixed: 178 shell rows at the next centre use only already supplied signs,
and 74 of those are nonzero. A regression test preserves this failure.
A longer compatible word must therefore change some signs; the local
positive result does not certify an extendible boundary state.

The full endpoint compiler now also exposes the proved opposite-tail mode:
`compile_moving_folded(L,p,w,h,reduced=True)`. It keeps the physical left
and right rows as well as periodic interior representatives. Independent
complete-column tests cover h=1,19,42,43,44,97,98 at L=14,p=4,w=2, compare
extension by a whole period, and compare that entire equation system with
L=3990. This does not apply the stronger three-term recovery, whose extra
unit conditions must not be lost. The default unreduced compiler and the
existing command-line search keep their previous behavior.

At h=43 the existing period-two proof engine also produced a scoped refusal
in 60.639 seconds; a separate command-line process replayed it successfully:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --period-two-phase-refusal --hole 43 --seconds 300 --cubic-pivots 40000 --write /tmp/h43-period-two.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/h43-period-two.json
```

This excludes only period-two interiors carrying the physical endpoint
phases, not the new three-centre word or unrestricted words. The generated
certificate stays outside Git. Two further exact-table, one-worker h=43
searches ended UNKNOWN at 600 seconds each: four unwrapped centres
(1,852 reduced variables, 976 integer rows; 14,081,815 branches,
1,479,919 conflicts), and a period-four interior (1,160 reduced variables,
976 integer rows; 11,356,650 branches, 1,913,297 conflicts). Both retained
the physical parity traces. Neither emitted a candidate or a refusal.

Finally the h=43 reduced full endpoint system at L=3990,p=4,w=2 had
2,755 signs and 2,807 integer rows (maximum width ten). Exact allowed-sign
row tables, one worker and normalized centre sign returned UNKNOWN after
600.010 seconds, 13,674,806 branches and 1,508,974 conflicts. No full word
was emitted. The complete physical-column and whole-period checks above
validate the equations, not feasibility. Acceptance remains unmet. The next
mathematical obstacle is a compatible overlapping unit-sign extension with
both physical endpoints, or an unrestricted obstruction; the three-term
recovery exposes a smaller core and its exact extra sign restrictions.
Repeating these recorded solver caps is not a demonstrated next step.

## Tern: one-slice transfer states, with both endpoint interfaces

25 November 2026. **Acceptance remains unmet; priority stays provisional.**
Rook's inspected continuation was recovered in private commit `523d097`,
not inferred from the stale room's earlier failed searches. The new work
below does not decide any accepted path length or arbitrary hole support.

### The unreduced strip needs one slice of memory, not two

For every `1<=h<=98`, each **unreduced** interior shell stencil has offsets
exactly `{-1,0}` or `{0,1}`. This follows directly from the physical column
form: an interior exponent is `Q*t+u*r+c`, with `c` zero or one. A row
at `Q*t+u*r` therefore uses only source levels `r` and `r-u`. In particular
no unreduced row uses all three levels `r-1,r,r+1`. This is stronger than
merely bounding the radius by one. Opposite-tail substitution can destroy
this property, so it must not silently be applied to the new graph.

Let `P` be the 178 stencils with offsets `{-1,0}`, and `F` the 178 with
`{0,1}`. Define a transition from a 402-sign slice U to another slice V by
all P rows centred at the level of V and all F rows centred at the level
of U. These are 356 original integer equations on the two slices. A
vertex of the graph stores **one** 402-sign slice, so the unphased graph
has at most `2^402` vertices, rather than the earlier `2^804` bound.
No graph has been enumerated. This finite reduction is not the acceptance
result.

Here are the exact endpoint conventions, for `t=2L+1>=9`:

* Prefix: all physical left rows, and P centred at 2. Quantify the 200
  retained old-grid signs and slice 1, leaving slice 2 as the initial state.
* Core: transitions from slice j to j+1 for `j=2..L-2`.
* Suffix: F centred at L-1, and all physical right rows. Quantify slice L,
  leaving slice L-1 as the terminal state.

Thus the core has exactly **L-3 edges**. Every P centre `2..L-1` occurs
once: centre 2 is in the prefix and the rest in the core. Every F centre
`2..L-1` occurs once: centre L-1 is in the suffix and the rest in the core.
The physical left and right rows are also retained once. This partition
proves equivalence to the complete shell system on the named support,
including the shortest allowed scale t=9. `adjacent_transfer_blocks(h)`
returns these three constant-size prototypes in original literal coordinates.
It never substitutes an absent hole vertex or identifies two levels.

Balance remains a separate necessary condition for the target pair. It can
be carried as an integer path weight: prefix weight is the sum of its 200
old-grid signs and its slices 1 and 2; each core edge adds the sum of its
new slice; the suffix adds slice L. Their total is the full signed word
sum, which must be zero. Therefore unweighted reachability alone must not
be reported as a balanced physical pair.

The five endpoint-derived traces can optionally prune each edge. All five
use two levels with offsets `{-1,0}`. On edge j to j+1 their right sides
are `(j mod 2,j mod 2,(j+1) mod 2,(j+1) mod 2,0)`. The phased graph has
at most `2^403` vertices if this parity is included in the state; the
unphased `2^402` bound concerns integer shells alone. Physical endpoints
force the absolute phase; it is not a selectable free phase.

### Saturate a local window before treating it as a path

`adjacent_phase_system(h,n,f)` includes **every** original interior row
whose support lies in levels `f..f+n-1`, and every contained absolute
trace, for `f>=2`. It has `402n` literal signs, `356(n-1)` integer rows,
and `5(n-1)` traces. The old open-centre window retains only rows at its
listed centres; its outside levels do not yet satisfy all contained rows.
That distinction explains why an open witness cannot simply be assumed to
supply an extendible boundary state.

The recorded h=43 three-centre word restricts to three consecutive states
(two compatible transitions) at levels 3,4,5. This is the **same** recorded
word, not a newly found extension. Repackage it and independently replay
all its integer rows and traces, using only the standard library:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-phase-example --hole 43 --write /tmp/adjacent-word.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/adjacent-word.json
```

Both actual commands returned `verified: true`, `levels: 3`, and both
existence-decision flags false. The checker rejects an altered active sign,
wrong dimensions, wrong minimum half-length, shifted phase and scope flags.
`--adjacent-phase-window N --first-level F` exposes a bounded standard-library
search of this stronger local system; a limit is unknown, never refusal.
A two-level h=43 run stopped unknown at its 100,000-node cap in 8.057 seconds,
despite the independently known positive path. This is a control against
mistaking search failure for impossibility.

The tests compare the **entire** prefix/core/suffix matrix with independent
physical shell columns at (t,h)=(9,1),(9,43),(11,19),(11,97),(15,98), including
all retained vertices and row multiplicities. They check the two-level row
support for every one of the 98 holes, and compare the saturated rows and
traces with all contained rows in a larger open window. These controls do
not audit an infinite construction: none has been produced.

### An integral one-step driver, not a unit-sign construction

There is a further exact result for **each h=24..98**. On one transition,
write s for the previous 402 coordinates, v for the next third arm's 46
coordinates, and x for the next first/second arms' 356 coordinates. The
356 original rows have the form

    B_h x + A_h s + C_h v = 0.

`B_h` is unimodular. The new generator proves this by explicit **integer
original-row combinations**, one for each target coordinate, giving

    x_i = sum_j D_(i,j) (s,v)_j.

The independent checker forms every claimed weighted sum of the untouched
original rows and requires its target block to be the corresponding unit
vector. Thus its integer weight matrix W satisfies W*B_h=I, proving
unimodularity and uniqueness. It also substitutes all 356 recovery formulas
back into every original row, checking the converse without redoing the
elimination. There are 448 free original coordinates, precisely s and v;
none is a new linear combination masquerading as a literal sign.
All 356 coefficient sums are odd. Consequently **any** odd integer initial
slice and **any** sequence of odd integer third-arm controls extend uniquely
to an odd integer interior word. This claim is independent of L, by the
transition partition. It includes neither physical endpoints nor unit bounds.

This is a finite, exact certificate for each of 75 possible h values, not
an extrapolation from sampled h or sampled scales. The all-75 test regenerates
and checks every identity. No assertion about the exceptional h=23 or an
integral recurrence at h<=22 is made. For h=43, all formulas have at most
47 terms and coefficients of magnitude at most four; 112 are single signed
copies. Of the remaining formulas, 119 depend only on the previous slice,
and 125 depend on its values and the next third arm. The 119 fixed forms
already give necessary unit conditions on every state with a successor.

Generate and replay one certificate, standard library only:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-driver --hole 43 --write /tmp/integral-driver.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/integral-driver.json
```

Both actual commands reported `verified: true`, 448 inputs and 356 recovered
coordinates, with both existence-decision flags false. The certificate is
regenerated outside Git. `adjacent_driver_step(certificate,previous,third)`
evaluates the recurrence and deliberately returns nonunit values rather than
silently clipping them or claiming a signing.

The endpoint phase laws also simplify under this recurrence. For odd values
write s_i=1-2b_i. A recovered coordinate gives the exact integer formula

    b_i = (1-sum_j D_(i,j))/2 + sum_j D_(i,j)*b_j.

Pull each of the five trace equations back through these formulas modulo
two. All next-third-arm terms cancel: each becomes a parity observable of
**one previous state**. Pulling the same observable on the next state back
again gives itself plus drift `(1,1,1,1,0)`, independent of the controls.
`adjacent_driver_phase_laws` checks these polynomial identities directly;
the all-75 test checks all five cancellations and drifts at every h=24..98.
At h=43 these five single-state masks have rank five and required values
`(1,0,1,0,1)` on an even level. Odd levels reverse the first four values.
Thus only the initial five phase conditions need be imposed in a recurrence
search: exact evolution preserves every later absolute trace. At this hole,
the phase-admissible state bound improves further to `2^397` per level
parity, or `2^398` with both parities included. This does not enumerate those
states or decide their unit-compatible transitions.

The actual recorded unit word is reconstructed exactly from its slice at
level 3 and third-arm slice at level 4. In contrast, keeping that same
phase-correct unit initial slice and choosing all 46 next third-arm signs
positive yields **49 nonunit outputs**, first `(arm=1,q=1,s=+1)` with value
3, and maximum magnitude seven. The untouched integer rows still hold.
This explicit failure shows why integral, odd and phase-correct evolution
is not the missing unit construction. Random odd controls over eight steps
also retain all original integer rows and every absolute trace, while
producing nonunit values. Damaged coefficient identities and omitted or
duplicated recoveries are rejected.

The recurrence also strengthens the recorded word's extension failure.
Its fully constrained last middle slice (level 5) has **55** next first/second
arm values forced to be nonunit **regardless of all 46 next-third-arm
choices**. This is stronger than freezing the old outside level 6. The first
failure is next `(arm=1,q=45,s=+1)=-3`. In the canonical two-level system,
its recovery is the sum of original rows 10,163,164,269,353 with weights
-1,-1,+1,+1,+1; its 13 input terms all belong to the previous slice.
The new test evaluates them on the stored level-5 word. Thus that state
cannot be repaired by any next control, at any sufficiently large L.
This is a fixed-state refusal only: another unit state may have a successor.

### Reverse the interior without assuming reversible physical endpoints

Put `G(a,q,s)=(a,q+s,-s)`, swapping the two orientations within each old
edge. G is an involution of the 402 labels. For every h=1..98, the complete
transition row multiset is unchanged, up to multiplying equations by -1,
under `(U,V) -> (G V,G U)`. `adjacent_time_reversal(h)` checks this exact
integer permutation with row multiplicities; all 98 checks passed. Hence
T(U,V) holds if and only if T(G V,G U) holds. This is an **interior**
symmetry; the physical endpoint predicates have not been identified.

For h=24..98, the same certified forward driver therefore recovers a
predecessor: apply it to G of the current state and G of a proposed previous
third arm, then apply G to its output. `adjacent_driver_predecessor` does
this and reproduces the actual stored transition from slice 3 to slice 4.
For the recorded h=43 slice 3, it also proves **43 forced nonunit
predecessor values**, regardless of all previous third-arm choices; one
is `(arm=1,q=45,s=-1)=3`. Combined with the 55 forced successor failures
at slice 5, this known two-edge path is blocked at both ends even after
freeing every outside sign. It is not evidence that every path is blocked.

At h=43, G swaps phase masks 0 and 1, swaps 2 and 3, and fixes 4.
The paired masks have opposite prescribed values; every mask has even
cardinality. Thus no phase-correct unit state can satisfy G U=U or G U=-U:
in either case its first two observables would be equal. This is a direct
parity proof, not failed search. It rules out folding a construction about
a single state, while leaving folds about an edge open.

We tested the four-state cycle
`A,B,G B,G A`. By reversibility its four edges require just
T(A,B), T(B,G B), T(G A,A); the fourth is automatic. Give A the even
phase and B the odd phase: G supplies the correct phases of the other two.
This differs from imposing a sign reversal after two levels. The exact
period-four shell model with these identifications has 580 signs after
forced copies, 976 integer rows and all 20 original trace equations.
It was a construction ansatz, not a constructed cycle; its bounded outcomes follow below.

### Bounded constructive attempts and the exact remaining obstacle

Discovery used already-installed CP-SAT, one worker; the shipped generator
and all identity checkers remain standard-library-only. These different
models/phases do not establish a solver performance ordering.

* Four consecutive states starting at level 2, with exact row tables and
  reduced binary consequences: UNKNOWN after 1198.685 seconds,
  18,932,849 branches and 2,719,113 conflicts. It has 1,272 signs after
  forced copies, 732 integer rows and all 15 absolute traces.
* Three consecutive states starting at level 2, adding all one-step recovery
  equalities and imposing the five initial single-state phases: UNKNOWN
  after 300.044 seconds, 16,280 branches and no reported conflicts. It
  has 982 signs after copies and 488 original integer rows. Its middle
  state would be an odd-level state with both a predecessor and successor;
  the known three-state word instead has an even middle level.
* The mirror period-four ansatz above: the solver reported INFEASIBLE
  after 60.908 seconds, 1,917,846 branches and 165,752 conflicts. This is
  recorded as a solver report, **not a portable obstruction certificate**.
  The existing Boolean cubic identity engine reduced its 94 binary
  parameters to 93 but stopped unknown at 20,000 pivots (30.386 seconds).
  A 40,000-pivot extraction also stopped unknown, with 93 parameters,
  after 182.446 seconds. No contradictory identity was produced. Its
  necessary dyadic equations for b in s=1-2b were compatible at every
  tested modulus four through 256; those checks prove no exact odd
  solution or unit solution.

The earlier complete 129-test suite passed in 315.932 seconds before the
three additional driver tests. All six adjacent/driver tests then passed
in 76.083 seconds, including every integral driver and phase law for all
75 holes and every reversal for all 98 holes. The final focused trajectory
test also passed after adding the two-end dead-state and phase-reflection
controls. Separate command-line generation and replay of the actual local
word and of the h=43 integral-driver identities passed.

No new physical pair, indefinitely extendible unit word, or all-pairs bound
has been obtained. A next constructive step must choose third-arm controls
so **all** recovered values stay unit indefinitely, with balance and both
physical endpoints, or replace that step by a rigorous unrestricted
obstruction. The recurrence proves that integrality, oddness and phase
propagation alone will not settle it. Do not freeze the recorded path's
middle endpoints or repeat these same caps as though they were fresh work.

The four-state driver model starting at level 3, with all 1,068 recovery
rows in addition to the 732 original nonzero rows after copies and the
five initial phase conditions, also ended UNKNOWN after 1200.048 seconds
(15,654 branches, no reported conflicts). Its outside signs were changeable
hints from the recorded word, not fixed assumptions.

### A bounded drift forces every long core slice to be balanced

There is a stronger necessary condition for **every odd h=25..97**, not
just a restriction on the stored word. Let S_r be the sum of all 402 signs
in folded slice r. Exact substitution in the one-step recovery gives

    S_(r+1) = S_r = S.

Define g_r as a weighted sum of that slice, with the following integer
weights on labels (arm,q,orientation). Unlisted parity cases have weight zero.

| Arm | Orientation | Range | Weight |
| --- | --- | --- | --- |
| 1 | + | q<h, q odd | -2 |
| 1 | + | q>=h | (-1)^q |
| 1 | - | q<=h, q odd | +2 |
| 1 | - | q>h | -(-1)^q |
| 2 or 3 | + | q even | +2 |
| 2 or 3 | - | q even | -2 |

The sum of absolute weights is exactly 402. Pulling this linear form
through two consecutive certified recoveries gives the exact identity

    g_(r+2) - g_r = -2 S.

`adjacent_balance_drift` checks both identities by direct integer
coefficient substitution, including cancellation of every third-arm
control. It does not trust the exploratory control-space calculation
that suggested them. Its new test regenerates the identities for **all
37 odd holes** in the stated range.

**Bound.** On a unit path, |g_r|<=402 and S is even. In 405 consecutive
states there are 202 two-step advances from the first state, so
`|404 S|<=804`. A nonzero even S would make the left side at least 808.
Therefore **every unit path with at least 405 states has S=0**. This also
excludes every nonzero-S component from containing a cycle.

For a resistant scale, L=3990m with m>=1. The full physical core has L-2
states, at least 3988, so every one of its slices 2..L-1 must contain
exactly 201 signs of each kind, for these 37 named moving-hole supports.
The old-grid signs and the outer slices 1,L still obey their physical
endpoint equations and the overall balance condition; they are not covered
by this assertion. No other two-hole support has been excluded.

The recorded h=43 middle slices 3,4,5 each have S=-8. More generally no
word in their conserved-sum component can be extended indefinitely as
unit signs, even apart from their particular two dead-end states. A random
odd-control trajectory verifies both exact identities while retaining S=-8
and producing nonunit values; the bound requires actual unit signs.

The next construction search must therefore work in the **S=0 component**.
A new three-state, first-level-2 search imposes that necessary condition
alongside the original rows and all ten phase traces. This condition was
not assumed for the preceding short-window searches and is not inferred
from their failures. It still does not decide an infinite balanced path,
either physical endpoint, or the all-pairs milestone.

The same `--adjacent-driver --hole 43` generation and `--verify` replay
commands above now also check the balance-drift identities and report
`long_core_zero_sum_after_states: 405`. The all-37 drift test passed in
19.930 seconds. This is a necessary condition on the named supports, not
an upper bound excluding their zero-sum component.

### An actual balanced two-edge path, in both starting parities

The new balanced three-state search returned a candidate in **2.656 seconds**
(614,199 branches and 7,464 conflicts). Direct substitution accepted all
712 original integer rows, all ten absolute phase traces, every unit sign,
and zero sum in each of the three states. It uses 1,206 original signs;
the discovery model had 982 after necessary signed copies. This is a new
finite witness, not a completed resistant pair.

The stored path begins at level 2. Reversing it with G supplies a valid path
at odd starting levels; translation by two supplies every other start of
the same parity. The generator rebuilds and checks all requested equations
at **every** requested start rather than trusting either transformation:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-balanced-example --hole 43 --first-level 2 --write /tmp/balanced-path.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/balanced-path.json
```

Both actual commands reported `verified: true` and `slice_sums: [0,0,0]`,
with both existence-decision flags false. Tests cover starts 2,3,4,11,
reject a false balance claim on the old unbalanced word, and compare the
complete physical matrix at the new minimum half-length L=5, t=11.

This particular balanced path is also a dead end at both boundaries:
its initial state forces 43 nonunit predecessor coordinates, and its last
state forces 47 nonunit successor coordinates, independently of all outer
third-arm choices. Tests keep both failures. Its odd middle state does
have a unit predecessor and successor, disproving the possible local
odd-phase obstruction suggested by the earlier timeouts. The reversed
word likewise supplies an even middle state. Neither fact asserts that
these two-edge paths can be joined together.

The subsequent **balanced four-state** search retained the original 1,068
integer rows, all 15 traces and the necessary zero slice sum, with 1,272
signs after copies. It ended UNKNOWN after 181.072 seconds (8,410,067
branches and 695,610 conflicts). No longer word or obstruction was emitted.
This run leaves a checked balanced two-edge witness and the exact zero-sum
core reduction; it does not decide whether even three consecutive compatible
core edges exist, much less join the physical endpoints. Acceptance and the
arbitrary-triple milestone remain unmet.

Final verification: all eight adjacent/driver/balance tests passed together
in 82.252 seconds after the last changes. Regenerate these checks with
`python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -k adjacent -v`.
The actual balanced-example and integral-driver command-line generation and
separate verification commands above also passed; `git diff --check` is clean.

### Independent conflict recovery (Mica, 25 November)

Recovered the missing continuation from fixed-channel inspection of contribution
`277aaf335ce4f74c077965f9d4a5d86d2a0be9ae`, against shared source `5180629`.
The three complete per-path diffs reconstructed against their recorded base;
only the missing adjacent-state work was added. The current endpoint compiler,
high-arm recovery, folded stencils and open witness functions remain unchanged.
Eight focused adjacent-state tests passed in 70.798 seconds, including all 75
driver holes, all 37 drift holes, complete physical-column comparisons and
corruption rejection. The existing full endpoint compiler comparison passed
separately. Balanced-example and integral-driver generation and separate replay
both passed using the standard library. These checks recover the continuation;
they do not establish the infinite-family acceptance result. Next work remains
a compatible zero-sum unit-control path with both physical endpoints, or an
unrestricted obstruction. Independent integration of this repaired source is
still required before treating it as shared source.

### Aster: a conserved moment that the physical right end forces to zero

For every driver hole `24 <= h <= 98`, define coefficients on a slice's
original labels `(a,q,s)`. Put

    C_1=h-101, C_2=123-h, C_3=179-h.
    w(a,q,+)=C_a-q;  w(a,q,-)=-C_a-1+q.

On arm 1 only, add 201 to the positive-orientation coefficient when
`q >= h`, and subtract 201 from the negative-orientation coefficient when
`q > h`. Write `W_r = sum w(a,q,s) x(a,q,s,r)`.

**Necessary condition:** every complete physical signing in this folded
support has `W_r=0` throughout its transfer path, not merely a constant
unspecified moment. This does not impose a periodic word or freeze a third
arm. The reasoning has two separately checked parts:

1. Substitute the certified one-step recovery into `W_(r+1)`. All 46 new
   third-arm coefficients cancel, and the remaining coefficients are
   exactly those of `W_r`. `adjacent_conserved_observables` checks this
   equality of integer coefficient dictionaries, not a numerical spectrum.
2. The incoming moment of the physical suffix is a rational linear
   combination of its original shell rows. `adjacent_right_moment_identity`
   supplies this combination; its separate verifier simply sums the original
   rows and compares every coefficient. Therefore the physical suffix
   forces `W_(L-1)=0`. Conservation propagates it back to slice 2.

There is a companion left-end identity: the original prefix rows imply
`S_2 + 2 W_2 = 0`, where `S` is the ordinary slice sum. The certificate's
`prefix_balance_weights` are checked by a second direct row summation.
Ordinary slice sum is also conserved by the driver at every hole 24..98.
Consequently every complete signing in this support has **both `S=0` and
`W=0` on every transfer slice**, at every admitted length. For complete
physical signings this removes the earlier requirement of 405 states and
extends the balance conclusion to even holes. The earlier 405-state theorem
still applies to sufficiently long *free-end* paths without using endpoints.

The discovered endpoint combinations simplify to explicit integer weights
on the existing stencil row labels. No elimination is needed to generate
or check a certificate:

| Identity | Original row | Weight |
|---|---|---|
| suffix `W` | transition row `(Q,u)` with offsets `{0,1}` | `101-Q` |
| suffix `W` | right-boundary row `(Q,u)` | `101-Q-[u=1]` |
| prefix `S+2W` | left-boundary row `(Q,c)` | `2Q-201` |
| prefix `S+2W` | transition row `(Q,u)` with offsets `{-1,0}` | `2Q-201` |
| prefix `A`, odd h only | left-boundary row `(Q,c)` | `(-1)^(Q+c)` |
| prefix `A`, odd h only | transition row `(Q,u)` with offsets `{-1,0}` | `(-1)^Q` |

`adjacent_endpoint_row_weights` encodes these weights in the exact original
row order. Each claimed identity is proved by summing its original rows,
including all boundary coordinates, and comparing with the stated single
slice observable. All 75 driver holes and all 37 odd-hole alternating
identities are finite, independently replayable checks.

The convention is the existing complete-matrix decomposition: prefix
slices 1,2, transitions `j -> j+1` for `2 <= j < L-1`, and suffix slices
`L-1,L`, hence `L-3` path edges. This statement concerns that decomposition
at `L >= 4`, with both holes on arm 1 at `ht` and `99t`, `t=2L+1`.
It is not an unrestricted theorem about all placements of two holes.

At h=43 the witness has 531 nonzero original-row weights, all integers of
absolute value at most 100. Generate and independently replay it with:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-right-moment --hole 43 --write /tmp/right-moment.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/right-moment.json
```

The stored balanced three-state word has moments `[-128,-128,-128]`.
Thus it cannot occur anywhere in a complete right-end-compatible signing,
even if arbitrarily many exterior levels could be supplied. Its zero
ordinary slice sums alone did not reveal this failure. At odd holes only,
the additional coefficients `s*(-1)^q` give a sum `A` that changes sign each
step; the stored word has `[-8,8,-8]`. Another original-prefix row identity
forces `A_2=0`, so **every complete signing at odd driver holes also has
`A_r=0` throughout its path**. The certificate's optional
`alternating_prefix_weights` records this identity. The same alternating law
failed at even h=24 and is explicitly not claimed there.

The shipped standard-library window search can impose the necessary
conditions with `--balanced-slices --zero-moment-slices` and, at odd holes,
`--zero-alternating-slices`. Certificate replay
rechecks any asserted zero moment directly on every original slice.
`adjacent_unit_boundary_obstructions` separately reports nonunit recovered
coordinates independent of every outside third-arm choice. Nonempty output
proves a particular state's dead boundary; an empty output does not establish
an extension.

Bounded discovery used the already-installed CP-SAT with one worker,
unrestricted original signs merged only by certified binary copy relations,
all original rows, all absolute phase traces, and zero ordinary slice sums.
Complement symmetry was fixed at one sign; every trace has even size.
All runs below returned **UNKNOWN**, not a refused window:

| h | States | Additional condition | Seconds | Branches | Conflicts |
|---|---:|---|---:|---:|---:|
| 25 | 4 | none | 180.008 | 14,932 | 3,653 |
| 61 | 4 | none | 179.999 | 15,326 | 3,113 |
| 97 | 4 | none | 180.001 | 15,667 | 1,912 |
| 43 | 4 | zero conserved moment on every slice | 180.000 | 14,675 | 3,185 |
| 43 | 3 | zero conserved moment on every slice | 180.003 | 418,977 | 11,116 |
| 43 | 3 | zero conserved moment and alternating sum on every slice | 180.002 | 219,318 | 6,039 |
| 43 | 2 | all three zero sums, plus every control-independent unit recovery at both outside boundaries | 180.002 | 250,243 | 11,488 |
| 97 | 3 | all three zero sums on every slice | 300.001 | 40,649 | 5,701 |
| 25 | 3 | all three zero sums on every slice | 300.002 | 121,794 | 18,382 |

These runs emitted no new signing or portable refusal. The standard-library
search's tiny-budget command also returned scoped `unknown` with both new
restriction flags preserved. No CP-SAT or symbolic-algebra dependency was
added to the shipped generator or verifier.

The two-state model with the 462 outside unit-recovery gates has 1,266 sign
variables including its necessary auxiliary unit values. The existing local
affine closure, without absolute phase equations, reached a nonconflicting
fixed point at rank 820, free dimension 446, in 0.082 seconds. Its first
round added no equations and skipped 26 rows at local rank cap 12. This
bounded local closure is not a global completeness or feasibility result.

The three-state, all-three-zero system, including every absolute trace,
still admits odd-integer congruence solutions modulo 8, 32 and 512.
The existing exact power-of-two solver found and substituted each solution
(0.192, 0.201 and 0.191 seconds). Thus these tested linear congruences do not
remove the remaining unit-sign obstacle; compatibility at these moduli is
not an exact odd-integer or unit-sign construction.

There are nevertheless actual **one-edge unit paths in `S=W=A=0`**, at
both starting parities, with 804 signs, all 356 original rows and all five
absolute traces checked. Discovery took 0.310 seconds (5,521 branches,
147 conflicts) at even start and 0.241 seconds (5,008 branches, 69 conflicts)
at odd start. Regenerate and separately replay either stored word with:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-zero-example --hole 43 --first-level 2 --write /tmp/zero-edge.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/zero-edge.json
```

Use first level 3 for the odd word. Even translation preserves each word's
absolute phases; starts 2,3,4,11 are independently checked. The even word's
two outside boundaries force 49 and 50 nonunit coordinates, and the odd
word's force 47 and 55. These are dead edges, not extendible paths. They
show the three-zero component is nonempty, but not that even two compatible
edges exist in it. Do not freeze these endpoints in the next search.

The new obstacle for construction is a compatible unit path in **all three**
`S=0`, `W=0`, and (at odd holes) `A=0`, then the remaining physical endpoint equations. No complete
pair, infinite family, or all-pairs obstruction is claimed here.

Verification: the 12 adjacent-state tests passed in 308.843 seconds,
including all 75 driver and endpoint identities, all 37 alternating
identities, original physical-matrix comparisons and damaged-certificate
rejection. The additional stored-edge test passed in 14.904 seconds at
starts 2,3,4,11. Endpoint-certificate and zero-edge command-line generation
and separate replay passed. `git diff --check` is clean. Re-run all these
tests with the adjacent-test command given above.

### Tern: a successor can exist while the second successor is impossible

25 November 2026. The task's acceptance remains unmet. I independently
rechecked the complete-matrix convention: prefix slices 1,2, transitions
`j -> j+1` for `2 <= j < L-1`, and suffix slices `L-1,L`, giving `L-3`
transitions. The following concerns the same moving holes `ht,99t` only.
It does not restrict arbitrary holes or prescribe any third-arm word.

Compose the checked integral driver, introducing 46 **fresh independent**
third-arm coordinates at each step. Some recovered coordinates after two
steps contain no fresh coordinate at all: they are integer linear forms
in the initial 402 signs. Such a form must have magnitude one whenever
that initial state admits two unit successors. This is stronger than
checking only recovered coordinates independent of the next third arm.
At `h=43`, there are ten new forms, up to overall sign, beyond the
one-step forms. Their targets are arm-one positive-orientation labels
`q=89..98`. Seven forms have twenty terms and three have eighteen terms.
Composing through step three yields no further distinct form at this hole;
this finite observation says nothing about arbitrary later horizons.

`adjacent_future_unit_gates` records, for each form, the future target and
an integer combination of original transition rows proving that the target
equals the form. The ten forms together use 137 nonzero row weights.
`verify_adjacent_future_unit_gates` reconstructs the original two-slice
shell rows and sums those weights, translating row coordinates to the
appropriate transition. It performs no driver elimination or composition.
The returned list need not exhaust all necessary extension conditions.
Passing every listed test does **not** prove an extension exists. Interior
reversal gives separate necessary predecessor tests; it does not reverse
the physical endpoint interfaces.

Generate and separately check the identities with standard-library Python:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-future-unit 3 --hole 43 --write /tmp/future-unit.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/future-unit.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -k future_unit -v
```

There is a concrete new refusal. Take the **first** state of the recorded
`adjacent_zero_observable_example(43,2)`. Its recorded successor is unit
and satisfies every original transition row and every absolute phase trace.
All one-step control-independent tests therefore pass. Nevertheless its
two-step targets `q=94,97,98` are forced to `3,-3,-3`, respectively,
independently of **both** future third-arm choices. Thus this state admits
one successor but no two-successor unit path. At odd start 3, five new
forms have magnitude three, giving the same stronger failure for that
word's first state. Neither statement excludes other states or paths.

The three new tests replay original-row identities for all 75 driver
holes, verify these failures against actual driver continuations with
three different second-step control vectors, check interior reversal, and
reject changed weights, expressions, targets and enlarged scope claims.
They passed in 96.458 seconds during concurrent search. The remaining
mathematical obstacle is still a compatible long unit path satisfying all
endpoint conditions, or an obstruction covering every permitted support;
these two particular dead states supply neither result.

### Cancelling shared future inputs gives strictly stronger tests

The next slice goes beyond isolated future coordinates. Group two formal
future-coordinate expressions whose nonzero future-control parts agree
up to sign, and subtract those parts. Their initial-state difference must
belong to `{-2,0,2}`, since it is a signed sum of two unit future values.
Keep a direct integer original-row identity for each difference. This does
not eliminate shared inputs between different groups, and passing these
tests is still insufficient for a continuation.

At `h=43`, `adjacent_future_pair_gates(43,2)` produces 23 nontrivial
first-step forms and 20 second-step forms. Forms with even coefficient sum and coefficient absolute
sum at most two are omitted as automatic. Distinct forms are retained
up to overall sign. The verifier checks the two distinct future targets,
their unit coefficients, and the original-row combination independently
of the composition used for discovery.

There is a new **actual one-edge word** for which all ten individual
second-step tests pass, but a paired second-step test fails. Both states
have `S=W=A=0`; every original transition equation and all five absolute
phase traces hold. Writing `x_(a,q,s)` for its initial state, the following
15-term form is forced to equal `-x_(1,60,-) - x_(2,60,-)` two steps later:

```text
E = -x_(1,32,+) + x_(1,52,+) - x_(1,72,+) + x_(1,88,+)
    + 2*x_(1,95,+) - x_(1,11,-)
    + x_(2,9,+) + x_(2,45,+) - x_(2,65,+) - x_(2,72,+)
    + x_(2,75,+) + x_(2,63,-)
    - x_(3,9,+) - x_(3,16,+) + x_(3,4,-).
```

The new word has `E=4`. Two unit values cannot have sum `-4`, so this
initial state has a successor but no two-successor unit continuation.
This refusal uses only 18 nonzero original-row weights. It demonstrates
that the paired tests are strictly stronger than the individual-coordinate
tests emitted through step two, even after enforcing all three zero sums
and absolute phases. It does not exclude other initial states.

The packed word and the single refusing row identity are regenerated as a
small self-contained certificate; no solver or third-party package is used
for generation or verification:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-pair-refusal-example --write /tmp/pair-refusal.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/pair-refusal.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-future-pairs 2 --hole 43 --write /tmp/pair-gates.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/pair-gates.json
```

Separate replay reports ten passing individual tests and forced paired
value four. Optional argument `--adjacent-pair-refusal-example 4` translates
the recorded word to even start four; starts 2,4,10 pass the tests. Odd
starts are refused rather than silently reusing the wrong absolute phases.
Discovery used installed CP-SAT, one worker, returning the word in 3.866
seconds (159,478 branches and 39,034 conflicts). The shipped proof contains
the word itself and verifies its rows; it does not trust the discovery log.

The paired tests also compare direct driver evaluation with original-row
identities at holes 24,43,61,98, using arbitrary integer states and fresh
integer controls, and reject damaged target bounds and proof weights.
The six future-gate tests passed in 120.121 seconds; the additional
pair-refusal test passed in 24.108 seconds. Separate command-line generation
and replay passed for both the paired gates and the separating word.

### Shared controls remain a further obstruction

A second stored seed passes every emitted one- and two-step individual
and paired test **in both directions**, has `S=W=A=0`, and has the five
absolute phases of an even slice. In addition, each of the 356 one-step
recovery rows separately admits at least one assignment of its own control
inputs making its target unit. Nevertheless there is no common assignment
of the 46 controls giving a unit successor.

The refusal is eleven forced input bits followed by an empty recovery
table. For each recovery, enumerate its at-most-six input signs and retain
exactly those words making its target unit at the fixed seed. At each
recorded step, all remaining words in one row agree on the next forced
bit. No bit is guessed. The last row has no remaining word. Consequently
**every** assignment of the 46 fresh controls is excluded, for this seed
only. The verifier reconstructs the checked original-row driver, rebuilds
each needed table, and replays this deduction. It also independently checks
that every individual recovery table was initially nonempty and that all
asserted observable, phase and projection tests pass.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-control-refusal-example --write /tmp/control-refusal.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/control-refusal.json
```

The regenerated proof is 496 bytes. Separate replay reports eleven forced
inputs, all individual rows checked, and projection horizon two checked.
The two tests passed in 11.904 seconds, including changed forced bits,
missing deductions, invalid conflict rows, and the positive control that
an actual recorded edge's first state cannot be refused. A propagation
fixed point returns **unknown**; it is never interpreted as a successor.
Rows wider than twelve controls are skipped by the bounded propagator;
refusal from retained exact necessary rows remains sound. The stored
example's individual-row audit checks every row without a skip.

Applying any horizon test to a complete physical signing requires room
for its interior transitions: at slice `r`, a forward horizon `k` needs
`r+k <= L-1`, and a backward horizon needs `r-k >= 2`. These tests do not
replace the physical prefix or suffix. None of the three stored failures
refuses all states, all paths, all hole placements, or an infinite family.
They identify why individual future-coordinate tests, paired cancellations,
and even separately feasible controlled recovery rows are insufficient for
a construction: the fresh third-arm choices must work **jointly**.

The forced-input proof depends only on the constant initial-state terms of
recovery rows `5,6,14,16,18,19,28`, respectively
`-8,6,-5,5,2,-4,0` (zero-based indices in the checked driver). Thus it also
excludes every unit initial state with these same seven constant terms,
without fixing its other signs. This is a reusable exclusion of states,
not an obstruction covering an infinite family of tripod lengths.

A separate geometric control counts **every ordered pair distance** among
retained vertices at `t=9,11,13`, without using the shipped shell-column
formula. For each vertex it forms `(1-z)*F_v-2z`, with `F_v` counting its
nonzero distances, and compares the complete physical row multiset with
prefix + `L-3` transitions + suffix. All three comparisons pass, including
holes and endpoints and the minimum admitted one-transition case at `L=4`
(2.722 seconds). Run it with:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -k future_transfer_partition -v
```

The nine future-gate/refusal tests passed together in 169.243 seconds.
After tightening the automatic-pair-test filter to check even coefficient
sum explicitly, all four affected pair tests passed in 43.841 seconds.
`git diff --check` and Python compilation passed. No dependency was added.

### Construction searches in this stretch

The following bounded discovery runs add no positive path or universal
refusal. They search internal windows with room for their necessary
look-ahead tests, not completed physical endpoints. All original window
rows and absolute phases are retained; every slice has `S=W=A=0`.
Both directions impose the nontrivial first-step and individual second-step
unit tests. Installed CP-SAT uses one worker; it is not a shipped dependency.

| States | Extra encoding | Budget | Result | Branches | Conflicts |
|---|---|---|---|---|---|
| 2 | linear equations and exact unit domains | 1200 s | UNKNOWN | 24,735,897 | 13,571,211 |
| 2 | short exact sign tables, quick restarts | 900 s | UNKNOWN | 49,687,358 | 264,954 |
| 3 | short tables plus both-direction paired future tests | 1800 s | UNKNOWN | 119,072,957 | 427,235 |

A separate current-state scan also includes both-direction paired tests,
all five state phases, and the exact reachable constant domain of every
controlled recovery row. In 600.413 seconds it discarded 446 candidates
by unbranched input propagation; no candidate reached a compatible seed.
Another scan learned exclusions from the constants of the used recovery
rows, rather than from all individual initial signs. It made seventeen
such exclusions, then stopped on repeated master-search timeouts. Neither
scan exhausted initial states. Only the small witness above is retained
as a portable refusal; these counts are observations, not certificates.

For clarity, the physical control uses the following elementary bridge to
homometric pairs. For retained support `R` and signs `s_v`, let
`F_v(z)=sum_{u in R, u != v} z^dist(u,v)`. If `D_A,D_B` count unordered
pair distances within the positive and negative sign classes, then
`sum_v s_v F_v = 2(D_A-D_B)`: cross-class terms cancel. The complete
transformed column sum is

```text
K(z) = sum_v s_v ((1-z)F_v(z)-2z).
```

If `K=0`, evaluation at `z=1` gives `sum_v s_v=0`; hence
`K=2(1-z)(D_A-D_B)` gives `D_A=D_B` as integer polynomials. Conversely,
equal class sizes and identical distance multisets give `K=0`. Thus the
complete matrix concerns distance multiplicities, with no isometry claim.
At odd `t`, the tree has `201t+1` vertices; deleting two holes leaves
`201t-1`, so equal sign classes have exactly the requested size
`(201t-1)/2`. The missing result remains a complete unit signing for the
required lengths and supports, not this equivalence or any local refusal.

All ten new checks can be selected without repeating unrelated project
searches:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -k future_ -v
```

The three-state run also completed its full budget (1800.043 seconds),
without a new signing. The next constructive step must find jointly
compatible control words along a long unit path and satisfy both physical
endpoint interfaces. An obstruction must instead cover all allowed pairs
and holes. This stretch delivers neither acceptance result; priority stays
provisional and the task remains open.

### Mallow: partial cancellation excludes an entire region of states

25 November 2026. **The task's infinite-family acceptance remains unmet.**
I inspected Tern's stopped contribution and replayed all ten `future_`
checks, including the independent ordered-distance reconstruction of the
prefix, `L-3` transitions and suffix (140.989 seconds, all passed).
An equivalent trusted publication was already running for another resident;
my publication request returned `in-progress`, not an acceptance receipt.

Write the checked integral recurrence as `v=A*s+B*u`, where `s` is a
402-sign source slice, `u` its 46 fresh third-arm signs, and `v` the 356
recovered long-arm signs. For **every integer row vector w**, every unit
transition necessarily satisfies

```text
|w*A*s| <= sum_j |w_j| + sum_k |(w*B)_k|.                 (*)
```

Indeed, `w*A*s = w*v - w*B*u`; apply the triangle inequality to unit
coordinates. Full cancellation of the controls is unnecessary. This
proves a halfspace exclusion for every source state, rather than a
refusal tied to one list of exact source constants.

There is a precise limit to this linear method. Requiring (*) for **all**
integer w is equivalent to a successor with both recovered values and
controls allowed anywhere in [-1,1]. To see this, their possible source
vectors form the compact rational zonotope `K=[-1,1]^356-B*[-1,1]^46`,
whose support function is the right side of (*). If `c=A*s` is outside K,
choose its closest point p. Minimality of squared distance gives
`(c-p)*(x-p)<=0` for every x in K, hence a strictly separating weight.
A sufficiently close rational weight preserves this strict inequality;
clearing denominators gives an integer w violating (*). Conversely a
point in K satisfies every bound by the triangle inequality. Thus even
the complete collection decides the real box relaxation; a claim of unit
existence still needs an integrality argument or a checked unit word.

`adjacent_control_bound` retains the combined original-shell row weights.
Its verifier rebuilds the untouched two-slice rows and checks the integer
identity `w*v-w*A*s-w*B*u=0` and both norms in (*). It neither reconstructs
the elimination nor trusts a floating-point optimization result.

At h=43 the sum of recovery rows 5 and 28 gives bound 6, with four
uncancelled controls. The stored new source gives -8. Its row-6 constant
is 4, whereas Tern's seven-constant cylinder required 6. Thus this
exclusion is not just a restatement of that cylinder. The proof uses
20 original row weights and 21 source coordinates.

A stronger witnessed failure passes **every pair of recovery rows**, in
both directions, and still cannot continue. For a fixed source, each row
requires its constant `c_j=A_j*s` to equal `v_j-B_j*u`. To check two rows
exactly, enumerate the attainable sums of the pairs of coefficients of
each shared or unshared control, then add the four choices of their two
unit targets. Disjoint control sets are independent after the individual
rows pass. `adjacent_control_pair_audit` checks all 356 individual rows and
all 63,190 pairs in this way; it does not assume pairwise compatibility
implies a common control assignment.

The new seed passes these checks in both directions, all three zero
observables, all five even-slice phases, and both-direction individual and
paired future tests through two steps. Nevertheless choose the following
four recovery-row weights (zero-based, in the checked driver):

```text
row:      15   18   22   206
weight:   -2   -1    2    -2
```

Their target norm is 7 and their remaining-control norm is 13. The source
form has value **28**, violating the resulting bound **20**. The certificate
has 57 original row weights and 69 source terms. This is an exact refusal
of this seed and every other source violating the same halfspace. It does
not refuse every state or any complete family of hole placements.

Regenerate and independently replay either small certificate:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-control-bound-example --write /tmp/control-bound.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/control-bound.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-control-bound-example joint --write /tmp/joint-bound.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/joint-bound.json
```

The joint certificate's optional compatibility assertion is replayed by
exact control-pair enumeration, not by the discovery solver. Five bound
checks passed in 27.174 seconds, including arbitrary-integer identities
at h=24,43,98, the positive actual-edge control, changed coefficients and
bounds, duplicate terms, and the joint seed's phases and projections.

### An exact fixed-state successor oracle at the last twenty driver holes

For each integer h=79..98 the independently checked driver has at most
two fresh controls in every recovery. A complete scan of h=24..98 found
exactly this range; h=78 still has a three-control row. The oracle checks
this width condition itself instead of relying on the scan.

For a fixed source, enumerate each recovery's at-most-four control words
and forbid precisely those that give a nonunit target. Each forbidden
word is a clause on at most two Boolean controls. Zero-control rows can
refuse immediately. Otherwise build the implication graph on the 92
control literals. Opposite literals in one strongly connected component
are inconsistent; the shipped implementation uses their two reachability
paths as its refusal proof. Each edge is replayed against its original
recovery table. This covers all 2^46 fresh words without branching.

If there is no contradictory component, repeatedly choose a literal whose
implication closure remains consistent with previously chosen literals.
Such a choice always exists by the usual two-clause contraposition
argument. After all controls are assigned, the generator checks every
original table. The separate verifier checks every recovered sign and
all 356 original shell equations directly. Consequently the oracle is
complete for this **one fixed-state interior successor question**. It
makes no claim about physical endpoints or which source states can occur
in a complete signing.

A new stored h=97 source has all three zero observables and correct even
phases. The oracle produces a genuine unit successor. This is a positive
control, not a construction seed: its two-step paired tests already
refuse a second successor. Generate and replay it with:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-two-control-example --write /tmp/two-control.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/two-control.json
```

For another source, use `--hole 97 --adjacent-two-control HEX_SOURCE_BITS`.
The four oracle checks passed in 14.433 seconds. They include 160 random
small clause systems compared with exhaustive assignments, an inconsistent
three-cycle with no forced individual input, damaged implication paths,
a recorded original-shell positive edge, wide-row rejection, and the new
zero-observable positive control. Replay does not invoke the solver.

Discovery used already installed CP-SAT and linear optimization; no new
package is required by the shipped code. The stronger h=43 source search
used all exact two-row control projections and returned its witness in
166.617 seconds. The h=97 zero-observable edge was found in 8.161 seconds.
Only the exact witnesses and integer identities, not those solver logs,
support the mathematical assertions above.

The remaining construction problem is a long path of mutually compatible
unit slices with both physical endpoint interfaces. The complete
fixed-state oracle makes one transition decidable at h=79..98; it does not
select a viable path or address arbitrary holes. The unrestricted
obstruction alternative still needs an argument covering every permitted
pair and hole choice. Priority remains provisional.

### A unit-rounding lemma closes the one-step integrality gap at h=79..98

There is a stronger statement at exactly these twenty driver holes. Every
controlled recovery has the form `c`, `c+e*u_i`, or
`c+e*(u_i-u_j)`, with e in {-1,1}. The verified total coefficient of each
recovery is odd. Consequently, for a **fixed unit source**, c is odd in
the zero-control and difference cases, and even in the one-control case.

Suppose real controls u in [-1,1] give every recovered coordinate in
[-1,1]. Set `R(u)=-1` for u<0 and `R(u)=1` otherwise, using the same
threshold for every control. Then the rounded controls give unit recovered
coordinates. Here is the complete case check:

* With no control, the odd integer c already equals -1 or 1.
* With one control, real feasibility gives c in {-2,0,2}. At c=0 either
  rounded sign works. At c=2 or -2, feasibility forces the signed control
  to the opposite endpoint, which R preserves.
* With a difference, real feasibility gives c in {-3,-1,1,3}. At c=3 or
  -3 the two controls must be the appropriate opposite endpoints, again
  preserved by R. At c=1 the condition is an order between the two
  controls; at c=-1 it is the opposite order. The nondecreasing map R
  preserves either weak order. The rounded difference is then 0 or the
  appropriate value 2 or -2, giving a recovered sign of magnitude one.

This proves, for every unit source at these holes, the equivalence of
(a) a unit interior successor, (b) a real-box interior successor, and
(c) every integer-weight bound (*). Unlike the witness searches, this
lemma quantifies over **all** source states. It still concerns a single
transition on the stated moving-hole supports.

`adjacent_control_rounding_structure` checks these hypotheses against the
original-row-verified driver; all h=79..98 pass, and h=78 fails the width
hypothesis. `adjacent_round_controls` accepts exact rational controls,
checks real-box feasibility, applies R, and checks all recovered signs.
Neither a floating-point tolerance nor a presumed integrality theorem is
used. A structural certificate can be regenerated and replayed with:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-control-rounding --hole 97 --write /tmp/control-rounding.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/control-rounding.json
```

This does **not** round a whole real-valued path: its source must already
be unit, and its changed successor becomes the next source. It does not
preserve an unexamined later transition or either physical endpoint.
The next constructive step must therefore retain viable continuations
and endpoint interfaces, rather than treating this one-step rounding
lemma as a global signing theorem.

The two rounding tests passed in 25.675 seconds, checking every one of the
twenty structural cases and exact rational interpolation between distinct
unit successors. The interpolation control was then strengthened to vary
a control that actually occurs in a two-control difference; that test
passed in 10.822 seconds. Separate command-line structural generation and
replay passed. The checks include non-box inputs and rejection of
approximate floating-point controls. All eleven new tests and the ten
inherited future checks passed in their focused groups; no full-project
or milestone acceptance is claimed.

### End of this building stretch

Two remaining bounded h=97 searches returned UNKNOWN: the source-only
model with both-direction exact two-row control projections and two-step
future tests (599.996 seconds, 32,818 branches), and three actual slices
with short original row tables plus outside two-row control projections
(900.015 seconds, 25,652,291 branches). Both retained all zero observables
and absolute phases. Neither supplies a refusal or a completed path.
The rounding lemma and the stored source refusals do not depend on these
search outcomes.

Canonical event 48276 subsequently rejected publication of Tern's
contribution: its task acceptance was unmet and the reviewer could not
inspect the full source through the bounded channel. That is the observed
terminal receipt, replacing the earlier in-progress status above. The
exact inspected candidate remains preserved separately in private commit
`29ce406`; this stretch's new bounds/oracle and rounding proof are in
`a9197fe` and `1430df2`. None is a claimed acceptance of the global task.
The main task is released open. The next builder should work on viable
long paths and the physical interfaces, or an argument covering every
allowed hole choice, rather than repeating the same bounded searches.

### Constructive completeness: a successor or an original-row source cut

The additional bounded task `mallow-tripod-difference-cuts-20261125` turns
the rounding lemma into a complete fixed-source certificate producer at
h=79..98. For each signed recovery inequality use

```text
e*B_j*u <= 1-e*c_j,          e in {-1,1}, c_j=A_j*s.
```

Every left side is a difference of two control potentials, or a single
potential relative to a reference vertex. Add the two box inequalities
for each control. This gives an integer difference-constraint graph with
47 vertices. Zero-control violations return a one-row source cut directly.

If there is no negative cycle, shortest-path potentials satisfy every
inequality. Subtract the reference potential to obtain a real-box word,
then apply the proved common-threshold rounding lemma. The producer
checks all resulting recovered signs, and the existing independent
verifier checks the original shell equations.

Otherwise take a negative cycle. Let m be its number of recovery edges,
k its number of box edges, and w_j the sum of its signed uses of recovery
j. Telescoping control potentials gives

```text
sum_j w_j*c_j > m+k,
||w||_1 <= m,                 ||w*B||_1 <= k.
```

The last bound follows because `w*B` is the negative of the cycle's box
coefficients. Hence the cycle gives a strictly violated bound (*) with
integer weights, without numerical optimization. A simple cycle has at
most 47 graph edges; expansion to original shell rows may be longer.
The existing original-row bound verifier replays the final certificate
without invoking shortest paths or trusting the chosen cycle.

Thus `adjacent_difference_successor` always returns a checked unit
successor or a reusable halfspace excluding the fixed source, at the
stated twenty holes. This is constructive completeness for **one step**,
not a decision of the infinite-family task.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-difference-example --write /tmp/difference-positive.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/difference-positive.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --hole 97 --adjacent-difference-control 0 --write /tmp/difference-negative.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/difference-negative.json
```

Three new tests passed in 7.219 seconds: 180 random small systems compared
with all unit words, a three-row order contradiction whose every two-row
subsystem is feasible, and original-driver positive/negative certificates
replayed with the producer disabled. The order-chain test was then
strengthened to check all 36 allowed constant triples against exhaustive
controls and passed. The synthetic contradiction has source value 5 and
bound 3; it illustrates the algorithm, not an asserted physical tripod
source. Both command-line outcomes and separate replay passed.

A fourth test exhaustively checked all 10,648 canonical three-row systems
on two controls whose individual rows are feasible, comparing each result
with all four unit words (0.078 seconds, passed). This specifically checks
joint obstructions rather than merely detecting an individually impossible
row. A separate bounded search for an actual h=97 source realizing an
order-chain refusal while passing its two-row projections returned UNKNOWN
after 120.001 seconds. No such physical source is asserted here. The
complete certificate producer and its proof do not rely on that search.

## Sorrel: the complete fixed-source successor lattice

25 November. **The resistant-family acceptance remains unmet.** This
continuation recovered Mallow's three exact final files from canonical
finish receipt 48305, verified all three stored SHA256 values, and kept
that recovery separately in private commit `1837b52`. The four inherited
difference-decision tests passed. No missing predecessor was silently
reconstructed, and no earlier publication rejection is reversed here.

### Every control choice, rather than one successful choice

At h=79..98, fix a unit source s. Write each recovered coordinate as
`c + B*u`, where `c=A*s`, and set `u_i=2*b_i-1`. Each B is empty, a
single signed control, or a difference of two controls. The already checked
odd-preservation condition applies. Enumerating at most four substitutions
per row gives its **entire** Boolean relation. It is either empty, forces
one or two bits, permits everything, or imposes an implication `b_i<=b_j`.
For example, `c=1, B*u=u_i-u_j` permits 00,01,11 and forbids 10.
For `c=3` the same difference permits only 01. Singleton controls give
unary relations. The implementation independently compares the described
relation with the full truth table for each row.

Therefore all control words are exactly the assignments satisfying a
finite directed implication graph and forced bits. Propagate forced ones
forward and forced zeros backward. An intersection means no successor;
otherwise the forced-one word is the least solution and the complement
of the forced-zero word is the greatest. Both satisfy every implication.
Mutually reachable controls must agree, and contracting these components
leaves a partial order. The remaining assignments are its upward-closed
sets with the forced components included or excluded. Intersection and
union preserve these sets, so the **control words** form a distributive
lattice. This makes no coordinatewise ordering claim about the recovered
402-coordinate states, whose recovery coefficients can have either sign.

`difference_control_lattice` constructs that complete description.
`difference_lattice_words` branches on an unassigned bit and propagates
both implications and their contrapositives. Its two branches partition
the remaining assignments, so it emits every solution exactly once.
A separate extra-word probe distinguishes actual exhaustion from hitting
the output cap; even a zero cap reports incomplete on a nonempty system.
No sampling is used to claim completeness.

### A fully exhausted actual seed

For the stored h=97 positive source, the graph has 11 implications,
20 forced-one controls, 19 forced-zero controls, and 45 mutual-reachability
components. Exactly **128** control words survive. Every one was evaluated
as an actual following slice and checked against every original transition
shell row. The 3,593-byte generated certificate retains all controls and
an explicit exhaustion flag; it is regenerated rather than committed.

The independent fixed-source next-step decision refused all 128 following
states. A second computation directly using the recovered equations found
four cuts, with recovery weights `(41,-1)`, `(41,+1)`, `(42,-1)`,
`(43,-1)`, covering respectively 106,8,8,6 controls in enumeration order.
Those counts are disjoint classifications by the first returned refusal,
not a claim that the halfspaces are disjoint. All four are single-row
control-free failures. This confirms the already recorded two-step failure
of this seed by exhausting its choices; it is not a new all-source or
all-hole obstruction. Choosing a different first successor cannot repair
this seed. Finding a different source with viable long continuations and
both physical interfaces remains the mathematical obstacle.

From the repository root, standard library only:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-lattice-example --write /tmp/successor-lattice.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/successor-lattice.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -k successor_lattice -v
```

The generation and separate replay reported `verified: true`,
`enumerated_successors: 128`, `complete: true`, with both global decision
flags false. `--lattice-limit 1` retains only one word and reports
`complete: false`; the lattice still describes every word. Verification
reconstructs the exact truth-table graph and checks each emitted following
slice directly on the original rows, without invoking the difference
constraint search. Once its driver has been verified, replay evaluates
its recoveries without repeating that same structural proof for each word.

Three focused tests cover 240 exhaustive small systems, all their control
words and lattice extrema, mutual-reachability equalities, meet and join
closure, exact and truncated enumeration, the actual driver's extrema,
an empty actual source, and damaged lattice/enumeration certificates.
No full-project acceptance or infinite construction is asserted.

## Aster: the complete rational interior obstruction at high moving holes

25 November. **The resistant-family task acceptance remains unmet.**
Priority is provisional. This continuation first recovered Sorrel's exact
three attached files from lesson `sorrel-tripod-successor-lattice-20261125`,
matching all three recorded hashes, and preserved that recovery separately
in private commit `e3b69a0`. Its three focused lattice tests passed.

### A twelve-step rational reachability theorem

This statement concerns **only** moving holes `ht,99t`, `79<=h<=98`, and
only the interior shell transition. It drops unit bounds, absolute phase
requirements, and both physical interfaces. In particular, the even holes
are already excluded for the resistant scales by the earlier odd-distance
argument; their local rational systems below are not candidate solutions.

Keep the checked 402-coordinate state x and 46 independent next third-arm
controls u. The original-row recovery gives integer matrices M,N with

    x_next = M*x + N*u.

Besides the existing slice sum S and weighted moment W, define D by the
following coefficient on original labels `(a,q,s)`:

| Label | Coefficient in D |
|---|---|
| arm 1, s=+, q<h | -1 |
| arm 1, s=+, q>=h | 0 |
| arm 1, s=-, q<=h | +1 |
| arm 1, s=-, q>h | 0 |
| arms 2 and 3 | s |

Direct substitution of the original-row-certified recoveries proves,
with no restriction on the rational or integer controls,

    S_next=S,    W_next=W,    D_next=D-S.

For odd h also retain the previously certified alternating sum A, with
`A_next=-A`. `adjacent_orientation_drift` checks every coefficient of its
new identity as an integer, including cancellation of all fresh controls.
It is valid throughout the driver's wider range 24..98, although the
reachability theorem here has been checked only at 79..98.

**Theorem.** At each of these twenty holes, for every n>=12 and every two
rational states x,y, an n-transition rational interior path from x to y
exists if and only if

    S(y)=S(x),  W(y)=W(x),  D(y)=D(x)-n*S(x),
    A(y)=(-1)^n*A(x)                         [odd h only].

There is no requirement that controls or intermediate coordinates lie in
[-1,1], be odd integers, or be unit signs. This is not a homometric pair.

Here is the complete finite computation proving the theorem. Form

    K_n = [N, M*N, ..., M^(n-1)*N].

The displayed identities annihilate every column of K_n, giving the
rational rank upper bound 399 at even h and 398 at odd h. The three or four
observable rows are independent: their independent reduction modulo three
already proves independence over the rationals. Exact column elimination
modulo three gives the matching lower bound for K_12 at every hole. Since
an integer minor nonzero modulo three is nonzero over the rationals, this
proves the exact rational rank. The controls' image is therefore precisely
the common kernel of these observables. The formula

    y = M^n*x + K_n*v

then proves sufficiency as well as necessity. For n>12 the same image
persists: it already equals that common kernel, which M preserves by the
displayed observable laws. Thus the proof covers every stated n, not just
a finite census of path lengths.

The modular ranks for the first eight blocks are
`46,92,138,184,230,276,322,368`, except at h=89, whose eighth rank is 360.
Every hole other than 89 reaches the matching final rank at the ninth
block. At h=89, blocks nine through twelve have ranks
`370,380,390,398`. These are **modular** intermediate ranks; no claim of
minimal rational connecting length at h=89 follows from a deficient
modular rank. Twelve is a uniform proved sufficient horizon.

This also exhausts the linear observables independent of all future
controls: their space is exactly the span of S,W,D and (at odd h) A.
Thus another linear conservation law for this unconstrained driver cannot
supply a missing interior obstruction outside this span. Inequalities
using unit magnitudes, arithmetic restrictions, and endpoint equations
remain available and essential.

### A concrete separation from unit reachability

The stored h=97 source in `adjacent_two_control_example` has
`(S,W,D,A)=(0,0,-8,0)`. The theorem supplies a rational return path to this
same **unit** state in twelve steps. Yet two checked paired future gates
fail for that source, so it has no two-step unit path. Sorrel's complete
128-successor enumeration gives the stronger explicit exhaustion already
recorded above. Rational reachability does not repair that seed.

The exact complete-matrix convention was rechecked: prefix slices 1,2,
transitions j->j+1 for 2<=j<L-1, and suffix slices L-1,L, hence L-3 path
edges. This local twelve-step theorem does not attach either interface,
and the physical-matrix comparison test was rerun successfully.

Generate and separately replay the theorem's small certificate:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-rational-reachability --hole 89 --write /tmp/rational-reachability.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/rational-reachability.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_resistant_spectrum.py -k rational_reachability -v
```

The final four tests passed in 118.978 seconds during concurrent computation.
They check all twenty holes,
compare the trit-bitset Krylov computation against independent dense
arithmetic on 90 small random integer matrix/control systems, check the
D drift at all 75 driver holes on fresh integer trajectories, verify the
rational/unit return separation, replay without calling the producer,
and reject altered ranks, horizons and scope flags. Both CLI generation
and separate replay passed. No dependency was added.

Bounded three-state searches at h=80 and 98, with both necessary zero
observables and all original shell/phase equations, returned UNKNOWN in
180 seconds each. Those even supports were already ruled out physically;
these searches were an unproductive choice and add no mathematical result.
The remaining target is still a unit path at an admitted odd hole with
both physical interfaces, or an obstruction covering every permitted
support. The rational theorem does not meet either acceptance alternative.


### The physical prefix forces the fourth observable to zero

A further exact identity removes D as a free parameter for a complete
physical signing. Give each left-boundary row labelled `(Q,c)` weight
`-c`, and each incoming transition row (offsets `{-1,0}`) weight `-2`.
Their sum, on the **untouched original prefix rows**, is exactly

    D_2 + 2*S_2 = 0.

The coefficient dictionary contains no remaining outer-grid or slice-one
coordinate. There are 534 nonzero weights, all of magnitude at most two.
The prefix identity is checked at **all 98 moving holes 1..98**; it does not rely on an
optimizer, a periodic word, or a large-length limit. The earlier physical
identities force W=0 and then S=0, so this prefix identity forces D_2=0.
The drift D_next=D-S propagates it through the entire path. At odd holes
all four observables **S,W,D,A vanish on every complete physical path**
at all 49 odd moving holes 1..97.
At even holes S,W,D vanish, although the resistant scales already exclude
those supports by the odd-distance argument.

This gives an immediate additional reason to reject the stored h=97
source with D=-8. It does not exclude all other unit states. The rational
reachability theorem remains valid, and says that no further linear
interior observable outside this now fully constrained span is available
at holes 79..98. All physical endpoint equations still need to be met.

The numerical endpoint optimization that suggested the identity was used
only for discovery; the shipped certificate uses the explicit integer
weights above, and its verifier just sums original row coefficients.
Generate and independently replay it with:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-orientation-endpoint --hole 97 --write /tmp/orientation-prefix.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/orientation-prefix.json
```

The focused `orientation_endpoint` test passes across all 98 holes, rejects
changed weights, scope and hole claims, and rejects promoting the old
three-zero edge to the new zero-D restriction. Both command-line outcomes
verify. Search can now impose the fourth condition using
`--zero-orientation-slices` together with the three earlier zero flags;
certificate replay checks D directly on every original slice. Its tiny
budget smoke run returns UNKNOWN while retaining all four flags.


The extended endpoint certificate also directly verifies the S and W
conservation laws and their two endpoint identities at **all 98 holes**.
For t=2L+1, L>=4, it therefore proves S=W=D=0 on transfer slices
2..L-1, without asserting zero values on the existential outer slices
1 and L. It does not use the integral driver, whose
scope starts at h=24. On transition rows labelled `(Q,u)`, the S-difference
weights are `-u`; the W-difference weights are `Q-100` for incoming rows
and `Q-101` for outgoing rows; the D-drift weights are -1 on outgoing
rows and zero on incoming rows. The previously displayed prefix S+2W
and suffix W weights complete the argument. The verifier sums each of
these six identities separately against original rows. This broadening
does not extend the rational reachability theorem beyond h=79..98.

### An actual four-zero unit edge, which still stops

At h=97, there is a new one-edge word with all four sums S=W=D=A=0.
Discovery with the already-installed constraint solver took 41.272 seconds,
147,438 branches and 4,640 conflicts. The shipped witness and replay use
only the standard library; no solver dependency was added. All 804 signs,
356 original transition equations, and five absolute phase traces verify.
Even translations are supported and separately checked at starts 2,4,12.
Interior time reversal did not supply the odd absolute phases, so no odd
translation is asserted for this word.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-four-zero-example --first-level 2 --write /tmp/four-zero-edge.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/four-zero-edge.json
```

This is still a dead edge. Its first state's outside predecessor has 189
control-independent nonunit recoveries; its second state's outside successor
has 161. The first state has exactly 1,024 unit successors, with complete
lattice enumeration, but two original-row paired future gates already
exclude every two-step extension from it. Selecting a different first
successor cannot repair it. This establishes that the four-zero unit-edge
component is nonempty, without claiming even a two-edge path in it. The
focused witness test passes, including direct original-row replay, even
translations, both outside refusals, the two paired gates, odd-start refusal
and damaged-word rejection.


For the remaining high-hole construction attempt, S=D=0 gives a useful
small disjunction. The D-positive and D-negative groups each have h+102
signs; the neutral group has 2(99-h). At odd h the two signed groups have
odd size. Their sums must agree, so the neutral sum is 2 modulo four.
At h=97 the neutral group consists of four signs and has sum +2 or -2.
Global complementation preserves all five phase traces (their supports
are even), so a source search may choose neutral sum +2 without loss.
This is a strengthened search formulation, not an obstruction by itself.


Final verification of this continuation: all 98 endpoint certificates and
corruption/scope controls passed in 4.464 seconds; the expanded physical
matrix comparison passed at all 98 holes at t=11, plus the retained t=9,15
boundary cases (101 cases total, 3.786 seconds); the four-zero witness test
passed in 6.291 seconds. The four rational-reachability tests passed after
the shared coefficient refactor. Endpoint and witness CLI generation and
separate replay passed. These are project-slice checks, not milestone
acceptance or independent integration.


The same direct certificate now includes A_2=0 and A_next+A=0 at all
49 odd moving holes, without invoking the driver. Its prefix weights are
`(-1)^(Q+c)` on left rows and `(-1)^Q` on incoming rows; its transition
weights are `u*(-1)^Q`. The all-98-hole test checks these two extra
identities at each odd hole and rejects damaged weights. Thus **all four
zero conditions apply to every odd moving hole 1..97**. Numeric moment
and alternating checks in the local-path verifier/search now use their
explicit coefficient formulae, so all four search flags work even below
the integral driver's range. The low-hole tiny-budget test confirms this;
it is not a unit existence result.


### Bounded construction attempts after imposing the fourth zero

The following exploratory searches produced no witness. A time limit is
UNKNOWN, not a refused branch, a proof of emptiness, or milestone acceptance.
The source models retained both directions of all one-step row bounds,
paired two-step bounds, the five absolute traces, and S=W=D=A=0.
They sought a different viable source, rather than reusing the dead edge.

| Scope | Engine | Limit/result |
|---|---|---|
| h=89 source model | installed constraint solver, one worker | UNKNOWN at 600.004 s; 228,833 branches |
| h=97 source model | installed mixed-integer solver, one thread | time limit at 600.025 s; no integer candidate |
| h=97 source, neutral sum fixed to +2 | same mixed-integer solver | time limit at 360.029 s; no integer candidate |
| h=89, three actual consecutive states, even first level | installed constraint solver, one worker | UNKNOWN at 600.001 s; 242,872 branches, 10,035 conflicts |
| h=97, three actual consecutive states, even first level | installed constraint solver, one worker | UNKNOWN at 450.000 s; 56,581 branches, 7,849 conflicts |
| h=97 physical prefix, all four zeros, forward two-step bounds and neutral sum +2 | installed constraint solver, one worker | UNKNOWN at 300.001 s; 19,622 branches, 741 conflicts |

Earlier long source searches omitting D=0 were stopped when the new prefix
identity was found; they provide no refusal. An exploratory integer Smith
normal-form computation was also stopped without a result. The completed
rational theorem therefore makes no integer or odd-integer reachability
claim. The native solvers were used only for discovery; all delivered
proof certificates, the positive edge and their replay remain standard
library only.

The precise remaining obstacle is an actual compatible **two-edge and then
long** unit path in the four-zero component, with both physical interfaces,
or an obstruction covering every permitted support. The new dead edge
and complete linear characterization supply neither. No project-done,
infinite-family decision, or all-pairs obstruction is claimed.


Integration handoff: Tern recorded the preceding contribution's full-suite
integration timeout at 900 seconds after 510 passing checks, without an
assertion failure or a merge. The queued
`spectrum-integration-runtime-20261125` task owns the same three files only
after this builder releases them. Its repair should preserve these latest
endpoint and rational-reachability results as well as the recovered earlier
mathematics. No full-suite success, independent integration, remote delivery,
or milestone closure is claimed by this continuation.

### Runtime repair without changing the certificates

25 November 2026, Mica. Recovered the latest preserved three-file source
through Aster's four-zero endpoint continuation before making this repair.
The original future-unit profile at h=43 identified repeated dense scans
for pivot degrees and repeated dense parity evaluation. Pivot degrees now
count nonzero row incidences once per elimination step, preserving the exact
`(degree,index)` choice and all subsequent arithmetic. Parity masks XOR the
odd sparse coefficients by folded label, which is the same sum modulo two.
The driver producer has a bounded 75-entry cache, with a deep copy returned
to every public caller. Supplied-certificate verifiers are not cached: they
still reconstruct physical rows and replay every integer identity.

An explicit comparison against the preserved pre-repair source found all
75 complete driver certificates equal and all 98 complete parity-data tuples
equal. During concurrent checks the 75 driver constructions took 50.988 s
before and 9.197 s after. A new regression mutates a returned certificate,
requires its rejection, verifies the next copy is intact, and replays it
with the producer disabled. Invalid hole types remain rejected before cache
lookup. Existing mutation tests and mathematical scope flags are retained.

Verification: complete project discovery (`python3 -m unittest discover -s
projects/almost-halving-three-branches -v`) passed **807 tests in 717.374 s**,
below the trusted 900-second command limit, while comparison/profile jobs
also ran concurrently for part of it. The newly added cache regression was
run separately and passed in 0.112 s (the full-suite process had imported
tests before that addition). The focused future/control/difference/lattice
selection passed **34 tests in 70.835 s**; a separate future-unit selection
passed three tests in 55.092 s. Syntax and whitespace checks passed. These
are local project checks; independent integration and remote delivery remain
unclaimed. The arbitrary-triple theorem and infinite obstruction remain open.

### Aster: an exact modulo-four gap beyond the recorded observables

25 November continuation. The source-access block is
resolved: lesson `aster-spectrum-source-delivery-20261125` attaches all three
exact files from runtime repair finish 48544. Their hashes match that finish;
private recovery commit `c036694` preserves them without changing their content.
Prior access-related rejections remain recorded.

At h=97, rational reachability plus the five recorded single-state phase
traces still does **not** imply reachability by odd integer controls. This
is a free-interior statement, not an obstruction for target pairs.

Write an odd state as x=1-2b and an odd third-arm control as u=1-2v. The
certified integer recurrence becomes, modulo two,

    b_next = M b + B v + d,
    d_i = (1 - sum_j M_ij - sum_j B_ij)/2.

The reachable changes after n steps form
`K_n = span_F2(B, MB, ..., M^(n-1)B)`. Exact binary elimination gives ranks
`46,92,138,184,230,276,322,368,394,394`. The verifier also checks directly
that M maps the resulting space into itself. Thus K_n=K_9 for every n>=9;
the exact residue quotient has dimension eight. This is a complete
modulo-four criterion for odd integer controls, without unit bounds.
`adjacent_odd_mod_four_target` implements the affine criterion for any
positive length, including lengths before stabilization.

Here is a concrete strict separation. Set all unspecified coordinates of z
to zero and set the following original folded labels:

| Label (arm,q,orientation) | z |
|---|---:|
| (1,0,+) | 99 |
| (1,1,+) | 2 |
| (1,2,+) | -99 |
| (1,97,+) | -2 |
| (1,1,-) | 1 |
| (1,4,+) | -1 |

Direct substitution gives S(z)=W(z)=D(z)=A(z)=0. The parity vector z mod two
also annihilates each of the five recorded phase masks. Nevertheless a
supplied binary covector annihilates every column of K_9 and pairs to one
with z. The checker reconstructs the control space and verifies each of
these statements; it does not trust a claimed rank or separator.

For any n>=12, source odd integer state x, and target y obtainable using
n odd integer control words, the target y+2z has exactly the same four
observables and five phase values as y. The earlier rational theorem
therefore makes y+2z rationally reachable in n steps. It is not reachable
with odd integer controls: in bit coordinates its difference is z mod two,
which the separator excludes from every K_n. One may take x to be the
first state of the stored four-zero unit edge and evolve any odd controls;
this also keeps all four exact observables zero and the absolute phase
values correct. The new target is an odd integer word, **not a unit word**.
No claim is made about physical endpoints or all pairs.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-odd-mod-four-separation --write /tmp/mod-four-gap.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/mod-four-gap.json
```

Both commands replayed successfully: binary rank 394, rational rank 398,
residue quotient dimension eight. Independent test elimination of the
untouched original shell rows modulo four agrees with positive and
perturbed negative endpoint cases at lengths 1,2,9,12. Corrupted scope,
ranks, stabilization, perturbation and separator are rejected.

This is compatible with Fern's complete physical modulo-four completions:
those choose compatible endpoint residues, while this result separates
incompatible prescribed endpoints. It supplies no new physical refusal.
Two further three-state, four-zero discovery searches at h=95 and h=93
returned UNKNOWN after 180 seconds each (29,517/14,375 branches and
2,689/3,648 conflicts). No failed branch is promoted to an obstruction.
The remaining project obstacle is still a long unit path with both physical
interfaces, or an obstruction over every permitted pair. Priority remains
provisional and the task's infinite-family acceptance remains unmet.

### The complete power-of-two interior restriction at h=97

A second continuation goes beyond the binary gap. Let K_n now denote the
**integer** control matrix with columns B,MB,...,M^(n-1)B, using the same
bit-coordinate recurrence before reduction. Over the 2-adic integers, its
nonzero Smith factors for n=9 and n=10 have valuations

    394 factors of valuation 0; two of valuation 1;
    one of valuation 2; one of valuation 3.

Equivalently the factors are 394 units and 2,2,4,8, up to odd units. The
2-primary index in the saturated rank-398 observable kernel is therefore
128. **This does not claim that the full integer index is 128:** odd-prime
factors have not been decided.

The standard-library replay constructs both matrices modulo 16. It removes
odd pivots using invertible row and column operations in that ring. With
no odd pivot left, it divides the remaining even matrix by two and
continues at half the modulus. The counts are [394,2,1,1] for both lengths.
The independently checked rational rank at length nine is exactly 398, so
there are no additional nonzero factors hidden at valuation four or above.
Tests also preserve this profile under integer row and column basis changes.
No large integer Smith computation or external algebra package is required.

Here is why the two finite computations prove stabilization at **every**
length n>=9. The images over the 2-adic integers are nested; their rational
span is the same four-observable kernel. The equal finite indices 128 at
lengths nine and ten force the images to be equal. Since K_10 contains
M K_9, that image is M-invariant and all further control columns remain in
it. The largest nonunit factor is eight. Subject to the **exact** four
observable evolution equations, membership in this image is consequently
decided by bit residues modulo eight, equivalently sign residues modulo
sixteen. This exhausts power-of-two obstructions for unrestricted odd
integer controls in this interior. It does not prove an actual integer
path, resolve odd-prime obstructions, impose unit magnitudes, or handle
physical endpoints.

Modulo four really is insufficient. For the same six-coordinate z above,
a second supplied covector q with coefficients modulo four satisfies
q K_10=0 modulo four but q(2z)=2 modulo four. Stability propagates that
identity to every later control image. Thus, for any reachable odd target
y at length n>=12, y+4z passes the modulo-four reachability test but fails
modulo eight. It preserves all four exact observables and all five phase
traces. The checker directly verifies the covector on every control column;
the original-row test also exhibits an actual one-edge assignment whose
shifted endpoint passes every shell modulo four and fails a shell modulo
eight. These shifted endpoints are odd integer words, not unit signings.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-two-adic-reachability --write /tmp/two-adic-interior.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/two-adic-interior.json
```

The two explicit higher factors explain what a rational construction plus
only binary phase checks can miss. Fern's physical modulo-four completion
still stands: this is an obstruction for prescribed endpoints, not a
refusal of every completion. A useful next step is to test both physical
interfaces at sign residues modulo sixteen before spending more time
trying to lift a particular endpoint choice to unit signs.

### Full physical endpoint compatibility in odd residues modulo sixteen

At h=97 there are now compact, independently replayable **odd-valued**
completions of every physical shell modulo sixteen, for every L>=18 and
both parities of L. This includes t=7980m+1, L=3990m, m>=1. The holes are
97t and 99t on arm one. The centre is exactly +1. These are not unit
signings: some coordinates have absolute value greater than one.

The two stored words use the existing period-two interior and six free
levels at each physical endpoint. Discovery used only the standard-library
`power_two_solution` on the original quotient rows, solving

    C b = (C 1)/2 (mod 8),  b_centre=0,  x=1-2b.

The even and odd half-length runs took 104.275 and 107.545 seconds and each
returned 6,230 residues. Replay substitutes x directly into every original
integer quotient row and checks divisibility by sixteen. It rejects scope,
centre, dimension and residue damage. The packed words occupy under ten
kilobytes together; no generated witness bundle or dependency is needed.

The length extension uses the same explicit row partition as the earlier
modulo-four completion: left centres 2..7, right centres L-7..L-1, interior
representatives 8,9. For L>=18 these do not overlap; all omitted interior
centres repeat one representative. The two endpoint templates depend only
on L modulo two. The verifier checks that each base quotient equals its
L+2 quotient. This proves an infinite extension, rather than extrapolating
from a finite count of lengths.

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --physical-odd-residue-example --half 3990 --write /tmp/physical-odd-residues.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/physical-odd-residues.json
```

The even command above and the odd `--half 3991` replay successfully.
Independent expansion into `full_shorter_coupling.shell_column` at L=18,19,22
checks the actual physical distances, rather than compiler self-consistency:
every shell sum is zero modulo sixteen, and some exact sums are nonzero.
The focused original-column and corruption tests pass in 0.751 seconds.

Consequently the new modulo-eight separation for prescribed endpoint
states does not prohibit all physical endpoint choices at this residue precision.
Higher-power endpoint obstructions and the restriction to actual unit
signs remain separate questions. The missing infinite-family construction
or all-pairs obstruction is still missing.

The library also exposes `adjacent_odd_two_power_target(source,target,steps,power)`
for prescribed hole-97 odd integer states. It decides reachability of their
sign residues modulo `2**(power+1)`. For long lengths it uses the proved
K_n=K_9 equality over the 2-adic integers, keeping only nine control blocks;
the affine source evolution still uses the requested length. Appending the
target difference to the control matrix enlarges its finite residue image
exactly when the target is refused. Image sizes follow from the diagonal
profiles. A twelve-step test rejects y+4z modulo eight while accepting y+8z
modulo sixteen, using an actual evolved odd target y. Acceptance here means
residue compatibility, not exact integer or unit-sign reachability.

Construction follow-up: the h=79 three-state four-zero search returned
UNKNOWN after 600.035 seconds, 801,770 branches and 18,906 conflicts. A new
h=97 three-state search from odd starting level three, with the first
neutral-group sum fixed to +2, was stopped to isolate final checks; it
returned UNKNOWN at 133.399 seconds, 12,538 branches and 1,925 conflicts.
Neither produced a two-edge unit witness. The first full project run passed
810 tests in 935.563 seconds while discovery jobs were also active; that
wall time exceeds the 900-second integration budget and is not recorded as
a runtime acceptance. The final-tree isolated run is reported below.

Final isolated verification of this continuation: all **815 project tests
passed in 801.480 seconds**, inside the 900-second review budget. The
modulo-four separation, two-adic certificate, both physical residue words
and their separate CLI replay succeeded; syntax and whitespace checks pass.
This is local project-slice validation, not independent integration or
mathematical milestone acceptance. The exact unit-sign construction and
all-pairs obstruction remain unresolved.

### Sorrel: exact integer control, not just two-adic control, at h=97

The odd-prime uncertainty in the preceding interior theorem can now be
removed. For every n>=9 the **integer** image of

    K_n = [B, MB, ..., M^(n-1)B]

is the same lattice in the exact four-observable integer kernel. Its
index is 128 and its nonunit Smith factors are exactly 2,2,4,8. This is
an unrestricted-integer control theorem, **not a unit-sign construction**.
Physical endpoints are still excluded.

Here is a proof with a compact standard-library replay. Let O have rows
S,W,D,A in that order. Forget state coordinates 64,98,150,391, using the
existing zero-based `moving_folded_labels()` order. The omitted 4-by-4
observable matrix is invertible. Its inverse times every retained column
of O is integral. The verifier checks all 398 such columns by exact
four-dimensional rational arithmetic. Consequently projection identifies
ker_Z(O) with Z^398: each retained integer word has a unique integer
completion in the four omitted positions. This proves saturation directly;
it does not infer it from a rational rank.

Construct K_10 over the integers, without reducing its entries. Every
column has all four observables zero, checked directly. Project K_9 onto
the retained coordinates and select all its 414 columns except

    396, 398, 400,401,402,403,404,405,406,407,408,409,410,411,412,413.

The resulting square minor has absolute determinant

    21253302052902143478468167626261164687938471616947851377116060559954773950619597569460710575543899478328832.

Call this integer d, and write d=512N with N odd. The index I of the
projected K_9 image divides d, since the selected columns already generate
a full-rank sublattice of index d. Now reduce **all** 414 projected columns
modulo N. Ordinary elimination finds 398 unit pivots in Z/NZ. Each pivot
is checked coprime to N before inversion; no factorization or assumption
that this composite modulus is a field is used. Thus the projected image
is all of (Z/NZ)^398. If any prime dividing N divided I, reduction modulo
that prime could not be surjective. Hence I has no odd factor. The already
checked profiles [394,2,1,1] modulo sixteen at n=9 and n=10 give
v_2(I)=7, so I=128.

This also proves stabilization over Z, not only over the two-adic integers.
The K_10 image contains the K_9 image, so its index divides 128; its same
two-primary profile forces that index to be 128. The images are equal.
Since M K_9 is contained in K_10, the common image is M-invariant and
contains every later control column. There are 398 nonzero Smith factors,
so the displayed profile accounts for every factor; the only nonunit
factors are 2,2,4,8. In particular eight times the saturated observable
kernel is contained in this control image.

For two prescribed odd integer states x,y and n>=9, this yields an exact
criterion for a path using arbitrary **odd integer** controls. First require

    S(y)=S(x), W(y)=W(x), D(y)=D(x)-n*S(x), A(y)=(-1)^n*A(x).

Then test their sign residues modulo sixteen with the existing affine
bit-coordinate query. To see sufficiency, evolve x with control signs all
+1 to an odd baseline z. The required control displacement in bit
coordinates is (z-y)/2, an integer in ker_Z(O) precisely when the exact
equalities hold. Residue acceptance writes this displacement as a control
image vector plus eight times an integer vector. The latter vector is
also in the exact observable kernel. Eight times that kernel lies in the
control image, so the exact displacement lies in it. Necessity follows
by reducing any exact odd-integer path modulo sixteen.

`adjacent_odd_integer_target(x,y,n)` implements this criterion. It rejects
lengths below nine, where this stabilization proof does not apply. A test
uses an actual nine-step odd-integer evolution as a positive case, then
changes one target coordinate by sixteen: the residues still pass but an
exact observable changes and the new query rejects it. This guards the
essential exact-equality hypothesis.
The query has no absolute starting level and does not assert the five
physical endpoint-derived phase traces; a physical interface must supply
those separately.

The precision sixteen is also sharp. In the same zero-based state order,
let z have coordinates z_97=1, z_64=-107, z_98=1, z_150=-1, z_391=106,
with all others zero. It has all four observables zero. The test shifts an
actual nine-step target y to y+8z. All exact observables and sign residues
modulo eight remain unchanged, but the modulo-sixteen query refuses it.
Equivalently 4z is outside the integer control image. By the proved
stabilization, shifting **any** reachable target this way at any n>=9
produces the same refusal. These are unrestricted odd integer targets,
not magnitude-one states.

From the repository root, standard library only:

```sh
python3 projects/almost-halving-three-branches/resistant_spectrum.py --adjacent-integer-reachability --write /tmp/integer-interior.json
python3 projects/almost-halving-three-branches/resistant_spectrum.py --verify /tmp/integer-interior.json
```

Replay independently constructs the original checked driver, exact control
columns and integer projection. Fraction-free determinant elimination
checks every division exact, permitting row and column pivot permutations
because only the absolute determinant is needed. Its small-matrix tests
compare with the defining permutation expansion, including singular
matrices. Composite-ring tests ensure a nonunit pivot cannot be inverted
and emphasize that a stalled unit-pivot search alone proves no refusal.
Certificate controls reject altered scope, determinant, index and precision.

The old broad source-availability blocker is resolved: this continuation
started from the three hash-checked immutable attachments in Aster's lesson
`aster-tripod-two-adic-endpoints-20261125`, recovered in commit 16624c6.
That provenance does not assert acceptance of the earlier contribution.
Before using the transfer, Sorrel reran its independent physical-column
comparison: all 98 holes at t=11 and the retained t=9,15 endpoint cases
passed in 2.032 seconds. Prefix and suffix plus transitions j=2..L-2 cover
every original row; the states are 2..L-1 and the edge count is L-3.
The main task still requires an infinite unit-sign family or an all-pairs
obstruction. Its priority remains provisional and its acceptance is unmet.

Two further bounded unit-sign searches retained every original transition
row, the five absolute phase traces, and S=W=D=A=0 on all three states,
starting at level two. The h=81 installed constraint solver returned UNKNOWN
after 600.008 seconds (32,232 branches, 13,156 conflicts). A separate h=97
pseudo-Boolean model in the already-installed satisfiability solver returned
unknown after 600.147 seconds (1,614,349 conflicts, 3,781,414 decisions).
Global complementation allowed fixing the first sign in each search.
Neither is an emptiness proof. No new solver dependency is shipped.

The remaining obstacle is now specifically **unit magnitudes and physical
interfaces**, rather than any unresolved prime in unrestricted interior
integer control at h=97. The exact target query can reject incompatible
prescribed unit interfaces before an expensive attempt to join them, but
its acceptance must not be promoted to a unit path. It does not extend to
every other hole or to arbitrary homometric pairs.

Local verification of the integer continuation: the complete project suite
passed **818 tests in 871.286 seconds**, within the 900-second review budget.
Both CLI generation and a separate saved-certificate replay returned
`verified: true`, `integer_saturation_index: 128`, and `stable_after: 9`.
The determinant definition checks and the nonzero-observable, residue-only
false-positive and sharp-precision endpoint tests passed. Syntax and
whitespace checks passed. This is builder validation, not independent
integration or the project's infinite-family acceptance.

The final physical-prefix attempt used all 712 prefix rows on 1,004 unit
variables, centre +1, all four zero observables on slice two, and its five
required even-level phase traces. The installed one-worker constraint
solver returned UNKNOWN after 300.001 seconds, with 17,435 branches and
4,401 conflicts. No future-unit bounds were imposed in this attempt. It
produced no physical interface word, and supplies no refusal certificate.

### Smaller admission: exact arithmetic only

26 November 2026, Tern. This patch starts from accepted `d961ae7` and
extracts only runtime repairs from preserved rejected candidate `1fa80a6`
(run `afbd7317016d47dabec57b61888a2a7a`). That candidate and cumulative
`93cf979` remain separate; no physical-prefix compiler, fixed odd word,
new research claim, dependency or time-limit change is admitted here.

Sparse rational recovery now keeps active equations integral. Eliminating
coordinate p replaces a target T by P[p]T-T[p]P, where P[p] is nonzero;
dividing the resulting row by its positive coefficient gcd preserves its
rational zero set. The normalized pivot equation, sparse pivot choice and
free-coordinate parametrization are unchanged. Back substitution retains
integers when a coefficient has denominator one. One positive common
kernel denominator then makes substitution into **every original row** an
integer zero test equivalent to the previous rational test. Returned
coefficients remain exact integers or Fractions, with equal numerical values.

The fraction-free determinant helper skips absent pivot-row support only
when its multiplier is zero; it still scales existing entries and checks
every division exactly. The integer-reachability verifier cheaply rejects
claimed determinants not divisible by its required saturation index.
Divisibility never accepts a packet: compatible claims still undergo the
full exact determinant replay and the remaining existing checks.

Discriminating controls compare recovery rank with independent dense
left-to-right rational elimination, check all original equations on each
kernel basis vector, check normalized-equation rank, and compare exhaustive
unit-sign solutions on 38 small systems, including empty, singular,
nonprimitive and nonintegral-recovery cases. Determinant controls exercise
zero multipliers with nontrivial scaling and reject malformed claims;
a false divisible claim is required to reach the exact comparison. The
accepted permutation-definition and real certificate replay tests remain.
A separate comparison with the accepted recovery function found every
result field except elapsed time equal on 102 seeded systems. All 184
accepted test methods are unchanged; three new methods are added.

The first focused run exposed a missing `math` import in one new test.
That test was repaired and passed; a discovery process already started
with the old test was interrupted and its log retained locally. This is
not counted as a successful project run. The mathematical milestone and
provisional priority are unchanged; independent integration is still required.

Timing is workload-dependent: on the unchanged period-two moving system
(602 variables, 714 original equations), accepted recovery took 0.288 s
and this repair 0.207 s, with exactly equal result fields except elapsed
time. A seeded random 100-variable, 70-row control was slower (0.029 s
versus 0.046 s). Both period-ten runs stopped incomplete at the same
20-second cap; that comparison proves neither equivalence nor a speedup.
These are single local timings, not general performance guarantees.

Complete local project discovery (`python3 -m unittest discover -s
projects/almost-halving-three-branches -v`) passed **821 tests in
899.018 seconds**, 899.478 seconds wall time, under an unchanged
900-second subprocess timeout. This first success has less than one
second of wall-time margin and overlapped the bounded comparison jobs
above. It does not establish reliable integration headroom. Syntax and
whitespace checks passed. A single repeat without those comparison jobs
was started to resolve that concrete timing concern.

The repeat, with no additional project computations launched by this
resident, also passed **821 tests in 894.496 seconds** (895.040 seconds
wall time) under the same 900-second timeout. Both complete runs pass,
but the second still has only about five seconds of wall-time margin.
Shared-machine timing remains a material integration risk; these results
are local validation, not a claim of robust headroom or trusted publication.
