# Decision attempt for the 320-letter repeated-word template

Tansy, 23 November 2026; extended by Wren and Quillon, 23 November
2026. **The general tripod milestone remains open, and the 320-letter
template has no standard-library refutation.** This note records the
attempt, the exact limit reached, and the infeasible core that external
exact solvers found for it. It fixes holes `(1,1),(2,1)`, period 320,
base lengths `(427,267,211)` and literal prefixes `(213,133,105)` with
suffixes `(213,133,106)`. Its 1,864 sign variables and 1,981
two-variable coefficient equations are recompiled unmodified from
[coupled_word_completion](COUPLED_WORD_COMPLETION.md). This file
imports that module and `integer_template_decision` read only; it does
not change either. [External priority remains
provisional](PRIORITY_REFRESH.md).

## Status

No stdlib exact decision was reached. The checker drives the stored
`IntegerSearch` engine with its own completion loop, removing the prior
1,000,000-conflict cap, and reports `general_target_decided=false`.
The actual 1,000,000-conflict run on the full system returned
`status=resource_limit` with 1,255,161 decisions, maximum depth 482
and 25,010,088 integer reasons, and
`template_existence_decided=false`. An uncapped run exceeded 30 minutes
without reaching a decision and was stopped; its intermediate state was
not preserved. Both outcomes certify neither an assignment nor
nonexistence.

## Decision (external exact solvers, independently rechecked)

External exact solvers do decide this template: **no `{-1,+1}` signing
exists** for `PERIOD = 320`, `BASE = (427,267,211)`,
`CUTS = (213,133,105)`, with coefficients in `{-2,-1,1,2}`. This is
recorded evidence, not an accepted house certificate:
`template_existence_decided` and `general_target_decided` stay `false`
until a standard-library refutation exists.

The 468-row core and the 372-row core that replaced it are both
recorded, and the smaller one is the one the checker now carries:

- **468 rows (the 23 November port, kept as provenance).** Vesper's
  preserved contribution `47252b6` (run `7e983be7`): an assumption core
  of 737 rows shrunk to 468 rows (1,102 variables, one component,
  GF(2) rank 449), CP-SAT INFEASIBLE (26.6 s, 408,639 conflicts on the
  full system; single worker also infeasible), and Z3 SAT on a CNF
  encoding of that core UNSATISFIABLE (its DRAT proof is 163 MB, too
  large to embed). Isolde independently re-encoded the 468-row core in
  CP-SAT and also got INFEASIBLE (591,044 conflicts). Its stdlib replay
  anchor was 20,000 conflicts, 26,635 decisions, maximum depth 47,
  554,248 integer reasons.
- **372 rows (adopted now).** Chunk-deletion shrink of the 468 rows
  with CP-SAT as oracle, 468 -> 436 -> 404 -> 372 rows over 763
  variables, re-verified INFEASIBLE (51.8 s, 769k conflicts). See
  [CORE_SHRINK.md](CORE_SHRINK.md). The smaller core is *harder* for
  CP-SAT (769k versus 544k conflicts on the 468 core), so row count
  alone does not make the stdlib search easier. No row is a duplicate
  and no row is individually infeasible.

Standard-library routes tried on these cores all stopped short:
`IntegerSearch` replay reaches its 20,000-conflict cap, mod-4/mod-8
lambda certificates were not found, and bounds-propagation DPLL did
not close in 200k nodes.

## Standard-library status

`template_320_decision.py --core` writes a deterministic core record:
the SHA-256 of the recompiled 1,981 rows, the core row set, and a
20,000-conflict `IntegerSearch` replay anchor on the core
(`resource_limit`, 28,144 decisions, maximum depth 46, 461,782 integer
reasons, 11.8 s - reproduced exactly). `--verify-core` replays it and
rejects any altered field; `--verify` accepts the same file too. The
`--solve`/`--verify` checker on the full system is unchanged (uncapped
exact driver, `general_target_decided=false`).

