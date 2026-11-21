# Interior omissions: parity certificates and exact completion

Sorrel, 21 November 2026. **The infinite long-frontier problem remains open.**
The target is 152+11340t on T(227+7560t,67+7560t,11+7560t), t>=0.
The full-prefix obstruction does not exclude arbitrary interior omissions.
This note gives a different, exact obstruction allowing interior holes, and a
bounded exhaustive method for arbitrary specified omissions. A complete finite
census now reports h(T(227,67,11))<=151, below the proposed target 152;
independent review is pending. This does not prove the requested infinite
structural obstruction. Neither a passed
parity test nor a failed construction is a homometric-pair verdict.
Priority remains provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

## What was already known

[BEYOND_REFLECTIONS.md](BEYOND_REFLECTIONS.md) supplies the full-partition
residue lemma. All seven full prefixes large enough for this frontier fail it.
[UNRESTRICTED_PATH_TRANSFER.md](UNRESTRICTED_PATH_TRANSFER.md) already classifies
all reflection-antisymmetric central-path transfers, including arbitrary tail
words. The preserved Rook interior-transfer contribution and Tern's
`RATIO_51_33_10.md` and `FIXED_DIFFERENCE_FAMILY.md` were inspected too. The
latter constructs T(c+76,c+56,c), not the present differences 216 and 56.
None of those finished cases is reopened or claimed here.

## A distance-union obstruction, with an exact converse for parity

Fix any finite metric space and an even retained set R of size 2m. Distances
are always measured in the original space, including across omitted vertices.
For each positive distance d, let G_d join the unordered pairs in R at d.
Write e_d for its edge count and a_d(v) for its vertex degrees.
If A,B partition R into equally sized homometric sets, then

    sum_(v in A) a_d(v) = e_d                         (1)

for every d. Indeed the left side is 2e_d(A)+e_d(A,B), while the right side is
e_d(A)+e_d(B)+e_d(A,B). This proves both directions of the integer equation.

For a set D of distances, let G_D be their edge-disjoint union. If every
vertex of G_D has degree congruent to epsilon modulo two, (1) implies

    |E(G_D)| = epsilon*m (mod 2).                    (2)

Violation excludes **every colouring of this retained set**, not one template.
Moreover, these are all obstructions to the *parity relaxation*: its binary
system a_d dot x=e_d, together with sum x=m modulo two, is inconsistent iff
some D and epsilon violate (2). To prove the converse, eliminate over F_2.
An inconsistent row is a sum of distance rows and possibly the cardinality
row with zero left side and right side one. It says precisely that the
selected distance rows have constant degree parity epsilon and violate (2).
Conversely any such selection sums to that inconsistent row. Consistent rows
can be back-substituted. This is a parity equivalence, not an existence theorem
for the integer equations or exact cardinality.

`parity_basis` retains the row combination. `verify_certificate` separately
recounts its actual selected edges and checks constant degree parity.

## An infinite interior-hole obstruction

**Theorem.** Let g>=5 and k_1,k_2,k_3>=0 be integers, with g*(k_1+k_2+k_3)
even. On the tripod with arm lengths L_i=g*k_i+3, no target-sized homometric pair can omit exactly the
penultimate vertices of any two distinct arms.

Put K=k_1+k_2+k_3. The retained order is gK+8 and its half is m=gK/2+4,
which is exactly floor((1+sum L_i)/2)-1. Select the distances d=2 modulo g.
On the full tree, every vertex has degree K+1 modulo two. Here is an explicit
count, including the centre and all endpoints. For 1<=j<=L_i, write
j=qg+s, 1<=s<=g. Same-arm neighbours plus the centre have count

    (q+[s>=3]) + (k_i-q+[s=1]) + [s=2] = k_i+1.

Each other arm contributes k_l plus an indicator determined only by s and
the common terminal residue 3. Those two indicators are identical and cancel
modulo two. At the centre the count is sum(k_i+1)=K+3, of the same parity.
All displayed counts use actual original-tree distances.

The full selected edge count is

    (K+3) + sum_i ((k_i+1)+g*k_i*(k_i+1)/2)
      + sum_(i<j) (g*k_i*k_j+3*k_i+3*k_j+1)
    = 8K+9+g*K*(K+1)/2.                              (3)

The terms count centre, within-arm, and between-arm edges respectively.
For a between-arm edge, the exceptional residue pair in {1,2,3} whose sum
is 2 modulo g is only (1,1); g>=5 ensures there is no other such pair.

A penultimate vertex has depth g*k_i+2. Its selected neighbours are exactly
the centre and **every depth divisible by g on every arm**. Two penultimate
vertices therefore have identical neighbourhoods and are not adjacent.
Deleting them subtracts 2(K+1) edges and preserves each remaining degree
parity. The retained selected graph has

    6K+7+g*K*(K+1)/2                                 (4)

edges. Subtracting the required parity representative gives the exact identity

    [6K+7+g*K*(K+1)/2] - (K+1)*[gK/2+4] = 2K+3.

This is odd, contradicting (2) for every permitted colouring and every k_i.
For even g the edge count is odd and the required count even; the identity
also handles odd g with even K, when those individual parities may reverse.

For the frontier, g=8 and (k_1,k_2,k_3)=(28+945t,8+945t,1+945t).
This excludes all three pairs of penultimate omissions for every t>=0.
At t=0 the retained selected graph has 5853 edges, every degree even and
m=152. These are genuine interior holes, not trimmed prefixes. The theorem
does **not** forbid moving either hole elsewhere, nor prove the requested
upper bound over all pairs of the original tree.

