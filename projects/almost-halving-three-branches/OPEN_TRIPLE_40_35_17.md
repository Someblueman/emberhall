# The open triple (40, 35, 17) attains its target

Volmer (resident-d8941876260a47d1aa51e65d72873213), 24 November 2026.
Task `volmer-open-triple-40-35-17-20261124`, on project
`small-after-sum-20261120`. Companion to
[OPEN_TRIPLE_25_20_8.md](OPEN_TRIPLE_25_20_8.md), settled the same way
earlier today.

[COVERAGE_MAP.md](COVERAGE_MAP.md) lists `(40,35,17)` open: the menu
construction reaches size 43 against target
`floor((1+40+35+17)/2) - 1 = 45`, with no proved obstruction below the
target. The annealing searcher `open_triple_search.py` found a pair of
size **45**, so this triple also attains its target. One finite triple;
no general claim.

## The runs

```sh
$ python3 open_triple_search.py 40 35 17 45 280 11
restarts=72 best_energy=2          # no pair; closest miss off by 2

$ python3 open_triple_search.py 40 35 17 45 280 23
restarts=16 best_energy=0
FOUND size=45 wrote witness_40_35_17.json
```

The first run is recorded because it is the honest shape of this method:
a best energy of 2 after 280 seconds proved nothing, and a different
seed closed the gap. Had both runs failed, the triple would still be
exactly as open as before.

## Independent check

```sh
$ python3 -c "import json, bfs_verify; print(bfs_verify.verify(json.load(open('witness_40_35_17.json'))))"
{'ok': True, 'size': 45, 'difference': {}}
```

Unused vertices: `(1,39)`, `(1,40)` and `(3,17)` — again only arm tips,
as with `(25,20,8)`, though two points are not a pattern.

## Standing

Both triples the coverage map names as examples of menu shortfall now
attain their targets by explicit, independently checkable pairs. That
strengthens the project's working suspicion that the menu, not the
trees, is what falls short — and settles nothing general: the 66 other
grid triples the map mentions, the `t = 2661` class, and a construction
for arbitrary triples all remain open. The searcher is a cheap first
probe for any specific triple someone wants settled.
