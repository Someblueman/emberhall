# Admission review: reconstructing the negative finding

Isolde, 18 November 2026. Independent reconstruction for project
`great-lethe-20261117`, milestone 1; task `lethe-admission-reconstruction`.
Frozen candidate: Hawthorn run `1268bdfa9dab42338bc2062828beb86d`, private
commit `6949f11fca13b3c1e4c848a0516119eb0acaa04b`, immutable finish 16052.
I obtained the five artifacts through trusted integrate inspection and
verified every SHA-256 against that finish before reading them:
`README.md`, `SEMANTICS.md`, `COMPARISON.md`, `ferry.lethe` and
`comparison.rs` all match. This review owns only this file; the candidate
is unchanged, and the owner's milestone/drop decision remains separate.

**Verdict: I reconstruct the failure to establish the frozen advantage.**
The candidate states a precise little safety contract, but in this closed
single-order core an ordinary typed encoding enforces the same two
restrictions under the same trusted-host assumptions. I tried to break
that claim four ways (below) and each attempt either fails or only works
by leaving the frozen contract, which the gate forbids as a rescue. A
stranger's one-sentence worth test: as a language there is not yet
anything here a programmer could not already get, but the pinned
counterexample — one order that must sometimes wait forever — is worth
keeping precisely because it stopped a runtime being built on a hope.

## What I re-ran, and what it actually proves

From the inspected `comparison.rs` in scratch space, with the repository
untouched (`rustc 1.98.0`; the author tested 1.97.1):

- All six interface tests pass and `rustfmt --check` is clean.
- The three deliberate invalid clients fail for exactly the stated
  reasons: `retry_pending` E0308 (`Pending` is not `Ready`),
  `forget_scope` E0425 (`bulletin` not in scope), `forge_ticket` E0451
  (private `Ticket` fields).
- Three probes of my own, appended only to my scratch copy: constructing
  `Ready` from client code fails (E0603, private constructor), and using
  a `Pending` twice fails (E0382, moved value — the permissions are
  linear in effect). A wildcard match arm that collapses `NotDone` into
  a panic *does* compile; see challenge 2 for why that is a liveness
  difference, not a safety one.

These checks witness the sealed interface and the six-field identity
validation. Like the author, I claim no more for them: they do not
execute the crash table, write a journal, simulate power loss, or prove
disk durability, and there is no Lethe checker to run at all. The
candidate is a paper contract plus a comparison; both sides of the
comparison lean on the same unwritten trusted runner.

## The argument, reconstructed in my own order

**At most one sale.** Registration mints no dispatch permit. Only the
atomic durable `Ready -> Intent` transition mints exactly one, volatile
and one-use, for the runner that wins it. Every later state (`Intent`,
`Done`, `Closed`, refusal, recovery) mints none, and death destroys the
permit without transfer. By induction over the listed transitions there
is at most one application invocation; at most one sale then needs the
further assumption that one invocation causes at most one service
acceptance and that transport retries are off. Both assumptions are
stated, not smuggled, and the Rust `begin`/`invoke_once` pair has the
same shape: `Ready` is consumed once, `Dispatch` cannot be recovered
from a restored `Intent`, and `invoke_once` consumes both tokens.

**Forgotten state stays forgotten.** Recovery is typed in context
`K ; empty`: no fleeting name, alias or product of one can be mentioned,
and the core has no references, functions or closures through which a
fleeting value could be smuggled into storage. This is a syntactic
restriction of a deliberately small grammar, not an analysis result
about a general language — the semantics says so itself. The Rust side
gets the identical property by lexical scope: `bulletin` is a local of
the start entry, `settle` receives only an `Outcome`, and my
`forget_scope` rerun confirms the compiler refuses the alias there.

**The crash table's two load-bearing rows.** Dying after the intent
commit but before dispatch leaves a durable `Intent` and zero sales,
possibly forever; dying after the service acted but before any durable
receipt leaves the same `Intent` and one sale. I walked both through
the transition rules and the `restore`/`observe` code paths: a restored
intent yields `Unknown(Pending)` in each case, only matching
authoritative `Sold` evidence can produce a ticket, only a durable
fence (`Closed` evidence) can cancel, and `Missing`/`InFlight`/
`Unavailable` all preserve the same pending order. The shipped tests
exercise the last three explicitly. No row lets recovery invent a
receipt, treat an empty lookup as no-sale, or dispatch again.

**Zero-sale versus delayed-sale.** At inspection, world A (died before
dispatch; no sale will ever happen) and world B (dispatched; the one
request is still in flight; no sale has happened *yet*) present the
same two observations: local `Intent` and an empty service answer. Any
rule using only those observations that retries risks a second sale in
B (nothing in the contract makes the service deduplicate a *new*
invocation), and any rule that declares no-sale can become false in B.
Waiting is safe in both and makes no progress in A. That is a correct
finite indistinguishability argument; a fence or a receipt resolves it
by adding evidence, and the core is right that renaming the `unknown`
branch adds none. Permanent waiting is therefore an honest outcome of
this contract, not an oversight.

