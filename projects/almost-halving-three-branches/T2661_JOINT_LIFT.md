# Integer lifting: a stronger necessary condition, not a colouring

Fern, 23 November 2026. Project `small-after-sum-20261120`;
task `halving-joint-bounded-lift-20261123-linnet`.
[Priority remains provisional](PRIORITY_REFRESH.md).

This is partial progress on the bounded system of
[T2661_JOINT_RESIDUE.md](T2661_JOINT_RESIDUE.md). **Neither hole pair is
proved feasible or impossible over bounded integers.** There is no new
homometric pair and no universal tripod theorem here.

The new result is a complete criterion for which parity branches extend
to solutions modulo four, before bounds on the second bit. In each case
it removes exactly half the parity branches. The predecessor's specific
odd-hole branch cannot lift even without bounds; its even-hole branch
passes this new test. A separate actual-vertex pair counter checks large
allocations without using the sparse shell equations.

## Obtain and reproduce

These files depend on Linnet's contribution `00058a865682afc57a69adb2449f60a77cea69d8`
(run `c4d6bb407010408d947e9ccf3ebf8b3a`), including `t2661_joint_residue.py`,
`t2661_same_parity.py` and `t2661_mod4_aggregate.py`. That prerequisite was
not yet integrated into this room's base. Integrate/review it before this
contribution; these files do not silently vendor or accept its source.
From a public checkout containing both contributions, Python 3.10+ and
only the standard library suffice:

```sh
python3 projects/almost-halving-three-branches/t2661_joint_lift.py --refine --parity odd
python3 projects/almost-halving-three-branches/t2661_joint_lift.py --refine --parity even
python3 projects/almost-halving-three-branches/t2661_joint_lift.py --control
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_t2661_joint_lift.py -v
```

For a prospective integer witness, `--allocation FILE --parity odd` reads
a JSON list of negative counts in the exact class order returned by
`family(1, 'odd')`. It verifies every bound and integer equation, realizes
the vertices, checks the partition, and independently recounts actual pairs.
An invalid allocation exits unsuccessfully. `--k` changes the scale for
refinement/allocation checks; the recorded results below concern **k=1**.

## The branch-independent modulo-four criterion

Write the original integer equations as `A x=b`, with `b=A n/2`, including
balance, anchor and cyclic shell derivatives. Let `u` be any bit vector
satisfying `A u=b (mod 2)`. The unrestricted next bit `v` must satisfy

```
A v = (b-A u)/2 (mod 2).
```

Elimination over the two-element field returns a basis of the left nullspace
of A. For each basis vector lambda, take its entries as ordinary zero/one
integers. Both `lambda A` and `lambda b` are even, because the original
parity system is consistent. Define exact integer equations

```
D_lambda = (lambda A)/2,       d_lambda = (lambda b)/2.
```

Then **u extends modulo four if and only if**

```
A u=b (mod 2),    D_lambda u=d_lambda (mod 2) for every basis lambda.
```

Proof: a finite-field linear system has a solution exactly when its right
side annihilates its left nullspace. Applying that fact to the equation
for v gives `lambda(b-Au)/2 = d_lambda-D_lambda u = 0 (mod 2)`.
The computed nullspace basis is complete: every dependent row supplies a
source bitset with its own distinct newly introduced row index; there are
exactly `row_count-rank` such independent dependencies. This tests every
parity branch, rather than attempting to lift just one vector.

Each divided equation is also an ordinary exact consequence of `A x=b`
for **every integer x**, with or without finite bounds. The checker retains
its source bitset, recomputes the integer row sum, and checks divisibility
before dividing. Rows are stored as coefficient dictionaries, including the long balance
and anchor rows; no dense integer matrix is allocated. Packed bit rows are used only for finite-field elimination.

Actual recorded results for `t=2661`, modulus 2660:

| Holes on arm 1 | Classes | Initial rank | Refined rank | Derived rows | Consistent |
|---|---:|---:|---:|---:|---|
| 19, 263439 | 7999 | 2658 | 2659 | 4 | yes |
| 18, 263438 | 7999 | 2658 | 2659 | 4 | yes |

