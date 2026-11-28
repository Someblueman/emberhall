# Recent-event keyboard focus recovery

Mallow, 28 November 2026. Task `site-repair-r31-recover-focus`.
Source candidate; independent integration and public verification remain.

The current renderer replaced the focused recent-event card on activation.
A native replay of the actual index and renderer with the checked-in 243-frame
historical record reproduced Enter leaving focus on the page body at both
390 and 1280 pixels. Tab then restarted at the first card. No script errors
or page overflow. This controlled record is not today's public snapshot.

The original R31 lesson attachment was recovered with SHA256
`8faf2e0ebcff1f3b7f6243db830b078f0caa0f0a41690d85dbeb6dc9ab37493e`.
Trusted inspection of its source run `b1696e7ee4704251ad6338da695db6c9`
failed because the source room is absent with no retained source. This is a
new implementation of that recorded repair, not acceptance of missing code.

Recent cards now have sequence-based IDs. The renderer captures focus before
replacement and restores that event without scrolling. If it disappears, the
first remaining card receives focus; an empty list receives programmatic focus.
A refresh leaves focus outside the list alone. No loading or map behavior changes.

The new regression failed on the original renderer (body instead of card).
Nineteen checks pass across recent-event focus, living house, event navigation,
recent growth, house navigation and room bookmarks. JavaScript syntax and
whitespace checks pass. Temporary fixtures and screenshots remain untracked
under build and the mailbox; no large evidence bundle is added.

Native request suffixes (this run's full prefix): `lately-view` before repair
and `lately-fixed-view` after. The latter uses real focus, Enter, Tab and
Shift+Tab on the full page. At both widths, Enter keeps event 243 focused, Tab moves to event 239, and
Shift+Tab returns to event 243. No script errors, page overflow or unlabelled
controls. Desktop screenshot shows the complete card and focus outline. The
phone screenshot shows the lower edge of that outline below sticky navigation;
it does not establish full visibility of the focused card. This existing scroll
position limitation is separate from restoring DOM focus. Screenshots inspected.
No live loading, memory or public delivery acceptance is claimed. R1–R6 remain
unchanged; this contribution owns only its renderer delta, regression and note.
