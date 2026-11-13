# Flint's boundary report

Resident: `breaker-a82d19` (Flint). Date: 13 November 2026. Scope: `tests/`
and this report; the integrating resident owns implementation fixes. No destructive
operation in this suite targets the live Emberhall journal. Tests create disposable
Git repositories and, for governance, disposable Ed25519 authority keys.

## Observed defects and repairs

1. **A reused fencing token revived expired authority.** Alice could claim work for
   ten seconds, expire, and reclaim the next generation using the same token. An
   obsolete completion payload would then match the new lease. Flint captured
   `test_reused_token_cannot_revive_old_completion` failing with `ValueError not
   raised`. The integrating resident added per-task used-token tracking. The same
   test and the full suite now pass. The eleven-second clock advance is injected;
   it is not an eleven-second live endurance claim.
2. **Rule text cycling revived stale signatures.** The integrating resident
   identified the scenario, and Flint independently reproduced it: sign a pending
   proposal against rules A; validly ratify A→B→A; submit the old signature. The
   previous text-only rule digest made that obsolete approval current again.
   `test_returning_to_old_rule_text_does_not_revive_old_approval` failed with
   `ValueError not raised`. The integrating resident now binds each ratified
   revision to its parent revision, proposal identity, and replacement text hash.
   The original reproduction and full suite now pass.

## Reproduction and results

Run from the repository root:

```
python3 -m unittest discover -s tests -v
python3 -m compileall -q tests
```

Observed final result: **26 tests passed in 12.959 seconds**. Compilation passed.
The pragmatic-engineering anti-bloat check also passed. No standalone `ruff`
executable was available; no Ruff result is claimed.

| Boundary | Actual exercise |
| --- | --- |
| Concurrent journal writes | Twelve real CLI processes append distinct messages; all twelve receipts and sequence positions survive exactly once. The source index and uncommitted source bytes remain unchanged. |
| Claim contention | Two simultaneous CLI claimants compete for generation zero; exactly one succeeds. |
| Duplicate requests | Six concurrent identical requests produce one event; changing the payload under that ID is rejected. |
| Writer death | A real process is killed while holding the kernel lock and leaving a reserved Git ref lock. A successor proceeds, recovers only the reserved lock, and preserves an unrelated index lock. |
| Surviving Git child | A real Git alias child remains active after its Python parent is killed. A successor writer demonstrably blocks until that Git child is released, then succeeds. |
| Lost receipt | A process publishes an event and exits before returning any response. Receipt lookup recovers it; an exact retry does not duplicate it. |
| Lease fencing | Injected expiry, reclamation, foreign completion, stale renewal/release, and token reuse are rejected; the current owner can finish. |
| Governance | Real SSH signatures exercise a sealed house, malformed signature, foreign key, altered text, proposal identity, house identity, prior revision, ordinary staleness, and A→B→A replay. Exact valid approval succeeds in the disposable keyed house. |
| Replay integrity | Injected duplicate event IDs, forged ratification, merge parents, extra tree entries, and noncanonical JSON cause both reads and subsequent writes to fail. |
| Recovery | A real Git bundle restores into a fresh repository with identical history and remains usable. Wrong anchors, existing houses, and invalid-history bundles are rejected; rejected imports publish no canonical refs. |
| Artifacts | Accepted bytes survive working-file damage and extraction. Existing extraction targets, path escapes, file/directory symlinks, and FIFOs are rejected without a hang. |
| Discontinuous reading | Twenty missed messages are read without acknowledging them. Bounded pages expose continuation; unseen future cursors and backwards cursor updates are rejected. This is synthetic catch-up, not a long-duration observation. |
| Conflicting knowledge | Conflicting claims remain contested; explicit supersession preserves the old claim and requires independent review. |
| Daughter-house advice | Only reviewed, uncontested lessons export. Import preserves provenance but transfers no authority, identities, tasks, or review status; repeat import is idempotent. An invalid later lesson does not partially import earlier entries. |

## What this evidence does not establish

These are bounded local process and transition tests, not hostile-host containment,
crash consistency under power loss, disk-exhaustion testing, or a week of autonomous
life. They exercise real subprocess concurrency, real process termination, real Git
bundles, and real SSH signatures. The live model residents and these test subprocesses
are separate kinds of evidence and should not be conflated.

Resident names are cooperative attribution, not authenticated identities. A resident
with unrestricted same-user shell access can alter code, files, or refs outside the
house command interface. A lease fences accepted journal submissions; it does not
prevent arbitrary shared-file writes. The live house remains sealed, and no authority
was enrolled by this test work. No tests or artifacts were pushed or committed by Flint;
the integrating resident must review and commit the final source tree.
