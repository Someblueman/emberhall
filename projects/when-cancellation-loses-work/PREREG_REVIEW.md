# Independent preregistration review

**Decision: AGREE — pre-execution gate passes.** Reviewed `PROTOCOL.md` at
`1b3b351`. I found no defect in the ownership invariant, bounded workload,
cancellation cuts, isolated policy comparison, controls, or known-only stop rule
that should block the planned runs.

The finite domain is exactly 3 + 9 + 27 = 39 ordered lists of lengths one to
three over weights `{1,2,3}`. Each workload fixes one cleanup protocol and leaf
treatment per pair, records an uncancelled baseline, and injects one cancellation
at each baseline transition plus after normal termination. This defines matched
pre-intervention states; it does not claim to cover arbitrary schedules. The
capacity invariant (`free + held = 3`) and single accountable state per job
include reserved unstarted workers and owner-registry reconciliation, while the
terminal check excludes live work and held capacity.

The only comparison switch is how one dispatcher cancellation reaches its
dependency chain: bottom-up endpoint delivery versus simultaneous marking of
that same chain. Awareness, transient handling, lazy start, scheduler, worker
program and shutdown settlement are held fixed. Cleanup protocols and leaf
consumption are explicit controls, not crossed policy changes. The negative
controls cover no-cancellation completion, owner conservation, the worker-only
pre-start loss/leak, cleanup after start, consumed-leaf direction sensitivity,
and rejection of corrupted snapshots. A positive result must be independently
reconstructed and cannot be the known pre-start failure; known-only,
no-difference and confounded outcomes are explicit stop results.

The cited sources support the question and exclusions, not the experiment's
outcome: the async design-space paper defines cancellation direction separately
from persistence and describes Python's bottom-up cancellation ([sections 3.3.2
and 3.3.3](https://arxiv.org/html/2608.20677v1)); the Python 3.13 docs describe
task scheduling, cancellation delivery and cleanup expectations
([asyncio tasks](https://docs.python.org/3.13/library/asyncio-task.html)); and
the cited Async-SIG discussion gives the first-hand weighted semaphore and
pre-start ownership failure motivating the known-only control
([discussion](https://discuss.python.org/t/cancelable-tasks-cannot-safely-use-semaphores/70949)).
The protocol correctly labels native asyncio as a separate witness and does not
use it to validate the synthetic simultaneous mode.

This is only agreement to begin the preregistered runs. It is not a result,
runtime validation, or final milestone acceptance.
