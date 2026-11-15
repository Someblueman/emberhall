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

1. **Phase 1 (pre-reveal).** Declare exposure, prediction and reasoning.
   Every field is required. Issuing the receipt hashes the canonical
   pre-reveal block with SHA-256, shows the copyable receipt, and only
   then unlocks phase 2. Do not change phase 1 text after issuing the
   receipt: the checker rejects a report whose phase 1 no longer matches
   the receipt. Issuing again overwrites the receipt and resets phase 2,
   so keep a copy of the first receipt if you need the original lock.
2. **Phase 2 (post-reveal).** The supplied synthetic prompt is displayed
   only after the receipt exists. Record an optional edit (how you revise
   your phase 1 record) and a required observation. Export produces one
   JSON report (shown below the controls and downloadable as
   `trial-report.json`). Export requires the receipt and a non-empty
   observation.

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
CLI accept/reject behaviour on a tampered copy. Recorded result for this
build: 11 tests ran, all passed (exit status 0) on 2026-11-15.

## Limits

A local hash cannot prove the trialist was honest or that the prediction
was right. The supplied prompt is synthetic and the bench scores nothing;
a separate independent non-author trial, recorded apart from these
checker tests, is required before the milestone can be called done.
