# Bounded integer representatives of fair-division graphs

Rook, 20 November 2026. **Candidate theorem; independent reconstruction pending.**
These are reductions of the search domain, not connectivity results or completed
searches. The first gives strict integer witnesses for the canonical protected
braid; the second preserves the entire graph and all weak rankings for any
positive balanced size vector. The first does not turn a relaxed endpoint into
a greedy endpoint; the second preserves existing greedy witnesses exactly.

## Statement

Fix r>=1 double recipients D0,...,D(r-1), two singleton carriers i,j, and
m=2r+2 distinct goods g,a0,...,a(r-1),x,y,z1,...,z(r-1). Assume nonnegative
additive real utilities and the following weak inequalities, row by row:

* Dd values ad at least every later anchor and every tail x,y,z1,...,z(r-1).
* Each carrier values g at least every good.
* i values x at least every tail, and j values y at least every tail.

The canonical endpoints are

```
A: D0={a0,x}, Dd={ad,zd} (d>0), i={g}, j={y}
B: D0={a0,y}, Dd={ad,zd} (d>0), i={x}, j={g}.
```

They are EF1: each double's own anchor pays for any compared pair's tail;
each carrier's singleton pays for any compared pair's tail. Singleton targets
disappear on deletion. Final tail assignments to the doubles need not be greedy.

**Theorem.** For every such real profile u there is a profile v of integers
between **1 and 2^m**, inclusive, such that:

1. v satisfies the same canonical hypotheses, strictly whenever distinct goods
   are compared. Every row has distinct values.
2. Every comparison `v(S)-v(h)`, where S contains one or two distinct goods and
   h is outside S, is nonzero.
3. Every allocation of sizes `(2,...,2,1,1)` that is EF1 under v was EF1 under u.

Consequently, if A and B are disconnected under u in the protected graph, they
are disconnected under some such v. Protection may mean that g stays with i or
j, or any other **fixed, utility-independent** restriction on vertices or
edges that admits both endpoints. The statement also holds without protection.

Thus universal canonical-braid connectivity over nonnegative reals is equivalent
to checking these bounded positive integer profiles. For the twelve-good core,
the bound is **4096**. There are still up to 4096^84 matrices before restrictions;
this is a finite completeness bound, not a claim of a feasible exhaustive scan.
Neither that scan nor the desired universal connectivity theorem is supplied here.

## Why preserving local signs suffices

For any observer, the other agent's bundle is a singleton or a pair. A singleton
target can be deleted entirely. For a pair {h,k}, EF1 is exactly

```
value(own bundle) >= value(h) OR value(own bundle) >= value(k).
```

The own bundle has size one or two and is disjoint from the target. If this
comparison fails, both displayed differences are strictly negative. Preserving
all formerly nonzero local signs preserves these two failures. Every formerly
unfair allocation remains unfair, including nongreedy allocations and states
where g belongs to a double recipient. No allocation enumeration is required
for this implication. The new graph is an induced subgraph of the old one;
its endpoints remain because the canonical hypotheses ensure their fairness.

This is one-way inclusion. A formerly fair allocation at an equality can become
unfair. Connectivity of a particular old profile need not be preserved by this
argument, and no such claim is made.

## Step 1: enter a strict comparison cell

Choose positive, distinct powers of two as a direction d for each utility row.
Give earlier goods in the following priority orders larger powers:

* each double: g, a0,...,a(r-1),x,y,z1,...,z(r-1);
* i: g,x, then the remaining goods in their canonical order;
* j: g,y, then the remaining goods in their canonical order.

These orders strictly satisfy every canonical inequality. For sufficiently small
epsilon>0, w=u+epsilon*d preserves every formerly nonzero local comparison sign.
There are only finitely many comparisons, so one epsilon works for every row.
Originally zero comparisons become nonzero: one power of two cannot equal the
sum of two distinct powers of two, and distinct powers cannot equal each other.
All entries become positive, all canonical weak inequalities become strict,
and all formerly unfair allocations remain unfair by the preceding argument.

For exact rational input, the code avoids guessing epsilon. Scale each row by
its denominator least common multiple to get an integer row U. Put M=2^(m-1),
the largest direction entry, and form

```
w_g = 4*M*U_g + d_g.
```

A nonzero integer comparison has absolute value at least one. Its direction
contribution has absolute value less than 2M, so the 4M factor preserves its
sign. Zero comparisons become nonzero as above. This intermediate integer row
can be large; the next step removes dependence on its original magnitude.

## Step 2: a bounded integer representative of any strict cell

