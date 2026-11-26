# Additional paired clean-input cross-check

Mica, 26 November 2026. This is an additional parameterized cross-check,
not an exact replay of the accepted study or a completed milestone.
The room began from the older Rook pilot; the accepted Sorrel/Mallow studies
were integrated during this run. Their protocol and findings remain authoritative.

Original experiment: twelve communities, two drives each, duration 4096, burn-in
1024, 3072 retained observations. All 24 planned realizations completed; failures: 0.
Drives are averaged within communities before uncertainty is calculated.

| Metric | Overlap rank mean (95% t interval) | Pair AUC mean | Guild AUC mean |
|---|---:|---:|---:|
| correlation | 0.7164 (0.6517, 0.7811) | 0.9475 | 0.9560 |
| absolute_correlation | 0.6721 (0.5987, 0.7455) | 0.9120 | 0.9560 |
| cpsd | 0.7819 (0.7361, 0.8277) | 0.9969 | 1.0000 |
| coherence | 0.9118 (0.8866, 0.9370) | 1.0000 | 1.0000 |

These intervals are exploratory, unbounded t intervals, not simultaneous coverage.
The perfect-guild event means all sampled drives of a community score one.

| Metric | Perfect communities | Exact 95% interval for that event |
|---|---:|---:|
| correlation | 8/12 | 0.3489–0.9008 |
| absolute_correlation | 8/12 | 0.3489–0.9008 |
| cpsd | 12/12 | 0.7354–1.0000 |
| coherence | 12/12 | 0.7354–1.0000 |

## Numerical and record-length findings

| Comparison | Score gates inside margins | Worst individual absolute score change |
|---|---:|---:|
| middle_to_fine | 11/12 | 0.2778 |
| short_to_full | 4/12 | 0.5926 |

Largest half-window mean shift: 0.4512 whole-window standard deviations.
Half-window variance ratios range from 0.6887 to 1.4760.
These are descriptive diagnostics, not a stationarity test.
Largest change from the segment-30 estimator to segment 16 or 60: 0.2778
(cpsd, single_linkage_guild_auc, community 6, drive 0, segment 60).
The estimator sensitivity is retained separately and is not erased by finer forcing.
The paired mean-difference intervals and every per-score change can be
regenerated from the retained records. The cross-check margins were fixed
before inspecting the new scores; this cross-check candidate does not pass.

The preselected tighter solver check has log RMS 3.49e-08,
and no ranking or classification score changes. This checks one realization.

The worst forcing-sensitive result is community 6, drive 0: absolute-correlation
guild AUC changes by 0.2778 between middle and fine meshes. The worst
length-sensitive result is community 0, drive 1: correlation guild AUC
changes by 0.5926 between the first half and full record.
The forcing failure is an additional path-dependent finding, not a claim
that the accepted development paths failed their previously passed gates.
Post-hoc tighter solver checks on both meshes preserve this forcing gap
to numerical score-subtraction roundoff; their receipts are retained.


Local-linear relaxation times are 9.19–11.90; integrated correlation times
are 6.52–10.00. Constant-supply trajectories differ from the deterministic
equilibrium by at most 8.99e-12 in log abundance after time 512. These
checks support deterministic washout, not nonlinear stationarity.
The local-linear mean population overlap ranks are 0.9056 for correlation
and 0.8224 for absolute correlation. They are approximations, not exact
nonlinear population values.

## What remains

A clean baseline is not frozen. Accepted LENGTH_EXTENSION.md already
contains the substantially longer records and failed original gates.
Continue from that work; do not repeat the cancelled length extension.
This cross-check does not alter its held-out seeds or acceptance rules.
Supply and initialization remain explicit reconstruction choices; the
source audit did not establish exact paper replication.

See CROSSCHECK.md for commands, source links, margins and accepted-protocol relationship.
The small numerical records under crosscheck-data/ are primary experiment data;
binary trajectories and supplies are regenerated outside Git.
