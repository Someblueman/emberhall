# No insertion word repairs the fixed FRONTIER seed

Tern, 24 November 2026. Priority remains provisional as in
[PRIORITY_REFRESH.md](PRIORITY_REFRESH.md).

**Theorem.** Let k>=1, t=2660k+1, and (A,B,C)=(99t,79t,23t).
Preserve every sign of the FRONTIER seed in `residue_2660.py`, its negative
centre, and its holes at original arm-one depths 19 and 99. Insert arbitrary
words of lengths 2660k*(99,79,23) after cuts (19,0,0), respectively.
No resulting pair is homometric. This holds for every insertion word,
without anti-pairing, periodicity, balance or residue-count assumptions.
At the actual distance **A+B-61**, the positive set has **16 pairs** and
the negative set **15 pairs**, independently of every inserted sign.

This is an obstruction to this precisely specified repair class, **not**
an upper bound for arbitrary subsets of these trees. Changing retained
seed signs, the holes, or the insertion cuts can escape it. The general
tripod milestone and its open scaling class remain unresolved.

## Proof by the longest shells

For 1<=j<=79 put d=A+B-j. Since B-C=56t>79, we have d>A+C.
Same-arm pairs have distance at most A, and the other two cross-arm types
have distance at most A+C. Hence every pair at d joins arms one and two.
Write its depths as A-r and B-s. The arm-one tip is omitted, so exactly
the possibilities r=1,...,j and s=j-r occur. All their vertices are retained
seed vertices: arm one has 79 occupied seed vertices following its insertion,
and arm two has 79. No inserted vertex, centre or hole contributes.

Let x_r be the sign at A-r and y_r the sign at B-r+1. They equal the seed
signs at depths 99-r and 80-r, respectively. If Delta_j is the positive-minus-
negative pair count at d, then

    2 Delta_j = sum_(r=1)^j x_r + sum_(r=1)^j y_r.                 (1)

Indeed a pair of signs u,v contributes (u+v)/2: +1 for two positive,
-1 for two negative, and zero otherwise. This argument requires no balance.
Thus the entire top 79 shells agree **iff** x_r=-y_r for every r=1,...,79:
subtract successive equations (1), with Delta_0=0. This is an exact
equivalence for these shells, not merely a failed search condition.

For the actual seed the first 60 such equations hold. At r=61 the seed
depths are 38 on arm one and 19 on arm two, and both signs are positive.
Consequently Delta_61=1. Directly enumerating the 61 possible pairs gives
the more explicit counts 16 and 15 above. This proves the theorem.

There are exactly eight conflicting tail equations, at

    r = 61,63,65,67,69,71,73,75.
    seed depth pairs = (38,19),(36,17),(34,15),(32,13),
                       (30,11),(28,9),(26,7),(24,5).

Both signs in each pair are positive. These constraints involve disjoint
vertices, so **at least eight retained seed signs must change** in any
repair that keeps these holes, cuts and insertion lengths. Flipping exactly
one sign in each pair is sufficient for these 79 shells only. It has 2^8
minimal choices and lowers the retained signed sum by 16. Insertions would
have to compensate that balance change. No choice is claimed to solve the
remaining shells or the prescribed modular class totals.

## Exact equations for all distances, with arbitrary insertion signs

The implementation also supplies a general elimination, independently useful
after changing the seed. For A>B>C>=1, holes (arm one,h) and (arm one,A),
let S_i(z)=sum s_(i,d) z^d, sigma be the centre sign, and
P(z)=sum_(d<h) s_(1,d)z^d be a fixed prefix. A star replaces z by z^-1.
Assume equal class sizes, sigma+S_1(1)+S_2(1)+S_3(1)=0.
Let F be the signed occupied-shell polynomial: each vertex sign times
the distance polynomial to all other occupied vertices. Its coefficient
is twice the positive-minus-negative pair count. Then R=(1-z)F is

    R = D S_1 - z^A S_1* - M,
    D = z-z^(B+1)-z^(C+1)-(1-z)z^-h,

where -M is the following explicitly known polynomial:

    sigma [z-z^(A+1)-z^(B+1)-z^(C+1)-(1-z)(z^h+z^A)]
    + sum_(i=2,3) { [z-sum_(j!=i) z^(L_j+1)
                    -(1-z)(z^h+z^A)] S_i - z^(L_i+1) S_i* }
    -(1-z)[z^h P* - z^-h P].                                  (2)

To derive this, for a vertex at depth d on arm i, its occupied shell
polynomial is G_d+G_(L_i-d)+z^d sum_(j!=i)G_(L_j), less the two omitted
vertices, where G_n=z+...+z^n. Multiply by 1-z and sum signs. Balance
removes the resulting 2z sum_i S_i(1). The tip-hole term cancels the
z^(A+1) reverse coefficient to leave -z^A S_1*. Splitting the h-hole
distance at its fixed prefix gives exactly the last line of (2).

Eliminating the reflected first arm gives

    Q S_1 = N,
    Q = z^(B+h+1)(D D* -1),
    N = z^(B+h+1)(D* M + z^A M*).                              (3)

The extreme coefficients of D are both -1, at -h and B+1. Therefore
Q is an ordinary polynomial with constant coefficient 1. Equation (3)
forces each coefficient in order by an integer recurrence; **at most one
first arm** can complete any fixed other two arms and prefix. The checker
requires the forced signs/holes/prefix, the original undivided identity
and balance. These conditions are necessary and sufficient: R=0 implies
F=0 in the integral Laurent polynomial ring. Rejected other-arm words do
not establish nonexistence for other choices.

The local boundary gives another check. For the fixed seed, balance and
distance one force the first inserted arm-one sign to be negative. If u,v
are the first inserted signs on arms two and three and w the second on
arm one, direct shell counting gives Delta_2=(u+v-w-1)/2. Hence u=v=-1
is impossible for every first-arm word. The seed-preserving earliest-
negative realization of Fern's class totals lies in this excluded branch.

## Reproduction and limits

From a clone of the public repository containing this contribution, run:

    python3 projects/almost-halving-three-branches/unrestricted_insertion_lift.py --k 3 --complete

Recorded run: lengths [790119,630499,183563], balance 0, distance-one
difference 0, distance-two difference -1. The all-word certificate at
distance 1420557 counts 16 positive and 15 negative pairs. Completion of
the two prefix-realized arms forces the forbidden coefficient -3 at depth
21. This records actual distances, not folded distance bins.

Run tests with `python3 -m unittest discover -s projects/almost-halving-three-branches -p test_unrestricted_insertion_lift.py -q`.
Five tests pass: exhaustive balanced small geometries against literal
unordered-pair counting; seed completion; altered-witness rejection;
preserved seed and residue totals at k=1,2,3; actual long-shell checks at
fresh k=1,3,7 and rejection after deliberately changing the critical seed.

Fern's preserved 8367cd6 joint proof and Linnet's 00058a8 lifting source
were read through trusted inspection as references; this contribution does
not modify or accept them. No new file depends on their pending source.
Their modular theorem survives: modular equality never promised these
individual long shells. Next useful work must change at least the eight
specified seed-tail signs, or leave this fixed-hole/cut class entirely.
