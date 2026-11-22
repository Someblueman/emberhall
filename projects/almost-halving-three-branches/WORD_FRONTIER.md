# A bounded-width transfer for every distance equation

Mica, 22 November 2026. **The general tripod milestone remains open.**
For holes `(1,1),(2,1)`, this gives an exact finite-state transfer for the
*entire* signed distance polynomial when the differences between arm lengths
are fixed. Unlike the end-shell filter, an accepting path is equivalent to
actual balanced homometry. It is not a practical solution of the remaining
family, a construction on that family, or an obstruction to other hole supports.
External priority remains [provisional](PRIORITY_REFRESH.md).

## Result and reproduction

**Theorem.** Fix integers `alpha>beta>0`. For every `c>=1`, on
`T(c+alpha,c+beta,c)` with the two holes above, existence of a balanced
homometric colouring is equivalent to an accepting path in the transfer below.
Every state label contains at most

```text
R = max(alpha+beta, alpha+1, 2)
W = alpha+beta+4 + 6(2R+1)                                     (1)
```

binary signs, independently of `c`. The centre may be fixed to +1 without
changing existence. For `(alpha,beta)=(216,56)`, `R=272,W=3546`; this includes
every `c=11+7560t`, `t>=1`. Thus the full compatibility problem has a uniform
bounded-state characterization, not just necessary endpoint equations.

