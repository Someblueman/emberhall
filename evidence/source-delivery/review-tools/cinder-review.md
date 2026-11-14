# Source review tools — independent Muse review

**Reviewer:** Cinder (resident-8ce5efdfe3004ff78be973499d85d26c, muse/muse-ember-1.0, run fad7af35aa484248ac99027eef484581)
**Task:** review-source-review-tools (gen 0 claimed as seq 1699, token cinder-review-1794630031-fad7af35)
**Source head at review:** `2287e93e0706dcf702f55bbcfd1d77c21fe3ac78` — canonical dirty `source-review-tools` work per keeper-01 1683/1689
**Date:** 14 Nov 2026

## Exact canonical hashes (SHA256, `sha256sum` of dirty candidate)

| Path | SHA256 |
|---|---|
| `house/integrate.py` | `cdd54ec8488196035ff5386d3e451e5f830c1f1ffaebbcb5b75c219aff06cbde` |
| `house/resident_actions.py` | `74e55a0128416e5c9a2485d48586e0955dcc589c12425ac7a075152f296864d7` |
| `house/source_delivery.py` | `5142629c63049dc1553ceee16b9e76387b3731c638ea656a37f0f8d554790ddd` |
| `house/home.py` | `70e46b646361429dd1020704ca59472479a18bda56f87426cc411126e536b622` |
| `house/maintenance.py` | `1b68d247be380ed56e4861aa764d2d0d92f02ced9b3ae0a4a16c6320e021e8f4` |
| `tests/test_source_inspection.py` | `0c308f3fc8c4d17d3e791b0236b842c4bd828ccbb2fd97cf12297e1010aa7d79` |
| `tests/test_source_review.py` | `a7c2176ef7b4a2e1d8b3e27dd092000aedd452c1edf8d72c63ba6b87af22f8d6` |

All 7 files read via permitted native `read_file` on absolute canonical `/Users/sws/Code/longhouse/...` (sandbox readable, writes only to this private room). No arbitrary host reads; no source edits; no integration of dirty source; no old full native preflight.

## What was checked

**Bounded committed-byte inspection — `inspect_contribution`:**
- Requires stopped completed run, awake distinct resident, `base==item[source_head]` and `commit==HEAD` of workspace via `workspace_path` (fixed-path/no-symlink). Identity change fails closed.
- `changed_paths` uses `git --literal-pathspecs diff --name-only -z --no-ext-diff --no-textconv --no-renames base commit` on the run workspace only. Caller-supplied `path` must equal an element of that literal list or raise `inspection path must be an exact changed contribution path`. This blocks `../document.txt`, `/etc/passwd`, `:(glob)*` (verified by test).
- Diff streamed via `Popen`, reading `INSPECTION_LIMIT+1` (64000); `truncated = len>limit` then `terminate`. No full buffering. Either whole diff ≤64k or a bounded prefix with `truncated:true`.
- Per-file content via `ls-tree -z` + `cat-file blob` on the exact commit (not working tree). Deleted → `content_status:"deleted"`; non-`100644/100755` or non-blob → `not-regular-file`; size >64k → `too-large`; non-UTF8 or NUL → `binary`; otherwise `complete` with content. No `integrate --publish` side effects, no lock/receipt mutation, no tests run.
- Verified by `test_inspection_reads_exact_committed_diff_without_receipt_or_lock_mutation` (holds `integration.lock` exclusively, inspection still returns without touching receipt/head/uncommitted decoy) and `test_large_binary_symlink_and_deleted_content_are_explicit`.

**Explicit rejection persistence, no self-review, no erase-acceptance:**
- `source()` enforces `actor != author` and `awake`, `status=="completed"`. `integrate --reject` requires non-empty stripped reason ≤4000 and `not publish`, returns before dirty-source check, writes `status:"rejected"` via atomic `save_result`.
- Existing `integrated` receipt replays after anchor/ancestry validation; `rejected` receipt replays against same run/commit without re-tests. Later `integrate --publish --reject` against either returns original bytes without modifying journal/HEAD. `test_rejection_is_terminal_preserves_source_and_skips_queue` + `test_project_tests_gate...` demonstrate.
- `home.pending_contributions` now skips `{integrated, rejected}`; `source_delivery.review_result` now includes `rejected` so `queue_review` does not re-queue terminal refusals and `Coordinator.finish` resolves the help when `review_result` is present. Preserves source; dirty work preserved.

**Project checks from actual merged Git paths:**
- `check_plan(candidate, base, head)` derives `paths = changed_paths(candidate, base, head)` from the candidate merge commit, not from report `paths`. `project_only = bool(paths) and all(...projects/name/...)` → per-project `discover -s project -v` + per-file `ast`/`json`/`node --check` with symlink rejection. Non-project-only → single foundation command `unittest discover -s tests -v` (full suite).
- `test_actual_git_paths_select_checks_even_if_report_lies` mutates `report["paths"]` to lie; `check_plan` still follows Git (foundation vs projects) while `inspect_contribution["paths"]` still reports the true diff. Good.
- `test_project_failure_does_not_publish` + `test_project_tests_gate...` verify real `publish` merges use this plan and that `reject` cannot erase an `integrated` receipt.

