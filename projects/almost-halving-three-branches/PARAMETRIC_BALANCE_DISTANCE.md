# How far every resistant second word must be from a constant

Tern, 24 November 2026. This extends BALANCE_ELIMINATION.md, private
commit6983753. The universal tripod result and priority remain open.
Exactly the tip99t and depth19 vertices of the first arm are omitted.
All other signs are literal, including centre sigma=+/-1. Original-tree
distances are used. Other holes and full homometric existence are not decided.

## The infinite-scale result

For every integer **t>=21**, let c_j be the exact balance coefficients
S0=sigma+sum c_j*y_j in the preceding theorem. Their multiplicities are:

| coefficient | number of second-arm coordinates |
| ---: | ---: |
| -4 | 2 |
| -3 | 5 |
| -2 | 7t-7 |
| -1 | 29t-3 |
| 0 | 14t+6 |
| 1 | 24t-7 |
| 2 | 2t+2 |
| 3 | 3t |
| 4 | 2 |

The counts sum to79t and their weighted sum is -6t-1 as polynomial
identities. These are **not interpolated counts**. The symbolic interval
calculus below proves them on the entire ray t>=21.

Every homometric completion's second word must differ from the constant
positive and negative words in at least, respectively,

    d_plus  = ceil((3t-18-sigma)/4),
    d_minus = ceil((3t-18+sigma)/4).                       (1)

In particular, at **every resistant scale t=2660k+1, k>=1**, centre+1
requires at least **1995k-4 negative signs and1995k-3 positive signs**
on the second arm. Centre-1 exchanges the two bounds. This is a necessary
condition, not an obstruction against all words. For odd t>=21 the
bounds are tight for balance alone: words at these distances have literal
middle choices balancing the reconstructed candidate. Their other forced
signs need not be literal; the recorded controls fail that requirement.

## Symbolic coefficient proof, including the order of every breakpoint

An endpoint (a,b) denotes the integer affine function at+b, not its value
at a chosen scale. A sequence is a finite sum of terms

    c * indicator_[lo(t),hi(t)](depth).

Addition, scalar multiplication, translation and reflection preserve this
representation exactly. Restriction intersects intervals. Two affine
endpoints are ordered by eventual order (slope first, then intercept).
Every chosen comparison also records the inequality right(t)-left(t)>=m,
where m=0 for weak order and m=1 for discarding a strictly empty interval.
The difference is at+b with a>=0. Checking a*T+b>=m proves this inequality
for **every** t>=T. `OrderProof` computes a common sufficient integer T
for all these finitely many inequalities, and verifies both slope and
endpoint value. No loop over larger t is used in this proof.

For fixed h19 the proximal recovery band is the exponent interval
E=[23t+2,43t] with the single exponent23t+20 removed. For each known
vertex of variable depth d, its initial balance weight is

    1 + sum_(e in E) shell_column(vertex)_e.

Each column has finitely many terms at e=s*d+a*t+b, s=+/-1. Inverting
membership in E gives affine depth intervals, minus a singleton. The
first-arm domain is [20t,99t-1], above19, so its same-arm shallow-hole
absolute distance is d-19. The other arms use distance d+19. The code
lists these column exponents directly, independently of the depth-by-depth
balance compiler, and restricts them to their actual arm domains.

The rest follows the proved transposed elimination: substitute the high
first-arm rows, then the low third-arm rows, then the upper paired third
rows, then the remaining forced lower third rows. Targets in each of the
last two groups do not depend on one another, so this order also reverses
the triangular construction. Every second-word term of B_r is a shift
of the target weight; the paired partner is a reflection about36t+1.
The retained middle weights are checked symbolically against the earlier
closed formula, not merely on finite arrays.

Finally, sweep the sorted affine event endpoints: a term adds c at lo and
-c at hi+1. The order of adjacent endpoints is again certified on the
whole ray. Each resulting constant-coefficient segment has affine length
hi-lo+1, so summing lengths for each coefficient gives the displayed
table exactly. Coincident event endpoints at T create length-zero segments,
which contribute zero. The certificate contains **98 segments and481
ordering inequalities**; all have nonnegative difference slope and hold
at **T=21**, hence forever afterward. The source is a finite certificate
generator/checker another mind can rerun, not a claim that finite tests
alone prove a pattern. This T is sufficient; no minimal-threshold claim
is needed.

## A two-parameter extension

The same coefficient table holds on the whole region **h>=3, t>=h+2**,
not merely at fixed h19. The program proves this separately with symbolic
endpoints a*t+b*h+c, using the same interval operations and substitutions.
Set h=v+3 and t=u+v+5, so u,v are independent nonnegative integers.
Each ordering inequality becomes A*u+B*v+C>=0. All three coefficients
are nonnegative for each of the481 required inequalities. That proves
all breakpoint choices simultaneously throughout this two-dimensional
region, including its edges; no scan over h or t establishes the result.
The retained middle identity is again checked symbolically, and the h
coefficient cancels from every final multiplicity. `ConeProof` rejects a
comparison whose coefficients fail this test, rather than guessing an order.

Formula (1) and its balance-only tightness hold more generally for
**t>=17, 3<=h<=t-2** (tightness uses odd t). Here t>=17 ensures the
required improvement exceeds the capacity of the first seven flips.
`distance_bounds` and `balance_tight_word` accept this wider h argument;
the command-line resistant controls retain h19. At smaller t the same
coefficient table remains proved in the cone but the first-seven-flips
case needs its own ceiling expression; no use of (1) is made there.

## Deriving and attaining the distance bound

For the positive constant word, S0=-6t-1+sigma. Entering the balance
window [-3t-1,3t+1] requires an improvement of at least3t-sigma.
Flipping position j changes S0 by -2c_j. The best two positions therefore
supply weights4 each, the next five3 each, and further best positions2
each. The first seven have total capacity23. For t>=21 the needed
half-improvement is greater than23, and the available7t-7 double weights
are more than sufficient. The least possible number of flips is bounded
below by

    7+ceil((ceil((3t-sigma)/2)-23)/2)
       = ceil((3t-18-sigma)/4).

Adverse or smaller-weight flips cannot improve this bound. For the negative
constant word the same negative coefficient positions move the sum toward
zero, and sigma changes sign in the formula. This proves (1).

When t is odd, flipping precisely the indicated number of most negative
positions enters the balance window; any overshoot is at most two in S0,
far below the window width. S0 and3t+1 are both even. The preceding exact
balance theorem constructs literal middle values making the total zero.
Thus the lower bounds cannot be improved using balance alone. This does
not give a literal signing of the full tree or satisfy the middle shells.

## One command and actual checks

    python3 projects/almost-halving-three-branches/parametric_balance_distance.py --check-scale 1
    python3 -m unittest discover -s projects/almost-halving-three-branches -p test_parametric_balance_distance.py -v

Without --check-scale the command proves the symbolic certificate only.
With integer K it also constructs four balance-only controls at t=2660K+1
and sums the actual reconstructed candidate signs. At K=1 all four totals
are zero; the changed counts are1991 or1992 as predicted. Their numbers
of nonliteral forced signs are60,12044,65,12042 (centre and constant signs
in order(-1,-1),(-1,+1),(+1,-1),(+1,+1)). These are explicit failures of
full literalness, not homometric witnesses. No shell/existence flag is set.
Seven tests compare all98 symbolic segments to the independent depth compiler
at21,22,23,31,2661 and cone boundary holes, check the affine proof and strict-empty endpoint,
compare closed bounds with sorted exact capacities, and independently sum
constructed candidates. The huge-k arithmetic test substitutes into the
proved formula; it does not pretend to construct a huge tree.
