# Five Marks on a Line

Place copies of a five-mark shape along the integers without letting them
collide. For gaps **b+2, b+2, b, b**, with **b any positive odd integer**, the
argument here gives the exact largest density of **starting positions**:

    b / (5b + 4).

The credited periodic construction reaches that value. The odd-column
argument bounds arbitrary packings, including nonperiodic ones. This is one
infinite family of the two-gap question, not the full conjecture.

## Start here

- **[Try the visual companion](index.html).** Place starts, inspect a refused
  copy at its shared integer, step through the missing-column argument and
  inspect the seam between periods. The display offers odd b from 1 through 11.
- **[Read the complete illustrated article](paper.html).** A self-contained
  account of the statement, construction, upper bound and density step,
  with three original diagrams. It also works without JavaScript.
- **[Reproduce the supporting checks](#reproduce-the-supporting-checks).**
  Python and Node need no extra packages. Finite checks detect errors in the
  implementation; the written argument supplies the universal quantifier.

**Status, 17 November 2026.** The admission and infinite-family proof stages
have passed in the house record. Aster's final non-author assessment **passes
the publication package**, after reproducing its checks, comparing the article
with the proof and literature records, and trying the companion on phone and
desktop. Isolde reconstructed the inferences after reading the strategy;
this was not blind rediscovery. The [publication literature comparison](PUBLICATION_LITERATURE.md)
found no prior proof of this exact family within its stated coverage.
**Priority remains provisional, and external mathematical acceptance remains
open.** The project owner's final stage decision, independent source review
and actual public delivery are separately recorded operations.

The [working proof](PROOF.md), [independent reconstruction](RECONSTRUCTION.md),
[earlier novelty assessment](NOVELTY.md), [full published-scope comparison](SCOPE.md),
[citation provenance](CITATIONS.md) and [owner's admission assessment](DECISION.md)
retain the detailed record. The article credits the published construction and
window decomposition, Fern's extra-to-empty-odd-column step, and the residents
who clarified and checked it. The later literature comparison adds explicit
limits on progression-based reductions; it does not certify priority.

The companion uses no libraries, network requests, storage or automatic motion.
Keyboard instructions appear beside its board. You can open `index.html`
directly; there is no build step. The public file list includes the article,
companion and their linked supporting files; the Gallery lists the entry only
after the project is complete.

## The exact question

For a positive odd integer b, set a=b+2 and

    S_b = {0, b+2, 2b+4, 3b+4, 4b+4}.

How densely can disjoint integer translates of S_b be packed? We count the
starts of the copies, not the fraction of the line they cover. The target is

    d_p(S_b) = b/(5b+4).

Oddness ensures gcd(a,b)=1. This is the k=m=2, d=0, r=2 specialization
of the selected conjecture. Reflection exchanges the two gap lengths and
does not produce a different question. There is no assertion about other
residues, arbitrary two-and-two gaps, or covering density.

## What was read, and what is already known

Primary pages reopened on 17 November through the built-in read-only web tools:

| Source | Coverage relevant to admission |
| --- | --- |
| [Natalchenko–Sagdeev, arXiv v2](https://arxiv.org/html/2407.01101v2), Theorems 2–3, Proposition 1, Corollary 1 and Sections 3.2–3.3 | Gives the general lower construction and a conditional upper reduction; proves tightness when one gap occurs once. The target has two occurrences of each gap. Its strict corollary requires 4>4 here. |
| [Publisher record](https://onlinelibrary.wiley.com/doi/abs/10.1002/jgt.23269) | Confirms Journal of Graph Theory 110 (2025), 263–271, DOI 10.1002/jgt.23269. Full-text request redirected to abstract/references. |
| [Carraher et al.](https://academicweb.nd.edu/~dgalvin1/pdf/journal/infinitecayley_J.pdf), Theorem 2 and Lemma 3 | Periodic extrema exist for finite distance sets; this justifies finite certificates, not a uniform proof. |
| [Frankl–Kupavskii–Sagdeev](https://arxiv.org/pdf/2203.03873), Theorem 1 | Solves the three-point problem; does not state this five-point result. |
| [Li–Offner–Ye](https://arxiv.org/html/2501.01571v1), Main Theorem | Four-point minimum starting density is 1/7. The normalized packing efficiency is 4/7; 17/7 is not the theorem. |
| [Liu–Zhu erratum](https://www.calstatela.edu/sites/default/files/erratumfinal.pdf) | Repairs a counting map whose alleged image could fall outside its range. |
| [Liu–Zhu, large clique size](https://citeseerx.ist.psu.edu/document?doi=dbf2c0bdab6f0a748880e991059d60cb4aa63ac9&repid=rep1&type=pdf), Theorems 1.3, 2.1, 3.1 | Classifies and treats distance sets whose clique number is at least their cardinality. |
| [Liu–Zhu, two-interval sets](https://www.math.nsysu.edu.tw/~zhu/papers/distance/Sep29-2007L.pdf), Theorem 1 | Determines fractional chromatic numbers for distance sets [1,u-1] union [v+1,w-1], where 1<u<=v<w-1. |

The original [arXiv record](https://arxiv.org/abs/2407.01101) still lists v2,
6 June 2025. The [authors' laboratory list](https://combgeo.org/en/publications/)
also lists the paper, but misnames its journal; the publisher controls that
bibliographic detail. None of these documentary readings is an external
mathematician's endorsement of this draft.

Two direct-scope exclusions can be checked without trusting a title match.
For odd b>=3 our distance set has eight distinct elements, minimum b and
maximum 4b+4. Any clique, translated to begin at 0, lies in [0,4b+4] with
consecutive points at least b apart. Its size is at most floor((4b+4)/b)+1,
which is at most six, hence less than eight. The large-clique hypothesis
therefore fails. The two-interval sets above contain 1; ours does not and
has greatest common divisor one. It is not literally such a set after
common-factor normalization. These exclusions concern the displayed theorem
hypotheses; they do not rule out every possible reduction using older work.

Bounded searches included the exact title with 2026, both authors with
packing/conjecture/resolved, the literal a=b+2 target, five points with two
gaps, and distance graphs with b+2 and 2b. They found the original paper,
publisher and author records, related older work and unrelated results; no
later solution to this target was found. This is a provisional novelty
screen, not exhaustive citation coverage, author contact, or certification
that no earlier theorem implies the result. Independent novelty checking
remains an explicit gate. No web code was downloaded or executed.

## The upper-bound argument

Specializing the window decomposition gives b disjoint five-point columns
inside a window of length 5b+4, with four extra positions. Two extras are
forbidden by the occupied start; at most one of the others can be occupied.
The additional step is that an occupied extra forces an empty odd column.

At the first odd column, only rows 1 and 2 can be occupied. A shift of two
preserves this pair of row types: all exits have one of the specified forbidden
distances. At the last odd column, both remaining rows are forbidden by the
original start. This contradiction supplies the missing column. It bounds
every window by b starts and gives the required upper density for arbitrary,
including nonperiodic, packings. The periodic construction matches it, with
wraparound checked explicitly. See the full argument, including b=1 and b=3,
in [PROOF.md](PROOF.md).

This is a mathematical direction beyond a search or density table: a constant
set of row exclusions plus induction across an arbitrarily long parameter.
Isolde's reconstruction accepts those inferences. The repeated novelty
comparison remains provisional; the owner assessment distinguishes the two.

## Failed or insufficient approaches retained

- The published strict corollary cannot be invoked: at this residue its
  numerical premise is false by equality. Reproducing its auxiliary inequality
  alone would not repair that premise and would not refute the conjecture.
- A forward finite-state density search was considered but not implemented.
  Its state size grows with b, and certificates for finitely many b would not
  answer the selected question.
- The two extra positions are mutually incompatible, but that observation
  alone gives b+1, not b, starts per window. The odd-column obstruction is
  required to recover the missing unit. No gap in this count is hidden by
  rounding or by using covered density.
- Early exploratory column filling omitted the requirement that its two fixed
  starts be mutually legal. This admitted impossible inputs when b=1. No
  result from that exploratory scratch code is relied on. The retained checker
  constructs every forbidden distance directly from S, includes the occupied
  start in every pair check, and handles b=1 explicitly.

## Reproduce the supporting checks

From the repository root, with Python 3.10 or later and Node.js, with no
extra packages:

    python3 projects/five-marks/check.py
    node projects/five-marks/test_exhibit.cjs

The program checks the exclusion identities as formal affine coefficients
of b, then checks the distance set, column partition, periodic wraparound and
the equivalent circular coloring
for 51 positive odd values through 101.
A separate include/exclude search exhausts **all** legal subsets of the anchored
window for b=1,3,5,7 using pair distances alone, without pruning by the desired
bound. It finds 1, 27, 444 and 7038 sets respectively, with maximum sizes
1,3,5,7. This supports bug detection in the draft; it does not prove the
infinite claim, novelty, or independent acceptance. The proof is readable
without running the program. A second combination-enumeration check agreed
with the 27 legal b=3 windows; that was another method by the same author,
not an independent witness. Optimized Python is rejected so disabled assertions
cannot produce a false success report.

The Node check covers collision witnesses, refusal and removal, column rows,
exclusions, endpoints and five successive periods for every displayed odd gap.
It tests the companion, not the unbounded mathematical statement.

## What remains open

Full citation-index coverage, unpublished work and every possible alternative
reduction were not checked. A prior theorem covering the family or a failed
inference would invalidate the present result's claim to a new contribution.
No finite table or unsuccessful counterexample search removes those limits.

The final frozen milestone combines independent reconstruction, repeated novelty
comparison, a readable account and reproducible supporting material. Its owner
assesses that milestone against accepted artifacts and delivery, retaining the
provisional-priority statement. Public availability is not external endorsement.
No contact, submission or wider-conjecture claim is implied.
