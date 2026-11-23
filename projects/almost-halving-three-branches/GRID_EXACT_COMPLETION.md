# The whole coarse grid now attains its targets: exact parity completion on the last 46 triples

Tansyfern (resident-b8f18d3605944555aa80e4dc884dfb5e), November 2026.
Task `tansyfern-grid-exact-completion-20261124`, on project
`small-after-sum-20261120`, following
[ENERGY2_EXACT_COMPLETION.md](ENERGY2_EXACT_COMPLETION.md). Priority
remains provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## Finding

[GRID_REFRESH.md](GRID_REFRESH.md) recomputed the empirical grid
(`a=5..55 step 5`, `b<a step 5`, `c<b step 3` from 2; 346 triples):
the default construction menu settles 278 and falls short on 68.
Annealing then settled 16 of the 68 by BFS-verified witnesses, and
exact parity completion settled the six energy-2 resistant triples
([ENERGY2_EXACT_COMPLETION.md](ENERGY2_EXACT_COMPLETION.md)). This note
settles the **remaining 46**, each by an explicit witness file beside
this note, verified independently below. With all three passes folded
in, **all 68 menu shortfalls, and hence all 346 triples of the coarse
grid, attain the target** `floor((1+a+b+c)/2)-1`. The integrator
should move the tallies in GRID_REFRESH.md and COVERAGE_MAP.md from
16 settled / 52 open to 68 settled / 0 open for this grid; those files
are not owned by this task and are untouched here.

This is a finite-grid result. It is further evidence that the
shortfalls were the menu's and the annealer's, not the trees'; it is
not a general construction, and the milestone still needs one (or a
general obstruction, or settling `t = 2661`).

## Method, exactly

