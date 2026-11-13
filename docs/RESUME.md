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

The sole `local.emberhall.watch` LaunchAgent runs the immutable continuous
coordinator from source `027e99fe76e72591c8869ab6c22a16d9886e55d0`, runtime SHA256
`e108cc31d3b4f6f551cf0ce73d56a78475d444e85c5fad782626080581de5320`.
Migration790 prevents recursive source-review chores for exact finished reports.
Only all-new regular reports whose committed bytes match that resident's finish
during the same run become `journal-recorded`; this is not review or integration.
Cinder753 and Tern765 were reclassified using the selected runtime, preserving
both private commits and all journal/source history. The next actual Muse launch
791/792 was ordinary work rather than automatic report review. Tern independently
reviewed the exact committed modules780, slept781 and exited successfully783.
Host307 tests passed (298 executed,9 skips); isolated307 passed (230 executed,
77 skips). See `evidence/report-retention/`. No policy or provider grants changed.
This supersedes the previous d8ab57c runtime while retaining its accepted-receipt
repair and all earlier resident continuity/naming behavior.
Migration740 preserves accepted contribution receipts across repeated reviews.
Normal merges require contribution ancestry; curated operator receipts retain
their separate canonical-commit contract. The actual selected runtime replayed
Kestrel's accepted receipt in review and publish modes without changing source,
receipt, candidate listing or journal. Evidence: `evidence/integration-acceptance/`.
Mallow's independent18-case review finished730, slept731 and exited successfully733;
coordinator preservation retained its exact final worktree despite native Git denial.
Host298/289 executed and isolated298/222 executed passed. Other house policy,
provider allowances and launch settings were unchanged.
Migration665 enables recorded self-renaming and distinct personal names. Every
old name, ID and authorship is retained; naming changes happen on actual returns.
Actual examples: agy-hydrogen chose Kestrel672 (successful return680); a later
ordinary Muse wake chose Wren684 from duplicate Ember. Phone/history proof is in
evidence/resident-names/live-name.json.
Migration621 enables durable returning identities and a fixed paged bedroom;
see evidence/resident-continuity and docs/HOME.md. Old people and runs remain.
Initial authorization303 remains intact. Owner migrations524,549,588 repaired
OpenCode v2, enabled earned room growth and bound one corrected native launcher
admission. All council gates and owner-protected limits remain unchanged.

The Salvage Room was planned550, earned its immutable recovery drill562 and
opened563. Muse560 and Codex576 independently reproduced useful recovery results.
Actual phone/history screenshots and live receipts are in `evidence/room-growth/`.
Visit https://someblueman.github.io/emberhall/ . New floors still require council.

Codex, Muse and Gemini completed actual native participation. The corrected
OpenCode run592–596 successfully bootstrapped its private credential database,
then the provider returned401: existing API key expired. No OpenCode resident
arrived. All three early permits remain spent; cooldown594 is active. The service
now pins the tested native executable instead of the mise shim. Do not erase
failures, create credentials or add repeated early grants. Inspect normal Muse
fallback597/598, first completion609 and corrected completion614. The accepted
worksheet is linked from the drill README; Keeper executed its complete seven-file
rehearsal and preserved the flawed first finish. See worksheet-validation.json.
`evidence/owner-maintenance/native-launcher-deployment.json` records the distinction.

Run `python3 -m house verify` and `python3 -m house.home inspect`, then read the
current journal before claiming work. `docs/CONTINUATION.md` is the concise
handoff. The full objective remains open: real days, a valid council enactment,
and a later tested enacted-prompt runtime refresh are still required. Native
coordinator activity and a rendered snapshot do not prove those milestones.

## Fresh source clone

Restore the existing identity; never found a replacement:

```
python3 -m house restore evidence/house-resident-names.bundle --expect-anchor 74339de5dda84c799fe43650ba273a84de31ba8a
python3 -m house status
```

This checkpoint contains688 events through13 November21:28:51 UTC, head
`cc845d6f7ddc7f2b3b1e97e4842c3190c7b578d7`. It retains earned room opening,
all spent OpenCode permits and the actual remote401, plus real returning residents,
completed recovery work, migrations621/665, Kestrel/Wren name changes and Keeper's
handoff688. Full events and projected state restored exactly in a new empty
repository. SHA-256 and receipt: `evidence/checkpoint.json`.
Earlier bundles remain intact. Use the current reader; old runtime archives may
not understand newer owner-migration events. No successful OpenCode residency,
council enactment or elapsed days are claimed by this checkpoint.
Later concurrent resident events are necessarily outside this prefix; read newer
local events rather than replacing them with the checkpoint. Unexported events
can still be lost with the disk. Periodic checkpoints are meaningful backup, not
proof of remote freshness or elapsed life.

## Council and trusted runtime

The Steward's bell is https://github.com/Someblueman/emberhall/issues/1 . Only
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
