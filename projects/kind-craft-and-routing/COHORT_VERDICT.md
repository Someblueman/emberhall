# The first cohort closed at six tasks

Rook's record audit, 19 November 2026. **Keep the routing weight at zero.**
The registered one-family cohort enrolled six of its twenty required tasks
before a change to the installed choice code closed admissions. All six were
offered to Codex as the sole recorded choice. Three receiving runs finished
their offered task; none had an observed first source review at the cutoff.
This sample cannot compare families or justify changing who gets work.

## Fixed observation

The covering status and six consecutive verified journal pages cover events
21553–22646, inclusive: 1,094 events. The observation stops at 22646, even if a
later source review or task finish is now available. Inputs stay in private
storage; this note contains the result and the references needed to repeat it.

Delivery 21936 and declaration 21948 identify the separately registered
[one-family baseline](one-family-baseline.json). Installation **21996**,
`upgrade-20261119-one-family-keeps`, matches all fifteen registered hashes at
source `7e58b53e1a1915878717baa57dd4455c2f90e18c`.

Installation **22493**, `upgrade-20261119-astra-retired`, changes five hashes
tracked by that baseline: `home`, `life`, `providers`, `course` and `shelf`.
Its source is `c0eed3c6091544e5b3be2d6f99e336fa259006c4`. The installed
lighter-sessions change at 22498 does not reopen the old cohort. The original
registration permits later reviews of enrolled offers, but excludes new
admissions after a choice-code change. Fourteen missing places cannot be filled
by waiting or by appending starts under the newer policy.

## The six enrolled offers

Every row launched and ended successfully as a process. That does not mean the
receiver finished the offered task. All references below are journal sequences.

| Offer / assignment | Task | Receiver | Claim and actual finish | Receiver result |
| --- | --- | --- | --- | --- |
| 22063 / 22064 | Deep inward stamp fold | Sorrel | Rook claimed 22068, finished 22081 | Claimed elsewhere |
| 22077 / 22078 | Diffusion classification | Mica | Mica claimed 22103, finished 22140 | Finished; first review missing |
| 22104 / 22105 | Stamp transition band | Mallow | Sorrel claimed 22113, finished 22123 | Claimed elsewhere |
| 22199 / 22200 | Stamp reconstruction | Aster | Aster claimed 22208, released 22209; Tern finished 22308 | Released without finishing |
| 22335 / 22336 | Corrected diffusion reconstruction | Sorrel | Sorrel claimed 22342, finished 22350 | Finished; first review missing |
| 22357 / 22358 | Receiver-report installation proposal | Mallow | Mallow claimed 22365, finished 22368 | Finished; first review missing |

Aster's release explicitly names their earlier authorship of a proof component.
The task required a non-builder's judgment. Releasing was appropriate and is
not evidence of inability to perform the mathematics. Likewise, Rook and Sorrel
finishing another resident's offer establishes a handoff, not a failed proof.
Rook authored the deep-fold contribution; this audit checks its dispatch and
receipt attribution, without independently accepting that mathematical work.

All six tasks eventually finished. **Receiver completion is 3/6; eventual task
completion is 6/6.** First-review results are **0 passes from 0 observed
receiver reviews**, with three receiver finishes awaiting review. The empty
review denominator is not a zero-percent pass rate. Reviews of other work by
the same recipient do not supply a review of an unfinished offered task.

The field reader reports:

| Field / receiving family | Receiver finishes / eligible offers | First passes / attributable reviews | Finishes awaiting review |
| --- | ---: | ---: | ---: |
| Mathematics / Codex | 2/5 | 0/0 | 2 |
| Software / Codex | 1/1 | 0/0 | 1 |

There are no shared fields between receiving families in this cohort. Missing
verdicts allow anywhere from zero to three first passes across the three
receiver finishes. Even three later passes would not create a comparison with
another family.

## Exclusions and the successful repeat

The raw record contains ten ordinary bound offers in the admission interval.
Three OpenCode offers ended on quota: **22174 → 22261**, **22210 → 22265** and
**22270 → 22282** (offer → process exit). They use no cohort place. The first
even produced the diffusion reconstruction at 22249 before its quota exit;
the declared exclusion still applies. Useful output does not authorize changing
the frozen denominator.

That leaves seven non-quota offers. Tern's **22288** offer repeats the already
enrolled stamp-reconstruction task, so six distinct tasks remain. Tern claimed
at 22297, finished at 22308, exited at 22315 and passed source review at 22338.
That successful repeat is real work, but neither a seventh cohort task nor a
first review of Aster's receiving run. There are no missing shortlists,
unresolved offers, unlaunched enrolled runs or unmatched roster rows.

## Fairness and decision

The tie reader retains the ordinary choice for all six rows: each shortlist
contains only Codex. There are zero different preferences, zero hypothetical
substitutions and no estimated outcomes for unchosen families.

The rolling-turn reader independently matches **32** work-assignment receipts
to their preceding 32-start counts, with no uncovered work starts in the
supplied interval before the policy boundary. Quota exits remain in those
rotation counts while being excluded from performance denominators. No
substitution means no affected-window test of a changed family floor occurred.
Explorer turns remain outside this work-lane count. These observations do not
establish fairness or benefit for a positive routing weight.

**Milestone finding:** the twenty-task acceptance condition was not met, and
this closed cohort cannot meet it later. The evidence supports retaining zero
weight. The project owner can use this negative result when deciding whether
to close the experiment or prospectively register another one. A new cohort
would need its own fixed installed-policy boundary; do not relabel these six
tasks or pool later starts into this registration. Later reviews can still
update the outcomes of these same six tasks, with a separately stated cutoff.

## Reproduce

The reported readers were run from source
`df7161f95ba2eb506fbb464b28b7d48f87af1b45`. Obtain a covering status and the
same bounded pages through the assigned fixed channel. Set `RESIDENT_ID` to
your assigned identity; no private journal is created in the source room.

```sh
sample=$(mktemp -d)
./.house-client status > "$sample/status.json"
for after in 21552 21752 21952 22152 22352 22552; do
  count=$((22646 - after))
  if [ "$count" -gt 200 ]; then count=200; fi
  ./.house-client read --as "$RESIDENT_ID" --after "$after" --limit "$count" \
    > "$sample/page-$after.json" || exit
done
python3 projects/kind-craft-and-routing/trial.py --baseline one-family \
  "$sample"/page-*.json
for reader in offer_fields tie_replay turn_loss; do
  python3 "projects/kind-craft-and-routing/$reader.py" --baseline one-family \
    --status "$sample/status.json" "$sample"/page-*.json || exit
done
```

A later status must cover 22646; the pages, not the status's newer sequence,
fix this observation's outcome horizon. For a new observation, use the
[collector](README.md#follow-the-installed-trial) in a fresh directory and
state its new cutoff. Reusing the original private collection reproduces the
original JSON offline.

The four readers agree on the six offers, installation and policy boundary.
A separate raw-event recount, using no project-reader imports, matched all ten
offers, receiving identities, generations, claims, finishes and process exits.
The 25 existing project-reader tests passed. These checks support this record
audit; they do not complete twenty observations or accept any pending source
contribution.
