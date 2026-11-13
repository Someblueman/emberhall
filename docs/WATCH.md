# The bounded watch

The Steward authorized a user-level scheduler to wake headless Codex residents,
with at most twelve runs per local civil day. This module attempts one wake; it
does not install a schedule. The integrator owns the planned four daily wakes,
activation, `docs/WATCH_PROMPT.md`, and uninstall instructions in `docs/RESUME.md`.

```sh
python3 -m house.watch --repo /Users/sws/Code/longhouse inspect
python3 -m house.watch --repo /Users/sws/Code/longhouse run
```

`inspect` is read-only. It shows today's journal start count, pending runs,
checkout/claim blockers, an eligible recovery run, and the twelve latest safe watch
records. Before activation, the integrator must freeze the reviewed, clean,
committed runtime and tracked prompt:

```sh
python3 -m house.watch --repo /Users/sws/Code/longhouse prepare-runtime
```

This returns the source commit, per-file hashes, archive SHA-256, absolute entry
path and scheduling argv. Install that returned command, which executes a private
`runtime-COMMIT.pyz`, instead of importing the mutable checkout with `-m`. The
archive contains committed house Python files and the prompt, plus a minimal
entry point. It is verified against the source blobs; an existing archive must
match exactly. Preparation does not install or run a model. The pinned entry
also accepts `house --repo REPO verify` (and the other house commands), so a
recovery resident can use the verified old journal implementation while repairing
broken working imports. The mandatory prompt gives its exact argv.

Runtime refresh after code/prompt changes is explicit: review and test the new
code, commit a clean checkout, prepare and inspect the new archive, verify its
journal replay and inert recovery checks, then update the scheduler entry. Never
silently import newer working files. Schema changes must preserve compatibility
or include a tested runtime refresh before new events require it; a stale runtime
fails closed. The runtime and rescue store remain private local files, not a
replacement for a reviewed journal/source backup.

`run` uses the frozen root-selected prompt and `/Users/sws/.local/bin/codex`. Its
exact model command is:

```text
codex exec --approve-for-me --json -C REPO -o PRIVATE_FINAL_FILE -
```

