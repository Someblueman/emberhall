# Which families tied for a task?

A shortlist answers one question. When the coordinator chose a family for this task, which families had equal first claim on the wake under ordinary rotation?

The coordinator checks which families are open, gives first priority to those below their busy threshold, and compares starts in the last 32 ordinary assignments divided by each family's current share. It keeps every family tied at the best of those two comparisons. The oldest last start wins within that group. Equal last-start sequences follow the established family order. A route resting on quota can transfer part of its family's share to Codex, which also changes how many active runs count as busy.

## Reading a decision

Look up the controller's `house-assignment-v1` message by run, then join it to the controller's `life/run-start` for the same run. The start names the selected family. Three optional fields in the assignment message describe the decision.

| Field | Meaning |
| --- | --- |
| `task` | The task ID the coordinator knew when it chose the family. |
| `task_generation` | The generation of that task at the choice. |
| `tied_families` | Distinct family IDs in scheduler declaration order. A single entry means rotation had just one best family. |

For example, a shortlist of `["codex", "opencode", "muse"]` with a Codex start permits a replay to compare OpenCode or Muse with the usual choice. Agy would be outside the comparison. A family can be absent because it was unavailable, already busy, or had received more starts per share. The shortlist alone cannot tell which reason applied. Its order does not rank the tied families by recency.

Coverage begins when this source passes independent integration and council installation. The fields cover supervised ordinary project-backlog tasks and ordinary help requests that name a task. A help request can carry the association even when the run-start itself only names the request. The task must have an identifier of at most 100 ASCII letters, digits, hyphens and underscores, beginning with a letter or digit. Only the identifier, generation and family names are copied. Task descriptions and request text have no place in these fields.

Direct starts, provider or resident requests (including a fallback when the preferred family is resting), helper work, ballots, source reviews, Explorer turns and unbound wakes have no shortlist. An admission refused before run-start has no assignment observation. An admitted startup can subsequently fail or exit on quota. Outcome analysis has to join the run's finish and exclude quota exits separately.

The offer must still describe the same task generation at admission. For example, a resident may attach an ordinary help task to a ballot after the family was chosen. The ballot wake follows the existing admission rules and carries no ordinary shortlist. The reader skips it and can enroll the next ordinary offer. A change after admission cannot erase a valid decision.

## Limits of replay

The shortlist comes from the state used by the picker. Admission rechecks its own conditions and may read newer state. The existing `prior_starts` field describes the start's read. A later status page, the list of configured providers or the next wake cannot supply a missing shortlist. For an older receipt, label any independently reconstructed choice as historical inference and report missing evidence separately. A proposed switch can be assessed only within the recorded tie. A tie gives no observation of how the other family would have done.

A task association is an offer of work. To count completion, follow the actual resident's claim and finish, accounting for competing claims and reclaims. First-review outcomes need their own independent review receipt. The twenty-task trial requires live eligible records after installation. The tests below use disposable journals.

```sh
python3 -m unittest tests.test_craft_parity_candidates tests.test_assignment_balance tests.test_quota_rest.SharingTests tests.test_course_correction.RotationTests
```
