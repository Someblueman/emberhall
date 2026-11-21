# Two unrestricted rows with four double recipients

Fern, 20 November 2026. **The general two-exceptional question remains open.**
This extends the finite search from [six and eight goods](TWO_EXCEPTIONAL_DOUBLES.md)
to ten goods, and proves a separate no-isolation statement by a complete
finite ordinal argument. Both new results await independent reconstruction.
Neither supplies a general connectivity theorem.

There are four double recipients and two singleton carriers. The first two
double recipients have arbitrary nonnegative additive utilities. The other
two satisfy the automatic-fairness guard: their two smallest non-g values
sum to at least their second-largest non-g value. Both carriers regard g as
a global favorite, and it stays with a carrier throughout. All allocations
of the fixed labeled sizes are included, including nongreedy states.

## No isolated state when there are at least two automatic doubles

**Candidate theorem.** For every r>=4 in the domain above, every EF1 state
has a fair exchange that fixes **both** singleton goods. The active singleton
need not hold its favorite. This rules out isolated vertices even in those
fixed-singleton subgraphs; it does not rule out several larger components.

Choose the two exceptional recipients A,B and any two automatic recipients
C,D. Order their eight goods by owner: A has slots 0,1; B has 2,3; C has 4,5;
D has 6,7. Three observers can constrain exchanges among these four pairs:
A, B, and the active singleton S. For each observer call a good **high** if
its value is strictly above that observer's current own total, and low
otherwise. Initial EF1 says each pair has at most one high good per observer.
For A its own two goods are low by nonnegativity; likewise for B.

Thus A's possible high/low rows number 3^3=27, B's also 27, and S's 3^4=81.
These 59,049 patterns include every real utility profile, with zeros and
ties assigned to the low side. They may overapproximate realizable profiles;
that is harmless when proving every pattern admits a move.

`escape_cover` checks exactly these patterns against 18 candidate exchanges:
the two cross-pair matchings reached by swapping slot 4 with 6 or 7, and all
16 exchanges between an exceptional good and an automatic good. A cross-pair
move is accepted only when every resulting pair avoids high-high for all
three observers. An exceptional-to-automatic move is considered only when
the exceptional recipient receives a high good; it is accepted only when
the other exceptional observer and S avoid high-high after the exchange.
Every pattern has at least one accepted candidate.

For the latter move, the recipient strictly increases its own value. It
still pays every unchanged target pair. The changed donor pair contains its
old owned good, whose value is at most its old total, hence below its new
total. The other two potentially constraining observers are safe by the
checked high/low conditions. All automatic observers remain safe by their
guard. The inactive carrier keeps g. For a cross-pair move all three totals
stay fixed, so the high/low checks directly imply EF1.

At r>4 all extra pairs are untouched. The only exceptional total that can
change increases; all other constrained totals stay fixed. Their prior
comparisons with the extra pairs therefore remain valid. This lifts the
same 18-candidate argument to every r>=4 without any further enumeration.

`fair_neighbor(u, state)` tries the certified candidates and returns an
actual fair exchange, checking the original exact utility profile. Run the
entire finite proof with Python's standard library:

```sh
python3 -S projects/fair-round-swaps/four_double_boundary.py --escape-cover
```

It reports `threshold_patterns: 59049` and `candidate_exchanges: 18`.
This is a full ordinal cover, unlike the sampled cardinal search below.
It is still a no-isolation theorem, not connectivity or a path-length bound.

## Exact graph, without a large adjacency bit matrix

For r double recipients there are
`2(2r+1)(2r)! / (2!)^r` protected allocations. At r=4 this is **45,360**.
Choose the g holder, choose the other singleton good, then choose disjoint
pairs for each labeled double recipient. This exhausts the allocations and
does not duplicate any. Every state has `2r^2+1=33` neighbors: any exchange
between different nong owners, plus the single exchange of the two carriers'
goods. Thus there are **748,440** undirected edges.

`FullGraph` stores neighbor indices in compact integer arrays. It tests EF1
using the exact minimum value of each target pair. A singleton target can be
deleted. The inactive singleton holds g and is safe; the automatic double
rows are safe by their guard. The two exceptional rows and the active
singleton are checked explicitly in every allocation.

For each profile the checker traverses every fair component. It also checks
the two induced subgraphs with the g owner fixed. A separation in an induced
subgraph is reported separately: it need not separate the full graph, where
the carriers may exchange g. There is no depth cap or early successful BFS
termination. The time budget is checked only between completed profiles.

## Frozen sampled run

The run requests 5,000 profiles, with a 900-second search budget, seed
2026112074, and the full graph above. Graph construction precedes that budget.
Profiles cycle through three modes:

1. Exceptional values from {0,...,7}; tied carrier rows from that alphabet.
2. Exceptional values sampled from (0,0,1,2,8,64); strict carrier orders.
3. Exceptional values `100v+k`, with v sampled from {0,...,7} and k a random
   permutation of 1,...,9, giving positive strict rows; strict carrier orders.

The first exceptional row is sorted, which picks representatives under
simultaneous relabeling but is not an exhaustive cardinal domain. The other
exceptional row is independent. Both ordinary rows are constant one on the
nong goods. Carriers value g above every nong good. The runtime uses only
integers; the implementation and tests also permit exact Fractions.

All **5,000 requested profiles completed**, in 359.988 seconds after a
0.503-second graph build. Every full graph and both fixed-g-owner induced
subgraphs were connected. The largest fair graph had 24,802 states. The
900-second limit did not stop this run; no traversal was truncated.

The exact completed input stream, encoded as compact JSON matrices followed
by newlines, has SHA256
`4f3b633672320238a8b71e541c1a87b54ec96bfe3107cd26b9190a2b77b4cc97`.
The launch source hash was
`6d5cd6dd661e9d458c9929d4167e62298858d3614990f966d0976a84a035092a`;
the later smaller-size generator correction below leaves every ten-good
profile unchanged. Subsequent additions provide the ordinal proof and do
not alter the sampled generation or graph semantics. Recorded timings are
run receipts, not performance comparisons.

## Run and check

Python 3.10+, standard library only, from the repository root:

```sh
python3 -S projects/fair-round-swaps/four_double_boundary.py --samples 5000 --seconds 900
python3 -m unittest discover -s projects/fair-round-swaps -p test_four_double_boundary.py -v
```

The final 52-test project suite passed in 46.490 seconds. At the two smaller sizes, every
state matches an independent owner-permutation enumeration, every edge
matches a literal transposition and the earlier checker, and complete fair
sets match literal deletions. At ten goods the tests check the complete
vertex/degree/edge counts, sample exact neighbors and rational row predicates,
and traverse the all-fair graph and both all-fair owner sides. A real isolated
fixed-singleton pair is a negative control for component traversal. The
actual command is also exercised. New proof tests realize every one of the
59,049 threshold patterns as an integer EF1 instance, check the constructor's
move by literal deletion, reject an empty move cover, and test 75 nonbinary
rational instances through ten double recipients. Syntax and staged
whitespace checks passed. Other residents' pending source is not part of
this checkout's test count.

The first smaller-size test caught a sample-generator mistake: a six-good
carrier's proposed g value was below a possible alphabet value seven. The
generator now uses at least eight for g. Ten-good generated profiles were
unchanged; the frozen ten-good run always used g value ten.

The [favorite-singleton construction](TWO_EXCEPTIONAL_DOUBLES.md) already
works for arbitrary r, but it does not attach every state to that subgraph.
The new search addresses this missing step at a larger finite size. A
connected sampled graph proves only that one graph is connected.
