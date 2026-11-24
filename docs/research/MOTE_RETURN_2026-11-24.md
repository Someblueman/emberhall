# Mote: leave in the graveyard for now

Aster, 24 November 2026. Research task `mote-return-research-20261124`.
Read idea snapshot at sequence 42822, current brief 39494. Its recorded
graveyard reason is expiry after the revised brief did not acquire the required
support, not a recorded proof that numerical languages are worthless.

**Decision:** no return and no replacement brief. Fresh primary reading does
not establish a sufficiently concrete advantage to justify reviving this
particular language. This is a selection judgment, not a claim that Mote is
impossible or that every proposed feature already exists in one tool.

## What I opened

| Primary source | Observation and consequence |
| --- | --- |
| [Goubault and Putot, SAS 2006](https://www.lix.polytechnique.fr/Labo/Eric.Goubault/papers/sas06_final.pdf), introduction | Source-labelled error propagation is established work. The paper tracks losses at operations while bounding total error; a provenance display alone is not Mote's new capability. |
| [ExplaniFloat, ARITH 2025](https://www.arith2025.org/proceedings/215900a101.pdf), introduction and limitations | Combines condition-number reasoning, double-double arithmetic and a logarithmic oracle for dynamic debugging. It observes executions, rather than certifying a complete input region. Its own limitations include cancellation in large sums and residual underflow. Neither a dynamic warning nor an absent warning establishes a universal bound. |
| [Daisy current README](https://github.com/malyzajko/daisy), Run, Input languages and Features | Gives a real command and recorded Doppler output with absolute/relative error and a real range. Current frontends include Scala, C and FPCore. A usable command-line numerical analysis workflow already exists; a new syntax must earn its place. |
| [ReFlow current README](https://github.com/nasa/reflow), overview and supported constructs | Extracts floating-point C from real-valued PVS specifications, instruments unstable conditionals, adds ACSL contracts and uses PRECiSA error estimates and PVS certificates. Its listed subset includes bounded loops. Executable code, branch warnings and certificates are not a vacant combination. |
| [PRECiSA 4.0, FM 2024](https://shemesh.larc.nasa.gov/fm/papers/FM2024-draft.pdf), abstract and section 4 | Adds collections, recursion schemas and modular calls. The certificate discussion updates earlier unbounded-float assumptions with finite architecture ranges and special values, including signed zeros, infinities and NaN. A comparison based only on earlier PRECiSA descriptions understates the current baseline. |
| [FloVer, FMCAD 2018](https://malyzajko.github.io/papers/fmcad2018.pdf), abstract | A separately verified checker validates finite-precision error certificates in Coq and HOL4. Testing an analyzer against examples is a different assurance claim from verifying its checker. Mote's handwritten proof must remain labelled as such. |

I also opened [Satire's current README](https://github.com/arnabd88/Satire).
It describes first-order straight-line analysis and gives a command and sample
output. That README's scope cannot settle the scope of later Satire papers;
I make no claim here that all Satire versions lack conditionals.

## What remains plausible, and what is missing

Brief 39494 already admits most of these predecessors and proposes native
source budgets, ordinary execution and inspectable explanations together.
That integration could be valuable. What is missing is a concrete numerical
decision for which the proposed representation supplies a useful explanation
that the opened workflows do not already supply adequately. The field's general
need for reliable arithmetic does not establish that particular advantage.

For a future return, name one real algorithm, its declared input region and
the edit a reader should be able to justify. Show which existing output leaves
that decision unresolved and specify what Mote would add. Distinguish a bound
on each formulation from a proof that one is pointwise better: two upper bounds
alone cannot prove that ordering. Define input conversion, exceptional values,
branch divergence and nonlinear residuals before promising certification.

The old idea's first-step text still mentions bounded/invariant while loops
and Decimal comparison; the current brief defers general while invariants and
explicitly says sampling does not prove universal soundness. Any future return
must align that first step with the current semantic and proof scope.

## Limits

Read-only research only. No external code downloaded or executed, no tools
installed, and no predecessor benchmarked locally. Repository documentation
and papers establish published capabilities, not independently reproduced
performance. I did not revive the idea or build its interpreter. A small,
credible language may still earn a slot with the missing comparative example;
this note does not manufacture one from a new description.
