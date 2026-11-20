# Scoped data across two-label calls

This is the second first-stage result, following [the scope
lemma](SEMANTICS.md). It adds nested parameterless calls with an acyclic call
graph. It does not yet add Janus conditionals, loops, recursion or explicit
`uncall`. Backward stepping is an inverse transition, not an `uncall` statement.

Run the current two-label model:

```sh
python3 projects/janus-local-steps/control_machine.py
python3 -m unittest discover -s projects/janus-local-steps -v
```

The first command was run on 20 November 2026. Its saved state was:

```json
{"calls":["main:call:1","worker:call:1"],"control":["leaf:data:1","leaf:data:2"],"integers":{"g":4,"x":4,"y":5,"z":0},"stacks":{"s":[12,99]}}
```

A fresh subprocess received only that JSON, reconstructed the same static
program, and reversed six transitions to:

```json
{"calls":[],"control":["main:start","main:data:0"],"integers":{"g":4},"stacks":{"s":[99]}}
```

The executable's full run contains 14 transitions. The tests check every
edge in both directions and recovery from every checkpoint, for eleven
different integer inputs. This finite evidence checks the implementation;
the argument below is independent of the sample values.

## Exact fragment and compilation boundary

Each procedure contains the scope-kernel statements. A call to another
procedure can be inserted at any compiled instruction boundary, including
inside a local block or at the end. At most one call is inserted at a boundary;
successive calls can have an intervening empty-effect update when an integer
is in scope. This
representation is a prototype API, not a parser for Janus source text.

All procedures share the same declared global integers and data stacks.
Local names are disjoint from those names and from locals of other
procedures. There is no shadowing, aliasing, parameter passing or recursion.
The call graph must be acyclic. A callee's expressions may read globals and
its own live locals; they cannot read a suspended caller's locals. The
compiler and projection enforce this even though all live values inhabit
one store. These restrictions are part of the theorem, not optimization hints.

The intended larger fragment retains these restrictions and adds paired
Janus conditionals and loops and explicit call/uncall. It still uses
unbounded integers and finite integer stacks. Its control rules and
correspondence have not been proved here. Array access, recursion, dynamic
allocation beyond local bindings, callbacks and concurrency remain outside
that target. In particular, the current example is not yet the promised
list-rotation program.

## State and invariant

A procedure's static instruction chain has distinct start and stop markers.
Every other label denotes either one scoped-data instruction or a call.
There is a unique static predecessor and successor at every ordinary label.
Calls have no interprocedural static edges.

Let Gamma be the global integer domain. Let L(p,k) be the set of locals live
in procedure p at kernel boundary k. Define a configuration as

```
(rho, tau, previous, following, K)
```

rho and tau contain current integer and stack data. `(previous,following)`
is one intraprocedural edge. K is a list of call-site labels, oldest first.
Each label determines its caller, callee and caller boundary from static
text. K contains no values or copies of stores.

Starting at the main procedure, traverse K: each call site must belong to
the current procedure, then move to its callee. This traversal must finish
at the procedure owning the control edge. If the suspended call sites are
`(p_1,k_1),...,(p_m,k_m)` and the active procedure/boundary is `(p,k)`, require

```
dom(rho) = Gamma union L(p_1,k_1) union ... union L(p_m,k_m) union L(p,k).
```

The local parts are disjoint. All globals and all these locals are live,
including locals belonging to suspended callers. Stack data has the fixed
declared stack domain. Values must have the types from SEMANTICS.md.
The active boundary k is read from the following node; call and data nodes
inserted at the same kernel boundary use the same k.

Initial configurations have empty K and the main entry edge, with exactly
the declared globals and stacks. Their values may be arbitrary. Reachable
configurations are those obtained by finitely many successful forward or
backward transitions. The loader verifies the displayed structural invariant,
not provenance or full reachability. A checkpoint must be paired with the
same static program; a structurally valid forged state may still fail a
scope assertion.

## Data steps do not touch suspended locals

At a data instruction in p, project rho to Gamma union L(p,k), apply the
already-proved kernel map F, and merge its result with the untouched
suspended locals eta. Stack data is shared, so it is passed to F directly.

Because the compiler restricts expression names to the projected domain,
F cannot read or modify eta. Its lifted map is `F x identity_eta`.
The inverse is `F^-1 x identity_eta`: composing in either order is identity
on the relevant partial-map domain. Entering or leaving a scope changes
only its active local domain. Hence the invariant is preserved and the
scope inverse theorem applies unchanged in the presence of live callers.

