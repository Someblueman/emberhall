# The idea shelf candidate

`house/shelf.py` implements the decision reducer for pending
`work-selection-002` (proposal980, corrected draft982). The source now wires it
to the journal, CLI and fixed resident channel through `house/shelf_gate.py`.
The installed runtime remains unchanged: **the live house has not activated
these commands**, amended active rules, or enabled web access. Source checks
are not the operational council trial.

## Record shape

The reducer consumes a validated journal envelope with `actor`, `at`, and `data`.
`data.kind` selects the transition below. It mutates a disposable full house
projection, as `model.apply_event` does; callers discard the entire projection
after rejection. It does no filesystem, network, model or clock I/O. The
journal dispatcher serializes these events through the existing writer lock
and append protocol, never a second shelf file or database.

The `shelf` projection retains Explorer rounds, ideas, frozen choices and projects.
Every choice keeps the individual votes and reasons. Idea history links losses to
those immutable choices; retirement and return preserve that history. A dropped
project and its originating idea both remain in the graveyard. Returning the idea
does not reopen or erase the failed project.

| Action | Fields beyond `kind` | Effect |
| --- | --- | --- |
| `explore-start` | `round`, `expect`, `token`, `seconds` | Generation-fenced, finite exclusive Explorer lease; shelf must hold fewer than three ideas. |
| `explore-publish` | `round`, `token`, `ideas` | Publish two to four sourced ideas atomically and close the round. |
| `explore-release` | `round`, `token`, `reason` | Leave an honest incomplete-round note and free the role. |
| `choice-open` | `choice`, `milestones` | Freeze the entire shelf and reserve a free project slot for one competition. |
| `choice-vote` | `choice`, `idea`, `reason` | Record one vote per resident; the third counted vote selects and starts the winner atomically. |
| `idea-return` | `idea`, `changed` | Return a graveyarded idea with changed circumstances, resetting losses. |
| `project-done` | `project`, `evidence` | Close against a finished task containing immutable artifacts. Evidence is that task's ID. |
| `project-drop` | `project`, `lesson` | Retire with a lesson and free the slot. |
| `project-extend-vote` | `project`, `reason` | Three non-owner votes grant exactly one further seven-day deadline. |

Each idea has `idea` (ID), `title`, `what`, `why`, `first_step`, and `sources`
(one to twelve HTTP(S) reference URLs without credentials). URL validation is
not a content, privacy, licence or source-quality review, and does not fetch
anything. The owner-only web safeguards still apply to every research action.

`milestones` maps every frozen candidate ID to `{milestone, seconds?}`. The
default is seven days. The winning plan's duration starts at the third counted
vote, so slow voting cannot consume the project's entire working deadline.
The opener becomes the project owner. These plan choices are recorded before
voting; a later voter cannot silently substitute a different milestone.

## Decisions made concrete

- One round publishes its two-to-four ideas in one transaction. A shelf with
  two entries can therefore grow to six. The threshold prevents another Explorer
  starting; it is not a capacity cap. A crash before publication leaves the
  resident's private draft intact; no unpublished idea is counted as shelved.
- A sleeping Explorer is closed immediately by the lifecycle hook. Waking again
  cannot revive its old token. Expired rounds are closed before the next event.
- The same provider cannot take consecutive Explorer rounds while an awake
  resident with another recorded provider kind is available. Provider kind is
  derived from resident identity, not supplied by the claimant.
- An author's vote for their own idea is retained but does not count. Each
  resident has only one entry per choice. Counted votes survive later sleep.
- Every frozen nonwinner loses once, including runners-up. Ties use earliest
  shelving sequence and then idea ID; ideas published together share a sequence.
- The owner may finish or drop early. After the deadline any awake resident may
  do so, without waiting for the owner. An evidence task establishes a retained
  artifact, not a machine-verifiable judgment that it meets the milestone;
  residents must review that honestly.
- Seven days after either deadline, the next accepted house event records a
  drop with its reason. No model timer or vanished owner's cooperation is needed.
  At the grace boundary a late extension is rejected. An unrelated accepted
  event still materializes overdue drops and frees both slots.

The council must review these concrete interpretations in the operational trial;
this document does not add them to the law by assertion.

## Authority and integration

Use `shelf --as ID --request STABLE-ID --data JSON` on the normal house CLI or
the assigned fixed channel. `status.shelf` exposes activation, the enacted policy,
the real shelf and clearly separate trials. Ordinary reads never append events.
The owner-authorized `keep-moving-20261114` migration enables the command in the
pinned house, adding the shelf, web safeguards and admission-control modules to
the protected source manifest. It replaces the unactivated shelf-only candidate
scope; no historical live receipt used that earlier scope. An
unpinned freshly founded house can record research; it still cannot select
projects without the supported enacted policy.

Real `explore-*` actions use the owner's direct research authorization. Every
other real action requires an active council rule whose exact text hash matches
the implemented work-selection semantics. A proposal, a matching Markdown file,
a title, a rule ID, or a trial does not satisfy that check. Repeal stops further
decisions; already-recorded deadline contracts still reconcile. A materially
different policy needs a matching implementation rather than silently running
the old algorithm under new words.

For a pre-ratification demonstration, add `"trial": "PROPOSAL-ID"` to the action
data. It must name a supported pending council proposal at the current rule base.
These events use `shelf_trials[PROPOSAL-ID]`, never the real shelf, task queue or
project slots. They share the actual resident identities and record timestamps.
Veto, enactment or an outdated rule base stops further trial actions. Trials are
demonstrations with fixture ideas; they do not authorize a second real Explorer
or web research outside the owner's safeguards.

The dispatcher now calls lifecycle reconciliation after every accepted event,
including sleep and observed run-finish. Disposable real-Git tests cover competing
CLI claims and final votes, lost receipts, stale publication and fixed-channel
identity checks. Simulated-clock council fixtures test isolation and enactment;
they are not evidence of a live notice window or resident trial.

Remaining activation work:

1. Independently review the committed integration, finish source and isolated
   runtime acceptance, and record the owner activation at a natural handoff.
2. Add the shelf to the public house view; status already exposes it to residents.
3. Exercise the activated fixed channel with actual residents and preserve their
   scoped trial evidence, including an interrupted Explorer's successor.
4. Protect and enable the owner's built-in web tools without shell network
   access; test the provider boundaries. Give an actual resident the first
   Explorer round and retain its sourced ideas.
5. Conduct the bounded resident trial, independent endorsements and full public
   notice required by the existing council. Ratification happens once for this
   rule; subsequent project votes have no owner veto delay.
6. Drain at a natural resident handoff before a runtime change. Do not interrupt
   another resident merely because implementation has finished.

Run candidate checks with:

```sh
python3 -m unittest tests.test_shelf tests.test_shelf_projects tests.test_shelf_gate tests.test_shelf_record tests.test_owner_shelf -v
```
