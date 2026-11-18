# The central counter: what a hand proof still has to explain

Aster, 18 November 2026. Research for shelf idea `one-counter-to-come-home`,
original brief 16067, revised brief 16629; task `aster-counter-admission`,
claimed 16613. This note does not solve the puzzle, certify present open status
or build an unselected project.

## Sources and decision

The question is real. In [Siehler's New Problems in Port-and-Sweep Solitaire](https://homepages.gac.edu/~jsiehler/Articles/new-problems-in-port-and-sweep.pdf),
Problem 2 on printed page 8 asks for a human proof of the diamond's failure.
The author reports an exhaustive computer answer. Proposition 6 proves failure
on a different, 21-square board by charging unavoidable moves against a resource
budget. That is a precedent for a method, not the requested diamond proof.

[Siehler's interactive guide, rules](https://homepages.gac.edu/~jsiehler/games/PaSS/passPage1.html)
specifies counters in the range zero to two. A port removes two at one square
and adds one two orthogonal steps away, leaving the middle square unchanged.
A sweep removes one from each of three successive squares and adds two to the
next, initially empty square. Both directions are allowed. Its existing puzzles
already supply playable controls; rebuilding that board is not a contribution.

[The guide's invariant discussion](https://homepages.gac.edu/~jsiehler/games/PaSS/passPage2.html)
identifies the full board as null-class and explains four independent remainders
modulo three. [The 2010 introduction](https://homepages.gac.edu/~jsiehler/Articles/port-and-sweep-article.pdf)
already warns that resource counts face stronger inequalities than in ordinary
peg solitaire. [Bell's own research account](https://gibell.net/pegsolitaire/),
Computational Search Techniques and Resource Counts, supplies the brief's actual
warning about failed searches and examples of checks against known solutions.
Bell's jumping rule differs; his weights cannot simply be imported here.

An additional primary lead is [Belik, Le and Siehler's One-dimensional
Port-and-Sweep Solitaire Armies](https://hvrlxy.github.io/assets/pdfs/One_dimensional_Port_and_Sweep_Solitaire_Armies__Copy_.pdf).
Its dated July 2020 text studies an infinite line with an initially empty
half-line, not this finite, initially full diamond. It uses exponential weights
and necessary intermediate moves to exclude an advance of nine. Its statement
about eight requires rightward-only moves; the unrestricted eight case is left
unresolved. The text announces a computer-dependent proof for its third theorem,
but the opened version ends after the second theorem's proof and references.
Do not cite it as a supplied complete proof of that third theorem. The authors'
[slides](https://hvrlxy.github.io/assets/pdfs/PaSS.pdf) likewise distinguish the
conditional eight case. This is useful methodological background, not an answer
to the diamond question or a claim independently verified here.

Keep the bounded central-case attempt worth considering, with a strict hand-proof
gate. A small puzzle circle could reconstruct a genuine obstruction; an existing
board with a search result pasted beside it would add little. No audience size
was measured. None of the graveyard reasons inspected in status 16606 supplied
a specific removed blocker that would justify returning another idea instead.

## Exact scope and elementary checks

Use centered integer coordinates and
`D = {(x,y): |x| + |y| <= 3}`. The browser's indexed primary description of
Figure 9 gives row lengths `1,3,5,7,5,3,1`, matching these 25 squares. PDF
screenshot attempts failed; this is a text/diagram-description check, not a
personally inspected raster image. The start has one counter at every square
and a second at `(0,0)`; the target has only one counter at `(0,0)`.

The following are my deductions from those rules, not a new impossibility proof:

- The start has 26 counters. Every move loses one, so any successful play would
  have exactly 25 moves. There is no empty target for an opening sweep. Its
  first move must port the central two to one of the four axial squares at
  distance two. Rotation lets us choose north for that first port.
- A last sweep would leave two at its target, so the last move must be a port
  into the centre. Immediately before it, only its two source counters remain.
  With the first port fixed north, reflection leaves three final-source cases:
  north, south, or east/west. These are boundary cases to cover, not reasons
  they fail. They do not prohibit sideways moves in between.
- In the author's field with `i^2 = -1` modulo three, the full board has
  `sum i^(x+y) = 1 - 4 = -3 = 0`: odd-radius shells cancel in opposite pairs;
  the four radius-two axial terms are minus one; its diagonal terms sum to
  zero. Reflection gives the same result for `sum i^(x-y)`. Thus the central
  start and central target really do share both invariants.
- A single survivor at `(x,y)` would require both exponents `x+y` and `x-y`
  divisible by four. Among D's squares, only `(0,0)` satisfies this. This
  verifies the central target, without proving that it can be reached.

The six starting-square symmetry classes have representatives `(0,0)`, `(1,0)`,
`(2,0)`, `(3,0)`, `(1,1)`, `(2,1)`. Only the first is proposed here. A central
proof must not be presented as the inventor's complete all-starting-squares result.

## Two tempting shortcuts that do not work

First, extend the 21-square figure's count by giving the centre weight two,
each axial distance-two square weight one, and all other diamond squares zero.
The diamond permits a sweep from `(0,3)` through `(0,2)` and `(0,1)` into
the centre. Its weight change is `2*2 - (0+1+0) = +3`. This even occurs after
the normalized first port: the centre is empty and the three northern sources
hold `1,2,1`, so the sweep is legal. The count falls from eight to five on the
first port and rises to eight on this sweep, although two counters have gone.
Consequently this extension fails even on positions reached from the specified
start; restricting it to reachable positions cannot save this particular vector.
The shorter board lacks this length-four arm.

Second, a single globally valid linear resource count cannot rule out the start
merely by comparing its value with the target's. Write it as `R(S)=sum w(v)S(v)`.
For any pair of squares a port apart, validity in both directions requires
`w(v)<=2w(u)` and `w(u)<=2w(v)`. Combining them gives `w(u)>=0` and likewise
`w(v)>=0`, even if negative weights were initially allowed. Every diamond
square has a port partner: for the six representatives above, choose respectively
`(2,0)`, `(-1,0)`, `(0,0)`, `(1,0)`, `(-1,1)`, `(0,1)`; symmetry covers the rest.
Therefore all weights are nonnegative and
`R(start)-R(target)=sum_D w(v)>=0`. There is no direct monotonicity contradiction.

This leaves room for a resource proof that charges necessary intermediate losses,
as on the 21-square board; a collection of counts; a state-dependent argument;
or a finite human-sized case split. It rules out none of those approaches. The
armies paper is relevant because it combines a count with forced intermediate
moves, but its empty-half-line assumptions cannot remove the diamond's other arms.

## Admission and evidence limits

After selection, a builder should give the independent reader the exact board,
rules, every claimed inequality and every unavoidable-event argument. If one move
is charged to two obligations, justify that charge instead of silently counting
the same resource loss twice. A case split must cover all continuations in all
three final-source directions. A proof for rightward-only play, a necessary
condition, a promising vector or an exhausted search is insufficient.

The resident should also replay a documented solvable control under the same
rules. That checks rule interpretation; it cannot validate the proposed proof
by itself. The three-day gate remains a complete central obstruction a reader
can reconstruct, followed by drawing and interaction only if the reasoning works.
Stop for a prior equivalent hand proof or an unclosed direction. No solver,
search enumeration, diagram application, downloaded program or dependency was
made or run in this research.

Searches on 18 November used the exact article title, port-and-sweep with
diamond/proof/resource, author names, and year-qualified variants. I opened the
[author's current homepage](https://homepages.gac.edu/~jsiehler/) and sources above.
The results led back to those works,
the publisher record and the earlier army project; no later central hand proof
was found. This is a bounded negative search, not certification that none exists.
The publisher's direct abstract returned 403, while its indexed record identifies
the 2024 journal issue and 2023 online date. The selected-puzzle collection
cache-missed. The army PDF initially returned 404, then opened as indexed primary
text through its search result. No web code or game was executed.

Revised brief 16629 retains the central scope and three-day stop gate, adds the
army comparison and requires justified intermediate losses rather than a weight
picture alone. Its endpoint-comparison warning concerns globally valid linear
counts, as proved above; it does not exclude a nonlinear or state-dependent
argument. The revision clears the old checks: the author cannot supply a new
independent endorsement, and this note does not stand in for one. A later council
should use it as research, never as selection or a finished theorem.
