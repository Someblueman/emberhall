# R49 · Missing-page home link

Hawthorn, 26 November 2026. Task: `site-repair-r49-missing-page-home-target`.

The missing-page screen's EMBERHALL home link measured 112.05 × 19 CSS pixels
at both 390 and 1280 widths. Its native inline text box was much shorter than
the navigation cards below it. The single `.house` rule now uses inline flex,
vertical centering and a 44px minimum height. Destination remains `/emberhall/`.

Native viewer checks used exact before/after copies with a temporary local
measurement script reporting the link's browser rectangle and computed focus
outline. At both widths the changed target measures 112.05 × 44 CSS pixels.
Real Tab presses focus EMBERHALL first and retain the solid 3px focus ring.
The phone and desktop text agree; neither trial reports overflow or script
errors. Opened both after screenshots: focus ring fits inside the page and
content remains clear. Temporary measurement files are removed before finish.

Viewer request aliases (prefix `3b71a44f0ff441cfa801df8dcc7d33aa-`):
`r49-before` (actual original page), `r49-measure-before`,
`r49-measure-after`, `r49-final` (actual changed page).
Screenshots remain in the run mailbox, not a new Git evidence bundle.

Checks: `python3 -m unittest tests.test_publish_not_found -q` — 2 tests pass;
`git diff --check` — passes. No new test for this one-rule style repair.

Source `site/404.html` SHA256: `6b3f233a0f9d5ae34375c91efd71de870868bca6243c194e5242d1e067040cbe`.

Independent integration and live phone/desktop verification remain. The main
page and stylesheet were held by other repairs; neither was edited here.
