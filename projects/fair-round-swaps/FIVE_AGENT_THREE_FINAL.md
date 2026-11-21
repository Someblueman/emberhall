# An obstruction to the three-final side-graph argument

Fern, 20 November 2026. **Exact obstruction, not a counterexample to the
greedy-endpoint question. Independent reconstruction pending.**

The next five-agent case has eight goods and sizes `(2,2,2,1,1)`. Fixing a
favorite good with one singleton leaves four agents and seven goods with
sizes `(2,2,2,1)`. It is tempting to connect arbitrary fair states in this
smaller graph, as in the earlier smaller side lemmas. That statement is
false. The counterexample below also extends to an isolated vertex in the
entire five-agent eight-good graph, and in its favorite-protected subgraph.
Both statements hold even with positive, pairwise distinct utilities in
every row. The isolated vertices have no greedy picking witnesses.

The [frozen model](proof.md) is unchanged: nonnegative additive real
utilities, arbitrary maximizing ties, fixed labeled sizes, and one exchange
of two goods held by different agents. A complete examination of all
exchanges proves isolation here; a sampled census does not carry the claim.
No literature priority is claimed.

## Four agents and seven goods

Agents A, B, C have two goods each; S has one. Use these utilities:

| Agent | a | b | c | d | e | f | t |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 1 | 0 | 2 | 0 | 0 | 2 | 2 |
| B | 2 | 0 | 1 | 0 | 2 | 0 | 2 |
| C | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| S | 0 | 2 | 2 | 0 | 2 | 0 | 1 |

Consider `A={a,b}, B={c,d}, C={e,f}, S={t}`, owner vector `0011223`.
Its own utilities are `(1,1,0,1)`. Every displayed pair contains a
zero-valued good in every observer's row. Deleting the more valuable good
therefore leaves zero. Singleton comparisons are automatic on deletion,
so this allocation is EF1.

There are exactly `C(7,2)-3=18` possible exchanges between different owners.
The table supplies an explicit failure for every one. The last two columns
are the indicated observer's own utility after the swap and the least
utility remaining in the envied bundle after any deletion. Thus every row
has a strict, best-deletion EF1 violation.

| Swap | Observer | Envied owner | Own | After best deletion |
| --- | --- | --- | ---: | ---: |
| a,c | S | A | 1 | 2 |
| a,d | A | B | 0 | 1 |
| a,e | A | C | 0 | 1 |
| a,f | B | C | 1 | 2 |
| a,t | S | A | 0 | 1 |
| b,c | B | A | 0 | 1 |
| b,d | S | B | 1 | 2 |
| b,e | B | A | 1 | 2 |
| b,f | S | C | 1 | 2 |
| b,t | B | A | 1 | 2 |
| c,e | A | C | 1 | 2 |
| c,f | B | C | 0 | 1 |
| c,t | C | B | 0 | 1 |
| d,e | S | B | 1 | 2 |
| d,f | A | B | 1 | 2 |
| d,t | A | B | 1 | 2 |
| e,t | A | C | 1 | 2 |
| f,t | B | C | 1 | 2 |

For instance, exchanging c and t puts `{t,d}` with B. Observer C owns
`{e,f}` of value zero, while both t and d have value one. Either deletion
leaves one. All exchanges are exhausted by the table, proving isolation.

There is another EF1 allocation: the greedy schedule
`S:b, C:t, B:e, A:f | C:d, B:a, A:c` gives owner vector `1302102`.
Each pick maximizes over the then-remaining goods. Thus the full EF1 graph
is disconnected, not merely a single isolated vertex with no other vertices.

## Five agents, eight goods, and a protected favorite

Add good g and singleton agent P. The four old rows give g values
`(2,2,1,3)`, respectively. P's row on `(a,b,c,d,e,f,t,g)` is
`(2,2,2,0,2,0,0,3)`. Keep all old bundles and give g to P, obtaining
`00112234`. Good g is the unique favorite of both S and P.

The old agents remain EF1, because the new bundle is a singleton. P can
delete the entirety of S's bundle; its own value three exceeds any value
remaining in the old pairs. Hence the extension is EF1.

Each of the eighteen old exchanges remains forbidden: its old blocking
observer and pair are unchanged. Only the seven swaps involving g remain:

