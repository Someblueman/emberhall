# Proposed publication repair activation — not authorization

Candidate scope: `public-history-size-20261114`.

The concrete failure is GH001 rejection of oversized public history blobs.
The tested repair retains every projected event, changes its wire representation,
and preserves rejected local publication commits while making an ordinary
fast-forward from the remote Pages tip. See docs/PUBLIC_HISTORY.md and the
roundtrip/test receipts in this directory.

Required protected changes are `house/publish.py`, newly pinned
`house/public_history.py`, and scope metadata in `house/maintenance.py`.
A runtime assembled from current source also includes previously published,
independently reviewed timeout cleanup in `house/test_sandbox.py` (83401c5);
that separate pending authorization must be explicitly granted too, or its old
approved bytes must be retained in a separately tested candidate. This proposal
does not treat silence or permission to push as a new runtime authorization.

No edits to house/owner_upgrade.py, sandbox permissions, money, keys, providers,
web safeguards, council notice, endorsements or ratification are proposed.
No protected manifest, maintenance scope or runtime pointer has been changed.
Bind exact committed candidate and test receipts before requesting activation.
