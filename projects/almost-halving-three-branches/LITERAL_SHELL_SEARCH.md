# Literal search against the complete shell equations

Tern, 24 November 2026. A bounded finite experiment on the universal tree
milestone, not an all-scale theorem. The preceding balance and middle
constraints remain necessary subsystems; this search includes **every**
exact shell row and requires every occupied sign to be +/-1.

## Actual finite results

On T(99,79,23), omit the first-arm tip99 and either the centre (h=0) or
depth1 (h=1). Exhaustive exact search proves **no balanced homometric
signing with these exact holes**, including both global orientations:

| shallow hole | occupied vertices | shell rows | search nodes | result |
| ---: | ---: | ---: | ---: | --- |
| 0 (centre) | 200 | 178 | 5440 | unsat |
| 1 | 200 | 178 | 53214 | unsat |

The recorded commands used100000 nodes and30 search seconds. Runs took
0.37 and4.63 seconds including table compilation on this machine.
The centre case is already excluded by the existing bipartition test in
`long_frontier.complete_support`; this independent integer-row run is not
a new centre-hole theorem. At depth1 that tool reports23 free parity bits
after complementation, so parity consistency alone does not settle it.
These computations do not concern the known size100 witness, whose second
hole is first-arm depth19. Fixing only its23 third-arm signs and centre,
the solver fills all176 unknown signs on the two longer arms in297 nodes
and returns the actual witness in0.15 seconds. Independent adjacency breadth-first distance counting verifies
equal cardinalities100 and equal distance multisets. Swapping one sign
of each kind preserves balance and is rejected by that independent counter.
Unseeded depth19 search at100000 nodes returns **unknown**, not unsat.

## Why an exhausted search is a finite proof

The exact shell column is the already proved coefficient of
K=(1-z)F-2zS. Each occupied vertex is one literal variable. For every
exponent e, require sum c_(e,v)*s_v=0. K(1)=-2S, so complete shell
vanishing also forces balance; balanced vanishing gives homometry by the
project's shell identity. The output candidate is additionally checked
for balance and all shell rows before any sat result is returned.

For each sparse row, enumerate all local sign patterns with row sum zero.
Propagation filters its pattern table by each assigned variable. An empty
table is a genuine contradiction. If every remaining pattern agrees on a
variable, that variable is forced. These operations remove no solution.
An explicit search stack tries both signs for each selected variable and
restores all changed assignments/tables before trying the other branch.
Exhausting that stack therefore excludes all literal assignments. With
no seeds, fix one sign positive: global reversal preserves every homogeneous
row and maps any omitted negative orientation into the searched half.
With fixed seeds no global orientation is discarded.

Node or time exhaustion returns unknown, without a candidate or negative
existence claim. The time limit is checked at search-node boundaries;
pattern-table compilation is included in elapsed time, outside that search
budget. Row width is limited to16 and the geometry wrapper to5000 occupied
vertices; this is a boundary-scale experiment, not a claimed solver for
the resistant t2661 instance. An explicit stack avoids treating a language
recursion limit as mathematical impossibility. Each engine is used once.

The eight tests compare random small homogeneous systems with exhaustive
literal enumeration, including fixed seeds; independently derive **every
matrix column** at h0,h1,h19 from adjacency distances rather than the
polynomial formula; reproduce the two unsat cases; recover and independently
check the known witness; and verify that a zero search budget returns unknown.
There is no large stored search trace: the standard-library program reruns
the finite proof from its equations. No new dependency is required.

## Reproduce

    python3 projects/almost-halving-three-branches/literal_shell_search.py 1 0 --nodes 100000 --seconds 30
    python3 projects/almost-halving-three-branches/literal_shell_search.py 1 1 --nodes 100000 --seconds 30
    python3 projects/almost-halving-three-branches/literal_shell_search.py 1 19 --arm3='+-+-----------------+-+' --centre -1 --seconds 10
    python3 -m unittest discover -s projects/almost-halving-three-branches -p test_literal_shell_search.py -v

CLI arguments are t,h; holes are exactly first-arm tip99t and depth h,
with h0 meaning the centre. The underlying column geometry accepts
0<=h<=20t-1. A sat result contains literal left/right vertex arrays; an
unsat result is restricted to these exact parameters; unknown settles
nothing. --arm2 and --arm3 accept fixed literal words; --centre fixes its
sign. For a word starting with minus use the equals form shown above.
These supplied signs are reported as seeded_vertices, not silently counted
as newly found signs. --third-first changes only the branching order.

## The bounded comparison and a slower propagation experiment

At t1, each h2..19 was tried with250000 nodes and10 search seconds;
every run returned unknown, reaching roughly65000..104000 nodes. This
settles none of those holes. The source can also propagate reduced exact
parity equations with --parity: write s=2x-1, divide each integer row by
two and reduce modulo two, then use Gaussian elimination and back
substitution over the two-element field. A parity row with one unknown
forces it; a fully assigned wrong row contradicts the current branch.
The complete shell system also implies balanced cardinality, so its parity
row is included. All added equations are necessary; the original integer
tables remain in force. Global reversal still preserves them. Random tiny
systems exhaustively check this hybrid and alternative variable orders.

In separate noncontrolled runs, depth1 still proves unsat, with48678 nodes
but8.30 seconds, compared with53214 nodes and4.63 seconds without parity.
Depth19 remains unknown at100000 nodes with either mode. This is not a
speed claim; extra propagation reduced nodes but cost more time in the
observed case. It stays optional. Third-arm-first branching also returned
unknown at100000 nodes; the seeded third-word control above is a genuine
positive result, whereas none of these unseeded limits is negative evidence.
The old parity/Gray-code completion tool remains useful; this alternative
search prunes exact integer row tables during partial assignments instead
of waiting to check a complete parity candidate.


## A finite route toward retaining only the shortest word

    python3 projects/almost-halving-three-branches/literal_shell_search.py 3 19 --two-arm-rank

Condition on the whole third arm and occupied centre, leaving only first-
and second-arm columns in the complete homogeneous shell system. Exact
Gaussian elimination over the prime field101 finds full column rank532
at t3,h19. The same exact computation at t11,h19 gives full rank1956
of1956 unknown columns, taking72.16 seconds in the recorded direct run.
A nonzero full-column minor modulo101 is also nonzero over the
rationals, so this proves at most one rational completion for every choice
of retained third word and centre **at each of these two exact scales and this hole placement**.
It proves neither literalness nor existence. A rank loss modulo101 only
gives an upper bound on rational nullity, not a rational kernel; a test
uses diagonal(101,1) to preserve this distinction. At t1,h19 the modular
rank is175 of176, so this method alone does not prove injectivity there.
The known literal signing is still recovered by the seeded search.

This route could reduce retained signs from a long second word plus seed
to the23t-sign shortest word plus centre, if an all-scale theorem can be
proved. The current finite result does not establish that theorem. It
suggests deriving two-arm transfer recurrences and checking their endpoint
determinant on the resistant scales, rather than extrapolating a rank table.
The extra optional --two-arm-rank mode runs instead of the sign search;
its arithmetic is exact and the same5000-occupied-vertex boundary applies.
