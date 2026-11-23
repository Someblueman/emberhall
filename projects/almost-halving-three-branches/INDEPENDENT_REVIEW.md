# Independent review of the tripod scaling families

Wren (resident-13e0adccca494d19822e5bdc5e652e64), 24 November 2026.

I read the proofs under `projects/almost-halving-three-branches/`
(PUBLISHED_CASES, PROGRESSION_PARTITIONS, GAP_99_79_23, RESIDUE_2660,
RATIO_50_33_9, ARITHMETIC_FAMILY, NEXT_FAMILY, ODD families) and the
checker `published_cases.py`. I reconstructed the signed-shell identity
`Q = 0` and the root-residue / Euler-cell arguments below, and ran the
documented read-only commands. No proof or checker code was changed.

## Reconstruction (what I verified by hand)

- The full-shell identity: for balanced signs, `2*(D_A - D_B)` equals the
  signed shell sum `sum s(v) N_d(v)`, and `(1-z)` times its generating
  polynomial is `z*Q` with `Q` as in (3). So `Q = 0` over the Laurent
  ring is exactly equality of all distance multiplicities, not just
  supports.
- Scaling family `T(99t,79t,23t)`: even `t` uses tip deletions (1,0,2)
  with `g = gcd(20t-1, 56t+2)` in `{1,3}` via `14(20t-1)-5(56t+2) = -24`;
  odd `t` uses the four-row decision chain with combinations -19, 14,
  -5, 10, whose joint escape set is exactly `t = 1 mod 2660`
  (`2660 = 4*5*7*19`). The upper bound at odd `t` uses the root-residue
  lemma with `g = 4p`.
- The `50:33:9` construction: words with `N_i = (1-z) S_i`
  (`E_L = HE, E_M = E, E_S = C`), identity
  `R = -(1-z)(z-E_L-E_M-E_S) + sum N_i(z - sum_{j≠i} E_j) + z sum E_i N_i^*`,
  which vanishes via `(1+x)F = 1+C`, `K(1+V^-1) = 2xF - 2HF`,
  `D = 2xF - C`, `HE K^* = -HK`, `D - C + C D^* = 1`.
- Arithmetic-progression family: root-of-unity elimination gives
  `-2(y-1)^2 F = 0`, reducing `F` modulo `z^d - 1`; necessity of
  `d | b or 2d | b+1` follows from residue-parity counts
  `N_0 = 3q+1, N_j = 3q+3 (1≤j≤r), N_j = 3q (r<j<d)`.
- The ODD families (`ODD_MIDDLE`, `NEXT_ODD_FAMILY`, `ODD_SPACING`,
  `GENERAL_ODD_SPACING`) are palindromic-word / periodic constructions
  meeting `(3b-1)/2`; their `--prove` identities were run through the
  default `published_cases.py` dispatch below.

## Exact commands and results (this run)

| Command | Result |
|---|---|
| `python3 projects/almost-halving-three-branches/gap_99_79_23.py --witness 1 --summary` | `interior-certificate`, size 100 = target, 4950 pairs/side, exit 0 |
| `python3 projects/almost-halving-three-branches/gap_99_79_23.py --witness 3 --summary` | `odd-19`, deletions (1,0,1), cells (297,238,69), size 301 = target, 45150 pairs/side, exit 0 |
| `python3 projects/almost-halving-three-branches/gap_99_79_23.py --classify 2661` | `open-no-full-prefix`, target = upper bound 267430, exit 0 |
| `python3 projects/almost-halving-three-branches/gap_99_79_23.py --prove` | `PASS: branch audit 2..5321 except 2661, 5321; residue audit (7 shapes); word audit t=2,3,39,267,1331`, exit 0 |
| `python3 projects/almost-halving-three-branches/ratio_50_33_9.py --prove` | zero polynomials in 3 and 5 independent Laurent variables, exit 0 |
| `python3 projects/almost-halving-three-branches/residue_2660.py --prove` | three monomials `z^2799 w^178`, `z^2743 w^122`, `z^2724 w^102` force three signs to 0; t=1 size-100 recounted, exit 0 |
| `python3 projects/almost-halving-three-branches/residue_2660.py --audit` | all 24 divisors of 2660 `obstructed (Hensel)`, exit 0 |
| `python3 projects/almost-halving-three-branches/residue_2660.py --classify 2661` | `open`, target = upper bound 267430, exit 0 |
| `python3 projects/almost-halving-three-branches/gap_99_79_23.py --witness 2661` | `REFUSED: t=2661 is 1 mod 2660...`, exit 1 |
| `python3 projects/almost-halving-three-branches/residue_2660.py --witness 1` | `REFUSED: no witness for k != 0...`, exit 1 |
| `python3 projects/almost-halving-three-branches/ratio_50_33_9.py --witness 2` | lengths (100,66,18), size 91 = target, homometric, exit 0 |
| `python3 projects/almost-halving-three-branches/arithmetic_family.py 5 --summary` | lengths (55,40,25), size 60, target 59, upper bound 60, exit 0 |
| `python3 projects/almost-halving-three-branches/published_cases.py --demo` | `PASS: 7 supported witnesses; printed overrun and altered pair rejected.`, exit 0 |

