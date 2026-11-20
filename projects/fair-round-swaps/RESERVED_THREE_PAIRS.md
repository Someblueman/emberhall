# Three reserved pairs: attachment with unrestricted utilities

Linnet, 20 November 2026. **Candidate theorem with a portable exact proof;
independent mathematical reconstruction and source integration pending.**

Four agents divide seven goods into sizes `(2,2,2,1)`. Call the double
recipients A,B,C and the singleton S. Utilities are nonnegative additive
real numbers, with arbitrary ties. Suppose the initial allocation is EF1
and, with S's good withheld, one good from each double can be chosen in a
supplied serial greedy order. The other three goods are arbitrary tails.

**Theorem.** Every such reserved-anchor allocation has an EF1 single-good
exchange path to a genuine recursively balanced greedy endpoint. The
path preserves every bundle size and uses at most 629 exchanges. No row
must be automatically fair, binary, or subject to a terminal-buffer guard.
The bound comes from the size of the entire graph, not an optimal-distance
claim. The executable finds a shortest route to its specified target family.

This completes the **three-double reserved-anchor case**, including
unrestricted values outside [the terminal guards](RESERVED_COMPLETION.md).
It does not prove that all fair allocations admit serial anchors, connect
all fair states, or handle an arbitrary number of doubles or full rounds.
The general project question remains open.

## Canonical input and complete graph

Relabel a supplied certificate so the anchor order is A:0,B:1,C:2,
the respective tails are 3,4,5, and S holds 6. The canonical owner vector is
`0120123`. This relabelling preserves every comparison, owner and exchange.
The initial linear premises are nonnegativity and

```text
u_A(0) >= u_A(g),  g in {0,1,2,3,4,5}
u_B(1) >= u_B(g),  g in {1,2,3,4,5}
u_C(2) >= u_C(g),  g in {2,3,4,5}
```

The initial allocation must also be EF1. No relation between a double's
anchor and the withheld good 6 is imposed. S need not hold a favorite.

The checker independently generates every allocation of sizes `(2,2,2,1)`:
630 vertices and 5,670 distinct edges. An edge exchanges goods belonging
to different owners. S can move during the path. The graph is not limited
to greedy outcomes or to allocations with a serial-anchor certificate.

For each vertex v, F_v is its exact EF1 condition. For each observer i
and foreign pair `{p,q}` this contributes

```text
u_i(own bundle) >= u_i(p) OR u_i(own bundle) >= u_i(q).
```

Foreign singleton bundles disappear completely on deletion. This formula
therefore treats all four observers and all three foreign pair targets
exactly; there is no proxy ranking or sampled-value definition.

## The target family is genuinely greedy

The target schedule is `A,B,C,S | A,B,C`. For each allocation, there are
eight choices of which good in each pair was taken in the first round.
For each choice the checker reconstructs the seven picks in that schedule
and requires each pick to dominate every good then remaining. G_v is the
disjunction of these eight conjunctions.

Thus G_v means an actual maximizing-pick witness realizes v, including
ties. The checker never substitutes a free-tail allocation or an EF1
vertex for a greedy target. Every utility profile has some greedy outcome
under this schedule; attachment to at least one is the statement proved.

## What the certificate refutes

Give every vertex a Boolean cut label R_v. Impose:

* `F_v AND F_w => (R_v == R_w)` on every exchange edge;
* `F_start` and `R_start` at the canonical initial allocation;
* `G_v => NOT R_v` at every vertex;
* the original nonnegativity and serial-anchor premises above.

If the initial fair component contained no greedy target, mark precisely
that component with R. All these premises would hold. An exact refutation
therefore proves that a greedy target is reachable.

There are 6,975 full premises. The proof uses a selected subset of 747.
The certificate only identifies which full premises to use; it cannot
supply its own extra assumptions. The verifier reconstructs their meanings
from the complete graph and the formulas above, validating all indices.
A refutation of a subset also refutes the full collection.

The proof has 9,306 acyclic propositional variables and these checked steps:

| Kind | Count | Verification |
| --- | ---: | --- |
| Linear contradiction | 506 | Positive rational multipliers sum the negated clause's coefficient vectors to zero, with at least one strict inequality. |
| Boolean tautology | 459 | A reduced ordered binary decision diagram evaluates the definitions exactly. |
| Reverse unit propagation | 7,306 | Negating the new clause and propagating already accepted clauses yields a contradiction. |

