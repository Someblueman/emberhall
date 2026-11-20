# A reversible scope boundary

First-stage working result, 20 November 2026. This proves the scope and
data-stack kernel below. It does **not** yet prove an extension of every
control rule in the published Janus machine. The generic algebra of partial
injections is established prior work; this document makes no novelty claim
for that algebra or for reversible allocation.

## Fragment and states

There are disjoint sets of integer names and stack names. Integers range over
all of Z; a stack is a finite list of integers with its head at the left.
Expressions are finite trees of integer literals, live integer names, addition,
subtraction and multiplication. Evaluation is pure and total when every name
is live. There are no machine-integer overflows or effects in expressions.

The implemented statements are sequences of:

```
x += e                    x -= e
push(x, s)                pop(x, s)
local x = e; body; delocal x = f
```

A local name must be fresh among live integers and all stack names. Shadowing
is excluded. The two boundary expressions may use any parent-scope integer,
including an enclosing local, but neither can use the newly bound `x`.
An update's expression cannot use its target. Names cannot escape a scope.
The empty sequence is skip. No heap, arrays, aliasing, procedures, branches,
loops or input/output statements are in this kernel.

Compile a sequence by emitting each primitive in order; compile a local as
`Enter(x,e)`, compiled body, `Leave(x,f)`. Record the set D_k of live integer
names at every instruction boundary k. Entry adds one name and leave removes
it. The data-stack name set is fixed. The code and all D_k are static.

A state is `(k, rho, tau)`: the next instruction index, the current integer
map, and the current stack map. A well-shaped state has `dom(rho) = D_k`,
the fixed stack domain, integer values and finite integer stacks. This exact
domain condition distinguishes an absent local from a live local equal to
zero. The serialized representation uses canonically ordered names.

Legal initial states have k=0, exactly the declared global integers and data
stacks, and arbitrary values of their declared types. There is no requirement
that all globals or stacks start at zero. A reachable state is one obtained
from a legal initial state by finitely many successful forward or backward
steps. Its domain is D_k by induction; integer types, stack types and the
absence of aliases are preserved. Shape validation alone does not prove
reachability or promise that the next assertion succeeds.

## Boundary maps and inverse theorem

Write `rho[x:v]` for fresh extension, and `rho\x` for restriction removing x.
Fix a parent live-name set D with x outside D, and an expression e over D.
The following are partial maps; an unsatisfied premise means refusal, with
no mutation of the input state.

```
C_e(rho, tau) = (rho[x : eval(e,rho)], tau)

D_e(rho', tau) = (rho'\x, tau)
    only if rho'(x) = eval(e, rho'\x).
```

The domains on the two sides are exactly D and D union {x}. In particular,
the deletion test is not allowed to obtain information from x itself.

**Lemma 1.** C_e and D_e are mutually inverse partial bijections.

For any parent state `(rho,tau)`, let v=eval(e,rho). C_e leaves every old
binding unchanged and installs x=v. D_e sees exactly rho after restricting
that extension, so its equality succeeds and it returns the original state.
Conversely, suppose D_e is defined on `(rho',tau)`. Let rho=rho'\x. Its
premise says rho'(x)=eval(e,rho); C_e therefore reinstalls exactly the removed
binding. Every other binding and every stack was retained. Thus C_e after
D_e is identity on D_e's domain. These two equations prove injectivity and
the inverse statement for arbitrary integer values, not just tested cases.

For `local x=e; S; delocal x=f`, entry uses C_e and exit uses D_f.
Reverse entry uses D_e, and reverse exit uses C_f. In particular, reverse exit
evaluates f in the **final surviving store**, not the store that existed at
entry. e and f may differ. Variables read by them may have changed inside S.
Neither the initial local value nor an old parent store is saved.

**Why the premise matters.** If `delocal x=x` were admitted and interpreted
as testing x against its own current value, both `{g:0,x:1}` and `{g:0,x:2}`
would pass, then become `{g:0}`. The deletion would be noninjective. Checking
before removal is necessary, but not sufficient: the expression must also
be evaluable from the surviving state. The compiler rejects this example.

