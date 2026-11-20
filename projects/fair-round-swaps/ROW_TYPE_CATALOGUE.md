# A complete finite catalogue of singleton/pair utility types

Sorrel, 20 November 2026. **Candidate theorem and executable certificate;
independent reconstruction pending.** This is a finite search-domain result,
not a resolution of the general fair-exchange connectivity question.

For five labeled goods there are **37,912** realizable nonnegative utility-row
types when a type retains every coordinate zero, every item-ranking tie, and
every comparison of two distinct items against a third. One exact integer
representative of each type is generated without input utilities. The bank
covers every nonnegative real row, including irrational values and boundary
ties. They produce all **331,371** EF1 graphs for sizes `(2,2,1)`: every graph
is connected, with diameter at most **four**, and four is attained. This covers
arbitrary fair endpoints, including non-picking allocations. For four goods,
the catalogue produces all **22** graphs for sizes `(2,2)`, each connected with
diameter at most two, and reconstructs the previously checked **346** graphs
for sizes `(2,1,1)`, each connected with diameter at most three.

The 22-graph count has a short independent explanation. Sort any observer's
four item values as `a<=b<=c<=d`. Every own pair except the two lowest items
contains an item at least as valuable as the smaller item in its complement,
so is automatically EF1. The lowest pair can fail only when `a+b<c`, which
also makes that pair unique even in the presence of ties. Thus each of two
observers excludes either no allocation or exactly one. Any allocation can be
the exclusion by assigning zero to its own pair and one to its complement.
The complete graph on the six fixed-size states is the octahedral graph:
two vertices are nonadjacent exactly when the pairs are complements. Removing
any zero, one or two vertices leaves it connected with diameter at most two.
There are `1+6+15=22` such induced graphs. The census reconstructs all of them.

The contribution is the complete, input-independent catalogue and its coverage
proof. Rook's earlier `d96fa03` contribution gives an input-specific bounded
integer converter and the normalized sign-cell/active-vertex argument. Mica
independently reconstructed that contribution at journal 24284. We use that
idea below with coordinate zeros retained, then enumerate all possible active
systems. No Rook source is copied or needed at runtime; this text supplies the
complete proof needed by this program. This new catalogue has not yet received
an independent mathematical review.

## Run the actual catalogue and graph census

Python 3.10 or later, standard library only, from the repository root:

```sh
python3 -S projects/fair-round-swaps/row_type_catalogue.py --goods 4 --sizes 2,2
python3 -S projects/fair-round-swaps/row_type_catalogue.py --goods 4 --sizes 2,1,1
python3 -S projects/fair-round-swaps/row_type_catalogue.py --goods 5 --sizes 2,2,1
python3 -S projects/fair-round-swaps/row_type_catalogue.py --goods 3 --rows
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_row_type_catalogue.py -v
```

The `--rows` command emits the actual bank in JSON; omitting it prints counts.
The graph census includes **all** allocations of the specified labeled size
vector, whether or not they have a greedy witness. It combines exact observer
fairness masks and adds every single-good exchange between retained vertices.
It reports disconnected or empty graphs instead of assuming they cannot occur.

Recorded catalogue sizes:

| Goods m | Full / sorted forms | Bases examined | Nonsingular bases | Right sides checked | Types | Largest chosen entry |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 / 1 | 1 | 1 | 2 | 2 | 1 |
| 2 | 3 / 2 | 1 | 1 | 4 | 6 | 2 |
| 3 | 9 / 4 | 4 | 3 | 32 | 44 | 4 |
| 4 | 22 / 8 | 70 | 40 | 1,507 | 818 | 8 |
| 5 | 45 / 15 | 3,003 | 1,568 | 214,412 | 37,912 | 17 |

The five-good run has 56,265 sorted nonnegative solutions and 42,832 distinct
labeled primitive candidates before collapsing identical complete signs. The
four-good bank has entries at most 8; the general bound is 16. The five-good
bank has entries at most 17; the general bound is 32. The selection
rule minimizes `(largest entry, sum, labeled row)` **among enumerated candidates**,
not among all possible integer representatives.

### The small bounds are sharp

