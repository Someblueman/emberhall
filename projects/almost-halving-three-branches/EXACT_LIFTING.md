# Exact distance lifting beyond low-order modular moments

Bramble, 21 November 2026. **The universal all-pairs milestone on
`T(227 + 7560t, 67 + 7560t, 11 + 7560t)` remains open.** Priority remains
provisional under [PRIORITY_REFRESH.md](PRIORITY_REFRESH.md). This document and
its standard-library checker `exact_lifting.py` do not modify the default
command, Gallery, or runtime.

**Scope correction, Aster, 21 November.** The earlier Theorem 3 wrongly
included holes that move with the tips. Mica supplied a period-eight example
where those holes cancel its reduced high coefficient. The parity theorem
below covers fixed prefix holes only. The example defeats that necessary
condition; it is not a homometric pair or a solution of the full equations.

**Carry correction, Tern, 21 November.** This recovers the three immutable
artifacts from finish29746, whose later contribution was rejected at event
30018. The old checker rotated `z^(r+3)` modulo eight without multiplying
by `1+u` when `r+3>=8`, where `z^8=1+u`. The corrected checker includes
that carry: it adds the old R0 to R1 and the old R1 to R2 in output residues
0,1,2. At t=1, residue 2 is now `(R0,R1,R2)=(-4,-5880,-5738334)`.
The window bound and all-t refutation survive; their numerical examples
below are corrected. This repair does not accept or alter the other six
files of the rejected nine-file contribution.

Starting from immutable finish `29561` of run `e4c753e724c941c587d4ffff0f61eed9`
(which showed that all 25 compressed equations modulo `(z^8 - 1)^3` and all Schur
bounds at holes `H = [(1, 1), (2, 1)]` admit parametric witnesses
`TRIPLE_ROOT_WITNESS_BRANCHES` for every `t >= 1`), we establish exact
realizability criteria and structural obstructions on `E(z) = 0` that go
strictly beyond low-order `(z^8 - 1)^3` moment feasibility:

1. **Theorem 1 (`E_hi` high-degree localization & all-`t` refutation of the
   triple-root witness branches).** Every exact colouring on `H = [(1, 1), (2, 1)]`
   at `t >= 1` forces `E_hi(z) = z^{7560t} R(z)` with `R(z)` supported strictly on
   degrees `[13, 228]`, pinning `(1 + u)^{-945t} E_hi(z) mod (z^8 - 1)^3` inside
   explicit `t`-independent bounds `|R_{0,r}| <= 96`, `|R_{1,r}| <= 1586`,
   `|R_{2,r}| <= 14854`. Pippin's `TRIPLE_ROOT_WITNESS_BRANCHES` violates the
   `R_{1,r}` bound for **every single integer `t >= 1`**.
2. **Theorem 2 (`Phi_3` decoupling & `z_0^3 + z_0 - 1 = 0` real-root
   localization).** At `omega^2 + omega + 1 = 0`, `Im(E(omega)) = 0` eliminates
   arms 1 and 2 identically for every `t >= 0`, forcing
   `s_0 = sum_{k=1}^c chi_3(k) s_3(k)`. At the unique real root
   `z_0 in (0.682327803828, 0.682327803829)` of `z^3 + z - 1 = 0`, tip
   antisymmetry cancels the first 56 reversed terms of arms 1 and 2, forcing
   `|(2 z_0 - 1)(s_0 + S_3(z_0)) - z_0^c S_3(1/z_0)| < 3.2 * 10^{-9}` for `t >= 1`.
3. **Theorem 3 (Obstruction of unsynchronized periodic middle insertions).**
   Because `v_2(7560) = 3`, every unsynchronized periodic middle insertion of
   primitive periods `p_1, p_2, p_3 | 7560`, with fixed cuts and all holes
   confined to fixed prefixes, fails the reduced `Q^2` condition for large `t`.
   Moving suffix holes are not covered. Separately, finite rank computations
   for the particular support `H = [(1,1),(2,1)]` and the periods and cuts listed
   below certify only those templates, forcing every sign variable to zero.
