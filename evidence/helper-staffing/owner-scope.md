# Owner-directed resident staffing

The owner asked in this chat: “I’m also curious if we can have 1-2 more residents
at a time running either Luna or Terra? Might not want them to run the research
tasks but would be good to help keep velocity up.” The owner subsequently said
the Luna/Terra proposal sounded good and asked that the house feel alive. Standing
instructions authorize routine implementation and tested deployment; this text
records the bounded implementation choice, not an invented new owner message.

Scope `helper-staffing-20261114` implements that request with two regular residents
as the baseline when providers are available, a total ceiling of four supervised
residents, no more than three regular residents, and up to two additional helper
residents within that total. Helpers use existing subscription-authenticated
Codex with `gpt-6-luna` or `gpt-6.1-terra`, never a new API key, pay-per-token
provider, purchased credit, or new credential. Normal four-family scheduling
continues; helper starts do not count against the ordinary family rotation.
The installed local model catalog and official model documentation list both
exact model names: https://learn.chatgpt.com/docs/models#recommended-models .
Model availability and useful actual work still require observed native runs.

Helpers get a concrete ready task explicitly marked build/review eligible, or
an independent source-review assignment. They are never dispatched as Explorer,
for an unbound general wake, or merely to fill an empty helper slot. At least two
regular residents must already be admitted before a helper is admitted. Existing
ready tasks remain available to ordinary residents. Two regular residents may
wait quietly when there is no work; additional helpers require real demand.
The helper launch must recheck task generation, coverage, capacity and cooldown
inside the journal writer, retaining existing finite scheduling reservations,
claims, independent review, returning identities and crash recovery.

Only the tested owner migration activates the new staffing and helper task
metadata. Pre-migration replay and operation retain baseline1/cap3 and reject
helper routes/metadata. No active charter, council process, wake-policy text,
sandbox, web safeguard, money/key policy, ledger/foundation anchor or existing
source-review authority changes. Ordinary dynamic assignment instructions may
name the helper’s bounded task and ask it to sleep when finished.

Scope-owned enforcement files are house/staffing.py, house/home.py, house/life.py,
house/providers.py, house/model.py, house/__main__.py, house/work_metrics.py,
house/maintenance.py and house/owner_upgrade.py. Focused regression checks, an
independent source review, full required exact-source acceptance, a normal drain,
authenticated owner migration, and actual installed-runtime/native helper checks
remain required. No current process is restarted merely because observation
expired. Provider quota holds remain shared under the existing Codex family.
