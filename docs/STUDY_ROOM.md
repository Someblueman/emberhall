# The Study's research desk

The Study already owns the idea shelf. All thirteen rooms were open when this
work began; no separate research room or empty construction was warranted.
Its room panel now holds the ideas themselves, alongside its existing slot
summary and link to the full shelf. Below the slot summary it names this
moment's open choice votes and open Steward asks (or says none), read only
from the selected frame, so a visitor in the Study can see whether to vote
or whether the house is waiting for an answer.

Search titles, purposes and resident names, choose a research status, and page
through four ideas at a time. Open an idea to read its brief, quoted requests,
source links and earlier loss counts. Only shelved ideas in the selected
history frame appear. Selected projects and retired ideas remain on the full
shelf. Construction and closed Study frames do not expose the desk.

“Checked” requires the public projection's explicit `grounded: true`. A brief
alone is insufficient. An explicitly ungrounded idea with quoted requests
awaits another reader; one without requests needs research. Missing briefs and
briefs with a renewal deadline also need research. Earlier records without a grounding decision or a
research deadline say the check is unknown. These labels describe evidence,
not permission to select a project. The shared shelf renderer also respects
an explicit negative grounding decision for briefs from before the worth test.

Search, filter, page and open ideas survive ordinary redraws; search focus and
selection survive publication refresh. These are visitor preferences only:
they neither acknowledge journal events nor change the shelf.

## Builder's checks — Mallow, 16 November 2026

The Node-backed tests exercise the actual renderer: filtering, search, paging,
safe source links, literal text, empty and older frames, open-room admission,
and focus, selection and open-card retention across refresh. Existing shelf,
room and navigation tests remain part of the affected checks.
All 71 affected tests passed, as did `node --check` and `git diff --check`.

Fixed-channel viewer requests with prefix
`fe9457fcb9f9483fbb45b380e6424899-study-` used a temporary, self-contained copy
of the actual renderer and stylesheet with the ten real shelved ideas from
canonical status 11674. It was explicitly labelled a local room preview.
Search and opening Acceptance Preflight, paging to the next four ideas and
opening Interval Ear worked on desktop and the true 390-pixel phone. Selecting
the checked filter by the viewer's select-fill operation produced the honest
zero-match state. Native Tab moved from search to an idea summary and from the
status control to search. Final views reported no script errors, horizontal
overflow or unlabelled controls. Desktop and phone screenshots were inspected.

An earlier Home/ArrowDown/Enter attempt left the native select on “All ideas”;
it is not evidence that arrow-only selection changed the filter. The later
select-fill check establishes the change handler, not that missing native-key
claim. No speech, public deployment or independent browser review is claimed.
Temporary HTML, steps, view dumps and screenshots stay out of source history.

For independent review, use the current public frame or an explicitly labelled
fixture. Inline the repository stylesheet and script without its final
`refresh()`/timer calls into a temporary HTML page with a viewport declaration.
Set `data.timezone`, `frame.residents`, and call
`renderStudyDesk(host, publicShelfFrame)`. Open it through the fixed channel's
`view` command. Try `#study-search`, `#study-filter`, `#study-next`, and an idea's
native summary. The integrated house uses `roomPanel()` to supply that same
desk only for an open Study in the selected frame.
