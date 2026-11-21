# The unrestricted seven-fold edge pair is impossible on the missing classes

Linnet, 21 November 2026. The paired-edge construction on
`L=(13+760t,10+760t,2+760t)` fails for **every** previously missing parameter
class: `t=0 mod 3`, `t!=3 mod 15`, and `t mod 11` outside `{1,6,9}`.
This excludes arbitrary signs on every edge in both rows, not just periodic
words or rows obtained from coarse colourings. In particular `t=165n`, for
every integer `n>=0`, is an explicit uncovered infinite obstruction family.

It also excludes every full homometric partition of the seven-fold prefix
`(91+5320t,70+5320t,14+5320t)`, even when different mirrored edge layers
use different pairs and the old coarse colouring is not fixed in advance.
It is **not** an upper bound over arbitrary vertex pairs on the original tree, and does not
refute or prove its size target `88+7980t`. The universal milestone and
[literature priority](PRIORITY_REFRESH.md) remain open. The earlier
[subdivision obstruction](BEYOND_REFLECTIONS.md) supplies context; the
argument here was independently derived without importing the active
edge-dependent contribution.

## Reproduce

From a complete repository clone, Python 3.10+ and its standard library:

```sh
python3 projects/almost-halving-three-branches/mixed_edge_seven.py --prove
python3 projects/almost-halving-three-branches/mixed_edge_seven.py 165
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_mixed_edge_seven.py
```

The recorded proof command prints
`PASS: exact reflection eliminations and t=165*n obstruction arithmetic`.
The parameter command reports coarse lengths `[125413,125410,125402]`,
pairwise gcds `[1,1,2]`, failed divisibilities `[false,false]`, and
`paired_edge_assignment_excluded: true`. Its separate field
`arbitrary_vertex_pairs_excluded` is false.

## A more general necessary condition

Let `a>b>c>0`, with a odd, `b=c=2 mod 4`, and

```text
gcd(a,b)=gcd(a,c)=1,       gcd(b,c)=2.                 (1)
```

For arbitrary signs `x_i,k,y_i,k` in `{−1,+1}`, put

```text
X_i=sum_(k=0)^(L_i-1) x_i,k z^k,     Y_i likewise,
(A,B,C)=(z^a,z^b,z^c),
F_X=sum_i X_i(1-sum_(j!=i) z^L_j),
W_X=sum_i z^(L_i-1) X_i(z^-1).
```

**Theorem.** If `F_X=W_Y` and `F_Y=W_X`, then either
`2(a-c)` divides b or `2(a-b)` divides c. No assumption is made about a
coarse vertex colouring, the number of sign changes, or the signs' period.

### 1. Reduction modulo four forces four reflection cases

Let `H_i=1+z+...+z^(L_i-1)`, and write `X_i=H_i−2P_i`, `Y_i=H_i−2Q_i`.
The coefficients of P and Q are bits. The two equations give

```text
F_P-W_Q=R,   F_Q-W_P=R,
R=(AB+AC+BC-A-B-C)/(1-z).                              (2)
```

Work now in `F_2[z]`; a star substitutes `z^-1`. Define
`D_i=P_i+z^(L_i-1)Q_i*`. The first equation becomes

```text
sum_i D_i + sum_i (sum_(j!=i) z^L_j) P_i = R.
```

Reverse the second equation and multiply it by `z^(a+b+c-1)`.
Add the first. Since `z^(a+b+c-1)R*=R`, the result is

```text
(1+B)(1+C)D_1+(1+A)(1+C)D_2+(1+A)(1+B)D_3=0,
or D_1/(1+A)+D_2/(1+B)+D_3/(1+C)=0.                   (3)
```

The gcd identity `gcd(1+z^r,1+z^s)=1+z^gcd(r,s)` holds in this field,
including repeated factors. Condition (1) and the degree bounds on D give

```text
D_1=d H_1,
D_2=(u+vz)(1+z^2+...+z^(b-2)),
D_3=((u+d)+(v+d)z)(1+z^2+...+z^(c-2)).                (4)
```

Indeed each denominator's factors absent from the other two must divide
its numerator in (3); the only shared factors are `1+z` for arm 1 and
`1+z^2` for arms 2 and 3. Substitution in (3) gives the displayed relation
between their remaining constant or linear numerators.

At z=1, the first equation in (2), modulo two, says `sum D_i(1)=R(1)=1`.
Here a is odd, b/2 and c/2 are odd, and `(b+c)/2` is even. Thus (4) gives
`d=1`. Returning from bits to signs, for two constants `alpha,beta` in
`{−1,+1}` we have, at **every** edge,

```text
x_1,k = -y_1,a-1-k,
x_2,k = alpha beta^k y_2,b-1-k,
x_3,k = -alpha beta^k y_3,c-1-k.                      (5)
```

This is a necessary consequence of the unrestricted equations, not an
extra template assumption.

### 2. The longest row is constant

Write `epsilon=(-1,alpha,-alpha)` and `beta_i=(1,beta,beta)`.
By (5), `W_Y=sum epsilon_i X_i(beta_i z)`. Reverse `F_Y=W_X` and multiply
by `z^(a+b+c-1)`. It becomes

```text
sum_i epsilon_i(A_j A_k-A_j-A_k) X_i(beta_i z)
    -sum_i A_j A_k X_i(z)=0,                         (6)
```

where `{i,j,k}={1,2,3}`. At any a-th root z, subtract `F_X=W_Y` from
(6). All terms except `−2(B−1)(C−1)X_1` cancel. At every nontrivial
a-th root, condition (1) makes both B−1 and C−1 nonzero. Hence H_1
divides X_1. Its degree and sign coefficients force `X_1=d H_1`,
`d=+1` or `−1`. Negate both rows if necessary, so d=1 below.

