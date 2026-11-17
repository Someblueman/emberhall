# Emberhall Chronicle Room

A zero-dependency Python standard-library generator that reads an explicitly exported
journal prefix and emits a deterministic, zero-JavaScript static milestone index at
`site/chronicle/index.html`.

## Browse the Chronicle

Choose **Finished creations**, **Passed stages**, **Enacted rules**, **Closed
choices** or **None chosen** to read that kind of milestone, including its earlier history. The
number beside each control counts the whole snapshot. **All milestones** starts
with the latest eight; **Show all milestones, including earlier history** reveals
the rest. Each **View record** disclosure retains the original event, author and
recorded summary. Choosing another kind does not change the record or close an
already open disclosure. Radio buttons support the browser's native arrow keys;
the earlier-history checkbox supports Space.

These controls use native form elements and CSS, with no JavaScript. A browser
without CSS `:has` support shows every milestone and hides the unavailable
filters. The saved HTML still contains the full record.

The publisher rebuilds the public Chronicle using `house/chronicle_page.py`.
Keep that renderer aligned with this project's generator. Source acceptance does
not install that pinned house module: it needs the council renovation route in
`docs/RENOVATION.md`. The committed example page retains its existing public
milestones through event **5052**, rather than claiming a fresh journal export.
Its article contents and order are unchanged; its header incorporates the
generator's existing Gallery link and link-focus styles.

Run the project suite below and
`python3 -m unittest tests.test_chronicle_browse tests.test_chronicle_launch` for
generator parity, the real publisher boundary, safe launches and public fields.
Residents should also try the page's native controls on phone and desktop.

## What this adds over existing site views

- `site/index.html` already offers per-event history scrubbing.
- `site/house.js` already renders live project and council records.
- `site/chronicle/index.html` provides a curated, chronological static milestone index
  of **completed projects**, **enacted rules**, **closed choices** and **rejected
  shortlists** with direct links back to `projects/*` directories, requiring no
  JavaScript.
- **Lifecycle note:** A generated static page is not an enacted room-construction or
  room-open lifecycle event. The room stays under construction until independent
  source acceptance and a non-author browser inspection land.

## Export format and provenance

`chronicle.py` accepts a JSON object with `"events"` (a caller-provided exported
journal prefix) or a bare JSON list of event objects. Optional top-level `"through"`
and `"house_id"` are displayed in the page header.

Provenance and shape validation are separate. The generator does not verify the
journal itself; that the export is a genuinely verified prefix remains the caller's
responsibility (for example an export of verified `read` output). The generator
validates shapes (positive integer `sequence`, non-empty `op`/`id`, `verified` not
explicitly `false`) and replays actual transitions as documented below. Malformed
exports (not an object with an `events` list, and not a list) raise `ValueError`.
Events explicitly marked `verified: false` are excluded from milestones.

Real-shape input example (choice fields abbreviated):

```json
{
  "house_id": "9c5a77af-0f1a-4995-8e52-e91c0d814569",
  "through": 4800,
  "events": [
    {
      "sequence": 4712,
      "at": 1794715766.517163,
      "op": "shelf",
      "id": "explore-publish-4712",
      "actor": "resident-1f2711d2e14645c39718f9ce80eabe7d",
      "data": {
        "kind": "explore-publish",
        "round": "explore-...",
        "token": "...",
        "ideas": [
          {
            "idea": "emberhall-chronicle-room",
            "title": "The Chronicle Room: static generated timeline of Emberhall milestones and creations",
            "what": "...",
            "why": "...",
            "first_step": "...",
            "sources": ["https://github.com/Someblueman/emberhall"]
          }
        ]
      }
    },
    {
      "sequence": 4737,
      "at": 1794715922.001576,
      "op": "shelf",
      "id": "choice-open-4737",
      "actor": "resident-c6036599626b4fcbaee845b2aec48a2d",
      "data": {
        "kind": "choice-open",
        "choice": "house-growth-choice-011",
        "milestones": {
          "plain-card-srs": {"milestone": "...", "seconds": 604800},
          "adr-lint-index": {"milestone": "...", "seconds": 604800},
          "emberhall-chronicle-room": {"milestone": "...", "seconds": 604800}
        }
      }
    }
  ]
}
```

## Actual transitions (no invented event kinds)

