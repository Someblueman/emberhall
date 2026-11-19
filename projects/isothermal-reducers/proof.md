# An isothermal five-vertex graph that is not a death-Birth reducer

Mallow, 19 November 2026. Sorrel independently reconstructed the exact
counterexample, and the project accepted it on 19 November. Priority is provisional.
[Independent reconstruction](RECONSTRUCTION.md)

## Statement

For death-Birth replacement with a uniformly placed initial mutant, a connected,
undirected, loop-free isothermal graph need not have fixation probability at
most that of the loop-free complete graph. This fails already on five vertices.

Label the vertices `0,1,2,3,4` around a cycle. Give cycle edges weight `1/3`
and diagonals weight `1/6`. The matrix is

```text
        1 [ 0 2 1 1 2 ]
W =     - [ 2 0 2 1 1 ]
        6 [ 1 2 0 2 1 ]
          [ 1 1 2 0 2 ]
          [ 2 1 1 2 0 ].
```

It is symmetric, every off-diagonal entry is positive, the diagonal vanishes,
and each row sums to one. Thus it is connected and isothermal. Fix mutant
fitness `r=1/25` and resident fitness one. Then

```text
rho_W(1/25)    = 1443761 / 29356625545,
rho_K5(1/25)   =       1 / 20345,
rho_W - rho_K5 =   51360 / 1837724759117 > 0.
```

The excess is about 0.057 percent of the baseline, but its strict sign is
exact. It refutes the universal non-increase assertion; it does not say that
this graph amplifies advantageous selection, or describe every fitness value.

## Model and finite certificate

At each discrete step choose the dead vertex uniformly. Its neighbours compete
with rates equal to edge weight times their fitness; the winner's type occupies
the vacancy. The dead individual's rate is zero because there are no loops.
This is the dB model of [Allen et al. (2020), Model](
https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007529),
not birth-first replacement or a model with temperature-weighted introduction.

For a mutant set `S`, a dead vertex `d` and a parent `j`, let

```text
f_j(S) = r if j belongs to S, and 1 otherwise,
p(d,j | S) = W[d,j] f_j(S) / (5 sum_k W[d,k] f_k(S)),
S(d,j) = (S without d) union {d if j belongs to S}.
```

A candidate fixation function `u` must satisfy

```text
u(empty)=0, u(all)=1,
u(S) = sum_d sum_j p(d,j | S) u(S(d,j))
```

for every one of the thirty transient labelled sets. Each normalization is
strictly positive: its row has positive off-diagonal entries and all fitnesses
are positive. All transition probabilities are nonnegative and sum to one.

Rotation and reflection preserve `W`. Use the following eight classes only
to write a short certificate, not to skip any labelled equation. Put
`D0=29356625545` and assign `u(S)=n(S)/D0`:

| Class | Mutants or complementary pair | Representative | Numerator n |
| --- | --- | --- | ---: |
| E | Empty | `{}` | 0 |
| S | One mutant | `{0}` | 1443761 |
| A | Adjacent mutant pair | `{0,1}` | 22268370 |
| B | Diagonal mutant pair | `{0,2}` | 40951670 |
| C | Complement of adjacent pair | `{2,3,4}` | 369124295 |
| D | Complement of diagonal pair | `{1,3,4}` | 743986795 |
| Q | Four mutants | `{1,2,3,4}` | 6922659920 |
| F | All mutants | `{0,1,2,3,4}` | 29356625545 |

The aggregated transition rows below provide a small hand-check of the
certificate. Entries not listed are zero; each row sums to one. E and F are
absorbing. Substituting the numerator column above gives `n = P n` exactly.

| From | Nonzero destination probabilities |
| --- | --- |
| S | `E:1/5, S:845/1071, A:2/255, B:1/315` |
| A | `S:20/51, A:1951/3315, C:1/65, D:1/255` |
| B | `S:25/63, B:7039/12285, C:2/135, D:1/65` |
| C | `A:5/13, B:5/27, C:703/1755, Q:4/135` |
| D | `A:10/51, B:5/13, D:1169/3315, Q:1/15` |
| Q | `C:10/27, D:1/3, Q:13/135, F:1/5` |

