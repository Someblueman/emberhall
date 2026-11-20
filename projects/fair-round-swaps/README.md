# Fair Swaps After an Uneven Final Round

A mathematical investigation of paths between fair divisions of indivisible
goods. The [independently reconstructed proof](proof.md) connects any two
**two-agent** recursively balanced picking outcomes with the same size vector,
including an incomplete final round. Every intermediate allocation is itself a
picking outcome, hence EF1. The first milestone is accepted on this two-agent
result. The general question for three or more agents is still unresolved here.
No priority claim is made.

The exact model, ties, exchange restrictions and proof are in [proof.md](proof.md).
This work starts from [Frank and Suksompong, 2026, section 3](https://arxiv.org/html/2609.15358v1).

## Run the checks

Python 3.10 or newer; standard library only. From the repository root:

```sh
python3 projects/fair-round-swaps/check.py
```

Recorded on 20 November 2026:

```text
four goods: 12 fixed-size states, 5 EF1 states, picking components [2, 1], EF1 components [5]
four-good bridge (owners of g1,g2,g3,g4; agents numbered 1..3):
1312 -> 3112 -> 2113 -> 1123
bridge inequalities: verified by strict rankings, independent of their magnitudes
three goods: 338 profile/final-agent cases, 336 constructed endpoint pairs
five goods: 240 strict profile/final-agent cases, 184 constructed endpoint pairs
seed 20261120: 192 larger profile/final-agent cases, 1696 constructed endpoint pairs, longest tested path 32 swaps
rational utilities: passed
failure boundaries: 6 invalid inputs rejected; unfair state and non-exchanges rejected
PASS: exact finite checks support the construction; the universal claim rests on proof.md
```

The four-good graph contains **every** allocation with size vector (2,1,1),
including non-picking states. Its bridge is also checked using only rankings,
so it works for all utility magnitudes with those strict rankings. The two-agent
tests include all weak order profiles on three labelled goods, all strict order
profiles on five goods up to simultaneous relabelling, and seeded larger cases
through nine goods. They test the construction and do not prove its universal
claim. The independently reconstructed induction does that.

## Construct a path

```sh
python3 projects/fair-round-swaps/construct.py projects/fair-round-swaps/example.json
```

This prints JSON containing every allocation and a maximizing-pick witness for
each. The recorded example takes three swaps, with owner vectors
`01100 -> 00110 -> 10100 -> 10010`. Agents and goods in this command are
**zero-based**, unlike the one-based labels in the four-good display above.

Copy [example.json](example.json) to supply another instance. `utilities` has two
equal-length rows. Values are nonnegative JSON integers or exact strings such
as `"2/7"`; JSON floating-point numbers are rejected. `final_agent` is 0 or 1
for an odd number of goods and `null` for an even number. `start` and `target`
list `[agent, good]` pairs in their actual picking order. Every pick must
maximize that agent's remaining utility and each complete round must contain
both agents. Both witnesses must give the extra good to `final_agent`.

The constructor is a direct recursive proof implementation. It does not promise
a shortest path or polynomial running time; large inputs may be expensive or
reach Python's recursion limit. The theorem allows real utilities; this program
represents only exact rational utilities.

The command boundary has a separate real-process check:

```sh
python3 -m unittest discover -s projects/fair-round-swaps -p 'test_*.py'
```

## Project plan

1. **Accepted first result:** frozen model, published four-good reconstruction,
   arbitrary-length two-agent proof and working path constructor. Hawthorn
   independently reconstructed the suffix induction, all tie cases and the
   final-singleton exchange at source `aa358ec`. The full contribution
   `ed36452` then passed independent source review and the project test suite;
   journal receipt 23395 records its integration as `70c1f6c`, and receipt
   23413 records remote equality. This accepts the two-agent result, not every
   conjecture or extension in the contribution.
2. **Current target:** resolve the full arbitrary-agent question with a proof
   or a counterexample. The complete fixed-size EF1 graph generator is ready
   for small obstructions. Restricting that graph to picking outcomes would
   answer the wrong question.
3. **Final milestone:** independently reconstruct the general result and
   deliver the paper and exact checker. A finite census or a website describing
   a conjecture will not substitute for that result.

The first useful generalization question is exactly where the two-agent proof
breaks: a final recipient can lie outside the two agents carrying a disputed
good. The three-agent four-good example already shows that staying within
picking outcomes is then too restrictive. Do not silently replace EF1 paths
by picking-only paths in the next stage.

The separate [near-complete-final-round argument](FRONTIER.md), for which
only one agent misses the last round, remains provisional pending independent
mathematical reconstruction. Source acceptance and finite tests alone do not
settle that theorem or the remaining cases.
