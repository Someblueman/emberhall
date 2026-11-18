# A closed ferry core, version 0

This is a proposed contract and a paper argument, not an implementation or
a general type-safety proof. Its restrictions are fixed for this admission
comparison. Extending them would need a fresh argument, not an automatic
claim that the negative finding disappeared.

## Values, environments and permissions

Data types are natural numbers, text and finite products of data. There
are no references, mutable aggregates, functions, closures, recursion,
user-defined effects or arbitrary host calls. Unsupported constructs are
rejected. This explicitly avoids claiming to analyze accepted closures.
`Order` abbreviates a natural-number identifier. `Ticket` and `Closed`
are opaque permissions constructed by the trusted runner from validated
evidence, not arbitrary products the application can construct itself.

`K` contains registered kept data; `F` contains temporary data in the current
entry. Literals are usable in either environment. A pure expression using
only `K` is kept; one using `F` is fleeting, including every ordinary alias
or product containing it. In the core there is no implicit or explicit
promotion from `F` into `K`. All kept input is captured atomically when the
run is registered, before `start`. Changing it starts a different business
order, outside the current order's single-attempt guarantee.

The typing judgments are `K ; F ; P |- c`, where the permission `P` is one
of `ready`, `pending(B)`, `done(B,t)` or `closed(B)`. The fixed program has
one named action, `sale`, and one outstanding order at most.

| Construct | Requirement and result |
| --- | --- |
| `fleeting x = advisory_board(e)` | `e` uses `K`; read-only adapter; extend `F` |
| `show(e)` before booking | may use `K,F`; local display has no external effect |
| `book sale = ferry_sale(args)` | `P=ready`; args use only `K`; commit intent, then invoke at most once |
| `recover` | entry receives `K ; empty ; P` from verified durable state |
| `settle` | exhaustive `done`, `not_done`, `unknown`; each arm has its corresponding permission |
| `done(t) => finish show(t)` | requires matching `done(B,t)`; only local display |
| `not_done(c) => finish show(...)` | requires matching `closed(B)`; cancel, no retry |
| `unknown(p) => wait p at settle` | retains `pending(B)`; only read-only inspection on a later wake |

All outcome arms terminate or park; there is no join after the match.
An unresolved arm may alternatively refuse and leave the intent unresolved,
but it cannot produce successful completion, re-register or call `book`.
There is no general `finish` escape hatch from a pending permission. The
complete program chooses `wait`. A vanished value cannot enter recovery
through an alias: recovery's context contains no `F` names and no pointers
or closures can be stored. These are syntactic restrictions, not deep
analysis of an unrestricted language.

## Durable and external state are separate

Let `B = (program_bytes, order, action_label, route, seats, schema)`.
Comparison uses exact equality, not a hash with an unstated collision
assumption. A practical implementation could use a specified digest but
would then have to state its additional assumption. `program_bytes` covers
the complete closed program; adapter/schema identity is included in schema.

The local record is `Ready(B)`, `Intent(B)`, `Done(B,t)` or `Closed(B)`.
The service is independently `Empty`, `InFlight`, `Sold(B,t)` or
`FencedNoSale(B)`. A read may instead be unavailable. `Empty` is a point
observation, **not** proof that the earlier request cannot still arrive.

The trusted runner must supply the following contracts in *both* examples:

1. A unique durable registration for the business order and one active
   fenced runner. A second client cannot mint another ready record for that
   order. Restoring an old backup, changing the business identifier or
   manually fabricating a new journal is outside the guarantee.
2. Local transitions are atomic and durable before acknowledgement, with
   no rollback of an acknowledged intent. A failed commit dispatches nothing.
   A crash during commit recovers either the complete old or new record.
   Missing/corrupt existing state is refused, never treated as a fresh run.
3. Only the process that commits `Ready -> Intent` receives a volatile
   one-use dispatch permit. A recovered intent receives none. Process death
   cannot leave another live dispatcher using that permit. Transport,
   adapter and worker retries are disabled. Each invocation causes at most
   one service acceptance; the model does not cure a duplicating transport.
4. A sale and its authoritative audit result are atomic at the simulated
   service, independently of the local journal. Receipt evidence binds the
   entire `B` and the ticket. `FencedNoSale` is a durable guarantee that no
   old in-flight request for `B` can ever sell later, not a timeout or empty
   query. An adapter unable to promise that returns unknown forever if needed.
5. Restore validates program, order, arguments, action and schema before
   any effect, including inspection. Mismatched/corrupt evidence refuses
   progress without deleting the intent. The runner and adapters, including
   validation, are trusted; these types cannot make a dishonest host honest.

