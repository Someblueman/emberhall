# An odd-spacing family: the short arm has four vertices

Sorrel, 21 November 2026. For every odd integer `b>=5`, the tree
`T(2b-4,b,4)` has disjoint homometric sets of size `(3b-1)/2`.
Here the arithmetic-progression spacing is `d=b-4`, which is odd.
This meets the half-minus-one target for an infinite family outside the
odd-middle/even-spacing theorem in [NEXT_ODD_FAMILY.md](NEXT_ODD_FAMILY.md).
It does not settle all odd spacings. Literature priority remains provisional.

The construction is optimal except at `b=5,9`, where a full partition is
already known. The accepted [full-partition criterion](PROGRESSION_PARTITIONS.md)
requires `b-4` to divide b or `2(b-4)` to divide b+1. For odd b>=5 these
conditions hold only at b=5 or b=9. Otherwise the target is an upper bound.
The checker reports that distinction instead of claiming every pair is maximal.

## Run and inspect the actual pair

From the complete repository, Python 3.10+ and its standard library suffice:

```sh
python3 projects/almost-halving-three-branches/odd_spacing.py 13 --summary
python3 projects/almost-halving-three-branches/odd_spacing.py --prove
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_odd_spacing.py
```

The first command returns lengths `[22,13,4]`, two sets of size 19, target
and upper bound 19, and `homometric: true`. It omits `[2,12]` and `[2,13]`.
Without `--summary`, both vertex lists and complete distance profiles are
printed; the output works with `published_cases.py --check -`.
At the contribution's base the unchanged default command returns size 18
on this same tree. This separate constructor closes that specific gap.

## The signs

Omit the last two vertices of the middle arm. The retained lengths are
`(2b-4,b-2,4)`, and distances between retained vertices are unchanged.
Give the centre sign +1. On the longest arm use:

* `(-1)^p` at depths `1<=p<=b-2`;
* -1 at depth b-1, then +1 at depth b;
* `-(-1)^p` at depths `b<p<=2b-4`.

On the middle arm use `-(-1)^p`. On the short arm use `(-1)^p`.
The two long-arm alternating intervals have odd lengths b-2 and b-4,
and each sums to -1. Its two exceptional signs cancel. The middle arm
sums to +1, the short arm to zero, and the centre to +1. Total sign is
zero. All `3b-1` retained vertices are used, so the two sign classes
each have `(3b-1)/2` vertices. This also works at the smallest b=5.

## One Laurent identity proves every b

Use the balanced-sign shell equation derived in NEXT_ODD_FAMILY.md:

```text
Q = 1-A1-A2-A3
    + sum_i Si*(1-sum_(j!=i) Aj) - sum_i Ai*Si(z^-1).
```

Its vanishing says all within-set distance multiplicities agree.
Put `u=z^b`, `D=1+z` and `Pi=D*Si`. Summing the signs above gives

```text
(A1,A2,A3) = (u^2/z^4, u/z^2, z^4),
P1 = -z - 2u/z - u^2/z^3,
P2 = z + u/z,
P3 = z^5-z.
```

A star inverts z and u simultaneously. Since `D*=D/z`, multiplication
of Q by D gives the finite Laurent identity

```text
D*(1-A1-A2-A3)
 + sum_i Pi*(1-sum_(j!=i) Aj)
 - z*sum_i Ai*Pi* = 0.
```

The proof command collects its integer coefficients in independent z,u
and returns zero. Thus the identity holds after substituting u=z^b;
cancelling nonzero D proves equality of every distance multiplicity.
This is an all-parameter proof, not an interpolation of small counts.

## Why this particular pattern does not generalize by changing four

There is a useful exact limit to this construction. Suppose the short arm
has any positive even length c, the retained lengths are `(2b-c,b-2,c)`,
the middle arm still alternates with first sign +1, and the long arm has
alternating outer stretches separated by a fixed-width correction near b.
More precisely, require the numerator form

```text
A = (u^2/v, u/z^2, v),       v=z^c,
P1 = -z + u*B - u^2*z/v,
P2 = z + u/z,
P3 = (1+z)*S3,
```

where B and the finite short-arm polynomial S3 do not depend on b.
Demand the shell identity for every sufficiently large odd b. Collecting
powers of u and their reflected equations forces

```text
P3 = z*(v*z^4 + v - 3*z^4 + 1)/(z^4-1).
```

The u^2 coefficient first gives
`B=z^3-3z^3/v-z^2*P3/v`; substitute this and its reflection into the
u coefficient together with the constant equation
`P3-v*z*P3*=(1+z)*(v-1)`. The resulting u coefficient is
`(v-1)/(v*z^2)` times
`(z^4-1)*P3-z*(v*z^4+v-3*z^4+1)`, giving the displayed expression.

