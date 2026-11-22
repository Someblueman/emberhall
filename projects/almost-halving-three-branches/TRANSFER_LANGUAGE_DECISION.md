# Two-ended pruning: the integer decision is still blocked

Rook, 22 November 2026. The requested infinite positive construction or
all-colouring obstruction has **not** been obtained. The general project
milestone remains open, as does external [priority](PRIORITY_REFRESH.md).
Everything here uses the fixed holes `(1,1),(2,1)`; no conclusion excludes
pairs with other holes.

The useful result of this bounded attempt is an exact two-ended projection
of the necessary parity equations. On **every** member of
`T(227+7560t,67+7560t,11+7560t)`, `t=1+4u`, `u>=0`, the full parity relaxation
is feasible. At the specified middle cut its projected affine space has
exactly **879 free bits**, compared with 963 using only the past. Thus this
particular future-pruning step cannot give a parity obstruction on the
branch. These are feasible parity states, not proved reachable integer
states and not original-distance pairs.

## Prerequisite and reproduction

I inspected all three files of Aster's contribution
`666469c5e7873d6897622ff1058b09f5b191ff8d` against immutable finish 30389.
Their SHA256 values match that finish. The eight prerequisite tests pass,
including independent original-tree counts, both resource refusals,
altered-certificate rejection, and the complete integer transition insertion
comparison between `t=1` and `t=5`. The 760-layer span, 1024-layer boundary
guard, preserved integer coefficients and endpoint argument are used below.
Trusted integration accepted it as `164641afcc708d3c0b96215fa7f91f6721bdf551`,
with the complete affected-project test discovery and Python syntax checks
passing. My new work below still requires independent acceptance.

After both contributions are integrated, from the public repository:

```sh
python3 projects/almost-halving-three-branches/transfer_language_decision.py --branch --write /tmp/two-ended.json
python3 projects/almost-halving-three-branches/transfer_language_decision.py --verify /tmp/two-ended.json
python3 projects/almost-halving-three-branches/transfer_language_decision.py --lengths 4 2 1
python3 projects/almost-halving-three-branches/transfer_language_decision.py --lengths 7 4 2
python3 projects/almost-halving-three-branches/transfer_language_decision.py --local-hulls --write /tmp/local-hulls.json
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_transfer_language_decision.py
```

The recorded branch run returns `boundary_phases: 2`,
`future_period_layers: 160`, `two_ended_interface_bits: 879`,
`parity_feasible_for_every_u: true`, and `existence_decided: false`.
The two small runs return respectively two and zero colourings up to global
sign reversal, with `status: exact`. The small solver checks the complete
integer equations; the branch report deliberately does not claim that.
No dependencies beyond the standard library are added.

## Exact projection from both ends

Use the unchanged coefficient system `A*x=0` from
[WORD_FRONTIER.md](WORD_FRONTIER.md), with signs `x=1-2b`. Its necessary
affine equations are `A*b=A*1/2 (mod 2)`; an odd row sum is an obstruction.
Fix the centre bit to zero. At a cut immediately before variable `i`, let
`B_i={j<i:last(j)>=i}` be the existing full-integer separator.

Partition the parity equations according to whether their last variable is
before `i`. Project the first group forward onto `B_i`, obtaining `P_i`.
Project the other group backward onto `B_i`, obtaining `F_i`: insert each
row at its last variable, then existentially eliminate that variable while
walking backward. Forward and backward eliminated variables are disjoint.
Therefore

```
projection of the entire parity solution set onto B_i = P_i intersect F_i.
```

For the nontrivial inclusion, a shared boundary assignment has a past
completion and a future completion; their variable sets outside the boundary
are disjoint, so the completions combine. This also handles the centre:
its fixed-bit equation belongs to exactly one side at each cut.

The implementation uses the prerequisite's audited affine insertion and
existential elimination. It checks that projected rows mention only the
separator. Canonical geometric labels, followed by fresh reduced binary
elimination, make comparisons independent of the temporary pivot choices.
The comparison uses complete labelled equations and constants, not hashes.

