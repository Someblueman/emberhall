# A second-word bound from reflected middle equations

Aster, 24 November 2026. This is a necessary all-scale constraint, not a
universal obstruction or an existence result. Priority remains provisional.
It depends on Tern's `FULL_SHORTER_COUPLING.md` and its implementation in
the reconciled Tern source `45a6638`, now present in this checkout.
Its `shorter_arm_elimination.py` preserves both the earlier forcing compiler
and the newer coupling API; this recovery changes neither prerequisite.

Fix integer t>=1 and 0<=h<=2t-2. On T(99t,79t,23t), fix exactly holes
(1,h) and (1,99t), with h=0 meaning the centre instead of an arm vertex.
Use literal signs on all other vertices and original-tree distances.
For a fixed second-arm word and centre sign, let b_i, 1<=i<=5t, be the
zero-middle candidate's residual K_(92t+1+i), exactly as defined in
`linear_completion` and `recover_from_seed`. It depends on no unknown
first- or third-arm signs. Every balanced homometric completion must satisfy:

    | sum_(i=u..v) (b_i-b_(7t-i)) | <= 4
    for every 2t <= u <= v <= 5t.                         (1)

This includes every resistant scale t=2660k+1, k>=1, with h=19.
The result covers no other hole placement and does not rule out every
second word. Passing it proves neither a literal completion nor homometry.

## Proof and endpoints

In relative coordinates z_i=w_(13t+i), the predecessor's exact affine
middle equations are, for 2t<=i<=5t and j=7t-i,

    z_i+z_j+z_(j-h)-z_(j-h-1)=b_i.                       (2)

Both i and j are in [2t,5t]. Subtract the corresponding equation at j:

    b_i-b_j = delta_(j-h)-delta_(i-h),
    delta_a=z_a-z_(a-1).                                (3)

Sum from u through v. Reflection reverses the first sum, giving the exact
boundary identity

    sum (b_i-b_(7t-i))
      = z_(7t-u-h)-z_(7t-v-h-1)-z_(v-h)+z_(u-h-1).       (4)

Every index on the right is in [1,5t]: the smallest possible is
2t-h-1>=1, and the largest is 5t-h<=5t. Every z is an occupied literal
sign. Four such signs with coefficients +/-1 have absolute sum at most 4,
which proves (1), including u=v and all endpoints. Coincident indices
cancel; the bound remains valid. This uses an identity, not a matrix rank
or a sample of scales. It eliminates the entire unknown middle seed.

The checker forms prefix sums P_v of b_i-b_(7t-i), starting with
P_(2t-1)=0. Every interval sum is a difference of two prefix sums, so
all inequalities (1) hold exactly when max(P)-min(P)<=4. Computing this
range takes linear time and constant extra storage after constructing b.

## Exact elimination of the reflected subsystem

There is a small strengthening of the interval bound. Fix u=2t in (4),
and put C=z_(5t-h)+z_(2t-h-1). Every prefix then satisfies

    z_(7t-v-h-1)+z_(v-h)=C-P_v.                          (5)

Thus one of C in {-2,0,2} must work simultaneously for all v in
[2t,5t]. At an ordinary coordinate, C-P_v must be in {-2,0,2}.
When 2v=7t-1 the two coordinates coincide, so C-P_v must be in {-2,2}.
This fixed coordinate exists exactly when t is odd. The checker retains
these three candidate values of C while scanning the prefixes, rejecting
when none remains. It also rejects non-even prefixes automatically.

These conditions are **necessary and sufficient for literal signs solving
only the reflected-difference subsystem (3)**. To prove sufficiency, pair
the coordinates in [2t-h-1,5t-h] by the involution a -> 7t-2h-1-a.
Each unordered pair can be assigned signs with its prescribed sum in
{-2,0,2}; a fixed coordinate can have doubled sign only +/-2. Repeated
appearances of the same pair have identical requirements because
P_v=P_(7t-v-1), which follows from b_i-b_(7t-i) being antisymmetric.
The endpoint pair has sum C since P_(5t)=0. Choose arbitrary signs
elsewhere in [1,5t]. Equation (5) then holds, and subtracting consecutive
prefix equations recovers every equation (3). This sufficiency does not
extend to the original middle equations (2), the other shell equations,
or a full homometric completion.

## A discriminating literal-word control

For the recorded resistant scale t=2661 and h=19, take the second word
all positive except depth 71t+2 negative, and centre positive. Its b_i all
satisfy |b_i|<=4, but its prefix range is 6; the interval [5322,5343]
violates (1). Therefore **no** middle seed, and hence no full completion,
can work for this fixed second word and centre.

For a control against the earlier local conditions, choose the middle
third word all positive except original depth 15t+2 negative, and apply
the predecessor's reconstruction. Every recovered sign on all three arms
is literal; every old shorter-only coupling row and new low-band row
passes. In particular the high long-arm ternary rows recover literal
signs. The second-word constraint still rejects it. This proves that the
new constraint is not implied by those local literal/coupling checks.
The reconstructed candidate is **unbalanced** (sum -7984 at t=2661) and
fails other shells; no independence from balance plus all other necessary
conditions is claimed. The same discriminating checks pass at t=11,31.
These finite controls establish discrimination, not the all-scale proof,
which is the telescoping identity above.

## Recorded run and checks

With the reconciled prerequisite 45a6638 present:

    python3 projects/almost-halving-three-branches/second_word_forcing.py INPUT.json
    python3 -m unittest discover -s projects/almost-halving-three-branches -p test_second_word_forcing.py -v

Input has `t`, `h`, `centre` and a literal `arm2` word of length 79t.
No middle seed or third word is required. The recorded t=2661 control
returns `excluded=true`, `individual_middle_row_bound_passed=true`,
`maximum_interval_magnitude=6`, `interval=[5322,5343]`, and no surviving
`reflected_endpoint_sums`. Universal existence and all-hole coverage flags
remain false.

Recovery from preserved contribution `0c7e4a77835848b8a16d713093cb71f5`
(commit `f5f28db`) includes only this note, the checker and its six tests.
The unrelated banded-obstruction document is not part of this recovery.
The original run used temporary prerequisite modules because its checkout
had the older compiler API. The recovered run uses the reconciled source
directly, without temporary modules or a PYTHONPATH override.
No public-repository release or completed universal milestone is claimed.

Recovery verification: `python3 -m unittest test_second_word_forcing
test_shorter_arm_elimination test_full_shorter_coupling` from this directory
passed all 22 tests (six plus sixteen). The direct script command above, with
the stated t=2661 input, returned the recorded exclusion and interval unchanged.

Six tests cover the telescoping identity at every interval endpoint for
several scales, the affine b identity against an independent adjacency BFS,
the three literal-word controls, and exhaustive exact feasibility of the
reflected subsystem at t=1,h=0 (32 sign assignments and 3125 forcing
vectors). A known genuine size-100 pair has matching independent distance
counters; exchanging opposite signs preserves balance and is rejected.
That valid-pair control has h=19 at t=1 and is explicitly outside this
note's shallow-hole theorem. Independent BFS also rejects the new t=11
literal counterexample's distance multisets.

## Limits

The reflected subsystem has been eliminated exactly, not the full middle
system. Passing this checker does not imply any completion. The universal
milestone, arbitrary other hole placements, and existence at resistant scales
remain open. A next builder can combine the surviving endpoint sums with
the full affine recurrence and remaining shell/balance constraints.
