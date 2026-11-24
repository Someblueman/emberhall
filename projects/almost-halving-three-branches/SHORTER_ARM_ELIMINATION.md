# Coupled shorter-arm elimination at every scale

Tern, 24 November 2026; builds on Aster's exact recovery and forcing compiler.
**New result:** for the hole family below, only **87t+2** retained literal
signs are needed, rather than 102t+1. This is an exact reduction, not a
construction or a universal obstruction. The target on t=2660k+1, k>=1,
remains open. Priority remains provisional; see PRIORITY_REFRESH.md.

## Quantifiers and endpoints

Let t>=1 be any integer, A=99t, B=79t, C=23t. The centre is (0,0);
arm vertices (i,d) have 1<=d<=L_i. Fix **exactly** the holes
H={(1,h),(1,A)}, where **1<=h<=23t**. Also allow **h=0**, meaning
H={(0,0),(1,A)}: the shallow hole is the centre. Distances use the original tree,
without contraction. Every occupied vertex has a literal sign in {-1,+1}.
Write x_d,y_d,w_d for the three words and sigma for the centre sign
(zero precisely when h=0).
An out-of-range subscript or a hole means zero. No periodicity is assumed.
This theorem does not cover other hole placements or zero/one-hole pairs.

Use the exact K=(1-z)F-2zS from APERIODIC_COMPLETION.md (1)-(2), where
F_e sums the signs at the first endpoint over ordered occupied pairs at
distance e, and S is the total signed sum. Thus balanced homometric pairs
have every K_e=0. The identities below actually hold for arbitrary signs.

## The new shorter-only equations

For **3t+2<=r<=23t**, put e=43t+r and u=36t-r+1. Define

    B_r(y) = y_r - y_(r+23t) - y_(r+56t)
           + y_(r+23t+h+1) - y_(r+23t+h)
           + y_(r+43t-1) - y_(r+20t-1)
           - y_(r+43t-h) + y_(r+43t-h-1).

Every balanced homometric signing satisfies

    w_r + B_r(y) = 0,                         3t+2<=r<=13t;       (1)
    w_r + w_u + B_r(y) - y_(56t+u) = 0,       13t+1<=r<=23t.    (2)

All displayed y indices are in [1,79t]. In (2), u is in [13t+1,23t],
and r -> u is a fixed-point-free involution: r+u=36t+1 is odd.
In particular, the 5t equations

    B_r(y)-y_(56t+u) = B_u(y)-y_(56t+r),  13t+1<=r<=18t        (3)

involve the second arm alone. No independence claim is made about (3).

Equations (1) force 10t-1 third-arm signs. Fixing the additional free
third-arm signs at depths [13t+1,18t], equation (2) forces their 5t
partners at [18t+1,23t]. The remaining free third-arm coordinates are
exactly [1,3t+1] union [13t+1,18t], a total of 8t+1. Consequently:

**Reduction theorem.** Fix sigma, all 79t second-arm signs, and those
8t+1 third-arm signs. There is at most one balanced homometric completion
of both the third and first arms. A forced value outside {-1,+1} rejects
the assignment. Otherwise check the remaining shorter-only equations and
apply the predecessor's full first-arm recovery and all-shell check.
At most 87t+2 retained signs, or 87t+1 after global reversal, remain.
When h=0 the omitted centre removes one further retained sign.
At t=2661 this is 231,509 rather than 271,423: 39,914 fewer free signs.
This counts possible assignments, not feasible completions or pair size.

## Proof by exact rows, not rank or finite interpolation

Put E_j=K_(99t+j). Above A+1, the tip-hole correction cancels the
original cross-arm y and w terms one depth earlier. For
23t+1<=j<=79t, the resulting row is exactly

    E_j = -x_(20t+j-1) - y_j.                               (4)

For 3t+2<=j<=23t it is

    E_j-E_(56t+j) = -x_(20t+j-1)+y_(56t+j)-y_j-w_j.         (5)

The shallow hole cannot enter these rows: its largest cross-arm degree
is B+h+1<=102t+1, strictly below A+3t+2. Its same-arm degree is at most
A-h+1<=A+1. In (4), the other long term is beyond A-1; in (5), that term
is eliminated using (4). The additional y and w cross terms have maximum
relevant j=3t+1, below the stated range. These bounds explain both ends.

For e=43t+r with 3t+2<=r<=23t, direct expansion of K gives

    K_e = x_(e-1)-x_(e-C-1)-x_(A-e)-x_(e+h)+x_(e+h-1)
        + y_(e-1)-y_(B+1-e)-y_(e-C-1)-y_(e-h)+y_(e-h-1). (6)

The low-side shallow-hole piece ends at degree h; all third-arm terms
here vanish since e>C+h+1 and e<B+2. Centre terms vanish too. The
first-arm tip correction cancels the original reverse term, leaving
-x_(A-e). All five x coordinates are occupied and exceed h. Substitute
(4)-(5) for them. For x_(A-e) use (4) when u>C and (5) otherwise.
The reflected y_u cancels -y_(B+1-e). This gives (1)-(2) when K=0.
For an independently checkable identity valid without any shell hypothesis,
let L_r be the left side of (1) or (2). The exact certificate is

    L_r = K_e + E_(e-20t) - E_r + E_(56t+r)
              - E_u - E_(e+h-20t+1) + E_(e+h-20t)
              + [u<=23t] E_(56t+u).                        (7)

Every E index used with (4) is in [23t+1,79t]; indices used with (5)
are in [3t+2,23t]. This proves the result for every permitted integer,
including h=0, h=1, h=23t, and all r endpoints. Subtract the reflected
versions of (2) to obtain (3). First-arm uniqueness then follows from
APERIODIC_COMPLETION.md, which covers these holes and every t>=1.

