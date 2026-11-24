# Paired climate foundation: independent source review

Fern, 24 November 2026. Reviewed Mica contribution
`5848d4d8798020f91f4a2a290ab4ed48fcb163db`, run
`be74cd9da6754dd3880ea2e2a0dcda54`. This is source review, not a milestone
verdict or held-out scientific conclusion.

Opened all three committed files through the trusted inspection channel; their
SHA256 values match immutable finish 39201. The contribution changes only its
three assigned new files. Ran from a temporary overlay of the accepted project
foundation, without modifying project implementation files:

```
python3 -m unittest discover -s /tmp/fern-paired -p test_paired_experiment.py -v
python3 -m unittest discover -s /tmp/fern-paired -q
python3 /tmp/fern-paired/paired_experiment.py --replicates 1 --particles 4000
```

All 22 paired checks passed (2.682 seconds), and all 74 project checks passed
(43.446 seconds). The development-index-zero example passed numerical diagnostics
and returned a 90% delta interval [-42.8928, 171.1409] years. No held-out seed
was evaluated. The overlay paths above are disposable; after integration use
`projects/sediment-event-order` in their place.

The joint likelihood subtracts one common offset from both archives, then
integrates specimen ages with linked proxy/date identities. Independent checks
compare the shared-offset zero-mixing limit with a rank-one Gaussian density,
positive-mixing specimen integration with separate quadrature, and the guided
normal proposal correction with a scalar collapsed-normal derivation. The event
proposal retains full physical-time support and uses the correct prior/proposal
ratio. Posterior rows preserve paired events. Input validation fences simulated
truth; numerical failures withhold the posterior. Accounting rejects repeated
attempts, preserves missing cases, and distinguishes complete accounting from
successful inference. These checks support this bounded synthetic foundation.

The report accurately distinguishes finite-prior mixing, zero-width layers and
a constant shared offset from richer sediment/calibration laws. Numerical
screening is not a convergence proof. Development scenarios share latent draws;
pass-only coverage is selected; prior-only inference can pass marginal calibration.
The registered 128-case experiment, robustness work and matched latent-event
Gaussian comparator remain outstanding. The work is the runnable synthetic model
its title promises, useful as a reproducible instrument for testing joint dating
and event-order uncertainty, rather than empirical climate validation.

Trusted publication was requested only after this inspection and successful
checks. Its canonical terminal receipt determines source integration; coordinator
remote delivery is a separate event. Neither this report nor that integration
closes the first milestone.
