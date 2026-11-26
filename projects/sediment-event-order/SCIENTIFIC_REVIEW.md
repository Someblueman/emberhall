# Independent scientific milestone review

Bellflower, 26 November 2026. Review of the frozen 128-unit sediment
comparison and `SCIENTIFIC_REPORT.md` from contribution `b2f4ad3`.

## Verdict

The completed execution is a useful, reproducible synthetic stress test, but it
does not establish a method or proxy-design winner and does not validate real
archive chronology. The report correctly keeps milestone closure open pending
this review. I recommend that the owner accept the *execution and reporting*
milestone as complete, with the scientific result explicitly limited to this
registered synthetic setup. I do not recommend treating it as general method
validation or as evidence that proxy-rich sampling is superior.

## Evidence and interpretation

The report identifies 128 independent latent draws, with five laws, three
designs and two paired methods inside each draw. Thus 3,840 fits are not 3,840
independent replications. It reports 3,612 successful fits, 108 importance
diagnostic failures and 120 timeouts, with none missing. These failures are
material selection: a passing-fit coverage estimate is conditional on numerical
success. The report's distinction between covered/requested and covered/passed
is therefore essential.

The strongest scientific finding is the deliberately fixed opposite dating
bias, which neither method models. The reported selected coverage around
63–73% is well below nominal 90%; this demonstrates a concrete failure mode of
the assumed common-offset dating model. For doubled mixing with date-rich
sampling, only 73/128 fits pass and 67 cover, so the requested-population
coverage is 67/128 (about 52.3%), while the passing-only ratio (67/73) would
hide selection. The small number of independent units also makes estimates
coarse: at 90% coverage the registered standard error is about 2.65 percentage
points before accounting for selection or model misspecification.

The report says all 100 registered marginal contrast intervals include zero.
That supports “no winner established,” not equivalence: these intervals are
compatible with meaningful differences in either direction. PIT summaries are
approximate weighted-posterior diagnostics on accepted rows, not exact
simulation-based calibration. Runtime is tied to the recorded execution
environment and resource limits; it is not a hardware-independent comparison.
The synthetic laws, fixed misspecification and finite-importance calculation
do not establish performance on real sediment archives.

## Review boundary

I inspected the trusted integration candidate for the report and the recorded
final synthesis lesson. The integration service ran the affected project suite
successfully (`test_exit: 0`). The lesson records the final CSV hash, successful
documented CSV summary command, checks of 30 strata and 25 paired contrasts,
and 12 frozen protocol tests. However, the candidate's final CSV and report are
not available as files in this private room, so I could not independently
recompute the requested key coverage, wrong declarations, bounds, paired
contrasts, error, width and PIT directly from all 3,840 rows. This review does
not represent those recorded checks as my own recomputation. Before using this
as an empirical benchmark outside the house, an independent reviewer should
repeat those calculations against the exact hashed CSV and verify its runtime
and source-version provenance.

The claim of value rests on the executable frozen experiment, retained
failures, complete held-out data and honest interpretation of selection and
misspecification. Those make it a worthwhile bounded scientific artifact;
they do not turn the synthetic benchmark into a real-world chronology result.
