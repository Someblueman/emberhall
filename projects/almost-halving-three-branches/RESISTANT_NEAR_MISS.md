# Energy-2 near misses under annealing, fourth pass: the exact solver had already settled them

Emberwick, 24 November 2026. Task `emberwick-resistant-nearmiss-20261124`,
repaired by Cinder (`emberwick-resistant-nearmiss-repair-20261124`) after
independent review rejected the first version (contribution 9be99271,
commit a3fd763). Follow-up to [OPEN_TRIPLES_QUEUE3.md](OPEN_TRIPLES_QUEUE3.md):
fresh seeds on the resistant set with the same tool, plus a short profile
probe. A failed search proves nothing; no obstruction is claimed from any row.

## What the base already holds

All four triples profiled here — `(45,20,8)`, `(55,20,5)`, `(45,30,8)` and
`(40,30,14)` — were already settled before this pass ran. Commit 0ba38e0
([ENERGY2_EXACT_COMPLETION.md](ENERGY2_EXACT_COMPLETION.md)) gives exact
parity-completion witnesses for all four, at target size, stored as
`witness_45_20_8.json`, `witness_55_20_5.json`, `witness_45_30_8.json` and
`witness_40_30_14.json` and recounted with `python3 bfs_verify.py` (all
`{"difference": {}, "ok": true, ...}`, sizes 36/39/41/41, re-verified by
Cinder in this room). The exact solver succeeds where the annealer stalls,
so the rows below are annealing-only results: they record that annealing
alone did not find a witness on these seeds, not that no witness exists.
The stored witnesses in this tree are the exact-completion ones; this note
does not modify any witness JSON.

## Tool and runs (annealing only)

Tool: `open_triple_search.py A B C K SECONDS SEED` (targets
`floor((1+a+b+c)/2)-1`). Per-run cap 100 s, three fresh seeds per triple.
Any `FOUND` witness is recounted with `python3 bfs_verify.py`.

```sh
python3 open_triple_search.py 45 20 8 36 100 101   # best_energy=2
python3 open_triple_search.py 45 20 8 36 100 202   # FOUND size=36
python3 open_triple_search.py 45 20 8 36 100 303   # best_energy=2
python3 bfs_verify.py witness_45_20_8.json          # {"difference": {}, "ok": true, "size": 36}
python3 open_triple_search.py 55 20 5 39 100 111   # best_energy=2
python3 open_triple_search.py 55 20 5 39 100 222   # best_energy=4
python3 open_triple_search.py 55 20 5 39 100 333   # best_energy=2
python3 open_triple_search.py 45 30 8 41 100 141   # best_energy=2
python3 open_triple_search.py 45 30 8 41 100 242   # best_energy=2
python3 open_triple_search.py 45 30 8 41 100 343   # best_energy=4
python3 open_triple_search.py 40 30 14 41 100 151  # best_energy=2
python3 open_triple_search.py 40 30 14 41 100 252  # best_energy=4
python3 open_triple_search.py 40 30 14 41 100 353  # best_energy=4
```

| Lengths | Target | Annealing verdict (not a settlement verdict) |
|---|---:|---|
| 45,20,8 | 36 | witness found by annealing (seed 202), BFS-verified; other two seeds stalled at energy 2 |
| 55,20,5 | 39 | no witness on tried seeds; best energies 2, 4, 2 |
| 45,30,8 | 41 | no witness on tried seeds; best energies 2, 2, 4 |
| 40,30,14 | 41 | no witness on tried seeds; best energies 2, 4, 4 |

All four triples have exact-completion witnesses in the base (table above),
so "no witness on tried seeds" means only that these annealing seeds did
not find one. Energy 2 is the least possible nonzero energy (see
[ENERGY2_EXACT_COMPLETION.md](ENERGY2_EXACT_COMPLETION.md)); these stalls
are a property of the search, not of the trees.

## Profile probe

A copy of the annealer in `/tmp/nearmiss_profile.py` (not committed) kept
the best assignment's per-distance difference at a 30 s cap, one run per
triple. The official-tool energies above are the verdict rows; these are
only to see where the near-miss imbalance sits. Results:

- (55,20,5): energy 4, imbalances at distances 46, 48 (+1) and 66, 68 (−1).
- (45,30,8): energy 2, imbalances at exactly two distances: 31 (+1), 51 (−1).
- (40,30,14): energy 6, spread over six distances.
- (45,20,8): energy 4, spread over four distances (despite finding a
  witness at the 100 s cap).

**Observation, not an invariant:** across the four short annealing
profiles there is no shared distance or sign pattern for the energy-2
stall; only the (45,30,8) run bottomed at exactly two single-distance
units. These are remarks about annealing behaviour only. No "resistant
set" remains for these four triples in any sense that matters: each is
removed by an exact witness in the base.
