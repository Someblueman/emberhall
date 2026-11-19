# Fair division on a path of ten chores

Three people disagree about the cost of doing chores. Each chore conflicts with its immediate neighbors, so one person cannot take two consecutive chores. For any path of up to ten chores, there is a way to assign them all so that each person, after hypothetically setting aside at most one of their own chores, values their remaining burden at or below anyone else's. The result includes costs that depend on which chores are bundled together. [Read the proof and its assumptions](proof.md).

From the repository root, using Python 3.10 or later, run

```sh
python3 projects/fair-ten-chores/check.py
```

Recorded output

```text
1536 assignments, 20616 exchanges, 53004 triangles
1535 tree edges, 19081 signed reductions, 0 unproved generators
The allocation complex is connected and simply connected.
```

To keep the proof steps and replay them in a fresh process, choose a destination for the certificate.

```sh
python3 projects/fair-ten-chores/check.py --write-certificate /tmp/ten-chores.json
python3 projects/fair-ten-chores/check.py --verify /tmp/ten-chores.json
```

Replay reconstructs the legal assignments and all exchanges, then checks the supplied tree and each signed triangle in order. The JSON lists the words, the edges between their zero-based indices, the tree's one-based edge numbers and the signed triangle boundaries. A positive edge number traverses its endpoints in ascending order. A negative number traverses them backwards.

The published seven-vertex counterexample can be tried with `--obstruction`. It produces zero complete fair assignments and exits with status 1 because its triangle evidence leaves 42 generators unproved. To reproduce the mutation tests, run

```sh
python3 -m unittest discover -s projects/fair-ten-chores -p test_check.py
```
