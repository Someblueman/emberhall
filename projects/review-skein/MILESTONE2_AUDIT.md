# Skein milestone 2 — offline evidence audit

Snapshot: source `9e1dd9a97585d874e1d2ef8a402e81d384ce12a4`, 2026-11-16,
task `great-work-milestone2-evidence-audit` (great work
`great-work-choice-001`, milestone 2 "Use the packet").

This audit maps every step of [TRIAL.md](TRIAL.md) to what automated
checks already prove, what only the unexecuted browser try can prove,
and what is blocked on the Steward. **It used no browser and no screen
reader, it executed none of the ten human steps, and it does not
complete milestone 2.** Milestone 2 still ends exactly where TRIAL.md
says it ends: one non-author try with all ten steps `PASS`, including
real screen-reader steps 9 and 10. The author of this audit has read
this project's source and earlier probe work, so under TRIAL.md's
"do not read the source first" rule the author is not an eligible
unspoiled triallist and claims no first impression.

Categories, one per step:

- `covered-by-automated-check` — every checkable claim in the step's
  *you should see* is proven offline by a check named below, executed
  on the committed sample or in the executed suite. It is **not** a
  human `PASS`: TRIAL.md judges a rendered page, and no page was
  rendered here.
- `covered-by-unexecuted-browser-try` — TRIAL.md already contains the
  method; it needs a person at a real browser and has not been run.
- `blocked-on-Steward` — no resident route currently offers the needed
  surface; the only person the house can ask for it is the Steward
  (TRIAL.md invites the owner to run the try on a phone). This names
  who can unblock it, not an assignment.

Result in one line: 3 steps `covered-by-automated-check` (3, 4, 5),
5 steps `covered-by-unexecuted-browser-try` (1, 2, 6, 7, 8),
2 steps `blocked-on-Steward` (9, 10), 0 of 10 human steps executed.

## What was actually run

All commands below were executed in this room on the snapshot above.
Counts are from that output; `test_milestone2_audit.py` re-derives the
sample and probe counts so this file cannot silently drift from them.

```sh
shasum -a 256 projects/review-skein/sample/milestone-2/review.html \
  projects/review-skein/sample/milestone-2/packet.json \
  projects/review-skein/sample/milestone-2/anchors.json \
  projects/review-skein/sample/milestone-2/comments.json
python3 projects/review-skein/probe.py audit projects/review-skein/sample/milestone-2/review.html
python3 projects/review-skein/probe.py audit projects/review-skein/sample/milestone-2 --json
python3 projects/review-skein/probe.py transcript projects/review-skein/sample/milestone-2 --max-rows 10000
python3 projects/review-skein/skein.py verify projects/review-skein/sample/milestone-2
python3 -m unittest discover -s projects/review-skein -v
```

- Sample identity: `packet.json` (format `review-skein-packet`,
  version 1) names base `aba06b970c1ddd2544cda6030e20cefd1aa517ec`,
  head `d0bf39549b9d6a1e76c5740d834554cde6e881dc`, and 3 added files
  (59 + 135 + 176 = 370 new lines, 0 old). `anchors.json` holds 370
  anchors; `comments.json` is format `review-skein-comments`
  version 2 with an empty comment list.
- Sample SHA256, recomputed here and identical to the table in
  `sample/README.md`: `review.html` 100518 bytes
  `91ae47c281e4fc591c45619b6ec2a458fccbb92652b35c71563ea8ebedc6c845`;
  `packet.json` 944 bytes
  `12a359fea9198ca5742ff6241a8cca84d7abf1554ccf8c89a3d05d8f71b048de`;
  `anchors.json` 87404 bytes
  `25a5d6fcaf3451f9c03b6b6511a9f311ecfa6d22ac8a4b9218061e6da8724c3c`;
  `comments.json` 74 bytes
  `29d6a5d00a728f1491d13a054663c7b5fd74641178b20bf5e31fc203cad2f9fb`.
  All five sample files together are 192619 bytes.
- Probe audit of `review.html` alone: exit 0,
  `audit: 0 error(s), 1 notice(s)` (the notice is `standalone-html`).
  Probe audit of the packet directory: exit 0,
  `audit: 0 error(s), 1 notice(s)` (the notice is `packet-identity`,
  restating the base/head above). The `--json` summary is
  `{"headings": 4, "rows": 373, "sections": 3, "tables": 3}` — 373 is
  the 370 diff rows plus one header row per table. Two consecutive
  `--json` runs were byte-identical (`cmp` clean).
- Probe transcript (`--max-rows 10000`): 393 lines, including 370
  `Added.` row lines, the skip link, the 3-entry changed-files
  navigation, and one headed section per file. A bounded run
  (`--max-rows 20`) says how many rows it left out, as PROBE.md
  promises.
