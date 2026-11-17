# Open a remembered moment

The House view has an **Open an event by number** field below its history
slider. Enter a positive whole number and press Enter or **Open event**. The
house opens that exact published moment, using the same navigation as room
receipt buttons. The room address stays selected when that room exists there;
an earlier moment cannot show a room that had not been recorded. **Latest**
returns to the newest published moment.

The field accepts digits, surrounding whitespace and leading zeroes. It explains
empty, fractional, negative, scientific-notation and unsafe-size numbers. A
number absent from the loaded snapshot shows the snapshot's event range and
leaves the current moment alone. A missing event inside that range is still
missing; no nearby event is substituted. Before history loads, the control asks
the visitor to try again once it appears. A new submission uses the latest
loaded snapshot, including events added by a successful refresh.

The field has a visible label, numeric phone keyboard hint, a live result and
invalid-state feedback. Enter submits; errors return focus to the field. Its
draft and focus survive the house's redraws because the form is outside the
replaced room content. Results describe a completed navigation, while the
existing event label and snapshot banner describe the current moment.

This is navigation within the already-public snapshot. It neither fetches a
private event nor makes a publication current. Inline style and script travel
with the existing published page; the publisher, history format, room renderer,
journal and runtime are unchanged.

Checks: `python3 -m unittest tests.test_event_navigation
 tests.test_room_bookmarks tests.test_room_memory_navigation
 tests.test_workshop_history`. The publisher check verifies the complete page,
 including inline code, and each external script and stylesheet separately. The event tests
exercise the real navigation function with a small DOM boundary, including a
sparse publication, unloaded history, refreshed data and draft preservation.
Local page-viewer trials and their limits are recorded with the finished task;
they are separate from independent source acceptance and public delivery.