**Why current values matter.** Start with g=4 and enter x=g. Add seven to x
and g, then leave with x=g. At exit both equal 11. Reverse exit must recreate
x=11. After reversing the two updates, x and g both equal 4 and reverse entry
can remove x. Saving or reusing x's initial value at reverse exit would be
wrong. The executable test `test_exit_uses_final_surviving_values` checks it.

## Other primitive maps

For an update, x is absent from e. Replacing rho(x) by rho(x)+eval(e,rho)
does not change any name read by e, so subtraction in the resulting store
undoes addition, and conversely. The argument is identical for subtraction.

For stack transfer, with v arbitrary and w a finite stack:

```
push:  (rho[x:v], tau[s:w])       -> (rho[x:0], tau[s:v::w])
pop:   (rho[x:0], tau[s:v::w])    -> (rho[x:v], tau[s:w])
```

The assignments change distinct bindings of distinct types. The displayed
equations show both inverse identities. Pop is undefined on an empty stack
or a nonzero destination; overwriting that destination would lose information.
The stack's values are live program data, not a trace of former stores.

## Machine theorem

Let F_i be the primitive map compiled at index i. A forward step applies
F_k and changes k to k+1. A backward step at k>0 applies F_(k-1)'s specified
inverse and changes k to k-1. The endpoints have no step in the outward
direction. All types and exact domains are validated before each step.

**Theorem 2.** For every well-shaped state p and q of this compiled fragment,
`forward(p)=q` if and only if `backward(q)=p`.

The index on q identifies the same instruction k used on p. Lemma 1 covers
both scope boundaries, the preceding equations cover updates and transfers,
and each inverse returns the original map and index. Conversely, each
successful inverse has the forward map as its inverse by those same
equations. Static D_k includes exactly the names needed by its expression.
There is no choice of an earlier instruction and no lookup in execution
history. The theorem applies to all well-shaped states where the relevant
partial step succeeds, hence in particular to all reachable states.

By induction on the number of successful steps, reversing a forward prefix
returns its initial state, and reversing a suffix can be resumed from its
last state plus the same static program. No termination claim is needed.

## Whole-statement correspondence

Define the whole-statement meaning on stores and stacks compositionally.
Updates and transfers use the maps above; a sequence uses their composition.
For a local statement its meaning is:

```
[[local x=e; S; delocal x=f]] = D_f o [[S]] o C_e.
```

It is undefined if a body operation or either boundary check is undefined.
The body starts and finishes with parent domain D union {x}; nested scopes
must have closed. This is the allocate/body/assert-and-deallocate convention
described by Jana's local/delocal syntax. It is our explicit target relation;
a proof against Jana's executable implementation is still outstanding.

**Theorem 3.** Executing a compiled statement from its first to last boundary
has exactly its whole-statement meaning, in both directions.

Induct on the statement tree. A primitive emits its own map. Concatenating
compiled sequences concatenates their runs and composes the same maps. A
local emits C_e, the body and D_f; the induction hypothesis identifies the
middle run with [[S]], yielding the displayed composition. Undefinedness also
agrees: each side requires exactly the same operations and equality checks
in the same order. For reverse execution, Theorem 2 gives the reverse sequence
of inverse maps, and `(D_f o [[S]] o C_e)^-1` is
`D_e o [[S]]^-1 o C_f`. This also establishes that the composition is a
partial injection. This structural argument covers arbitrary finite nesting,
not only the two nesting levels used by the demonstration.

## What the first result does and does not settle

The boundary lemma works around any body relation on the extended domain;
the whole-machine proof above is for the finite straight-line kernel only.
To extend the published Janus machine, a later proof must incorporate its
pair of control labels and live control stack, show how local scope records
interact with calls and uncall, and prove reachable-context correspondence at
branches, loops and returns. A plain increasing index cannot stand in for
that proof. A past-store trace would avoid some issues but violates this
project's specified result.

The kernel is a worked foundation, not a research novelty result or a
completed first milestone. The comparison in [RELATED_WORK.md](RELATED_WORK.md)
records substantial prior overlap and the unread full texts. An independent
resident must still judge whether a completed faithful Janus extension adds
enough beyond them to continue the selected project.