**Unchanged sandbox/authority:**
- `house/maintenance.py` adds `REVIEW_TOOLS_SCOPE = source-review-tools-20261114` with narrow `OWNER_MODULES | {house/integrate.py, house/resident_actions.py, house/source_delivery.py, house/home.py}`. `providers.py`, `windows.py`, `test_sandbox.py`, `council.py` are **not** in scope; `test_review_tool_migration_preserves_policy_and_cannot_widen_permissions` proves a bad manifest touching those raises `outside.*scope` while the good migration preserves all non-maintenance keys.
- `tests/test_source_review.py` owner-migration tests, atomic stopped-source + returning-author rejection, queue prioritization, and partial-receipt `review_result` `None` all pass on canonical. No provider/web/governance or native-permission change in diff.

## Proportionate tests (inside Muse sandbox, `PYTHONDONTWRITEBYTECODE=1 python3 -B`)

- `tests.test_source_review.SourceReviewTests` (4/4 OK):
  - `test_activation_preserves_all_policy_and_requires_owner_and_exact_pins` — OK
  - `test_queue_prioritizes_product_one_at_a_time_and_preserves_failed_reviews` — OK
  - `test_review_requires_stopped_source_and_rejects_returning_author_atomically` — OK
  - `test_review_tool_migration_preserves_policy_and_cannot_widen_permissions` — OK
- `tests.test_source_inspection` with `EMBERHALL_CANDIDATE_SANDBOX=1` (5 OK, 2 skipped due to nested sandbox):
  - `test_inspection_reads_exact_committed_diff...` — OK
  - `test_large_binary_symlink_and_deleted_content...` — OK
  - `test_rejection_is_terminal...` — OK
  - `test_actual_git_paths_select_checks...` — OK
  - `test_native_fixed_parser_keeps_modes_exclusive` — OK
  - `test_project_tests_gate...`, `test_project_failure...` — skipped `cannot nest macOS sandboxes`
- `EMBERHALL_CANDIDATE_SANDBOX=1 tests.test_source_review` (4 OK, 1 skipped `inert native fixture requires host process observation`) — lifecycle test skipped for same nesting reason.
- Un-skipped run (`tests.test_source_inspection` without `EMBERHALL_CANDIDATE_SANDBOX`) produced 6 OK + 1 `tests-failed` on `test_project_tests_gate...` — expected nested-sandbox failure (`sandbox-exec` inside Muse sandbox). Host evidence `evidence/source-delivery/review-tools/focused-tests.txt` (11 passed host) and `host-tests.txt` (430 passed, 420 executed,10 skipped, 407.790s) show the same suite green on host without nesting; the failure is a sandbox-nesting limit, not a source defect. Not claimed as pass beyond the 9 executed above.

**Live channel:** pinned runtime at `2287e93e` (`show help` for `integrate` lists only `--publish`/`--as`/`--request`) does not yet expose `--inspect/--reject/--path` until `source-review-tools-20261114` is owner-activated. Verification here is direct `house.integrate` unit tests against the candidate, not a live `--inspect` via the fixed channel — honestly noted.

## Concrete findings / limits

No blocking defect in the scoped boundary. Bounded acceptance for the intended contract subject to:

- **Edge:** `check_plan` filtering `if (candidate / project).is_dir()` can yield an empty `test_commands` list when a whole tested project directory disappears (or when no discovered command remains). `integrate` would then record `test_scope:"projects:..."` with zero commands run and `test_exit 0` → `reviewed`. In practice a new project addition always leaves its directory, and deleted-file-only cases still skip syntax checks (documented `Deleted files have no syntax`), but a future project that deletes its directory entirely would be accepted without any executed test. Recommend requiring at least one command or falling back to foundation when the filtered list is empty.
- **Edge:** symlink in project-only change raises `ValueError("project acceptance requires regular files")` out of `check_plan`/`integrate` (exit 2 retained for review) rather than recording a `tests-failed` receipt. That is fail-closed and the reviewer can `--reject` explicitly, but the behavior differs from a failed test receipt.
- **Remaining observed limitation (declared in `evidence/source-delivery/review-tools/README.md`):** timeout descendant cleanup is not fixed by this scope. No other scope change impacts that.
- Nothing else in scope was widened: `integrate` still fast-forwards only when `status=="reviewed"` + unchanged candidate + shared source still clean; publication still requires the separate coordinator push, not local integrate.

## Verdict

**Bounded acceptance:** the new `--inspect`/`--reject` and project-scoped acceptance correctly implement read-only bounded committed-byte inspection with literal paths and 64k limits, terminal rejection preserving source, no self-review or receipt erasure, and actual-Git-path checks with full-suite fallback, without widening sandbox/authority. Test evidence above plus host 430/420 passes supports it. No blocking defect; the two noted edges are retained for Keeper to consider before owner activation.
