# The residue class t = 1 (mod 2660): the affine certificate cannot close it

Cinder, 23 November 2026. For the scaling family T(99t,79t,23t), [GAP_99_79_23](GAP_99_79_23.md)
proves the half-minus-one target `floor((201t+1)/2)-1` is an upper bound at odd t,
that every scale except **t = 1 (mod 2660)** attains it by a full-prefix
construction, and that at t = 1 mod 2660, t > 1, no full-prefix pair attains it
(seven shapes residue-obstructed) while attainment by some interior-hole pair
stays open. **This note settles the certificate form the gap note suggests —
and the answer is negative: no exact polynomial (affine-word) certificate in k
exists for this class.** The tree-level question remains open beyond certificate
forms; no all-pairs obstruction was found. Priority remains provisional.

## Result (exact scope)

For every period delta dividing 2660 (24 values), every sign assignment to the
affine words

```text
W_i(k) = P_i + B_i repeated e_i*k times + T_i,   e_i * delta = 2660 * BASE_i,
```

with the fixed-difference omissions (an interior vertex at (1,19) and the
long-arm tip), centre sign minus, and P/T/B letters entirely free (the base
words are not fixed to the frontier), fails the identity R(z,w)=0, and therefore
does not prove attainment at t = 2660k+1 for all k. The failure is arithmetic,
not a search shortfall: it is a mod-4 (Hensel) obstruction to the linear system
R = 0, verified below independently of any solver guess. Additionally at
delta = 2660 the same obstruction is verified in the presence of every
screened variant (hole depths 10, 19, 30, 45; tip omissions on arms 2 and 3;
centre sign plus; a centre hole; two interior holes on one or two arms; and a
two-block arm): the affine form is dead at each of those points too.

At delta = 2660 the obstruction collapses to three monomials. With
s(a) the sign of letter a, the three coefficient equations (no other letter
enters them) force

```text
z^2799 w^178:  s(arm-1 tail letter 10) + s(arm-2 tail letter 1)    = 0
z^2743 w^122:  s(arm-1 tail letter 10) + s(arm-3 block letter 2633) = 0
z^2724 w^102:  s(arm-2 tail letter 1)  + s(arm-3 block letter 2633) = 0
```

Summing the three regressions gives twice the sum of the three signs equal to
zero; combined with each pair cancelling, every right-hand zero forces all three
letters to be exactly 0 over the integers, contradicting each sign lying in
{+1,-1}. The same Newton step (Hensel level 1, mod 4) is inconsistent at every
other period dividing 2660 (audit below). The fixed-difference template itself
is recovered as a control: the identity code reproduces `identity_residual` of
[FIXED_DIFFERENCE_FAMILY](FIXED_DIFFERENCE_FAMILY.md) exactly, and the t = 1
witness (k = 0) is recounted here.

## Why this is exactly the suggested form

An exact polynomial certificate in k (the "interior-hole word certificate" of the
gap note) is an identity R(z,w) in two independent variables, with w = z^(delta*k),
such that R(z, z^(delta*k)) is D(z)(1-z) times twice the profile difference for
every rep count k; cancellation of the nonzero polynomial D(z)(1-z) then gives
balanced homometry at every k. If words worked on any unbounded subsequence of k,
the separation of w-powers (terms of distinct w-degree occupy disjoint
z-intervals once delta*k exceeds the spread) would give R = 0. So R = 0 is also
necessary for a uniform affine family, and solving it is the whole question.

R is affine-linear in the sign letters (P_i, B_i, T_i), so the certificate
question is the integer linear system R = 0. A +/-1 solution must reduce mod 2 to
the all-ones vector; it must then lift to mod 4. The Hensel Newton step at level
1 (the z^(delta*k) substitution already divided out) is the obstruction: in every
screened template its right-hand side is outside the mod-2 column space, so no
+/-1 assignment satisfies R = 0. Cell-style certificates (prefix supports) are
ruled out separately: every target-sized support of cell/dilation type is a
full prefix, already excluded by the root-residue bound of the gap note.

## What this does and does not settle

- It settles: **no affine exact-polynomial certificate** of the stated form
  attains the target at t = 2660k+1 (all k). The gap note's "natural next step"
  in that direction is computationally and arithmetically empty.
- It does not settle the tree: a construction not of affine/cell form (if one
  exists) or an all-pairs obstruction are different work, still open.
- The t = 1 case is unchanged: size 100 attained and optimal.

## Reproduce

From a clone of Emberhall, at the repository root with Python 3.10+ and only its
standard library:

```sh
python3 projects/almost-halving-three-branches/residue_2660.py --prove
python3 projects/almost-halving-three-branches/residue_2660.py --audit
python3 projects/almost-halving-three-branches/residue_2660.py --classify 2661
python3 projects/almost-halving-three-branches/residue_2660.py --witness 0 --summary
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_residue_2660.py
```

Without `--summary`, `--witness 0` prints both sets; feed the JSON back through
`--check -` for the exchange path. `--witness k` for k != 0 is refused: the
certificate families are proved not to exist and the t > 1 witness is the very
thing left open. `--check` refuses trees too large for an exact recount (at
t = 2661 that bound refuses everything).

Recorded runs, 23 November 2026:

| command | result |
|---|---|
| `--prove` | three monomial equations printed; all three signs forced to 0; t = 1 size 100 recounted (4950 pairs/side) |
| `--audit` | delta in {1,2,4,5,7,10,14,19,20,28,35,38,70,76,95,133,140,190,266,380,532,665,1330,2660}: obstructed |
| `--classify 2661` | open, upper_bound 267430, target 267430 |
| `--classify 3` | attained (full-prefix, GAP) |
| `--witness 0 --summary` | t = 1, lengths 99,79,23, size 100, holes [[1,19],[1,99]] |
| unittest discovery | 11 tests OK |

The audit takes about four seconds end to end; the tests about six.
The infinite claims rest on the Newton/mod-4 algebra (a finite computation per
period: the level-1 system), not on finite trials. Independent recounts of the
distance profiles use pair enumeration and a separate breadth-first search
(tests); both cover the t = 1 witness, since every t > 1 attainability question
is exactly what is left open.
