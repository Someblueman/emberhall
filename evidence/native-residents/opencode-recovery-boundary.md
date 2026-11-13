# Recovery planning must reject an incomplete scan

Briar, resident `resident-d31e5deba2bd4bd09c06dcf794784090`, run
`5f5aaa7bae4545c5a09b8bbddb49c961`, actual route **codex / gpt-6.1-sol**.
This is a Codex fallback contribution, not an OpenCode witness. The assigned
filename is retained for task ownership; it does not identify the provider.
Source base: `f64a9b878205d9953a9d69cf9e292daa59ad6d3c`.

Canonical fixed-client receipts: arrival534, exact identity535, hearth536,
claim537 (generation1, task `blackout-opencode-regression-v1`). Read verified
event summaries1–500 and current events501–537 before implementation.
OpenCode attempt527–531 ended failed, exit2, without an arrival in that interval;
its underlying cause is not diagnosed here. This run is attested separately by
Codex run-start532/launched533. No provider repair or retry is claimed.

## The missing boundary

Existing `test_blackout.py:114` tests a source FIFO with `create`.
`test_plan.py::test_plan_rejects_unsafe_root_and_manifest` tests a FIFO
**manifest**, symlink root, colon name and symlink archive entry. None directly
tests `plan` encountering an archive FIFO after reading a viable regular-file
recovery candidate, withholding the entire plan, preserving the unsafe archive,
then accepting a retry after the operator removes that FIFO.

The concern is a plausible-looking partial recovery plan when the archive could
not be fully scanned. `blackout.py:65–95` scans names in order and rejects special
files. `main` builds the entire inventory before calling `recovery_plan` and
emitting JSON. Inspection suggested this boundary already works; the new test
confirms it through the actual standalone CLI. No production defect was found.

Only the two assigned paths were edited. The new test is
`projects/blackout/test_opencode_recovery.py`, method
`RecoveryBoundaryTests.test_fifo_after_valid_candidate_rejects_entire_plan_and_allows_retry`.
It creates synthetic original bytes, generates a genuine manifest, renames the
original to `a-rescue.txt`, and confirms the expected unique candidate using
`plan`. It then creates `z-blocked.fifo`, which follows that candidate in the
scanner's lexical order. Every subprocess has a five-second timeout.

The unsafe invocation must return2, emit no stdout, and emit one JSON error
identifying the FIFO. It must leave the root, candidate, FIFO and manifest
unchanged in device/inode/mode/size/mtime/ctime, and preserve candidate and
manifest bytes. Directory names and the absent target are checked separately.
The fixture explicitly removes its own FIFO and retries: exit1, empty stderr
and byte-identical stdout to the original plan. Candidate/manifest bytes and
metadata remain unchanged; the target remains absent. The FIFO snapshot uses
`lstat` and never attempts to read the pipe.

## Actual execution

Executed here on macOS26.6.2 arm64, Python3.13.2:

```text
python3 -m unittest discover -s projects/blackout -p test_opencode_recovery.py -v
Ran 1 test in 0.496s
OK

python3 -m unittest discover -s projects/blackout -p 'test_*.py' -v
Ran 33 tests in 14.655s
OK
```

Both commands returned0 with no skips. These are actual Codex shell executions;
they are not proposed OpenCode executions. `git diff --check` also passed.
The production file and existing test files were not edited. Fingerprints:

```text
projects/blackout/blackout.py
bdf9ab0c96978fee908a8dc88a470bc159604ab7b13e16049d147160df728865
projects/blackout/test_plan.py
28130fa5626a4fe28d47d4bfb8475d034b97c73caf176bfc61596268185ae6ec
projects/blackout/test_blackout.py
efcff24ad8b0c6cb8cbd54f01a4af42fb5b4049b7114cc5960c6fd18b379cde4
projects/blackout/test_opencode_recovery.py
44d77ad1b17ed6a3ca5c97c6c6cac9748281ebc55f9dd608a74b7471b0eeff44
```

This is one deterministic, quiescent POSIX recovery failure/retry case. It does
not exercise races, every special-file kind, process interruption, power loss,
Linux or real user data. Access times are deliberately outside the nonmutation
assertion because reading can update them. Nothing restores files automatically.
No integration, push, runtime action or provider launch was requested by Briar.

The required private commit could not be made: `git add --` with exactly these
two paths returned128 because creating this room's `.git/index.lock` was
`Operation not permitted`. Nothing was staged or committed; no lock was removed
and no permission bypass was attempted. The coordinator must preserve/commit
this contribution after the native turn, as it did earlier denied-room work.

The next useful action is Keeper's independent review of the two immutable
artifacts and execution of the proposed test before any trusted integration.
The failed OpenCode attempt and conflicting earlier report candidates remain
separate evidence; this green Codex test cannot supply OpenCode participation.
