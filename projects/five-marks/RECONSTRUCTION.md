# Five Marks: independent reconstruction of the candidate proof

Isolde (neither the proof's author Fern nor the novelty assessor Vesper).
Task `five-marks-proof-reconstruction`. This note re-derives every identity
the argument in [PROOF.md](PROOF.md) rests on and gives a verdict on the
argument itself. It does not assess novelty (see [NOVELTY.md](NOVELTY.md)),
close any milestone, or widen the claim.

**Method, stated honestly.** I read the statement, the displayed set M and
the column setup in PROOF.md, and the one-paragraph strategy sketch in
[README.md](README.md), then stopped. Everything below — the pair
enumeration for M, the partition, both exclusion tables, the endpoint, the
edge cases, the wraparound and the density step — was derived and checked
symbolically (as affine functions of b) before I opened the obstruction,
density and graph sections of PROOF.md. I then compared. My two tables
agree with the proof's entry for entry; where my derivation differs in
form (the wraparound case split) I give my form and say so. So this is an
independent re-derivation of the identities, not a blind rediscovery of
the strategy, and the verdict rests on the identities, not on trust.

## Statement being checked

For positive odd b, a = b+2, S = {0, a, 2a, 2a+b, 2a+2b}
= {0, b+2, 2b+4, 3b+4, 4b+4}. A set A of integers is a packing when its
translates x+S are disjoint. Claim: every packing has upper density
(limsup of |A ∩ [-N,N]|/(2N+1)) at most b/(5b+4), and some packing attains
it. That pair of facts is exactly "d_p(S) = b/(5b+4)" under the standard
definition of d_p as the supremum of upper densities of packings; PROOF.md
uses that definition without restating it (see Gaps, item 1).

## 1. The difference set M, from the ten pairs

With s = (0, b+2, 2b+4, 3b+4, 4b+4), the ten positive differences are

    s1-s0 = b+2    s2-s1 = b+2    s3-s2 = b      s4-s3 = b
    s2-s0 = 2b+4   s3-s1 = 2b+2   s4-s2 = 2b
    s3-s0 = 3b+4   s4-s1 = 3b+2
    s4-s0 = 4b+4

so M = {b, b+2, 2b, 2b+2, 2b+4, 3b+2, 3b+4, 4b+4}, as displayed. Two
translates of S meet exactly when their starts differ by an element of
±M, so A is a packing iff no two distinct elements of A differ by an
element of M. The eight values are in fact distinct for every positive
odd b: for b >= 3 they sort strictly as written (using b+2 < 2b and
2b+4 < 3b+2, both equivalent to b > 2), and for b = 1 they are {1..8}.
PROOF.md's remark about repeated values is therefore unnecessary, and
harmless.

## 2. Lower bound and wraparound (my case split)

Let n = 5b+4, R = {0, 2, ..., 2b-2} (b residues, since 2b-2 < n), and
A = R + nZ. Suppose two elements of A differ by m in M. Then
m ≡ d (mod n) for some difference d of two elements of R, where d is
even and |d| <= 2b-2. Since b <= m <= 4b+4, m-d lies in [2-b, 6b+2], in
which the only possible multiples of n = 5b+4 are 0 and (for b >= 3) n.

- m = d: then m is even and at most 2b-2. For odd b the even elements of
  M are 2b, 2b+2, 2b+4, 4b+4, all at least 2b. Impossible.
- m - d = n: then n-m = -d is even and at most 2b-2. Here n is odd
  (b odd), so m must be odd; the odd elements of M are b, b+2, 3b+2,
  3b+4, giving n-m = 4b+4, 4b+2, 2b+2, 2b, all larger than 2b-2.
  Impossible.

The second case is exactly the cross-period (wraparound) pair, so the
construction is legal across period boundaries as well as inside one
period, and its density is b/n. This matches PROOF.md's parity argument;
the range bound on m-d above is the step that limits the shift to 0 or
one period, which PROOF.md states (difference magnitude < n) but in
compressed form.

## 3. Columns, partition and the four extra positions

Let b >= 3 for now. For 0 <= c <= b-1 the column C_c = c+S contains at
most one point of any packing, since distinct points of C_c differ by an
element of M (Section 1). The columns are pairwise disjoint: each lies
one point in each of the five row intervals

    [0,b-1], [b+2,2b+1], [2b+4,3b+3], [3b+4,4b+3], [4b+4,5b+3],

the intervals are disjoint, and within an interval the point c+s_i
determines c. Counting confirms the partition: b columns of 5 points
fill 5b of the 5b+4 positions of [0,5b+3], and the complement is exactly

    b,  b+1,  2b+2,  2b+3,

the two gaps of two between consecutive row intervals (rows 2–3 and 3–4
are adjacent, so contribute no gap).

Anchoring at 0 (translate so that 0 is in A): positions b and 2b+2 lie
in M, hence not in A. The remaining extras t_low = b+1 and
t_high = 2b+3 differ by b+2, which is in M, so at most one is in A.
If neither is, the column bounds give |A ∩ [0,5b+3]| <= b at once.
If one is, an empty column is needed to keep the count at b. Sections
4–6 show an odd column is empty.

## 4. First six-entry table: the first odd column

C_1 has positions 1+s_i = (1, b+3, 2b+5, 3b+5, 4b+5) in rows 0..4.
Distances from each candidate extra t, for rows 0, 3, 4, computed by
direct subtraction (each is an identity in b, and each value is in M):

    t = b+1:   row0 (b+1)-1 = b          row3 (3b+5)-(b+1) = 2b+4
               row4 (4b+5)-(b+1) = 3b+4
    t = 2b+3:  row0 (2b+3)-1 = 2b+2       row3 (3b+5)-(2b+3) = b+2
               row4 (4b+5)-(2b+3) = 2b+2

So whichever extra is occupied, rows 0, 3, 4 of C_1 are forbidden;
if C_1 is occupied at all, its point is in row 1 or row 2. (Nothing here
asserts rows 1–2 are attainable; for t_high, row 1 is in fact also
forbidden, distance b. The argument needs only the exclusions.)

## 5. Second six-entry table: stepping by two columns

Let c be odd, suppose C_c is occupied at row i in {1,2}, and consider a
point of C_{c+2} at row j. The distance between c+s_i and c+2+s_j is
|2 + s_j - s_i|, independent of c. For j in {0,3,4}:

    i=1 (s=b+2):  j=0 |2-(b+2)| = b        j=3 2+(3b+4)-(b+2) = 2b+4
                  j=4 2+(4b+4)-(b+2) = 3b+4
    i=2 (s=2b+4): j=0 |2-(2b+4)| = 2b+2    j=3 2+(3b+4)-(2b+4) = b+2
                  j=4 2+(4b+4)-(2b+4) = 2b+2

All six values lie in M (the j=0 entries are negative before the
absolute value, with magnitudes b and 2b+2 as shown). Hence no point of
C_{c+2} in rows 0, 3, 4 can coexist with a row-1-or-2 point of C_c:
under the assumption that every odd column is occupied, the row-set
{1,2} propagates from each odd column to the next.

## 6. Endpoint at c = b-2, and where oddness is used

Because b is odd, the odd columns are C_1, C_3, ..., C_{b-2}: the chain
starting at 1 in steps of 2 lands exactly on b-2. At c = b-2 the two
surviving rows sit at

    (b-2) + s_1 = (b-2)+(b+2)  = 2b     in M,
    (b-2) + s_2 = (b-2)+(2b+4) = 3b+2   in M,

so both are forbidden by 0 in A. Combining: if an extra is occupied and
no odd column were empty, Section 4 puts C_1's point in rows {1,2},
Section 5 inductively puts every later odd column's point in rows
{1,2}, and the endpoint forbids both rows in C_{b-2} — contradiction.
Therefore some odd column is empty, the columns contribute at most
b-1 points, the occupied extra contributes 1, and

    |A ∩ [0,5b+3]| <= b        whenever 0 is in A.        (1)

Oddness of b is essential precisely here (and in the parity of
Section 2): for even b the chain would end at c = b-1, where the row-1
and row-2 positions are 2b+1 and 3b+3, not in M, and the obstruction
evaporates. The tables of Sections 4–5 are identities for all b; only
the endpoint alignment needs b odd.

## 7. Edge cases b = 1 and b = 3

b = 1: M = {1..8} and n = 9, so with 0 in A the whole window [0,8]
contributes only 0 itself, giving (1) with b = 1 directly. The column
argument cannot run (there is no odd column and c = b-2 = -1), and is
not needed; PROOF.md separates this case, correctly. The lower-bound
argument of Section 2 works unchanged (R = {0}).

b = 3: there is a single odd column, C_1, which is simultaneously the
first and the last (b-2 = 1). Section 4 forbids its rows 0, 3, 4 (via
the occupied extra) and Section 6 forbids rows 1, 2 at positions
2b = 6 and 3b+2 = 11 (via 0), so C_1 is empty with no induction step.
The partition also checks concretely: row intervals [0,2], [5,7],
[10,12], [13,15], [16,18] leave extras {3,4,8,9}. Extra coincidences
at b = 3 (e.g. the C_1 row-1 position b+3 = 2b) only add forbiddens;
the argument uses only that the tabulated distances are in M, which
holds by the same affine identities.

## 8. From the anchored window to upper density, nonperiodic A included

Translation invariance turns (1) into: any interval [x, x+n-1] with
x in A contains at most b points of A. An arbitrary block J of n
consecutive integers then also contains at most b points: if J meets A,
let x be its first point of A; every point of A ∩ J lies in
[x, x+n-1] (it is >= x and at most the end of J, which is <= x+n-1).
Partitioning [-N,N] into ceil((2N+1)/n) such blocks (extending a short
final block to length n can only add points, so the bound applies) gives
|A ∩ [-N,N]| <= b·ceil((2N+1)/n), so the upper density of every
packing — periodic or not, finite or infinite — is at most b/n. The
anchoring hypothesis is fully discharged by the first-point step; no
periodicity, compactness or limiting argument is hidden here. Together
with Section 2 the density b/n is both an upper bound for all packings
and attained, which is the claimed equality. (The same per-block bound
gives the result for densities measured along [0,N] or any Følner
sequence of intervals, so the conclusion is not an artefact of the
symmetric window.)

## 9. The graph-language corollary (spot-checked, one external input)

PROOF.md's final section converts the result to independence ratio and
fractional/circular chromatic numbers. The coloring arithmetic
re-derives cleanly: with u = (n+1)/2 (an integer since n is odd) and
color ux mod n, for even m in M, um ≡ m/2 (mod n), giving
b, b+1, b+2, 2b+2; for odd m in M, um ≡ (n+m)/2 (mod n) (the difference
is n(m-1)/2), giving 3b+2, 3b+3, 4b+3, 4b+4. All eight residues lie in
[b, n-b], so adjacent vertices receive colors at circular distance at
least b, as claimed, including b = 1. The remaining step — equality of
fractional chromatic number with the reciprocal independence ratio for
these distance graphs — is cited to Carraher et al., Theorem 1, and is
not proved in PROOF.md. I did not re-derive that identity; it is an
external dependency of the corollary only, not of the density equality.

## 10. Cross-checks run (supporting, not substituting)

An independent script written for this note (no project code imported)
verified: M as a set of affine forms from the ten pairs; all twelve
table entries and both endpoint positions as affine identities in M;
the partition and the lower-bound wraparound for all odd b up to 101;
and, by its own exhaustive search over the anchored window, maxima of
1, 3, 5 for b = 1, 3, 5, matching the bound b. The project's check.py
also passes (51 odd parameters; exhaustive maxima 1, 3, 5, 7 for
b = 1, 3, 5, 7). These finite checks can only catch errors; the
universal claims above rest on the affine identities, which I verified
symbolically.

## Gaps and hidden assumptions found

1. **Definition of d_p is imported, not restated.** PROOF.md defines the
   upper density of a packing but not d_p itself. What is proved is
   "every packing has upper density <= b/(5b+4), and one packing attains
   it"; the equality d_p(S) = b/(5b+4) follows under the standard
   definition used in the source literature. Presentational gap, not a
   logical one — but the note should not be read as re-establishing the
   definition.
2. **Graph corollary has one cited, unproved input** (Section 9). It
   does not feed back into the main equality.
3. **Two compressions, both repairable from stated material:** the
   wraparound paragraph's parity sentence needs the magnitude bound
   stated just before it to exclude shifts by 2n (supplied explicitly
   in Section 2 above), and column disjointness is asserted where the
   row-interval listing one line later proves it.
4. The remark about repeated values in M is unnecessary: the values
   are distinct for all positive odd b (Section 1).
5. Nothing in PROOF.md or in this note speaks to novelty. That question
   is Vesper's NOVELTY.md and the project owner's admission decision,
   which this note does not make.

No failed inference was found. I did not need the task's
stop-and-preserve clause, because no step failed when re-derived.

## Verdict

**Accept.** The argument in PROOF.md is a correct proof of its stated
density result for every positive odd b: difference set, partition,
both six-entry exclusion tables, the c = b-2 endpoint, the b = 1 and
b = 3 edges, the periodic wraparound and the anchored-window-to-density
step all re-derive as claimed, with only the presentational and
definitional caveats listed above. Acceptance here is of the argument's
logic only; it certifies neither novelty nor the project's admission,
and closes no milestone.
