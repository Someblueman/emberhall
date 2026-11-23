# Run the tests your change can break

Tool: [`scripts/affected_tests.py`](../../scripts/affected_tests.py) (stdlib only).

The full house suite takes about fifteen minutes. Before committing a
change, ask which test modules could actually notice it:

```sh
python3 scripts/affected_tests.py            # list test modules for your working-tree diff
python3 scripts/affected_tests.py --explain  # the same, with the reason per changed path
python3 scripts/affected_tests.py --run      # run exactly that selection
python3 scripts/affected_tests.py --base HEAD~2 --head HEAD   # a committed range instead
```

## How the mapping works

- A changed `tests/test_x.py` runs itself.
- A changed `house/*.py` module runs every test that imports it, directly
  or through other modules (house modules and sibling tests alike; the
  graph is read from the sources with `ast`).
- Any other changed file runs the modules whose source names that path in
  a string literal, then the tests that reach those modules.
- **Anything unmapped means the full suite**: a house module no test
  imports, a deleted house module, shared test support
  (`tests/support.py`, `tests/__init__.py`), or a path nothing names.
  The selector never drops a test; it narrows only when the mapping is
  visible in the source.

Integration is unchanged: `house.integrate.check_plan` still sends
foundation changes to the full suite. This tool is for your own run, so
you find breakage in seconds instead of at integration.

## Checking the selector against history

```sh
python3 scripts/affected_tests.py --replay 40
```

Replay rebuilds the graph at each of the last 40 foundation commits from
git plumbing (no checkout) and reports, per commit, FULL or SUBSET with
module counts, plus misses: a miss is a commit that changed a test the
selector would not have run from that commit's code changes alone.

Recorded 24 November (Tansyfern): 40 foundation commits replayed, 7
FULL, 33 SUBSET, **0 misses**. The first replay found real gaps — tests
importing sibling tests, scripts imported by bare stem
(`import wake_brief`), and files under a directory a test names
(`docs/skills/`) — each is now followed, with a regression test. The
remaining FULL fallbacks are mostly top-level `docs/*.md` pages nothing
names. Honest limit: the median subset was 157 of ~235 modules,
because central house modules are imported almost everywhere. Leaf
changes narrow to 1-9 modules; central ones barely narrow, and one
unmapped path in the diff sends the whole change to FULL. Expect real
savings on leaf work, not on `house/model.py`.

## Limits worth knowing

- Imports made only at runtime through computed names are invisible; a
  module reached that way looks unimported and falls back to FULL, which
  is the safe direction.
- String-literal matching for non-Python paths is substring-based, so it
  can over-select (safe) or miss a path built by joining pieces; a miss
  there means FULL only when nothing at all names the path. If your data
  file is read through a computed path, run the full suite yourself.
- Tests: `python3 -m unittest tests.test_affected_tests` (the selector
  maps its own script to exactly this module).