The lower bound g>=5 cannot simply be removed. At g=4, T(7,3,3) has a
size-six pair with exactly those omissions, (1,6) and (2,2): take A to be
long-arm depths 1,2,3,4,5,7; take B to be the centre, middle-arm depths 1,3,
and short-arm depths 1,2,3. Their common profile at distances 1 through 6 is
(4,4,3,2,1,1). The independent graph counter checks this positive boundary.

## Complete bounded search on a specified retained set

`complete_support` first solves the parity system above. If it is consistent,
it fixes the first vertex outside A (complementation permits this), expresses
all remaining bits in terms of the free columns, and enumerates every such
assignment in Gray order. It checks exact cardinality and every *integer*
equation (1). These conditions are necessary and sufficient, so a completed
negative result excludes every pair on that support. A positive result emits
both sets and passes them through the existing full-distance checker.

There is also a direct bipartition prefilter. Let E be the number
of retained even-depth vertices. If A has x and B has y such vertices,
equality of the odd-distance counts gives (x-y)(m-x-y)=0. Since x+y=E,
E must be even or equal to m. An odd E unequal to m excludes that support
before elimination. This uses integer counts, not an experimental heuristic.

This finite method has a provable barrier on the long frontier. With two
omissions it has a+b+c-1 variables, at most a+b distance rows, one cardinality
row and one complement-fixing row. A consistent system therefore has at least
c-3 = 8+7560t free bits. At t=1 that already means at least 7568 bits.
Thus completing the t=0 computation cannot be promoted to an infinite proof
by simply increasing the search cap; a different structural argument is needed.

The cost is exponential in the parity nullity. A size or nullity limit is
explicitly inconclusive, never an obstruction. No random trials, external
solver, dependencies, or default-selector changes are involved. To conclude
anything about *all* pairs, all eligible omissions (including fewer omissions
for larger pairs) must be covered; one support is not enough.

For even-order trees, `--census A B C` checks the empty omission set and
every two-vertex omission set. These exhaust all possible supports of pairs
at least as large as half-minus-one. It stops if it finds a witness. Otherwise
it records every inconclusive support; an all-pairs upper bound is emitted
only when every support was proved impossible. The result concerns the one
supplied finite tree and never asserts an infinite family.

## Reproduce

From the repository root, with Python 3.10+ and its standard library:

```sh
python3 projects/almost-halving-three-branches/long_frontier.py --penultimate 0
python3 projects/almost-halving-three-branches/long_frontier.py --penultimate 1000000 --arms 1 3
python3 projects/almost-halving-three-branches/long_frontier.py --solve 227 67 11 --omit 1 226 --omit 3 10
python3 projects/almost-halving-three-branches/long_frontier.py --solve 5 4 2 --omit 1 1 --omit 1 2 > /tmp/interior-pair.json
python3 projects/almost-halving-three-branches/long_frontier.py --check /tmp/interior-pair.json
python3 projects/almost-halving-three-branches/long_frontier.py --census 227 67 11 --max-free 20
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_long_frontier.py
```

The symbolic commands allocate no tree. The third emits a distance-union
certificate. Save it and use `--verify-certificate FILE` to recount it. The
fourth emits a size-five pair on unequal arms with two interior omissions;
the fifth checks its complete distance multisets. Tests independently build
original trees and use breadth-first distances, exhaust small retained sets,
check fresh unequal witnesses, and reject altered pairs and certificates.

## Recorded finite obstruction, 21 November 2026

The `--census 227 67 11 --max-free 20` command completed with:

```text
status: finite_all_pairs_bound
all_pairs_upper_bound: 151; target: 152
census_complete: true; infinite_family_proved: false
tested_supports: 46666
bipartition count: 23408
parity certificate: 49
exhaustive parity completion: 23209
inconclusive: 0
```

There are 306 vertices. Disjoint equal-sized pairs of size at least 152
can only have size 153 (no omissions) or size 152 (two omissions). The run
covers the single full support and all C(306,2)=46665 two-hole supports.
Thus the computation gives an upper bound over **every permitted pair**
for this one tree. It does not determine the exact maximum and supplies no
upper bound for t>=1. The infinite-family milestone remains open.

The first run with the default cap 16 correctly reported one inconclusive
support, not a bound: omissions (1,216),(2,56) leave 17 free bits after
complement symmetry. Its separate cap-20 run exhausted 131072 parity
assignments, including 13486 balanced ones, with no valid pair. The complete
cap-20 rerun above then covered it together with all other supports. The
failed cap is retained here rather than relabelled as a negative result.
A separate temporary implementation using precomputed full-tree adjacency
also exhausted all 23257 two-hole supports with same-depth-parity omissions without finding
a pair; this is corroboration, not a replacement for the documented command.
All 49 parity-obstructed supports were separately passed through the verifier.

All 136 project tests passed, including eight tests for this contribution.
The independent breadth-first counter checks fresh unequal witnesses and
the symbolic obstruction on moduli 5, 6, 8 and 10. A 70-vertex positive
control is found by the new solver; its altered equal-sized, disjoint pair
is rejected by the real CLI. Whitespace and the size advisory pass. Ruff
is unavailable. Source integration and non-author review are still required.
