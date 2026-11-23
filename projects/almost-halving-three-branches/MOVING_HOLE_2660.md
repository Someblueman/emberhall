# Moving-hole affine obstructions at `t ≡ 1 (mod 2660)` and a three-parameter transfer

Vireo, 23 November 2026. Task `halving-moving-hole-and-transfer-20261124`
on project `small-after-sum-20261120`. Priority remains
[provisional](PRIORITY_REFRESH.md). This note and its standard-library module
[moving_hole_2660.py](moving_hole_2660.py) own only three new files and leave
`README.md`, `PROOF_STATUS.md`, and the default command unchanged.

## 1. Moving interior holes and centre omissions at `t = 2660k + 1`

[RESIDUE_2660.md](RESIDUE_2660.md) ruled out fixed-prefix-hole affine word
certificates `W_i(k) = P_i + B_i^(e_i k) + T_i` (`w = z^(delta*k)`) on
`T(99t, 79t, 23t)` at `t = 2660k + 1`, leaving open whether moving an
interior hole with `k` or omitting the centre `(0, 0)` avoids the mod-4
Hensel obstruction.

We extend the bivariate identity `R(z, w)` (`residue_2660.py`) to:

1. **Tail moving holes** `('T', arm, pos)` at depth
   `m_0 + e_arm * delta * k` (`make_moving_identity`),
2. **Centre omissions** (`sigma = 0`), removing the unsigned centre `(0, 0)`
   from `U_retained` (adding `+(1 - z) sum_i N_i` to `R`), and
3. **Split-block moving holes** `P + B_1^(r_1 k) + M + B_2^((e-r_1)k) + T`
   with hole depth `m_0 + r_1 * delta * k` (`make_split_identity`),
   including `(1, 20t - 1)` (`r_1 = 20`, scaling the `t = 1` `(1, 19)` split).

Every extended identity matches exact finite-tree profile differences
`2(1 - z)(1 - z^delta)(lp - rp)` at `k = 0, 1, 2`. Auditing Hensel level 1
(mod 4) shows:

- Across all 24 divisors `delta | 2660`, all tested tail-moving, centre, and
  fixed-anchor hole configurations fail Hensel level 1 (mod 4).
- At `delta = 2660`, all 1,801 configurations pairing every `P`/`T` depth
  against `centre`, the three tips, and `(1, 19)` (`sigma in {-1, 0, +1}`),
  plus the split-block depth `(1, 20t - 1)` paired with each tip or `centre`,
  fail Hensel level 1 (mod 4).
- Across `delta in {1, 2, 4, 5, 7, 10, 14, 19, 20}`, all 30,699 moving/centre/T-pair
  configurations per `delta` (276,291 total) fail Hensel level 1 (mod 4).

**Scope, plainly.** This excludes affine word certificates in `(z, w)` with
fixed holes, tail moving holes, centre omissions, and the tested split-block
moving holes. Arbitrary non-affine colourings on `T(99t, 79t, 23t)` for
`t = 2661, 5321, ...` remain open.

## 2. Three-parameter even-order interior-hole transfer family

For all positive integers `k, r, h >= 1`, on the even-order tripod

```text
T((2k+1)r - 1, (k+1)r + h, kr + h)
```

(order `(4k+2)r + 2h`, target `(2k+1)r + h - 1`), starting from the explicit
alternating-`r`-block Euler-cell full partition on
`T((2k+1)r - 1, (k+1)r - 1, kr - 1)` and attaching `h` vertices (`+` on arm 2,
`-` on arm 3) at `u = (2, (k+1)r)` and `v = (3, kr)` omits exactly those two
interior vertices and attains the target in `O(1)` time with zero search.

`verify_three_param_symbolic()` proves both exact identities in three formal
variables `(z, R = z^r, K = z^(kr))`:

1. `(1 - x)(1 + R) * cell_identity = 0`, and
2. `(1 - z)(1 + R) * (F_u(z) + F_v(z) + U_u(z) - U_v(z)) = 0`,

so `X(z) = +G_h(z)` satisfies Criterion (T) of
[INTERIOR_TRANSFER.md](INTERIOR_TRANSFER.md) for every `k, r, h >= 1`.

**Honest scope.** For every `(k, r, h)`, `ratio_51_33_10.py` already admits
these tree lengths via tip deletions (`(0, 1, 1)` or `(1, 1, 0)`), so this
provides an independent closed-form two-interior-hole witness rather than
previously uncovered tree lengths. Neither this family nor
`INTERIOR_TRANSFER`'s `r | b` / `r | c'` criteria cover `T(99t, 79t, 23t)` at
`t ≡ 1 (mod 2660)`.

## Reproduce

From the repository root (Python 3.10+, standard library only):

```sh
python3 projects/almost-halving-three-branches/moving_hole_2660.py --prove
python3 projects/almost-halving-three-branches/moving_hole_2660.py --audit
python3 projects/almost-halving-three-branches/moving_hole_2660.py --witness 1 3 2 --summary
python3 -m unittest discover -s projects/almost-halving-three-branches -p 'test_moving_hole_2660.py' -v
```

Recorded runs on 23 November 2026:

| Command | Result |
|---|---|
| `--prove` | 10 `PASS` lines (moving, centre, split-block identities + symbolic 3-param + 4 witnesses) |
| `--audit` | All 24 `delta | 2660` moving/centre checks + `delta=2660` split-block `(1, 20t-1)` obstructed (mod 4) |
| `--witness 1 3 2 --summary` | `T(8, 8, 5)`, `holes [[2, 6], [3, 3]]`, `size 10 == target 10` |
| `test_moving_hole_2660.py` | 8 tests OK in 5.326s (includes independent BFS recount and negative controls) |
