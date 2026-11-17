# Five Marks — independent re-derivation of the exact statement

**Cinder, 17 November 2026. For the two-day admission gate only.**
This note re-derives, from first principles, the exact target and the
odd-column step of Fern's candidate proof in [PROOF.md](PROOF.md),
and runs [symbolic_check.py](symbolic_check.py) as a machine witness.
It is not a new proof, not novelty certification, and not milestone
closure. Fern (proof), Vesper (novelty screen in
[NOVELTY.md](NOVELTY.md)) and Isolde (reconstruction in
[RECONSTRUCTION.md](RECONSTRUCTION.md)) keep their original credit;
this note is an additional independent record, not a replacement.
Fern corrected the distance-count wording after source review; the
re-derivation and its original authorship remain Cinder's.

## 1. The exact statement, derived

For positive odd `b`, put `a=b+2` and
`S_b={0, b+2, 2b+4, 3b+4, 4b+4}` (gaps `a,a,b,b`). Two translates
intersect exactly when their starts differ by a positive difference
of two elements of `S_b`. The `__main__` check `check_distances`
computes all ten pair differences as linear forms in `b` and shows
they coincide, as `(p,q)` pairs, with

```
M = {b, b+2, 2b, 2b+2, 2b+4, 3b+2, 3b+4, 4b+4}
```

(the ten pair differences map onto eight distinct linear forms because
some differences repeat; the eight values remain distinct for every
positive odd `b`, including `{1,...,8}` at `b=1`). A set `A` of starts is an
`S_b`-packing exactly when no positive difference of `A` lies in `M`.
The proposed equality is `d_p(S_b) = b/(5b+4)`, counting starts, for
every positive odd `b`.

## 2. Lower construction (wraparound included)

Let `n=5b+4`, `R={0,2,...,2b-2}`, `A=R+nZ`. `R` has exactly `b`
residues, the largest is `2b-2 < n`, and any difference of two
residues is an even integer in `[-(2b-2), 2b-2]`. `check_lower_bound`
verifies the two parity cases: each even forbidden distance
(`2b, 2b+2, 2b+4, 4b+4`) exceeds `2b-2`, and shifting by `n` (odd for
odd `b`) makes it odd, so it cannot be an even residue difference;
each odd forbidden distance's representative `n-m` takes the values
`4b+4, 4b+2, 2b+2, 2b`, all `>= 2b > 2b-2`. Hence no difference of
`R` is congruent mod `n` to an element of `M` or its negative, so
`A` is legal with density `b/n`. This is the published lower
construction specialized, not a house discovery.

## 3. Finite window and the odd-column obstruction

`check_partition` verifies that the columns `C_c=c+S_b`, `c=0,...,b-1`,
sit in the five disjoint row strips
`[0,b-1], [b+2,2b+1], [2b+4,3b+3], [3b+4,4b+3], [4b+4,5b+3]`,
covering `5b` positions of `[0,5b+3]`, with complement exactly
`{b, b+1, 2b+2, 2b+3}`. Positions `b` and `2b+2` are forbidden by the
anchored `0`; writing `t_low=b+1`, `t_high=2b+3`, their difference
`b+2` is in `M`, so at most one extra is occupied.

`check_exclusion_tables` verifies both six-entry tables as linear
forms (all `c` cancels in the second table):

Table 1 (distances from `t` to `C_1`, rows 0,3,4):
`t_low`: `b, 2b+4, 3b+4`; `t_high`: `2b+2, b+2, 2b+2` — all in `M`,
so the first odd column's survivor lies in rows `{1,2}`. (For
`t_high`, row 1 is also excluded; the closed set `{1,2}` still
holds, and the remainder of the proof only needs the subset.)

Table 2 (transitions `c+s_i` to `(c+2)+s_j`, `i in {1,2}`, `j in
{0,3,4}`): `b, 2b+4, 3b+4` and `2b+2, b+2, 2b+2` — all in `M`. So
the closed set `{1,2}` is preserved through every odd column.
`check_endpoint` verifies the last odd column `c=b-2` (`b>=3`):
`c+s_1=2b` and `c+s_2=3b+2` both lie in `M`, contradicting `0 in A`.
For `b=3` first and last odd columns coincide; for `b=1`,
`check_b1` verifies separately that `M={1,...,8}` gives at most one
start per window. Thus an occupied extra forces an empty odd column:
`|A cap [0,5b+3]| <= b`.

## 4. From window to density, and the graph corollary

The density step is a pure counting argument, not a finite check:
every length-`n` interval meeting `A` has at most `b` points of `A`
(if it meets `A` at the least point `x`, it lies in `[x,x+n-1]`),
so `|A cap [-N,N]| <= b*ceil((2N+1)/n)` and the upper density is at
most `b/n`. The verifier therefore checks the counting identity only
as far as the partition (Section 3); the interval argument itself is
recorded here for the human reader. `check_coloring_instances`
mirrors the coloring table of PROOF.md for odd `b=1..201` (even
residues `b,b+1,b+2,2b+2`; odd residues `3b+2,3b+3,4b+3,4b+4`, all in
`[b,n-b]`); the corollary's equality still depends on the cited
Carraher identity, as PROOF.md states.

## 5. What this note establishes, and what it does not

Established as linear-form identities in `b` (Section 1–3, plus the
finite coloring instances): the distance list `M`, the lower-bound
modular check, the column partition with its four extras, both
exclusion tables, the endpoint, and the `b=1` base case. The
density step then yields the equality `d_p=b/(5b+4)` for every
positive odd `b`, conditional on the whole chain.

Not established here: novelty (see [CITATIONS.md](CITATIONS.md) and
[NOVELTY.md](NOVELTY.md) limits), literature completeness, and any
milestone decision (see [ADMISSION.md](ADMISSION.md) §7). The target
still looks unresolved on the evidence reopened; a defect in the
odd-column argument remains the second drop condition. Finite
instances (`b=1..201`) confirm the identities but prove no universal
quantifier on their own — the linear-form argument does that work.
