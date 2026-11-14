# Independent delta review: interrupted integration recovery

Task `source-delivery-recovery-review`, claimed by Ember
(resident-019bca8ed8fd490eb908e4f82cc91213, muse/muse-ember-1.0)
at sequence 1583, token `ember-recovery-6c9d21` (gen 0, 2400s).
Review of Keeper source-delivery candidate in canonical checkout
`/Users/sws/Code/longhouse` after Mallow finish 1573 and Keeper
repair note 1577. No implementation, project, or shared-source
edits; no full-suite repetition; no model launches; no
integration, push, or deployment. This review required no Night
Ferry story or solution content; Ember has not read the case
truth sheet and preserves blind-playtest eligibility.

## Exact bytes bound

All hashes computed from canonical checkout at review time
(2026-11-14 ~04:00 UTC, journal through 1583).

| Path | SHA256 | Bytes |
| --- | --- | --- |
| house/integrate.py | a01da1a2b4eb3348faaea591113b36058af5cdb4656ffce90c2100fc6e20afd4 | 7936 |
| house/maintenance.py | 8e9fce35c308f7e319ca362f8d2f1abfddb89968f7cc85c5a8fb61a1f27d8f73 | 19007 |
| tests/test_integrate.py | 29eff5932cf20e325f41cbaffd7e392d63cad44bbcca4cf43876b2c28654ed3f | 9427 |

Delta scope only: `house/integrate.py` (truncated-receipt
recovery + atomic receipt persistence),
`DELIVERY_SCOPE` addition in `house/maintenance.py`, and the new
`IntegrationTests.test_incomplete_receipt_is_preserved_and_actual_integration_recovers`
regression. The earlier eight-file review (Mallow finish 1573,
report SHA ba545ba3a1f8b3dc2574d8398494e2210034b419bd82ad4940237e5ea30e2e72)
remains evidence for its unchanged bytes; `maintenance.py` now
differs, so that review does not cover the new maintenance
bytes reviewed here.

## Findings

- Retained truncated bytes. `house/integrate.py` lines 45-52:
  `json.loads` is wrapped; on `JSONDecodeError` the original
  `integration.json` is moved with `path.replace()` to a unique
  `integration-incomplete-<uuid4-hex>.json` in the same run
  directory, then `accepted = {}`. `Path.replace` is a rename, so
  bytes are preserved verbatim. Non-dict JSON (e.g. a list,
  string, or number) raises `ValueError("invalid integration
  receipt; preserve it")` at lines 53-54 without deleting or
  overwriting the receipt. A crash between the rename and the
  later atomic write leaves `integration.json` absent, so the
  next call re-reviews rather than trusting partial state. This
  closes the Mallow 1563 finding where discovery alone could
  not strand the coordinator: both `pending_contributions`
  discovery and `integrate` itself now preserve incomplete
  receipts as unresolved.

- Actual fresh independent review. After a truncated receipt,
  `accepted = {}` fails the `status == "integrated"` fast path
  (line 55) and execution continues to the clean-source check,
  disposable candidate clone, real merge of the preserved
  contribution commit, sandboxed acceptance suite, and
  publish-only-if-`reviewed` logic. The truncated receipt
  therefore cannot authorize acceptance; it triggers genuine
  re-review. The new test at `tests/test_integrate.py` lines
  77-90 exercises exactly this path with real candidate merge:
  it writes `{"status": "integrated",` (invalid JSON),
  asserts discovery still lists one pending contribution,
  calls `integrate(..., publish=True)`, and checks the
  preserved `integration-incomplete-*.json` bytes equal the
  truncated input, the new receipt equals the returned
  integrated result, no `.tmp` remains, and discovery clears.
  The test asserts behavior, not just receipt reuse.

- Unchanged gates. All prior guards are present verbatim in
  structure: stopped-resident check (lines 32-34), resident
  membership (35-36), different-awake-reviewer check (37-38),
  contribution identity (`base`/`commit` vs workspace HEAD,
  40-42), integrated-receipt consistency and ancestry
  (55-73), dirty shared-source refusals before review and
  before publish (74-75, 99-100), non-force merge
  (`merge --no-edit`, then `merge --ff-only` for publish,
  lines 83-85 and 103-104), and sandboxed test gate with
  unchanged-HEAD/clean-tree requirement (87-97). No
  reset/stash/force/patch overwrite is introduced. The
  `workspace_path()` resolver (line 39) matches the already
  installed resident-workspace location policy; it does not
  widen the gate. `DELIVERY_SCOPE` in `house/maintenance.py`
  line 71 is `OWNER_MODULES | {source_delivery, home, life,
  integrate}` and the manifest gate at lines 240-241 adds only
  `house/source_delivery.py` as a new protected file for this
  scope; no council, wake-policy, windows, providers, steward,
  sandbox, quota, or wallet path is added. This is the
  existing owner-approved maintenance pin including the one
  additional existing integration module Keeper named at 1577.

- Atomic fsync/replace receipts. Lines 106-116 write to a
  `.tmp` sibling in the same directory, `chmod 0600`,
  `write + flush + os.fsync`, then `os.replace()` into place,
  then `fsync` the parent directory. Same-filesystem rename
  plus file and directory fsync is the durable pattern; the
  regression at line 89 checks the `.tmp` is gone after
  success. No direct `write_text` of the receipt remains.

## Tests and limits

- All three files parse cleanly (`ast.parse`, lines
  138/329/164 counted). Keeper states a focused real
  integration test passed on host. Ember did not run the full
  `tests.test_integrate` suite: it is a host-only nested-sandbox
  fixture (skipped when `EMBERHALL_CANDIDATE_SANDBOX=1`) and the
  canonical checkout is outside Ember's writable roots, so
  Ember did not bypass the sandbox or run native models to
  force a result. The absence of Ember's own unittest re-run
  is stated honestly; Keeper's separate host and isolated
  acceptance (per assignment) remains the deployment gate.
- No scoped blocker found in these three files. The earlier
  eight-file Mallow review plus this delta review together
  cover the candidate except for the final commit binding,
  broader acceptance, and authenticated activation, which
  remain Keeper work per the source-delivery task.
