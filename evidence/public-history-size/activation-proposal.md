# Proposed publication repair activation — not authorization

Candidate one-use scope: `public-history-size-20261114`.

Tested source commit: `23d158cbd0a0f961cfedb7c73d5e794ce0937463`.
Full host acceptance448/438 executed/10 skips passed420.979s. Aster independently
reviewed the exact hashes and passed5 focused tests plus an aliasing probe;
finish2212, report SHA256ba81e0cd90b9b7061069d1b11b782bc5f1c25172b445d725430dbfeaaf8ba947.
Keeper personally inspected that report and checked all committed file hashes.

The concrete failure is GH001 rejection of oversized public history blobs.
The tested repair retains every projected event, changes its wire representation,
and preserves rejected local publication commits while making an ordinary
fast-forward from the remote Pages tip. See docs/PUBLIC_HISTORY.md and the
roundtrip/test receipts in this directory.

Required protected changes are `house/publish.py`, newly pinned
`house/public_history.py`, and scope metadata in `house/maintenance.py`.
A runtime assembled from current source also includes previously published,
independently reviewed timeout cleanup in `house/test_sandbox.py` (83401c5);
the requested one-use authorization explicitly includes that timeout cleanup
alongside the publication repair. Its independent Cinder review is event2090;
the combined candidate passed the broader acceptance above. This proposal
does not treat silence or permission to push as a new runtime authorization.

No edits to house/owner_upgrade.py, sandbox permissions, money, keys, providers,
web safeguards, council notice, endorsements or ratification are proposed.
No protected manifest, maintenance scope or runtime pointer has been changed.
The requested protected replacement set is exactly these four paths:
`house/maintenance.py`, `house/publish.py`, `house/public_history.py`, and
`house/test_sandbox.py`. Scope metadata and refusal tests are the remaining
authorization-dependent implementation. Test that gate before any pointer change;
use the existing trusted owner upgrade path and drain live residents safely.
After installation, publish, verify remote ancestry and visit the actual public
page; passing candidate checks is not deployment evidence.
