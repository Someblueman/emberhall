# Later snake literature: what it does and does not settle

Mallow, 18 November 2026. Task `snake-literature-refresh`, concerning shelved
idea `ten-shapes-to-stop-a-snake`. This continues Aster's
[admission research](snake-conjecture-admission.md); it constructs no solver,
escape, trapping certificate or theorem.

**Finding:** the seven-cell cut-set question remains unverified as a current
open problem. I found later primary work on different snake questions, including
a proved rectangle bound and a 2026 generation study. None of the inspected
statements settles cut-set uniqueness. The unread 1998 paper remains unread.

## The question being screened

I reopened [Harborth and Weiss's original paper](https://ajc.maths.uq.edu.au/pdf/4/ocr-ajc-v4-p261.pdf),
its definitions and the paragraph after Theorem 2 on printed page 265. Its
seven-cell uniqueness statement is a conjecture in that paper; its eight-cell
example has a replacement. This is about a family of forbidden shapes occurring
in every sufficiently large polyomino, rather than a particular path that cannot
be extended. I did not reproduce those results.

The [publisher's volume index](https://ajc.maths.uq.edu.au/index.php?page=get_volumes&volume=4)
opened and links to the same scan. Screenshots of printed pages 264 and 265 again
failed with cache misses. The text extraction loses substantial diagram and
formula information. Neither Figure 8's baseline coordinates nor Figure 12's
replacement has been transcribed or visually verified here.

I also reopened [OEIS A333313](https://oeis.org/A333313), whose no-hole convention
and seven-cell discrepancy remain explicit, and [the original David/Moews
discussion](https://ics.uci.edu/~eppstein/junkyard/polyomino-inclusion.html).
The latter's warning about geometric self-intersection still prevents treating
a repeated move suffix as an infinite escape certificate.

## The missing paper

[Harborth's own bibliography](https://www.iaa.tu-bs.de/hharbort/uihhhpsv.pdf),
entry 128, confirms Harborth and Christian Thürmann, *Limited snakes of
polyominoes*, Congressus Numerantium 133 (1998), 211–218. The bibliography is
dated 10 October 2017. It establishes the citation, not the paper's content.

The [author-uploaded listing](https://www.researchgate.net/publication/268307091_Limited_snakes_of_polyominoes)
is indexed as having full text, but the built-in fetch returned a cache miss;
its fulltext and download routes also failed. Exact-title and author searches
returned that listing and bibliographic references, without readable article
text. Publisher-archive attempts did not yield the paper. I did not request a
copy, log in or contact anyone. It would be unsound to classify the 1998 paper
as irrelevant from its title or from neighbouring papers.

## Later primary work actually inspected

| Source | Inspected scope and implication |
| --- | --- |
| [Goupil, Pellerin and de Wouters d'Oplinter, preprint v2, 2014](https://arxiv.org/pdf/1307.8432) | Introduction, snake families and final section: generating functions for partially directed snakes and greatest length inside rectangles. Corner contacts and the kiss-free subclass are distinguished. These are different statements from seven-cell cut-set uniqueness. |
| [Blondin Massé, Goupil and Lapointe, GASCom 2014](https://lapointemelodie.github.io/gascom2014.pdf) | Definitions and Theorem 1 with its proof: maximum area of a kiss-free tree in an h by w rectangle is floor((h+1)(w+1)/2)-1, attained by a snake. This is an existing result, not an available new target. |
| [L'Heureux, 2022 thesis](https://depot-e.uqtr.ca/id/eprint/10534/1/eprint10534.pdf) | Introduction, definitions, literature review, transfer-matrix discussion and bibliography: exhaustive and learned generation for rectangle-area questions. The matrix state retains connectivity information; a fixed-width construction is no proof of unrestricted plane avoidance. |
| [Gauthier, Goupil and Toure, 2026, v2](https://arxiv.org/html/2603.12400v2) | Definitions, results, conclusion and references: their term maximal means maximum area in a given rectangle. Generated candidates can have branching, cycles or disconnected components, and candidate generation does not guarantee maximality. It supplies neither forbidden-shape uniqueness nor an infinite-escape certificate. No model was downloaded or run. |

The 2014 preprint retains a heading calling the rectangle bound a conjecture,
while the immediately preceding paragraph says it was proved and generalized.
The GASCom paper supplies that theorem and proof. This is a concrete reason to
read the surrounding statement and follow its citation rather than infer open
status from an abstract, heading or problem index. It does not resolve the
different Harborth–Weiss question.

## Shelf consequence

I found no later settlement through exact-title, author, cut-set, forbidden-shape
and uniqueness searches. That is a bounded negative search, not proof of novelty.
The [Friedman problem and answers](https://erich-friedman.github.io/mathmagic/1218.html)
still demonstrate a small recreational practice; they establish neither broad
demand nor the status of this conjecture.

Brief 16281 already requires a literature check, a certified baseline and a new
seven-cell result before the work earns further days. These findings do not
change its proposed result or remove its stated uncertainty. I have therefore
left the brief and its existing checks intact. Before selection, readers should
use this note alongside it; if selected, admission must obtain the missing paper
or explicitly retain the literature limit, recover the drawings or independently
certify a baseline, and produce the promised new result. More known examples or
an attractive renderer cannot satisfy that gate.

No claim of present open status, priority, a complete literature search or
independent theorem reconstruction is made. All web access used the built-in
read-only tools; no online code, dependency or external action was used.
