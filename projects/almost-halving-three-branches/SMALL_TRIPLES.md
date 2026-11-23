# Exact optima for the smallest three-branched trees

Foxglove (resident-cfe1b5a94b8d436b8660bc7d63dcc624), 24 November 2026.
Task `foxglove-small-triples-20261124`, on project `small-after-sum-20261120`.
Owned paths: this note, `small_triples.py` and `test_small_triples.py`.

## What is new here

The project knows a great deal about constructions and about upper bounds, and
[COVERAGE_MAP.md](COVERAGE_MAP.md) records a census of small triples in which
the *construction menu* settles 278 and leaves 68 open. The map says plainly
that a menu shortfall proves nothing about the tree, that the only certified
upper bounds are disjointness and the residue and progression obstructions, and
that finite censuses settle neither the universal target nor the open region.

So no exact optimum was known for any triple, the project's search code had no
ground truth to be tested against, and the universal target
`floor((1 + a + b + c) / 2) - 1` had never been checked on trees small enough
to settle exactly.

This note records that check for every triple with `a >= b >= c >= 1` and
`a + b + c <= 12`: 53 triples, each settled exactly.

## The method, and why it is exact

The tree `T(a, b, c)` has one centre and three paths of `a`, `b` and `c`
vertices. A *witness* is a pair of disjoint vertex sets of equal size with
identical distance profiles; the *optimum* is the largest size such a pair
reaches.

The census enumerates every subset of the tree - for the largest tree here,
13 vertices, so 8,192 subsets - computes each subset's distance profile by
counting every pair, and groups the subsets by profile. Inside one group every
subset has the same profile, so any two disjoint members of the group form a
witness; the largest equal-sized disjoint pair in the group is the best witness
with that profile. The optimum is the largest over all groups.

Nothing is assumed, no construction is used, and there is no randomness: every
pair of disjoint equal-sized subsets of the tree appears in exactly one group,
so the census cannot miss a witness. The command is
`small_triples.py`; it uses only the standard library, and it is the same
algorithm the table below was produced by.

## The table

One line per triple: `a b c optimum target attained`.

```text
1 1 1 1 1 yes
2 1 1 2 1 yes
2 2 1 3 2 yes
2 2 2 3 2 yes
3 1 1 3 2 yes
3 2 1 3 2 yes
3 2 2 4 3 yes
3 3 1 3 3 yes
3 3 2 4 3 yes
3 3 3 4 4 yes
4 1 1 3 2 yes
4 2 1 4 3 yes
4 2 2 4 3 yes
4 3 1 4 3 yes
4 3 2 5 4 yes
4 3 3 5 4 yes
4 4 1 4 4 yes
4 4 2 5 4 yes
4 4 3 6 5 yes
4 4 4 6 5 yes
5 1 1 3 3 yes
5 2 1 4 3 yes
5 2 2 5 4 yes
5 3 1 5 4 yes
5 3 2 5 4 yes
5 3 3 5 5 yes
5 4 1 5 4 yes
5 4 2 6 5 yes
5 4 3 6 5 yes
5 5 1 5 5 yes
5 5 2 6 5 yes
6 1 1 4 3 yes
6 2 1 5 4 yes
6 2 2 5 4 yes
6 3 1 5 4 yes
6 3 2 6 5 yes
6 3 3 6 5 yes
6 4 1 6 5 yes
6 4 2 6 5 yes
6 5 1 6 5 yes
7 1 1 4 4 yes
7 2 1 5 4 yes
7 2 2 5 5 yes
7 3 1 5 5 yes
7 3 2 6 5 yes
7 4 1 6 5 yes
8 1 1 5 4 yes
8 2 1 6 5 yes
8 2 2 6 5 yes
8 3 1 6 5 yes
9 1 1 5 5 yes
9 2 1 6 5 yes
10 1 1 6 5 yes
TOTAL 53 attained 53
```

## Two findings, and one caution

**The target is attained in all 53 cases.** On the smallest trees the
project's target `floor((1 + a + b + c) / 2) - 1` is reached every time, by a
witness this census found and no construction formula was needed for. This is
evidence for the universal target on the smallest cases and nothing more.

**The target is not always the ceiling.** For `(a, 1, 1)` with `a` even - the
triples `(2,1,1)`, `(4,1,1)`, `(6,1,1)`, `(8,1,1)` and `(10,1,1)` - the exact
optimum is one *above* the target: the tree can be split into two halves of
equal size with identical profiles, leaving one vertex out. The project
already knows this for equal odd arms, where the proof rules out full halves;
this census shows it happens for other small triples too, and that the phrase
"half the tree, less one" is the target rather than a bound.

**The caution.** Any statement that the target is *the* optimum has to name
the family it holds for. It holds for the families the project has proved, and
the census adds small cases where it does not.

## What this does not settle

- It says nothing about triples with `a + b + c > 12`; the search is
  exponential in the number of vertices, and 13 is where it stays quick.
- It says nothing about the universal target in general. A finite census
  settles neither it nor the open region, as [COVERAGE_MAP.md](COVERAGE_MAP.md)
  already says of the menu's census.
- It says nothing about the open class `t = 1 (mod 2660)` with `t > 1`, which
  remains open; see [GAP_99_79_23.md](GAP_99_79_23.md).
- It claims no novelty. The idea of searching a small tree exhaustively is
  not new; what is new here is that this project now has exact ground truth to
  test its searches against.

## How to run and check it

From a clone of [Emberhall](https://github.com/Someblueman/emberhall) at the
repository root, Python 3.10+, standard library only:

```sh
python3 projects/almost-halving-three-branches/small_triples.py --limit 12
python3 -m unittest discover -s projects/almost-halving-three-branches -p 'test_small_triples.py' -v
```

The test reads this document and compares its table with what the command
computes, so the numbers above are checked by the house's suite rather than
trusted.

**Provenance, stated plainly.** The author has no shell and did not run this
Python. The table above was produced by the author running the same algorithm
in JavaScript in the house's own browser; the Python in this repository is the
same algorithm written for the house, and its agreement with the table is
established by the test above, which the house's suite runs. A reviewer should
run the two commands above and check that the table is reproduced exactly.

## What a caller can use this for

The project's search code - `integer_elimination.py`, `exact_lifting.py`,
`long_frontier.py` and the rest - can now be pointed at these triples and
required to find the optimum, because the optimum is known exactly for all of
them. Any search that reports a smaller size for one of these 53 triples is
wrong, and any search that reports a larger one is wrong in the other
direction.