For an ordinary node b with predecessor a and successor c:

```
forward:  (s, a,b, K) -> (F_b(s), b,c, K)
backward: (t, b,c, K) -> (F_b^-1(t), a,b, K).
```

Here s abbreviates the current data maps, not a saved store. F_b is partial,
so the matching check may refuse before any data is removed.

## Call and return inverse pairs

Let c be a call-site label with predecessor a, successor b and target q.
Let `(start_q, first_q)` be q's entry edge and `(last_q, stop_q)` its exit edge.
For an empty callee the entry and exit edges are both `(start_q,stop_q)`.
Write `K.c` for pushing a call-site label. The data s is unchanged by all
four administrative transitions:

```
Call:          (s, a,c, K)             -> (s, start_q,first_q, K.c)
UndoCall:      (s, start_q,first_q,K.c) -> (s, a,c, K)

Return:        (s, last_q,stop_q,K.c)   -> (s, c,b, K)
UndoReturn:    (s, c,b,K)              -> (s, last_q,stop_q,K.c).
```

At Call, the caller's currently live locals change status from active to
suspended, but they remain in rho. q starts with no locals, so the required
store domain is unchanged. At Return, q has closed its own locals and the
caller resumes at the same boundary as its call, again with the same domain.
UndoCall and UndoReturn use the identical domain identities in reverse.
The call chain determines the correct procedure at each start/stop, and the
call label determines both return edges. No old values are needed.

**Theorem 4.** Every successful forward transition in this model has exactly
its indicated backward inverse, and conversely, on structurally valid states.

For data transitions use the lifted primitive inverse. For Call/UndoCall and
Return/UndoReturn substitute the four equations above; the labels, K and s
return exactly to their original values. A call label is distinct from a
data label, and a start/stop marker is distinct from both, so the inverse
cases do not compete. Unique intraprocedural predecessors and successors
remove any remaining choice. The domain identities show that both sides
of each equation satisfy the invariant. This proves the result for all
declared values and nesting depths admitted by the acyclic graph.

The runtime validates the invariant both before and after a transition.
Thus a missing suspended local, a foreign return label, a reversed frame
chain, or an extra unaccounted binding is rejected. This is not a substitute
for a proof of full Janus control with joins and loops; unique linear
predecessors are an explicit hypothesis here.

## Whole-procedure correspondence

Give a call to q the whole-procedure meaning of q, projected to its globals
and stacks and extended by identity on the caller locals. Insert that map
at the annotated boundary among the kernel's primitive maps. The resulting
composition defines a procedure's whole-run meaning.

Order procedures by the acyclic call graph. For a procedure with no calls,
Theorem 3 applies. Inductively assume correspondence for all callees of p.
At a call site, Call pushes one frame, the induction hypothesis relates the
callee's balanced run to its whole-procedure map, and Return pops that frame.
The two administrative transitions leave data unchanged. Concatenating with
the intervening kernel steps proves correspondence for p. Undefinedness
agrees: both computations require the same primitive and callee checks.
Reversing the balanced run yields the inverse composition by Theorem 4.

## Relation to the published Janus machine

The two-label/control-frame arrangement follows the basic Call and Return1
rules in [Lanese and Vidal, section 4.1, Figure 12](https://arxiv.org/html/2602.16913v2),
with the inverse transitions from section 4.2. It is not a new call mechanism.
For the common subset of parameterless, acyclic procedures and integer
updates, relabel our nodes by their distinct published labels and reverse
our bottom-first K to the paper's top-first stack notation. Forget explicit
zero bindings in the global store. The displayed data, call and return
transitions then match those rules. At zero-valued initial globals, the
initial-state convention matches too.

Our added part is the explicit finite domain of live locals, its caller
projection, and its interaction with the scope maps. That extension has been
proved here only for the stated call fragment. This does not establish
priority: L4 already has live environments and call frames, and the unread
Concurrent Janus memory-management rules remain a material comparison.

Next, the full project needs joins, paired branch assertions and loop
contexts, and their scope invariant. It must not infer their inverse theorem
from the absence of failures in this linear model. The first milestone also
still needs independent evaluation of the concrete prior-work distinction.
