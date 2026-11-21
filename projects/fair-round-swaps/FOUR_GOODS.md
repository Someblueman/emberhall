# Three people, four goods: every fair division is within three swaps

Candidate theorem and exact certificate by Rook, 20 November 2026. Independent
reconstruction is pending. This extends the single four-good example in
the project to **all** nonnegative additive real utilities in this size case.
It does not settle the arbitrary-length question or claim priority.

## Statement and exact reduction

There are three agents, four labelled indivisible goods, and a fixed size
vector `(2,1,1)`. Utilities are additive and nonnegative, with arbitrary ties.
Every vertex is an EF1 allocation: for each observer and each other bundle,
removing at most one good from that bundle eliminates the observer's envy.
An edge swaps one good of one agent for one good of another agent.

**Candidate theorem.** This entire EF1 graph is connected and has diameter
at most three. The bound three is attained. Consequently any two recursively
balanced picking outcomes with this size vector are connected through EF1
allocations in at most three exchanges, even when their picking-only graph
is disconnected. Relabelling agents gives the other permutations of `(2,1,1)`.

The universal quantifier over real utilities has the following finite reduction.
Call the double-bundle owner A and the singleton owners B and C. If A owns
`{p,q}` and the singleton goods are `b,c`, the only nontrivial EF1 conditions are

```
u_B(b) >= min(u_B(p), u_B(q))
u_C(c) >= min(u_C(p), u_C(q)).
```

Indeed any observer can remove the entire good from an envied singleton,
leaving value zero; their own utility is nonnegative. When B or C observes
A, removing the more valuable of A's two goods leaves exactly the minimum.
The condition for an agent observing itself always holds. A's utilities
therefore have no effect on any vertex or edge in this graph.

For each singleton agent replace its four utility values by their ascending
distinct-value ranks `0,...,k-1`, assigning the same rank exactly to tied
values. This preserves both displayed inequalities in both directions.
Conversely each such rank vector is itself an allowed nonnegative utility
row. Thus the replacement gives **exactly** all possible graphs, not a
sampling or approximation of cardinal utilities. Unequal gaps, irrational
values and zeros introduce no additional graph in this particular size case.
This argument fails for larger bundles, where sums rather than just ranks
can matter; it must not be reused for seven goods.

There are 75 rank vectors: one for each ordered partition of four labels.
The checker generates all `4^4` vectors with entries `0,...,3` and retains
exactly those whose used entries are `0,...,max`. This is bijective with the
rank vectors above. All `75^2 = 5,625` pairs are checked. A's omitted row is
arbitrary; it is not silently fixed by the theorem.

For each pair the checker constructs all `4! / 2! = 12` allocations by
permuting `(0,0,1,2)`, keeps exactly the allocations satisfying the two
inequalities, and constructs every edge by exchanging two differently
owned goods. Breadth-first searches from **every** remaining allocation
check connectedness and compute its exact diameter. No picking outcome
filter, symmetry reduction, random seed, floating point, external package
or downloaded code is involved.

## A direct proof of connectedness

For each singleton agent, call a good **safe** if its value is at least that
agent's second-highest value among all four goods, counting goods rather than
distinct values. There are at least two safe goods, even with ties. Holding
a safe good always satisfies that agent's EF1 inequality: no pair of other
goods can both be strictly more valuable.

Call an allocation a core allocation when B and C each hold a safe good for
themselves. Core allocations exist because each safe set has at least two
members, so the two agents can be assigned distinct safe goods.

Every EF1 allocation is at most one exchange from a core allocation:

* If both singleton goods are safe, it is already in the core.
* If just B's good is unsafe, at least one of B's safe goods is held by A
  (B holds none, and C can hold at most one). Exchange it for B's good.
  B is now safe and C remains safe, so EF1 holds. The other case is symmetric.