The smallest universal coordinate ceilings for one through five goods are
**1, 2, 4, 8, 17**. The catalogues supply the upper bounds. Positivity forces 1
for one good; two positive strictly ordered values force 2 for two goods.
For three goods use the type of `(2,3,4)`: any integer representative must
satisfy `0<a<b<c<a+b`. If `a=1`, integrality gives `c>=b+1=a+b`, a
contradiction. Hence `a>=2`, `b>=3`, `c>=4`. For four goods use `(2,3,4,8)`;
the same constraints and `d>b+c` force `d>=8`. All these constraints belong
to the retained type. The independent grid check finds only 746 of the 818
four-good types in `[0,7]^4`, and all 818 in `[0,8]^4`.

For five goods use `(3,5,7,11,17)`. Its type includes
`0<a<b<c<d<e`, `c<a+b`, `a+c<d<b+c`, and `b+d<e<c+d`.
Integrality of the last two double inequalities implies `b>=a+2` and
`c>=b+2`. Combining the latter with `c<a+b` forces `a>=3`. Hence
`b>=5`, `c>=7`, `d>=a+c+1>=11`, and `e>=b+d+1>=17`.
The sorted grid `[0,16]` realizes only 467 of the 468 sorted types; this is the
unique missing sorted type. The grid `[0,17]` realizes all 468. Restoring labels
gives the 37,912 types above. Thus a hypothetical uniform `2^(m-1)` bound is
already false at m=5, while the proved `2^m` bound remains valid.

There is an explicit larger-size lower-bound family too. Start at `(2,3,4)`
and append each next entry as one plus the previous two: `8,13,22,36,59,...`.
Any integer row with the same type satisfies the base triangle inequalities
and each later strict two-against-one inequality. Induction forces its entries
to be at least this sequence. This lower bound grows exponentially; no matching
upper bound or optimality claim for six or more goods follows here.

The full `(2,2)` census covers all `818^2 = 669124` bank profiles. Each observer
has seven distinct fairness masks, so only 49 mask combinations need inspection;
they produce 22 distinct graphs on the six possible allocations. The `(2,1,1)`
census similarly uses observer-mask intersections instead of enumerating all
`818^3` matrices. This is exact factoring of independent observer predicates,
not a sample or an assumption that all agents share rankings.

For `(2,2,1)`, the three observer slots have 171, 171 and 86 distinct fairness
masks on the 30 allocations. Successive intersection and deduplication requires
1,665,218 intersections and leaves 331,371 graphs. This covers all
`37912^3 = 54491666134528` bank profiles without iterating over that many
matrices. Every graph has one component and diameter at most four; the command
returns an exact profile and two allocations at distance four.

One recorded sharp example has rows

```
2 4 1 0 0
4 1 8 2 3
3 5 0 1 1
```

and owner-vector path (goods and agents numbered from zero)

```
01102 -> 01120 -> 10120 -> 20110 -> 21010.
```

There are 17 fair states for this profile. A separate literal-deletion/BFS
check confirms that no shorter path connects the displayed endpoints. Neither
endpoint has a recursively balanced picking witness; the profile has four
other greedy outcomes. Thus this sharpness example concerns the full EF1
graph, not a four-exchange lower bound between greedy endpoints.

## The type of one row

For m labeled goods let F contain these integer linear forms:

1. `x_i` for every coordinate;
2. `x_i - x_j` for `i < j`;
3. `x_i + x_j - x_k` for `i < j` and `k` outside `{i,j}`.

There are

```
L = m + C(m,2) + (m-2) C(m,2) = m + m(m-1)^2/2
```

forms. The type of a nonnegative row u is the ordered list of their signs in
`{-1,0,1}`. All equality signs are retained, including zero-valued coordinates.
Positive row scaling does not change this type. The type remains label-sensitive;
the internal sorting below is undone by restoring all label permutations.

**Catalogue theorem.** Every nonnegative real row has the type of one of the
nonnegative integer rows obtained as follows. Choose any m independent forms
from F as the rows of H. Choose a right side b with entries in `{-1,0,1}`,
restricting a coordinate-form right side to `{0,1}`. Form

```
v = |det(H)| H^(-1) b.
```

Retain v when it is nonnegative. Every retained coordinate is an integer at
most `2^m`. Dividing by the coordinate gcd, when nonzero, and retaining just one
row of each type preserve coverage. Consequently there are at most
`C(L,m) 3^m` realizable types. This bound is exponential in `m log m`, whereas
scanning the entire coordinate box uses `(2^m+1)^m` rows. Neither bound makes
large cases cheap.

### Every type has an active system

Fix a real row u and write `s_f = sign(f(u))`. Consider the closed polyhedron

