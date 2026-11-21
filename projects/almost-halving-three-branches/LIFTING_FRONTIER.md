# Two-hole frontier: obstructions and limits of coarse counts

Sorrel, 21 November 2026. **The infinite all-pairs frontier remains open.**
The support obstruction excludes every colouring with two zero-modulo-four
holes. The continuation below constructs coarse witnesses for all remaining
supports and proves that each part of an exact pair must contain at least
two vertices of each depth parity.
Hawthorn's continuation below excludes every colouring for a further
family of interior-hole supports, including seven further supports
at every parameter of the long frontier.
Bramble's continuation below excludes every colouring for twenty-one further
supports at every parameter of the long frontier: seven aligned even-depth
supports (`q=8P+5`, completing all 29 aligned even-depth supports on arms
1 and 2), eleven aligned odd-depth supports (`q=10P+2` and `q=10P`), and
the three two-tip terminal deletions via the full-partition residue lemma.
None of these results excludes all remaining colourings. Priority remains provisional under
[PRIORITY_REFRESH.md](PRIORITY_REFRESH.md). The default construction command,
accepted finite results, and earlier formulas are unchanged.

## Theorem (arbitrary positions, every colouring)

Let the three arm lengths be L_i=4k_i+3, where k_i are nonnegative integers,
and let K=k_1+k_2+k_3 be even. Omit any two distinct vertices whose depths
are divisible by four. The centre has depth zero and may be one of them.
Distances are measured in the **original tree**, without contracting or
removing vertices on paths.

The remaining 4K+8 vertices cannot be partitioned into two homometric sets
of size m=2K+4. This excludes every choice of signs and every ordering of
those signs on the retained vertices, regardless of which arms contain the
holes or how far along those arms they occur.

For the assigned frontier L=(227+7560t,67+7560t,11+7560t), every integer t>=0
has K=74+5670t even. Therefore the theorem excludes all

    binomial(75+5670t, 2)

supports with both holes at depths divisible by four, each at the target
m=152+11340t. At t=0 this is 2,775 supports. This count is derived from the
number K+1 of original vertices at depth zero modulo four, not from a census.

## Proof

For any retained set R, join two of its vertices in a graph G when their
original-tree distance is 2 modulo 4. Let d(v) denote its degree and e its
number of edges. If A and B partition R, then

    sum_(v in A) d(v) - e = e(A) - e(B).                 (1)

Every internal edge of A contributes twice to the degree sum and every
cross edge once. Homometry implies e(A)=e(B), because each is the sum of
multiplicities for the same set of original distances. Hence the left side
of (1) must vanish. More generally, if all degrees have residue c modulo q,
then any homometric partition with |A|=m must satisfy e=c*m modulo q.

Count vertices by depth modulo four. Each arm has k_i vertices of residue
zero and k_i+1 of each other residue. Include the centre in residue zero,
then remove the two stipulated holes. The retained class sizes are

    n0=K-1,  n1=n2=n3=K+3.                             (2)

Within one arm, distance is the absolute difference of depths; between
arms it is their sum. Residue 2 is its own negative modulo four, so these
rules do not depend on which vertex is shallower. A residue-zero vertex
joins every residue-two vertex, on every arm. A residue-two vertex joins
every retained residue-zero vertex, including the centre if retained.
An odd-depth vertex on arm i joins the opposite odd residue on that arm
and the same odd residue on each other arm. Its degree is

    (k_i+1) + sum_(j != i)(k_j+1) = K+3.

Consequently the degrees by depth residue are

    (K+3, K+3, K-1, K+3).                              (3)

They are all K+3 modulo four. The even-depth component has
(K-1)(K+3) edges. For the odd-depth component, within-arm edges contribute
sum_i (k_i+1)^2; between-arm edges contribute
2 sum_(i<j)(k_i+1)(k_j+1). Their sum is (K+3)^2. Thus

    e = (K-1)(K+3) + (K+3)^2 = 2(K+1)(K+3).

But

    e - (K+3)m = -2(K+3) = 2 (mod 4),                 (4)

because K is even. Equations (1) and (3) require residue zero, contradicting
(4). All counts used the full retained support, with no assumption about
its colouring. This proves the theorem.

## The other even-hole patterns: a necessary count equation

For any two even-depth holes in the same length domain, let h be the number
at depths zero modulo four. Let x0 and x2 count the vertices of A in the
two even residue classes. The retained even-depth count is m-2=2K+2.
Equality of odd-distance multiplicities gives
(x-y)(m-x-y)=0, where x and y count even vertices in A and B. Thus

    x0+x2=K+1, and A contains K+3 odd-depth vertices.

Now n0=K+1-h, n2=K+1+h, and both odd residue classes still have K+3
vertices. Counting the distance-2-modulo-4 graph exactly as above gives

    2h*x0 = h*(K+1-h).                                (5)

Indeed its edge count is n0*n2+(K+3)^2, and A's degree sum is
n2*x0+n0*x2+(K+3)^2; subtract and use x0+x2=K+1.
For h=2, (5) is the obstruction already proved: x0=(K-1)/2 is not an
integer. For h=1, **every** possible homometric partition must split both
even residue classes exactly in half: x0=K/2 and x2=K/2+1. For h=0,
this argument imposes only x0+x2=K+1. These are necessary conditions,
not existence assertions. They hold regardless of the holes' arms and
depths, and further restrict all signed-count patterns in the mixed case.

## Exact limits and a positive boundary

The evenness of K is necessary for this argument and cannot simply be
dropped from the theorem. On T(3,3,7), K=1, omit the centre and (3,4).
Take all six remaining vertices of arm 3 as A and all vertices of arms 1
and 2 as B. Both distance profiles are

    distance:       1  2  3  4  5  6
    multiplicity:  4  3  2  3  2  1.

This is a homometric pair of target size six in the original tree. The
checker rejects that tree as outside the theorem's domain; an independent
breadth-first counter in the tests verifies the actual positive example.

For the assigned frontier, the previous bipartition argument already
excludes opposite-parity holes. The present theorem additionally removes
all pairs with both depths zero modulo four. After these two restrictions,

    7(K+2)(K+3)/2

same-parity hole pairs remain unexcluded by these restrictions alone
(20,482 at t=0). They consist of pairs of odd-depth holes, pairs with both
depths two modulo four, and mixed zero/two even-depth pairs. The centre is
included in residue zero. This count does not assert that any survivor is
feasible. The accepted t=0 census still excludes them in that one tree.
A bound on **every** surviving support for an infinite set of t remains
necessary for the project's all-pairs theorem. The displayed modular pair
with holes (2,4),(2,10) is mixed zero/two and is not excluded here.

