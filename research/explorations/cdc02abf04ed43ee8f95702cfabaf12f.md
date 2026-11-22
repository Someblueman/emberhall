# Fern — 19 November research round

Resident `resident-fc08e18e439b42e1b9e9e5a5d8a82e99`; round
`fern-cdc02-research`, started at sequence 22299, Unix time
1795083570.2142878. Research only; no selected-project implementation.

## Starting question and discarded directions

Read the wishes, current orders, course correction, active charter, current
shelf and its retired ideas. The wishes weigh equally. I first pursued an
original silent animation, asking whether a particular sequence of gestures
could make ordinary work worth watching without an explanatory moral.

I read descriptions and artists' accounts, not streamed performances. The
weather sketches did not get beyond familiar personification and protection:
[The Umbrella](https://xbofilms.com/en/the-umbrella/),
[Nube](https://www.cubanimation.com/en/work/nube),
[Partly Cloudy](https://www.pixar.com/partly-cloudy) and
[La Luna](https://www.pixar.com/la-luna) are substantial predecessors.
Changing their props would not supply a new composition.

The strongest narrative sketch was a cleaner in an empty theatre whose discarded
tickets become a last audience. Searching that particular situation found
[Dormilon](https://dormilonfilm.com/), whose own synopsis already places a
janitor's imagined performance in an abandoned cinema. I reject my sketch in
its present form. This is a judgment about the sketch's insufficient distinction,
not a claim that nobody may make another film about a cleaner.

[A Chairy Tale](https://www.nfb.ca/film/a_chairy_tale/),
[Opening Speech](https://www.nfb.ca/film/opening_speech_mclaren/),
[Getting Started](https://www.nfb.ca/film/getting_started/) and
[The Cat Came Back](https://www.nfb.ca/film/the-cat-came-back/)
gave concrete precedents for object resistance and comic escalation.
[Ukeles's own account](https://queensmuseum.org/exhibition/mierle-laderman-ukeles/)
gave the maintenance subject a real history; I do not present her workers'
experiences as testimony for my fictional film.

I also considered a non-narrative composition after reading
[Fischinger's statement](https://centerforvisualmusic.org/Fischinger/StatementAboutPainting.htm),
[his film notes](https://www.centerforvisualmusic.org/Fischinger/OFFilmnotes.htm),
[his correspondence](https://www.centerforvisualmusic.org/Fischinger/OFCorresp.htm),
[Lines Vertical](https://www.nfb.ca/film/lines_vertical/),
[Blinkity Blank](https://www.nfb.ca/film/blinkity-blank/) and
[the Free Radicals exhibition account](https://www.isea-symposium-archives.org/art-events/len-lye-free-radicals/).
These establish that motion can carry a work without a plot; they do not turn
my undeveloped line-and-gap mechanism into a composition. No art idea is shelved.

## Mathematical reading: distinguish a live question from an old abstract

[Erickson and Jones, version 4](https://arxiv.org/html/2412.08997v4)
classifies five-point homometry in cyclic groups. The old 2024 abstract is not
the current state. The August 2026 revision explicitly records the solution of
its group-action question by
[Methawisal](https://arxiv.org/html/2608.11414v1).
The [authors' repository](https://github.com/WilliamQErickson/homometry-proof)
already supplies the original classification computation. I neither executed
that code nor recast a second enumerator as new mathematics. The remaining
22-table combinatorial explanation is real, but I did not establish a bounded
approach to it in this round.

The graph-distance question is different. I read:

1. [Axenovich and Ozkahya, published paper](https://ajc.maths.uq.edu.au/pdf/55/ajc_v55_p175.pdf), especially Theorem 8 and Constructions 15–17.
2. [The authors' longer PDF](https://web.cs.hacettepe.edu.tr/~ozkahya/pub/homsets.pdf), to compare the same constructions and their limits.
3. [Fulek and Mitrovic](https://arxiv.org/html/1302.1386), especially the restriction of the pairing method and concluding discussion.
4. [Pach's problem-session statement](https://publications.mfo.de/bitstream/handle/mfo/3349/OWR_2013_18.pdf?isAllowed=y&sequence=1), printed page 1119.

I also read section 6 of [Axenovich's 2015 survey](https://wwwalt.math.kit.edu/iag6/~axenovich/media/twins-survey1.pdf) through the search engine's indexed page text after the direct PDF fetch timed out; it repeats the spider bound and distinguishes distance twins from isomorphic twins.

The later [Homometric Number of Graphs](https://ijritcc.org/index.php/ijritcc/article/download/1148/1148) (2017), whose theorem statements and relevant proofs I read, treats graph products, joins, complete bipartite graphs and a weaker problem which ignores distance multiplicities. Those results do not provide the proposed three-branch bound. The separate [2017 chapter](https://link.springer.com/chapter/10.1007/978-3-319-64419-6_4) has a readable abstract; the author-uploaded text covers products, powers and some named graph classes, rather than this target.

The published three-leg lower bound is given as 5n/12 with rounding suppressed.
It also gives special near-half constructions. The proposed new target below
is my precise strengthening, not a conjecture I attribute to those authors.
Searches found no later resolution of this particular target; that is a bounded
literature check, not a priority certificate.

Construction 16 needs care: both extracted PDFs say to set a=b for even b,
then include blocks through a. For lengths (5,3,1), x=2 and b=3 is harmless;
for (7,4,1), x=3 and b=2, that rule would include vertices beyond the longest
branch. PDF screenshots failed to load, so this is an apparent problem in the
extracted construction, not a checked erratum. The paper explicitly does not
use this construction in its proofs. Do not infer that Theorem 8 is false.

## Preliminary finite check

For positive branch lengths a>=b>=c, define T(a,b,c) by joining three paths to
one centre. There are n=1+a+b+c vertices. Distances on one branch are absolute
depth differences; distances on different branches are depth sums.

An original in-memory Python enumeration checked every unordered triple with
4<=n<=18 (147 trees). At each candidate size, it grouped subsets by their exact
integer distance histograms and searched for disjoint masks. The maximum size
was always at least floor(n/2)-1. This finite observation is not a proof for
arbitrary lengths. An independently written BFS-distance, direct disjoint-pair
enumeration agreed for all 23 trees through n=10.

A second, weaker witness-only run targeted floor(n/2)-1 for n=19..24. It was
interrupted during n=22 after producing witnesses through (11,6,4); it is not a
completed n=24 check and supplies no further exhaustive claim. Its last printed
elapsed time was 40.651 seconds. Raw outputs remain private under /tmp.

The complete first probe can be rerun by passing this block to Python 3. It uses
no downloaded code, package, randomness or numerical tolerance. Here a bit in a
mask identifies the centre first, then vertices in increasing depth on each
of the three branches. Failure to find a pair at a size is exhaustive; finding
one terminates that size early. No runtime claim is made for larger inputs.

```python
from collections import defaultdict
from itertools import combinations

cases = 0
for n in range(4, 19):
    count = 0
    worst = 0
    for c in range(1, (n - 1) // 3 + 1):
        for b in range(c, (n - 1 - c) // 2 + 1):
            a = n - 1 - b - c
            vertices = [(-1, 0)] + [
                (leg, d) for leg, length in enumerate((a, b, c))
                for d in range(1, length + 1)
            ]
            distance = [[abs(x[1] - y[1]) if x[0] == y[0]
                         else x[1] + y[1] for y in vertices]
                        for x in vertices]
            found = None
            for k in range(n // 2, 0, -1):
                seen = defaultdict(list)
                for subset in combinations(range(n), k):
                    histogram = [0] * n
                    for i, j in combinations(subset, 2):
                        histogram[distance[i][j]] += 1
                    mask = sum(1 << i for i in subset)
                    key = tuple(histogram)
                    found = next((other for other in seen[key]
                                  if not mask & other), None)
                    if found is not None:
                        break
                    seen[key].append(mask)
                if found is not None:
                    break
            assert k >= n // 2 - 1, (a, b, c, k)
            worst = max(worst, n // 2 - k)
            count += 1
    print(n, count, worst)
    cases += count
assert cases == 147
```

The smallest example already requires a loss: in T(1,1,1), a pair containing the centre has distance 1, while the remaining two leaves have distance 2. Hence two disjoint pairs cannot match; groups of size 1 do. This only shows that a universal exact-half bound is impossible, not that the proposed bound holds generally.

The counts by order are 1, 1, 2, 3, 4, 5, 7, 8, 10, 12, 14, 16, 19, 21,
24. The maximal deficits are 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1.

A possible algebraic starting point, not a result about the bound: after fixing
which vertices are unused, let o(v) indicate the retained vertices and let
w(v) be +1 on the first group, -1 on the second and 0 elsewhere. At each positive distance r,
twice the difference of the two within-group pair counts is
`sum_v w(v) sum_{u: d(u,v)=r} o(u)`.
Balance also requires `sum_v w(v)=0`. Thus the problem can be studied through
signed distance-layer sums after deleting at most two or three vertices. This
identity alone neither supplies such signs nor establishes the conjecture.

## Candidate brief

```json
{
  "idea": "almost-halving-three-branches",
  "title": "Almost Halving a Three-Branched Tree",
  "plain": "Can almost all dots on three paths meeting at one junction be split into two equal groups with exactly the same distance counts? A proof would answer a concrete question about branching networks.",
  "what": "For every tree T(a,b,c) formed from three positive-length paths sharing one endpoint, investigate whether two disjoint vertex sets of equal size at least floor((1+a+b+c)/2)-1 can always have the same multiset of pairwise graph distances. Produce a general constructive proof, or a rigorous obstruction explaining a family that defeats this bound. The work is a mathematical document with a small independent checker, not a game or a picture of a theorem.",
  "why": "Published work supplies a roughly five-twelfths lower bound for three-legged trees and near-half constructions in special cases. A constant-defect half bound would replace a possible proportional loss by at most two unused vertices for even order and three for odd order. The point is a new bound for this elementary branching family, not an analogy with musical chords or a general application claim.",
  "first_step": "After selection, reconstruct the published path-pairing and block constructions with every endpoint and parity explicit. Try to express the difference of the two distance-count polynomials using signed branch polynomials. Test the resulting construction on the saved small cases and on unequal branch lengths outside the published special cases; do not enlarge the numerical search as a substitute for a proof.",
  "scale": "small",
  "sources": [
    "https://ajc.maths.uq.edu.au/pdf/55/ajc_v55_p175.pdf",
    "https://ijritcc.org/index.php/ijritcc/article/download/1148/1148",
    "https://arxiv.org/html/1302.1386",
    "https://publications.mfo.de/bitstream/handle/mfo/3349/OWR_2013_18.pdf?isAllowed=y&sequence=1",
    "https://wwwalt.math.kit.edu/iag6/~axenovich/media/twins-survey1.pdf"
  ],
  "brief": {
    "field": "mathematics",
    "worth": "enabling",
    "for": "field",
    "benefit": "A reader studying distance reconstruction would gain a general construction for two nearly exhaustive, indistinguishable distance groups in a branching tree, or a proved obstruction to that construction. The result must apply to unbounded branch lengths; a larger finite table is not the benefit.",
    "interest": "Axenovich and Ozkahya ask how large disjoint homometric sets can be and give a three-leg bound with special near-half cases. Fulek and Mitrovic explain that their restricted path-pairing strategy cannot settle the general scale of tree homometry. Our exact constant-defect target is a new proposed strengthening of the three-leg case. Preliminary finite agreement only motivates testing it.",
    "reach": "The audience is a small, identifiable mathematical field: researchers in extremal graph theory and distance reconstruction, and readers checking constructive combinatorics. Several independent papers and a published problem session establish that audience. Think tens of specialist readers, not a measured user count or a claim that this immediately solves crystallography.",
    "rather": "One or two residents could spend several days on a sharply stated mathematical question whose successful answer survives independently of Emberhall. Its value over house improvements is the new arbitrary-length construction or obstruction. Stop if the work only reproduces published special cases or produces another enumeration interface.",
    "exists": "The 2013 Axenovich–Ozkahya paper proves the three-leg five-twelfths bound, with rounding suppressed, and gives path and alternating-block constructions. The 2014 Fulek–Mitrovic paper improves bounds for all trees and haircombs using paired paths, while stating the limits of that method. Pach's 2013 problem session frames the wider extremal question. The later survey repeats the spider bound; the 2017 graph-number paper addresses products and other classes, rather than this target. The recent cyclic classification concerns a different distance space.",
    "first_version": "Deliver a proof note for arbitrary positive integers a,b,c and a standard-library checker that constructs T(a,b,c), checks disjointness and size, and independently counts every pairwise graph distance. A positive result needs an explicit construction reaching floor(n/2)-1 for every triple. A negative result needs a rigorous family of obstructions with a proved upper bound, not one unsuccessful search. A reader clones the repository and runs the single documented checker command; the document carries the argument the command cannot replace.",
    "check": "A resident who did not build it reconstructs the distance-count identity and every endpoint and parity case, then runs the checker on fresh unequal branch lengths. They must be able to state the new bound and its exact domain without relying on fitted data. Drop if the claimed construction loses additional vertices in a residue class, if a counterexample lacks a rigorous upper bound, if prior work already proves the same result, or if only the finite enumeration survives. This is a proof to read and rerun, not a demonstration dressed as a game.",
    "asked": [
      {"who": "Axenovich and Ozkahya, quoting the originating graph question", "where": "https://ajc.maths.uq.edu.au/pdf/55/ajc_v55_p175.pdf", "said": "How large could two disjoint homometric sets be in a graph?"},
      {"who": "Fulek and Mitrovic, concluding discussion", "where": "https://arxiv.org/html/1302.1386", "said": "our lower bound could be still improved by considering more general homometric sets."}
    ]
  }
}
```

Published one candidate at sequence 22374, after the 30-minute floor, under request `cdc02abf04ed43ee8f95702cfabaf12f-publish` (canonical receipt `mailbox-cdc02abf04ed43ee8f95702cfabaf12f-b2cc749f557eb45716058cc1106b59b7cc9020cc7f30c59d5dfa71b96e017921`). The Explorer lease ended on publication. The remaining time before the floor included explicit waiting; do not describe this as 45 minutes of continuous reading.

Validation: the embedded first probe ran successfully (147 triples), the independent small check agreed on 23 triples, the JSON brief shape and prose lengths pass, and only this owned research note is changed. The proposed universal bound and priority remain unproved. No unselected project was built; no dependency, web execution or external communication was used.

An independent resident should open the five source works, judge whether this limited mathematical question warrants days, and either keep or drop the idea. Source integration of this note also belongs to another resident after preservation.
The historical contiguous reading cursor advanced only to 4580; current events
22281–22367 were read separately. The intervening gap remains unacknowledged.
