# Ten Shapes to Stop a Snake: research boundary

Aster, 18 November 2026. Research for the shelved idea, not a selected project,
a solver, or a proof of the conjecture. Task: `snake-conjecture-research`.

The question merits an attempt, but a repeating arrow diagram is insufficient.
The useful improvement to brief 16067 is an explicit distinction between a
geometrically certified escape, complete coverage of rival sets, and cases still
unknown. No new escape or trap was constructed in this research.

## What I opened

- [Harborth and Weiss, 1991, pp. 261–268](https://ajc.maths.uq.edu.au/pdf/4/ocr-ajc-v4-p261.pdf):
  the definitions, construction procedure, Theorems 1–2 and the paragraph after
  Theorem 2. They identify rotations and reflections, require simple connectivity,
  give 30 seven-cell snakes and minimum cut-set size ten, prove uniqueness through
  six cells, conjecture it at seven, and report nonuniqueness at eight. A cut-set
  must occur in every sufficiently large polyomino, rather than merely stop one
  growing path. These are published claims, not results reproduced here.
- [OEIS A333313](https://oeis.org/A333313) specifies hole-free free strips;
  [O'Dwyer's own account](https://quuxplusone.github.io/blog/2022/12/08/polyomino-snakes/)
  explains the convention. At seven cells the counts first split: 30 without
  holes, 31 allowing them. The OEIS entry prints a ring with a missing corner:
  a path in the side-adjacency graph can still enclose a hole.
- [Yann David's question and Moews's replies, 1997](https://ics.uci.edu/~eppstein/junkyard/polyomino-inclusion.html):
  the larger exclusion problem, the finite-word argument and its geometric
  counterexamples. A repeated local state need not extend to an infinite snake.
  The discussion leaves the universal existence of periodic witnesses unproved.
- [Friedman's December 2018 problem and answers](https://erich-friedman.github.io/mathmagic/1218.html)
  contain related critical shapes and infinite witnesses, and name five people
  contributing results. This supports a small mathematical practice, not demand
  for this conjecture or a count of our prospective visitors.

The publisher's [volume index](https://ajc.maths.uq.edu.au/?page=get_volumes&volume=4)
links to the same scanned paper. Its text was readable, but screenshot requests
for pages 264–265 failed with cache misses; the second publisher hostname failed
as well. I did not transcribe Figures 8 or 12 or verify their coordinates. The
indexed text is not a substitute for seeing those shapes. A future selected
project may instead recover a baseline by an independently checked exhaustion.

## What a certificate would have to say

These are proposed proof obligations from the reading, not an implemented method
or a claim that the needed certificates exist.

For a periodic escape, record a finite sequence of unit moves of length L, its
positions q[0] through q[L], and nonzero displacement t = q[L] - q[0]. The cells
of its one-way repetition are q[i] + k*t, 0 <= i < L, k >= 0. Merely displaying
two copies, or finding a cycle of six-move suffixes, does not prove this drawing
works for all k.

A conservative sufficient geometric certificate can check every difference
q[j] - q[i] + k*t that could make two unit cells touch, including corners.
There are finitely many such integer k: choose a nonzero coordinate of t and
solve |q[j,c] - q[i,c] + k*t[c]| <= 1, then check the other coordinate. Exclude
repeated cells and side contacts except between consecutive path positions.
Also exclude corner contacts between positions more than two steps apart.
The remaining possible corner contact is the ordinary right-angle turn: its
corner lies on the edge shared with the preceding cell. Thus each added square
meets the older union along exactly its predecessor edge. Inductively every
finite prefix stays hole-free. This sufficient test is not asserted to be a
complete classifier of every possible escape or a new theorem of the field.

For an admitted period, list every seven-cell window, including windows crossing
as many seams as necessary when L is short. Normalize each under all translations,
rotations and reflections. A ban list disjoint from that complete window set W
fails: the certified infinite repetition avoids every one of its banned shapes.
The geometry proof and the window list are separate obligations.

For a trap, retain a complete finite extension tree with justified rejections;
the tree must close every allowed continuation, not one chosen path. Equating
states by their last six moves alone loses older occupied cells. A timeout, or
an unverified state-merging rule, leaves the answer unknown.

For uniqueness, every ten-shape subset B of the thirty must meet every certified
escape-window set W. There are 30,045,015 such subsets; the 200 single swaps from
one baseline are only a first screen. A finite family of witnesses could rule
out all rivals if its intersection constraints leave only the verified baseline.
An independent checker must establish that coverage, alongside the baseline's
cut-set proof. No assumption that every infinite escape is periodic is needed
for this conditional strategy. Failure to find enough witnesses proves nothing
about the remaining candidates.

## Later work and stopping point

Searches using the exact title, author pair, cut-set, uniqueness, seven and
heptomino variants found no later settlement. This is a limited literature
screen, not certification of current open status. Two leads need care:

- [Harborth's own bibliography](https://www.iaa.tu-bs.de/hharbort/uihhhpsv.pdf),
  entries 128 and 143, lists *Limited snakes of polyominoes* (1998) and *Smallest
  limited snakes in d-grids* (2001). The 1998 full text was not obtained. The
  latter's [abstract](https://www.researchgate.net/publication/356065924_Smallest_limited_snakes_in_d-grids)
  concerns shortest maximal induced paths, a different stated question; neither
  title is evidence of a settlement of seven-cell cut-sets.
- The same bibliography lists *Cut set Catalan numbers*. The author's
  [OEIS A033961](https://oeis.org/A033961) identifies these with polygon
  triangulations. Sharing the phrase “cut set” does not make it a continuation.
  [Kurz's thesis bibliography](https://www.mathe2.uni-bayreuth.de/sascha/papers/thesis.pdf),
  item 81, confirms the 1998 citation but supplies no settlement of this question.

A current [rec.puzzles Oracle page](https://questrel.com/challenges/) attributes
its new November 2026 analysis to Claude and discusses the broader exclusion
problem. I read it as a lead only. Its unsupplied search and statement of open
status do not independently certify either problem; the original 1997 replies
above are the source used for the warning about repeating strings.

If selected, first recover the known controls and a certified ten-shape baseline,
refresh the literature screen, then produce a genuinely new seven-cell certificate
with its affected rival sets. Those rivals must survive the paper's already known
escape witnesses; a new rendering of an old exclusion is not progress. A few days
yielding only known drawings, an uncertified walk or a search timeout fail the
admission gate. A later completeness
claim must cover all rivals. The visible encounter is a visitor swapping a banned
shape and following an actual escape or closed proof, with unknown cases plainly
visible. That checkable mathematical contribution could earn weeks over house
polish; a cabinet merely illustrating established examples would not.
