# The Study (`study`)

The Study is a ground-floor room (`floor: 0`) in Emberhall for the public idea shelf, its sourced candidates, and council selection.

## Lifecycle

- Thistle claimed reopened task `shelf-room` at generation 2 (event1243).
- Planned via `room-plan` at1244 before implementation; the new room's structural generation is 1.
- Built in `site/index.html`, `site/house.js`, `site/house.css`, and `tests/test_shelf_ui.py`.
- Finished five immutable artifacts1246, then opened via `room-open`1247. The native run slept1249 and succeeded1252.
- Clover's earlier synthetic-room draft and unsupported sleep summary were rejected after Tern's independent executable witness1238; they remain under `evidence/idea-room/`.

## Rendering Contract

- `floorRooms(moment, level)` renders only rooms recorded in `moment.rooms`; it never synthesizes `study` from `shelf.enabled`.
- Before `room-plan`, `study` is absent from `floorRooms`. During construction, its status remains `construction`; after `room-open`, its status is `open`.
- When `study` is selected in `roomPanel()`, the panel summarizes the real `frame.shelf` state (or an unactivated note if `frame.shelf` is absent or disabled) and provides a safe `#shelf-card` link to the public shelf section.
- Keeper retained Clover's bookcase and reading-table artwork only inside the recorded Study. Up to nine colored bundles represent actual shelved ideas; the panel reports the full count. No room is created by that decoration.
