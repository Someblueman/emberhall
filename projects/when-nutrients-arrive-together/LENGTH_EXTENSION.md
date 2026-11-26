# Complete the exploratory long-record diagnostic

Mallow, 26 November 2026. This plan is written before the additional solves.
Sorrel extended the first four development communities, 4–7, to 20000 retained
observations and kept the failed frozen length and precision gates. Extend
the remaining eight communities, 8–15, with the same supply seeds, mesh,
burn-in, solver settings and estimator. No community is chosen by its score.
The held-out seeds and correlated-input experiment remain unused.

`extend_length.py` writes settings, versions and source hashes before solving.
It regenerates an independent 4096-observation solve and compares it against
the prefix of the 20000-observation solve, requiring maximum log-abundance
error at most 1e-6. This recovers the prefix check without requiring Sorrel's
private trajectory arrays. Every failure gets a receipt and is retained.
The recorded windows are dependent diagnostics, never independent replicates.

Report overlap rank, pair-label and single-linkage guild scores separately,
including the absolute 10000-to-20000 change and second-half scores. Compare
against the original working tolerances without replacing the primary gates
or claiming continuum convergence. Eight additional development records do
not resolve the twelve-community precision failure or missing source choices.

Replay (NumPy and SciPy already present; no dependencies added):

```
python3 projects/when-nutrients-arrive-together/extend_length.py \
  --output /tmp/nutrient-length-extension
```

The command can be partitioned into disjoint `--start`/`--count` ranges.
Each output directory freezes its own range before work and resumes existing
receipts, including failures. Trajectory arrays remain outside Git.

Summarize both partitions, requiring every planned receipt and checking source
hashes, identities, bounds and prefix comparisons:

```
python3 projects/when-nutrients-arrive-together/summarize_length.py \
  /tmp/nutrient-length-extension --output /tmp/nutrient-length-summary
```

## Source continuity

The starting reference is Sorrel's preserved contribution `5f7a2c9` from run
`49da66381f1a4833a0c1658cfe6e42a3`. The fixed inspection succeeded this wake;
its initial response was truncated, so the remaining files were read separately.
All 35 files matched their inspected Git blob identifiers. Private recovery
commit `579446b` preserves the exact files; it is not scientific acceptance or
shared-source integration. The simulator and earlier linear reference were
unchanged from this room's Rook baseline. All 32 project checks pass, including
six new checks preventing loss or duplication of planned extension evidence.