## Four attempts to overturn the negative result

1. **"Rust only shows expressibility; Lethe enforces it for every
   program."** True in general and the strongest objection. A Rust
   author can add ambient I/O, stash the bulletin in global state, use
   `unsafe`, or ignore the boundary module entirely; the Lethe grammar
   as written cannot even spell those moves. But the frozen comparison
   is one closed client with one service capability, and there the two
   programs reject and accept the same things. The enforcement gap
   appears only when the comparison widens to *all* programs each
   language admits — a broader effect-confinement claim this milestone
   never specified or tested, and which the comparison names honestly
   as unexamined. Rescuing the gate with it now would change the
   experiment after seeing its result. It is a reason a *future*,
   differently-scoped brief might exist; it is not an error in this one.

2. **"Exhaustive handling is compulsory in Lethe, optional in Rust."**
   My wildcard probe confirms a Rust client may collapse arms or drop
   the `Outcome` altogether. But dropping is also legal in the core,
   which expressly permits refusing and leaving the intent unresolved;
   in neither language can the client convert that refusal into a second
   booking or a fabricated ticket. The remaining difference is whether
   the programmer must *write down* the unknown arm. For the single
   fixed program both texts do write it, in about the same number of
   lines. That is notation and discipline, which the milestone excludes
   as sufficient by itself.

3. **"The ferry program is far shorter, so clearer."** `ferry.lethe` is
   33 lines and `comparison.rs` is 280, but most of the Rust is the
   trusted boundary and its tests — work Lethe also needs, as runner
   code that has not been written. Counting an unwritten runner as zero
   would manufacture the clarity win. Client against client, the two
   settle blocks are near-identical, and no independent-reader test of
   either text exists. Clarity is plausible, not demonstrated.

4. **"Exact binding is stronger in the core."** The core compares full
   `program_bytes`; the Rust `Binding.program` is a static label. But
   supplying the *true* program identity is a trusted-host duty on both
   sides — the paper checker does not exist either — and within that
   shared assumption the Rust test mutates each of the six identity
   components and is refused every time, as I re-ran. Changed-code
   refusal is at parity; neither side offers code migration, and neither
   pretends to.

## Primary sources reopened

- **Modal Crash Types** (Derakhshan et al., ESOP 2023). I corroborated
  the stable/unstable distinction, restoration erasing volatile state,
  and the crash-type framing from the publisher's and authors' pages;
  I did not re-derive Figure 4 line by line. The comparison's use is
  appropriately modest: a labelled schematic judgment, no claim that
  the published calculus runs the ferry, and no claim that Lethe
  invents the memory rule. Nothing I found contradicts that reading.
- **AWS Durable Execution idempotency guide.** Verified directly: under
  at-most-once-per-retry the `START` checkpoint commits *before* the
  step body runs, interruption raises `StepInterrupted` on replay
  instead of re-executing, and a no-retry policy is separately required
  because the default is at-least-once and a retry can still start a
  new attempt. That is exactly the comparison's account, including its
  caution. I verified `StepInterruptedError` and the interrupted-step
  section exist in the error guide; I did not fully re-open its payment
  example's wording, and that example is not load-bearing here — the
  Rust encoding, which I ran, carries the negative argument.
- **Ficus** (Zhang, Gregersen & Tassarotti, arXiv:2607.12642, §6).
  Verified that §6 is a crash-recovery logic with asynchronous durable
  storage recovering Perennial-style features. Combined typed crash and
  effect reasoning therefore predates this core, as claimed; using it
  would impose proof obligations, and the comparison does not pretend
  to have discharged any.
- **AWS Builders' Library, idempotent APIs.** Corroborated the
  atomic receiver-side recording and late/delayed-request handling the
  comparison cites for the missing-result-versus-durable-fence
  distinction. Types on the client supply neither, on either side.

## Limits of this review

The transition-by-transition correspondence between core and Rust is a
hand argument (the author says so); I checked its cases against the
code and found no missing transition, but nothing here is
machine-checked. The crash table is complete only over the modeled
boundaries — storage corruption, a duplicating transport, unfenced
competing runners and a dishonest host are outside it by stated
assumption, for both programs equally. My one wording nit: the
pre-registration row's "refuse uncertain registration" hedges a case
the atomicity assumption already reduces to the old-or-new record; it
changes no outcome. I ran no service, installed nothing, and executed
no web code. Scratch copies and probes stay outside the repository,
uncommitted.

**What would change this verdict:** a concrete program *inside this
unchanged contract and its stated assumptions* that the core accepts
safely while the sealed Rust encoding either rejects it or admits an
unsafe trace — or the reverse. I looked for one with the probes above
and did not find it. Until somebody does, the required combined safety
or clarity advantage is not established, and building a runtime would
decorate that gap rather than close it. I agree with dropping this
scope; whether the project itself drops is the owner's separate call.

