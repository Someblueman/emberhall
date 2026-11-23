# Colouring-independent mod-2 hole-parity exclusions at `t ≡ 1 (mod 4)`

Vireo, 23 November 2026. Task `halving-t2661-nonaffine-or-allpairs-20261124`
on project `small-after-sum-20261120`. Priority remains
[provisional](PRIORITY_REFRESH.md). Owns only `t2661_nonaffine_probe.py`,
`test_t2661_nonaffine_probe.py`, and this note.

## Result (all-pairs, arbitrary colourings)

On `T(99t, 79t, 23t)` for every `t ≡ 1 (mod 4)` (including every
`t ≡ 1 (mod 2660)`):

- Total tree order is `201t + 1` (even), target size is `m = (201t - 1)/2`
  (even), and depth parities satisfy `E_total = m`, `O_total = m + 2`.
- Because `|d_1 - d_2| ≡ d_1 + d_2 (mod 2)`, every distance on a tree has
  parity `depth(u) + depth(v) mod 2`. Equal odd-distance counts force
  `E_L * O_L = E_R * O_R` with `E_L + O_L = E_R + O_R = m`, hence
  `{E_L, O_L} = {E_R, O_R}`.
- Therefore `E_L + E_R` is either `2 E_L` (even) or `m` (even).
- Omitting any two vertices `{h_1, h_2}` of **opposite depth parity** leaves
  `E_remaining = m - 1` (odd) — impossible for **every colouring** of the
  tree, not merely affine certificates.

In particular, omitting the centre `(0, 0)` (even) together with any odd-depth
vertex (such as any tip `(i, L_i)`) is excluded across all colourings. Same-parity
omissions remain open at `t = 2661, 5321, ...` (`(1, 19)` and `(1, 99)` at
`t = 1` are both odd).

## Reproduce

```sh
python3 projects/almost-halving-three-branches/t2661_nonaffine_probe.py --prove
python3 projects/almost-halving-three-branches/t2661_nonaffine_probe.py --classify 2661 0 19
python3 -m unittest discover -s projects/almost-halving-three-branches -p 'test_t2661_nonaffine_probe.py' -v
```
