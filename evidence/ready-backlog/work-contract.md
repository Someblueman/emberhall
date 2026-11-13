# Useful concurrent work: compare offline backup inventories

This is the real work for the ready-backlog residency witness, not a synthetic
model prompt or an occupancy exercise. Blackout Kit can scan and verify archives,
but cannot expose its existing manifest comparison through the CLI when neither
archive is mounted. Comparing two saved inventories helps a person understand
what changed between backup dates without needing either storage device.

## Frozen interface

Add `python3 projects/blackout/blackout.py diff OLD_MANIFEST NEW_MANIFEST`.
Both inputs use the existing strict version1 manifest loader. No archive root is
read or inferred from manifest paths. Neither input nor any named archive file
may change. Use the existing `compare` semantics and emitter, not another schema:

- `ok`: true only when both inventories describe identical entries.
- `missing`: paths in OLD but absent from NEW, sorted.
- `extra`: paths in NEW but absent from OLD, sorted.
- `changed`: shared paths whose byte length or SHA256 differs, sorted.
- `matched`: count of identical entries at identical paths.
- Exit0 for identical inventories,1 for differences,2 for invalid/unsafe input or
  output failure,130 for a handled interrupt, as the existing CLI does.

Path spelling remains exact, including case and Unicode normalization. Record
order is irrelevant. A diff compares recorded claims; it does not verify today's
archive bytes or infer renames. Existing create/verify/plan behavior stays intact.
No new dependencies, downloads, personal archives, house imports or credentials.

## Exclusive ownership

Three ready tasks have independent scopes. Each native resident claims exactly
one initially, with the current generation and fresh token; losers reread and
choose another available scope. A launch is not a claim.

1. Implementation owns only `projects/blackout/blackout.py`. Reuse the existing
   loader/comparator/emitter; keep the change small. Run existing product tests
   and direct new CLI examples, preserving both manifests. Finish the exact file
   with a concise result naming checks, limitations and its canonical receipt.
2. Independent acceptance owns only new `projects/blackout/test_manifest_diff.py`.
   Write real CLI tests against this contract, including order-independent equality,
   directional missing/extra, size/hash changes, exact path spelling, invalid input
   on either side, input immutability and failed output. Do not mirror internals.
3. Documentation owns only `projects/blackout/README.md` and `QUICKSTART.md`.
   Explain direction, exit statuses and inventory-versus-live-byte semantics. Add
   one safe, executable invented-data recipe showing both equality and differences.
   The existing ZIP already includes these docs and blackout.py; do not change its
   allowlist or add an unrelated package surface.

The test and documentation residents can draft independently while implementation
proceeds. To execute the new CLI, read the implementation's immutable finish
receipt and extract its artifact into a new private temporary fixture directory;
verify its hash and inspect the code before executing it in the existing native
sandbox. Never modify or commit the other resident's assigned path.
The artifact is source for testing, never a replacement house/runtime. Use only
the existing sandbox's permitted filesystem. If transport or permissions prevent
that validation, preserve the exact limitation rather than bypassing it.

Each resident finishes only its own artifacts. Keep output concise and evidence
in the finish result rather than creating report-on-report files. After a completed
stretch, read latest, sleep with a useful handoff and exit normally so the coordinator
preserves the private commit. The coordinator maintains continuous presence.
Keeper independently reviews all changes, runs the integrated product suite and
an extracted-kit recipe, then accepts/publishes task-owned files. No one accepts
their own contribution merely by returning with another name. Do not claim success
before actual commands pass or call three inert test processes native residents.
