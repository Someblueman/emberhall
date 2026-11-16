# Acceptance Preflight

**Before you call the work finished, say what a reader will have to open.**

Acceptance Preflight is one offline command that reads a Git change and reports
the reading and reconstruction load a reviewer would carry:

- which files a reader must open whole, and which are longer than a bounded
  reader's limit;
- how far the change spreads across directories and subsystems, and how the
  churn is concentrated;
- which groups of files nothing links, so they could be handed over separately,
  each with its own load;
- whether behaviour changes are mixed with documentation-only edits or pure
  moves;
- whether changed production files come with a test file in the change;
- which content in the tree would never reach a reviewer.

It makes no claim about how long a review takes. Pull-request size does not
reliably relate to time-to-merge (Kudrjavets, Nagappan & Rastogi, MSR 2022,
arXiv:2203.05045), and a size statistic is not a danger statistic (repowise
says so of its own score). Preflight counts what can be counted and names what
a reader would have to open. The judgement stays with the reader.

## Run it

Inside a Git checkout, with Python 3 and Git, and nothing else:

```sh
python3 preflight.py BASE..HEAD          # a committed range
python3 preflight.py BASE...HEAD         # a range from the merge base
python3 preflight.py REF                 # REF against the working tree
python3 preflight.py                     # uncommitted work
python3 preflight.py BASE..HEAD --json   # the same report as JSON
python3 preflight.py --root /path/to/checkout BASE..HEAD
```

`preflight.py` is a single file with no dependencies outside the standard
library: no network, no model, no account, no installation. Drop it into a
repository and run it, or copy it out of this repository and run it from a
clone.

The same tree and the same command give the same report every time. Nothing in
the output depends on the clock, the environment or the order of files.

## What each signal means

Every rule below is stated exactly, so a reader can disagree with the rule
rather than with a hidden number.

| Signal | The rule |
| --- | --- |
| whole-file read | a new file, a deleted file, or a change touching at least a third of the file's base lines |
| over the reader's limit | the file is longer than `--reader-limit` lines (400 by default), so it cannot be held in one window |
| dispersion | the number of distinct top-level directories and of directories touched |
| churn spread | the share of changed lines in the largest file, and how many files hold 80% of the churn |
| groups nothing links | files joined by a textual mention of one another (an import, a quoted path, a file name); the connected components are the groups |
| mixed documentation and code | some changed file has only blank or comment lines changed, or is a pure move, while another file changes code |
| production file without a test | a changed source file with no changed test file for it: none matched by name (`test_x.py`, `x_test.py`, `x.test.js`, `x.spec.ts`, or a file under `tests/`) and no changed test file that names it (an import, a quoted path or a file name in the changed lines or their nearby context), so a differently-named test still counts |
| content a reviewer would never see | a path named in the change that exists in the tree but is not part of the change, listed once however many changed files name it; untracked files; unstaged edits outside the range |

Links between files are textual mentions in the changed lines and their
nearby context, not a dependency graph. A missing link can hide a real
dependency, so a suggested split is a question, not an instruction.

## What you could act on

The report ends with a numbered list of things an author can act on: a file to
read whole, a group to hand over separately, a production file with no test, a
documented reference the reviewer cannot see, untracked content that would
never arrive.

## Trying it

The tool's own acceptance test, from the idea's brief, is worth stating: a
resident who did not build it runs the command on three real changes — one
believed small, one believed huge, one believed to be a single change spread
over several files — and the tool must name, for each, at least one thing the
author did not know and could act on. Then they take the smallest split the
tool suggests and check that a reviewer can reach the same understanding with
strictly less reading. If the tool only ever says *this diff is big*, if its
suggested splits make the change harder to understand, or if its numbers
cannot be reproduced twice on the same tree, the idea is dropped.

## Tests

```sh
python3 -m unittest discover -s projects/acceptance-preflight -v
```

The unit tests feed the parser and the analysis fixed diffs, so they check the
tool's own judgements. The end-to-end tests build a real temporary Git
repository, run the command over it and check the report, including that two
runs over the same tree are byte-identical.

## Where this came from

The idea is `acceptance-preflight` on the house's idea shelf; its brief was
recorded in the house journal, and the research behind it (six pages read in
full, including the Google small-change guide, repowise's change-risk and
change-records pages, and two studies of review effort) is in
`research/explorations/ea9b1c7230f24a4ab86c9daafa7a24fe.md`. The brief names
the worth question this first version answers: *what will this cost the person
(or the agent) who reads it, and what can I change before I hand it over?*

## Honest limits

- It counts reading load, not comprehension, and it never estimates time.
- "Must be read whole" is a proxy with a stated rule, not a measurement of
  what a reader would actually do.
- Links are textual mentions near the change, not a dependency graph. A
  bare common file name (`index.html`, `summary.json`) can match an
  unrelated path that happens to share the name.
- "Production file without a test" is a file-name convention plus test files
  naming the file, not coverage; a test that exercises a file without naming
  it in the changed lines or their context still looks absent.
- A documentation-only edit is detected from comment markers; a docstring body
  counts as code.
- Binary files are reported as unreadable in a text diff rather than measured.
- Nothing here has been tried on a real change by a person outside this
  repository yet.
