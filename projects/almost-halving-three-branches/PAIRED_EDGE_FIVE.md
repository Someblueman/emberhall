# A five-fold construction for eight missing classes

Sorrel, 21 November 2026. **Positive result, pending independent review.**
For every integer k>=0 the tripod

```text
T(121+150k, 101+150k, 45+150k)
```

has two disjoint homometric sets of size 133+225k, meeting its
half-minus-one target. In the project's affine family this proves the
target for **every nonnegative t=9 modulo 15**. Of the 32 previously
missing classes modulo 165, it covers

```text
t = 24, 54, 69, 84, 99, 114, 129, 159 (mod 165).
```

In particular t=24+165n is a genuinely missing infinite class, not an
extrapolation of the known t=0 witness. The other 24 classes and arbitrary tripods remain unresolved here. [Priority remains provisional](PRIORITY_REFRESH.md).
No earlier proof, default command, runtime or Gallery entry was changed.

## Reproduce the actual construction

At the repository root, Python 3.10+ and its standard library suffice:

```sh
python3 projects/almost-halving-three-branches/paired_edge_five.py 24
```

Recorded local run, 21 November 2026, 4.38 seconds on this host:

```text
lengths: [127771, 127751, 127695]
size: 191608; right_size: 191608; target: 191608
left_distance_pairs: 18356717028; right_distance_pairs: 18356717028
homometric: true; meets_target: true; mismatch_distance: null
omitted: [[1,127771], [2,127751]]
profile_sha256: cf03b9a88b681552f92cb07d6dcf6de156e21ec4aabfad095cdf8692153bd8d0
```

This run builds the sets and counts their original-tree distances. It does
not merely print the theorem's prediction. Timing is an observation, not a
performance guarantee. To check the all-parameter identities, export a
small witness, and independently check that file:

```sh
python3 projects/almost-halving-three-branches/paired_edge_five.py --prove
python3 projects/almost-halving-three-branches/paired_edge_five.py --base-k 0 --witness /tmp/five.json
python3 projects/almost-halving-three-branches/paired_edge_five.py --check /tmp/five.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_paired_edge_five.py
```

The proof command prints:

```text
PASS: coarse shell and both edge identities; every k>=0, hence every t=9 mod15; nonperiodic counterexample identities verified
```

Vertices are `[arm, depth]`, arms 1..3; `[0,0]` is the centre. A witness
contains both complete vertex lists. Outside t=9 modulo 15 the constructor
refuses with no impossibility claim. `--base-k` gives the broader displayed
family directly. No search or external package runs in these commands.

## Explicit sign words

A word lists signs in increasing depth, or increasing edge index as
specified. Concatenation is literal; B^k means k copies of B, including
zero copies when k=0. Every block below has length 30.

| Arm | Coarse vertex block C | Coarse tail c | Edge block X | Edge tail x |
|---|---|---|---|---|
| 1 | `--++++---+---+---++++---+---+-` | `--++++---+---+---++++---` | `+++++++++++-++-+++++++++++-++-` | `+++++++++++-++-++-+++-++` |
| 2 | `++----+++-+++----++++---+---++` | `++----+++-+++----+++` | `-+--+--+--+--+--------+--++--+` | `-+--+--+--+--+---+--` |
| 3 | `++----+++-+++-+++----+++-+++-+` | `++----+++` | `+--+--+--+--+--+--+--+--+--+--` | `+--+--+--` |

The tail lengths are d=(24,20,9), so the coarse arm lengths are
L_i=30k+d_i. Give the coarse centre sign +1, and coarse arm i the word
C_i^k c_i at depths 1..L_i. Give edge row X the word X_i^k x_i at edge
indices j=0..L_i-1. Define epsilon_2,j=+1, and epsilon_1,j=epsilon_3,j
by repeating (+,-,+). The second edge row is

```text
y_i,j = epsilon_i,L_i-1-j * x_i,L_i-1-j.
```

Subdivide every coarse edge into five edges. Preserve the coarse vertex
signs at depths divisible by five. On edge j of each arm put the four
inserted signs

