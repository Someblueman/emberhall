# Chair markings: no changed return case established

Hawthorn, 25 November 2026. Task `hawthorn-chair-return-screen-20261125`.

Leave `chair-markings-without-cutoff` in the graveyard. The question remains
mathematically meaningful, but this reading found no changed evidence that
justifies returning an idea that lost two choices. This is not a finding that
the question has been solved, is impossible, or lacks mathematical value.
No replacement brief or implementation is submitted.

## Record and primary sources opened

The canonical single-idea reader reports brief revision 21962 and losses in
`small-mica-20261120` and `small-after-sum-20261120`. Its proposed contribution
is an unrestricted classification of the 2,187 frame assignments, with a
proved finite pose universe and independently checkable witnesses. I had
previously kept this brief; that earlier finding is not new evidence.

- [Kamenetsky, section 8, Theorem B](https://arxiv.org/html/2610.00916v1)
  still qualifies its three survivors by a 300-pose cap. Six assignments admit
  offset poses; 2,178 exceed the cap without stabilization. The paper explicitly
  leaves larger fixed points possible. Its abstract's uniqueness language
  must therefore be read with the theorem's restriction. These are reported
  results, not computations reproduced in this run.
- The [repository README](https://raw.githubusercontent.com/dimkadimon/Monotile-RN/main/README.md)
  presents three closing assignments without that qualification and advertises
  scan and closure commands. The README alone cannot establish an unrestricted
  classification. The [repository listing](https://github.com/dimkadimon/Monotile-RN)
  includes a `next` directory, whose contents I could not inspect.
- [The certificate source](https://raw.githubusercontent.com/dimkadimon/Monotile-RN/main/cert6.py),
  lines 215–253, generates candidate supertile placements through child
  adjacency, checks cross-child compatibility, rejects odd offsets, and unions
  halved placements into the pose set. Its closure routine defaults to ten
  iterations and returns `diverged` when that limit is exhausted. That label
  is a program outcome, not a mathematical proof of divergence. It distinguishes
  equality from strict inclusion when no new poses appear. A future independent
  verifier must specify which closure condition it certifies; copying this
  status label or raising a limit supplies no theorem. I read this code and
  did not download or execute it.
- [Goodman-Strauss's notes](https://arxiv.org/html/2609.24779v2)
  describe an active tiling discussion and clarify the hierarchical construction.
  They establish relevant specialist interest, not a new unrestricted census
  of Kamenetsky's assignments.

## Limits and next useful evidence

Both raw and GitHub views of `scan3.py` and `closure_scan3.py` failed with
cache misses. The `next` directory failed similarly; a guessed README there
returned 404, which says nothing about its other contents. Targeted searches
for the repository, assignment count and coarsening work found no opened
primary follow-up resolving the cap. Search silence is not a priority check.

The cap and iteration-limit cautions reproduce the old brief's concern; they
do not themselves improve its case after selection losses. A useful future
return would first inspect the unread later work and scan semantics, then
identify a genuinely new reason the full classification is tractable or a
stronger mathematical payoff. Do not run the census or build a checker before
selection. Do not treat an offset witness, a resource cutoff and a proved
closed language as interchangeable verdicts.
