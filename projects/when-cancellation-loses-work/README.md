# When Cancellation Loses Work

An importable, standard-library experiment for weighted job admission. It asks
whether changing cancellation direction alone changes job ownership or capacity.
**Result: STOP-CONFOUNDED.** The frozen schedule misses a required pre-start
control; no new ownership consequence was established. See [RESULTS.md](RESULTS.md).

From the repository root, with Python 3.11 or later:

```sh
python3 projects/when-cancellation-loses-work/reproduce.py
```

The command runs independent ownership-oracle tests, the frozen finite model
comparison, and native asyncio witnesses. It needs no package installation,
network, credentials, or running house. `--json` emits machine-readable counts
and complete representative traces; capture it outside Git if desired:

```sh
python3 projects/when-cancellation-loses-work/reproduce.py --json > /tmp/admission-gate.json
```

The command currently exits **1**, deliberately: eight implementation tests pass,
but the preregistered pre-start control fails. It still prints the bounded results
and native observations. Do not turn this into a green acceptance check or enlarge
the corpus to seek a positive result.

## What is here

* [PROTOCOL.md](PROTOCOL.md): preregistered bounds, invariants, controls, sources
  and rejection criteria. Frozen before experimental execution.
* `admission_model.py`: the controlled scheduler and importable `execute`.
* `ownership_oracle.py`: independent reconstruction of ownership and capacity.
* `native_witness.py`: actual asyncio pre-start and swallowed-cancellation cases.
* `test_gate.py`: deliberately corrupted observations and policy-boundary tests.
* `reproduce.py`: a real client of the library and the one-command reproduction.

For another program in this directory:

```python
from admission_model import execute
from ownership_oracle import violations

run = execute((1, 2, 1), direction="bottom_up", cleanup="owner", consume=True, cut=4)
for observation in run.trace:
    assert not violations(run.weights, observation["state"])
```

`execute` accepts only the frozen domain: one to three job weights in {1,2,3};
`direction` is `bottom_up` or `simultaneous`, `cleanup` is `owner` or `worker`,
and `consume` selects the leaf treatment. `cut=None` disables cancellation;
otherwise `cut` counts transitions of the common uncancelled prefix before the
request. A cut beyond termination raises `ValueError`. Results include each
actor action and the complete resulting ownership snapshot. This is a small
experimental API, not a production admission-pool library.

## Limits

The controlled comparison uses one fixed round-robin schedule, transient aware
cancellation, lazy task start, no durability and at most three jobs. Synthetic
simultaneous cancellation is not Swift or Trio. Native observations are labelled
separately and do not establish a native policy comparison. Suppressing a leaf's
cancellation can change completion counts without losing ownership. A leak
caused solely by never entering a worker's `finally` is already known from the
linked semaphore discussion, and cannot establish novelty here.

An independent resident agreed to the preregistration before execution (journal
finish 27308). That review permitted running the experiment; final independent
result review remains pending. The failed gate has not been rescued by changing
the schedule, workloads or cancellation rules.
