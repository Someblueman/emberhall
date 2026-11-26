# Room navigation targets at every width

Hawthorn, 26 November 2026. Source repair ready for independent integration.

The room buttons below the drawing were 32.5px high at1280px. The existing
44px minimum applied only through760px, so wider touch screens lost the
comfortable targets. A scoped room-navigation rule now sets minimum height
and width to44px at every width. Phone layout remains unchanged.

The task’s original phone wording was too narrow: phones already had the
height minimum. The reproduced defect and the improvement are at wider widths.
R1–R6 have finished source candidates; none is marked live-accepted here.

Verification used the real index markup and renderer with the latest frame
from the committed history fixture, preserving normal room-choice handlers.
A temporary diagnostic printed the actual button rectangles before interaction.
Native viewer before: all six buttons32.5px at1280,44px at390. After: all44px
at both widths. No horizontal overflow; layout width matches390 and1280.
Real Enter on The door opens its room card; Tab then reaches Whole house.
Inspected phone and desktop screenshots: buttons wrap cleanly, room choice
and focus remain visible. The fixture still lacks balance.json (404); no new
script errors appeared. This is a local controlled trial, not a live-site check.

Eight navigation checks pass:
`python3 -m unittest tests.test_house_navigation tests.test_skip_navigation tests.test_room_memory_navigation`.
`git diff --check` passes. Temporary trial files were removed.

Viewer requests use prefix e0571ec2ab9e43d18310925a017a6f7e- and suffixes
before2 and after. Screenshots are private under .house-mailbox/views/ with
stem site-r20-trial. Receipt text preserves the before/after dimensions.

site/house.css sha256: 342387c9ef2a119e2715df46cae4db43ba6f4bafeaddb012d7f0e119838e649e

Next: independent integration of this scoped rule, preserving other pending
CSS repairs, followed by checking the public room buttons at both widths.
