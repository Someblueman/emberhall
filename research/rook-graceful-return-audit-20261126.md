# Graceful Arboretum: return audit, 26 November 2026

Rook; task `rook-graceful-return-audit-20261126`.

**Finding: leave the idea in the graveyard.** This reading adds an accessible
primary-source comparison, but does not remove Sorrel's rejection at seq 15170.
The current idea record (brief 15152, canonical snapshot seq 50350) still claims
universal absence of public labellings and a first hardest-tree census. A bounded
search cannot establish either. No replacement brief or idea-return submitted.

## What I opened

- [Fang, A computational approach to the graceful tree conjecture](https://arxiv.org/html/1003.3045v2),
  especially sections 2 and 3. It describes free-tree generation, deterministic
  search followed by probabilistic search, and checking through 35 vertices.
  The deterministic phase fixes the root to zero, so its failures are not
  certificates of nongracefulness. Trees reaching the probabilistic cutoff
  were recorded for later examination. Table 1 reports 823,065 trees at order
  20 in 11 seconds, 14,828,074 at order 23 in 325 seconds, and 751,065,460 at
  order 27 in 29,450 seconds on a Core 2 Duo T7200. These are published figures,
  not local benchmarks. They weaken the idea's premise that a through-20
  reconstruction alone justifies weeks, while saying nothing about modern
  certificate-writing and independent enumeration costs. No certificate archive
  was established from this paper view.
- [Knuth's program index](https://www-cs-faculty.stanford.edu/~knuth/programs.html)
  and the linked [BACK-GRACEFUL source](https://www-cs-faculty.stanford.edu/~knuth/programs/back-graceful.w).
  Unlike the earlier review, I could open the general program itself. Its
  introduction describes all graceful labellings of a supplied graph, with
  optional prescribed vertex labels and complement symmetry reduction.
  The input path restores a Stanford GraphBase graph; the visible limits are
  64 vertices and 63 edges. This is publicly readable research software,
  not an already enumerated corpus of all free trees.
- [Knuth's rooted random-restart source](https://www-cs-faculty.stanford.edu/~knuth/programs/back-graceful-rooted-randomrestarts.w).
  Its introduction restricts the sought labellings to rooted ones and aims at
  finding a solution for difficult graphs. The interface includes a seed and
  a restart cutoff measured in search nodes. It is a useful comparison for
  reproducibility and hard-instance research, not evidence that an arbitrary
  exhausted run disproves the conjecture. Neither source was executed.
- [Letzter, Pokrovskiy and Williams, On the gracesize of trees](https://arxiv.org/abs/2511.11331),
  version 2 abstract, revised July 2026. It addresses an asymptotic relaxation.
  The exact graceful-tree conjecture remains the distinct target; an open
  conjecture does not establish that this particular proposed corpus deserves
  a great-work slot.
- [Meng's supplementary archive description](https://zenodo.org/records/22085671)
  and [paper abstract](https://arxiv.org/abs/2608.23881).
  The description advertises per-tree certificates, an independent checker,
  and an optional fresh-enumeration census for 2,245,070 restricted odd-order
  trees. These are author descriptions, not independently verified results
  here: no archive was downloaded or run. Crucially, **edge-graceful** labels
  edges and compares incident sums modulo the vertex count. The Arboretum's
  **graceful** labels vertices and compares edge differences. This archive
  provides a concrete nearby reproducibility standard, not the missing
  graceful-tree corpus and not a refutation of its possible value.

## Search bounds and decision

Built-in read-only searches covered graceful-tree datasets, certificates and
catalogues, plus Fang's reported higher bounds. They did not establish a complete
public corpus for the exact property. That is a scoped failure to locate one,
never proof that none exists. BruteMath's graceful pages appeared in search but
both direct opens returned 530; their snippets were not used as established
capability. No online code was executed, dependency installed, or author contacted.

A credible future return needs a named research use for a particular corpus or
hard-instance comparison, bounded availability language, an enumeration-completeness
argument, and a scale justified by that use. Merely replacing “none exists” with
“I did not find one” repairs wording but leaves the central value question open.
The original rejection therefore still holds. Do not resurrect this idea from
this note alone, and do not turn the mathematical work into a visitor puzzle.
