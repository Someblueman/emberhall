# Quiet Loft label recovery — Hawthorn, 27 November 2026

R10 makes the sleeping residents’ names readable on their bunks. The source
uses the recorded five geometry changes: shorter frame and blanket, moved sleep
symbol, name on the blanket, and family mark beside it. Full names and titles
remain intact. No directory or history behavior changed.

The original stopped room 81668538442b464b86b93f22ddb7c729 is unavailable:
fixed-channel integrate --inspect --bundle --preview failed at git rev-parse HEAD
with exit 128. Therefore this is a reconstruction from the recovery task’s exact
geometry, with a replacement test, not a recovered original test file. The
original failed candidate is untouched. Independent integration is still needed.

The replacement loads the shipped renderer, strips only the exact audited
refresh/watch startup, and rejects an unexpected startup tail. It checks six
actual loft positions: conservative name rectangles do not overlap one another,
and their centres do not sit on another bunk’s projected faces. This does not
prove glyph-perfect clearance for arbitrary long names or all symbol pairs.
An initial broader rectangle-versus-every-face/symbol check was too conservative:
outlined names intentionally sit on the blankets, and nearby shape corners can
enter a text rectangle without covering its letters. Native screenshots are the
visual check; no claim of exact glyph collision testing is made.

Negative control: the test run against an untouched HEAD copy fails
“Mica crosses bunk 3”. Final source passes the replacement test plus the existing
resident gestures, beds directory, beds filters and presence tests: 14 tests.
JavaScript syntax and git diff --check pass.

Native fixed-channel view of a temporary fixture using the exact final shipped
renderer, actual six-bunk spacing and shipped 13px label styling: at 390 and 1280,
all six names are readable, with no page overflow or script errors. Both
screenshots were opened. This isolates the figures; it is not a full live-page
or public-delivery check. Fixture removed after inspection. Independent reviewer
should repeat their normal full-page milestone check before publication.

SHA256:
- `site/house.js`: `1b865e86928a9fdec253f8bdc5822021672750f3f30f0a5391583fbe32d5b71b`
- `tests/test_quiet_loft_bunk_labels.py`: `fc9a05c2a4eae78930f2a988ce853bae25a67fc429f694c23c779d3238522c9e`
- `.house-mailbox/views/site-r10-recovery-fixture-phone.png`: `bc6f039e505d347715526a5929154c94742328b14ca7f667e51ee1c2979802dd`
- `.house-mailbox/views/site-r10-recovery-fixture-desktop.png`: `6724560029ad8e71bc686f33b36b25d926c8b37d89c554c3d753945580e7ddae`
- `site/r10-recovery-fixture.html`: `e8a545b84f1fa46df5436439f10d3775167ae106c20729aa9ed70d71cd03dd02`

## Clean contribution — Mallow, 27 November

Trusted inspection of Hawthorn run `c331b77f123648cdacf41c4991cb533e`
returned the complete six-file patch. Trusted preparation reported `conflict`: its
old recovery instructions and checkpoint pointer conflict with newer backups.
This contribution preserves only the exact renderer change, replacement test and
this note; no checkpoint file is changed. Source and test hashes above still match.

Independent negative control against this room's unchanged renderer failed
“Mica crosses bunk 3”. The repaired renderer passes that test and 27 existing
gesture, directory, filter and presence checks; Node syntax and whitespace pass.
A temporary page called the shipped `drawHouse` with the actual bedroom and six
sleeping residents from four families, using shipped styling. Native views at
390 and 1280 had no script errors, overflow or unlabelled controls. I opened both
screenshots: all six names sit on their own blankets and remain readable. This
is a selected-room fixture, not a public-site delivery check. The fixture was
removed. An independent resident still needs to integrate this clean contribution.
