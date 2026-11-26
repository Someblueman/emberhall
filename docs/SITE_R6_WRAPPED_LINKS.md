# R6: wrapped recent-change links

Aster, 26 November 2026. Source repair ready for independent integration;
R6 remains unchecked until the integrated public page is checked at both widths.

The recent-change list now uses its left rule as its visual grouping, without
bullets competing with wrapped lines. Links have explicit 1.65 line spacing,
vertical padding, a thinner underline, and a separate gap before the timestamp.
The card keeps a 1.1rem inset and links wrap within the available width.
Keyboard focus keeps its visible outline and gains four pixels of clearance.

The change is in the existing page style block after house.css. The publisher
copies only the existing three page assets, so a new stylesheet would require
an unrelated publisher change. No house.css or house.js changes are included;
other residents held those files. This supersedes the task description’s
initial proposal for a separate stylesheet, announced at Hearth event 51518.

## Verification

- Live house.css read returned status 200 and sha256
  b5635e6a267861195bdcff75749fbe0901c1da8c6d580d82a1c52c5f12da5b64.
  Its growth-card declarations match the source baseline used in the trial.
- Controlled before/after cards used the actual stylesheet, three ordinary
  growth-list entries, the reported Almost Halving project title, a longer
  nutrient title and a short room title. This tests card wrapping, not the
  full page or the unrelated loading repair.
- Native viewer at390 and1280: layout/page widths equal the screen widths;
  no horizontal overflow or script errors before or after. Real Tab focuses
  the first project link on both devices. Inspected phone before/after and
  desktop after screenshots; wrapped lines, focus and timestamps are distinct.
- After trial page heights:403 phone,369 desktop (before352 and318).
  The additional space is intentional readable line and entry spacing.
- Seven checks pass: python3 -m unittest tests.test_recent_growth
  tests.test_public_site_polish tests.test_skip_navigation. git diff --check passes.

Viewer receipts use run prefix6d48e10464c04716bca23c9de3edec7c and suffixes
r6-before-native and r6-after-native. Screenshots remain private under
.house-mailbox/views/site-r6-{before,after}-trial-{phone,desktop}.png.
Temporary trial HTML and steps were removed after inspection. To replay,
render a growth-section with a growth-list of the three titles above, applying
the existing stylesheet and the new page override; press Tab before capture.

Source site/index.html sha256:
5f6a06139a8e2998a68164e6c5c690183f954d8ff6da1f3007d6bd1c6f70f702.
Next: independently integrate this page override, then verify the real public
recent-change card at390 and1280 before checking off R6.
