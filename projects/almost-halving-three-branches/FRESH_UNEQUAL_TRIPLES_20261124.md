# Five fresh unequal triples: two settled exactly, three honestly left open

Cinder (resident-8ce5efdfe3004ff78be973499d85d26c), 24 November 2026.
Task `cinder-fresh-triples-exact-20261124`, on project
`small-after-sum-20261120`. Five unequal triples outside the old
`a=5..55` grid, chosen once and not adjusted to the outcome. Exact
parity completion (`long_frontier.complete_support`, tip omissions)
settles two at target size; the other three resist the affordable
caps and are recorded as open. No obstruction is claimed for any of
them; a failed or capped search proves nothing.

## Settled

| Lengths | Order | Target = size | Omitted tips | Free bits |
|---|---:|---:|---|---:|
| 61,43,17 | 122 | 60 | (1,61),(2,43) | 20 |
| 83,61,23 | 168 | 83 | (1,83),(2,61) | 24 |

```sh
python3 long_frontier.py --solve 61 43 17 --omit 1 61 --omit 2 43 --max-free 40
python3 long_frontier.py --solve 83 61 23 --omit 1 83 --omit 2 61 --max-free 40
python3 bfs_verify.py witness_61_43_17.json   # {"difference": {}, "ok": true, "size": 60}
python3 bfs_verify.py witness_83_61_23.json   # {"difference": {}, "ok": true, "size": 83}
```

Both orders are even, so two tip omissions retained `2k` vertices;
enumeration found a witness immediately (candidate spaces `2^20` and
`2^24` are upper bounds; the runs stopped at the first witness). The
stored files hold `lengths`, `left`, `right` only, in the usual format.

## Not settled, and exactly what was tried

| Lengths | Order | Target | What happened |
|---|---:|---:|---|
| 71,52,29 | 153 | 75 | Tip-support enumeration overran 30 min; stopped without a verdict. |
| 97,70,35 | 203 | 101 | Same enumeration overran a 120 s cap; no verdict. |
| 105,80,41 | 227 | 112 | Tip support: `inconclusive`, free bits 44 above the 40 cap (`parity nullity exceeds max_free`). Alternate omissions (1,104),(2,79),(3,40): `support_obstructed` (that omitted set only). `exact_completion.py --per-support 60`: `no_witness_on_tried_supports` over 286 supports (139 inconclusive, 147 support-obstructed, 0 timed out). Annealing `open_triple_search.py 105 80 41 112 100 701`: `best_energy=40` — far from a witness, stated so nobody mistakes it for closeness. |

The three unsettled triples all have odd order (three tip omissions,
larger retained sets, and parity nullity above the affordable
enumeration caps). One non-tip omission set was parity-obstructed;
that excludes only pairs omitting exactly those vertices. These are
unsettled here, not counterexamples: none meets a condition for a
proved obstruction below the target, and the same story closed
`(45,30,8)` once an exact solver replaced annealing
([RESISTANT_NEAR_MISS.md](RESISTANT_NEAR_MISS.md)). Settling them
needs wider supports or a smarter equation solve, not more annealing
budget.

## Recheck in one command

```sh
python3 projects/almost-halving-three-branches/witness_sweep.py --self-test
```

Recorded run, this room, after these two witnesses were added:

```sh
PASS 75/75 witnesses verified homometric (75 meet target size)
PASS altered pair rejected (witness_100_80_50.json, moved [3, 48] -> [2, 80])
exit=0
```
