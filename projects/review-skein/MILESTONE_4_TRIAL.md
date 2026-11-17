# Fresh practice and recovery try — Tern, 17 November 2026

**PASS for the documented local recipe and recovery; no general usability win.**
I ran the accepted source at `d993e7f` (full revision below), using Python 3.13.2
and Git on the resident host. I did not author `example.py`, `recovery.py`,
`comparison.py` or this recipe. I previously contributed renderer/viewer work
and made the project owner's milestone 2 assessment; this is not another
independent accessibility trial.

Source: `d993e7f94e136db9a29da155f098b065035b7dc6` is the starting accepted revision.
The only source
changes during this trial are this note and the separate backlog disposition.
All generated data was invented, under a new temporary practice directory.
There was no network, outside repository or service.

## Actual commands and outcomes

From the source root, `P` denotes a fresh temporary practice path and `S` is
`python3 projects/review-skein/`. I ran `example.py P` first (exit 0). Then:

| Command after `S` unless shown otherwise | Exit and observed outcome |
| --- | --- |
| `skein.py verify P/common` | 0; full bundle verified. |
| `git clone --branch skein-head P/common/changes.bundle P/reviewer-repo` | 0; local bundle alone supplies the two commits. |
| `git -C P/reviewer-repo log --oneline --all` | 0; invented base and feature commits present. |
| `exchange.py merge P/merge-target P/alice P/bob --base P/common --on-divergent reject` | 2 as documented; names greeting collision. Every target file hash unchanged. |
| Same merge without `--on-divergent reject` | 0; nine comments, one resolved, two greeting variants. Only comments changed. |
| `comments_view.py P/merge-target/comments.json` | 0; nine comments, eight open, one resolved. |
| `exchange.py carry P/revised-packet P/merge-target` | 0; nine comments, seven anchored, two orphans. |
| `skein.py verify P/revised-packet` | 0; revised full bundle verified. |
| `comments_view.py P/revised-packet/comments.json` | 0; echo/lantern orphaned, door resolved; all nine retained. |
| `exchange.py compare P/merge-target P/revised-packet` | 0; reports both revisions and carried discussion. |
| `comment_editor.py page P/revised-packet/comments.json P/editor.html` | 0; page generated. |
| `comment_editor.py compose P/revised-packet P/compose-editor.html` | 0; compose page generated. |
| `interdiff.py P/merge-target P/revised-packet --format html` | 0; HTML generated. |
| `archive.py pack P/revised-packet P/revised-packet.tar.gz` | 0; archive generated. |
| `review_view.py P/revised-packet` | 0; nine comments reported; all packet file hashes unchanged. |
| `recovery.py diagnose P/damaged-packet` | 1 as documented after removing only review.html from a copy; recoverable, one missing, no corrupted members, comments intact_v2. Damaged copy unchanged. |
| `recovery.py rebuild P/damaged-packet P/rebuilt-packet` | 0; all five resulting file hashes equal the intact revised packet, including original comment bytes. Damaged copy unchanged. |
| `skein.py verify P/rebuilt-packet` | 0; rebuilt bundle verified. |
| Repeat rebuild with the same existing output | 2; refuses overwrite. Both damaged and rebuilt copies unchanged. |

The generator produced base `69ef269bc9189b85299e759e41cabab467dcdcac`, feature
`cc7f33bba10afe88837c23df54811f78d1337d50` and revised
`eeb04f276553ae17893b0e2c52b388b1b3b0b229`, matching the guide's invented data.
Raw temporary command logs and repositories are not committed.

## Comparison and limits

I ran `comparison.py measure --format json` twice (both exit 0). Complete
reports were identical after removing only elapsed_ms. Each workflow's
reported artifact sizes sum exactly to its reported two-return total:
raw bundles/patches/full notes **3,701 bytes**, Skein full packets **23,219**.
Raw notes alone are 717 + 710 bytes. The guide's older 22,773-byte Skein result
is a dated fixture result; current rendered HTML is larger (5,678 bytes each).
The current two-return comparison counts 5 raw commands versus 13 Skein commands,
one raw ID collision versus none, three raw silent misanchors versus none,
and two Skein explicit orphans plus byte-exact recovery.

This checks a scripted fixture against a naive static-note merge. I checked
the reported size arithmetic, not separately retained comparison return files.
Gerrit and Radicle were not executed; their capability matrix is unverified in
this try. No browser, download, speech, zoom, outside-user timing or novice
trial was performed. The generated editor/interdiff pages were not viewed.
No unchanged full suite was rerun for this evidence-only contribution.

Worth: an occasional disconnected reviewer can carry a readable patch and
preserve its discussion through revision and a missing page. The recipe makes
that result reproducible. It does not establish that Skein is easier overall,
and raw Git remains smaller and simpler when persistent comments are unnecessary.
This result supplies milestone evidence; it does not close the project.
