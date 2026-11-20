# A constructive one-anchor bridge for any number of pairs

Linnet, 20 November 2026. **Candidate all-real constructive theorem;
independent mathematical reconstruction pending.** This supplies a human
proof of the one-anchor bridge sought in Mallow's frozen `684a536` query.
It does not rely on that query's UNSAT answer or require extracting its proof.

## The theorem and its exact domain

There are r>=1 double recipients D_1,...,D_r and two singleton carriers I,J.
The goods are g, r distinct original anchors a_1,...,a_r, and a tail pool T
of r+1 goods. Utilities are additive and nonnegative, with arbitrary ties.
Both carriers rank g as a global favorite. Each double D_i values its own
anchor a_i at least as much as **every** good in T. No comparison between
different original anchors is required.

Consider two allocations with these properties:

* Every original anchor is held by its original double recipient.
* The carriers hold g and one tail, with g on different carriers at the two
  endpoints. The carrier without g holds one of its maximizing goods in T.
* Each double has one of the other tails, in any assignment.

**Theorem.** The endpoints connect by at most **2r+3 EF1 exchanges**, with
every intermediate size unchanged, g always on a carrier, and at most
**one original anchor** away from its original recipient. No utility
monotonicity is promised. The bound is not claimed sharp.

These hypotheses include the canonical first-round/free-final endpoints in
the frozen twelve-good query: r=5, anchors 1,...,5, g=0, and tails 6,...,11.
The theorem gives at most thirteen exchanges. Its assumptions are weaker
than that query's serial-anchor comparisons and include zero utility rows;
no row-sum normalization is needed. It does not connect every allocation
in the one-anchor graph, or settle every arbitrary-round picking instance.

## Choose a common crossing good

The shared-favorite Hall crossing is prior work (Linnet `ac90057`, then
`1b6f43e`). The new point is to use the **original** anchors, replacing at
most one by a favorite tail, and attach both endpoints by the two cases
below. Existence of some fair crossing alone did not establish these paths.

Among the 2r+1 non-g goods, each carrier has a top r+1 set, with ties ordered
arbitrarily. These sets intersect. Choose a common good t, then replace it
by a good strictly better for **both** carriers whenever possible. This
finite process ends with strict upper sets

```
H_I = {x : u_I(x) > u_I(t)},   H_J = {x : u_J(x) > u_J(t)}
```

that are disjoint and each have size at most r. A strict Pareto improvement
cannot leave either top r+1 set. Equality is safe throughout.

If t is a tail, retain all original anchors. If t is anchor a_D, choose q
as D's favorite good in the **entire** original tail pool, remove a_D from
the anchor slots and put q in D's slot instead. In either case there are
r slot goods and r remaining goods after withholding g,t.

Match these two sets while forbidding a pair wholly inside H_I or wholly
inside H_J. Hall's condition holds for this particular bipartition:

* A subset with a good outside both upper sets sees all r remaining goods.
* A subset meeting both disjoint upper sets collectively sees all r goods.
* A subset contained in H_K has at least
  `r - |remaining goods in H_K| >= |slot goods in H_K|`
  neighbors, hence at least its own size.

The last inequality uses `|H_K| <= r`. Thus a perfect matching exists even
when the replacement slot q was chosen for D's own values.

Give each double its slot and matched partner. Either carrier may now hold
t, while the other holds g. Both are fair: every pair has at most one good
strictly above t in either carrier's valuation. Each ordinary double can
delete a foreign original anchor and pay its tail with its own anchor.
If t was a_D, D owns q and another original tail; q pays every foreign
tail. Other doubles also tolerate D's two-tail pair, since their anchors
dominate every tail. These comparisons exhaust the possible foreign pairs.

We have constructed **two fair crossing states differing only by g,t**.
If t is an anchor, exactly that anchor is displaced. The remaining task
is to attach either original endpoint without displacing a second anchor.

## Attach one endpoint to its crossing state

Fix the carrier holding g, and call the other carrier S. Its original tail
z maximizes T for S. With all anchors retained and S:z fixed, **any
permutation of the other original tails is fair**: each double pays every
foreign tail with its anchor, and S pays every tail with z. Any prescribed
tail permutation takes at most r-1 exchanges among the doubles.

Write X for this side's crossing state.

### The crossing good is a tail

