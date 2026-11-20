# Almost halving a three-branched tree

Status: published constructions reconstructed; **the general target remains
open in this project**. [PUBLISHED_CASES.md](PUBLISHED_CASES.md) supplies
arbitrary-length proofs, explicit parity and endpoint limits, sources and
provisional priority. No finite census is offered as a theorem.

From a clone of [Emberhall](https://github.com/Someblueman/emberhall), run this
single command at the repository root (Python 3.10+, standard library only):

```sh
python3 projects/almost-halving-three-branches/published_cases.py --demo
```

The command prints seven JSON witnesses, including both vertex sets and every
distance multiplicity, then two expected rejections. Arm numbers are 1–3;
`[0,0]` is the centre, and `[i,d]` is depth d on arm i. Distances are in the
original tree, not an induced subgraph.

Real run, 20 November 2026 (compact transcription; full counts are emitted by
the command):

| Arm lengths | Construction | Equal size | Target | Meets target |
|---|---|---:|---:|---|
| 8, 5, 2 | path | 7 | 7 | yes |
| 9, 7, 4 | alternating | 9 | 9 | yes |
| 9, 7, 5 | alternating | 9 | 10 | no |
| 11, 7, 3 | block | 11 | 10 | yes |
| 13, 7, 3 | block | 11 | 11 | yes |
| 14, 7, 3 | block | 11 | 11 | yes |
| 23, 12, 6 | best supported: path | 18 | 20 | no |

The `(11,7,3)` profile, written `distance: multiplicity`, was
`1:9, 2:7, 3:5, 4:3, 5:3, 6:3, 7:3, 8:4, 9:4, 10:4, 11:4, 12:3, 13:2, 14:1`
for both sets: 55 pairs in each. The final output was:

```text
EXPECTED REJECTION: printed Construction 16 overruns arm: endpoint 19 > 15 (quotient=4, remainder=0)
ALTERED PAIR REJECTED: ... "homometric": false ...
PASS: 7 supported witnesses; printed overrun and altered pair rejected.
```

The altered pair preserves disjointness and cardinality but moves the centre
of a `(10,7,5)` alternating witness to the unused vertex `[1,10]`. For example,
distance 2 then occurs five times on the left and seven times on the right.

Generate another witness with `python3 projects/almost-halving-three-branches/published_cases.py 11 7 3`.
Use `--construction path`, `alternating` or `block` to restrict the formula.
The default chooses the largest supported witness over arm relabelings; it
does not optimize over all subsets. A valid witness below the target exits
successfully and explicitly reports `"meets_target": false`.

To check a proposed pair, put `{"lengths":[a,b,c],"left":[[i,d],...],"right":[[i,d],...]}`
in a JSON file and run `python3 projects/almost-halving-three-branches/published_cases.py --check pair.json`.
`--check -` reads standard input. Exit code 0 means valid and homometric;
exit code 1 means malformed, overlapping, unequal-sized or nonhomometric.
The checker reports both complete profiles and their signed difference.
Duplicate entries are errors rather than silently converted to a set.

Run the implementation checks:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p 'test_*.py' -v
```

Recorded run: 9 tests passed. Their separate breadth-first distance counter
checks implementation, not novelty or the universal target. A non-author's
mathematical review and independent fresh examples are still required.
