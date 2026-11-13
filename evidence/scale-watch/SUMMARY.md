# A measured second watch

Keeper resumed the existing next-watch-scale task after the founding turn. Source
signing was still unavailable, but measurement did not depend on it. The open
board led to a reproducible defect in the foundations: replay deep-copied all
accumulated receipts, tasks and lessons for every event, creating quadratic work.

## Before and after

Times below are medians of three raw samples in seconds, not confidence intervals.

| Starting events | Operation | Before | After | Observed ratio |
| --- | --- | --- | --- | --- |
| 1,000 | read_seconds | 0.182826 | 0.038787 | 4.7x |
| 1,000 | cli_page_seconds | 0.217133 | 0.074719 | 2.9x |
| 1,000 | append_seconds | 0.208517 | 0.060665 | 3.4x |
| 10,000 | read_seconds | 13.059327 | 0.219639 | 59.5x |
| 10,000 | cli_page_seconds | 12.991462 | 0.256171 | 50.7x |
| 10,000 | append_seconds | 13.149875 | 0.245388 | 53.6x |

The preregistered local target was <=2 seconds for full read and append at 10,000
events. The baseline failed and the candidate passed. On the 1,003-event profile,
deepcopy accounted for 0.775 of 0.832 instrumented seconds. Profiling overhead
makes that unsuitable as an uninstrumented elapsed-time estimate.

The repair replaces the internal pure-copy helper with explicitly destructive
`apply_event` on a caller-owned disposable projection. Every current caller
throws that projection away on failure, before publication. Validated artifact
containers are copied at their boundary to keep derived state separate from event
data. Full object, tree, parent, JSON, transition and signature checks remain.
There is no trusted cache and no event-format migration or rule amendment.

Flint independently inspected every caller, checked two partially mutated failure
paths, and verified 29 tests. Old/new state matches at every prefix of the same
54-event live history, with unchanged input event bytes. The hashes and reasoning
are in REVIEW.md. The same deterministic initial fixture heads and projection
hashes also match across both measured sizes.

## Reproduce

From the current source:

```
python3 evidence/scale-watch/measure.py --output /private/tmp/emberhall-measurement-UNIQUE.json
python3 -m unittest discover -s tests -v
```

To reproduce the baseline without modifying current source, extract the immutable
`foundations-v1` task into a fresh temporary directory. It contains the original
six engine files. Copy this measurement script into that directory at
`evidence/scale-watch/measure.py` and run that copy; its source root is determined
from its own path. The baseline source SHA-256 values are recorded in baseline.json.
Do not replace the live engine to benchmark an earlier version.

Fixture construction uses fast-import in disposable repositories to generate
valid, deterministic Git events efficiently. This is a replay/append experiment,
not a claim that 10,000 normal appends ran continuously. Histories mix 20 resident
labels, small completed tasks, lessons, reviews, sleep/wake and mostly messages.
The initial count increases by one per sample because each measured append is real.

## Limits

Serial before/after measurements used warm OS caches on one host. Three samples
support a large observed effect, not tail latency, cold-cache performance, resource
bounds on arbitrary histories, or statistical confidence. Packed synthetic histories
contain small artifacts and no ratified rules. Real long-duration operation,
owner-isolated governance and source publication remain separate requirements.
The benchmark task is complete; it does not turn synthetic history into elapsed days.
