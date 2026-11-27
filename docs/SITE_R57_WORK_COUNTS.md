# R57: show work results when their panel opens

Hawthorn, 27 November 2026. Candidate, not independent integration or live
acceptance. Owns the one loader call, its regression control, this note and
the R57 repair-list entry.

The current-only snapshot initially draws House without Accounts. The work
results loader returns because its panel does not exist. Opening Accounts
later creates “Work and its first review” but never starts its request, leaving
“Loading recent work outcomes…” indefinitely. The same panel is used in the
Counting Room and Archive.

Start the existing loader after creating the panel. Its publication-identity
validation, timeout, in-flight coalescing, cached success and failure message
remain unchanged. Hidden Accounts still makes no request. The existing
snapshot-refresh call safely shares an already pending request.

## Evidence and replay

The regression fails on the original source with zero requests on panel entry.
After the change it covers lazy initial loading, repeated entry while pending,
successful results, mismatched-publication rejection, failed requests and a
late reply that cannot repaint a newer snapshot. These focused commands pass:

```
python3 -m unittest tests.test_craft_outcomes tests.test_craft_receivers_ui \
  tests.test_deferred_views tests.test_account_view tests.test_snapshot_freshness
python3 -m unittest tests.test_counting_room tests.test_archive_lessons \
  tests.test_archive_lesson_trail tests.test_craft_receivers_ui
node --check site/house.js
git diff --check
```

Rebuilt the witnessed public snapshot with `scripts/public_site_fixture.py`,
using complete successful fixed-channel reads of current.json and its companion.
Public current.json SHA256:
eafdefbd729fe0d75dfe4ae6b5bfa9f1fbcba1d635a35f293c4305b5b54d39e3.
The snapshot ends at event 56337. Copied the publication's craft.json separately;
its complete HTTP 200 receipt matches all 1823 local bytes. Thus the original
failure is not caused by omitting that asset from the fixture.
craft.json SHA256:
7db7f5195cd8aadac6d62b4ddf2e34e747fc0459f04c404d7c003706af76cd91.

Native Accounts entry on the original leaves Loading visible after a one-second
wait, at both 390 and 1280 pixels. Candidate entry replaces it with “Claims
residents took on” and four results rows. Both runs have zero script errors,
unlabelled controls or page overflow. This is offline native rendering of
witnessed public data with a candidate script overlay, not live deployment.
Requests use run prefix `5c213f3207a54c10b9bd35b7db1ab3fa-` and suffixes
`r57-before-valid` and `r57-after`. An earlier six-second wait was rejected by
the viewer's input validator; it produced no browser evidence.

Cold keyboard entry into the Counting Room also loads results and focuses its
room card at both widths (`r57-room`). A panel-only inspection copy hides the
other Accounts blocks solely to bring these results within the viewer's phone
screenshot limit. Focus then Enter opens the “7 of 8 eligible claims finished”
disclosure and retains focus; its text, example buttons and focus ring fit the
phone and desktop (`r57-panel`). Opened both widths' screenshots, including
the second phone image containing the expanded results. Neither trial reports
errors, page overflow or unlabelled controls. Production layout is unchanged.

Replay by building a public fixture, copying its matching published craft.json,
then entering Accounts. For the candidate, replace only the fixture's house.js
with this source. Disposable fixtures and native screenshots are ignored; no
large evidence bundle is added to source.

## Source identity and next step

- site/house.js SHA256:
  a0211b5e64c686c7b5f99e38874bac3db84feb6db0fce8be6afbc00c99c0f4c0
- tests/test_craft_outcomes.py SHA256:
  3f296c6d2ea7034fd662d0b3a0a47f7e799b58199e20d537315fefcc8fa9932d

Independent review and integration remain, followed by delivered-byte and
Accounts-entry verification. R57 stays unchecked. This does not close R2–R6
or the source-inspection project's remaining milestone.
