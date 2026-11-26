# Initial-condition memory under a shared input

Rook, 26 November 2026. Frozen before the new solves. This diagnostic tests
whether the accepted 512-unit burn-in removes the difference between two
specific starting states in the twelve development communities. It cannot
prove nonlinear stationarity, uniqueness of a stationary law, convergence
from every state, or sufficient finite-record precision.

Use communities 4–15 without score selection. For each community, compare
the accepted all-ones amounts with its positive deterministic equilibrium
under mean supply. Both ecological states receive exactly the same forcing.
Use drive zero of the paired-refinement study: OU seed 80000+100*community,
conditional bridge seed 90000+100*community, coarse mesh 1/16 and fine mesh
1/32. Generate only its first 1024 units. Both OU generation and midpoint
refinement consume random numbers in temporal order, so these are the same
prefixes, not new input replicates. The scientific unit is still a community;
the two initial conditions are a paired comparison, never independent data.

Solve the two states jointly, with independent ecological equations and
shared forcing, so they use the same adaptive solver steps. Unit-spaced
observations include time zero and end at 1023. Use relative tolerance 1e-9,
absolute tolerance 1e-11 and maximum step 1/32. Preselected community 4
receives a second solve at tolerances 1e-11/1e-13 and maximum step 1/64.
The tighter solve checks numerical sensitivity of this diagnostic, not a
uniform bound on other communities. A constant-supply control compares the
joint solver against the original simulator and checks equilibrium invariance.

Record maximum consumer log differences at 0, 32, 64, 128, 256, 512 and 1023,
maximum post-burn resource and log differences, and log differences divided
by the all-ones run's retained species standard deviations. Compute all
four measures and all three score targets separately on the 512 retained
samples, segment 30. Record descriptive half-window shifts and variance
ratios for both initializations. Small coupling differences do not imply
small estimator variance; near ties may change discrete rankings even when
trajectories nearly agree. No success cutoff or baseline gate is introduced.

Preserve every supply, resource, extinction or numerical failure. Save both
trajectories, including the tighter control, outside Git; bind them to receipt
hashes. Before summarizing, replay all diagnostics from the saved arrays.
Freeze source hashes, settings and library versions before the first solve.
The computational budget is twelve joint solves plus one tighter control.
No source conventions, held-out reservation or original failed gate changes.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/burn_coupling.py --output /tmp/nutrients-burn-coupling --report-only
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/burn_coupling.py --output /tmp/nutrients-burn-coupling --start 4 --stop 10
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/burn_coupling.py --output /tmp/nutrients-burn-coupling --start 10 --stop 16
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/burn_audit.py /tmp/nutrients-burn-coupling --output /tmp/nutrients-burn-audit
```

Initialize before launching the disjoint partitions. Each worker owns its
seed-specific receipt and arrays. Only report after the workers stop; an
incomplete report remains explicitly incomplete. Failed receipts are retained
on resume. New settings or source hashes require a new output directory.

## Completed diagnostic and witnessed exporter failure

All twelve planned joint solves and the preselected tighter control succeeded.
Both starting states had identical floating-point consumer and resource
trajectories at every retained time 512–1023, for every community; all twelve
measure/target score differences were zero. This is numerical coalescence,
**not an assertion of exact mathematical equality** or a uniform error bound.

Maximum consumer log difference across communities at the fixed checkpoints:

| Time | Maximum difference |
|---:|---:|
| 0 | 3.60883 |
| 32 | 0.0101594 |
| 64 | 0.000548216 |
| 128 | 0.00000158827 |
| 256 | 0.0000000000212981 |
| 512 | 0 at floating precision |
| 1023 | 0 at floating precision |

Local-linear relaxation times range from 8.98469 to 11.89641 units. The
tighter community-4 solve also coalesces by burn-in. Across original versus
tighter solves its maximum retained log difference is 2.82e-8; maximum
full-state difference over all times is 2.29e-7. These numerical controls
support the paired observation, without certifying exact dynamics.

The frozen runner's first exporter rejected its own stationarity replay
because it compared floating reductions with exact equality. The largest
discrepancy was 4.81143e-13. Reconstructing the original solver array memory
layout reproduces all twelve stationarity receipts exactly, identifying
reduction order as the cause. Neither trajectories nor receipts were changed.
The separate burn_audit.py verifies **all original frozen source hashes**,
array and receipt identities, and replays with an explicit absolute tolerance
1e-12. It also audits the saved tighter-control arrays. This repair is in the
exporter, not in any scientific score, source setting or ecological solve.
Use that auditor for final reporting; the original --report-only path retains
its witnessed exact-equality limitation.

Committed burn-coupling-protocol.json, burn-coupling-summary.json and
burn-coupling-scores.csv retain the settings, compact audited evidence and
per-community differences. Full trajectories and detailed receipts stay private.
The finding makes persistence of **these two initial states on these twelve
input prefixes** an implausible explanation for the previous length failures.
It does not establish a stationary nonlinear distribution, test every initial
state or path, or improve community precision. In particular, small initial
memory and large finite-record estimator variation are compatible.
