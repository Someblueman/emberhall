# Exact fixed-graph calculation

Mallow, 19 November 2026. Foundation for the selected five-vertex project,
not its final theorem or milestone acceptance.

From the repository root, using Python 3.10 or later and its standard library:

```sh
python3 -m unittest discover -s projects/isothermal-reducers -p 'test_*.py' -v
python3 projects/isothermal-reducers/markov.py --screen
```

The first command currently runs nine tests. The second checks twelve fixed
five-vertex matrices at fitness `1/4, 9/10, 11/10, 4`, with exact rational
arithmetic. It prints `PASS 48 fixed cases; no counterexample in this finite
screen`, followed by the still-open universal conditions. Every sample is
also checked against all thirty transient state equations. This is a bounded
negative screen, not an argument from the vertices of a polytope. Exact
cross-check values from that run include:

| Graph | Fitness | Fixation | Complete-graph gap |
| --- | ---: | ---: | ---: |
| Complete graph | `1/4` | `4/425` | `0` |
| Five-cycle | `1/4` | `2/235` | `18/19975` |
| Complete graph | `4` | `256/425` | `0` |
| Five-cycle | `4` | `128/235` | `1152/19975` |

The screen separately differentiates the neutral harmonic system twice. Each
of the twelve matrices has uniform first derivative exactly `3/10`, as required
by the known weak-selection isothermal theorem, and second derivative no larger
than the complete graph's `-1/10`. These are local checks, not all-fitness bounds.

## Model and certificate

The convention follows [Allen and colleagues, 2020, Model and equation (1)](
https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007529):
an undirected, connected graph without loops; a uniformly chosen death;
a replacement parent chosen proportionally to fitness times edge weight;
and one initial mutant chosen uniformly. Here the common positive weighted
degree is scaled to one. All entries, intermediate values and residuals are
exact fractions. Floats, negative weights, nonzero diagonal entries, unequal
row sums, asymmetry, disconnected graphs and nonpositive fitness are rejected.

For mutant set `S`, let `a_d = sum(W[d,j] for j in S)`. Conditional on death
at `d`, the replacement is mutant with probability

```text
m_d = r a_d / (1 + (r - 1) a_d).
```

The solver aggregates those two possible types for each death. It solves
`(I-Q) u = b` on all nonempty, nonfull subsets by rational elimination.
The certificate contains the original matrix, fitness, model, version and
every subset probability, including `u(empty)=0` and `u(full)=1`. Bit `j`
means vertex `j` is mutant. Uniform fixation is the average of the singleton
entries; it is not the probability at an arbitrarily chosen vertex.

The verifier does not call the solver or its transition builder. It enumerates
each ordered death/parent pair and checks the entire harmonic equation by
exact equality. It rejects changed boundaries, an altered transient value,
fitness/model mismatches and out-of-range probabilities. Passing these checks
certifies **one specified matrix and one fitness**, not a neighbourhood of it.

Why this is sufficient for that fixed input: connectivity supplies a spanning
tree. From every mixed state, repeatedly copying one existing type across a
tree boundary reaches an absorbing state in at most `N-1` changes. Every such
edge event has positive probability because the edge weight and both fitnesses
are positive. There are finitely many states, so their chosen finite paths
have a positive minimum probability. Failure to absorb through successive
blocks therefore tends to zero geometrically. The absorbing boundary problem
has a unique solution: the difference of two bounded solutions has zero
boundaries and its expected value after any number of steps equals its starting
value; absorption forces that difference to zero. This argument does not
require a quantitative lower bound uniform over all graph weights or fitnesses.

## Saving and checking a certificate

For example, save this two-vertex graph as `/tmp/fixation-input.json`:

```json
{"weights": [["0", "1"], ["1", "0"]], "fitness": "2"}
```

Then run:

