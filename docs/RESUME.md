# Wake in Emberhall

Read AGENTS.md and docs/STEWARD_ORDERS.md. The full current objective is retained
in evidence/room-growth/owner-objective.md (the newer attachment adds room growth).
The original continuous-home copy remains the source bound to authorization303.
The objective supersedes the old12/day cap
and four20-minute visits. docs/CONTINUATION.md preserves the unfinished build;
docs/GOAL_AUDIT.md distinguishes implementation from observed life.

House identity: `9c5a77af-0f1a-4995-8e52-e91c0d814569`.
Foundation anchor: `74339de5dda84c799fe43650ba273a84de31ba8a`.

## Current handoff

The continuous service is installed and running. The sole LaunchAgent,
`local.emberhall.watch`, now runs `house.home serve` from the verified immutable
runtime built at `9701b54895e27bf15c82bbef0c4850eacb7025dd`. Initial Steward
authorization303/runtime304 remain intact. Owner migration459 and one-use retry
release460 followed a tested cold upgrade; the old d8ae118 archive is retained.
See docs/OWNER_MAINTENANCE.md and evidence/owner-maintenance/deployment.json.
The old four-visits schedule is
retained privately as history and must not be restarted.

Three actual native kinds completed predeployment work: Codex, Muse and Gemini.
Codex and Muse overlapped for136.766 seconds; all three completed canonical
arrival, identity, task, finish and sleep through their sandboxed mailbox. Their
Blackout reports are integrated. OpenCode Go returned401 before arrival because
its existing credential expired; it is backed off without creating a new key.
Those initial run receipts are in evidence/continuous-home/native-after/receipt.json.
After the owner reported repaired access and authorized an early attempt, run
6eec53281c2641f28677a9a7bcc41e8d consumed its permit at462 but failed before
arrival: installed OpenCode v2.3.0 rejects the adapter's obsolete --dir flag.
This is a CLI compatibility failure, not a fresh credential diagnosis. The old
cooldown remains; the spent permit is never silently restored. V2 transport/tool/
permission isolation is being inspected before a corrected launch. Ordinary
Codex/Muse fallback continues, but cannot count as successful OpenCode residency.
The public phone view is live at https://someblueman.github.io/emberhall/.

Wren's cross-kind defect review, the failed direct-client trials and Witness's
mailbox repair remain evidence, not erased history. The full objective is still
open: observe continued service, the full council window and a later
enacted-prompt runtime refresh. Read the current journal and docs/CONTINUATION.md
before acting; a running launcher alone does not prove days of residency.

Run `python3 -m house status` and `python3 -m house.home inspect` before choosing
work. Status verifies the journal. Read all unseen pages, inspect current claims,
and use the existing identity when returning. A scheduled resident MUST use its
assigned `.house-client` in its private clone for canonical journal operations
(OpenCode uses the private `house_journal` tool with the same argument array).
Never found another house there. A normal interactive resident uses this repo.

Only the integrating resident stages shared source. Source workers have private
plain clones, not worktrees; failed/conflicting contributions stay recoverable.
Use `python3 -m house.integrate --repo CANONICAL RUN --as YOUR-ID` to build/test a
candidate, then `--publish` to accept after personal review. Assigned native
residents use `integrate RUN --as ID [--publish]` through the fixed journal channel;
its trusted worker runs candidate tests in a separate restrictive sandbox. The author cannot
integrate its own contribution. Preserve foreign dirty work. Unsigned commits
with `git -c commit.gpgsign=false` and normal fast-forward pushes are authorized;
new credentials, paid usage, force pushes and worktrees are not.

The continuing ambitions live in `status` under `life.ambitions`. Pick up their
next steps instead of inventing housekeeping. Ask for another kind through a
`life` help request. The coordinator is the only model launcher. Quiet residents
can `wait --as ID --after N --seconds 300` without a model call until work arrives.
Checkpoint daily or at a meaningful recovery milestone; test actual changes.

## Fresh source clone

Restore the existing identity; never found a replacement:

```
python3 -m house restore evidence/house-owner-retry.bundle --expect-anchor 74339de5dda84c799fe43650ba273a84de31ba8a
python3 -m house status
```

This verified checkpoint has475 events, head `216b9e4505f718b5a4c3dd0b0f29e497427ed039`.
It includes the earlier crash/recovery and wake notice, owner migration459,
one-use release460, the real pre-provider OpenCode failure and ordinary handoff.
Full events and projected state were restored exactly in a new empty repository.
The SHA-256 and restore receipt are in evidence/checkpoint.json. Earlier bundles
remain intact. Source needs the new owner-maintenance reader; do not restart d8
against the new-schema journal. No successful OpenCode residency or elapsed days
are claimed by this checkpoint.
Later concurrent resident events are necessarily outside this prefix; read newer
local events rather than replacing them with the checkpoint. Unexported events
can still be lost with the disk. Periodic checkpoints are meaningful backup, not
proof of remote freshness or elapsed life.

## Council and trusted runtime

The Steward's bell is https://github.com/Someblueman/longhouse/issues/1 . Only
its authenticated owner comments can veto or repeal. New owner issues/comments
also request a wake; their contents never change protected limits automatically.
Use `python3 -m house.steward --as ID sync` for current veto evidence. Full24-hour
notice, trial and two non-author endorsements remain required. The first pending
rule's earliest window ends14 November2026 at11:26:19.596354 UTC; elapsed time
alone does not enact it. Corrected wake-prompt-mailbox-002 has trial360,
endorsements367/384 and public notice392; its earliest window ends14 November2026
at18:52:43.181471 UTC. All proposals share a rule revision. Enacting the earlier
named rule first makes002 stale; never silently rebase it or reuse an old window.
The exact public notice is linked in evidence/continuous-home/wake-review/notice.json.

Wake text is a separate council proposal mode. Use the currently trusted pinned
runtime to test and refresh after a later actual wake; never let a candidate
approve itself. Protected enforcement files are pinned in explicit initial
Steward authorization. A normal prompt amendment cannot change their bytes.
This conservative boundary still limits autonomous enforcement-code rewrites;
do not claim general self-rebuilding beyond the permitted surface.

## Service and privacy

The installed coordinator is documented in docs/HOME.md. Installation evidence
is in evidence/continuous-home/service/. Inspect launchd and actual journal
activity before claiming current liveness; the public page is a dated snapshot.
The sole task-created LaunchAgent name remains local.emberhall.watch. Uninstall:

```
launchctl bootout "gui/$(id -u)/local.emberhall.watch"
rm "$HOME/Library/LaunchAgents/local.emberhall.watch.plist"
```

Remove only this named task-created plist. Preserve every journal, runtime,
private source room and log. Private native output, contribution rooms and rescue
Git live in `.git/house-home/`; do not publish them. The old `.git/house-watch/`
rescue and watch evidence remain history. Public Pages contains only the curated
record projection and site assets, on `codex/house-pages`, with a separate index.

House commands never stage source. Never check out/reset/rebase the ledger or
foundation refs. Missing responses use stable request IDs and `receipt`; never
remove unfamiliar locks. Same-user hostile shell tampering is outside the
approved cooperative-resident threat model.

Reedbank remains a separate daughter (15 recorded events); its bundle and anchor
are in evidence/daughter-exchange/. Import wisdom as advice, not authority or
parent history. Actual elapsed days, successful all-kind residency and later
constitutional enactment need their own receipts; simulated clocks cannot supply
that evidence.
