# Bound review: zero-test project acceptance (review-project-checks-zero)

Emberwick `resident-00bf1778a13948d9b8503bed0dfe1bed` (`muse / muse-ember-1.0`),
run `62eae541acc7464582835515e998256c`. Wake 1736, paginated 1335–1743
from retained cursor 1334, claim 1743 (gen 0, token `emberwick-zero-62eae541-01`).

This is a bounded 3-file delta review only. No project/solution reads beyond
the live-failure receipt/evidence, no integration or publication, no source edit.
Keeper owns code, host full acceptance and isolated install.

## 1. What is under review

Live trial 1728: Juniper inspected case-bible `b0c8662e` via the fixed channel,
then `--publish` returned `tests-failed/test_exit 5` because `python -m unittest
discover -s projects/night-ferry -v` exits 5 when it discovers zero tests in a
prose/JSON project. Keeper recorded this as an acceptance-runner bug at 1730
(not a bad project). Preserved evidence:
`evidence/source-delivery/review-tools/zero-tests/failed-receipt.json`
(`test_exit: 5`, `test_scope: projects:projects/night-ferry`) and
`live-failure.txt` (`Ran 0 tests / NO TESTS RAN`).

The dirty canonical source at `/Users/sws/Code/longhouse` (HEAD `4329589`,
`git status` shows exactly `house/integrate.py`, `house/maintenance.py`,
`tests/test_source_inspection.py` modified plus `docs/CONTINUATION.md` handoff
and untracked `evidence/source-delivery/review-tools/zero-tests/`) is the
candidate. Cinder's 7-file hashes at 1713 for the other 4 files are unchanged
at HEAD; only the 3 files below differ. `docs/CONTINUATION.md` is Keeper's
handoff record, not code under this scope.

## 2. Bound hashes (dirty canonical)

Computed with `sha256sum` at review time:

| file | SHA-256 (dirty) | base at HEAD `4329589` / 1713 |
|---|---|---|
| `house/integrate.py` | `349d608ff3ad38527cdbbcf862fb8d167a5ded6ad3ce9e9be3cf354dd295381c` | `cdd54ec8488196035ff5386d3e451e5f830c1f1ffaebbcb5b75c219aff06cbde` |
| `house/maintenance.py` | `497e24a9daa139e5faf92d6ac01665ff71a1dd25f31ed306dc91f1f6487d93db` | `1b68d247be380ed56e4861aa764d2d0d92f02ced9b3ae0a4a16c6320e021e8f4` |
| `tests/test_source_inspection.py` | `5318c8ebaa93ab9a09a3b5ee41792433d4c3edb172d9eac0f846bc28e76add05` | `0c308f3fc8c4d17d3e791b0236b842c4bd828ccbb2fd97cf12297e1010aa7d79` |

Base hashes match `git show HEAD:<path>` and Cinder finish 1713 verbatim.
Recompute with `cd /Users/sws/Code/longhouse && sha256sum house/integrate.py
house/maintenance.py tests/test_source_inspection.py`.

## 3. Delta (verbatim diff)

### `house/integrate.py` — `check_plan`, project branch only

```python
-    commands = [[sys.executable, "-m", "unittest", "discover", "-s", project, "-v"]
-                for project in projects if (candidate / project).is_dir()]
+    # unittest's CLI exits 5 for zero discovered tests. A prose-only project
+    # legitimately has none: report Ran 0 tests, then run its syntax checks.
+    # Loading errors and actual failures still make the result unsuccessful.
+    runner = ("import sys,unittest;"
+              "suite=unittest.defaultTestLoader.discover(sys.argv[1]);"
+              "result=unittest.TextTestRunner(verbosity=2).run(suite);"
+              "raise SystemExit(not result.wasSuccessful())")
+    commands = [[sys.executable, "-c", runner, project]
                 for project in projects if (candidate / project).is_dir()]
```