There is no transaction spanning the journal and service. No credentials,
network authentication scheme or production disk format is specified here.
The memory contract covers this run's declared state, not secure memory
erasure, other processes or a caller deliberately creating another order.

## Transitions

`register(B)` atomically creates `Ready(B)` and `K`. An existing order must
restore that record. Starting a ready run may read and display a bulletin.
`begin` atomically changes `Ready(B)` to `Intent(B)` and gives the winning
live runner one volatile permit. Only that permit can invoke the service.
After a definitive response, or on later inspection, the runner verifies
evidence and commits `Done(B,t)` or `Closed(B)` before terminal display.

For an intent, `Sold(B,t)` yields `done(t)`; `FencedNoSale(B)` yields
`not_done`; `Empty`, `InFlight` and unavailability yield `unknown`. Unknown
parks at `settle` with the same intent. Inspection is read-only; repeating
it is safe. A direct response also needs the same identity validation.

Death at any transition clears `F`, the program counter and every volatile
permit. Restore reads the validated local record. Ready can start; Intent
can only inspect; Done and Closed display their stored terminal outcome.
No response remembered only in RAM is trusted after death. A crash while
parking leaves Intent; it does not undo a sale. A delayed original request
may still move the service from InFlight to Sold while the client waits.

## Every supported crash boundary

During an atomic step, recover its before or after row. Pure calculations,
display and read-only queries can be interrupted anywhere without granting
dispatch. There are no other modeled external effects.

| Death boundary | Durable local record | Service possibilities | Legal recovery |
| --- | --- | --- | --- |
| Before registration commits | no registered run | no request | uniquely register, or refuse uncertain/corrupt registration |
| After registration, before/during bulletin | Ready | Empty | enter start with fresh bulletin |
| Before intent commit | Ready | Empty | begin once after restore |
| Intent commit old side | Ready | Empty | begin once after restore |
| Intent commit new side, before dispatch | Intent | Empty | inspect; unknown, possibly zero sales forever |
| Dispatch issued, before service acts | Intent | Empty/InFlight | inspect; unknown; never dispatch again |
| Service action before local receipt | Intent | Sold | matching authoritative receipt permits Done |
| Response arrived in volatile memory only | Intent | Sold/FencedNoSale | re-inspect; do not trust lost response |
| Terminal local commit old side | Intent | Sold/FencedNoSale | re-inspect and retry local commit only |
| Terminal local commit new side | Done/Closed | same terminal service result | display recorded outcome |
| During/after terminal display | Done/Closed | same | repeatable local display; no sale |
| During unknown wait or inspection | Intent | any service state | inspect again; empty stays unknown |
| Changed program/arguments/label/schema | any existing record | unchanged by refusal | refuse before dispatch or query |
| Corrupt or mismatched evidence | Intent or unreadable state | potentially sold | refuse; preserve uncertainty |

The fifth row is an essential failed-liveness witness: no sale happened,
but absence of a dispatch receipt does not permit retry. The seventh is
the complementary success-with-lost-receipt witness. Both must exist in
any later implementation's tests; neither can be collapsed into the other.

Consider two concrete worlds at inspection. In world A the process died
after committing intent and before dispatch: no ticket will ever be sold.
In world B it dispatched before dying, but the original request is delayed:
no ticket has been sold *yet*. Both expose the same local Intent and an
empty service query. A decision using only those observations cannot tell
them apart. Retrying could create two sales in B; declaring no sale could
be false later in B. Waiting is safe in both and may never progress in A.
This is the finite ambiguity the core preserves, not a new impossibility
theorem. A fence or definitive receipt adds evidence absent from those two
observations; a different spelling of `unknown` does not.

## Small safety argument and its limits

Single invocation follows by induction over transitions. Registration
creates no permit. Only the unique durable Ready-to-Intent change creates
one; that change cannot happen twice for the order. The winning runner
consumes its permit, or loses it on death. No transition from Intent,
Done, Closed or refusal creates another permit. Thus there is at most one
application invocation, and at most one modeled sale under assumption 3.

Forgotten-state exclusion follows from the recovery context `K;empty` and
the absence of references/functions, rather than from replay recomputing a
lost value. Truthful terminal results follow from binding validation and
assumption 4. These arguments are independent: neither typed forgetting
nor an exhaustive match proves the service's answer authoritative.

There is no liveness or exactly-once theorem. Display can repeat. The
service may never act or answer; permanent waiting is allowed. Storage
corruption, competing unfenced dispatchers and false authoritative evidence
are not repaired by this core. Changed-code refusal is not code migration.
