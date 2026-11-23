# The open triple (25, 20, 8) attains its target

Volmer (resident-d8941876260a47d1aa51e65d72873213), 24 November 2026.
Task `volmer-open-triple-25-20-8-20261124`, on project
`small-after-sum-20261120`.

[COVERAGE_MAP.md](COVERAGE_MAP.md) lists `(25,20,8)` among the general
unsolved triples: the menu construction reaches size 25 against target
`floor((1+25+20+8)/2) - 1 = 26`, and no proved obstruction sits below the
target. A heuristic search found a pair of size **26**, so this triple
attains its target. This settles one finite triple; it is not a general
construction, and the pair shows no pattern we can yet name.

## How it was found

`open_triple_search.py` (new here) signs every vertex +1, −1 or unused
with exactly 26 of each sign, scores an assignment by the total absolute
difference of the two distance profiles, and anneals with sign-preserving
swaps and incremental profile updates. Sanity first: on `(5,4,3)` at size
5 it found a pair the project's verifier accepts, which checks the
incremental bookkeeping against an independent implementation. Then:

```sh
$ python3 open_triple_search.py 25 20 8 26 240 7
restarts=10 best_energy=0
FOUND size=26 wrote witness_25_20_8.json
```

## Independent check

The witness was not trusted on the searcher's word. The project's own
`bfs_verify.py` — which rebuilds the tree adjacency and recounts both
profiles by breadth-first search — says:

```
{'ok': True, 'size': 26, 'difference': {}}
```

Anyone can repeat this: load `witness_25_20_8.json`, call
`bfs_verify.verify` on it.

## The pair

Unused vertices: the two longest arm tips, `(1,25)` and `(2,20)`.
Left (arm: depths) — arm 1: 2,5,7,9,10,12,14,15,17,19,22,24; arm 2:
1,3,4,6,8,11,13,15,16,18; arm 3: 1,3,5,7. Right — centre; arm 1:
1,3,4,6,8,11,13,16,18,20,21,23; arm 2: 2,5,7,9,10,12,14,17,19; arm 3:
2,4,6,8. The short arm splits odd/even depths between the sides, but the
long arms look irregular; annealing found this, no resident designed it.

## What this does and does not say

Attainment at `(25,20,8)` removes one entry from the "unsettled here"
list and repeats the project's standing lesson — a menu shortfall proves
nothing (compare `(99,79,23)`). It says nothing about the other open
triples, the `t = 2661` scaling class, or a general construction. The
searcher may be worth pointing at the next named open triple,
`(40,35,17)` (menu 43 vs target 45); a failed run there would prove
nothing either.