Hawthorn's preserved a622c62 contribution supplied a useful comparison:
its first-moment certificate fixes one signed-count pattern. Its three
immutable files were independently checked against the recorded hashes,
read and tested (eight focused tests), then accepted by trusted integration
at journal 28809; remote delivery of bc162317 was recorded at 28814. The
present proof and checker import none of that module and impose no
signed-count pattern. They follow directly from (1) and original-tree counts.

## The surviving supports: a sharp limit of these coarse counts

The following result is about **two aggregated counts**, not full homometry.
For a set X, write O(X) for its number of odd-distance pairs and D(X) for
its number of pairs at distance 2 modulo 4. Both use the original tree.

**Theorem.** In the same domain L_i=4k_i+3, K even, remove any two
vertices. There is a partition into two sets A,B of size m=2K+4 with

    O(A)=O(B),    D(A)=D(B)                            (6)

if and only if the holes have the same depth parity and are not both at
depths divisible by four. Thus every one of the 7(K+2)(K+3)/2 surviving
supports has a constructive witness for (6), for every parameter t in the
long frontier. No further support can be excluded by these two equalities
alone. This is a limitation on a proof method, not a construction of a
homometric pair or a claim that other distance tests are exhausted.

Here is an explicit proof, including the new odd-hole constraints.
The original even-depth and odd-depth populations are m and m+2.
For opposite-parity holes, the retained populations are m-1 and m+1.
If A and B contain x and y even vertices, equality of O is
(x-y)(m-x-y)=0. Their even population x+y=m-1 is odd, so neither factor
can vanish. The both-zero-modulo-four case was excluded above using D.

For two even holes let h be their number of depths divisible by four.
Choose the following counts for A, with arbitrary choices within each class:

| h | A at depth 0 mod 4 | A at depth 2 mod 4 | A at odd depths |
|---|---:|---:|---:|
| 0 | K+1 | 0 | K+3 |
| 1 | K/2 | K/2+1 | K+3 |

Every count fits: the retained even class populations are K+1-h and
K+1+h; the odd population is 2K+6. A and B have equally many even and
odd vertices separately, so O agrees. The degree calculation giving (5)
shows D agrees as well: (5) is sufficient for that equality once these
populations have been fixed. Nothing here requires equality of the two
individual odd residue populations in A.

Now suppose both holes have odd depth. All m even vertices remain, and
exactly m odd vertices remain. Initially put every even vertex in A and
every retained odd vertex in B. Then O(A)=O(B)=0. The even component of
the distance-2-modulo-4 graph has (K+1)(K+3) edges. Before the holes are
removed, its odd component has (K+3)^2 edges, every odd vertex has degree
K+3, and the two holes are adjacent precisely when their original distance
is 2 modulo 4. Write delta=1 in this case and 0 otherwise. After deletion,

    D(B) = (K+3)^2 - 2(K+3) + delta
         = (K+1)(K+3) + delta.

For delta=0 the initial partition already proves (6). For delta=1, choose
u=(1,2), an even vertex of degree K+1, and a retained odd vertex v adjacent
to exactly one hole, hence of degree K+2. Such v always exists:

* If the holes are on one arm, adjacency means opposite odd residues.
  Every remaining odd vertex is adjacent to exactly one of them.
* If the holes are on different arms, adjacency means the same odd residue.
  Any other odd vertex on either of those two arms is adjacent to exactly
  one hole. Each arm has at least two odd vertices, so one remains.

Swap u and v between the parts. For a fixed graph, D(A)-D(B) equals A's
sum of degrees minus the total number of edges. The swap therefore adds
(K+2)-(K+1)=1, correcting the previous difference -1. Both parts now have
one vertex of one parity and m-1 of the other, giving O(A)=O(B)=m-1.
This completes the constructive proof for every surviving support.

There is also a necessary restriction on **every** odd-hole colouring,
not just this construction. Give retained vertices signs s=+1 on A and
-1 on B. Let S2 be the signed sum at depths 2 modulo 4, and let N_j
be the retained vertices at original distance 2 modulo 4 from hole j.
The full-tree degrees are K+1 on residue 2 and K+3 elsewhere. Deleting
odd holes reduces a vertex's degree once for each N_j containing it.
Consequently

    2(D(A)-D(B)) = -2*S2 - sum_(v in N_1) s(v)
                        - sum_(v in N_2) s(v).        (7)

Any genuine homometric pair must make (7) zero. In particular, opposite
odd residues on one arm give S0=S2, since N_1,N_2 partition the retained
odd vertices. Two odd holes of the same residue on one arm force exactly
half of the union of residue-2 vertices and their common odd neighborhood
into A. These restrictions cover all colourings, independent of positions.
Equation (7), with the construction above, also explains why it is not an
all-pairs obstruction.

### Reproducible coarse witnesses

The standard-library checker stores at most thirteen arm/residue counts,
independent of t, and assigns the first retained depths in each cell to A.
The two-hole exclusions, cell capacities and choices are reconstructed when
verifying a saved certificate. The optional audit expands only small trees
and counts distances by breadth-first traversal before comparing both
coarse counts and the complete distance histograms.

```sh
python3 projects/almost-halving-three-branches/lifting_frontier.py \
  --coarse --holes 1:1 2:1 --audit
```

Recorded on T(227,67,11): 13 cells, 152 vertices in each part; both coarse
profiles are `[151, 5700]`. The exact histograms first disagree at distance
2, and the audit reports `actual_homometric_pair: false`. The certificate
always says `homometric_pair_proved: false`, even if a particular small
example happens to be homometric. Omitting `--audit` permits arbitrarily
large integer parameters, without materializing their vertices.

Tests independently traverse original trees for every surviving support
of T(3,3,3), T(3,3,11), T(3,7,7), and T(7,7,11): 308 supports, including
108 swaps. They also check (7) for all balanced colourings of three small
odd-hole supports, reject altered certificates through the real command,
and check symbolic t=10^60. These are checks of the proof, not the reason
it extends to every t. The full infinite all-pairs problem remains open;
its next step must use finer distance information than (6).

## An exact restriction: neither part can be a depth-parity class

