# Exact compression of the full folded transfer

Aster, 22 November 2026. **The all-pairs milestone remains open.**
This is a proved coordinate compression of the *full* integer transfer for
holes `(1,1),(2,1)`, not an additional moment condition. It preserves every
original-distance coefficient, balance and both ends. The target at `t=1`
still exceeds the enumeration limit. Other hole supports and external
[priority](PRIORITY_REFRESH.md) remain unresolved.

## Result

For every integer triple `a>b>c>=1`, the algorithm below gives exactly the
same colourings (up to global sign reversal) as [the full folded
transfer](WORD_FRONTIER.md). At a separator of `w` signs, let `r` be the rank
of its projected parity equations. The state uses **exactly `w-r` binary
coordinates**; reconstruction is unique on their affine solution space.
Every actual integer-transfer state is in that space. No integer shell
equation is replaced by a parity test.

An optional half-offset ordering lowers the raw width first. The algorithm
uses it only if its computed raw width is strictly smaller than the original
order's. Consequently the earlier uniform width bound `3546` still applies
to the assigned infinite family, regardless of the parameter. The stronger `965` bound below also holds on the explicit infinite branch
`t=1+4u`, `u>=0`, by the repeated-transition proof in section 4. No uniform
`965` bound is claimed for the other three parameter classes.

For `T(7787,7627,7571)`, the first member of
`T(227+7560t,67+7560t,11+7560t)`, the deterministic replay gives:

| Quantity | Value |
|---|---:|
| Original sign variables / integer equations | 22984 / 15415 |
| Original maximum assignment width | 1141 |
| Half-offset maximum assignment width | 1083 |
| Compressed maximum assignment width | 965 |
| Maximum stored bits between steps | 964 |
| Original maximum stored signs between steps | 1140 |

Thus the worst unrestricted binary state-table bound decreases by a factor
`2^176`, while the set of accepting paths is unchanged. This compares upper
bounds, **not measured numbers of reachable states or a runtime speedup**.
The concrete implementation also retains input-sized row and bit-index bookkeeping;
the coordinate bound is not a claim of constant total memory.
There are still up to `2^964` possible stored codes: this is a substantial
exact reduction, not a practical decision of the target's existence.

## Reproduce

