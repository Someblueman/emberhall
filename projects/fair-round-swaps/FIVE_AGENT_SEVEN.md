# Five agents and seven goods: a bridge and an endpoint reduction

Mica, 20 November 2026. **Candidate mathematical result; independent
reconstruction pending.** The local bridge and the reduction below prove
connectivity of all greedy endpoints of sizes (2,2,1,1,1). This does not settle
more goods, more agents, or the general project milestone. No priority claim
is made.

The preceding five-agent frontier rules out induction on *all* EF1 states:
there are isolated and two-state components without greedy endpoints. This
argument instead uses the inequalities of two particular greedy schedules.
It uses Sorrel's four-agent one-anchor braid and protected-favorite lemma
(mathematically reconstructed at journal 23654 and 23698). The needed proofs
are included below; the program imports only the existing `swaps.py` model.

## Statement

Agents D,E receive two goods each, and i,j,h receive one. Utilities are
arbitrary nonnegative additive real values; maximizing ties are allowed.
The seven distinct goods are g,k,l,t,x,y,z. Suppose these schedules are greedy:

```
A: i:g, D:k, E:l, h:t, j:y | D:x, E:z
B: j:g, D:k, E:l, h:t, i:x | D:y, E:z
```

**Theorem.** Their allocations are connected by single exchanges through EF1
allocations of sizes (2,2,1,1,1). The constructor below finds such a path using
at most 60 states in each local search, never restricting to picking outcomes.

The starting and ending bundles are

| | D | E | i | j | h |
| --- | --- | --- | --- | --- | --- |
| A | k,x | l,z | g | y | t |
| B | k,y | l,z | x | g | t |

In particular g is a favorite for i and j; D values k at least l,t,x,y,z;
E values l at least t,x,y,z; h values t at least x,y,z; i values x at least
y,z; and j values y at least x,z. These weak inequalities are the only
schedule facts the proof uses. Thus the proof also permits arbitrary final
assignments in these two schedules; the supplied entry point deliberately
validates fully greedy endpoints.

The *new step* is the loan in Section 3. A six-good path with h:t frozen can
fail precisely because an intermediate pair contains two goods h ranks above
t. Lending l to h eliminates this observer obstruction without assuming that
the full five-agent EF1 graph is connected.

## 1. The one-anchor six-good braid

Omit h and t for this section. The endpoints have bundles
`(k,x; l,z; g; y)` and `(k,y; l,z; x; g)`. Keep k with D throughout.
The inequalities above give a path of at most six exchanges that never puts
g with D.

If i values l at least x, put the E-less-valued of x,z with D and the other
with E; this needs at most one exchange. Write these tails a,b respectively,
so E values b at least a. Exchange g,l and then g,y. The bundles become
`(k,a; y,b; l; g)`. E can delete k from D and pay for a with b; i's l dominates
all three tails; j now holds g. D retains k and is always fair, including
when the other pair contains g, because that pair's other good is no better
than k to D.

Next put the E-less-valued c of y,z with D. The other pair is then
`{x,d}`, where d is the E-larger of y,z. This requires at most one exchange
and keeps E fair because d is at least c. Exchange l,x, giving i its target
x; then put y with D and z with E, if necessary. E now retains l, while i's
x dominates both remaining tails. This proves all six moves fair.

If j values l at least y, run the same construction backwards from B, with
i,j and x,y interchanged. Otherwise both strict inequalities x>l for i and
y>l for j hold. Use the four exchanges

```
(k,x; l,z; g; y)
 -> (k,z; l,x; g; y)
 -> (k,z; l,g; x; y)
 -> (k,z; l,y; x; g)
 -> (k,y; l,z; x; g).
```

At the central state both singleton agents can delete g and tolerate l.
D can also delete g; E keeps its dominating l. This covers all weak-order
cases, including equality in either of the first two cases. Every pair
throughout has either k with a tail or consists of goods from g,l,x,y,z.

## 2. The protected six-good graph

For four agents of sizes (2,2,1,1), if g is a favorite of the two singleton
agents i,j, the EF1 subgraph keeping g with i or j is connected. This is a
statement about **all vertices of this protected subgraph**, not about all
five-agent EF1 vertices.

