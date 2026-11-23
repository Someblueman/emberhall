# Almost halving a three-branched tree

Status: published constructions reconstructed; optimal pairs proved for
`(10t,7t,4t)` for all `t>=2`, `(7t,5t,3t)` for every positive t, and every arithmetic-progression triple
`(b+d,b,b-d)` for every integer `b>=2` and `1<=d<b`, including all arm
relabelings. Full partitions of arithmetic-progression triples are classified;
when a full partition is impossible, the command attains the half-minus-one target.
**The general target remains open in this project.**
[PUBLISHED_CASES.md](PUBLISHED_CASES.md) retains the earlier constructions and
sources. [NEXT_FAMILY.md](NEXT_FAMILY.md),
[PROGRESSION_TARGET.md](PROGRESSION_TARGET.md), and
[PROGRESSION_PARTITIONS.md](PROGRESSION_PARTITIONS.md) prove the extensions;
[ODD_MIDDLE.md](ODD_MIDDLE.md) closes the odd scales of `(7t,5t,3t)`.
[NEXT_ODD_FAMILY.md](NEXT_ODD_FAMILY.md) covers odd middle lengths with even
spacing, and [MIDDLE_PREFIX.md](MIDDLE_PREFIX.md) covers odd spacing. The
specialized formulas in [ODD_SPACING.md](ODD_SPACING.md) and
[GENERAL_ODD_SPACING.md](GENERAL_ODD_SPACING.md) are also selected within
their stated domains; no bounded search runs in the default command.
[ARITHMETIC_FAMILY.md](ARITHMETIC_FAMILY.md) records a separate `(11t,8t,5t)`
construction, now covered by the even-middle result. Independent mathematical
review is pending and [priority remains provisional](PRIORITY_REFRESH.md).

From a clone of [Emberhall](https://github.com/Someblueman/emberhall), run this
single command at the repository root (Python 3.10+, standard library only):

```sh
python3 projects/almost-halving-three-branches/published_cases.py 110 77 44
```

The command prints a JSON witness with two disjoint sets of size 115, both
complete distance profiles, target 115 and certified upper bound 115.
Arm numbers are 1–3;
`[0,0]` is the centre, and `[i,d]` is depth d on arm i. Distances are in the
original tree, not an induced subgraph.

Current real default-command runs, 21 November 2026:

| Arm lengths | Size | Target | Upper bound | Meets target |
|---|---:|---:|---:|---|
| 110,77,44 | 115 | 115 | 115 | yes |
| 137,100,63 | 150 | 149 | 150 | yes |
| 12,9,6 | 14 | 13 | 14 | yes |
| 16,13,10 | 19 | 19 | 19 | yes |
| 133,95,57 | 142 | 142 | 142 | yes |
| 43,31,19 | 46 | 46 | 46 | yes |
| 19,11,3 | 16 | 16 | 16 | yes |
| 40,23,6 | 34 | 34 | 34 | yes |
| 54,47,40 | 70 | 70 | 70 | yes |
| 50,33,9 | 43 | 45 | 46 | no |

The last row is an explicit remaining gap, not a counterexample. The command
searches the proved construction menu, not all subsets. [GAP_99_79_23.md](GAP_99_79_23.md) closes the separate one-short triple (99,79,23): size 100 is attained and optimal there, and T(99t,79t,23t) attains its target at every scale except the open class t ≡ 1 (mod 2660), t > 1 (`gap_99_79_23.py --witness 1`, recorded 23 November 2026). To replay the original
seven published-case examples and two expected rejections, use `--demo`.

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
| 23, 12, 6 | printed path baseline | 18 | 20 | no |

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
Use `--construction path`, `separated-path`, `alternating` or `block` to
restrict the formula. The default chooses the largest supported witness,
including the new family and arithmetic-progression constructions, over arm relabelings; it
also tries the 20 prefix subtrees obtained by deleting at most three arm tips.
Their distances are unchanged; any trimming is labelled in the output.
It does not optimize over all subsets. A valid witness below the target exits
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

Recorded run, 21 November 2026: 74 tests passed. Their separate breadth-first distance counter
checks implementation; exact Laurent-polynomial identities verify the
family formulas for symbolic lengths. Neither establishes novelty or the
universal target. A non-author's review is still required.

The new family has a separate command, so it cannot be mistaken for a
repaired published construction:

```sh
python3 projects/almost-halving-three-branches/published_cases.py --gap-family 6
```

Recorded run, 20 November 2026: lengths `[23,12,6]`, two disjoint sets of size
21 (all 42 vertices), identical distance profiles, `"meets_target": true`.
The common profile begins `1:13, 2:8, 3:10, 4:8` and totals 210 pairs.
For comparison, the published-formula command above gives only size 18 on
the same tree. The new command prints all vertices and all multiplicities.
For odd t it omits the longest-arm tip and returns size `floor(7t/2)`;
`--gap-family 5` returned two sets of size 17 with one omitted vertex.
Pass either output through `--check -` for the independent input-validation
path. The proof concerns this infinite family, not all three-branched trees.

The output also reports a certified `upper_bound`. It uses disjointness and,
where applicable, the proved residue or arithmetic-progression obstruction to a full partition. A
valid witness with `attains_bound: true` is therefore optimal for that tree.
Failure to attain this bound proves nothing about whether a better pair
exists. Equal odd arms attain exactly the project's half-minus-one target;
the proof rules out full halves for every such arm length.
Recorded runs: `11 7 5` chose separated paths of size 11 and certified upper
bound 11; `3 3 3` chose alternating sets of size 4 and certified upper bound 4.
Both reported `attains_bound: true`.

The second unequal-arm family has a separate command:

```sh
python3 projects/almost-halving-three-branches/published_cases.py --sharp-family 8
```

Recorded run: `[31,23,15]`, size 34 in each set, equal profiles containing
561 distances each, two omitted vertices, certified upper bound 34.
`attains_bound: true`. The proof rules out all larger pairs on this family,
not just larger outputs of the implemented constructions.

Another recorded run, `python3 projects/almost-halving-three-branches/published_cases.py 29 17 6`,
selected `trim (0, 1, 0): block(1, 2, 3)` and returned size 26, target 25,
upper bound 26 and `attains_bound: true`. This uses a valid construction on
`(29,16,6)`, not a repair of the source's invalid even-quotient formula.

The former gap `T(10t,7t,4t)` is now resolved by the proof in NEXT_FAMILY.md:
the optimum is `floor(21t/2)` for all `t>=2`. Its old menu-only bound of
`10t+3` remains a correct historical limitation of the earlier formulas.
The default command now uses the stronger result; explicit published modes
still use their original formulas. Arbitrary triples remain unresolved;
arithmetic-progression triples are now covered by the normal command.