| Swap | Observer | Envied owner | Own | After best deletion |
| --- | --- | --- | ---: | ---: |
| g,a | S | A | 1 | 2 |
| g,b | B | A | 1 | 2 |
| g,c | C | B | 0 | 1 |
| g,d | A | B | 1 | 2 |
| g,e | A | C | 1 | 2 |
| g,f | B | C | 1 | 2 |
| g,t | P | A | 0 | 2 |

This proves isolation in the **entire** fixed-size graph. In particular it
is isolated in the smaller graph requiring g to stay with S or P. That
protected graph is also nontrivial: the greedy schedule
`S:g, P:b, C:t, B:e, A:f | C:d, B:a, A:c` gives `14021023`, with g still
held by one of its two favorite holders. This disproves connectivity of
the whole protected graph, without claiming separated greedy endpoints.

## The obstruction survives positive strict preferences

Number the columns from zero. In either profile replace each entry v in
column j by `20*v+j+1`. Every entry is positive. Distinct old tiers remain
ordered, and ties within a tier are broken by distinct column indices.

The proposed allocation remains EF1. For A and B its own sum is at least
20, whereas the minimum of any other pair is at most eight: each pair
has an old zero in that observer's row. For C its own sum is `5+6=11`,
again at least every such minimum. S still owns t, worth 27, and every
old pair contains a low good worth at most six. In the extension P owns g,
worth 68, and the minimum of any pair is at most 43. Singleton comparisons
remain automatic.

Every blocking inequality in either table has an old integer gap of at
least one. After multiplying by 20 the gap is at least 20. An observer's
own bundle has at most two goods, so its added column offsets sum to at
most 15; the minimum in the envied pair gains at least one. Thus every
listed strict violation survives. The same tables certify isolation for
the two positive strict profiles, with their adjusted numerical values.

## Why these are not greedy counterexamples

In the four-agent allocation, the following necessary first-round order
constraints form a strict cycle:

* S must pick before A: t is worth two to A, greater than either of A's
  goods. Until S picks, t remains available.
* A must pick before B: a is worth two to B, greater than either of B's
  goods. If a were A's final pick, B could not complete its first pick at all.
* B must pick before S: c is worth two to S, greater than its own t.

These constraints persist in the strict refinement. No recursively balanced
picking witness exists. Removing P and its single good from any putative
five-agent witness would leave a four-agent witness for exactly this
allocation: removing an alternative cannot invalidate a maximizing pick,
and the first round becomes one complete four-agent round. Therefore the
eight-good isolated allocation also has no greedy witness.

## Reproduce the exact checks

Python 3.10+ and the standard library, from the repository root:

```sh
python3 projects/fair-round-swaps/five_agent_three_final.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_five_agent_three_final.py -v
```

The command prints every failed exchange and enumerates every allocation,
all maximizing ties and both round orders. Recorded counts:

| Profile | All states | EF1 states | Component sizes | Greedy outcomes |
| --- | ---: | ---: | --- | ---: |
| Four-agent integer | 630 | 147 | 1,146 | 55 |
| Four-agent positive strict | 630 | 119 | 1,118 | 18 |
| Five-agent integer | 5040 | 791 | 1,790 | 395 |
| Five-agent positive strict | 5040 | 549 | 1,548 | 84 |

All greedy outcomes lie in the larger component for each profile. The
five-agent favorite-protected graphs have respectively 319 vertices in
components `1,318`, and 244 vertices in components `1,243`.

The tests independently try every possible deletion on every fixed-size
allocation and independently enumerate the permutations of both rounds
and every maximizing tie. They check every exchange, the strict refinement,
invalid claims of isolation, and the real command's output. The tables
prove the fixed obstructions; the component census only describes these
four fixed profiles. It is not a universal theorem about component counts.

## Next obligation

This rules out two tempting premises for the three-final induction: full
connectivity of the four-agent seven-good side graph, and full connectivity
of the five-agent favorite-protected graph. A valid proof must identify and
connect the particular components containing its constructed braid states,
or use an endpoint-specific bridge. Existing greedy-endpoint theorems do
not turn arbitrary intermediate states into greedy ones. The separate
eight-good builder owns that bridge. Nothing here decides all eight-good
greedy endpoints, the `5q+3` lift, or the general milestone.
