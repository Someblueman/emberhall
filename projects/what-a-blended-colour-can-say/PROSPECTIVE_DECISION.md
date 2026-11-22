# Stop the comparison series; leave M3 unresolved

Fern, 22 November 2026. Recommendation for the project owner; this document
does not change an outcome, accept a report, or authorize another experiment.

## Evidence and its limits

The [first comparison](COMPARISON_RESULT.md) was INCONCLUSIVE: both views
scored 20/20, with clarity totals 17 (distributions) and 20 (atlas), a gain of
3/5 rather than the required 1. The [second frozen protocol](COMPARISON_V2.md)
addressed the first reader's observation-scope confusion and used new cases.

Mallow's second report, `COMPARISON_V2_RESULT.md`, is preserved in contribution
`6342732407eb330f9aa15bca448036643fdb06f6`, run
`e5105308854445f59fa27b804718a5b2`, finished at journal 30270. I obtained its
complete text through fixed-channel path inspection, without integration or
acceptance. Its independent source review remains pending. Report SHA-256:
`3bf1ce2aa26ddb7d9861c40ca79f4c88e37a0d2caab9c182851291e6354966a3`.

The report records another 20/20 tie, clarity totals 18 and 23, and an
INCONCLUSIVE frozen execution. Baseline ratings were 4,3,4,4,3; atlas ratings
were 5,5,5,4,4. It records seals at 30237 and 30262 before opening answers,
phone/desktop checks, identical regeneration and independent certificate
reconstruction. Those remain the assessor's evidence, not checks repeated or
independently accepted here. No reader-benefit claim or M3 pass follows.

## Checked arithmetic diagnosis

`comparison_v2.score` delegates to `comparison.score_responses`. The latter
divides each five-rating sum by 5, then subtracts the two binary floating-point
means. Thus `23/5 - 18/5` evaluates to `0.9999999999999996`, below `1.0`, whereas
the rational difference is exactly `(23-18)/5 = 1`. This is a numerical boundary
defect, not a measured clarity shortfall. It does not turn the frozen result
into PASS, nor establish that the atlas is ineffective.

Let A and D be integer atlas and distribution clarity totals, and a and d
their objective scores. The prose gates can be expressed exactly as:

- Fail if a view is unreadable, a < 17, any atlas classification is wrong,
  A < 20, or d > a.
- Otherwise pass if a-d >= 2, or if a >= 18, d >= 18 and A-D >= 5.
- Otherwise remain inconclusive. Probability-answer tolerance is the existing
  exact rational 1/200; it needs no floating-point approximation.

These are diagnostic equivalents of the prose, not a replacement scorer.
No epsilon, rounded difference or altered threshold is needed.

With readable views, perfect objective scores and correct classifications:

| D | A | Exact gain | Frozen float gain | Prose margin / frozen decision |
| ---: | ---: | ---: | ---: | --- |
| 15 | 20 | 1 | 1.0 | met / PASS |
| 16 | 21 | 1 | 1.0 | met / PASS |
| 17 | 22 | 1 | 1.0000000000000004 | met / PASS |
| 18 | 23 | 1 | 0.9999999999999996 | met / INCONCLUSIVE |
| 19 | 24 | 1 | 1.0 | met / PASS |
| 20 | 25 | 1 | 1.0 | met / PASS |
| 18 | 22 | 4/5 | 0.8000000000000003 | missed / INCONCLUSIVE |
| 17 | 23 | 6/5 | 1.1999999999999997 | exceeded / PASS |

A temporary standard-library calculation checked all 441 pairs of legal
five-rating totals (5 through 25), comparing the existing scorer on synthetic
perfect-objective answers with the integer gates. The sole outcome mismatch
was D=18, A=23. The first result's D=17, A=20 remains inconclusive. No sealed
reader response was rescored. The essential calculation is reproducible with:

```python
from fractions import Fraction
mismatches = [(d, a) for d in range(5, 26) for a in range(20, 26)
              if (a/5 - d/5 >= 1) != (a-d >= 5)]
assert mismatches == [(18, 23)]
assert Fraction(23-18, 5) == 1
```

## Prospective decision and finite stop

**Recommend zero further reader attempts in this comparison series.** Fixing
the arithmetic is a deterministic engineering question, answered above without
sampling anyone. A third new reader under the same design would supply another
subjective rating, but leave the same case-difficulty and presentation-order
confounds. Selecting a new attempt now because the last one narrowly missed a
software gate risks making the series a search for a passing draw.

The distinct unanswered scientific question is whether interval-first views
improve interpretation across readers and cases when case difficulty and order
are controlled. The current single-reader, different-set comparisons cannot
settle it; both also hit the objective-score ceiling. A study addressing that
question would need a separately justified design and resources. No such study,
new pack, reader recruitment or conditional retry is proposed or authorized here.

For the owner: retain both INCONCLUSIVE outcomes and the existing M1/M2 work;
leave M3 open and the benefit claim unestablished. Obtain the already-required
independent review of Mallow's report, including its seals and stated limits.
That review may correct the record of evidence but is not a third assessment or
a route to relabel either result. This series stops regardless of that review's
outcome: no repaired rescore, same-reader retest, new-reader substitution,
additional pack or Gallery promotion to meet the existing gate. Any future
research must be a new, explicitly authorized question and design, not an
automatic next attempt. Do not mark the project or M3 complete on this decision.

Only this document and [README.md](README.md) change. Both frozen packs,
protocols, scorers, results and response seals remain unchanged.
