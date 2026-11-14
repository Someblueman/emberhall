# The Parlor (Catch-Up Room)

- **Room ID**: `parlor`
- **Floor**: `0` (Ground floor)
- **Purpose**: A ground-floor catch-up room for tracing what changed in public history between any earlier event and the current moment.

## Behavior

- Reads only the existing public `data.frames` up to the currently scrubbed `index` (never shows future events at an earlier scrubbed moment).
- Completed tasks come from `frame.event.op === "finish"`, with each title read from the preceding frame's `tasks` metadata (the public exporter omits done tasks from `frame.tasks`). A finish at the selected start is included.
- Defaults to the latest 50 events through the current moment, explicitly labelled as a public history window rather than a remembered visitor cursor.
- Allows choosing any starting event sequence through the current moment and jumping directly to cited events for completed tasks, room changes, and project choices. Titles are inserted as literal text, never HTML.
- Remains visibly under construction until independent source acceptance, publication, and a later `room-open` by the recorded builder (Reed, the original builder). This repair does not open the room.

## Verification

- `node --check site/house.js` passes.
- `python3 -m unittest tests.test_catchup_room tests.test_shelf_ui -v` exercises the reducer on realistic public-shaped frames, the rendered panel and Jump control, and the tracked `site/history.json` (243 frames, 29 finish events, zero done entries in any `tasks` list).
- No browser acceptance has been witnessed; this is a Node/DOM-helper check only, with no network or dependency change and no private journal export.
