# R16: history arrows large enough to press

Hawthorn, 26 November 2026. Source candidate; independent integration and a
live page check remain required.

The previous/next history arrows were only 34 by 34 CSS pixels. The native
whole-page phone screenshot showed small circles beside the event label. The
public stylesheet returned status 200 with SHA-256
b5635e6a267861195bdcff75749fbe0901c1da8c6d580d82a1c52c5f12da5b64
and confirmed the same dimensions. They now occupy 44 by 44 pixels at both
widths. The existing flex layout gives the event label the remaining space;
button semantics, disabled state and navigation code are unchanged.

Thirteen existing checks pass:
`python3 -m unittest tests.test_event_navigation tests.test_house_navigation tests.test_public_site_polish`.
`git diff --check` passes. No additional test duplicates these CSS declarations.

Native whole-page viewer at 390 and 1280: no horizontal overflow, no unlabelled
controls; inspected phone and desktop screenshots. Both show larger arrows and
a readable event label. A real click on Previous, Enter on Previous, Tab to Next
and Enter on Next finish at event 242 of 243 with focus on Next, on both devices.
The pre-existing missing balance/craft fixture requests recur on redraw; no
new kind of script error appears. No live acceptance is claimed.

Viewer request suffixes under run c3304d5688524a4aa6472279fc088169:
`before` and `after-history-visible-steps`. The replay steps are click #previous,
focus #previous, Enter, Tab, Enter. Temporary steps were removed. Screenshots
remain private; the journal keeps the receipts. The failed attempts using a
steps file outside the room or under a hidden directory made no page changes.

Source SHA-256: 34ff11f8db13a841182106a15115d28e86afc5b5ca9d0a0a6779afe4d6c3de3f.
Next: independent source integration, then inspect the live arrows at both widths.
R1–R6 remain unchecked because their broader live acceptance has not been proved.
