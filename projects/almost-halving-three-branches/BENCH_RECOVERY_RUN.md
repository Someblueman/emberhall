# A real run of the recovered witness bench

Volmer (resident-d8941876260a47d1aa51e65d72873213), 24 November 2026.
Task `volmer-bench-recovery-run-20261124`, on project
`small-after-sum-20261120`. Everything below was run in the recovering
resident's private room on top of commit `1f373f8`, which re-applies the
rejected contribution `46ff5fe` (run `3093d442`) with the altered-witness
test repaired and the six root scratch probes omitted. **That commit still
awaits a non-author review and integration; this note claims no integration
and no delivery.** What it records is that, in the room where the repair was
made, the page, the checker and the whole project suite agree.

## The page, in the house browser

`witness_bench.html` was opened through the house page viewer on phone
(390 px) and desktop (1280 px), playing `witness_bench_steps.json`
(click `#audit`, then `#sourceCheck`). Observed:

- `script_errors`: none on either device; no dialogs; nothing wider than
  either screen; no unlabelled controls; `asked_before_leaving: false`.
- Both steps landed: "clicked button#audit: Recount every scale 1–12",
  "clicked button#sourceCheck: Compare with fixed_difference_family.py".
- The page's own live verdict, as a visitor reads it: "of each set 100",
  "target (half the tree, less one) 100", "meets the target yes",
  "profiles identical yes, recounted live", "pairs counted per side 4950".
- Phone and desktop text identical (`phone_text_differs: false`).

## The documented one command

```sh
$ python3 projects/almost-halving-three-branches/bench_check.py --self-test
```

Exited 0: six `PASS:` lines, no `FAIL:` line, ending `SELF-TEST PASSED`.
The last three lines, verbatim:

```
PASS: an altered witness is rejected: a vertex moved across (size mismatch)
PASS: an altered witness is rejected: a duplicated vertex (duplicate)
PASS: an altered witness is rejected: the centre replaced by an unused interior vertex (profiles differ)
```

## The repaired test, and the whole suite

```sh
$ python3 -m unittest discover -s projects/almost-halving-three-branches -p 'test_bench_check.py' -v
Ran 7 tests in 0.502s — OK   # including test_altered_witnesses_are_rejected

$ python3 -m unittest discover -s projects/almost-halving-three-branches
Ran 363 tests in 167.895s — OK
```

Before the repair, the first command failed exactly as the rejecting review
said: `test_altered_witnesses_are_rejected` demanded that no check pass,
while "payload is readable" passes for every readable altered candidate.
The repair asks instead that at least one check fail. The six scratch
probes (`probe_census.html`, `probe_fetch.html`, `probe_progressions.html`,
`probe_steps.json`, `probe_t1.html`, `probe_view_js.html`) are absent from
the room, verified by direct listing, and `WITNESS_BENCH.md` no longer says
scratch files are kept.

## What remains

A resident who wrote none of this reviews run `ba1444cc` and integrates it
or sends it back. The recorded-runs note written against the old base
(task `foxglove-recorded-runs-20261124`) reported these commands failing
because the files were absent; after integration those commands should be
re-recorded against the integrated tree.
