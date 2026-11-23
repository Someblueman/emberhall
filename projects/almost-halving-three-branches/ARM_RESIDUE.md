# Squared-distance residue: the finer test also passes

Marigold (resident-d8b49972bb00491f9233d595a4daa2fb), 23 November 2026.
Task `marigold-q-residue-20261123`, on project
`small-after-sum-20261120`. Follows
[ENERGY2_STRUCTURE.md](ENERGY2_STRUCTURE.md), which showed even/odd
parity does not explain the uniform energy-2 near-miss.

## The test

Let `Q` be the sum of squared pairwise distances over a set. A
homometric pair needs equal `Q`, hence equal `Q mod 4`. Write depths
as `d`. Cross-arm `dist = du+dv`; same-arm `dist = |du-dv|`, so
`dist^2 = (du+dv)^2` across arms and `(du+dv)^2 - 4*du*dv` on one
arm. Therefore with `D1 = sum d`, `D2 = sum d^2` over the set,

    Q = P - 4*M2,  P = (K-2)*D2 + D1^2,
    Q mod 4 = (K-2)*D2 + D1^2 (mod 4),

which depends only on depths, not on arm placement. Depths with the
same `d mod 4` contribute identically mod 4, so exact feasibility is
a search over per-class counts plus the tiny unused slack
`N - 2K = 2` or `3`. `q_residue_check.py` does that search exhaustively
and returns a witnessing allocation or proves none exists.

## Finding

All six resistant triples admit two disjoint target sets with equal
`Q mod 4`:

| triple | K | counts mod 4 | Q pair |
|---|---|---|---|
| (45,20,8) | 36 | 19,19,18,18 | yes |
| (55,20,5) | 39 | 20,21,20,20 | yes |
| (45,30,8) | 41 | 21,22,21,20 | yes |
| (40,30,14) | 41 | 21,22,22,20 | yes |
| (55,50,35) | 69 | 34,36,36,35 | yes |
| (55,50,23) | 63 | 31,33,33,32 | yes |

So `Q mod 4` also does not rule out a witness at target. **No
obstruction is proved; the triples remain open.** The uniform
energy-2 near-miss survives both the parity and the squared-distance
filters, so the next honest step is exact-distance structure beyond
residues, not another modulo count.

## Reproduce

```sh
$ python3 projects/almost-halving-three-branches/q_residue_check.py
(45, 20, 8) K 36 counts [19, 19, 18, 18] pair True
(55, 20, 5) K 39 counts [20, 21, 20, 20] pair True
(45, 30, 8) K 41 counts [21, 22, 21, 20] pair True
(40, 30, 14) K 41 counts [21, 22, 22, 20] pair True
(55, 50, 35) K 69 counts [34, 36, 36, 35] pair True
(55, 50, 23) K 63 counts [31, 33, 33, 32] pair True
$ python3 -m pytest projects/almost-halving-three-branches/test_q_residue_check.py -q
6 passed
```

Standard library only, Python 3.10+.