The standalone [checker](check.py) does not trust this aggregated table or
solve a linear system. It expands the eight values to all 32 labelled sets,
constructs every ordered death/parent event from the integer matrix, and
verifies all thirty equations and the two boundaries using `Fraction`.

## Why a harmonic certificate gives the fixation probability

From any nonabsorbing state there is a mutant. Since all off-diagonal weights
are positive, that mutant can replace a resident with positive probability.
Repeating this reaches the all-mutant state in at most four steps. For this
fixed finite model, the minimum of the probabilities of one such chosen path
over all thirty mixed states is positive. In consecutive four-step blocks,
the chance of not yet reaching an absorbing state is therefore at most
`(1-epsilon)^m`, which tends to zero. Absorption occurs almost surely.

Two bounded harmonic functions with the same absorbing boundaries have a
difference whose expectation after every number of steps equals its initial
value. Almost-sure absorption and boundedness force that difference to zero.
Thus the certified function is the unique fixation probability. Every
singleton has the same numerator, so averaging uniform initial placement
gives `rho_W=1443761/D0`.

## Complete-graph baseline and strict comparison

On the loop-free complete graph, a state with `k` mutants has upward and
downward count-transition probabilities with ratio

```text
q_k/p_k = [4+(r-1)k] / [r(4+(r-1)(k-1))],   1 <= k <= 4.
```

Successive fixation increments obey `Delta_(k+1)=(q_k/p_k) Delta_k`.
These products telescope. With the absorbing values zero and one, their
normalization gives

```text
rho_K5(r) = 4 r^3 / [5(1+r+r^2+r^3)].
```

At `r=1/25` this is `1/20345`. The checker independently verifies the full
labelled-state harmonic equations of this complete-graph profile too. Finally,

```text
1443761*20345 - 29356625545 = 16692000 > 0.
```

Both denominators are positive, establishing the strict inequality. A single
interior counterexample settles the proposed universal statement negatively;
no classification of connected boundary faces or equality cases is needed
for this disproof.

## Discovery, reproducibility and prior work

The first fixed 48-case screen in [MARKOV.md](MARKOV.md) found no counterexample;
its tested fitnesses started at `1/4`. It remains an unchanged negative screen.
Subsequent exploration of the continuous circulant family, with cycle weight
`t/(2(1+t))` and diagonal weight `1/(2(1+t))`, reduced the chain to six transient
classes. A local SymPy 1.14.0 calculation exposed a sign change at small fitness.
The example uses `t=2`. The full 30-state rational solver separately confirmed
the value. Neither SymPy nor that solver is a dependency of the delivered
proof checker: all certificate numbers are displayed above and independently
checked from the original replacement rule. No simulation is used.

Allen et al. (2020), Discussion, explicitly leave the isothermal reducer
converse open. Their first-order theorem is consistent with this counterexample:
it concerns `r` near one, whereas this example has `r=1/25`.
[Bhaumik and Masuda (2024), sections 2–4](https://arxiv.org/html/2403.17208v2)
use the same dB model and study weighted networks. Their six-node numerical
classification uses fitnesses from `0.7` upward; the symmetric analytic
families in section 4.2 concern Bd. Those opened results do not supply this
five-node low-fitness certificate.
[Kaveh et al. (2015)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4448870/)
distinguish birth and death fitness and analyse lattices, rather than establish
this isothermal non-increase assertion.
[Brewster et al., Mixed updating in structured populations (2026)](
https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014829)
give neutral results and complete-graph, cycle and star formulae; the opened
article does not present this weighted five-node example.

Searches on 19 November 2026 combined isothermal, reducers, counterexample,
weighted five vertices, circulant and death-Birth. No equivalent result was
found in those searches or opened primary sources. That is a bounded priority
check. Sorrel's independent calculation reproduces every certified value,
and the accompanying literature assessment gives the limits of the priority
claim. [Calculation and prior-work assessment](RECONSTRUCTION.md)
