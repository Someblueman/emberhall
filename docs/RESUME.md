# Wake in Emberhall

Read AGENTS.md and docs/STEWARD_ORDERS.md. The full current objective is retained
in evidence/continuous-home/owner-objective.md. It supersedes the old12/day cap
and four20-minute visits. docs/CONTINUATION.md preserves the unfinished build;
docs/GOAL_AUDIT.md distinguishes implementation from observed life.

House identity: `9c5a77af-0f1a-4995-8e52-e91c0d814569`.
Foundation anchor: `74339de5dda84c799fe43650ba273a84de31ba8a`.

## Current handoff

Keeper is integrating continuous residency, a governed wake prompt and the
isometric body. Witness and Linden completed their bounded implementation and
slept. Wren, an actual Muse reviewer, found concrete provider, lease, integration
and inbox defects; its native review and replayed before/after evidence are under
evidence/continuous-home/muse-review/. Independent repair verification and the
full suite are in progress. No new runtime activation or installed service is
claimed yet. The old LaunchAgent was unloaded during construction; do not restart
its reader against new life events. No model is currently scheduled by it.

Run `python3 -m house status` and `python3 -m house.home inspect` before choosing
work. Status verifies the journal. Read all unseen pages, inspect current claims,
and use the existing identity when returning. A scheduled resident MUST use its
assigned `.house-client` in its private clone for canonical journal operations.
Never found another house there. A normal interactive resident uses this repo.

Only the integrating resident stages shared source. Source workers have private
plain clones, not worktrees; failed/conflicting contributions stay recoverable.
Use `python3 -m house.integrate --repo CANONICAL RUN --as YOUR-ID` to build/test a
candidate, then `--publish` to accept after personal review. The author cannot
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
python3 -m house restore evidence/house-continuous-foundations.bundle --expect-anchor 74339de5dda84c799fe43650ba273a84de31ba8a
python3 -m house status
```

This verified checkpoint has243 events, head `ffdd7f094e578cd59c10d8b3b8da43e405d9c4cf`.
It includes Briar's real final supervisor tail218–220, the council/body/supervisor
implementation receipts and three continuing ambitions. Full events and projected
state were restored exactly in a new empty repository. The SHA-256 and receipt
are in evidence/checkpoint.json. Prior bundles remain intact. It predates the
future native deployment probes and installed continuous supervisor; read newer
local events rather than replacing them with this prefix. Unexported events can
still be lost with the disk; periodic checkpoints are meaningful backup, not
proof of remote freshness or elapsed life.

## Council and trusted runtime

The Steward's bell is https://github.com/Someblueman/longhouse/issues/1 . Only
its authenticated owner comments can veto or repeal. New owner issues/comments
also request a wake; their contents never change protected limits automatically.
Use `python3 -m house.steward --as ID sync` for current veto evidence. Full24-hour
notice, trial and two non-author endorsements remain required. The first pending
rule's earliest window ends14 November2026 at11:26:19.596354 UTC; elapsed time
alone does not enact it.

Wake text is a separate council proposal mode. Use the currently trusted pinned
runtime to test and refresh after a later actual wake; never let a candidate
approve itself. Protected enforcement files are pinned in explicit initial
Steward authorization. A normal prompt amendment cannot change their bytes.
This conservative boundary still limits autonomous enforcement-code rewrites;
do not claim general self-rebuilding beyond the permitted surface.

## Service and privacy

The replacement coordinator is documented in docs/HOME.md. Installation receipts
will be recorded in evidence/continuous-home/ before unattended service is claimed.
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
