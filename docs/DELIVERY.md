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

`evidence/publication.json` records the source commit and fresh-clone recovery
result when they are observed. The clone must restore the exact checkpoint in
`evidence/checkpoint.json` using the command in RESUME.md. It must run independently
of this checkout and retain the sealed charter and pending amendment.

The previous three-turn signing blocker is historical evidence in
`evidence/blocked-audit.json`; it is no longer the current obstacle. Historical
journal return notes remain intact. Events 61–63 record the owner's authorization
and the updated return note.

The full goal is still not complete. See GOAL_AUDIT.md for missing isolated
governance, ratification, multi-day operation and work beyond a single context.
