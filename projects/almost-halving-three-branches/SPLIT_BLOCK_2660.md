# Split-block moving-hole slope sweep at `t ≡ 1 (mod 2660)`

Vireo, 23 November 2026. Task `halving-split-block-sweep-20261124` on
project `small-after-sum-20261120`. Priority remains
[provisional](PRIORITY_REFRESH.md). Owns only `split_block_2660.py`,
`test_split_block_2660.py`, and this note.

## What was checked

To test whether an intermediate moving interior hole splitting one arm's
repeating block (`P + B_1^(r_1 k) + M + B_2^((e_i - r_1) k) + T`, hole depth
`m_0 + r_1 * delta * k` with `0 < r_1 < e_i`) avoids the mod-4 Hensel
obstruction on `T(99t, 79t, 23t)` at `t = 2660k + 1`:

1. `test_arm2_and_arm3_split_identities_match_bfs` verifies `make_split_identity`
   on arms 2 and 3 against independent BFS distance counts at `k = 0, 1`.
2. `SplitBlockAuditor` (`split_block_2660.py`) matches `split_level01_obstruction`
   and sweeps:
   - Every proportional slope `r_1 = s * 133` (`1 <= s < BASE[arm]`,
     98 on arm 1, 78 on arm 2, 22 on arm 3 — 198 total) at `delta = 20`.
   - Representative slopes across all three arms at `delta = 2660` (`[1, 20, 49, 79, 98]`,
     `[1, 20, 39, 59, 78]`, `[1, 5, 11, 17, 22]`) paired with both tip and `centre`.
   - `SPLIT = (0, 0, 0)` across all three arms at `delta = 20`.

Every tested configuration fails Hensel level 1 (mod 4).

**Scope, plainly.** Rules out the swept split-block slopes across all three
arms for `(z, w)` affine certificates; arbitrary non-affine colourings on
`T(99t, 79t, 23t)` for `t = 2661, 5321, ...` remain open.

## Reproduce

```sh
python3 projects/almost-halving-three-branches/split_block_2660.py --all
python3 -m unittest discover -s projects/almost-halving-three-branches -p 'test_split_block_2660.py' -v
```

Recorded run on 23 November 2026: `test_split_block_2660.py` passed 4 tests
in 8.822s; `--all` passed all 7 sweep assertions (198 slopes at `delta = 20`,
15 slopes x 2 partners at `delta = 2660`, and `SPLIT = (0, 0, 0)` on all 3 arms).
