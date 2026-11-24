# A bounded joint-modulus allocation for every scale

Fern, 23 November 2026; project `small-after-sum-20261120`.
[Priority remains provisional](PRIORITY_REFRESH.md).

**Result.** For every integer k>=1, put t=2660k+1. On
T(99t,79t,23t), omit the two arm-1 vertices at depths 19 and 99t.
There are disjoint sets of size `(201t-1)/2` whose unordered pair-distance
histograms agree modulo **2660**, on the same colouring. The bounded
allocation is explicit below and independently recounted on actual vertices.

**This is not full homometry.** The recorded k=1 pair differs at distance
one. The even-hole pair from the task remains unresolved. The general
tripod milestone remains open; modular compatibility is not its acceptance.

## One command and a real run

After cloning the public repository containing this contribution and its
prerequisite, run with Python 3.10+; no added dependencies are required:

```sh
python3 projects/almost-halving-three-branches/t2661_joint_lift.py
```

Recorded k=1 output: `valid: true`, `size_each: 267430`, `modulus: 2660`,
`actual_counter: true`, `full_homometry_claimed: false`. The histogram hash
was `593635b45222c51c5650e5d079572c30f89ef266537c723b141d8f15fbb7e697`;
the actual run took 10.526 seconds under concurrent search load.
`--k 2` also passed the actual counter, with size 534760 and histogram hash
`8f61d01b7cce720f87d54a931f88e0ab33677528c6737fa70b7da67e8530c143`.
Its recorded run took 13.821 seconds. These are observations, not guarantees.

`--full` additionally recounts every original distance and reports the first
mismatch; at k=1 it reports `(1,-1)`.
`--output FILE` saves the negative class counts as JSON;
`--allocation FILE` independently validates such a prospective witness.
The default command constructs counts rather than reading a stored witness.

```sh
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_t2661_joint_lift.py -v
```

Integration prerequisite: Linnet's source contribution
`00058a865682afc57a69adb2449f60a77cea69d8`, run
`c4d6bb407010408d947e9ccf3ebf8b3a`, must be reviewed/integrated before these
files. This room's base predates it. Development used its inspected bytes
in a temporary import overlay; this contribution neither vendors nor
silently accepts that source. The implementation builds on its exact
[bounded reduction](T2661_JOINT_RESIDUE.md), [seed and lifting lemma](T2661_SAME_PARITY.md).

## Construction, bounds and proof for every k

Write P=2660, B=(99,79,23). Use the existing exact FRONTIER witness on
T(99,79,23), centre negative and holes at depths 19 and 99. Its two sets
have size 100. This is the previously recorded seed, not a new claim.

Insert `P*k*B_a` vertices after cuts (19,0,0), preserving original order.
Original vertices keep their depth residues modulo P. Partition occupied
vertices into the predecessor's interval/depth-residue classes. The centre
and the 18 vertices before the first hole are singleton **tiny classes**.
Every arm has exactly one further, **large**, class for each residue r.

Let n0_j count seed vertices in class j, and m0_j its seed negative count.
Both are zero or one. On a large arm-a class set d_j=B_a; on a tiny class
set d_j=0. The actual population is exactly `n_j=n0_j+k*d_j`.
For the large classes define `s_j=(-1)^r`; for tiny classes put s_j=0.
Let epsilon be k modulo two. The construction is

```
x_j = m0_j + (k*d_j + epsilon*s_j)/2.
```

Each x_j is the number of negative vertices in that class. Choose its
first x_j vertices in increasing depth; all remaining occupied vertices
are positive. The centre stays negative. Tiny classes retain their seed
signs. The groups are disjoint and omit exactly the stated two holes.

**Integrality and bounds.** Every large d_j is odd. If k is odd, the two
odd terms in the numerator sum to an even number; if k is even the
correction vanishes. In both cases
`0 <= (k*d_j+epsilon*s_j)/2 <= k*d_j`. Since `0<=m0_j<=n0_j`, every bound
`0<=x_j<=n_j` follows, including the singleton bounds.

**Seed contribution.** Every inserted arm segment consists of complete
residue cycles. An old vertex gains exactly `k*sum(B)=201k` neighbours in
each distance bin, independently of its position. Distances between old
vertices retain their residues. The seed's balanced homometry therefore
implies `A m0=A n0/2` in the new exact system A, including balance and anchor.
This argument does not assign colours to the insertions yet.

**Alternating kernel.** In fact the vector s supported on each individual
large arm is in the integer kernel of A. Work modulo `z^P-1` and put
`E(z)=sum_(r=0)^(P-1) (-1)^r z^r`. Then `zE=-E`, `E(z^-1)=E(z)` and the
coefficient sum of E is zero. All three arm lengths and both hole depths
are odd. In the cyclic derivative column formula, the `2z` term vanishes
after summing its alternating weights. The remaining occupied-tree terms
are:

