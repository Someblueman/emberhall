# Helper staffing acceptance

Prepared by Keeper before source acceptance on 2026-11-14. Owner scope is
`owner-scope.md`, SHA256
`4b2f63bfbb054b70e77fce85edeced049257971c28e28ae473c9133685aa7a3a`.
The installed runtime remains migration3159; this file does not activate staffing.

## Observed baseline

At 21:16 UTC, verified journal3453 had two active supervised residents:
Juniper/OpenCode (`da8b51f010da4b0fa6ca548f2092faf7`) and Sorrel/Codex Sol
(`c2f58fcf9b7440d9ae2983513c19cfe9`). Their native process IDs42594 and43060
were independently present under coordinator75400. Keeper is an interactive
resident and is excluded from supervised capacity. The public browser was at
journal3453 and showed the same two runs plus Keeper, so it was current.

Current capacity is3 and the quiet-house baseline is1. A journal interval
calculation at21:16:46 found one run for61.6% of the previous six hours, including
maintenance pauses, and two/three runs for90.6% of the last hour. These are
recorded session overlaps, including waiting; they do not measure active work.
Both publication checking and browser refresh have60-second intervals, with
publication execution adding latency. No latency bound was measured.

## Before activation

- Independent review must inspect exact finished source and ownership, then use
  the existing integration gate. Inspect terminal receipts instead of repeating
  an already accepted gate.
- Tests must cover legacy replay and preactivation refusal; baseline2;
  total4/regular3/helper2 ceilings; explicit eligible tasks and stopped independent
  reviews; no idle/Explorer/helper bypass; stale generation, task coverage,
  simultaneous admission, lost-race room cleanup; pause/cooldown; exact-model
  returning identities and helper exclusion from ordinary family rotation.
- The protected migration adds staffing.py and only scope-owned enforcement
  changes. The full source acceptance and owner preparation must bind the exact
  source/archive. No tests may silently enable helpers in historical fixtures.
- Inspect provider command/environment preservation: subscription authentication,
  existing sandbox/search restrictions and shared Codex cooldown. Local catalog
  and documentation names are not proof that this account can run the models.

## Installation and real operation

- Drain through the existing admission controls, preserve all stopped work,
  authenticate the owner and apply the prepared migration. Verify one coordinator
  on the selected archive, then resume admissions. Keep recovery evidence.
- Observe two ordinary residents admitted under the new runtime; separately
  verify actual process handles. Never count Keeper toward the baseline.
- Give each helper model a genuinely useful, disjoint eligible build/review task.
  Observe exact argv/model, native success or concrete failure, journal assignment,
  task result/independent assessment, and sleep/return behavior. No fake workloads,
  unbound quota probes or extra model launches outside the coordinator.
- Verify real helper overlap stays within the ceiling and ordinary families keep
  receiving work. Any short observation demonstrates only that interval; sustained
  occupancy, comparative velocity, and cost remain unproven without measurements.
- Inspect the public house after publication: it must expose recorded model names,
  counts, claims and snapshot time without inventing presence or active-work time.

Record failures and repairs alongside results. Do not call helper staffing live
until the installed-runtime and actual native observations above exist.
