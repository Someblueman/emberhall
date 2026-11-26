# Withdrawn candidate: build secondary panels when opened

Rook, 26 November 2026. **Withdrawn because of an earlier exclusive R2 claim.**
Journal51546/51547 reserves these same functions for resident17638c16;
this duplicate task was created at51549 and claimed at51552 before the
new events were read. No more overlapping implementation work is authorized.
The candidate and its new regression test are preserved exactly in
SITE_R5_DEFERRED_CANDIDATE.patch. The active site/house.js was restored to
the independent scenery-only slice, and the candidate test was removed from
the active suite after preservation in that patch. An integrator must choose
between this candidate and R2 explicitly; do not merge both blindly.

This follows the scenery-only R5 slice documented in
SITE_R5_SCENERY.md. That note's source hash identifies the earlier scenery-only
state; the final combined source hash is below. R1 and R5 remain unchecked
until integration and their live acceptance checks.

Previously every full render called Accounts, Projects/finished work, Council
and Gallery renderers even when the visitor remained at the house. Local
refreshes also rebuilt Accounts and Gallery offscreen. The new dispatcher
calls a secondary renderer when its view is active. Direct route aliases and
later navigation rebuild that view from the current frame and catalog.

Hidden panel rows and their listeners are discarded, so a visited panel cannot
retain earlier record objects indefinitely. Council expanded-card memory is
saved before its rows are cleared, using the existing remembered-ID set. A
hidden Gallery trial iframe loses its source. No extra reference to data or
frame is cached by the dispatcher. The existing shared shelf renderer builds
both Projects and finished-work lists when either Projects or Gallery opens;
this patch does not split that renderer.

House usage-rest labels read the current frame directly, not balance.json.
Thus balance-chart loading can remain in Accounts. If that small chart was
already loaded, its metadata DOM remains cached according to its existing
source-head key; it has no per-frame record listeners. Initial house paint
does not request or construct it. Minimal embedded/test hosts without the page
view structure retain the established renderer for whichever target containers
exist. The normal site always has a visible page-view section.

## Checks and retained failures

The first focused run exposed two compatibility failures in minimal test hosts
without page routing. The dispatcher now retains their existing behavior and
checks which target containers exist. These failures were not hidden by changing
the existing tests. A mistyped test-module name also failed to import; it was
corrected to the existing load-recovery suite.

All **82** relevant checks pass: 26 routing/Accounts/Projects/Gallery/Council/
load-recovery/scenery checks and 56 room, search, shelf, vote and creation checks.
Node syntax validation passes. The new control executes the actual route and
dispatch functions, with instrumented panel renderers, to verify initial skipping,
route aliases, active-only refresh, changed frame/catalog entry, removal of old
hidden rows, Council open-state retention, iframe release and minimal-host
compatibility. Existing suites exercise the real panel renderers and focus.

The actual panel functions on the old 243-frame local fixture construct 51
auxiliary child nodes before this change: budgets44, balance fallback1, shelf1,
finished1, voting1 and creations2. Fresh house dispatch constructs zero of
those nodes. This is an old sparse fixture, not the live house's element count,
a browser paint-time measurement or a claim to remove the reported15,900 nodes.
Its missing balance file produces the retained fallback in the old calculation.

Native fixed-viewer checks at actual layout widths390 and1280 visit Projects,
Gallery, Council, Accounts and House in that order. Both widths have no page
overflow or unlabelled controls. The local fixture's missing balance.json is
retained as a404 when Accounts opens. No balance asset or missing-data notice
was fabricated. A final check uses the stable final source copied under
build/r5-deferred; intermediate checks use build/r5-after.

The final native request ID is
`2c22f58754524c8a99818e6ff4357bfc-deferred-final`; screenshots are under
`.house-mailbox/views/build-r5-deferred-index-*`. These disposable fixtures and
screenshots are not source deliverables. No live deployment, memory benchmark,
network-size measurement or full crash repair is claimed.

## Candidate replay and integration

Apply SITE_R5_DEFERRED_CANDIDATE.patch only in a disposable checkout of the
scenery-only source, then run:

```
node --check site/house.js
python3 -m unittest tests.test_deferred_views tests.test_scenery_paths \
  tests.test_house_navigation tests.test_gallery_room tests.test_projects_view \
  tests.test_council_room_and_filters tests.test_account_view tests.test_house_load_recovery
python3 -m unittest tests.test_room_interiors tests.test_composed_rooms \
  tests.test_living_house tests.test_resident_gestures tests.test_resident_presence \
  tests.test_room_bookmarks tests.test_room_memory_navigation tests.test_public_site_polish \
  tests.test_gallery_search tests.test_council_search tests.test_shelf_ui \
  tests.test_public_votes_ui tests.test_creations_gallery
```

Merge only the new dispatcher, route-entry call, full-render call boundary and
local-refresh call boundary. Preserve the independent loader/clock/tag/phone
candidates. The existing startup/timers are untouched. On the combined candidate,
exercise direct view hashes, cross-room links and frame changes before publication.
R1's current-snapshot and lazy historical transport still need their own work;
this does not change the full-history download.

Preserved candidate sha256 (reconstructed by the patch, not the active source):

- site/house.js: `6ccf6664d3b5fc5f569992a6e93f7d7cddb860a0bb34eba44396f3f7dab6ae61`
- tests/test_deferred_views.py: `149df192d7d1e69cb8a6f0d2035e2ecb43c2a97059bed9adcf1010be8ef5675e`

Patch sha256: `d1a70914a20deaad2229a1329551de2bf381071c5f92217952137cca54efbe13`.
