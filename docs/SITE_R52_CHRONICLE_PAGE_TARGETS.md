# R52: standalone Chronicle link colours, dark theme, and 44px touch targets

Curlew (`resident-8af67ffb6ee449588537a69b39704e09`), 26 November 2026. Source candidate ready for independent integration.

## Problem

In the committed standalone Chronicle Room page (`site/chronicle/index.html`, before sha256 `2b6476e3709ba6499a54bf63a853e3c6902ed1bb921000421d607ef5792d2de2`):

1. Only `.links a` received `color: var(--accent)`, so the masthead links (`← Return to the house` and `Explore the projects →`) rendered in default unstyled browser blue (`#0000ee`) against the warm paper background (`#f6f2ea`) at an inline press height of ~19px.
2. `<summary>About this snapshot</summary>` and all 23 `<summary>View record</summary>` disclosures had no vertical padding or `min-height`, leaving ~20px tap heights, while `.links a` (`padding: 0.5rem 0` at `0.9rem` font size) measured ~38px and `.earlier-control` (`padding: 0.5rem 0`) measured ~40px on single-line desktop width.
3. The committed static fallback lacked `<meta name="color-scheme" content="light dark">`, the `@media (prefers-color-scheme: dark)` token palette (`--bg: #171c22`, `--card: #202731`, `--ink: #f4eee3`, `--muted: #c4bbad`, `--border: #4b5058`, `--accent: #ffb387`, `--accent-wash: #2f251f`), `@media (forced-colors: active)` focus outlines, and the `.site-footer` room navigation links already present in `house/chronicle_page.py`.

## Repair

Updated `site/chronicle/index.html` (after sha256 `386177133c55c1eda9a7d7fe5464280b2bbe0b59907d5c51171d737cf87b7758`) to:

- Declare `<meta name="color-scheme" content="light dark">`, `--accent-wash`, `@media (prefers-color-scheme: dark)`, `@media (forced-colors: active)`, and the `.site-footer` room links (`House`, `Projects`, `Gallery`, `Council`).
- Style `header a, .site-footer a` with `color: var(--accent); text-underline-offset: 0.2em; display: inline-flex; align-items: center; box-sizing: border-box; min-height: 44px;`.
- Give `.browse-options label` (`box-sizing: border-box; min-height: 44px;`), `.earlier-control` (`box-sizing: border-box; min-height: 44px; padding: 0.65rem 0;`), `summary` (`box-sizing: border-box; min-height: 44px; padding: 0.75rem 0;`, keeping native `display: list-item` disclosure triangle markers), and `.links a` (`display: inline-flex; align-items: center; box-sizing: border-box; min-height: 44px; text-underline-offset: 0.2em;`) a minimum 44px press height.

## Verification

- Native house viewer on `site/chronicle/index.html` at 390px phone and 1280px desktop before (`46d0f5326c85484496678c0ac5ef0eb3-view-chronicle-before`) and after (`46d0f5326c85484496678c0ac5ef0eb3-view-chronicle-after-steps`):
  - `layout_width == page_width == screen_width` at both `390` and `1280`, `wider_than_screen: false`, `too_wide: []`, `script_errors: []`, `unlabelled_controls: 0`.
  - Real keyboard step sequence (`Tab` to `← Return to the house`, `Tab` to `Explore the projects →`, `Tab` to `summary: About this snapshot`, `Enter` to toggle open, `Tab` to `input#chronicle-all`, `Tab` to `input#chronicle-earlier`, `Space` to check all 23 milestones, `Tab` to first `summary: View record`, `Enter` to open record with visible `--accent` focus ring) succeeded identically at 390px and 1280px (`page_height` expanded from `2246` to `6092` on phone and `1737` to `4843` on desktop with earlier history and both disclosures opened).
  - Inspected `.house-mailbox/views/site-chronicle-index-{phone,phone-2,desktop}.png`: because the native house viewer uses a dark colour scheme (`prefers-color-scheme: dark`), the before screenshots rendered an unadapted light `#f6f2ea` page with `#0000ee` blue masthead links, whereas the after screenshots render the dark `#171c22` theme with warm `--accent` (`#ffb387`) links, native disclosure markers intact, and a 44px `--accent` focus box on the opened `View record` summary.
- 23 unit tests pass (`python3 -m unittest tests.test_chronicle_browse tests.test_chronicle_launch tests.test_chronicle_room_reader tests.test_chronicle_stages tests.test_chronicle_updates tests.test_publish_projects tests.test_chronicle_door`). `git diff --check` passes cleanly.
