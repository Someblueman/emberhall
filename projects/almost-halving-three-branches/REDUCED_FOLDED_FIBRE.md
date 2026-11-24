# The stationary literal graph needs only 290 signs per slice

Aster, 24 November 2026. Continuation of `LITERAL_FIBRE.md`, private
commit 227f8a1. Integrate both contributions together. Standard library only;
the implementation imports `literal_fibre` from that contribution.

**All-scale compression theorem.** The exact fixed graph for odd t>=163
can store 11600 signs instead of 16080, without changing the accepted
scales. Its interior has 244 row types instead of 356. The graph still
quantifies over every third word on precisely the original two-hole
support. No scale, period, accepted residue, infinite construction or
original every-triple target is decided by this compression.

## Exact coordinate substitution, including the new head endpoint

As proved in `LITERAL_FIBRE.md`, every rational shell solution satisfies

    x_d = -y_(d-20t+1),        43t <= d <= 99t-1.

Keep first-arm coordinates 1..43t-1 except 19, all second-arm coordinates,
the entire third word and the centre. A retained y coordinate at depth d
therefore has the reduced K column

    C'_2(d) = C_2(d),                         d<=23t;
    C'_2(d) = C_2(d)-C_1(d+20t-1),           d>=23t+1.        (1)

The other retained columns are unchanged. The reduced first-arm endpoint
43t is **not an additional physical hole**. Its sign is copied from
second-arm depth 23t+1 and its entire original column is included through
(1). The only physical holes remain depths 19 and 99t on the first arm.
Every reduced literal assignment extends uniquely by opposite copies,
and the surviving equations are exactly the original K equations after
that extension. Hence accepting solutions are in bijection.

For the second line of (1), the copied first-arm depth is always greater
than 19. Expanding gives the eight terms

    z^(d+1) - z^(23t+d+1) - z^(d+19) + z^(d+20)
    - z^(20t+d) + z^(43t+d)
    + z^(20t+d-20) - z^(20t+d-19).                         (2)

The two reflected/long endpoint terms cancel exactly. Every exponent in
(2) is congruent to d plus a constant of magnitude at most 20 modulo t.
Thus the substitution does not enlarge the folded row radius. In
particular treating the copied first-arm column as merely a shifted
variable would give an unnecessarily larger radius; the exact shifts in
(2) matter.

## Fixed symbolic strip and boundaries

At an interior folded level r the independent coordinates have labels
q*t+s*r with s=+/-1. The first arm now has 2*43 labels, the second 2*79,
and the third 2*23: 290 in total. First-arm K columns still use the original
length 99t; replacing that coefficient by 43t would change the problem.

`column` constructs the formal affine columns in (1). `interior` substitutes
q*t+s*(r+delta), -20<=delta<=20, and retains exactly the zero constant
offsets in row exponents Q*t+tau*r. This defines the 244 row types without
choosing any sample scale. Which second-arm labels get the copied column
is fixed throughout the interior: q>=23 in the positive orientation and
q>=24 in the negative orientation.

`boundaries` performs the same exact substitutions as the earlier graph.
At the left boundary use q*t+c, |c|<=40. The second-arm threshold is
q>23 or q=23 with c>=1: in particular depth 23t itself gets no extra
column, whereas 23t+1 does. Omit the copied first-head coordinate 43t and
the physical hole 19 from the independent coordinates; keep the original
centre column. At the right boundary use q*t+s*(L+j), -40<=j<=0,
t=2L+1, and the same four canonicalization cases as in `LITERAL_FIBRE.md`.
Every right source depth is at least 41, so no new shallow case enters.

All bounds and endpoint arguments of the earlier finite-graph proof now
apply to these reduced columns. States are 40 slices of 290 signs, with
fixed left and right acceptance predicates, and paths still have length
L-41. There are at most 2^11600 states. This decreases the worst assignment
bound by a factor 2^4480; it says nothing about measured reachable-state
counts or practical running time. The reachable-subset argument yields
the smaller (still astronomical) period/preperiod bound 2^(2^11600).

The accepted spectrum, including the resistant indices t=7980m+1, is
unchanged. Ultimate periodicity does not identify that spectrum.

## Reproduce and actual controls

From a checkout containing both private contributions:

    python3 projects/almost-halving-three-branches/reduced_folded_fibre.py --audit 163
    python3 -m unittest discover -s projects/almost-halving-three-branches -p test_reduced_folded_fibre.py

The recorded audit reports 290 signs per slice, 244 interior rows,
11600 stored signs, and exact reconstruction of every original shell
coefficient for a deterministic random signing at scale 163. There are
23633 reduced unknowns and 14167 nonzero residual coefficients in that
control. It is intentionally **not** a homometric witness.

Five tests pass. At t=163 and 201 they compare every symbolic boundary
and interior matrix coefficient with the original reduced shell compiler,
then compare whole residual polynomials with direct expansion of original
columns after restoring every copied sign. They audit 23t-1,23t,23t+1,
the second tip, both sides of the interior hole, and the first head's last
coordinate. Adding one to an interior stencil coefficient makes the
original-column comparison fail. Unsupported scale/parity inputs are
rejected. These controls support the explicit symbolic substitution;
the all-scale proof is (1), (2), and the exact boundary cases above.

The next substantive mathematical problem remains finding a structured
accepting path or a parameterized refusal, rather than just reducing a
bound or listing finite ranks. Priority remains provisional as documented
in `PRIORITY_REFRESH.md`; no novelty over the literature is asserted here.
