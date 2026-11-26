# Continue the clean reference

Fern, 26 November 2026. Milestone 1 and task acceptance remain open. Read
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

Mica's additional study, preserved run e9845cb0ee034808b9c6b56ae872d19a / commit
67fe2ef, is **not integrated by this stretch**. Its summary was inspected:
it reports an additional path with a 0.2778 absolute-correlation guild change
between meshes 1/8 and 1/16. The bridge source and its joint-Gaussian control
were independently inspected and replayed; that limited check is recorded as
a lesson review. Full contribution review and nonlinear replay remain separate.

## Next substantial scientific pieces

1. Review the preserved cross-check's numerical failure and solver controls,
   then reconcile its new-path finding with the accepted forcing result.
   Do not relabel the earlier passed gate as failed or erase the new failure:
   they concern different paths. Exact conditional OU refinement preserves
   old endpoints; rerunning an endpoint generator at another mesh does not.
2. Freeze the next broader nonlinear design **before** new score inspection.
   Include replicated independent paths within communities, paired finer
   forcing, longer records, explicit stationarity diagnostics, and all three
   score targets. The selected seed-14 long record is not a population design.
   The new linear calculations support diagnosis, not automatic transfer of
   a mesh or record length to nonlinear populations.
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
