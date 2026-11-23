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
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_template_320_decision.py
```

An exact command has no conflict limit, but its runtime is unbounded
and was not completed. The focused tests compare the engine with
exhaustive sign enumeration on 60 small integer systems and with
independent breadth-first original-tree distance censuses on fresh
unequal triples. They audit the control word at repetition counts 0, 1
and 4, reject a size-preserving sign swap, and reject altered limit
receipts. All 6 focused tests pass; the prior 7 integer-template tests
also pass.

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
