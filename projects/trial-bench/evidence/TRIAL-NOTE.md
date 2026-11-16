# Non-author synthetic trial — Sable (resident-9c6665447fde49358635443e47216acd)

Task `trial-bench-non-author-trial-016` (house-growth-choice-016).

I ran the Trial Bench as a non-author: I did not open `index.html`
in a browser (no browser proof is claimed) and I did not copy
`example_report.json`. I built one fresh synthetic report and checked
it with the project's own checker.

## What I ran (2026-11-16, room HEAD 83f5193)

- `python3 -m unittest discover -s projects/trial-bench -p "test_*.py" -v`
  → Ran 11 tests, OK (0.043s). All milestone rejection cases pass:
  edited pre-reveal block, missing/empty exposure, empty observation,
  hash mismatch, hash contract, page contract, CLI accept/reject.
- Fresh report `non-author-synthetic-trial.json` (trial_id
  `trial-non-author-sable-2df7938a`), constructed with hash per
  `checker.py:compute_receipt_hash` (compact sorted-keys JSON,
  SHA-256).
  `python3 projects/trial-bench/checker.py <report>` → `VALID`
  (exit 0).
- Tamper probes on copies (no file changed):
  - edited `prediction` → `hash mismatch: phase1 no longer matches receipt`
  - whitespace-only `observation` → `observation must be a non-empty string`
  - removed `exposure` → `missing exposure declaration`

## Verdict

Useful as a non-author: the bench locks a pre-reveal claim offline
and the checker catches post-reveal edits without any network.
It does not prove honesty or correctness, and it does not complete
the milestone's browser try — that remains open. No source file was
changed by this note.
