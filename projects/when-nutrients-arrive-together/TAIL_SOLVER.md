# Solver accuracy along the selected long record

Rook, 26 November 2026. Frozen before this control is solved. This is a
post-hoc numerical diagnostic of the previously selected community 9,
drive 0; it creates neither a new ecological replicate nor a passed gate.

Regenerate the exact original OU endpoints (seed 80900, mesh 1/16) and
conditional midpoints (seed 90900, mesh 1/32) through time 66048. Keep the
all-ones initial state and 512 burn-in. Repeat the entire solve at relative
tolerance 1e-11, absolute tolerance 1e-13 and maximum step 1/32, compared
with the original relative tolerance 1e-9 and same maximum step. Keeping
the maximum step fixes forcing interpolation and tests tolerance sensitivity;
it is not an independent integration method or a rigorous error bound.

Before solving, bind the prior protocol, receipt and complete trajectory by
SHA-256. Require the exact recorded prior trajectory identity. Preserve any
failure. Freeze settings, library versions and executable source identities.
Report log-trajectory errors, all four measures and all three score targets
on prefixes 4096, 8192, 16384, 32768 and 65536. Compare every score discrepancy
with the original .005 solver margin, retaining the actual differences.
This does not test forcing resolution along the tail or stationarity.

Budget: one additional long solve, expected about 25 minutes from the prior
1385-second solve; no outcome-driven extension. Arrays stay outside Git.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/tail_solver.py --baseline /tmp/nutrients-coherence-extension-fbc0 --output /tmp/nutrients-tail-solver-d200
```

After completion, replay all 180 before/after/difference score values and
all trajectory-error summaries from the hash-bound arrays, then export the
compact protocol, score table and summary. The exporter refuses changed
source, libraries, baseline identities or trajectory hashes. Score comparison
uses 1e-12 absolute/relative numerical tolerance, not a claim of symbolic
equality; trajectory-error reductions use the same recorded operations.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/tail_solver_report.py --baseline /tmp/nutrients-coherence-extension-fbc0 --study /tmp/nutrients-tail-solver-d200 --output /tmp/nutrients-tail-solver-report-d200
```

## Completed full-record tolerance control

The tighter solve succeeded in 2391.9 seconds (39.9 minutes), compared with
1385.2 seconds for the saved baseline. Retain this measured cost rather
than the optimistic 25-minute estimate. Minimum consumer abundance was
6.350865. All sixty before/after score comparisons are unchanged, including
the entire 65536-observation window; maximum absolute score difference is
zero at ordinary recorded precision, inside the original .005 margin.
This does not assert exact trajectories: maximum log-abundance difference
is 5.80e-8 and RMS difference 6.33e-9 over the full record.

| Prefix length | Maximum log-abundance difference | RMS difference |
|---:|---:|---:|
| 4096 | 3.6083e-8 | 6.3421e-9 |
| 8192 | 3.6949e-8 | 6.2090e-9 |
| 16384 | 4.3181e-8 | 6.3008e-9 |
| 32768 | 5.3902e-8 | 6.3070e-9 |
| 65536 | 5.7998e-8 | 6.3280e-9 |

The exporter independently recomputed all 180 before/after/difference
score values from the two hash-bound trajectories and replayed every
trajectory-error reduction and margin decision. Four copied-receipt
tamper controls rejected changed score values, protocol, numerical source
identity and refined trajectory identity. Original arrays were untouched.
The compact tail-solver-scores.csv retains all twenty measure/window rows;
tail-solver-protocol.json and tail-solver-summary.json bind exact settings,
source identities, full receipt, exporter and both trajectory identities.
Full arrays remain outside Git and are regenerated from the recorded seeds.

This rules out score sensitivity to the tested tolerance change as an
explanation of this selected record's witnessed length changes. In particular,
the absolute-correlation rank change .10714 from 32768 to 65536 remains.
It is not a second integration-method check, a full-tail forcing refinement,
a rigorous ODE error bound, a new independent path or population evidence.
The original failed length and precision gates remain failed, and milestone
acceptance and the reserved intervention remain blocked on the stated
scientific prerequisites rather than being certified by this control.
