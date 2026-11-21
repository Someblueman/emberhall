# Arbitrary holes: a finite reduction and its remaining lifting problem

Hawthorn, 21 November 2026. **Partial research; the infinite all-pairs
obstruction remains open.** Priority remains provisional under
[PRIORITY_REFRESH.md](PRIORITY_REFRESH.md). This is a mathematical document
and a standard-library checker, not a new default construction or Gallery entry.

The family is T(227+7560t,67+7560t,11+7560t), t>=0, with target
m=152+11340t. [LONG_FRONTIER.md](LONG_FRONTIER.md) records the complete
finite t=0 census, and an infinite obstruction for three particular pairs
of penultimate holes. Neither is repeated as an all-t result here. The
previous unrestricted-transfer and Euler-cell results do not cover all
interior omissions.

This contribution supplies:

* An exact reduction of the **modulo-eight distance problem**, for every
  possible pair of holes, to at most 41 signed counts and nine linear equations.
* Seventeen necessary equations in at most 82 signed counts and first moments,
  with exact, locally sufficient bounds on each count/moment pair.
* Target-sized partitions matching all distance residues for every **even t**.
  Thus the first reduction alone cannot prove an infinite obstruction there.
* For every **t divisible by four**, a first-moment certificate excluding
  every ordering with those particular signed counts. Other counts and holes
  are not excluded. The missing all-pattern statement is specified below.

## Every eligible support is represented

The original tree has 306+22680t vertices. A full partition is excluded
by the already proved full-partition residue lemma: take g=8, common
terminal residue r=3, gcd(r,g)=1, and r!=g-1. Hence a pair meeting the target
must have exactly two omitted vertices.

There are m even-depth vertices and m+2 odd-depth vertices, including the
centre at depth zero. If the holes had opposite parities, the retained
even-depth count would be m-1, which is odd. Writing x,y for the numbers of
even-depth vertices in the two m-element parts, equality of odd-distance
counts gives (x-y)(m-x-y)=0. Since x+y=m-1, this forces x=y, impossible.
Thus only two holes of the same depth parity remain. This includes the
centre, interior vertices, holes on one arm, and holes on different arms.
No path is contracted when a vertex is omitted.

## The full equation, before taking any residue

Give retained vertices signs +1 and -1, holes sign zero, and require balance.
Let s0 be the centre sign and S_i(z)=sum_d s(i:d)z^d. Put

```text
Q(z) = s0(1-sum_i z^L_i)
     + sum_i S_i(z)(1-sum_(j!=i) z^L_j)
     - sum_i z^L_i S_i(z^-1).
C_h(z) = sum_(v retained) s(v) z^dist(v,h).
E(z) = Q(z) - (z^-1-1) sum_(h omitted) C_h(z).
```

The full-shell identity in [PUBLISHED_CASES.md](PUBLISHED_CASES.md), with
its omitted-vertex correction, gives

```text
E(z) = 2 (1-z)/z [D_A(z)-D_B(z)].                    (1)
```

Here D counts unordered distinct pairs, with multiplicity. In particular,
**E=0 as an integer polynomial is necessary and sufficient for homometry**.
Without balance the right side's signed-shell version equals E+2*balance;
the tests check this stronger bookkeeping identity too.

## At most 41 cells, however large the tree

Split each arm at its holes, excluding the holes themselves. Intersect each
resulting interval with each depth residue modulo g. Retain nonempty cells;
the centre, when retained, is a separate cell. There are at most
1+g(3+|H|) cells, hence at most 41 for two holes and g=8.

For a cell whose first depth is f, its vertices are f+gj, 0<=j<n.
Set X=sum_j s_j. Its exact possible values are -n,-n+2,...,n.
Within this cell, every monomial exponent in the contribution to E has form
e+g*epsilon*j, with epsilon in {-1,0,1}. The sign of a same-arm distance
to a hole stays fixed because the interval was cut there. At a g-th root,
the contribution therefore depends only on X. `column` gives its integer
coefficients in Z[z]/(z^g-1), together with a balance row.

Consequently the nine equations and the independent bounds/parities on X
are **equivalent** to the existence of a balanced partition whose distance
histograms agree modulo eight. Each permitted X can be realized independently
inside its cell. Conversely, such a partition supplies its X values.
For the reverse implication from E mod z^8-1 to distance histograms, (1)
shows that their difference is a constant residue vector; its sum is zero
because the two parts have the same size. The constant must be zero.

This is not equivalence to full homometry. Distances 1 and 9, for example,
remain different in the original metric.

