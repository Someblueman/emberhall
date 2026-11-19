# An isothermal graph that is not a death-first reducer

An exact five-vertex counterexample to universal non-increase of fixation
probability under death-Birth replacement. Independent project review is
pending and priority remains provisional.

After cloning this repository, run from its root:

```sh
python3 projects/isothermal-reducers/check.py
```

Python 3.10 or later suffices. There is no installation, network access,
third-party package, symbolic algebra system or simulation in that command.

Place five vertices around a cycle. Cycle edges have weight `1/3`; diagonals
have weight `1/6`. Every vertex has total weight one. A death is chosen uniformly,
then its neighbours compete by fitness times edge weight. Introduce one mutant
uniformly, with fitness `1/25` against resident fitness one.

[The proof](proof.md) gives the graph, all state probabilities, absorption and
uniqueness arguments, and the exact comparison. The checker reconstructs every
labelled replacement event from the graph, verifies all state equations, and
checks the loop-free complete graph as a separate control.

Recorded run, Mallow, 19 November 2026, Python 3.13.2, exit status zero:

```text
PASS connected symmetric loop-free graph; every row sums to one
PASS all 30 transient equations and both absorbing boundaries
PASS all 30 complete-graph equations and both absorbing boundaries
fitness = 1/25
counterexample fixation = 1443761/29356625545
complete-graph fixation = 1/20345
strict positive difference = 51360/1837724759117
PASS exact counterexample; independent review and priority remain separate
```

Two deliberate failures must each exit with status one:

```sh
python3 projects/isothermal-reducers/check.py --mutate-certificate
python3 projects/isothermal-reducers/check.py --mutate-model
```

The first changes one certified value. The second keeps the certificate but
uses the wrong fitness. Both fail a harmonic equation. These controls establish
that the check depends on the data and model; they do not replace independent
mathematical review.

[The earlier calculation tools](MARKOV.md) support further experiments and
document the initial negative screen. The result is the explicit counterexample,
not that screen, a general classification, or a claim about biological effects.
The deferred birth-first question is not addressed.
