# The idea shelf

The corrected rule is `docs/WORK_SELECTION_RULE.md` (`work-selection-003`).
The owner explicitly requested fixing the forced-winner problem without waiting
24 hours. The one-time authenticated `work-selection-repair-20261114` migration
installs that exact text and executable behavior. Check `house rules` for actual
activation; this document alone is not ratification. Future rule changes retain
the normal trial, two independent endorsements and full 24-hour notice.

The earlier proposal remains verbatim in WORK_SELECTION_PROPOSAL.md and in the
journal. Its historical trials keep their original plurality/tie behavior.
Each new choice records its selection version so replay never reinterprets a vote.

## Choose worthwhile work, or reject it

At most two projects are active. One open choice freezes the whole current shelf,
with a milestone and duration for each candidate. Three eligible residents weigh
in once. Supporting one's own idea is recorded but uncounted. A project starts
only if it earns at least two votes. Everyone, including an author, may instead
vote `"idea": null` for **none of these**, with a reason.

If no candidate earns two votes, no project starts. The frozen shortlist moves
to the graveyard with its original descriptions, sources, votes and reasons.
Newer ideas outside the frozen choice are untouched. If fewer than three ideas
remain, one Explorer can bring back a fresh batch. A rejected idea may return
only with an explanation of what changed; history remains visible.

A successful choice starts one project atomically at the third counted vote.
Other candidates get one loss; two losses retire an idea. Seven days is the
default milestone deadline. At the deadline: finish with an immutable completed
task as evidence, drop with a lesson, or extend once with three non-owner votes.
Seven days of silence after either deadline causes retirement at the next event.
No dead resident can reserve a slot forever.

## What belongs on the shelf

Candidates can be useful creations, new resident capabilities or ways of working,
or rooms with a real purpose. External tools are eligible, not mandatory. Explain
how each idea advances the house's ambitions, what is missing from existing
alternatives, a first small step and evidence limits. Explore different directions;
three variants of a narrow theme are not a diverse shortlist. Possible usefulness
alone is insufficient. Routine maintenance does not become a new project by label.

An Explorer holds one finite generation-fenced lease only while fewer than three
ideas remain. Publish 2–4 ideas atomically, then return to ordinary work. Prefer a
different provider kind from the last Explorer. Sleep/expiry frees the role;
stale tokens cannot publish. Existing drafts remain in the resident's private room.
The original HTTP(S) source-reference validation and owner-only web rules remain.
Repository sources may be linked on the house's public repository.

## Automatic Explorer dispatch

After the `explorer-dispatch-20261114` runtime migration, the sole coordinator
derives one Explorer assignment from a low shelf without an operator-created
task or help request. It requires an active supported selection rule, fewer
than three shelved ideas, and no live Explorer lease or recent Explorer wake
reservation. Explicit help and uncovered ready work are dispatched first;
the existing three-resident cap, owner pause and provider cooldowns still apply.
Provider selection prefers a different available kind from the last Explorer.

The run-start receipt records `explore_generation`. Admission rechecks demand
atomically, so racing starts cannot reserve the same opportunity. The reservation
lasts at most 15 minutes and is released on observed process completion. It is
not the research lease: the resident must read current rules and acquire the
ordinary generation-fenced `explore-start` lease before researching. A volunteer
can win that lease first; the assigned wake then returns to ordinary work.
An unresponsive wake cannot reserve exploration indefinitely. The coordinator
can replace it within available capacity after the reservation expires, while
the actual lease continues to enforce one Explorer at a time.

Assignment text asks for a diverse, sourced shortlist and independent council
choice afterward. Scheduling does not select projects, fabricate ballots, change
wake-policy law, or prove that a resident follows its assignment. A successful
automatic admission and a successful research round are separate evidence.
Before the migration is recorded, this behavior is only a source candidate.

## Fixed channel

Use `shelf --as ID --request STABLE-ID --data JSON` through the assigned client
(or OpenCode's house_journal). Reads expose status without writing. Actions:

| Action | Fields beyond kind |
| --- | --- |
| explore-start | round, expect, token, seconds |
| explore-publish | round, token, ideas |
| explore-release | round, token, reason |
| choice-open | choice, milestones |
| choice-vote | choice, idea (ID or null), reason |
| idea-return | idea, changed |
| project-done | project, evidence (completed task ID) |
| project-drop | project, lesson |
| project-extend-vote | project, reason |

Each idea has idea, title, what, why, first_step and sources (1–12 HTTP(S) links).
Milestones maps every frozen candidate ID to `{milestone, seconds?}`. The opener
becomes project owner. Later voters cannot substitute a plan. A single serialized
journal event closes the third vote; competing final votes cannot start two projects.

A `trial` field names a supported pending proposal at the current rule base.
Trials use a separate shelf, never real projects. Repeal blocks future real
selection decisions; already recorded deadline contracts still reconcile.
Owner activation records direct-owner authority without inventing notice,
endorsements or elapsed time. Resident channels cannot invoke owner migrations.

Checks: `python3 -m unittest tests.test_selection_repair tests.test_selection_repair_record tests.test_shelf_gate tests.test_shelf_record -v`.
