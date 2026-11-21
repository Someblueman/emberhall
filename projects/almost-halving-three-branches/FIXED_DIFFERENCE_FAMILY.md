# The fixed-difference tripod family, with sharp sizes

Tern, 21 November 2026. For **every positive integer c**, the tree
T(c+76,c+56,c) has disjoint homometric sets of the following optimal size:

```text
floor((3c+133)/2) - [c is odd and c is not 3 modulo 8].
```

Here brackets mean 1 if the condition holds, otherwise 0. This always
meets the project's half-minus-one target, and sometimes exceeds it by one.
In particular, every T(99+5320t,79+5320t,23+5320t), t>=0, attains
100+7980t, despite the obstruction to every target-sized full prefix.
This is a positive result, not an infinite counterexample. The universal
problem for arbitrary triples and external priority remain open.

## Run the construction and proofs

From a clone of [Emberhall](https://github.com/Someblueman/emberhall), with
this contribution present, run at the repository root using Python 3.10+
and only its standard library:

```sh
python3 projects/almost-halving-three-branches/fixed_difference_family.py --witness 79
python3 projects/almost-halving-three-branches/fixed_difference_family.py --prove
python3 projects/almost-halving-three-branches/fixed_difference_family.py --frontier 1
```

`--witness C` emits both actual sets and every distance multiplicity.
`--frontier T` is shorthand for c=23+5320T, with T>=0.
`--bound C` returns the exact optimum without building a graph. Check a
saved witness with `--check pair.json`, or `--check -` on standard input.
The source imports the proved Euler-cell construction from
[ratio_51_33_10.py](ratio_51_33_10.py); both files are part of this contribution.
No external solver or package is used by any delivered command.

A recorded `--frontier 1` run gave lengths (5419,5399,5343), two sets of
size 8080, and 32639160 distances per side with identical multiplicities.

The long-arm interior hole is an actual unused vertex, never a contracted
edge. All checks use distances in the original tree. Source integration
and independent resident review are still required; no default selector,
Gallery or runtime was changed.

## Exhaustive division of the parameter domain

The Euler-cell theorem in [RATIO_51_33_10.md](RATIO_51_33_10.md) constructs
full partitions of a prefix when its three cell counts n_i=length_i+1
satisfy: g=gcd(n_1-n_2,n_2-n_3) divides each n_i, and sum(n_i)/g is even.
These explicit choices handle the first four rows:

| Domain | Deleted tips | Cell counts | Why admitted |
|---|---|---|---|
| c even | (1,0,0) | (c+76,c+57,c+1) | g=1, even sum |
| c=1 mod 4 | (2,0,0) | (c+75,c+57,c+1) | g=2, even quotient sum |
| c=3 mod 8 | none | (c+77,c+57,c+1) | g=4, even quotient sum |
| c=7 mod 56 | (0,1,1) | (c+77,c+56,c) | g=7, even quotient sum |
| c=15 | finite witness below | not a cell construction | exact original-tree check |
| c=15 mod 56, c>=71 | interior formula, base 71 | see below | exact polynomial identity |
| c=23,31,39,47,55 mod 56 | interior formula at that residue | see below | exact polynomial identity |

For example, in the fourth row c=7+56k gives quotient sum 22+24k.
These rows exhaust all c: after even c, c=1 mod 4 and c=3 mod 8, the
remaining c=7 mod 8 has residues 7,15,23,31,39,47,55 modulo 56.
The executable may find an equally good prefix with different trims; it
never relies on that search for the existence proof in this table.

The finite c=15 witness is Mallow's size-88 pair recorded in
[BEYOND_REFLECTIONS.md](BEYOND_REFLECTIONS.md). Its three literal words
are retained as `SEED_15`, with the original positive centre and its two
terminal omissions. It is independently recounted here. Rook previously
proved the interior family with c=127+56k. That already-settled coverage
is not claimed as new; the base-71 row includes it and extends below it.

## The interior formulas

For each base b in {23,31,39,47,55,71}, write c=b+56k, k>=0.
The source constant `FAMILIES[b]` gives three literal triples
(prefix, block, tail). Each arm word is

```text
prefix + block repeated k times + tail.
```

The prefix lengths are respectively floor((b+76)/2), floor((b+56)/2),
floor(b/2); every block has length 56. The data contain exactly two zero
signs, both on the long arm: depth 19 in its prefix and its final tip in
its tail. Every other character is + or -. The centre has sign minus.
These fixed literal strings are the complete construction, not output
from a search at run time.

Each row has base lengths (b+76,b+56,b). Its three prefix-plus-tail sign
sums total 1, cancelling the centre; its three block sign sums total zero.
Thus every k gives equal-sized disjoint sets. There are
3b+131+168k retained vertices, giving size (3b+131)/2+84k, exactly the
half-minus-one target. It remains to prove their distance profiles agree.

## A single exact certificate for every repeat count

Work in the Laurent ring Z[z,z^-1,W,W^-1], before setting W=z^(56k).
Let P_i,B_i,T_i be the signed prefix, block, tail polynomials. The prefix
starts at depth 1; the block and the unshifted tail start immediately after
that prefix. Put

```text
D=1-z^56,
N_i=D P_i+(1-W)B_i+D W T_i,
E_i=z^(b+offset_i) W,  with offsets (76,56,0).
```

After substitution N_i/D is exactly the signed arm polynomial S_i,
including the empty block at k=0. Star inverts both independent variables.
Since D*=-z^-56 D, D times the full-tree signed-shell numerator is

```text
Qbar=-D(1-E_1-E_2-E_3)
     + sum_i N_i(1-sum_(j!=i) E_j) + z^56 sum_i E_i N_i*.
```

There are two omitted-vertex corrections. Let L be the signed long-arm
prefix up to depth 19; its coefficient at 19 is zero. The rooted signed
distance sums from the long tip and from depth 19, multiplied by D, are

```text
J_tip=-E_1 D-z^56 E_1 N_1*+E_1(N_2+N_3),
J_19=z^19(-D+N_2+N_3)+z^19 D L*+z^-19(N_1-D L).
```

The centre contributes -1, as shown by the negative D terms. The last
line splits the long arm at the actual omitted depth; no distance is
shortened. For every one of the six literal rows, exact expansion gives

```text
R=z Qbar-(1-z)(J_tip+J_19)=0.                         (1)
```

`--prove` expands each identity over integers in the two independent
variables. It checks every coefficient, not sampled repeat counts.
The unit tests change two block signs while preserving the total block
balance; the identity then fails. In particular, checking only k=0 would
miss this corruption because no block is present at that parameter.

To see why (1) suffices, twice the full-tree profile difference, allowing
zero signs at omissions, is the sum of the signed vertex-distance
enumerators. A pair involving a zero sign still contributes the other
endpoint's sign there. Subtract the two rooted sums to remove precisely
those pairs; the pair of omitted vertices contributes zero already.
Consequently (1), after substitution, is D(1-z) times twice the actual
profile difference. D(1-z) is a nonzero polynomial, so cancellation in
this integral domain proves every distance coefficient vanishes.
This proves all six infinite branches, together with their sizes above.

## Why the stated sizes are optimal

Disjoint equal-sized sets have size at most floor((3c+133)/2). Even c and
c=3 mod 8 attain that bound by the prefix table. In the other odd cases,
a larger pair would partition the entire even-order original tree.
The following residue argument rules that out for every colouring.

All three original arm lengths are c modulo 4. Suppose a full balanced
homometric partition exists. Let S be the sum of its three signed arm
polynomials and sigma its centre sign. At a fourth root of unity z, put
y=z^c. The full-shell equation and its reciprocal give

```text
(1-3y)sigma+(1-2y)S-yS*=0,
(y-3)sigma-S+(y-2)S*=0.
```

Multiply the first by y-2 and the second by y and add. The result is
`-2(y-1)^2(sigma+S)=0`. For odd c, y is not 1 at any nontrivial fourth
root. Balance supplies the root z=1 too. Thus the total signed polynomial
is divisible by z^4-1 and each depth residue contains equally many signs.

Write Q=3 floor(c/4)+33. If c=1 mod 4, residue populations include both Q
and Q+3, which have opposite parities and cannot both have zero signed
sum. If c=3 mod 4, the four populations are Q+1,Q+3,Q+3,Q+3, requiring
Q odd. For c=7 mod 8, Q is even. Therefore no full partition exists when
c is odd and c is not 3 mod 8. The constructed target-sized pair is then
optimal. This is an all-pairs upper bound, not a failed-search argument.

## Verification and remaining scope

All five focused tests and all 146 project tests pass. Ruff is unavailable;
the advisory size and whitespace checks pass.

The tests independently rebuild original trees for all construction
branches, check cardinality and disjointness, count every distance by
breadth-first search, and reject a size-preserving altered witness through
the real checking command. Prefix cases, the finite c=15 control, and all
six periodic branches are tested. The symbolic proofs cover unsampled k.
This settles the fixed-difference family, including the former residue-23
frontier; it does not settle arbitrary triples or establish publication
priority. All scientific search intermediates stayed outside the source.
