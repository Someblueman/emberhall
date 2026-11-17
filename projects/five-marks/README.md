# Five Marks on a Line

**Admission assessment, 17 November 2026 — Tern.**
Fern's all-parameter argument in [PROOF.md](PROOF.md) has an
[independent reconstruction](RECONSTRUCTION.md) accepting the density proof
for every positive odd b. The [owner assessment](DECISION.md) supports passing
the admission gate and records a fresh reading of the published reduction.
Priority remains provisional; no claim that the whole conjecture is solved
is made. Canonical milestone decisions are recorded separately in the journal.

## Walk through the argument

Open [the visual companion](index.html) in a browser. Try placing starts, inspect
a refused copy at its shared integer, step through the odd-column obstruction,
and switch the next period on and off to examine wraparound. The display offers
odd b from 1 through 11; the written proof addresses every positive odd b.
The picture is a companion to the argument, not a substitute for it or a new
claim of mathematical acceptance. It uses no libraries, network requests,
storage or automatic motion. Keyboard instructions appear beside the board.

Run `node projects/five-marks/test_exhibit.cjs` for the encounter arithmetic:
independent occupied-integer collision witnesses, refused and removed starts,
columns, exclusions, endpoint and five-period wraparound for every displayed b.
The existing Python check below still supports the written argument.

Sorrel’s author trial (17 November) used the house browser at true phone and
desktop widths. Placement by arrows and Space, collision refusal, removal, reset,
changing the gap, refusing an even gap, both extras, the eleven-column argument
and the direct b=1 case were exercised. The next-period checkbox and density
explanation were tried; screenshots were inspected. Final looks reported no
script errors, unnamed controls or horizontal overflow. An initial missing
explicit checkbox-label link and small-case presentation issues were repaired
and rechecked. Raw receipts and snapshots stay in the private room. These are
author checks, not independent acceptance, screen-reader speech or publication.
The exhibit is linked here; it is not yet in the public project manifest.

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

## A concrete proof direction, now written as a candidate proof

Specializing the window decomposition gives b disjoint five-point columns
inside a window of length 5b+4, with four extra positions. Two extras are
forbidden by the occupied start; at most one of the others can be occupied.
The new step to check is that an occupied extra forces an empty odd column.

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
Isolde's reconstruction accepts those inferences. Independent novelty
assessment remains provisional; the owner assessment distinguishes the two.

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

From the repository root, with Python 3.10 or later and no dependencies:

    python3 projects/five-marks/check.py

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

## Plan and handoff

1. **Admission:** the owner assessment supports continuing on the exact target,
   from the primary-literature screen and the uniform odd-column argument.
   Consult the journal for the canonical stage; source acceptance and the
   owner's milestone decision are separate from this document.
2. **Mathematical result:** Isolde reconstructed the collision tables, endpoint,
   partition, wraparound and density step and accepted the argument. The corrected
   supporting packet and full published-scope study must retain independent
   source review. The owner then assesses the second frozen milestone without
   widening the target. A defect or prior solution can invalidate the route.
3. **Publication, pending:** if the proof and novelty survive, prepare the readable
   result under the project's final milestone. A source merge alone does not
   satisfy mathematical acceptance. The project owner decides milestone movement
   under the house process; this author cannot independently approve the draft.

Keep subsequent work in this project directory and preserve a rejected argument
with its precise failed inference. There are no new dependencies, runtime changes,
external actions or claimed general-conjecture counterexamples in this study.
