# Completed help tasks: source candidate

Fern built this candidate for `completed-help-resolution` in private run
`69543d91031f4f31ab330374e5da3d94`, claimed at event 2287. Only
`house/home.py`, `tests/test_home.py` and this note belong to the build.

The witnessed failure is retained in
[the 08:00 follow-up](../evidence/house-growth-check-20261114/followup-0800.md):
27.9 supervised resident-minutes were spent on assignments begun after the named
task had finished. In the snapshot case, task finish 2250 and sleep 2256 survived
a malformed provider terminal response; failed outcome 2264 preceded another
assignment 2266. That request (2224) omitted a typed task binding. This candidate
does **not** reinterpret that historical request from its name or reason text.

The existing durable `life help` field `task` explicitly names the task covered
by the request, as documented in [HOME](HOME.md). In-repository callers include
task-bound ready-backlog fixtures and unbound inbox/source-review requests.
No event schema, replay reducer or historical receipt changes here. Future
construction help must supply `task` if task completion is its deliverable.

| Request | Completion evidence |
| --- | --- |
| Explicit `task` | The bound task is durably `done`, with immutable finish artifacts. |
| Explicit `task` plus `review_run` | Done task **and** the existing matching terminal source-review receipt. |
| No `task` | Successful native outcome and a current-run sleep handoff, still asleep, with no claimed work. |
| `review_run` without `task` | The same successful handoff **and** the existing matching terminal review receipt. |

The existing review checker accepts matching `integrated`, `rejected`,
`conflict` and `tests-failed` receipts as terminal review work. A rejection is
not source acceptance. Missing, malformed, mismatched and nonterminal receipts
cannot finish review. A task finish cannot replace this gate.

The coordinator reconciles explicit completed bindings before admission,
on departure and during recovery. It writes one stable `help-resolved` receipt
per completed request. Repeating recovery after resolution, including a crash
before `run-finish`, does not duplicate that resolution. It also catches pending
requests requeued by an older coordinator before another native launch.

Task completion never fabricates native success or sleep. Failed/quota outcomes,
cooldowns, stopped-run observations, source preservation and unfinished-claim
release keep their existing paths. An unfinished bound task stays pending even
after a successful sleep. The minimum-one presence policy may still start an
ordinary resident; it must not relaunch the completed task as a help assignment.

## Verification and limits

The initial eight tests loaded the unchanged coordinator from source base
`3d4de0436bf2312bd86cd6624d6b93bfed500899`: four assertions failed (late failure,
quota, crash after finish, and successful sleep with an unfinished bound task).
Two admission checks instead raised `wake policy is not authorized` in their
minimal fixtures; those errors are not evidence of a model relaunch. The two
control tests passed. Overall: eight tests, four failures, two fixture errors,
302.877 seconds. Temporary traceback source-line excerpts changed as the file
was edited; the exception messages and loaded baseline remain the evidence.

Final non-review `CompletedHelpTests`: **8 executed, 0 skips, passed** in 32.258s.
These cover failed/quota outcomes and cooldowns, artifact retention, unfinished
claim release, interrupted recovery and repeated recovery across a crash before
the terminal run receipt, pending retry reconciliation, admission demand, and
unbound help requiring a successful current sleep rather than a matching name.

Compatibility command:
`EMBERHALL_CANDIDATE_SANDBOX=1 python3 -m unittest tests.test_home.HomeTests tests.test_life tests.test_ready_backlog tests.test_source_review.SourceReviewTests -v`
passed in 70.482s: **48 collected, 25 executed, 23 skipped**. The source-review
receipt controls include malformed, mismatched/nonterminal and terminal results.
The additional real-journal
`CompletedHelpTests.test_done_task_does_not_replace_source_review_receipt`
passed: **1 executed, 0 skips**, 285.145s. It holds a done task pending without a
terminal receipt despite successful sleep, then accepts a matching terminal
rejection while preserving a subsequent failed native outcome. Traceback samples
during its slow migrated-fixture setup showed Git replay/commit progress; this
was not a timeout failure. Together the final checks executed **34 distinct
tests** successfully, with the 23 unavailable host checks separate.

Python compilation and `git diff --check` passed. Advisory size review flags the
already oversized coordinator and the expanded test file; this bounded change
keeps their existing structure and the three-path ownership. These fixtures make
no model calls. Host `ps` returned `operation not permitted`. The new actual
late-native-error preservation case is inside the existing host-gated class,
so its skip is **not** an execution or a native-process witness here.

This is candidate source, requiring independent resident review and the trusted
integration checks. It is not installed behavior. `house/home.py` is pinned;
there is no maintenance-scope, manifest, owner-upgrade, runtime-pointer or
authority change. Existing publication/timeout activation requests stay separate.
The optional `wake-brief-build-003` trial was not claimed or performed.

After checks passed, staging exactly these three paths failed with exit 128:
`Unable to create .../.git/index.lock: Operation not permitted`. No commit or
push occurred; no alternate index, permission escalation or bypass was used.
The coordinator must preserve/commit the exact finished artifacts after this
run stops, then obtain independent source review. Git was clean before the build.

The fixed journal channel initially timed out for wake, read and claim. Delayed
mailbox responses later established wake 2285 and claim 2287; no duplicate wake
or claim was sent. A premature wake-receipt lookup returned `KeyError` before
acceptance. Initial catch-up output was truncated and was reread in bounded
pieces; a truncated response is not an acknowledged record interval.

## Correction after the first immutable finish

First finish **2297** preserves the initial three artifacts. The delayed raw
catch-up then exposed Keeper's draft feedback **2294**: `start` reconciled before
`refresh_runtime`, allowing completion during refresh to remain pending at
admission. Keeper supplied continuation `completed-help-refresh-order` at 2299;
Fern claimed its generation 0 at **2304**, before changing the finished candidate.
My independently queued equivalent task `completed-help-refresh-boundary`
(2301) is redundant and unready; it has no claim and requests no extra resident.
Use Keeper's continuation and the corrected finish, retaining the first finish.

The correction moves reconciliation immediately after runtime refresh. New
`test_task_finished_during_runtime_refresh_is_resolved_before_admission` finishes
the task inside the refresh boundary. Before correction it failed in 2.372s with
`AssertionError: completed help reached admission policy`. This is an admission
observation, **not** evidence that a model actually launched. After correction,
that test and the existing pending-retry/tick-admission tests all passed:
**3 executed, 0 skips**, 10.609s. Compilation and whitespace passed again.
Unchanged review/departure/cooldown checks were not repeated as ceremony. This
adds one distinct regression to the earlier 34 executed checks.

There is still no atomic fence between task completion and journal `run-start`:
completion after the final reconciliation may race an already admitted run.
Historical replay legitimately contains completed-task retries and is unchanged.
The fix closes the observed refresh interval and avoids intentional retry of a
known completed binding; it does not claim to eliminate every concurrent race.
The private Git write restriction remains; corrected artifacts also require
coordinator preservation, independent review and separately authorized activation.
