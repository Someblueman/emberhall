# An odd-column argument for five marks

Fern, 17 November 2026; exposition clarified by Tern after Isolde's
[independent reconstruction](RECONSTRUCTION.md). **The reconstruction accepts
the density argument; priority remains provisional.** The argument below
addresses every positive odd integer. See [the owner assessment](DECISION.md)
for the distinction between mathematical checking and the literature screen.

## Statement

For a positive odd integer b, put a = b + 2 and

    S = {0, a, 2a, 2a+b, 2a+2b}.

The proposed conclusion is

    d_p(S) = b / (5b+4).

Here A is S-packing when the distinct translates x+S, x in A, are disjoint.
Its upper density is the limsup of |A intersect [-N,N]|/(2N+1), and d_p(S)
is the supremum of these upper densities over all S-packing A subset Z.
Thus d_p counts translation starts. The fraction of covered integers would
instead be five times this density. The upper bound allows arbitrary A,
including nonperiodic sets. The lower construction below attains the supremum.

Two translates intersect exactly when their starts differ by an element of

    M = {b, b+2, 2b, 2b+2, 2b+4, 3b+2, 3b+4, 4b+4}.

These are the positive differences of S. A is therefore S-packing exactly
when every positive difference of two distinct elements of A avoids M.
There are eight distinct values for every positive odd b. For b=1 they
are {1,...,8}; for odd b>=3 they increase strictly in the displayed order.

## Lower bound, with wraparound

Let n = 5b+4, R = {0,2,...,2b-2}, and A = R + nZ. There are b distinct
residues because 2b-2 < n. Suppose a forbidden distance m is congruent
modulo n to a difference d of residues in R. We have 0<m<n and
|d|<=2b-2<n. Therefore -n<m-d<2n, so the only possible multiples of n
are 0 and n: either d=m or d=m-n. The integer d is even and n is odd.

If d=m, then m is even and at most 2b-2. But the smallest even element
of M is 2b, a contradiction. If d=m-n, then m is odd and n-m=-d is
an even integer at most 2b-2. For the four odd forbidden distances,
the values of n-m are

    4b+4, 4b+2, 2b+2, 2b.

All are larger. Thus no difference of R is congruent to an element of
M or its negative. This checks the boundary between periods as well as
pairs in one period. A is legal and has starting density b/n.
This is the specialization of the published lower construction, not a
new lower bound.

## A finite inequality for the upper bound

We prove that every M-avoiding A containing 0 satisfies

    |A intersect [0,5b+3]| <= b.                         (1)

The set A may be finite or infinite. If b=1, M={1,...,8}; (1) follows
immediately, as n=9. Suppose henceforth that b>=3 is odd.

For each integer 0 <= c <= b-1, call C_c = c+S a column. Distinct
members of a column have differences in M, so at most one is in A.
The b columns are pairwise disjoint. To see their entire union, list
the five disjoint row intervals:

    [0,b-1], [b+2,2b+1], [2b+4,3b+3],
    [3b+4,4b+3], [4b+4,5b+3].

Their complement in [0,5b+3] consists of just

    b, b+1, 2b+2, 2b+3.

The positions b and 2b+2 are forbidden by 0 in A. The other two positions,
call them t_low=b+1 and t_high=2b+3, cannot both be in A: their difference
is b+2 in M. If neither is in A, the b column bounds already prove (1).
It remains to prove that if one of them is in A, at least one column is
empty. In fact an empty column has an odd index.

## The odd-column obstruction

Number the five row offsets s_0,...,s_4 by

    (0, b+2, 2b+4, 3b+4, 4b+4).

Suppose, for a contradiction, that one of the extra positions t is in A
and every odd column C_1,C_3,...,C_(b-2) is occupied. There is a last
odd column because b is odd. Each occupied column has exactly one row.

At C_1, rows 0,3,4 are impossible. Their distances from t are:

| t | Row 0 | Row 3 | Row 4 |
| --- | ---: | ---: | ---: |
| b+1 | b | 2b+4 | 3b+4 |
| 2b+3 | 2b+2 | b+2 | 2b+2 |

Every entry is in M. Thus the occupied row of C_1 is in {1,2}.

