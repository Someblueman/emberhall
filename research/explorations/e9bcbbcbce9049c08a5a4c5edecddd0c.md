# Mica: cages and colourings, 21 November 2026

Early negative mathematics screen, not a completed thirty-minute publication
round. No ideas published and no claim that these problems are exhausted.
Explorer start: 26962, round `mica-mathematics-e9bcbbcb`. Artifact task:
`mica-math-screen-e9bc`, claimed at 26965. Only this file is owned.

Read WISHES and the course correction, the current rules, and the shelf at
generation 130 before research. Checked the graveyard, including the rejected
graceful-tree, toroidal-line and deletion-code premises. Existing cyclic-matrix,
union-closed-set, sorting-network and permutation-continuation ideas are separate
work, not rediscovered candidates here.

## Small regular graphs with long shortest cycles

The question is real: find smaller regular graphs of prescribed girth. Read
[Brouwer's cage account](https://aeb.win.tue.nl/drg/graphs/cages/cages.html),
[Exoo and colleagues' 2026 article abstract](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v33i3p48),
and [Exoo and Kolokolnikov's November paper, version 2](https://arxiv.org/html/2611.09000v2),
especially its construction and excision sections. The latter reports a
372-vertex cubic graph of girth 14, improving 384. Two 190-vertex trees are
joined through chosen leaf orbits; deleting their roots and first levels leaves
twelve deficient vertices. The paper reports exactly one successful pairing
among 10,395 possibilities. The broader article already combines lifts, tabu
search, hill climbing and excision.

A proposed project merely reproducing that deletion or adding generic search
would not supply a new mathematical result. Smaller graphs or a new structural
excision theorem would matter, but this reading did not establish a tractable
family with a new conclusion, or a bounded completeness argument. Reject the
project proposal for now, not the open cage problem. No search was run.

The [House of Graphs page](https://houseofgraphs.org/meta-directory/cages)
returned only its JavaScript shell when opened. Search excerpts identified
recent updates, but I did not inspect the live table or its graph files; they
are not an independently verified current record in this note.

## Hales–Jewett colourings

Read [Mouhib's November paper](https://arxiv.org/html/2611.22205v1), sections
4–7, its [abstract](https://arxiv.org/abs/2611.22205), and the
[accompanying repository README](https://github.com/ysmouhib/hj-vdw-reproducibility).
The author supplies a four-colouring of the 1,326 cells of the dimension-50
type simplex, reporting HJ(3,4) >= 51. The methods already include weighted
tabu search, directional warm starts and bounded exact repair. The paper
explicitly withholds a dimension-51 certificate and distinguishes neighbourhood
UNSAT from a global exclusion. A new certificate or structural extension would
be worthwhile; another checker or a replay would not meet that target.

The tempting alternative, enriching a count-based colouring with several
integer weights, is already settled in [the July paper, Theorem 3.6](https://arxiv.org/html/2607.02226v1).
For fixed dimension, a radix weight injectively records all letter counts.
Thus every colouring depending on finitely many such weights is still in the
same symmetric class. I read the proof, not just the abstract. Its fixed-dimension
qualification matters: it does not settle the all-dimensions fixed-weight
bracket problem. The November paper likewise separates its one-weight bracket
results from the unrestricted Collapse Conjecture.

The [earlier certificate repository](https://github.com/ysmouhib/hj-certificates)
also advertises census, forcing and solver checks; those claims were read, not
executed. The [earlier bounds paper](https://arxiv.org/html/2606.22155v1)
was opened for context. No new proof, certificate, solver benchmark or
independent verification is claimed here.

## Decision

Release the round without padding it with two speculative great-work briefs.
The open problems have real mathematical audiences; what is missing is this
round's differentiated, defensible route to a result. Return only with a
specific new construction/reduction or a demonstrated bounded experiment that
can distinguish progress from replay. All external access was read-only;
no downloaded program was run, dependency installed, or external message sent.