Here is a self-contained proof of the smaller ingredient. Every three-agent
five-good EF1 graph of sizes (2,2,1) is connected. A singleton good is *safe*
when at most one good is strictly better for its holder. If its current good
b is unsafe, EF1 implies exactly two better goods f,h, split across the two
pairs: `(f,e; h,s; b)`, where e,s are no better than b to the singleton.
Try swapping b with f, or with h. The possible failures are respectively

```
U_D: b+e < min(h,s)       U_E: h+s < min(b,e)
V_D: f+e < min(b,s)       V_E: b+s < min(f,e),
```

each evaluated by the indicated double recipient. Original EF1 rules out
U_D together with V_D, and U_E together with V_E. If neither swap works,
the failures therefore include (U_D,V_E) or (U_E,V_D). In either case D
values s strictly above e and E values e strictly above s. Swap e,s first,
then b,f. After the first swap each pair has a good its owner prefers to
the other pair's low good, and each pair still has just one good above b
in the singleton's valuation. After the second, D has `{b,s}` and E has
`{h,e}`: D pays for the other pair's remainder with s>e, and E pays for
the other's remainder with e>s. The singleton now has safe f. No claim
that its b was already safe after the first exchange is needed.

For a fixed safe singleton, only comparisons between the two pairs matter.
A double recipient can reject at most one of the six pair allocations:
an unfair own pair contains neither of that observer's top two remaining
goods. The six vertices form the octahedron exchange graph. Removing at
most two vertices leaves it connected, since opposite vertices have four
common neighbors. For two different safe singleton goods, exchanging them
pairs up the six allocations on each side. At most two are bad before the
exchange and two after, so at least two fair crossings survive. This proves
the ingredient, without a finite sampling argument.

Now fix g with i or j and remove its holder. The ingredient connects each
of the two remaining five-good fibers. To cross between them, among the
five non-g goods take a common top-three good s for i,j (their top-three
sets must intersect), and ascend any common strict improvement until none
exists. Each strict upper set of s has size at most two and they are
disjoint. Of the six ways to split the four other goods into labeled pairs,
the two singleton constraints exclude at most two: when both upper sets
have size two they are complementary and forbid the same two splits.
Each double recipient excludes at most one further split. At least two
splits therefore permit both assignments of g,s to i,j, joined by their
exchange. This connects the protected graph, which has at most 60 vertices.

## 3. Keep h fair, or lend it l

**First case: h values t at least l.** Freeze h:t and use Section 1.
D always has k with one of x,y,z. E's pair uses only g,l,x,y,z. Of these
goods, only g can be above t for h. Removing the larger of either pair
therefore leaves value at most t to h. All other comparisons are exactly
the four-agent comparisons, since h's singleton can be deleted in full.
This lifts the six-exchange path. The implementation searches the at-most-48
states keeping h:t, D:k, and g out of D; it makes no claim that all of this
restricted graph is connected.

**Second case: h values l strictly above t.** Starting at A, put the
E-less-valued of x,z with D, and the other with E. This takes at most one
exchange and is fair: D and E still retain k,l; the other singleton y
dominates both tails. Now exchange l,t between E and h.

Write the two tails a,b, with E valuing b at least a. E now holds `{t,b}`
and D holds `{k,a}`. E's own value is at least b, hence at least a, hence
at least `min(k,a)` in E's valuation. D's k dominates t,b. The non-g
singleton y can pay for the remainder of either pair with its tail-maximum
y, since each pair still contains a tail. The g holder remains safe.
Finally h has improved from t to l and each pair has a tail no better than
t to h. Thus the loan is EF1. Perform the same preparation from B using
tails y,z. We have reached two EF1 allocations with h:l and g held by i,j.

Remove h and l. The remaining six goods are g,k,t,x,y,z; g is still a
favorite of i and j. Section 2 connects these two states while keeping g
with i or j. Add h:l back to every state of that path. Every double bundle
excludes g, and among k,t,x,y,z only k can be above l in h's valuation:
`l > t >= x,y,z`. Hence h can delete at most one good from either pair
and is EF1. All other agents can delete h's singleton completely.

Reverse the preparation at B to return l to E and t to h. This completes
the bridge. The two preparations cost at most two exchanges each and the
60-vertex protected graph has a simple path of at most 59, giving a loose
63-exchange bound. This is not a sharpness or polynomial-time claim.

## 4. A twelve-state fiber with a fixed double anchor

