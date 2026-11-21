# Two-hole frontier: obstructions and limits of coarse counts

Sorrel, 21 November 2026. **The infinite all-pairs frontier remains open.**
The support obstruction excludes every colouring with two zero-modulo-four
holes. The continuation below constructs coarse witnesses for all remaining
supports and proves that an exact pair must mix depth parities in both parts.
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
