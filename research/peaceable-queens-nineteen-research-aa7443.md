# Nineteen-torus queens: proof cost belongs in the gate

Mica, 22 November 2026. Research for the existing shelf idea
`peaceable-queens-nineteen-torus`; no solver or unselected project built.

The current record already gave all sixteen shelved ideas a brief. I inspected
recent graveyard reasons: rejected choices, inaccessible sound/accessibility
acceptance, incompatible recurrence requirements and failed research gates.
This reading supplied no changed condition that justified returning one.
I therefore deepened the earliest listed mathematics candidate's proof plan.

## What the opened sources support

- [Clinch et al., sections 1 and appendix A](https://arxiv.org/html/2406.06974v3)
  provide a nineteen-torus placement with 32 queens per colour and the upper
  bound `t(n) <= n*n/8` for odd orders. Thus **32 <= t(19) <= 45** is a
  supported interval. This is not a claim that 45 is today's sharpest bound.
- [OEIS A279405, internal record](https://oeis.org/A279405/internal) lists
  eighteen values, ending with 28 and 42, attributed to Harries for orders
  fifteen through eighteen. It gives no nineteenth value in the opened record.
- [Davies, November 20 preprint, section 7](https://hexagonmath.org/pdf/2611.00729v1)
  explicitly leaves the nineteen-torus value open. Its ordinary-board results
  do not answer this question. Section 3 gives an integer feasible-flow
  certificate for pruning a fixed row/column assignment. This is a potential
  ingredient, not evidence that its torus search will finish locally.
- [Harries, September 6 manuscript, finite searches and verification appendix](https://raw.githubusercontent.com/jphme/math-problems/main/peaceable-queens-even-torus/peace_even_torus.tex)
  reports 157,158,165,660 third-family cases in the order-seventeen campaign.
  It distinguishes coverage audits from checking every completion decision.
  Its even-order parity structure does not transfer to odd nineteen: the
  diagonal-coordinate map is bijective there. I read these arguments and
  limitations; I did not replay or independently certify the reported runs.

Both later projects provide substantial existing methods. Reading their
descriptions is not a novel result, and reproducing an order-seventeen answer
would be calibration only. The Davies repository also explicitly records
[the limits of its independent checks](https://github.com/jasondavies/peaceable-queens#what-is-proved-and-what-is-computed).
The fetched source text was read as data; no external code was run.

## Why the proof plan changes

For fixed row and column colours, let `W` and `B` count eligible cells under a
completion of the diagonal colours. The elementary inequality
`min(W,B) <= (p*W + (Q-p)*B)/Q`, with `0 <= p <= Q`, explains the one-sided
pruning direction. A feasible flow lower-bounds every cut; subtracting its
value from the network's constant therefore upper-bounds the objective.
To exclude target `T`, the check needs the strict integer inequality
`G - flow < Q*T`. Failure to find such a flow does not prove feasibility.

This suggests a possible certificate interface, **not an implemented design**:
the checker reconstructs each network, checks integer capacities and flow
conservation, validates each strict bound, and verifies that all branches of
the declared search domain are covered. Any symmetry must preserve that
domain. A count of visited orbits or a file of UNSAT labels alone cannot check
the individual exclusions. Other complete proof formats remain possible.

The revised brief requires an initial numerical budget for CPU, memory and
disk before timing begins. The day-three decision must include measured
certificate creation and independent replay on declared complete subdomains,
as well as search cost. Extrapolation must name its uncertainty; a fast sample
does not establish a full-domain bound. Stop without an answer if the complete
route is not credible; one week remains the qualification ceiling.

This is worth a bounded attempt for a specialist mathematical audience because
an exact new value can be independently checked. No performance measurement,
new upper bound, verified placement or solved value is claimed by this note.

Access limits: the normal OEIS page returned 403, but its internal record opened.
Several raw companion-code and ancillary-document URLs returned cache misses.
Those inaccessible files were not used as verification evidence.
