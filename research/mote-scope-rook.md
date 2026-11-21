# Mote: a defensible first language

Rook, 21 November 2026. Research for task `rook-mote-scope-4686`.
This corrects shelf brief 28875; replacement 28990 was accepted. Its prior check
must be repeated. This note is not an implementation or a soundness proof.

## Finding

Keep a smaller language proposal, conditional on a real semantic argument and useful
diagnostics. The earlier brief promises too much from sampled validation: arbitrary
loop invariants, two floating-point formats, square roots, source attribution and
universal error bounds. Its account of the alternatives also needs updating.

The worthwhile difference is an inspectable, standard-library language in which
source-level error budgets and provenance are part of running a program. Neither
roundoff analysis nor provenance is new. Convenience alone does not establish
usefulness: the first programs must show that a reader can make a justified change.

## Sources opened

1. [Goubault and Putot, Static Analysis of Numerical Algorithms, 2006](https://www.lix.polytechnique.fr/Labo/Eric.Goubault/papers/sas06_final.pdf),
   introduction, sections 2.1 and 3.4. Fluctuat already separates source-labelled
   first-order errors from higher-order remainders. It also accounts for error
   introduced by the analyzer's own arithmetic. A single nextafter at the end of
   a calculation is not a replacement for this obligation.
2. [Goubault and Putot, Robustness analysis, 2013](https://arxiv.org/html/1309.3910),
   abstract and sections 3–4. Divergent real and floating-point branches require
   a discontinuity term. A warning about a branch alone does not make the error
   bound sound. Their method already attributes these terms to tests.
3. [Tirpankar, Das and Gopalakrishnan, Satire, 2025](https://arxiv.org/html/2503.05924v1),
   abstract, section 7 and conclusion. It handles conditionals and mixed precision
   in loop-free programs. Calling it merely a straight-line alternative misses
   a material part of the current paper. This does not establish loop invariants.
4. [Daisy's current repository](https://github.com/malyzajko/daisy) and
   [Abbasi and Darulova, modular analysis, 2023](https://malyzajko.github.io/papers/sas2023a.pdf),
   README and introduction. The repository lists modular analysis, array-like
   structures and several input frontends. The 2023 paper analyzes nonrecursive
   procedures while excluding loops and conditionals in its stated scope. A 2017
   quotation cannot characterize every feature of today's repository.
5. [NASA ReFlow](https://github.com/nasa/reflow), README. This existing tool produces
   C from a real-valued specification, instruments unstable tests, supports bounded
   loops, and uses PRECiSA certificates. Mote must not claim that this combination
   of capabilities is absent from open tools.
6. [Becker et al., FloVer, 2018](https://malyzajko.github.io/papers/fmcad2018.pdf),
   section V. Its theorem separates types, real ranges, machine ranges and errors.
   The IEEE bridge states an additional no-subnormal premise. Its reported division
   bug illustrates why the floating denominator needs checking as well as the real
   denominator. These are standards to meet, not guarantees Mote inherits.
7. Python's [Fraction documentation](https://docs.python.org/3/library/fractions.html)
   and [nextafter documentation](https://docs.python.org/3/library/math.html#math.nextafter).
   Exact rational representations are available in the standard library; nextafter
   moves to an adjacent float. Neither API certifies a composed abstract interpreter.

Access limits: both Fluctuat overview URLs returned 403, and the original NASA PDF
URL was inaccessible. The directly opened papers and NASA repository above supply
the substantive comparison; I did not verify the unavailable pages' quotations.
No downloaded code was executed and no package was installed.

## Two arithmetic probes

These small local calculations challenge the proposed checks; they are not a Mote
prototype. On this room's Python, for the finite binary64 input `x = 1e100`, the
expression `(x + 1) - x` produced:

| Evaluation | Result |
| --- | --- |
| Python binary64 arithmetic | 0 |
| Exact rational arithmetic on that same binary64 input | 1 |
| Decimal with precision 80, starting with Decimal.from_float(x) | -60813469985856815104 |

Thus a fixed 80-digit Decimal calculation is not universally exact ground truth.
For the smallest positive binary64 value times one half, binary64 returns zero;
the exact absolute error is 2^-1075. A relative-only local rounding bound misses
that case. These observations do not test any existing analyzer.

## Proposed boundary

Start with binary64 round-to-nearest, exact rational source constants and box
endpoints, arithmetic, let-bindings, conditionals, and literal-count loops with an
explicit analysis cap. Specify whether a box describes real inputs before rounding
or already represented machine inputs; account for conversion accordingly. Omit
fixed-point while analysis, square root and mixed precision from first acceptance.

For every accepted bound, define the related real and machine executions. Preserve
source and iteration identity for contributions, a separately named nonlinear
remainder, and any branch-divergence contribution. Bound radii are conservative
attribution under a chosen decomposition, not percentages of unique causal blame.
Prove composition through operations, joins and finite unrolling. Include rounding
inside the analyzer or use exact arithmetic there. Check both real and machine
division domains. Handle subnormals explicitly or return unknown before certifying
their path. Overflow, resource exhaustion and unsupported semantics also return
unknown; they do not become successful checks.

Source budgets and comparisons should distinguish proved bounds, failed budget
proofs and observed witnesses. A larger upper bound does not prove that formulation
A is less accurate than B on every input. A witness is one input, never a worst-case
certificate. High precision and random tests are useful bug finders, not a proof.

## First acceptance

Deliver a real command-line interpreter for `.mote` source, its semantic document,
and three small programs: equivalent cancellation-prone formulations, a literal
bounded accumulation, and a branch that can differ between real and float. Each
program runs and gives an attributable bound or an explicit unknown result.
A non-author must reconstruct the soundness argument for the supported subset,
check the numerical boundary cases, and run exact small-domain checks independently
of the bound calculation. They must also use a diagnostic to choose and explain a
source edit on a program they did not write. Reject the milestone if nothing useful
is certifiable, if a needed remainder is hidden, or if the supported language adds
no demonstrable benefit beyond the cited tools. No first-of-its-kind claim is made.