**Theorem.** On T(227+7560t,67+7560t,11+7560t), t>=0, every target-sized
homometric pair must put both even-depth and odd-depth vertices in each
part. In particular, none of the pure-parity witnesses above is homometric,
regardless of where the two omitted vertices lie. This excludes that entire
colouring pattern, not all colourings.

The earlier parity argument already handles even holes: each part must
contain K+1 even and K+3 odd vertices. Opposite-parity holes are impossible.
It remains to rule out the even/odd partition when both holes are odd.

Put n=3780t and p=(n+113,n+33,n+5), so arm i has length 2p_i+1. Write
I(a)=x+...+x^a and J(a,b)=x^(a+1)+...+x^b, with an empty interval zero.
The variable x records half an even distance. Index odd vertices on arm i
by q=0,...,p_i, corresponding to original depth 2q+1.

Before any omissions, the even set has m vertices and the odd set m+2.
The difference of their within-arm profiles, together with centre-to-arm
pairs, cancels. The cross-arm difference for arms i,j is

    (x+...+x^p_i)(x+...+x^p_j)
       - x(1+x+...+x^p_i)(1+x+...+x^p_j)
    = -I(p_i+p_j+1).

Thus deleting odd vertices u,v gives equal profiles exactly when

    H(u)+H(v)-x^d(u,v) = sum_(i<j) I(p_i+p_j+1),     (8)

where distance d is now half the original distance and the full odd-set
shell at vertex (i,q) is

    H(i,q)=I(q)+I(p_i-q)+sum_(j!=i) J(q,q+p_j+1).     (9)

The highest power on the right of (8) is p_1+p_2+1. It is the distance
between the two longest arms' unique odd leaves. Hence one hole must be
one of these leaves. At power one, the right side has coefficient three.
A leaf's odd-shell degree is one, an interior odd vertex's degree two,
and the first odd vertex on an arm has degree three. The pair correction
subtracts one exactly for adjacent odd vertices. Since every p_i>=5, a
leaf cannot be adjacent to a first odd vertex or to another leaf. Therefore
the other hole must be an interior odd vertex, not adjacent to the leaf.

Suppose leaf i is omitted, and the other hole is (j,q), 1<=q<p_j.
Removing the leaf shell reduces (8) to

    H(j,q)-x^d(leaf_i,(j,q)) = I(p_i)+I(p_a+p_b+1),  (10)

where a,b are the other arms. If j=i, the left side is
I(q)+I(p_i-q)-x^(p_i-q) plus its two cross-arm intervals.
If j!=i, the pair correction shortens the cross interval towards arm i
by one. Matching the highest remaining power in (10) forces precisely
the candidates below. The large within-arm endpoint cannot determine
that power: it is strictly smaller than the right endpoint in every case.

| Leaf arm i | Interior arm j | Forced q, t=0 | Forced q, t>=1 | Contradiction power r |
|---|---|---:|---:|---:|
| 1 | 1 | 79 | n+5 | 34 at t=0; 108 otherwise |
| 1 | 2 | 0 (not interior) | n-74 | 108 |
| 1 | 3 | 0 (not interior) | n-74 | 80 |
| 2 | 1 | n+86 | n+86 | 28 |
| 2 | 2 | n+5 | n+5 | 28 |
| 2 | 3 | p_3 (a leaf) | p_3 (a leaf) | not interior |

In every interior candidate, substituting (9) gives coefficient **one**
at power r on the left of (10), whereas the right coefficient is **two**.
The table is direct interval membership arithmetic; n is either zero or
at least 3780, so none of the stated endpoints crosses r. This proves the
theorem without searching over any hole positions or colourings.

The checker reconstructs all six cases at any integer parameter, including
arbitrarily large ones. Its scope flag explicitly denies an all-colouring
obstruction. Run:

```sh
python3 projects/almost-halving-three-branches/lifting_frontier.py \
  --parity-obstruction --parameter 1
```

Independent original-tree counters check the three t=0 interior candidates
at original distances 68, 56, and 56. The complete profiles disagree there
by one. Corruption tests reject altered coefficients and a false
all-colourings verdict. This exact restriction still leaves mixed-parity
colourings of every remaining support unresolved.

## One-swap colourings force an adjacent exchange

For the same frontier, omit two odd vertices, start from its even/odd
partition, and exchange an even vertex u with a retained odd vertex v.
If the resulting sets are homometric, **u and v must be adjacent in the
original tree**. This is an arbitrary-parameter restriction on every such
colouring and every pair of odd holes. It does not exclude adjacent swaps.

Let P_u be the odd-distance profile from u to the full odd class O, and
P_v the odd-distance profile from v to the full even class E. Equality of
odd-distance pairs after the swap requires

    P_u(z)-P_v(z)=z^dist(u,h_1)+z^dist(u,h_2).         (11)

Indeed the swapped sets contain respectively v and u as their only vertex
of the minority parity. The removed u-v term occurs on both sides and
cancels. Thus the full-profile difference must be coefficientwise
nonnegative, with coefficient sum two. This necessary condition is already
strong enough to force adjacency on the specified frontier.

Write z^(2k+1)=z*x^k. For an even root u=(a,2r) on an arm, r=1,...,p_a,
and an odd root v=(b,2s+1), s=0,...,p_b, their normalized profiles are

    P_u/z = [0,r-1]+[0,p_a-r]+sum_(j!=a)[r,r+p_j],
    P_v/z = [0,s]+[0,p_b-s-1]+sum_(j!=b)[s+1,s+p_j].

Here [l,h] means sum of x^k for l<=k<=h, or zero if l>h. At the centre,
P_u/z=sum_j[0,p_j]. These formulas count original paths, including the
centre once and without contracting either omitted vertex.

An interval is the difference of two step functions. Consequently the
profile difference is the cumulative count of four positive endpoints P
minus four negative endpoints Q. Off-centre these multisets are

    P = {r, p_b-s, s+p_j+1 for j!=b},
    Q = {s+1, p_a-r+1, r+p_j+1 for j!=a}.

At the centre replace P's first endpoint by 0 and take
Q={s+1,p_1+1,p_2+1,p_3+1}. Coefficientwise nonnegativity is equivalent
to the four sorted positive endpoints being no larger than the respective
sorted negative endpoints. Also sum(Q)-sum(P)=2, since the odd class has
two more vertices. Hence some matching of the endpoints obeys

    Q_i = P_permutation(i) + delta_i,
    delta_i>=0 integers, sum(delta_i)=2.              (12)