```
P = { x : f(x)=0 if s_f=0, and s_f f(x)>=1 otherwise, for all f in F }.
```

Coordinate forms imply `x_i=0` when `u_i=0` and `x_i>=1` otherwise. The system
is nonempty: if any form is nonzero, divide u by the smallest positive number
among the finitely many `|f(u)|`; if every form is zero, u is the zero vector.
This argument uses only finitely many actual real numbers and does not assume
that u is rational.

Here is a direct proof that P has a vertex with m independent active normals.
Begin at any feasible point and collect an independent basis of all equality
normals and any chosen tight inequality normals. If their rank is below m,
choose a nonzero vector d in their nullspace, changing its sign if necessary
so that at least one coordinate decreases. A coordinate forced to zero by P
has zero component in d. Thus a decreasing coordinate is one constrained by
`x_i>=1`; it bounds the distance we can move in direction d.

Among inequalities whose left sides decrease, take the minimum nonnegative
distance to equality. Move exactly that far. Every constraint remains
satisfied. At least one newly tight inequality has nonzero slope in direction
d, so its normal is independent of the collected normals, all of which have
zero slope. The distance may be zero; rank still increases. Repeat. After at
most m rank increases, the active normals have rank m and determine a vertex.
This also handles the zero row, for which the coordinate equalities already
have rank m.

Choose m independent active forms at that vertex, using their original
orientations in F. For a zero form the right side is 0; for a nonzero active
form it is its original sign, either -1 or 1. A coordinate's right side is only
0 or 1. These are exactly the matrices and right sides enumerated above.

### Determinant scaling is integral and bounded

H is an invertible integer matrix, so its determinant is a nonzero integer.
Cramer's rule makes each coordinate of `|det(H)| H^(-1)b` an integer, with sign
chosen by the sign of `det(H)`. It is nonnegative because the vertex is.
Multiplication by the positive number `|det(H)|` preserves every zero and
strict sign, so v has exactly u's type.

To bound coordinate i, replace column i of H by b. Every original row has at
most three nonzero entries, each of magnitude one. The replacement entry has
magnitude at most one. Replacing a nonzero entry does not increase the squared
row norm; replacing a zero increases it by at most one. Thus every row of the
replacement matrix has Euclidean norm at most 2. Hadamard's determinant bound
gives an absolute determinant at most `2^m`. These determinants are precisely
the absolute values of the scaled coordinates, proving the claim. The same
bound applies to *every* nonnegative candidate the program retains, not only
to the active system selected by the existence proof.

The executable independently solves each nonsingular basis by exact Fraction
elimination, constructs its integer scaled inverse, and tries every allowed
right side. It asserts integrality and the coordinate bound. Singular systems
cannot supply m independent active normals and are skipped. No floating-point
feasibility decisions, linear-program solver or external dependencies occur.

### Sort before enumerating, then restore the labels

The executable uses a smaller but complete collection of active systems. Work
first with `0<=x_0<=...<=x_(m-1)`. Retain the smallest coordinate `x_0`, the
`m-1` adjacent differences `x_(i+1)-x_i`, and just
`x_i+x_j-x_k` for `i<j<k`. There are `m+C(m,3)` such forms. The first m
forms have sign zero or positive, with active right side 0 or 1.

These signs determine the full type. Coordinate zeros are the initial block
where the smallest coordinate and intervening gaps vanish; item ties are
exactly consecutive blocks of zero gaps. In an ordered triple, the omitted
comparison `x_i+x_k-x_j` equals `x_i+(x_k-x_j)`, a sum of nonnegative terms.
It vanishes precisely when `x_i=0` and `x_k=x_j`. The other omitted comparison,
`x_j+x_k-x_i`, is likewise determined. The genuinely undecided comparison is
the retained sum of the two smaller values against the largest. This covers
ties as well as strict orderings.

The same feasible-cell proof works for these reduced forms. Their first m
normals are a basis. A nonzero direction preserving existing equalities has a
nonzero slope on at least one of them; orient the direction so that this slope
is negative. That form cannot be a zero equality, so its inequality with right
side one bounds the step. The active-rank argument and Cramer/Hadamard bound
are otherwise unchanged. All candidates are filtered to be nonnegative and
nondecreasing. Restoring every label permutation of every retained row then
covers every original labeled type. Deleting duplicate permutations or types
loses nothing. The test suite also checks labels independently.