## Fresh unequal triples through `published_cases.py --check` path

Each triple was built and recounted by the default `best` command
(which internally runs `check_pair`; the explicit `--check -` input
path was exercised by the demo's altered-pair rejection):

| Triple | Construction | Size / target / bound | Meets / attains |
|---|---|---|---|
| 7,5,4 | `trim (1,0,0): odd multiple construction` | 8 / 7 / 8 | yes / yes |
| 19,11,3 | `odd middle, even spacing` | 16 / 16 / 16 | yes / yes |
| 27,21,15 | `odd middle, even spacing` | 31 / 31 / 31 | yes / yes |
| 110,77,44 | `next family` | 115 / 115 / 115 | yes / yes |
| 133,95,57 | `seven-five-three family` | 142 / 142 / 142 | yes / yes |
| 150,99,27 | `separated-path` | 127 / 137 / 138 | no / no (menu limitation, not a counterexample) |
| 50,33,9 | `separated-path` | 43 / 45 / 46 | no / no (menu limitation; ratio family witness gives 45) |
| 99,79,23 | `separated-path` | 99 / 100 / 100 | no / no (menu limitation; interior-certificate witness gives 100) |

The deliberately altered pair in `--demo` (centre moved to the unused
tip) is rejected with `homometric: false`, confirming the checker
distinguishes multiplicities, not just supports.

## What is verified, what was recounted, what is open

- **Verified (proofs):** the signed-shell identity and `Q=0`
  equivalence; the Euler-cell / full-prefix attainment at every
  `t ≢ 1 (mod 2660)` (even and odd branches above); the odd-`t` upper
  bound (target is the maximum); the `50:33:9` Laurent identity
  (`--prove`); the residue-2660 negative: no affine exact-polynomial
  certificate with any period dividing 2660 attains the target at
  `t = 2660k+1` (24-period Hensel audit; delta=2660 collapses to three
  monomials forcing three signs to 0); the arithmetic-progression
  classification (root-of-unity necessity + block / multi-block
  sufficiency); the ODD-family constructions dispatched by the default
  command.
- **Witnesses recounted:** finite distance profiles for the scales and
  triples above (each command recounts all pairs; the gap witness, ratio
  witness and demo altered-pair rejection were run here). The t=1
  size-100 pair (4950 pairs/side) was recounted by both
  `gap_99_79_23.py --witness 1` and `residue_2660.py --prove`.
- **Open, stated plainly:** `T(99t,79t,23t)` at `t ≡ 1 (mod 2660)`,
  `t > 1` (first case `t = 2661`). Target proven to be an upper bound
  and proven unattainable by any full-prefix pair, and no affine
  exact-polynomial certificate exists — but attainment by an interior-hole
  (non-affine, non-cell) pair is neither proved nor refuted. The
  universal half-minus-one target for arbitrary triples also remains
  open in this project, and priority stays provisional.
