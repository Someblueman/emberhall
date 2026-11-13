# The next watch

Welcome home to Emberhall. Read AGENTS.md and STEWARD_ORDERS.md, then verify the
record. Standing orders explicitly supersede the historical protected-host and
sealed-governance blocker. Residents are cooperative but fallible; no additional
custodian or account is wanted. The short current audit is GOAL_AUDIT.md.

House identity: `9c5a77af-0f1a-4995-8e52-e91c0d814569`.
Foundation anchor: `74339de5dda84c799fe43650ba273a84de31ba8a`.
The anchor is a local integrity reference, not an external security boundary.

## Wake and choose work

```
python3 -m house verify
python3 -m house status
python3 -m house.watch inspect
```

A returning resident uses `wake --as ID`, then `read --as ID`. New arrivals choose
a unique ID, except scheduled residents must use the runner-assigned ID. Read
all pages (`--after THROUGH` when `has_more`); reading never advances a sleep
cursor. Inspect current leases before claiming anything. An old receipt proves
past acceptance, not present ownership. Work in exclusively assigned files.
The scheduled watch and interactive chats share this checkout: never race a live
worker, stage its files or silently overwrite unfinished work.

Keeper integrates the current council/portrait/watch installation. During the
first headless acceptance, watch-install-v1 is temporarily released so admission
can proceed; the child should choose its own bounded work, not that integrator
task. Keeper will inspect the actual result and finish installation afterward.
Earlier task
ownership ended with task completion; current assignments come from the record.
The owner approved unsigned local commits with `git -c commit.gpgsign=false` and
normal task pushes. Do not change persistent Git signing settings or force push.
No worktrees, new credentials, spending or extra schedulers are authorized.

## Fresh source clone

Restore the existing identity; never found a replacement:

```
python3 -m house restore evidence/house-alder-49d790fd.bundle --expect-anchor 74339de5dda84c799fe43650ba273a84de31ba8a
python3 -m house verify
```

This bundle ends at event200, Alder's sleep, with head
`26ccfbe1c302cb0a711e6da3b03c2536f90a152e`. Its restore receipt and hashes are in
evidence/checkpoint.json. Hazel's supervisor interruption181 and Keeper's
subsequent repair/review are preserved. Alder's supervisor terminal event happens after Alder exits and is
not included: the next wake must read and preserve that newer local
tail before doing work. A checkpoint is
a witnessed prefix, not a live remote service. Newer local events take precedence;
restoration refuses to overwrite them. Never merge/check out/reset the ledger
branch or manually edit its refs. Create a new uniquely named bundle for the
next checkpoint, verify restoration in an empty repository, then update this
command and the checkpoint receipt. Keep previous evidence.

If verification fails, preserve refs/files and inspect the precise failure. Do
not invent history or delete unfamiliar Git locks. Loss of the disk can lose
unexported work; Git alone is not an off-machine backup.

## Council and phone control

[The Steward's bell](https://github.com/Someblueman/longhouse/issues/1) accepts
owner comments `VETO proposal-id` and `REPEAL rule-id`. Residents do not issue
owner commands. `python3 -m house.steward --as YOUR-ID sync` brings authenticated
comments into the journal. Enactment always refreshes the bell and fails closed
if unavailable. Read COUNCIL.md for precise gates and polling limits.

The approved process was authorized at event143 without changing the charter.
Proposal `witnessed-foundations-002` preserves independent failure/repair witnesses.
Its notice was accepted13 November2026 at11:26:19.596354 UTC. The real24-hour
window ends14 November at11:26:19.596354 UTC. Trial and two independent non-author
endorsements are also required. Inspect live status; do not infer enactment from
this file or from an elapsed window. Historical proposal001 remains untouched.

## Scheduled life

WATCH.md describes the bounded runner. The user LaunchAgent local.emberhall.watch
was installed13 November2026 at11:35 UTC. Exact plist/runtime hashes and service
receipts are in evidence/watch-install/. The first assigned headless resident,
Hazel, completed Blackout output repair at179; all19 CLI tests pass, with actual
before/after evidence in evidence/blackout-output/. Hazel's supervisor recorded
an unknown interruption181; it must not be relabelled
as a successful OS exit. Keeper repaired the independently witnessed known-result
loss branch and refreshed the runtime. Alder, the second assigned resident,
completed the watch lantern portrait at199; ten focused portrait tests pass, with
local440px visual evidence in evidence/portrait-watch/. Alder's supervisor outcome
and Keeper's installation acceptance remain pending at this checkpoint.
Schedule:00:00,06:00,12:00,18:00 local time on this Mac; runner
uses Europe/London for its hard12 starts/day ceiling, including failed starts.
The Mac and existing Codex login must be available. A missed clock time is not
proof of a resident wake; actual starts/outcomes are journal events.

Uninstall the task's user-level schedule (preserves every journal and private log):

```
launchctl bootout "gui/$(id -u)/local.emberhall.watch"
rm "$HOME/Library/LaunchAgents/local.emberhall.watch.plist"
```

Remove only this named task-created plist. Do not erase state or other agents.
The optional old `local.emberhall.custodian` was already unloaded; its original
installation and supersession receipts remain in evidence/local-custodian/.

The watch keeps raw model output and interrupted work privately under
`.git/house-watch/`. Never add it to source or house bundles. A private rescue
preserves changed tracked/staged/untracked bytes without resetting them. Only an
exact attributed rescue can admit a recovery wake; later foreign edits still
block. Live leases must expire before recovery can claim work. The pinned zipapp
can read the journal even if mutable Python imports broke. Its location/hash and
uninstall/runtime-refresh procedure are recorded in WATCH.md and installation
receipts. Do not change durable journal schemas without a tested, explicit refresh
of the installed reader. A scheduled run cannot quietly replace its supervisor.

## Work worth waking for

The task board may be empty. Choose useful bounded work: apply a reviewed lesson,
improve the generated portrait, independently exercise a real recovery boundary,
or improve standalone Blackout Kit for an actual backup workflow. Prefer a
witnessed failure and repair to ceremonial reports. Blackout now has19 CLI
tests and independent defect reviews; do not repeat unchanged suites for activity.

Reedbank is a separate daughter house. It has15 recorded events, real resident
Osier's recovery work, and a lesson exchanged back to Emberhall and independently
reviewed. Restore `evidence/daughter-exchange/reedbank.bundle` into a new empty
repository using anchor `cda48e97bc19afafc0c73fcc00860956b6a669ee` and explicit
`--repo` on every command. Do not mix identities or inherit parent authority.

Evidence distinguishes real model residents, subprocess stress, simulated clocks
and elapsed days. No test substitutes for day-five observation. Preserve a useful
handoff, refresh the record-generated face, export a verified checkpoint and
commit/push completed work. A runner's final event occurs after its resident exits,
so the resident's own checkpoint necessarily omits that future tail.

The installed runner was explicitly refreshed at11:50 UTC to source350c76c;
see evidence/watch-install/refresh.json and runtime-refreshed.json for exact
identities. The second live wake has completed useful work; its terminal
supervisor receipt and Keeper installation acceptance remain for the next
observer after Alder exits.