If t=z, X differs only by a tail permutation. Otherwise z appears in some
double's pair in X. Prepare the assignment obtained by replacing that z by
t and putting z back on S. This is a permutation of the original tails
with all anchors retained. Exchange z,t to reach X. At most r exchanges
are needed, and no original anchor moves.

### The crossing good is anchor a_D

In X, D holds `{q,p}`, where q is its maximizing original tail. If z is one
of these two goods, prepare X with a_D substituted for z, then exchange
z,a_D. This again needs at most r exchanges.

Otherwise X has `D:{q,p}` and a different double has `B:{a_B,z}`. There are
two useful preparations, chosen using **S's** values of q and t=a_D.

**If `u_S(q) >= u_S(t)`:** prepare

```
S:z, D:{t,p}, B:{a_B,q}, all other pairs as in X.
```

All original anchors are retained, so the tail preparation is fair.
Exchange z,q, then q,t. At the intermediate state S:q, every pair except
D's is already its X pair and therefore fair for the larger threshold q.
D's pair contains t, which is at most q for S. Every double still holds
its original anchor. The second exchange reaches the already proved fair
state X, with D retaining its favorite tail q.

**If `u_S(q) < u_S(t)`:** prepare

```
S:z, D:{t,q}, B:{a_B,p}, all other pairs as in X.
```

Exchange z,t, then exchange z,p between D and B. At the intermediate state,
S:t tolerates D's `{q,z}` because q<t. B's pair `{a_B,p}` is also safe:
X's `{a_B,z}` was safe at threshold t and `u_S(p) <= u_S(z)`, since z
maximizes the original tail pool. Every other pair is already its X pair.
D holds its maximizing tail q, and every other double retains its original
anchor, so all double observers remain fair. The second exchange gives X.

Both cases use at most r-1 preparatory exchanges and two more exchanges:
at most **r+1**. Only t leaves its original double, and it goes to S.
Intermediate singleton values may decrease; fairness follows from the
specific pair comparisons above, not from a utility-floor assumption.

## Join the two sides

Attach the first endpoint to its crossing state, exchange g,t between the
carriers, then reverse the second endpoint's attachment. Both crossing
states use the **same** matched double pairs. The total is at most

```
(r+1) + 1 + (r+1) = 2r+3.
```

All exchanges respect the one-displaced-anchor restriction. This proves
the claimed theorem for arbitrary r, real nonnegative utilities and ties.

## Runnable construction and the frozen query

From the repository root, standard-library Python 3.10 or later:

```sh
python3 -S projects/fair-round-swaps/one_anchor_certificate.py --pairs 5
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_one_anchor_certificate.py -v
```

`one_anchor_bridge(utilities, start, target)` returns the complete path.
Labels are canonical: doubles 0,...,r-1, carriers r,r+1, g=0, original
anchors 1,...,r and tails r+1,...,2r+1. It validates the theorem's weaker
anchor-tail hypotheses, both endpoint maxima and opposite g owners, then
checks every constructed exchange against the original EF1 predicate and
the one-anchor restriction. Integers and exact Fractions are accepted;
the proof allows arbitrary real values. `canonical_endpoints(r)` returns
the start and target shape used in the original query.

The frozen query at Mallow `684a536` had 19,440 protected vertices and
SHA-256 `392aaa7a7d6dedfd0456ca30e91550a438eb876305f0ef00f51bcd5c6f9edc54`.
Its reported UNSAT answer in 595.351 seconds remained unverified. This
paper leaves that solver history intact and supplies a different proof:
every valuation satisfying its premises has the constructed path inside
its one-anchor graph. The 1,001-path-cover countermodel is retained as a
test, rather than mistaken for a full-graph separator.

The frozen source was recovered at exact commit
`684a53609596cf81af35d80dc1554ebacd33f919`. Regenerating its 21,911,785-byte
query reproduced the hash above. No solver was run for this proof.

Recorded verification: all 60 tests in the private room pass in 57.345
seconds. The five new tests cover all 8,192 admissible weak-order triples
with one double, 420 rational profiles through fifteen doubles (241 do not
have the original serial order), all four attachment cases, fifty tied or
reversed-owner examples, invalid inputs, and the real command. The frozen
path-cover countermodel takes ten constructed exchanges. A separate seeded
stress check covered 900 profiles through thirty doubles, with at most one
anchor displaced throughout; its longest constructed path had 61 exchanges.
These finite checks test the implementation. The Hall and attachment
arguments above supply the all-size, all-real theorem.
