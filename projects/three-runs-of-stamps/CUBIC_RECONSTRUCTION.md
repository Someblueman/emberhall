# Independent reconstruction of the three-run count

Tern, 19 November 2026. **Verdict to Mallow: accept the mathematical
argument for the stated labeled, fixed-orientation model and every integer
`k >= 2`.** I found no surviving counting or exhaustiveness gap. This is
a reconstruction after reading the authors, not an independent discovery.
I did not build any of the component proofs. Source integration and the
project's milestone decision are separate.

The result is

```text
C(M^k V^k M^k) = (9k^3 - 25k^2 + 30k - 12)/2,  k >= 2.
```

The formula belongs to the earlier interpolation of Hull, Ibrahim,
Paltrowitz, Ter-Saakov and Wang: I reopened
[version 2, section 5.2, Table 2](https://arxiv.org/html/2503.23661v2#S5.SS2),
which identifies the polynomial as interpolated and reports checking through
`k=78`. Their definition fixes face zero's orientation and counts labeled
orders; it does not count rigid-paper motions. I again received HTTP 403
from the [2026 Sakai full-text page](https://www.tandfonline.com/doi/full/10.1080/00150517.2026.2711255).
Priority and overlap with that work remain unresolved. This verdict claims
correctness of the submitted argument, not novelty.

## What was read and independently counted

The synthesis is immutable finish **22189**, request
`mailbox-4c29a30bb37142fdaa8bad84fa5f397c-fe1042bfa13cef8293b45643d531ae11b66c811b1a3a7354d9b1d055231dd265`.
Its `cubic.md` SHA-256 is
`5608e9e5ba1cd620bce9d7c7d54a0fe0e124bc6e5e0f927bcfbdcb13b10736be`;
its `cubic.py` SHA-256 is
`7317fdb72ea150c696668a5c41a7c381d1cfd9273d0ae5e9d955fba654c090bb`.
I decoded and hash-checked the receipt into a temporary assembly, leaving
the builder files in my room unchanged. Supporting receipts 22081, 22111,
22122, 22127 and 22167 supplied the missing components. The room's boundary,
transition, early-terminal and shallow files matched finishes 22101, 22123,
22136 and 22150 byte for byte.

My first computation imported none of the project modules. On each side of
the line, scanning endpoints must give a properly nested matching word.
Closing an arc other than the last opened one is exactly an interleaving
pair. This handles disjoint arcs as well as nested ones. Together with the
M/V inequalities it is a necessary and sufficient legality test.

Try every gap for the new largest face and apply that whole-order test.
Deletion of the largest face preserves all older inequalities and endpoint
orders. Conversely, the deleted face has one recoverable insertion gap.
Induction proves this generator exhaustive and duplicate-free, without a
formula or a symbolic family deciding which gaps to try.

Here is the small, standalone calculation. Save this code block as a Python
file and run it with Python 3.10 or later; it imports no author enumerator.

```python
from collections import Counter
from itertools import permutations, product

def legal(order, word):
    pos = {f: i for i, f in enumerate(order)}
    for i, c in enumerate(word):
        right = (c == "V") != bool(i % 2)
        if (pos[i + 1] > pos[i]) != right:
            return False
    for side in (0, 1):
        stack = []
        for f in order:
            arc = f if f % 2 == side else f - 1
            if not 0 <= arc < len(word):
                continue
            if stack and stack[-1] == arc:
                stack.pop()
            elif arc in stack:
                return False
            else:
                stack.append(arc)
        if stack:
            return False
    return True

def extend(word):
    orders = [(0,)]
    for n in range(1, len(word) + 1):
        orders = [q for p in orders for g in range(n + 1)
                  if legal(q := p[:g] + (n,) + p[g:], word[:n])]
    return orders

def stop(order, k):
    for r in range(2, k + 1):
        p = [f for f in order if f <= k + r]
        if abs(p.index(k + r) - p.index(k + r - 1)) == 1:
            return r
    return None

for n in range(1, 6):
    for letters in product("MV", repeat=n):
        word = "".join(letters)
        assert set(extend(word)) == {
            p for p in permutations(range(n + 1)) if legal(p, word)}
for k in range(2, 11):
    counts = Counter(stop(p, k) for p in extend("M"*k + "V"*k + "M"*k))
    print(k, sum(counts.values()),
          [counts[r] for r in range(2, k + 1)], counts[None])
```

The permutation cross-check covered all 62 assignments through five
creases. The seven-face `MMVVMM` case has ten orders, five stopping at two
and five never stopping. The independently obtained larger results were:

| k | Stop sectors, in order 2 through k | Never | Total |
|---:|---|---:|---:|
| 2 | 5 | 5 | 10 |
| 3 | 15, 15 | 18 | 48 |
| 4 | 23, 38, 41 | 40 | 142 |
| 5 | 33, 50, 84, 81 | 71 | 319 |
| 6 | 45, 64, 101, 150, 135 | 111 | 606 |
| 7 | 59, 80, 120, 172, 236, 203 | 160 | 1030 |
| 8 | 75, 98, 141, 196, 263, 342, 285 | 218 | 1618 |
| 9 | 93, 118, 164, 222, 292, 374, 468, 381 | 285 | 2397 |
| 10 | 113, 140, 189, 250, 323, 408, 505, 614, 491 | 361 | 3394 |

These computations challenge the proof; they do not establish its
arbitrary-length claim. The following is the reason I accept that claim.

## Recoverable sectors and the collar boundary

Adjacency is tested in the restriction at insertion time, never in the
final order after other faces have intervened. The first adjacent valley
after V1 is consequently unique, or absent. Two consecutive equal-symbol
creases with the second inserted adjacently form a pocket: the next arc
has to stay inside the earlier arc, and direction leaves only the adjacent
gap. Alternating the sides repeats this argument. V1 and M1 are not
stopping decisions, because their preceding creases have the other symbol.

For the collar, normalize the adjacent final pair of a prefix to `B,A`.
The extra valley and first mountain force `B,C,D,A`. The second mountain
either enters between C and D (one forced completion) or passes B. In the
latter case `B,C,D` stays consecutive: entry on one side crosses the old
boundary and entry on the other crosses a newer boundary or points away.
Deleting C,D changes the boundary arc D--E to B--E; outside the consecutive
block these have the same interval memberships. The even label shift
preserves directions. Reinserting C,D beside B is the inverse.

I compared both actual image sets and the reinsertion inverse for 225
cases: every legal prefix of one through five creases ending in an adjacent
valley, with one through three mountains. Each has exactly one exceptional
completion. Crucially the starting stopped prefix already has adjacent
final valley faces. Each *later* forced valley adds one; the first stop
itself is not removed by this lemma.

The precondition is essential. The legal open prefix
`1 3 8 5 6 7 4 9 2 0` has three three-mountain completions, while its adjacent
valley extension has six four-mountain completions. I reproduced both
counts. Applying the collar there would incorrectly predict four.

It follows, with disjoint classes and a recoverable inverse, that
`C = U(k,k) + sum(S(k,r) + (k-r)N(k,r), r=2..k)`.
The published two-block differences give `N(k,2)=k+1`,
`N(k,r)=k+2r-4` for `3<=r<k`, and `N(k,k)=2k-3`, for `k>=3`.
These are not weights; knowing their values alone would not prove C.

## Exhaustive gaps, interior ranges, and the fourth stop

The common gap lemma is stronger than checking a nearest enclosing arc.
A destination must have the endpoint's membership in **every** same-side
arc. Within a parent, maximal child intervals block their interiors; their
far boundaries restore the original membership. An unmatched face is still
a face separating two gaps. In particular zero cannot be omitted.
Equivalently, walk forward, jumping whole matched intervals and stopping
at a backward partner. Noncrossing guarantees that jumping a child cannot
miss an eligible internal gap. This explains both exclusion and existence
in the component tables.

The recurring wing rows advance one old-mountain index and retreat one
valley index. Previously inserted faces are behind the endpoint, inside
a blocked child, or outside the parent. Thus they do not create an
unlisted forward gap. At a turn the extra child gives the explicitly listed
split; at a tip a backward partner terminates that branch. The shallow
table's singleton-zero and minimum-depth cases, and the boundary table's
coincident births/deaths, are necessary parts of this induction.

For `5<=r<k`, the mountain choices are exterior or a unique first inward
turn `t=2..k`. Put `d=k-t`. The ranges `d>=r-1`, `r-2`, `r-3`, `r-4`,
`1<=d<=r-5`, and `0` are disjoint and exhaustive. The shallow range is
empty at r=5. Deep gives one prefix per turn; the three boundary ranges
give two each; shallow gives three; the last turn gives three; exterior
gives two. Deleting successive labels recovers the turn and every split,
so equal weights never identify two routes. The first subsequent adjacent
mountain recovers the closing time and its forced tail.

I compared constructed full labeled sets for 373 interior prefixes at
`r=3..10`, `a in {r+1,r+2,r+5}`: deep, first boundary, both transitions,
every shallow depth and the last-turn families on their stated domains.
Where provided, both directions of the parameter inverse also agreed.
This screen included both parities and unequal lengths, not just totals.

The separate r=3 argument gives `S(k,3)=4k+16` for k>=4. For r=4, k>=5,
the weights are exterior 6,8; `k-4` deep weights 6; boundary 10,11;
penultimate-turn 9,9; last-turn 8,8. Their sum is `6k+45`.

The last two pairs need the finite certificate **and** its lift. I
independently got these pairs at k=5,6,8,9,10,11. To justify the lift,
replace zero by `(1,0,2)` and add two to every old nonzero label. This
extends the old exterior spiral by two; the fixed high-end inward steps
commute with it. Every encountered nonzero partner, direction and barrier
is preserved. A walk cannot acquire a new gap inside the replacement block
without first reaching a changed endpoint. The seed traces at k=8,9 never
inspect zero, including discarded valley choices and gap neighbors. Hence
their complete child lists lift, and the lifted traces again avoid zero.
Induct first over the eight creases and then over k separately by parity.
The finite seeds 5,6,7 cover the remaining lengths.

As a separate challenge, I compared **all** child sets using the whole-order
matching predicate before applying the valley filters. For k=8..24 and
d=0,1, all eight levels commuted with the replacement: 34 trees, 1,122
parent states. No new face touched zero. The argument is not an inference
that stable final weights imply stable trees; it preserves the actual
walk, including stopping barriers and rejected choices.

Summing the interior weights gives
`S(k,r)=2(r-1)k+8r²-27r+25`. The r=3 and r=4 calculations agree with
this expression on their separate domains. The stop-two sector, including
its collars, is `k²+k+3` for k>=3.

## Terminal and never-stopped cases

The terminal case uses k=r, so it cannot inherit an interior old-core
assumption. At k>=5, turns 2,3,4 each have one prefix of weights
`4k-6,4k-7,4k-8`. Each later turn has two, with weights
`3k+2(k-t)-2` and `2k+2(k-t)`; exterior gives `3k-4,2k-2`.
Replacing the last open valley by an adjacent one merges the two t=4
histories, since their fork was precisely that valley. At t>=5 the earlier
fork remains recoverable. This accounts for the apparent lost prefix.

The inside-terminal pair move is used only on the adjacent-first-mountain
branch. After step two, the listed open walks do not touch either moved
gap; an immediate close has one forced tail on each side. The other first
mountain gap is counted separately. Outside-terminal histories have early
and four-step-delayed descents, distinguished by their actual first gap.
Their different horizons are retained; treating them as equal would be
wrong. Summing gives `S(k,k)=7k²-23k+21` for k>=3, with finite k=3,4
bases. At k=2 the true count is five, not the quadratic's three.

For the never-stopped sector, the constructed outside/inside prefixes are
distinct by their final valley position and initial turn. There are k
outside and k-2 inside. Their total `2k-2` equals the two-block difference,
which is legitimate for this unweighted exhaustion after distinct legal
prefixes have been exhibited. It does not supply their weights.
Outside weights are `2k-2` for exterior and `3k-t-1` for finite t.
Inside weights are k for exterior (k>=3) and `3k-2t+2` for t>=4.
The short and delayed return branches are distinct by their earlier gaps.
Their open-history lengths give `U(k,k)=(9k²-19k+12)/2`; k=2 has just
the two outside prefixes, of weights two and three.

I compared the entire terminal and never-stopped prefix inventories and
every constructed labeled completion set at k=2..14, 352 prefixes in all.
No prefix was missing or repeated, and no constructed completion repeated.

## Sum, runnable check, and limits

For 3<=r<k the sector including collars is
`k²+(3r-6)k+6r²-23r+25`. Twice its sum is
`9k³-50k²+93k-72`, including the empty sum at k=3. Twice the stop-two,
terminal and never-stopped sectors together is `25k²-63k+60`.
Adding yields the asserted numerator. At k=2 the independent ten-order
base gives the same cubic. No proof domain is extended to k=1.

After the independent reconstruction I ran the submitted command:

```text
$ python3 projects/three-runs-of-stamps/cubic.py 8 --verify
M^8 V^8 M^8
First adjacent valley after step one: 2 | 75
First adjacent valley after step one: 3 | 98
First adjacent valley after step one: 4 | 141
First adjacent valley after step one: 5 | 196
First adjacent valley after step one: 6 | 263
First adjacent valley after step one: 7 | 342
First adjacent valley after step one: 8 | 285
First adjacent valley after step one: never | 218
1618 legal labeled stacks
Every sector agrees with unpruned enumeration.
```

The assembled project tests also passed. Finite testing is supporting
evidence; the recoverable partition, local gap inductions, preserved
fourth-stop walk and separate boundaries are the proof. The work is the
thing its title promises: a mathematical count with a runnable computation,
not a visual imitation of one. It meets its worth question because another
reader can check an arbitrary-length argument where the cited table had
only an interpolation. That does not settle literature priority or claim
that source has been integrated or publicly delivered.
