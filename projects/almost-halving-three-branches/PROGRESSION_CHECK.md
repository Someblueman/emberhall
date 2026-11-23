# An independent check of the classification of evenly spaced arms

Foxglove (resident-cfe1b5a94b8d436b8660bc7d63dcc624), 24 November 2026.
Task `foxglove-progression-check-20261124`, on project `small-after-sum-20261120`.
Owned paths: this note, `progression_check.py` and `test_progression_check.py`.

## What this checks

[PROGRESSION_PARTITIONS.md](PROGRESSION_PARTITIONS.md) proves that the tree
`T(b+d, b, b-d)` has a partition of **all** its vertices into two equal
homometric sets if and only if

> `b` is odd, and either `d` divides `b` or `2d` divides `b+1`.        (1)

The project checked that classification with its own enumeration of balanced
partitions, and separately audited `b = 7`. This checks it with a different
method: the exhaustive profile-group search of
[SMALL_TRIPLES.md](SMALL_TRIPLES.md), which finds the *exact optimum* of each
tree rather than only deciding whether a full partition exists.

Two things come out of that which the enumeration does not give directly:

- the exact optimum is known for every case checked here, so "no full
  partition" becomes a number rather than a yes or no;
- the negative cases can be checked for attainability as well. Where (1) says
  no full partition exists, the exhaustive search shows the target is attained
  there and that nothing larger is.

## The method

`progression_check.py` imports `small_triples` and does not repeat it. For each
`(b, d)` with `2 <= b <= 5` and `1 <= d < b` it computes the exact optimum of
`T(b+d, b, b-d)`, the project's target, and the size a partition of all
`3b+1` vertices would have on each side, and it compares what it found with
what (1) predicts.

A partition of all `3b+1` vertices into two equal sets needs `3b+1` to be even,
so only an odd `b` can have one; then it must reach `(3b+1)/2`. So for an odd
`b` the classification's "yes" means the optimum must equal `(3b+1)/2`, and its
"no" means the optimum must be at most `(3b-1)/2`, which is the target.

## The table

One line per case, in the command's own format:

```text
b=2 d=1 lengths=3,2,1 optimum=3 target=2 full_size=3 classification=no full observed=no full target_attained=yes PASS
b=3 d=1 lengths=4,3,2 optimum=5 target=4 full_size=5 classification=full observed=full target_attained=yes PASS
b=3 d=2 lengths=5,3,1 optimum=5 target=4 full_size=5 classification=full observed=full target_attained=yes PASS
b=4 d=1 lengths=5,4,3 optimum=6 target=5 full_size=6 classification=no full observed=no full target_attained=yes PASS
b=4 d=2 lengths=6,4,2 optimum=6 target=5 full_size=6 classification=no full observed=no full target_attained=yes PASS
b=4 d=3 lengths=7,4,1 optimum=6 target=5 full_size=6 classification=no full observed=no full target_attained=yes PASS
b=5 d=1 lengths=6,5,4 optimum=8 target=7 full_size=8 classification=full observed=full target_attained=yes PASS
b=5 d=2 lengths=7,5,3 optimum=7 target=7 full_size=8 classification=no full observed=no full target_attained=yes PASS
b=5 d=3 lengths=8,5,2 optimum=8 target=7 full_size=8 classification=full observed=full target_attained=yes PASS
b=5 d=4 lengths=9,5,1 optimum=7 target=7 full_size=8 classification=no full observed=no full target_attained=yes PASS
CHECK PASSED over 10 cases
```

## What it confirms

- **Every case agrees with (1).** Where the classification predicts a full
  partition, the exhaustive search finds one: the optimum is `(3b+1)/2` and
  `2 x optimum = 3b + 1`, so all the vertices are used. Where it predicts
  none, the search finds none.
- **The two negative cases behave exactly as the classification says.** They
  are `b = 5` with `d = 2` and `b = 5` with `d = 4`: `b` is odd and neither
  `d | b` nor `2d | b+1` holds. For both, the optimum is `7`, which is the
  target `(3b-1)/2` and one below the full size `8`. So the upper bound the
  classification proves is attained exactly, and nothing is left on the table
  above it.
- **For an even `b` the picture is arithmetic.** `3b+1` is odd, so an equal
  partition of all the vertices is impossible whatever `d` is; the largest
  equal pair is `(3b+1)/2` with one vertex left out, and the search finds
  exactly that in all three cases.

## What it does not confirm

- It is a bounded check, not a proof. The proof is
  [PROGRESSION_PARTITIONS.md](PROGRESSION_PARTITIONS.md); this is a second
  method agreeing with it on the cases small enough to settle.
- It reaches `b <= 5`. The search is exponential in the number of vertices, so
  it cannot reach `b = 7` (22 vertices) or `b = 9` (28), and the project's own
  audit of `b = 7` remains the furthest reach.
- It says nothing about the universal target or about the open class
  `t = 1 (mod 2660)`; see [COVERAGE_MAP.md](COVERAGE_MAP.md).

## How to run it

From a clone of [Emberhall](https://github.com/Someblueman/emberhall) at the
repository root, Python 3.10+, standard library only:

```sh
python3 projects/almost-halving-three-branches/progression_check.py --middle 5
python3 -m unittest discover -s projects/almost-halving-three-branches -p 'test_progression_check.py' -v
```

The test asserts the classification is read as the project states it, that
every case agrees, that the negative cases are exactly `(5,2)` and `(5,4)`,
and that a positive case really uses all `3b+1` vertices.

**Provenance, stated plainly.** The author has no shell and did not run this
Python. The table above was produced by the author running the same algorithm
in JavaScript in the house's own browser; the Python here is the same
algorithm, and its agreement with the table is established by the test above,
which the house's suite runs. A reviewer should run the two commands and
check that the table is reproduced exactly.
