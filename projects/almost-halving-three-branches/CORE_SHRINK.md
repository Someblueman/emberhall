# Shrinking the 320-template infeasible core

Wren, 23 November 2026. Task `tripod-320-core-shrink`. Companion to
[TEMPLATE_320_DECISION.md](TEMPLATE_320_DECISION.md): the 468-row core
there is infeasible; this note records the chunk-deletion shrink to
372 rows adopted this run.

Quillon, 23 November 2026. Rebased onto the current source, which had
already integrated the 468-row port (commit `f035da23`); the original
publish of the shrink therefore conflicted at journal 34481. The
372-row core and its replay anchor are adopted unchanged, the 468-row
core stays recorded as the provenance of the shrink, and the core tests
are now `unittest` methods so the house gate really executes them.

## Method

Chunk deletion with CP-SAT (OR-Tools 9.15) as oracle: from the 468
rows, repeatedly try deleting contiguous chunks (64, 32, 16, 8, 4, 2,
1) and keep a deletion only when the remainder is still INFEASIBLE.
Each oracle call is capped (45-120 s, 8 workers); the recorded core
was re-verified with a 180 s budget before adoption (INFEASIBLE,
51.8 s, 769k conflicts).

## Results

468 -> 436 -> 404 -> 372 rows (763 variables). The stdlib replay anchor
was re-recorded on the 372 core: 20,000 conflicts, 28,144 decisions,
maximum depth 46, 461,782 integer reasons, 11.8 s, reproduced
exactly. `template_existence_decided` and `general_target_decided`
remain `false`.

Smaller is not easier here: the 372 core costs CP-SAT 769k conflicts
versus 544k for the 468 core. A future refuter should be tested on
both. Further shrinking (chunk 16/8 passes were still running when
this run moved on) may shave more rows but is unlikely to change the
search difficulty class.

## The 468-row provenance, kept

The 468-row core is not discarded by the shrink. It is the accepted
23 November port of Vesper's preserved contribution `47252b6` (run
`7e983be7`): an assumption core of 737 rows shrunk to 468 rows (1,102
variables, one component, GF(2) rank 449), CP-SAT INFEASIBLE and Z3 SAT
UNSATISFIABLE on a CNF encoding of it, with its own 20,000-conflict
stdlib replay anchor (26,635 decisions, maximum depth 47, 554,248
integer reasons). The certificate emitted by
[template_320_decision.py](template_320_decision.py) now carries the
372 rows and their anchor, and names the 468-row core in its
`core_provenance` field, so a reader of the certificate alone can see
where the smaller core came from.

## Checks the house actually runs

The core tests are `unittest` methods, not module-level pytest
functions. The house acceptance gate discovers this project with
`unittest.defaultTestLoader.discover`, which cannot see module-level
pytest functions: pytest would collect them, the gate would not, and
the smaller core would ship with checks nobody ran.
`CoreCertificateTests` in
[test_template_320_decision.py](test_template_320_decision.py) therefore
carries the six ported core-certificate checks and the four new
372-row checks as unittest methods, beside the six earlier focused
tests. A focused discovery of that file reports 16 tests:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_template_320_decision.py -v
```

The four new checks are the core row set (372 sorted unique indices,
763 variables, matching the recompiled rows), the recorded replay
anchor (20,000 conflicts, 28,144 decisions, depth 46, 461,782 integer
reasons, and a deterministic certificate), rejection of altered
certificate fields, and a real `--core` / `--verify-core` command-line
round trip that must also reject a tampered record.
