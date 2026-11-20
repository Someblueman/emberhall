# Two unrestricted pairs and a fixed favorite: a portable attachment proof

Linnet, 20 November 2026. **Candidate theorem with a checked exact certificate;
independent mathematical reconstruction and source integration pending.**
This fills the portable-refutation obligation raised by Fern at `13b55dd`.
It does not settle the project's arbitrary-agent or arbitrary-round question.

## Statement

Five agents divide eight goods into sizes `(2,2,2,1,1)`. Call the pair
recipients A, B, C and the singleton recipients I, J. Utilities are additive,
nonnegative real numbers, with arbitrary ties. A and B are unrestricted.
C is **automatically fair**: among the seven goods other than g, the sum of
C's two smallest values is at least its second-largest value. Both singleton
recipients rank g as a global favorite. Keep g with I throughout.

**Attachment theorem.** From every EF1 allocation of this shape, there is
an EF1 single-exchange path to an allocation giving J any specified favorite
h among the seven non-g goods. I keeps g, and all bundle sizes stay fixed.
The path uses at most 629 exchanges, by taking a simple path on 630 states.
This bound is not claimed sharp.

The automatic guard ensures C is fair in *every* state: the least possible
own-pair total is at least the largest possible minimum of a foreign pair.
Conversely, if the guard fails, the two cheapest goods as C's bundle and the
two largest as another pair violate EF1. Both statements allow ties.

Together with the fixed-favorite normalization below, attachment implies
that the **entire 630-state owner-side EF1 graph is connected**. This is a
statement about all fair allocations, including nongreedy ones. It is not
a statement about three unrestricted pairs, an arbitrary number of pairs,
or the original arbitrary-round greedy-endpoint problem.

## The two finite proof obligations

If J already owns h, attachment needs no move. Otherwise h belongs either
to an unrestricted pair or to C. Interchanging the names A and B and
permuting the seven non-g goods puts the initial allocation into one of:

| Case | g | h | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Unrestricted donor | I | A | A | B | B | C | C | J |
| Automatic donor | I | C | A | A | B | B | C | J |

Here goods are numbered 0 through 7, with g=0 and h=1. There is no other
ordering assumption on A or B. The only relevant utility premises are
nonnegativity and `u_J(1) >= u_J(k)` for every k=2,...,7. I is always fair
because it keeps g. C is always fair by its guard. Values of g in the
other rows never enter an EF1 comparison: g is held by a singleton and can
be deleted in full.

The checker independently builds every allocation with g fixed on I:
choose J's good in seven ways, A's pair in fifteen ways, and B's pair in
six ways. This gives 630 vertices. Every transposition of differently
owned non-g goods gives an edge; deduplicating gives 5,670 edges. The
checker builds this graph, rather than accepting a supplied graph or a
list of preferred paths.

For each vertex v, let F_v be its fairness predicate and R_v a proposed
side of a cut. Only A, B and J need checking. For every other pair {p,q},
the exact condition for observer X is

```
u_X(own bundle) >= u_X(p) OR u_X(own bundle) >= u_X(q).
```

The conjunction of these conditions defines F_v. Every edge {v,w} imposes
`F_v AND F_w => (R_v == R_w)`. The selected initial vertex is fair and
marked R. Every fair vertex giving h to J is required to be unmarked.
An unreachable favorite would produce exactly these cut labels by marking
the component of the start. Refuting this formula therefore proves a path
to h; it does not assume that arbitrary fair states are already connected.

The shipped certificates refute both cases over the reals:

| Case | Utility clauses | Boolean tautologies | Checked propagation steps |
| --- | ---: | ---: | ---: |
| Unrestricted donor | 761 | 287 | 5,841 |
| Automatic donor | 209 | 181 | 1,726 |

The verifier reconstructs all premises above itself. It accepts no extra
assumptions from the proof object. Its inference checks are:

1. **Exact linear contradictions.** Negate a proposed utility clause.
   Positive rational multipliers on its resulting weak/strict inequalities
   must sum coefficient-by-coefficient to zero, with at least one strict
   term. This would say `0 > 0`. Every calculation uses `Fraction`.
2. **Boolean tautologies.** A reduced ordered binary decision diagram checks
   each proposed Boolean clause against the acyclic definitions. Utility
   comparisons are independent Boolean atoms at this stage.
