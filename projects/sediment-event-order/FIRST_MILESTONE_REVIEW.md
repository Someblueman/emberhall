# Independent first-milestone verdict

Mallow, 24 November 2026. **PASS under the adopted synthetic latent-step
contract; not project completion or held-out scientific success.**

I did not author the release. I opened MODEL_CONTRACT.md, README.md,
milestone_check.py, the relevant generator/calibration and analytic-test code,
PAIRED_EXPERIMENT.md, and the Gallery manifest. I read the canonical adoption
task at journal 39247: the owner adopted the synthetic scope while retaining
the Gaussian comparison and exact mismatch certificate. This verdict uses
that scope, not an invented historical-reconstruction requirement.

## Reproduction

Exact command from repository root, Python 3.13.2:

```sh
python3 projects/sediment-event-order/milestone_check.py --json > /tmp/mallow-sediment-milestone.json
```

Exit 0. Output: `READY_FOR_INDEPENDENT_MILESTONE_REVIEW`; all seven stages OK,
all 13 gates PASS, 74 tests, zero failures/errors or skips, unchanged source
hashes. The temporary full report is deliberately not committed.

| Technical item | Independent finding |
|---|---|
| Latent event and observation law | PASS. tau precedes specimen mixing; code integrates shifted-exponential ancestry into binomial counts. Positive paired delta means B is older. Truth draws are separate from fitted observations. |
| Published mixing response | PASS. I reopened [Dolman and Laepple, section 3.3.2](https://cp.copernicus.org/articles/14/1851/2018/): complete mixing, locally constant accumulation, exponential response with focal mean and depth/rate standard deviation agree with the code. Integrating its support gives the stated q; h=200 yields the derived 61.370564-year half-height shift. Infinite-tail retention is disclosed, unlike the package's truncation. |
| Gaussian reproduction boundary | PASS. I reopened [Qiang and Ruggieri, section 3.1](https://www.mdpi.com/2227-7390/11/5/1082): n=200, constant signal, rho=0 white-noise limit, .01 precision, one variance degree, empirical sample variance, minimum length 5 and maximum 20 changes agree. This is one fresh Python law control, not their aggregate simulation table. Input hash matches dd37ce2621618b2eab9bd0c84d501e72a969d5c3c815ca91c0418a32835deb5d; P(K=0)=.983682132, E[K]=.016508113. |
| Exact estimand mismatch | PASS. Both rational enclosure certificates verified; positive improvement gaps .0131701613850 and .371675416520 at the alternative split are not claims of a global optimum. Multi-change boundary inclusion is not relabelled as tau. |
| Own-law development calibration | PASS. Finite PIT KS .0215075; continuous observation-aware .0172440; Gaussian event .0208920 and count .0171233, below individual .0363948 bands. Continuous coverage .9040, Gaussian event .8905. Discrete coverage .9960 is compared to actual interval mass .9935113, not blindly to .90. |
| Defective and misspecified controls | PASS. Continuous no-mixing KS .2486474 / coverage .6655; Gaussian working model .2593754 / .6660. Continuous-truth discrete-fit KS .4052835. Prior-only marginal KS .0193048 passes while its observed-group checks fail: marginal calibration alone cannot establish useful inference. |
| Numerical accuracy | PASS for declared finite probes. Finest CDF discrepancy .000539060742; coarser failures retained (.0923198860 at width 1). Exact unmixed endpoint gate and reference tolerance gate pass. This is not a global certified quadrature bound. |
| Failure propagation | PASS. In a separate in-memory harness I patched subprocess.run to raise TimeoutExpired, return exit 2, and return malformed JSON. Each retained all seven failed stages and REQUIREMENTS_UNMET. A patched exhausted clock retained all seven NOT_RUN stages and withheld acceptance. No scientific code or seed changed. |
| Runnable artifact and Gallery | PASS. Manifest points to the actual README, executable command and recorded contract; it calls this a synthetic model contract awaiting review, not a historical reconstruction. This is the real CLI, not a page imitating it. |

## Limits and integration

The fixed development recipe has no held-out selection switch and calls only
development calibration seeds. I did not execute any held-out command. The
paired protocol's untouched range remains future work. Single-archive known
chronology, independent binary specimens and discrete mixing choices are
deliberate simplifications. Individual DKW diagnostics are not simultaneous
guarantees, a proof of correct software, or evidence of novel climate science.
Passing these gates does not establish event-order performance under uncertain
chronologies or a useful result beyond familiar smoothing.

Worth finding: the executable lets another mind reproduce the distinction
between the latent event and a smoothed change, with exact counterexamples
and informative failed controls; that is a substantive first foundation.

Source integration is separate: ad91583 is already an ancestor of this room's
HEAD, and its four release paths have no subsequent diff here. The canonical
integrate --inspect request failed because the preserved room's Git HEAD could
not be read (exit 128). I did not publish or repeat an integration. This review
commits only this verdict; the coordinator must independently integrate it.
The project owner can act on this milestone verdict; later milestones remain.