4. **Positive controls (`H = [(1, 1), (2, 1)]` outside `3 mod 4`).** Infinite
   families `T(5 + 4k, 4, 2)` and `T(9 + 4k, 5, 3)` admit exact target-sized
   homometric pairs on `H = [(1, 1), (2, 1)]` for every `k >= 0`, showing any
   infinite obstruction of `H = [(1, 1), (2, 1)]` on the `3 mod 8` frontier must
   use its length residues.

## 1. Exact `E(z)` split and `E_hi` window bounds (Theorem 1)

Write `a = 227 + 7560t`, `b = 67 + 7560t`, `c = 11 + 7560t` (`t >= 1`), and
for `H = [(1, 1), (2, 1)]` put `S_1(z) = sum_{d=2}^a s_1(d) z^d`,
`S_2(z) = sum_{d=2}^b s_2(d) z^d`, `S_3(z) = sum_{d=1}^c s_3(d) z^d`.
Split `E(z) = E_lo(z) + E_hi(z)` where:

```text
E_lo(z) = s_0 (2z - 1 - z^a - z^b - z^c)
        + S_1(z)(z + z^-1 - z^-2) - z^a S_1(z^-1)
        + S_2(z)(z + z^-1 - z^-2) - z^b S_2(z^-1)
        + S_3(z)(2z - 1)          - z^c S_3(z^-1),

E_hi(z) = -(z^b + z^c) S_1(z) - (z^a + z^c) S_2(z) - (z^a + z^b) S_3(z).
```

Every term of `E_lo(z)` has degree `<= a + 1`. Consequently `E(z) = 0` forces
every coefficient of `E_hi(z)` at degree `>= a + 2` to vanish:

* **56 tip-antisymmetry equations** (`a + c + 1 <= d <= a + b`):
  `s_2(b - r) = -s_1(a - r)` for `0 <= r <= 55`.
* **160 four-term band equations** (`b + c + 1 <= d <= a + c`):
  `s_1(u + 160) + s_1(u + 216) + s_2(u) + s_3(u) = 0` for `7560t - 148 <= u <= 7560t + 11`.
* **`7560t - 150` six-term interior equations** (`a + 2 <= d <= b + c`):
  `s_1(u + 160) + s_1(u + 216) + s_2(u) + s_2(u + 216) + s_3(u) + s_3(u + 160) = 0`
  for `2 <= u <= 7560t - 149`.

Thus `E_hi(z)` is supported strictly in `[c + 2, a + 1] = [13 + 7560t, 228 + 7560t]`,
so `R(z) = z^{-7560t} E_hi(z)` has degree `<= 228`, nonzero terms only in
`13 <= d <= 228`, and coefficients bounded in magnitude by 4 (`<= 5` term sources).
Setting `z^8 = 1 + u`, writing `z^d = z^r (1 + u)^q` (`d = 8q + r`, `0 <= q <= 28`),
and summing the absolute term bounds over `[13, 228]` gives exact
`t`-independent bounds on `(1 + u)^{-945t} E_hi(z) mod (z^8 - 1)^3`:

```text
|R_{0,r}| <= [94, 94, 94, 94, 96, 94, 94, 94]
|R_{1,r}| <= [1550, 1550, 1550, 1550, 1586, 1456, 1456, 1456]
|R_{2,r}| <= [14448, 14448, 14448, 14448, 14854, 12992, 12992, 12992].
```

### Refutation of `TRIPLE_ROOT_WITNESS_BRANCHES` for all `t >= 1`

In `TRIPLE_ROOT_WITNESS_BRANCHES` (`t = t_0 + 4k`, `t_0 in {1, 2, 3, 4}`, `k >= 0`),
the quadratic coefficients of `Y(k)` satisfy `Y_{2, 1, r} + Y_{2, 2, r} + Y_{2, 3, r} = 0`
for every residue `r`. Hence `R_{1, r}(k)` is **exact affine-linear** in `k`
(`Delta^2 R_{1, r} == 0`). Direct evaluation at `k = 0, 1, 2` certifies across
every branch `t_0 in {1, 2, 3, 4}` that multiple residues satisfy both
`|R_{1, r}(0)| > max_r1[r]` and `R_{1, r}(0) * (R_{1, r}(1) - R_{1, r}(0)) >= 0`
(for example at `r = 2`: `R_{1,2}(0) = -5880, slope = -30512` for `t_0 = 1`;
`-6810, -16344` for `t_0 = 2`; `-24210, -30976` for `t_0 = 3`; and
`+17094, +16072` for `t_0 = 4`, all exceeding `1550`). Therefore no member of
`TRIPLE_ROOT_WITNESS_BRANCHES` is realizable by any `{+1, -1}` colouring for any
`t >= 1`.

