# Five Marks — admission packet for owner decision

**Marigold, 17 November 2026. For the two-day admission gate only.**
This note gathers the three independent records the project already holds
— Fern's candidate proof in [PROOF.md](PROOF.md), Vesper's novelty screen
in [NOVELTY.md](NOVELTY.md), and Isolde's independent reconstruction in
[RECONSTRUCTION.md](RECONSTRUCTION.md) — into one place for the project
owner (Tern) to decide. It adds no new proof, no new literature reading,
no milestone claim, and no stage advance. A visual companion lives in
[index.html](index.html) and is not re-argued here.

## 1. The exact statement

For positive odd `b`, put `a = b+2` and

```
S_b = {0, b+2, 2b+4, 3b+4, 4b+4}.
```

Two translates intersect exactly when their starts differ by an element of

```
M = {b, b+2, 2b, 2b+2, 2b+4, 3b+2, 3b+4, 4b+4}.
```

The candidate conclusion is `d_p(S_b) = b/(5b+4)`, counting translation
starts (not covered integers; the covered fraction would be five times
this). This is the `k=m=2`, `a-b=2`, `d=0`, `r=2` case of
Natalchenko–Sagdeev's two-nonmixed-gaps conjecture: each gap length
appears twice, reflection included. There is no assertion about other
residues, arbitrary two-and-two gaps, or covering density.

## 2. Argument map

| Step | Content | Verification on record |
| --- | --- | --- |
| Lower bound | Periodic packing `R + nZ`, `n=5b+4`, `R={0,2,…,2b-2}`; parity plus magnitude bound excludes period-boundary conflicts. | Re-derived by Isolde §2 (case split `m=d` vs `m-d=n`); `check.py` checks all ordered residue pairs and both signs for 51 odd parameters through 101. Source is the published lower construction, correctly credited as not new. |
| Finite inequality | Every `M`-avoiding set containing 0 has at most `b` points in `[0,5b+3]`: `b` disjoint columns `c+S`, extras `{b,b+1,2b+2,2b+3}`, at most one extra occupied. | Partition, extras, and column bounds checked as affine identities in `check.py` and by Isolde §3–§4. |
| Odd-column obstruction | If an extra is occupied, some odd column is empty: at `C_1` only rows `{1,2}` survive; step-of-two preserves `{1,2}`; at `c=b-2` both positions lie in `M`. | Both six-entry exclusion tables and the endpoint checked symbolically (coefficients of `b`) in `check.py` `check_affine_identities` and by Isolde §§5–8. The `b=1` case (`M={1,…,8}`) and `b=3` coincidence are handled separately. |
| Density step | Anchored-window bound extends to all `n`-intervals and partitions `[-N,N]`; divide and take limsup. | Re-derived by Isolde §9 (density step); the graph corollary's coloring arithmetic (`u=(n+1)/2`) spot-checked there. |
| Graph corollary | Independence ratio `b/(5b+4)`; `χ_f=χ_c=(5b+4)/b` via Carraher et al. Thm 1. | Corollary only; it does not feed back into the density equality. The cited identity is an unproved external input of the corollary (Isolde §9). |

## 3. What the programme checks, and what it cannot

Re-ran `python3 projects/five-marks/check.py` this run: symbolic
coefficient check (both exclusion tables and endpoint), 51 odd
parameters through 101, exhaustive anchored windows `b=1,3,5,7` with
maxima `1,3,5,7` — all pass. The exhaustive search uses only pair
distances; it does not prune with the claimed bound, column argument,
or residue construction.

These finite checks can only catch errors. The universal claims rest on
the affine identities, which Isolde re-derived symbolically before
reading the obstruction and density sections. The visual companion's
encounter arithmetic (`node projects/five-marks/test_exhibit.cjs`)
covers the same finite instances on screen. Neither the programme nor
the exhibit is the proof of the universal quantifiers.

## 4. Novelty screen, with its limits stated

Vesper's screen (NOVELTY.md), reopened 2026-11-17 through built-in
read-only web tools, found no prior theorem stating or directly
implying the uniform upper bound for this family:

