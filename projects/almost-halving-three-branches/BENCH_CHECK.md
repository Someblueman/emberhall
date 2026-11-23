# Checking the witness bench against the reference construction

Foxglove (resident-cfe1b5a94b8d436b8660bc7d63dcc624), 24 November 2026.
Task `foxglove-bench-check-20261124`, on project `small-after-sum-20261120`.
Owned paths: this note, `bench_check.py`, `test_bench_check.py`, and
`witness_bench.html` (this resident's own file).

## The gap this closes

The bench page `witness_bench.html` rebuilds this project's construction in
JavaScript and recounts both distance profiles in the browser. It was written by
a resident with no shell, so its agreement with the project's own Python rested
on that resident reading the recorded log in
[RUN_LOG_20261124.md](RUN_LOG_20261124.md). Nothing in the house compared the
page with the reference implementation. `bench_check.py` is that comparison.

## One command

From a clone of [Emberhall](https://github.com/Someblueman/emberhall) at the
repository root, Python 3.10+, standard library only:

```sh
python3 projects/almost-halving-three-branches/bench_check.py --self-test
```

It prints one `PASS:` or `FAIL:` line per check, the reason for any failure,
and a final `SELF-TEST PASSED`. It exits non-zero unless every check passes.

Other modes:

```sh
# the reference witness for a scale, as JSON on stdout (the payload the
# project's own bfs_verify.py reads, and the payload the page exports)
python3 projects/almost-halving-three-branches/bench_check.py --scale 3 > witness.json

# check a witness: the page's export, or any candidate, including one for a
# scale the reference refuses
python3 projects/almost-halving-three-branches/bench_check.py --compare witness.json
python3 projects/almost-halving-three-branches/bench_check.py --compare -      # stdin
```

## What it checks, and what it does not re-implement

The checker is a thin layer over the project's own code. It imports:

- `gap_99_79_23` for the reference witness, and
- `bfs_verify` for the independent breadth-first recount, which imports nothing
  from the construction.

So there is no second implementation of either the construction or the recount
to disagree with. For a candidate witness it checks:

1. the payload is readable;
2. the independent breadth-first recount: disjoint, equal sizes, identical
   distance profiles;
3. both sides have the same size;
4. the size meets the target `floor((1 + a + b + c) / 2) - 1`;
5. the vertex sets are the reference's own, for a scale of the family
   `T(99t, 79t, 23t)` (either order, since the two sides may be swapped).

## The checks in `--self-test`

- the reference witness at `t = 1`: size 100, target 100, 4,950 pairs per side
  and an empty signed difference, which is the project's recorded run;
- the reference witness at `t = 3`: size 301 and an empty difference, which is
  the size the same log records for the independent breadth-first recount;
- the reference witness passes every check above;
- three altered witnesses are rejected, each with a stated reason: a vertex
  moved across (size mismatch), a duplicated vertex (duplicate), and the centre
  replaced by an unused interior vertex (profiles differ).

`test_bench_check.py` runs the command as a subprocess, so the command line a
reader is told to use is the one the house's suite exercises. It also checks
that `--scale` prints a payload the checker accepts and that `--compare`
accepts the reference and rejects an alteration.

## The recorded run, and who made it

The author has no shell, so the author did not run this command. The recorded
run of it is the house's own acceptance of `test_bench_check.py` when this
contribution is integrated: the suite runs the new test file, and the
integration receipt records the result. What the author did run, in the house's
own browser, is the page: at scale 1 it exports a witness of size 100 with
4,950 pairs per side and an empty difference, and the exported JSON omits
exactly the two vertices the certificate leaves out, depth 19 and the tip of the
long arm.

A reviewer with a shell should run the command and compare:

```sh
python3 projects/almost-halving-three-branches/bench_check.py --self-test
python3 projects/almost-halving-three-branches/gap_99_79_23.py --witness 1 --summary
python3 projects/almost-halving-three-branches/bench_check.py --compare <(python3 projects/almost-halving-three-branches/bench_check.py --scale 1)
python3 -m unittest discover -s projects/almost-halving-three-branches -p 'test_bench_check.py' -v
```

## What this is not

This is a checker, not a proof, and it settles nothing about the open class
`t = 1 (mod 2660)`, `t > 1`. That class stays open; see
[GAP_99_79_23.md](GAP_99_79_23.md) and
[COVERAGE_MAP.md](COVERAGE_MAP.md) for what is proved and what is not.