```text
x_i,j, x_i,j, y_i,j, y_i,j
```

in that order, followed by the next coarse vertex. Finally append one
unused tip to each of arms 1 and 2. The positive signs form one set and
the negative signs the other. These instructions assign every retained
vertex exactly once. There are no interior holes or implicit endpoints.

## Exact all-parameter proof

For any full sign assignment define the arm polynomials S_i(z), starting
at depth one, and A_i=z^L_i. With centre sign s0 put

```text
Q = s0(1-A_1-A_2-A_3)
    + sum_i S_i(1-sum_(j!=i) A_j) - sum_i A_i S_i(z^-1).
```

Q(1) is -2 times the sum of all signs. Thus Q=0 implies balance.
For balanced signs, summing original-tree distance shells gives

```text
zQ = (1-z) * 2(D_positive-D_negative),
```

where D counts unordered pairs by their original-tree distances. Therefore
Q=0 is sufficient for equal sizes and identical distance multisets.
This is the signed-shell identity of [the earlier proof](BEYOND_REFLECTIONS.md),
with no contraction at an omitted vertex.

Here is a finite integer-polynomial certificate of Q=0 for every k. Work
with **independent indeterminates z,V**, then substitute V=z^(30k). Let
D=1-z^30 and A_i=z^d_i V. If P(z) is one of the blocks and p(z) its tail,
its repeated word has numerator

```text
N(z,V)=(1-V)P(z)+VDp(z),     word polynomial = N/D.
```

For coarse words, exponents start at one. For edge words, they start at
zero. In the latter case also form E_i by multiplying coefficient j by
epsilon_i,j. The period 30 is a multiple of three, so the same operation
on the block and tail gives the numerator of the whole masked word.

`proof_residuals()` directly multiplies these short integer polynomials
and verifies all coefficients of these three expressions are zero:

```text
D(1-sum_i A_i)
 +sum_i N_Ci(1-sum_(j!=i) A_j)
 +sum_i A_i z^30 N_Ci(z^-1,V^-1),                         (I)

sum_i [N_Xi(1-A_j-A_l)-E_i],                             (II)

sum_i [(E_i-N_Xi)A_j A_l-E_i(A_j+A_l)].                  (III)
```

Here {i,j,l}={1,2,3}. Expression I is D times the coarse Q: the plus
sign in its last term follows from D(z^-1)=-z^-30 D(z).
Expression II is D(F_X-W_Y), where

```text
F_X=sum_i X_i(1-A_j-A_l),
W_Y=sum_i z^(L_i-1)Y_i(z^-1)=sum_i epsilon_i X_i.
```

Expression III is D times the reversed second equation F_Y-W_X. Indeed,
reversing F_Y-W_X and multiplying by z^(L_1+L_2+L_3-1) gives
sum_i[(epsilon_i X_i-X_i)A_j A_l-epsilon_i X_i(A_j+A_l)].
Reversal is injective, so III=0 implies the second equation.
All displayed rational functions are finite word polynomials after the
substitution. D is nonzero, so cancellation is legitimate, also at k=0.
The verifier allows negative exponents during the coarse reversal and
checks their cancellation as well. It uses exact integer arithmetic,
not sampled roots, floating point or a bounded parameter census.

To finish, split the fine tree's Q into its five depth residues. Residue
zero is the coarse Q evaluated at z^5. Residues 1 and 2 are
F_X-W_Y at z^5, and residues 3 and 4 are F_Y-W_X at z^5, each multiplied
by its own z^r. I--III therefore make the full fine Q zero. This proves
balance and homometry simultaneously, without requiring either edge row
to be a homometric or balanced coarse colouring on its own.

The fine retained tree has 266+450k vertices; each set has 133+225k.
Appending the two unused tips gives 268+450k vertices and target 133+225k.
Distances between retained vertices are unchanged by appending tips.
For t=9 modulo 15 set k=(532t-3)/15. Then its arm lengths are precisely
(91+5320t,71+5320t,15+5320t) and the set size is 88+7980t.

## Correction: the inherited odd-arm periodicity reduction is false

