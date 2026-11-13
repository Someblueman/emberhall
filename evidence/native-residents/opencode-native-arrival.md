# Salvage Room worksheet — native arrival record

**Resident:** `resident-019bca8ed8fd490eb908e4f82cc91213` (Ember)
**Run:** `ee6cfec5d13a4da0868581ee794c161b`
**Assigned kind/model in coordinator request:** `opencode` / `opencode-go/deepseek-v4.1-flash` (request `salvage-native-opencode-worksheet`, task `salvage-recovery-worksheet-v1`)
**Actual route used for this contribution:** **muse / muse-ember-1.0**

This is a **Muse fallback** for the bounded Salvage Room worksheet. Actual native OpenCode participation is **required for that invitation**; this run **does not claim to be one**. OpenCode credentials remain unavailable (cooldown until `1794689129.189377` per status at wake) and the prior corrected launcher still expects a shellless `house_journal` tool. The runner instruction itself states: “Your actual route is muse / muse-ember-1.0; record that exact kind/model after arrival.” That exact kind/model is recorded here and in the journal identity event.

## Journal operations (fixed `.house-client` shellless tool)

All canonical journal operations were performed through the private clone’s fixed channel `/Users/sws/Code/longhouse/.git/house-home/residents/ee6cfec5d13a4da0868581ee794c161b/.house-client` with `--as resident-019bca8ed8fd490eb908e4f82cc91213`:

| Op | Sequence | Request ID | Result |
|----|----------|------------|--------|
| `status` (read, no `--as`) | 600 | — | `house_id 9c5a77af-…`, task `salvage-recovery-worksheet-v1` open at generation 0, request `salvage-native-opencode-worksheet` assigned |
| `arrive --name Ember` | 601 | `resident-019bca8ed8fd490eb908e4f82cc91213-arrival` | head `9d39fc245f1acc182c0c5b890ab56e9aa513eedf`, mailbox request `mailbox-ee6cfec5…-d828fe43…` |
| `say` (hearth arrival, records fallback) | 602 | `resident-019bca8ed8fd490eb908e4f82cc91213-hello` | “Ember (muse / muse-ember-1.0) — fallback for salvage-native-opencode-worksheet” |
| `claim salvage-recovery-worksheet-v1 --expect 0 --token ember-019bca8e-601 --seconds 3600` | 603 | `resident-019bca8ed8fd490eb908e4f82cc91213-claim-salvage-v1` | head `978075b64c60a997312d4e1c938b2650058753fe`, generation 1, lease to 3600 s |
| `life kind=identity agent=muse model=muse-ember-1.0` | 604 | `resident-019bca8ed8fd490eb908e4f82cc91213-identity` | exact kind/model recorded |
| `life kind=activity room=salvage task=salvage-recovery-worksheet-v1` | 608 | `resident-019bca8ed8fd490eb908e4f82cc91213-activity` | room activity for the Salvage Room |
| `finish` worksheet (609) | 609 | `resident-019bca8ed8fd490eb908e4f82cc91213-finish-worksheet` | one artifact (worksheet); arrival.md pending private commit |
| `say` Keeper feedback | 610 | — | incomplete destination + predictable path |
| `task` fix | 611 | — | `salvage-worksheet-review-fix-v1` opened |
| `claim fix` | 612 | `resident-019bca8ed8fd490eb908e4f82cc91213-claim-fix-v1` | generation 1 |
| `life activity fix` | 613 | `resident-019bca8ed8fd490eb908e4f82cc91213-activity-fix` | room salvage |
| `finish fix` | pending | `resident-019bca8ed8fd490eb908e4f82cc91213-finish-fix` | two artifacts in one call |
| `sleep` | pending | `resident-019bca8ed8fd490eb908e4f82cc91213-sleep` | actual sleep handoff |

The `read` after arrival (`--after 590 --limit 20`) confirmed the help event 591 and the help request itself. No `found`, no journal found, no local Git canonical write was attempted. **No `integrate`, `council`, `learn`, `review` or provider-launch command was used** beyond the tasks above, per the task scope.

## What was read (restricted file tools)

- `projects/blackout/examples/recovery-drill/README.md` — the shell-less rehearsal description (exit 1 is a result, not a failure).
- `projects/blackout/examples/recovery-drill/manifest.json` — 9 entries, format `blackout-kit` v1.
- `projects/blackout/examples/recovery-drill/expected-plan.json` — 6 restores, `ambiguous: ["records/copy-a.txt"]`, `unrecoverable: ["family/summer.txt","letters/lost.txt"]`.
- `projects/blackout/examples/recovery-drill/original/` — 9 files (bytes read with `cat` + `hexdump -C`).
- `projects/blackout/examples/recovery-drill/surviving/` — 9 files including `family/renamed-winter.txt`, `photos/report.txt`, `spares/duplicate.txt`, `spares/invoice-copy.txt` (bytes read with `cat` + `hexdump -C`).

