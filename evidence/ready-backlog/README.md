# Ready work and useful concurrency

The owner observed usually seeing only one or two residents. At889 the verified
scheduler kept one supervised resident home and started extras only for explicit
help requests. Normal open tasks and continuing ambitions could not create demand.
`before.json` retains this witness and proves that the candidate reader reproduces
the installed reader's exact existing state/events, including old task projections.

The repair adds explicit ready work and withdrawal. New tasks may opt in with
`task --ready`; existing unclaimed tasks use `ready TASK --expect GENERATION`,
adding `--blocked` to withdraw them. Readiness uses the existing task generation
CAS and cannot modify a live claim. An expired claim's readiness is metadata,
not a claim that the former writer stopped.

The workload calculation counts all active recorded runs, including warm startups,
and considers claimed active residents occupied even after lease expiry. It covers
ready tasks named by pending/active help once and reserves assigned helpers from
unrelated idle capacity. Existing explicit help requests retain their semantics.
A backlog run-start refences aggregate uncovered demand under the journal writer
lock, and the coordinator recomputes after each accepted start. Failed starts and
stale demand stop the current tick; unchanged quiet state does not fill three seats.
The existing enforced three-run ceiling, provider holds and owner limits remain.

Actual native Codex Fern independently critiqued the design896 and inspected the
refined draft898. No implementation or residency proof follows merely from that
review. `work-contract.md` defines the useful three-way product work for a later
live witness: implementation, independent CLI acceptance and an executable guide
for comparing offline Blackout manifests. Those are independent owned paths and
a real outside-house capability, not fabricated tasks solely to increase occupancy.

The full goal remains active. Tests with inert processes are not native residency,
and no current work proves elapsed days, successful OpenCode, a constitutional
enactment or a later enacted-prompt runtime refresh. Those retain their own gates.
