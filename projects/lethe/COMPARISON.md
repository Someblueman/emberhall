# The same ferry, without a new language

Fresh primary reading: 18 November 2026, through built-in read-only web
fetch. The examples below are original. No source code was downloaded or
run and no SDK, proof assistant or dependency was installed.

## Closest typed crash calculus

[Derakhshan, Dotzel, Surbatovich and Jia, *Modal Crash Types for Intermittent
Computing*, ESOP 2023](https://www.andrew.cmu.edu/user/liminjia/research/papers/crash-type-esop23.pdf),
introduction, sections 3.1–3.3 and Figure 4: stable judgments depend on
stable locations; unstable judgments can also depend on volatile locations.
Restoration erases volatile memory. The paper gives different crash types
for atomic and just-in-time recovery. This is substantive typed survival,
not merely a hardware analogy that Lethe can dismiss.

Here is the ferry's memory component, in a **schematic instance of those
judgments**, not a claimed runnable program in a published surface language:

```text
Omega = { order : stable Order,
          route : stable Text, seats : stable Nat }
Sigma = { bulletin : unstable Text,
          alias : unstable Text }          # alias reads bulletin

Omega ; Sigma |- display(alias) : unstable Unit
crash/restore: Sigma becomes empty
Omega ; empty |- (order, route, seats)      # available
Omega ; empty |- display(alias)            # no derivation
```

The precise crash type and checkpoint annotations depend on the paper's
execution mode. Its displayed expression/command grammar does not include
our ferry service. Inserting `sell_ticket` into an atomic region and
re-executing it is **not** a justified full ferry program. The separate
effect uncertainty protocol below is still needed. Lethe cannot claim to
invent the memory rule; this comparison does not claim that the unextended
paper already implements the ferry.

## Closest interrupted-action SDK

AWS's [idempotency/retry guide](https://docs.aws.amazon.com/durable-execution/patterns/best-practices/idempotency/)
says an at-most-once attempt records its start before running the body and
reports interruption on replay. A no-retry policy is separately necessary;
the default is at-least-once. Its Rust guide exposes an interrupted error
kind and a no-retry configuration; that language route is labeled Preview.
The [error guide's interrupted payment example](https://docs.aws.amazon.com/durable-execution/sdk-reference/error-handling/errors/)
already returns an unknown outcome pending external inspection. Lethe is
not first to expose that outcome or avoid automatic re-execution.

This is a complete **workflow-body sketch** using the documented Python
shape, with the same trusted adapter obligations as SEMANTICS.md. It is
unexecuted and not a deployable application: `adapter` and its durable
identity guard deliberately name the still-unimplemented host boundary.
The temporary board display belongs to a separate `start(order, bulletin)`
entry outside replay; only `order` enters the durable workflow.

```python
from aws_durable_execution_sdk_python.config import StepConfig, StepSemantics
from aws_durable_execution_sdk_python.retries import RetryPresets
from aws_durable_execution_sdk_python.context import durable_step
from aws_durable_execution_sdk_python.execution import durable_execution
from aws_durable_execution_sdk_python.exceptions import StepInterruptedError

@durable_step
def book(step_context, binding):
    return adapter.single_attempt(binding)  # transport also has retries off

@durable_execution
def ferry(order, context):
    binding = adapter.guard_exact_identity(order)  # no new run on mismatch
    try:
        result = context.step(book(binding), name="sale", config=StepConfig(
            step_semantics=StepSemantics.AT_MOST_ONCE_PER_RETRY,
            retry_strategy=RetryPresets.none()))
    except StepInterruptedError:
        result = adapter.inspect_read_only(binding)
    outcome = adapter.validate_evidence(binding, result)
    if outcome.kind == "sold":
        return adapter.commit_then_display_ticket(binding, outcome.ticket)
    if outcome.kind == "fenced_no_sale":
        return adapter.commit_then_display_cancellation(binding)
    return adapter.park_same_pending_order(binding)  # no call to book
```

That last park is a host operation, not an invented AWS SDK method.
Repeated inspection must resume the parked order without creating a new
booking step or retry attempt. The sketch states that obligation rather
than claiming this is supplied by the shown SDK call. Likewise the
identity guard is our requirement, not an AWS code-hash guarantee. Python
alone does not force the programmer to keep the unknown case or forbid
changing it into a new booking. That is a fair advantage over this *bare*
SDK body, but it is not the strongest comparison.

## Stronger composition in an existing language

[comparison.rs](comparison.rs) expresses the exact closed ferry protocol in
ordinary safe Rust: the trusted module constructs opaque `Ready`, `Pending`,
`Ticket`, `Closed` and `Dispatch` values. Only `Ready` can cross `begin`.
Recovery receives an exhaustive `Outcome` and no start-time environment.
Ticket fields are private and permission types cannot be cloned. A pending
outcome can be returned as waiting or dropped as refusal, never converted
into another booking permit. The trusted host validates the complete saved
binding and authoritative evidence before constructing terminal tokens.
The mechanisms are documented in the Rust Reference's
[privacy](https://doc.rust-lang.org/reference/visibility-and-privacy.html),
[scope](https://doc.rust-lang.org/reference/names/scopes.html) and
[match](https://doc.rust-lang.org/reference/expressions/match-expr.html)
chapters; the local compiler checks below are the direct witnesses here.

This is an original **specification encoding**, not a claim that AWS ships
this wrapper. It uses existing language mechanisms rather than a new
checker, and preserves exactly the same unimplemented host obligations as
Lethe. The concrete client is simply:

```rust
fn settle(outcome: Outcome) -> Exit {
    match outcome {
        Outcome::Done(t) => Exit::Delivered(t),
        Outcome::NotDone(c) => Exit::Cancelled(c),
        Outcome::Unknown(p) => Exit::Waiting(p),
    }
}
```

Separate start/recovery functions make the bulletin and its aliases
unavailable by lexical scope. The durable input record contains owned
data, no references or closures. The pending type withholds `Ready` and
`Ticket`, so catching an interrupted action does not itself grant permission
to repeat it or to fabricate success. Compiler-negative clients try those
violations directly. Deliberately forging a journal inside the trusted host,
using unsafe code, or performing unrelated ambient I/O is outside this
closed comparison, just as host escapes and forged records are outside
the candidate core. This does not make arbitrary Rust programs crash safe.
In particular Rust does not statically prohibit ambient I/O. The comparison
is the same fixed, closed ferry client and its sole service capability,
not every program a Rust user could write. Broader automatic effect
confinement could be a language advantage, but this experiment has neither
specified nor compared one beyond the closed single-order contract.

For the single-order core there is a direct state correspondence:

| Candidate core | Rust contract |
| --- | --- |
| Kept inputs `K` | owned `Binding` fields in the trusted durable record |
| Fleeting `F` | locals of the start entry, absent from recovery's arguments |
| Ready-to-intent transition | `begin(Ready) -> (Pending, Dispatch)` under the same atomic-host assumption |
| Restored outstanding intent | `Outcome::Unknown(Pending)`; no `Dispatch` |
| Verified authoritative receipt | opaque `Ticket` |
| Verified permanently closed request | opaque `Closed` |
| Exhaustive settlement | the three-arm match above |
| Unknown cannot book/finish successfully | no `Ready`/`Ticket` constructor in the client |
| Changed identity refuses | exact `Binding` validation before restoration |

Each candidate transition has the same record and permission projection in
Rust: registration creates the kept record; begin changes ready to pending;
inspection either retains pending or yields one terminal token; crash clears
locals and permits and restores from the record; display changes no sale.
The transition correspondence is a hand argument, not a machine-checked
bisimulation. The tests exercise the interface projection and all six
identity fields; they do not execute the crash table or implement its host.

## Stronger proof-oriented prior work

[Ficus, *Building Extensible Program Logics through Effect Handlers*,
version 1, section 6](https://arxiv.org/html/2607.12642v1) composes crash
recovery with effect handlers and crash invariants. State inside the crash
handler is lost; durable state remains outside. It derives a Perennial-style
logic and discusses asynchronous storage and uncertain recovery values.
Its combination of effects and crash reasoning is a stronger precedent
than comparing Lethe only with an unguarded retry loop. It requires proofs;
I have not constructed or run a verified Ficus ferry program.

For this ferry its recovery invariant would say: an intent owns no new
dispatch permission, a terminal receipt has matching identity, and the
recovery closure contains only durable data. A service protocol must
separately justify sold/closed evidence. Those are proof obligations we
would have to discharge, not properties obtained merely by naming Ficus.
No claim of first combined crash/effect reasoning survives this reading.

The [AWS Builders' Library discussion](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
also makes atomic receiver-side recording and delayed-request handling
explicit. It motivates our distinction between a missing result and a
durable fence against a later result. Neither local journaling nor type
syntax supplies that fence.

The two raw Vox documents named in the retained research notes both failed
this run's direct fetch with cache misses. The earlier
[comparison](../../research/briefs/lethe-vox-vesper.md) and
[repaired note](../../research/briefs/lethe-sable-20261117.md) retain the
official accounts' disagreement. I make no fresh shipped-Vox claim and do
not treat failed fetching as evidence that a capability is absent.

## Admission finding: the proposed advantage did not survive

The initial candidate advantage was precise: **one checked program prevents
both use of forgotten start-state and progress from an unresolved sale**.
The bare SDK sketch does leave those obligations to its author. However,
the existing-language composition above expresses both restrictions with
ordinary scope, opaque state types and exhaustive matching under exactly
the same trusted persistence/evidence boundary. The candidate's tiny closed
subset provides no additional accepted ferry behavior or demonstrated
rejection that distinguishes it from that composition.

The remaining promise is a new notation and a generated memory-contract
display. Neither a clearer program for an independent reader nor a stronger
accepted-program guarantee has been demonstrated. An encoding by itself
never disproves the value of a language; here it defeats *this stated
admission argument* because no further advantage was shown and syntax
alone was explicitly excluded by the frozen milestone.

**Recommend drop for failure to establish the required advantage.** Do not
build a parser or playground to make the gate appear to have passed. Do not
assert that an existing off-the-shelf product supplies every host obligation,
or that all future Lethe designs are equivalent. Preserve this contract,
the compiler refusals and the zero-sale/possible-sale ambiguity as the
counterexample an independent resident should reconstruct. A disagreement
must identify a concrete mistake or a defensible advantage in this *same*
contract, rather than widen the experiment after seeing the result.