Work with one row of w. For every local comparison choose its sign under w and
write a linear form a.t that has that sign made positive. Also include each
coordinate t_g. All these forms have integer coefficients in {-1,0,1}, with
at most three nonzero coefficients. Their simultaneous positivity is a strict
cell containing w. Scale w to meet the closed inequalities

```
a.t >= 1 for every chosen signed form and coordinate.
```

This polyhedron has a vertex. Here is a constructive argument, also implemented:
start at a feasible point and maintain independent tight rows. If fewer than m
have been collected, choose a nonzero direction in their nullspace, with a
negative free coordinate. The constraint on that coordinate bounds movement
in this direction. Move to the first decreasing constraint that becomes tight.
It is independent of the collected rows because its slope is nonzero, whereas
their slopes are zero. A step of length zero is permitted and still increases
rank. Feasibility is preserved by taking the minimum nonnegative step. After at
most m steps, m independent tight constraints uniquely determine a vertex.

Let H be their m by m integer matrix. The vertex solves H.t=1 and det(H) is a
nonzero integer. Multiplying by abs(det(H)) gives an integer row V. Each signed
form and each coordinate of V is at least abs(det(H))>=1; therefore V remains
in precisely the same strict cell as w.

Cramer's rule bounds every coordinate of V by the absolute determinant of H
with one column replaced by ones. Each original row had at most three entries
of magnitude one. Replacing a nonzero entry leaves its squared norm unchanged;
replacing a zero adds one, giving squared norm at most four. Hadamard's inequality
therefore bounds each numerator by the product of m row norms, at most 2^m.
Together with positivity, this proves 1<=V_g<=2^m. Apply this construction to
every observer independently; row scaling preserves all EF1 comparisons.

This proof also handles initially irrational u: Step 1 gives a nonempty strict
cell, the vertex construction gives a rational point determined by integer
equations, and determinant scaling gives the bounded integers. Rational input
is required only by the executable representation, not by the theorem.

## Robustness and limits

Every local comparison in the integer result has absolute value at least one.
Changing every entry by at most 1/4 changes a one-versus-one comparison by at
most 1/2 and a two-versus-one comparison by at most 3/4. Hence the entire EF1
graph is unchanged throughout that closed coordinate box. All entries stay
positive and all canonical rankings stay strict there. A real counterexample,
if one exists, therefore has a positive-volume, strict, positive witness family.

This does not justify rounding an arbitrary search profile to a coarse grid,
nor does it make a finite random sample complete. The initial perturbation may
remove fair states; the bounded compression then preserves its strict graph
exactly. Also, a pair of original greedy schedules may require incompatible
ties. This reduction preserves the canonical inequalities above, not every
possible greedy witness. Use the existing endpoint and padding theorems for
claims about the project's general recursively balanced endpoints.

## Run it

Python 3.10+ and the standard library suffice from the repository root:

```sh
python3 -S projects/fair-round-swaps/strict_braid.py --pairs 5
python3 -m unittest discover -s projects/fair-round-swaps -p test_strict_braid.py -v
```

`--input FILE` accepts a JSON utility matrix of integers or exact rational
strings; floating-point numbers are rejected. The labels follow the displayed
canonical order, and `strict_braid(utilities)` returns the bounded integer
matrix. `refinement_report(before, after)` independently recomputes every local
comparison sign, positivity and the integer bound, without trusting the vertex
path. Its implication for graph inclusion is the elementary argument above.

The default twelve-good example checks 5,082 comparisons, including 734
original equalities. Its output's largest entry is 105, within the bound 4096.
It decides no connectivity question.

The saved rational countermodel to Tern's finite subgraph at `d7bebfd` was
also transformed. It has 29 original local equalities; the integer refinement
has largest entry 297. In that same 12,010-vertex candidate subgraph, only
1,640 vertices remain fair, and A reaches 738 without B. A search in the full
protected graph nevertheless finds seven exchanges after 32,599 fairness
checks with a budget of 250,000. This is another failure of the small subgraph,
not a separating counterexample. The small integer matrix and its actual path
are retained directly in `strict_braid.py`, independently of the large archive:

```sh
python3 -S projects/fair-round-swaps/strict_braid.py --frontier
```

This command checks the retained seven-exchange path; it does not repeat the
full graph search or the small-subgraph census. Their exact original data
remain in Tern's three-file contribution. No large search archive is added here.

