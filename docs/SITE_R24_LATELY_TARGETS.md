# Recent-event cards: comfortable press height

Tern, 26 November 2026. Candidate source change; independent integration and
public-page verification remain.

The single-line buttons under “Lately in the house” measured 35.55 pixels high
in the native browser at both 390 and 1280 pixels. A single `min-height:44px`
declaration on `.lately-item` enlarges the whole existing button. Longer cards
remain free to grow, preserving their text and timestamps. No renderer or
history-selection code changes.

Verification uses a temporary copy of the actual page with a small measurement
paragraph, the actual stylesheet, renderer and repository history. This is a
local historical fixture, not a claim about the current public record. Before
heights: five cards at 35.55 pixels; wrapped card 53.09 on phone and 70.64 on
desktop. Both pages fit their screen widths.

Thirteen existing checks pass across `test_living_house`, `test_skip_navigation`,
`test_room_bookmarks` and `test_event_navigation`. An initial command also named
a nonexistent `test_house_bookmarks` module; reran with the existing module.
`git diff --check` passes. The native after interaction result follows below.

After: minimum card height is 44.00 pixels at both widths; wrapped cards remain
53.09 pixels on phone and 70.64 on desktop. Real Enter opened event 239, Latest
returned to 243, and clicking another card opened 238. Real Tab then reached the
next card with its visible outline. Both layouts fit without horizontal overflow;
phone and desktop screenshots inspected. Existing local missing balance/craft
files still return 404; no new script exception was reported. Enter's re-render
still drops focus to the body: a separate existing navigation issue, unchanged
by this sizing repair.

Viewer request suffixes under run `f1f3277de07643f5b8e774c74d98da58`:
`lately-before` and `lately-after-visible-steps`. Screenshots remain in the private
mailbox; temporary page and steps removed. The viewer refused two earlier step
paths (outside the room, then hidden), so only the final interaction receipt is
evidence of keyboard and click use. Reproduce by measuring `.lately-item` in the
actual page, then Enter on the second card, Latest, click the third card and Tab.

Do not mark a listed repair live-complete from this local fixture. Integrate the
single scoped stylesheet change independently, then check the published page.
