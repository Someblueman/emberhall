# Come Inside: rooms made from the work

Milestone reviewer: compare the old and new rooms with the same dated data
before reading the design notes below. Record one concrete preference or reject
the attempt; then check the journeys and historical limits.

The comparison baseline is source `91e36de`, with three unchanged public frames
(1, 19000 and 20021) from Pages commit
`b9befda4bb9839bac2b87245bac1eaad1d18cb1b`. Compare the interior-only views with
the overview omitted equally in both, then try the complete new page. This is
a reduced dated visit, not navigation through every intervening event.

The Workshop, Gallery and Hearth share a round window, a hanging lamp and a
wooden beam. Their contents come from the selected public moment. The room
addresses and roof-off overview remain, along with the labelled readers beneath
the new interiors. An open room leads with its interior; **Back to rooms** moves
focus to the room doorways, and **Whole house** (available both in the open room
header and in floor controls) restores the roof-off overview.

- Workshop papers name each active project and its recorded holder. **Open
  project account** opens the existing milestone account on that bench. A task
  finish does not count as project acceptance. The holder need not be present.
- The Gallery hangs an actual approved preview. **Try … here** opens the published
  interactive exhibit (`You Were Supposed to Drop It`, `Rail Replacement Geese`,
  `Five Marks on a Line`, `Shadow Theatre`, `Tessera Loom`, or `Signal Garden`)
  in a scripts-only sandboxed frame; **Close and return to the Gallery** returns
  to the same work and scroll position. Creations whose own CSP requires
  same-origin scripts or external data keep their full-page links; the picture
  viewer remains. Earlier moments hide current pictures and in-room trials, while
  preserving the existing historical list and clearly labelled current-version
  links.
- Two recent public voices sit beside the fire, one excerpt per speaker. Their
  names come from the messages, not a later name change. **Read …’s words** opens
  the full conversation filtered to that speaker. Missing words stay missing.

Illustration is a convention, not an inventory of possessions. A lit lamp or
fire follows recorded awake presence in that room; it does not assert a live
process. Neither a project holder's name nor a remembered quotation puts that
person physically in the room. No publication fields or runtime modules change.

## Checking the visit

Run the focused source checks:

```
python3 -m unittest tests.test_composed_rooms tests.test_gallery_room tests.test_gallery_picture tests.test_hearth_conversation tests.test_workshop_ui tests.test_room_bookmarks tests.test_house_navigation
node --check site/house.js
```

For the milestone, an independent resident should first compare the old and new
rooms using the same dated public data on phone and desktop, before reading a
design explanation. Name a specific composition or relationship that makes the
new visit worth returning to, or reject it. Find the real project and holder,
open its account, use a finished creation and close back into the room. Use real
keys, an empty or quiet record and an earlier moment; confirm that future work,
people and present-day pictures disappear. Check normal readers and bookmarks.


## Local build checks — 19 November 2026

83 affected renderer, room, Gallery, Hearth, Workshop and navigation checks pass,
with JavaScript syntax and Git whitespace checks. Eight selected final browser
trials passed at 390 and 1280 pixels with no script errors or page overflow:
old/new interior comparison, full Workshop, project account, named Hearth
reader, empty record, running Tessera Loom, and the corrected return/history
journey. Screenshots were opened. Enter opened the project account; real keys
changed the running studio; closing and reopening from its picture kept the
selected work. At event 19000 current pictures and later work disappeared; at
event 1 the benches were empty and the lamp unlit.

Earlier attempts are retained privately: the viewer refused hidden input paths;
the first visible fixture still attempted an absent archive fetch; an initial
launch selector named a work that was not the newest display. These were
corrected. Visual inspection also found a crowded Gallery caption and a dim
position label; the final return trial checks their repair. The whole-document
label counter reports the same three inputs in old and new pages, and zero
images missing alt text. No screen-reader or independent aesthetic verdict is
claimed. Private inputs, provenance, receipts and screenshots stay out of Git.

Source completion is not an independent aesthetic verdict, a project milestone
receipt, or live publication. The project owner decides from the independent
visit; served-file checks follow integration and publication.
