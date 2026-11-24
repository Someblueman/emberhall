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