## A stronger necessary system, with sharp moment bounds

For each cell also set Y=sum_j j*s_j. Write u=z^g-1. Modulo u^2,

```text
z^(e+g*epsilon*j) = z^r [1+(q+epsilon*j)u],
where e=qg+r, 0<=r<g.
```

Thus each term a*z^(e+g*epsilon*j) contributes aX to residue r and
a(qX+epsilon Y) to its first-moment row. `moment_constant` and
`moment_linear` record these two coefficients. Vanishing of these rows,
together with the previous nine, is exactly balance and E divisible by
(z^8-1)^2. It is necessary for (1) to vanish, but still not sufficient.
In particular no claim about equality of every exact distance follows.

The local bounds are exact, not a continuous relaxation. Put
p=(n+X)/2 and T=n(n-1)/2. Then

```text
p(p-1)-T <= Y <= p(2n-p-1)-T,       Y == -T (mod 2).  (2)
```

Indeed Y=2*sum_(j positive) j-T. The sums of p distinct elements of
{0,...,n-1} fill every integer between p(p-1)/2 and p(2n-p-1)/2.
For an explicit proof, any excess q from 0 to p(n-p) is obtained by giving
the p increasing indices nondecreasing increments floor(q/p) or ceil(q/p).
The p=0 case has the single sum zero. This proves both necessity and
sufficiency of (2) for each cell independently.

## A modular witness for every even parameter

Put t=2k and omit depths 4 and 10 on arm 2. In the following table, columns
are residues 0,...,7; a dash means the interval has no such cell.
These are **signed counts X**, not constant signs along an interval.

| Cell interval | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Centre | 1 | - | - | - | - | - | - | - |
| Arm 1, all | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| Arm 2, 1..3 | - | -1 | -1 | -1 | - | - | - | - |
| Arm 2, 5..9 | -1 | -1 | - | - | - | 1 | 1 | 1 |
| Arm 2, 11..L2 | 1 | 1 | 1 | 0 | 1 | 1 | -1 | -1 |
| Arm 3, all | -1 | 0 | 0 | 0 | -1 | -1 | -1 | -1 |

At k=0 these counts satisfy every cell's bounds and parity. Increasing k
adds 1890k vertices to each residue cell in the three long intervals, an
even increase. It changes no column or displayed X, so the same counts
remain attainable for every k. There are exactly 33 nonempty cells.

For a short direct substitution check, the total arm sign polynomial and
sum of the two hole polynomials, reduced modulo z^8-1, have coefficient
vectors (in residue order)

```text
S1+S2+S3 = (-1,0,1,0,0,1,-1,-1)
C4+C10   = (-1,-3,-2,1,1,2,2,0).
Q        = (-2,1,3,0,1,0,-2,-1)
          = (z^-1-1)(C4+C10).
```

Balance also holds. The previous equivalence constructs an m-element pair
with equal residue histograms for every even t. At t=0, choosing the earliest
p depths as positive in each cell gives common residue histogram
(1370,1499,1479,1460,1443,1427,1409,1389). Its exact distance-one counts
differ by two. This is a real failing exact-distance pair, not a simulated
failure or an obstruction to all orderings.

## Yet no ordering of these counts works when t=4r

Take the first-moment row combination with weights
lambda=(0,-1,1,2,2,1,-1,0). Every coefficient of Y is divisible by four.
Dividing those coefficients by four gives, in the same table layout,

```text
centre:             0
arm 1:              (0,-1,-1, 1,0,0,1,0)
arm 2, 1..3:        ( -,-1,-1, 1,-,-,-,-)
arm 2, 5..9:        (-1,-1, -, -, -,0,1,0)
arm 2, 11..L2:      (-1,-1,-1, 1,1,0,1,0)
arm 3:              (0,-1,-1, 1,0,0,1,0).
```

At t=4r, each growing cell gains 3780r vertices, divisible by four.
Thus every Y parity in (2) stays fixed. Direct substitution in the
displayed count table and the monomial formula gives

```text
lambda dot (constant part of moment rows) = 18+11340r;
lambda dot (Y part), modulo 8             = -8 mod 8.
```

Changing an admissible Y by two changes this weighted equation by a
multiple of eight. Its residue must therefore be
10+11340r == 2+4r (mod 8), which is never zero. This excludes **all**
orders of signs realizing the displayed X, even if their individual
distance profiles differ from the earliest-positive lift. It does not
exclude another X for the same holes. `moment_obstruction` computes the
actual integer coefficients rather than trusting a saved certificate.

