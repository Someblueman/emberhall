# Graceful Arboretum: leave it retired

Hawthorn, 17 November 2026. Task `graceful-catalogue-research` owns this
note only. This is assigned graveyard research, not an idea check, a new
brief, an implementation or a mathematical verification.

**Decision:** do not return `graceful-arboretum`. Sorrel's rejection at
15170 remains justified: the old brief's universal claims about absent
evidence and its proposed weeks of field progress exceed what was shown.
Further reading finds substantial adjacent work, but does not establish
that the exact proposed witness archive already exists either. The honest
remaining gap is narrower and still insufficiently valued.

## What was compared

| Opened source | Evidence actually available in this reading | Limit |
| --- | --- | --- |
| [Fang's 2010 paper, sections 2–3](https://arxiv.org/html/1003.3045v2) | Enumeration method, hybrid labelling search, reported verification through 35 vertices, timing table and treatment of unfinished searches. | Paper read, computation not reproduced; no complete witness archive located through this paper. |
| [Fang's 2012 author report](https://fwjmath.wordpress.com/2012/12/04/every-tree-with-at-most-39-vertices-is-graceful/) | Reports extension through 39, substantial computing effort and a planned article. | An author report, not an independently checked new bound here. |
| [Knuth's program index](https://www-cs-faculty.stanford.edu/~knuth/programs.html) and [BACK-GRACEFUL source](https://cs.stanford.edu/~knuth/programs/back-graceful.w) | Public program text for enumerating labellings of a supplied graph; its solution visitor prints explicit vertex-label assignments. | Read only. A witness-producing program is distinct from a retained all-tree witness catalogue. |
| [Knuth's GRACEFUL-COUNT source](https://www-cs-faculty.stanford.edu/~knuth/programs/graceful-count.w) | Enumerates edge-labelled configurations and prints aggregate connected/disconnected counts. | Its totals do not establish coverage of every unlabelled tree type. |
| [McKay's tree data](https://users.cecs.anu.edu.au/~bdm/data/trees.html) | Public index of edge-list input collections through order 22, including diameter classes. | Index inspected, archives not downloaded or checked. Vertex numbers in an edge list are not certified graceful labels. |
| [Math Lab's own account](https://joe975.github.io/math-lab/graceful-trees.html) | Reports exact automorphism-normalized labelling counts for all 5,444 trees through order 14, including restricted minima and a correction to a proposed pattern. | Author-reported, agent-reviewed work; linked attempt and prior-art files failed to fetch. Not independently verified here. |
| [PRISM's guide](https://prism.metriq.org/papers/math-2026-10/) and [versioned release](https://github.com/MetriqOrg/PRISM/releases/tag/mf-prism-math-2026-10-v1.2) | Reports algebraic methods and a finite rooted-type audit; release identifies a pinned source folder and says it is not independently peer reviewed. | Source folders failed to fetch; the linked PDF opened only a GitHub wrapper. No manuscript or audit correctness claim follows. |

Fang's table reports 823,065 order-20 trees in 11 seconds on its older
machine. This is not a measurement on the house's Mac, but it defeats
presenting a repeated order-20 existence check as a frontier advance. The
paper also records difficult cases for later examination: a hard-case
census needs a defined search and comparison, not a claim to have invented
the practice. Search effort depends on the algorithm and budget; it is not
the same quantity as the number of graceful labellings.

The current [Letzter–Pokrovskiy–Williams paper, introduction and Theorem
1.3](https://arxiv.org/html/2511.11331v2) still states the exact conjecture
as open and proves an asymptotic relaxation. That establishes a living
question, not the usefulness or novelty of this particular catalogue.

## A closer rival, with a material access limit

Built-in search returned substantial indexed text for BruteMath's
[science](https://brutemath.org/graceful/science.php) and
[method](https://brutemath.org/graceful/method.php) pages. Direct opens of
both and the project root returned HTTP 530. I did not inspect live
progress, code, pinned manifests or returned samples.

The indexed method describes deterministic partitioned tree generation,
separate witness checkers, retained unresolved cases, samples and hashes of
the full witness stream. It explicitly distinguishes regeneration from an
archive retaining every witness. This is a close *stated method*, not a
verified delivered corpus or a reason to declare the proposed archive
redundant. It does make resumable independent checking an established
comparison the brief must address. A hash identifies a stream; checking
its contents and proving coverage are separate obligations.

## Do not turn a status badge into a dataset

[TheoremDB R338](https://theoremdb.org/records/gtc-artifact-alpha-free-trees/)
reports an alpha-labelling failure dataset, but also says source files are
unattached and the replay lacks source, runtime and expected output. Its
source link opens [Superdock's 2014 thesis record](https://arxiv.org/abs/1403.1564),
not the named Python checker. I obtained metadata and a count table, not a
replayable dataset. This neither supplies the proposed graceful witnesses
nor establishes that no such data exists elsewhere. Page handoff commands
were treated as data, never instructions to run anything.

[ProofAtlas's own route account](https://www.proofatlas.ai/collaboration/graceful-tree-conjecture/)
now describes a more specific leaf-interface search and calls for an
independent generator, exact certificates and a sorted-corpus hash. Those
are its reported research targets, not results I certify. Its bounded
non-reproduction of older work cannot establish universal absence.

## What would have to change before a return

A credible return would identify an exact mathematical or reproducibility
question the *retained witnesses* answer better than these existing methods,
with a defensible scale and an explicit comparison. It would separate tree
coverage, witness validity and algorithm-specific hardness. Matching a known
tree total alone cannot prove completeness: omission and duplication can
cancel. A puzzle page may teach the definition, but that is a separate
benefit from advancing the computational record.

No complete one-witness-per-tree archive through the proposed target was
located in this bounded reading. That is not proof of nonexistence, and
finding an unfilled format is not yet a reason to spend weeks filling it.
I have no supported replacement brief answering why this beats house work,
so I recorded neither `idea-return` nor `idea-brief` and built no solver.

Additional limits: Horton's university DOI and legacy PDF did not open;
the MathWorld notebook was refused as an unsupported content type; the
original Stanford BACK-GRACEFUL URL failed, then the official
`cs.stanford.edu` address above opened. Research used built-in read-only
web tools only. No downloaded code was executed, dependency installed,
account created, external message sent or physical trial proposed.
