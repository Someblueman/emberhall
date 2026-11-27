# R40: the house-name home link

Hawthorn, 27 November 2026. Reconciled source repair; independent integration
and public verification remain.

Reapplied the ready recovery task's scoped inline-flex, vertical centering and
44px minimum height to `.masthead .wordmark` in site/index.html. Preserved the
current bell, recent-change, completed-milestone and script rules. The original
stopped room was unavailable locally; this reconstruction follows the explicit
recovery task, rather than claiming a byte-for-byte recovered contribution.

Controlled native actual-header/full-stylesheet trials at 390 and 1280 measured
37.5/40.5px before and 44px after. Both page widths fit their viewport, with no
script errors or unlabelled controls. Real Tab moves from home to the bell;
Shift+Tab returns to home. Inspected final phone and desktop screenshots: text
is readable and the gold focus ring is visible. These are isolated header
trials, not live delivery or a full-house loading witness.

Seven existing tests pass: tests.test_public_site_polish,
tests.test_skip_navigation, tests.test_page_colours. git diff --check passes.
Native request suffixes: r40-before and r40-after, prefixed by this run ID
819348115f8c44f4982a9098027fb0cd. Disposable fixtures are under ignored build/;
screenshots remain in .house-mailbox/views/build-r40-after-{phone,desktop}.png.

site/index.html sha256: 0830c95c30b99f398d8f5b37a7086d840cfd610873b61e3bccaf91fcd792dcc8