The affine solution dimensions are therefore 5341 and 5340 respectively:
exactly half the original branches survive. All four derived rows reject
the predecessor's odd-hole bit vector; none rejects its even-hole vector.
These are congruences on allocation counts, **not** distance bins modulo
four, and passing them does not solve the integer equations.

## Tiny bounds and the explicit failed prefix

`--branch --parity even` starts with the predecessor's recorded bit vector,
then follows the deterministic zero-free-variable choices of the new
eliminator. At each step `x=u+2y`, it retains
`0<=y_j<=floor((n_j-u_j)/2)`. Every upper-bound-zero variable is explicitly
fixed to zero in the next parity system. It never treats the 19 singleton
classes as freely liftable.

In the recorded even-hole run, levels 0, 1, 2 and 3 pass. At level 4 the
chosen prefix is rejected, with a checked 1329-row parity dual. Maximum
upper bounds were 100, 50, 25, 12 and 6. This rejects only that selected
prefix (including choices made after the first bit), **not** the even-hole
first branch, other kernel choices, or all colourings. The odd-hole first
branch fails already at the next step. Dual verification reconstructs the
selected equations and checks that all variable coefficients are even
while their right side is odd. A small regression has a rejected prefix
and an independently verified valid allocation in the same system.

## Independent actual pair counter

For each selected set, build the literal arm indicator polynomials F_a.
Same-arm positive distances are coefficients at `L_a+d` of
`F_a(z) z^L_a F_a(z^-1)`. Cross-arm distances are coefficients of `F_a F_b`.
A selected centre contributes the arm depths once. Fold these **actual
positive distances** into the requested bins, after convolution.

The implementation packs polynomial coefficients into fixed-width bytes
and multiplies Python integers. Its radix exceeds the total vertex count;
every individual convolution coefficient is at most that count, so no
coefficient carries into another. This is exact integer arithmetic, without
an FFT or the derivative/anchor formulas. A total-pair identity checks that
no pair was lost. Exhaustive small tests compare it with literal unordered
pairs, including asymmetric lengths and positive-lag orientation.

Real recorded control: the earlier odd-hole mod-4 construction on
T(263439,210219,61203) has 267430 vertices in each disjoint set. This counter
confirmed equal mod-4 histograms but **2659 unequal joint-modulus bins**.
The even-hole control gives the same sizes and number of unequal bins.
The odd run took 5.16 seconds and the even CLI run 6.364 seconds here;
these are observations, not performance guarantees. No new joint witness
is being smuggled in as a positive control.

## Search bounds and the unresolved boundary

Exploratory searches used already installed solvers, without installing a
dependency or making them requirements of the delivered checker. All used
the original sparse `A x=b` equations and integral class counts:

- OR-Tools 9.15.6755, CP-SAT, odd holes: domains
  `max(0,floor(n/2)-r) <= x <= min(n,ceil(n/2)+r)`, floor-midpoint hints,
  seed 123. Radius 2, one worker, 120 seconds: UNKNOWN, 708 branches.
  Radius 10, four workers, 600 seconds, linearization level 0,
  randomized search and centre count fixed to zero: UNKNOWN, 2078 branches.
  Centre fixation loses no feasibility because colour complementation
  exchanges its two possible values.
- SciPy 1.18.0/HiGHS, even holes: zero objective, all variables integral,
  full `[0,n]` bounds, 120-second limit: no incumbent. This is inconclusive.

A Z3 4.16.0 trial on the even-hole midpoint-only domains, including the
four derived exact equations, also returned unknown (requested 120-second
timeout; observed solver check 423.33 seconds). It supplies no certificate.

A failed restricted domain is not a proof about the full bounds. Neither
UNKNOWN nor an absent incumbent is an infeasibility certificate. A sparse
unit-pivot experiment on the odd system eliminated 2657 variables but left
five dense rows with large coefficients; it was not promoted to a solver
or a mathematical obstruction.

What remains is an exact bounded solution after retaining the surviving
5340-dimensional parity freedom, or a verified contradiction valid across
all those branches and all allowed class counts. The 19 tiny classes and
all upper bounds must remain in that problem. A larger timeout alone is
not the next mathematical result. The full homometry milestone remains open.
