# Independent paired-freeze delivery and milestone review

Tern, 24 November 2026. **PASS for milestone two's implementation and
prospective freeze.** This is not a held-out calibration verdict. The project
owner decides milestone closure.

Reviewed contribution `7786cbea4c1dea9604dbf2e5f004e73c03e889b0`, run
`522bab9bae9a4f76ba5244935aea6267`. Trusted inspection names exactly the three
restored freeze files; its complete diff matches the local Git diff. Each local
file matches its immutable SHA256 in original finish 39746:

| File | SHA256 |
|---|---|
| PAIRED_PROTOCOL_FREEZE.md | c207adef107a185f2d6cca44b47a37e840c5c11a7dced7329198452acba76e74 |
| paired_protocol_check.py | a05d2aa188144fa0ee42139c5a9a0234ae8ae1dab560f7ae9eeb9af414636b4c |
| test_paired_protocol_check.py | 22838762f8be1252b3b44282f3b8efdbe3dd1e0f5fca9fbf5589b44ce05f74b5 |

The original rejection at 39841 remains part of the record. Fresh redelivery,
not a retry that overwrites that rejection, resolved delivery: terminal trusted
integration 39986 records this contribution as integrated, project-wide tests
and both new Python AST checks with exit zero. Delivery 39989 records the same
commit at public remote main. I did not request another publication.

## Executable checks

From the repository root, Python 3.13.2:

```sh
python3 -m unittest discover -s projects/sediment-event-order -p 'test_paired*.py' -q
python3 projects/sediment-event-order/paired_protocol_check.py > /tmp/paired-preflight.json
```

All 32 tests passed in 2.721 seconds. The bounded preflight exited zero with
`READY_FOR_INDEPENDENT_REVIEW`, all twelve analytic/failure checks passing,
unchanged nine pinned scientific inputs, and `held_out_executed: false`.
Every development record equals the freeze's recorded JSON exactly; only wall
times differ. Balanced, proxy-rich and date-rich order probabilities are
0.8481377129558578, 0.9202548281932194 and 0.8830460709365493 respectively.
All remain unresolved. These are paired designs on one latent draw.

I opened the prior independent source review, paired probability-law contract,
freeze implementation and failure tests. The implementation guards held-out
streams during preflight, checks the complete protocol fingerprint, refuses
changed scientific pins, and preserves failed-worker evidence. Its tests alter
every pin, alter an otherwise unlisted protocol field, try held-out generation,
force numerical failures and timeout, and verify manifest-only execution draws
no randomness. The twelve analytic checks include shared-offset integration,
positive-mixing specimen quadrature, joint proposal corrections and accounting
controls. This is proportionate confirmation of the already reviewed paired
scientific foundation, not a new claim of convergence.

## Scope and next gates

The current milestone asks for a frozen paired synthetic experiment with finite
specimens, monotone chronology, independent/shared errors and separated held-out
seeds. The delivered code and explicit probability law meet that scope. This is
the runnable synthetic instrument promised, useful for testing joint dating and
event-order uncertainty; it is not empirical climate validation.

Before milestone-three evaluation, implement and independently check
misspecification and simultaneous-event robustness cases, plus a comparator
targeting the same latent climate times. The Gaussian depth-boundary control
cannot serve as that comparator. Preserve paired indices, failed and missing
denominators, and the untouched registered range. No held-out draws ran here;
they still require an explicit later task. Finite-width layers, age-varying
calibration and continuous mixing remain outside the adopted model. The current
development results establish neither calibration nor a winning measurement
budget.
