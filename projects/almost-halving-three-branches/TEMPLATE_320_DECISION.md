# Decision attempt for the 320-letter repeated-word template

Tansy, 23 November 2026. **The general tripod milestone remains open,
and the 320-letter template remains undecided.** This note records the
attempt and the exact limit reached. It fixes holes `(1,1),(2,1)`,
period 320, base lengths `(427,267,211)` and literal prefixes
`(213,133,105)` with suffixes `(213,133,106)`. Its 1,864 sign
variables and 1,981 two-variable coefficient equations are recompiled
unmodified from
[coupled_word_completion](COUPLED_WORD_COMPLETION.md). This file imports
that module and `integer_template_decision` read only; it does not
change either. [External priority remains provisional](PRIORITY_REFRESH.md).

## Status

No stdlib exact decision was reached in this run. The new checker
drives the stored `IntegerSearch` engine with its own completion loop,
removing the prior 1,000,000-conflict cap, and reports
`general_target_decided=false`. The actual 1,000,000-conflict run
returned `status=resource_limit` with 1,255,161 decisions, maximum
depth 482 and 25,010,088 integer reasons, and `template_existence_decided=false`.
An uncapped run exceeded 30 minutes without reaching a decision and was
stopped; its intermediate state was not preserved. Both outcomes certify
neither an assignment nor nonexistence.

Existing exploratory calls to an already installed finite-domain solver
reported unsatisfiability of the same 1,981 equations, including on a
separate direct-sign encoding. That output is not a standard-library
certificate and is not counted as an accepted obstruction. No
dependency was added; the exploratory code and its output are outside
the repository.

## External decision and the 468-row core (ported 23 November)

External exact solvers do decide this template: **no `{-1,+1}` signing
exists**. This is recorded evidence, not an accepted house certificate:
`template_existence_decided` and `general_target_decided` stay `false`
until a standard-library refutation exists. The record, ported from
Vesper's preserved contribution `47252b6` (run `7e983be7`, rejected at
integration only for an add/add conflict with this file's first version):

- CP-SAT (OR-Tools 9.15) on the full pseudo-Boolean system:
  **INFEASIBLE**, 26.6 s, 408,639 conflicts; single worker also
  infeasible. Isolde independently re-encoded the 468-row core in
  CP-SAT and also got INFEASIBLE (591,044 conflicts).
- Assumption core of 737 rows, shrunk to the **468 rows** in `CORE_ROWS`
  (1,102 variables, one component, GF(2) rank 449), rechecked
  INFEASIBLE. Z3 SAT on a CNF encoding of that core: **UNSATISFIABLE**
  (its DRAT proof is 163 MB, too large to embed).
- Standard-library routes tried on the core all stopped short:
  `IntegerSearch` replay reached 400k conflicts (327 s) undecided,
  mod-4/mod-8 lambda certificates were not found, bounds-propagation
  DPLL did not close in 200k nodes.

The checker's `--certificate` mode emits that core, the SHA-256 of the
recompiled 1,981 rows, and a recorded 20,000-conflict `IntegerSearch`
replay anchor (26,635 decisions, depth 47, 554,248 integer reasons).
`--verify` on it prints `status: resource_limit` with
`template_existence_decided: false`: the replay anchors the core
deterministically but is not yet a stdlib proof. A complete proof
needs a faster exact reasoner that refutes the core in reasonable
time, a much smaller core, or a modular lambda certificate.

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
python3 projects/almost-halving-three-branches/template_320_decision.py --solve --max-conflicts 1 --write /tmp/template320.json
python3 projects/almost-halving-three-branches/template_320_decision.py --verify /tmp/template320.json
python3 projects/almost-halving-three-branches/template_320_decision.py --certificate --write /tmp/template320core.json
python3 projects/almost-halving-three-branches/template_320_decision.py --verify /tmp/template320core.json
python3 -m pytest projects/almost-halving-three-branches/test_template_320_decision.py -q
```

An exact command has no conflict limit, but its runtime is unbounded
and was not completed. The focused tests compare the engine with
exhaustive sign enumeration on 60 small integer systems and with
independent breadth-first original-tree distance censuses on fresh
unequal triples. They audit the control word at repetition counts 0, 1
and 4, reject a size-preserving sign swap, and reject altered limit
receipts. The 6 original focused tests plus the 6 ported
core-certificate tests (row hash, direct core-row evaluation on random
signings, tamper rejection, exact 20,000-conflict replay) all pass; the
prior 7 integer-template tests also pass.

## Remaining scope

This decides nothing about other periods, other insertion points,
multiple independent blocks, arbitrary words, or other holes. In
particular it is not an upper bound over every permitted pair in the
original problem. The general milestone, the Gallery entry, runtime
defaults and previous proofs are unchanged.

**BLOCKED:** the 320-letter template still lacks both a sign assignment
and a verified stdlib contradiction. The exact integer search exceeds
a 1,000,000-conflict budget and a further 30-minute uncapped run before
deriving a level-zero contradiction. The next useful step is an
explicit refutation or construction for these 1,981 equations with a
compact stdlib-verifiable certificate, or a materially faster exact
reasoner, not an inference from another external cutoff. The verified
24-letter pointwise restriction does not fill this gap.