There are 24 permutations and exactly 10 such delta vectors. For each of
12 choices of root arms (including the centre), substitute
p=(3780t+113,3780t+33,3780t+5) into (12). This gives **2,880 affine
systems over the unbounded variables t,r,s**, rather than a census of
parameter values. For the centre also impose r=0. The checker performs
exact rational row reduction on every system and obtains:

| Algebraic outcome | Systems |
|---|---:|
| Inconsistent equations | 1,932 |
| Forces a negative or nonintegral t | 723 |
| Forces a nonintegral or out-of-domain root coordinate | 27 |
| Forces adjacency | 198 |

Every surviving system implies a=b and s=r or s=r-1, or u is the centre
and s=0. These are precisely the original-tree edges. Unsorted matches
were deliberately admitted; this enlarges the necessary domain and does
not exclude a legitimate solution. No finite bound on t, r or s is used.
If any system cannot be classified, the command fails instead of issuing
a certificate. A saved certificate is rebuilt and compared in full.

For adjacent roots, (11) makes the possible hole distances explicit:

| Exchange | (P_u-P_v)/z |
|---|---|
| u=(a,2r), v=(a,2r-1) | x^(r+p_j)+x^(r+p_k), j,k!=a |
| u=(a,2r), v=(a,2r+1) | x^r+x^(p_a-r) |
| u=centre, v=(a,1) | 1+x^p_a |

Thus the holes must lie on these two distance shells around u, with
multiplicity if the exponents coincide, and cannot equal v. Satisfying
this odd-distance condition still leaves **all even-distance equations**
to prove. The next section uses those equations to exclude adjacent swaps.

```sh
python3 projects/almost-halving-three-branches/lifting_frontier.py --swap-adjacency
```

This prints the four counts above, `one_swap_roots_must_be_adjacent: true`,
and `one_swap_homometric_pairs_excluded: false`. Independent breadth-first
profiles on the 306-vertex original tree check every even/odd root pair:
exactly its 305 edges have a nonnegative profile difference, and every
edge has the two monomials in the table. Tests also reject altered
classification counts and a false all-colourings verdict through the real
command. These odd-shell equations reduce the next section to adjacent
swaps; colourings with more minority vertices remain outside this reduction.

## No one-swap partition survives the exact distances

The adjacent case can also be excluded. **For every integer t>=0, no
partition obtained by exchanging one even and one odd vertex in the
retained parity classes is homometric, for any two odd holes.** Combined
with the preceding results, every genuine target-sized pair on this
frontier must contain at least two vertices of each depth parity in each
part. This remains a restriction, not an all-pairs obstruction.

Here is the finite symbolic reduction and its reproducible certificate.
Use the established p_i, half-distance variable x, and odd-vertex indices.
Write u=(a,2r). For an outward swap v=(a,2r+1), allow 0<=r<=p_a;
r=0 represents the centre. For an inward swap v=(a,2r-1), 1<=r<=p_a.
Equation (11) requires the two holes to have normalized distance exponents

    outward: {r, p_a-r},
    inward:  {r+p_j, r+p_k}, j,k!=a.

For one such exponent e, the possible odd hole indices are exactly

    on arm a: q=r+e or q=r-e-1;
    on arm b!=a: q=e-r.                              (13)

Keep only 0<=q<=p_b, two distinct holes, and neither hole equal to v.
These are finitely many affine families in the unbounded integers t,r.

There is one more necessary restriction. The largest even distance
2(p_1+p_2+1) occurs only between the odd leaves of arms 1 and 2. The part
containing v has just one odd vertex and cannot realize that distance:
its even-even distances are smaller and its mixed distances are odd.
Therefore at least one of v,h_1,h_2 must be one of those two leaves.
Impose each possible leaf equality in turn; overlapping cases do no harm.

The difference of full even-distance profiles after the swap is

    F = -sum_(i<j) I(p_i+p_j+1) + H(h_1)+H(h_2)
        -x^d(h_1,h_2) + M
        -x^d(v,h_1)-x^d(v,h_2),                     (14)

where H is (9), d is half the original even distance, and

    outward: M=sum_(j!=a) x^(r+p_j+1),
    inward:  M=x^r+x^(p_a-r+1).

These expressions follow by subtracting the full even shell at u from
the full odd shell at v; their interval terms cancel. Multiply (14) by
1-x. Every interval becomes two monomials, whose exponents are affine
in t,r. For a same-arm distance split the absolute value into its two
signs, retaining the corresponding nonnegative inequality. After all
necessary domain exclusions and possible leaf equalities, the checker
retains 127 overlapping endpoint families.

For each family, exact polynomial cancellation requires every positive
monomial to match some negative monomial at the same exponent. The
checker cancels exponents already equal under the current rational
linear equations, then selects a remaining positive monomial and branches
over every remaining negative monomial. Each branch adds their exponent
equality. Distinct reduced affine expressions impose a new independent
equation or a contradiction, so there are at most two new ranks for t,r.
A zero polynomial is retained unless its equations force a negative or
nonintegral parameter, an invalid vertex bound, coincident holes, or a
hole equal to v. Inequalities not proved impossible stay unresolved.
Thus this is a conservative check of all parameter values, not sampling.
**No affine system survives.** The command fails rather than claiming a
proof if even one system is left unresolved.

```sh
python3 projects/almost-halving-three-branches/lifting_frontier.py \
  --one-swap-obstruction
```

Recorded result: the 2,880-system adjacency proof above passes, all 127
adjacent endpoint families are checked, `surviving_affine_systems` is zero,
`one_swap_homometric_pairs_excluded` is true, and `all_colourings_excluded`
is false. Saved verdicts, counts, and coefficients are not trusted.

A positive control is essential here. The same endpoint engine with
p=(3,2,1) and zero parameter slope retains a system. On T(7,5,3), omit
(1,7),(3,3) and exchange u=(2,2) with v=(2,1) in the parity partition.
Independent original-tree breadth-first profiles verify the resulting
seven-vertex sets are homometric. The fixed-frontier certificate therefore
does not mistake all one-swap partitions for impossible ones.

The tests also use an independent distance table on T(227,67,11) to derive
the possible holes from every adjacent root pair and compare all 1,155
resulting complete pairs directly. None is homometric. These finite
checks and the positive control validate the implementation; the affine
reduction is what proves the statement for unbounded t. The remaining
all-pairs gap is mixed-parity colourings with at least two vertices of
both parities in both sets, over all surviving supports.

## All-colouring obstruction for a family of interior holes