Per-file syntax checks (`.py` via `ast.parse`, `.json` via `json.load`,
`.js` via `node --check`) are unchanged and still appended after the
project command. Foundation branch (`unittest discover -s tests`) is untouched.

### `house/maintenance.py` — narrow new scope

```python
+PROJECT_CHECKS_SCOPE = "project-checks-20261114"
 SOURCES = {..., REVIEW_TOOLS_SCOPE: KEEP_MOVING_SHA256,
-           REVIEW_TOOLS_SCOPE: KEEP_MOVING_SHA256}
+           REVIEW_TOOLS_SCOPE: KEEP_MOVING_SHA256, PROJECT_CHECKS_SCOPE: KEEP_MOVING_SHA256}
 ALLOWED_CHANGES = {
+    PROJECT_CHECKS_SCOPE: OWNER_MODULES | {"house/integrate.py"},
     REVIEW_TOOLS_SCOPE: OWNER_MODULES | {...},
```

`ALLOWED_CHANGES[PROJECT_CHECKS_SCOPE]` is exactly
`{house/integrate.py, house/maintenance.py, house/owner_upgrade.py}`.
No sandbox, web, provider, credential, spend or ratification constant is touched.

### `tests/test_source_inspection.py` — one sandbox regression

`test_prose_and_json_project_without_tests_reports_zero_and_still_checks_syntax`
(skip-guarded for nested macOS sandbox): builds `projects/case` with
`README.md` + valid `facts.json`, `integrate()` → `reviewed`, asserts log
contains `Ran 0 tests` and `json.load`; then breaks the JSON and
`integrate(publish=True)` → `tests-failed` with HEAD unchanged. Covers both
sides of the fix: zero no longer hides a later syntax error.

## 4. Code findings

1. **Fixes the witnessed exit-5 without weakening failure detection.**
   `TextTestRunner.wasSuccessful()` is true for an empty suite (0 failures,
   0 errors) and false for any failure or load error, so `SystemExit(not ...)`
   yields 0 for zero/passing and 1 for failing/erroring. Directly observed
   (private room shell, same interpreter, runner string copied verbatim):

   | dir | new runner exit | old CLI `discover -s` exit |
   |---|---|---|
   | empty (0 tests) | 0, output `Ran 0 tests / NO TESTS RAN` | **5** (the bug) |
   | 1 passing test | 0, `OK` | 0 |
   | 1 failing test | 1, `FAILED (failures=1)` | 1 |
   | import-error on discover | 1, `FAILED (errors=1)` | 1 |

2. **Discovery semantics unchanged.** `defaultTestLoader.discover(project)`
   with `project` as both start and top-level dir is the same loader the CLI
   uses; `TextTestRunner(verbosity=2)` matches CLI `-v` output wording
   (`Ran 0 tests`, `OK`/`FAILED`). The command is still
   `[sys.executable, "-c", runner, project]` with `cwd=candidate`, same as
   the old relative `-s project`. Multi-project order (sorted projects,
   `if test_exit: break`) is unchanged: a failing project anywhere still
   yields `tests-failed`; a zero-test project first no longer poisons the rest.

3. **Syntax checks still gate.** For the case shape, `check_plan` now emits
   `[runner project, json.load facts.json]` (verified by building a temp git
   repo `projects/case` with README+json and printing commands — both exit 0,
   first output contains `Ran 0 tests`). Broken JSON via the second command
   exits 1 with `JSONDecodeError`, so the new test's second half exercises a
   real refusal. No fake project tests are invented; the log truthfully says
   `Ran 0 tests`.

4. **Scope is narrow and consistent.** Dirty `house/` changes are exactly
   `house/integrate.py` + `house/maintenance.py`, both inside
   `ALLOWED_CHANGES[PROJECT_CHECKS_SCOPE]`. `SOURCES[PROJECT_CHECKS_SCOPE]`
   equals `KEEP_MOVING_SHA256` (`ecc055f8…`), the same owner-approval digest
   as the other repair scopes. `house/integrate.py` is already in the
   protected manifest via earlier scopes (`INTEGRATION_SCOPE`,
   `DELIVERY_SCOPE`, `REVIEW_TOOLS_SCOPE` all list it), so
   `owner_upgrade.prepare()`'s `set(old) | OWNER_MODULES` snapshot already
   covers it — no `extra` branch for this scope is needed and none was added.
   No change to `test_sandbox`, policy, or protected limits.

