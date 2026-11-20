# Four agents and one final extra good

Theorem by Sorrel, 20 November 2026. **Aster independently reconstructed the
mathematical argument at journal 23698.** Source integration of this run remains
separate. All utilities below are additive nonnegative reals; maximizing ties
are arbitrary. This is a size-family result, without a priority claim.

**Theorem.** For four agents and `4q+1` goods, q>=1, any two greedy recursively
balanced outcomes with the same doubled recipient D admit a single-exchange
EF1 path. Intermediate allocations may be non-greedy.

Together with the separate `4q+2` theorem in
[FOUR_AGENT_LIFT.md](FOUR_AGENT_LIFT.md) and the near-complete `4q+3` theorem
in [FRONTIER.md](FRONTIER.md), this covers every incomplete final round
for four agents. It does not settle five or more agents, and it does not
claim that every EF1 allocation of these sizes is a greedy endpoint.

## 1. A protected five-good bridge

There are five goods, one double recipient D and three singleton recipients.
Fix two singleton agents i,j who both rank g as a favorite. The EF1 subgraph
in which g belongs to i or j is connected, including every fair state in
that subgraph, whether or not it is greedy.

For a fixed holder of g, remove that holder and g. The remaining graph has
three agents and four goods of sizes (2,1,1). Its entire EF1 graph is connected
by the direct proof in [FOUR_GOODS.md](FOUR_GOODS.md). Briefly, a singleton
holding a top-two good is always safe; any fair state is at most one exchange
from a state with both singletons safe, and safe states connect by giving
the singletons their target safe goods. Adding the global favorite g back
preserves fairness.

It remains to connect the two holders. Among the other four goods each
carrier has at least three goods with at most two strictly better goods.
The two sets intersect. Choose t in their intersection with no good strictly
better for both: repeatedly improving both values remains in the intersection
and terminates. The strict upper sets of t for i,j are disjoint and have at
most two elements each. They lie in a set of three remaining goods, so at
most one can have two elements.

Give t to the other carrier. Of the three remaining goods, give a pair to D
and one to the third singleton h. There are three possible pair choices.
The carriers can forbid at most one: the pair of two goods strictly above t
for one carrier. Agent h can forbid at most one: it fails EF1 only when its
own good is strictly below both others, and only one of three goods can have
that property. D has only singleton bundles to compare with and cannot fail.
At least one pair choice therefore works with g,t assigned either way.
Exchange g,t to cross, proving the assertion.

This proof gives a finite constructor by searching at most 24 states.
`carrier_path` does so, with the protected carriers explicitly named.

## 2. The five-good greedy base case

For completeness this specializes the one-extra-good induction, without
assuming that all four-agent five-good EF1 states are connected.

If a singleton holds a favorite g as the first pick, remove it and g. The
three-agent four-good graph is connected and its paths lift: the fixed
singleton holds a global favorite, and everyone else can delete its bundle.
Thus each singleton-first class is connected.

Fix D's first good k and partition those outcomes by the second pick i:h.
Since h maximizes i's value among all goods except k, any path after removing
i,h lifts: D's pair contains at most one k, and its other good is no better
than h for i. The remaining three-agent four-good graph is connected. This
connects each second-pick class in the ambient EF1 graph; it need not keep k
fixed along its internal path.

Distinct second agents with different favorites commute their picks. If i,j
share favorite h, let the other singleton pick its favorite l identically
after D:k and the first h. Two goods x,y remain. Equal last choices give one
exchange. Otherwise the endpoints have the form

`A=(D:{k,x}, i:{h}, j:{y}, other:{l})`,

`B=(D:{k,y}, i:{x}, j:{h}, other:{l})`.

Both carriers rank h above x,y, and the fixed other singleton ranks l above
x,y. Try exchanging h,y in A, then x,y; or try x,y first, then h,x. The only
possible failed comparison in the first trial is i against D, and in the
second it is j against D. If both fail, then

`u_i(y)<min(u_i(k),u_i(x))`,

`u_j(x)<min(u_j(k),u_j(y))`.

Use instead

`A -> (D:{x,y}, i:{h}, j:{k}, other:{l})`

`  -> (D:{x,y}, i:{k}, j:{h}, other:{l}) -> B`.

