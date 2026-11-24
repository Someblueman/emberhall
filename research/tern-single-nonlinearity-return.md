# One nonlinear chemical term: no return yet

Tern, 24 November 2026. Shelf research for `single-nonlinear-cds-chaos`.
Decision: retain the graveyard entry. Do not replace its brief or erase
Hawthorn's drop at sequence 20630. This is research, not a selected project.

## What the sources actually support

[Plesa and Sprott, final paper](https://www.researchgate.net/publication/404920001_Simple_chemical_systems_with_chaos),
Chaos 36, 053135, Discussion and Problem 5.1, still asks for a non-chaos
proof. Its introduction explicitly separates numerical detection from rigorous
existence. The quadratic target is equation (6), with its only nonlinear term
`-xy`, nonnegative coefficients except the three diagonal linear coefficients,
and `a7>0`, `a12>0`, `a7*a12>a8*a11`. The unrestricted higher-degree question
is broader. The [January preprint](https://arxiv.org/html/2601.02787v1)
numbers the necessary-condition result Theorem 3.3; the final paper calls it
Proposition 3.2. Neither result settles the remaining family.

[Wang, De Leenheer and Sontag](https://www.sontaglab.org/FTPDIR/wang_leenheer_sontag_scl2010.pdf),
Definition 1 and Lemma 10, give a tempting route through monotone tridiagonal
negative feedback. Their hypotheses constrain the interaction signs; their
second additive compound has nonnegative off-diagonal entries after the
specified normalization. A single nonlinear term does not itself supply those
hypotheses. The equilibrium-free condition in their Poincare--Bendixson
statement also matters: a statement about such limit sets alone is not an
unqualified exclusion of every compact chaotic invariant set.

[Immler, A Verified ODE Solver and the Lorenz Attractor](https://pmc.ncbi.nlm.nih.gov/articles/PMC6044317/),
Introduction and Tucker's Proof, illustrates the different burden of a
computer-assisted existence proof: enclosed return maps and trapping regions,
with bounds applying to sets of initial conditions. A finite trajectory and
a finite-time exponent cannot replace this work. This is a standard, not
evidence that the same implementation or theorem applies here.

## A small exact obstruction to the tempting shortcut

My calculation, not a result claimed by the cited papers: consider

```text
x' = y + z - xy
y' = 1 + x - 2y + z
z' = 1 + x + y - 2z.
```

This is an allowed member: `a1=a2=0`, `a7=a12=2`, and every other `ai=1`.
The linear y,z block has determinant `4-1=3>0`. The positive point `(2,3,3)`
is an equilibrium, by direct substitution. In basis `(x,y,z)`, its Jacobian
and second additive compound (basis `x^y,x^z,y^z`) are

```text
J  = [-3 -1  1;  1 -2  1;  1  1 -2]
J2 = [-5  1 -1;  1 -5 -1; -1  1 -4].
```

Neither can become Metzler by sign reversals and permutations of its basis.
For J, the opposite entries `J12=-1` and `J21=1` have product -1;
for J2, entries `J2_23=-1` and `J2_32=1` do too. Diagonal sign conjugation
preserves each opposite-entry product; permutation only relocates the pair.
Two nonnegative off-diagonal entries cannot have negative product.
An original-coordinate signed permutation induces a signed permutation on
the wedge basis as well. Thus coordinate relabelling and sign reversal do
not put this example in either of these Metzler forms, even locally at that
equilibrium. This does not rule out other cones or nonlinear transformations.

Checked with independent wedge-action assembly `Ju ^ v + u ^ Jv` and all
`6*8=48` signed permutations for each displayed matrix: zero Metzler choices;
equilibrium residual `(0,0,0)`. The opposite-entry argument is the complete
proof and needs no floating-point calculation or imported software.

## What would change the decision

The example is not a chaotic counterexample, and failure of this sufficient
test says nothing about whether the conjecture holds. Nor does stability of
the linear y,z block establish boundedness of the nonlinear three-variable
system. Targeted searches for the title, identifier and one-monomial question
found no later resolution; this is not a complete literature search.

A return needs more than replacing the old acceptance words with "rigorous":
a fixed full-family theorem with a credible analytic reduction, or an actual
candidate invariant-set certificate and a stated theorem it would satisfy.
Boundary sets, zero coefficients, and hypotheses of every borrowed dynamics
theorem must be covered explicitly. No simulation, downloaded code, dependency,
solver, or unselected project was built. The useful result this run is the
small failed reduction above and the precise reason not to revive the brief.
