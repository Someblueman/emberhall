# `exact_completion.py`: exact parity completion for a fresh triple, one command

Tansyfern, November 2026. Task `tansyfern-exact-completion-tool-20261124`.
This packages the method of [ENERGY2_EXACT_COMPLETION.md](ENERGY2_EXACT_COMPLETION.md)
and [GRID_EXACT_COMPLETION.md](GRID_EXACT_COMPLETION.md) so any triple,
not only grid triples, can be tried the same way. Standard library only;
run from this directory.

```sh
python3 exact_completion.py 61 38 17 --out witness_61_38_17.json
python3 bfs_verify.py witness_61_38_17.json
```

Real recorded run in this session (the triple is off the coarse grid):

```text
{"bfs_ok": true, "free_bits": 18, "lengths": [61, 38, 17], "omitted": [[1, 61], [2, 38], [3, 17]], "parity_rank": 95, "size": 57, "status": "witness", "supports_tried": 1, "wrote": "witness_61_38_17.json"}
{"difference": {}, "ok": true, "size": 57}
```

The command tries the tip-omitted support first, then combinations of
the same size from the pool `[centre, tips, penultimates, depth-1,
depth-2 vertices]`, calling `long_frontier.complete_support` on each.
Any witness is recounted by `bfs_verify` before it is reported or
written; a solver output that fails the recount raises an error rather
than being written.

Exit codes: `0` means a BFS-verified witness at target size
`floor((1+a+b+c)/2)-1`; `1` means no witness on the supports tried.
Exit `1` is never an obstruction for the triple — the summary prints
`"all_omissions_obstructed": false` and counts how many tried supports
were exactly obstructed for that support versus inconclusive. The one
documented pool fallback is in the tests: on `(50,30,5)` the tip
support is obstructed and the pool finds `(1,50),(3,5)`.

Costs are honest: enumeration stops at the first witness, which on the
52 grid triples and the fresh triples above arrived in seconds, but a
support whose first witness is late — or absent — can enumerate for a
long time when its free-bit count is large. `(100,63,29)` did not
finish in 60 s at the default cap in this session. Lower `--max-free`
(and `--pool-max-free`) to trade completeness for a prompt
`inconclusive`, or cap wall-clock per support with `--per-support
SECONDS` (SIGALRM, main thread; a clear error where unsupported): an
overrun support is counted `timed_out` and skipped, which is
inconclusive for that support and never an obstruction. Without the
flag, behaviour and output are unchanged. Recorded runs (Lupin,
November 2026; see also
[BROADER_SUPPORT_SWEEP.md](BROADER_SUPPORT_SWEEP.md), whose winners
needed 42–65 free bits against the shipped caps of 40/22):

```text
$ python3 exact_completion.py 80 70 50 --max-free 80 --no-pool --per-support 5
{"all_omissions_obstructed": false, "lengths": [80, 70, 50], "size": 99, "status": "no_witness_on_tried_supports", "supports_tried": 1, "verdicts": {"inconclusive": 0, "support_obstructed": 0, "timed_out": 1}}
```

(The uncapped tip support of `(80,70,50)` finds its witness at about
17 s, so a 5 s cap honestly loses it.) With raised free-bit caps and a
2 s per-support cap, the CLI walks past slow pool supports to the same
witness the rim-4 sweep found, at small-pool support 124, in 140 s:

```text
$ python3 exact_completion.py 100 80 50 --max-free 80 --pool-max-free 80 --per-support 2 --out /tmp/w100_cli.json
{"bfs_ok": true, "free_bits": 50, "lengths": [100, 80, 50], "omitted": [[2, 80], [3, 50], [3, 49]], "parity_rank": 177, "size": 114, "status": "witness", "supports_tried": 124, "wrote": "/tmp/w100_cli.json"}
```

```text
$ python3 exact_completion.py 100 63 29 --max-free 20 --no-pool
{"all_omissions_obstructed": false, "lengths": [100, 63, 29], "size": 95, "status": "no_witness_on_tried_supports", "supports_tried": 1, "verdicts": {"inconclusive": 1, "support_obstructed": 0}}
```

Tests: `python3 -m unittest test_exact_completion -v` (7 tests, recorded
OK November 2026) cover a tip-support witness, the `(50,30,5)` pool
fallback, support ordering without repeats, CLI writing, rejection
of non-positive lengths, and the per-support cap (firing and counting
`timed_out`, leaving fast supports alone, rejecting bad values).

Finite witnesses settle single triples. This tool is a cheaper first
exact step than annealing for a named triple; the general construction
the milestone asks for is still open.
