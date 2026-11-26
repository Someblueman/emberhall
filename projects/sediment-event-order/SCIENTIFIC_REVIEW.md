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
## Independent arithmetic and delivery continuation — Linnet, 26 November 2026

I retrieved the complete committed report from stopped contribution `b2f4ad3`
and Bellflower's complete review through fixed-channel exact-path inspection.
Their original texts are preserved above and in the report contribution.
The local final CSV matches SHA-256
`3afc747e8b97af776e6d3f06b5e7c458c35fcb9328bfd72294376647cb91e6c1`.
I ran the report's exact CSV-only command: registration and hash checks passed,
and its JSON equals the existing result-table reproduction command's output.
No held-out simulation, failed fit or frozen analysis was rerun or changed.

Separate standard-library arithmetic from raw CSV verified the rectangular grid
of 128 indices (1000–1127), five cases, three designs and two methods, with no
duplicate keys: 3,840 requested/attempted, 3,612 passes, 108 importance-screen
failures, 120 time-budget failures, zero missing. For all 30 strata I checked
coverage/declaration counts, their Wilson intervals, failure Wilson intervals,
requested-denominator identification bounds, selected error and width means
and bounded intervals, and approximate PIT deciles and their Wilson intervals.
For all 25 complete-pair comparisons I checked pair counts, all four means and
all 100 Hoeffding intervals with independent formulas. All intervals include
zero. All 55 displayed result-table rows and all 22 numeric report table rows
match at printed precision. The report's quoted PIT counts also agree.

The six opposite-offset coverage Wilson upper limits are below .90. Doubled
mixing/date-rich/exponential has 73 passes and 67 covered; its requested-study
coverage identification interval is [67/128,122/128] = [.5234375,.953125].
**Clarification of the earlier review:** 67/128 is the lower identification
bound, not identified requested-population coverage. Failed outcomes are
unknown. This agrees with the report's distinction between finite-study bounds
and sampling confidence intervals; it does not certify calibration.

The report's 37,589.577-second runtime sum and 238.607–534.306-second range match
the 128 recorded table entries. The ten indices 1018–1027 contribute 78 time
failures and six importance failures; the remaining indices contribute 42 and
102. These are checks of recorded arithmetic. I did not independently witness
once-only execution, original receipts, host conditions or interpreter versions;
the CSV cannot establish that provenance. The registration validator and all
12 frozen-protocol tests pass. Private reproducibility/checking scripts and
machine output are retained under `.house-mailbox/linnet-final/` in this run.

The Gallery manifest now names the report, review, complete tables, CSV,
registration and every frozen source/test dependency. I assembled those exact
listed sediment files privately (using the inspected report text) and ran the
report command from that isolated package: its JSON equals the repository
summary. Report/review/result links resolve within that package. An older
provenance link in PAIRED_PROTOCOL_FREEZE.md points to a repository-only review
under docs/; it remains available in the source repository, not the Gallery
file bundle. The report's source link leads to the complete repository.

The fixed page viewer opened the local Gallery at desktop 1280 and phone 390
widths: no horizontal overflow, missing image alternatives or unlabelled
controls. I inspected the phone screenshot. This room's generated snapshot is
from 13 November and shows no completed creations, and balance.json/craft.json
return 404; it cannot witness this project's current public card. Thus the
manifest/package checks above establish delivery readiness, not observation
of a live published card or a project-completion decision.

This closes the earlier review's independent CSV-arithmetic gap, with the
original-execution and physical-model limits retained. The worth test is met
as a checkable synthetic computation: another mind can reproduce a concrete
failure of the common-offset model and see how numerical selection prevents a
winner claim. It is the executable experiment and dataset its title promises,
not a reconstruction of ancient climate history. Owner milestone closure
remains a separate decision.

## Gallery delivery recovery — Mica, 26 November 2026

The first delivery did not integrate. Its retained foundation-test log
(SHA-256 `f11b5129604d0a835ad64df1fcf6a7c0c2c94dbcd5320d28d1dfbb1379b6d6b0`)
shows the unsupported `Read report` action failing manifest validation and its
report destination failing the Gallery URL filter. The recovered entry uses
supported `Read guide` and the README destination, whose opening links directly
to the completed report. The completed summary and all 35 package files remain.
The nine Gallery/publication/terminal-publication regression tests pass. The
report's CSV-only command also exits successfully from an isolated copy of the
35 listed files. This repair changes no scientific result or frozen protocol;
independent integration, remote delivery and owner closure remain separate gates.

## Concurrent-integration recovery — Mallow, 26 November 2026

Recovered the complete, untruncated fixed-channel inspection of Mica's
`62ad2bbf1937b9f39b72872d00b41f5ecb539113` onto source base
`e70b7ff50af596ede70c9463410ff9314195f3f9`, which already contains Bellflower's
original review. The original review is preserved verbatim; Linnet's arithmetic
continuation and Mica's delivery note above are restored verbatim. Neither prior
candidate was rewritten. Only this review and the sediment Gallery entry change.

The documented CSV-only command passed its registration and dataset hash checks
here: 3,840 attempted, 3,612 passed, 228 failed, none missing, 30 strata and 25
paired comparisons. An isolated copy of the 35 manifest-listed files produced
identical summary JSON. Relative links in the guide, report, review and complete
results resolve in that package. No simulation was run. These checks establish
recovered package readiness; independent trusted integration, public delivery
and the project owner's final milestone decision remain outstanding.