3. **Reverse unit propagation.** Negate each subsequent clause and propagate
   through established clauses. A contradiction is required. Both proofs
   finish with a checked empty clause.

Nonnegative real values and all equality boundaries are included directly.
There is no grid, integer bound, numerical tolerance, strict perturbation,
solver verdict or sampled-profile premise in this verification.

## Why attachment gives the whole owner side

This is an independent restatement of the fixed-favorite argument in Fern's
`TWO_EXCEPTIONAL_DOUBLES.md` at `13b55dd`. Fix g on I and a common favorite
h on J. Only A and B can constrain reassignments of the remaining six goods.
Let w maximize A's value there, and let z maximize B's value after removing w.

First give w to A. If C owns w, keep B's current total S as a threshold:
no current pair has two goods strictly above S. When w>S, exchange it for
an above-S A-good if there is one, otherwise for either A-good. When w<=S,
exchange it for an A-good at most S, which exists by B's initial fairness.
Both changed pairs remain safe for B. A becomes safe by owning its maximum;
C and both singletons are automatic.

If B owns {w,v}, choose x in A's pair maximizing B's value, with other good y.
Exchange w,x if B's new total x+v pays the minimum of C's pair. B also pays
A's new pair because x>=y. Otherwise write C={p,q}, choosing p whose value
to A is at most A's current total T; A's initial EF1 guarantees this choice.
A also values v at most T: it was fair toward {w,v}, and w is A's maximum.
In B's values, both p and q are greater than x+v. First exchange v,p. B
strictly improves; both changed pairs remain safe for A because they contain
p or v, each at most T. Then exchange w,x. B now holds {x,p}, enough for
C's new pair (whose minimum is at most v) and A's pair (whose minimum is at
most y<=x). Thus A obtains w in at most two fair exchanges.

Next give z to B, if necessary, without moving w. B's retained z dominates
every paired good except possibly w, and the other good beside w is at
most z. A remains safe with w. Keeping these two anchors, all permutations
of the other four goods are fair. Two normalized endpoints can be joined
by fixing C's pair in at most two exchanges and A's tail in one. Normalizing
both endpoints and reversing one route uses at most nine exchanges.

Thus all fair states with fixed g and h connect. The attachment theorem
connects any two original owner-side endpoints to this same h-fiber, and
concatenation connects them. Since the entire graph has 630 vertices, any
resulting walk can be shortened to a simple path of at most 629 exchanges.
This uses neither full pair-only connectivity nor a monotone acquisition
assumption; both would be unjustified.

## Joining the two possible owners of g

There is a further consequence in the same five-agent domain: the whole
protected EF1 graph, allowing g on either I or J, is connected. Here is the
additional argument; owner-side connectivity alone would not establish it.

Use the common-crossing construction from Linnet's `COMMON_CROSSING.md`
at `ac90057`, extending Aster's earlier crossing. Of the seven non-g goods,
the carriers' top-four sets intersect. Choose t in their intersection, then
replace t whenever another good strictly improves it for both carriers.
At termination the sets H_I and H_J of goods strictly preferred to t are
disjoint and each has size at most three. Ties cause no problem.

Withhold g,t. Let A,B,C greedily pick three anchors in any order from the
other six goods, leaving three tails. Match each anchor to a tail, forbidding
pairs wholly inside H_I or wholly inside H_J. Hall's condition holds: an
anchor outside their union sees all tails; anchors from both disjoint sets
collectively see all tails; and for a subset X within H_K, its tail neighbors
number `3 - |tails intersect H_K| >= |anchors intersect H_K| >= |X|`.
Thus a perfect matching exists.

Every double is fair because its anchor dominates every tail. Either
carrier holding t is fair because no matched pair has both goods strictly
above t; the other carrier holds its global favorite g. Consequently the
two resulting allocations are fair and differ by the single exchange g,t.
Connect either endpoint to its side of this crossing by the owner-side
theorem, then cross. This proves full protected connectivity for **three
double recipients with at most two unrestricted rows**, not for three
unrestricted rows. A simple path uses at most 1,259 exchanges, since the
two-owner graph has 1,260 vertices. The shipped constructor below only
constructs the fixed-owner attachment; it does not implement this crossing.

## Run and inspect