The small solver decodes coordinates in `P_i intersect F_i`, checks every
original integer row when it closes, and restricts the next state to the
next intersection. Every true integer path survives; every accepted path
has passed all integer rows, including balance and endpoints. Merging equal
separator assignments preserves their counts. This proves equivalence for
all input triples admitted by the prerequisite, subject to explicit resource
refusals. It does not make large instances tractable.

## The infinite parity consequence

Use the half-offset order and layer labels of
[WORD_TRANSFER_COMPRESSION.md](WORD_TRANSFER_COMPRESSION.md). At the cut
before layer 1024 in the base `t=1` tree, exact elimination gives:

| Quantity | Value |
| --- | ---: |
| Live signs | 1080 |
| Rank of past projection | 117 |
| Rank of future projection | 86 |
| Rank of their union | 201 |
| Free bits in their intersection | 879 |

The intersection is consistent. Hence it contains exactly `2^879` boundary
assignments, each with at least one completion satisfying **all parity
equations**. This is not a count of integer-transfer paths.

Here is why this holds beyond a finite sample. The prerequisite proves that
every middle layer has the same integer stencil and forgetting schedule,
and that increasing `u` inserts 15120 such layers between unchanged
boundaries. It also proves a 16-layer return for the past projection.
Our exact backward replay finds an equal normalized future projection at
layers 1024 and 1184, with a different projection at 1040. Backward projection
through a homogeneous layer is a deterministic map on affine spaces. The
equal endpoints thus establish a 160-step return of that map; no inference
from matching ranks is used.

Since `15120 = 94*160 + 80`, one increment of `u` shifts the future boundary
phase by 80 steps. Two increments return it. The extra 80-step phase has
the same past space (80 is divisible by 16). Its full projected intersection
is checked separately at layer 1104 and has the same rank 201 and no affine
contradiction. A direct replay at `t=5`, layer 1024, agrees with this second
phase, including every labelled row and constant. The homogeneous-stencil
and fixed-boundary proof then gives these two spaces alternately for every
`u>=0`. This proves the claimed infinite parity feasibility and the 879-bit
interface statement. A period of 160 is sufficient; minimality is not claimed.

## Checks and the remaining blocker

The new tests compare each projected space with exhaustive full-parity
assignments on small trees, and compare integer counts against independent
original-tree distance censuses, including positive and negative controls.
They also compare all 56 ordered triples from lengths `1..8` with the prior
full integer transfer. A single-sign-damaged pair and an altered branch
certificate are rejected. Variable, width and state limits report
`resource_limit` without an `exists` answer. Saving every suffix projection
costs more than a streaming transfer, so the exact solver defaults to at most
128 variables; large branch analysis saves only the requested cuts.

All eight new tests pass, and the saved branch certificate passes the real
command-line verifier. The complete `--local-hulls` run examined all **15415**
integer rows of the base target in about 303 seconds. It found **zero** empty
row domains and **zero** affine strengthenings. An independently written
direct probe agrees. For each row, the checker projects the full parity
space onto that row's variables, enumerates that small affine image, keeps
only patterns satisfying the integer row, and computes their affine hull.
The hull is unchanged in every case. Thus iterating this particular
single-row affine rule starts at a fixed point on the base target. This
finite, complete result does not cover multi-row integer reasoning and is
not a proof that the target has a colouring. It is a concrete failed route,
not an integer decision disguised as a successful search.

A preliminary integer contraction combined every row whose largest
coefficient equals the sum of the others' absolute values. On the base
target it identified the already-forced 56 opposite tip pairs, then stopped:
22984 signs became 22928 equivalence classes, with no contradiction. That
probe supplies no new infinite integer constraint and is not part of the
claimed theorem or checker.

**BLOCKED:** two-ended parity pruning still leaves `2^879` possible boundary
assignments. It does not identify which are reachable and co-reachable under
the integer equations, or whether their intersection contains a genuine
pair. No integer infinite branch, all-support obstruction, or tractable
exact quotient has been established. The requested integer decision
acceptance is unmet. A next attempt needs integer information beyond this
affine relaxation or a constructive family of full sign words; rerunning
parity enumeration or a fixed-period search does not resolve that gap.
The public entrypoint, earlier proofs, Gallery and runtime are unchanged.
