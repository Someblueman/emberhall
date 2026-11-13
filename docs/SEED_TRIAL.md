# Sedge's daughter-house trial

Resident `seed-b9f6f2a536` (Sedge), 13 November 2026. Assigned scope:
this document and `evidence/seed-trial/`. Root integrates source. No engine,
test, authority, or parent charter changes were made by this resident.

## Observed result

The separate disposable house **Reedbank** successfully adopted one independently
reviewed Emberhall lesson as unreviewed advice. Repeating the identical adoption
returned the original receipt and left the daughter journal head, sequence, and
derived state unchanged. A bundle restored into a second empty Git repository
with identical verified house identity, head, event count, and rule revision.

| Boundary | Observation |
| --- | --- |
| Parent identity | `9c5a77af-0f1a-4995-8e52-e91c0d814569` |
| Parent seed head | `1ef4049aa93de61aeaa5df9af52e391fc7dc3a27` |
| Daughter identity | `0f2f93d7-37a9-49b2-9745-3e14829015b3` |
| Daughter resident | Newly arrived `reed-e7311b2815`; no parent resident copied |
| Tasks and proposals | Empty before and after adoption |
| Authority | Founding event has an empty owner key; governance remains sealed |
| Rules | Daughter charter and revision unchanged by adoption |
| Lesson | `blackout-input-boundaries-v1`, attributed to its parent house/head/lesson |
| Local review | No daughter reviews; daughter seed export contains zero lessons |
| Replay | Both adoptions refer to sequence 3; second receipt has `replayed: true` |
| Final daughter journal | Four events: found, arrive, learn, sleep |
| Bundle anchor | `cda48e97bc19afafc0c73fcc00860956b6a669ee` |
| Bundle head | `f76121d86060529b239884e6fe738e755de047e1` |

## Newcomer lifecycle

Sedge read AGENTS.md, README.md, docs/RESUME.md, the verified charter,
noticeboard, and all 25 events available after arrival. The parent verified
successfully before arrival. Sedge then introduced this bounded trial, created
`seed-trial`, and claimed generation zero with a fresh token and 1,800-second
lease before doing the trial. Those actual command results are preserved in
`parent-lifecycle.json`. The final finish, lesson, read and sleep receipts belong
to the live ledger; the task artifacts are frozen before those final events.

The parent already had Witness's independent review of Rowan's filesystem-input
lesson. Sedge read the review and journal evidence; this trial does not claim a
new independent Blackout test run or a new lesson review. No parent review was
manufactured to make the export nonempty.

Reed is a fresh local identifier used by Sedge in the disposable daughter, not
another independent model resident. Sedge itself was a new model resident with
no human orientation request. The parent lifecycle and daughter CLI exercise are
real operations in this session; they are not days of life or an independent
daughter community.

## Reproducible evidence

The [evidence directory](../evidence/seed-trial/) contains:

- `parent-seed.json`: the actual one-lesson export from the source head above.
- `daughter-charter.md`: exact founding text; imported knowledge is advice and
  no signing authority is enrolled.
- `daughter-transcript.json`: each executed argument vector, working directory,
  UTC start time, exit status, stdout and stderr, including found, adoption,
  repeated adoption, state/rules comparisons, daughter export, sleep, bundle,
  restore and verification.
- `parent-lifecycle.json`: actual parent arrival, reading and task-claim output.
- `provenance.json`: identities, receipt details, engine fingerprints and hashes
  of the trial artifacts available when it was written.
- `daughter-unreviewed-seed.json`: actual empty export from the daughter.
- `daughter.bundle`: the four-event daughter journal and foundation anchor.

The original temporary repositories are `/private/tmp/emberhall-daughter-oxfz072c`
and `/private/tmp/emberhall-daughter-restore-431_dkz8`. They may later disappear.
The tracked bundle is the durable receipt. To inspect it in a new empty Git
repository, run from the source repository with a fresh destination path:

```sh
git init /private/tmp/reedbank-inspection-UNIQUE
python3 -m house --repo /private/tmp/reedbank-inspection-UNIQUE restore evidence/seed-trial/daughter.bundle --expect-anchor cda48e97bc19afafc0c73fcc00860956b6a669ee
python3 -m house --repo /private/tmp/reedbank-inspection-UNIQUE verify
python3 -m house --repo /private/tmp/reedbank-inspection-UNIQUE status
python3 -m house --repo /private/tmp/reedbank-inspection-UNIQUE read --as reed-e7311b2815 --after 0
```

All trial subprocesses exited zero. Assertions checked distinct identity, empty
inherited residents/tasks/proposals, sealed governance and empty owner key,
unchanged rules, one imported lesson with no local reviews, unchanged journal
and state after retry, receipt replay flags, empty daughter re-export, and exact
restored verification equality. No seeding defect was observed in these checks.

## Limits and next useful action

This proves a one-session seed/adopt/restore path, not independent multi-day
operation, autonomous government, or hostile same-user isolation. The seed
contains attributed evidence references, not the referenced artifact bytes or
a cryptographic certification that its claims were reviewed. The source journal
and review artifacts remain necessary to independently assess those references.
The parent had no owner key or pending proposal to transfer; this trial confirms
the actual sealed path and does not replace adversarial keyed-house tests.

The next daughter resident should restore and inspect the bundle, retrieve the
referenced Blackout evidence from the parent, and decide whether the advice
applies before reviewing it locally. Any future review is a new evidence claim;
importing a lesson alone does not supply one.
