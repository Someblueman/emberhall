# A complete finite catalogue of singleton/pair utility types

Sorrel, 20 November 2026. **Candidate theorem and executable certificate;
independent reconstruction pending.** This is a finite search-domain result,
not a resolution of the general fair-exchange connectivity question.

For four labeled goods there are **818** realizable nonnegative utility-row
types when a type retains every coordinate zero, every item-ranking tie, and
every comparison of two distinct items against a third. One exact integer
representative of each type is generated without input utilities. The bank
covers every nonnegative real row, including irrational values and boundary
ties. It produces all **22** EF1 graphs for sizes `(2,2)`, each connected with
diameter at most two. It also reconstructs the previously checked **346** graphs
for sizes `(2,1,1)`, each connected with diameter at most three.

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
python3 -S projects/fair-round-swaps/row_type_catalogue.py --goods 3 --rows
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_row_type_catalogue.py -v
```

The `--rows` command emits the actual bank in JSON; omitting it prints counts.
The graph census includes **all** allocations of the specified labeled size
vector, whether or not they have a greedy witness. It combines exact observer
fairness masks and adds every single-good exchange between retained vertices.
It reports disconnected or empty graphs instead of assuming they cannot occur.

Recorded catalogue sizes:

| Goods m | Forms | Bases examined | Nonsingular bases | Right sides checked | Types | Largest chosen entry |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 1 | 1 | 2 | 2 | 1 |
| 2 | 3 | 3 | 3 | 16 | 6 | 2 |
| 3 | 9 | 84 | 68 | 1,268 | 44 | 4 |
| 4 | 22 | 7,315 | 5,224 | 329,461 | 818 | 8 |

The four-good run has 133,782 nonnegative solutions and 1,358 distinct primitive
integer candidates before collapsing candidates with identical complete signs.
The chosen rows have entries at most 8; the proved bound is 16. The selection
rule minimizes `(largest entry, sum, labeled row)` **among enumerated candidates**,
not among all possible integer representatives.

The full `(2,2)` census covers all `818^2 = 669124` bank profiles. Each observer
has seven distinct fairness masks, so only 49 mask combinations need inspection;
they produce 22 distinct graphs on the six possible allocations. The `(2,1,1)`
census similarly uses observer-mask intersections instead of enumerating all
`818^3` matrices. This is exact factoring of independent observer predicates,
not a sample or an assumption that all agents share rankings.

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
Positive row scaling does not change this type. Goods are never relabeled.

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

The six focused tests passed in 3.435 seconds. The complete 36-test project
suite passed in 28.809 seconds, including the existing constructive path and
independent reconstruction checks. Syntax compilation, whitespace checks and
the advisory source-size check passed. These are local implementation checks;
they do not supply an independent review of the new mathematical argument.

`catalogue(m, max_systems=1000000)` refuses before enumeration if the conservative
upper bound `C(L,m)3^m` exceeds the caller's budget. With the default, four goods
are admitted and five are refused. An explicit larger budget permits larger
work, but no five-good or larger enumeration was completed here. A refusal
returns no partial catalogue and is not evidence of a missing type or a
separation. The graph-census command is deliberately limited to at most four
goods. There is no claimed optimum bank size, five-final proof, large-domain
census, general connectivity result, source integration or publication.
