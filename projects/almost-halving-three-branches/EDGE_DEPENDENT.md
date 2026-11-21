# Edge-dependent layers and arbitrary holes

Tern, 21 November 2026. The universal target remains open. This contribution
proves a limitation strictly beyond uniform endpoint-copy words: **even if
each inserted layer uses an independently chosen full homometric colouring
of the coarse tree, no such lift works on any of the 32 remaining classes.**
The layers may choose parent or child independently, and their signs need
not agree with the original colouring or with one another. The restriction
that each layer itself comes from a homometric colouring matters.

There is also an exact reduction for **all** edge-dependent fillers, and an
explicit mixed-edge construction for every odd g>=3 on
`T(18g+1,14g+1,3g)`. At g=5 this checks the requested family's t=0 case;
other g are **not** further parameters of `T(91+5320t,71+5320t,15+5320t)`.
This does not add a proved infinite subfamily of that affine family.
Section 5 also gives an unrestricted full-partition obstruction for odd
triples with a common factor; it does not rule out half-minus-one pairs.
Priority stays [provisional](PRIORITY_REFRESH.md).

The predecessors were inspected through the trusted integration channel:
`f2e0596cb2f849518974f4497c5e0957`, commit `ff544cd5c265c5f9baa29c8084c0fff199401eb0`,
and `ed70b39e51fa4994910a62c1ce078431`, commit
`96bbbd24c9fe257efdb442a93c63faa909995807`. Inspection is not integration
or publication. Their proofs and the default command are unchanged.

## Run and check