### 3. The two constant reflection cases

Suppose beta=1. Subtracting the full equations, not just their evaluations,
gives the following exact consequences:

| alpha | Consequence of (6) minus the first equation | Remaining equation |
|---|---|---|
| +1 | `(1-C)X_1+(1-A)X_3=0` | `(1+z^(a-c))X_2=H_(a-c)(1-B)` |
| −1 | `(1-B)X_1+(1-A)X_2=0` | `(1+z^(a-b))X_3=H_(a-b)(1-C)` |

The cancelled factor is respectively `−2(1-B)` or `−2(1-C)`, a nonzero
polynomial. In the first row X_3=−H_c; in the second X_2=−H_b.
Over the rationals, H_r and `1+z^r` have no common root. Also
`1+z^r` divides `1−z^m` exactly when `2r` divides m. The table therefore
proves the theorem's two divisibilities for beta=1.

### 4. Alternating reflection is impossible when b differs from c

For beta=−1, exchanging X and Y changes alpha's sign, so take alpha=1.
Set `U=X_1(z)`, `V=X_1(−z)`, `P=X_2(z)`, `Q=X_2(−z)`, `T=X_3(z)`,
`S=X_3(−z)`. Equations (5),(6), and their substitutions at −z give

```text
M (P,Q,T,S)^t = -(K U, J U, K V, J V)^t,
K=2-B-C,   J=-2BC+B+C,

M = [ 1-A-C       -1          1-A-B        1       ]
    [ -AC         AC-A-C     -AB          -AB+A+B ]
    [ -1          1+A-C       1            1+A-B  ]
    [ -AC+A-C     AC          AB-A+B       AB     ].
```

Its determinant is `4(A−1)(A+1)(A^2−BC)(B−1)(C−1)`, a nonzero
polynomial after specialization, since `2a>b+c`. Substituting
`U=(1-A)/(1-z)` and `V=(1+A)/(1+z)` and eliminating gives

```text
(A^2-BC)(z^2-1) P = N,
N=(B-1)[BC(z-1)-A^2(z+1)] + 2AB(C-1)z.               (7)
```

For an explicit way to verify this elimination, the common denominator
is `D=(A^2-BC)(z^2-1)`. The numerators of U,V are respectively
`(A^2-BC)(A−1)(z+1)` and `(A^2-BC)(A+1)(z−1)`.
The numerator of T is
`−(C−1)[A^2(z+1)+BC(z−1)]+2AC(B−1)`.
Those of Q,S are the numerators of P,T with A,z replaced by −A,−z.
Multiplication by the four rows of M verifies (7); `--prove` checks every
coefficient and the determinant in independent A,B,C,z.

At z=1 the left side of (7) has a double zero. But, after
`A=z^a,B=z^b,C=z^c`, direct differentiation gives `N'(1)=2(c−b)`.
This is nonzero because b>c. Contradiction. This completes all four cases.

## Apply the theorem to the assigned infinite family

For `a=13+760t,b=10+760t,c=2+760t`, the gcds are
`gcd(3,b)`, `gcd(11,c)`, and `gcd(8,c)`.
If `t=0 mod 3` and `t mod 11` is neither 1 nor 9, these are `[1,1,2]`;
a is odd and b,c are both 2 modulo 4. Now `a−b=3`, `a−c=11`.
The first possible divisibility, `6|c`, fails since c=2 modulo 3.
The second, `22|b`, is equivalent to `t=1 mod 11`, also excluded.
This includes all 32 previously missing classes modulo 165. In particular
`t=165n` always belongs to the missing classes and never satisfies either
divisibility, proving the promised infinite obstruction.

## Checks and boundary

The full-prefix consequence uses the exact shell polynomial

```text
Q=s0(1-A-B-C)+sum_i S_i(1-sum_(j!=i) A_j)-sum_i A_i S_i(z^-1).
```

For a full balanced colouring, `(1-z)` times twice the difference of
distance polynomials is `zQ`. Subdivide every coarse edge into g edges.
With `w=z^g`, write the signed arm polynomials as

```text
S_i(z)=S_i,old(w)+sum_(r=1)^(g-1) z^r X_i,r(w).
```

The residue-zero part of Q is precisely `Q_old(w)`. Its residue-r part is
`z^r [F_(X_r)(w)-W_(X_(g-r))(w)]`. Distinct residues cannot cancel. Thus
any full homometric colouring forces the old Q to vanish and **every**
mirrored edge pair to solve the equations proved impossible above.
For odd g>=3 there is at least one such pair. In particular g=7 excludes
all full partitions of the retained prefix. Its homometric number is at
most `87+7980t`, one below the original target, on the stated classes.
The original tree may still attain its target by omitting other vertices.

Seven focused standard-library tests and all 97 project tests pass. Besides the formal identities
and arithmetic refusal boundary, they independently expand both edge
equations, accept a positive control on `(25,22,14)`, and reject an altered
row. The control's seven-fold lift preserves a full coarse colouring and
omits the two original tips on `(175,155,99)`: independent breadth-first
original-tree distances agree for two disjoint size-214 sets. Exchanging
one positive and one negative vertex preserves their sizes and makes the
distance profiles unequal. This checks the intended metric and sign
orientation; it is not evidence for the negative theorem's infinite scope.
That scope follows from the argument above, which permits every paired
edge assignment. Different omissions and arbitrary original-tree pairs
remain outside it; varying the mirrored edge layers does not.
