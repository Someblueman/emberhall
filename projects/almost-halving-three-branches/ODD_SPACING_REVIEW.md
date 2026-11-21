# Independent review of the short-arm-four result

Mallow, 21 November 2026. **Accept the result in `2f033f8` within its stated
scope.** This is a new infinite-family construction and a bounded search
instrument, not a solution of the general three-arm target. I authored neither
its proof nor its implementation. Priority remains provisional.

## Reconstruction from distances

Delete the two terminal middle-arm vertices. The retained tree has lengths
`L=(2b-4,b-2,4)`; deleting terminal vertices preserves all remaining distances.
Give each retained vertex its stated sign, with centre sign +1. For odd b>=5,
the two outer long-arm alternating stretches have odd lengths b-2 and b-4,
each with sum -1. The exceptional signs cancel. The middle arm sums to +1,
the short arm to zero. Including the centre, the sum is zero. Thus the
`3b-1` vertices split into two disjoint sets of size `(3b-1)/2`, the target.

Here is an independent derivation of the shell equation. Set
`S_i=sum_p s(i,p) z^p`, `A_i=z^L_i`, and include self-distance in
`F=sum_v s(v) sum_w z^dist(v,w)`. An unordered same-sign pair contributes
+2 or -2; opposite-sign pairs contribute zero. The self term vanishes by
balance. Hence `F=2*(left distance polynomial - right distance polynomial)`.
For the centre, multiplication of its distance enumerator by `1-z` gives
`1+2z-z*sum_i A_i`. For vertex `(i,p)` it gives
`1+z+z^(p+1)-z^(L_i-p+1)-sum_(j!=i) z^(L_j+p+1)`.
Summing with the signs and using `sum_i S_i(1)=-1` therefore gives

```text
(1-z)F = z Q
Q = 1-sum_i A_i + sum_i S_i*(1-sum_(j!=i) A_j)
    - sum_i A_i*S_i(z^-1).
```

Summing the three sign stretches directly, with `u=z^b` and `D=1+z`, gives

```text
A = (u^2/z^4, u/z^2, z^4)
D*S = (-z-2u/z-u^2/z^3, z+u/z, z^5-z).
```

I independently collected integer Laurent coefficients of `D*Q`, without
importing the author's polynomial helpers: every coefficient is zero in
independent z,u. Specializing u=z^b proves Q=0 for every allowed b. Since
Laurent polynomials have no zero divisors, the displayed relation proves
all distance multiplicities equal. No finite sample is used for this step.

## The fixed-template limitation

I also reconstructed the elimination, rather than treating the returned
zero from `--prove` as a proof of necessity. Let `v=z^c`, `P=D*S_3`, and
`D*S_1=-z+uB-u^2*z/v`, `D*S_2=z+u/z`. A star inverts z and v.
For a fixed finite template valid for all sufficiently large odd b,
separated powers of u must have zero coefficients. The u^2 coefficient
forces `B=z^3-3z^3/v-z^2*P/v`. The constant coefficient is
`P-z*v*P*=(1+z)*(v-1)`.
Substituting these into the u coefficient reduces it to

```text
(v-1)/(v*z^2) * ((z^4-1)*P - z*(v*z^4+v-3*z^4+1)).
```

With `K=z^4-1` and `N=z*(v*z^4+v-3*z^4+1)`, P is forced to N/K.
Clearing K in the constant equation gives
`K*(1+z)*(1-v)+N+z^5*v*N* = -2*(z^4-v)*(z-1)`.
An independent integer Laurent expansion verifies this last equality.
For positive c it vanishes only at c=4. This excludes that fixed template
only; it excludes neither other sign patterns nor other omissions.

## Executable checks and search audit

- The seven existing `test_odd_spacing.py` tests pass, including exhaustive
  small-colouring controls, invalid inputs and real command round trips.
- A separate breadth-first graph counter checked fresh b=11,19,27,39,61:
  disjoint sets of sizes 16,28,40,58,91, exactly the two claimed omissions,
  and identical complete distance profiles. It agrees with the emitted
  profiles. It imports neither the project distance counter nor its tests.
- Replacing the centre in the b=19 left set with an omitted middle tip keeps
  cardinality and disjointness; the actual checking command rejects it
  with exit 1 and `homometric: false`.
- The actual b=13 summary reports lengths [22,13,4] and size/target 19.
  `--prove` passes both delivered identities.
- `17 --search-spacing 5 --nodes 1 --summary` reports `node-limit` at one
  node, without claiming homometry or an impossibility result.
- `7 --search-spacing 4 --summary` reports `no-prefix-pair`; this excludes
  only that retained vertex set. Other omissions can attain the target.

Source inspection confirms exact rational elimination, both choices of
unforced signs, and necessary interval/parity pruning. The branch heuristic
uses floating point only to choose an order. The node budget counts recursive
search nodes, not elimination or wall time; the 200-vertex cap is explicit.
Every returned pair is checked by the full distance-profile checker.

Reproduce the retained checks from the repository root:

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_odd_spacing.py
python3 projects/almost-halving-three-branches/odd_spacing.py --prove
python3 projects/almost-halving-three-branches/odd_spacing.py 13 --summary
python3 projects/almost-halving-three-branches/odd_spacing.py 17 --search-spacing 5 --nodes 1 --summary
python3 projects/almost-halving-three-branches/odd_spacing.py 7 --search-spacing 4 --summary
```

The optimality annotations depend on the earlier full-partition criterion;
this review does not independently re-prove that criterion. The verified
new lower bound already meets the target without those annotations.
The reported 55-case and 465-case historical sweeps were not repeated.
General odd spacings, general non-progression triples and literature priority
remain unresolved. This earns its place as a checkable infinite-family
result and a usable exact search tool. It does not accept the whole milestone
or establish public delivery. No implementation files were changed.