The new independent check bypasses arm-series multiplication and residue
rotation. For each non-centre cell and each other arm, put
`q,r=divmod(first+L_other-7560t,8)` and subtract
`(X, qX+Y, binomial(q,2)X+qY+Z)` at residue r. It compares all three output
arrays on every parameter branch and at t=4,000,000. Since the shifted q
is independent of t, X is branch-constant, and Y is quadratic in k, the
quadratic coefficient of R1 is exactly `-2 sum_arm Y2` per residue. The
tests verify those eight coefficients vanish on each of the four branches;
the corrected intercepts and unchanged slopes therefore prove the all-t
claim rather than merely sampling it. The original seven tests plus these
two checks pass. The real sign-word problem remains separate; see
[WORD_REALIZABILITY.md](WORD_REALIZABILITY.md).

## 2. `Phi_3` decoupling and `z_0^3 + z_0 - 1 = 0` localization (Theorem 2)

For every `t >= 0`, `7560t == 0 (mod 3)` implies `a == 2`, `b == 1`, `c == 2 (mod 3)`.
At `omega = e^{2 pi i / 3}`:

* `z + z^-1 - z^-2 - z^b - z^c = omega + omega^2 - omega - omega - omega^2 = -omega`,
  while `-z^a = -omega^2`; thus `S_1` enters `E(omega)` as `-2 Re(omega S_1(omega))`.
* `z + z^-1 - z^-2 - z^a - z^c = -omega^2`, while `-z^b = -omega`; thus `S_2`
  enters `E(omega)` as `-2 Re(omega^2 S_2(omega))`.
* Both arms 1 and 2 vanish identically from `Im(E(omega)) = 0`, leaving
  `s_0 = sum_{k=1}^c chi_3(k) s_3(k)` (`chi_3(k) = +1, 0, -1` for `k == 1, 2, 0 mod 3`).

At the unique real root `z_0 in (0.682327803828, 0.682327803829)` of
`z^3 + z - 1 = 0`, `z_0 + z_0^{-1} - z_0^{-2} = 0`, suppressing `S_1(z_0)` and
`S_2(z_0)` by `O(z_0^c)`. Tip antisymmetry cancels `sum_{r=0}^{55} (s_1(a - r) + s_2(b - r)) z_0^r = 0`,
leaving `|(2 z_0 - 1)(s_0 + S_3(z_0)) - z_0^c S_3(1/z_0)| < 3.2 * 10^{-9}` for `t >= 1`.

## 3. Obstruction of unsynchronized periodic insertions (Theorem 3)

Suppose an infinite family for `T(227 + 7560t, 67 + 7560t, 11 + 7560t)` uses
fixed finite prefixes `P_i`, fixed finite suffixes `T_i`, and fixed cut depths
`(d_1,d_2,d_3)`. Every hole has fixed depth and lies in its arm's prefix;
there are **no holes in the moving suffixes or repeated blocks**. The centre
is retained. After depth `d_i`, insert `N = 7560t` signs by repeating a block
of primitive length `p_i | 7560`. Write that block as
`b_i(z) = sum_{j=0}^{p_i-1} epsilon_{i,j} z^j`, with every `epsilon` equal to
`+1` or `-1`. Put `B = lcm(p_1,p_2,p_3) | 7560` and expand each block to the
same length:

```text
C_i(z) = b_i(z) (1 + z^{p_i} + ... + z^{B-p_i}).
```

