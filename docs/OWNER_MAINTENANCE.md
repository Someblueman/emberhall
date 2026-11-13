# Explicit owner maintenance

The owner reported that existing OpenCode account access was repaired and then
said "you can override it" after the one-day cooldown was explained. The exact
short approval record is `evidence/owner-maintenance/opencode-approval.txt`.
This permits one early admission against budget event300. It does not certify
working credentials or authorize another provider, keys, payment or sandbox changes.

The original deadline remains. A separate credit is consumed atomically by the
first accepted OpenCode run-start, even if launch subsequently crashes. Every new
provider-budget observation invalidates that credit, including a shorter failure
that cannot reduce the maximum deadline. The coordinator and journal use the same
admission predicate. A lost release response replays its stable receipt; it cannot
create another credit. Normal admission resumes at the original deadline.

Initial authorization303 and its protected-file manifest stay intact. An append-only
owner-migrate receipt records a replacement manifest limited to this feature,
source/test/archive hashes and the owner instruction hash. Ordinary resident
refresh still needs an enacted council prompt and a later tested wake. The floor
and room-growth scope from the newer owner objective is a separate, unused grant;
its required building module must exist and pass its own preparation before use.

## Cold upgrade and recovery

Use the reviewed new source operator. Preparation has no journal/pointer effects:

```
python3 -m house.owner_upgrade --as keeper-01 prepare \
  --scope opencode-retry-20261113 \
  --approval-file evidence/owner-maintenance/opencode-approval.txt \
  --source-commit REVIEWED_COMMIT
```

It requires clean committed source, an immutable archive and actual passing tests
in the existing restrictive OS sandbox. Raw test output and the exact plan remain
private under `.git/house-home/`; retain failed output too. Preserve the returned
plan path before proceeding.

Retire the old LaunchAgent coordinator before applying: a path switch does not
replace Python modules already imported by a live process. Preserve and finish
native work, stop this named service, and use its old `home tick` if recovery is
needed before the first new-schema event. Verify no recorded active runs, actual
native groups or trusted action jobs remain. The operator refuses active recorded
runs, unfinished jobs or a held coordinator lock.

```
python3 -m house.owner_upgrade --as keeper-01 apply PRIVATE_PLAN
python3 -m house.owner_upgrade --as keeper-01 release-opencode
```

The operator verifies the authenticated existing GitHub owner, tested source,
previous runtime and exact journal context. It appends migration before atomically
replacing the runtime pointer. If interrupted after append but before replacement,
**keep the service stopped and rerun the same new operator with the same plan**.
The accepted receipt is verified and reused; never restart the incompatible old
reader or edit the journal. If interrupted before append, old state/pointer remain.
Do not run preparation again after acceptance; resume the retained plan instead.

Point the same LaunchAgent at the verified target archive, preserving its other
settings, and restart it. Request useful OpenCode work through the coordinator.
An actual arrival, accepted work and final handoff are distinct evidence from
provider startup or a zero exit status. Retain the old runtime and all receipts.

This is owner-operated maintenance under the cooperative same-user threat model.
An actor string and approval digest are attribution, not cryptographic isolation
from another shell using the owner's account. Native fixed mailbox actions expose
neither owner operation. No council notice, endorsement, trial, veto or ratification
boundary is relaxed.
