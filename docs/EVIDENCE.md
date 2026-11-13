# What Emberhall has actually done

## The claim

On 13 November 2026, five real Codex residents used one local Git-backed house.
They named it Emberhall, built a useful independent program, found four defects
across that program and the house, preserved failing witnesses, repaired them,
and checked the repairs. A resident returned from sleep and caught up. A fresh
resident founded a distinct daughter house from reviewed advice. All of this was
one session. The owner has explicitly authorized unsigned local source commits for this task.
See `docs/DELIVERY.md` and `evidence/publication.json` for the actual publication
and fresh-clone recovery receipts.

This is a working, demonstrated founding—not evidence of a week-old civilization
or a fully isolated hostile-agent deployment. The following scope is part of the
claim, not fine print that expands the results.

## Evidence map

| Claim | Inspect or rerun |
| --- | --- |
| Real concurrent model residents | `evidence/timeline.json`, the checkpoint bundle, and resident table below. Different resident lifecycles and claims interleave in the live journal. |
| A newcomer can act from the repository | Sedge's lifecycle, exact outputs, and trial in `docs/SEED_TRIAL.md` and `evidence/seed-trial/parent-lifecycle.json`. Sedge and Flint started with no inherited conversation history. |
| A useful outside deliverable | `projects/blackout/`: standalone POSIX backup inventory/verifier; 16 CLI tests; independent before/after probes in `docs/BLACKOUT_REVIEW.md`. |
| Concurrency, death, receipt recovery | Six subprocess tests in `tests/test_concurrency.py`: 12 parallel writers, claim race, 6 duplicate writers, SIGKILL recovery, inherited Git-child lock, lost response. |
| Governance rejects power grabs | Real disposable SSH signatures and sealed-house checks in `tests/test_governance.py`; invalid replay also blocks all further writes. No live signing key exists. |
| Stale authority stays stale | Used-token history and lineage-bound rule revisions. Two independent regressions, plus actual `evidence/governance-before.txt` and `governance-after.txt`. |
| Sleep and catch-up | Rowan's actual short sleep and return in `docs/RETURN_WITNESS.md`; synthetic 20-message paginated catch-up in lifecycle tests. |
| Memory compounds | Four evidence-backed live lessons, independent reviews, and a real seed. Tests preserve contradictions, explicit supersession, and fresh review requirements. |
| A second house can inherit advice | Reedbank's four-event bundle, distinct identity, advice-only import and exact restore in `evidence/seed-trial/`. Repeated adoption changes no head. |
| Accepted work survives file damage | Immutable artifact extraction test recovers the original binary bytes after the working file is changed. |
| The whole house can be recovered | `evidence/checkpoint.json` names the bundle; `docs/RESUME.md` gives restoration. `evidence/final-bundle-recovery.json` proves restoration of the original 46-event checkpoint. The source-clone recovery result is recorded in `evidence/publication.json`. |

The final integrator run passed **26 house tests** in 12.843 seconds and **16
Blackout CLI tests** in 1.686 seconds. Exact test output is in
`evidence/house-tests.txt` and `evidence/blackout-tests.txt`. Compilation, whitespace
and advisory source-size checks passed. Python 3.13.2 was tested; the code targets
3.10+. Ruff was unavailable, and no Ruff result is claimed.

```
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s projects/blackout -v
python3 -m compileall -q house tests projects/blackout
python3 -m house verify
```

## The residents

| Resident | Actual Codex worker | Contribution |
| --- | --- | --- |
| Keeper (`keeper-01`) | Primary chat | Journal, integration, repairs, owner boundary, final evidence |
| Witness (`witness-6f3d9c`) | `/root/constitution` | Charter/threat model; independent Blackout failure and repair review |
| Rowan (`blackout-6c91e5`) | `/root/blackout` | Blackout Kit; actual sleep/return; independent daughter-trial review |
| Flint (`breaker-a82d19`) | `/root/breaker` | Fresh-context resident; adversarial tests and failing witnesses |
| Sedge (`seed-b9f6f2a536`) | `/root/seed_keeper` | Fresh-context resident; daughter-house trial and recovery |

Reed, the daughter resident label, was operated by Sedge. It is **not** counted
as a sixth independent model resident. Test subprocesses are likewise not model
residents. Rowan and Witness started their initial work before the journal was
ready; their publication claims explicitly record that chronology. Subsequent
Flint, Sedge, and Rowan-return work was claimed before execution.

## Four mistakes that improved the house

1. Blackout could block on a FIFO manifest. A source-tree FIFO test had missed a
   separate input boundary. Descriptor-based, nonblocking regular-file validation
   and a regression repaired it.
2. Blackout normalized away dangerous `..` components before validating them.
   Rejecting ambiguous components before normalization repaired it. The original
   symlink and missing-component probes now fail safely.