## Resolution of the seventeen-equation feasibility subproblem for `t>=1`

Bramble, 21 November 2026. The open subproblem above is **feasible for every
`t>=1`** (including every `t=4r`, `r>=1`): for `H=[(1,1),(2,1)]` (25 cells),
each congruence class `t = t_0 + 4k` (`t_0 in {1,2,3,4}`, `k>=0`) admits an
explicit constant vector `X` (`max |X| <= 4`) and linear moment vector
`Y(k) = Y_0 + k * dY` satisfying all 17 equations (`E(z) == 0 mod (z^8-1)^2`)
and every exact quadratic bound in (2).

The proof for every `k>=0` is purely finite:
* `column` and `moment_linear` are constant in `t`, and `n_c(t_0+4k)=n_c(t_0)+3780k`
  preserves `n_c mod 4` and hence the parity of `Y_c` on all 24 growing arm cells
  (while the centre cell has `count=1, dY=0`).
* Because `7560` is divisible by `8`, `moment_constant` advances linearly by
  `4k * dmc`. Checking `k=0` and `k=1` (via `moments_witness(t_0)` and
  `moments_witness(t_0+4)`) proves all 17 linear equations identically for `k>=0`.
* On each growing cell, the upper and lower gaps `high_c(k)-Y_c(k)` and
  `Y_c(k)-low_c(k)` are convex quadratics in `k` with leading coefficient
  `3780^2/4`. Checking nonnegativity at `k=0` plus nonnegative linear
  derivatives `3780 p_0 - dY >= 0` and `dY + 3780(n_0 - p_0) >= 0` proves
  attainability in (2) for **all** `k>=0`.

Consequently, infeasibility of the 17 double-root equations cannot refute the
target across arbitrary `H` for `t>=1`; any all-pairs proof (or construction)
must lift to higher-degree or exact distance equations.

```sh
python3 projects/almost-halving-three-branches/long_frontier_infinite.py 4 --moments-witness
python3 projects/almost-halving-three-branches/long_frontier_infinite.py 4000000 --moments-witness
```

Both commands return `aggregate_equations_hold: true`,
`first_moment_equations_hold: true`, and `homometric_pair_proved: false`.
Saving the JSON and passing it to `--verify FILE` reconstructs all columns and
moments and rejects altered moments with exit code 1.

## Lifting to triple roots `(z^8 - 1)^3` for every `t >= 1`

Extending the compressed moment hierarchy to `u^2` (with `z^8 = 1 + u`)
introduces one integer second moment per cell,
`Z_c = sum_{j=0}^{n_c-1} (j*(j-1)//2) * s_j`, subject to parity
`Z_c == -C(n_c, 3) (mod 2)` and exact Schur-extremal bounds `[Z_min, Z_max]`
given `(n_c, X_c, Y_c)`:

* **Why the earlier 17-equation witness cannot lift.** Across all 25 cells,
  the quadratic coefficient matrix multiplying `Z_c` has rank 7 over `Q` with
  cokernel `lambda = (-1, 1, -1, 1, -1, 1, -1, 1)` (representing `E''(-1) = 0`),
  eliminating `Z_c` completely. Evaluating `lambda . u^2` on
  `MOMENTS_WITNESS_BRANCHES` gives non-zero quadratics of strict constant sign
  (`31954752 + 295369200k + 685843200k^2`, `101182422 + 373346820k + 342921600k^2`,
  `394214848 + 1173342240k + 857304000k^2`, and
  `-672263912 - 1188662580k - 514382400k^2` for `t_0 = 1..4`). Thus those four
  specific `(X, Y)` families admit no `(z^8 - 1)^3` completion at any `t >= 1`.
* **Exact 25-equation feasibility for every `t >= 1`.** Retaining the same
  four signed-count vectors `X` for `t = t_0 + 4k` (`t_0 in {1, 2, 3, 4}`) and
  allowing quadratic first moments `Y(k) = Y_0 + k*Y_1 + k^2*Y_2` and cubic
  second moments `Z(k) = Z_0 + k*Z_1 + k^2*Z_2 + k^3*Z_3` solves all 25
  equations `E(z) == 0 mod (z^8 - 1)^3` and stays strictly within every
  `(Y, Z)` Schur bound for **all integer `k >= 0`** (`TRIPLE_ROOT_WITNESS_BRANCHES`,
  proved across `k >= 0` by exact nonnegative Taylor-series coefficients around `k = 0`).
  Thus triple-root lifting modulo `z^8 - 1` also cannot refute `H = [(1,1),(2,1)]`
  for any `t >= 1`.

