# When Nutrients Arrive Together

A controlled consumer–resource study of diet inference under shared nutrient
delivery. Current work is the **independent-input pilot**, not a completed
correlated-input study or a replication of a published figure.

From the repository root, with the already installed NumPy and SciPy:

```
python3 projects/when-nutrients-arrive-together/reference.py --output /tmp/nutrient-reference
```

This regenerates four seeded communities, their supply and abundance arrays,
per-community metrics at three spectral resolutions, and `report.json` with
uncertainty, solver/forcing convergence, versions and failures. Runtime is a few minutes on the development machine. Outputs are generated outside the source
checkout; binary arrays are not committed. To test:

```
cd projects/when-nutrients-arrive-together
python3 -m unittest -q
```

Read [MODEL.md](MODEL.md) before interpreting a score. It distinguishes the
source equations from our explicit supply choices, lists every approximation,
and names the remaining scientific work. [PILOT.md](PILOT.md) records the first
run. No web interface, new dependency, or external service is needed.

For longer records or finer forcing, use `--duration`, `--burn`,
`--drive-spacing` and `--seeds`. At least 240 retained observations are
required for all spectral checks. Existing outputs are replaced, so use a new
output directory to preserve an earlier experiment.

The next study is `convergence.py`; [PROTOCOL.md](PROTOCOL.md) freezes its
nested-path, longer-record and held-out design. [SOURCE_AUDIT.md](SOURCE_AUDIT.md)
records the additional source checks and unresolved conventions.
[FORCING.md](FORCING.md) derives an exact input interpolation error calculation;
it is not a bound on ecological scores. No correlated-input experiment has run.
[LINEAR_WELCH.md](LINEAR_WELCH.md) gives the independently checked stationary
linear prediction for our exact fixed-segment estimator. For a second independent
path per community, run `repeated_paths.py /tmp/nutrients-clean-v1 --output
/tmp/nutrients-repeat-v1`, then add `--analyze` after both studies finish.
The explicitly exploratory first-four-community duration extension is
`long_record.py /tmp/nutrients-clean-v1 --output /tmp/nutrients-long-v1`.
It checks the saved trajectory prefix before reporting longer-window scores.

[RESULTS.md](RESULTS.md) records the completed twelve-community refinement,
second-path and four-community long-record study. Solver and finest-mesh
sensitivity gates passed; record length and precision did not. The committed
score tables preserve this measured failure; milestone 1 remains open.

[LINEAR_CALIBRATION.md](LINEAR_CALIBRATION.md) isolates finite-record effects
using exact stationary linear sampling: 12 communities, four paths each and
prefixes through 131072 observations. It supplements the failed nonlinear
convergence study and does not complete the milestone.
# Further long-record investigation

[LENGTH_EXTENSION.md](LENGTH_EXTENSION.md) completes the exploratory
20000-observation records for all twelve development communities, diagnoses
the covariance changes, and follows the worst observed correlation case to
65536 observations. The original convergence and precision gates remain failed.
It also records a matching candidate derivative kernel with measured timing
controls; the scientific runs retain the original simulator.

[FINITE_COVARIANCE.md](FINITE_COVARIANCE.md) derives exact finite-record
covariance moments and conservative correlation-score envelopes for the
stationary Gaussian linear reference. It separates one-community coverage
from simultaneous study coverage and retains the elementary bound's failure.
These analytical diagnostics do not certify the nonlinear clean baseline.

[INTERPOLATED_LINEAR.md](INTERPOLATED_LINEAR.md) gives the exact stationary
linear model for the simulator's straight-line supply interpolation. It
separates population interpolation bias from realized-path score sensitivity.

[AMPLITUDE_LIMIT.md](AMPLITUDE_LIMIT.md) completes a twelve-community,
same-path nonlinear-to-linear amplitude check. Trajectory errors halve with
input amplitude; the remaining coherence rank discrepancy is retained.
[NEXT.md](NEXT.md) records the substantial work still needed before accepting
the clean reference or using the held-out experiment.

[PAIRED_REFINEMENT.md](PAIRED_REFINEMENT.md) records 24 new nonlinear paths
with paired 1/16-to-1/32 forcing and 4096-to-8192 record comparisons. All
observed forcing margins pass; eighteen paths exceed a length margin. The
report audits every score from saved trajectories and separates fixed-cohort
input uncertainty from population claims after adaptive community reuse.
The compact protocol, scores and summary are linked from that report.

