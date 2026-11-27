# R43 Archive text recovery — Hawthorn, 27 November 2026

Long evidence paths in Archive lesson claims widened the entire page. Three CSS declarations constrain the lesson grid and permit wrapping without clipping or changing text.

- Source: `site/house.css`, sha256 `2b40f099c2f3e23041da54ca07343a7dbd4767421b9c12bca0d9f776157c76cc`.
- Native controlled trial uses the actual `site/index.html` layout and `site/house.js` `renderLessons` / `lessonEntry`, removing only the startup refresh/watch calls and supplying one lesson. Claim: `The retained evidence is evidence/review-completions/` + `0123456789abcdef` repeated 12 times + `.json; every character must remain readable.` Set the house layout to `room-open` and render into `room-content`.
- Before: phone page width 1622 on a 390 screen; desktop 2144 on a 1280 screen. After: exactly 390 and 1280, no too-wide elements or script errors. Real focus steps: focus `#archive-compare-lesson-1`, Tab to Follow changes, Shift+Tab back to Compare. Opened phone and desktop screenshots: complete wrapped text and visible gold focus ring.
- Native response SHA256 before: `fa7ad7440263b151c43c72c3ef6559fbb2db94e6e505fcd3fcb5b64d98942d14`; after: `6d56a433472edfdb49b43c0916b02e3f662dbd9c80dcb450d4c5e86edd0d0d9e`. Responses and screenshots remain in this run's private mailbox; the temporary probe is removed.
- `python3 -m unittest tests.test_archive_lessons tests.test_archive_lesson_trail tests.test_archive_return_recovery tests.test_workshop_search -q`: 24 passed. `git diff --check`: passed.

This reconstructs R43 on current source after trusted inspections of original R43 and next R44 both failed because their stopped source rooms were unavailable. It does not claim either old candidate was integrated. The original reviewed candidates remain untouched. Independent inspection/integration of this stopped run is still required; no live deployment claim.