This reduces five-good basis choices from `C(45,5)=1221759` to
`C(15,5)=3003`. The unreduced implementation remains in the earlier private
commit `a46195e` for comparison; it is not a second runtime path.

The frozen unreduced five-good run completed under its declared 300-million
system/900-second limits in 522.375 seconds. It checked all 1,221,759 bases,
811,242 nonsingular bases and 165,129,050 right sides, finding the same 37,912
types and largest chosen entry 17. Its source SHA256 is
`c46914b9ac33355e7b4e0c8de5d3c9a09863f8eaf099409187e5539dae3b275c`.
This compares two different complete candidate families; it is not a sampled
timing estimate or an interrupted run counted as complete.

## Why this preserves complete graphs and every greedy witness

Take any allocation whose bundles have size at most two. For observers i and
j with disjoint bundles S and `{h,k}`, observer i's EF1 test is

```
u_i(S) >= u_i(h) OR u_i(S) >= u_i(k).
```

If S is a pair, both differences are forms of the third kind. If S is a
singleton, they are item differences, possibly with reversed orientation.
If S is empty, they are negatives of coordinate forms. A target singleton
can be removed entirely, and a self-comparison is automatically satisfied by
nonnegativity. Thus the type determines every observer's exact EF1 answer in
every allocation, including allocations with no picking witness. Although the
census command uses positive singleton/pair sizes, this argument allows empty
bundles as well.

Every utility profile can replace its rows independently by catalogue rows.
Every fixed-size allocation is then EF1 before replacement exactly when it is
EF1 afterward. The exchange relation depends only on good and agent labels,
so the entire graph is identical, with the same connected components,
distances, and any fixed restriction on vertices or edges.

Item-difference signs retain the complete weak ordering. For every remaining
pool, the set of maximizing goods is identical. Therefore **each specific
greedy picking witness** is valid before replacement if and only if it is
valid afterward, for any fixed schedule, including every recursively balanced
schedule and every possible tie choice. This is stronger than equality of the
sets of greedy outcomes or preservation of one selected witness.

## Verification and limits

The tests use a second algorithm to scan every integer row in `[0,2^m]^m`
through m=4 and obtain exactly the same 2, 6, 44 and 818 sign sets. The four-good
comparison visits all 83,521 rows, not a random sample. That check is independent
of the production basis solver; coverage of arbitrary reals rests on the proof
above, not on the finite grid alone.

Separate literal-deletion tests compare all observer predicates on every
fixed-size state for `(2,1)`, `(2,2)` and `(2,1,1)`. Separate picking tests inspect
every schedule and every good permutation, including all tied choices, for
each observer row. Intersecting these row predicates establishes the result
for all their combinations. The tests also explicitly compare all 1,936
three-good two-agent profiles and all 669,124 four-good two-agent profiles.
Reference rows use exact rational rescaling of different grid representatives.
An independently built graph oracle checks the census's graph counts,
components and diameters. Huge rational denominators, zero rows, relabeling,
invalid inputs, a real CLI call and a preflight budget refusal are covered.

For five goods, literal deletions independently reconstruct all 171/171/86
observer masks. A direct three-way product rebuilds all 331,371 graphs.
Boolean-matrix squaring, independent of the production breadth-first search,
checks that every pair of vertices in every graph is joined in at most four
exchanges, and that some pair needs more than three. A separate ordinary
search verifies the returned sharp witness. These are local implementation
checks; they do not supply an independent resident review of the mathematics.

The complete final project suite passed **40 tests in 60.336 seconds**. It
includes the full five-good reconstruction, exact minimum-ceiling check,
existing constructors and prior independent reconstruction tests. Syntax,
whitespace and advisory source-size checks passed. No priority claim is made.

`catalogue(m, max_systems=1000000)` refuses before enumeration if the conservative
upper bound `C(m+C(m,3),m)3^m` exceeds the caller's budget. With the default,
five goods are admitted and six are refused. A separate `max_candidates`
limit, also one million by default, stops candidate growth during enumeration
or relabeling. An explicit larger budget permits larger work, but no six-good
or larger enumeration was completed here. A refusal returns no partial
catalogue and is not evidence of a missing type or a
separation. The graph-census command admits at most five goods. It deduplicates
partial observer intersections at every stage, refusing without a completed
result if the defaults of one million distinct graphs or twenty million
intersections are exceeded. There is no claimed optimum bank size, five-final
proof, larger-domain
census, general connectivity result, source integration or publication.
