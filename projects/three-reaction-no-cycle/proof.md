# No periodic orbit in the three-reaction example

Sorrel, Emberhall, 18 November 2026. The polynomial multiplier and proposed
extension were suggested in Aster's [research note](../../research/explorations/02e18e1b9de843708e5f1e405cf52192.md).
This document supplies the derivation and domain argument. It is an author
proof awaiting independent mathematical review, not a peer-reviewed publication.

## Statement and source

**Theorem.** For every real `a,b,c > 0`, the system

\[
 \dot x=ax^2-bxy+cy,\qquad \dot y=2ax^2-bxy                         \tag{1}
\]

has no nonconstant periodic solution in the nonnegative quadrant. In
particular it has no positive limit cycle.

The source is Banaji, Boros and Hofbauer, *Oscillations in three-reaction
quadratic mass-action systems*, Studies in Applied Mathematics **152** (2024),
249–278, DOI [10.1111/sapm.12639](https://doi.org/10.1111/sapm.12639).
Their [section 6](https://pmc.ncbi.nlm.nih.gov/articles/PMC10953466/)
asks about this example after the classification of local bifurcations.
The equation image in the journal HTML did not load during this audit;
the equations and reactions were independently transcribed from the text
extraction of the [authors' preprint, printed page 22](https://arxiv.org/pdf/2304.02303).
The attempted PDF screenshot also failed. This is a text-verified transcription,
not a claim to have inspected an equation image.

With `a=κ₁`, `b=κ₂`, `c=κ₃`, the three reactions are

| Reaction | Rate | Change in `(x,y)` |
| --- | --- | --- |
| `2X -> 3X + 2Y` | `a x²` | `(1,2)` |
| `X + Y -> 0` | `b xy` | `(-1,-1)` |
| `Y -> X + Y` | `c y` | `(1,0)` |

Summing the rate times each change gives (1), including its factor of two
and the absence of a linear `y` term in the second equation. The result
concerns this mathematical model, not an experimentally realised reaction.
The first product has molecularity five: a theorem restricted to products
of molecularity at most three does not settle it.

## 1. Exact normalization

Set

\[
 x=\frac cb u,\quad y=\frac cb v,\quad s=ct,\quad \alpha=\frac ab>0.
\]

Since `dx/dt=(c²/b) du/ds` and similarly for `y`, division of the original
right sides by `c²/b` gives, with prime denoting `d/ds`,

\[
 u'=f=\alpha u^2-(u-1)v,\qquad
 v'=g=2\alpha u^2-uv.                                             \tag{2}
\]

This is an invertible positive spatial scaling and positive constant time
change. A period `T` becomes `cT`, so periodicity and nonnegativity are
preserved in both directions. The checker verifies the substitution with
formal rational monomials, not with sampled rate constants.

## 2. Any positive periodic orbit lies strictly to the right of `u=1`

Suppose a nonconstant positive periodic solution exists. The continuous
periodic function `u(s)` has a minimum at some `s₀`. At this time `f=0`, hence

\[
 (u(s_0)-1)v(s_0)=\alpha u(s_0)^2>0.
\]

Since `v(s₀)>0`, its minimum satisfies `u(s₀)>1`. Thus the entire orbit
satisfies `u>1`; it cannot cross or touch `u=1`. This does not assume that
every positive trajectory reaches that region or that all trajectories
are bounded. Independently, on `u=1` the vector field has `u'=α>0`.
Consequently the half-plane `u>1` is forward invariant for as long as a
solution exists: a first finite exit would have `u'<=0` at the boundary,
contradicting `u'=α`.

## 3. The polynomial identity and its sign

Define

\[
 H=(u-1)(v+2)-\alpha u^2=2(u-1)-f,
 \qquad P=u[\alpha(u-2)^2+2(u-1)].                                 \tag{3}
\]

The derivatives are

\[
 \operatorname{div}F=2\alpha u-v-u,\qquad
 H_u=v+2-2\alpha u,\qquad H_v=u-1.
\]

Direct multiplication and collection gives

\[
 H\operatorname{div}F-H_uf-H_vg
 =-\alpha u^3+(4\alpha-2)u^2+(2-4\alpha)u=-P.                       \tag{4}
\]

All `v` terms cancel. On `u>1`, `αu(u-2)²>=0` and `2u(u-1)>0`;
therefore **`P>0`**, including at `u=2`.

Along a solution, (4) also says

\[
 \frac{dH}{ds}=H\operatorname{div}F+P.                              \tag{5}
\]

In particular on `H=0` within `u>1`, its derivative is `P>0`. This boundary
is not an invariant curve: it is crossed only towards increasing `H`.

## 4. The singular boundary cannot meet the hypothetical orbit

At the minimum used in section 2, `f=0`, so
`H(s₀)=2(u(s₀)-1)>0`. On any finite interval of the hypothetical periodic
solution starting at `s₀`, let

\[
 A(s)=\int_{s_0}^{s}\operatorname{div}F(u(r),v(r))\,dr.
\]

Equation (5), by the integrating factor formula, gives

\[
 H(s)=e^{A(s)}\left[H(s_0)+\int_{s_0}^{s}e^{-A(r)}P(u(r))\,dr\right]>0
 \quad(s\ge s_0).                                                  \tag{6}
\]

Here the orbit is compact and stays in `u>1`, so the integrands are continuous
and the strict sign is justified. Applying (6) for a full period proves
that every point on the orbit has `H>0`, including points whose original
time precedes `s₀` by periodicity. Neither a tangency to `H=0` nor an
unnoticed return crossing is possible.

The same formula proves forward invariance of

\[
 D=\{(u,v):u>1,\ H(u,v)>0\}                                       \tag{7}
\]

on the maximal existence interval for any initial point in `D`, since
section 2's boundary argument keeps `u>1` and `P` is independent of `v`.
This is a finite-time invariance statement, not a global existence claim.
For the contradiction, it suffices that the hypothetical periodic orbit
is entirely in `D`.

## 5. Topology and the Dulac contradiction

The domain `D` is open and simply connected. In fact

\[
 (u,v)\longmapsto(u,H(u,v)),\qquad
 (u,h)\longmapsto\left(u,\frac{h+\alpha u^2}{u-1}-2\right)
\]

are smooth inverse maps between `D` and `(1,∞) × (0,∞)`. Their Jacobian
determinant in the forward direction is `u-1>0`. We deliberately permit
negative `v` in `D`; the polynomial field extends there, and the positive
orbit is a subset of it. No deletion of an equilibrium or puncture is needed.

The function `B=1/H` is continuously differentiable on all of `D`. Equation
(4) yields

\[
 \operatorname{div}(BF)
 =\frac{H\operatorname{div}F-\nabla H\cdot F}{H^2}
 =-\frac{P}{H^2}<0 \qquad\text{everywhere in }D.                    \tag{8}
\]

The Bendixson–Dulac criterion therefore excludes a nonconstant periodic
orbit in `D`, contradicting section 4. For a direct form of the criterion,
uniqueness for this smooth vector field makes a nonconstant periodic orbit
a simple closed curve. Its enclosed region lies in `D` because `D` is
simply connected. Green's theorem would give a strictly negative integral
of (8) over that region, yet its boundary flux is zero because `BF` is
tangent to the orbit. This is impossible. The standard criterion, with the
same regularity and topology assumptions, is stated in
[Osuna–Villasenor, Theorem 1](https://www.math.u-szeged.hu/ejqtde/p720.pdf).

## 6. Axes, equilibria, and scope

A periodic solution confined to the nonnegative quadrant cannot meet
`x=0,y>0`: at a minimum of its differentiable nonnegative `x` coordinate,
its derivative must be zero, whereas (1) gives `x'=cy>0`. Similarly it
cannot meet `y=0,x>0`, since `y'=2ax²>0`. If it meets the origin, uniqueness
forces it to be the constant origin solution. Thus any nonconstant
nonnegative periodic solution would have been positive, already excluded.

The only equilibria in the nonnegative quadrant are the origin and

\[
 (x_*,y_*)=(2c/b,\ 4ac/b^2),\qquad (u_*,v_*)=(2,4\alpha).
\]

Indeed `g=0` with `u>0` forces `v=2αu`, and `f=0` then forces `u=2`.
At the positive equilibrium `H=2`, so the Dulac multiplier is regular there.
Its Jacobian is `[[0,-1],[4α,-2]]`, with trace `-2` and determinant `4α`.
Neither local stability nor absence of a Hopf bifurcation is used to infer
the absence of periodic orbits. Equilibria are constant periodic solutions
in some terminology; the theorem explicitly excludes only **nonconstant**
ones. We assert no global convergence, permanence, or bound on all solutions.

## 7. Extension after the `m=2` proof

Replace the second equation by `y'=m a x²-bxy` for any real `m>=2`, leaving
the first equation unchanged. The normalized second component is then
`g_m=mαu²-uv`. The preceding `u` minimum argument and `H` are unchanged.
The only change in (4) is `-(m-2)αu²(u-1)`, hence

\[
 H\operatorname{div}F_m-\nabla H\cdot F_m=-P_m,\quad
 P_m=P+(m-2)\alpha u^2(u-1)>0\quad(u>1).                            \tag{9}
\]

Sections 4 and 5 apply verbatim with `P_m`. On the `y=0,x>0` axis,
`y'=ma x²>0`; the other boundary argument is unchanged. Therefore the same
no-nonconstant-periodic-solution conclusion holds for every real `m>=2`.
For integer `m`, its reaction interpretation replaces the first product
by `3X+mY`. This is an ODE extension for real `m`, not a fractional-molecule
interpretation. No claim for `m<2` follows from this sign certificate.

## 8. Bounded prior-literature audit

Audited on 18 November 2026 using built-in read-only web search/fetch. Queries
included the exact paper title with 2025/2026, `three-reaction Dulac`,
`three-reaction open problem`, `3X + 2Y limit cycle`, the equation terms,
and later papers by Banaji, Boros and Hofbauer. Equation-only searches mostly
returned irrelevant conic equations. No discovered paper supplied this
specific exclusion or a counterexample. That is a bounded negative search,
**not proof of novelty**; unpublished work, unindexed papers, equivalent
coordinate forms and general theorems missed by the search remain possible.

| Source opened | What was checked; relation to this claim |
| --- | --- |
| [Original 2024 paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10953466/), section 6; [2023 preprint](https://arxiv.org/pdf/2304.02303), p.22 | Explicit open example, reconstructed above. This does not settle all the paper's cases 9 and 10. |
| [Banaji–Boros–Hofbauer, 2024 follow-up](https://pmc.ncbi.nlm.nih.gov/articles/PMC11466909/), abstract, introduction, remarks and conclusion | Local bifurcations with up to four reactions and product molecularity at most three. Its no-cycle statement for three reactions is explicitly restricted to that molecularity. |
| [Banaji–Boros–Hofbauer, 2025 inheritance](https://pmc.ncbi.nlm.nih.gov/articles/PMC12085349/), abstract and introduction | Preservation of local bifurcations under enlargement. No resolution of the present global question was found in these sections. |
| [Craciun–Erban, 2025](https://link.springer.com/article/10.1007/s00285-025-02221-0), abstract and discussion | Constructions and bounds for chemical limit cycles by polynomial degree, molecularity and reversibility; cites the original small-network paper. No exclusion of this example found. |
| [Blokhuis–Stadler–Vassena, preprint v2](https://arxiv.org/html/2508.15273v2), introduction and supplement S1 | Oscillatory cores and parameter-rich kinetics. S1 explicitly distinguishes standard mass action; its positive existence recipes do not establish a cycle here. |
| [Beldiman–Halanay, October 2026](https://arxiv.org/html/2610.27188v1), abstract, introduction and discussion | Canard-point classification with a fast/slow splitting; no specific resolution of this example found. |
| [Beldiman–Halanay, November 2026](https://arxiv.org/html/2611.15129v1), abstract and introduction | Extension of canard analysis to one slow direction; no specific resolution of this example found. |
| [Banaji's publications](https://muradbanaji.github.io/publications/) and [Boros's publications](https://sites.google.com/view/balazsboros/publications) | Later-title audit; the 2026 entries concern other problems. Author lists are not exhaustive citation indexes. |
| [Osuna–Villasenor, 2011](https://www.math.u-szeged.hu/ejqtde/p720.pdf), Theorem 1 | Established Dulac criterion used here; no claim to invent that method. |

Priority must remain provisional at independent review. The deliverable is
the explicit argument and reproducible identities, not a claim that a
literature search certifies a first discovery.
