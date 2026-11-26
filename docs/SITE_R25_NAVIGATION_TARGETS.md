# R25: comfortable house-view navigation

Hawthorn, 26 November 2026. Source repair for independent integration.

The five top-level view links were only 34px high at both 390px and 1280px.
Three declarations in the existing `.view-nav a` rule give them a 44px minimum
height and center their labels vertically. Existing horizontal padding and
phone spacing keep all five links in one row. Their destinations are unchanged.

## Verification

The controlled native-browser trial copies the actual navigation from
`site/index.html` and loads the entire actual `site/house.css`. It isolates this
geometry repair from the pending history-loading changes. The before trial
reports all five links at 34px, no horizontal overflow, no script errors, and
five native tab stops in document order at both widths. Both screenshots were
inspected. This is a navigation trial, not a full live-site performance test.

The after trial reports all five links at 44px at both widths, no horizontal
overflow and no script errors. Real Tab reaches House then Projects; Enter
changes the destination to `#projects-view` on both devices. Both after
screenshots were inspected: labels remain centered in one row and the Projects
focus ring stays distinct. The trial uses native fragment navigation; the
existing route tests exercise the actual house route handler.

Existing checks: `python3 -m unittest tests.test_house_navigation
 tests.test_public_site_polish tests.test_skip_navigation` — 11 passed.
`git diff --check` passes.

Viewer request prefix: `66843d7ff98341d8bc6208474f682431-`, suffixes
`nav-before` and `nav-after-local`. The latter presses Tab, Tab, Enter. Temporary
trial pages are removed after inspection; screenshots remain in the private
mailbox. Reproduce with the actual `.view-nav` markup and stylesheet, output
`getBoundingClientRect().height` for each link, then press Tab twice and Enter.

Source `site/house.css` sha256:
`b6c3a2de7a1f3087d7f31bb37e5a3a9b820346554f57b219686f81917dbfcd6d`.

Next: independently integrate the scoped navigation rule, then check the
published page at both widths. The original repair checklist is unchanged.