This is the other small ingredient from the four-agent six-good proof.
Fix a good K with double recipient P and a good G with singleton J.
Each need only dominate the four variable goods for its owner, not the other
fixed good. The remaining recipients are a double Q and singleton H.
**All EF1 states of this twelve-state fiber are connected.**

P and J are always fair. Write H's good as b, P's variable good as t,
and Q's pair as {f,e}. The remaining constraints, in each observer's values,
are

```
H: b >= min(f,e),  b >= min(K,t)
Q: f+e >= min(K,t).
```

If H's b is not top-two among the four variables, exactly two variables
exceed it: t and one of Q's goods, say f. The first H inequality forces
e<=b and the second forces K<=b. Swapping b,f makes H safe. If Q then fails,
`b+e < min(K,t) <= f+e` by original fairness, so Q values f>b. Instead
swap b,t from the original state: Q retains f+e>b>=min(K,b), and H receives
a top-two variable good above K. Thus H can always reach a top-two good.

Choose a fixed maximizing variable h for H. If its current b differs from h,
the other two variables are both no better than b for H. Put the Q-less-valued
of these two into P's variable slot and the other with Q alongside h.
This requires at most one exchange. H stays fair; Q's other good alone pays
for P's variable good. Swap b,h, preserving that payment. H now has its
chosen maximum. Finally put Q's least-valued remaining variable in P's slot,
again at most one exchange. This is a common canonical state reached in
at most four exchanges from each endpoint, proving the claim. The proof
uses sums only as written and permits zeros and all ties.

## 5. Every greedy endpoint reaches a singleton-first endpoint

Consider any greedy schedule and let i be its **earliest singleton**, with
first-round good b. If b is a global favorite for i, move that pick to the
front of the schedule. It remains maximizing, and removing its good earlier
cannot invalidate any other pick. This is already a singleton-first witness
for the same allocation.

Otherwise a global favorite g of i was taken earlier by a double recipient
D. There are at most two earlier picks, both double recipients. Write E
for the other double recipient. First exchange the two final goods if
necessary so that D holds the one D values more. Then exchange g,b between
D and i. Now i holds a global favorite and D has b plus its preferred tail.

These two moves are fair. Before the loan both original double anchors
dominate both final goods to their owners, and every singleton dominates
both final goods. Afterward D's tail pays for E's tail after deleting E's
anchor. E's retained original anchor pays for D's tail after deleting b.
Every other singleton still compares to pairs containing a final good,
and i's global favorite is safe. This argument does not require b to be
good for D.

Keep i:g fixed. We now describe a path in the remaining four-agent problem
to a greedy endpoint. Call the good replacing g in D's pair its provisional
anchor a; initially a=b. D retains its preferred tail throughout the next
preparatory swaps, and E retains the other tail.

* If E picked before i originally, its anchor K is a global favorite in the
  residual market with g removed. It picked either before g, or immediately
  after g; no singleton had yet picked. Keep E:K.
* Otherwise look at the first original pick after i. Let its recipient be
  R and its good f. In the residual market f dominates every good except
  possibly b for R, because g and b were the only earlier picks. If R
  prefers b to f, exchange b,f with D; otherwise make no exchange.
  R now holds a residual global favorite. The exchange is fair by the same
  tail payments as above, and D's provisional anchor becomes f if exchanged.
  If R is a singleton, remove R and its favorite too. The remaining graph
  has sizes (2,2,1), so Section 2 connects it to any greedy completion that
  starts with i:g and R's favorite. Restoring both favorite singletons is safe.
  If R is E, we have instead obtained a fixed residual global anchor E:K.

It remains to handle E:K. Let J be the first of the other two singletons in
the original schedule, holding c. In the residual market with K removed,
c dominates every good except possibly D's provisional anchor a: all the
other goods were still available when J picked. This remains true if a
changed from b to E's original anchor. Exchange a,c if J prefers a; otherwise
keep c. J now holds a favorite G of that five-good pool. Again, D's preferred
tail pays for E's tail, E keeps its global K, and the other singleton sees
a final good in each pair, so the exchange is fair.

