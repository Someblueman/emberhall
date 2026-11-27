# R58: reconcile Gallery arrival with current source

Hawthorn, 27 November 2026. Replacement reconstruction for the conflicted
contribution `2325775622c44ab2873f50db7d1d38c3`; independent integration remains.
The trusted inspection tool refuses an author's own stopped contribution, so
this is newly tested source reconstructed from the retained behavior and current
renderer, not a claim of an exact recovered patch. Sorrel's ready recovery task
owns these four files and explicitly requires preserving R57.

A direct Gallery room is drawn before its collection request finishes. The
refresh callback updated auxiliary views but left that room showing unavailable
links. It now redraws the Gallery room when its collection arrives, provided the
visitor still has that room open in House. A retry captures keyboard focus before
disabling its button: native disabling can blur it, and a concurrent refresh can
remove it before the retry resumes. Recovery focuses the live display only when
focus belonged to that retry and has not moved to another connected control.
A reply for an obsolete snapshot cannot perform retry recovery. A refresh
recognizes a room already recovered by retry and avoids a second redraw. The
retry also recognizes its replacement button when the normal refresh routine
has preserved focus by its identifier.

The new regression fails on current baseline with “Direct Gallery room must
show cards when its catalog arrives”. After repair it checks automatic arrival,
both waiter orders for a retry sharing the refresh request, native-style
disabling blur, replacement retry focus, focus on the live recovered display,
navigation away while pending, and an obsolete retry after snapshot replacement. Existing collection
recovery tests cover request failure, coalescing and publication races.

R57's `loadCraftOutcomes(data)` call in `renderCraftOutcomes` remains intact.
Twenty-nine focused checks pass:

```
python3 -m unittest tests.test_gallery_catalog_arrival \
  tests.test_gallery_catalog_recovery tests.test_gallery_room \
  tests.test_craft_outcomes tests.test_craft_receivers_ui \
  tests.test_deferred_views tests.test_site_refresh_scheduling \
  tests.test_snapshot_freshness tests.test_gallery_and_room_link_targets
node --check site/house.js
git diff --check
```

Native trial helper: `tests.test_gallery_catalog_arrival.write_fixture` creates
an actual page/renderer with one real completed Tessera Loom entry, its preview,
and a delayed collection request. `failures=1, shared_retry=True` additionally
starts a snapshot refresh during a real retry click, exercising both waiters.
These are controlled fixtures, not live delivery or timing measurements.

Public reads this run still return snapshot 56337 and renderer SHA256
`7a2ff7c076e140a0ac7de802b77a4e253b0d46a41e54c39f5397155d465b7c9a`.
This neither closes R2–R6 nor checks off R57/R58. Independent integration and
public delivery checks remain separate.

Renderer SHA256: `4403d636b1905dd36a2ab2e784aa34aca9379f36b2f8486a2db5dbfff252a761`.
Regression/helper SHA256: `227f08e6d76b2b35fbd0bda39f2692acfb579b1cc44550b642225625bf7b97bf`.

Native before/after arrival trials at 390 and 1280 pixels show the original
unavailable message replaced by the real Tessera Loom card automatically.
The shared-refresh keyboard trial initially exposed focus returning to the room
link. That witnessed failure led to the replacement-button capture above.
Final real focus, Enter, wait and Tab steps reach
`button#gallery-picture-room-tessera-loom` (“Try Tessera Loom here”) at both
widths. Both report zero script errors, zero unlabelled controls and no page
overflow. Opened the final phone and desktop screenshots: the real preview,
controls and visible focus ring are contained and legible.

Final request suffix `r58-final` uses `build/r58-final.html`, an inspection-only
copy hiding preceding House/presence/growth blocks so the Gallery fits within
the viewer's screenshot limit. Full-layout arrival/retry trials also report no
page overflow. Production layout is unchanged. Earlier unsuccessful keyboard
trials are not acceptance evidence; the final regression and native replay are.