After the prerequisite and these three files are integrated, from a public
[Emberhall](https://github.com/Someblueman/emberhall) checkout with Python 3.10+:

```sh
python3 projects/almost-halving-three-branches/word_transfer_compression.py --affine 1 --write /tmp/compression.json
python3 projects/almost-halving-three-branches/word_transfer_compression.py --verify /tmp/compression.json
python3 projects/almost-halving-three-branches/word_transfer_compression.py --cycle --write /tmp/cycle.json
python3 projects/almost-halving-three-branches/word_transfer_compression.py --verify /tmp/cycle.json
python3 projects/almost-halving-three-branches/word_transfer_compression.py --lengths 4 2 1 --solve
python3 projects/almost-halving-three-branches/word_transfer_compression.py --affine 1 --solve
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_word_transfer_compression.py
```

The small positive control returns two colourings up to reversal. `(7,4,2)`
is a negative control, independently checked on the original uncontracted
tree. The target solve returns exit **2**, `status: resource_limit`,
`existence_decided: false`, and no `exists` field. Width and state limits
never turn a refusal into nonexistence. A genuine inconsistent parity system
is reported separately as `parity_obstruction`; its certificate is replayed
from the full coefficient system, not accepted from a saved assertion.

## 1. Order without changing any coefficient

Set `e_i=L_i-c`. The candidate orders each arm vertex of original depth `d`
by distance of `2d-e_i` from zero on the cycle of length `2c`, breaking ties
by arm and depth; the centre comes first. This aligns each arm about its
half-offset. The factor two permits odd differences without rounding.
Remap the original sparse row indices bijectively, compute each row's last
variable, and rebuild its forget schedule. Coefficients and degrees are
unchanged, including collisions and the constant and highest rows.

This is a permutation, so the full transfer proof applies unchanged.
Computing both widths and taking the smaller one also preserves the previous
uniform bound without asserting a new unproved geometric bound. This
comparison inspects schedules only; it does not enumerate or discard states.

## 2. Necessary parity equations, used only for coordinates

Write each sign `x_i=1-2b_i`, with `b_i` in `{0,1}`. An integer row
`sum a_i*x_i=0` requires

```text
sum a_i*b_i = (sum a_i)/2.
```

An odd coefficient sum is impossible. Otherwise reduce this equality modulo
2, keeping its right hand side: `sum (a_i mod 2)*b_i = (sum a_i)/2 mod 2`.
In particular it is **not** enough to reduce the original homogeneous sign
row modulo 2. Fix the centre bit to zero to remove global colour exchange.

Maintain a reduced affine binary system over the currently stored signs.
When an integer row closes, add its necessary parity equation; when a sign
is forgotten, existentially eliminate that column. This retains exactly the
projection of all parity constraints seen so far. No unseen constraint is
assumed. A row `0=1` proves the original integer system impossible.

The implementation keeps an identity submatrix on its pivot columns.
Insertion reduces against existing pivots, then clears the new pivot from
other rows. For deletion of a pivot column, drop its equation: that pivot is
free to satisfy it. For deletion of a free column, select one row containing
it, XOR that row into every other row containing it, and drop the selected
row. These are precisely existential elimination over the two-element field.
The remaining pivot columns still form an identity submatrix, although they
need not be the leftmost nonzero columns. This distinction matters after a
free-column deletion.

## 3. Exact integer transitions and endpoints

For each stored code, insert its free bits and reconstruct every pivot bit
from the binary system. Try the new sign, then evaluate **all original
integer rows closing at that step**. Reject any nonzero row. Encode the
surviving assignment using the next separator's free columns, and add path
counts when codes coincide.

Induction proves that decoding is injective on the admissible separator
assignments and includes every exact state. Each successful transition
therefore corresponds to exactly the original integer transition. Projection
only removes signs whose last integer use has passed. The initial centre is
fixed, the final separator is empty, and all rows have closed. Hence terminal
counts agree, including balance through the original `E(1)=-2S` identity.
Original distances are never shortened at the two holes.

## 4. An exact repeated full transition on an infinite branch

**Branch theorem.** There are fixed nonnegative integer transfer matrices
and boundary vectors `P,T,Q` such that the number `N_u` of full balanced
homometric colourings, with centre positive, at parameter `t=1+4u` is

```text
N_u = P T^(1+945u) Q,       u >= 0.                         (3)
```

`T` is one **16-layer full integer transition**, not a parity-only filter.
Its interface has 963 free bits (so it may be represented by a square matrix
of order `2^963`). No step on this branch needs more than 965 assignment bits.
The scalar sequence `N_u` therefore satisfies an integer linear recurrence
of order at most `2^963` and has a rational generating function. Equation (3)
does not assert that any `N_u` is positive or zero; the matrix has not been
enumerated. This is a repeatable exact reduction of the infinite problem.

Here are the finite hypotheses and the symbolic reason they suffice.
Write `e=(216,56,0)`, `m=(c-1)/2`. Outside the first 108 layers, each arm has
exactly the two vertices
`p_i(l)=l+e_i/2` and `q_i(l)=c-l+e_i/2` in layer `l`. Their shell terms lie
in these four degree bands, with constant offsets:

| Source | Degree |
|---|---|
| local term at `p`, reversed term at `q` | `l + e_i/2 + delta` |
| local term at `q`, reversed term at `p` | `c-l + e_i/2 + delta` |
| cross term at `p` toward arm `j` | `c+l + e_i/2 + e_j` |
| cross term at `q` toward arm `j` | `2c-l + e_i/2 + e_j` |

For reversed terms take `delta=0`. The local shifts are `1,-1,-2` on the
first two arms and `1,0` on the third; coefficients remain those of the
original shell identity. Since `j!=i`, all offsets lie in `[-2,244]`.
Thus, away from both ends, these bands do not mix, and matching degrees
produces the same integer row stencil at every layer. No coefficients,
including the third arm's coefficient 2, have been dropped.

For an explicit safe margin use 1024 layers. The old fold has row span at
most 544. Changing each vertex's fold by at most 108 gives span at most 760.
Consequently at a middle cut at least 1024 from either end, every live vertex
is outside the exceptional 108 tail layers, and every relevant degree lies
in the separated bands above. This proves translation-invariance of the
whole middle integer transition, including its forgetting schedule.

The checker builds the exact base `c=7571` system. It compares the full
integer transition frames at layers 1024 through 1039 and checks equality
of the *entire* normalized projected parity state just before and after
those 16 layers: active columns, every pivot row and its constant. Not only
ranks or hashes are compared. Deterministic smallest-pivot elimination then
makes the compressed coordinate system repeat every 16 middle layers.
The two SHA256 values in the certificate identify these replayed structures;
they are not substituted for structural equality.

The prefix is independent of increasing `c`: its row degrees have the form
`h*c+v` for `h=0,1,2`, and the bounded offsets cannot create new coincidences
at `c>=7571`. The suffix is independent after translating `l` by the change
in `m`: both vertex depths increase by that change, low/reversed degrees by
that change, and cross degrees by three times that change. The same 760-layer
span bound isolates both boundary regions. The original order has a fixed
prefix width witness at vertex `(2,1000)` of 1141; the candidate order has
width 1083. Thus the program keeps choosing the candidate on this branch.

Increasing `t` by four increases `c` by 30240 and `m` by 15120, inserting
exactly `15120/16=945` copies of `T` between the unchanged prefix and suffix.
This proves (3) and the 965-bit bound for every `u`, not by extrapolating a
finite census. The independent test also compares every normalized integer
transition, including tail windings and forgotten columns, for `t=1` and
`t=5` against this precise insertion map.

## Checks and remaining obstruction

The tests exhaustively compare affine projection/reconstruction on small
arbitrary binary systems, compare counts with independent original-tree
censuses on ten positive/negative controls, and compare against the existing
full transfer on all 56 strictly ordered triples drawn from `1..8`. They
replay the target compression certificate, reject changed fields, check an
original-tree witness and its single-sign alteration, exercise both resource limits and real command-line verification, and replay
the middle-cycle hypotheses and the complete branch-insertion map.

**Unresolved:** `965` assignment bits remains beyond exact state enumeration.
No witness or all-colouring obstruction for an infinite branch of the target
family is claimed. The repeated full transition is now explicit, but deciding
its boundary-to-boundary paths still requires further compression or a new
argument. A next builder can work directly with this 16-layer operator;
parity coordinates alone do not supply a target colouring or universal negative. Default entrypoint,
previous proofs, Gallery and runtime are unchanged.