- `z^(depth+1)`: -E;
- the two cross-arm endpoint terms: -2E;
- the reversed own-arm endpoint term: -E.

Their total is -4E. Each omitted vertex contributes `(z-1)` times its
weighted distance polynomial. That polynomial is -E, whether the distance
is `depth+h`, `depth-h` or `h-depth`, because h is odd and E is invariant
under reversal. Each hole therefore contributes +2E, cancelling -4E.
On arm 1 all large classes lie between the holes, so these distance forms
do not change within their interval. On the other arms both holes are
cross-arm distances. Thus every cyclic derivative is zero.

Balance is zero because E has coefficient sum zero. The weighted shell
histogram is consequently constant, and its sum is `(N-1)*sum(s_j)=0`,
where N is the number of occupied vertices. Over integers that constant
must be zero; in particular the anchor is zero. This proves `A s=0`,
including the constant cyclic mode, without relying on finite-field rank.

Finally `A x=A n0/2+(k/2)A d+(epsilon/2)A s=A n/2`.
The exact reduction gives equal sizes and all joint distance bins. There
are `201t-1` occupied vertices, giving the asserted size per set. At even k
the correction is zero: that special case is already supplied by Linnet's
anti-paired lifting lemma. The alternating correction is what handles odd k.

## Independent actual pair counter and the full-distance boundary

The counter builds literal selected-vertex indicator polynomials F_a.
Same-arm positive distances are coefficients at `L_a+d` of
`F_a(z) z^L_a F_a(z^-1)`. Cross-arm distances are coefficients of `F_a F_b`.
A selected centre contributes each selected arm depth once. Only then
are actual distances folded into residue bins. This counter uses neither
sparse shell columns nor their derivative/anchor formulas.

Fixed-width byte packing and Python integer multiplication implement exact
convolution. The radix exceeds the total vertex count, while each individual
coefficient is at most that count; no carry can mix coefficients. The
unordered total-pair identity checks that no pair was lost. Exhaustive
small tests compare with literal unordered-pair enumeration, including
unequal arms, positive-lag orientation and a same-size altered allocation.

A separate actual full-distance run at k=1, using modulus 473659 (larger
than the diameter), found 473656 unequal distances. The first is distance
one, with positive-minus-negative pair-count difference **-1**. Thus this
specific pair is demonstrably not homometric. Earlier mod-4-only witnesses
remain useful negative controls: the new counter reproduces their equal
mod-4 bins but finds 2659 unequal joint bins at k=1.

## Additional exact restrictions and retained search limits

`--refine --parity odd` or `even` performs a complete modulo-four extension
test on all parity branches. For every left-nullspace basis vector lambda
of A modulo two, form the exact integer consequence
`D=(lambda A)/2`, `d=(lambda b)/2`. A bit vector u extends modulo four iff
`A u=b (mod 2)` and `D u=d (mod 2)` for all these dependencies: apply the
left-nullspace solvability criterion to `A v=(b-Au)/2 (mod 2)`.
Source bitsets reconstruct each divided row exactly. Both k=1 systems have
7999 classes, four derived rows, and consistent rank increasing 2658 to
2659; exactly half the initial parity branches survive. The predecessor's
chosen odd branch fails all four new rows; its even branch passes them.

`--branch` probes one explicit prefix with upper-bound-zero variables fixed
at every lift. Its checked parity dual rejects the chosen prefix only.
The predecessor's even prefix passes levels 0–3 and fails at level 4, with
a 1329-row dual; upper bounds were 100,50,25,12,6. This is not an obstruction
to its other kernel choices, the even hole pair, or the construction above.

Before the explicit construction, installed OR-Tools 9.15.6755 searches used
midpoint-radius domains `max(0,floor(n/2)-r)..min(n,ceil(n/2)+r)`, floor hints,
seed 123. Odd holes, radius 2/one worker/120 seconds returned UNKNOWN (708
branches); radius 10/four workers/600 seconds, linearization 0, randomized
search, centre fixed zero returned UNKNOWN (2078 branches). SciPy 1.18.0
HiGHS on full even-hole bounds, zero objective, integral variables and a
120-second limit had no incumbent. Z3 4.16.0 on even-hole midpoint-only
bounds with the four derived equations returned unknown (requested timeout
120 seconds; observed check 423.33 seconds). None supplied an obstruction.
An even-hole radius-zero, one-worker, linearization-zero CP-SAT run also
returned UNKNOWN after 600 seconds (44355113 branches); it did not affect
the analytic odd-hole construction. These packages are research history,
not dependencies of the delivered result.
