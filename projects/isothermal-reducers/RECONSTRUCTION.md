# Independent reconstruction of the five-vertex counterexample

Sorrel, 19 November 2026. Reviewed source `2c957a3`, particularly `proof.md`,
`check.py`, `markov.py` and `MARKOV.md`. I did not write those files.

**Accept the mathematical result.** A connected, symmetric, loop-free,
row-normalized five-vertex graph can have strictly greater death-Birth fixation
probability than the complete graph. This is the promised exact counterexample,
not a simulation or a web demonstration. It answers the project's enabling
question: another reader can now refute universal non-increase with a small
rational certificate. Priority remains provisional; source integration and the
project owner's milestone decision remain separate.

## Model and independent arithmetic

The matrix in the proof is symmetric, has zero diagonal, and has two entries
`1/3` and two entries `1/6` in every row. It is therefore isothermal and connected.
If the dead vertex has total mutant-neighbour weight `a` and resident-neighbour
weight `b`, then at fitness `1/25` its replacement is mutant with probability
`a/(a+25b)`. Each death has probability `1/5`. The zero diagonal ensures that
the dead individual never competes, even though the weights use the old state.

For a singleton, the probability of extinction in one step is `1/5`.
The total chances of growing into an adjacent or a diagonal pair are,
respectively, `2/(5*51)=2/255` and `2/(5*126)=1/315`. From an adjacent pair,
loss to a singleton has probability `20/51`; growth into the two triple classes
has probabilities `1/65` and `1/255`. These independently reconstructed entries
match the displayed table. The computation below does not use that table or
its symmetry classes: it solves all thirty labelled states using sets.

For the complete graph, at mutant count `k`,

```text
p_k = (5-k)/5 * kr/(kr+4-k)
q_k = k/5 * (5-k)/((k-1)r+5-k).
```

Thus `q_k/p_k = (4+(r-1)k)/(r(4+(r-1)(k-1)))`. The products of these ratios
and the two absorbing boundaries give the proof's complete-graph formula.
Separately solving the full complete-graph system below gives `1/20345`.
The graph's singleton probability is `1443761/29356625545`; subtracting the
baseline gives `51360/1837724759117 > 0`. Cross-multiplication also gives the
positive integer `16692000`. Every independently solved state agrees with the
certificate, including the two different pair and triple classes.

All transition normalizations are positive. From any mixed state, a mutant
can replace a resident along a positive edge, repeated until fixation in at
most four steps. There are finitely many states, so the minimum chosen-path
probability is positive. Repeating four-step blocks proves almost-sure absorption.
Bounded harmonic functions with the prescribed boundary values are then unique.
This justifies identifying the solved values with fixation probabilities.
A single strictly positive interior counterexample disproves the universal
assertion; no claim about every boundary face or equality case is needed.

## Reproduce the independent solve

From the repository root, run this with Python 3.10 or later. It uses no project
solver. Only after computing both answers does it import the supplied certificate
to compare all thirty values.

```python
from fractions import Fraction as Q
from itertools import combinations

V = frozenset(range(5))
states = [frozenset(c) for k in range(1, 5) for c in combinations(V, k)]
index = {s: i for i, s in enumerate(states)}


def reconstruct(weight):
    rows = []
    for s in states:
        row = [Q(s == t) for t in states] + [Q(0)]
        for d in V:
            mutant = sum(weight[d][j] for j in s)
            resident = sum(weight[d][j] for j in V - s)
            p = mutant / (mutant + 25 * resident)
            for t, chance in ((s | {d}, p / 5), (s - {d}, (1 - p) / 5)):
                if t == V:
                    row[-1] += chance
                elif t:
                    row[index[t]] -= chance
        rows.append(row)
    for c in range(30):
        p = next(i for i in range(c, 30) if rows[i][c])
        rows[c], rows[p] = rows[p], rows[c]
        pivot = rows[c][c]
        rows[c] = [x / pivot for x in rows[c]]
        for i in range(30):
            if i != c:
                factor = rows[i][c]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[c])]
    return {s: rows[i][-1] for s, i in index.items()}


weights = [[Q(0) if i == j else Q(2 if (i-j) % 5 in (1, 4) else 1)
            for j in V] for i in V]
answer = reconstruct(weights)
control = reconstruct([[Q(i != j) for j in V] for i in V])
rho = sum(answer[frozenset({i})] for i in V) / 5
baseline = sum(control[frozenset({i})] for i in V) / 5
print('fixation', rho)
print('complete', baseline)
print('gap', rho - baseline)
assert rho - baseline == Q(51360, 1837724759117) > 0

import importlib.util
from pathlib import Path
path = Path('projects/isothermal-reducers/check.py')
spec = importlib.util.spec_from_file_location('certificate', path)
certificate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(certificate)
for s, value in answer.items():
    mask = sum(1 << i for i in s)
    assert value == Q(certificate.NUMERATORS[certificate.orbit(mask)],
                      certificate.DENOMINATOR)
print('all 30 independently solved values match the certificate')
```

Observed outputs are the three fractions above and the final all-thirty match.
The advertised `python3 projects/isothermal-reducers/check.py` exits zero and
prints the same fractions. `--mutate-certificate` exits one at state 1 with
residual `226/31440945958695`; `--mutate-model` exits one with residual
`-351271491/870277164281525`. The nine existing `test_*.py` tests pass. The
earlier 48-case negative screen is unchanged and is not offered as this proof.

## Opened literature and limits

- [Allen et al. (2020), Model, weak-selection theorem and Discussion](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007529):
  the same weighted, loop-free dB rule and uniform initial placement; the
  isothermal-reducer converse is explicitly open. A first-order result near
  fitness one does not exclude this low-fitness example.
- [Bhaumik and Masuda (2024), sections 2 and 4](https://arxiv.org/html/2403.17208v2):
  the weighted dB convention agrees. Their six-node classification samples
  fitness from `0.7` upward, and their larger symmetric analytic examples use
  birth-first updating. Neither supplies this certificate.
- [Kaveh et al. (2015), sections 3–6](https://pmc.ncbi.nlm.nih.gov/articles/PMC4448870/):
  separate birth/death rates and self-loop conventions require care. Its
  complete-graph and lattice calculations are not this five-vertex weighted
  dB example; its loop-inclusive baseline must not replace ours.
- [Brewster et al. (2026), Setup and Discussion](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014829):
  mixed updating on unweighted graphs, with cycle/star formulas and neutral or
  non-deleterious main results, does not settle this weighted low-fitness case.

On 19 November I also searched combinations of isothermal, reducers,
counterexample, death-Birth, five vertices, circulant, and the exact certificate
numerator/denominator. No equivalent result was found in the opened primary
papers. A search surfaced a claimed Lean formalization of the birth-first
isothermal theorem; its linked Zenodo record was inaccessible, so it was not
verified or used as evidence. This is a bounded non-duplication assessment,
not proof of novelty. No author was contacted and no external action was taken.
