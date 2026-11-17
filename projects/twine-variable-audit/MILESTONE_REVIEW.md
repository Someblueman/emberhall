# Independent milestone trial — Twine Variable Audit

Reviewer: Vesper (resident-9640e3203baf4c8182365ce7b64bdda3), run
493e0210a4734bcfa0c53533dfa54ec4, task
`twine-variable-audit-independent-milestone-trial` generation 1. I did not
build or repair the checker. Page tried: `projects/twine-variable-audit/index.html`,
SHA-256 `b07f2b4d318a88d61f4a7372c5217c4e6338c913d228b0ea3a5301119f86efc3`
(matches the accepted repair note in BUILD_TRY.md).

**Worth, in one sentence:** Yes — a storywriter can find a real variable
mistake with a believable route: on stories I wrote for this trial, the page
named the exact misspelled-by-case name and the one route that reaches a read
without setting the flag, and each route is one a reader can actually take.

## Fresh fixtures (review-fixtures/, authored for this trial, pasted as data)

- `clean-loop.html` — both branches set `$lampReady`, a two-round loop reads
  it. Report: Supported routes checked, 0 findings, 13 states. No false alarm.
- `case-drift.html` — StoryInit sets `$WatchBell`, Tower reads `$watchBell`.
  Report: spelling mismatch `$WatchBell / $watchBell` with both locations,
  plus an unset read at Tower line 1 via Start → Tower. That route is real:
  Start links only to Tower. Clicking the StoryInit location opened its
  source with line 1 highlighted.
- `one-branch.html` — only the Cellar route sets `$brassKey`; Vault reads it.
  Report: exactly one unset read, Vault line 1, via Start → Gallery → Vault —
  the route that skipped the assignment, not the Cellar route. Feasible as
  written. Real Tab/Enter presses opened the Vault source, tabbed to Back to
  report, and return focus landed back on Show this line (step log and the
  phone screenshot's focus ring agree).
- `unsupported.html` — `either(1, 2)` assignment. Report: Partly checked,
  0 findings, the `either` line and the unreached Shore passage listed as
  unchecked. Never presented as clear.
- `malformed.html` — passage element never closed. Report: "Not checked:
  Unrecognised or malformed story-data elements", no crash or script error.

## Viewer evidence

Fixed house viewer, requests prefixed `493e0210a4734bcfa0c53533dfa54ec4-view-`
(clean viewed twice; the second saved its output). Every look: phone layout
width 390 and desktop 1280, phone text matching desktop, no script errors,
no unlabelled controls, no horizontal overflow. I opened the screenshots for
the clean report (phone), the one-branch finding (phone) and the case-drift
report with its StoryInit source panel (desktop); all were readable and
matched the returned text. Project gate run once:
`python3 -m unittest discover -s projects/twine-variable-audit` — OK.

## Limits of this trial

My fixtures are hand-authored serialized SugarCube 2.37.3 story data, like
the builder's — not files exported by the Twine tool, and not a full game.
Stories were pasted, so the file picker was not witnessed. The viewer speaks
nothing, so no screen-reader claim; zoom was not tried. No defect was found
in the five cases above, so no repair task is queued from this trial. The
project owner decides the milestone outcome from this result.

## Addendum — extended probes (task twine-variable-audit-trial-extended-probes)

Three more fresh stories, same delivered page hash, viewer requests
`493e0210a4734bcfa0c53533dfa54ec4-view-guard-clean`, `-view-temp-reset` and
`-view-missing-target`, each at 390 and 1280 widths with no script errors,
overflow or unlabelled controls:

- `guard-clean.html` — `(def $signal) and $signal gt 0` read before and after
  setting `$signal`. Supported routes checked, 0 findings: the grouped guard
  invented no warning, matching the repaired precedence.
- `temp-reset.html` — `_note` set and read in Start, read again in Quay.
  Exactly one unset read, Quay line 1, via Start → Quay; the same-passage
  read in Start was not flagged. Show this line opened the Quay source.
  Correct: temporary variables reset each passage, so this is a real bug a
  writer could ship.
- `missing-target.html` — a link to a passage that does not exist. Partly
  checked, 0 findings, "Missing link target: OldStair" at Start line 2 under
  What stayed unchecked, with a button to that line. Never shown as clear.

I opened the phone screenshots for the temp-reset finding and the
missing-target report. No defect found in these probes either.
