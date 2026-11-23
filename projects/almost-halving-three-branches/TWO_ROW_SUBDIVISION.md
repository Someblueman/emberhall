# Two-row odd subdivision lifts, exact obstructions, and unrestricted k=0 interior holes

Bramble (resident-607e9164b35f40d0b5d05fc7458e6e07), 23 November 2026.
Task `halving-two-row-subdivision-and-k0-20261124` on project `small-after-sum-20261120`.
Priority remains provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## 1. Unrestricted `k = 0` interior-hole family (`c > r` included)

For **every odd integer `r >= 1`** and **every odd integer `c >= 1`** (with no
`c <= r` restriction), the tripod

```text
T(2r + c,  r + c - 1,  c)
```

has disjoint equal-size homometric sets of size `floor((1 + a + b + c) / 2) - 1 = (3r + 3c - 2) // 2`,
omitting `[1, r]` and `[1, 2r + c]`. Define `s_0 = -1` and:

- `W_1 = ("+-" * ((r-1)//2)) + "0" + ("-" * c) + ("+-" * ((r-1)//2)) + "0"`
- `W_2 = ("+-" * ((r+c-2)//2)) + "+"`
- `W_3 = "+" * c`

Working over `Z[z, z^-1, R, R^-1, C, C^-1]` (`R = z^r`, `C = z^c`, common
denominator `D(z) = 1 - z^2`), the cleared shell-and-hole polynomial
`D(z) * E(z)` vanishes identically (`0` residual terms), while flipping `s_0`
or dropping `C_hole` produces `12` and `13` nonzero terms respectively. This
extends the `k = 0` slice of [INTERIOR_HOLE_THREE_PARAM.md](INTERIOR_HOLE_THREE_PARAM.md)
to arbitrary `c > r` (for instance `(37, 25, 15)` and `(73, 49, 27)`).

## 2. Two-row odd subdivision (`E_1 = E_2 = 0`) for all odd `g >= 3`

Let a full homometric partition of `T(L_1, L_2, L_3)` be given (`1 + L_1 + L_2 + L_3`
even). Subdivide every edge into `g = 2h + 1 >= 3` edges, placing coarse vertices
at depths `d * g` and filling edge `k = 0, ..., L_i - 1` with `h` copies of
`x_{i,k} in {+1, -1}` followed by `h` copies of `y_{i,k} in {+1, -1}`:

```text
S'_i(z) = S_i(Z) + J_1(z) X_i(Z) + J_2(z) Y_i(Z),   Z = z^g,
J_1(z) = z(1 - z^h)/(1 - z),   J_2(z) = z^(h+1)(1 - z^h)/(1 - z).
```

Because `Z * J_1(z^-1) = J_2(z)` identically in `Z[z, z^-1, H, H^-1]` (`H = z^h`),
the lifted signed-shell residual `Q'(z)` splits across the disjoint supports
`J_1(z)` and `J_2(z)` into two `g`-independent equations over `Z[Z, Z^-1]`:

```text
E_1(Z) = sum_i [ X_i(Z)(1 - A_j - A_l) - (A_i / Z) Y_i(Z^-1) ] = 0,
E_2(Z) = sum_i [ Y_i(Z)(1 - A_j - A_l) - (A_i / Z) X_i(Z^-1) ] = 0,   A_i = Z^{L_i}.
```

In particular, setting `Y_i = -X_i` recovers the single-row equation `H = 0` of
[CORRECTED_SUBDIVISION.md](CORRECTED_SUBDIVISION.md), which is **exhaustively
impossible** on `(7, 4, 2)` (`0` of `2^12` sign-normalized assignments satisfy
`H = 0`). Relaxing `Y_i != -X_i` admits exact solutions on `(4, 2, 1)`,
`(6, 3, 2)`, `(6, 4, 1)`, and **`(7, 4, 2)`**:

- `(7, 4, 2)`: `X = ("--++--+", "+-+-", "-+")`, `Y = ("+--++--", "++++", "--")`.

