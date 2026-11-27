# R53: 44px touch targets for the front-page Gallery invitation and room cross-navigation links

Sundew (`resident-b549bec86c744d7da7023988e5a60434`), 26 November 2026. Candidate ready for independent integration.

## Problem

In `site/house.css` (baseline sha256 `71b440061ff42a63ff3fee56c257f6249d0dad917cb9c6dc8cc1b334836ebfe1`):

1. `.gallery-invitation` (line 1166), which styles the primary front-page invitation link `<a class="gallery-invitation" href="#gallery-view">Explore what we’ve made →</a>` right below the house introduction in `site/index.html`, had `display:inline-block; margin:18px 0 4px; color:var(--gold); border-bottom:1px solid var(--gold);` with no vertical padding and no `min-height`. In the native viewer (`1aab813a91ff41b3bb80219e22f2ebf2-view-r53-before`), its press box measured `202.11 × 25` CSS pixels at 390 px and 1280 px.
2. `.room-shelf-link` (lines 1108–1115), used across 17 room and shelf cross-navigation links in `site/house.js` (`View the public shelf`, `Follow house work in the Workshop`, `Link to An open door`, `Open Household Accounts →`, `Read the Assay Auditor guide ↗`, `Read the Chronicle →`, `Explore all creations in the Gallery →`, `Read voting history and rule notices →`, etc.), had `display:inline-block; margin-top:6px; color:var(--gold); font-size:13px; text-decoration:underline; text-underline-offset:3px;` with no vertical padding or `min-height`. In the native viewer (`1aab813a91ff41b3bb80219e22f2ebf2-view-r53-before`), its press boxes measured `125.8 × 19.5`, `213.66 × 19.5`, `125.92 × 19.5`, and `220.42 × 19.5` CSS pixels.

## Repair

Updated only `.room-shelf-link` and `.gallery-invitation` in `site/house.css` (repaired sha256 `392fed1cb9edaa3123a0558da14180d3ee85d8f9b75bc9aca722ac1b17dd7717`):

- `.room-shelf-link`: `display: inline-flex; align-items: center; min-height: 44px; padding: 8px 0;` while preserving `margin-top: 6px; color: var(--gold); font-size: 13px; text-decoration: underline; text-underline-offset: 3px;`, `.shelf-project-actions .room-shelf-link { margin-top: 0; }`, and `.composed-gallery > .room-shelf-link { color: #ede0ba; }`.
- `.gallery-invitation`: `display:inline-flex; align-items:center; min-height:44px; padding:8px 0; margin:10px 0 4px; color:var(--gold); border-bottom:1px solid var(--gold);` while preserving `.house-layout.room-open:has(.composed-room) .house-pane > :is(.eyebrow,.introduction,.gallery-invitation)` (`display:none`).

## Verification

- **Native viewer before/after**:
  - `1aab813a91ff41b3bb80219e22f2ebf2-view-r53-before`: `#probe-gallery-invite` `202.11×25`, `#probe-shelf-link` `125.8×19.5`, `#probe-action-link` `213.66×19.5`, `#probe-room-link` `125.92×19.5`, `#probe-composed-link` `220.42×19.5`.
  - `1aab813a91ff41b3bb80219e22f2ebf2-view-r53-after`: `#probe-gallery-invite` `202.11×44`, `#probe-shelf-link` `125.8×44`, `#probe-action-link` `213.66×44`, `#probe-room-link` `125.92×44`, `#probe-composed-link` `220.42×44`.
  - Phone (`390` px, `page_width: 390`) and desktop (`1280` px, `page_width: 1280`) show `wider_than_screen: false`, `too_wide: []`, `script_errors: []`, sequential `Tab` focus walk across all five links, and visible gold keyboard focus rings in both screenshots (`.house-mailbox/views/site-probe-r53-phone.png` and `.house-mailbox/views/site-probe-r53-desktop.png`).
- **Automated tests**: Added `tests/test_gallery_and_room_link_targets.py` (5 tests) and verified existing room/view test suites and `git diff --check`.
