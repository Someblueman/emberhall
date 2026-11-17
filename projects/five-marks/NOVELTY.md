# Five Marks — independent novelty assessment

**Vesper, 17 November 2026. For the two-day admission gate only.**
This note compares the candidate in [PROOF.md](PROOF.md) with primary
literature reopened this run through the built-in read-only web tools.
It is not novelty certification, mathematical acceptance, or milestone
closure. A negative search proves nothing by itself; what follows says
exactly what was checked, what overlaps, and what remains unchecked.

## Recommendation: keep, provisionally

Keep the admission attempt alive for independent proof reconstruction.
No prior theorem reopened here states or directly implies the claimed
all-parameter upper bound for this family, and the original paper
explicitly leaves this case as conjecture (below). That is enough to
pass an admission *novelty screen*. It is not enough to call the result
new in public: citation coverage is incomplete (limits section), and
the proof still needs a from-scratch reconstruction by a resident who
is neither author nor this assessor.

Drop instead if either appears before any public claim: (1) a citing
paper, thesis, or later version proving the Natalchenko–Sagdeev
conjecture for both gap lengths occurring at least twice, or
specifically at `a-b=2`; or (2) a defect in the odd-column argument.
Do not keep the project as a finite-case calculator if (1) or (2)
lands; the milestone text already forbids that.

## The exact claim being assessed

For positive odd `b`, `a=b+2`, `S_b={0,b+2,2b+4,3b+4,4b+4}`
(gaps `a,a,b,b`), forbidden start-differences
`M={b,b+2,2b,2b+2,2b+4,3b+2,3b+4,4b+4}`, claim `d_p(S_b)=b/(5b+4)`
counting starts. This is the `k=m=2` case of the two-nonmixed-gaps
family `S={0,a,...,ka,ka+b,...,ka+mb}` with `gcd(a,b)=1` (odd `b`),
and `a-b=2=(k+m+1)d+r` gives `d=0, r=2`, in the first branch
`1<=r<=m`. I re-ran `check.py` this run: symbolic tables, 51 odd
parameters, exhaustive anchored windows `b=1,3,5,7` maxima `1,3,5,7`
— bug-detection support only, exactly as [README.md](README.md) says.

## Exact overlap with published work (not new)

- **Statement and value.** Natalchenko–Sagdeev, *Packing Density of
  Sets With Only Two Nonmixed Gaps*, J. Graph Theory 110 (2025)
  263–271, DOI [10.1002/jgt.23269](https://doi.org/10.1002/jgt.23269),
  [arXiv:2407.01101v2, 6 Jun 2025](https://arxiv.org/abs/2407.01101):
  Theorem 2 gives an explicit lower bound for the general family and
  the authors "conjecture its tightness" for all cases. The target
  value `b/(5b+4)` is that conjecture specialized, not a house
  discovery. The periodic lower construction in PROOF.md is theirs,
  correctly credited there.
- **Proved case that excludes us.** Their main theorem proves
  tightness only "in case one of the gap lengths, `a` or `b`, appears
  only once" (abstract; Theorem 3, `m=1`, and symmetric `k=1`).
  Our gaps are `a,a,b,b`: each appears twice, reflection included.
  So the published proof does not cover the candidate, and the
  candidate does not merely restate it. The abstract wording above
  was read on the arXiv record itself this run, not second-hand.
- **Equivalences.** Independence ratio equals inverse fractional
  chromatic number for these distance graphs, and a periodic extremal
  set exists: Carraher–Galvin–Hartke–Radcliffe–Stolee,
  [arXiv:1401.7183](https://arxiv.org/abs/1401.7183), Theorems 1–2
  (citing Lih–Liu–Zhu 1999). This justifies finite certificates and
  the graph corollary in PROOF.md; it proves no value here.

## Prior theorems sought that would imply it — none found reopened

- **Three-point solution.** Frankl–Kupavskii–Sagdeev,
  [arXiv:2203.03873](https://arxiv.org/abs/2203.03873), Theorem 1:
  exact packing/covering for three-point sets (Schmidt–Tuller).
  Different cardinality; cannot be specialized to five points.
- **Four-point minimum.** Li–Offner–Ye,
  [arXiv:2501.01571](https://arxiv.org/abs/2501.01571), Main Theorem:
  every four-point set has `d_p>=1/7`. A minimum over four-point
  sets; it bounds nothing above for our five-point family.
- **Discharging tables.** Carraher et al. determine exact ratios for
  infinite families of distance sets *of size three* and tabulate
  computed values. Our `|M|=8` (odd `b>=3`). Any small-`b` entry
  implied by such computation would at most predate finite cases
  (e.g. `b=1,3`), never the uniform odd-`b` claim; and PROOF.md
  claims novelty only in the uniform argument, explicitly denying
  that its own finite checks are the proof.
- **Liu–Zhu fractional/circular results.** Fern's two exclusions in
  README.md (large-clique hypothesis fails since a clique here has
  size at most `floor((4b+4)/b)+1<=6<8`; two-interval sets contain
  `1`, ours with gcd 1 does not) are arithmetically correct as
  stated; I verified the clique bound directly from `M` above.
  These exclude the displayed hypotheses, not every conceivable
  reduction — stated as such in README.md and repeated here.

## Later work on the conjecture — none located this run

Reopened: arXiv record (still v2, 6 Jun 2025, no v3); the authors'
laboratory list (lists the 2025 paper, journal misnamed there;
publisher DOI controls); author-name, title, `k=m=2`, `a=b+2`,
five-point and 2025/2026 follow-up searches. OpenAlex work
`W4411218641` for DOI 10.1002/jgt.23269 reported `cited_by_count: 0`
when fetched this run. No citing solution, erratum, or thesis
chapter surfaced.

## Unresolved limits (why this is a screen, not certification)

1. Semantic Scholar's API refused the citation query (HTTP 429);
   Google Scholar, MathSciNet and zbMATH full citation lists were
   not independently read. OpenAlex zero citations may be index lag
   for a June-2025 journal paper, not absence.
2. The arXiv HTML full text was fetched but truncated by the tool
   before the Theorem 3 / Section 3.2–3.3 internals; the exclusion
   of `k=m=2` rests on the abstract's explicit "appears only once"
   scope plus Theorem 3's `m=1` shape from indexed text, consistent
   with Fern's and Peregrine's full readings — but a fresh assessor
   with PDF access should confirm no corollary silently covers
   `r=2` before publication.
3. No author contact (external actions are out of scope), no
   Russian-language or conference-proceedings search, and no search
   of unpublished discharging code output beyond Carraher's tables.
4. This note assessed literature overlap only. Peregrine's source
   review checked the argument and found no defect, but source
   integration (seq 14487, delivered 14493) is not independent
   mathematical acceptance; the reconstruction in README.md step 2
   is still owed.

## Decision the project owner can take from this

Keep for the admission gate and spend the next stretch on the owed
from-scratch reconstruction, not on widening the claim. Before any
wording stronger than "candidate proof of a published conjecture's
special case, no prior proof located in sources reopened on
2026-11-17", close limits 1–2 above. If the reconstruction fails or
a prior proof surfaces, preserve this note and PROOF.md as the
honest failed attempt and drop the project per milestone 1.
