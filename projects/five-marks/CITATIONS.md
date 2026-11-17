# Five Marks — citation refresh for the unresolved target

**Marigold, 17 November 2026; provenance repaired by Cinder. For the
two-day admission gate only.**
This note refreshes the "target remains unresolved" check in
[NOVELTY.md](NOVELTY.md) beyond its HTML read. It is a literature screen,
not novelty certification and not milestone closure. Only built-in
read-only web fetch and search were used; no code was downloaded or run.

Provenance: Marigold's direct readings are as recorded below (arXiv
record, abstract, section titles, indexed snippet, OpenAlex/Crossref
counts, searches). Cinder's repair adds only new direct readings of the
arXiv record page (abstract verbatim) and the full-text HTML contents
list, plus a fresh OpenAlex count re-check, all opened in this repair
run (see "Direct readings in this repair" below). No earlier receipt is
repaired or certified by attribution alone.

## Version and abstract (reopened today)

The arXiv record for 2407.01101
([arXiv:2407.01101](https://arxiv.org/abs/2407.01101),
[full-text HTML](https://arxiv.org/html/2407.01101v2)) still lists v2,
6 Jun 2025, no v3, with journal reference Journal of Graph Theory 110
(2025), 263–271, DOI 10.1002/jgt.23269
([publisher record](https://doi.org/10.1002/jgt.23269)). The abstract
still states verbatim:

> "We obtain an explicit lower bound on the corresponding optimal density,
> conjecture its tightness, and prove it in case one of the gap lengths,
> a or b, appears only once."

Our family has each gap twice (`a,a,b,b`), reflection included, so the
published proof's explicit scope excludes it. The value `b/(5b+4)` is
that conjecture specialized, not a house discovery.

## Scoping of the upper-bound section (indexed corroboration)

The HTML table of contents shows Section 3 "Upper bound" with
3.1 main inequality, 3.2 first case, 3.3 second case. A search snippet
reopened today quotes Section 3 opening as generalizing "the ideas for
the special case k = m = 1" — consistent with Fern's and Peregrine's
full reads of Theorem 3 as the `m=1` shape (Vesper's truncated/indexed
reading, below, is consistent with but is not a full read). No snippet
or record reopened today shows a corollary covering `k=m=2, r=2`.

Honest limit: this tool's fetch truncates the HTML before the Theorem 3
internals, so I did not re-derive the exclusion from the full proof text
myself. The scoping here rests on the abstract's explicit wording, the
section titles, the indexed snippet, and prior full readings by Fern and
Peregrine. Vesper's reading is **not** a full reading: [NOVELTY.md limit
2](NOVELTY.md) explicitly records that Vesper's fetched HTML was
truncated by the tool before the Theorem 3 / Section 3.2–3.3 internals,
with the exclusion resting on the abstract's once-scope plus indexed
`m=1` shape. Earlier wording that counted Vesper among the full
readings is corrected here. A fresh assessor with PDF access should
confirm no corollary silently covers `r=2` before any wording stronger
than "candidate proof of a published conjecture's special case; no
prior proof located in sources reopened on 2026-11-17."

## Citing literature (rechecked today)

- OpenAlex work `W4411218641` for DOI 10.1002/jgt.23269
  ([OpenAlex record](https://api.openalex.org/works/doi:10.1002/jgt.23269)):
  `cited_by_count: 0`, re-fetched today.
- Crossref record for 10.1002/jgt.23269
  ([Crossref registry](https://doi.org/10.1002/jgt.23269)):
  `is-referenced-by-count: 0`.
- Semantic Scholar graph endpoint: still HTTP 429 today, as in
  NOVELTY.md; Google Scholar, MathSciNet and zbMATH lists remain
  unread. Zero counts may be index lag for a June-2025 journal paper,
  not absence.
- Web searches reopened today — "Natalchenko Sagdeev packing density two
  nonmixed gaps cited by", "2407.01101 OR two nonmixed gaps packing
  density proof 2026", "Sagdeev packing density distance graph
  independence ratio new proof" — returned the original paper, its
  mirrors and the authors' laboratory list only. No citing solution,
  erratum, thesis chapter, or later version proving the conjecture for
  both gap lengths at least twice, or specifically at `a-b=2`,
  surfaced.

What would count as a prior solution (and would trigger the drop
condition in [ADMISSION.md](ADMISSION.md)): a citing paper, thesis,
later version, or corollary proving Natalchenko–Sagdeev tightness in
the both-gaps-at-least-twice case.

## Direct readings in this repair (Cinder, 17 November 2026)

- [arXiv record](https://arxiv.org/abs/2407.01101): opened with built-in
  read-only fetch today (200 OK). Abstract verbatim confirmed, v2
  6 Jun 2025, journal reference 110 (2025) 263–271 confirmed on the
  record page itself.
- [arXiv full-text HTML](https://arxiv.org/html/2407.01101v2): opened
  today (200 OK). The returned text confirms the contents list (Abstract,
  Introduction, Lower bound, Upper bound with 3.1 main inequality, 3.2
  first case, 3.3 second case, Concluding remarks) but truncates before
  the Theorem 3 / Proposition 1 / Corollary 1 internals. No claim about
  those internals is made from this fetch; they remain inherited
  evidence (Fern/Peregrine full reads plus indexed snippets), not new
  direct readings in this repair.
- [OpenAlex record](https://api.openalex.org/works/doi:10.1002/jgt.23269):
  re-fetched today (200 OK); `cited_by_count: 0` confirmed directly.

## Verdict for the owner

On the evidence reopened today, the target still looks unresolved and
the candidate proof remains a candidate: keep the admission attempt
alive for the owner decision, preserve the four novelty limits in
NOVELTY.md (citation lists unread, Theorem 3 internals confirmed only
via abstract/titles/snippets plus prior full reads, no author contact,
no Russian or proceedings search), and drop rather than widen if a
prior proof or a proof defect appears. No theorem is claimed from a
finite table; the finite searches in [ADMISSION.md](ADMISSION.md) and
`counterexample.py` support or undermine the argument, they do not
replace it.
