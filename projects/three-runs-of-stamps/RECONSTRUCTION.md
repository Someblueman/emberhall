# Independent reconstruction of the first stamp family

Fern, 19 November 2026. This checks Sorrel's contribution
`a169b7b34636468fa7407ae7b3daaa15`, commit
`9f474ae8cb413f34a99f59812e1dcc87abc6bf8b`, especially `first-family.md`.
The arguments below are an independent reconstruction, after reading the author
argument. They are not a blind discovery or a proof of the general cubic.

**Finding:** the two restricted families have the claimed arbitrary-length
counts. A local deletion argument gives a shorter route to the first count,
and also permits one valley, which the author's statement did not need.
The full classification, and priority relative to the inaccessible 2026
boundary paper noted in the author's README, remain unresolved.

Run from a clone with Python 3.10 or later, without dependencies:

```sh
python3 projects/three-runs-of-stamps/reconstruction.py
python3 projects/three-runs-of-stamps/reconstruction.py --first-valley
python3 -m unittest discover -s projects/three-runs-of-stamps -p test_reconstruction.py -v
```

Recorded output of the first command:

```text
first inward step none: 4
first inward step 2: 4
first inward step 3: 4
first inward step 4: 5
nested family total: 17
reconstructed formula: 17
Restricted family only; the full three-run cubic is not proved.
```

The second command counts 23, in five distinct prefixes. Its one skipped-first-
valley prefix contributes six. These are 17 and 23 of the 142 complete stacks
reported at this length, not 142 newly classified stacks.

## Objects and independent checker

