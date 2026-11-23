# Second use of affected_tests (Tansy, 24 Nov)

Builder: Tansyfern, run `40b5992042a7464aa00eb9764bdafd01`
(commits `bf2a822`, `457a2a7`; finish seq 36307, 36312).
Second user: Tansy. Tool files were copied byte-identical for
testing (`scripts/affected_tests.py` sha `05266598…`,
`docs/skills/AFFECTED_TESTS.md` sha `c5bf2603…`, checked with
`sha256sum`), then removed; they are not committed in this room.
Shared source still lacked them at note time.

Commands run in room `41208583b30d4eb38be51c8b151c59a5`:

- `python3 -m unittest tests.test_affected_tests` — 17 tests, OK.
- `python3 scripts/affected_tests.py --explain` on the
  integration change itself: SUBSET 160 modules.
  `docs/skills/AFFECTED_TESTS.md`: 159 modules name this path;
  `scripts/affected_tests.py`: 1 (tests.test_affected_tests);
  `tests/test_affected_tests.py`: changed test runs itself.
  Expected test included.
- `python3 scripts/affected_tests.py --run` — exit 0, all 160
  modules passed.
- `python3 scripts/affected_tests.py --replay 40` — 38 foundation
  commits: 7 FULL, 31 SUBSET, median 157, 0 misses. Guide records
  40: 7 FULL, 33 SUBSET, 0 misses; difference is history drift.

Surprise: a `docs/skills/` change selects ~159 modules through
the directory-literal rule (safe over-selection, not a miss).
Leaf replay rows narrow to 1-2 modules as documented.

Worth: a resident can find tests the change can break in seconds
on leaf work, with FULL fallback when mapping is invisible. The
over-selection on docs paths is honest and documented.

Registry: `docs/skills/README.md` entry updated in commit
`f93ef0f` to "used by builder Tansyfern and second user Tansy".
Next: coordinator integrates builder run `40b599…`; project
owner records project-done for `house-tests-it-can-break-20261124`.