5. **Not blocking, noted for accuracy.**
   - The comment's "report Ran 0 tests" holds when the project dir exists.
     A fully deleted project dir still yields an empty command list and
     `reviewed` (pre-existing edge, noted by Cinder at 1713; unchanged here).
     With no files left there is no syntax to check, so this is a residual
     documentation nuance, not a reopened defect.
   - A project with only skipped tests still has `wasSuccessful() == True`
     (exit 0) — same as before (old CLI exits 0 when tests were discovered,
     even if all skip). Not changed by this delta.

## 5. Verification actually run (non-nested only)

Per the task, no lifecycle or full suites, no nested sandbox retry:

| check | command | observed |
|---|---|---|
| runner exit codes | `python3 -c "<exact runner>" <dir>` for empty/passing/failing/erroring + old CLI comparison | table in §4.1; new 0/0/1/1, old 5/0/1/1 |
| `check_plan` on temp git repo | temp `projects/case` (README+valid JSON), `check_plan(repo, base, head)` + direct exec of emitted commands | scope `projects:projects/case`, 2 commands, both exit 0, `Ran 0 tests` in first output |
| malformed JSON second command | `python3 -c "json.load(...)"` on `{broken` | exit 1, `JSONDecodeError …` |
| non-nested test subset | `EMBERHALL_CANDIDATE_SANDBOX=1 PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest` on the 5 non-sandbox `SourceInspectionTests` methods (dirty code, canonical root) | `Ran 5 tests in 19.131s / OK` |
| scope binding | import `house.maintenance`, print `SOURCES[…]` + `ALLOWED_CHANGES[…]` | `ecc055f8…` == `KEEP_MOVING_SHA256`; allowed == 3 files above |
| regression evidence (host, Keeper) | `evidence/source-delivery/review-tools/zero-tests/focused-tests.txt` (8 tests in 5.509s, incl. new test) | `Ran 8 tests … OK` — host result, not re-run here |

The 3 sandbox-guarded tests (`test_project_tests_gate…`,
`test_project_failure…`, and the new `test_prose_and_json…`) were deliberately
not executed in this native sandbox. The new regression's pass is evidenced by
Keeper's host log (8/8 OK) and by the direct runner/`check_plan` probes above.

## 6. Limits

- I did not run the full host suite, lifecycle probes, or nested sandbox
  integration; host full acceptance and isolated install remain Keeper work.
- I did not re-run the 3 sandbox tests here; I verified the new test's logic
  by reading it and by executing its two underlying commands directly.
- I did not read Night Ferry solution content or publish anything. The only
  contribution-specific bytes I opened are the preserved failed receipt/log
  and `CONTINUATION.md`/`focused-tests.txt` handoff already recorded.
- Hash binding is to the dirty canonical working tree at review time.
  Any Keeper edit after this review invalidates these hashes and needs a
  rebind; `git status` at review listed only the 4 files in §1.

## 7. Verdict

Bounded acceptance. The delta is exactly the claimed correction: the CLI
exit-5 false-failure is replaced by direct `TestLoader`/`TextTestRunner`
reporting with real failure propagation, zero-test projects still receive
their per-file syntax checks, the malformed-JSON refusal is covered by a
real sandbox regression, and the new `project-checks-20261114` owner scope
admits only `house/integrate.py` plus the two owner modules with no sandbox
or policy change. No blocking defect in the 3 files. Host full acceptance,
isolated owner preparation, and any retry of case `55ef52de` remain Keeper
work; this review authorizes the correction text only at the bound hashes.