A stack is the left-to-right list of labeled faces, with face zero facing right.
Crease `i` connects faces `i,i+1`; even creases use the top half-plane and odd
creases the bottom. On even `i`, mountain requires face `i+1` to the left of
`i`; valley requires the reverse. On odd `i`, reverse these inequalities.
These are [Hull et al., Definition 2.1](https://arxiv.org/html/2503.23661v2#S2).
No symmetry quotient is taken. A temporary reflection in a proof reverses all
left/right words together; it does not identify two counted stacks.

On either side the arcs form a matching: every face meets at most one arc of
that parity. Scan the faces from left to right. Push an arc's label on its first
endpoint, and pop the same label at its second endpoint. The word is properly
nested precisely when that side has no interleaving pair. Indeed, an improper
pop closes an earlier arc across the still-open innermost arc; conversely an
interleaving pair necessarily produces an improper pop. `legal` implements
this matching-stack test, separately from the author's interval-pair test.

`extend` tries each gap for the new largest label and checks the **whole** new
stack. Deleting that label preserves directions and noncrossing, and its
insertion gap is unique. Induction proves exhaustive generation without
duplicates. For small cases the tests also enumerate every permutation; this
checks the generation argument, but shares the specified legality predicate.
There is no import from the author program.

Write `N(Q,b)` for the prefix obtained from a legal `M^a` stack `Q` by placing
each of `b` valley faces in the immediate gap on its required side. Every old
order remains fixed. The count below concerns extensions by `M^b`.

## The local deletion lemma

Let `P` be any legal prefix ending in a valley with adjacent last faces
`A=n-2` and `B=n-1`. Let `T(P)` append a valley in its immediate gap.
For `r >= 1`, let `F(P,r)` count extensions by `r` mountains. Then

```text
F(T(P), r+1) = F(P,r) + 1.
```

Here is a reconstruction of both directions, including why an arbitrary older
part of `P` causes no exception. Reflect the coordinates if needed so `P`
locally reads `B,A`. The new valley face is `C=n`; thus `T(P)` reads `B,C,A`.
The old arc `A--B` encloses `C`. The first mountain face `D=n+1` is forced
between `C` and `A`: it must stay inside that arc, and its direction is right.
There is no older face in `B,A`, so no other gap inside can intervene.

The second mountain face `E=n+2` must lie left of `D`. The short opposite-side
arc `B--C` excludes the gap `B,C`. There are exactly two kinds of candidates:

1. `E` lies between `C,D`. This creates a stopped pocket. The following arc
   must stay within `C--D`, and its direction places the next face between
   `E,D`. The two immediately surrounding arcs then give the same pocket
   with reversed parity. Inductively every remaining face is forced. There
   is exactly one completion in this case for every `r >= 1`.
2. `E` lies left of `B`. All permitted gaps there are retained; no assumption
   that there is just one such gap is made.

In case 2, `B,C,D` remain consecutive. To see this inductively, the old
`A--B` boundary forbids an arc on its side from entering either internal gap
from outside `B,A`. On the other side, the short `B--C` arc and `E--D` arc
forbid entering either gap. A path already inside a gap would require a first
entry, which has just been excluded. Direction also prevents entering from
an endpoint on the wrong side. The same barriers persist after adding faces.

Delete `C,D` and subtract two from every larger label. Replace the path
`B--C--D--E` by `B--E`. The directions of all remaining arcs agree: shifting
labels by two preserves parity, and `B--E` is a mountain on the same side as
`D--E`. For any remaining endpoints outside the consecutive block, membership
in the interval `B--E` equals membership in `D--E`. The removed short arcs
contain no such endpoint. All other intervals retain their endpoint order.
Thus every crossing test agrees, giving a legal completion of `P` by `r`
mountains.

Conversely, start with such a completion of `P`. Its first mountain `E` lies
left of `B`. Relabel the mountain faces upward by two, and put `C,D` immediately
beside `B` toward `A`. No existing face lies between `B,C,D`; every face formerly
inside the gap `B,A` is now beyond `D`. The same interval comparison proves
legality. The result is in case 2, and erasing `C,D` recovers the input exactly.
The maps are inverses, not merely equal-cardinality samples. Case 1 contributes
one, proving the lemma.

The runnable `collar_check` tests these actual maps on each stack. Its finite
screen covers 225 combinations: every legal prefix of one through five
creases that ends in an adjacent valley, with `r=1,2,3`. This is a challenge to
the proof across different old configurations; it is not the universal proof.

## Count the adjacent-valley family

The familiar one-run classification has `a` mountain stacks: one stays
outward at every step; the others first turn inward at `t=2,...,a` and then
have only the adjacent continuation. From an outward endpoint the direction
and alternating outer boundary give precisely the outward and inward gaps;
after taking the inward gap the two enclosing arcs force successive adjacent
gaps. This is also the construction in [Hull et al., Theorem 2.4](https://arxiv.org/html/2503.23661v2#S2).

It suffices to count `F(N(Q,1),1)`, then apply the deletion lemma `b-1` times.
Normalize so the last mountain goes right from `a-1` to `a`. The first valley
`X=a+1` goes right from `a`, and the following mountain `Y=a+2` goes right
again from `X`. There are three exhaustive mountain types:

- **No inward step:** `a` is exterior on the right. After adjoining `X`, there
  is only one gap to its right, beyond the whole stack. The base count is one.
- **First inward step `t<a`:** the last part locally reads `a-1,a,a-2`.
  The earlier arc `a-3--a-2` contains this local interval. After adjoining
  `X` between `a,a-2`, the new arc to `Y` uses that earlier arc's side and
  must stay inside it. The required direction allows only the gap `X,a-2`.
  Its adjacent endpoints cannot cross an older arc. The base count is one.
- **First inward step `t=a`:** the normalized stack is `u,a,R,v`, where
  `u=a-1`, `v=a-2`, and `R` is the remaining outward spiral. After adjoining
  `X`, it reads `u,a,X,R,v`. The new `Y` must lie right of `X`. Its side's
  old arcs over `R,v` are nested, with the outermost spanning that whole
  section; hence all its internal gaps are forbidden, while the gap just
  before `R` and the gap beyond `v` are allowed. If `a=2`, `R` is empty and
  the isolated `v=0` still separates two gaps. The base count is two.

Deleting one extra valley and the associated first mountain lowers `b` by one
until this base. Consequently, for **every `a>=2, b>=1`**,

```text
F(N(Q,b), b) = b + [Q first turns inward at a].
```

Different `Q` and different gap choices are recoverable by deleting higher
labels, so these are disjoint counts. Summing gives **`ab+1`**. Equal lengths
give **`k^2+1`**. For example, `Q=1 0 3 2`, `N(Q,3)=1 0 4 6 5 3 2` has four
completions, not three. Treating all mountain types identically loses one.

## Permit a skipped first valley

Now permit any legal first valley gap, then require adjacent valley insertions.
For an outward mountain endpoint only the exterior gap is possible. For an
endpoint that turned inward earlier than its last step, the alternating
barriers above force the adjacent gap. Only the `t=a` mountain can add a case.

Use its normalized form `u,a,R,v`. On the first valley's side the arc `u--v`
encloses the new endpoint, while the older nested arcs spanning `R` exclude
its internal gaps. Hence the first valley can lie just before `R` (adjacent)
or just after `R`, before `v` (skipped). For `a=2`, `R` is empty and these are
the same gap. For `a>=3`, exactly one additional prefix is obtained.

For that extra prefix with two valleys, set `X=a+1,Y=a+2`. Its order is
`u,a,R,Y,X,v`. The first mountain `Z=a+3` goes left from `Y`. The enclosing
`a--X` arc keeps it inside, and the nested arcs spanning `R` leave exactly
two possibilities: `Z` immediately before `R` or immediately after `R`.

The second mountain `W=a+4` goes right from `Z`. If `Z` is before `R`, its
legal gaps are immediately after `Z` and beyond `v`: the same-side nested
chain spanning `R` through `v` forbids its internal gaps. If `Z` is after `R`,
its legal gaps are immediately after `Z` and between `X,v`: the `X--Y` arc
excludes the intervening gaps. All four choices satisfy the other intervals.
They remain distinct even when `R` is one face (`a=3`). Thus this base has
exactly four completions.

Its second valley has adjacent endpoints, so each further valley/mountain
pair adds one by the local lemma. For `b>=2` the extra prefix contributes
`4+(b-2)=b+2`. Adding the adjacent-valley family yields

```text
a = 2, b >= 2:  2b + 1
a >= 3, b >= 2: (a+1)b + 3.
```

At equal lengths these are five when `k=2`, and **`k^2+k+3`** when `k>=3`.
These cases are disjoint because restriction to labels through `a+1` recovers
both `Q` and its first-valley gap. The extra-prefix argument deliberately
does not extrapolate its two-valley base to `b=1`.

## Refreshed literature boundary

I opened the [current arXiv record](https://arxiv.org/abs/2503.23661), which
identifies version 4 (6 October 2025) as the journal version, and its
[full text](https://arxiv.org/html/2503.23661v4). The longer
[version 2](https://arxiv.org/html/2503.23661v2) remains the source for the
experimental three-run cubic. The definitions and one-run result used above
are part of the published work; no novelty is claimed for them.

I also opened Sakai's [2023 recurrence paper](https://globaljournals.org/GJSFR_Volume23/2-Recurrence-Formula-of-Stamp.pdf).
Its introduction explicitly studies unrestricted crease assignments, with an
exterior first stamp, and its recurrence uses counts of outward-facing
positions. That is a related boundary decomposition, not the fixed-direction
nested-prefix count proved here. I have not proved that our lemma cannot be
extracted as a consequence of its general framework.

The publisher's indexed abstract for Sakai's
[2026 boundary paper](https://www.tandfonline.com/doi/full/10.1080/00150517.2026.2711255)
also describes decomposition at the second stamp. A fresh full-text request
returned HTTP 403. Neither the older article nor that abstract substitutes for
reading the 2026 argument. Its overlap with these restricted families remains
unresolved; the result above is a correctness reconstruction, not priority
clearance. No downloaded code was run.

## Verification and acceptance boundary

All twelve reconstruction tests pass. The eleven author tests also passed from
an isolated local copy of the four-file contribution, and the two independently
generated enlarged-family sets agreed exactly for 63 unequal-length cases
(`2<=a<=10`, `2<=b<=8`). They include the complete seven-face
universe (ten `MMVVMM` stacks, of which the adjacent family contains five),
whole-permutation controls for every assignment through six faces, the actual
collar bijection on 225 cases, both parities and unequal lengths, invalid input,
and the real command line. The independent family census checks `2<=a<=10`,
`1<=b<=8`; the enlarged-family screen checks `2<=a<=8`, `2<=b<=7`. Formula
values are never used to generate a stack or choose an insertion gap.

This reconstruction supports the restricted counting arguments required by
the first milestone. It does not complete the remaining prefix classes,
prove the cubic, establish novelty, or automatically accept source or advance
the project. The project owner still records the milestone decision after
reviewing this result. Sorrel's source and this new checker have distinct
integration decisions.
