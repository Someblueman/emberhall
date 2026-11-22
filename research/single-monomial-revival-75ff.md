# Single-monomial chaos: keep the proposal retired

Mallow, 21 November 2026. Research task `mallow-single-monomial-revival-75ff`.
Idea: `single-nonlinear-cds-chaos`; original rejection: journal 20630.

The rejection still holds. I found no supported repair that justifies returning
this idea to the shelf. A precise proof-only promise would fix its wording, but
the research below does not establish a credible route to that proof. This is
not evidence that the mathematical question is impossible or unimportant.

## What the sources establish

- Plesa and Sprott, [published paper, publisher-supplied text](https://www.researchgate.net/publication/404920001_Simple_chemical_systems_with_chaos),
  DOI [10.1063/5.0323112](https://doi.org/10.1063/5.0323112): Problem 5.1 asks for
  exclusion of a chaotic invariant set, including the quadratic system (6) with
  sole nonlinear monomial `-xy`. Proposition 3.2 supplies necessary coefficient
  constraints, not the desired exclusion. The paper calls positive Lyapunov
  exponents numerical indicators; a finite estimate is not the promised proof.
- The [arXiv version](https://arxiv.org/html/2601.02787v1) calls the coefficient
  result Theorem 3.3. The [author-hosted PDF](https://sprott.physics.wisc.edu/pubs/paper547.pdf)
  also uses that numbering. Do not confuse it with the final Proposition 3.2.
  Both versions retain Problem 5.1. The old brief alternates between the full
  family and a subcase, and still permits a numerical trajectory as acceptance.
- Li and Muldowney, [A Geometric Approach to Global-Stability Problems](https://www.academia.edu/451041/A_Geometric_Approach_to_Global_Stability_Problems),
  [publisher record](https://doi.org/10.1137/S0036141094266449): sections 2–3
  provide a genuine possible proof method. Their global-stability theorem
  requires a suitable domain, compact absorbing set, unique equilibrium and
  negative long-time bound for a transformed second compound equation. A
  stable two-variable linear block alone does not check those conditions.
  The [author's linked copy](https://sites.ualberta.ca/~myli/research/ps_files/global.pdf)
  opened as a scan without extractable text; the paper text above was readable.

## A concrete obstruction to the simplest contraction shortcut

The following is my algebraic check, not a result claimed by either paper.
Within the allowed family take

```
x' = 1 + 4x - xy
y' = x - y
z' = x - z
```

All required nonnegative coefficients are nonnegative. The linear `(y,z)`
block has trace `-2` and determinant `1`, satisfying the stated strict bounds.
At the interior point `x=y=z=1/4`, the Jacobian and its second additive compound
(basis `e1∧e2, e1∧e3, e2∧e3`) are

```
J = [15/4  -1/4   0]       J^[2] = [11/4    0      0]
    [ 1     -1    0]                [  0   11/4  -1/4]
    [ 1      0   -1]                [ -1     1     -2]
```

The first row of `J^[2] - (11/4)I` is zero, so `11/4` is an eigenvalue.
Consequently no fixed norm, even after a constant similarity transformation,
can give a negative logarithmic norm for this compound matrix at every point
of the positive orthant. I checked these rational entries with Python's
standard-library `Fraction`; no numerical ODE integration was involved.

This excludes only that pointwise, whole-orthant certificate. It does not
exclude a state-dependent transformation, a smaller absorbing region or a
negative time-average bound. It certainly does not demonstrate chaos: here
`z` does not feed back and the first two equations form a planar subsystem.

## Decision and the next meaningful evidence

Keep the idea in the graveyard; record no replacement brief or return. The
existing source note `research/explorations/3e82748572fe4d9b96c3ed85cf9cfb39.md`
already explains rejection 20630. This note adds the contraction obstruction
and identifies the hypotheses a future proof route must actually discharge.

Reconsider only with a specified new theorem and a worked route that handles
its invariant-domain and boundary cases, or a rigorous invariant-set
certificate for a counterexample. Reproducing the already proved coefficient
conditions, plotting trajectories, or renaming a subcase as the whole problem
does not repair the proposal. No solution or exhaustive literature search is
claimed. Built-in read-only searches for the title, paper identifier and
single-monomial question did not identify a later resolution. No downloaded
code, dependency, parameter search or unselected project was built.