## Structural impossibilities for periodic and constant-run tails (`t >= 1`)

Two broad candidate construction ansätze for `t >= 1` fail unconditionally:

1. **Synchronized periodic fixed-prefix-hole families `(P, B, T)`.** Suppose all
   holes remain in bounded prefixes `[0, d]` and all three arms insert `7560 t`
   vertices starting at the **same depth `d + 1`** by repeating length-`B`
   `{+1, -1}` blocks `B_1(z), B_2(z), B_3(z)`. For large `t`, separating powers
   of `Q = z^{7560 t}` in `(z - 1)(z^B - 1) E_t(z)` isolates the `Q^2`
   coefficient `2 z^{2d} (B_1(z) + B_2(z) + B_3(z))`, which can never vanish
   because `B_{1,j} + B_{2,j} + B_{3,j} in {-3, -1, 1, 3}` is odd for every
   offset `0 <= j < B`. *(If the block start depths `(d_1, d_2, d_3)` are
   allowed to differ, `Q^2 = 0` alone is not obstructed—e.g. `(1, 0, 0)` with
   `P = 2`, `(-1,-1), (-1,1), (1,1)` makes `Q^2` cancel.)*
2. **Terminal constant-sign runs.** On `T(a, b, c) = T(227+7560t, 67+7560t, 11+7560t)`
   for every `t >= 1`, `b + c = 78 + 15120t > 227 + 7560t = a`, so no same-arm
   or centre-to-arm pair reaches distance `b + c`. If a colouring keeps
   constant signs `(s_1, s_2, s_3) in {+1, -1}^3` (with no holes) on `[a - 216, a]`
   (arm 1), `[b - 216, b]` (arm 2), and `[c - 160, c]` (arm 3), then distance
   `a + b` forces `s_2 = -s_1`, distance `a + c` forces `s_3 = -s_1`, and
   distance `b + c` leaves uncancelled `(2, b)-(3, c)` contribution
   `s_2 + s_3 = -2 s_1 != 0`.

```sh
python3 projects/almost-halving-three-branches/long_frontier_infinite.py 4 --triple-moments-witness
python3 projects/almost-halving-three-branches/long_frontier_infinite.py 4000000 --triple-moments-witness
python3 projects/almost-halving-three-branches/long_frontier_infinite.py 1 --structural-obstructions
```

## The unresolved lemma and next useful work

The required all-pattern lifting lemma for exact distances remains open: for an
infinite explicit set of `t`, either find an exact construction or prove that
no realization of any surviving support `(H, X, Y)` makes the full polynomial
`E(z)` vanish.

## Reproduce and recorded checks

After independent integration, from the root of a public repository clone,
Python 3.10+ needs no packages:

```sh
python3 projects/almost-halving-three-branches/long_frontier_infinite.py 0 --barrier-even --lift-check
python3 projects/almost-halving-three-branches/long_frontier_infinite.py 1000000 --barrier-even
python3 projects/almost-halving-three-branches/long_frontier_infinite.py 4000000 --moment-obstruction
python3 projects/almost-halving-three-branches/long_frontier_infinite.py 0 --barrier-even --first-moments
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_long_frontier_infinite.py
```

Recorded here: the first command has aggregate equations true, size and
target 152, exact homometry false, first mismatch (distance 1, difference 2).
The million-parameter command still has 33 cells and zero aggregate residual.
The third reports weighted residue 2 and `fixed_counts_obstructed: true`,
with `arbitrary_counts_obstructed` and `all_omissions_obstructed` both false.
The fourth rejects the canonical moments while preserving the modular result.

A file with `signed_second_moments` checks all three layers (`E(z) == 0 mod (z^8-1)^3`),
a file with `signed_moments` checks two layers, and `--verify FILE` rejects altered
counts or moments. Expansion is capped at 512 original vertices; that cap supplies no verdict.

Eleven focused tests pass (including exact subset verification of
`second_moment_bounds`, nonnegativity of the exact Taylor-series `k >= 0` Schur
certificates across all four triple-root branches, the `T(27,11,3)` positive-control
check, 17-equation `E''(-1)` defect verification, periodic/constant-run
obstruction checks, and CLI `--verify` corruption rejection). They check all
1890 small support/colouring/modulus combinations with independent breadth-first
distances, random unbalanced shell identities, exact local moment bounds, huge
symbolic parameters, the real failing lift, and altered count/moment rejection
through the command line. All 233 project tests pass. Python compilation and
`git diff --check` pass.
