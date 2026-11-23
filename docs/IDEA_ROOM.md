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
- Below the slot summary the panel names this moment's open choice votes (`frame.voting`, with slot, candidate count and counted votes) and open Steward asks (`frame.shelf.needs`), or says none is open or waiting. Both read only the selected frame, never later data.
- Keeper retained Clover's bookcase and reading-table artwork only inside the recorded Study. Up to nine colored bundles represent actual shelved ideas; the panel reports the full count. No room is created by that decoration.

## Compare at the reading table

Choose **Compare** beside two ideas in the Study. The table puts their promises,
audiences, reach, reasons for taking the time, first versions, checks and risks
beside each other. Quoted evidence and research sources have links to open;
missing information says it was not recorded. On a phone each comparison row
stacks with the idea's name repeated so the two accounts remain distinguishable.

One choice shows its name while you find a second. After two choices, other Compare buttons
are disabled until one is removed. **Remove** frees one place; **Clear comparison**
frees both and returns focus to search. The second choice moves keyboard focus
to the comparison. Search, filters and pages keep the chosen pair, and an ordinary
snapshot refresh keeps it too. Visiting an earlier moment removes choices absent
from that moment's shelved ideas and reads all displayed fields from that moment.
Those removed choices are not restored on returning to Latest.

This is a reader's comparison, not a council vote or an eligibility calculation.
**Evidence checked** uses the published `grounded` assessment. The page cannot
infer a number of independent readers or their kinds from that flag. Earlier
records without an assessment remain explicitly unknown. Comparing a proposal
does not establish that its promises are verified results.