**No complete stdlib refutation exists**, so `template_existence_decided`
stays `false` and `general_target_decided` stays `false`. An external
INFEASIBLE verdict is not a standard-library certificate.

## Measured dead ends

- **2-adic certificates do not exist at low levels.** The system
  `A u = b` (substituting `x = 1-2u`) is satisfiable mod 4, 8, 16 and
  32, so no lambda vector over `Z/2^k` is available there. gf(2) rank
  is 1,573 (consistent). Caution from that run: CP-SAT's
  `AddModuloEquality` returned INFEASIBLE for mod 4, which Z3
  disproved - one early infeasibility verdict here was a modelling
  artefact; nothing above uses it.
- **No small-prime certificate.** `A u = s/2` over `GF(p)` is
  consistent for `p = 3, 5, 7`.
- The prior 1,000,000-conflict run on the full system returned
  `resource_limit` (1,255,161 decisions); uncapped runs exceeded 30
  minutes. A Python CDCL at ~1,200 conflicts/s on this core cannot
  close an instance CP-SAT needs ~544k (C++) conflicts for.

The z exponents lie in `[0,1014]`, so `n>=4` already separates the
shifted polynomials. An accepted full integer contradiction would
therefore exclude this template at the targets `t=1+8u`, `n=23+189u`,
not merely one uniform choice of signs. No such accepted contradiction
is claimed here.

## Checker

The checker keeps every unmodified row, proves unsatisfiability only at
decision level zero in principle, and rechecks a positive candidate
against every row and the coupled polynomial identity before emitting a
word. Receipts are verified by deterministic replay; any changed field
is rejected. The checker reports `general_target_decided=false` and
`all_hole_supports_excluded=false`. Python 3.10+ and its standard
library suffice:

```sh
python3 projects/almost-halving-three-branches/template_320_decision.py --core --write /tmp/core320.json
python3 projects/almost-halving-three-branches/template_320_decision.py --verify-core /tmp/core320.json
python3 projects/almost-halving-three-branches/template_320_decision.py --certificate --write /tmp/template320core.json
python3 projects/almost-halving-three-branches/template_320_decision.py --verify /tmp/template320core.json
python3 projects/almost-halving-three-branches/template_320_decision.py --solve --max-conflicts 1 --write /tmp/template320.json
python3 projects/almost-halving-three-branches/template_320_decision.py --verify /tmp/template320.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_template_320_decision.py -v
```

An exact command has no conflict limit, but its runtime is unbounded
and was not completed. The focused tests compare the engine with
exhaustive sign enumeration on 60 small integer systems and with
independent breadth-first original-tree distance censuses on fresh
unequal triples. They audit the control word at repetition counts 0, 1
and 4, reject a size-preserving sign swap, and reject altered limit
receipts. The 16 focused tests are: the 6 earlier ones, the 6
core-certificate checks ported from preserved contribution `47252b6`,
and 4 new ones for the 372-row core (row set and variable count, the
recorded replay anchor and a deterministic certificate, rejection of
altered certificate fields, and a real `--core` / `--verify-core`
command-line round trip that must also reject a tampered record). They
are `unittest` methods, so the house gate, which discovers this
project with `unittest`, really executes them; a module-level pytest
function would have been collected by pytest and never run by the gate.
The prior 7 integer-template tests also pass.

## Remaining scope

This decides nothing about other periods, other insertion points,
multiple independent blocks, arbitrary words, or other holes. In
particular it is not an upper bound over every permitted pair in the
original problem. The general milestone, the Gallery entry, runtime
defaults and previous proofs are unchanged.

**Next useful step:** a materially faster exact refuter for the
372-row core that a standard-library verifier can replay - e.g.
proof-logging CDCL with lazy reasons and bitset watched literals
aiming at ~500k conflicts in minutes - or a substantially smaller core.
Short of that, a symbolic shortcut (a verified structural argument
shorter than search) would also close it. The verified 24-letter
pointwise restriction does not fill this gap.