```sh
python3 projects/isothermal-reducers/markov.py --solve /tmp/fixation-input.json > /tmp/fixation-cert.json
python3 projects/isothermal-reducers/markov.py --verify /tmp/fixation-cert.json
```

The result is exactly `1/2`: with two vertices, the first death determines
which type survives, independently of fitness. This is also a direct check
that the model excludes the dead individual from parental competition.
Changing a nonabsorbing certificate value makes verification fail with a
named state and an exact nonzero residual. JSON rationals are strings such as
`"2/3"`; JSON numbers and booleans are not accepted as certificate fractions.

## Independent calibrations and frozen screen

The complete-graph control is
`((N-1)/N) / sum(r**(-j), j=0..N-2)`, using the loop-free death-first baseline.
For the cycle, contiguous mutant blocks form a one-dimensional birth/death
chain. Its downward/upward ratios are `(r+1)/(2r)` at block size one,
`1/r` internally and `2/(r+1)` at size `N-1`. The usual product-of-ratios
solution gives the separate `cycle_probability` formula. Tests compare both
controls at three, four and five vertices and four rational fitnesses.
Twenty exact cases independently reconstruct the four-vertex research seed
in [Hawthorn's note](../../research/explorations/17b878633e654889be2d24469a427bdf.md).
At neutrality, every subset of an asymmetric five-vertex matrix has
probability exactly its cardinality divided by five.

For the optional derivative calculation, `m_d'(1)=a_d(1-a_d)` and
`m_d''(1)=-2 a_d^2(1-a_d)`. Differentiating the finite harmonic system gives
`(I-Q)u' = Q'u` and `(I-Q)u'' = Q''u + 2Q'u'`, with zero derivatives at both
absorbing boundaries. Tests compare the complete-graph derivatives with
`(N-2)/(2N)` and `(N-2)(N-6)/(6N)`. They also differentiate the four-vertex
seed independently: its second derivative is `-(1+a^2+b^2+c^2)/8`.

The screen uses the complete graph, one five-cycle, four mixtures of that
cycle and one triangle-plus-edge matrix, and six four-vertex-of-polytope
mixtures originally selected with seed `20261119` and now frozen as explicit
index and integer-coefficient lists in the source. They do not depend on the
Python version's sampling algorithm. Those last words refer to polytope
vertices, not four population sites: every screen matrix is five by five.
All coefficients and the four fitnesses are fixed before the screen runs.
`five_vertex_extremes` enumerates twelve labelled half-weight five-cycles and
ten triangle-plus-edge matrices, as suggested by the research note. The ten
disconnected matrices are rejected as solver inputs, but can participate in
connected convex mixtures. This program does not independently prove that
these are all vertices of the weight polytope.

## An obstruction to a simple proof route

The complete graph's fixation probability as a function only of mutant count
is **not** a supermartingale on every isothermal graph. Thus checking that
particular function state by state cannot prove the desired upper bound.
For the five-cycle at fitness `1/4`, begin at a single mutant. The next change
is a loss with probability `1/5` or a gain with probability `2/25` per update.
The complete graph's fixation values at counts zero, one and two are
`0, 4/425, 17/425`. Its one-step expected increase is therefore

```text
(2/25)(17/425 - 4/425) - (1/5)(4/425) = 6/10625 > 0.
```

The true five-cycle fixation is nevertheless `2/235 < 4/425`. This exact
calculation rejects only the naive count-only supermartingale argument;
it is not a counterexample to the project's conjecture. A proof could still
use a graph-dependent test function or a comparison of averaged excursions.

## Remaining work

No all-weight inequality, all-fitness certificate, equality classification or
priority finding is established. A positive outcome still needs the complete
five-vertex theorem and connected boundary faces; one rational matrix with a
strictly larger exact fixation probability would instead refute it. A larger
sample without such a counterexample is not the promised outcome. The final
`proof.md`, `README.md` and one-command `check.py` remain for the theorem work;
this foundation deliberately does not present itself as that final result.
