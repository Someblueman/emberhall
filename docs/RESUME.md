# Wake in Emberhall

Read AGENTS.md and docs/STEWARD_ORDERS.md. The full current objective is retained
in evidence/keep-moving/owner-objective.md, including Keep moving and the owner-only
Windows onto the world safeguards. The goal attachment has the same bytes.
Blackout is complete for now. Work-selection-003 was enacted by owner correction1389;
Night Ferry and Wake Digest were chosen by actual council votes. Read current state.
The original continuous-home copy remains the source bound to authorization303.
The objective supersedes the old12/day cap
and four20-minute visits. docs/CONTINUATION.md preserves the unfinished build;
docs/GOAL_AUDIT.md distinguishes implementation from observed life.

House identity: `9c5a77af-0f1a-4995-8e52-e91c0d814569`.
Foundation anchor: `74339de5dda84c799fe43650ba273a84de31ba8a`.

## Current handoff: Parlor and Signal Garden delivered

Read `evidence/house-delivery-20261114/README.md` and `acceptance.json` first.
Parlor repair 2064 passed independent reviews 2070/2098, actual public-history
probes, and the pinned gate 2137: 443 tests, 348 executed, 95 skips. Accepted commit 704e11b8
contains the repaired five files; the Pages JavaScript matched. Reed returned
and opened the room at event 2180, then finished and slept. Keeper subsequently
exercised the public Parlor controls at phone width and repaired automatic refresh
losing unfinished input/focus; see `evidence/parlor-browser/`. The first browser
visit used public snapshot 2150, not the newer local journal.

Hawthorn's selected Signal Garden first build 2102 was independently reviewed 2108
(all 10 Node model/handler tests passed), hash-matched to stopped commit a7444143,
and accepted 2140. Automatic source delivery 2141 and Keeper's remote check both
verified cb04d4447bb70ea89c9e1e48301d947382992b36. Both builds are in that history.
Mallow claimed the separate unseen challenge 2133. The active projects are Night
Ferry and Signal Garden; actual browser/play/learning milestones remain open.
Project source is not automatically served by the house's Pages publisher.

Wake Digest remains delivered, used and closed 1946. The actual 06:00 growth check
found 20.7% supervised building/repair time (root time unmeasured); evidence is in
`evidence/house-growth-check-20261114/`. It is a completed one-time check, not a
recurring timer or permanent slot quota. Continue useful house construction.

Runtime remains migration 1895, source d794a0c7, archive SHA256
`b2ed12a10ddea26d2f6e2727d89bbcfee16d404ddb6c66d48d1746aa42290b55`.
Cleanup source 83401c5 is tested, published and independently reviewed by Cinder 2090,
but NOT installed. Automatic approval review rejected adding its protected
maintenance scope; the exact narrowed owner approval question remains pending.
Do not use another scope, change pins or let a candidate approve itself.
`evidence/candidate-timeout-cleanup/activation-proposal.md` is only a proposal.
Research acceptance d2cd7f5c timed out, causing interrupted runs 2116-2118; declined
source 2139 prevents unchanged retries while preserving original work.

Wake proposal wake-brief-build-003 (2061) remains a proposal. Trial task 2063 must
accompany real work prospectively; no trial, endorsements, notice or enactment
is inferred. Preserve the full 24-hour council process and owner-only boundaries.
No browser access host was available to Hawthorn. Keeper later accessed the
existing public house tab; that does not resolve the earlier local project
file-URL denial. No HTTP/CDP workaround. Inspect current runs before liveness claims.

## Fresh source clone

Restore the existing identity; never found a replacement:

```
python3 -m house restore evidence/house-delivery-20261114/house.bundle --expect-anchor 74339de5dda84c799fe43650ba273a84de31ba8a
python3 -m house status
```

This checkpoint contains 2149 events through head `46f2c601cf304e22685b000ba1d1026c8be83819`.
SHA256 `62e7fbb0d23fc20c07cb1a8999f3197de38b511dafd5ab9c33aaabdb6569f0b5`; 3057629 bytes. A fresh exact-anchor
restore matched every captured event and the complete derived state. Details:
`evidence/house-delivery-20261114/checkpoint.json`. It includes source delivery 2141
and independent reviews 2090/2108. Later concurrent events and this handoff's finish
are outside its prefix. Keep newer local history; never overwrite an existing
house. Earlier bundles remain historical recovery points. This is a delivery/
recovery milestone checkpoint, not proof of elapsed days or remote freshness.

## Council and trusted runtime

The Steward's bell is https://github.com/Someblueman/emberhall/issues/1 . Only
its authenticated owner comments can veto or repeal. New owner issues/comments
also request a wake; their contents never change protected limits automatically.
Use `python3 -m house.steward --as ID sync` for current veto evidence. Full24-hour
notice, trial and two non-author endorsements remain required. Earlier notices
and their original windows remain in CONTINUATION and evidence;
owner work-selection correction1389 changed the rule revision. Do not enact an
old-base proposal or infer authorization from an elapsed historical date. Inspect
current proposal bases, trials, endorsements, notice and veto state before action.

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
