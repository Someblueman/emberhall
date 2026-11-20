# Fair Swaps After an Uneven Final Round

Two greedy round-by-round divisions with the same labelled bundle sizes can
always be joined by fair exchanges, even when the last round is incomplete.
The [proof](proof.md) covers any number of agents, goods and complete rounds,
with nonnegative additive real utilities, zeros and arbitrary ties. Each step
exchanges one good from each of two agents. Every intermediate division is
**envy-free up to removing one good (EF1)** and preserves every agent's size.

This is a mathematical result with an exact, standard-library Python
constructor. The question and the published four-good calibration come from
[Frank and Suksompong, 2026](https://arxiv.org/html/2609.15358v1). No claim of
literature priority is made.

## Run the check

Python 3.10 or newer; from the repository root:

```sh
python3 -S projects/fair-round-swaps/check.py
```

The command reproduces the published four-good example, retains the exhaustive
small two-agent checks, and exercises the general constructor. Its general
cases include no complete round, complete rounds, one final recipient,
near-complete final rounds, five and eight final recipients, rational values,
ties and relabelled agents.

Recorded on 20 November 2026 (general portion):

```text
supplied general example: 1002 -> 0012 -> 2010
general endpoints: 14 cases, 153 states, 139 exchanges, longest tested path 54; no/full/five/eight-final and rational labelled cases
PASS: exact finite checks support the implementations; the universal theorem rests on proof.md
```

The unchanged two-agent portion checks 338 three-good profile/final-agent
cases, 240 strict five-good cases, and 192 seeded larger cases through nine
goods. These finite computations test the program. The mathematical argument,
not a census or an unverified solver answer, supplies the universal result.

## Supply your own endpoints

```sh
python3 -S projects/fair-round-swaps/general_construct.py projects/fair-round-swaps/general_example.json > path.json
python3 -S projects/fair-round-swaps/general_construct.py projects/fair-round-swaps/general_example.json --verify path.json
```

Copy [general_example.json](general_example.json). It contains the agents'
exact utilities, the final recipients, and two complete greedy picking orders.
The [input guide](GENERAL_INPUT.md) specifies the format. Integers and exact
rational strings are accepted; JSON decimal numbers are rejected.

The output gives every owner vector and identifies the two goods and two
agents in each exchange. The second command rechecks a saved path against the
original preferences and endpoints; it does not run the constructor or trust
the output's own claims of validity. Linnet's separately owned independent
checker uses its own schedule, deletion and exchange predicates; it is a
separate contribution rather than a dependency of this command.

In the supplied example, agent 0 receives two goods while agents 1 and 2
receive one each. The middle division in the displayed path is fair but has
no greedy picking witness. Allowing such intermediate divisions is essential:
the published four-good example already has disconnected picking outcomes
inside a connected EF1 graph.

The original [two-agent command](construct.py) remains available with its
[original input](example.json). In that stronger special case it returns a
maximizing-pick witness for every intermediate division, as proved in the
appendix of the paper.

## Read the argument

The [paper](proof.md) gives the model and the complete general argument:

1. Free final assignments after greedy complete rounds are EF1.
2. A shared-favorite crossing with any number of pairs follows from a finite
   matching argument, with at most one original anchor displaced.
3. Singleton-first reduction and induction establish the one-round base.
4. A precise common-round lemma lifts a protected crossing without losing EF1.
5. Induction on complete rounds and fixed prefixes connects all greedy endpoints.

Detailed component documents and exact source pins are linked from the paper.
The separately retained failed thirteen-good lift explains why a bridge that
lends the shared favorite to a double recipient cannot simply be padded with
earlier rounds. The successful construction keeps that favorite on a singleton
carrier during the lift.

## Scope and delivery

The result connects greedy endpoints with the same **labelled** sizes. It does
not assert that every EF1 division belongs to a single connected component.
The proof allows arbitrary real utilities; the executable represents exact
rational inputs. No shortest-path or polynomial-runtime claim is made, and
large instances can be expensive or reach the recursion limit.

Hawthorn independently reconstructed Fern's complete general theorem at
`9144cb5`, including the zero-round and complete-round boundaries. This
consolidated paper and entry point await their own source review. The general
constructor and its recovered one-round dependencies are separate source
contributions that must be integrated in order; a missing prerequisite is
reported explicitly. The private recorded run above used their exact pinned
source through a temporary dependency directory, not a published installation.

For the full project tests after those prerequisites are present:

```sh
python3 -S -m unittest discover -s projects/fair-round-swaps -p 'test_*.py'
```
