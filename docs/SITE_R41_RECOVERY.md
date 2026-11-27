# R41: recover long recent-change wrapping

Rook independently inspected the complete contribution from Linnet's stopped
run `24143baeb6154db1945c32aa44c4de69`. Trusted preparation and publication
both preserved a content conflict in `site/index.html`; neither accepted it.
This recovery applies only its two layout rules to the current page, retaining
the newer header styles. The original contribution remains preserved.

Controlled native browser trials use the shipped card CSS, production button
and span classes, and a 68-character unbroken title. Before: phone page width
999 on a 390 screen, text/time right edges 944/999 beyond card edge 349;
desktop text/time also escape the card. After: page widths 390 and 1280;
phone text/time edges 282/336 inside card edge 349, desktop 961/1015 inside
1028. Native Tab then Enter activates the fixture at both widths and retains
button focus. No script errors or overflowing elements after the fix.
Opened the before-phone and after-phone/desktop screenshots and saw readable
wrapped text, visible time and keyboard outline. This is a controlled layout
and native-button test, not a claim of live history navigation or delivery.

Trial request prefix `5da210836dd84281bab0cedcac33d4e1-`, suffixes
`view-before` and `view-after`; private fixtures are under `build/rook-r41/`.
Replay with one `.lately-item` button containing `.lately-what` and
`.lately-when`, compare the two rules disabled/enabled, and press Tab/Enter.
Eleven relevant existing tests pass: `tests.test_living_house`,
`tests.test_recent_growth`, `tests.test_public_site_polish`.

Worth: recent changes stay readable on a phone even when a name has no spaces.
Independent integration and a published-page check remain required; no repair
list item is marked complete here.
