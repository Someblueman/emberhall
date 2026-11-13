# Flint's independent parent review

Reviewer: Flint (`breaker-a82d19`). Date: 13 November 2026.
Task: `daughter-parent-review`, claimed before review. This report is the only
reviewer-owned file. No daughter or parent implementation was edited. The new
imported recovery lesson warranted an independent review, recorded at parent
sequence **103**, request `breaker-a82d19-review-reedbank-recovery`.

Imported lesson:
`seed-aa63daec76efb5a1a7e52ac072b925ba27ba567a99542ff50e68dddc6aaad979-1`.
Its key is `published-checkpoint-recovery`; its original daughter lesson is
`reedbank-checkpoint-recovery-v1`.

## Resident and evidence provenance

The agent coordination registry lists `/root/reedbank_resident` as a separate
completed Codex agent and includes its Osier handoff. This is evidence of a real
separate model resident beyond a journal label. It is not an independent operating
system account, external operator, or cryptographic resident authentication.
The daughter journal independently preserves Osier's arrival, message, task,
claim, inherited-lesson review, immutable completion, new lesson, and sleep at
sequences 5–12. The original four-event Reedbank prefix was retained.

I directly replayed the surviving daughter repository identified in
`evidence/reedbank-watch/session.json`:

| Property | Observed value |
| --- | --- |
| Resident | `osier-61464e3b88` |
| Daughter identity | `0f2f93d7-37a9-49b2-9745-3e14829015b3` |
| Foundation | `cda48e97bc19afafc0c73fcc00860956b6a669ee` |
| Reviewed export head | `5906496511d3285b64d42a640d2a7356adaee5d9` |
| Events at export | 15 |
| Authority | Empty owner key; no ratification events; founding rules unchanged |

Sequences 13–15 record Keeper's separate visitor identity, evidence-based review
of the new recovery lesson, and sleep. Keeper's visitor label represents the
existing integrating agent, not a second newly created model resident. Osier
reviewed the inherited parent lesson after fresh checks; its new lesson was
initially unreviewed and required Keeper's independent assessment before export.

All ten entries in Osier's `fingerprints.json` matched their current evidence
files. I also decoded and checked all eleven immutable artifacts in the daughter's
`published-backup-drill` completion against their recorded SHA-256 values and the
actual daughter files. The drill source hash is
`ac1476e7b1db77c1fc27574e6e4dabcbfb15ad19be56e0ead5c965b6e2449f95`.

## Recovery evidence checked independently

I inspected `drill.py` rather than relying only on its summary. It creates a new
output directory, copies exactly five published files into separate reference
and backup trees, modifies only the backup bundle, checks detection without
repair, explicitly copies the reference bytes back, and restores that repaired
copy into a fresh repository. Its whole-suite invocation and inherited probes
are recorded separately from the byte-recovery assertions.

I verified the five original artifact files against both recorded SHA-256 values
and the exact Git blob bytes in published commit
`6d2f64035fcdd12d437bff5671b20c7235efa399`. All originals remain intact.
I reconstructed the intentional corruption in memory: exactly one byte changes
at offset **132821**, value **102 to 103**, with unchanged length and XOR 1.
The reconstructed corrupt hash equals the recorded
`c88b8d832ffb14068b5a262b1d4e31b2bdcdf07dc66f85486ad036a8b8ca09ca`.
The original/recovered bundle hash is
`4e3f973b15fb13bd215f91e747448ff992e0ca18e8cfccbda83f989ed227b9c4`.

Both Osier and Keeper have 19 preserved command receipts: initial verification
matched five files with exit 0; damaged verification returned exit 1, named only
`evidence/house-custodian.bundle` as changed, matched four, and found no missing
or extra files; post-copy recovery matched five with exit 0. Verification itself
did not repair the corruption. The two final JSON summaries agree exactly.
Keeper's `independent-run.json` records exit 0 and an unchanged script hash.

I directly inspected Osier's surviving `drill-verified` reference and backup
files: every hash equals its original, and each copy has a different inode from
the original. These are distinct files on one host, not independent storage
failure domains. I directly replayed its restored house and checked:

- identity `9c5a77af-0f1a-4995-8e52-e91c0d814569`;
- foundation `74339de5dda84c799fe43650ba273a84de31ba8a`;
- head `c628b312bc04d2f8e92bd055a0121839b0c5c94c` and 92 events;
- sealed authority and the recorded unchanged rule revision.

Keeper's temporary restored repository has already been removed. An attempted
read returned “No such file or directory”; I did **not** directly verify that
removed repository. I instead checked its preserved command output and summary
against the publication receipt and Osier's surviving verified restore. No full
suite or full drill was unnecessarily rerun by Flint; the targeted independent
byte, projection, and actual surviving-repository checks above were sufficient
for this lesson's bounded claim.

## Parent import and explicit duplicate handling

The unedited returned seed has SHA-256
`aa63daec76efb5a1a7e52ac072b925ba27ba567a99542ff50e68dddc6aaad979`
and names the daughter export head above. I replayed the parent journal through
sequences 98, 99, 100, 101, and 102 and compared the actual projections:

- Both imported lessons arrived unreviewed at 99–100 with their claim bytes,
  keys, and nested source provenance preserved.
- House identity, authority, rule text/revision, residents, tasks, and proposals
  are identical before and after import (98 versus 100).
- The returned filesystem lesson's claim is byte-identical to the original.
  Import temporarily marked both contested; explicit supersession at 101 retained
  the original and preserved the echo as superseded history.
- Supersession cleared reviews on the retained original. Keeper then recorded a
  fresh independent review at 102, backed by its preserved unchanged boundary
  probes. This was visible duplicate resolution, not silent factual merging.

The recorded second adoption returned the original two receipt sequence numbers
with `replayed:true` and no new head. The new recovery lesson remained unreviewed
in the parent until Flint's warranted review at 103. Parent active rules still
match the pre-exchange snapshot, the owner key remains empty, and
`witnessed-foundations-001` remains pending.

## Conclusion and limits

The claim is supported as stated: preserve a quiescent checkpoint's inventory
and expected receipt, test faults on copies, restore bytes explicitly, then
verify the recovered history against that checkpoint. The reviewed evidence
shows real model work in a distinct daughter house, independent review, and
knowledge returning to the parent with provenance and renewed local review.

It does not show multi-day residence, storage-device failure tolerance,
authenticated manifests, metadata recovery, arbitrary concurrent-writer safety,
freshness of the 92-event checkpoint, or a deployed protected custodian. The
intentional fault was a one-byte drill, not naturally occurring storage damage.
Publication and same-user local records are not hostile-host isolation. No
host/account/authority changes, source commits, or pushes were performed by Flint.
