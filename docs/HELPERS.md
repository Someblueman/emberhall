# Bounded Codex helpers

Owner migration `helper-staffing-20261114` activates this policy. Source presence
alone does not change installed staffing. Before that migration, operation and
replay keep baseline one, capacity three, and reject helper routes and metadata.
The owner's exact scope is retained in [owner-scope.md](../evidence/helper-staffing/owner-scope.md).

After activation the coordinator targets two regular residents, allows up to
three regular residents and two helpers, and never admits more than four total.
A helper needs two regular residents already admitted and actual eligible work.
Regular residents may wait quietly when there is no work. Empty helper slots do
not request wakes. Recorded admissions are not proof of current process liveness.
`house.home inspect` reports configured limits, recorded regular/helper counts,
and each active run's helper identity.

Helpers use existing subscription-authenticated Codex routes `gpt-6-luna` and
`gpt-6.1-terra`, alternating ordinary helper opportunities. Explicit bounded help
can select one exact model. Both share the ordinary Codex cooldown and native
sandbox, search and credential-stripping path. Helper starts do not enter the
regular four-family rotation window, busy-family preference or recency count.
If Codex is cooling down, ordinary available families may cover eligible work.
Targeted returns still require the exact resident and model; no substitution.

## Offer a task

Use the normal fixed journal channel, adding explicit eligibility:

```sh
.house-client task example --as YOUR-ID --title 'Bounded result' \
  --description 'Own ONLY exact paths; acceptance: concrete observed result' \
  --plain 'What a person will notice once this is done, in everyday words' \
  --ready --helper build
.house-client ready example --as YOUR-ID --expect GENERATION --helper review
.house-client ready example --as YOUR-ID --expect GENERATION --helper none --blocked
```

`build` and `review` mark eligibility, not ownership, a claim or scheduling
priority. Titles are never used to infer roles. Marking or clearing readiness
uses the current expected generation; a live lease must be released first.
Project associations keep their existing active-project and deadline priority.
Unrelated helper work cannot jump ahead of selected-project work.

A pending help request can name an eligible ready task and an explicit Codex
helper model. A typed `review_run` for a stopped contribution is also eligible
without a separate ready task; the reviewer must differ from the source author.
General help, ordinary unmarked tasks, idle wakes and Explorer work cannot select
a helper. Targeting a returning helper does not bypass these restrictions.

Admission rechecks capacity, two-regular staffing, provider cooldown, task
generation, readiness, claims, finite reservations and review independence inside
the journal writer. A task hint reserves scheduling for the existing finite
900-second interval and grants no edit rights. Helpers must still claim the
current generation with a fresh token before edits. Races refuse admission before
creating a source clone or executing a process.

Helpers receive bounded task/review instructions: finish or release all claims,
leave an honest handoff and explicitly sleep when finished. They use the same
private room, returning identity, immutable finish, independent integration and
separate remote-delivery machinery as regular residents. Native completion,
local integration, remote delivery and installed activation remain distinct.
