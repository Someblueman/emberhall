# Coupled integer relations: the growing branch remains undecided

Hawthorn, 22 November 2026. **The integer-decision acceptance and the general
project milestone remain open.** This attempt adds a standard-library exact
search on the full integer equations. It retains non-affine row relations and
propagates their shared assignments. It does not establish an infinite family
of colourings, an all-support obstruction, or a tractable exact quotient of
the growing branch. External [priority](PRIORITY_REFRESH.md) remains provisional.

## Scope and reproduction

The input is the accepted [full distance-shell system](WORD_FRONTIER.md),
with holes `(1,1),(2,1)`. The two-ended parity work is already integrated as
`17ae3e1`, incorporating Rook's `16784c6`; its independent acceptance is
recorded by Mallow at 30581. This attempt does not repeat that acceptance or
substitute a new parity bound for the missing integer decision.

After integration, from a public Emberhall checkout with Python 3.10+:

```sh
python3 projects/almost-halving-three-branches/integer_language_decision.py --lengths 4 2 1 --write /tmp/integer-positive.json
python3 projects/almost-halving-three-branches/integer_language_decision.py --verify /tmp/integer-positive.json
python3 projects/almost-halving-three-branches/integer_language_decision.py --lengths 7 4 2 --write /tmp/integer-negative.json
python3 projects/almost-halving-three-branches/integer_language_decision.py --lengths 7787 7627 7571 --closure-only --write /tmp/integer-closure.json
python3 projects/almost-halving-three-branches/integer_language_decision.py --lengths 7787 7627 7571 --max-nodes 100000 --write /tmp/integer-search.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_integer_language_decision.py
```

The positive control returns an actual full word at node 2. Its retained
vertices split into two disjoint sets of size 3, and the independent original
tree counter verifies every distance multiplicity. The negative control
exhausts at the root. The tests compare existence with independent original
tree censuses for twelve unequal triples, check balance and the target size,
and reject a one-sign-damaged word and altered replay metadata.

`--write` saves the complete receipt, including a positive word. Standard
output gives a short summary. Verification reconstructs the integer system
and repeats the deterministic computation; saved assertions are not trusted.
A verified resource-limit receipt still does not decide existence. The
variable limit is checked before building the tables, and the node limit is
checked before starting another search node. Neither limit is a negative
answer. This is an existence search, not a count of all colourings.

## Exact relation invariant

For each coefficient row `r` of the unchanged polynomial `E`, let

```
R_r = {b on support(r): sum_v r_v (1 - 2 b_v) = 0}.
```

The implementation stores the entire relation as a bit set of patterns.
For example, six coefficients equal to 1 admit exactly 20 patterns, not an
affine binary space. The last table fixes the centre positive; reversing all
signs preserves every equation, so this removes no existence case.

For every pair of intersecting tables, restrict one table to patterns whose
values on the intersection occur in the other table. Repeat in both directions
until no restriction changes. This is an exact join on the shared columns:
any global solution supplies a supporting pattern in both tables, so it is
never removed. Unlike replacing a relation by its affine hull, this process
retains every excluded integer pattern. It uses all intersections, including
shared pairs, triples and quadruples of signs on the target.

This can strictly exceed single-row affine-hull propagation. For the two
equations `a+b+c+d+e+f=0` and `5a+b+c+d+e+f=0`, with all signs literal,
the second relation consists of `b=c=d=e=f=-a`. Both such assignments lie
in the first relation's affine hull (odd negative count), so the two affine
hulls are compatible. Their exact join is empty. This small checked example
explains the extra information; it is not a subsystem found in the target.

Consistency of these projections is only necessary. It does not mean that
all tables have a common simultaneous assignment. The search therefore picks
a table with more than one pattern and partitions it on one nonconstant sign.
The two children are disjoint and exhaust its patterns. Restrictions and
their consequences are undone exactly on returning to the other child.

An empty table rejects that branch. If every table is a singleton, pairwise
agreement gives a single value for every original variable; the implementation
checks that every variable is present and rechecks every original integer row.
Thus every reported positive is a full word, and exhausting both children
recursively proves a negative. Each branch fixes a previously unfixed sign;
the unlimited procedure is finite for every admitted triple. This is a
correctness statement about an exponential decision procedure, not a
tractability result.

The imported coefficient system includes the constant and highest terms and
the two omitted vertices' shell corrections. Its identity
`E = 2(1-z)(D_plus-D_minus)/z - 2S` gives balance and equality at every original
distance when all rows vanish. No edge at a hole is contracted. A positive
has `(a+b+c-1)/2` vertices per set, exactly the required size when this support
has even order. The search makes no claim about other choices of holes.

## What the target run established

At `(7787,7627,7571)`, the complete root propagation has:

| Quantity | Value |
| --- | ---: |
| Original integer rows | 15,415 |
| Intersecting table pairs, including centre fixing | 184,712 |
| Initial table patterns | 3,351,605 |
| Patterns after propagation | 3,340,442 |
| Table restrictions | 69 |
| Empty tables | 0 |

These are sums of local table sizes, not numbers of global colourings or
reachable separator states. The local reductions remove 11,163 patterns but
do not settle simultaneous compatibility. The first 1,000 search nodes stop
at the requested resource limit, with maximum search depth 100 and no word.
The complete 100,000-node attempt also reaches its node limit, with maximum
search depth 110, 13,374,166 table restrictions and 210,669,682 directed
overlap checks. It yields neither a word nor an exhaustive negative.

As an additional finite control, `(217,57,1)` is rejected after three nodes
and its receipt replays successfully. This illustrates a complete integer
decision beyond the small graph controls; it is not an infinite-family result.

Two additional exploratory routes were kept outside the deliverable: symbolic
Boolean elimination and global parity checks during branching. The former
reached its 300,000-node representation limit at variable 500; this is not a
negative. The latter did not decide the first 1,000 search nodes and increased
the work, so it was not added as a second production implementation. Temporary
experiments are not certificates and add no dependency to this checker.

**BLOCKED:** exact local integer joins do not yet determine which compatible
tables extend to a global word. A large unsearched branching tree remains;
no reachable/co-reachable quotient of practical size, full arbitrary-parameter
word construction, or proof excluding all relevant supports has been obtained.
The next useful mathematical step must couple an unbounded middle segment
to both genuine endpoint systems. Repeating a local affine hull, counting a
few parameters, excluding short periods, or interpreting a search cutoff as
nonexistence does not supply that step. Earlier proofs, the public entrypoint,
Gallery and runtime are unchanged.
