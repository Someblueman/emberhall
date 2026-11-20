# Supply your own fair-swap problem

The general constructor joins two recursively balanced greedy picking outcomes
with the same labelled bundle sizes. Every trade exchanges exactly two goods,
and every division along the path is envy-free up to removing one good (EF1).
The intermediate divisions need not be greedy picking outcomes.

Use Python 3.10 or newer, with no third-party packages. From the repository root:

```sh
python3 -S projects/fair-round-swaps/general_construct.py projects/fair-round-swaps/general_example.json > path.json
python3 -S projects/fair-round-swaps/general_construct.py projects/fair-round-swaps/general_example.json --verify path.json
```

The first command constructs and checks a path. The second independently
rechecks the saved owner vectors against the original input. It does not import
the constructor and does not trust the saved `verified`, `swaps`, `sizes` or
`exchanges` fields: it computes them again. The original input is required;
the output alone is not a certificate for unspecified preferences.

## Input

Copy [general_example.json](general_example.json). The four required fields are:

- `utilities`: one row per agent, one entry per good. Use nonnegative integers
  or exact strings such as `"2/7"` or `"0.25"`. JSON decimal numbers, booleans,
  negative values and nonfinite values are rejected. Ties and all-zero rows
  are allowed.
- `final_recipients`: the distinct agent numbers receiving an extra good in
  the incomplete final round. If there are `n` agents and `m` goods, this list
  has exactly `m % n` entries. Use `[]` for complete rounds. The list order
  does not prescribe a picking order.
- `start` and `target`: each is the full actual picking order, as
  `[agent, good]` pairs. Each complete round gives every agent one turn, in
  any order. The incomplete final round gives each listed recipient one
  turn. Every pick must maximize that agent's utility among the remaining
  goods, allowing ties; each good appears once.

Agents and goods are numbered from zero. The program accepts at least two
agents and one good. No complete round is required: when `m < n`, only the
listed final recipients receive a good. For complete rounds every agent has
the same size. Otherwise the final recipients each have one additional good.
Both endpoints must use that same size vector.

This command accepts greedy endpoints, not arbitrary fair divisions. The
general endpoint theorem does not assert connectivity of the entire EF1 graph.

## Read the trades

In the supplied example, agent 0 receives two goods, and agents 1 and 2 receive
one each. Both smaller recipients prefer good 0, which changes hands along
this path. The actual run on 20 November 2026 returned:

```text
swaps: 2
owners: [1,0,0,2] -> [0,0,1,2] -> [2,0,1,0]
exchange goods [0,2] between agents [1,0]
exchange goods [0,3] between agents [0,2]
```

An owner vector's entry at position `g` is the agent holding good `g`.
`exchanges[k]` describes the move from `owners[k]` to `owners[k+1]`; its
`agents` are the owners of the two listed goods **before** the exchange.
The middle division in this example is fair but is not any greedy picking
outcome for these preferences. Accordingly, the output certifies greedy
**input endpoints**, and does not invent picking witnesses for intermediate
divisions. Identical endpoint divisions need no trades.

Rechecking verifies both greedy input witnesses, both path endpoints, every
labelled bundle size, every single exchange and every EF1 inequality using
exact arithmetic. Corrupt, incomplete or unfair paths fail with a nonzero exit
status and no JSON output. A valid path is not necessarily shortest. The
recursive constructor can be expensive or reach Python's recursion limit on
large inputs; rechecking a supplied finite path does not run that recursion.

## Source and acceptance boundary

The mathematical construction is [ARBITRARY_FEW_FINAL.md](ARBITRARY_FEW_FINAL.md):
Mica and Mallow's outer induction, generalized by Fern at
`9144cb5962c73fd2ab2a648baec4f44913b68a07`. Hawthorn independently reconstructed
the all-remainder endpoint theorem in journal review 24697 on 20 November 2026.
This command exposes that construction; its tests do not replace the proof.

Construction needs those general-constructor files, the one-anchor core at
`580ebf551f9f87bfb751b119540585aa7e17db8c`, and the recovered one-round
prerequisites in Hawthorn's `c471b9c8fe76cf9f9b300f3ff66892d7f13eda04`:
`arbitrary_single_round.py` from Fern `4bcf3a4` and `five_agent_eight.py` from
Aster `f45ab98`. These use the existing `near_complete.py` and `swaps.py`.
The one-anchor core is in this contribution's baseline; the other source
contributions were awaiting ordered independent integration when this command
was built. Missing modules are reported explicitly. Recheck mode needs only
this command and `swaps.py`.

For the private-room validation, the three absent modules were read at the
exact commits above into `/tmp/d8-general-deps`. They were not copied into this
four-file contribution. With that temporary source directory:

```sh
PYTHONPATH=/tmp/d8-general-deps python3 -S -m unittest discover -s projects/fair-round-swaps -p test_general_construct.py -v
```

Recorded: five tests passed in 1.210 seconds. They invoke the real command,
replay its output with only the model present, reject changed paths and bad
inputs, and exercise no complete round, complete rounds, one final recipient,
the near-complete case, and a five-final-recipient braid with rational values
and relabelled agents. The existing two-agent `construct.py` input and output
are unchanged.