After integration, in a public checkout of
[Emberhall](https://github.com/Someblueman/emberhall), Python 3.10+ suffices:

```sh
python3 projects/almost-halving-three-branches/word_frontier.py --affine 1
python3 projects/almost-halving-three-branches/word_frontier.py --lengths 4 2 1 --solve
python3 projects/almost-halving-three-branches/word_frontier.py --affine 1 --solve
python3 projects/almost-halving-three-branches/word_realizability.py --control 0 --write /tmp/word.json
python3 projects/almost-halving-three-branches/word_frontier.py --verify /tmp/word.json --audit-graph
python3 -m unittest discover -s projects/almost-halving-three-branches -p test_word_frontier.py
```

The first recorded run reports 22,984 sign variables, 15,415 equations,
maximum equation layer span 218, assignment width 1,141, and the proved
uniform bound 3,546. It does **not** decide existence. The second run counts
two colourings up to global sign reversal. The third exits **2**, with
`status: resource_limit`, `reason: width`, `existence_decided: false`.
No state pruning is interpreted as a mathematical negative. Actual solving
defaults to width at most 20 and at most 100,000 simultaneous states; both
limits can be explicitly changed. A valid negative has `status: exact`,
`existence_decided: true`, and `exists: false`.

The state bound is exponential and presently impractical on the assigned
family. The implementation stores the compiled input and schedule in linear
space, and annotates states with integer path counts. Only the state-label
width is constant in `c`; neither the total implementation memory nor the
number of arithmetic bits is claimed constant. No homogeneous transfer matrix,
eventual periodicity in `t`, or new infinite family of accepted/rejected
parameters is asserted.

## 1. The full constraint system

Write `a=c+alpha`, `b=c+beta`, let `s` be the centre sign, and put
`X=sum_(d=2)^a x_d z^d`, `Y=sum_(d=2)^b y_d z^d`,
`Z=sum_(d=1)^c w_d z^d`, with every coefficient in `{+1,-1}`.
As in [the exact completion proof](WORD_REALIZABILITY.md), with
`K=z+z^-1-z^-2` and `P*=P(z^-1)`, the full expression is

```text
E = s(2z-1-z^a-z^b-z^c)
  + (K-z^b-z^c)X-z^a X*
  + (K-z^a-z^c)Y-z^b Y*
  + (2z-1-z^a-z^b)Z-z^c Z*.                                  (2)
```

For original-tree distance multiplicity polynomials `D_+,D_-`, and total
sign sum `S`, direct shell summation gives
`E=2(1-z)(D_+-D_-)/z-2S`. In particular `E(1)=-2S`. Therefore all
coefficients of `E` vanish **if and only if** the colouring is balanced and
homometric. The resulting pair has size `(a+b+c-1)/2`, the target whenever
the retained order is even. If that order is odd no accepting colouring exists.

`build_system` expands (2) into integer linear equations, combines coinciding
terms, and drops only equations that are identically zero. It includes all
nonzero coefficient rows, including constant and highest degrees. Vertices
at the holes have no variables; their edges remain in the original tree.

## 2. Why folding bounds the width

For a vertex at depth `d`, assign layer
`ell(d)=min(d,c-d)` if `0<d<c`, and layer zero otherwise. The centre also
has layer zero. There are at most six vertices in any positive layer:
one at each end of each of three arms. All tails at depths `c` and beyond,
plus the centre, contribute at most `alpha+beta+4` layer-zero variables.
This is an upper bound even when holes remove some of them. An even `c`
has only one vertex per arm at its middle layer; nothing is counted twice.

Let `f(k)` be distance from the residue of `k` to zero on the cycle of
length `c`, that is `min(k mod c, c-(k mod c))`. This is 1-Lipschitz in
cyclic distance and invariant under negation. A non-tail variable at depth
`d` occurs in (2) only at degrees `d+1,d-1,d-2`, `d`,
`L_i-d`, or `L_j+d`, with `L_i=c+e_i`, `e_i` in `{alpha,beta,0}`.
Terms not belonging to its arm are simply absent. Hence each occurrence
at degree `k` satisfies `|ell(d)-f(k)|<=R`.

For a tail write `d=c+h`, `0<=h<=e_i`. A cross term has residue `h+e_j`
with `j!=i`, whose magnitude is at most `alpha+beta`. The other residues
are `h+1,h-1,h-2,h`, or `e_i-h`, bounded in cyclic distance by
`max(alpha+1,2)`. Its layer is zero, so the same inequality holds.
The centre's degrees also obey it. Thus any two variables occurring in
one coefficient row have layers differing by at most `2R`.

Order variables by layer, then arm and depth. Immediately before assigning
a variable, retain an earlier sign exactly when an equation using it has a
variable at this step or later. Every retained sign is at most `2R` layers
behind the current layer. Counting at most `2R+1` positive layers plus all
layer-zero variables proves (1), including the sign about to be assigned.
This proof is uniform in the arm lengths, rather than extrapolated from the
reported width at `t=1`.

## 3. Exact transitions and both endpoints

Each row has a last variable in the deterministic order. Start with the
empty state and assign the centre +1. For each subsequent vertex, try both
signs. Evaluate every row whose last variable is this vertex. Reject the
transition unless each evaluates to zero. Retain only assigned variables
that occur in a row with a later last variable; this assignment is the new
state. Equal states merge, with their path counts added.

Inductively the state contains every assigned sign needed by a future row,
and every completed row has been checked. Consequently a true solution
always determines a surviving path. Conversely, successive transitions give
one sign to every retained vertex, and at the last step every row of (2)
has been checked. No sign is lost before its last use. The terminal separator
is empty, so its count is exactly the number of colourings with positive
centre. This proves necessity and sufficiency, including the moving ends,
constant coefficient, balance, and high-distance remainder. It uses neither
independent prefix/suffix assignments nor a periodic sign-word assumption.

The schedules may depend on `c`, but the finite state alphabet does not:
use arm, prefix/suffix, and age at most `2R` for positive-layer positions,
and fixed tail slots for layer zero. There are finitely many local transition
types on these bounded slots. The supplied program generates the schedule
from the exact coefficient rows instead of listing an enormous automaton.

## Checks and remaining work

Six tests compare exact transfer counts with exhaustive, separately built
original-tree distance counts on ten small triples; compare all polynomial
coefficients on 75 arbitrary, including unbalanced, assignments; exercise
folding at small lengths and collisions; and reject an altered literal
certificate. CLI tests distinguish resource refusal from exact negatives.
The existing word certificate format is preserved; optional original-tree
BFS verification uses the accepted completion module and its size limit.

Next useful research is to exploit these exact transitions structurally or
compress reachable states enough to decide a new infinite parameter branch.
The measured 1,141-sign frontier is not such a compression. Other hole
supports and the original all-pairs milestone remain open.