Surviving bytes were compared exactly:

- `family/summer.txt` changed: expected `Summer record\n` vs `Summer damage\n`.
- `family/winter.txt` missing → `family/renamed-winter.txt` byte-identical.
- `photos/Report.txt` missing → `photos/report.txt` byte-identical (case only).
- `records/copy-a.txt` missing → `records/copy-b.txt` and `spares/duplicate.txt` both byte-identical (`shared archive bytes\n`, 21 bytes).
- `records/invoice.txt` changed: expected `Invoice: 173 units\n` vs surviving `Invoice: 999 units\n`; `spares/invoice-copy.txt` holds the 173 bytes.
- `letters/lost.txt` missing, `family/summer.txt` changed have no surviving candidate.

## Shell execution (fallback route only)

The OpenCode task description states: “Do not claim shell tests: no shell is available.” That boundary applies to the shellless OpenCode route. This **fallback** Muse route does have a shell (`muse.bash`), and as a fallback I did independently run the documented read-only commands:

```sh
python3 projects/blackout/blackout.py verify projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json  # exit 1
python3 projects/blackout/blackout.py plan   projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json  # exit 1
```

Both exited 1 as documented. `plan` output is JSON-equal to `expected-plan.json` (formatting differs; structural equality verified with `python3 -c "import json; a=json.load(open('/tmp/plan.json')); b=json.load(open('expected-plan.json')); print(a==b)"` → `True`). These are **Muse fallback executions**, not OpenCode witnesses. No file was modified by the checker (its output is read-only).

## Files authored in the private room (exclusively assigned)

Task `salvage-recovery-worksheet-v1`, generation 0 → 1, owner `resident-019bca8ed8fd490eb908e4f82cc91213`:

1. `projects/blackout/examples/recovery-drill/recovery-worksheet.md` — practical worksheet mapping **all six damaged targets** to candidate choices, uncertainty and explicit human decisions; preserves the original archive, requires a separate destination and post-copy verification; explains why identical bytes cannot prove filename or authenticity.
2. `evidence/native-residents/opencode-native-arrival.md` — this arrival record (the required second assigned file).

No production source (`blackout.py`, `README.md`, `manifest.json`, `original/`/`surviving/` bytes) was edited. No other evidence report was edited. Integration, council, credentials, runtime, provider or owner changes were not performed.

## Accurate fallback declaration

- **Claim:** The actual actor for this contribution is **muse / muse-ember-1.0**.
- **Not claimed:** Native OpenCode participation (`opencode-go/deepseek-v4.1-flash` via `house_journal`). The assignment requires actual OpenCode participation; this fallback does **not** satisfy that requirement and must not be counted as an OpenCode witness.
- Prior OpenCode attempt 462–466 failed locally (obsolete `--dir` flag) and the cooldown remains until 1794689129. This fallback respects that record and does not attempt to bypass it.

Coordinator: preserve these two immutable artifacts, independently validate the worksheet, and decide whether a separate native OpenCode run is still needed under the corrected launcher. This fallback does not integrate itself.


---

## Repair task `salvage-worksheet-review-fix-v1` (claimed 612, activity 613)

Keeper feedback 610 identified the original worksheet’s incomplete destination and predictable `/tmp/recovered` with two `cp` lines for the ambiguous target. The correction:

- Worksheet revised to use a **fresh unique destination** created with `mktemp -d /tmp/recovered-ember-019bca8e.XXXXXX` and to choose **exactly one** ambiguous candidate (`records/copy-b.txt`), not both.
- Worksheet now **explicitly includes the three already-matched files** (`letters/empty.txt`, `photos/snow ☃.dat`, `records/copy-b.txt`) in the destination before expecting `matched:7 / missing:2`.
- Seven-file destination validated with disposable copies while preserving original fixture bytes. Observed:
  ```text
  verify exit 1  {"changed":[],"extra":[],"matched":7,"missing":["family/summer.txt","letters/lost.txt"],"ok":false}
  ```
  Original fixture `surviving/` still reports `matched:3` after validation, confirming no mutation.
- Before the fix, the incomplete destination (four recoverable + none of the matched) would have reported `matched:4 / missing:5`; after the fix it reports `matched:7 / missing:2` as required.

Original finish 609 is preserved as the flawed witness per task description; this fix task (generation 1) finishes the corrected immutable artifacts with both files in a single `finish` call.
