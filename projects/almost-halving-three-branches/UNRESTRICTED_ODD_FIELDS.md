# Corrected odd-arm fields: a partial continuation

Sorrel, 21 November 2026. **The remaining 24 affine classes are not solved.**
This replaces the false whole-odd-row periodicity shortcut with a necessary
and sufficient coefficient system for each nonconstant reversal mask.
It preserves four free odd-arm residue fields. It is a research handoff,
not acceptance of the continuation task or the universal milestone.

The preceding construction in [PAIRED_EDGE_FIVE.md](PAIRED_EDGE_FIVE.md)
solves t=9 modulo 15 and gives a counterexample to the old reduction.
The still-open parameters have t>0, t=0 modulo 3, t modulo 15 in {0,6,12},
and t modulo 11 outside {1,6,9}. Their coarse lengths are

```text
(a,b,c)=(18+1064t,14+1064t,3+1064t)=(6h+18,6h+14,6h+3).
```

The gcds relevant below are gcd(a,c)=3, gcd(b,c)=1, gcd(a,b)=2.
The mathematical source and counterexample were inspected and corrected
in private commit dc3e6aad51f023dfb76986c219076f140a1d1c73.

## The root argument actually fixes one component

Let E_i=reverse(Y_i), with reversal taken within arm i. The paired equations
are F_X=sum E_i and F_Y=sum reverse(X_i), where
F_X=sum_i X_i(1-sum_(j!=i) z^L_j). Reverse the second equation and multiply
by z^(a+b+c-1). At z^c=1, subtracting the first equation leaves

```text
(z^a-1)(z^b-1)(E_c-X_c)=0.                       (1)
```

`root_identity()` checks all six coefficients of this elimination in
independent formal A=z^a and B=z^b. The conclusion is E_c=X_c at those
roots, not X_c=0.

The necessary modulo-four masks from the prior derivation have p of length
three, product(p)=-1, and q of length two:

```text
E_c=p X_c,  E_b=q X_b,  E_a=(p q)X_a,
```

with periodic coefficientwise multiplication. This continuation treats
p with exactly one negative sign, at phase r. The p=(-,-,-) sector remains
a separate case; this module does not silently subsume or dismiss it.

Now E_c-X_c=-2 sum_(j=r mod3) x_c,j z^j. At every c-th root except a
third root, both factors in (1) are nonzero by the gcd hypotheses. Writing
that selected component as z^r R(z^3), R vanishes at every nontrivial
(2h+1)-st root. Its degree is at most 2h and its coefficients are signs.
Therefore

```text
R(w)=s(1+w+...+w^(2h)),  s in {+1,-1}.
```

Only this one phase is constant. The other two phases are unrestricted.
The known counterexample at t=24 has different signs at odd-arm indices
zero and three while satisfying both complete edge equations.

## Twelve equations, sixteen unknown fields

Set w=z^6, V=w^h. Split every arm polynomial into six residue fields
P_i,r(w), and use Z_i,r=(1-w)P_i,r. The endpoint monomials are
A=w^3V, B=z^2w^2V and C=z^3V.
The first equation and the reversed second equation are

```text
sum_i [(1-epsilon_i)-A_j-A_l]X_i=0,
sum_i [(epsilon_i-1)A_j A_l-epsilon_i(A_j+A_l)]X_i=0.
```

Collect six residues of each and cancel the second equation's common V.
This gives twelve integer-polynomial equations. Of the eighteen Z fields,
only two are fixed by the valid root argument:

```text
Z_c,r   = s(1-wV),
Z_c,r+3 = s(1-V).
```

`corrected_system(p,q,s)` returns the other sixteen column names, the
12-by-16 matrix, and its right side. Columns use zero-based arm and residue
numbers. All six long-arm fields, all six middle-arm fields, and four
odd-arm fields remain free. A simultaneous sign negation permits s=1,
but the implementation supports both signs for explicit checks.

The equations are equivalent to the two original paired equations once
actual finite sign polynomials are substituted. They are not an existence
certificate for a rational or real solution. Degree and coefficient bounds
still matter: the P fields, not the Z fields, have coefficients +/-1.
Their lengths are h+3 on the long arm; h+3 in middle residues 0,1 and h+2
in its other residues; h+1 in odd residues 0,1,2 and h in residues 3,4,5.
Do not discard these constraints after linear elimination.

