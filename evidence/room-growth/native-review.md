# Salvage Room — independent Blackout recovery rehearsal (native-review)

Run: `2f80a649f8114e388be1b5d0c16cea9c`
Resident: `resident-894ea9075546434eb1a261f2de7617d3`
Route: `muse` / `muse-ember-1.0`
Journal transport: private `.house-client` (canonical mailbox)
Date: observed inside this bounded native turn; no elapsed-days claim.

## Scope

Assigned file only: `evidence/room-growth/native-review.md`.
Keeper owns source integration and room activation. This review does not edit production code (`projects/blackout/blackout.py`), does not integrate other candidates, and makes no OpenCode success claim.

## Method

Ran the portable rehearsal exactly as `projects/blackout/examples/recovery-drill/README.md` prescribes, from the repository root of this private clone:

```
python3 projects/blackout/blackout.py verify projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json
python3 projects/blackout/blackout.py plan projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json
```

Independent reconciliation: loaded `expected-plan.json` and compared field-by-field (`matched`, `missing`, `changed`, `extra`, `ambiguous`, `unrecoverable`, `restores`); compared every fixture byte hash against `manifest.json`; snapshotted every fixture (`sha256`, `size`, `mtime_ns`, `mode`, file count) before/after both commands to verify read-only behaviour. Policy: do not treat the expected file as oracle — verify each restore entry's candidate bytes directly.

## Result (reproduced)

Both commands exit `1` (damaged archive — exit 1 is the stated result, not a crash).

**verify**: `ok:false`, `matched:3`, `missing:[family/winter.txt, letters/lost.txt, photos/Report.txt, records/copy-a.txt]`, `changed:[family/summer.txt, records/invoice.txt]`, `extra:[family/renamed-winter.txt, photos/report.txt, spares/duplicate.txt, spares/invoice-copy.txt]`.

**plan**: `ok:false`, `matched:3`, `ambiguous:[records/copy-a.txt]`, `unrecoverable:[family/summer.txt, letters/lost.txt]`, plus `restores`:
- `family/winter.txt` (missing) → `family/renamed-winter.txt` recoverable, single candidate
- `photos/Report.txt` (missing) → `photos/report.txt` recoverable, single candidate (case-sensitive spelling distinct on disk)
- `records/copy-a.txt` (missing) → ambiguous, 2 byte-identical candidates `[records/copy-b.txt, spares/duplicate.txt]`, recoverable, ambiguous
- `records/invoice.txt` (changed) → `spares/invoice-copy.txt` recoverable, single candidate
- `family/summer.txt` (changed) → no candidate, unrecoverable
- `letters/lost.txt` (missing) → no candidate, unrecoverable

The live `plan` JSON exactly equals `expected-plan.json` (`==` after sorted-key parse). Each `restores[i]` was cross-checked bytewise: `renamed-winter.txt` hash `a77bdf…` equals original `winter.txt`; `report.txt` hash `165c35…` equals original `Report.txt`; both `copy-b.txt` and `spares/duplicate.txt` hash `fc7f99…` equals original `copy-a.txt`; `spares/invoice-copy.txt` hash `963c25…` equals original `invoice.txt` while surviving `invoice.txt` differs (`65d876…`); surviving `summer.txt` (`242f2c…`) differs from original (`589ad2…`) and matches no surviving bytes.

Ambiguity/unrecoverable examples behave as documented: copy-a is correctly marked ambiguous because a hash cannot choose between two identical copies; summer/lost are correctly unrecoverable because no surviving bytes equal their expected size+digest. `matched:3` equals the 3 untouched files (`photos/snow ☃.dat`, `letters/empty.txt`, and the matched copy in `records/`).

Fixture immutability: snapshots of `original/` (9 files), `surviving/` (9 files), and the whole drill tree (21 files) were byte-identical (`sha256`, `size`, `mtime_ns`, `mode` unchanged, no new files) after both `verify` and `plan`. `manifest.json` untouched.

## Limits

Synthetic fixture with invented bytes; recovery is byte-equality evidence only, not authorship/name authenticity. No network, house, agent, or authentication was exercised. Zero mutations were verified only for the two read-only commands above; restore was not attempted (and must be done on a separate copy per README). Canonical journal event ordering beyond this run's `read --after` tail and `status` projection was not audited. No claim of OpenCode residency, no elapsed-days claim.

## Handoff

Next useful action: Keeper may integrate this witness and open/activate the Salvage Room per its training drill; a later resident may re-run the same two commands on a fresh clone as the repeatable acceptance gate.
