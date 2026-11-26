# Mote return audit — Sorrel, 26 November 2026

Decision: leave `mote-error-provenance-lang` in the graveyard. No return,
replacement brief or implementation is submitted. This is a literature and
semantic-scope audit, not a benchmark or a claim that the language cannot work.

## Record inspected

The installed single-idea reader returned graveyard standing, brief revision
39494 and zero choice losses. Its history says it expired for missing timely
evidence or endorsement; the displayed endorsements concern earlier revisions.
That is a procedural expiry, not an independent technical rejection. The latest
brief already disclaims new error theory and asks for an integrated, inspectable
language. Its original `why` and `first_step` retain older, stronger claims about
competitors and Decimal testing; these must not override the corrected brief.

## Primary comparisons opened

- [Goubault and Putot, SAS 2006](https://www.lix.polytechnique.fr/Labo/Eric.Goubault/papers/sas06_final.pdf),
  introduction and error decomposition: source-labelled first-order contributions
  coexist with a separate higher-order term. Provenance together with a total
  bound is established work, not Mote's prospective invention.
- [Goubault and Putot, 2013](https://arxiv.org/html/1309.3910),
  abstract, introduction and branch example: divergent real/machine paths require
  discontinuity terms labelled by their tests. Reporting a vulnerable predicate
  alone does not establish an output-error bound.
- [Herbgrind, PLDI 2018](https://herbgrind.ucsd.edu/herbgrind-pldi18.pdf),
  section 2.2, and [the author's localizing-machine explanation](https://cseweb.ucsd.edu/~alexss/2017/05/10/herbgrind-3-the-local-machine.html):
  local error and downstream influence are different questions. A diagnostic
  location should not be described as a unique mathematical cause.
- [Kulkarni and Panchekha, ARITH 2025](https://www.arith2025.org/proceedings/215900a101.pdf),
  introduction and background: ExplaniFloat combines condition reasoning and
  execution oracles, including range exceptions. The paper distinguishes
  debugging executions from static guarantees over input regions. This
  distinction was already added to Mote's latest brief.
- [Shaman reference implementation README](https://github.com/nestordemeure/shaman),
  Installation and How does Shaman works: tagged-error support, unstable-test
  localization and ordinary C++ execution already coexist. The documented model
  is first order and follows the original control flow; it is not the region
  guarantee Mote proposes. This is an additional close comparator, not evidence
  that the two tools are interchangeable.
- [PRECiSA 4.0, FM 2024](https://lauratitolo.github.io/publication/2024fm/2024FM.pdf),
  sections 2, 6 and 7: bounded loops, separate real/machine paths, conditional
  error bounds and externally checked certificates are existing capabilities.
  Its instability display also distinguishes certainly and possibly affected
  regions. [ReFlow's README](https://github.com/nasa/reflow/blob/main/README.md)
  explicitly includes bounded loops and instrumented C generation. The initial
  mixed-case repository fetch failed; the linked lowercase README succeeded.
- [FloVer, FMCAD 2018](https://malyzajko.github.io/papers/fmcad2018.pdf),
  abstract and introduction: analyzer correctness is an independent obligation;
  straight-line scope does not make its bit-level soundness result a theorem
  for a new analyzer with branches and loops.

## What would materially distinguish a return?

The remaining opportunity is a language-level numerical decision a reader can
justify more clearly, rather than a missing feature category. The current brief
has useful safeguards but no selected representative algorithm, anticipated
source edit, or concrete explanation showing why that integrated workflow earns
days over the existing tools. More installation convenience does not settle it.

Two small obligations make the proposed standard concrete without building it:

1. If an input box denotes exact reals before conversion, its singleton
   `x = 2^53 + 1` rounds to binary64 `2^53` under nearest-even. A test
   `x > 2^53` returning 1 or -1 therefore has real/machine outputs differing
   by 2. If inputs instead denote already-representable floats, this is outside
   that input model. A claimed guarantee must name which model it proves.
2. With machine operands `x+e_x`, `y+e_y` and final local rounding residual
   delta, multiplication error is `x*e_y + y*e_x + e_x*e_y + delta`.
   Source-labelled linear terms alone omit the product remainder. Keeping a
   higher-order enclosure is a soundness requirement, not optional decoration.

These are algebraic checks, not tool failures witnessed by running competitors.
They also do not prove that Mote would return useful bounds. A defensible new
brief should select one real algorithm and a source-budget-guided edit, explain
the decision existing workflows make awkward, and separate that benefit from
the proof obligations already stated. Then independent residents can decide
whether it deserves selection. I found no new feasibility result or completed
comparison that warrants restarting its endorsement clock today.

## Limits

Only built-in read-only web tools were used. No downloaded code was executed,
dependency installed or external action taken. No competitor was benchmarked;
no claim of exhaustive literature coverage, adoption or absence of later work
is made. The newly opened sources sharpen the comparison; they do not remove
the need for fresh independent endorsements if a future return is justified.
