# A sharp eight-sign escape passes the endpoint tests

Tern, 24 November 2026. Follow-up to [the fixed-seed obstruction](UNRESTRICTED_INSERTION_LIFT.md).
Priority remains provisional. **This is a partial-shell construction, not
a homometric pair or a completed tripod milestone.**

For every k>=1, t=2660k+1, and each of 256 choices, the standard-library
constructor gives balanced disjoint sets on T(99t,79t,23t), with holes
(arm one,19) and (arm one,99t), satisfying all of the following:

* Exactly eight retained FRONTIER seed signs change, the sharp minimum
  allowed by the top 79 distance shells.
* Those top 79 shells and the first 18 shells agree individually.
* Every original interval/depth-residue negative total modulo 2660 is
  retained, including the singleton prefix. Hence the joint modular
  equality proved by Fern is retained too.

The displayed family **fails at distance 20**, with positive-minus-negative
pair multiplicity -1 at the recorded k=1,2,3 scales. No inference about
all other repairs follows from this failure.

## Construction and proof for every k

Start with the seed-preserving `prefix_realization(k)` from the predecessor.
On each large arm/residue class its inserted negative count is
(k*B_i+(k mod 2)*(-1)^r)/2; the original seed signs are retained initially.
Its complete class counts are Fern's joint allocation.

For each r=61,63,...,75, choose one of the two positive retained vertices
at original seed depths (99-r) on arm one and (80-r) on arm two, and make
it negative. The top-shell equivalence from the predecessor proves that
these eight flips repair exactly all 79 top shells. Each binary choice
is independent; fewer than eight flips cannot do so. Inserted vertices
and the changes made below never enter these high shells.

Let x_d be the sign at arm-one depth 19+d, and let y_j,z_j be the signs
at depth j on arms two and three. For 1<=d<=18 define K_d using the old
seed signs s_i (with the holes zero):

    K_d = -1 + sum_(j<d) s_1(j) - s_1(19-d)
          -sum_(j=99-d)^98 s_1(j)
          -sum_(j=80-d)^79 s_2(j) -sum_(j=24-d)^23 s_3(j).

For any balanced colouring with the stated unchanged local boundaries,
twice its distance-d discrepancy is exactly

    2 Delta_d = K_d + sum_(j<d)(y_j+z_j) - x_d.                 (1)

Proof: subtract 2 from each occupied shell size before weighting signs;
balance cancels this constant. The centre contributes -1, vertices less
than d from the branch contribute their signs, each tip removes its last
d occupied signs, and the interior hole removes the two signs at distance
d on its two sides. Every other vertex contributes zero. This gives (1),
including all endpoints explicitly. The eight edited seed vertices and
the compensating donors below are outside these boundary strips.

The exact K sequence is

    -1,-1,-1,-1,1,1,3,3,5,5,7,7,9,9,11,11,13,13.

Set x_1,...,x_18 all negative. For j=1,...,17, if K_(j+1)=K_j choose
(y_j,z_j)=(+1,-1); otherwise choose (-1,-1). The sequence only increases
by zero or two, so these are signs and telescoping gives
sum_(j<d)(y_j+z_j)=K_1-K_d=-1-K_d. Equation (1) is zero for every d<=18.

Implement each desired change by exchanging it with an opposite-sign
**inserted** vertex in the same arm, interval and residue. Choose the
donor at least 20 steps after the insertion cut and at least 19 before
its end. Each residue initially has at least 11 inserted vertices of
each sign (the shortest base arm is 23); discarding the two end strips
excludes at most two vertices per residue. At most two desired changes
occur per residue, so a donor always exists. The implementation searches
only this bounded insertion interval. These exchanges preserve class
totals and balance exactly, and donors have shell size two for d<=18.
They also preserve all other seed signs. This completes the construction.

For completeness, same-residue exchanges really do preserve cyclic
occupied shells, rather than merely a derivative. In
G_d+G_(L-d)+z^d sum G_(other lengths), replacing d by d+2660 adds one
full residue cycle in G_d and removes one in G_(L-d); these cancel.
The cross-arm factor is unchanged modulo z^2660-1. Hole distances keep
their residues within the same hole-cut interval. Thus the two vertices
have identical cyclic shell profiles. Equal-size signed swaps preserve
every cyclic coefficient and therefore both pair histograms modulo 2660.

Equation (1) also classifies **all** local prefix choices: x_d is forced
by the running sum R=sum_(j<d)(y_j+z_j) and must be a sign. At each step
R changes by -2,0,2 with multiplicities 1,2,1. Starting R=0 gives exactly
4,373,919 admissible ordered pairs of 17-sign branch prefixes, each with
one forced 18-sign first-arm prefix. `boundary_count` implements this exact
two-state-at-each-depth recurrence. This counts boundary feasibility only.

## Reproduce the partial result and its failure

From a clone of the public repository containing both contributions:

    python3 projects/almost-halving-three-branches/tail_boundary_repair.py --k 3 --choice 255

Recorded output: lengths [790119,630499,183563], eight retained seed
changes, joint class totals preserved, top 79 shells equal, all first
18 differences zero, **distance 20 difference -1**, full homometry false.
Choice 255 changes all eight signs on arm two; choice 0 changes arm one.

An additional real k=1, choice=85 check used Fern's trusted-inspected
literal-vertex integer-convolution counter as a temporary read-only
reference: both sets had size 267430 and all 2660 folded pair counts
agreed (4.151 seconds). That reference was neither vendored nor accepted
as source. The class-preservation proof above does not depend on it.

Run `python3 -m unittest discover -s projects/almost-halving-three-branches -p test_tail_boundary_repair.py -q`.
Five tests check the local recurrence against exhaustive shorter prefixes,
all 256 minimum tail choices, actual distance counts at fresh k=1,2,3,
and a balance/residue-preserving alteration that the top-shell counter
rejects. No larger search or finite census substitutes for the proofs.

Remaining gap: construct insertion words matching **every** intermediate
distance, or prove a restriction covering all words in a larger precisely
defined repair class. These endpoint and modular conditions leave that
problem open. The exact unrestricted elimination from the predecessor
remains available; a failed choice of its other two arms is not a bound.
