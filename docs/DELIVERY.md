# Owner-approved local publication

The owner explicitly answered **“Allow unsigned local commits for this task.”**
This resolves the earlier source-signing blocker. Publication uses a per-command
`git -c commit.gpgsign=false commit` override; persistent Git signing settings
remain unchanged. Nothing is authorized for push, authority enrollment, or rule
ratification by this answer.

The source implementation was reviewed and checked before publication. The house
has 29 passing boundary tests, Blackout Kit has 16 passing CLI tests, and the
scaling repair has independent historical-equivalence evidence. No engine or test
source changed while waiting for the signing decision.

Source commit `718469e0df42be33430c1473a5bb6b630a1857e1` was created locally with the authorized
per-command override. A fresh independent `--no-local --single-branch` clone
restored all 63 checkpoint events and matched the full canonical state and event
hashes. Its 29 house tests and 16 Blackout CLI tests passed. The sealed charter
and pending amendment were preserved. Git's persistent signing setting remains
`true`; nothing was pushed.

`evidence/publication.json` records the actual commands, commit, recovery results,
source hashes and test receipts. A subsequent evidence-only commit records these
observations; it does not change the verified engine or tests.

The previous three-turn signing blocker is historical evidence in
`evidence/blocked-audit.json`; it is no longer the current obstacle. Historical
journal return notes remain intact. Events 61–63 record the owner's authorization
and the updated return note.

The full goal is still not complete. See GOAL_AUDIT.md for missing isolated
governance, ratification, multi-day operation and work beyond a single context.
