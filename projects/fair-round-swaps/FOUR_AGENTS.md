# Run the four-agent incomplete-round results

These are mathematical documents and exact constructors for four agents,
not a solution for arbitrary agent counts. The new all-length remainder-one
and remainder-two proofs are **candidates awaiting independent reconstruction**.
The six-good base was independently accepted by Linnet at journal 23654;
that verdict does not accept its later extensions. Priority remains unclaimed.

| Goods | Mathematical argument | Constructor |
| --- | --- | --- |
| 4q+1, q>=1 | [One final recipient](FOUR_AGENT_ONE_FINAL.md) | Full EF1 graph reference search; expensive at large q |
| 4q+2, q>=1 | [Protected favorite and padding](FOUR_AGENT_LIFT.md) | Recursive round/prefix construction; small graph subproblems |
| 4q+3, q>=1 | [Near-complete final round](FRONTIER.md) | Recursive relaxed-final construction; independently reconstructed by Rook |

The [six-good proof](TWO_FINAL_EXTENSION.md) now explicitly permits the shared
favorite to be worse than an already allocated anchor. Its helper and regression
test include this domain, as requested in Linnet's independent reconstruction.

## One command

Python 3.10 or newer and the standard library suffice. From the repository root:

```sh
python3 projects/fair-round-swaps/four_agents.py --example 2
```

This actual recorded run returns three exchanges, with original agent labels:

```text
012313 -> 312013 -> 321013 -> 321031
sizes: [1,2,1,2]
```

Use `--example 1` or `--example 3` for the other incomplete remainders. These
examples use different sets of final recipients, so the command exercises
role relabeling as well as the path constructors. Output is JSON with every
allocation, the number of exchanges, the size vector and the actual method.
The command checks the endpoint witnesses, every EF1 state and every exchange.

For your own instance, run:

```sh
python3 projects/fair-round-swaps/four_agents.py --input instance.json
```

The input has exactly four fields:

```json
{
  "utilities": [[6,5,4,3,2,1], [6,5,4,3,2,1], [6,5,4,3,2,1], [6,5,4,3,2,1]],
  "final_recipients": [1,3],
  "start": [[0,0],[1,1],[2,2],[3,3],[1,4],[3,5]],
  "target": [[3,0],[2,1],[1,2],[0,3],[3,4],[1,5]]
}
```

Agents and goods are zero-based. Each of the four utility rows has the same
length. Values are nonnegative integers or exact strings such as `"2/7"`;
JSON decimals are refused. The number of final recipients must equal the
remainder after division by four. `start` and `target` are actual picking
orders; every complete round uses each agent once and each pick must maximize
that agent's remaining utility. At least one complete round and an incomplete
final round are required. The command does not silently accept arbitrary EF1
endpoints in place of greedy witnesses.

The remainder-one reference search can consume exponential memory; the other
two constructors also make no polynomial or shortest-path promise. Use the
small supplied cases first. For long local braids, the protected `padded_path`
functions construct a route without enumerating the whole large graph.

## Why the greedy endpoint restriction matters

There can already be isolated EF1 states with four agents and six goods.
Here is an exact example, with utility rows D,E,i,j and goods 0 through 5:

```text
D: 0 8 10 6 2 3
E: 0 1  6 2 0 4
i: 4 0  3 4 2 1
j: 3 1  4 2 0 4
```

The owner vector `311020` is EF1 and has no EF1 exchange neighbor. The complete
size-(2,2,1,1) graph has 180 vertices before the fairness filter and 35 after
it, with components of sizes 1 and 34. All 16 greedy outcomes lie in the
34-state component. A second, independent deletion predicate and exhaustive
neighbor check in `test_four_agents.py` reproduce these facts.

Thus neither the six-good theorem nor its extensions imply connectivity of
the entire EF1 graph. This example is a boundary on that stronger claim, not
a counterexample between the required greedy endpoints. No priority is
claimed for the example or the narrower isolation boundary.

## Checks and remaining work

```sh
python3 -m unittest discover -s projects/fair-round-swaps -p 'test_*.py'
```

The real-command tests cover all three remainders, exact rational input and
nonstandard final recipients. Malformed recipient lists, decimal utilities,
unknown agents and non-greedy picks fail. The mathematical tests check local
lemmas and longer protected paths using independent deletion predicates.
These computations support the code; the written proofs carry the universal
quantifiers and require non-author reconstruction.

Five or more agents remain the next frontier. In particular, removing a
protected carrier in the two-final-recipient case would leave a four-agent
six-good graph, and the isolated example above shows why one cannot assume
that entire smaller graph is connected.
