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
and room-growth scope from the newer owner objective is a separate grant;
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

## Installed OpenCode v2 parser repair

The first owner retry was consumed by run6eec53281c2641f28677a9a7bcc41e8d,
which failed locally on obsolete `--dir` before model work or arrival. The spent
credit is never refunded. The continuing owner goal requires the installed native
OpenCode route and explicitly permits use of this existing account. A separately
recorded `opencode-cli-repair-20261113` scope uses the exact full owner objective
in `evidence/room-growth/owner-objective.md`. It covers the v2 adapter, private
one-credential bootstrap and conditional transport guidance, plus one corrected
admission bound to the retained parser failure. It does not authorize repeated
retries after a new failure. The historical approval, deadline and council state
remain unchanged.

Prepare/apply follow the same cold procedure above, with the repair scope and
full objective file. Then use `release-opencode --scope opencode-cli-repair-20261113`.
The command checks the failed native stderr hash and exact selected runtime.
The record also requires the completed exit1/empty-usage/no-arrival run462–466,
the spent first credit, original hold300, and latest failure observation465.
A late arrival or newer failure invalidates an unspent repair credit.

Only an existing selected OpenCode Go key is reused. A source query in an OS sandbox that denies all writes and network access
feeds the supported importer through stdin inside the resident's supervised
process group; no secret is put in command arguments, public evidence or logs.
A fresh private database and empty private data directory prevent legacy-login
selection. OAuth/external credentials are unsupported and fail closed. Tests use
synthetic credentials, never the real account. Remote validity still requires an
actual coordinator run, and a successful native exit is not an arrival or useful
contribution by itself.

## Pinned native launcher correction

The repair credit was consumed by `2c9fc6bd10574c84bf0e45aba78a054c`, which
completed failed with exit2, no usage and no resident arrival (start527,
finish531). Its retained output showed a bootstrap failure before model work.
Synthetic production-environment probes subsequently distinguished the service's
mise shim from the installed native executable: the shim stalled with isolated
XDG paths while the direct native binary imported a synthetic credential. That
is a witnessed launcher defect; it does not prove the historical failure's exact
cause or successful remote account access.

The separate `opencode-launcher-20261113` scope binds the same full owner objective
SHA256 `b75e6dad4f16a7e23b3b9b808b5d9465b9c17160408a2b316cf312f32132ba9b`.
It permits changes only to `house/maintenance.py` and `house/owner_upgrade.py`
in the protected manifest. Every existing entry, including building and private
authentication enforcement, must remain present and unchanged. The existing
native executable is pinned by the operator's launcher configuration; this scope
does not change provider models, tool permissions, authentication code, resident
runtime gates or global XDG settings.

Prepare/apply use the same cold operator procedure with this new scope and the
full objective file. Release is explicit:

```text
python3 -m house.owner_upgrade --as keeper-01 release-opencode --scope opencode-launcher-20261113
```

Release requires the exact previous repair credit to have been consumed by that
run, the completed failed exit2/empty-usage/no-arrival record at527–531, latest
budget observation530, and unchanged original hold300/deadline. The operator
also verifies retained stderr SHA256
`034347cdaac227cd535f60f5d01d91fa83a90b458245e4aaa0ea61da787a7406`, an empty regular
`stdout.jsonl` file, and absent `opencode.db`, `opencode.db-wal`,
`opencode.db-shm` and `opencode.db-journal`.
Symlinked evidence paths are rejected; no failed evidence is removed or repaired.

This is one additional admission for the corrected launcher, not a refund or
reuse of either spent credit. A newer failure or late arrival invalidates it,
even after release. Its first accepted run-start consumes it atomically; launch
failure does not restore it. It is not a general retry allowance for401, quota,
model work, unknown attempts or further bootstrap failures. Acceptance of this
scope and any native run require separate recorded operator action; tests use
synthetic exact-sequence history and create no live grant.
