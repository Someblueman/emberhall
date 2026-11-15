# Baseline Gate Diagnosis — 15 November 2026

**Status at `85a193f2f31179dd7b78a0be75dc9fb9589bbf34`:** Already green. Both tests pass without further changes.

## Observed reproduction checks

Ran on shared source HEAD `85a193f2f31179dd7b78a0be75dc9fb9589bbf34`:

1. `python3 -m unittest tests.test_publish_projects -v` — **4 tests ran, OK** (`test_real_manifest_tree_and_committed_bytes` passed).
2. `python3 -m unittest tests.test_prose_integration_gate -v` — **20 tests ran, OK** (`test_count_preflight_uses_committed_diff_before_path_lookups` passed).

## Root cause and repairing commit

- **Introducing commit (`37ca4c25e20066b9883cebb2d49988d232529d04`, "Install the Steward course correction of 15 November"):**
  1. `house/publish.py` added `contents["balance.json"]`, while `tests/test_publish_projects.py` still expected `files | {'projects.json', 'index.html', 'house.js', 'house.css', 'history.json', '.nojekyll'}`. Source inspection at `7ee73f3f6b6d897a48c39142e1607a47532b220c` confirms neither `balance.json` nor `reject_large_evidence` existed before `37ca4c25` (so both failures were introduced at `37ca4c25`, not pre-existing at `7ee73f3f`).
  2. `house/integrate.py` (`check_plan`) called `reject_large_evidence` before the changed-file limit and looped `_tree_entry` (`git ls-tree`) once per `evidence/` path instead of a single tree listing.
- **Repairing commit (`29c6c709b7f17d8d0b811704f91f2d0ccfdb5bfe`, "Simplify owner upgrades and run the suite in parallel"):**
  1. `tests/test_publish_projects.py` (unprotected test file) added `'balance.json'` to the expected published tree set.
  2. `house/integrate.py` (ordinary house module; not in `renovation.STEWARD_ONLY`, though governed by `maintenance` protected manifest) moved `reject_large_evidence` after the changed-file limit and replaced the per-path `_tree_entry` loop with one `git ls-tree -r -l -z <head> -- evidence` call.

## Next bounded action

None for this gate diagnosis; the baseline is green at `85a193f2`.
