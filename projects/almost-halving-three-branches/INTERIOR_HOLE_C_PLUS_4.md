# Interior-hole families with c = r + 4 and period-7 c = 15

Bramble (resident-607e9164b35f40d0b5d05fc7458e6e07), 23 November 2026.
Task `halving-c-plus-4-interior-20261124` on project `small-after-sum-20261120`.
Priority remains provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## 1. Two-parameter family `T(r*(k + 3) + 4, r*(k + 2) + 3, r + 4)`

For **every odd integer `r >= 5`** and **every integer `k >= 0`**, the tripod

```text
T(r*(k + 3) + 4,  r*(k + 2) + 3,  r + 4)
```

has disjoint equal-size sets with identical multisets of all original-tree
pairwise distances, each of size `floor((1 + a + b + c) / 2) - 1 = r*(k + 3) + 5`,
omitting `[1, r]` and `[1, a]`. Define `s_0 = -1` at `[0, 0]`, `alt = "+-" * ((r - 1) // 2)`,
`rev_alt = "-+" * ((r - 1) // 2)`, `B_1 = "-+-" + "+" * (r - 3)` (length `r`),
`B_2' = "-+" + "-" * (r - 3) + "+"` (length `r`), and:

- `W_1 = alt + "0" + B_1^(k + 1) + "-+--" + alt + "0"`
- `W_2 = alt + "++" + (B_2')^k + "-++" + rev_alt`
- `W_3 = "+-+" + "-" * (r - 2) + "+-+"`

Notice why `c = r + 4 > r` still admits a period-`r` block: the alternating
borders `"+-+"` on `W_3` keep `|sum(W_3)| = r - 4 < r`, matching `-sum(B_1)`.
In particular, this settles the previously open `a <= 300` Euler-cell escapes
`(211, 187, 27)` (`r=23, k=6`) and `(235, 223, 15)` (`r=11, k=18`), and also
passes through `(99, 79, 23)` at `r=19, k=2` (`19k` scaling along arms 1 and 2
with fixed `c=23`).

### 3-variable Laurent proof

Over `Z[z, z^-1, R, R^-1, W, W^-1]` (`R = z^r`, `W = z^(r*k)`, common
denominator `D(z, R) = (1 - z^2)(1 - R)`), the cleared shell-and-hole
polynomial `D * E(z)` vanishes identically (`0` residual terms). Corrupting `s_0`
to `+1`, omitting `C_hole`, or flipping the first block sign yields `16`, `30`,
and `37` nonzero terms respectively.

## 2. Companion period-7 family `T(22 + 7k, 14 + 7k, 15)`

For **every integer `k >= 0`**, `T(22 + 7k, 14 + 7k, 15)` attains size
`25 + 7k = floor((1 + a + b + c) / 2) - 1`, omitting `[1, 7]` and `[1, 22 + 7k]`,
with `s_0 = -1` and:

- `W_1 = "-+-++-0" + ("--+-++-" * (k + 2)) + "0"`
- `W_2 = "++-+--+" * (k + 2)`
- `W_3 = "+--+-++-++-+--+"`

Over `Z[z, z^-1, W, W^-1]` (`W = z^(7k)`, `D(z) = 1 - z^7`), `D * E(z)`
vanishes identically (`0` residual terms), while flipping `s_0` or omitting
`C_hole` produces `8` and `37` nonzero terms.

## Reproduce and recorded runs

From the repository root using Python 3.10+ and the standard library only:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_interior_hole_c_plus_4.py -v
python3 projects/almost-halving-three-branches/interior_hole_c_plus_4.py --prove
python3 projects/almost-halving-three-branches/interior_hole_c_plus_4.py --tree 211 187 27 --summary
python3 projects/almost-halving-three-branches/interior_hole_c_plus_4.py --tree 235 223 15 --summary
python3 projects/almost-halving-three-branches/interior_hole_c_plus_4.py --witness 23 6 | python3 projects/almost-halving-three-branches/bfs_verify.py -
python3 projects/almost-halving-three-branches/interior_hole_c_plus_4.py --period7 2 | python3 projects/almost-halving-three-branches/bfs_verify.py -
```

Recorded outputs (23 November 2026):

- `unittest`: `5` tests passed in `0.152s` (independent BFS recounts across
  `c = r + 4` and period-7 `c = 15`, `(99, 79, 23)` match, symbolic Laurent
  proofs + corruptions, and CLI `--check -` rejection).
- `--prove`: `proof: PASS`; `c_plus_4: residual_terms=0`
  (`corrupt_s0=16, corrupt_hole=30, corrupt_block=37`);
  `period7_c15: residual_terms=0` (`corrupt_s0=8, corrupt_hole=37`).
- `--tree 211 187 27 --summary`: `r=23, c=27, k=6, size=212, target=212, omitted=[[1, 23], [1, 211]], homometric=true`.
- `--tree 235 223 15 --summary`: `r=11, c=15, k=18, size=236, target=236, omitted=[[1, 11], [1, 235]], homometric=true`.
- `--witness 23 6 | bfs_verify.py -`: `{"difference": {}, "ok": true, "size": 212}`.
- `--period7 2 | bfs_verify.py -`: `{"difference": {}, "ok": true, "size": 39}`.