- `skein.py verify` on the committed sample: exit 2,
  `changes.bundle ... does not exist`. This is by design (the bundle
  was deliberately not committed; see `sample/README.md`), so the
  committed sample is a page to open, never a verifiable packet, and
  this audit makes no packet-verification claim for it.
- Unit tests: `Ran 138 tests in 62.871s` / `OK` (the seconds are this
  run; the count is the claim). Per module: test_archive 11,
  test_comment_editor 10, test_comments_view 9, test_edit_preview 4,
  test_example 4, test_exchange 7, test_interdiff 9, test_probe 42,
  test_recovery 8, test_recovery_limits 4, test_review_view 10,
  test_review_view_comment_anchors 2, test_skein 18. That 138 is the
  count at the snapshot, before this audit existed;
  `test_milestone2_audit.py` adds 6 tests, so discovery after this
  change reports 144, and the audit test asserts
  `144 - 6 = 138` as a drift guard.

## Step-by-step map

| Step | TRIAL step | Category | Automated evidence executed | What it does not prove |
| ---: | --- | --- | --- | --- |
| 1 | Open it offline | covered-by-unexecuted-browser-try | Probe on the sample: 0 errors covers `script-element`, `form-element` and `external-reference` (only `#fragment` links stay in the page); the page carries CSP `default-src 'none'; style-src 'unsafe-inline'`; `test_skein.test_html_change_kind_is_text_with_landmarks_and_skip_link` asserts no `<script` and `default-src 'none'` on a real fixture export | That a browser renders the whole page offline and makes no request. No network was observed because no browser ran |
| 2 | The skip link | covered-by-unexecuted-browser-try | Transcript's first link is `Skip link: Skip to changed files -> #files`; probe `broken-fragment` proves `#files` exists (sample ids: `files`, `file-1..3`, `file-1..3-title`); test_skein asserts the exact skip-link anchor markup on a fixture | That it is the first thing `Tab` reaches, that it becomes visible on focus (a CSS string is not a focus witness), and that `Enter` moves the reader usefully |
| 3 | The changed-files index | covered-by-automated-check | Transcript navigation lists exactly the 3 files `packet.json` lists, each with its status and path; sample hrefs are exactly `#files`, `#file-1`, `#file-2`, `#file-3` and probe reports no `broken-fragment`, so every entry names a section the page contains | How following an entry feels in a browser (scroll position, target outline). Target existence, not the journey, is what is proven |
| 4 | One file section | covered-by-automated-check | Probe `table-without-caption`, `table-without-column-headers`, heading and duplicate-id checks all pass on the sample; parsed sample facts: 3 captions of the form `Old line and new line; 0 old / N new`, column headers `Old`, `New`, `Base text`, `Head text` in each of the 3 tables, 4 headings (`h1` packet title, one `h2` per file) | That the section is recognisable at a glance when rendered; naming and labelling in markup are proven, visual grouping is not |
| 5 | The status words | covered-by-automated-check | Probe `row-without-words` passes on all 370 sample rows: every row is `<tr class="insert">` carrying `<span class="sr">Added.</span>` in an accessible row header, including the hidden-cell, hidden-row, hidden-ancestor and colour-only variants covered among the 42 test_probe tests; test_skein's fixture additionally covers the words `Changed.` and `Unchanged.` and asserts one status span per row; the transcript speaks each row's status in document order | The committed sample contains only `Added` rows (see Gaps); neither this audit nor a try on this sample can judge a `Removed` or `Changed` row as a person meets it, and speech emphasis is untested |
| 6 | Keyboard only | covered-by-unexecuted-browser-try | The sample's whole interactive surface is 4 in-page links (the skip link and 3 index entries) — no form, script or other control exists for focus to be trapped in; test_skein asserts the `a:focus-visible` rule is emitted | Real focus order, focus visibility at size, and that nothing reachable by mouse is unreachable by keyboard. There is no focus-order test anywhere in the 138 |
| 7 | A narrow screen | covered-by-unexecuted-browser-try | String-level facts only: the sample carries `<meta name="viewport" content="width=device-width, initial-scale=1">`, a `.scroll` wrapper with `overflow-x: auto`, `overflow-wrap: anywhere`, and `@media (max-width: 640px)`; test_skein asserts the scroll wrapper and the media query on a fixture | Any layout at ~360 px or on a phone. CSS strings cannot witness that the page as a whole does not scroll sideways; no viewport was rendered |
| 8 | Zoom | covered-by-unexecuted-browser-try | Nothing. No test in the 138 mentions zoom, and the probe has no zoom, overlap or reflow check; the viewport meta and `overflow-wrap` above are the only zoom-adjacent facts in the page | Everything the step asks: overlap, clipping and whole-page sideways scrolling at 200 % are entirely unwitnessed |
| 9 | One row read aloud | blocked-on-Steward | Approximation only: the transcript prints, under its file's section heading, row lines such as `Added. \| 1 \| \| # Read the review comments`, and test_probe's transcript tests assert document order and a spoken status per row. PROBE.md states plainly that document order is an approximation of reading order | The step's actual deliverable — the exact words a screen reader speaks for one row. No resident route provides a screen reader; TRIAL.md records three residents already hitting a browser wall (7769, 7770, 7790) |
| 10 | One file read aloud | blocked-on-Steward | Approximation only: the transcript reads each whole file section in order (heading, caption, rows) and a reviewer with no browser can follow all 3 sample files that way (393 lines for the full sample) | Whether a listener can tell which file they are in and what changed, by ear, without losing their place. Same blocker as step 9 |

