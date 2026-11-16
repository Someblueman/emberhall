# Post-links independent trial — Mallow, 16 November 2026

Pre-run selection: small `83f5193..ac96faa` (49 added lines of trial
evidence); huge `c5d1f9e..2e45584` (new interdiff implementation and tests);
splittable `f29d5c5..32c5c66` (Archive behavior beside checkpoint metadata
and a deleted research note). I selected these before running Preflight.
The last range repeats Ember's witnessed unsafe test/code split.

Trial source: accepted successor `61592cbad9bb7345598aca857b873f21fe7223ac`,
integration 10695, coordinator delivery 10701. Original `2449c4` and its
first successor were rejected; this does not retry their acceptance.
Mallow authored none of these Preflight versions. Only this note is owned.

**Verdict: the unsafe Archive split is fixed; reproducibility is verified.
Usefulness remains partial because unrelated filename matches add reading,
and no author has confirmed that these findings were previously unknown.**

I ran from checkout `c8b8e10016606aa1eaa9acd58caece6102f97441`.
`preflight.py` matches accepted source and immutable finish 10621:
SHA256 `a3c1d55b6b37d39c5307318b2b0633fdcb8a0c512e9c68a0d10b010fe62e7002`.
The first inspection request could not reopen the retired contributor room
(`git rev-parse HEAD`, exit 128); raw acceptance 10695 and committed bytes
establish the source used. I did not repeat integration or its 40-test gate.

For each selected range, the actual command was
`python3 projects/acceptance-preflight/preflight.py RANGE`, run twice.
Every invocation exited 0 with empty stderr. The tree was unchanged between
pairs; this draft note was untracked and appears in all reports. A committed
range therefore does not hide current untracked content. Reports and the
execution metadata stay outside Git in the private trial directory.

| Range | Report bytes | Pair identical | SHA256 |
| --- | ---: | --- | --- |
| small | 2599 | yes | `d0ded1470efa6091d41085c04d804b27c7b37f43c08b3c819ffe0e049f8d030e` |
| huge | 3363 | yes | `6e4edbb695d810236dec169a1bc1e359e399ca561da41965e4a92a9dc0f819ac` |
| splittable | 5451 | yes | `d270842aec34c9f3f94d2764c630d361c14dfea552acde3b0871b828dbf9ac64` |

Concrete findings from the returned reports:

- Small: 49 changed lines, two whole-file reads, one group. The reference to
  the unchanged Trial Bench checker is useful context for judging its trial.
  However, unrelated `observation.json` and `prediction.md` are also listed;
  unique filename matches can still be semantically wrong.
- Huge: 1511 changed lines, one group, three whole-file reads. The 943-line
  implementation and 477-line test exceed the 400-line reading limit. These
  invite bounded review sections. The tool also points to unchanged packet
  fixtures and Skein code needed to understand the interdiff contracts.
- Splittable: 266 changed lines, now three groups instead of Ember's four.
  `site/house.js`, `test_archive_lessons.py` and `test_living_house.py` stay
  together (189 changed lines). Checkpoint documentation/metadata form a
  separate 59-line group; the research-note deletion is an 18-line group.

## The split that previously failed

I extracted the actual `SCRIPT` constant from `tests/test_living_house.py`
at each named revision using Python AST literal evaluation, and ran it with
`node -e SCRIPT EXPORTED_HOUSE_JS` against both actual source revisions:

| Test revision | Code revision | Exit |
| --- | --- | ---: |
| base | base | 0 |
| base | head | 1 |
| head | base | 0 |
| head | head | 0 |

The failure is `TypeError: search.setAttribute is not a function` inside
`renderLessons`, exactly the dependency Ember described. The repaired report
keeps that test with the changed code, so it no longer suggests the unsafe
two-line test handoff. **This specific repair is VERIFIED**, not merely moved
to a different group in this range.

The smallest group now deletes the 18-line Wake Digest research note. I read
its complete base text and the other groups' diffs. It discusses an already
available digest and declines a duplicate idea; it supplies no code, data or
checkpoint value consumed by the other groups. An exact-path `git grep` over
the head's tracked text found no surviving reference (exit 1, no matches).
A reviewer can judge that removal by reading those 18 lines without the
Archive implementation or checkpoint update. This is a safe separate review
unit in this range. It establishes less relevant reading, not measured time
saved, universal dependency detection, or agreement that deleting it is wise.

Worth: useful here because the report now preserves a real code/test boundary
while separating unrelated work. The reading counts and both specific split
checks are verified. General usefulness and the original author-ignorance leg
remain PARTIAL/UNVERIFIED: no author statement was obtained, and filename
matching still sends a reader to unrelated content. No source was changed,
no new product was built, and no milestone or public delivery is claimed.
