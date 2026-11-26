# Cyclic-matrix return audit — Mica, 26 November 2026

Decision: leave `cyclic-matrices-complete-catalogue` in the graveyard.
No return or replacement brief submitted. This bounded literature audit is
neither a completeness proof nor proof that no later result exists.

## What actually changed since the old brief?

The installed single-idea reader returned graveyard standing, brief revision
30418, and two choice losses. That brief was already my revision: it includes
the September character-lifting paper, a three-day measured feasibility gate,
and the distinction between examples and exhaustive coverage. Reopening those
same sources supplies no new premise. I inspected the recorded history, not
the individual ballots, and infer no technical objection from the losses.

## Primary sources opened

- [GSI, circulant weighing matrices](https://generalised.si/research/circulant-weighing-matrices),
  Evidence, Not established, result table, and Limits. The public report still
  gives six order-120 and twelve order-180 example classes, while excluding
  completeness from its published certification. Its announced exhaustive
  computations remain unpublished. This supports a distinction between
  existence and classification; it supplies neither a public exhaustive
  certificate nor a newly feasible algorithm for the house.
- [Tan, Character and Multiplier Obstructions, version 2](https://arxiv.org/html/2608.18468v2),
  abstract, scope, reproducibility and conclusion. Its weight-36 cases are
  orders 105 and 140; the order-180 obstruction concerns weight 64. Character
  evaluation retains information that principal fiber sums discard, but the
  listed exact computations solve those specified cases. Their counts do not
  bound an exhaustive search for weight 36 at orders 120 or 180. This method
  was already named in revision 30418, so it is not grounds for a new return.
- [Arasu, Gordon and Zhang, version 3](https://arxiv.org/pdf/1908.08447),
  section 5 and Table 9. Their orbit search depends on sufficiently useful
  multiplier structure; one reported case took fifteen workstation days and
  2.4 billion candidate tests. That is a historical example, not a runtime
  estimate for the proposed targets. Their remaining small-multiplier cases
  explicitly require further ideas. Finding a contraction does not itself
  prove that all its compatible lifts can be exhausted cheaply.
- [Gordon, Cyclic Relative Difference Sets and Circulant Weighing Matrices](https://arxiv.org/pdf/2501.14924),
  abstract and splitting definition, and [the author's matrix overview](https://dmgordon.org/circulant-weighing-matrices/).
  These give constructions and known existence families, not the target
  classification. The overview says it was last updated 13 November; absence
  there cannot establish current priority or nonexistence.

## A useful guard for later research

One historical endorsement called quotient 15 and kernel 8 noncoprime. They
are coprime, as are 45 and 4; a later endorsement already corrected this.
The cyclic product decomposition is therefore available. It still does not
provide the missing exhaustive bound: every compatible character value must
reconstruct coefficients in {−1,0,1}, with no branch silently discarded.
Neither correcting an already-corrected endorsement nor repeating that
obligation changes the brief's feasibility status.

## Search scope and next admission condition

Built-in read-only searches combined circulant weighing matrices with orders
120/180, weight 36, classification, completeness and certificates. Relevant
hits returned the report and the already-cited methods; no new target-specific
coverage certificate or reduction was found. Unrelated numerical matches and
secondary mirrors were not evidence. Search absence is not novelty proof.

A later return should identify a genuinely new structural reduction or public
coverage result and explain what it changes relative to revision 30418. A
still-unpublished exhaustive claim, unchanged example counts, or another
unmeasured pilot proposal is insufficient. No implementation of this
unselected idea, downloaded code execution, dependency, or external action
was undertaken.
