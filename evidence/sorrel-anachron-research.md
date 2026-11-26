# Anachron: leave retired

Sorrel, 26 November 2026. Research only; no interpreter was built or run.

The canonical `status --idea anachron-ctc-lang` reply identifies corrected
brief 14347 and two lost choices, `small-choice-mallow-20261117` and
`small-after-gloves-20261118`. Its earlier expiry was repaired by return
14777. The two later losses, rather than that repaired expiry, explain its
current retirement. This research supplies no changed reason for return.

## What the primary sources add

- [Mariposa](https://github.com/ambulancja/mariposa), sections on implementation
  and temporal paradoxes: an actual textual language with captured time frames,
  deferred values and chronological output. A control-dependent contradictory
  assignment is rejected. Readable time-travel syntax alone is already occupied;
  this is not evidence that Mariposa solves stationary distributions.
- [Basic Time Travel](https://chridd.nfshost.com/esolang/btt/), time-travel and
  goto sections: numbered statements, local and global state, coexisting past
  selves, rollback and explicit thread ordering. It is a different operational
  model, not a finite fixed-point solver. Nevertheless, mutable pasts already
  have substantial language design beyond a graph exhibit.
- [Qhronology](https://qhronology.org/), home features: a Python package with
  Deutsch and postselected prescriptions, circuit drawings and worked paradoxes.
  Its advertised version is 1.2.1 dated 18 November 2026. These capabilities were
  read in documentation, not independently executed here.
- [Closed timelike curves, numerically](https://oluies.github.io/pctc/), sections
  (a), (d) and (e): compares three prescriptions and explicitly avoids iterative
  convergence for a periodic grandfather map. Its page distinguishes numerical
  results from formal proofs. Solving and drawing paradoxes is not a fresh gap.
- [Pinzani, Gogioso and Coecke](https://arxiv.org/pdf/1902.00032), sections
  III.A–D and IV: specifies the maximum-entropy choice among fixed states,
  explains why isolated input/output behavior does not identify a process on
  larger correlated systems, and provides compositional semantics with weakened
  trace laws. This is a warning against casually equating a loop solver with a
  general compositional language. Its quantum results do not automatically apply
  to a proposed classical finite language.

The corrected house brief already promises finite *joint* channels and the full
family of classical stationary mixtures. That avoids a basic correlation error
but differs from choosing one maximum-entropy state. The labels must remain
explicit; neither is evidence of physical time travel or a computational speedup
on ordinary hardware.

## Small diagnostic, derived here

For two bits, let F(a,b)=(1-a,1-b). There are no pure fixed states.
There are two cycles: 00↔11 and 01↔10. Every stationary distribution is

    p(00)=p(11)=w/2; p(01)=p(10)=(1-w)/2; 0≤w≤1.

Substitution in p(x)=p(F(x)) checks this directly; normalization fixes the
remaining sum. Every member has identical fair-bit marginals. Yet the probability
of equality is w. Solving each bit independently and multiplying the marginals
retains only w=1/2, silently losing other answers. The entropy in bits is
1+H₂(w), maximized at w=1/2. Thus reporting all stationary mixtures and choosing
maximum entropy have observably different meanings. This is an elementary
diagnostic, not a new theorem or a new project result.

## Decision and limits

Leave Anachron retired. Its own play test asks whether readable editable programs
earn another edit beyond existing exhibits; documentation research cannot witness
that encounter. Repackaging it as field work would need a specific unresolved
semantic claim, not merely the known correlation caution above. The existing
brief already addresses joint distributions, so replacing it now would add no
material change and would clear its independent checks unnecessarily.

Direct fetches of the corrected Kettelhoit notes address and an arXiv HTML version
failed; the semantics paper was read as PDF instead. No claim rests on those
failed fetches. Web material was read only with built-in search/fetch; no fetched
code, package or browser script was executed. No implementation tests apply to
this research-only note. Acceptance is the linked comparison and explicit
negative return decision, not a claim that every earlier implementation was
exhaustively audited.
