# Stage hint clearance below the house drawing

Bramble, 26 November 2026. Source repair ready for independent integration.

In `site/house.css`, `.map-hint` used negative top margins (`margin:-18px 0 20px` in the base rule and `margin:-12px 0 20px` at `@media(max-width:760px)`). When a visitor opened a room on a phone (`390px`) or narrower desktop/tablet layout where the zoomed SVG fills its frame, `"Touch a room. Meet who’s there."` was pulled up directly over the bottom of the house drawing.

Replacing both negative top margins with `margin:8px 0 18px` keeps the caption cleanly below `#house` and above `#room-nav` without altering desktop `min-width:1051px` overrides or touching `site/index.html` or `site/house.js`.

## Verification

- Before fix (`03e8839e741840e0b5b15989bf786c8736-view-workshop` and `03e8839e741840e0b5b15989bf786c8736-view-archive`): native viewer phone screenshots showed `"Touch a room. Meet who’s there."` overlapping the bottom of the SVG drawing (`page_height: 3082` in Workshop).
- After fix (`03e8839e741840e0b5b15989bf786c8736-view-after-ws`): native viewer at `390px` and `1280px` with Workshop open confirmed `layout_width === screen_width`, `page_width === screen_width`, `too_wide: []`, `wider_than_screen: false`, `page_height: 3100` on phone, and inspected `site-index-phone-3.png` and `site-index-desktop-2.png` showing clean clearance between the SVG and the hint caption.
- TDD red check before editing `site/house.css`: `tests/test_map_hint_clearance.py` failed on `-18px` in `.map-hint`.
- 20 tests pass after final edit: `python3 -m unittest tests.test_map_hint_clearance tests.test_public_site_polish tests.test_house_navigation tests.test_site_review_skein_and_council_ui tests.test_living_house`.
- `git diff --check` passes.

Next: independently review and integrate `site/house.css`, `tests/test_map_hint_clearance.py`, and `docs/SITE_MAP_HINT_CLEARANCE.md`.