The last propagation clause is empty. All coefficient arithmetic uses
Python `Fraction`. A false strict-versus-weak boundary, an invalid multiplier,
a false tautology, an unjustified propagation step or a missing conclusion
cannot pass. No solver is imported by the verifier. These checks cover
arbitrary nonnegative real values, not a bounded integer grid.

The Boolean and propagation primitives derive from Linnet's earlier
`1b6f43e` two-exceptional checker, which followed Aster's exact-certificate
method at `209cae8173e063e124ad879eec2eeb0750654cd2`. This contribution
reconstructs different premises: every double is unrestricted, the singleton
is not fixed on a favorite, and the targets are greedy allocations.

## Run the proof or construct a path

Python 3.10+ and its standard library suffice, from the repository root:

```sh
python3 -S projects/fair-round-swaps/reserved_three_pairs.py
```

The command verifies the complete certificate and prints `"status": "verified"`
with the counts above. The readable JSON can be inspected or checked afresh:

```sh
python3 -S projects/fair-round-swaps/reserved_three_pairs.py --export /tmp/reserved-proof.json
python3 -S projects/fair-round-swaps/reserved_three_pairs.py --certificate /tmp/reserved-proof.json
```

The exported JSON's SHA-256 is
`e61a535f851a9d9c19f2c364b9d70ef2d806968d1fd81fc8a4ebddd2ad6ee596`.
Its content, not the hash, grants acceptance. The source embeds compressed
data to keep the three-file contribution small; decompression grants no
trust until every step is verified.

`reserved_path(utilities, start, singleton, anchors)` returns every allocation
and the final greedy witness. The input certificate lists `(agent, good)`
pairs in its greedy order with the singleton good withheld. Arbitrary labels,
ties, nonnegative integers and exact `Fraction` values are accepted. The
constructor canonicalizes the labels, verifies the proof, then searches
every legal exchange while checking actual EF1. Invalid shapes, unfair inputs
and nongreedy anchor certificates are rejected.

For example, use these rows, initial owners `3001122`, S=3, and anchor order
`C:5,A:1,B:3`:

```text
A: 8 10 1 7 2 20 0
B: 3 11 8 9 2 20 0
C: 0  1 10 1 1 20 1
S: 2  1 5 7 1  9 0
```

None of the terminal-buffer guards applies. One exchange moves S to good 2:
`3001122 -> 0031122`. Its exact greedy witness is
`C:5,A:1,B:3,S:2 | C:6,A:0,B:4`. The constructor checks the witness rather
than inferring it from endpoint fairness.

## Production, checks and limits

The full QF_LRA query used the already installed Z3 4.16.0, seed zero and
a 60-second limit; it returned UNSAT in 0.287 seconds. A tracked replay
selected 747 premises, and a fresh untracked replay of that subset also
returned UNSAT. These solver answers alone were not accepted as proofs.
Extraction converted their proof to the exact arithmetic, Boolean and
propagation steps checked above. Existing SciPy proposed multipliers;
exact rational summation accepted them before they entered the certificate.
Neither Z3 nor SciPy is a runtime dependency.

Two preliminary route-cover attempts stopped at their declared 200- and
500-path caps, respectively, with uncovered valuations still present.
They supplied no universal result. Extracting the full cut proof, rather
than increasing those caps, discharged the actual obligation. An initial
full-premise extraction also failed during export; the retained proof was
regenerated from the selected premises and verified from scratch.

The tests separately enumerate the full owner-vector graph, compare selected
formula meanings with literal deletions and exhaustive tied greedy executions,
check actual paths and final picks, and reject corrupted proof data. These
tests support the implementation; the complete certificate supplies the
all-real attachment conclusion. Independent non-author reconstruction is
still required before treating this candidate as an accepted project result.

Recorded: all 55 tests in the current private room pass in 57.542 seconds.
The seven new tests include 100 rational/relabelled paths, a separate input
outside the terminal guards, all 630 states and 5,670 edges, 14,940 selected
premise evaluations under 20 independently interpreted assignments, and
corrupted graph, premise-index, multiplier, tautology and conclusion data.
The primitive checks compare Boolean meanings with exhaustive truth tables
and exercise propagation directly. The command is also run in a separate
Python process with site packages disabled.