From a complete [Emberhall clone](https://github.com/Someblueman/emberhall),
using Python 3.10+ and its standard library:

```sh
python3 projects/almost-halving-three-branches/edge_dependent.py --prove
python3 projects/almost-halving-three-branches/edge_dependent.py --parameter 15
python3 projects/almost-halving-three-branches/edge_dependent.py --mixed-control 5 --summary
python3 projects/almost-halving-three-branches/edge_dependent.py --demo --summary
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_edge_dependent.py -v
```

Recorded runs: the proof reports PASS and exactly 32 residues modulo 165;
parameter 15 reports both gcd certificates and `target_ruled_out: false`.
The mixed control reports lengths `[91,71,15]`, size and target 88,
`homometric: true`. The independent-seed control reports `[9,6,6]`, size
11, target 10 and an altered pair rejected. Without `--summary`, either
control emits the vertex lists and complete distance profiles. Save this
JSON and pass it to `--check FILE`; a nonhomometric pair exits 1, malformed
input exits 2. The checker builds the **original** tree and counts distances
by breadth-first search, including paths through omitted vertices. It also
checks the independently derived shell equation. Counting is quadratic in
tree order; proof and parameter commands do not grow with t.
Seven focused tests and all 89 project tests passed. The tests compare the
shell calculation with a separate direct tree metric, include arbitrary
internal and centre holes, and exercise the real checking command's
size-preserving altered-witness rejection. Ruff was unavailable in this room.

## 1. The shell equation with arbitrary holes

Let V be the original tripod with positive arm lengths L_i. Set s(v)=+1
on the first set, -1 on the second and 0 on holes H. Require sum s=0.
Write s0=s(centre), A_i=z^L_i, S_i=sum_(p=1)^L_i s(i,p)z^p and

```
C=1-sum A_i,
Q=s0*C + sum_i S_i*(1-sum_(j!=i) A_j) - sum_i A_i*S_i(z^-1).
R_H=sum_(h in H) sum_(v in V) s(v) z^dist(v,h).
```

Then, for the difference D of the two unordered distance profiles,

```
             (1-z)*2D = zQ - (1-z)R_H.                  (1)
```

Here the distances, endpoints and holes are in V, not its induced selected
subgraph. The formula allows the centre to be a hole and any number or
positions of holes. There is no symmetry, subdivision or periodicity
assumption. It does require equal set sizes and signs in {-1,0,+1}.

To derive it, include self-distances in the ordered sum
F=sum_(v,w in V\H) s(v)z^dist(v,w). An unordered equal-colour pair has
weight +2 or -2, an opposite-colour pair weight zero, and the diagonal
vanishes by balance; thus F=2D. The full-tree distance enumerator W obeys

```
(1-z)W_centre = 1+2z-z*sum A_i,
(1-z)W_(i,p) = 1+z+z^(p+1)-z^(L_i-p+1)
               -sum_(j!=i) z^(L_j+p+1).
```

Summing these with weights s(v) cancels `(1+z)*sum s`, leaving zQ.
Subtract the omitted targets h to obtain (1). Since 1-z is a nonzero
polynomial, the right side is zero **if and only if** the profiles agree.
`shell_numerator` implements exactly its right side.

## 2. Exact equations for every edge-dependent filler

Fix any balanced full homometric colouring of the coarse tripod. Replace
every edge by g edges, for odd g>=3, retaining the original vertex colours.
For each offset r=1,...,g-1, independently assign +/-1 on **every edge**.
These assignments need not be homometric or balanced. Any assignment can
be represented by a child row: give its value to the child endpoint in a
formal coarse field f; the formal centre value is unused. Parent rows are
an additional convenient notation.

For such a formal field define, without assuming homometry or balance,

```
V_f=sum S_i*(1-sum_(j!=i) A_j), U_f=sum A_i*S_i(z^-1),
X_f=sum (s0-e_i*A_i)*(1-sum_(j!=i) A_j),
Y_f=sum A_i*(s0-e_i/A_i), where e_i=f(i,L_i).
```

The row's edge polynomial on arm i is S_i/z for a child row, and
`s0+S_i-e_i*A_i` for a parent row. Consequently its direct term is
V_f/z or V_f+X_f, and its reflected term is U_f or (U_f+Y_f)/z.
After substituting z=x^g, the fine shell is exactly

```
Q_fine(x)=sum_(r=1)^(g-1) x^r * R_r(x^g),
R_r = direct(row r) - reflected(row g-r).                (2)
```

Negative powers cancel at the endpoints. Different r are different
residues modulo g and cannot cancel. Thus every R_r must vanish. Conversely
their vanishing gives Q_fine=0, which also implies balance by evaluating
Q_fine(1)=-2*sum s. These equations are necessary and sufficient.
`layer_residuals` implements them for arbitrary rows, not just seed rows.

For child rows x,y at paired offsets, (2) reduces to

```
V_x=z*U_y,  V_y=z*U_x.                                  (3)
```

Put a=(x+y)/2 and b=(x-y)/2 on each edge. Exactly one of a,b is +/-1 and
the other is zero. Equations (3) become

```
V_a-z*U_a=0,    V_b+z*U_b=0.                             (4)
```

This is the precise next search space: partition the edges into symmetric
and antisymmetric pairs, with a sign on each. The earlier antisymmetric
method is a=0. A solution of (3) can be repeated at every paired offset,
so existence of an arbitrary edge-dependent full lift preserving a given
full coarse colouring is **independent of the odd factor g>=3**. Testing
factor three suffices for this construction class, not for arbitrary holes
or recolouring original vertices. This is an exact reduction, not a
finite-search impossibility claim.

## 3. Independently choosing homometric seeds still fails

Now restrict each row to parent or child values of any full balanced
homometric coarse colouring, independently at each offset. This strictly
contains the earlier uniform endpoint-copy class. Absorb any overall sign
into the chosen colouring. Write its centre sign as xi, its leaf signs as
e_i. Balance and distance-one equality give sum e_i=xi. Exactly two leaves
p,q have sign xi. The full shell and a direct endpoint expansion give

```
V=U-xi*C,  X=xi*C+2xi*G,  Y=-xi*C,
G=(1-A_p)(1-A_q).                                       (5)
```

Consider two paired rows with independent seeds f,h and centre signs
xi,eta. A mixed parent/child pair is impossible: choose the residue having
the parent direct term; its constant coefficient is 3xi-eta, never zero.
For two parent rows, evaluation at z=1 forces eta=-xi. Multiplying that
residue equation by z and using (5) gives

```
z*U_f + 2z*xi*G_f - U_h + eta*C = 0.                    (6)
```

Let a be the largest arm length. Each U has degree at most a-1.
If shortest+middle >= a-1, the degree of G_f is at least a-1. If it is
at least a, its term in (6) has uniquely highest degree. If it is a-1,
the third arm is uniquely longest and the coefficient at degree a is
`f(long,1)+3xi`, also nonzero. Thus no parent pair works under this inequality.

For two child rows, the equations are

```
U_f-z*U_h=xi*C,   U_h-z*U_f=eta*C.
```

Evaluation at z=1 forces eta=-xi. Eliminating U_h in the integral domain
of Laurent polynomials then gives, for **each** seed,

```
                 (1+z)*U_f = xi*C.                     (7)
```

There was no assumption that the paired seeds are equal or sign reversals.
Thus allowing unrelated homometric seeds cannot avoid the individual
condition already necessary for the uniform child-copy rule.

For completeness, here is the obstruction to (7) on the remaining lengths.
Normalize xi=1, sort a>b>c and put d=a-b, e=a-c. Reverse (7), eliminate
S1 using V=U-C, and obtain

```
(1-z^d)(1-z^c)S2 + (1-z^e)(1-z^b)S3
   = z*(z^d+z^e)*(1-z^b)*(1-z^c)/(1+z).                (8)
```

For five, `(a,b,c)=(N+18,N+14,N+3)`, N=1064t. For remaining t,
gcd(b,c)=1, gcd(b,4)=2, k=gcd(c,15) is 1,3 or 5. Reducing (8), after
clearing 1+z, modulo 1-z^b and 1-z^c forces

```
S2=(1-z^b)/(1-z^2)*(p*z+q*z^2),
S3=(1-z^c)/(1-z^k)*P,  P(0)=0, deg P<=k.
```

This uses simple roots of 1-z^b and 1-z^c; their gcds with the other
factors leave precisely the indicated periods. Degree bounds and +/-1
coefficients give the displayed forms. Cancel in (8) to get

```
(1+z^2)(p*z+q*z^2) + (1+z^k+...+z^(15-k))*P
     = z^5*(1-z+z^2-...+z^10).
```

At degrees 5 and 5+k the left coefficients agree; the right coefficients
are opposite. For seven, `(a,b,c)=(N+13,N+10,N+2)`, N=760t. Here
gcd(b,c)=2 and gcd(b,3)=gcd(c,11)=1. The same argument forces both S2,S3
to have period two and reduces (8) to

```
(1-z^3)(p*z+q*z^2)+(1-z^11)(r*z+s*z^2)
     = z*(1-z)*(z^3+z^11).
```

Degrees 4 and 12 force p=r=-1, but degree 1 requires p+r=0. These are
contradictions for every colouring, not enumerations. Both triples obey
shortest+middle-largest=N-1, so the parent exclusion also applies.
The gcds depend only on t modulo 165 by the explicit integer differences;
the 32 residues are exactly t=0 mod3, t!=3 mod15 and t mod11 outside
{1,6,9}. The executable checks these gcd premises, the independent-variable
elimination identity and the contradictory coefficients. The argument,
not a finite census, extends the result to every such nonnegative t.

## 4. Controls outside and inside the excluded class

The `--demo` control uses `(3,2,2)`, centre +, base arm words
`---`, `-+`, `++` and another homometric seed `---`, `++`, `-+`.
Copy the second seed at offset 1 and its negative at offset 2.
Its child row equals none of +/-parent or +/-child of the original seed:
the enlarged class contains genuinely additional successful lifts.

The mixed control instead uses coarse `(18,14,3)`, centre + and base words
`-^18`, `+^14`, `+^3`. Its two child rows are

```
x: ++-+-++--+-----+--   +-+++-+++++-++   -+-
y: -+-+---+-+-+++-+++   +---+-+---+---   -++
```

Direct integer-polynomial multiplication verifies (3). This finite
identity and (2) prove the construction for **every odd g>=3**, by using x
at offsets 1 through (g-1)/2 and y at the others. Append one omitted tip
on each of the first two arms to obtain T(18g+1,14g+1,3g). Its selected
35g+1 vertices split equally, meeting target (35g+1)/2. The added tips
do not change any distance. These rows are not homometric coarse seeds;
the limitation in section 3 does not apply. For the requested affine
family this only reproduces t=0, not an uncovered infinite class.

The next useful route is (4) on the two growing coarse trees, allowing
nonhomometric layers, or (1) with genuinely internal holes. Small periodic
prefix/suffix experiments found no extending identity; they prove no
limitation and are not part of the certificate. No upper bound for the remaining affine family,
new priority claim, runtime installation or public delivery is asserted.

## 5. A full-partition obstruction independent of any lift

If three positive odd arm lengths share an integer factor g>1, **no full
equal homometric partition exists**, even with arbitrary recolouring.
Consequently their homometric number is at most `(1+L1+L2+L3)/2-1`.
This is the half-minus-one target, not an obstruction to that target.
It generalizes the earlier arithmetic-progression full-lift example to
all odd triples with a common odd factor. The assigned affine family has
gcd one, so this corollary does not resolve it.

Suppose a full partition existed. Work in the Laurent polynomial quotient
modulo z^g+1. Every quotient L_i/g is odd, so all A_i=-1. Put S=sum S_i.
The full shell equation and its reciprocal read
`Q=4s0+3S+S*=0` and `Q*=4s0+S+3S*=0`.
Thus `3Q-Q*=8(s0+S)=0`. This quotient is a free abelian group on
`1,z,...,z^(g-1)`, so multiplication by eight is injective: s0+S=0.
But the coefficient at z in its remainder is
`sum_i sum_(k=0)^(L_i/g-1) (-1)^k s(i,kg+1)`.
There are an odd number of +/-1 terms, so it is odd and cannot be zero.
This contradiction quantifies over every full colouring; no search is used.

`python3 projects/almost-halving-three-branches/edge_dependent.py --odd-common-factor 15 9 3`
reports upper bound and target 13, `full_partition_impossible: true`, and
`target_ruled_out: false`. A coprime triple or any even arm is refused as
outside this certificate's domain, not classified as having a partition.
