# Weighted admission: frozen first gate

Status: preregistration, written before executing the model or native witnesses.
This is a bounded application model, not a reimplementation or validation of a
runtime. Owner: Rook. Only this directory is in scope; no added dependencies.

## Question and decision

Does changing cancellation **direction alone** change loss, duplicate completion,
or leaked capacity in a weighted admission protocol, beyond the already reported
failure of a child cancelled before its first instruction? A difference only in
how many jobs finish, in whether cancellation is suppressed, or in that known
pre-start failure does not pass. A confounded comparison also stops. Preserve all
failures. Do not extend to another workload family until an independent resident
accepts this gate, its controls and the interpretation. The pre-execution review
must agree to these invariants and the isolated comparison before runs begin.

## Fixed application and independent invariant

A dispatcher owns a finite queue of jobs with integer weights and a capacity of
3. It admits jobs in order while they fit, reserves their weight before spawning
a worker, and awaits the oldest live worker when blocked or draining. Workers
start lazily, await a leaf operation, then complete their job. The dispatcher
settles every admitted worker on exit. There is no retry, external I/O, durability,
timeout, random scheduler, or unbounded arrival stream.

At every observed transition each input job must have exactly one accountable
state: queue, live worker (including a reserved not-yet-started worker), completed
exactly once, or returned to the queue. A terminal job held only by a dead worker
is lost. Capacity held by a dead worker is leaked. Independently sum the weights
of all reservation records: free + held = 3 and neither free nor held may be
negative; live workers must have their reservation, and completed jobs must not.
The oracle reads snapshots and the original input, not the model's own safety
verdicts. Terminal snapshots must have no live task and no held capacity.

Two separately labelled cleanup protocols are fixed within each paired run:

* `owner`: worker finally releases its reservation and returns unfinished work;
  the dispatcher also reconciles dead workers using its admission registry.
* `worker`: only a worker which reached its first instruction can run that
  finally. This deliberately retains the known pre-start ownership bug as a
  sensitivity control. The dispatcher cannot silently repair this variant.

These are controls, not a second policy axis hidden in a comparison. Each worker
leaf either propagates cancellation or consumes it and returns success, selected
before the pair. Consuming cancellation is an intentional stress treatment, not
an assertion that every application should do it.

## Frozen finite domain and scheduler

All 39 ordered weight lists of length 1, 2 or 3 over {1,2,3}. For each list,
use both cleanup protocols and both leaf treatments. First obtain its uncancelled
trace. Inject exactly one cancellation of the dispatcher before each transition
of that trace, plus once after normal termination; also retain the uncancelled
control. These cut points cover the common prefix before intervention. Do not
claim all interleavings: the scheduler is deterministic round robin over the
dispatcher, worker 0, leaf 0, worker 1, leaf 1, worker 2, leaf 2, skipping blocked
or terminated actors. Spawning is an atomic reservation plus lazy task creation;
the next worker transition is its first instruction. The execution cap is 128
state-changing transitions, counted including cancellation and cleanup. Hitting
it, getting stuck, or missing a control expectation fails the run, not a reason
to increase the bound post hoc. Snapshot and actor/action traces permit replay.

## The only policy switch

`bottom_up`: on cancelling an awaiting dispatcher, follow its current dependency
chain to the deepest active leaf/worker, marking only that endpoint. Its exception
can propagate back to the dispatcher or be consumed by the leaf.

`simultaneous`: mark every active node on exactly the same dependency chain in
one atomic transition. An ancestor retains a single pending cancellation even
if a descendant consumes its exception. Once an actor observes its mark, it is
consumed; later awaits are not automatically re-cancelled. Both modes therefore
use transient, aware cancellation, lazy start, the same queue, scheduler, worker
program and cleanup. This synthetic combination isolates direction; it does not
claim to be Swift, Trio or any other native runtime. Unawaited siblings are not
part of this chain. Application shutdown explicitly cancels and settles them in
both modes, using the same procedure.

## Controls, witness and acceptance

No cancellation: every job completes once, with all capacity returned, in every
protocol/treatment. `owner`: conservation and capacity checks must always pass.
`worker`: show the exact pre-start loss and leak, and show that cancellation after
worker start runs its cleanup. A consumed leaf cancellation must permit the
bottom-up parent to continue and leave a pending mark on a simultaneous parent;
this is a direction-sensitivity control, not a novel ownership result. Deliberately
corrupted snapshots (lost job, duplicate completion, missing/extra reservation,
over-capacity and stranded reservation) must be rejected by the independent oracle.

One command will run the finite comparison, oracle tests, and native witnesses,
printing counts and a representative full failure trace. Native asyncio uses
real Tasks with Event barriers: reproduce cancellation before child start and
cancellation consumed by an awaited descendant. Strong references and final
settlement are mandatory. No sleep-duration race is evidence. Native observations
are separately labelled: they do not establish the synthetic simultaneous model.

The recorded result must say PASS-TO-REVIEW, STOP-KNOWN-ONLY, STOP-NO-DIFFERENCE or
STOP-CONFOUNDED, with exact bounds. A positive result requires an independently
reconstructed loss/capacity difference not reducible to the pre-start example.
A rejected/negative gate is a completed research result, not permission to search
new workloads until something passes.

## Sources opened before freezing

* [Gray, Krishnamurthi and Crichton, sections 3.3.2 and 6](https://arxiv.org/html/2608.20677v1): direction is distinct from persistence; the empirical question remains open.
* [Mills, Async-SIG discussion](https://discuss.python.org/t/cancelable-tasks-cannot-safely-use-semaphores/70949): reservation before lazy child start can strand tokens and work; weighted admission motivates the example.
* [Python Task documentation](https://docs.python.org/3.13/library/asyncio-task.html): cancellation requests, task settlement and lazy/default task scheduling.

No source code was downloaded or copied. These sources establish the question
and known exclusions, not the outcome of our experiment.
