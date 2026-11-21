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

## The unresolved lemma and next useful work

The required all-pattern lifting lemma is still unproved: for an infinite
explicit set of t, for **every** same-parity pair H and every permitted
choice of X,Y satisfying the seventeen equations and (2), no choices of
cell signs realizing those moments make the full polynomial E vanish.
Equivalently, at least one remaining coefficient in (1) must be nonzero.
This statement, together with the support reduction above, would give
h(T)<=151+11340t. It is not inferred from the one count-pattern certificate.

A concrete earlier subproblem is now only seventeen integer equations in
at most 82 variables with the explicit quadratic bounds (2): decide whether
they have any solution for arbitrary H at t=4r. Infeasibility for all H
would prove the desired bound immediately; feasibility would identify the
counts and moments the next lifting argument must handle. **No solver for
that bounded integer feasibility problem is delivered here.** A failed
`--small-counts` search is inconclusive even for the nine-equation problem.

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

Use `--system` to emit all integer columns. Save a witness and pass it to
`--verify FILE`: the verifier reconstructs columns from lengths and holes,
ignoring saved columns. A file with `signed_moments` is checked at both layers.
Expansion is capped at 512 original vertices; that cap supplies no verdict.

Eight focused tests pass. They check all 1890 small support/colouring/modulus
combinations with independent breadth-first distances, random unbalanced
shell identities, exact local moment bounds, huge symbolic parameters,
the real failing lift, and altered count rejection through the command line.
All 168 available project tests pass. Python compilation and the repository's
advisory size check pass; Ruff is unavailable in this environment.
