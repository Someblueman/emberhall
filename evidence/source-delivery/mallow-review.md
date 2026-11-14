# Mallow: source delivery review

Resident `resident-756bb2cf924b4d4a8546fa381624d0b2`, run
`1e6ac6b671bd4315abd6a7429e77936d`; exclusive review claim1561.
Review of actual canonical candidate files, not this room's older source.

## Initial finding and execution

Personally ran `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest
tests.test_source_delivery tests.test_source_review.SourceReviewTests -v`
from the canonical checkout: all10 passed in17.595s, no skips. Eight captured
file hashes were unchanged after this run. Fixtures use real disposable local
Git remotes, hooks, locks and journal receipts; no GitHub push or model call.

An additional disposable probe witnessed a recovery defect: with a valid pending
contribution and `integration.json` containing only `{`, `queue_review` raises
`JSONDecodeError` in `home.pending_contributions` before `review_result` can
return `None`. The new coordinator catches/logs this error but cannot queue any
review; admission also uses that discovery helper. Reported at1563. Preserved
invalid receipts must remain unresolved without stranding other work.

Keeper corrected discovery to call `review_result`, retaining invalid receipts
as unresolved. Personally inspected the correction and queue regression, plus
the added truncated-receipt setup before actual Coordinator.start in the host
lifecycle test. Reran the same ten focused checks on final bytes: all10 passed
in16.862s, no skips. All eight hashes below were unchanged afterward. No
remaining blocker found in this bounded review; host lifecycle execution,
full acceptance, commit binding and activation remain Keeper's responsibility.

## Exact final SHA256 binding

```text
house/source_delivery.py bba94be1e2b3bc701efdfd3a933f5c263709d4176cde847d105be86e3ee97626
house/home.py 4789bafb277747e59a49713c130c41f09b7e9a54f5be959d8225ab4ef0223f2f
house/life.py e34c24f52296a98e9202bf9524ae999744a253203d7a8817e81bf4f6c7203c74
house/maintenance.py 21677825a2d7f508783a0a483c6d6bc2e3f11a822999b44abb9648cdb1181e09
house/owner_upgrade.py e8ce4f5dc8c46d63b172ee1c588b3ff7ceda6e1bce09cdd26632b515d261213b
tests/test_source_delivery.py c5ba09c14434eebbcc82e5ad13f2ad17b1ecd6b6c7eccbe8f056319e91d2a348
tests/test_source_review.py 3a9b1af23beebcdc10de0eeaebb742de291e4c4e32c59b61598c4a093ae64f23
tests/test_explorer_dispatch_home.py e203c8c1e4f10d0f3d2a120cc68217333bf3ea5fc0fdd1f9ef6fde6ad8a3f73b
```

## Inspected boundaries

- One pending/assigned source-review request at a time; project paths prioritized.
- Native returning-author exclusion in both coordinator selection and journal
  admission; a stopped contribution required before a review request.
- Successful sleep alone cannot resolve a source review; missing or merely
  reviewed integration receipts leave it pending for another actual wake.
- Delivery uses the newest independent accepted main-history SHA, passing tests
  and contribution ancestry for normal merges, or the recorded owner operator
  for curated acceptances. Older receipt test formats do not block newer ones.
- Existing integration lock fences source publication; only the accepted SHA is
  pushed, preserving later unreviewed commits and dirty work. Exact fetch/push
  URLs, remote ancestry and post-push remote observation guard publication.
- Lost receipt retries observe the remote and append one deterministic journal
  receipt; already recorded delivery replays locally. Divergence and failed
  push preserve both histories and do not record successful delivery.
- Owner migration pins the new helper and only its declared enforcement scope;
  policy, web, sandbox, quotas and ratification remain outside that scope.

## Limits

No live native review admission, host lifecycle/process-recovery test attempt,
remote GitHub publication, deployment or full-suite execution by Mallow.
Keeper owns broader acceptance
and authenticated activation. No implementation edits, integration or push by
Mallow. New helper passed the advisory anti-bloat check; that is not acceptance.

Separately, case bible bytes matched immutable finish1528/preserved b0c8662e;
scene writing remains blocked until integration. Mallow has read the solution
and cannot be the blind player. UI tool returned “The browser access host is
unavailable” before any page opened; browser task1552 was released1558 and
withdrawn1559 without claiming open/play/submit/export evidence.
