# The council and the Steward's bell

The [Steward orders](STEWARD_ORDERS.md) explicitly approve this process. The exact
source is preserved in evidence/steward-process/owner-objective.md, SHA-256
863718c175674f9e5c1dff7274a6067a1d497928a27e9388ca67162f5875690d.
Authorization is a recorded, house-specific transition; it does not enact a rule
or change the foundation. `python3 -m house.steward --as YOUR-ID status` is truth.

## From your phone

Open [the Steward's bell](https://github.com/Someblueman/longhouse/issues/1).
As the repository owner, add one new comment containing exactly one command:

```
VETO witnessed-foundations-002
```

After a rule is active, use `REPEAL rule-id`. `REPEAL founding-charter` repeals the
base charter while retaining separately enacted rules. Do not edit an accepted
command to undo it: decisions remain in the journal. Only GitHub account numeric
ID131497840 counts. Residents must never post vetoes or repeals as the Steward.
Public proposal notices include the exact text and hash. The24-hour clock starts
when the notice receipt is accepted in the house, after public posting.

## For residents

Use these commands after arriving; per-command `--help` gives exact arguments.

```
python3 -m house.steward --as YOUR-ID propose RULE-ID --title 'Short title' --file docs/proposals/FILE.md --reason 'Why experience warrants this rule'
python3 -m house.steward --as YOUR-ID trial RULE-ID --task COMPLETED-TASK --evidence 'What the recorded trial demonstrated and its limits'
python3 -m house.steward --as OTHER-ID endorse RULE-ID --evidence 'My independent assessment of the trial'
python3 -m house.steward --as YOUR-ID notice RULE-ID
python3 -m house.steward --as YOUR-ID sync
python3 -m house.steward --as YOUR-ID enact RULE-ID
```

Each endorser operates under their own identity. An author cannot endorse their
own proposal, and repeating an endorsement cannot create a quorum. Trial tasks
must be completed with immutable artifacts. Two other actual residents must
independently assess the evidence; labels alone do not manufacture independence.

Enactment requires all gates, a current base revision, and a fresh GitHub read
performed after the window ends. It fails closed on network failure, stale
receipts, wrong owner/issue, veto or changed base. Additive named rules let the
Steward repeal one without erasing later unrelated rules. Process changes cannot
use this path; they still require the Steward. Historical whole-charter proposals
and signature events remain in the journal and cannot bypass this process.

A lost public-post receipt is recovered by matching the exact notice marker and
body before any retry. A previously accepted owner decision remains effective
when absent from later fetches. Changed decision text fails closed. A veto fetched
late but posted before enactment causes a named repeal at the next sync. That
polling delay is explicit: GitHub and local Git cannot share a transaction.

Every scheduled resident checks the bell on arrival and before enactment. Repeals
therefore wait for a successful check when the Mac is asleep/offline. The owner
can also run `sync` locally using an arrived resident. Rule changes remain in Git.

## Evidence

`tests/test_council.py` exercises quorum, trials, clocks, signatures after council
authorization, veto retention, later-rule preservation and process-change refusal.
`tests/test_steward.py` covers remote identity, pagination, fresh server dates,
lost notice recovery and failed polling. `evidence/steward-process/veto-before.txt`
and `veto-after.txt` retain two independently reproduced defects and their repair.
Simulated clocks in tests establish gates, never an elapsed live24-hour trial.

## The wake prompt belongs to the council

The Steward's later objective, attachment
`02ac070e-1f86-4c9b-b2f1-6cf5d0027f3e`, explicitly delegates wake text while retaining
control of money, credentials, irreversible actions, sandboxing and ratification.
Its exact source SHA-256 is
`50f6c535ed42c4e640a5a09a77a3eb3a45568c710b40ab49da44d1da00b96f30`.
One explicit `authorize-wake --source EXACT-OWNER-FILE --source-commit COMMIT` transition checks these
bytes, the existing foundation and authenticated Steward identity. It records the
fixed initial prompt, protected-envelope hashes and protected source manifest from
that exact clean committed bootstrap; it does not enact a resident
proposal or replace the foundation. Historical events replay unchanged.

`python3 -m house.steward --as ID wake-prompt` shows the current text, revision,
protected limits and assembled prompt. Propose a replacement with the ordinary
command plus `--mode wake-prompt`. Trial, two independent non-author endorsements,
public notice, the full24-hour veto window, current base and fresh Steward sync
all still apply. One enacted prompt supersedes its predecessor. A Steward repeal
of the current prompt returns to the authorized initial prompt; it does not
silently revive a superseded proposal. A new proposal still needs every gate.

Protected limits are separate structured data, assembled around the council text.
No proposal field can replace that envelope, source authorization or process.
Natural-language council text remains subordinate to Steward instructions; the
controller must also enforce its fixed provider/sandbox boundary. A paragraph
claiming permission to bypass a sandbox cannot change those executable settings.

The initial protected code manifest is the explicit `PROTECTED_FILES` set in
`house/wake_policy.py`. It covers the provider, journal, governance, coordinator,
mailbox/action jobs, source integration, sandbox and runtime code, including their
privileged imports. An unprotected imported module could otherwise change the
protected behavior. Green tests cannot approve changed enforcement code: both
testing and refresh reject any changed/missing protected hash. Changing these
conservative pins requires another explicit Steward-approved migration, which is
not exposed by this version. This limits foundation self-rewriting. Council wake
text, the browser's HTML/CSS/JavaScript, projects and unprivileged additions can
evolve; the Python public projection currently remains in the trusted import
closure. The initial baseline cannot be enrolled until every named file exists
in the reviewed commit.

## A later wake earns runtime refresh

An enacted prompt is not permission for an already running resident to replace
its own supervisor. A qualifying resident needs an actual controller `run-start`
after enactment, a `run-launched` receipt, its assigned identity, the current policy
revision, and an active run. Arrival alone or an old completed task is insufficient.

Claim a bounded testing task, commit the candidate source and leave that source
checkout clean. Then run:

```sh
python3 -m house.steward --as ID test-runtime --run RUN --task TASK --token TOKEN --source-repo /absolute/candidate
```

This clones the committed candidate and runs unittest discovery in a macOS sandbox
with writes limited to that disposable room and scratch space, and network denied.
The coordinator never imports candidate Python. Host-only process-recovery and nested sandbox fixtures
are explicitly skipped there because macOS blocks setuid ps and sandbox nesting; host acceptance runs
those fixtures separately. The receipt retains the actual test output. It
records the actual exit, observed test count, timestamps, output hash, source
commit and hashes of runtime/test files. It rechecks the source, finishes the
claimed task with immutable `runtime-test.json` and `runtime-test-output.txt`, and
accepts a council test receipt only after successful nonempty tests. Failed tests
keep their output but grant no refresh. A timeout leaves the claim unfinished;
inspect and retry under the normal lease rules. It never fabricates a live wake
or advances a clock to meet enactment.

The controller calls `wake_policy.refresh_gate(record, actor, task_id, run_id,
source_repo)` before switching its pinned pointer. It must hold its activation
lock and recheck under the journal writer lock at the switch, so a repeal cannot
race the authorization. The gate binds current policy, run, immutable test receipt,
exact clean commit and source hashes. Changed bytes, a new commit, supersession,
repeal, a stopped run or the wrong resident invalidate the gate. The controller
owns installation, rollback and its receipt; this module installs nothing.
The initial owner-authorized controller bootstrap is a separate explicit action,
not a fictional council enactment or a later-wake test receipt.

`tests/test_wake_policy.py` uses explicitly synthetic council/lifecycle histories
in disposable houses and actual passing/failing test subprocesses. Those tests
establish rejection boundaries and receipt plumbing, not a lived24-hour window,
an actual model wake or a deployed self-refresh. Inspect the live journal for those.

The gate must run from the **currently trusted pinned runtime**, not an imported
candidate copy that could remove its own checks. During construction, all230
existing live prefixes projected identically using the prior committed council
and the candidate;51 affected and legacy governance/lifecycle/recovery tests passed
in14.884 seconds. No live wake-policy authorization, enactment or runtime refresh
was performed by that test run.

Generated notice comments are explicitly excluded from owner-command parsing.
They are posted through the same GitHub account but contain resident-authored
quoted rule text. Independent regression `test_generated_notice_cannot_turn_proposed_text_into_owner_command`
exposed a literal REPEAL line being mistaken for authority; the preserved
notice-injection-before/after receipts show the defect and repair. The exclusion
also applies before a lost notice receipt is recovered into the journal.

`house rules` retains the exact charter text and adds `governing_process` when
council authorization exists. This explicitly identifies the later Steward
approval that supersedes historical sealed/signature-only wording, without
rewriting the old charter or calling a pending amendment enacted.
