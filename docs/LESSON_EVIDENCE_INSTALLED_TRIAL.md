# Installed lesson evidence trial: successful replay, room gate open

Hawthorn, run `12d92b94ac584ca4a65748dd0576263b`, 24 November 2026.
The owner readied generation 2 at sequence 43368; claim 43396.
This resident reviewed the feature and repaired its contention tests earlier,
but did not implement the attachment or reader feature.

Installation is verified from canonical `renovation-install` 37953:
source `06bde37491b0d0807c7250afb55cbaa70cf30634`, 1,377 tests.
The exact installation identity, pin, fetch hashes and output are in
`evidence/lesson-evidence-installed-trial/result.json` and adjacent small files.

## What actually ran

Rook's lesson `rook-sixth-two-arm-obstruction-20261124` carries a checker absent
from this fresh assigned source checkout. A new replay directory contained no
files before the installed fixed client fetched `third_word_two_arm.py`.
The client returned 10,320 bytes, SHA-256
`34ba16b72bdb6f2897352e252853a21aa5986af5e73dc928929be1fdd4e7d594`,
matching the lesson metadata. No original-room file was copied.

After inspecting the complete checker (standard library only), from that
replay directory:

```
python3 -I third_word_two_arm.py 1
python3 -I third_word_two_arm.py 7981 --obstruction
```

Both exited zero. The first computes rank 175, nullity 1 and checks the full
shell residual internally. The second emits the residue certificate and
nullity lower bound; its first-arm and second-arm arrays vanish, while the
third-arm array is `[0,-3,-3,0,3,3]`. It does not prove global literal existence.
Independent review 43399 records this limited witness. Its phrase “zero residue
arrays” refers to the first two arms, not the third; the Hearth correction
makes that explicit.

The attached test module was fetched separately. Five selected tests passed:
all-column original-tree breadth-first comparisons, residue certificate,
left identities, rational transfer, and a deliberately damaged kernel control.
The command used `python3 -E -s -m unittest` from the directory containing only
the two fetched files. The complete test module is **not** self-contained:
its known-literal-pair test imports unattached `gap_99_79_23`. That test and the
other unselected tests were not run. The CLI checker itself has no such import.
Fetched source copies are left privately in `replay/`, not duplicated in Git.

## Acceptance remains unmet

This is a successful installed fetch and isolated replay in an empty directory
inside the assigned room. The assigned room itself is a repository checkout.
The task explicitly asks for a genuinely empty resident room; the preceding
Rook witness already distinguished that from an empty directory. This result
does not silently weaken that gate or claim project completion.

Next: provide a resident with a genuinely empty fixed source room through the
controller's approved assignment mechanism, then fetch this standalone checker,
run the two commands and record its review. No new credentials, network access
or relaxed sandbox is needed. The original task remains open for that witness;
the project owner can inspect this bounded progress without repeating the
missing-dependency attempt. If independence excludes prior test contributors,
choose a resident who also did not repair the contention tests.
