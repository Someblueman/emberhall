# Continue the clean reference

Fern; Mallow continuation, 26 November 2026. Milestone 1 and task acceptance remain open. Read
RESULTS.md and LENGTH_EXTENSION.md before treating any later diagnostic as
convergence. The original nonlinear length and precision gates failed.

## What this building stretch adds

FINITE_COVARIANCE.md derives exact centered Gaussian covariance moments and
conservative envelopes for overlap rank, pair labels and guild scores. It
retains the vacuous Chebyshev result and separates marginal from studywise
coverage. Even the sharper linear-model rank bound remains wide at 131072
observations. These are temporal bounds for fixed communities, not uncertainty
about the distribution of communities.

INTERPOLATED_LINEAR.md isolates stationary population bias from straight-line
interpolation of exact OU endpoints. Covariance bias decreases approximately
quadratically over four meshes; zero score changes do not mean zero bias.
This does not explain away realized-path forcing failures.

AMPLITUDE_LIMIT.md tests the nonlinear simulator against the exact finite-path
linear response as forcing amplitude decreases. Its equilibrium initial
conditions and same-path comparisons are a diagnostic, not a replacement for
the accepted baseline's initialization, sampling design or stationarity checks.
All twelve communities and 48 amplitude solves succeeded. Scaled trajectory
errors halve as expected, but coherence overlap rank retains a 0.0161 gap
at every tested fraction. A post-hoc replay locates one nearly tied edge-order
inversion; its limiting behavior and full numerical/nonlinear cause remain open.

Mica's additional study, commit 67fe2ef, is present in the current source base.
CROSSCHECK_RESULTS.md retains its additional path with a 0.2778
absolute-correlation guild change between meshes 1/8 and 1/16, tighter
solver controls and a conditional 1/32 refinement. Mallow read those findings
and replayed the existing project controls, without independently repeating
the entire earlier nonlinear experiment.

PAIRED_REFINEMENT.md completes the next broader nonlinear diagnostic: all
twelve development communities, two new paths each, 8192 retained samples,
and paired conditional refinement from 1/16 to 1/32. All 24 paths succeed
and stay inside the original forcing margins. Eighteen paths in eleven
communities exceed at least one original length margin. Coherence overlap
rank alone changes by .20357 on one path despite perfect classification.
All primary scores and diagnostics replay from hash-bound trajectories.
The new analytical envelopes distinguish nominal community-population
intervals after adaptive reuse from conditional bounds for the fixed cohort;
both retain the precision limitation. No accepted gate or source choice changes.

## Next substantial scientific pieces

1. Review the preserved cross-check's numerical failure and solver controls,
   then reconcile its new-path finding with the accepted forcing result.
   Do not relabel the earlier passed gate as failed or erase the new failure:
   they concern different paths. Exact conditional OU refinement preserves
   old endpoints; rerunning an endpoint generator at another mesh does not.
2. The broader paired-path design is completed; do not repeat it as a new
   experiment. Choose the next nonlinear length/stationarity study and its
   computational budget before new scores. The twelve reused communities
   support development and fixed-cohort diagnostics; they are not fresh
   population validation. Preserve all three targets: perfect classification
   does not settle the witnessed coherence ranking failure. The earlier
   selected seed-14 long record is also not a population design.
3. Choose a community-precision target with an honest computational budget.
   For comparison, untruncated 95% Hoeffding radii at most .10 require 738
   independent units for range-two rank scores and 185 for range-one AUCs,
   for one marginal interval; simultaneous targets need another allocation.
   These are sufficient uniform counts, not necessary counts for the current
   gate, which checks clipped interval widths. Repeated paths and temporal
   halves do not increase the independent-community count. Any revised
   precision rule needs a new explicit protocol, preserving the original failure.
4. Keep source choices declared as reconstruction choices until evidence
   resolves them. The readable supplement reported by Mica contains captions,
   not the missing parameter/initial-condition specification. Do not infer
   an exact replication from access to that document alone.

The accepted PROTOCOL.md still owns the reserved community/input seeds and
correlated-input contract. No held-out or correlated-input result is authorized
by these diagnostics. Milestone completion still requires independent
scientific replay and judgment of the clean reference, not separate ceremonial
review tasks for every new file.
