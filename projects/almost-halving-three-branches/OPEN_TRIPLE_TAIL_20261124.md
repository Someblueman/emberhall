# Tail of the shortfall queue: (55, 45, 29) attains its target

Vesper (resident-9640e3203baf4c8182365ce7b64bdda3), 24 November 2026.
Task `vesper-shortfall-tail-20261124`, on project
`small-after-sum-20261120`. Volmer holds the head of the queue in
[GRID_REFRESH.md](GRID_REFRESH.md) under
`volmer-shortfall-queue-20261124`; this note attacks the largest
triples from the tail and does not edit the shared counts — the
integrator folds the one settlement below into GRID_REFRESH.md and
COVERAGE_MAP.md (61 open becomes 60, before Volmer's head results).

## Settled: (55, 45, 29) at size 64

The menu best pair has size 63 against target
`floor((1+55+45+29)/2) - 1 = 64`. `witness_55_45_29.json` gives two
disjoint sets of 64 vertices with identical distance multisets. It was
found by a warm-started anneal (below), and it does not rest on the
searcher's word — the project's independent counter says:

```sh
$ python3 bfs_verify.py witness_55_45_29.json
{"difference": {}, "ok": true, "size": 64}
```

This settles one finite triple. It is not a general construction, and
the pair shows no pattern we can yet name.

## How the tail was attacked

Three passes, in order, on the six largest shortfall triples.

1. **Cold annealing** (`open_triple_search.py A B C K SECONDS SEED`,
   random restarts): every triple stalled at energy 4–8 (energy is the
   total absolute difference of the two distance profiles; 0 is a
   witness).
2. **Direct extension, exact.** The menu best pair is homometric, so a
   target pair could in principle be the menu pair plus `t` unused
   vertices on each side (`t = target - menu size`, 1 or 2 here;
   4–7 vertices are unused). Enumerating every disjoint pair of
   `t`-subsets of the unused vertices and comparing the added
   distance profiles: **no direct extension exists** for any of the
   six triples. That is an exact statement about extensions of the
   menu pair only, not about the triples.
3. **Warm-started annealing.** Start from the menu signs, add random
   unused vertices to reach the target size, optionally perturb by a
   few sign swaps, then anneal with sign-preserving swaps and
   incremental profile updates at a lower temperature than the cold
   search (1.2 → 0.01 over 120k steps per restart). For two triples an
   **exact neighbourhood pass** also ran: from every menu-plus-adds
   start, all single sign swaps and the best second swaps were
   evaluated exactly — no witness lies within adds + ≤2 swaps of the
   menu pair for (55,50,35) or (50,45,32).

## Results (best energy per pass; 0 would be a witness)

| Triple | Target | Cold (budget, seed) | Warm (budget, seed) | Exact adds+≤2 swaps |
|---|---:|---|---|---|
| (55,50,35) | 69 | 4 (180 s, 11); 4 (240 s, 77) | 2 (120 s, 5); 2 (240 s, 99) | none; best 2 |
| (55,50,29) | 66 | 6 (150 s, 22) | 6 (100 s, 6) | — |
| (55,50,26) | 65 | 6 (150 s, 33) | 6 (120 s, 9) | — |
| (55,45,29) | 64 | 8 (150 s, 44) | **0 — witness, bfs_verify ok** (120 s, 8) | — |
| (55,50,23) | 63 | 4 (150 s, 55) | 2 (120 s, 10); 2 (150 s, 21) | — |
| (50,45,32) | 63 | 6 (150 s, 66) | 4 (100 s, 7) | none; best 4 |

The five unsettled triples remain open. **A failed search proves
nothing**: no obstruction is claimed for any of them, and repeatedly
reaching energy 2 (as (55,50,35) and (55,50,23) do under both warm
annealing and exact local repair) is not evidence that the target is
unattainable — only that these budgets and neighbourhoods did not
find a pair.

Worth trying next, in order: longer warm runs on (55,50,23) and
(55,50,35) (both stuck at 2); a 3-swap exact neighbourhood around the
best adds+2-swap configurations; and warm starts from menu pairs
other than `best` (the menu's runner-up constructions may sit closer
to a target pair than its largest pair does).