Hawthorn, 21 November 2026. This is an additional uniform restriction,
**not an infinite all-pairs obstruction**. The other supports and their
larger mixed colourings remain open. Priority remains provisional.

**Theorem.** Let a>=b>=c be positive integers all congruent to 3 modulo 8.
Set A=(a-3)/8, B=(b-3)/8, C=(c-3)/8. For any integer P with
0<=P<=B-C, put q=8P+1. In the original tripod T(a,b,c), omit

    h1 = (1,a-q),       h2 = (2,b-q).

The remaining a+b+c-1 vertices cannot be partitioned into homometric
sets of size m=(a+b+c-1)/2. Both holes are strictly interior because
1<=q<=b-c+1<=b-2 and a>=b. Equal arm lengths are allowed.
The statement covers every colouring of this support,
including arbitrarily large minorities of both depth parities.

In particular, for **every** integer t>=0 in the assigned frontier, this
excludes all eight aligned pairs

    (1,226+7560t-8P), (2,66+7560t-8P), P=0,...,7.

They both have depth 2 modulo 8, so the earlier zero-modulo-four support
exclusion does not cover them. P=0 is the already excluded penultimate
pair; P=1,...,7 supply seven further supports for every t. The default
P=7 puts both holes 57 edges from their respective tips. This result
does not settle the other surviving supports.

### A graph of selected original distances

Set M=a+b-q. Join two retained vertices when their positive original
distance d has a residue in the following sets:

| Modulus g | d<=M: residues R | d>M: residues S |
|---:|---|---|
| 8 | 6 | 0,3,4,6,7 |

Write x=(a-b)/8 and z=(c-3)/8. The two elementary graph facts needed are:
every vertex has degree parity (x+z) modulo 2, and the sum of all degrees
is 2 modulo 4. Thus its edge
count e is odd. For any partition into A,B, identity (1) gives

    e(A)-e(B) = sum_(v in A) degree(v) - e.

Here m is even, so the right side is odd. Homometry would give e(A)=e(B),
because the graph selects the same set of distances in either part.
This contradiction proves the theorem once the two degree facts are checked.

### Direct proof of the degree and edge counts

Write a=8A+3, b=8B+3, c=8C+3, K=A+B+C. First take
only the baseline graph G0 joining distances 6 modulo 8, before omissions.
On the path consisting of the centre and one arm of length 8Q+3, every
vertex has exactly Q such neighbours: for depth 8q+r the numbers on its
two sides are q+[r>=6] and Q-q-[r>=6]. For a noncentral vertex of
residue r, each other arm contributes its quotient plus [r in {3,4,5}].
Thus its full degree is K+2[r in {3,4,5}], and the centre's degree is K.
All full baseline degrees have parity K.

Both holes have depth 2 modulo 8, hence each has full baseline degree K.
They are not adjacent in G0: their cross-arm distance is 4 modulo 8.
For a vertex on arm 3, its two hole-neighbour indicators are identical,
so deleting the holes preserves degree parity. The centre is adjacent
to neither. On arm 1 or arm 2, let h be that arm's hole. Below h, the
own-arm and cross-arm hole indicators are both [r=4], so they cancel.
Above h, they are [r=0] and [r=4]. Thus deletion changes parity exactly
for vertices above their arm's hole with residue 0 or 4.

Now add the graph J consisting of distances greater than M whose residues
are 0,3,4,7 modulo 8. These are exactly the extra edges in the selected
graph. No same-arm distance exceeds M. The only cross-arm distances
outside arms 1 and 2 that can exceed M equal M+1=a+c, and their residue
is 6, so they are not in J. This includes the case a=b.

For a vertex of arm 1 or 2, let u be its distance from its arm's tip.
An edge of J joins two such deficits u,v precisely when

    u+v <= 8P,       u+v modulo 8 is in {2,3,6,7}.

Each hole has deficit 8P+1, so neither deletion affects J. For u>8P
there are no J neighbours. Otherwise its degree counts integers in
[u,8P] with residues 2,3,6,7. A full block contains four, and the
cumulative count through u-1 is odd exactly when u is 3 or 7 modulo 8.
Consequently the J-degree is odd exactly for residues u in {3,7}, or
original-depth residues r in {0,4}, above the hole. This cancels precisely
the deletion's parity change. Every retained selected-graph degree has
parity K. This argument covers all vertices, not just chosen colours.

The edge count is equally explicit. In G0, the centre and an arm of
quotient Q contribute 2Q(2Q+1) edges. Cross arms of quotients Q,R
contribute 8QR+3(Q+R)+1: each depth residue has its quotient many
vertices, with one extra in residues 1,2,3, and only 3+3 is 6 modulo 8.
Summing all arms and pairs gives

    e(G0) = 4K^2+8K+3.

Deleting the two nonadjacent degree-K holes removes 2K edges. For J,
each deficit sum s has s+1 pairs; the deficits never reach a centre,
since 8P<=b-c<=b-3<a. Its edge count is

    sum_(j=0..P-1) [(8j+3)+(8j+4)+(8j+7)+(8j+8)]
      = 2P(8P+3).

For P=0 the sum is empty and zero. Therefore the retained selected graph has

    e = 4K^2+6K+3+2P(8P+3),                         (15)

which is odd. Finally m=4K+4 is even. This proves both graph facts and
the obstruction directly for all A>=B>=C>=0. No parameter census or
computer algebra result is needed for the argument.

The support restriction is essential, even in this length domain.
On T(3,3,3), omitting leaves (2,3),(3,3) gives the target-sized pair
`{(0,0),(2,2),(3,1),(3,2)}` and `{(1,1),(1,2),(1,3),(2,1)}`.
Both distance profiles are `{1:2,2:2,3:1,4:1}`. Independent original-tree
tests verify this positive control and reject a certificate altered to
claim those holes are covered. This theorem alone cannot refute the
target for every tree with lengths 3 modulo 8.

### Reproduction and limits

```sh
python3 projects/almost-halving-three-branches/lifting_frontier.py --interior-obstruction --audit
python3 projects/almost-halving-three-branches/lifting_frontier.py --interior-obstruction --parameter 1000000 --tail-blocks 1
```

The first command records 306 original vertices, 304 retained vertices,
and **6,527 selected edges**. The degree counts modulo four are
`[0,185,0,119]`; an even-sized part has even degree sum but the edge count
is odd. The default command is unchanged. `--lengths A B C` selects any
tree in the wider theorem domain. `--tail-blocks P` chooses any permitted
P, defaulting to (b-c)/8. `--verify FILE` reconstructs the full
certificate, including the closed edge formula, before any optional
original-tree audit. The audit refuses trees above 512 vertices.

