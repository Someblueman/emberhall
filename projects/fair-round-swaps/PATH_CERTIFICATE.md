# Independently check a saved fair-exchange path

`verify_path.py` checks one finite path using exact rational arithmetic. It is
a standalone standard-library program: copy that single file and the JSON
input/output to another directory or machine. It imports neither the path
constructor nor the shared allocation model.

With the separately supplied general command and its prerequisites installed:

```sh
python3 -S projects/fair-round-swaps/general_construct.py projects/fair-round-swaps/general_example.json > /tmp/fair-path.json
python3 -I -S projects/fair-round-swaps/verify_path.py projects/fair-round-swaps/general_example.json /tmp/fair-path.json
```

The verifier returns JSON with `valid: true` only after checking:

- both complete endpoint picking orders, including every maximizing choice,
  round schedule, good label and final recipient;
- every allocation's labelled bundle sizes and every EF1 inequality;
- every transition as an exchange of exactly two differently owned goods;
- the supplied `exchanges` list, if present, against the actual owner changes.

For EF1 it literally tries removing each good from each target bundle and sums
the remaining utilities. It does not use the constructor's largest-item
formula, singleton/pair shortcuts or acceptance flag. Empty bundles are
handled directly. Greediness is required only of the two input witnesses.
Intermediate allocations need not have picking witnesses.

## Input and claims

The first file has exactly `utilities`, `final_recipients`, `start` and `target`,
with the same schema as [the general command](GENERAL_INPUT.md). Agents and
goods use integer labels starting at zero. There must be at least two agents
and one good. Utilities are nonnegative JSON integers or exact rational strings
such as `"2/7"` or `"0.125"`; floating-point JSON values and booleans are
rejected. Zeros, ties, arbitrary permutations of labels, no complete round and
an empty final round are supported. Final-recipient list order is immaterial.

The second file is an object with a nonempty `owners` list. Each vector gives
one owner per good, in good-label order. An optional `exchanges` list must give
exactly one object per transition, with precisely `goods` and `agents`, both
two-element integer lists. The agents own the corresponding goods **before**
the exchange. Either ordering of the two goods is accepted if the agents are
ordered consistently. The verifier's output uses ascending good labels.

Other output fields such as `verified`, `scope`, `swaps` and `sizes` are
untrusted annotations. They are ignored; counts, sizes and trades in the
verifier's result are recomputed. An explicit trade list is checked, not
silently replaced. Omitting it still checks all transitions from owner vectors.
Malformed input exits with status 2, a diagnostic on standard error and no
success JSON. Duplicate JSON keys and nonfinite JSON constants are rejected.

One file may instead contain exactly `{"instance": INPUT, "path": OUTPUT}`.
Then omit the second argument. For a standalone example, save this as
`/tmp/fair-certificate.json`:

```json
{
  "instance": {
    "utilities": [[0,100,0,0], [30,0,11,10], [30,0,10,11]],
    "final_recipients": [0],
    "start": [[1,0], [0,1], [2,3], [0,2]],
    "target": [[2,0], [0,1], [1,2], [0,3]]
  },
  "path": {
    "owners": [[1,0,0,2], [0,0,1,2], [2,0,1,0]],
    "exchanges": [
      {"goods": [0,2], "agents": [1,0]},
      {"goods": [0,3], "agents": [0,2]}
    ]
  }
}
```

```sh
python3 -I -S projects/fair-round-swaps/verify_path.py /tmp/fair-certificate.json
```

Recorded result: valid, 3 agents, 4 goods, 3 allocations, 2 swaps, sizes
`[2,1,1]`. The middle division is not a balanced greedy outcome: agent 0 must
pick good 1 first, and both singleton agents would take good 0 before agent 0's
final turn. The verifier correctly accepts that fair intermediate division.

## Verification and scope

```sh
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_verify_path.py -v
```

Recorded on 20 November 2026: all nine tests passed. Real subprocess tests copy
only `verify_path.py`, use `-I -S`, and check both file formats, failure exits
and duplicate-key refusal. Other cases cover exact rational gaps below floating
precision, zero and tied rows, empty recipients, triple bundles, wrong endpoint
owners, missing/extra goods, bad schedules, unfair states, repeated states,
three-owner cycles and inconsistent trade logs.

Separate end-to-end runs used the frozen general command at
`06f49ee8081c0074cca4fbf56cce5345da434b85`, Fern's general constructor at
`9144cb5962c73fd2ab2a648baec4f44913b68a07`, the recovered one-round modules at
`c471b9c8fe76cf9f9b300f3ff66892d7f13eda04`, and the one-anchor core at
`580ebf551f9f87bfb751b119540585aa7e17db8c`. `near_complete.py` and `swaps.py`
came from baseline `b7e23b459ed3a71fe4c4c80d2bda0dcc11a2ca77`. These are validation
dependencies only; the verifier itself needs none of them.

All seven generated paths passed isolated checking. Agent labels were reversed
and utilities divided exactly by seven in each run:

| Agents | Complete rounds | Final recipients | Allocations | Swaps |
| --- | --- | --- | --- | --- |
| 4 | 0 | 2 | 2 | 1 |
| 3 | 1 | 0 | 2 | 1 |
| 4 | 2 | 0 | 2 | 1 |
| 5 | 2 | 1 | 3 | 2 |
| 4 | 1 | 3 | 4 | 3 |
| 8 | 2 | 5 | 19 | 18 |
| 9 | 3 | 5 | 39 | 38 |

This checks those supplied paths. It neither reconstructs the universal
endpoint theorem nor proves connectivity of the entire EF1 graph. It makes no
shortest-path claim. It checks exact rational utilities; a claim about all real
utilities requires the mathematical proof. File sizes and running time are
not bounded by this program; checking a large certificate costs proportionally
more work, but never invokes recursive path construction or graph search.
