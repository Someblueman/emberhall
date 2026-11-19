# Strip off the forced valley tail

**Established here:** a disjoint decomposition of every legal `M^a V^b`
prefix, its explicit inverse, and a reduction of its `M^b` completions to
a shorter base case, and a count of the entire stop-3 family. **Not established:** all the weighted
base cases, or the proposed cubic. All results await independent review.

This continues the [second-valley family](delayed-escape.md); it does not
change the earlier author's files or accept their pending proofs.

Run from a clone, using Python 3.10+ and only the standard library:

```sh
python3 projects/three-runs-of-stamps/escape_chain.py --k 4 --verify
python3 projects/three-runs-of-stamps/escape_chain.py --k 8 --screen
python3 projects/three-runs-of-stamps/escape_chain.py --a 12 --b 7 --by-turn
python3 -m unittest discover -s projects/three-runs-of-stamps -v
```

The command imports the standalone gap sweep in `delayed_escape.py`. Its
unpruned comparison and the earlier `count.py` are different searches over
the same model; they are not independent mathematical proofs. Separate
permutation predicates test the five- and seven-face universes.

## The chain and its inverse

Fix a,b>=2 and the labeled orientation from the previous note. Call a valley
insertion adjacent if its new face is immediately beside the previous face
at the moment it is inserted. Later insertions do not change this recorded
history: delete their larger labels before inspecting adjacency.

Start with any legal `M^a` order and any legal first valley. Continue trying
all legal non-adjacent valley insertions. At each subsequent valley step
r, also emit its one adjacent child, but stop branching below that child.
The adjacent same-symbol trapping lemma forces every remaining valley.
If no adjacent child has been chosen by step b, emit the complete open chain.

A stopped chain stores the order only through r, its stop r, and the tail
length b-r. An open chain stores the entire two-run order and has no stop.
`Chain.expand()` inserts the forced adjacent tail. This is a bijection onto
all legal `M^a V^b` orders:

- For any legal order, restrict to labels <=a+r in turn and find the first
  adjacent valley step r>=2. Its restriction is exactly the stored chain;
  the trapping lemma forces its remaining tail. If no such r exists, the
  whole order is the open chain.
- Conversely every emitted chain and its tail are legal. New adjacent
  endpoints do not introduce an intervening old face, so preserve the gap's
  memberships; the trapping lemma then applies.
- The first recovered stop is unique. The mountain order, first valley gap,
  and all pre-stop non-adjacent gaps are also recovered by restriction.
  No two chains can expand to the same order.

This proof holds for arbitrary a,b. It is not a classification of the
non-adjacent geometric trajectories into finitely many closed formulas.
The code's `recover` is this inverse on **known legal orders**, not a complete
legality validator for arbitrary permutations; it checks shape and the
forced tail but relies on that precondition.

## The weighted reduction

Let O(a,j) be the set of open chains with j valley creases: no valley from
step 2 through j was adjacent. O(a,1) contains every legal first valley.
Write A(P) for the adjacent valley extension of P, and F(P,c) for the number
of legal c-mountain completions of P. Define

    N(a,r) = |O(a,r-1)|,
    S(a,r) = sum over P in O(a,r-1) of F(A(P),r),
    U(a,b) = sum over P in O(a,b) of F(P,b).

For r=2,...,b there are N(a,r) stopped chains. Each has an adjacent last
valley at r. Repeated collar removal from `delayed-escape.md` gives

    F(expand(A(P)),b) = F(A(P),r) + (b-r).

Thus, exactly and for arbitrary lengths,

    C(M^a V^b M^b) = U(a,b)
                     + sum(r=2..b) [S(a,r) + (b-r) N(a,r)].

The `base` column sums S, the `tail` column is (b-r)N, and open chains
contribute U without a tail. Every full stack restricts to one prefix,
so this weighted sum also has neither omissions nor duplicate stacks.
The program computes S and U by exact search on those bases; it does not
replace them with the unproved expressions below.

For a prefix count P(a,b)=C(M^a V^b), the same bijection gives

    P(a,b) = sum(j=1..b) |O(a,j)|,
    |O(a,j)| = P(a,j)-P(a,j-1)  (j>=2).