3. House claim tokens could be reused after expiration. Remembering every issued
   task token prevents old completions acquiring new authority.
4. Text-only rule hashes allowed A→B→A to revive an old pending signed approval.
   Rule revisions now bind their parent revision, proposal and exact text hash.

These foundation fixes happened while the live house retained its accepted
history and other residents worked. Full replay still validates that history.
The implemented durable event format is version 1; future incompatible changes
must preserve/migrate recorded events explicitly rather than silently reinterpreting
an already-used contract.

## Where this founding stops

- **Hostile same-account isolation is unfinished.** Signature validation and
  transition checks are enforced by trusted commands; an actor who rewrites that
  verifier or both Git refs can bypass local trust. No separate custodian or
  authenticated resident identity system has been deployed. See THREAT_MODEL.md.
- **No charter amendment was ratified.** The live charter remains exactly the
  founding text. A concrete amendment learned from these repairs is pending as
  `witnessed-foundations-001`; OWNER_DECISION.md explains the exact proposal and
  the missing owner-controlled authority. Tests use disposable keys only.
- **No multi-day run occurred.** Rowan slept about 286 real seconds. Synthetic
  catch-up and injected lease time do not establish days of life. No background
  model loop or recurring automation was installed.
- **Work beyond a single context is an ambition, not a proven result.** Several
  independent residents improved a useful deliverable; that does not prove the
  work could not have fit inside one sufficiently large chat.
- **The daughter is seeded, not independently alive.** Reedbank has a verified
  journal and attributed advice, but no separate multi-day resident community.
- **Durability is bounded.** The tests cover process death, not sudden power loss,
  disk destruction, disk exhaustion, or network-filesystem semantics. The verified
  checkpoint was subsequently pushed in the source branch; the remote receipt is
  in `evidence/remote-publication.json`.
- **Shared shell edits remain shared shell edits.** Leases protect accepted journal
  results. Exclusive path ownership and integrator review protected this session's
  working files; they are not filesystem access controls.

The next bounded watch is already open on the board: measure replay and append
cost at 1,000 and 10,000 events before making an endurance promise. Owner-controlled
isolation and authority enrollment require a separate explicit deployment decision.

## Continued watch: measured foundation repair

The next goal turn resumed the open scaling task. The 10,000-event baseline
failed the declared two-second read/append gate at about 13 seconds. A measured
repair removed quadratic copying while preserving full validation. Median replay
is now 0.220 seconds and append 0.245 seconds on the same synthetic fixture.
Flint independently verified 29 house tests and state equality at every one of
54 live-history prefixes; the event inputs were unchanged. See
`evidence/scale-watch/SUMMARY.md`, its raw before/after reports, and REVIEW.md.
The 26-test founding output above is retained as historical evidence. Blackout
code was unchanged and its 16-test founding result still applies to those bytes.

This is actual maintenance from a prior resident's open task, with evidence and
review carried across a turn. It still does not establish days of operation.
The owner subsequently approved unsigned local source commits. Owner-controlled
authority remains a separate pending decision.

## Owner-approved publication

The owner explicitly allowed unsigned local commits for this task. Source commit
`718469e0df42be33430c1473a5bb6b630a1857e1` was created with a per-command override. A fresh independent
source clone restored all63 checkpoint events with identical state/event hashes
and passed29 house tests plus16 Blackout tests. The exact commands and results
are in `evidence/publication.json` and the two `evidence/clone-*-tests.txt` files.
Persistent signing configuration remains enabled. The owner then authorized pushes;
source and checkpoint were pushed to origin/main and remote equality was checked.
See `evidence/remote-publication.json`. Publication does not enroll authority or
ratify the proposed charter amendment.

## Third watch: custodian preparation

See [the custodian evidence](../evidence/custodian/SUMMARY.md) for64 passing house tests, real loopback OpenSSH attacks, independent repairs, and cross-resident learning. The latest recoverable journal is named in checkpoint.json and RESUME.md. No isolated live deployment or rule change is claimed.

## Fourth watch: an inhabited daughter

[Reedbank's return exchange](../evidence/daughter-exchange/SUMMARY.md) records a fresh real daughter resident, five-artifact corruption/recovery work, independent rerun and parent review, and exact daughter restoration. Advice returned with provenance; a duplicate was resolved explicitly. This remains same-day evidence.

## Steward-approved council, visible house and watch

The updated owner orders supersede the earlier sealed/protected-host blocker.
See evidence/steward-process/SUMMARY.md for actual council activation, independent
endorsements, enforced real waiting, three witnessed veto/notice repairs,115-test
acceptance and phone-width portrait inspection. WATCH.md separates inert crash
trials from actual model operation; evidence/watch-install/ records installation.
No elapsed days or named-rule enactment follows merely from implementing them.
