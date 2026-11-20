# Reconstructing the published tripod cases

Mica, 20 November 2026. Published-case admission and a separate signed-shell
result. **The general half-minus-one target remains unproved.** The formulas
below are proved for arbitrary lengths within their stated domains.

## Sources and priority

The principal source is Axenovich–Özkahya,
[On homometric sets in graphs](https://ajc.maths.uq.edu.au/pdf/55/ajc_v55_p175.pdf),
Australasian Journal of Combinatorics 55 (2013), 175–187: Construction 13
(p. 179), Constructions 15–16 (pp. 181–182), and Theorem 8 (p. 177).
The [December 2012 author manuscript](https://web.cs.hacettepe.edu.tr/~ozkahya/pub/homsets.pdf)
has the same extracted block endpoint. The older
[arXiv version](https://arxiv.org/html/1203.1158) numbers these constructions
9, 11, 12 and labels the block arm differently. Do not mix those labels.
The journal states a roughly five-twelfths bound for three legs and special
half-size cases, with a general warning that floors/ceilings are sometimes omitted.

Priority refresh on 20 November 2026:

* Fulek–Mitrović, [Homometric sets in trees](https://arxiv.org/html/1302.1386v2),
  Sections 2–4, improves general-tree and haircomb lower bounds. Its limitation
  concerns a restricted construction, not all homometric pairs.
* Anu–Lakshmanan, [Homometric Number of a Graph and Some Related Concepts](https://doi.org/10.1007/978-3-319-64419-6_4),
  checked in the [author-uploaded text](https://www.researchgate.net/publication/319138539_Homometric_Number_of_a_Graph_and_Some_Related_Concepts),
  treats products, powers, regular graphs and related parameters.
* Lakshmanan–Menon–Anu, [Homometric Number of Graphs](https://ijritcc.org/index.php/ijritcc/article/download/1148/1148),
  concerns graph operations and weak homometry; weak distance **sets** do not
  establish equality of multiplicities.
* The relevant [Oberwolfach report](https://publications.mfo.de/bitstream/handle/mfo/3349/OWR_2013_18.pdf?isAllowed=y&sequence=1),
  printed p. 1119, poses a general-graph asymptotic problem, not this tripod bound.
* Alon, [Problems and results in Extremal Combinatorics III](https://web.math.princeton.edu/~nalon/PDFS/extremalIII4.pdf),
  Section 2 (2016), improves the general-graph lower bound, not this target.
* The [institutional abstract of Mohankumar–Abhishek (2021)](https://www.amrita.edu/publication/detour-homometric-number-of-a-graph/)
  studies detour homometry on graphs with cycles. Its full text was not
  retrievable; the abstract alone is not a complete priority check.

None of these opened results resolves the proposed target. Searches for
“homometric sets” with trees, spiders, three legs and later dates found no
resolution. This is **provisional priority**, not proof of novelty. A later
successful retrieval of the
[twins survey](https://wwwalt.math.kit.edu/iag6/~axenovich/media/twins-survey1.pdf)
resolved that source gap: its Section 6, Theorems 6.4–6.5, repeats the
three-legged bound and later general-tree/haircomb bounds, not this target.
Anu's thesis, *A study on two graph parameters: double Roman domination
number and homometric number*, is now located in the
[university reader](https://mgutheses.in/page/authors_view.php?q=T+3952&word=):
chapter 6 is named “Homometric number”, but its links returned the same
contents page, not readable chapter text. The
[Shodhganga record](https://shodhganga.inflibnet.ac.in/handle/10603/370098)
was inaccessible. That chapter remains unchecked. No theorem may be
advertised as new until those gaps are addressed. Publication dates above are
from the papers, not the search engine's crawl dates.

## Conventions

Let the centre be `o=(0,0)`. On arm `i`, write `i:d` for its vertex at distance
`d`, with `1 <= d <= l_i`. The centre is not part of an arm's length. The order
is `n=1+l_1+l_2+l_3`; the project asks for size `floor(n/2)-1`.
For distinct vertices, distance is `|d-e|` on one arm, `d+e` on different arms,
and `d` from the centre. Every profile counts unordered distinct pairs once.
All intervals below include both endpoints; an interval with upper endpoint
below its lower endpoint is empty.

## Path construction, including both parities

Order the lengths `a >= b >= c`. Form the isometric path

`1:a, 1:(a-1), ..., 1:1, o, 2:1, ..., 2:b`.

It has `m=a+b+1` vertices. With `k=floor(m/2)`, take its first `k` vertices
as A and next `k` as B. If `m=2k`, nothing on this path is omitted; if
`m=2k+1`, its final vertex is omitted. Both sets are consecutive paths of
`k` vertices and are disjoint. For each distance `d=1,...,k-1`, both profiles
have multiplicity `k-d`; all other coefficients vanish. This proves equality
of the full profiles, not just equality of their supports.

The unused count in the whole tree is `c + (m mod 2)`.

### An additional pair of separated paths

There is also an immediate construction not requiring both sets to lie in
one diameter path. Put `q=min(a,b+c+1)`. Take the first q vertices of arm 1,
and the first q vertices of the path from the tip of arm 2 through the centre
to the tip of arm 3. They are disjoint isometric q-vertex paths. Both profiles
therefore have coefficient `q-d` for `1<=d<q`.
Since `n=a+(b+c+1)`, their unused count is `|a-(b+c+1)|`. This construction
meets the project target exactly when that absolute difference is at most 3.
It is labelled `separated-path` in the checker, distinct from the printed
diameter-halves construction. No novelty is claimed for this observation.

## Alternating construction, including a one-vertex third arm

Relabel arms temporarily so `a >= b`, with third length `c`; do not require
`b >= c`. Put `k=floor(c/2)` and take

`A = {o} union {1:d : 1<=d<=b-1} union {3:2j : 1<=j<=k}`,

`B = {2:d : 1<=d<=b} union {3:(2j-1) : 1<=j<=k}`.

Both sizes are `b+k`. The sets are disjoint by arm and parity. When `c=2k`,
all vertices on arm 3 are used. When `c=2k+1`, its last vertex is omitted.
For `c=1`, both third-arm parts are empty; for `b=1`, the first-arm part of
A is empty. These are included cases, not exceptional repairs.

Here is an explicit distance-preserving bijection. Send `o` to `2:1`,
`1:d` to `2:(d+1)`, and `3:2j` to `3:(2j-1)`. Within the first two parts
distances are consecutive differences, within the alternating parts they are
`2|j-j'|`. A cross distance in A is `d+2j`, allowing `d=0` for the centre;
the corresponding B distance is `(d+1)+(2j-1)=d+2j`. Thus each unordered
pair has a counterpart of the same distance. This stronger fact is sufficient
here; it must not be imposed on unknown solutions to the project target.

The unused count is `1+a-b+(c mod 2)`. With all arm permutations, the largest
alternating size for sorted lengths is
`max(b+floor(c/2), c+floor(a/2))`.

For equal lengths `t`, this gives the target for every parity: size `3t/2`
when `t` is even, and `(3t-1)/2` when `t` is odd. In the latter case this
argument does not justify the journal's unrounded half-size wording.

## Block construction: admissible domain and quarantined endpoint

Use journal labels `a >= b > c`, and define `x=b-c > 0`,
`a+1=q*x+r`, `0<=r<x`. The extracted printed prescription makes its last
block index `h=q-1` for odd `q`, and `h=q` for even `q`, and uses blocks
`P_i={1:d : ix<=d<=(i+1)x-1}`, interpreting depth zero as `o`.
It assigns the even blocks and all of arm 3 to A, and the odd blocks and
all of arm 2 to B.

**Odd q:** the final endpoint is `q*x-1=a-r`, which exists. With `q=2s+1`,
A has `(s+1)x+c` vertices and B has `sx+b=(s+1)x+c`. They are disjoint and
omit exactly the final `r` vertices of arm 1. Hence size is `(n-r)/2`.
This includes `s=0` whenever the length inequalities permit it.

**Even q:** the prescribed endpoint is `(q+1)x-1=a+(x-r)>a`.
The final block needs `x-r` nonexistent vertices, for every permitted
remainder. Example: `(a,b,c)=(15,7,3)` gives `x=4,q=4,r=0` and demands
depths 16 through 19. The checker rejects this case. It does not shorten,
shift or drop a block and attribute the changed formula to the authors.

Publisher and author-PDF text extraction agree. The browser's PDF screenshot
requests returned cache-miss errors, so a visual check of the typeset formula
was unavailable. The precise ambiguity remains: extraction error or a printed
endpoint error. No correction or intended replacement is asserted here.

### Independent coefficient proof for every admissible odd-q block case

Use a formal variable `z`; coefficients count distances. Write
`F=1+z+...+z^(x-1)`, `C=z+...+z^c`, and

`E=F*(1+z^(2x)+...+z^(2sx))`,
`O=F*(z^x+z^(3x)+...+z^((2s-1)x))` (zero when `s=0`).

These are the depth enumerators of the even and odd block unions. The
secondary arm enumerators are `C` for A and `C+z^(c+1)*F` for B.
The identity `E-z^x*O=F` gives the cross-part profile difference

`E*C - O*(C+z^(c+1)*F) = F*C - z*F*O`,

using `(z^x-1)*C=z^(c+1)*F-z*F`.

Let `H_j=sum_(d=1)^(j-1) (j-d)*z^d` be the profile of a consecutive
`j`-vertex interval. The long-arm profile difference is

`H_x + sum_(k=1)^s z^(2kx)*F(z)*F(z^-1) = H_x + z*F*O`.

To see the first equality, delete the last even block: the remainder is a
translate of O, so only the internal pairs of the deleted block and its pairs
with the other even blocks remain. Since different blocks are ordered, all
these exponents are positive. The second equality uses
`F(z^-1)=z^(-(x-1))*F(z)`.

The secondary-arm difference is `H_c-H_(c+x)`. Splitting a consecutive
`c+x`-vertex interval into parts of sizes `x` and `c` proves

`H_(c+x)=H_x+H_c+F*C`.

Adding the three displayed profile differences yields zero coefficient by
coefficient. This exhausts internal and cross-part pairs, including all
centre pairs through depth zero in E. It proves the valid block family
without extending the formula beyond its domain.

## Exact boundary of what these constructions settle

For sorted lengths, put `p=floor((a+b+1)/2)`,
`u=max(b+floor(c/2), c+floor(a/2))`. If `b>c` and
`q=floor((a+1)/(b-c))` is odd, also put `v=(n-r)/2` with the remainder above.
Otherwise v is unavailable, not zero evidence for an upper bound.
The largest size of these published implementations is exactly
`K=max(p,u,v when available)`.
The cases unsettled **by these published formulas** are exactly those with
`K<floor(n/2)-1`. This arithmetic criterion is not a classification of h(T).

There are infinitely many such gaps: for integer `t>=4`, take
`(a,b,c)=(4t-1,2t,t)`. The path gives `3t`, the two alternating candidates
give at most `3t`, and the printed block quotient is 4, so it is inadmissible.
But the target is `floor(7t/2)-1>3t`. This proves insufficiency of the
reconstructed constructions, **not an obstruction to arbitrary homometric
sets**. It is a useful first family for the next mathematical step.

For that step, a complete exact equation is available. If `f_i(z)` lists
selected depths on arm i, and `e` is 0 or 1 for centre membership, its profile
is

`D(z)=sum_i positive_part(f_i(z)*f_i(z^-1))
      +sum_(i<j) f_i(z)*f_j(z) + e*sum_i f_i(z)`.

Here positive_part keeps strictly positive exponents, once each; diagonal
terms at exponent zero are excluded. Two sets must have identical D,
disjoint supports, disjoint centre membership and equal cardinality. This
is a formulation, not a solver or existence proof. Searching only for
distance-preserving bijections would impose an unjustified extra restriction.

## Signed shells, with an exact omitted-vertex correction

Give every vertex a sign `s(v)` in `{-1,0,1}`: plus for A, minus for B,
zero for an omitted vertex. Write `R={v:s(v)!=0}` and
`N_d^R(v)=|{w in R:dist(v,w)=d}|`, for `d>=1`. Then

`sum_v s(v)*N_d^R(v) = 2*(D_A(d)-D_B(d))`.                 (1)

Proof: collect each unordered retained pair's two contributions. Equal plus
signs contribute 2, equal minus signs -2, opposite signs zero. Thus disjoint,
equally sized sets of the target size exist **if and only if** there is such
a sign assignment with `sum_v s(v)=0`, at most `2+(n mod 2)` zeros, and
every left side of (1) zero. This equivalence covers all pairs, not only
isometric pairs or a search class. It does not assert such a sign assignment
always exists.

For a fixed omitted set H, the equations are linear in the remaining signs:

`N_d^R(v)=N_d^V(v)-sum_(w in H) [dist(v,w)=d]`.              (2)

Counting full-tree shells without this correction gives the wrong equations.
The coefficients count paths in the original tree; deleting a vertex from
R does not delete it from the paths defining the metric.

## Maximum homometric pairs for the uncovered family

**Proposition (priority provisional).** For every integer `t>=2`, the tripod
with lengths `(4t-1,2t,t)` has disjoint homometric sets of size `floor(7t/2)`.
This is maximum by disjointness, so `h(T)=floor(7t/2)` for this family.
It settles the entire gap family identified above, not arbitrary triples.
This is a separate formula, not a proposed repair of Construction 16.

First let `t=2h`, where `h>=1`. All `14h` vertices will be used.

Here and below `[p,q]` denotes all integer depths between its endpoints,
and is empty when `p>q`. Assign the centre minus. On arm 1, assign minus on

`[h+1,2h-1], [2h+1,3h-1], [5h,6h-2], [6h,7h-2]`,

and plus everywhere else. On arm 2 assign plus on `[1,h-1]` and
`[2h+1,3h-1]`, minus elsewhere. On arm 3 assign plus on `[h+1,2h-1]`,
minus elsewhere. Let A be all plus vertices and B all minus vertices.
All endpoints lie in their arms, including `h=1` where the four negative
intervals on arm 1 and all positive intervals on arms 2 and 3 are empty.

The plus counts on the three arms are `4h+3`, `2h-2`, `h-1`, summing to
`7h`; the rest, including the centre, are the other `7h` vertices.
It remains to prove every distance coefficient equal.

### A polynomial form of the full-shell equations

For a fully retained tripod of lengths `a_1,a_2,a_3`, put
`S_i(z)=sum_(p=1)^a_i s(i:p)*z^p` and let `s_0` be the centre sign.
Assume the signs sum to zero. Equation (1) for all distances is equivalent to

`Q(z)=s_0*(1-sum_i z^a_i)
      +sum_i S_i(z)*(1-sum_(j!=i) z^a_j)
      -sum_i z^a_i*S_i(z^-1) = 0`.                       (3)

For completeness, the full distance enumerator from `i:p` is
`U_p + U_(a_i-p) + sum_(j!=i) z^p*U_(a_j)`, where
`U_k=z+...+z^k`. Multiplying by `1-z` gives
`2z+z^(p+1)-z^(a_i-p+1)-sum_(j!=i)z^(p+a_j+1)`.
For the centre it gives `3z-sum_i z^(a_i+1)`.
Sum with signs and use their zero total. The result is `z*Q(z)`.
By (1), this is `2*(1-z)*(D_A(z)-D_B(z))`; hence (3) is an equivalence
over integer Laurent polynomials, not merely a necessary test.

### Verifiable identity for the stated intervals

Write `r=z^h`, `T_i=(1-z)*S_i`. Summing the signed intervals gives

`T_1 = z-r^8 - 2r*(1+r)*(1+r^4/z)*(z-r)`,

`T_2 = z-z*r^4 - 2r*(1+r^2)*(1-z*r)`,

`T_3 = -z+z*r^2+2z*r-2r^2`.

For example, on arm 1 start with all plus, then subtract twice its four
minus intervals: `S_1=U_(8h-1)-2*z^h*(1+z^h)*(1+z^(4h-1))*U_(h-1)`.
The other formulas follow from the two positive interval lists in the same
way. Define `T_i^*=T_i(z^-1,r^-1)`. Substitution in `(1-z)*Q` gives

```
-(1-z)*(1-r^8/z-r^4-r^2)
+ T_1*(1-r^4-r^2) + T_2*(1-r^8/z-r^2) + T_3*(1-r^8/z-r^4)
+ r^8*T_1^* + z*r^4*T_2^* + z*r^2*T_3^* = 0.             (4)
```

This is an identity in the **independent** Laurent variables z and r:
expanding the three factored expressions cancels every monomial. The exact
coefficient test in `test_gap_family_formal_identity` performs that expansion
with integer coefficients and checks an empty residual dictionary. This is
not testing a list of numerical h. Substituting `r=z^h` in (4) proves (3)
for every positive h, and (1) proves the even-t case.

### Odd t

Let `t=2h+1`, `h>=1`. Omit just the last vertex of the longest arm.
The remaining tree has lengths `(8h+2,4h+2,2h+1)` and the same distances
between retained vertices. Give its centre a minus sign. The negative
intervals on arm 1 are now

`[h+2,2h], [2h+2,3h], [5h+2,6h], [6h+2,7h]`.

Assign plus elsewhere on arm 1, plus on `[1,h-1]` and `[2h+2,3h]` on arm 2,
and plus on `[h+2,2h]` on arm 3; all remaining vertices get minus signs.
The counts of plus vertices are `4h+6`, `2h-2`, `h-1`, summing to `7h+3`.
The retained order is `14h+6`, so the minus count agrees. Empty intervals
at `h=1` need no exception.

In the notation of (3), put `A=(1-z)S_1`, `B=(1-z)S_2`, `C=(1-z)S_3`.
The signed interval lists give

`A = z-z^3*r^8 - 2*z*r*(1+r)*(1+r^4)*(z-r)`,

`B = -z+z^3*r^4 + 2*(1+z*r^2)*(z-r)`,

`C = -z+z^2*r^2 + 2*z*r*(z-r)`.

Here `r=z^h` as before. With stars again inverting both variables, the
independent-variable identity is

```
-(1-z)*(1-z^2*r^8-z^2*r^4-z*r^2)
+ A*(1-z^2*r^4-z*r^2) + B*(1-z^2*r^8-z*r^2) + C*(1-z^2*r^8-z^2*r^4)
+ z^3*r^8*A^* + z^3*r^4*B^* + z^2*r^2*C^* = 0.           (5)
```

The same exact Laurent-coefficient test checks (5). It is `(1-z)Q` for
the retained tree. Therefore both sets are homometric there and in the
original tree. Their size is `7h+3=floor(7t/2)`, proving the odd-t case.

As a necessary condition that may help extend this result: in a full
partition of sorted lengths `a>=b>c`, the last `b-c` vertices of arms 1
and 2 must have opposite signs at equal distances from their respective
tips. For distance `a+b-k`, `0<=k<b-c`, only those two arms can contribute.
Equation (1) reads `sum_(i=0)^k (s(1:a-i)+s(2:b-i))=0`. Subtract successive
equations (or use k=0 first) to obtain the claim. For omitted vertices one
must use (2); this full-partition condition alone cannot refute the target.

### What remains

The proposition covers this whole gap family but not arbitrary triples.
It supplies no upper bound for any negative family.
Its priority still needs the thesis check and an independent mathematical
review. A next builder can use (1)–(2) on other uncovered triples with at most
two or three omissions, or search for a broader symbolic pattern; a failed search proves
neither nonexistence nor a universal upper bound.

## A full-partition obstruction and a sharp case

The root-of-unity calculation below is an upper bound over **every** full
partition, not over a class of searched constructions. Suppose there is an
even integer `m>=2` and positive integers `k_1,k_2,k_3` of odd total K such
that the arm lengths are `a_i=k_i*m-1`. Then `n=K*m-2` is even and

`h(T) <= n/2-1`.                                          (6)

To prove this, assume a full homometric partition and use its signs in (3).
Let z be any nontrivial m-th root of unity, let `S=S_1+S_2+S_3`, and note
`z^a_i=z^-1`. Multiplication of (3) by z yields

`(z-3)*s_0 + (z-2)*S(z) - S(z^-1) = 0`.

Use this equation at both z and z^-1 to eliminate `S(z^-1)`. The result is

`2*(2-z-z^-1)*(S(z)+s_0)=0`.

The first factor is nonzero: on the unit circle `z+z^-1=2` only for z=1.
Hence the total sign polynomial `F=s_0+S` vanishes at every nontrivial m-th
root, and balance gives `F(1)=0` too. Divide F by `z^m-1`. The remainder
has degree less than m and vanishes at m distinct roots, so is zero.
Each remainder coefficient is therefore the sum of signs on one depth
residue modulo m. But each nonzero residue contains K vertices, while
residue zero contains `K-2` (including the centre). Both counts are odd.
An odd number of signs in `{-1,1}` cannot sum to zero, a contradiction.
This excludes all full partitions and proves (6).

For the program, it suffices to take `m=gcd(a_1+1,a_2+1,a_3+1)`: an even
divisor with odd quotient sum exists exactly when this greatest divisor is
even and its quotient sum is odd. A smaller divisor multiplies that sum by
an integer, so cannot make an even sum odd. If the criterion fails, the
program reports only the ordinary disjointness upper bound; it makes no
claim that this bound is attained.

For equal odd arms `l`, take `m=l+1` and all `k_i=1`. The alternating
construction supplies `(3l-1)/2` vertices in each set, matching (6), so

`h(T(l,l,l)) = (3l-1)/2 = floor(n/2)-1` for every odd l.

For even l, the same construction reaches `3l/2=floor(n/2)`, the
disjointness upper bound. These exact parity statements are stronger than
silently assigning a rounding convention to the source's displayed `n/2`.
This obstruction concerns full partitions only. Omitted vertices change
(3) through (2); it cannot rule out pairs meeting the project's target.
In particular it does not turn the earlier construction-gap family into
a counterexample.

## An unequal-arm family attaining half-minus-one exactly

**Proposition (priority provisional).** For every positive even integer t,
the tree with lengths `(4t-1,3t-1,2t-1)` has
`h(T)=9t/2-2=floor(n/2)-1`. Thus the proposed target cannot be raised even
if equal-arm trees are excluded. The upper bound is (6), with `m=t` and
`(k_1,k_2,k_3)=(4,3,2)`. Here is a matching construction.

Omit depths `t-1` and `4t-1` of arm 1 and assign the centre minus.
On arm 1, alternate plus at odd depths and minus at even depths on
`[1,t-2]` and `[3t+1,4t-2]`; assign minus throughout `[t,3t]`.
On arm 2, alternate plus at odd depths and minus at even depths, except
make depths t and 2t plus. On arm 3, use plus everywhere except depth t.
All signs and omissions are disjoint and within range, including t=2.
The plus counts are `t-2`, `3t/2+2`, `2t-2`, totaling `9t/2-2`.
The retained order is `9t-4`, so the minus count agrees.

For a coefficient proof put `E=z(1-z^(t-2))/(1+z)`, the alternating
polynomial of `[1,t-2]`, and `U_j=z+...+z^j`. With the S_i of (3),

```
R = z^(3t)*E - z^(t-1)*U_(2t+1),   S_1=E+R,
S_2=(z+z^(3t))/(1+z)+2z^t+2z^(2t),
S_3=U_(2t-1)-2z^t.
```

These are finite polynomials because t is even. Set `p=t-1`, `a=4t-1`.
The signed distance polynomials from the two omitted vertices to retained
vertices are exactly

```
C_p=-z^p+z^p*E(z^-1)+z^-p*R+z^p*(S_2+S_3),
C_a=-z^a+z^a*S_1(z^-1)+z^a*(S_2+S_3).
```

The four terms respectively count the centre, the part of arm 1 on the
near side, its far side, and the other two arms (the tip has only one side).
Equation (2) says the required identity is `z*Q=(1-z)*(C_p+C_a)`.

For an explicitly finite verification, put `r=z^t`, `D=1-z^2` and clear
the common denominator D. The numerators of E, R, S_2, S_3 become

```
E_D=(1-z)*(z-r/z),
R_D=r^3*E_D-r*(1+z)*(1-z*r^2),
P_2=(1-z)*(z+r^3)+2*(r+r^2)*D,
P_3=(1+z)*(z-r^2)-2*r*D;   P_1=E_D+R_D.
```

Substitute these in the preceding identity using `z^p=r/z`, `z^a=r^4/z`
and `D*S_i(z^-1)=-z^2*P_i(z^-1,r^-1)`. Expansion has zero residual in
independent Laurent variables z and r; the exact integer coefficient test
checks this identity as well as (4)–(5). Substituting `r=z^t` and applying
(1)–(2) proves equality of all distance multiplicities for every even t.
This is a proof for this infinite family, not a conclusion from its examples.
Odd t and arbitrary triples are not covered by this proposition.

## Present coverage, and the remaining question

Removing only the last vertices of arms leaves a connected prefix subtree
isometric in the original tree: every unique path between retained vertices
stays in that subtree. Consequently any proved witness there lifts unchanged
to the original tree, with the same size and distance multiplicities.
The default checks all 20 nonnegative tip-deletion triples whose sum is at
most three, keeping only positive resulting arm lengths. Three is sufficient
for this closure operation when seeking the target, since a target pair
omits at most three original vertices in total. This does not say that a
target pair must arise from these constructions or from prefix subtrees.

For each such subtree, the checker takes the maximum of the published
sizes p, u, v above, the separated-path size `min(a,b+c+1)`, and the size
from either proved family when its exact length conditions hold. It then
takes the maximum over the 20 subtrees, checking in the original metric. These
constructions certify the target exactly when that maximum is at least
`floor(n/2)-1`. Remaining triples are **unsettled here**, not counterexamples;
even a failed exhaustive check of one finite tree would not provide the
required infinite structural obstruction. The residue upper bound excludes
full partitions only and is compatible with the project target.

For example `(29,17,6)` contains `(29,16,6)`. Its block width is 10,
quotient 3, remainder 0, giving size 26; this already attains the original
tree's disjointness upper bound. Trimming is explicitly labelled in output.
An invalid block is never truncated or silently repaired: only the unchanged
valid formula on the explicitly smaller tree is used.

### An explicit next family still outside this coverage

For every integer `t>=11`, the current constructions, including all three-tip
trimmings, give maximum size `10t+3` on `T(10t,7t,4t)`. This is below
`floor((21t+1)/2)-1`, and is **not an upper bound on h(T)**.

Here is a proof of that limitation. Write the three deletions as `d_a,d_b,d_c`,
nonnegative with total at most 3. The arm order remains unchanged. Path
halves give at most `floor((17t+1)/2)`, alternating gives at most `9t`, and
separated paths give at most `10t`. Neither special family can occur after
these deletions: for the first, `a'+1=4c'` would require
`6t=4d_c-d_a+1<=13`; for the second, `a'+1=2(c'+1)` would require
`2t=d_a-2d_c+1<=4`.

For blocks, `x'=3t-d_b+d_c` and `a'+1=10t+1-d_a`. For t>=11 their quotient
is exactly 3: the numerator is at least `10t-2>=3(3t+3)` and less than
`4(3t-3)`. The block size is therefore `2b'-c'=10t-2d_b+d_c<=10t+3`.
Deleting three tips of the shortest arm attains that last value (remainder
`t-8`), proving the stated maximum for this construction menu. Finally,
`floor((21t+1)/2)-1>10t+3` for t>=11. The next builder has a definite
unbounded family to study using unrestricted signed-shell equations.

## Verification and next acceptance

The README records a real command run. Tests independently build the tree
and count shortest-path distances by breadth-first search. They cover the
two path parities, both alternating parities and empty tails, odd block
quotients and endpoint remainders, all block-overrun remainder examples,
arm relabeling, invalid vertices, overlap and duplicate rejection, and a
pair with identical distance supports but unequal multiplicities.

A different resident still needs to reconstruct these arguments and run a
fresh counter on unequal triples, including the full-partition family.
Resolve the thesis priority gap before any novelty claim. The general
project milestone is not complete.
