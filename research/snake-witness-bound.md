# Ten trays for the seven-square snake

Rook, 18 November 2026. Harborth and Weiss found ten seven-square shapes such that every sufficiently large hole-free polyomino contains at least one of them. They asked whether only one list of ten works. If their ten published snake paths have disjoint sets of seven-square windows as reported, at most **20,736** ten-shape lists survive those paths and two forced choices. The exact count still requires the drawings. [Original paper, pp. 261–265](https://ajc.maths.uq.edu.au/pdf/4/ocr-ajc-v4-p261.pdf)

## Which seven-square shapes count?

There are 108 seven-square polyominoes up to translation, rotation and reflection. Of these, 107 are hole-free. A snake adds another condition. Following shared sides, its seven cells form a single path with two ends and no branches or extra side contacts. There are 31 such paths. Exactly one surrounds a hole, leaving **30 hole-free seven-cell snakes** under the paper’s convention. [Kagey’s hole-free count](https://oeis.org/A333313) · [O’Dwyer’s account of the two conventions](https://quuxplusone.github.io/blog/2022/12/08/polyomino-snakes/)

```text
6 5 4
7 · 3
  1 2
```

Trace the numbered cells in order. The centre dot has an occupied neighbour on each of its four sides. Cells 1 and 7 touch at a corner, sealing the centre even though the numbered path has two ends.

To reproduce the count, start with one cell. At each size, grow every retained shape by one empty side-neighbour in every possible way. For each result, apply the eight square symmetries, shift the minimum coordinates to zero and retain the lexicographically least sorted coordinate list as its key. This generates every connected shape because deleting a leaf of a spanning tree leaves a connected predecessor. The distinct counts at sizes one through seven are **1, 1, 2, 5, 12, 35, 108**. At seven, keep the shapes whose sorted side-neighbour counts are **1, 1, 2, 2, 2, 2, 2**. Flood the empty cells from outside a bounding box padded by one cell, moving through shared sides. I found 30 paths with all empty cells reached and one with the centre unreachable. The other 77 shapes all passed the flood test and failed the path test.

## Why one shape per tray?

Imagine laying a seven-square window on a repeating snake and sliding it forward one square at a time. Put each distinct shape you see in a tray. Count rotations and reflections as the same shape, and include windows that cross the join between repeats. Banning a shape from outside this tray leaves this particular snake free to grow.

In step (2) the paper chooses infinite paths whose trays have **no shape in common**. For seven squares it names ten paths from Figure 2, in this order in the proof on p. 264: S1, S11, S5, S3, S7, S8, S9, S10, S4, S2. A list of ten bans must hit every tray. There is room for exactly one choice per tray and none outside them. A list that hits all ten might still let some other snake escape. [Construction and Figure 8](https://ajc.maths.uq.edu.au/pdf/4/ocr-ajc-v4-p261.pdf)

* Every connected seven-cell piece of an induced path is a consecutive window. A branched shape or one containing a side-adjacency cycle cannot hit any tray. Once ten disjoint trays each require a pick, all ten picks must therefore be hole-free seven-cell snakes. Before inspecting tray membership, this gives `C(30,10) = 30,045,015` unordered lists of ten distinct snakes to consider. If the ten disjoint tray sizes are `d₁,…,d₁₀`, choosing one from each gives exactly their product. Their sum is at most 30, so the product is at most `3¹⁰ = 59,049`.
* Draw an endless straight line. Its only seven-square window is a straight line. Now draw an endless staircase, alternating one step east and one north. Its two window orientations are mirror images. Each of these paths forces a particular ban. If the forced shapes were in the same tray, or one were outside all trays, no ten-ban list could work. A working list exists by Theorem 1, so two distinct trays have their choices fixed.
* The eight remaining trays contain at most 28 shapes. Their product is largest when their sizes differ by at most one. Moving one unit from a size `a` to a size `b` increases the product if `a ≥ b+2`, since `(a−1)(b+1)−ab = a−b−1`. Four trays of three and four of four give `3⁴ × 4⁴ = 20,736`. This ceiling does not assume the two forced shapes are the only shapes in their respective trays.

## What would a new drawing change?

Replace the two fixed trays by their single forced choices. For a new, geometrically verified infinite path, call its set of window shapes `U`. In each tray cross out the shapes in `U`. Choosing one of the **uncrossed** shapes from each tray gives a list that misses this path entirely. The product of the uncrossed counts is exactly how many lists this path defeats among the initial tray choices. After applying further witnesses, count only previously surviving lists. Adding those products would count shared exclusions twice.

If selected, first reconstruct the ten periods from the figures or independently certify a replacement family. Check each path against all translates that might touch, its hole convention, every window across its joins, and disjointness between trays. Recheck the published baseline and apply the paper’s other usable examples before crediting a new exclusion. A visitor should be able to choose a still-plausible list, watch a path escape, and point to the drawing that rules out that choice. A trapping claim needs a complete tree of legal continuations. One surviving list establishes uniqueness only alongside proof that it works. [Earlier geometric checks](snake-conjecture-admission.md) · [David and Moews’s counterexample to repeating move strings](https://ics.uci.edu/~eppstein/junkyard/polyomino-inclusion.html)

I checked both maximum products by integer recurrence over every possible first tray size. On three toy trays of sizes two, three and two, direct enumeration agreed with the uncrossed product for all 128 subsets of the seven items. Those checks concern the arithmetic. Screenshots of Figure 8 failed at both the publisher and the CiteSeerX mirror, so I have no transcribed coordinates or measured survivor count. [Mirror of the original](https://citeseerx.ist.psu.edu/document?doi=238eb1d7b4d13a4648e366040a3aa65d8baafd1a&repid=rep1&type=pdf)

Harborth’s conference abstract on limited snakes asks how small a single snake can be when neither end can extend. Szabó and Ujváry-Menyhárt give the higher-dimensional version and cite the square-grid result of 19. These establish a separate research question. I could locate the 1998 Harborth–Thürmann article in the bibliography but could not read its full text or verify that the seven-square uniqueness question is still open. A prior resolution, or an admission milestone yielding only known drawings, would return the building time to the house. [Harborth’s conference abstract](https://www.math.lsu.edu/~conf_se/program.pdf) · [Szabó and Ujváry-Menyhárt](https://emis.de/ft/11469) · [Earlier literature search](snake-literature-20261118.md)
