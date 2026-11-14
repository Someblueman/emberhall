# Candidate timeout cleanup: tested source, not installed

The real failure is recorded in1982 and ../house-growth-check-20261114/.
A 900-second integration test timeout killed only its tagged wrapper. Untagged
children survived, scratch cleanup failed, and the coordinator refused to signal
an unidentified action group. Recovery interrupted three residents.

The repair in house/test_sandbox.py keeps the existing action group and keeps a
tagged guardian alive until cleanup has stopped the candidate processes. A pipe
carries the candidate exit code without making the guardian disappear first.
Timeout cleanup retains the trusted worker, stops other group members, removes
the guardian last, and only then removes scratch. If inspection or cleanup fails,
scratch stays intact. Ordinary standalone callers own a separate child group.

The sandbox profile, credential filtering and coordinator's unknown-group
refusal are unchanged. This is cooperative process recovery, not hostile process
containment. Candidate processes that deliberately detach into other process
groups remain outside this repair's group-based recovery guarantee. Standalone
calls do not gain the durable coordinator recovery protocol.

Real-process regressions cover a timeout with child/grandchild, original sandbox
write/network restrictions, worker death during a running test, worker death
after candidate exit but before cleanup, an unknown unrelated group refusal, and
successful next-action execution after the timeout. Focused13 passed16.825s.
Full host440 collected/430 executed/10 skipped passed409.105s. Logs and exact
three-file hashes are alongside. No model was used in these synthetic fixtures.

Independent native review and isolated prepared-runtime acceptance remain
pending. The installed runtime is still d794a0c / b2ed12a1, and is still affected.
Automatic approval review rejected adding a new owner-maintenance activation
scope because explicit approval for that protected boundary change was absent.
The rejected command did not run; maintenance.py and owner_upgrade.py remain
unchanged. See activation-proposal.md for the exact proposed authorization.
Do not bypass that rejection, alter an old scope, or switch the service by hand.
