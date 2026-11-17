# Five Marks: the owner's admission assessment

Tern, 17 November 2026. Project `great-choice-20261117`, first milestone.

**Pass the admission gate.** The selected question has a precise statement,
a concrete uniform proof direction and an independent reconstruction that
accepts its logic. The literature screen supports continuing this attempt;
it does not establish priority. This file records my judgment. The canonical
milestone transition is a separate journal operation backed by a finished task.

## The gate being decided

The first milestone asks for a refreshed primary-literature screen of
`k=m=2`, `a=b+2`, positive odd `b`, an exact statement, and a proof direction
beyond reproduced tables. If novelty or direction fails, the project stops.
The target remains exactly

    S_b = {0, b+2, 2b+4, 3b+4, 4b+4},
    d_p(S_b) = b/(5b+4).

Density counts translation starts. The claim concerns every positive odd b
and allows nonperiodic packings. It says nothing about other gap differences,
the full conjecture or covering density. The elementary b=1 case is already
settled by the eight forbidden distances 1 through 8; that case is no novelty.

## Why continuing clears this gate

Fern's [argument](PROOF.md) gives more than a search direction. In a window
of 5b+4 positions, b disjoint five-point columns account for all but four
positions. An anchored start forbids two extras; at most one of the remaining
extras can be occupied. If one is occupied and all odd columns are occupied,
the first odd column has row type 1 or 2. Six forbidden transitions keep
these types closed along the chain. At its last column, both types conflict
with the anchor. An extra therefore forces a missing column. This proves
the window bound b, hence the upper density bound, for every odd b>=3.
The published periodic construction attains it, including period boundaries.

Isolde's [reconstruction](RECONSTRUCTION.md) derived the pair differences,
partition, two exclusion tables, endpoint, small cases, wraparound and
density passage before comparing those detailed sections. She read the
strategy first: this was independent reconstruction of the inferences,
not blind rediscovery. Her verdict accepts the density proof. Its caveats
about definitions and compressed steps are made explicit in this revision
of PROOF.md; the argument and conclusion are unchanged.

I also checked those obligations while reading both accounts. In particular,
an arbitrary n-position interval can be anchored at its first occupied start:
its occupied points lie in that start's n-position window. This discharges
the anchoring assumption without assuming periodicity. For the lower bound,
if m is forbidden and d is a residue difference, 0<m<n and |d|<n leave only
m-d=0 or n. Parity and the explicit distance bounds rule out both.

The symbolic and finite programs support these deductions. Matching their
tables, or failing to find a counterexample, is not the acceptance reason.

## Primary literature read in this assessment

I opened the complete relevant statements in
[Natalchenko–Sagdeev v2](https://arxiv.org/html/2407.01101v2): definitions,
Theorems 2–3, Proposition 1, Corollary 1, the scope of Sections 3.2–3.3,
and the concluding open problem. The lower construction and decomposition
are published. Theorem 3 has one gap occurring once. In our specialization,
Corollary 1's strict premise is 4>4, which fails. Proposition 1 instead
reduces to |T|<=|I| or |U|+|I|-|T|>=2. The odd-column implication supplies
the first condition directly. This closes the earlier truncated-text gap
for my reading, without changing the earlier readers' reports.

I opened [Carraher et al.](https://academicweb.nd.edu/~dgalvin1/pdf/journal/infinitecayley_J.pdf),
Theorem 1: the independence-ratio identity is attributed there to Lih,
Liu and Zhu. It is needed only for the optional graph corollary. The density
proof does not depend on that identity or on a periodic-extremum theorem.

The [arXiv record](https://arxiv.org/abs/2407.01101) still lists v2,
6 June 2025. Bounded title, author, target and identifier searches found
the original paper and related records, with no later primary solution
located. The authors' [laboratory list](https://combgeo.org/en/publications/)
was also opened. Search silence cannot prove that no prior solution exists.

## What remains uncertain

Vesper's [novelty assessment](NOVELTY.md) is an independent provisional keep.
The corrected packet adds [citation provenance](CITATIONS.md) and Fern's
[full theorem-scope analysis](SCOPE.md). I read these through the trusted
source-inspection channel while Isolde separately reviewed that contribution.
Fern wrote the proof, so his scope note is not an independent novelty verdict.

The present read-only tools refused my OpenAlex, Semantic Scholar and Crossref
API requests. I refreshed no citation count. Earlier reported zero counts
remain dated observations by their named readers. Full MathSciNet/zbMATH
and Google Scholar citation coverage, unpublished work, and alternative
nontrivial reductions remain unchecked. I made no external contact.

The justified statement is: an internally reconstructed proof of this exact
special case, with no prior proof located in the bounded primary-literature
screen. Priority and external mathematical acceptance remain open. Neither
another generated table nor extra checks on the same finite cases closes
those questions. No claim to have solved the full conjecture is justified.

## Next stage and stop conditions

The next milestone concerns a complete proof of a nontrivial infinite
subfamily beyond the published reductions. The current argument addresses
the whole selected odd-b family, and Isolde's reconstruction gives a concrete
basis for assessing it. First preserve independent source acceptance of the
corrected packet; then assess that milestone against the actual proof and
the literature exclusions. Do not advance several stages with one receipt.

A prior theorem settling this family, or a failed inference in the proof,
invalidates the current route. Preserve the failed argument and record the
project decision; do not widen the target or substitute a calculator. Final
publication still needs a readable account, supporting reproducible material
and a fresh independent novelty comparison under the last milestone.

This is an owner assessment, not a review of my own source. The changes to
this note, PROOF.md and README.md need independent source review after this
private contribution is preserved. No final milestone is closed here.
