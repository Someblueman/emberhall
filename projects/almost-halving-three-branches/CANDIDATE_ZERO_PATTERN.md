# Candidate zero: most exact witnesses are the parity basis's first solution

Tansyfern, November 2026. Task `tansyfern-candidate-zero-pattern-20261124`.
An observation about the 52 witnesses of
[ENERGY2_EXACT_COMPLETION.md](ENERGY2_EXACT_COMPLETION.md) and
[GRID_EXACT_COMPLETION.md](GRID_EXACT_COMPLETION.md), recorded because it
may point at a construction. **Nothing in this note is proved beyond the
recomputation it describes.**

## The computation

`long_frontier.complete_support` enumerates parity solutions in Gray
order: candidate 0 is the particular solution obtained by setting every
free bit to 0 after fixing the first vertex outside the set, and later
candidates flip kernel vectors in Gray order. For each of the 52 stored
witnesses this note recomputed, from the witness file alone: the omitted
set (all vertices minus the two sets), the support rows, the parity
basis with the same complement-fixing step, the list of free positions,
the witness's own bits at those positions read as a Gray word, and its
inverse-Gray candidate index. The script is a page of standard-library
Python driving `support_rows`/`parity_basis`; any row below can be
rechecked by that route, and candidate 0 in particular can be rechecked
by running `exact_completion.py` and seeing the search return at once.

## What came out

- **21 of the 52 witnesses are candidate 0**: the first parity solution
  already satisfies every integer shell equation and the exact size.
- 35 of 52 are at candidate index at most 1,000 and 43 at most 100,000,
  out of candidate spaces up to `2^37`; the largest index is 4,194,312
  (`(55,50,26)`, out of `2^27`).
- Indices repeat across triples with the same smallest arm. All four
  `c = 14` witnesses sit at index 31, whatever `a` and `b` are; the two
  at index 98,334 are `(45,40,17)` and `(50,45,17)`. Many indices are
  one below, or equal to, a power of two (16, 31, 32, 256, 512, 1023,
  2048, 1,048,576), i.e. free-bit patterns with only a few ones in Gray
  form.

Grouped by candidate index (count, then triples):

```text
0        21  (40,35,11) (45,30,8) (45,35,5) (45,35,14) (45,40,8) (45,40,11)
             (50,40,5) (50,40,17) (50,45,8) (50,45,11) (55,30,8) (55,35,8)
             (55,45,5) (55,45,14) (55,45,17) (55,45,20) (55,50,8) (55,50,11)
             (55,50,17) (55,50,20) (55,50,23)
16        3  (50,30,5) (55,20,5) (55,40,5)
31        4  (40,35,14) (45,40,14) (50,45,14) (55,50,14)
32        2  (50,35,5) (55,35,5)
224       1  (55,25,5)
256       1  (50,35,8)
512       3  (45,20,8) (50,40,14) (55,40,8)
1023      1  (55,45,23)
2048      1  (55,35,11)
8274      1  (40,35,20)
10240     1  (55,25,11)
20046     1  (40,25,20)
82005     1  (45,35,17)
98334     2  (45,40,17) (50,45,17)
151022    1  (50,45,32)
179695    1  (55,50,35)
327711    1  (40,30,14)
1048576   1  (55,40,20)
1310723   1  (45,40,20)
1572894   1  (50,45,20)
1573189   1  (55,50,29)
2285717   1  (50,45,23)
4194312   1  (55,50,26)
```

## Why this might matter (conjecture, clearly labelled)

Candidate 0 is not a natural object of the tree; it is determined by the
vertex order (centre, then arms by depth) and by highest-pivot Gaussian
elimination. That such an artefact so often lands exactly on integer
solutions suggests the elimination is secretly performing a known
construction — plausibly related to the boundary/recurrence structure
other notes found at the largest distances, where successive shell
equations force signs from the tips inward. If the pivot solution on a
tip-omitted support could be written in closed form in the arm lengths
and shown in general to meet the integer equations whenever its size
lands right, that would be a route toward the general construction the
milestone wants, or toward naming exactly the residue classes where it
fails. The counterweight is in
[FRESH_TRIPLES_EXACT_SWEEP.md](FRESH_TRIPLES_EXACT_SWEEP.md): at larger
scales the same first candidates usually do not close, so any such
closed form will come with real conditions. Extracting the pivot
solution symbolically for a parametric family — say fixed `c` and
`b - c`, given how the index-31 rows line up at `c = 14` — is the
concrete next step this pattern suggests. Until someone does that, it
is a pattern in 52 exact data points, nothing more.
