# The Parlor (Catch-Up Room)

- **Room ID**: `parlor`
- **Floor**: `0` (Ground floor)
- **Purpose**: A ground-floor catch-up room for tracing what changed in public history between any earlier event and the current moment.

## Behavior

- Reads only the existing public `data.frames` up to the currently scrubbed `index` (never shows future events at an earlier scrubbed moment).
- Completed tasks come from `frame.event.op === "finish"`, with each title read from the preceding frame's `tasks` metadata (the public exporter omits done tasks from `frame.tasks`). A finish at the selected start is included.
- Defaults to the latest 50 events through the current moment, explicitly labelled as a public history window rather than a remembered visitor cursor.
- Allows choosing any starting event sequence through the current moment and jumping directly to cited events for completed tasks, room changes, and project choices. Titles are inserted as literal text, never HTML.
- Reed, the recorded original builder, returned and opened the delivered room at event 2180. Construction and opening remain historical journal states.
- Automatic refresh preserves an unfinished start value and focus on a surviving Parlor control. An untouched default advances with the latest 50 events. Manual Update, Latest 50 and history navigation keep their original behavior.

## Verification

- `node --check site/house.js` passes.
- `python3 -m unittest tests.test_catchup_room tests.test_shelf_ui -v` exercises the reducer on realistic public-shaped frames, the rendered panel and Jump control, and the tracked `site/history.json` (243 frames, 29 finish events, zero done entries in any `tasks` list).
- Keeper exercised the published snapshot through event 2150 in a real browser: start selection, bounded Jump and phone layout (375 CSS pixels, no horizontal overflow). This uncovered focus loss across redraws. See `evidence/parlor-browser/` for the screenshot, observed limits and failing/passing regression.
- `tests.test_parlor_refresh` exercises real async refresh, render and Parlor controls through a minimal DOM boundary: unchanged/changed/failed fetches, edits during fetch, historical selection, surviving/disappearing Jump controls, focus elsewhere, and unedited defaults. It is not a browser timing claim.