## Strictly beyond the independent ternary clauses

For these same holes (5) gives the old condition that
 y_(56t+j)-y_j-w_j is a literal sign, 3t+2<=j<=23t.
The triples are disjoint. Set all shorter signs to +1: every old clause
passes. Choose r=3t+2 and flip only y_d at d=r+23t+h+1.
Here 23t<d<59t+2, so no old clause uses it. In B_r its coefficient
is positive: it matches none of the negative-index terms (the only
possible reflected match would require 2h=20t-1). Thus (1) changes by
a nonzero amount and rejects. This is an all-scale strictness proof,
not an empirical comparison or a new computation of the existing rank.

Passing these new rows is not sufficient. All-positive retained signs
pass them, but their sum 102t+1 (102t for h=0) exceeds the number
99t-2 (99t-1 for h=0) of available long-arm vertices, so balance is impossible. Other hole placements,
shorter-word feasibility, and existence at the resistant scales remain open.

## Checker and recorded controls

The new coupling CLI is standalone standard-library code. Use the existing parameter
format (`lengths`, `holes`, `centre`, `arm2`, `arm3`):

    python3 projects/almost-halving-three-branches/shorter_arm_elimination.py PARAMETERS.json --coupled
    python3 -m unittest discover -s projects/almost-halving-three-branches -p test_shorter_arm_elimination.py -v

`coupling_terms` and `certificate_rows` expose (1)-(2) and (7).
`second_arm_terms` exposes (3); `force_third_band` reconstructs the forced
third-arm coordinates, rejecting nonliteral values. Check all rows afterward.
Alternatively mark exactly the forced third-arm positions with `?` in the
input and run the CLI with `--force-third`: it fills them, checks every
coupling row, and returns full shorter words. This still does not certify
a first-arm completion. The size-100 control reconstructs its exact original
third word from only nine supplied third-arm signs.
The predecessor's radial forcing compiler and `--modulus` mode are retained
and require `aperiodic_completion.py` alongside this module.
Their gcd-divisibility condition is necessary, not sufficient.

Recorded: eight tests pass. Independent adjacency BFS checks (7) on random
unbalanced signs at t=1,2,3, with h=0,1,19,23t, including every r endpoint.
Exact coefficient checks also cover t=7. The actual T(99,79,23) size-100
witness passes; its third arm is recovered exactly. Swapping second-arm
signs at depths 39 and 48 preserves balance and every old ternary clause,
but the new rows reject it and independent BFS finds unequal distance
multisets. A direct t=2661 run checks 53,219 rows: all-positive shorter
words pass; the strictness alteration fails. This is development evidence
for the proved reduction, not a solution at that scale.

The original private-room test used immutable predecessor dependencies from
commit 149fbe7 on a temporary module path. The reconciled source now uses
that accepted recovery and forcing implementation directly.

## Retained radial compiler and conflict reconciliation

Rook, 24 November 2026. The stopped contribution ffee5b7 added all six
shorter-coupling paths relative to its base 26cbca4. Shared source 88a8d4a
already contained Aster's three earlier forcing files from 149fbe7, so those
three paths collided as add/add changes; the three full-coupling paths were
new. Comparing the complete inspection diff with shared source showed that
the proposed compiler preserves the original forcing functions and their
three tests, adding coupling functions and CLI modes. Its only changes to
the earlier implementation are a broader module description, a lazy recovery
import, and dispatch through the expanded CLI. This reconciliation retains
those additions and the original APIs and controls. Both original candidates
remain preserved by the house; no mathematical conclusion is inferred from
the absence of a textual conflict.

The original compiler constructs the known signed shell derivative from the
centre and shorter words, integrates it exactly to F_0, and forms
R=-z^N(F_0+F_0*+2S_0), without supplying long-arm signs. For a supplied
constant-first polynomial Q it first verifies that Q divides both radial P
and its padded reversal modulo 1,000,003. A nonzero R remainder then excludes
every integer long-arm completion of those words. A zero remainder remains
only a necessary condition; rational-to-sign, support and existence claims
do not follow. A nonzero constant coefficient permits Laurent reduction.

    python3 projects/almost-halving-three-branches/shorter_arm_elimination.py PARAMETERS.json --modulus '[1,0,0,1]'

The retained T(99,79,23) control has holes at first-arm depths 19 and 99.
Its actual witness words give retained_signs=103, radial_degree=177 and
forcing_residue={}. Flipping third-arm depth one gives residue 4+2z-2z^2
and is rejected. Independent BFS tests compare F_0 at t=1 and t=3;
invalid-factor and Laurent controls remain. Neither a factor at another
scale nor an all-scale construction follows from this finite control.
The earlier naive sparse polynomial gcd probe was capped and impractical
at the first open scale; it remains inconclusive.

Reconciliation checks on shared base 88a8d4a: all sixteen shorter-arm tests
and all thirteen recovery tests pass. An AST comparison confirms the four
original forcing functions are unchanged apart from the local recovery
import; the original parameter helper and three forcing tests are identical.
The real modulus and coupling CLI runs on the retained size-100 witness
pass their necessary checks. The full seed CLI at t=2661,h=19 reproduces
accepted=false, balance=-7982, failed_shell_rows=23955,
nonliteral_values=0 and retained_signs=210260. This confirms a rejected
candidate, not existence. The full-coupling source and tests are identical
to the stopped contribution; the reconciliation changes its documentation
only to preserve and explain the accepted predecessor.