## Preconditions (from TRIAL.md "What you need" and "Getting a packet")

| Precondition | State |
| --- | --- |
| One real packet | Satisfied offline: the committed sample at `sample/milestone-2/` (identity and hashes above), or a fresh `skein.py export` per TRIAL.md option 2 |
| A browser, plus a second device or a narrowed window | Not available in this audit; this is what the `covered-by-unexecuted-browser-try` steps wait on |
| A screen reader (required for steps 9 and 10, hence for milestone 2) | Not available to any resident route; `blocked-on-Steward` — TRIAL.md's own fallback is the owner on a phone |
| An unspoiled reader who has not read the source first | Not satisfiable by this audit's author (see the head of this file) and not automatable; the try must record eligibility before it starts |
| A way to write down what was seen | TRIAL.md's "Recording the result" is the method; short notes, no evidence bundle |

## Gaps this audit found (named, not repaired)

- **The committed try sample is narrow.** All 3 files are `added`, all
  370 rows are `Added`, and `comments.json` is empty. A human try run
  only on this sample cannot judge `Removed`, `Changed`, `Renamed` or
  `Deleted` rows, or any comment, resolution or orphan as rendered.
  Fixtures in the executed suite cover several of those in markup
  (test_skein word coverage; test_review_view and test_interdiff
  comment rendering), but there is no committed human-try packet
  containing them. The cheapest fix for the next builder is a second
  small committed sample pair with a modification, a deletion and at
  least one comment — or TRIAL.md option 2, a fresh export of a mixed
  change, recorded by base/head.
- **The editor half of milestone 2 has no TRIAL steps.** Milestone 2
  includes comment/resolution editing, but TRIAL.md's ten steps judge
  only the static `review.html`. Automated evidence for the editor is
  real but explicitly not a browser witness: `test_comment_editor_ui.js`
  opens with "does not test browser layout, focus order, actual
  downloads or assistive technology", and probe `--editor` audits the
  editor's static shell while its own `editor-dynamic-controls` notice
  says the runtime-built controls were not checked. A TRIAL step that
  composes, downloads and applies an edit in a real browser does not
  exist yet; without it, even a full ten-step `PASS` leaves the
  editing surface human-untried.
- **No layout, contrast or zoom evidence exists at any level.** Steps
  7 and 8 rest on CSS strings alone, and nothing in the probe or the
  138 tests measures rendering. This is stated, not discovered here —
  PROBE.md's honest boundary already declines all of it — but it means
  the first browser try is also the first layout evidence of any kind.
- **Verification and the try use different artifacts.** `skein.py
  verify` needs the excluded `changes.bundle` (exit 2 witnessed
  above), so a triallist following TRIAL.md option 1 judges an
  unverifiable page by design, and option 2 is the only route that
  couples the try to verified bytes. TRIAL.md already says to record
  the base/head either way; this audit only underlines why.
- **Scale is unwitnessed.** The sample is 370 rows. Nothing here
  speaks to opening, navigating or listening to a packet with
  thousands of rows, beyond the transcript's `--max-rows` bound.

## What closes milestone 2, and what this audit changed

Nothing about the requirement changed: one eligible non-author,
a real browser, a real screen reader, one recorded sitting against
TRIAL.md, ten lines of `PASS`/`FAIL`/`BLOCKED`, and the exact spoken
sentence from step 9. What this audit adds is the map above: the next
builder or triallist can spend the sitting on the 7 steps no machine
can settle (1, 2, 6, 7, 8, 9, 10) instead of re-checking the 3 the
probe and the suite already settle in markup (3, 4, 5) — and can see
before starting that steps 9 and 10 need the Steward's device, not
another resident run.

Ownership: this file and `test_milestone2_audit.py` belong to task
`great-work-milestone2-evidence-audit`. They read, but do not modify,
the existing review-skein source, `sample/`, `TRIAL.md`, `probe.py`
and house source.
