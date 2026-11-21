# Reversible Steps Through Local Janus Programs

Work in progress: a mathematical document and executable models for a
proposed statement-level Janus machine with locals and stacks. A scope kernel
and acyclic parameterless-call model run; the full Janus interpreter, loops,
conditionals and explicit uncall are not implemented. No novelty or completed
project milestone is claimed.

From the repository root, using Python 3.10 or later and no dependencies:

```sh
python3 projects/janus-local-steps/check.py
```

Recorded on 20 November 2026:

```text
Ran 9 tests
OK
checkpoint inside two scopes: {"integers": {"g": 4, "x": 5, "y": 0}, "pc": 3, "stacks": {"s": [10, 99]}}
fresh process: reversed 3 steps; recovered {"integers": {"g": 4}, "pc": 0, "stacks": {"s": [99]}}
Scope kernel only: full Janus control flow and novelty review remain open.
```

The command stops after moving an inner local onto a data stack, passes only
the displayed current state to a fresh Python process, and reverses to the
initial state using the same static example program. It also tests nonzero
scope initializers, a changed outer variable, nested scopes, failed deletion,
stack underflow, nonzero pop destinations and malformed checkpoints.

[SEMANTICS.md](SEMANTICS.md) proves the kernel's inverse-step and compositional
whole-statement correspondence for all well-shaped states where a step is
defined. The finite tests check its implementation, not the theorem's
unbounded domain. [RELATED_WORK.md](RELATED_WORK.md) explains existing overlap
and the comparisons still needed before a first-milestone acceptance.

[CONTROL.md](CONTROL.md) adds the two-label model and proves its call/scope
inverse and whole-procedure correspondence. Try its fresh-process nested-call
checkpoint, then all fifteen tests:

```sh
python3 projects/janus-local-steps/control_machine.py
python3 -m unittest discover -s projects/janus-local-steps -v
```

Next: add branch/loop contexts to the two-label model, compare the concrete
scope/call interaction with existing machines, and obtain independent
reconstruction. This is not a replacement for Jana. The Python APIs and
checkpoint schemas are experimental; a checkpoint belongs to the exact
static program and source version that created it.
