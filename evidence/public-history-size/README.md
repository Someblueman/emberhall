# A growing house exceeded its publishing format

On 14 November 2026, a locked ordinary push of local Pages commit
`7ddeb8393425ef585fa57ec105311a709ff6fe85` was rejected by GitHub:

> remote: error: File history.json is 103.45 MB; this exceeds GitHub's file size limit of 100.00 MB
> remote: error: GH001: Large files detected.
> remote: pre-receive hook declined

The receipt named eleven oversized unpublished snapshots (100.16–103.45 MB).
Replacing only the latest file would still resend those ancestors. The old
publisher kept retrying; the last observed deployed page remained event 2150,
source cb04d444. This is a real delivery failure, not merely a forecast.

## Actual historical-data probe

`roundtrip.json` binds the rejected snapshot and exact bytes/hashes:
108,475,647 bytes became 2,335,273 bytes, retaining all 2,192 frames and every
projected field. Python compared the complete decoded object to the original.
Node executed the actual browser decoder and compared complete JSON hashes;
the actual catch-up reducer also agreed at four different historical moments.
This is execution of the client code, not an actual browser rollout witness.
No full private journal was published, and no event was truncated or sampled.

The 12 focused tests exercise malformed references, old public-format reading,
exact reconstruction, Parlor interaction and refresh, real local Git recovery,
rejected upload/retry, remote divergence refusal, size rejection before ref
mutation, and preservation of source/index/journal. `focused-tests.txt` is the
receipt. The real Git fixture uses a deliberately lower size threshold rather
than creating another 100 MB test blob; the actual GitHub failure above supplies
the external size-boundary observation.

The existing large site module was reviewed without unrelated restructuring.
The codec is a separate small module because the publisher and evidence checks
share its format. No dependency, credential, active rule or runtime pin changed.
The new publisher remains candidate source pending the protected activation gate.

Broader host acceptance passed448 tests in420.979 seconds:438 executed,10 skipped.
The full receipt is `full-tests.txt`; JavaScript syntax and Python compilation also
passed. Independent resident Aster finished review2212 with no scoped blocker, five
focused checks and a separate243-frame frozen-child alias probe; exact report
bytes are retained in `independent-review.md`. Keeper inspected the report and
matched all committed hashes against the reviewed candidate23d158c. No live runtime or Pages format migration
has been performed; do not infer deployment from this commit.