The prompt arrives on stdin. No worktree, model override, API credentials,
`--full-auto` or unrestricted sandbox flag is added. This follows the checked
[official noninteractive documentation](https://learn.chatgpt.com/docs/non-interactive-mode).
The installed CLI/login were inspected by the integrator; these tests never
invoke a live model.

## Budget and ownership

The fixed ceiling is twelve **attempts**, including failed executable launches,
per local calendar day. Each accepted `start` records its observed local day in
the Git journal before launching anything. Old days are not reinterpreted from a
later timezone or backwards-adjusted journal timestamp. Local timezone follows
the scheduler process/system configuration; keep it consistent with this Mac's
Europe/London schedule. The attempt is charged even if the launcher dies before
spawning a model. An attempt crossing midnight before the launch gate is released
is aborted. The `--seconds` option may shorten the default 1,200-second deadline;
it cannot increase it.

Admission checks the quota, all tracked/untracked dirty work and every live task
claim against the same verified journal head, under the existing writer lock.
Pre-existing unrelated dirty work and every live claim cause a safe `skip`,
without consuming a start. A dirty checkout left by a scheduled run has the
bounded recovery route below. No files are reset, stashed, committed or removed
to force admission. Expired claims do not block admission, but their owner,
generation and token remain unchanged. Finish/release claims and commit completed
work before first activation. Every start assigns a unique `watch-UUID` resident
ID in the journal and a mandatory prompt prefix; the model chooses its name.
Recovery identifies prior claims through that exact assigned ID, never by treating
all post-start arrivals as belonging to the run.

An inherited kernel lock under the Git common directory prevents simultaneous
scheduled runs. Every invocation that encounters an active run, a dirty checkout,
a live task, or exhausted quota records its skip. Interactive residents must
also inspect the watch before editing this shared checkout: the watch cannot
stop a new interactive resident from claiming work after admission or writing
outside the cooperative protocol. It is not a hostile-shell isolation boundary.

## Death and deadlines

The launcher spawns a separate supervisor and passes its lock descriptor. The
supervisor retains the lock and deadline if the launcher dies. It checks both
monotonic elapsed time and the recorded wall deadline, so a backwards clock does
not grant more runtime and a Mac sleep does not grant another full window on wake.
The model subprocess starts in a new process group behind a pipe gate. Its group
ID is written to Git before the gate allows `exec`; if the supervisor dies before
that receipt, closing the pipe prevents the model from starting.

At the deadline the supervisor kills the process group and reaps its direct
child **before** journalling the timeout. The same cleanup occurs after ordinary
exit, so leftover processes in that group do not continue in the background.
The supervisor confirms the group is stopped before publishing a terminal
finish. A killed supervisor leaves an unfinished start; the launcher, or the
next invocation if both died, recovers it before admitting new work. Recovery
checks the unique run ID in the surviving group's command lines before signalling
it, avoiding an unrelated group after PID reuse. An unidentified or unkillable
group makes the runner fail closed with a recorded skip; inspect local processes
rather than deleting its record or guessing at a PID.

The process-group guarantee covers processes remaining in that group. A tool
that deliberately detaches into another session is outside it. Scheduled prompts
must prohibit persistent background processes and further model scheduling.
A power failure prevents further work and may delay the interruption receipt
until the next wake; it does not refund the attempt.

## Records and private output

The dedicated machine resident `watch-keeper` writes structured `say` messages
prefixed `house-watch-v1 `. The schema has `kind` and `run`, with bounded metadata:
`start`, `launched`, `timeout`, `execution-result`, `supervisor-exit`, `rescue`, `rescue-blocked`, `finish`,
`recovered-interruption`, or `skip`.
Deterministic `watch-RUN-KIND` receipt IDs preserve retry identity. The quota and
completion state come from replaying those messages; there is no separate
mutable counter. Do not impersonate this resident or write hand-edited watch
messages. A machine supervisor is not evidence of another independent model mind.

Raw JSONL events, stderr, the base/assigned prompts and final output stay in
`.git/house-watch/RUN/` (the Git common directory for linked checkouts). Directories
are mode 0700; created logs are 0600. None is added to source or journal artifacts.
The journal contains outcome codes, not model output or exception text. Keep raw
logs private: tool responses and final messages can contain secrets. Review and
redact any proposed report before publishing it. `inspect` is the safe concise
summary interface.

A completed invocation prints a JSON result, including a failure or skip; its
shell exit is zero when that result was delivered. Invalid configuration,
unreadable state, or output-channel errors exit 2. Check the result's `kind` and
`outcome`, not only the shell exit. A lost output response never retries a model
run automatically: inspect the journal first. Internal `_worker` and `_exec`
subcommands implement the supervisor/gate and are not scheduling interfaces.

## Evidence

`python3 -m unittest tests.test_watch -v` uses actual executable fixtures in
fresh Git repositories. It exercises the supported argv and stdin, twelve failed
starts and the thirteenth denial, concurrent invocations, dirty/live-claim skips,
nonzero exit, a sleeping child and grandchild at timeout, killed launcher,
killed supervisor, both killed followed by recovery, private log permissions and
nonpublication, closed summary stdout, read-only inspection, civil-day boundaries,
and the hard deadline ceiling. The prior-day fixture uses explicitly synthetic
journal dates; it does not pretend a day elapsed.

Process-table access is required for the real orphan checks. The Codex tool
sandbox denied `ps`; the authorized tests were run outside that sandbox against
inert fixtures. Initial temporary-source commits also inherited this Mac's signing
configuration; tests now disable signing only for that fixture commit command.
No user Git settings changed. These are implementation tests, not evidence that
launchd is installed, that a live Codex task completed, or that days have elapsed.
The integrator owns those subsequent acceptance receipts.

Observed implementation acceptance on 13 November 2026: twelve focused watch
checks passed in 15.147 seconds; the broader suite immediately before the final
wall-deadline gate regression ran eighty tests in 45.692 seconds, with five
opt-in legacy loopback SSH checks skipped. Compilation and the repository's
advisory module-size check passed; Ruff was unavailable. Live read-only inspection
reported zero starts, no pending runs, and `dirty-checkout`; no live watch was
started by the implementation resident.

## Repairing the dirty-checkout dead end

The first implementation preserved files but rejected every later dirty wake.
Keeper identified the goal-level consequence before activation: a timed-out
resident could leave the house needing a human forever. Sedge reproduced it with
an inert child that changed a tracked prompt, created `unfinished.txt`, then
exited 7. The exact original command and observed assertion were:

```text
python3 -m unittest tests.test_watch.WatchTests.test_scheduled_dirty_failure_can_resume_without_reset -v
FAIL: test_scheduled_dirty_failure_can_resume_without_reset
Traceback (most recent call last):
  File "/Users/sws/Code/longhouse/tests/test_watch.py", line 233, in test_scheduled_dirty_failure_can_resume_without_reset
    self.assertEqual(resumed.get('kind'), 'finish', resumed)
AssertionError: 'skip' != 'finish'
- skip
+ finish
 : {'kind': 'skip', 'run': 'faa0435f1cbb41c4b23d7019990eaa15', 'reason': 'dirty-checkout'}
Ran 1 test in 0.964s
FAILED (failures=1)
```

This is Sedge's before witness. Keeper's attempted sandboxed reproduction could
not inspect processes; the escalated rerun happened after repair and passed, so
it is not claimed as an independent reproduction of the original failure. The
original completed runner remains immutable in task `bounded-watch`, sequence
134. The repair is published separately as `watch-dirty-recovery`.

After the model group stops, the supervisor preserves changed regular working
files, deletions, distinct staged versions, and safe regular untracked files in
`.git/house-watch/rescue.git`, a **separate private bare Git store**. It records
the source HEAD, status and exact bytes in `rescue.json`. This includes the case
where staged content differs but the working file again matches HEAD. Only the
private commit ID, source HEAD and fingerprint enter the house journal. The
private store's objects and refs do not enter ordinary source pushes or house
bundles. It can contain secrets from unfinished files: do not copy, bundle, push
or publish it without explicit review. Raw model logs are never part of rescue.

A later dirty wake is allowed only if its last scheduled start has a recorded
rescue and the current HEAD, index and working/untracked bytes exactly match that
snapshot. An unrelated edit after the snapshot blocks recovery. A killed
supervisor leaves an unfinished start; interruption recovery first stops its
identified group, then records the private snapshot before allowing another
attempt. The clean admission witness attributes the observed checkout to the
scheduled interval under the cooperative exclusive-checkout convention. It does
not prove authorship against arbitrary outside writers during that interval.

The recovery wake consumes the same twelve-per-day budget. Its new assigned
resident receives a restricted prefix: inspect the original run and private
rescue, preserve all changes, repair only that unfinished work, do not reset,
stash, unlink, publish rescue data, alter journal schemas or start unrelated work.
The ordinary prompt is not appended to a recovery assignment, avoiding conflicting
instructions to start unrelated work. Its original bytes are kept privately for
provenance, so a child that damages the working prompt cannot rewrite the next
recovery assignment. Recovery may commit a verified repair locally but does not
push or publish private evidence. Existing live leases still
block admission; later recovery may reclaim expired work only through the normal
current-generation/fresh-token protocol. The runner never renews or steals an
old resident's claim.

Snapshot input is bounded to 8 MiB per file and 64 MiB total decoded working/index
bytes. Symlinks, nonregular paths reported by Git, changed-during-read files,
missing private evidence and excessive snapshots fail closed. Git-ignored files
and untracked special files that Git does not report (such as FIFOs) are neither
read nor modified. They are not claimed as rescued. These unsupported or damaged
cases remain explicit blockers; this is a bounded regular-file recovery path,
not an arbitrary filesystem repair tool. A separate inherited kernel writer lock fences snapshot Git children; only this
protocol's exact private rescue ref lock may be recovered under that lock. Git
objects and refs preserve accepted snapshot bytes across process interruption. They remain on this Mac's disk:
physical disk loss, deletion of private state and replication are not solved by
this local rescue store.

Additional inert regressions verify exact tracked/untracked/staged preservation,
recovery budget participation, changed-after-snapshot refusal, old live lease
retention followed by recovery after actual expiry, private object separation,
and recovery through the pinned zipapp after invalid syntax is written into both
mutable `watch.py` and `model.py`. The ordinary mutable module invocation then
fails with `SyntaxError`, while the pinned journal command and recovery run
succeed without silently resetting either broken file. A first snapshot attempt
also exposed an access-time false positive; mutation checks now compare identity,
mode, size, modification and change times, excluding the access time changed by
our own reads.

Sedge also replayed the original dead end from the SHA-256-verified immutable
`bounded-watch` source (`37cfafef62ce9fe48774764c4e29840e40128ad347380766ab8c9688fe99f85a`)
in a disposable source copy and Git house. An inert executable wrote the same
tracked/untracked values and exited 7. First result: `finish / child-failed`, run
`6b5ec29ad393446bb0111861290136ed`; next result: `skip / dirty-checkout`, run
`bec8610955c140c596e77c98d2f0fc44`. The partial bytes remained intact. This confirms
the before behavior can still be reproduced from the preserved earlier artifact;
it does not change Keeper's independent-observation limits.

Repair acceptance on 13 November 2026: all twenty-one focused watch tests passed
in 28.713 seconds; thirteen existing journal concurrency/recovery checks passed
in 4.487 seconds. After narrowing the recovery prompt to omit ordinary new-work
instructions, the three affected preservation, pinned-runtime and timeout checks
passed again in 5.730 seconds. Compilation and advisory module-size checks pass.
These checks used inert executables and disposable houses; no live model run,
scheduler installation, source commit or push was performed by Sedge.

## First real wake: keep a known result through delayed cleanup

Hazel's actual headless watch171-181 completed useful Blackout repair179 and
pushed bf23574. Its model stream ended with turn.completed, but the original
supervisor left no OS exit receipt; recovery recorded interruption181. That
history is retained. We do not infer an OS exit code from a final model message.
The2.395-second gap after final output is consistent with the2-second cleanup
check, but the old runner discarded diagnostics. The actual cause is unproven.

Sedge tried four real disposable launchd jobs with inert successful leaders and
sleeping descendants. All finished normally; that topology did not reproduce
Hazel's outcome. No arbitrary larger cleanup timeout was introduced.

Keeper and Sedge independently reproduced the loss of a known result with an
actual inert child exiting0 and the cleanup-confirmation predicate forced false.
The supervisor now writes a nonterminal `execution-result` before checking that
all descendants stopped. It still refuses `finish` while cleanup is incomplete.
Recovery first stops/confirms the process group; only then can it publish a finish
carrying that already recorded outcome, with `recovered: true`. If the observed
result is absent, it retains the original unknown-interruption outcome. It never
refunds an attempt or reruns a model to recover a receipt.

The launcher records `supervisor-exit` and retains private stderr in
`.git/house-watch/RUN-supervisor.log`, mode0600 under the private directory.
A cleanup-pending diagnostic is local only. These records distinguish observed
child exit, supervisor exit and group cleanup without publishing model output.
`evidence/watch-install/result-before.txt` and `result-after.txt` preserve the
independently witnessed branch regression. The second actual wake191-203 tested the
refreshed pinned runtime: execution-result201, finish202 and supervisor-exit203
all record exit0/success, with the process group independently observed empty.
Its private supervisor log was empty. This validates the installed successful
path; it does not retrospectively identify the first run’s discarded exit code.
