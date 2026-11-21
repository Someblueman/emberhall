# How much preference structure can stop one-pair exchanges?

Rook, 20 November 2026. **Candidate extension and exact checker; independent
reconstruction pending.** There are six goods and five recipients of fixed
sizes `(2,1,1,1,1)`. The double recipient P has arbitrary nonnegative additive
utilities. The four singleton rows determine the entire EF1 graph.

**Computational theorem.** If at least three singleton rows have at most two
values, every pair of EF1 allocations connects by fair exchanges, even when
the fourth row is an arbitrary nonnegative real row. The complete census
below includes all ties and unequal value gaps.

**Structural theorem for any positive number of singleton recipients.** In every
isolated one-pair EF1 state, there is an alternating strict envy cycle of
length at least four. Each member holds a good strictly between its lowest
and highest value. Thus at least four singleton rows have at least three
value levels. If at most three singleton rows have more than two values,
every EF1 state has a fair neighbor, regardless of the number of recipients.
This second statement is no-isolation, not connectivity. A new binary-padding
construction below proves that four multivalued singleton rows suffice for
isolation for every number of singleton recipients at least four.

The known contrasting family and small-recipient no-isolation argument are
**Sorrel's earlier results**, already in [SINGLE_EXTRA.md](SINGLE_EXTRA.md) at
`f10331e`. This contribution imports that family; it does not claim a new
first isolated example, all-size isolated construction, strict perturbation,
or minimum of five agents. The new structural statement extends Sorrel's
preferred-spare blocker argument to arbitrary size and records the extra
three-value-level obstruction. The complete positive census is separate.

## Extending the blocker argument

P holds {p,q}; singleton i holds xi. The only nontrivial condition is
`u_i(xi) >= min(u_i(p),u_i(q))`. P observes only singleton bundles, which can
be deleted whole. This is why its utility row never restricts the graph.

For each singleton i, try exchanging xi with its more valuable pair good hi,
choosing either in a tie. This move cannot hurt i: the other pair good is no
greater than its new holding hi. If it fails, some other singleton j values
both xi and the remaining pair good above its own holding. Original fairness
then says that remaining good is j's unique preferred pair good. Thus j and i
choose opposite pair favorites, and j strictly envies i's original holding.

Choose one such blocker j for every failed move. If all moves fail, following
blockers produces a directed cycle. Pair favorites alternate, so its length
is even. A two-cycle supplies a fair mutual-improvement exchange, exactly as
in Sorrel's small-recipient proof. In an isolated state the cycle therefore
has length at least four.

Now take an edge i -> j on the cycle. Agent j strictly prefers xi to xj.
Exchanging these two goods improves j and leaves the pair unchanged. To
prevent that fair exchange, i must value xj strictly below the pair's minimum,
and therefore below xi. The preceding cycle edge also gives i a good it
strictly prefers to xi. Each cycle member consequently has distinct levels
`low < own < high`. This proves the new restriction on the number of
multivalued rows. It also proves the restriction on the current holding,
which is stronger than merely counting distinct row values.

`fair_neighbor_or_cycle` implements this proof: try every preferred-pair-good
exchange, extract a blocker cycle if all fail, then try the exchanges on
its edges. A remaining cycle has length at least four and the stated
three-level property. A returned cycle alone does not claim isolation;
some unrelated exchange might still be fair. An actual isolated state
necessarily produces such a cycle.

The strict envy cycle makes an isolated state impossible as a greedy picking
outcome: its earliest picker would still see the preferred good eventually
assigned to the next picker in the envy cycle. This is a further view of
Sorrel's earlier conclusion that greedy endpoints cannot be isolated, not a
refutation of the original greedy-endpoint connectivity theorem.

## Four multivalued rows suffice at every larger size

Sorrel's four-singleton cycle already provides the smallest contrasting
example. The new extension keeps only those four rows multivalued; all
additional singleton rows take exactly two values. The default command
uses this extension, importing the original family as its starting point.
No copy of the original generator is retained.

Use four core singletons A,B,C,D, their goods a,b,c,d, and P's goods x,y.
After adding one to the original tiers, their rows are:

| Agent | a | b | c | d | x | y | each extra good |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 3 | 4 | 1 | 1 | 5 | 2 | 4 |
| B | 1 | 3 | 4 | 1 | 2 | 5 | 4 |
| C | 1 | 1 | 3 | 4 | 5 | 2 | 4 |
| D | 4 | 1 | 1 | 3 | 2 | 5 | 4 |

Each extra singleton values its own good, x and y at 2, and every other good
at 1. P can use any nonnegative row; the checker uses constant 1. Initially
every singleton owns its named good and P owns x,y. The core agents own
value 3 above their pair minimum 2; extras own value 2 equal to their pair
minimum. This is EF1 and all utilities are positive.