Each `C_i` has exactly `B` coefficients, all signs. The inserted word is
`z^{d_i+1} C_i(z) (Q-1)/(z^B-1)`, where `Q = z^N`. Multiplying the shell
identity `E_t(z)` by `z^B-1` gives a polynomial in `Q` with fixed Laurent
polynomial coefficients. For sufficiently large `N`, its three finite
coefficient supports are disjoint, so an exact family requires each to vanish.
Fixed prefix holes add no `Q^2` term. Finite suffix signs add `Q^2` terms
divisible by `z^B-1`, which vanish on reduction modulo `z^g-1`,
`g = gcd(B,8)`. The remaining high coefficient is
`-2 z^3 sum_i z^{d_i+1} C_i(z)` because all three base lengths are `3 mod 8`.
The ring `Z[z,z^-1]/(z^g-1)` is torsion-free and `z` is invertible, so the
necessary condition is:

```text
sum_i z^{d_i+1} C_i(z) == 0 (mod z^g - 1).
```

Because `v_2(7560) = 3`, `B / g` is always **odd**. Each residue class modulo `g`
in each expanded `C_i` therefore sums `B/g` signs, an odd integer. Multiplying
by a power of `z` permutes the residues; three odd integers cannot sum to zero.
This excludes the stated fixed-prefix family for every such primitive-period
triple and fixed cuts, with arbitrary fixed prefix/suffix signs.

Separately, `periodic_template_q_rank` builds all three coefficient systems for
`H = [(1,1),(2,1)]` and its **supplied** common period and cuts. At periods
`B in {8,16,24,32,48,64,100,150}`, for each of cuts `(2,2,1)` and `(171,11,11)`,
elimination modulo the prime `1000000007` gives full column rank. A nonzero
minor modulo that prime is nonzero over `Q`; thus these particular templates
have no nonzero rational solution. This is not a claim about every cut or
hole support, or every period with a larger power of two. Such an insertion
requires `B | 7560t` (for example, `B=16` restricts to even `t`).

### Why moving suffix holes must be excluded

Mica's example has common period eight, cuts `(0,0,0)`, holes
`(1,N+226),(1,N+227)`, and blocks `b_1=--------`, `b_2=++++++++`,
`b_3=--++--++`. Including the omitted vertices' distance terms changes the
reduced `Q^2` condition, up to an invertible monomial, to

```text
2 z^3 b_1(z) + (z + z^3)(b_2(z) + b_3(z)) == 0 (mod z^8-1).
```

This equality holds; finite suffix signs vanish from this reduced coefficient.
The independent interval-distance shell regression reconstructs the complete
polynomial at `t=1,2`, under two suffix/centre sign choices, and reduces its
high coefficient. It obtains eight zeros with these moving holes and nonzero
residues for the fixed-prefix control. The example's full shell polynomial is
nonzero: passing this necessary condition proves no homometric witness.

## 4. Surviving gap and open frontier

Neither the exact-lifting criteria above nor exhaustive checks on smaller
`3 mod 8` trees (`(19,11,3)`, `(27,11,3)`, `(27,19,11)`, `(43,27,19)`,
`(219,59,3)`, `(227,67,11)`) settle all-pairs existence for arbitrary
non-periodic sign assignments on `H = [(1, 1), (2, 1)]` (or other surviving
supports) when `t >= 1`. In particular, the remaining question includes:

* **For `H = [(1, 1), (2, 1)]` at `t >= 1`**: does there exist any
  `{+1, -1}` colouring satisfying the full identity `E(z) == 0`? This includes
  non-periodic words and templates outside Theorem 3. Every solution must
  satisfy simultaneously (i) `E(z) == 0 mod (z^8 - 1)^3`,
  (ii) the `E_hi(z)` window bounds `(96, 1586, 14854)` and 6-term band equations,
  (iii) `Phi_3` decoupling `s_0 = sum chi_3(k) s_3(k)`, and (iv) the `z_0`
  real-root bound `< 3.2 * 10^{-9}`? Settling that for all `t >= 1` (or for the
  remaining surviving supports in `LIFTING_FRONTIER.md`) remains open.

## Reproduce

From the repository root using only Python 3.10+ standard library:

```sh
python3 projects/almost-halving-three-branches/exact_lifting.py
python3 projects/almost-halving-three-branches/exact_lifting.py --refute-all-t
python3 projects/almost-halving-three-branches/exact_lifting.py --periodic-obstruction 16
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_exact_lifting.py
```
