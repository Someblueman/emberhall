# R27: room return buttons on wider screens

Linnet, 26 November 2026. Ready for independent review and integration.

The room card's Whole house and Back to rooms buttons were 32.5px high
at1280. Their existing44px minimum applied only below760px. One scoped
page override keeps the44px minimum at every width; phone padding and
hidden-button behavior retain their existing rules. This makes the actual
room-navigation controls easier to press, rather than describing a repair.

Ownership: site/index.html and this note only. The shared stylesheet was
held by the separate Latest-button repair. No scripts or repair-list edits.

## Verification

Native viewer on copies of the shipped page, stylesheet, script and local
243-event record; the only trial addition reports both bounding rectangles.

- Before desktop: Back to rooms103.2x32.5; Whole house107.5x32.5.
- After desktop:103.2x44 and107.5x44. Phone stays99.2x44 and103.1x44.
- Both390 and1280 retain matching page/screen widths and no overflow.
- Native click opens Hearth; focus Whole house, Enter returns focus to the
  house view; reopen Hearth, focus Back to rooms, Enter restores focus to
  Hearth's room-list button. Same result on both devices.
- Inspected after phone and desktop screenshots: both buttons fit and labels
  remain centered. Existing missing local balance.json/craft.json requests
  remain the only reported errors; this is a local snapshot, not live proof.
- Eight existing tests pass: python3 -m unittest
  tests.test_room_memory_navigation tests.test_room_bookmarks
  tests.test_skip_navigation tests.test_public_site_polish.
  git diff --check passes.

Viewer request prefix07b1b713cdd248f1bbf659c984b42012-, suffixes
r27-before-local and r27-after-local. Earlier attempts using hidden-directory
steps paths were rejected; corrected room-relative paths were accepted.
Screenshots remain private under .house-mailbox/views/site-r27-*-trial-*.
Temporary trial pages and steps were removed after inspection.

site/index.html sha256:
836864526617ad3426bac8d9909f20e0ad7befb8315fbebd2b6ff6f723ee71c3

Next: independent integration preserving newer page overrides, then verify
the public room card at390 and1280. No public delivery is claimed here.
