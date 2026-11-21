# First admission gate: stop

**STOP-CONFOUNDED: a preregistered control was not reached.** There is no new
application-level ownership consequence established by this experiment, and no
permission to extend the corpus. Here “confounded” labels a failed gate design,
not an observed extra difference between the two policy implementations.

## What was frozen and reviewed

Protocol commit `1b3b351`, SHA-256
`b30b2968da2c99d75515b2ae9e14a7483e428ed9e6a66bce6096389f87f5bbb1`.
The protocol was committed before any model or native execution and remains
unchanged. A non-author agreed to it in task `cancellation-preregister-review-2f3`,
finish **27308**, before the first run. The review report SHA-256 is
`f5bd0354dd96070aaab7883404f8b402781673986d0f829161b3cdb67e557293`.
That was pre-execution agreement, not acceptance of this result.

Run the actual program from the repository root (Python 3.11+):

```sh
python3 projects/when-cancellation-loses-work/reproduce.py
```

It exits **1** because the scientific gate failed. For complete representative
snapshots, use `--json`. Implementation tests can be checked separately with:

```sh
python3 -m unittest discover -s projects/when-cancellation-loses-work -p test_gate.py -v
```

## Recorded run, 21 November 2026

CPython 3.13.2, native `_UnixSelectorEventLoop`, default lazy task factory.

| Measurement | Result |
|---|---:|
| Distinct ordered weight lists | 39 |
| Uncancelled executions (both directions, both cleanup/leaf treatments) | 312 |
| Paired single-cancellation cases | 3,168 |
| Cancelled executions | 6,336 |
| Pairs with different terminal ownership/outcome signatures | 122 |
| Pairs with different ownership violations | 0 |
| Owner-protocol runs with ownership violations | 0 |
| Worker-only runs with ownership violations | 0 |
| Expected model pre-start failure observed | **No** |
| Maximum state-changing transitions | 25 of 128 |
| Bound hits / stuck runs | 0 / 0 |
| Final implementation unit tests | 8 passed |

The 122 differences are completion versus return of work after a leaf consumes
cancellation. They are not lost or duplicated jobs. For weights `(1,)`, consuming
leaf, cut 4: bottom-up completes job 0; simultaneous returns job 0. Both return
all capacity and preserve ownership. This confirms the policy switch can affect
execution; it does not pass the project's worth/novelty gate.

## Exact failed premise and its preserved trace

The first command exited 1 before the finite sweep because the initial unit test
expected `lost:0` after cancelling the dispatcher at cut 1 with weights `(2,)`:

```text
FAIL: test_cancel_before_and_after_start
AssertionError: 'lost:0' not found in ()
Ran 8 tests
FAILED (failures=1)
```

The diagnostic run retained the same model, workload, scheduler and protocol:

```text
00 initial                                  queue=[0], live=[],  held={}
01 reserve 2 and spawn worker 0 lazily       queue=[],  live=[0], held={0:2}
02 cancel dispatcher (bottom-up)             queue=[],  live=[0], held={0:2}
03 worker 0 enters finally-protected body    queue=[],  live=[0], held={0:2}
04 dispatcher observes cancellation          queue=[],  live=[0], held={0:2}
05 worker 0 awaits leaf                      queue=[],  live=[0], held={0:2}
06 leaf completes normally                   queue=[],  live=[0], held={0:2}
07 dispatcher cancels remaining workers      queue=[],  live=[0], held={0:2}
08 worker 0 cancels, returns job, releases    queue=[],  live=[],  held={}
09 dispatcher settles                        queue=[],  live=[],  held={}
```

The mistake was expecting lazy start to imply cancellation before start. In this
round-robin schedule, the newly created worker gets its first turn before the
dispatcher handles its own pending cancellation. Both directions therefore miss
the intended pre-start control. Changing scheduling or cancelling the worker
directly would be a different experiment. We did neither in the finite sweep.

The incorrect *implementation-test expectation* was changed to assert this actual
ordering. The scientific control remains false, is emitted as
`prestart_control_observed: false`, and still makes the command exit 1. The harness
was adjusted to print results after that failure instead of aborting before the
finite sweep. This is not a revised protocol or a successful preregistered gate.

## Separate native observations

The frozen native direct-child witness does reproduce the known mechanism:
reserve weight 2, create a child, cancel it without an intervening await. Its
body never starts; worker-only cleanup leaves `lost:0`, `stranded:0` and
`unsettled-terminal`. Parent registry reconciliation returns the job and capacity.

A second native witness fills capacity with weights 1 and 2. Cancelling the
awaiting dispatcher reaches its leaf; the leaf consumes cancellation, worker 0
completes, and the dispatcher continues and admits another weight-1 job. Cleanup
settles all tasks and returns all capacity. Events, not sleep durations, establish
the cancellation boundary. This supports only the native bottom-up observation;
no native simultaneous runtime was tested.

These observations reproduce the [known semaphore ownership problem](https://discuss.python.org/t/cancelable-tasks-cannot-safely-use-semaphores/70949)
and cancellation suppression, not a new answer to the
[paper's empirical question](https://arxiv.org/html/2608.20677v1).
The model's atomic ledger and cleanup also exclude many real external handoff
failures. No durability, throughput, prevalence, universal safety or relative
runtime ranking follows from this result.

**Next action:** independent result review, then the project owner records this
stop result. Do not begin the fan-out or multi-step corpus milestones on the
strength of this run. A later different experiment would need an explicitly
revised and independently agreed protocol, not a post-hoc repair of this gate.
