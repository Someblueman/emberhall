# When Cancellation Loses Work

An importable, standard-library experiment for weighted job admission. It asks
whether changing cancellation direction alone changes job ownership or capacity.
This first gate may legitimately stop the project on a known-only result.

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

A zero exit means the controls and bounded reproduction passed. **It does not
mean the research gate passed**: read the printed `decision`. STOP-KNOWN-ONLY is
an honest negative research result, not permission to enlarge the corpus.

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

Pre-execution independent review is pending. No experimental results are claimed
by this draft; the result document will identify the review and actual run.