- The **statement and value** are Natalchenko–Sagdeev's conjecture
  (J. Graph Theory 110, 2025, 263–271, DOI 10.1002/jgt.23269;
  arXiv:2407.01101v2). Theorem 2 gives the lower bound; tightness is
  conjectured, not proved, for this case. The published proof covers
  only the case where one gap occurs once (`m=1`); our gaps are twice
  each, so the candidate does not merely restate it.
- **Equivalences** (independence ratio = inverse fractional chromatic
  number; periodic extrema) come from Carraher–Galvin–Hartke–Radcliffe–Stolee
  and justify finite certificates; they prove no value here.
- **Prior theorems sought that would imply it — none found:** Frankl–Kupavskii–Sagdeev
  (three points), Li–Offner–Ye (four-point minimum `1/7`), Liu–Zhu
  large-clique and two-interval results (hypotheses fail here, as
  Fern's README exclusions state and Vesper verified). ArXiv record
  still v2 with no citing solution, erratum, or thesis chapter located;
  OpenAlex `cited_by_count: 0` at fetch time.

Limits that keep this a **provisional screen, not certification**
(NOVELTY.md §Limits, in effect):

1. Semantic Scholar citation query refused (HTTP 429); Google Scholar,
   MathSciNet and zbMATH lists not independently read. Zero OpenAlex
   citations may be index lag for a June-2025 journal paper.
2. The arXiv HTML full text was truncated by the tool before
   Theorem 3 / §3.2–3.3 internals; exclusion of `k=m=2` rests on the
   abstract's explicit once-scope plus indexed `m=1` shape. A fresh
   assessor with PDF access should confirm no corollary silently
   covers `r=2` before any public claim.
3. No author contact, no Russian-language or conference-proceedings
   search, no unpublished discharging-code output beyond Carraher's
   tables.
4. Peregrine's source review and trusted integration (seq 14487/14493)
   are not independent mathematical acceptance.

The strongest wording this packet supports today is: *candidate proof
of a published conjecture's special case; no prior proof located in
sources reopened on 2026-11-17.* Anything stronger must first close
limits 1–2 above.

## 5. Reconstruction verdict and gaps

Isolde (neither author nor novelty assessor) re-derived every identity
symbolically and **accepts** the argument's logic for every positive
odd `b`, with only presentational caveats:

- `d_p` is imported, not restated; what is proved is "every packing has
  upper density at most `b/(5b+4)`, and one attains it", which equals the
  `d_p` claim under the standard definition. Presentational, not logical.
- The graph corollary has one cited, unproved input (Carraher Thm 1);
  it does not affect the main equality.
- Two compressions are repairable from stated material (magnitude bound
  before the wraparound parity sentence; row-interval listing proves
  column disjointness). The remark about repeated values in `M` is
  unnecessary — the eight values are distinct for all positive odd `b`.

Acceptance is of the argument's logic only. It certifies neither
novelty nor admission, and closes no milestone.

## 6. Drop conditions (the stop gate)

Per milestone 1, the project is **dropped rather than turned into a
calculator** — with this note and PROOF.md preserved as the honest
failed attempt — if either of these appears before any public claim:

1. A citing paper, thesis, later version, or corollary proving the
   Natalchenko–Sagdeev conjecture for both gap lengths occurring at
   least twice, or specifically at `a-b=2`; or
2. A defect in the odd-column argument (any step that fails the
   affine identities in §2).

Finite tables, matching examples, or failure of an auxiliary
inequality cannot satisfy the milestone by themselves.

## 7. Options the owner holds

- **Advance to milestone 2** only if the owner judges the admission
  screen plus reconstruction sufficient to spend the next stretch
  resolving the infinite subfamily as a complete proof (or a legal
  periodic counterexample). The candidate already aims at all positive
  odd `b`; milestone 2 is where that aim is proved or refuted as a
  research result, not where tables substitute for it.
- **Drop** if the owner judges limits 1–2 above too open for the
  weeks at issue, or if either drop condition lands. Dropping is a
  complete outcome for this milestone text, not a failure to be
  hidden.

Neither option is decided by this packet. No milestone is closed by
this source contribution.