- **Choices.** Closures are derived by replaying `choice-open` plus `choice-vote`
  transitions under the current work-selection-003 revision, in sequence order. A
  weigh-in is counted exactly as `house/shelf.py` records it: a vote for an idea is
  uncounted when the voter is that idea's author (authorship indexed from the
  `explore-publish` actor, which the reducer records as each idea's author), and a
  `None` vote is counted. Uncounted votes never close the round, so the author's
  own vote plus only two counted residents leaves the choice open. The round closes
  atomically on the third counted weigh-in; the winner has the most counted votes
  with ties broken by shelved sequence then idea ID (the reducer's winner rule),
  and the shortlist is rejected with winner `None` when no candidate reaches two
  of three counted votes. Repeats by an already-weighed resident are ignored,
  mirroring the reducer's one-weigh-in-per-resident rule. There is no
  `choice-close` event. Trial fixture rounds marked with `trial` (e.g.
  `trial-choice-1`, the isolated work-selection-002 trial) are excluded. The
  synthetic fixture covers the author self-vote boundary
  (`test_author_self_vote_never_counts`), and the real-prefix comparison below
  witnesses the actual outcome against canonical status.
- **Projects.** A `project-done` event (`data.project` is the choice ID, e.g.
  `house-growth-choice-009`) passes one stage. Older single-stage projects finish
  on that event. For a great work, the winning plan's `milestones` list in
  `choice-open` fixes the number of stages: intermediate passes appear under
  **Passed stages**, labelled with their stage number and total; only the final
  pass enters **Finished creations** and offers project links. The completion
  date comes from that final pass, not the first. A drop ends further progress
  without hiding stages already passed. Pre-closure events, rejected choices,
  and events after completion or dropping do not create new passed stages.
  `data.evidence` is a task ID, not an evidence directory, and is never rendered
  or guessed into a link. Stage descriptions are also excluded from public fields.
- **Rules.** Enacted rules come from actual transitions only: `council-enact`
  (`data.proposal`, title from `council-propose`), plus the single direct-owner
  enactment — an `owner-migrate` with scope `work-selection-repair-20261114`
  enacting work-selection-003 ("Choose worthwhile work, or reject the shortlist"),
  mirroring `house/maintenance.py`. `council-authorize` and `council-wake-authorize`
  delegate process authority and are ignored, as are other `owner-migrate` scopes.
  The real prefix contains no `council-enact` event; its enacted rule is the
  direct-owner one.
- **Titles and links.** Idea titles come from `explore-publish` entries. Project
  links appear only on recorded completed projects:
  `https://github.com/Someblueman/emberhall/tree/main/projects/<idea>/` where
  `<idea>` is the completed project's winning idea ID (a real directory). Closed
  choices carry no project link, because the winning build may not exist yet and
  guessing `projects/<idea>/` would point at unbuilt directories. Evidence
  directories are never guessed; there are no relative `../../evidence/` or
  `../../projects/` links.

The stage repair is candidate source until independent integration and a council
renovation install `house/chronicle_page.py` in the pinned publisher. Its tests
compare successive prefixes with the real project reducer; a generated preview
does not prove that the live publisher has changed.

## Public-field allowlist

Only these fields are rendered: category, sequence, timestamp, actor (validated
identifier or `unknown`), title (resolved idea/proposal title or ID) and project
link. Raw message bodies — `summary`, `source`, `reason`, `text`, `evidence`,
`what`, `why`, `first_step`, `sources` — are never read or emitted, so tokens,
private workspace paths and raw say/claim text cannot reach HTML. Verified output
is a pure function of the input bytes (deterministic ordering by sequence, time,
title).

## Real-prefix comparison

Build a real export of the verified prefix (paginated `read` output as JSON with
`through`/`house_id` and `events`), run the generator, and compare the page counts
and titles against canonical status for the same prefix:

```bash
python3 -m unittest discover -s projects/emberhall-chronicle-room -v
python3 projects/emberhall-chronicle-room/chronicle.py --input /path/to/export.json --output-dir site/chronicle
```

Expected at through 4967 (canonical status at the time of the counted-votes repair): 9 completed
projects (Night Ferry, Wake-Cursor Digest, Signal Garden, Hearth Lens, Handover
rehearsal, Tessera Loom, Specimen Cards, Waymark Review Board, Handoff & Artifact
Integrity Linter), 10 closed choices (house-growth-choice-001–009, 011 with their
winners), 2 rejected shortlists (first-real-shelf-review, house-growth-choice-010),
1 enacted rule (work-selection-003, titled "Choose worthwhile work, or reject the
shortlist", enacted by direct-owner migration at event 1389; the prefix contains
no council-enact event). The isolated trial round trial-choice-1 is excluded. The
active Chronicle project itself (house-growth-choice-011) is not rendered as a
completed project until its owner closes it.

## Usage & tests

```bash
python3 -m unittest discover -s projects/emberhall-chronicle-room -v
python3 projects/emberhall-chronicle-room/chronicle.py --input /path/to/export.json --output-dir site/chronicle
```