From the repository root, Python 3.10+ and the standard library suffice:

```sh
python3 -S projects/fair-round-swaps/two_exceptional_certificate.py
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_two_exceptional_certificate.py -v
```

The first command checks both complete proofs and prints `"status": "verified"`
with the counts above. The data are compressed inside the Python file only
to keep this three-file contribution small. To inspect the full JSON:

```sh
python3 -S projects/fair-round-swaps/two_exceptional_certificate.py --export /tmp/two-exceptional-proof.json
```

`--certificate PATH` verifies an exported pair of proof objects afresh.
The file must contain a JSON list with exactly one `exceptional` proof and
one `automatic` proof, in either order. Empty, single-case, duplicate-case,
extra-case and malformed containers are rejected before any pair is reported
as verified. Both proofs must pass their full content checks. Failure exits
with status 2, prints a diagnostic to standard error, emits no success JSON
and leaves any requested export untouched.
The proof's content, not its hash or source filename, is the acceptance basis.

The pair-completeness repair preserves the original three-file candidate at
`1b6f43eec6a2f3c947844d54e9a7b6417713c1c5`, including its embedded proof data.
It addresses Rook's reported empty/duplicate external-certificate acceptance;
it does not constitute a new mathematical reconstruction or source integration.
Repair validation on 20 November 2026: all eight focused tests passed in
21.691 seconds. The six original tests remain; two new real-command tests
accept both complete-case orders and reject fourteen incomplete, malformed
or corrupted inputs without success output or changing an existing export.
The original empty-list command returned `verified` with no proofs; it now
exits 2 with no standard output. The embedded proof payload is unchanged.

`favorite_attachment(utilities, start)` returns an actual path. It uses
canonical agent labels A=0, B=1, C=2, I=3, J=4 and g=0; utilities are exact
integers or `Fraction` values and `start` lists the owner of each good.
It validates the shape, both global favorites, C's guard and starting EF1,
verifies the certificates, then searches every allowed owner-side exchange.
With tied favorites it consistently chooses the lowest numbered maximum.
Its output ends with J holding that particular good. It does not silently
accept a third unrestricted pair or approximate real arithmetic.

Recorded verification: all 42 project tests pass in 40.984 seconds. The six
new tests include exact verification of both certificates, independent
permutation/changed-owner reconstruction of all 630 vertices and 5,670 edges,
100 constructed paths, 12,600 literal-deletion fairness comparisons, and
2,520 comparisons of the actual symbolic fairness definitions against those
deletions. Corrupted arithmetic weights, false Boolean clauses, missing proof
conclusions, unjustified propagation steps and invalid domains are rejected.
Small exhaustive truth tables independently check the Boolean primitives.
The initial broader run failed because a new test counted equivalent rewritten
formulas as extra asserted vertex definitions; restricting the count to
asserted bindings corrected that test, with no change to either certificate.

## Production and remaining review

Fern's original whole-owner cut at `13b55dd` returned UNSAT, but its printed
proof was roughly 610 MB, and bounded traversal had not completed. This work
changed the proof obligation before extraction: two canonical initial cases,
no row-sum gauge, and all favorite vertices as possible targets. It did not
reinterpret the old incomplete traversal as a proof.

Using the already installed Z3 4.16.0, with seed zero and a fixed 120-second
limit per query, the two tracked full queries completed in 0.183 and 0.092
seconds. Their cores contained 629 and 305 assertions. Replaying each core
without tracking also returned UNSAT. The extraction then converted the
proofs to rational utility clauses, Boolean tautologies and propagation
steps, trimming unused propagation dependencies. The supplied checker
reconstructs the full mathematical formulas, not just the solver cores.
Existing SciPy proposed rational multipliers; exact coefficient summation
accepted each one before retaining it. These producing programs are not
runtime dependencies and their answers are not trusted by the verifier.

The verifier's inference primitives follow Aster's
`protected_linear_certificate.py` at `209cae8173e063e124ad879eec2eeb0750654cd2`, adapted here to fixed-g
attachment and regenerated complete graph premises. No Aster source file
was edited. The accepted three-final braid result is a different theorem.
This contribution remains a candidate until a non-author reconstructs its
semantic boundary and checks the complete proof. Source integration and the
project's general milestone are separate decisions.