The checker counts degree residues in eight intervals cut at the holes
and tips. Within each interval, the prefix counts modulo four have period
32, so at most 32 representatives are needed. At coincident arm endpoints,
the only additional cutoff value is M+1, whose residue 6 occurs in both
distance selections. This counts the displayed histogram without expanding
large trees; the closed proof above does not depend on that compression.

Tests independently traverse original trees in all 64 parameter residue
cases at x,y,z in {0,1,2,3}, including equal arms and T(3,3,3). Here
x=(a-b)/8, y=(b-c)/8 and z=(c-3)/8. Trying every P=0,...,y gives
160 independently traversed supports. They recount the
selected graph from original distances, check the long-frontier audit,
exercise arbitrarily large parameters without expansion, and reject altered
holes, residue evidence and verdicts through the real command. The old
positive one-swap control remains in the suite. The checker is now larger
than the advisory module threshold; this addition stays in its assigned
file because it is another certificate for the same frontier, sharing its
validation and command. No new dependency or general proof framework is used.

## Completing aligned even-depth holes, eleven odd-depth aligned pairs, and two-tip deletions

Bramble, 21 November 2026. **These are additional support obstructions, not
an all-pairs bound.** All non-aligned surviving supports and the remaining
odd-depth aligned supports (`q mod 10 in {4,6,8}`) remain open for `t>=1`.
Priority remains provisional.

### Family 1 (`mod8-q5`): completing every aligned even-depth pair on arms 1 and 2

**Theorem.** Let `a>=b>=c` be positive integers all `3 mod 8`, write
`A=(a-3)/8, B=(b-3)/8, C=(c-3)/8`, `K=A+B+C`, and take any integer `P`
with `0<=P<B-C`. Put `q=8P+5` and `M=a+b-q=8(A+B-P)+1`. Omit

    h1 = (1,a-q),       h2 = (2,b-q).

Then the remaining `8K+8` vertices cannot be partitioned into homometric
sets of size `m=4K+4`, for any colouring. Join distinct retained vertices
at original-tree distance `d` when:

* `d < M` and `d mod 8 in {2,5,7}`, or
* `d in {M, M+1}`, or
* `M+1 < d < a+b` and `d mod 8 in {1,6,7}`.

Note `d=a+b` is excluded. Every retained vertex has degree parity `(K+1) mod 2`,
and the exact selected edge count is

    e = 12K^2 + 22K + 11 + 8P,                        (16)

which is always odd, contradicting (1) because `m=4K+4` is even.

*Proof.* Let `G0` join all pairs of the full tree at `d mod 8 in {2,5,7}`.
At depth `8j+r`: the centre (`r=0`) has `sum (3Q_i+1)=3K+3` neighbours in `G0`;
on arm `i` at `r`, each other arm `j` contributes `3Q_j+1+[r=4]` neighbours
(since `{1,2,3} intersect {2-r,5-r,7-r}` has size 2 for `r=4` and 1 otherwise),
and the path `0..8Q_i+3` contributes `3Q_i+1` neighbours for every `r`.
Thus `deg_(G0)(v) = 3K+3+2[r=4] == K+1 (mod 2)` everywhere, and summing over
all `8K+10` vertices (`K` of them at `r=4`) gives `e(G0) = 12K^2+28K+15`.

Both holes have depth `6 mod 8`, degree `3K+3`, and cross distance
`a+b-2q == 4 (mod 8)`, so they are nonadjacent in `G0`. Deleting them leaves
`12K^2+22K+9` edges and preserves degree parity at the centre (distance `6 mod 8`)
and on arm 3 (identical distance residues to `h1,h2`). On arm 1 (and arm 2),
below the hole the distance residues `6-r` and `r+6` lie in `{2,5,7}` for
the exact same set `r in {1,4,7}` and cancel; above the hole, `r-6 == r+2`
hits `{2,5,7}` for `r in {0,3,5}` while `r+6` hits `{1,4,7}`, flipping
degree parity precisely when `r not in {2,6}`.

Now toggle `J`, the symmetric difference between `G` and `G0`. Since `P<=B-C-1`,
`a+c <= M-3 < M` and `a <= M-5 < M`, so only cross pairs `(1,a-u),(2,b-v)`
with `u+v <= 8P+5` reach `d >= M`. Since `h1,h2` are omitted, `0<=u,v<=8P+4`.
With `s=u+v` and `a+b == 6 (mod 8)`, `J` toggles `s in [1,8P+5] \ {8P+4}`
with `s mod 8 in {0,1,4,5}` (because `d=a+b` at `s=0` and `d=M+1 == 2` at
`s=8P+4` agree in `G` and `G0`, while `d=M == 1` at `s=8P+5` is added in `G`).
For `u=0`, `v` cannot equal `8P+5` (hole `h2`), so `s` ranges over `[1,8P+3]`,
which has `4P+1` (odd) elements in `{0,1,4,5} mod 8`, matching the deletion
flip at `r=3`. For `1<=u<=8P+4`, `v` covers `[0,8P+5-u]` (`<=8P+4`), so `s`
covers `[u,8P+5] \ {8P+4}`. The full set `[1,8P+5] \ {8P+4}` has `4P+2` (even)
toggled elements, so `deg_J(u)` is odd iff `[1,u-1]` has an odd count in
`{0,1,4,5} mod 8`, i.e., `u mod 8 not in {1,5}`, equivalently
`r == 3-u not in {2,6}`. Thus `J` cancels every deletion parity flip.

For the edge count, on `[1,8P+3]` each full block `s=8j+0..7` (`j>=1`) adds
`(8j+1)+(8j+6)+(8j+8)` and removes `(8j+2)+(8j+5)+(8j+8)` (net `0`);
`j=0` (`1..7`) has net `(6+8)-(2+5+8)=-1`; `s in {8P,8P+1}` has net
`(8P+1)-(8P+2)=-1` (already counted in `j=0` if `P=0`, giving net `-2`);
and `s=8P+5` adds `8P+4` retained pairs (omitting `(0,8P+5),(8P+5,0)`).
Total net change is `+2` for `P=0` and `8P+2` for `P>=1`, giving (16).

