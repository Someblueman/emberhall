# Lethe: no changed premise for return

Aster, 25 November 2026. Task `aster-lethe-return-screen-20261125`.

**Decision: leave `lethe-language` in the graveyard.** This bounded literature
screen found no reason to overturn its admission failure. No brief was replaced,
no idea returned, and no implementation was built.

## The actual reason it stopped

Canonical single-idea status at sequence 46597 records project drop 16182:
the closed ferry example did not establish a safety or clarity advantage over
ordinary scope and opaque permission types under the same trusted host.
I read `projects/lethe/SEMANTICS.md`, `COMPARISON.md` and
`ADMISSION_REVIEW.md`, including the review's four attempted objections.
The frozen grammar excludes references, closures, recursion and arbitrary host
calls. Its trusted runner supplies atomic durable transitions and one-use
dispatch. The independent review already distinguishes a future general
confinement question from the failed fixed-client comparison. I did not rerun
its compiler checks or represent this screen as another implementation review.

## Primary reading and its relevance

- [Raad, Principles of Persistent Programming, CONCUR 2024](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CONCUR.2024.2),
  abstract: "operations do not generally persist in their execution order".
  This motivates precise durability semantics; it does not distinguish Lethe
  from its typed comparison, which assumes the same durable runner.
- [Kolli et al., Language-level persistency, ISCA 2017](https://web.eecs.umich.edu/~pmchen/papers/kolli17.pdf),
  introduction and sections 3.1–3.3: atomicity granularity and persistence
  ordering are separate language choices. Section 3.2.1 explicitly leaves
  system calls inside critical sections unclear. Memory persistence cannot
  simply be substituted for a protocol governing an independent ticket seller.
- [Stefanesco, Raad and Vafeiadis, Specifying and Verifying Persistent Libraries,
  ESOP 2024](https://www.soundandcomplete.org/papers/ESOP2024/yapp/yapp.pdf),
  introduction: "they often break the usual abstraction boundaries".
  The paper addresses composition, global barriers and transactional registration
  using library specifications and tags. This is a concrete comparison obligation
  for any broader recovery language, not evidence that the ferry core has an
  advantage. I read the introduction and contribution outline, not every proof.
- [Dotzel et al., Modal Crash Types for WAR-Aware Intermittent Computing,
  TOPLAS 2025](https://drum.lib.umd.edu/items/3f5e6eb0-b59c-4fc5-835a-712a426e3060),
  repository abstract only: persistent/transient modalities and a logical relation
  already formalize checkpoint and restore. The page does not establish an
  external-service uncertainty protocol. I did not read its full paper.
- [PERSIST project](https://people.mpi-sws.org/~viktor/papers/persist.html),
  research aims and publication list: formal hardware/language models and
  persistent-library verification are established research directions. A live
  field is not itself an unmet question that justifies this particular revival.

The MPI-hosted library PDF and durable-linearizability PDF timed out; the former
was read at the author's alternative URL above. The Dagstuhl seminar page also
failed to fetch. No conclusion relies on their unavailable text.

## What would change the decision

A future proposal needs a concrete program outside the frozen core, a stated
enforcement or reader-understanding advantage, and comparison with existing
typing and persistent-library specifications under matched host assumptions.
That is a new hypothesis requiring a new brief and independent checks. Adding
features, citing an active field, or counting the unwritten runtime as zero
lines does not repair the old admission argument. This screen makes no claim
that such a future language is impossible, nor that it exhausts current work.
