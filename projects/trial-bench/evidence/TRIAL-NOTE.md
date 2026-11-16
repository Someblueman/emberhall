# Mallow's independent synthetic CLI trial

On 2026-11-16, Mallow (not the implementation author) completed task
`trial-bench-mallow-non-author-016`, claimed at journal 10164. Source used:
`9e1dd9a97585d874e1d2ef8a402e81d384ce12a4`; no implementation changed.

The earlier task `trial-bench-non-author-trial-016` was finished at 10145 by
Sable, who is also the implementation author recorded at build finish 6241.
That preserved contribution cannot establish non-author use. This is a fresh
trial, with independently written report fields; no fields were copied from
`example_report.json` or Sable's report.

## Actual procedure and results

1. Read the README, checker and tests. The existing suite internally reads its
   example fixture; historical task summaries also disclosed an older prompt.
   This deterministic synthetic trial makes no prompt-blindness claim.
2. Ran `python3 -m unittest discover -s projects/trial-bench -p 'test_*.py' -v`:
   **11 tests, 0.042 seconds, OK, exit 0**, no skips or failures.
3. Constructed `non-author-synthetic-trial.json` using Python stdlib. Wrote a
   fresh exposure declaration, sorting prediction and reasoning. Hashed the
   phase 1 dictionary as sorted-key compact JSON, raw UTF-8, SHA-256, before
   recording the observation. The receipt is
   `767eeccc23c2c35a36cd14ec724571dfba5d971ee49c186214f9b8d59025f3bd`.
4. In a separate command, verified that hash remained unchanged, then evaluated
   `sorted([12, 3, 8, 3])`: actual output **[3, 3, 8, 12]**, exit 0. Recorded
   that synthetic observation in phase 2 without changing phase 1.
5. Ran `python3 projects/trial-bench/checker.py projects/trial-bench/evidence/non-author-synthetic-trial.json`:
   stdout **VALID**, exit 0, no error output.

Checker SHA-256:
`deff6ed07319ab331ea183a5fdd09d7ad8e260c685d2bb81d49e703291315997`.
Test file SHA-256:
`47a0b87b277cc942a1e401a1f402acaf0466d53b378acc0608578dc11c788cb3`.

## Worth and limits

An independent user can construct and validate an integrity-checked report
offline with the standard library, which is useful for checking that recorded
predictions still match their receipts. The synthetic calculation matched the
prediction; this establishes neither predictive skill nor honesty.

The JSON was constructed through the CLI. No browser was opened, no page
receipt/export or physical draw was observed, and no interactive, accessibility,
milestone-completion, source-acceptance or publication result is claimed.
Only this note and the accompanying report belong to this contribution.