The inequalities make the holder of k safe; h is safe for either carrier;
the fixed observer dominates both goods in D's pair. None of these paths
puts k,h together with D. This proves the shared-favorite second-pick bridge.
Tied choices of the same second agent connect through another singleton's
favorite class. Hence the D-first class is connected.

Finally join first-pick classes. Different favorite goods commute. Two
singleton first agents with the same favorite connect by Section 1. If D
and a singleton share favorite g, let the other two singletons pick identically
after g is removed. The last two goods are x,y. In the D-first run let the
carrier singleton take its favorite x, leaving y for D. In the singleton-first
run D gets both x,y. These endpoints differ only by exchanging g,x and are
greedy. Same-agent ties connect through another first-agent class. This
proves the q=1 base case.

## 3. Padding and the arbitrary-round induction

The padding lemma in [FOUR_AGENT_LIFT.md](FOUR_AGENT_LIFT.md) works verbatim
with five tail goods instead of six. Its hypotheses are: r common complete
greedy rounds with g omitted, and every agent values its own common bundle
at least the common bundle of either protected carrier. If a fair tail
keeps g with i or j, the full allocation is fair.

For the carrier holding g, delete g and use the common-bundle comparison.
For every other target bundle, delete its first common-prefix good, shift-match
the other prefix picks, and use the last own prefix good to pay for the largest
tail good. That largest tail good is not g and was available to the entire
common greedy prefix. Tail EF1 pays for the remainder. With an empty prefix,
the assertion is just tail EF1.

Induct on q, using Section 2 at q=1. For q>=2 use a second backwards induction
over a fixed first-round prefix. At a complete first round, remove it and
apply q-1, then put it back using ordinary greedy-round lifting. Within a
next-pick class, extend the fixed prefix and apply the inner induction.

Different next agents with different favorites commute. For a shared favorite,
run the usual braid: the other eligible agents choose identically between
the two carriers; in later rounds each carrier first takes its previous
unmatched good, then common picks occur and the opposite carrier picks last.
Equality of those last picks closes in one exchange. If a carrier is D,
let it absorb the unmatched final good; again one exchange closes the runs.

The only case left has two singleton carriers. Let h be the remaining
singleton. Their common picks in complete round t are k_t for D and l_t for
h; the two last choices from the common pool are x_t,y_t. If the braid has
not already closed, the final disagreement lies in

`g, k_q, l_q, x_q, y_q`.

All other goods agree. For t<q, group k_t,l_t,x_t,y_t as a common complete
round with g omitted, retaining the original order of D,h and then choosing
x_t,y_t. Both carrier choices maximize on the common pool before either is
removed, so this is greedy. Every agent's common good dominates either
carrier's common good in that agent's valuation: D,h picked earlier and
the carriers both maximized on the same pool. Summing gives the padding
hypotheses. Section 1 supplies the protected five-good path and padding lifts
it to the full allocation.

Because q>=2, all goods in the originally fixed first-round prefix are among
the common bundles, which never move. Only D,h can occur in that prefix
before the two singleton carriers, so the reconstruction preserves its
original order. Same-agent tied choices connect through another eligible
agent, or, at the last first-round pick, by taking both tied goods across
the next round boundary in opposite orders. That complete next round exists
for q>=2. The two inductions therefore close.

## Computation

From the repository root, Python 3.10+ and the standard library:

```sh
python3 projects/fair-round-swaps/four_agent_one_final.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_four_agent_one_final.py -v
```

The demonstration prints

```
10302 -> 12300 -> 21300 -> 20310
```

Each step is one EF1 exchange, with g remaining with a carrier. The module
also exposes `padded_path` for a checked common prefix of any length, and
`path` for fully greedy endpoints with final recipient 0. The latter now uses
the same round/prefix induction engine as the two-final-recipient constructor.
Only its five-good base case and protected bridge use graph searches, on at
most 60 and 24 states respectively. No shortest-path or polynomial-complexity
bound is claimed. Sections 1–3 supply the arbitrary-length argument.

The tests use independent deletion checks, arbitrary cardinal utilities and
ties, every protected carrier pair, real greedy endpoint witnesses and longer
padded braids. No external solver or new dependency is used by this code.
The mathematical reconstruction covers the argument; the later shared-engine
implementation still needs the ordinary independent source integration.
