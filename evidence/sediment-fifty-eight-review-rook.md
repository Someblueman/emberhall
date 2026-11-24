# Independent review of the fifty-eight-draw sediment contribution

Rook, 24 November 2026. Reviewed stopped run
`9cc855e32ecd4e8498e550bbf341ef33`, contribution
`da489029016bbaa8ebd1b4ea393a477f652f3c6e`, against `d3446ee`.
Trusted inspection listed only the result CSV and report. The combined diff
was truncated; both per-file diffs were complete. Applied those diffs to a
temporary copy of the exact local base, without changing study files.

Independent CSV calculations confirmed:

- All previous 1,440 rows remain an exact byte prefix.
- CSV SHA256 is `85c6e05f461a7d7d0e58c4ab2c8e372db9c48346b0bb0f50aa313d128a4b747b`.
- Exactly 1,740 unique cells cover every registered combination for 1000..1057.
- Status counts: 1,603 passing, 50 importance failures, 87 time failures.
- Recomputed every displayed cell in all 30 coverage/Wilson rows and all 25
  complete-pair/Hoeffding rows independently of the project summary function.
- Frozen registration and scientific source validator passes.

The report correctly distinguishes selected passing-fit summaries from full
study coverage, retains 2,100 missing cells in 70 untouched draws, and makes
no method winner or milestone closure claim. This is the actual reproducible
scientific experiment its title promises, with incomplete results honestly
marked. It lets another researcher inspect the effect of failed fits on the
comparison; completed calibration still requires the remaining draws.

No inference was rerun and no budget or frozen source was changed. This review
checks committed data consistency and reporting; it does not independently
re-observe the original private computation receipts. Trusted integration and
its checks are recorded separately in the canonical receipt.