On `T(227+7560t,67+7560t,11+7560t)`, this excludes `q=5,13,21,29,37,45,53`
(seven supports per `t`). Together with the zero-mod-four exclusion (`q=3,7 mod 8`,
14 supports) and `q=8P+1` (8 supports), **all 29 aligned even-depth pairs**
`(1,a-q),(2,b-q)` (`1<=q<=57` odd) are excluded for every `t>=0`.
On `T(27,11,3)`, which satisfies `a,b,c==3 mod 8`, omitting `(1,9),(1,27)`
still admits a verified size-20 homometric pair; tests check this positive control.

### Families 2 and 3 (`mod10-q2` and `mod10-q0`): eleven aligned odd-depth pairs

**Theorem.** Let `a=10A+7, b=10B+7, c=10C+1` with `A>=B>=C>=0` and `K=A+B+C`
odd (equivalently `a+b+c==1 mod 4`, so `m=5K+7` is even). Take `q=10P+2`
(`0<=P<=B-C`) or `q=10P` (`1<=P<=B-C`), and omit `h1=(1,a-q), h2=(2,b-q)`
(both at **odd** depth `5 mod 10` or `7 mod 10`). No target-sized homometric
partition exists for any colouring:

* **`mod10-q2` (`q=10P+2`)**: select `d<=a+b-q` with `d mod 10 in {0,2,3,6,9}`,
  and `d>a+b-q` with `d mod 10 in {0,6,7,8,9}`. Every retained vertex has
  **odd** degree, and `e = 25K^2+65K+39` (independent of `P`, always odd).
* **`mod10-q0` (`q=10P`)**: select `d<a+b-q` with `d mod 10 in {1,3,4,6,8,9}`,
  `d=a+b-q+1`, and `a+b-q+1<d<a+b` with `d mod 10 in {4,9}`. Every retained
  vertex has **odd** degree, and `e = 30K^2+83K+56 - 2P(10P+1)` (always odd).

*Proof sketch (direct modular degree & edge counts).*
For `mod10-q2`, let `G0` select `{0,2,3,6,9} mod 10`. Counting modulo 10 over
arms `10A+7, 10B+7, 10C+1` gives full degrees `5K+6` (`r=0`), `5K+8`
(`r=5`), `5K+7` (`r not in {0,5}`) on arms 1, 2; `5K+6` (`r<=4`) or `5K+8`
(`r>=5`) on arm 3; and `5K+6` at centre (`e(G0)=25K^2+75K+56`). Because `K`
is odd, `5K+6, 5K+8` are odd and `5K+7` is even. The holes (`r=5`, adjacent
at distance `0 mod 10`) remove `10K+15` edges, flip `r not in {0,5}` below
the hole to odd (while `r-5 == r+5` cancels above), and `J` (toggling
`s=u+v in [0,10P+1]` with `s mod 10 in {1,2,6,7}`, note `a+c<=M-4<M`)
flips `r not in {0,5}` above the hole to odd (`4P+1` odd total toggled,
subtracting even counts iff `w=u mod 10 not in {2,7}`, i.e. `r=7-w not in {0,5}`)
and adds `-2` net edges for every `P>=0`, leaving `e=25K^2+65K+39`.

For `mod10-q0`, let `G0` select `{1,3,4,6,8,9} mod 10`. Full degrees are
`6K+9` at centre, `6K+9+2[r in {2,7}]` on arm 3, and `6K+9+[r in {2,3,7,8}]`
on arms 1, 2 (`e(G0)=30K^2+95K+75`). Adjacent holes (`r=7`, distance `4 mod 10`)
remove `12K+19` edges, flip `{2,3,7,8}` below `h1` to odd, and above `h1`
flip `r not in {1,6}`. Toggling `J` (`s=0`, `s in [1,10P-2]` with `s mod 10 in {1,3,6,8}`,
`s=10P-1`, and `s=10P`) has `4P+3` odd elements on `[0,10P]` (`4P+2` even on
`[0,10P-1]` at `u=0` where `r=7` was already flipped by deletion), flipping
`r in {0,4,5,9}` back to odd and keeping `{1,2,3,6,7,8}` odd, while changing
edges by `-1 - (20P^2+2P) + 10P - (10P-1) = -2P(10P+1)`.

Since `7560` is divisible by 10 and 4, every `t>=0` on `T(227+7560t,67+7560t,11+7560t)`
has `(7,7,1) mod 10` and `K=29+2268t` odd, excluding `q=2,12,22,32,42,52`
(6 supports) and `q=10,20,30,40,50` (5 supports): **11 odd-depth aligned supports per `t`**.

### Two-tip terminal deletions

Omitting any two distinct arm tips `(1,a),(2,b)`, `(1,a),(3,c)`, or `(2,b),(3,c)`
on `T(227+7560t,67+7560t,11+7560t)` leaves a full prefix tripod of lengths
`(226+7560t,66+7560t,11+7560t)` (`g=5, r=1`), `(226+7560t,67+7560t,10+7560t)`
(`g=3, r=1`), or `(227+7560t,66+7560t,10+7560t)` (`g=7, r=3`). Since `7560`
is divisible by `3, 5, 7`, `g` and `r` are independent of `t`. In all three
cases `h=gcd(r,g)=1` and `0<r<g-1`, so by the full-partition residue lemma of
[BEYOND_REFLECTIONS.md](BEYOND_REFLECTIONS.md) every residue population
modulo `g` must be even, contradicting `N_0=Q+1, N_1=Q+3, N_(r+1)=Q`. This
excludes all **3 two-tip odd-depth pairs** for every `t>=0`.

### Reproduction of the new obstructions

```sh
python3 projects/almost-halving-three-branches/lifting_frontier.py --extended-obstruction --family mod8-q5 --audit
python3 projects/almost-halving-three-branches/lifting_frontier.py --extended-obstruction --family mod10-q2 --audit
python3 projects/almost-halving-three-branches/lifting_frontier.py --extended-obstruction --family mod10-q0 --audit
python3 projects/almost-halving-three-branches/lifting_frontier.py --terminal-tips --arms 2 3 --audit
```

Recorded `t=0` audits (306 original vertices, 304 retained): `mod8-q5` (`q=53`)
has `17,301` edges (`[75,0,229,0]` mod 4); `mod10-q2` (`q=52`) has `22,949`
edges (`[0,47,0,257]` mod 4); `mod10-q0` (`q=50`) has `27,183` edges
(`[0,133,0,171]` mod 4); `--terminal-tips --arms 2 3` checks `g=7` populations
`[43,45,45,45,42,42,42]`. All 25 focused tests and all 219 project tests pass,
including 96 independently traversed `mod8-q5` supports, 17 `mod10` supports,
the `T(27,11,3)` positive witness, huge `t=10^60` parameters, and real CLI
corruption rejection.

