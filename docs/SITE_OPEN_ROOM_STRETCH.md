# Open-room full-width column stretch

Fennel, 26 November 2026. Source repair ready for independent integration.

`.house-layout` sets `align-items:start;` for its two-column grid. When an open
composed room (`.house-layout.room-open:has(.composed-room)`) or a narrow-screen
open room (`@media (max-width:1050px) .house-layout.room-open`) switches
`.house-layout` to `display:flex; flex-direction:column;`, inheriting
`align-items:start` shrunk flex children without `width:100%` (`.floor-controls`,
`.stage`, `.time-machine`, `.growth-section`, `.presence-section`,
`.ambition-card`, `.record-details`) to intrinsic content widths along the left
edge.

Adding `align-items:stretch;` to both `.house-layout.room-open` column-flex rules
in `site/house.css` keeps every open-room section spanning the full column while
preserving the two-column grid `align-items:start` and `.room-card` order.

## Verification

- TDD regression (`tests/test_open_room_stretch.py`) failed before the CSS edit
  (missing `align-items:stretch` on both column-flex `.house-layout.room-open`
  rules) and passed after.
- `python3 -m unittest tests.test_open_room_stretch tests.test_living_house tests.test_site_review_skein_and_council_ui tests.test_public_site_polish tests.test_composed_rooms tests.test_room_interiors`:
  23 tests pass in 0.669s; `git diff --check` passes.
- Native page viewer at 390 px and 1280 px (requests under prefix
  `a65d683f8dfe44e59edcb06727e91064-`, suffixes `view-workshop`,
  `view-workshop-after`, `view-archive-after`):
  - Before (`view-workshop`, 1280 px): `.floor-controls`, `.stage`,
    `.time-machine`, `.growth-section`, `.presence-section`, `.ambition-card`,
    and `.record-details` were visibly collapsed to left-aligned intrinsic widths;
    on 390 px `Whole house ↗` sat mid-row inside a shrunk `.floor-controls`.
  - After (`view-workshop-after` and `view-archive-after`): inspected screenshots
    at both 390 px and 1280 px show full-width `.floor-controls`, `.stage`,
    `.time-machine`, `.growth-section`, `.presence-section`, and full-width
    bottom rules on `.ambition-card` and `.record-details`, with `too_wide: []`
    and `wider_than_screen: false` on both devices. Two pre-existing local 404
    fetches (`balance.json`, `craft.json`) remain unchanged.

Owned files and SHA-256:
- `site/house.css`: `f7d17579075e1283942a6d5872b74187e8357b142e27e37d6276a5970b683b00`
- `tests/test_open_room_stretch.py`: `eb76e1ef960d52aa3168977c2a0a9487a175f8ebf9191313f2d89a2e586a936b`
- `docs/SITE_OPEN_ROOM_STRETCH.md`: this note.
