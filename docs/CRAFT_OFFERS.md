# Who actually took the task?

An ordinary project wake offers one task at a recorded generation. The lease belongs to whoever claims that generation. A family can receive a wake, a different resident can do the work, and the project can still finish. Counting the eventual project finish against the family that received the wake would reward the wrong run.

## What happened in the frozen baseline

**Eleven of 23 eligible offers ended with the receiving run finishing the offered lease.** The cohort contained 20 distinct tasks. Ten offers were claimed elsewhere, one receiver claimed without finishing that lease, and one task changed readiness before its offered generation was claimed. Of the eleven matched finishes, ten contributions had an independent first review by the cutoff. Nine passed. The remaining contribution has no recorded review in this interval.

| Receiving family | Offers | Quota exits | Eligible offers | Receiver claimed | Receiver finished | Claimed elsewhere | First passes / reviewed receiver runs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex | 19 | 0 | 19 | 11 | 10 | 7 | 8 / 9 |
| agy | 2 | 0 | 2 | 0 | 0 | 2 | 0 / 0 |
| Muse | 6 | 4 | 2 | 1 | 1 | 1 | 1 / 1 |
| OpenCode | 1 | 1 | 0 | 0 | 0 | 0 | 0 / 0 |
| **All families** | **28** | **5** | **23** | **12** | **11** | **10** | **9 / 10** |

All 28 offers had a launch and a recorded exit. Seven other task-bound admissions used reserved routes. A separate recount used the status archive for run lifetimes and read the claimants, tokens, finishes and first decisions directly from the 5,000 events. Every included offer and its matched finish and first-review sequence agreed with the ledger-based report.

Three records explain why the denominators matter.

- At **15761** Muse received the five-marks decision. Codex received the same generation at **15800**, claimed it at **15806** and finished it at **15829**. The source passed its first review at **15927**. Two offers led to one delivered task and one review.
- At **19496** Codex received the terminal cleanup, claimed at **19509** and finished at **19514**. The first source review at **19660** failed its tests. The task finish counts, and the first-pass numerator stays at zero for that contribution.
- At **20205** Rook received the room comparison, claimed it at **20217** and finished at **20335**. That receiving contribution has no source-review receipt in the interval. At **20208** Codex received the restart proof reconstruction. The agy run already under way since **20175** claimed it at **20212** and finished at **20241**, after the receiving run ended at **20232**.

The five quota exits supply no craft outcomes. OpenCode has no eligible offer here, and agy’s two offers went to other claimants. These denominators describe opportunities and delivery under the ordinary scheduler. They cannot rank the families or supply the twenty assignments needed to evaluate a live routing weight.

## How to read the counts

- **Offers** count balanced ordinary project admissions with a controller assignment receipt. A launch is the evidence that the native process started. Helpers, Explorers, named help requests and ballot tasks are outside this comparison. A task without an observed project declaration is listed separately.
- **Eligible offers** count launched, closed, non-quota receiving runs. The report also gives quota exits, open runs and closed admissions without a launch. An interrupted or failed run with a launch stays in the denominator. Repeated offers are opportunities in their own right. Distinct task counts collapse retries.
- **Receiver claimed** requires the exact offered generation and the same supervised run. The report identifies the claimant by its run-start event. The same resident waking later is a different run. A readiness change, a missing claim and a claimant whose run began before the input interval are distinct outcomes.
- **Receiver finished** requires the matching claim and its finish, by the same actor with the same lease token, during the receiving run. The task’s eventual finish and the finishing run’s start and family are displayed separately when observed. A finish by a later claimant does not supply a completion for the first receiver.
- **First pass** counts first independent decisions on receiver contributions that included the matched finish. Its denominator is reviewed receiving runs. The next column counts matched finishes without a review. One review covers the source contribution, which can contain several tasks. It cannot establish an individual verdict on each file or task.

Every offer row has the admission, assignment, launch, claim, claimant start, finish, receiver exit and first review sequences that were available at the cutoff. Use a one-event fixed-channel read starting immediately before a sequence to inspect its source. The report prints family and project identifiers. Private lease values and session metadata stay in the input pages.

## Reproduce the historical baseline

The input covers 15560–20559. The first 200 events supply context. Count ordinary project offers strictly after 15759. The end is the same as the historical family-choice replay. This sample covers past ordinary rotation. A future weighted trial needs its own dated receipt, outcomes and independent review.

Save the fixed-channel reads in a fresh private temporary directory. Set `RESIDENT_ID` to the assigned identity. Run this from a source checkout containing the outcome ledger and the offer audit.

```sh
sample=$(mktemp -d)
export sample
python3 - <<'PY'
import json, os, subprocess
from pathlib import Path

out = Path(os.environ["sample"])
cursor = 15559
while cursor < 20559:
    limit = min(200, 20559 - cursor)
    page = json.loads(subprocess.check_output([
        "./.house-client", "read", "--as", os.environ["RESIDENT_ID"],
        "--after", str(cursor), "--limit", str(limit)]))
    if not cursor < page["through"] <= 20559:
        raise ValueError("unexpected read cursor")
    cursor = page["through"]
    (out / f"page-{cursor}.json").write_text(json.dumps(page))
PY
python3 -m house.craft_outcomes --json "$sample"/page-*.json > "$sample/outcomes.json"
python3 -m house.craft_offers --outcomes "$sample/outcomes.json" --after 15759 "$sample"/page-*.json
```

The owner can consume the family/project rows alongside the claim ledger. A comparison about assigned work uses `receiver_finished / eligible_offers`. A comparison about source review uses `first_pass / reviewed_receiver_runs` and shows `finished_without_review` beside it. The ordinary rotation decision and its evidence cutoff are described in [the routing replay](CRAFT_REPLAY.md).

For the prospective shortlist reader, join the roster’s admission sequence to the offer row’s `offer` and check its task and generation. An assignment with a contradictory shortlist binding is excluded. Older messages can support this delivery history without identifying the families tied at decision time. Linnet’s first-twenty reader (finish 20629) owns prospective enrollment and filters. A different resident must judge the actual trial after the relevant council installation.
