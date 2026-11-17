# Five Marks: a further literature comparison

Mallow, 17 November 2026. I proposed the original idea, but wrote neither
the searches nor the odd-column proof. This is a literature assessment,
not a second proof reconstruction, priority certificate or milestone decision.
I read the existing proof before this comparison; no blind discovery is claimed.

**No earlier proof of the selected family was located in this bounded search.**
The direct published reduction still leaves an obligation that Fern's argument
addresses. Two additional comparisons below do not supply the missing upper
bound. Full citation coverage remains unavailable: this work does **not** close
that gap in NOVELTY.md or authorize an unqualified claim of novelty.

The target remains, for every positive odd integer b,

    S = {0,b+2,2b+4,3b+4,4b+4},       d_p(S) = b/(5b+4),
    M = {b,b+2,2b,2b+2,2b+4,3b+2,3b+4,4b+4}.

Density counts starts, allows nonperiodic packings, and is not covered density.
The elementary b=1 case is not a novelty claim.

## Direct comparison, reopened in full

I read the complete relevant statements in Natalchenko–Sagdeev's
[v2 HTML](https://arxiv.org/html/2407.01101v2): Theorems 2–3, Definition 1,
Proposition 1, Corollary 1, the scope declarations of Sections 3.2–3.3,
and Section 4. Theorem 2 supplies the lower construction; Theorem 3 has one
gap occurring once. Section 4 still calls tightness of Theorem 2 open.

My substitution a=b+2, k=m=2 gives d=0, r=2, n1=5b+4, n2=5b+6.
Proposition 1's alternatives are |T|<=|I| or |U|+|I|-|T|>=2.
Corollary 1 separately requires 4>4 as well as its counting inequality;
the strict premise fails. The later two sections expressly assume m=1
and k=1, respectively. They do not state the two-and-two case. Reflection
exchanges the gaps without changing their multiplicities. Thus invoking
the published corollary directly would not prove this target.

This independently confirms the direct scope analysis in SCOPE.md. It does
not exclude every combination of older results or every graph transformation.
The [arXiv record](https://arxiv.org/abs/2407.01101) still lists v2,
6 June 2025. The [publisher record](https://doi.org/10.1002/jgt.23269)
identifies Journal of Graph Theory 110, 263–271 (2025); its full-text route
returned abstract/references, so the full statements above were read on arXiv.

## A general lattice theorem does not give the target value

I opened Candela–Chamizo–Córdoba,
[On sets with missing differences in compact abelian groups, v2](https://arxiv.org/html/2408.09301v2)
(15 September 2024), Theorems 1.3, 2.5 and 5.1 and Proposition 3.4.
Their explicit formula in Theorem 1.3 requires a relation lattice of rank
one. Theorem 5.1 guarantees a periodic optimum in a finite-group-times-Z
setting. These are different assertions.

Here is my specialization. List M as m1,...,m8. For irrational theta, the
eight circle elements theta*mi modulo 1 are nonzero and distinct, even up
to sign, and their relation lattice is exactly

    Lambda = {z in Z^8 : sum(mi*zi)=0}.

Indeed, an integer multiple of irrational theta is an integer only when
that multiple is zero. Since gcd(b,b+2)=1, the map Z^8 -> Z with those
coefficients is onto. Its kernel has rank seven, and its quotient is Z;
the images of the eight basis vectors are precisely M. Theorem 2.5
therefore identifies the corresponding densities, but Theorem 1.3's
rank-one premise fails. Theorem 5.1 gives existence of a periodic optimum,
not b/(5b+4). Replacing the eight distances by the two gap generators
would change which pairs are forbidden and would be a different problem.
This excludes that direct formula application, not all uses of the paper.

## A small additional subset exclusion

Gupta–Tripathi's [1999 three-page paper](https://web.iitd.ac.in/~atripath/publications/density_M-sets_AP.pdf)
was opened in full. Its theorem determines density for a missing-distance
set that is an arithmetic progression. Pandey–Srivastava's
[2022 publisher abstract](https://doi.org/10.11650/tjm/210702), available as
indexed primary text, names three- and four-distance families. The direct
publisher body returned a protection page, so I do not claim to have read
all its theorem statements.

The following exclusion is my deduction, not a theorem quoted from either
paper. For odd b>=3, M has no four-term arithmetic progression.
To see the large cases, write each member uniquely as (i+j)b+2i, where
0<=i,j<=2 and (i,j)!=(0,0). For any consecutive triple in a progression,

    ((i0+j0)-2(i1+j1)+(i2+j2))*b = -2(i0-2i1+i2).

The right side has absolute value at most eight. For b>=9 the integer
coefficient of b must vanish, hence both i and j have zero second
difference. Four such points would have coordinates in arithmetic
progression inside {0,1,2}. Their integer common steps must both be zero,
contradicting distinctness.

For b=3,5,7, checking the 56 triples of the displayed eight-element M
gives exactly the following five three-term progressions:

    (b,2b+2,3b+4),       (b+2,2b+2,3b+2),
    (2b,2b+2,2b+4),      (2b,3b+2,4b+4),
    (2b+4,3b+4,4b+4).

None extends at either end. I checked these three finite lists by direct
combination enumeration; they are the finite exceptions in the argument,
not finite tests standing in for the universal density proof.

Consequently any P subset M consisting of one arithmetic progression and
at most one extra distance has at most four members. Any distance set
with at most four members has independence ratio at least 1/5: greedily
color each finite interval with five colors in increasing order, take a
diagonal limit to color Z, then one fixed color has upper density at
least 1/5 along infinitely many centered intervals. Since

    1/5 > b/(5b+4),

a single subset bound mu(M)<=mu(P) of that shape cannot attain the target.
The same reasoning excludes a single subset with at most four distances
from the 2022 families. Scaling preserves progression shape and density.
This does not exclude unions of several progressions, combined bounds,
homomorphisms, or the rest of any incompletely read paper.

## Other promising leads

Kupavskii–Popova's [Tilings of Z with multisets of distances, v2](https://arxiv.org/html/2304.05082v2)
was opened through its definitions and main statements. Its tiles may permute
the gaps of a given multiset. Our translates must preserve the ordered gaps
a,a,b,b. A tiling by a larger family of shapes does not give the required
upper bound for packings of this one shape. No claim about all possible
consequences of its proof is made.

The indexed author text of the [2009 Integers conference paper](https://web.iitd.ac.in/~atripath/publications/Motzkin2.pdf)
specifies three missing differences. The [2015 journal repository abstract](https://www.dml.cz/handle/10338.dmlcz/144179?show=full)
likewise specifies {a,b,a+nb}. Single subsets of these sizes are covered by
the cardinality bound above; their inaccessible full texts remain unassessed.
Huang's [2025 dissociation paper](https://www.dmgt.uz.zgora.pl/publish/pdf.php?doi=2563)
surfaced through a citation lead: its indexed primary abstract studies sets
inducing maximum degree at most one, rather than independent sets. The body
timed out, so I leave its possible upper-bound consequences unassessed.
None of these leads is evidence of a later proof of our exact family.

## Later work and access limits

- Searches used both spellings of the exact title, its arXiv identifier and
  DOI, the two author names, the literal expressions `5b+4` and `3b+4`,
  and Russian author names with packing/density terms. No later primary
  proof of this exact family surfaced. Irrelevant hits were not evidence.
- The authors' [Russian laboratory publication list](https://combgeo.org/publications-ru/)
  lists the original paper, with a mistaken journal name; the publisher
  record above controls. This is a selected list, not a complete bibliography.
- The [DGD 2024 program](https://dgd.math.bme.hu/program.html) was readable
  as indexed primary text. Natalchenko's abstract specifies
  S={0,a,a+b,...,a+kb}: one gap occurs once, so it does not announce this
  two-and-two result. Direct program fetch returned 404 and I did not
  obtain its slides. This is one conference abstract, not a proceedings census.
- Exact-title searches restricted to MathSciNet and zbMATH supplied no
  usable target record. Their direct title/DOI searches were inaccessible.
  Google Scholar's exact-title query was also inaccessible.
  OpenAlex's retained work identifier and DOI route, Crossref's work route,
  and Semantic Scholar's arXiv citation route were also inaccessible.
  **No citation list or citation count was refreshed.** Search snippets
  and an old reported zero count cannot substitute for those lists.
- Primary author-hosted 2009 and 2011 missing-differences PDFs and the
  2015 Mathematica Bohemica PDF did not yield full text here. Indexed
  fragments of the 2011 paper give bounds for further progression-related
  sets, but I leave those parts unassessed. ORCID direct pages required
  JavaScript. No subscription, account, external contact or shell web access
  was used.

## Wording supported by this work

Use: **An internally reconstructed proof of the stated odd-b special case
of a published conjecture; no prior proof was located in the bounded sources
reopened on 17 November 2026. Priority and external mathematical acceptance
remain open.** Keep credit for the question, lower construction and window
decomposition with Natalchenko–Sagdeev, and for the odd-column step with Fern.

Do not turn failure to fetch citation services into a claim of zero citations,
or this negative search into proof of priority. A prior solution or a failed
inference still invalidates the route. The project owner decides milestones;
another resident must review this new source contribution. I changed no proof,
code, exhibit, earlier assessment or public project status.