Now substitute that forced expression and its actual reflection back into
the constant equation. After multiplying by `z^4-1`, its residual is
`-2*(z^4-v)*(z-1)`. The proof command independently collects the
coefficients of this residual identity. Vanishing forces v=z^4 and hence
**c=4 is necessary for this template**, even without requiring the
short-arm coefficients to be signs. This is not an obstruction to a
different construction on the same tree.

## Verification and remaining work

The tests rebuild the graph and count breadth-first distances on fresh
odd b, cover the smallest case and both full-partition exceptions, reject
an altered equal-sized disjoint pair, and round-trip the actual command
through the existing checker. A separate symbolic expansion also gives
zero. No external solver is needed by the delivered code or tests.

## A bounded instrument for the still-open cases

An explicit research mode searches one retained vertex set: omit exactly
the last two vertices of the middle arm. For example:

```sh
python3 projects/almost-halving-three-branches/odd_spacing.py 17 --search-spacing 5 --summary
```

This returns a checked pair of size 25 on `(22,17,12)`. It is a finite
search result, not a formula for an infinite family. The mode accepts odd
b and any integer `0<d<b`, up to 200 retained vertices. `--nodes` sets its
positive branch-node limit, default 100000; rational elimination happens
before that count. It uses neither floating-point feasibility nor a solver
dependency. A floating-point score only orders branches.

For each distance k, build the integer row `N_k(x)` on the retained tree.
Sign balance and every equation `sum_x sign(x)*N_k(x)=0` form an exact
linear system, by the shell argument above. Fix the retained centre's sign
to +1, which loses only the globally reversed colouring. Rational row
reduction expresses pivot signs in the free signs. Clear each row's
denominators; it becomes `sum_j a_j*s_j` equal to one of two integer
targets. Branch on free signs in {-1,+1}. Interval bounds, residue parity
modulo twice the remaining coefficients' gcd, and single-variable rows
prune choices; `check_pair` then counts both complete distance profiles.
Each pruning condition is necessary, and every unforced free sign is
branched both ways. Rational row operations preserve the solution set.
Thus finishing the search exhausts exactly the full sign partitions of
this retained vertex set; reaching the node limit does not exhaust them.

`found` supplies both complete vertex lists. `node-limit` means the search
stopped without a conclusion. `no-prefix-pair` means exhaustive failure
for this one retained vertex set, never for other omissions or the original
target. For example, b=7,d=4 returns `no-prefix-pair`, although the
odd-middle/even-spacing theorem supplies a target-size pair using different
omitted vertices. Tests keep these two failure meanings distinct and cover
d=1, where the short arm is longer than the retained middle arm.

The finite research check used the following 55 (b,d) pairs, frozen before
searching. They were below target in the default menu at base `cb20e70`,
with the newly proved short-arm-four family excluded:

```text
(17,5) (21,13) (23,17) (25,17) (27,19) (27,21) (29,9) (29,17)
(29,21) (31,7) (31,11) (31,21) (31,23) (31,25) (33,9) (33,13)
(33,21) (33,25) (35,11) (35,13) (35,23) (35,25) (35,27) (35,29)
(37,13) (37,21) (37,25) (37,29) (39,7) (39,15) (39,25) (39,27)
(39,29) (39,31) (39,33) (41,17) (41,25) (41,29) (41,33) (43,9)
(43,13) (43,15) (43,17) (43,27) (43,29) (43,31) (43,33) (43,35)
(43,37) (45,13) (45,17) (45,25) (45,29) (45,33) (45,37)
```

All 55 yielded a pair, first through a linear external-solver prototype
and then again through the delivered dependency-free search.
The latter needed at most 185 branch nodes in this run. These witnesses
suggest examining whether removing those two tips always suffices for odd
b,d. They do not prove that conjecture. The fixed-parameter construction
and its all-b proof above remain the theorem delivered here.

A second fixed audit covered all 465 odd pairs `3<=b<=61`, `1<=d<b`,
with a 10000-node cap per case. It found 463 pairs, each checked with
breadth-first graph distances. `(47,7)` and `(57,9)` reached the cap and
remain unresolved by that run; neither was retried with a larger budget.
All 60 project tests passed, including exhaustive sign-colouring oracles
for every spacing at b=3 and b=5 and explicit node-limit handling.

General odd spacing remains open. Broader periodic discovery templates
are attempts to find a different construction; failure to fit their finite
samples is not a graph-theoretic impossibility result. This contribution
needs independent reconstruction and integration, and makes no full-project
completion or public-delivery claim.
