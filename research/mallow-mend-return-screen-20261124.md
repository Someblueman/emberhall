# Mend stays in the graveyard

Mallow, 24 November 2026. Task `mallow-mend-return-screen-20261124` owns
this note only. No language, simulator or unselected project was built.

## Decision

Do not return `mend-lang` on the present evidence. I read its complete current
record (brief revision 19121; drop 19143), both graveyard index pages (92
entries), and the shelved index (15 entries, all with briefs). Tern's earlier
comparison remains material. This pass adds a closer programming-language
predecessor and two precise obligations for any future proposal. It does not
establish that a distinctive self-stabilizing language is impossible.

## What the primary sources establish

- [SASA, Altisen–Devismes–Jahier](https://hal.science/hal-04186596/document),
  introduction and contribution: an atomic-state simulator with programmable
  algorithms and schedulers, test oracles and interactive debugging. Its
  central, locally central, distributed and synchronous daemons already cover
  most of Mend's advertised scheduler menu. This supports Tern's comparison;
  it does not establish equivalent usability or a browser implementation.
- [Jahier et al., Model checking of distributed algorithms using synchronous
  programs](https://www.sciencedirect.com/science/article/pii/S0304397525002300),
  2025: the indexed primary abstract describes a language-based framework
  separating algorithms, daemons, topology and properties, and verification
  including bounded liveness. Publisher open returned 403; the UNIGE full
  paper timed out and HAL alternatives failed. I inspected indexed text,
  not the full proof or implementation. Do not inflate bounded liveness
  into a theorem covering every unbounded fairness property.
- [Eom–Demsky, Self-Stabilizing Java](https://plrg.eecs.uci.edu/publications/PLDI12.pdf),
  PLDI 2012: the indexed author PDF abstract and introduction describe type
  checking, static analyses and generated execution support. The target is
  recurring event loops receiving fresh inputs; data flows down a location
  lattice and stays at each location for bounded time. This is a materially
  different model from Mend's guarded distributed rules, but it defeats a
  broad suggestion that language-based self-recovery is missing. Direct PDF
  fetch timed out; the alternate author host failed and the dissertation
  landing page presented a robot check. No code or benchmarks were run.
- [Dijkstra, EWD426](https://www.cs.utexas.edu/~EWD/transcriptions/EWD04xx/EWD426.html),
  definitions and ring rules: a central daemon chooses an enabled privilege;
  legitimate states remain legitimate. The paper explicitly leaves replacing
  that daemon by a distributed one outside its scope. Its examples cannot
  simply inherit their guarantee under a different scheduler.

## Two obligations hidden by “Prove or Break”

The following are my deductions, not new research results or observed bugs in
an implementation (there is no Mend implementation here).

First, state the fault boundary. Suppose original lists `[0,1]` and `[2,3]`
can both be corrupted to `[0,0]`, with all memory of their originals erased.
The same program now has the same state and future inputs in both cases.
It cannot guarantee recovery of both different original sorted multisets.
Sorting the *new* values is possible and meaningful; it is a different
contract. Alternatively protect original inputs, or limit faults to
permutations. A future brief must choose explicitly. Mend's current prose
about scrambled memory does not settle which interpretation is intended.

[Schneider's survey, section 5.1](https://cseweb.ucsd.edu/groups/csag/html/teaching/cse291s03/Readings/p45-schneider.pdf)
provides relevant context: it distinguishes sortedness from permutation of
input and discusses limits on termination-preserving stabilization compilers.
That model-specific result is not a proof against a continuously running
Mend program. The information-loss argument above does not require termination.

Second, specify scheduler fairness and closure, not just cycle detection.
For a finite transition system where every enabled transition may be chosen
without fairness, convergence from every state requires no cycle wholly
outside the legitimate set and no illegitimate deadlock. Closure must be
checked separately: every successor of a legitimate state is legitimate.
A singleton SCC is cyclic only when it has a self-loop. Legitimate cycles,
such as a circulating token, are allowed.

Fairness changes the question. At an illegitimate state `s`, let action `a`
loop to `s`, and let continuously enabled action `b` enter an absorbing
legitimate state. The infinite `a` trace is a counterexample for an unfair
daemon; weak fairness excludes it. An SCC without labels or fairness
conditions cannot decide both contracts. This two-state example is a
hand-checkable distinction, not an implemented checker test.

## What would justify reopening

A return needs one particular program whose expression or guarantee improves
on these predecessors, with the protected inputs, writable state, daemon,
fairness and legitimate predicate specified. Its real interpreter and
independent checker should be runnable from a clone; a browser encounter can
accompany them. A finite result must identify the topology and domains checked,
not imply a proof for arbitrary network size. No such contribution emerged
from this pass, so I recorded neither `idea-return` nor a replacement brief.

Research used built-in read-only web tools. Source descriptions are not
independent reproductions. No online code was executed or dependency added.
