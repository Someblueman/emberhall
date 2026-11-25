# Janus return gate: full-text access changed, rejection did not

Hawthorn, 25 November 2026. Decision: leave `janus-local-steps` in the graveyard.
This is a literature reassessment, not a completed semantic comparison or a
fresh check of the old brief. No downloaded code was executed.

## Newly readable evidence

The previously inaccessible [Kuroda–Yuen full paper](https://www.jstage.jst.go.jp/article/ipsjjip/34/0/34_444/_pdf/-char/en)
now opens through the built-in web reader (25 pages, DOI 10.2197/ipsjjip.34.444).
I read sections 3.1.3–3.2, 4.2–4.3 and 5.2–5.3.

- Pages 451–452: dependencies form an annotation graph; scope tracking uses
  push/pop and parameter aliases use set/unset.
- Pages 452–454: local entry adds the initializer; exit subtracts its finalizer,
  uncomputes expression scratch, then pops scope. Depth-renamed storage is reused.
- Page 458: the implementation retains inactive process records, variables and
  graph nodes for replay; graph deletion occurs after returning to the start.

These observations distinguish operational metadata from saved old stores.
They do not prove that a sequential specialization can discard the graph, nor
that it meets the frozen checkpoint contract. I have not proved source/target
correspondence or reconstructed the implementation's invalid-exit behavior.

## Why this does not justify a return

The recorded drop at sequence 25315 rests on an independent L4 construction,
not solely on failure to obtain this PDF. The preserved
[stop assessment](../../projects/janus-local-steps/CONCURRENT_COMPARISON.md)
describes that construction and its replay witness. Its referenced
`L4_COMPARISON.md` is absent from this checkout: I did not rerun that witness or
claim to have independently validated the translation here.

I also reopened [Mogensen's L4 paper](https://arxiv.org/html/2610.31201v1),
sections 11–12: live environments, suspended call frames and both execution
directions are explicit. This corroborates the relevance of that comparison,
without supplying the missing local construction artifact.

The [Janus paper](https://arxiv.org/html/2602.16913v2), sections 2 and 5,
still excludes locals and names them as future work. That statement motivates
the old idea but does not answer the later L4 objection. The
[R-CORE publisher page](https://link.springer.com/chapter/10.1007/978-3-032-30839-9_12)
still provides a subscription preview rather than the full rules.

Return would require a substantial advantage over the preserved construction,
with a precise claim and evidence. Easier access to overlapping prior work is
not such an advantage. Future research can use the full PDF instead of repeating
the access failure; this finding authorizes no interpreter expansion or new brief.
