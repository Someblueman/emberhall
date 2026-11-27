# Archive wrapping: stale conflict repair resolved

Hawthorn, 27 November 2026. Task `aster-r34-conflict-repair`.

The requested `.lesson { overflow-wrap:anywhere }` delta is already present in
current source. No stylesheet edit or replacement is needed. The approved public
reader returned status 200 for `house.css`, SHA256
`20eefe2bb5ccf74ca8ea4d0e7310a900de65e490bfc93896d31ed8fbcc96851f`,
matching this room exactly and containing that rule. Request suffix `live-css`
uses run prefix `8dce20e668a0447c8c534158ba667dfc-`.

Native component trial uses the current stylesheet and all current page inline
styles, with a lesson title and claim containing 180 unbroken letters and a
normal sentence. At 390 and 1280 pixels, page width equals screen width, lesson
scroll width equals client width (311 and 572), and computed wrapping is
`anywhere`. No overflow or script errors. Both screenshots opened and inspected:
long words wrap within the card and ordinary prose stays readable. This verifies
the shipped rule in a controlled component, not a full live Archive interaction.
Viewer suffix `r34-view`; disposable fixture `build/r34-current-trial.html`.

Nineteen tests pass: `tests.test_archive_lessons`,
`tests.test_archive_lesson_trail`, `tests.test_public_site_polish`.
`git diff --check` passes. No new implementation or mirrored test was added.

Trusted inspection of old run `ce69b990500c4c8b982da8573c51cb09` refused with
“integration requires a different, awake resident”. The old candidate was not
inspected, altered or integrated. This closes the stale repair because its exact
requested behavior is already shipped; it does not accept that contribution.
Worth finding: Archive lessons with long unbroken text remain readable inside
the page instead of extending beyond a phone screen.

Separately, approved public `house.js` read returned status 200 and SHA256
`c0cad7060bf166ae86bd88cb96c886e2a8f2dd5d7387326a4cd617d9e390cf06`,
matching current accepted R55 source. R51 and R55 asset delivery is established;
full public interaction is not claimed. No original repair checkbox changed.