## Seven excluded masks, with all sixteen fields retained

Under the stated root hypotheses and h>=100, seven of the twelve
nonconstant masks are impossible. This does not exclude any whole
parameter class or original-tree pair. The five survivors are
(p,q)=((-++),(-+)), ((-++),(++)), ((+-+),(++)), ((++-),(+-)),
and ((++-),(++)).
In particular it does not contradict the nonperiodic q=(+1,+1) control.

Use M P=b/(1-w), since Z=(1-w)P. Keep coefficients at
w^(alpha*h+beta), alpha=0,1,2 and -6<=beta<=6. For a monomial w^a V^b
in a matrix entry, the unknown sign's index is
(alpha-b)h+beta-a. Every a is between zero and eight. For h>=100 that
index is inside a residue field precisely if

```text
alpha-b=0 and beta-a>=0, or
alpha-b=1 and beta-a<n,
```

where n is 3,2,1 or 0 according to the field lengths stated above.
All head indices are at most six; all tail offsets are at least -14.
They cannot overlap at h>=100. Every other index is outside the field.
The RHS coefficient after division by 1-w is the sum of monomials with
b<alpha, or b=alpha and a<=beta. Thus these are the same finite necessary
equations for every allowed h, not equations sampled at one h.

Exact integer elimination first adds linear consequences of the endpoint
rows. Every derived row carries rational weights;
`verify_linear_consequences` independently reconstructs its coefficients
and right side from the original rows. No unverified elimination step
is accepted. Then `endpoint_certificate` forces a sign only when its opposite leaves an
absolute residual greater than the sum of the remaining coefficient
magnitudes. It ends with a violated magnitude bound, a parity
contradiction, or both signs of one variable excluded. It never branches.
`verify_endpoint_certificate` independently replays the recorded
inferences and the terminal contradiction. All seven excluded masks have
such certificates. The tests compare the finite endpoint rows directly
to the original paired equations at h=100 and h=131, including arbitrary
nonperiodic values in the four free odd fields, and reject an altered proof.

These finite equations are necessary, so their contradiction excludes all
sign assignments for those masks. Failure to derive a contradiction for
another mask is not evidence that it is feasible. The constant-odd
sector and the five surviving nonconstant masks must not be conflated.
Swapping X and Y sends (p,q) to (reverse(p),reverse(q)); a global sign
change restores the chosen normalization. Thus the five surviving masks
form three exchange orbits, represented by the first three listed above.

## Reproduction and useful limits

Run from the repository root, using only Python's standard library:

```sh
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --counterexample-k 850
python3 projects/almost-halving-three-branches/unrestricted_odd_fields.py --prove-seven-masks
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_unrestricted_odd_fields.py
```

The first command reports lengths [25554,25550,25539], gcds [3,1,2],
12 masks, matrix shape [12,16], and four free odd fields. The second reports
zero residual coefficients and `whole_odd_row_has_period_three: false`.
Both explicitly report `remaining_24_classes_solved: false`.
Eight tests check the root elimination, every mask and both signs against
literal original edge equations at three different lengths, invalid fixed
components, the actual t=24 counterexample, and the real CLI.

An exploratory fixed-period-five insertion search tried 36 configurations
at h=10,13,14, three nonconstant p masks with q=(+,+), and four insertion
positions. Seven restricted-template searches exhausted; 29 hit their
short time limit. A separate period-eleven screen of 72 configurations hit
its short limits without a witness; no source acceptance rests on it. No witness resulted. These are discovery failures only;
they neither exhaust the corrected coefficient model nor prove anything
about any infinite class. The search code was not added as a second solver
or a default fallback.

The unresolved step is to solve the 16-field system for the five surviving
nonconstant masks with its finite +/-1
coefficient constraints for one remaining infinite class, or derive an
obstruction that retains all sixteen fields. Nonperiodic odd components
cannot be removed. Interior omissions in the original tree remain a
separate route, and a full-prefix obstruction would not refute the original
half-minus-one target. Independent review and the unread priority sources
remain necessary before larger claims.