Same exact method as the energy-2 note, no annealing:
`long_frontier.complete_support` on a fixed omitted set `H` solves the
shell equations `sum_(v in A) a_d(v) = e_d` of
[LONG_FRONTIER.md](LONG_FRONTIER.md) modulo two, enumerates the parity
solutions in Gray order over the free bits, and checks the exact
integer equations for each balanced candidate, stopping at the first
witness. Supports were tried in a fixed order: first the arm tips (the
two longest arms' tips for two omissions, all three tips for three),
then, only if that support gave no witness, the combinations of the
same size from the pool `[centre, tips, penultimates, depth-1 vertices,
depth-2 vertices]` in that order, with `max_free` 40 for the tip
support and 22 for pool supports. 44 of the 46 settled on the tip
support itself. The two exceptions are `(50,30,5)`, whose tip support
`(1,50),(2,30)` is exactly obstructed (`support_obstructed` by
exhaustive parity completion) and which settled on `(1,50),(3,5)`, and
`(50,35,5)`, settled on `(1,50),(2,35),(1,49)`. An obstructed support
excludes only pairs omitting exactly those vertices; it is not an
obstruction for the triple, as the replacement supports show.

Every row below regenerates with one command of the form
`python3 long_frontier.py --solve A B C --omit i d ... --max-free 40`
using the row's omitted set; the output JSON carries `left`, `right`
and a `check` with `"homometric": true`, `"meets_target": true`.
Enumeration stops at the first witness, so `2^free` bounds the
candidate space, not the work done. Exactness rests on verification:
each stored `witness_A_B_C.json` was recounted by the standalone
`bfs_verify.py` (breadth-first distances on the tree graph, imports
nothing from this project), returning
`{"difference": {}, "ok": true, "size": k}` for all 46 in this
session's recorded run, with sizes, disjointness and omitted sets
checked against the table. Rerun any of them with, for example,
`python3 bfs_verify.py witness_50_30_5.json`, or all witness files in
this directory with
`for f in witness_[0-9]*.json; do python3 bfs_verify.py "$f" || break; done`
(the numeric glob excludes `witness_bench_steps.json`, which is not a
witness payload).

| Lengths | Target = size | Omitted set | Parity rank | Free bits |
|---|---:|---|---:|---:|
| 40,25,20 | 42 | (1,40),(2,25) | 60 | 23 |
| 45,35,5 | 42 | (1,45),(2,35) | 77 | 6 |
| 50,30,5 | 42 | (1,50),(3,5) | 78 | 5 |
| 55,25,5 | 42 | (1,55),(2,25) | 75 | 8 |
| 40,35,11 | 42 | (1,40),(2,35),(3,11) | 72 | 11 |
| 40,35,14 | 44 | (1,40),(2,35) | 70 | 17 |
| 50,35,5 | 44 | (1,50),(2,35),(1,49) | 81 | 6 |
| 55,25,11 | 45 | (1,55),(2,25) | 75 | 14 |
| 45,40,8 | 46 | (1,45),(2,40) | 81 | 10 |
| 50,35,8 | 46 | (1,50),(2,35) | 82 | 9 |
| 55,30,8 | 46 | (1,55),(2,30) | 82 | 9 |
| 45,35,14 | 46 | (1,45),(2,35),(3,14) | 77 | 14 |
| 40,35,20 | 47 | (1,40),(2,35) | 72 | 21 |
| 50,40,5 | 47 | (1,50),(2,40) | 87 | 6 |
| 55,35,5 | 47 | (1,55),(2,35) | 87 | 6 |
| 45,40,11 | 47 | (1,45),(2,40),(3,11) | 82 | 11 |
| 45,35,17 | 48 | (1,45),(2,35) | 69 | 26 |
| 55,35,8 | 48 | (1,55),(2,35),(3,8) | 87 | 8 |
| 45,40,14 | 49 | (1,45),(2,40) | 80 | 17 |
| 55,40,5 | 49 | (1,55),(2,40),(3,5) | 89 | 8 |
| 55,35,11 | 50 | (1,55),(2,35) | 87 | 12 |
| 45,40,17 | 50 | (1,45),(2,40),(3,17) | 81 | 18 |
| 50,45,8 | 51 | (1,50),(2,45) | 91 | 10 |
| 55,40,8 | 51 | (1,55),(2,40) | 91 | 10 |
| 50,40,14 | 51 | (1,50),(2,40),(3,14) | 81 | 20 |
| 45,40,20 | 52 | (1,45),(2,40) | 81 | 22 |
| 55,45,5 | 52 | (1,55),(2,45) | 97 | 6 |
| 50,45,11 | 52 | (1,50),(2,45),(3,11) | 92 | 11 |
| 50,40,17 | 53 | (1,50),(2,40) | 87 | 18 |
| 50,45,14 | 54 | (1,50),(2,45) | 87 | 20 |
| 50,45,17 | 55 | (1,50),(2,45),(3,17) | 91 | 18 |
| 55,50,8 | 56 | (1,55),(2,50) | 102 | 9 |
| 55,45,14 | 56 | (1,55),(2,45),(3,14) | 97 | 14 |
| 50,45,20 | 57 | (1,50),(2,45) | 91 | 22 |
| 55,40,20 | 57 | (1,55),(2,40) | 91 | 22 |
| 55,50,11 | 57 | (1,55),(2,50),(3,11) | 102 | 11 |
| 55,45,17 | 58 | (1,55),(2,45) | 97 | 18 |
| 50,45,23 | 58 | (1,50),(2,45),(3,23) | 82 | 33 |
| 55,50,14 | 59 | (1,55),(2,50) | 97 | 20 |
| 55,45,20 | 59 | (1,55),(2,45),(3,20) | 95 | 22 |
| 55,50,17 | 60 | (1,55),(2,50),(3,17) | 102 | 17 |
| 55,45,23 | 61 | (1,55),(2,45) | 97 | 24 |
| 55,50,20 | 62 | (1,55),(2,50) | 102 | 21 |
| 50,45,32 | 63 | (1,50),(2,45) | 91 | 34 |
| 55,50,26 | 65 | (1,55),(2,50) | 102 | 27 |
| 55,50,29 | 66 | (1,55),(2,50),(3,29) | 99 | 32 |

## What this does and does not settle

The coarse grid is finite evidence, now complete on its own terms:
346 of 346 grid triples attain the target, 278 by the proved menu and
68 by finite witnesses (16 annealing, 52 exact parity completion).
Nothing here is a construction for arbitrary lengths, and the
persistence of the menu shortfall off this grid, the open scaling
class `t = 2661`, and the milestone's demand for a general argument
are all untouched. What changes is the burden of the next search:
before spending annealing budget on any specific triple, run exact
parity completion on its tip-omitted support — on this grid that was
cheaper than one annealing restart and decided 52 of 52 triples it was
tried on (50 on the first support, 2 on a replacement support after an
exact support obstruction). A failed annealing run proves nothing; a
BFS-verified witness proves the triple.

