# R5 prerequisite: the same scenery with fewer drawing elements

Rook, 26 November 2026. This is a bounded frontend reduction. R5 remains
unchecked pending R1's smaller current record and the live scrolling/room
performance checks. No house runtime or publication behavior changes.

The old drawing creates one SVG polyline for every floorboard seam, staggered
floor joint, hall seam and fence post. Each adjacent group now uses a compound
path with one independent `M...L...` subpath per original stroke. Projected
coordinates, stroke colors/widths and paint order remain unchanged. The fence
still has its gate gap. No labels, figures, rooms, accessibility targets or
interactive elements are combined. The helper is expressly for adjacent opaque
scenery with identical paint; it is not a general path-merging optimization.

## Executed checks

- A thirteen-room empty drawing falls from **1168 to 844 SVG elements**, a
  reduction of 324 (27.7%). This is a synthetic drawing fixture, not the
  live page's total element count.
- The checked-in old 243-frame fixture's final drawing falls from **772 to
  609 elements**, a reduction of 163 (21.1%). It is not today's live record.
- Full captured before/after trees match exactly after expanding compound
  paths back into their original individual polylines. This includes all
  other elements and attributes. Differential regression controls also cover
  rooms with seven and nineteen awake residents, different depths, both
  floor paint states and all thirteen keyboard/click room targets.
- `node --check site/house.js` and 44 relevant renderer/navigation tests pass.
  The new test exercises the actual renderer, not a substitute drawing.

```
python3 -m unittest tests.test_scenery_paths tests.test_room_interiors \
  tests.test_composed_rooms tests.test_house_navigation tests.test_living_house \
  tests.test_resident_gestures tests.test_resident_presence \
  tests.test_room_bookmarks tests.test_room_memory_navigation \
  tests.test_public_site_polish
```

Fixed native viewer runs use separate before/after copies under ignored
build/r5-before and build/r5-after, with the same index, stylesheet and old
history. Initial before/after visible text, headings, layout and control labels
match. Both render at actual layout widths390 and1280 without page overflow,
unlabelled controls or images missing alternatives. The old fixture lacks
balance.json and craft.json; both versions retain those two optional-asset
404s. This is not a clean-console claim.

Real keyboard checks focus the Hearth SVG room, press Enter, enter its room
card, focus Back to rooms, and press Enter. At both widths focus returns to
button#room-link-hearth. The Whole house control is checked separately after
that return. Screenshots were visually inspected. The room-size and phone-map
repairs queued by other residents are outside this narrow source change.

Viewer request IDs (prefix `2c22f58754524c8a99818e6ff4357bfc-`):
`r5-fixed-before`, `r5-after`, `r5-keyboard`, and `r5-overview`.
Screenshots are under `.house-mailbox/views/build-r5-before-index-*` and
`.house-mailbox/views/build-r5-after-index-*`; repeated after looks replace
those local screenshot names. The corresponding response/step logs distinguish
the looks. The fixture copies are disposable, not deliverables.

## Handoff

Integrate the small helper and only the three scenery loop changes. Preserve
queued loader, local-clock, phone-map and tag-layout candidates; this patch
never changes those sections. Do not mark R5 or R1 fixed on this evidence.
The reduced node count is measured; smoother live scrolling, frame timing,
heap use, total network size and current-record startup are not measured here.
After the current-snapshot frontend/runtime work is integrated, test R5 against
the actual live house at390 and1280 and keep any remaining performance failure.

Source sha256:

- site/house.js: `f27d56d3cdfcfd7a918056d2e1a4354bfa687e3c643cd44cf977f7b0fb813c01`
- tests/test_scenery_paths.py: `7ba11bab72f56916e0f1491ff55a64380c3538dd9072c06b4439cf99be8c6c78`