This set of row types is preserved on passing to the next odd column.
Indeed, for a point c+s_i and the next column's point c+2+s_j, the
following distances exclude every transition from i in {1,2} to
j in {0,3,4}:

| Current row i | Next row 0 | Next row 3 | Next row 4 |
| --- | ---: | ---: | ---: |
| 1 | b | 2b+4 | 3b+4 |
| 2 | 2b+2 | b+2 | 2b+2 |

Again all six entries belong to M. This is a one-way exclusion;
we do not assert that every remaining transition is legal. Induction
along c=1,3,...,b-2 puts the final occupied row in {1,2}.

But at c=b-2 these two positions are

    c+s_1 = 2b,       c+s_2 = 3b+2.

Both belong to M and hence are forbidden by 0 in A. This is the
contradiction. At least one odd column is empty. The one extra occupied
position compensates for at most that one missing column, proving (1).
For b=3 the first and final odd column coincide; the same argument applies
without an induction step.

## From the finite inequality to upper density

Translation of (1) gives at most b points in [x,x+n-1] whenever x is in A.
Any interval J of n consecutive integers has the same bound: if it has
any point of A, let x be its first such point. All of A intersect J then
lies in [x,x+n-1], so it has at most b points. (If it has none, the bound
is immediate.) Partition [-N,N] into full n-element intervals and a final
shorter interval. The final interval also has at most b points by extending
it to length n. Consequently

    |A intersect [-N,N]| <= b * ceil((2N+1)/n).

Divide by 2N+1 and take the limsup. The upper density is at most b/n.
Together with the periodic lower construction this proves the stated
equality. This logical conclusion is separate from the question of whether
an earlier result already proves it.

## Equivalent graph answer

The same target can be stated in the language of distance graphs. For G with
vertex set Z and forbidden distance set M, the candidate result gives

    independence ratio = b/(5b+4),
    fractional chromatic number = circular chromatic number = (5b+4)/b.

For completeness, the coloring half can be checked directly. Put
u=(n+1)/2 and color an integer x by the residue ux modulo n. A circular
(n,b)-coloring requires the circular distance of the colors of adjacent
vertices to be at least b. For the four even distances in M, the residues
um modulo n are

    b, b+1, b+2, 2b+2.

For the four odd distances, in the order b,b+2,3b+2,3b+4, they are

    3b+2, 3b+3, 4b+3, 4b+4.

Every displayed residue lies in [b,n-b], including b=1. Thus the coloring
has ratio n/b. The standard inequalities are
chi_f(G) <= chi_c(G) <= n/b; the independence-ratio identity
chi_f(G)=1/alpha(G) gives the reverse bound from the candidate proof.
Carraher et al., Theorem 1, states that identity for these distance graphs.
This is a corollary of the same candidate argument, not a separate
result with a separate novelty claim. In particular an ordinary coloring alone
would not prove the required fractional bound.

## What the new step would be

The published window decomposition specializes to the columns above.
The extra implication established here is that an occupied extra position
forces an empty **odd** column by the closed row set {1,2} under a step
of two. This would establish the stronger inequality |T| <= |I| in this
family directly; it does not use the strict corollary whose hypothesis
fails here. The proof's substantive, reviewable obligations are the
partition, the two six-entry exclusion tables, the endpoint and the
anchored-window-to-density argument. The program checks finite instances
of those obligations and exhausts small windows; it is not the proof
of their universal quantifiers.

## Sources and attribution

- Natalchenko and Sagdeev, [Packing Density of Sets With Only Two Nonmixed
  Gaps, v2](https://arxiv.org/html/2407.01101v2), Theorem 2 and Section 3.1:
  the conjectured value, lower construction and window decomposition.
- Carraher, Galvin, Hartke, Radcliffe and Stolee, [On the independence ratio
  of distance graphs](https://academicweb.nd.edu/~dgalvin1/pdf/journal/infinitecayley_J.pdf),
  Theorem 1, attributed there to Lih, Liu and Zhu: the external identity
  used only in the graph corollary.
- Fern authored the odd-column argument. Isolde reconstructed its identities,
  endpoint, wraparound and density step independently of their detailed
  derivations; her method and caveats are in RECONSTRUCTION.md. Tern's changes
  above make those presentational obligations explicit and add no stronger
  mathematical conclusion.
