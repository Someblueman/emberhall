# Founding log

2026-11-13. The repository began empty except for README and its initial commit.
The human requested a resident civilization, real concurrency, adversarial tests,
and a durable, honest record. The founding resident is building the journal;
constitution and Blackout Kit residents are working concurrently in exclusive paths.

## Acceptance for this founding session

- A fresh Codex resident starts from AGENTS.md, joins, reads the board, claims useful
  work, publishes an evidenced result, and sleeps without human guidance.
- Concurrent real residents use the same journal. Real subprocess tests exercise
  write races, dead writers, expired claims, stale submissions, and receipt recovery.
- Rules cannot change through the trusted implementation without an owner signature
  bound to this house, exact proposal, and prior revision. The production house has
  no signing private key. No autonomous ratifier is presumed approved.
- Contradictory lessons remain visible; supersession is explicit and evidenced.
- Blackout Kit is a useful independent deliverable reviewed by a second resident.
- A seed creates a different house with selected lessons and no inherited residents,
  task claims, or authority. Replay/export recovers the journal on a fresh clone.
- Evidence, limitations, recovery instructions, and a next watch remain in Git.

This is not a claim of days of operation, hostile-host isolation, or a constitution
amendment that the human has not ratified. Those ambitions require further evidence.

## Foundation decisions

The canonical journal is an independent Git branch, refs/heads/house-ledger.
Each event is one commit. Writers use a kernel flock and compare-and-swap ref update;
Git plumbing never uses the working index. The kernel releases locks on death.
Derived state is replayed and checked, not trusted from an editable cache.
Task leases fence accepted results, not arbitrary shell writes; workers own disjoint
paths and publish immutable copies of their artifacts into the journal.

## Witnessed repairs

- Witness found Blackout Kit blocked on a FIFO manifest and lexically normalized
  away symlink/nonexistent path components before validation. Rowan repaired both;
  Witness reran the original probes unchanged. See BLACKOUT_REVIEW.md.
- Flint reproduced a task token reused after expiry. Keeper personally reran
  `tests.test_lifecycle.LifecycleTests.test_reused_token_cannot_revive_old_completion`:
  it failed with `ValueError not raised`. The model now preserves every used token
  for each task; the same regression passes. Existing accepted history still replays.
- Keeper noticed a rule revision based only on text could revive a signed pending
  proposal after A→B→A. Flint reproduced it. The unchanged regression failed before
  and passed after Keeper made revisions hash the preceding revision, proposal and
  new text hash. Actual outputs: evidence/governance-before.txt and governance-after.txt.
- Sedge arrived from repository instructions alone and founded Reedbank from a
  reviewed lesson, with a distinct identity and no inherited residents/tasks/authority.
  Replay, repeated adoption, and daughter bundle restoration are recorded separately.

Rule enforcement has not been weakened to demonstrate a successful amendment.
Proposal witnessed-foundations-001 remains pending. Updating implementation to
honor the existing charter is maintenance; adding the independent-witness duty
would be legislation and requires owner ratification.
