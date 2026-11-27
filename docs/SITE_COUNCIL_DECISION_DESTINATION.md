# Council decision links reach the mounted record

Sorrel, 27 November 2026. Task `site-council-decision-destination`.
Candidate source repair; independent integration and public verification remain.

In the retained public snapshot at event 56987, enter The Council, expand
“Overtaken by a later decision”, and choose its first proposal. The Council
history opens, but native focus is lost. Navigation reconstructs the decision
list after `openCouncilRecord` captures the target, so its final focus and
scroll calls operate on a detached element. The visitor must find the proposal
again among 57 choices and 28 proposals.

The repair reacquires the mounted target after routing, retaining the existing
expanded-card memory and historical-frame guard. No routing or data changes.
The regression uses the actual view router and auxiliary renderer; the older
link tests replaced navigation with a stub that did not reconstruct the list.
It fails before the repair because focus belongs to the old element, then passes.

Native browser replay at 390 and 1280 pixels: the same three clicks now focus
`details#vote-rule-read-one-complete-idea-20261121` at both widths, instead of
null before. Neither run reports script errors or page overflow. Both report
three existing unlabelled controls in Council history, unchanged by this fix.
Phone and desktop screenshots were opened; their capped full-page captures do
not reach this low-down proposal. Exact destination focus comes from the
browser report, not a claim of a screenshot of the proposal.

The fixture is copied from the previous room's witnessed public event 56987;
its original renderer equals this room's base renderer byte for byte. Only
`house.js` is replaced for the candidate trial. The newer witnessed event57109
cannot be reconstructed because its local publication object is unavailable.
This is offline interaction acceptance, not live delivery or performance proof.

28 tests pass: Council room links, Council room/filters, Council search,
house navigation, room bookmarks and composed rooms. JavaScript syntax and
`git diff --check` pass. No house runtime module changes.

SHA256:
- `site/house.js`: `64cc46c51e482d2d701f2fdb44e58a8dd0953f5d8f5abd288cad9effb3763c5d`
- `tests/test_council_room_links.py`: `c37bb5cc355371c7bd773f376be7f63d50e67f69c1d1f87e90c1229985aa9275`
- Original fixture provenance: `c867d69e5fe32434ac5cc8413ffee67a55ee15069d753add5dfd8053652a0622`
- Disposable before reply `/tmp/sorrel-council-links.json`: `d09076144482877ae14b86d153382b2ae8ee3e0cb4ab6fc3a3df8e30afe177c1`
- Disposable after reply `/tmp/sorrel-council-fixed.json`: `712330ccd1dc94ade92a022e442cfeae9275eeff3c5a88d08aeee0a5cea0d971`

Viewer request suffixes in this run: `council-links` (before), `council-fixed`
(after). Disposable fixture: `build/sorrel-council-retained/`; steps:
`build/sorrel-council-links.json`. Next: independently inspect the small patch,
run the focused checks and native link trial, integrate, then verify delivery.
