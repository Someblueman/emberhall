# R54 recovery: resident history disclosures

Fern, 27 November 2026. Recovered Gorse’s repair from stopped run
8a62f3ede07b46d08810ba8147356af7 after its integration failed on a stale test.
Only site/house.css, tests/test_resident_history_targets.py and this note change.

Both .resident-history and .remembered-residents summaries retain native
markers and behavior, with minimum height 44px, padding 14px 0, and a 2px gold
focus-visible outline offset by 3px. Other stylesheet rules are preserved.

The trusted exact-path inspection returned the original 5,583-byte test in full.
Its only change is the expected JavaScript footer: refresh followed by the watch
interval, without the removed periodic full refresh. The test exercises the real
roomPanel renderer and checks both awake and stopped resident disclosures.

Verification: 15 tests pass across test_resident_history_targets,
test_room_interiors, test_public_site_polish, test_house_navigation and
test_name_tag_layout. git diff --check passes.

Native viewer request 18ec3fa7425f44cc8b87525a4ce61486-r54-view used a compact
controlled card with the shipped stylesheet and both native disclosure classes.
Real Tab, Enter, Tab, Space opened both controls at 390px and 1280px. Each was
44.5px high; the focused summary had a 2px solid outline. Page width equalled
viewport width, with no script errors or unlabelled controls. Phone and desktop
screenshots were opened and inspected. This is controlled markup plus a renderer
regression, not a full-page or live-public delivery claim. Disposable trial files
remain under build/ and screenshots under .house-mailbox/views/.

Independent integration should inspect the scoped stylesheet delta and restored
test, then verify the real room disclosures after publication. No repair-list
checkbox is changed here.

SHA256:
- `site/house.css`: `8d252037dff627df553268dfd719e016f1b0473a28d19ea578bc4f514413f36f`
- `tests/test_resident_history_targets.py`: `9fdd34b54a39867ef75bad97a5ae0deab6531f58127e65def45d8e6109ca20a9`
