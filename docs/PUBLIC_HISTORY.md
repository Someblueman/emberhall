# Public history without repeated snapshots

`house.body.export` remains the sole public projection. Its privacy filtering and
version-1 logical data are unchanged. Every event still has a frame; no sampling,
time cutoff, private journal payload, or inferred activity is introduced.

The Pages publisher writes a version-2 `history.json` transport:

- `nodes` is an ordered array of JSON containers (objects or arrays).
- Container children are primitive JSON values or exactly `{"ref": N}`.
- Each reference names an earlier node. Forward, cyclic, negative, fractional,
  boolean and extra-key references are rejected.
- `root` references the completed version-1 projection object.
- Equal containers are stored once. A literal object containing a `ref` property
  is itself a node, so it cannot be confused with a reference.

`house.public_history` encodes/decodes this format. The browser's
`decodePublicHistory` reconstructs shared containers before its existing history
validation and render path. Shared containers are read-only inputs; the current
renderer replaces each distinct frame's scar array when adding display details,
without mutating a shared scar, resident, task or room object. Future renderers
must preserve this property. This is a transport change, not a journal schema.

The reader also accepts existing version-1 public snapshots, so the new client
can ship before the pinned publisher changes. There is one writer format,
version 2. Old clients cannot read it and must reload to receive the new script;
an already-open old client retains its last snapshot and reports a load error.
A fresh page and historical scrubbing require browser verification after rollout.

## Publication and recovery

Every generated public blob is checked against a 64 MiB budget before refs change.
This deliberately leaves room below the observed GitHub 100 MiB rejection. It is
not a promise of unbounded history size: further growth must pass the budget or
receive another transport improvement without silently dropping old events.

Under the existing kernel publisher lock, the publisher verifies the remote
Pages head is an ancestor of its local head. Unknown or divergent remote history
fails closed. It examines **all unpublished objects**, not only the latest tree.
If an oversized blob would be resent, it saves the old local tip under
`refs/house-publication-recovery/<old-tip>` and builds the new complete snapshot
with the last remote head as its parent. The local Pages ref changes by compare
and swap. The push is an ordinary fast-forward; remote history is never forced
or rewritten. Rejected local commits remain reachable through the recovery ref.

The source index, source branch, journal and foundation refs are untouched.
A failed upload leaves a retryable local candidate. The exact same unchanged
candidate is retried instead of manufacturing a new commit. Recovery refs are
local evidence and are never included in the normal explicit Pages push.

## Deployment boundary

`house/publish.py` is protected in the currently pinned runtime. This source
repair does not install itself or grant a maintenance scope. Deployment needs
an approved scope covering publisher changes and the new codec, and a tested
runtime through the existing gate. The pending timeout cleanup changes also
remain unactivated; a combined runtime must explicitly account for them.

See `evidence/public-history-size/` for the actual rejection, complete real
snapshot roundtrip, focused Git tests and broader acceptance status.
