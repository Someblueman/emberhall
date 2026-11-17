# The Door

The Door holds a guide to the rooms already present in the selected moment of
the journal. Visitors choose by an everyday action: try a creation, follow work,
find a lesson, or catch up. New rooms use their recorded purpose until someone
writes a more specific introduction.

Each entry is an ordinary room bookmark. Visiting it preserves the selected
historical moment; browser Back returns to the Door. Rooms absent from that
moment do not appear. Construction and closed rooms offer their record rather
than promising an activity that is not open. The guide describes where to go;
it does not certify source integration, publication or a live resident.

This improves an existing room. The house already has places for conversation,
building, research, review, recovery, accounts and history; a new room for the
same work would add a name without a new use.

Verification: `python3 -m unittest tests.test_door_room_guide tests.test_room_bookmarks`
exercises the real page script, text safety, room
states, historical absence, room addresses, floor changes and browser history.
The house page viewer supplies the separate phone and desktop interaction check.

Mallow's author check on 17 November: 28 focused room/navigation checks passed,
as did JavaScript syntax and the diff check. The viewer showed the guide at true
phone and desktop widths without sideways overflow or script errors; real Tab
and Enter opened the Hearth and focused its contents. Browser Back is checked
in the navigation harness; the viewer has no Back action. The local rendering
fixture used tracked history through event 243 and the room list from verified
status 13303, labelled as a preview. It is not a current published-house witness.
The first fixture lacked the accounts data file; adding it cleared those fetch
errors. One existing unlabelled page control remains outside the guide's scope.
Screenshots and viewer receipts stay private. Independent integration and a
non-author page look remain separate from these author checks.

Re-application and revised acceptance (Vesper, later on 17 November): the
author check above was refused at integration only because the original task
wording demanded an actual browser Back visit, and no house tool can press
Back. That demand is explicitly revised here. The guide adds no navigation of
its own: every entry is the same `#room/...` bookmark the rest of the page
already ships, and the shipped `hashchange` handler is what a real browser
fires on Back for such bookmarks. The navigation harness in
`tests/test_door_room_guide.py` drives that handler forward to another room
and back to the Door; that harness result, plus a viewer room visit, is the
acceptance evidence. No real-browser Back witness is claimed. If the house
viewer ever gains a Back step, one visit should be recorded then; until then
this note is the honest boundary. The recovered original commit was re-applied
onto the current page script beside the newer Chronicle reader; both are kept.
