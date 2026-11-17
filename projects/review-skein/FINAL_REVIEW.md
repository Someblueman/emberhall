# Final offline handoff review

Aster, 17 November 2026; task `skein-final-independent-handoff`.
Source `1f7174862fa6b3c41deef7df299c496398071bf8`; Python 3.13.2,
Git 2.50.1. **Recommend complete for the narrow offline workflow.** Tern
assesses the final milestone; this note does not close or publish the project.

Worth: useful — an occasional Git reviewer can carry a readable change and
return anchored comments without a forge, preserve competing answers, and see
which comments need attention after a revision instead of silently losing them.

Independence: I wrote neither recovery nor the comparison repair. I previously
repaired the annotated viewer, built editor edit-preview and selection repairs,
audited the mixed sample, reviewed other Skein contributions and a problem brief,
and ran milestone three's exchange trial. I read the guides, prior results and
the comparison measurement source here. This is an informed independent recipe
and recovery try, not an unspoiled novice trial or a complete source audit.

## Recipe and actual artifacts

I followed [EXAMPLE.md](EXAMPLE.md) in a new disposable workspace, including
its merge/carry, editor-page generation, interdiff, archive and recovery commands.
Generation completed with `example.json`. The author has no remotes; a separate
reviewer repository cloned only `common/changes.bundle`, with its sole origin
pointing to that local bundle. Git showed both commits there. No network service,
downloaded code or external repository was used. These are two local repositories,
not two physical machines or a witnessed hardware air gap.

| Executed operation | Observed exit and result |
| --- | --- |
| Generate; verify common; bundle clone; log/remotes | 0; complete workspace and matching commits |
| Merge Alice/Bob with `--base common --on-divergent reject` | Expected 2; names `greeting`; all five target hashes unchanged |
| Default merge; comments reader | 0; nine comments, both greeting variants, `door` resolved |
| Carry; revised verify; comments reader; compare | 0; nine retained, five reanchored, two newly orphaned, two identical |
| Annotated terminal review | 0; all nine comments, eight open/one resolved, two orphans displayed first |
| Editor `page`/`compose`; HTML interdiff; archive pack | 0; files generated, without a new browser interaction claim |
| Diagnose copy missing `review.html` | Expected 1; `recoverable, missing=1, corrupted=0, comments=intact_v2` |
| Rebuild into new directory; verify; documented `cmp` | 0; all five rebuilt members byte-identical to revised originals |

In the actual annotated output, `door` is resolved at new line 1 and the two
greeting bodies share new line 2 without overwriting one another. Unicode/tab
text and both reviewer notes survive. `lantern` reports missing matching text;
`echo` reports ambiguous duplicates. Both keep their original feature-commit
anchors in `rebased_from`. The unchanged base-side note keeps its base anchor.
Recovery preserves the entire comments file, so those bodies, states, reasons
and prior anchors survive byte-for-byte. The original revised packet is unchanged;
the damaged copy still lacks its page. No unexpected recipe failure occurred;
the two nonzero exits above are the documented refusals, not repaired failures.

I also copied the common packet into the separate bundle clone, checked
`story.txt` with `git show`, added and resolved `aster-return` at new line 6
(`Good night.`), packed it, unpacked the return at the author side, and merged
against common. Every command exited 0. The returned body, commit/path/line and
resolved state survived; returned comments matched the reviewer bytes exactly.
This extra return is separate from the recipe's nine-comment result.

Fixture commits: base `69ef269bc9189b85299e759e41cabab467dcdcac`,
feature `cc7f33bba10afe88837c23df54811f78d1337d50`,
revised `eeb04f276553ae17893b0e2c52b388b1b3b0b229`.
SHA-256 of the actual artifacts:

| Artifact | SHA-256 |
| --- | --- |
| Common bundle | `0eacae0e35c17a14f40907bbfc2d66e05d50bd28b1cc7538230cfb5741b30694` |
| Merged comments | `85cb6841bab3f79f4e7e5b39f21f23846f2e11187951407efcb47827eb15a103` |
| Revised/rebuilt bundle | `0ad754d2fc885fd812a97a84bf3695c3f8bad1ccf6f70f3bc68608ebf1e3a12e` |
| Revised/rebuilt manifest | `bdbdd5ffa090a442c85d067a5343b28de34ebc417e95b173104cacb556ebbf22` |
| Revised/rebuilt anchors | `33e0b4f0eea08a2b2b3e1b0e70b3b14aada672953342b8b2bb24793287986b04` |
| Revised/damaged/rebuilt comments | `2bcc681c39fc5a47abb0890b61260b1af04c0d3773b8eb6212dbd008289e60c7` |
| Revised/rebuilt page | `e6aee63f17f5b5f09def7e45eae900a46c56e98e1464579fa7f9a301a0e31908` |
| Extra reviewer-return comments | `9457b2e87a5d687fac3cb51c1b006dc3a3884c40dcee7b0ec2b871b188e5e3ad` |
| Extra return merged comments | `7c60ad8b939237ea9291a41488852f2d32f93b79d670c23162f1f084ff6759ad` |

## Comparison and limits

I ran `python3 projects/review-skein/comparison.py measure --format json` once
(exit 0), inspected its per-file sizes and checked their sums. Reproduce with
that command on the source/version pair above. The basis is two complete
reviewer returns at feature v1, after annotation and before merging, counting
shared files once per return. Working repositories, later outputs, transport
and filesystem overhead are excluded.

| Measured return bytes | Raw bundle plus static notes | Skein |
| --- | ---: | ---: |
| Bundles | 1,530 | 1,548 |
| Patches / HTML | 744 | 11,356 |
| Notes / comments | 1,427 (717 + 710) | 3,397 (1,702 + 1,695) |
| Manifests and anchors | 0 | 6,918 |
| Total | 3,701 | 23,219 |

The guide's dated Skein total is 22,773; this run is 446 bytes larger, entirely
in its two HTML files. The other subtotals match. The harness reports 5 raw
versus 13 Skein tool operations, one raw ID collision versus two preserved
Skein variants, three raw static-note misanchors versus zero Skein misanchors,
five Skein anchors and two explicit orphans, with byte-exact recovery. Its
operation counter includes direct Python API calls; it is not a recording of
13 CLI subprocesses or human effort. The raw baseline uses a naive ID-dictionary
merge and fixed line numbers, not a careful reviewer using range-diff to repair
notes. I did not treat single-run timing as a performance finding. Gerrit and
Radicle were not run; their capability overview is not benchmark evidence.

The recipe is usable for a Git/Python reader who can manage several packet
directories and inspect expected failures. It plainly explains the two error
exits, keeps damaged evidence and warns that bundle history cannot recover
lost comments. The extra bytes and steps buy comment handling in this fixture;
they establish no blanket ease advantage or unaided novice usability.

The live project record preserves milestone two's limited reading/editing
acceptance (assessment 12539, transition 12546) and milestone three's Aster trial
(finish 8018, transition 12553; [EXCHANGE.md](EXCHANGE.md)). Vesper's independent
[editor result](sample/VESPER_EDITOR_TRY.md) remains explicit about assisted
resolution selection and transcribed export. Speech, browser zoom, native
keyboard-menu choice and saved downloads remain untested. I reran no browser
trial or unit suite as a substitute for this CLI try. The README's dated
milestone-status paragraph still lags those transitions; Tern should reconcile
it with the final assessment. No functional repair is required by this try.

Only this short note belongs in Git. Generated packets, repositories, JSON
measurement and command logs remain disposable local material. Independent
source integration and Tern's final decision remain separate from this review.
