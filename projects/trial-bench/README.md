# Trial Bench

An offline two-phase recorder for a blind trial. Phase 1 locks a prediction
before the prompt is shown; phase 2 records what was observed afterwards.
The receipt hash proves the pre-reveal text is unchanged in the exported
report. It cannot prove honesty or correctness.

Open `projects/trial-bench/index.html` in a modern browser. No build,
install, server, internet connection or account is required. The page is a
single self-contained file (inline CSS and script, no external requests)
with a Content-Security-Policy that disables network connections. Nothing
is saved automatically; a reload discards the working trial.

## Phases

1. **Phase 1 (pre-reveal).** Choose the software task (S-03 or S-04)
   before issuing the receipt. Declare exposure, prediction and reasoning.
   Every field is required. Issuing the receipt hashes the canonical
   pre-reveal block with SHA-256, shows the copyable receipt, and only
   then reveals the supplied prompt and unlocks phase 2. The chosen task is
   captured before hashing starts. While hashing, the task controls are disabled
   and the text fields cannot be edited; on failure both become editable again
   and the prompt stays concealed. The first successful receipt keeps the task
   fixed, makes phase 1 read-only and disables issuing another receipt. Export keeps
   that exact phase 1 snapshot. Keep a copy of the receipt; reload to
   start a different trial, declaring any prompt you have already seen.
   If automatic copying is refused, the receipt stays selected and the
   page asks you to copy it manually; no clipboard permission is required.
2. **Phase 2 (post-reveal).** The supplied synthetic prompt for your
   chosen task is displayed only after the receipt exists. **Run software
   example** sorts the hidden numbers in ascending order (duplicates
   retained) and displays the sorted list plus your task's answer. Each
   task hides its own input, so knowing one answer does not expose the
   other: S-03 hides `[12,3,8,3,-2,0]` (sorted `[-2,0,3,3,8,12]`, 4th
   smallest value `3`), while S-04 hides `[4,9,4,6,1,4]` (sorted
   `[1,4,4,4,6,9]`, most frequent value `4`). The input stays concealed
   until the receipt; both task types are described beforehand so you can
   predict one number before running. Record what the page actually outputs
   in your observation. Running the example never fills or overwrites that
   field and does not score the prediction.
   Record an optional edit (how you revise your phase 1 record) and a
   required observation. Export produces one JSON report (shown in full
   below the controls as selectable text and downloadable as
   `trial-report.json`). Export requires the receipt and a non-empty
   observation. Editing the observation or revision clears that export
   and disables download until you export again, so an older report
   cannot silently stand in for the text currently on screen.

The current demonstrations are software prompts S-03 (4th smallest value)
and S-04 (most frequent value), with the task choice made before the
receipt. The historical `example_report.json`, earlier trial reports and
`SOFTWARE-EXAMPLE.md` retain the old bead-draw (S-01), numeric-sort (S-02)
and first rank-only (S-03) demonstrations as dated synthetic fixtures;
they have not been rewritten or relabelled as runs of the current page.
Reports remain version 1; the checker validates the recorded fields and
hash, not which prompt was run or what its result was.

Report shape (`version: 1`):

```json
{
  "version": 1,
  "trial_id": "trial-…",
  "phase1": {"exposure": "…", "prediction": "…", "reasoning": "…"},
  "receipt": {"hash": "<64 lowercase hex>"},
  "phase2": {"edit": "…", "observation": "…"}
}
```

Hash contract (shared by the page and `checker.py`): the SHA-256 of the
compact JSON of `{"exposure":…, "prediction":…, "reasoning":…}` with
sorted keys and raw UTF-8. The page uses `crypto.subtle.digest('SHA-256')`
on that string; the checker recomputes the same digest.

## Checker

Stdlib only. It validates structure and integrity, not correctness:

```
python3 projects/trial-bench/checker.py <report.json>
```

Exit 0 prints `VALID`; exit 1 lists `INVALID: …` lines (edited pre-reveal
block / hash mismatch, missing exposure declaration, empty observation,
and other malformed reports); exit 2 means unreadable file, invalid JSON
or bad usage.

## Tests

```
python3 -m unittest discover -s projects/trial-bench -p "test_*.py" -v
```

The suite exercises every milestone rejection case against
`example_report.json` (a synthetic example, not a real trial): edited
pre-reveal block, missing exposure declaration (absent key, empty and
whitespace-only values), empty observation (empty and whitespace-only),
hash mismatch, plus the valid acceptance case, malformed hashes and
wrong versions. It also checks the page contract (self-contained, phase 2
starts locked, certificate gating strings, single JSON export) and the
CLI accept/reject behaviour on a tampered copy. When Node is available,
the same command also runs `test_page_ui.js` against the page's actual
script with real WebCrypto: conceal/reveal, required fields, pending and
failed hashes, retry, immutable receipt and export, both task calculations
(S-03 rank and S-04 frequency), and download Blob bytes matching the
displayed JSON. Python then checks
that JavaScript-exported report and rejects a tampered copy. This form
control fixture does not establish layout, real keyboard use or an actual
browser download to disk.

## Limits

A local hash cannot prove the trialist was honest, unexposed or that the
prediction was right. The prompt is concealed in the rendered page until
receipt issuance, but remains readable in the self-contained HTML source.
The supplied prompt is synthetic and the bench scores nothing;
a separate independent non-author trial, recorded apart from these
checker tests, is required before the milestone can be called done.
