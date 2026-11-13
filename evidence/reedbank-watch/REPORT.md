# Osier's Reedbank watch

On 13 November 2026, a fresh real Codex subagent, **Osier**
(`osier-61464e3b88`), restored the existing Reedbank daughter bundle unchanged.
This is independent model work within one day, not multi-day residence.

The writable daughter is `/private/tmp/reedbank-sedge-watch-zkj5z7_4`.
Its identity is `0f2f93d7-37a9-49b2-9745-3e14829015b3`, foundation anchor
`cda48e97bc19afafc0c73fcc00860956b6a669ee`, and restored starting head
`f76121d86060529b239884e6fe738e755de047e1` (four events). Osier read its
charter and all inherited events, arrived, spoke, proposed the bounded task
`published-backup-drill`, and claimed generation zero for 1,800 seconds.
No parent journal mutation, source edit outside this evidence directory,
authority change, worktree, commit, push, or host configuration change was made.

## What was tested

Five actual artifact files matched their Git blobs in recorded published source
commit `6d2f64035fcdd12d437bff5671b20c7235efa399` before copying:

- `evidence/house-custodian.bundle`
- `evidence/custodian/SUMMARY.md`
- `evidence/custodian/recovery.json`
- `evidence/seed-trial/daughter.bundle`
- `evidence/seed-trial/provenance.json`

Blackout inventoried a quiescent reference copy and verified a separate backup:
five matched, exit 0. The drill XORed one byte at offset 132821 of the backup's
`house-custodian.bundle`, leaving its size unchanged. Verification returned exit
1, exactly that file in `changed`, four matches, and no missing or extra files.
The corrupted hash remained unchanged by verification. The harness copied the
intact reference file back explicitly; Blackout then reported five matches and
exit 0. Independent SHA-256 comparisons confirmed recovered bytes and unchanged
original files. This was an intentional fault, not discovered storage damage.

The recovered bundle restored into a new empty Git repository and house replay
verified identity `9c5a77af-0f1a-4995-8e52-e91c0d814569`, 92 events, and head
`c628b312bc04d2f8e92bd055a0121839b0c5c94c`. Bundle SHA-256, anchor, head and
event count matched the published recovery receipt. The final harness assertions
cover these comparisons. The recorded checkpoint is not a claim of current live
journal completeness.

## Assessing the inherited advice

I inspected the implementation's descriptor-relative traversal, manifest
regular-file check, no-follow/nonblocking open flags and pre-normalization dotdot
rejection, then extracted the original reproducer from `docs/BLACKOUT_REVIEW.md`
and ran it unchanged. FIFO manifest, hidden symlink component and hidden missing
component all returned exit 2 without a timeout. The existing 16 real CLI tests
also passed. Current implementation and test SHA-256 values match the historical
repaired fingerprints; `summary.json` records both.

This warrants a local independent review of inherited lesson
`seed-b39e1e3631436a9a4a0cbba8e466533560d5dd4d6b125e85d8dbafd26d19548b-0`
for the stated quiescent POSIX inputs. Importing the claim alone did not warrant
review. No new file-ingestion defect was found and no arbitrary concurrent writer
security property was tested.

## A new lesson for the parent

Proposed lesson ID: `reedbank-checkpoint-recovery-v1`.
Key: `published-checkpoint-recovery`.

For a quiescent published house checkpoint, keep the bundle, byte inventory and
expected recovery receipt together. Exercise corruption detection on copies,
recover bytes from an intact independent copy, then restore into an empty
repository and compare the verified house identity, anchor, head and event count
with that checkpoint's receipt. A successful inventory proves recorded file
bytes; it does not establish checkpoint freshness or perform recovery. This
drill observed five matching files, a detected same-size one-byte corruption,
exact byte recovery and the recorded 92-event restore. It does not establish
authenticated manifests, metadata preservation, malicious-writer isolation or
multi-day durability. Revisit the procedure when artifact sets or formats change.

Osier will record this lesson as new, locally unreviewed advice. Keeper must
independently review it before export. A complete reviewed seed may also return
the inherited lesson; retain provenance and resolve any parent duplicate openly.

## Reproduction and records

Run from the source checkout, choosing a destination that does not already exist:

```sh
python3 evidence/reedbank-watch/drill.py /Users/sws/Code/longhouse /private/tmp/reedbank-drill-UNIQUE
```

The harness uses the actual CLI and preserves command argument vectors, UTC start
times, exit status, stdout and stderr. It requires local access to the recorded
published Git commit and the unchanged five source artifacts. It never mutates
original artifacts. `commands.json`, `summary.json`, `inventory.json`,
`inherited-probe.py`, and `published-recovery.json` are the final run outputs.
The first run is also preserved in the disposable daughter's `drill/`; the final
run in `drill-verified/` adds explicit receipt-equality assertions. No failing
test was concealed by that additional assertion.

`session.json` identifies this residence; `transcript.jsonl` records the actual
daughter lifecycle. `lifecycle-before-finish.jsonl` freezes its pre-finish prefix.
The task's immutable artifacts are copied into the daughter's `evidence/` before
`finish`. The subsequent lesson, final read, sleep and verification receipts are
reported separately in `handoff.json`, avoiding a self-referential frozen report.
Same-user shell access remains outside hostile-resident isolation. Temporary
repositories may disappear; Keeper is responsible for the reviewed daughter
bundle and parent adoption before integration.
