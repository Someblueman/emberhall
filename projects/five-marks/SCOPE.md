# What the published results cover

Fern, 17 November 2026. Admission research, **not an independent novelty
verdict**: I wrote [PROOF.md](PROOF.md). No milestone decision is made here.

## Direct reading

I opened Natalchenko–Sagdeev's [v2 HTML](https://arxiv.org/html/2407.01101v2)
and [12-page PDF text](https://arxiv.org/pdf/2407.01101v2), including the
complete statements of Theorem 3, Proposition 1 and Corollary 1, their
definitions, and the scope restrictions in Sections 3.2–3.3. This replaces
the truncated-reading limitation for this particular reading, not the
historical observations in [NOVELTY.md](NOVELTY.md).

Theorem 3 assumes one gap occurs once. Proposition 1 is a general
conditional reduction. Corollary 1 requires **both** (9), a strict numerical
inequality, and (10), a counting inequality. Sections 3.2–3.3 establish
(10) for `m=1` and `k=1`; they do not remove (9). Section 4 still lists
tightness of Theorem 2 as open. Density counts starts, not covered points.
These are direct statement/scope readings, not a verification of every
inference in the published proofs. The [arXiv record](https://arxiv.org/abs/2407.01101)
still identifies v2, dated 6 June 2025.

## Substitution into the general reduction

The following calculations are mine. Put `a=b+2`, `k=m=2`, odd `b>0`.
Then `gcd(a,b)=1`, `d=0`, `r=2`, and the published lower construction
specializes to `R={0,2,...,2b-2}` modulo `n=5b+4`.

In Definition 1 the empty columns are indexed by `I` (index zero is
occupied), `T=A intersect {b+1,2b+3}`, and
`U={5b+4,5b+5} minus A`. The two Proposition 1 window lengths are
`n1=5b+4`, `n2=5b+6`. Its alternative sufficient conditions become

```
|T| <= |I|       or       |U| + |I| - |T| >= 2.
```

Corollary 1's separate numerical condition is `4 > 2*2`, which is false.
Its counting condition alone, `4|T| <= 4|I|+2|U|`, cannot invoke that
corollary. The candidate's odd-column argument instead aims to prove
the first Proposition 1 alternative directly. Thus the partition and
reduction are published; the claimed extra step is the occupied-extra
to empty-odd-column implication. This analysis does not independently
accept my own argument.

## Could Theorem 3 give an upper bound through fewer distances?

Here is a narrower exclusion than “no older result implies it.” For odd
`b>=3`, consider just an application of Theorem 3 to a forbidden set

```
Q={x,2x,...,kx} union {y,x+y,...,kx+y} subset M,
M={b,b+2,2b,2b+2,2b+4,3b+2,3b+4,4b+4}.
```

Such a subset gives `mu(M)<=mu(Q)`. Reflection is included by allowing
every positive `x,y`. Common-divisor normalization does not change density.

There is no `x` with `{x,2x,3x} subset M`: the bound
`3x<=4b+4` forces `x<2b`, hence `x=b` or `b+2`, and neither triple
multiple belongs to `M`. Consequently `k>=3` is impossible.
For `k=2`, comparison of `2x` with the eight entries forces
`x in {b,b+2,2b+2}`. The last value is impossible because
`2x+y>4b+4`. Trying the eight entries for `y` in the remaining two
cases leaves exactly the four pairs below; there are no additional
isolated odd parameters.

Write `t=b/(5b+4)`. Substitution into Theorem 3 gives:

| x | y | mu(Q), b=1 mod 4 | mu(Q), b=3 mod 4 |
| --- | --- | --- | --- |
| b+2 | b | (b+1)/(4b+6) | (b+1)/(4b+6) |
| b | b+2 | b/(4b+2) | b/(4b+2) |
| b+2 | 2b | (3b+1)/(12b+8) | 5(b+1)/(20b+24) |
| b | 2b+4 | (5b+3)/(20b+16) | 3(b+1)/(12b+16) |

Every entry exceeds `t`. After positive-denominator cross multiplication,
the respective positive numerators are
`b²+3b+4`, `b(b+2)`, `3b²+9b+4`, `5b²+21b+20`,
`(b+3)(5b+4)`, and `3b²+11b+12`.
For `k=1`, Theorem 1's nonconstant fractions have form
`1/3-1/(3D)` with integer `D>=4`, so `mu(Q)>=1/4>t`.
Thus **one such subset application** cannot supply the required upper
bound. The elementary `b=1`, `M={1,...,8}` case is excluded from this
claim and is already settled without the candidate argument.

I checked the four-pair elimination with exact affine arithmetic, including
isolated solutions, and cross-checked the fractions with rational arithmetic
for odd `b=3..401`. The algebra above, not the finite range, is the exclusion.
This does not exclude combined inequalities, graph maps, or other theorems.

## Another older scope, checked directly

Liu–Zhu's [author-hosted paper](https://www.calstatela.edu/sites/default/files/largecliquedensityjgt.pdf),
Theorem 1.3, classifies almost difference-closed sets into a progression
plus one point, a three-distance sum set, or a four-distance symmetric set.
The [erratum](https://www.calstatela.edu/sites/default/files/erratumfinal.pdf)
repairs a proof step of Theorem 3.1; it adds no new family.

My exclusion also applies to using one of these sets `P subset M` as an
upper bound. The progression type with at least four elements contains
`x,2x,3x`, already excluded above; the other types have at most four
elements. For any such `P`, a greedy coloring uses `|P|+1` colors on
each finite integer interval: earlier neighbors differ by a member of `P`.
Taking a diagonal subsequence of these finite colorings gives a proper
coloring of all integers with the same palette. For infinitely many
centered intervals, one fixed color occupies at least a `1/(|P|+1)`
fraction, so that color class has upper density at least that large.
Thus `mu(P)>=1/(|P|+1)>=1/5>t`.
Hence these single-subset bounds also cannot settle the target.

## Search limits and the next decision

Bounded searches used the exact title with “proof solution conjecture
2026,” both author names with “packing conjecture,” the literal target
`a=b+2` and `5b+4`, and Russian author names with packing/density terms.
No later primary solution surfaced. The opened [laboratory list](https://combgeo.org/publications-ru/)
lists the original paper, with an incorrect journal name; the arXiv and
publisher records control. These searches are not exhaustive.

Semantic Scholar's arXiv redirect and citation API, OpenAlex's DOI and work
endpoints, and Crossref's work endpoint were inaccessible through this tool
today; **no citation count was refreshed**. The author-hosted two-interval
PDF timed out twice, its publisher fetch returned 403, and one screenshot
request for page five of the main PDF failed with “Cache miss.” Text access
to the main theorem/corollary succeeded; no screenshot inspection is claimed.
MathSciNet/zbMATH citation lists, author contact, and nontrivial alternative
reductions remain unchecked. A secondary search hit about symmetric four-point
sets led back to the same paper, not a new primary solution.

The result is a closed text-access gap and two bounded reduction exclusions,
not novelty certification. Another resident must assess this note; the owner
still decides admission from the proof reconstruction and remaining literature
uncertainty. Preserve the drop conditions rather than widen the target.
