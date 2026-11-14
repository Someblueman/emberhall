# Occupants and remembered residents

The owner observed residents accumulating at the Door. The actual1275-event
projection contained Bryn and Ember Muse with ended, interrupted runs and no
sleep event, plus newly woken Juniper. The drawing treated all three as figures.
Wake resets location to Door; read/status/wait do not record room movements.

This display-only repair excludes the existing `unconfirmed` pose from figures,
room occupant counts, room-size growth and displayed bunks. It keeps those
identities and their run histories under a collapsed “Remembered here” section
in their last recorded room. Scars remain where they happened. No journal event,
room assignment, sleep, authority, launcher or runtime was changed. A later wake
restores the same identity as a figure through the existing projection.

Door occupants are labelled “Arrived · no later room activity recorded”. This
does not claim a live heartbeat, reading, waiting or work that was not recorded.
The header separately counts stopped residents without a sleep event.

Seven focused tests passed, including the actual JavaScript map/panel renderer,
existing projection return/history tests and Study/shelf tests. Node syntax and
Git whitespace checks passed. `before.txt` shows the new behavioral test fails
against the previous renderer because the ended resident remains a figure;
`checks.txt` records the repaired result. An initial test harness attempt failed
on Node cross-context array comparison; converting the array in the test context
fixed the harness before the actual before/after check.

Actual browser acceptance used a loopback preview of the real1278-event journal
at a390x844 requested phone viewport. Document/client width were both375px:
no horizontal overflow. The Door showed only Juniper; expanding “Remembered here”
revealed Bryn and Ember Muse with their original interruption labels and histories.
The eight recorded Door scars remained visible. At1270 the Door had zero figures;
at Juniper wake1271 it had exactly the same returning resident ID. The view was
returned to latest and the temporary viewport reset. This verifies the tested
frames/device size, not universal layout or process liveness.
