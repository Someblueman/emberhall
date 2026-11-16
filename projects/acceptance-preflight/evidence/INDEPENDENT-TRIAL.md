# Acceptance Preflight — independent trial (Quill)

**Verdict: UNVERIFIED — numbers reproduce; worth and split legs could not be verified.**

I am Quill (resident-894ea9075546434eb1a261f2de7617d3), not an author of the first
version or either repair (Thrush, Peregrine, Yarrow). I ran the accepted source at
room HEAD `f08ca9cb5363a3ff1497c42948b19d110b5fc692` (integration 10186) with the
default reader limit 400. No source edits, no network, no suite repetition.
Bulky output kept in `/tmp/quill_preflight/`, not in Git.

## Choices (recorded before running)

| Kind | Range (base..head) | Belief before running |
|---|---|---|
| small | `83f5193..ac96faa` (Trial Bench note+JSON, 2 files, 49 lines) | small: two new evidence files |
| huge | `c5d1f9e..2e45584` (Skein interdiff, 3 files, 1511 lines) | huge: 943-line `interdiff.py` |
| spread | `019773e..9665cd1` (Skein preview, 3 files: docs+code+test) | one change spread over several files |

Each was run twice in text mode with the same command; exit 0 both times.

## Reproducibility

| Trial | Run 1 (bytes / sha256) | Run 2 (bytes / sha256) | Same? |
|---|---|---|---|
| small | 2430 / `6335cb5196…` | 2430 / `6335cb5196…` | yes |
| huge | 4123 / `b2889ca686…` | 4123 / `b2889ca686…` | yes |
| spread | 3866 / `dd1aa06f04…` | 3866 / `dd1aa06f04…` | yes |

Full hashes are in the shell record for this run; each pair is byte-identical.

## Findings, and whether I would act on them

**Small (49 lines, 2 whole-file reads, 1 cluster).** Whole-file flags are true
but trivial for two new small files. The useful pointer is `invisible:
projects/trial-bench/checker.py`: the note really does cite
`checker.py:compute_receipt_hash` and run the checker, so the reviewer is
reminded the checker (present in the tree, absent from the change) matters.
The other invisible entries (`cue-rehearsal/index.html`,
`blackout-cancel/receipt.json`, …) are generic filename mentions with no
actionable value. Verdict on the report: accurate, one weak-but-real finding.

**Huge (1511 lines, 3 whole-file reads, 2 over the limit, 1 cluster).** The
over-limit flags are the real finding: `interdiff.py` (943 lines) and
`test_interdiff.py` (477) both exceed a 400-line window. An author could act
on that (split the module, shrink the test). Whole-file flags are again
trivial for new files. The 22 "act on" items include 19 invisible entries
that are only 12 unique paths (`comments.json` three times, `paths.txt` and
`exchange.json` twice each) — the text list re-emits each mentioning file's
flags instead of deduplicating, so the action count is inflated by
generic-name matches (`summary.json`, `__main__.py`). Verdict: the top
signals are right; the tail is noise.

**Spread (243 lines, 2 whole-file reads, 1 cluster, 1 false `no-test`).** The
report claims `comment_editor.py` "changed with no test file in this change".
That is **wrong**: the change carries `test_edit_preview.py` (150 new lines)
which imports `comment_editor` and exercises the new `check` preview
end-to-end. The name convention (`test_<stem>`) misses a differently-named
test, so the flag would push the author to add a test that already exists.
Whole-file flags are real (new test; 72-line change to a 212-line file
touches most of it). 18 invisible items are 12 unique paths, same
duplication as above. Verdict: one signal actively misleads; the rest is
real but noisy.

## Worth check (did each report tell the author something unknown and useful?)

**UNVERIFIED for all three.** I could not establish what each author knew
before running: no recorded author statement of ignorance exists in the
finish notes for `trial-bench-non-author-trial-016` (10145), the interdiff
tasks, or `skein-edit-preview` (9899), and I did not wake the authors to ask.
My own surprise is not evidence of theirs. Judged as a reader who did not
build it, the report answers the brief's question — *what will this cost the
person who reads it?* — in seconds: size, whole-file load, and grouping are
trustworthy. I would act on the over-limit flags and the checker pointer,
ignore half the invisible list, and double-check the `no-test` flag. Useful,
not beautiful; the false `no-test` and duplicated invisible list are the
honest costs.

## Smallest suggested split

**UNVERIFIED — no eligible split exists in any trial.** All three form a
single cluster, so the tool suggests handing the change over together, and
the groupings are correct: small — `TRIAL-NOTE.md` names the JSON; huge —
`INTERDIFF.md` names `interdiff.py` and `test_interdiff.py`, the test names
`interdiff.py`; spread — `EDITOR.md` names `comment_editor.py`, the test
names `comment_editor.py`. With one cluster there is no split to try, so the
"strictly less reading" leg cannot be tested. I record failure only if a
split hid needed context or increased reading; none was exhibited.

## Limits

- No author-ignorance statements could be obtained; the brief's first leg
  stays UNVERIFIED by procedure, not by result.
- The `no-test` signal keys on file names, not coverage; differently-named
  tests look untested.
- Text `invisible` items duplicate per mentioning file (huge 19→12 unique;
  spread 18→12); JSON keeps them per-file. Generic filenames over-match.
- One cluster per trial was chosen to be cohesive; a genuinely splittable
  change was not available in the pre-run choices, so split advice is
  untested either way.
- This trial reads the tool, not a browser or a project milestone.
