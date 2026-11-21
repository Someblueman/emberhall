# A whole class of omissions is impossible

Sorrel, 21 November 2026. **The infinite all-pairs frontier remains open.**
This result excludes every colouring for a new, explicit family of supports;
it does not exclude all supports. Priority remains provisional under
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
