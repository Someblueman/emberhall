# Three Runs of Stamps

For $k\ge2$, the crease pattern `M^k V^k M^k` has
$(9k^3-25k^2+30k-12)/2$ legal labeled stacks in the fixed orientation.
The [author proof](cubic.md) partitions every stack by the first adjacent
valley after step one. Tern’s [independent reconstruction of the full argument](CUBIC_RECONSTRUCTION.md)
accepts the count for every integer $k\ge2$ in this model, including the
fourth-stop induction and the terminal boundaries. This is a reconstruction
after reading the authors, not an independent discovery. **Literature priority
and overlap remain unresolved.**

Read the [proof](cubic.md), follow the [independent reconstruction](CUBIC_RECONSTRUCTION.md),
or run the [standalone checker](cubic.py). The reconstruction includes a small
Python calculation that imports none of the author’s modules. The proof’s
opening review-status sentence predates that completed reconstruction.

From the repository root of a [clone of Emberhall](https://github.com/Someblueman/emberhall),
with Python 3.10 or newer and no dependencies, reproduce the count and compare
every sector with unpruned enumeration:

```sh
python3 projects/three-runs-of-stamps/cubic.py 8 --verify
```

Recorded again from the complete source on 20 November 2026:

```text
$ python3 projects/three-runs-of-stamps/cubic.py 8 --verify
M^8 V^8 M^8
First adjacent valley after step one: 2 | 75
First adjacent valley after step one: 3 | 98
First adjacent valley after step one: 4 | 141
First adjacent valley after step one: 5 | 196
First adjacent valley after step one: 6 | 263
First adjacent valley after step one: 7 | 342
First adjacent valley after step one: 8 | 285
First adjacent valley after step one: never | 218
1618 legal labeled stacks
Every sector agrees with unpruned enumeration.
```

More checks from the same repository root:

```sh
python3 projects/three-runs-of-stamps/count.py --k 2 --list
python3 projects/three-runs-of-stamps/count.py --k 2 --draw
python3 projects/three-runs-of-stamps/count.py --k 4 --family --list
python3 projects/three-runs-of-stamps/count.py --k 4 --nested-family
python3 projects/three-runs-of-stamps/count.py --k 4 --first-valley-family
python3 -m unittest discover -s projects/three-runs-of-stamps -v
```

`--draw` gives terminal arc charts for the actual enumerated stacks, rather
than an unrelated illustration. Read a crease's two endpoints in the printed
layer row: even-numbered creases go above it, odd-numbered below. Each arc has
its own row for readability; nesting and crossing are determined by endpoint
order, not by the drawn row height. M/V and the crease number label every arc.
This is a combinatorial drawing, not a simulation of physical paper motion.

## The model

The convention is Definition 2.1 of [Hull, Ibrahim, Paltrowitz, Ter-Saakov and
Wang, published paper](https://dmtcs.episciences.org/en/articles/15454/download)
(2025), pp. 2–3. Face zero's labeled side faces right. Even labels also face
right, odd labels left. A stack is the list of labels **from left to right**;
it is not the label-to-position map in the paper's inequalities.

Let `p[i]` be the position of face i in that list. Crease i joins i to i+1.
For even i, M requires `p[i] > p[i+1]`, and V requires `<`.
For odd i these inequalities reverse. Even creases lie above the line; odd
creases below it. For any two creases on the same side, their endpoint
intervals must be disjoint or nested. Strict endpoint interleaving is illegal.
No rotation, reversal or relabeling is quotiented out. Reflecting the layer
list swaps M and V in this fixed convention; it is not another stack for the
same assignment. Empty assignment means the single face `(0,)`.

These are idealized flat stacks with elastic joins, not rigid-unit motions.
[Sawada and Li](https://www.cis.uoguelph.ca/~sawada/papers/stamp2.pdf) discuss
that model and fast generation. Our original implementation uses simple
insertion, not their optimized algorithm or downloaded code.

## Exactness and controls

Start with face zero. Insert each new largest label into every gap consistent
with its required direction, rejecting crossings with older creases on the
same side. Old arcs and their relative orders remain unchanged. Deleting the
largest label from any legal stack leaves a legal prefix (the paper's
Lemma 2.3); thus this search is exhaustive and visits each stack once.
It uses exact integer positions, with no geometric tolerance or floating point.
It streams final results, though time grows with all valid prefixes and gaps;
this is a small-case tool, not a claim of practical enumeration at k=78.

`violations` checks a complete stack directly. The tests use a further,
separate permutation predicate based on directed pairs and interval membership.
They compare *all* M/V assignments through six faces and all 5,040 permutations
for the seven-face control. They also test nesting, disjoint arcs, a pure
crossing rejection, reflection, input errors and the actual command line.

Recorded local run, 19 November 2026:

```
$ python3 projects/three-runs-of-stamps/count.py --k 2 --list
1: 5 6 4 1 2 3 0
2: 5 4 1 2 3 6 0
3: 5 4 1 2 3 0 6
4: 1 2 5 6 4 3 0
5: 1 2 5 4 3 6 0
6: 1 2 5 4 3 0 6
7: 5 6 4 1 0 2 3
8: 5 4 1 0 2 3 6
9: 1 0 2 5 6 4 3
10: 1 0 2 5 4 3 6
MMVVMM: 10 legal labeled stacks
published conjecture: 10
```

A rejected candidate is `1 0 2 5 4 6 3`. It obeys **every** M/V inequality,
but its bottom creases `(3,4)` and `(5,6)` interleave: their sorted positional
intervals are `[4,6]` and `[3,5]`. It fails only the crossing condition.
For an orientation control, M on two faces allows `(1,0)` and rejects `(0,1)`;
V allows the reverse. These controls catch inverse-permutation and reflected
orientation mistakes which can otherwise preserve a count.

| k | Enumerated two-run stacks | Proven two-run formula | Enumerated three-run stacks |
|---|---:|---:|---:|
| 2 | 4 | 4 | 10 |
| 3 | 11 | 11 | 48 |
| 4 | 22 | 22 | 142 |
| 5 | 37 | 37 | 319 |
| 6 | 56 | 56 | 606 |
| 7 | 79 | 79 | 1030 |
| 8 | 106 | 106 | 1618 |

Reproduce any row with `--assignment` followed by the literal M/V string,
or `--k` for the three-run column. The proven control `2k^2-3k+2` is from the
paper's two-block edge case. It is for k>=2; blindly evaluating it at k=1
would be wrong. The three-run numbers match the longer preprint's prediction
`(9k^3-25k^2+30k-12)/2`, but matching is not a proof.

## First symbolic result

For the prefix with an exterior mountain spiral and tightly nested valley
run, the [gap proof](first-family.md) gives exactly k completions.
Allowing all k mountain stacks but keeping the valley run tightly nested
gives a growing family with **k²+1** completions: one prefix contributes k+1,
the others k each. Fern's [independent reconstruction](RECONSTRUCTION.md) verifies the family.

```
$ python3 projects/three-runs-of-stamps/count.py --k 4 --nested-family
MMMMVVVVMMMM: 17 legal labeled stacks
nested-family theorem: 17 (see first-family.md)
```

The program enumerates these completions from the definition; it does not
use either formula to generate or count them. `--family` selects only the
exterior prefix, and `--nested-family` selects all k tightly nested prefixes.
The tests also check the exceptional prefix, not just the sum. The family is
a small part of the full problem: 17 of the 142 stacks at k=4.

The next enlargement permits the first valley crease in any legal gap,
then nests the remaining valleys. For k>=3 it has k+1 prefixes and
**k²+k+3** completions; k=2 has two prefixes and five completions. A local
insertion/deletion bijection in the same proof note establishes the linear
growth in the valley-run length. Its tests check the map in both directions,
as well as counts and the exceptional smallest case.

```
$ python3 projects/three-runs-of-stamps/count.py --k 4 --first-valley-family
MMMMVVVVMMMM: 23 legal labeled stacks
first-valley-family theorem: 23 (see first-family.md)
```

The [independent reconstruction](RECONSTRUCTION.md) also verifies this larger
family. The [full decomposition](cubic.md) counts the stacks whose second
or later valley face is placed in a nonadjacent gap.

## Literature status and review

The [longer preprint, version 2](https://arxiv.org/html/2503.23661v2), section
5.2, Table 2, gives the cubic as an interpolation tested through k=78.
The published version retains the open general counting question and refers
back to the longer version for the experimental results. The component proofs
and their parameter ranges are collected in [the full argument](cubic.md).

A fresh search on 19 November 2026 found an additional lead:
[Shintaro Sakai, *Stamp folding patterns and a boundary-based counting
approach*](https://www.tandfonline.com/doi/full/10.1080/00150517.2026.2711255),
published online 4 September 2026. The indexed publisher abstract describes a
boundary decomposition for labeled stacks and limitations of its product
structure. Direct full-text retrieval returned 403; PDF retrieval also failed.
The abstract alone does not settle whether any argument here overlaps it.
**Full-text priority and overlap remain unresolved.** The search also found
Sakai's [earlier recurrence paper](https://journalofscience.org/index.php/GJSFR/article/view/102616).
Neither abstract certifies a solution to the fixed three-run problem.

The [full independent reconstruction](CUBIC_RECONSTRUCTION.md) is complete:
it checks the classification, the fourth-stop induction and both terminal
boundaries, and reconstructs small counts without importing the author’s
enumerator. Finite agreement supports the argument; it does not replace its
arbitrary-length proof. Resolving the literature overlap still requires
access to the cited full text.
