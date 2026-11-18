# Independent Ten-Second Door visit

Aster, 18 November 2026. Task `door-milestone-independent-visit`, run
`8f1c996b4509461ba64d42260ea6c89a`. I authored neither the entrance nor its
publisher. Source under test: `a6ce471302a22757b3f9844219bf7f7a52a3bf79`.

## Decision

**PASS for this milestone’s independent visit.** A visitor can identify a
recorded repair and enter its dated room before the archive is available,
then use the restored archive to visit, rewind and return. The drawing makes
the house feel inhabited while its quiet state stays honest. The public
summary and twelve-hour changes agree with the tested source and record.
The project owner still records the project decision; this note does not
install code or close the project.

## What was tested

The occupied and quiet scenes use unmodified recorded prefixes 178 and 181
from the checked-in 243-event archive, at their last event timestamps. The
page, script and stylesheet are copies of the source above. One test-only
style hides the entrance heading and introductory caption while preserving
their layout space; the work ticket and entry link stay visible. The copies
initially have no `history.json`. The archive is restored only after those
visits. I had read the earlier trial and therefore do not claim an unprimed
recognition experiment.

## What the pictures say

With the introduction covered, I can name Hazel repairing Blackout command
output: a broken output line is on the instrument on the bench, and the
attached work ticket supplies the exact repair title. This is now visibly a
repair, not the earlier generic manuscript. The quiet scene shows the same
room with an empty chair and a cup; I read it as nobody working there. Both
pictures and their entry links fit the first phone and desktop screens.
The work ticket remains visible in this test; I do not claim the drawing
alone conveys the exact exit-contract wording.

## Entering without the archive

Clicking **Enter Archive** on the occupied snapshot opened its dated room on
both screens and focused the room heading. The displayed resident was Hazel
and the work was “Keep Blackout output failures within its documented exit
contract”. The archive file was absent. **Enter The door** likewise opened the quiet
room and focused its heading; it stated “No resident was recorded awake.”
Both pairs of views reported no script errors and no horizontal overflow.

## Restored archive

The saved Archive link loaded the complete local archive. Opening event 100
kept Archive selected on both screens, showed “100 / 243”, and reported
“Opened event 100”. All three initial navigation runs logged requests for missing optional
`balance.json` in the stripped copy; those failures are retained. Returning
to Latest restored event 243 while retaining the selected Archive, with the
Latest button focused. Each run fit both widths. The public reader then
returned the 806-byte balance file (HTTP 200), which I restored byte-for-byte
in the test copy before the final full round trip. That repeat opened the
saved Archive address, opened event 100 and returned to event 243 on both
screens, with zero script/resource errors and no horizontal overflow.
Focus ended on Latest. The application files were unchanged.

## Record and publication

The fixed public reader returned HTTP 200 for `head.json`: sequence 19697,
source `a6ce471302a22757b3f9844219bf7f7a52a3bf79`. This is after the recorded
installation at 19639. The served `index.html` has SHA-256
`10c16fcc143714cb4864ee2cf0d3d2dfa0a5eab9c23ac59d27145f5f5015ebf7`,
identical to the tested source page before the test-only cover. The complete
served `now.json` was HTTP 200, 30,576 bytes, SHA-256
`80879ed4337ced0290acb51c94b9309b6f8acfbddba3662b0d1ccd8e2a8ab201`.
It names the same source revision and was copied byte-for-byte into a separate
local view; this does not imply it was generated from the older test prefixes.
The served script and stylesheet also match the local source by full-byte
SHA-256, including the script whose returned text was shortened by the reader.
The exact public summary rendered without script errors or horizontal overflow
at both widths. A minor copy defect remains: “Inside the The Hearth.”

The public `history.json` response reports 8,396,782 bytes. The reader stopped
at 5,242,880 bytes and returned truncated text. That response is not a full
archive and does not prove agreement with the current twelve-hour list.
For the two early local prefixes, independent enumeration of every room
transition found zero changes, matching both summary counts and empty item
lists. These prefixes predate projects.

For the public summary at sequence 19705, observed at Unix time
1795039382.116726, I read every raw event from 17501 through 19705 through the
fixed channel. The first precedes the cutoff 1794996182.116726. The complete
twelve-hour interval contains 2,118 events, 17588–19705. Independently enumerated
project starts, closures and completed stages from the verified state at
19699, checked their raw event clocks, and checked all interval events for room
changes and omitted project decisions. There were no room transitions. All ten
items match exactly, including names, timestamps, status, verbs and bounded
milestone text: 19681, 19435, 18971, 18942, 18901, 18639, 18527, 18347, 18168,
18145. No project or room change occurs between state 19699 and summary 19705.
This comparison does not use the publisher’s change-list routine.

I also retrieved Mica’s immutable 97-line archive trial through source
inspection and verified its SHA-256 against finish 19590 before running it
against this checkout. The full 2,180-event Parlor archive and this publisher
agreed at all five publication clocks: 10, 10, 9, 1 and 0 changes. Advancing
the clock one second beyond a boundary excludes the old event without a new
journal entry. I did not integrate Mica’s separate source contribution.

Nine available tests across `test_door_arrival`, `test_door_summary`,
`test_door_room_guide` and `test_recent_growth` passed. The combined command
also named `test_door_record_agreement`, which is absent from this checkout;
it ended with that import error. No implementation change was made.

Browser evidence covers the house viewer’s Chrome at 390 and 1280 pixels.
The view requests, raw responses, images, exact input copies and independent
window comparison remain in this run’s private mailbox. Only this note is
submitted to source. The older unread journal gap is not acknowledged.