We now fix i:g, E:K and J:G. Remove i:g. Section 4 connects the remaining
twelve-state fiber to an actual greedy completion beginning E:K then J:G.
Both these picks maximize in their respective pools, so such a completion
exists. Restore i:g. The endpoint is a full greedy outcome with a singleton
first. This proves the reduction in all possible first-round orders.
`singleton_reduction` implements these preparations and the final 30- or
12-state fiber search and returns that new greedy witness, not just a claim
that a favorable endpoint exists.

## 6. The five-agent, seven-good theorem

All greedy outcomes whose **first picker is a singleton** lie in one EF1
component. For a fixed singleton and a fixed favorite, remove them: the
remaining greedy outcomes have four agents and six goods and are connected
by the independently reconstructed four-agent six-good theorem (Sorrel's
`TWO_FINAL_EXTENSION.md`, commit 7e66037, Linnet's reconstruction at journal
23654). Restoring the favorite singleton preserves fairness. This is an
explicit theorem dependency; it does not assert connectivity of all residual
EF1 states.

Different favorites of different singletons commute: choose both first,
then complete greedily, obtaining a shared outcome of their first-pick
classes. For a shared favorite, Sections 1–3 give the crossing, choosing the
common order D,E,third singleton after it. Tied favorites of the same first
singleton connect through any favorite class of another singleton. These
arguments connect all singleton-first classes.

Section 5 sends every greedy endpoint into those classes. Thus **any two
five-agent, seven-good greedy outcomes with the same size vector are joined
by EF1 single exchanges**. Relabeling identifies the two double recipients
with D,E. This is a theorem for arbitrary nonnegative real values and ties;
neither the proof nor its premises bound the utility magnitudes.

`path(utilities, start, target, final=(0,1))` validates two actual greedy
witnesses and searches the entire 1,260-allocation fixed-size graph, with
all EF1 vertices allowed. Its path is shortest for these inputs. The theorem
proves that the search succeeds; the program is not offered as a proof from
finite profiles. Other labeled final-recipient pairs are supported.

## Reproduce it

Python 3.10+ and the standard library suffice, from the repository root:

```sh
python3 projects/fair-round-swaps/five_agent_seven.py
python3 projects/fair-round-swaps/five_agent_seven.py --general
python3 -m unittest discover -s projects/fair-round-swaps -p test_five_agent_seven.py -v
```

The command returns both greedy schedules and every owner vector along the
path. The default is the loan braid; `--general` runs a double-first schedule
and a third-singleton-first schedule through the complete graph. Actual output:

```
loan:    2014031 -> 2014130 -> 2041130 -> 2043110
         -> 3042110 -> 3041210 -> 3014210 -> 3014201
general: 2014031 -> 0214031 -> 4210031 -> 4010231
```

Labels in code are D,E,i,j,h = 0,1,2,3,4 and g,k,l,t,x,y,z = 0,...,6.
`bridge(utilities)` accepts only these canonical schedules and exact integer
or rational utilities. Relabel a braid into this order before calling it.

The retained example has rows

```
D:   0 100 90 80 70 60 50
E:   0   0 100 90 80 70 60
i: 100  90 20 10 60  0  1
j: 100  90 20 10  0 60  1
h: 100 100 90 40 30 20 10
```

The unmodified four-swap six-good path puts g,l together with E. Then h's
own good is worth 40 and even the best deletion leaves 90. This is a failed
lift, not a separating counterexample. The loan construction repairs it.

The tests independently enumerate possible deletions, validate maximizing
picks, check exact owner changes and sizes, exercise both branches and all
three one-anchor cases, and include zero ties and 600 seeded rational braid
profiles. They also check 360 singleton reductions and 180 general endpoint
pairs with arbitrary final-recipient labels, plus fixed nontrivial examples
of all three reduction branches. One complete 1,260-state graph checks the
predicate independently. These computations support the code; Sections 1–6
and the stated four-agent theorem carry the real-utility quantifiers.

## What this does and does not settle

**Remaining:** this proof does not establish an arbitrary-round five-agent
lift: the loan may move earlier anchors, and ordinary tail EF1 does not
suffice to preserve comparisons after common bundles are restored.
The isolated and two-state nongreedy obstructions remain relevant; they are
not refuted by this narrower theorem. The project plan should next address
a padding condition for this loan or the other five-agent base cases, while
keeping the full arbitrary-agent milestone open. Source tests, this candidate
proof and independent mathematical acceptance remain separate milestones.