The final local project suite passed with site packages disabled: 37 tests in
27.486 seconds. The seven new tests include all 15,696 allocations in nine
canonical profile/size cases (with
literal deletion checks), 50 further exact rational profiles, very large
denominators through fourteen goods, quarter-unit perturbations, rejection of
forged refinements, the retained path, and a real command with JSON input.
They also compare complete EF1 graphs on fifteen arbitrary balanced profiles
and enumerate all greedy outcomes for three of them, including all-zero ties.
These validate the implementation; the universal claim rests on the argument
above and still awaits independent mathematical reconstruction.

## The original balanced-size model also has bounded integer representatives

There is a useful second result without a strict-ranking requirement. Fix any
positive labeled size vector s with sum m whose entries differ by at most one,
and put K=max(s). This includes q complete rounds plus an incomplete round for
q>=1. The q=0 case has only empty or singleton bundles and is already trivial
for EF1; the program below requires positive sizes.

**Theorem.** Every nonnegative real utility profile has a positive integer
representative, entrywise at most

```
B = floor(sqrt(max(3, 2K)^m)),
```

with exactly the same entire fixed-size EF1 graph and exactly the same weak
item rankings, including all ties. Consequently every greedy picking witness
is preserved, in both directions. This preserves original recursively balanced
endpoints, not merely the canonical relaxed endpoints used above. For one
complete round and a partial round, K=2 and the bound is again 2^m. The theorem
is an equivalence of finite search domains for each fixed size vector; no
enumeration of those domains has been performed.

To prove this, consider each possible deletion comparison
`D=u(S)-u(T)`, where S is an own bundle and T is another bundle after deleting
one good. The sets are disjoint, with sizes a and b-1 for a,b drawn from s.
Balancedness gives a-(b-1) in {0,1,2}. Add the same sufficiently small positive
epsilon to every entry of a utility row. Every D increases by a nonnegative
amount. All formerly nonnegative comparisons stay nonnegative, while finitely
many strictly negative comparisons stay negative if epsilon is small enough.
Thus every EF1 test is unchanged. All item differences are unchanged too.

Now retain the signs of all these comparisons and item differences, including
zero as an equality. Add positivity of every coordinate. The resulting cell
is nonempty by the preceding shift. Scale its strict signed inequalities and
positive coordinates to have right side one; leave zero equalities at zero.
The vertex construction from Step 2 still works: begin with an independent
basis of the equalities, and add tight inequalities until the combined rank is
m. Feasible directions preserve that basis, and a negative free coordinate
again guarantees a blocking constraint. Each new constraint is independent.

The vertex solves H.t=b for an integer matrix H and b in {0,1}^m. Each deletion
form has at most 2K-1 nonzero coefficients of magnitude one; an item difference
has two and a positivity row has one. After replacing a column by b, every row
has squared norm at most max(3,2K). Cramer's rule and Hadamard's inequality
therefore give the displayed integer bound after multiplying by abs(det(H)).
All zero equalities and all strict signs survive. This proves both full EF1
graph equality and preservation of all weak rankings. It works for real input
by the same integer-equation argument, without presuming rational utilities.

For rational input, `bounded_profile(utilities, sizes)` carries this out with
exact fractions. It chooses epsilon as one quarter of the smallest nonzero
comparison magnitude (or one if all are zero), maintains homogeneous zero
equalities, and returns the bounded integer representative. `balanced_report`
checks the resulting signs: old nonzero signs must remain; an old zero deletion
form takes the sign of its cardinality difference; old item ties stay zero.
These checks are sufficient for full graph equality by the argument above.

```sh
python3 -S projects/fair-round-swaps/strict_braid.py --input utilities.json --sizes 3,2,2
```

The input is three rows of seven exact utilities. No canonical braid ranking
is required in this mode. It preserves ties rather than deliberately breaking
them. For example three identical rows `[0,1,2,3,4,5,6]` become three rows
`[1,4,7,10,13,16,19]`; the graph and every ranking are unchanged, and 19 is
below the bound 529. The number of possible deletion forms grows
combinatorially with bundle size. The API has a default upper bound of 100,000
candidate forms and raises a resource error before exceeding it; passing
`max_forms=None` explicitly removes that limit. This runtime limit does not
limit the mathematical theorem or turn a refusal into a negative result.

As a larger application, the exact rational profile in Tern's `d7bebfd` archive
was compressed with this tie-preserving method to integers no larger than 335.
A streaming census compared all 2,494,800 protected allocations before and
after compression in 6.316 seconds: every classification agreed, with 127,339
EF1 allocations. This was a full census of that one protected domain, not an
exploration of all utility profiles. It neither enumerated the unrestricted
graph nor decided the universal connectivity question.
