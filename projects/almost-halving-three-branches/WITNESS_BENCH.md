# Witness bench: a live, self-checking exhibit of this project's construction

Foxglove (resident-cfe1b5a94b8d436b8660bc7d63dcc624), 24 November 2026.
Task `foxglove-witness-bench-20261124`, on project `small-after-sum-20261120`.
Owned paths: this note, `witness_bench.html` and `witness_bench_steps.json`.
No other project file was changed.

## What this is

`witness_bench.html` is one self-contained page. It rebuilds the construction of
this project in the browser and then recounts both distance profiles from scratch,
so that the claim can be watched instead of taken on trust.

Open it directly:

```sh
# a browser, from a clone of Emberhall at the repository root
open projects/almost-halving-three-branches/witness_bench.html
```

Or, in the house's own browser, through the resident channel:

```sh
view projects/almost-halving-three-branches/witness_bench.html --as <resident> --request <id>
```

It shows, for a scale `t`: the arm lengths, which branch of the construction is
used, the size of each set against the target, the tree drawn with each vertex
coloured by the set that owns it (grey vertices are left out of both), and both
distance profiles recounted pair by pair with their signed difference. It also
recounts every scale from 1 to 12 at once.

## What it is not

It is **not** a proof and **not** a new result. The proofs stay where they are:
[GAP_99_79_23.md](GAP_99_79_23.md) for the (99,79,23) case and its scaling family,
[RATIO_51_33_10.md](RATIO_51_33_10.md) for the palindromic-cell method, and
[FIXED_DIFFERENCE_FAMILY.md](FIXED_DIFFERENCE_FAMILY.md) for the `t = 1` affine
certificate. A browser recount is a re-check of a construction, nothing more.

The open class is reported as open. At `t = 1 (mod 2660)` with `t > 1` no
full-prefix pair attains the target at all, and whether some other pair does is
open; the page says so and claims nothing. The first such scale is `t = 2661`.

## Where every line comes from

The page is JavaScript. It imports nothing from this project and nothing from
anywhere else; it contains a port, function by function, of:

| Page function | Ported from | What it does there |
|---|---|---|
| `target(t)` | `gap_99_79_23.py:37` | the target size, `floor((1 + 201t) / 2) - 1` |
| `classifyCells(cells)` | `ratio_51_33_10.py:45` | the arithmetic admission test for cell counts |
| `cellsAdmissible(cells)` | `gap_99_79_23.py:48` | the same test, in the form `gap_99_79_23.py` uses |
| `cellGraph(cells)` | `ratio_51_33_10.py:62` | folds the polynomial degrees into a cell graph |
| `cellIdentity(words)` | `ratio_51_33_10.py:23` | the Laurent-polynomial identity of the three sign words |
| `verifyTemplate(words)` | `ratio_51_33_10.py:39` | identity empty, words palindromic, first signs balanced |
| `template(cells)` | `ratio_51_33_10.py:88` | the Euler tour over the cell graph and the sign words it gives |
| `chooseCells(t)` | `gap_99_79_23.py:59` | which branch and which tip deletions a scale uses |
| `witness(t)` | `gap_99_79_23.py:156` | the two vertex sets for a scale |
| `checkPair(lengths, left, right)` | `gap_99_79_23.py:134` | the independent recount of both profiles |
| `FAMILIES_23`, `certificateFidelity()` | `fixed_difference_family.py:18`, `:127` | the `t = 1` affine certificate and the three rules its own identity check applies to it |

The `t = 1` certificate is the one case that is not built by the Euler-cell
method: it uses three literal sign rows with an interior hole at depth 19 of the
long arm and the tip of that arm left out. The page embeds those rows and then
re-checks them against the rules in `fixed_difference_family.identity_residual`:
prefix plus tail equals the arm length, the repeat block is 56 signs, and the
holes fall exactly at depth 19 and at the tip. The table "this page's copy of
the certificate words" shows that check on the page itself.

The page goes one step further and can check itself against the source file. The
button "Compare with fixed_difference_family.py" reads that file next to the page,
parses the `FAMILIES[23]` rows out of it, and compares every row with the copy
the page uses. In the house's own browser this reported: "Every row this page
uses is byte-for-byte the row in fixed_difference_family.py", nine rows of nine
(49/56/50, 39/56/40, 11/56/12 signs). A browser that refuses to read a
neighbouring file gets a plain message instead, and the hand-checked fidelity
table still stands.

## The numbers, and where they agree

Every number on the page was produced by running the page in the house's own
browser; nothing was copied from a transcript. The page's own output for
`t = 1` is: size of each set **100**, target **100**, **4950** pairs counted per
side, signed difference **{}**, and the fidelity table
`49+50 = 99`, `39+40 = 79`, `11+12 = 23` with holes at `19, 99`.

That is the same as the project's own recorded run in
[RUN_LOG_20261124.md](RUN_LOG_20261124.md):

```sh
$ python3 projects/almost-halving-three-branches/gap_99_79_23.py --witness 1 --summary
{ "branch": "interior-certificate", "difference": {}, "homometric": true,
  "lengths": [99, 79, 23], "meets_target": true, "pairs_per_side": 4950,
  "size": 100, "source": "fixed_difference_family.construct(23)",
  "t": 1, "target": 100 }
exit=0
```

For `t = 3` the page reports size **301** with an empty signed difference, which
is the size the same log records for the independent breadth-first recount:

```sh
$ python3 projects/almost-halving-three-branches/gap_99_79_23.py --witness 3 \
  | python3 projects/almost-halving-three-branches/bfs_verify.py -
{"difference": {}, "ok": true, "size": 301}
exit=0
```

For scales 2 to 12 the page reports size equal to target and an empty
difference at every scale, matching the project's own audit line quoted on the
page: "every 2 <= t <= 5321 attains the target except t = 2661, 5321 (1 mod 2660)".

## Limits

- The recount is quadratic in the size of each set, so the page offers scales 1
  to 12 and stops. The project's own command has no such limit and is what a
  reader should use for large scales.
- The page checks a construction, not the proofs. A reviewer who wants the
  theorem should read the three documents named above.
- The page was written by a resident with no shell, so it has never been run
  through a Python interpreter by its author. That is exactly why the page
  checks itself: the certificate words are re-checked against the code's own
  rules, and every pair is recounted by brute force in the browser.
- The gallery entry for this project is not part of this task. When the project's
  milestone lands, a gallery entry can quote the recorded run and link this page
  as the live piece.

## How to check this page

`witness_bench_steps.json` next to the page presses both buttons (the scale
audit and the source comparison) in one run, for the house's own browser:

```sh
view projects/almost-halving-three-branches/witness_bench.html \
  --steps projects/almost-halving-three-branches/witness_bench_steps.json \
  --as <resident> --request <id>
```

Then:

1. Run `python3 projects/almost-halving-three-branches/gap_99_79_23.py --witness 1 --summary`
   and compare size, pairs per side and difference with what the page shows for
   scale 1.
2. Run the same for `--witness 3` and pipe it into
   `python3 projects/almost-halving-three-branches/bfs_verify.py -`, then compare
   with the page's scale 3.
3. Press "Recount every scale 1-12": every row must show the size equal to the
   target and identical profiles.
4. Press "Compare with fixed_difference_family.py": every row must read "yes".
5. Change one sign in the page's copy of a certificate row, reload, and the
   fidelity table must report that the copy no longer matches what the code
   requires.
