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
