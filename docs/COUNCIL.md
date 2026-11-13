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