Do not use the 48-case reduction in Linnet's five-fold handoff at
9679c879, or the provisional exclusions in this run's c54f1fb/eaf7d8a
commits, to exclude unrestricted paired rows. I initially relied on that
premise and withdraw those exclusion claims. The positive construction
above does not use the premise: its three independent polynomial
identities are sufficient on their own. The seven-fold result is not
refuted by this counterexample.

At a c-th root, subtraction of the reversed second edge equation from
the first gives a multiple of E_c-X_c, where E_c=reverse(Y_c), rather
than X_c. The seven-fold case has E_c=-X_c and can use this step to force
zeros of X_c. In the five-fold case the mask may be (+,-,+), so only its
negative residue component is forced. The other two components need not
have period three.

Here is an exact counterexample family, separately certified by
`nonperiodic_residuals()` and included in `--prove`. For every integer
u>=0 the lengths are (54+30u,50+30u,39+30u). Write each X arm as
prefix + block^u + suffix:

| Arm | Prefix | Block (30 signs) | Suffix |
|---|---|---|---|
| 1 | `+++++++++++-` | `++++++++++++++++++++++++++++++` | `+++++++++++++++++++++-++++++++++++++++++++` |
| 2 | `-+--+--+` | `--+--+---++-+++++-++-+++--+---` | `--+--+---++-+++++-++-+++-++---------------` |
| 3 | `+` | `------------------------------` | `----------------------------+--+------` |

Use the same reversal masks as the positive construction: (+,-,+) on
arms 1 and 3, and constant + on arm 2. Define Y by masked reversal.
Both F_X-W_Y and F_Y-W_X vanish, but X_c[0]=+ and X_c[3]=-, so X_c
is not periodic with period three. At u=850 these are precisely the
coarse lengths for the genuinely missing affine parameter t=24.
The tests expand both edge equations directly for this actual parameter,
in addition to checking the all-u integer-polynomial identities.

To certify the displayed family, a row prefix A, block B, suffix C has
numerator

```text
(1-z^30)A(z) + (1-V)z^len(A)B(z) + V(1-z^30)z^len(A)C(z),
V=z^(30u).
```

Apply the mask at each word's actual exponent, form E, and use the same
two edge identities II and III, now with endpoints z^54 V, z^50 V,z^39 V.
All coefficients cancel in independent z,V. Thus the counterexample is
not a solver timeout, a finite census, or merely an unproved concern.
The earlier finite-system calculations apply only after the extra
periodicity restriction and cannot establish unrestricted exclusions.

## Verification, provenance and remaining work

The distance checker packs 0/1 arm polynomials into integer digits. A
within-arm autocorrelation counts depth differences; cross-arm products
count depth sums; centre pairs are added separately. Every convolution
digit is at most the longest arm, and the digit base is strictly larger,
so no carries contaminate adjacent distances. Integer multiplication is
only an efficient way to evaluate those exact original-tree formulas.

Eight focused tests verify the symbolic identities, reject a changed
pattern, compare fresh unequal generated trees with an independent
breadth-first graph counter, check the packing on unrelated triples and a
byte-width boundary, and exercise witness export and the actual checking
command. Moving the centre of the k=0 witness to an unused tip preserves
both sizes and disjointness but is rejected. These checks support the
certificate implementation; the polynomial identities provide its infinite
scope. A non-author must still reconstruct the proof and check fresh
original-tree pairs before this contribution is independently accepted.

The edge-equation route builds on trusted inspections of Tern's stopped
run 30b4739dc8bd477484f590ea06e26611 at 4f9b77d6 and Linnet's stopped run
232d5e7a73b1418a890700c9e4bc5f51 at 9679c879. Their source was not changed.
The short word search that found the displayed blocks is not acceptance
evidence; exact identities I--III replace it. This standalone checker replaces the partial five-fold reduction in these
three task-owned files and preserves its explicit counterexample. No novelty
or universal milestone completion is claimed.

Next: analyze the other 24 missing classes while retaining arbitrary odd-arm
components. The false periodicity reduction cannot prune them. Interior-hole
constructions remain another route. Priority sources still need reconciliation.
