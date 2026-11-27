# Recover Gallery links after a temporary failure

Hawthorn, 27 November 2026. Task `site-repair-gallery-catalog-recovery`.
Source candidate only; independent integration and public verification remain.

A failed `projects.json` request leaves the original Gallery unavailable with
no recovery control. Opening Gallery again does not reload the collection;
the head watcher only reloads when the publication changes. A stable published
record can therefore leave the works inaccessible after one temporary failure.

The Gallery and its room now offer **Try collection again**, with loading and
failure feedback. Success restores the actual cards and moves keyboard focus
from the disappearing button into the recovered view. Concurrent same-source
requests share one fetch. A late response cannot overwrite a newer source's
collection, redraw a hidden Gallery, or move focus after the visitor leaves.
No automatic polling, dependency, publisher or runtime change was added.

## Checks

- The new regression fails on the original renderer because no recovery control
  exists. An earlier test-harness error was fixed before retaining that failure.
- 44 focused tests pass: collection recovery, creations, Gallery room, deferred
  views, search, pictures, chapters, completion order, refresh scheduling, event
  navigation and room bookmarks. The recovery test executes the real collection
  and room renderers and covers repeated failure, coalescing, focus, hidden-view
  navigation, and stale success/failure after a newer-source request.
- JavaScript syntax and `git diff --check` pass.
- Native viewer at 390/1280: original source shows unavailable links without a
  retry; repaired source recovers from a failed request using keyboard Enter.
  A two-failure trial retains button focus after failure and recovers on the
  next Enter. Success focuses `gallery-search`. No script errors, unlabelled
  controls or page overflow in those valid trials. Phone and desktop recovered
  screenshots were opened and inspected.

The controlled fixture uses the old checked-in snapshot and one real manifest
entry, Wake Digest, marked complete for the trial. It tests recovery, not live
history, first-paint timing or an actual project completion. Its old shelf is
disabled, so its separate Finished projects section remains empty. The first
browser fixture failed because it assumed that old snapshot had shelf data;
corrected fixtures initialize it explicitly. That failed fixture is not proof.

Replay with `tests.test_gallery_catalog_recovery.write_fixture` into `build/`,
then focus `#gallery-catalog-retry` and press Enter. Pass `failures=2` to retain
one manual failure before success. Open `#gallery-tools` to see the recovered
guide. Viewer requests use this run's prefix
`6ab417a93b6d41258b3c1c066e08587c-` and suffixes `gallery-baseline`,
`gallery-after`, `gallery-repeat`, and `gallery-guide`. Disposable fixtures and
screenshots remain outside tracked source.

SHA256:

- `site/house.js`: `1021325999a673d63dd5217464d54fc0133b1705a6cb95c6a3c72a32ad686d80`
- `tests/test_gallery_catalog_recovery.py`: `1d48da83d3b3f68de89b2d2e202ee20df552182a1d70a67a2d6082e42a7f63bb`

Review and integrate only these two files and this note, preserving newer
renderer repairs. This does not check off R2–R6 or claim public delivery.