The first equation treats the term j=b as the open chains and each earlier
term as a stopped chain at j+1. This relates the chain census to the proven
two-block counts in [Hull et al., section 3.1 and its edge cases](https://arxiv.org/html/2503.23661v2#S3.SS1).

## A fully counted next bucket

For a>=4 and b>=3, the family stopping at valley 3 has a+2 prefixes and
exactly **(a+2)b+a+10** completions by b mountains. Equivalently
S(a,3)=4a+16. Here is the additional case needed beyond the preceding note.

If the first valley was adjacent, this bucket is exactly D(a,b), already
counted as (a+1)b+a+7. Otherwise the mountain first turned inward at its
last step, and the first valley skipped the older central spiral. Normalize
the mountain order to `w,a,u,R,v`, with w=a-1, u=a-3, v=a-2 and R containing
0,...,a-4 in exterior-spiral order. The first valley goes after R. For the
second valley to be non-adjacent, it must go immediately after u: the A
arc u--v requires it inside, the A arc spanning R excludes R's interior,
and direction excludes the gap beyond the first valley. There is precisely
one such extra chain when R is nonempty, and none when a=3. After the
adjacent third valley its normalized order is

    w,a,u,X2,X3,R,X1,v.

Let L,H be R's first and last faces. Its complete three-mountain gap tree is:

| Z1 | Z2 | Z3 |
|---|---|---|
| (X3,L) | (u,X2) | (Z2,X2) or (X1,v) |
| (X3,L) | (X3,Z1) | (Z2,Z1) |
| (H,X1) | (a,u) | (Z2,u) or (v,+inf) |
| (H,X1) | (H,Z1) | (Z2,Z1) |

There are six leaves. For exhaustiveness, A (parity a-1) contains the old
arcs w--a, u--v and the outer arc of R, plus X1--X2. B contains v--w,
H--u, a--X1 and X2--X3. Nested internal arcs of R introduce no additional
reachable gaps: the outer A arc of R and B's H--u already exclude its
interior. First Z1 is inside u--v and X2--X1 but outside R, leaving the
two displayed gaps. If Z1 is before R, B's H--u restricts Z2 to (u,X2)
or (X3,Z1); if it is after R, B's a--X1 and H--u restrict Z2 to (a,u)
or (H,Z1). The listed A intervals then give the Z3 column. This remains
valid when R is a singleton (omit its empty outer arc), and for odd a
after reflection. Subsequent collar additions give this extra prefix
6+(b-3)=b+3 completions. Adding to D(a,b) gives the stated formula.

The exact gap trees, singleton case, both parities and absence at a=3 are
tested through a=12. At a=b=3, D itself contributes 15 and there is no
extra prefix; applying the a>=4 formula there would incorrectly give 28.

## Recorded exact output

19 November 2026, k=4 with `--verify`:

```
M^4 V^4 M^4: exact decomposition, no fitted formula
first adjacent V | prefixes | base completions | tail bonus | total
               2 |        5 |               13 |         10 |    23
               3 |        6 |               32 |          6 |    38
               4 |        5 |               41 |          0 |    41
            none |        6 |               40 |          0 |    40
total: 22 prefixes; 142 completions
Every tail reduction agrees with direct extension.
```

For k=8 the (prefixes,base,tail,total) rows are:

| Stop | Prefixes | Base | Tail | Total |
|---|---:|---:|---:|---:|
| 2 | 9 | 21 | 54 | 75 |
| 3 | 10 | 48 | 50 | 98 |
| 4 | 12 | 93 | 48 | 141 |
| 5 | 14 | 154 | 42 | 196 |
| 6 | 16 | 231 | 32 | 263 |
| 7 | 18 | 324 | 18 | 342 |
| 8 | 13 | 285 | 0 | 285 |
| None | 14 | 218 | 0 | 218 |

There are 106 prefixes and 1,618 full stacks. The stop-2 bucket is exactly
the earlier first-valley family. Stop 3 includes the second-valley family
and can also include a non-adjacent first valley followed by another
non-adjacent valley; it is not just that family under a different name.

## An exact target for the remaining proof

For equal lengths k>=3, the **unweighted** numbers follow from the cited
two-block formula, its small-b and a=b/a=b+1 edge cases, and the difference
identity above:

    N(k,2)=k+1;
    N(k,r)=k+2r-4             (3<=r<=k-1);
    N(k,k)=2k-3;
    |O(k,k)|=2k-2.

The first and third lines are distinct cases when k=3; the middle range is
empty. The k=2 case is kept separate and has ten stacks by full permutation
enumeration. Unweighted counts do not determine weighted completions.

The following **general weighted formulas remain conjectures**, apart from
the r=3 interior case proved above. They were suggested by
the exact chain census, screened at k=3..13, and are stored separately in
`conjectured_bases`. The main count does not call that function.

    S(k,2) = 2k+5;
    S(k,r) = 2(r-1)k + 8r²-27r+25   (3<=r<=k-1);
    S(k,k) = 7k²-23k+21;
    U(k,k) = (9k²-19k+12)/2.

`--screen` reports enumerated-minus-conjectured residuals, rather than
printing a conjecture as an accepted count. All residuals were zero in
that finite screen. This neither proves the formulas nor rules out an
exception at a later length. In particular, extending the interior S
formula to r=k is false: at k=4 it predicts 69, while S(4,4)=41.

The reduction proves a useful conditional statement: proving precisely
these weighted claims for all k>=3 would prove the proposed cubic. Indeed,
stop 2 contributes k²+k+3, an interior stop r contributes

    k² + (3r-6)k + 6r²-23r+25,

and the final stop and open chains contribute the last two formulas.
Sum r=3,...,k-1 using
sum r = k(k-1)/2-3 and sum r² = (k-1)k(2k-1)/6-5. Twice the interior sum
is 9k³-50k²+93k-72. Adding twice the other three contributions yields
9k³-25k²+30k-12. This is an algebraic implication, **not** a proof of its
unproved weighted premises.

### Finer targets, and a failed shortcut

The command's `--by-turn` mode prints the actual stopped prefixes as well
as their weights. This makes a more specific proposed pattern inspectable.
Let t be the first inward mountain step, d=a-t, and consider r>=5, a>=r+1.
The following are **unproved multisets of individual weights** for stop r:

| Initial mountain type | Proposed weights F(A(P),r) |
|---|---|
| Exterior | 2r-2, 3r-4 |
| d>=r-1 | 2r-2 |
| d=r-2 | 4r-6, 4r-5 |
| d=r-3 | 4r-7, 4r-7 |
| d=r-4 | 4r-9, 4r-8 |
| 1<=d<=r-5 | 2r+2d-1, 2r+2d, 3r+2d-2 |
| d=0 | 2r, 2r, 3r-2 |

An explicit screen of r=5..18 and a in {r+1,r+2,r+5} compared all 595
initial-mountain buckets with these multisets, with no mismatch. The two
small r boundaries must not be folded into this table: at r=4 the last
type has weights 8,8; at r=3 it has 5,6, and the exterior type has only 4.
These exceptions explain why a uniform branch story can fit late rows and
still fail early ones. The table is a target for geometric classification,
not that classification: it does not yet identify the individual paths by
an arbitrary-length inverse construction.

If the table is proved, summing its rows yields the interior S formula.
For r>=5 there are a-r deep types. The three transition rows contribute
24r-42, the d=0 and exterior rows contribute 12r-8, and summing
7r+6d-3 over d=1,...,r-5 contributes (r-5)(10r-15). Including the deep
types gives 2(r-1)a+8r²-27r+25. This reduces the unknown weighted sum to
explicit path-level targets; it does not prove those targets.

One tempting shortcut is false. Collar removal requires the prefix
**before** the appended valley to end in an adjacent pair. An arbitrary
open chain does not satisfy that assumption. For example:

```
Q = 1 3 8 5 6 7 4 9 2 0           (M^6 V^3)
A(Q) = 1 3 8 5 6 7 4 10 9 2 0    (M^6 V^4)
```

Q has three M^3 completions; A(Q) has six M^4 completions, not four.
One A(Q) completion is
`1 3 8 11 13 14 12 5 6 7 4 10 9 2 0`.
Deleting 10 and 11 and lowering higher labels by two gives
`1 3 8 11 12 10 5 6 7 4 9 2 0`, which violates the M direction at crease
9--10. This failed deletion is kept as a regression. A proof of the open
chain weights needs a different map, or a genuine case decomposition.

## Checks and next work

Nine tests pass. They compare the expanded chain set with unpruned insertion
for all a,b=2..8, recover every chain uniquely, and compare **each** tail
reduction with direct completions for all a,b=2..7. Separate permutation
predicates check every five-face order and every seven-face full stack.
The extra double-escape gap tree, complete stop-3 family and failed open-chain
collar extension are tested,
as are the finite weighted residuals through k=13. The k=2..8 totals
reproduce the earlier enumerator's controls. CLI and
invalid-shape/forced-tail boundaries are exercised. An initially unsuitable
test swapped unrelated outer faces; that need not break the inverse's
stated precondition. The final test instead corrupts the forced tail itself.

Next useful proof work is to classify open-chain trajectories by the
initial mountain's first inward step and their encounter with its other
spiral. Prove one weighted identity with a gap table and inverse before
relying on the full sum. The terminal stop and never-stopped chains need
their own boundary arguments. Priority overlap and independent milestone
reconstruction remain unresolved. Do not promote zero residuals, or this
conditional reduction, to a proof of the cubic.

### Literature check, 19 November 2026

The [2026 Sakai publisher page](https://www.tandfonline.com/doi/full/10.1080/00150517.2026.2711255)
again returned 403; its indexed abstract describes a second-stamp boundary
decomposition, and PDF retrieval failed. This does not settle overlap.
I also opened [Sakai's 2023 paper](https://globaljournals.org/GJSFR_Volume23/2-Recurrence-Formula-of-Stamp.pdf):
the introduction counts unrestricted assignments with an exposed first
stamp, and sections II(c,d) track exposed endpoints across that boundary.
That scope differs from our fixed three-run weights; I have not certified
the older recurrence or inferred what the inaccessible newer paper proves.

A further primary lead is [Jia and Mitani, 2025](https://pphmjopenaccess.com/index.php/jpjana/article/download/3443/1672/7548).
Definition 1.2 joins the strip ends into a ring; Definitions 3.1–3.3 and
Theorem 3.6 describe generation by alternating and same-direction pieces.
Their tree components identify rotations and flips, unlike our labeled
orders. Those opened sections do not supply our weighted identities. This
is a model comparison, not a complete non-duplication certificate; no claim
that decomposition or recursive generation is itself new is warranted.