* If both are unsafe, exchange their goods. To see why this works, consider
  B's initial good `b`. At least two goods are strictly above it. EF1 says
  at least one of A's two goods is no greater than `b`. Thus C must hold one
  of the two higher goods, the other is held by A, and there cannot be a
  third higher good. C's good is therefore safe for B. The symmetric argument
  shows B's good is safe for C.

Finally the core is connected with diameter at most two. Encode its singleton
goods as `(b,c)` and a target as `(d,e)`; A holds the two omitted goods. If
`d != c`, first change B's good to `d`, then C's to `e`, omitting unchanged
steps. Both moves are exchanges with A and remain in the core. If `d == c`
and `e == b`, swap B and C. If `d == c` and `e != b`, first give C good `e`
from A, then give B good `d` from A. Each agent always receives its target
safe good, and the two singleton goods stay distinct.

This proves connectedness for all the stated real utilities without relying
on a program, and supplies a four-exchange bound. The exhaustive order-type
certificate tightens four to three and shows that three is necessary.

## Reproduce the certificate

From the public repository root, Python 3.10 or newer:

```sh
python3 projects/fair-round-swaps/four_goods.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_four_goods.py -v
```

Recorded run:

```
weak orders: 75
profiles: 5625
allocations per profile before the EF1 filter: 12
distinct labelled EF1 graphs: 346
diameter 2: 4311 profiles
diameter 3: 1314 profiles
vertex counts: 5:864, 6:2296, 7:912, 8:1134, 9:160, 10:234, 12:25
certificate SHA256: a7c8f21c0e0eff04bf99de48e669944dfb92b174160e5251a85d03ba8200d121
five tests: passed
```

The command prints these values as JSON. For each lexicographically ordered
rank pair the digest consumes one ASCII JSON line `[B,C,mask,diameter]`, using
compact separators and a trailing newline. Bit `i` of `mask` means that
allocation `i` in the sorted 12-allocation list is EF1. The digest is a
reproducibility aid, not an independent proof of the implementation.

The tests reconstruct ordered partitions by a different method (permuting
labels and cutting between tie blocks). They compare every graph to the
general additive EF1 definition and a direct two-owner-change edge test.
Three rounds of set expansion, separately from the checker's breadth-first
search, reach every vertex from every starting vertex. A separate check
replaces ranks by highly uneven exact rational levels. These checks support
the implementation; the reason they cover all real utilities is the reduction.

## Three swaps are sometimes necessary

Use goods `0,1,2,3`, with B values `(0,0,1,1)` and C values `(1,1,0,0)`.
A may have any nonnegative values. Writing owners of each good as four digits,
the checker returns this path:

```
0102 -> 0120 -> 0210 -> 2010
```

Each arrow exchanges two differently owned goods. Both endpoints and every
intermediate allocation satisfy the displayed inequalities. The endpoints
are not adjacent and have no common EF1 neighbor, so two swaps cannot suffice.
The test verifies that lower bound as well as the three-edge path. The bound
is for all EF1 endpoints; it does not assert that these particular endpoints
are both greedy picking outcomes for a single choice of A's utilities.

## Place in the project

[Frank and Suksompong, section 3 and Proposition 3.4](https://arxiv.org/html/2609.15358v1)
show why an incomplete final round defeats paths restricted to picking
outcomes. They already give an EF1 bridge for their particular strict-ranking
example. This result concerns every utility profile for three agents and four
goods, and every EF1 endpoint of the balanced size vector; it is not a new
claim about their particular bridge. Only that primary paper was checked for
this addition, so priority remains provisional.

The larger project still asks for arbitrary agent counts and numbers of
goods, with greedy picking endpoints and EF1 exchange intermediates.
The all-length two-agent proof and the separate near-complete-final-round
candidate keep their own review status. This finite order-type classification
does not accept either candidate, complete the general milestone or justify
closing the project. It removes the smallest remaining three-agent size case
as a possible counterexample, subject to independent reconstruction.
