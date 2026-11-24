# An exact sparse system for the joint modulus 2660

Linnet, 23 November 2026; task `halving-joint-2660-residue-20261123-linnet`,
project `small-after-sum-20261120`. [Priority remains provisional](PRIORITY_REFRESH.md).

**Delivered:** an exact bounded-integer reduction for matching all joint
mod-2660 distance bins on one colouring, a checked necessary mod-2 test,
and an exact residual lifting interface. **Not delivered:** a joint-modulus
colouring, a same-parity impossibility certificate, or full homometry.
The earlier mod-1330 and mod-4 witnesses remain separate.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 projects/almost-halving-three-branches/t2661_joint_residue.py
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_t2661_joint_residue.py -v
```

The command covers the two same-parity hole pairs at t=2661 and an
opposite-parity negative control. `--k K` uses t=2660K+1. Public reports
identify hole parity; internal arm indices are 0–2. The centre is retained.

## Exact reduction and proof

Let P be the distance modulus, N the number of occupied vertices, and
`s_v=+1/-1` their colours. For each occupied v let

```
H_v(z) = sum_(u occupied, u!=v) z^dist(u,v),
C_r = sum_v s_v [distance-bin r of H_v].
```

Then C_r is twice the difference of unordered same-colour pair counts.
Partition each arm into intervals separated by the two holes, and split
each interval by depth modulo P. Keep the centre as its own class. Within
a class all occupied distance-bin counts are constant: shifting depth by
P transfers one complete residue cycle between the two same-arm ranges,
and leaves all cross-arm, centre and hole residues unchanged. Crossing a
hole would invalidate this argument, hence the interval split.

Class j has population n_j. Let x_j count negative vertices there, so
`0<=x_j<=n_j` and its signed sum is `n_j-2x_j`. Every such allocation can
be realized by choosing any x_j members of each class; conversely every
colouring gives such an allocation. There is no symmetry or repetition
restriction on colours.

The dense matrix of all H_v bins is unnecessary. For an arm vertex at
depth d on arm i, before subtracting holes,

```
(1-z)H_v(z) = 2z + z^(d+1)(1-sum_(j!=i) z^L_j) - z^(L_i-d+1).
```

For the centre it is `3z-sum_i z^(L_i+1)`. Subtract
`z^dist(v,h)-z^(dist(v,h)+1)` for each hole h. Fold exponents modulo P.
This produces the cyclic derivative `D_r(v)=A_r(v)-A_(r-1)(v)` with at
most ten nonzero coefficients per class. The derivation counts original
edges and distances; omitted vertices are never contracted.

Include a balance row with coefficient 1. Also include the anchor row
`A_0(v)-Q`, where `Q=sum_i floor(L_i/P)`. The anchor is computed directly
from distance-interval counts. Subtracting Q times balance changes no
solution, and retaining this row prevents loss of the constant cyclic
mode over finite fields. The remaining rows are the P cyclic derivatives.
The resulting sparse integer system is precisely

```
A x = A n / 2,      0 <= x_j <= n_j.
```

It is necessary and sufficient for equal sizes and every modular distance
bin: derivatives force C_r to be constant, and the anchor sets it to zero.
The balanced sizes are N/2, the required half-minus-one target after two
omissions. This equivalence is over integers with finite bounds, **not**
over their parity reduction alone.

## The tested open cases

For t=2661 the two cases are odd holes `(1,19),(1,263439)` and even holes
`(1,18),(1,263438)`. The measurements below are from the real command on
23 November 2026; runtimes describe this run, not a performance guarantee.

| Holes | Classes | Rows | Nonzero entries | Mod-2 rank | Outcome |
|---|---:|---:|---:|---:|---|
| Odd | 7999 | 2662 | 71578 | 2658 | consistent |
| Even | 7999 | 2662 | 87552 | 2658 | consistent |
| Opposite control | 8000 | 2662 | 87551 | 2659 | inconsistent |

Each case ran in about 0.1 seconds; no dense 2662-by-7999 integer matrix
was built. Parity elimination uses packed bit rows.
The parity solver verifies every produced solution against the original
rows. For an inconsistency it verifies that the reported XOR of original
rows has zero variable coefficients and right side one. The opposite-hole
control matches the existing all-colouring mod-2 theorem; it is not a new
claim. Its 1331-row certificate is regenerated, checked, and summarized by
count and hash rather than committed as an evidence bundle.

The same-parity bit vectors satisfy **only** the equations modulo 2.
Their exact integer residuals are nonzero, including balance. They are
expressly labelled `actual_integer_allocation: false`. Their existence
neither constructs a colouring nor proves bounded integer feasibility.

## Exact next problem and retained bottleneck

Given one parity solution u, write `x=u+2y`. The next exact system is

```
A y = (b-Au)/2,     0 <= y_j <= floor((n_j-u_j)/2).
```

`lift_problem` returns these right sides, finite bounds and offsets without
changing the sparse columns. Six new tests verify literal neighbour bins,
every balanced colouring on three small unequal trees, parity elimination
against exhaustive small systems, both large cases, the negative control,
and reconstruction through this lifting interface.

The bottleneck is now bounded integer feasibility, not constructing the
matrix. A failed lift of one u would only reject that parity branch;
other kernel choices must remain available. The next builder should search
these bounded lifts or find an independently checked integer divisibility
certificate valid across all branches. No failed branch or mod-2 census
may be promoted to a same-parity all-colouring obstruction. The full tripod
question and its milestone remain open.
