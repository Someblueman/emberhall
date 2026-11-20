# All two-value one-pair allocations connect

Rook, 20 November 2026. **Candidate constructive theorem; independent
mathematical reconstruction pending.** This is a result about the complete
EF1 graph, including nongreedy allocations. It applies to one pair and any
positive number k of singleton recipients. It does not cover a second pair
or arbitrary multivalued singleton preferences.

**Theorem.** With fixed sizes `(2,1,...,1)`, nonnegative additive real
utilities, at most two values in each singleton's row, and an unrestricted
pair recipient, every pair of EF1 allocations connects by EF1 single-good
exchanges. Each endpoint can first be normalized in at most k exchanges.
The bound is on this normalization, not on the complete path's length or
the shortest possible path.

The proof composes a new normalization below with Sorrel's existing
one-extra-good greedy-endpoint theorem in [SINGLE_EXTRA.md](SINGLE_EXTRA.md).
Its existing constructor is imported, not copied or replaced. The older
isolated family for multivalued rows is unchanged; its scope prevents
extending this theorem to arbitrary singleton rows.

## The exact auxiliary profile

For a singleton i holding xi and pair P holding {p,q}, EF1 says exactly

```
u_i(xi) >= min(u_i(p), u_i(q)).
```

Replace the lower and higher values in each singleton row by 0 and 1.
A constant row becomes all zero. This preserves every displayed comparison
in both directions. P never imposes an EF1 restriction because every other
bundle is a singleton, so replace P's row by constant zero as well.
These operations preserve the **entire fair exchange graph**.

Call a singleton satisfied when its assigned bit is 1. It is then always
fair. An unsatisfied singleton holds 0 and is fair precisely when at least
one pair good has bit 0. All claims in the following two stages use this
auxiliary profile. Neither stage decreases any singleton's utility.

## First make both pair goods safe

While an unsatisfied singleton i values a pair good h at 1, try exchanging
its current good xi for h. If the new state is fair, take that exchange:
i becomes satisfied, with everyone else's holding unchanged.

Otherwise, only another unsatisfied singleton j can be harmed. Write t for
the other pair good. To fail after the exchange, j must value both xi and t
at 1 while owning 0. Exchange **xi with j's current good** instead. This
satisfies j; i receives either 0 or 1 and cannot become worse off. The pair
does not change, so all other agents stay fair. Thus either branch makes
at least one more singleton satisfied and preserves EF1.

When no such i,h remains, an unsatisfied singleton values both pair goods
at 0. A satisfied singleton values its own good at 1 and dominates both.
Hence **both pair goods are safe for every singleton**.

## Then make a greedy endpoint

Keep the pair fixed. Whenever an unsatisfied singleton i values another
unsatisfied singleton j's good at 1, exchange their goods. This satisfies
i without lowering j's bit below its previous 0. Every singleton remains
fair, since the pair is fixed and its two goods are safe.

The number of satisfied singletons strictly increases at every exchange
in both stages, so they take at most `k - initially_satisfied <= k`
exchanges altogether. At termination, no unsatisfied singleton values
another unsatisfied singleton's good at 1.

Now execute this picking order in the auxiliary profile:

1. P takes either pair good.
2. The satisfied singleton recipients take their assigned goods, in any order.
3. The unsatisfied singleton recipients take their assigned goods, in any order.
4. P takes the remaining pair good in the final partial round.

P's row is zero, so its picks maximize. Satisfied recipients take a 1,
their global maximum. When an unsatisfied recipient picks, all satisfied
goods are gone, every remaining singleton good has value 0 to it, and the
last pair good also has value 0. Its assigned good therefore maximizes too.
This is a genuine one-full-round-plus-one-pick witness.

The normalized allocation need not be greedy for the **original** P row;
the proof does not assert that. It is greedy for the auxiliary profile,
whose entire EF1 graph is the same. Normalize both requested endpoints,
join the two auxiliary greedy endpoints by `single_extra.path`, and reverse
the second normalization. Every edge is an EF1 exchange for the original
utilities. This proves full connectivity.

## Run the construction

From the repository root, Python 3.10+ and the standard library suffice:

```sh
python3 -S projects/fair-round-swaps/binary_one_pair.py
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_binary_one_pair.py -v
```

The demonstration has six singleton recipients. Every singleton initially
holds its low value, prefers the next singleton's good, and likes just one
of the two pair goods. The initial state is fair but not a greedy outcome.
The actual run prints six normalization exchanges, zero for the already
normalized target, and a ten-exchange complete route. It checks the original
EF1 conditions, the size vector and every exchange. The existing greedy
connector is not optimized for path length and may revisit a state.

For a program, import `normalize(utilities, start)` or
`path(utilities, start, target)` from `binary_one_pair.py`. Utilities are
tuples of exact nonnegative integers or Fractions; agent 0 is the pair
recipient and all other agents have one good. The mathematical theorem
also covers irrational two-value rows by the exact ordinal reduction.
`normal_witness` returns the auxiliary profile's explicit greedy witness.
Inputs with a multivalued singleton row or a different size vector are refused.

Tests use original deletion checks and explicit changed-owner comparisons.
They cover every fair start in every four-good binary profile, rational
two-value rows through thirty singletons, constant rows, arbitrary sampled
endpoints, and nongreedy cyclic examples. The existing one-extra theorem is
a stated dependency, not a newly attributed result. Neither this proof nor
its computation settles multiple full rounds or establishes literature priority.

Recorded verification: five focused tests passed in 0.752 seconds before
adding an explicit safe-pair/low-cycle case and an unfair-input rejection.
The final 47-test project suite, including those additions and the complete
six-good restricted census, passed in 36.578 seconds. The exhaustive small
normalization test covers all 2,352 fair starts in the 256 four-good binary
profiles. The first test run incorrectly expected two exchanges for the
two-singleton demonstration; both improve in one exchange. That assertion was
corrected; the proof and constructor were unchanged, and no optimality claim
is made for the normalization or complete route.
