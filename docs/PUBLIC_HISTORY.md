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
can ship before the pinned publisher changes. A fresh page and historical
scrubbing require browser verification after rollout.

## Version 3: the history in parts

The node table is a long persistent prefix that only grows by appending, plus a short
rebuilt tail. Version 3 cuts the prefix into **sealed parts** so no single file nears
GitHub's 100 MiB limit. There is one writer format, version 3; readers still accept 2.

- `history/part-NNNN-<16 hex>.json` is a JSON array of consecutive nodes, closed once
  its serialised size reaches `PART_TARGET` (8 MiB). Compact separators, no NaN, so
  the bytes are reproducible. The name holds the position and the first 16 hex digits
  of the content's SHA-256, so a part can be cached for ever.
- `history.json` is `{"version": 3, "parts": [{"path", "nodes", "sha256"}, ...],
  "root", "nodes"}`. Node references keep their global indexes: the table is the
  parts' nodes in order, then the file's own `nodes` (the unsealed rest and the tail).
- The private cache records where each part ends and its name and hash, so later
  publications re-emit old parts unchanged and only add parts at the end. Part bytes are
  also kept in `.git/house-home/history-parts/` (mode 0600) and rebuilt from the cache
  if lost. A cache without boundaries gets them computed once, without a replay. A
  rebuilt cache (changed code) may cut different parts; unreferenced parts leave the tree.
- `head.json` carries `"history_version": 3`; a previous publication without it is
  republished. The "did anything change" check reads head.json, never the parts.
- `decode(wire, parts)` takes a path-to-bytes mapping or a callable for version 3 and
  checks each part's hash and node count. The page keeps fetched parts in memory by
  path, fetches only new ones (three at a time, 60 s each, normal browser caching),
  checks their node counts and decodes as before. A failed part shows the usual
  "Try again" notice; a retry reuses the parts already held.

Old clients cannot read version 3 and must reload to receive the new script; an
already-open old client retains its last snapshot and reports a load error.

## Publication and recovery

Every generated public blob (each part included) is checked against a 64 MiB budget
before refs change. This leaves room below the observed GitHub 100 MiB rejection;
with parts of about 8 MiB the history itself no longer approaches it. Total size
still grows, and the repository and each visitor's first load grow with it.

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