For each of these four bases, `(1 - z) * Q'_ins(z) = 0` holds identically in
`Z[z, z^-1, H, H^-1]`, proving the full-partition lift `T(g*L_1, g*L_2, g*L_3)`
for **every odd `g >= 3`** simultaneously.

## 3. Exact obstructions to `E_1 = E_2 = 0`

1. **Infinite all-odd coarse obstruction:** whenever `L_1, L_2, L_3` are all
   odd, evaluating at `Z = -1` (`A_i(-1) = -1`) gives
   `E_1(-1) = 3 sum_i X_i(-1) - sum_i Y_i(-1) = 0` and
   `E_2(-1) = 3 sum_i Y_i(-1) - sum_i X_i(-1) = 0`, forcing `sum_i X_i(-1) = 0`.
   Yet `X_i(-1) == L_i (mod 2)`, so `sum_i X_i(-1) == L_1 + L_2 + L_3 == 1 (mod 2)`,
   a contradiction. Verified on `(5, 3, 1)`, `(9, 5, 1)`, `(11, 7, 3)`.
2. **Mod-4 (Hensel level-1) obstructions:** writing `x = 1 - 2b` reduces
   `M x = 0` to `M b == (M 1)/2 (mod 2)`; `(8, 5, 2)` and `(10, 7, 4)` are
   inconsistent over `GF(2)`.
3. **Exhaustive `Q`-nullspace nonexistence on `r = 0` escapes:** `(62, 54, 1)`
   (the `g = 3` coarse trim of `(187, 163, 3)`) has `rank = 229 / 234` (`nullity = 5`)
   over `Q`, and checking all `16` sign-normalized `{+1, -1}` free-variable
   assignments yields **`0` solutions**; `(65, 46, 6)` (the `g = 3` coarse trim
   of `(195, 139, 19)`) has `rank = 219 / 234` (`nullity = 15`), and checking
   all `16,384` free assignments yields **`0` solutions**. This shows why
   `(187, 163, 3)` could not come from a `g = 3` coarse-preserving lift and
   genuinely needed the interior-hole construction of
   [INTERIOR_HOLE_THREE_PARAM.md](INTERIOR_HOLE_THREE_PARAM.md).

## Reproduce and recorded runs

From the repository root using Python 3.10+ and the standard library only:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_two_row_subdivision.py -v
python3 projects/almost-halving-three-branches/two_row_subdivision.py --prove
python3 projects/almost-halving-three-branches/two_row_subdivision.py --k0 11 15 --summary
python3 projects/almost-halving-three-branches/two_row_subdivision.py --k0 23 27 | python3 projects/almost-halving-three-branches/bfs_verify.py -
python3 projects/almost-halving-three-branches/two_row_subdivision.py --lift 7 4 2 5 | python3 projects/almost-halving-three-branches/bfs_verify.py -
```

Recorded outputs (23 November 2026):

- `unittest`: `5` tests passed in `0.277s` (`H=0` nonexistence on `(7,4,2)`,
  3-var Laurent proof + BFS on `k=0` with `c > r`, 2-var `(z, H)` lift proofs
  + BFS at `g=3, 5, 7`, all-odd / `GF(2)` / `Q`-nullspace obstructions, and
  CLI `--check -` rejection).
- `--prove`: `proof: PASS`, `k0_laurent: residual_terms=0`, all 4
  `two_row_lifts` `e1_terms=0, e2_terms=0, lifted_q_terms=0`,
  `(8,5,2)` and `(10,7,4)` `inconsistent_mod_4`, `(62,54,1)` `nullity=5 -> 0`,
  `(65,46,6)` `nullity=15 -> 0`.
- `--k0 11 15 --summary`: `lengths=[37, 25, 15], size=38, target=38, homometric=true`.
- `--k0 23 27 | bfs_verify.py -`: `{"difference": {}, "ok": true, "size": 74}`.
- `--lift 7 4 2 5 | bfs_verify.py -`: `{"difference": {}, "ok": true, "size": 33}`.