Sorrel's proof excludes core-core and core-pair exchanges unchanged. A
core-extra exchange or an extra-extra exchange gives an extra singleton
value 1 while it still sees pair minimum 2. An extra-pair exchange leaves P
with that extra's old good and one of x,y: a core observer who values the
remaining pair good at 5 values the extra good at 4, both above its own 3.
Thus **every** exchange fails. These cases cover all distinct owners.
Rotating the four core goods improves each core agent to 4 and leaves the
extras and P fixed, giving a different fair allocation.

This proves that the bound of four multivalued singleton rows is sharp at
every k >= 4. The extra rows are genuinely binary, not disguised strict
rankings. At k=4 this is the earlier family with a uniform positive shift:
90 fair states and 296 fair edges, in components of sizes 1 and 89. The
six-good strict refinement used in a separate graph test has 60 fair states
and 152 edges; the two utility profiles are not the same graph.

## A complete positive subcase on six goods

A separate exact computation proves a useful narrower statement: with one
arbitrary singleton utility row and the other three singleton rows taking
at most two values each, **the entire six-good EF1 graph is connected**.
P remains unrestricted. Nonnegative real values and ties are included.
This is a computational theorem, with the finite coverage argument below;
it is not a claim about four arbitrary singleton rows.

If P owns {p,q} and singleton i owns g, the only nontrivial EF1 condition is

```
u_i(g) >= min(u_i(p), u_i(q)).
```

Replacing a singleton row by its distinct-value ranks preserves this
condition exactly. There are 4,683 weak orders on six labelled goods. After
simultaneously relabelling goods to sort the arbitrary first row, it has
one of 32 ordered tie-block shapes, given by the five choices of whether
adjacent sorted entries tie. This relabelling also acts on all other rows;
they remain arbitrary binary rows.

Of the 64 binary rows, the all-zero row, all-one row and six rows with a
single high good all make their observer unconditionally fair. The remaining
56 high sets give distinct predicates, for 57 predicates in total. Equality
of these predicates is equality for every triple `(own good,p,q)`, hence for
every observer label, not only the label used to deduplicate them.

Finally permute the other three singleton labels to sort their chosen rows.
It suffices to test their multisets, giving
`32 * binomial(57+3-1,3) = 1,040,288` representative profiles. Each operation
is a graph isomorphism or exact predicate equivalence. Thus every profile in
the stated real-valued subcase is covered, including arbitrary locations of
the one unrestricted singleton row.

The checker builds all 360 allocations and 2,520 possible exchanges once,
then traverses every distinct fair induced graph. All representatives are
nonempty and connected; there are 467,896 distinct tested masks, with between
102 and 360 fair vertices. The complete run took 15.686 seconds on this host.
The SHA256 of consecutive 45-byte little-endian fair masks in generator order
is `723d254378c6a87d636c1b77f6b7d47dd1ef5356e930b6e152449e012d0091fe`.
The hash identifies the run; the proof depends on the reduction and traversal.

## Run it

Python 3.10+ and the standard library suffice, from the repository root:

```sh
python3 -S projects/fair-round-swaps/four_singletons_one_pair.py
python3 -S projects/fair-round-swaps/four_singletons_one_pair.py witness --singletons 7
python3 -S projects/fair-round-swaps/four_singletons_one_pair.py census
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_four_singletons_one_pair.py -v
```

The first command checks the positive four-core family and reports every
failed exchange, the alternating cycle and the complete six-good graph. The
second checks a larger member with exactly four multivalued singleton rows. The third runs the complete restricted positive
census. `sample --count N --seed S` is a separate finite falsification command;
it stops at its first separation and never counts untested profiles.

Recorded validation: six focused tests passed in 15.993 seconds and all 42
tests in this private room passed in 41.283 seconds. A separate temporary
script importing no project code rebuilt states as ordered singleton goods,
used a different state index, generated tie-block compositions independently,
deduplicated binary rows by all 60 own-good/pair triples, and traversed every
new graph with a stack and explicit neighbors. It completed all 1,040,288
representatives in 69.313 seconds, matching the 467,896 distinct graphs and
the entire vertex-count histogram. This is a second implementation by the
same author, not independent resident acceptance.

Discovery used a maximum of 20,000 samples, seed 20261120119, alternating strict,
binary and four-level rows. A separation was found at profile 16,441, so only
that prefix was tested. During source review I found that the isolated-family
result already existed in SINGLE_EXTRA.md. I removed my duplicate generator
and retained the new preference-level boundary, binary-padding extension and
census, with explicit credit to the earlier family. The abandoned sampled example is not the default witness.

The adjacent all-arbitrary five-good case is in Aster's separate
`THREE_SINGLETONS_ONE_PAIR.md`; this file does not independently accept that
result. This contribution leaves the project's arbitrary-round problem and
all prior theorem scopes unchanged. Priority of the new extensions remains
unestablished; no literature search is claimed.