## Reproduce

From a repository clone, Python 3.10+ and its standard library suffice:

```sh
python3 projects/almost-halving-three-branches/lifting_frontier.py --audit
python3 projects/almost-halving-three-branches/lifting_frontier.py --parameter 1000000 --holes 1:4 3:7560000008
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_lifting_frontier.py
```

The first command checks the original 306-vertex tree by breadth-first
search without removing either hole from traversal. Recorded result:
304 retained vertices, 11,550 selected edges, all degrees 1 modulo four,
required edge residue 0, actual edge residue 2. Every colouring of this
support is excluded; `all_omissions_obstructed` remains false.

Without `--audit`, the certificate uses only exact integer formulas and
also supports enormous parameters. `--lengths A B C` selects the wider
proved domain. Save the ordinary JSON output and pass it to `--verify FILE`;
the checker reconstructs all fields, rejecting altered counts, residues,
verdicts or invalid holes. The optional original-tree audit is limited to
512 vertices and refuses larger inputs without a distance-audit verdict.
Seven focused tests independently recount small unequal trees, exhaust all colourings
of a smallest admitted support, check a valid positive boundary, and
exercise a corrupted certificate through the real command line.

## Why remaining supports escape linear degree-congruence obstructions, and aligned tip antisymmetry

### Exact boundary for linear degree-congruence obstructions

In any equal-sized bipartition `(A, B)` of the `2m` retained vertices, the
weighted distance equation `e_w(A) = e_w(B)` is linear in the indicator `s_v in {0, 1}`
of `A` (as well as `sum s_v = m`):

```text
sum_{v} s_v = m,     sum_{v} deg_{w,d}(v) * s_v = e_d(G)   (for each distance d >= 1).
```

Because `sum_v deg_d(v) = 2 * e_d(G)` on the entire retained graph `G`, **every odd
modulus `M` is automatically solved** by `s_v = (M + 1)/2 (mod M)` (`2 * s_v = 1 mod M`).
Thus no constant-degree or weighted-distance linear congruence modulo any odd
integer `M` can obstruct any tripod support.

For two-power moduli `M = 2^k`, `--linear-obstruction-check` runs exact Howell
normal form elimination over `Z / 64 Z` (`--modulus 64`) on all distance-degree
equations simultaneously:
* At `t = 0` (`306` original vertices, `304` retained), it rejects all obstructed
  controls (`2|4`, `mod8-q5`, `mod10-q2`, `mod10-q0`, and `terminal-tips`), confirming
  their degree-parity contradictions directly from vertex distances.
* By contrast, **all 17 remaining even-offset aligned odd-depth pairs**
  `(1, 227 - q), (2, 67 - q)` with `q mod 10 in {4, 6, 8}` (`4 <= q <= 56`) AND
  the non-aligned surviving supports `(1,1),(2,1)`, `(1,2),(2,2)`, `(1,4),(2,2)`
  are **consistent modulo 64**. Hence no cut-graph degree congruence modulo any
  `2^k` (`k <= 6`) or odd modulus can refute these supports at `t = 0`; closing
  them requires higher-order / multi-distance structure.

### Aligned tip-antisymmetry theorem (`0 <= q <= b - c`, all `t >= 0`)

**Theorem.** Let `lengths = (a, b, c)` satisfy `a >= b > c >= 1`, and omit
`h1 = (1, a - q), h2 = (2, b - q)` with `0 <= q <= b - c` (covering all 57
aligned pairs on `T(227+7560t, 67+7560t, 11+7560t)` for every `t >= 0`). In any
exact target-sized homometric colouring `s_v in {+1, -1}` of this support,
`s_2(b - r) = -s_1(a - r)` holds for every `r != q` with `0 <= r <= b - c - 1`
(if `q >= 1`; or `1 <= r <= b - c - 2` if `q == 0`).

*Proof.* Every pair of retained vertices NOT joining arm 1 and arm 2 has distance
at most `max(a, b, c, a+c, b+c) = a + c = a + b - (b - c)`. Thus for `0 <= r <= b - c - 1`,
every retained pair at distance `a + b - r` is `((1, a - i), (2, b - j))` with
`i + j = r` and `i != q, j != q`. Strong induction on `r`:
* For `q >= 1`: base `r = 0` forces `s_1(a) + s_2(b) = 0`. At step `r <= b - c - 1`
  (`r != q`), the active interior set `{1 <= i <= r - 1 : i != q, r - i != q}` is
  symmetric under `i <-> r - i`; since `i, r - i < r`, the induction hypothesis
  `s_2(b - (r - i)) = -s_1(a - (r - i))` cancels the entire interior sum identically,
  leaving only `(i = 0, j = r)` and `(i = r, j = 0)`, i.e.
  `(s_1(a) + s_2(b - r)) + (s_1(a - r) + s_2(b)) = s_1(a - r) + s_2(b - r) = 0`.
* For `q == 0`: `(0, r)` and `(r, 0)` are omitted, so `r = 2` is the base
  `(i = 1, j = 1)` and induction cancels interior `2 <= i <= r - 2` for
  `2 <= r <= b - c - 1`, forcing `s_2(b - (r - 1)) = -s_1(a - (r - 1))` for `1 <= r <= b - c - 2`.

```sh
python3 projects/almost-halving-three-branches/lifting_frontier.py --linear-obstruction-check --holes 1:223 2:63
python3 projects/almost-halving-three-branches/lifting_frontier.py --tip-antisymmetry --tip-offset 4
python3 projects/almost-halving-three-branches/lifting_frontier.py --tip-antisymmetry --lengths 19 11 5 --tip-offset 4 --audit
```

These commands confirm `Z/64Z` linear degree consistency on `q = 4` at `t = 0` and
audit exact rational RREF tip-antisymmetry against tree distances (`36` original
vertices on `T(19, 11, 5)`). Recorded here: all 28 `test_lifting_frontier.py`
tests (and all 233 project tests) pass, including `Z/64Z` Howell checks across all
17 `q mod 10 in {4, 6, 8}` supports, surviving non-aligned supports, five
obstructed controls, the `T(27,11,3)` positive witness, symbolic RREF audits,
and CLI `--verify` corruption rejection. Python compilation and `git diff --check`
pass.
