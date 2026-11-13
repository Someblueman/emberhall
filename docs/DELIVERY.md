# Owner-approved publication

The owner explicitly answered **“Allow unsigned local commits for this task.”**
This resolves the earlier source-signing blocker. Publication uses a per-command
`git -c commit.gpgsign=false commit` override; persistent Git signing settings
remain unchanged. The owner subsequently said **“you can push whenever you
want”**, authorizing pushes for this task. Neither answer enrolls authority or
ratifies a rule.

The source implementation was reviewed and checked before publication. The house
has 29 passing boundary tests, Blackout Kit has 16 passing CLI tests, and the
scaling repair has independent historical-equivalence evidence. No engine or test
source changed while waiting for the signing decision.

Source commit `718469e0df42be33430c1473a5bb6b630a1857e1` was created locally with the authorized
per-command override. A fresh independent `--no-local --single-branch` clone
restored all 63 checkpoint events and matched the full canonical state and event
hashes. Its 29 house tests and 16 Blackout CLI tests passed. The sealed charter
and pending amendment were preserved. Git's persistent signing setting remains
`true`. The owner-authorized push to `origin/main` then succeeded; the remote
matched `6653c00499558f713ff9e7d209ad158f1b0f55e8` when checked.

`evidence/publication.json` records the actual commands, commit, recovery results,
source hashes and test receipts. A subsequent evidence-only commit records these
observations; it does not change the verified engine or tests.

The previous three-turn signing blocker is historical evidence in
`evidence/blocked-audit.json`; it is no longer the current obstacle. Historical
journal return notes remain intact. Events 61–63 record the owner's authorization
and the updated return note.

The full goal is still not complete. See GOAL_AUDIT.md for missing isolated
governance, ratification, multi-day operation and work beyond a single context.

`evidence/remote-publication.json` records that remote verification. Source and
the portable 63-event checkpoint are included in main. The live journal refs are
local; a fresh clone uses RESUME.md to restore the bundled history. Pushes remain
authorized for this task after relevant checks; no further routine permission
request is needed. This does not authorize worktrees or governance changes.

## Third-watch publication

The optional custodian and client add35 tests to the existing29; all64 passed, including five disposable real-SSH tests. The previous Blackout16-test evidence remains applicable because its source is unchanged. The latest bundle is evidence/house-custodian.bundle; checkpoint.json names its exact head and recovery.json records its restore comparison. The same per-command unsigned commit and owner-authorized push policy applies. No live deployment or authority change accompanies source publication.

Implementation/checkpoint commit `6d2f64035fcdd12d437bff5671b20c7235efa399` was pushed and origin/main matched it exactly. The worktree was clean and persistent signing remained true. `evidence/custodian/publication.json` records this observation; its subsequent receipt-only commit changes no tested code.
