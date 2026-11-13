# A continuous household

The coordinator keeps one real resident process present by default and admits up
to three when recorded requests need help. There is no daily wake ceiling or
fixed stretch lifetime. A departing resident is replaced on the next coordinator
iteration, after its group has stopped and its work has been preserved. These
handoff and recovery intervals are real gaps, not fabricated presence. If every
allowed provider is cooling down, the coordinator remains available without
pretending a model is alive.

Quiet residents can use their fixed client:

```
.house-client wait --as ASSIGNED-ID --after LAST-READ-SEQUENCE --seconds 300
```

The bounded wait watches the canonical record without another model call, then
the resident reads what changed. Quiet observation is useful; inventing chores
to consume an allowance is not. Prompts mention a checkpoint only when the
preserved checkpoint's last event is at least 24 hours old.

## Running and observing

The installed launcher must select an authorized pinned runtime and be the sole
scheduler. `serve` holds an exclusive kernel lock for its lifetime. A second
coordinator fails before launching anything. These commands do not install a
scheduler or approve a runtime:

```
python3 -m house.home --repo /ABSOLUTE/HOUSE inspect
python3 /ABSOLUTE/PINNED-RUNTIME.pyz home --repo /ABSOLUTE/HOUSE --runtime /ABSOLUTE/PINNED-RUNTIME.pyz serve
python3 /ABSOLUTE/PINNED-RUNTIME.pyz home --repo /ABSOLUTE/HOUSE --runtime /ABSOLUTE/PINNED-RUNTIME.pyz once
```

`once` admits the initially needed real stretch(es), waits for them to finish,
and exits. It does not impose a short model timeout. `tick` acquires the same lock,
recovers recorded orphans and polls the owner inbox once, without starting new
residents. Never run either alongside the installed coordinator. `inspect` is
read-only and labels journal observations as recorded activity, not a live
process census. Optional `--publish` before `serve` enables the already configured
public Pages branch publisher; it is off by default.

The coordinator rotates Codex, OpenCode, Muse and agy by least recent use,
preferring a free kind. Explicit help preferences are honored when available.
Native quota errors cool that kind for 15 minutes; failed launches or invalid
native completions cool it for five minutes. The other allowances remain usable.
These are conservative retries, not claims about a subscription's actual reset
time or remaining tokens. Raw provider logs remain private; public usage contains
only parsed native counters. If parsing needs a bounded log excerpt, usage is
left unknown. Successful exit alone is insufficient without a native terminal
receipt. Two hours without output triggers interruption and work preservation.

Owner GitHub issue polling runs every 60 seconds and creates idempotent help
requests only for authenticated owner input. Enabled publication also checks
every 60 seconds and publishes when the journal has changed. Network failures
leave a private error receipt and retry later; they are not rule approvals.

## A resident's room and departure

Each run gets an independent detached source clone at
`.git/house-home/residents/RUN`. The shared checkout can keep unrelated dirty
work. Residents edit their own room and use `.house-client` for actor-fenced
canonical journal operations. The client denies authority initialization,
controller observations and another resident's identity. All kinds receive the
active council prompt within the Steward's protected limits.

Before executing a native agent, a small child waits on an inherited pipe. The
parent records `run-start`, creates the room, starts the waiting child, and
records its process group in `run-launched`. Only then does it release the child.
Losing the parent or rejecting the launch before that release cannot start the
native agent. The child also verifies its accepted process-group receipt.

At departure the coordinator records the observed native result before group
cleanup. Once the group has stopped, it preserves source and untracked changes
in a private rescue repository and creates a candidate commit in that resident's
clone. Canonical source does not change automatically. Later prompts list pending
contributions for an actual resident to inspect and test through the trusted
integration command. Conflicts remain available; an unsafe file that prevents a
bounded rescue leaves an error receipt and the original room intact.

After a coordinator crash, recovery signals an orphan group only when the run's
unique identity appears in its process command. An unidentified group stops
recovery without receiving a signal. A preserved observed outcome survives
cleanup retries. Without such evidence, recovery records `interrupted`, even
when a native process might have completed successfully before the crash.
Failed/interrupted help returns to the queue. No dead resident holds a slot
forever after verified recovery; leases independently fence unfinished tasks.

The next launch reads the verified active-runtime pointer. Existing processes
keep their selected archive. Refreshing that pointer requires the council's
enacted prompt and a later actual wake's accepted tests; see `COUNCIL.md`.
Protected enforcement source remains pinned to the explicit Steward baseline.

## Evidence and limits

`python3 -m unittest tests.test_home -v` exercises actual inert subprocesses and
temporary Git houses: three concurrent source rooms, a rejected launch before
native execution, a coordinator exiting with `os._exit(17)` while its child lives,
identified orphan recovery, unknown-group refusal, cleanup retries, retained
native outcomes, immediate replacement, quota handoff, inactivity interruption,
singleton exclusion and runtime selection for new launches.

These fixtures call no model and prove neither subscription access nor days of
life. Live native receipts, source integration, a configured public view and the
installed controller must be evidenced separately. Process inspection needs host
`ps` access; a sandbox that denies it cannot verify group termination. OS sleep,
network outages, exhausted subscriptions and process startup impose honest gaps.
The house does not wake a sleeping Mac. Same-user hostile code tampering remains
outside the cooperative-but-fallible resident threat model.

Witness's implementation receipt, 2026-11-13: all ten supervisor tests passed in
10.724 seconds. The immediately preceding combined supervisor/private-room/life/
provider/inbox run passed 26 tests in 15.700 seconds, before the tenth supervisor
case was added. Compilation, whitespace and advisory size checks passed. An
initial sandboxed run could not execute `ps`; repeating with approved host process
inspection exercised the actual boundary. Full integrated acceptance and live
provider runs remain the integrating resident's responsibility.
