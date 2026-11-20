# Four agents and six goods: removing the final-good guard

Candidate theorem by Sorrel, 20 November 2026. **Independent reconstruction
pending.** This settles a size case, not arbitrary numbers of rounds or agents.
No priority claim or new literature search is made here.

**Theorem.** For four agents and six goods with nonnegative additive real
utilities, any two greedy recursively balanced picking outcomes with the same
size vector are joined by single exchanges through EF1 allocations. Ties are
arbitrary. Relabel the agents so D,E receive two goods and i,j one each.

The model and meaning of EF1 are unchanged from [proof.md](proof.md). The
proof below actually connects the larger family with a greedy first complete
round and arbitrary assignment of the two final goods to D,E. Every such
allocation is EF1 by the free-final-round lemma in [FRONTIER.md](FRONTIER.md).
An arbitrary final assignment is used explicitly, never asserted to be greedy.

The earlier conditional bridge in `TWO_FINAL.md` remains valid but is not
needed here. Its common-final-good guard can fail in the new example.

## 1. An unguarded braid with one anchor retained

Use six distinct goods g,k,l,x,y,z. Assume

* g is a favorite of both i,j;
* D values k at least l,x,y,z, and E values l at least x,y,z;
* i values x at least y,z; j values y at least x,z.

We connect these allocations, keeping k with D throughout:

| | D | E | i | j |
| --- | --- | --- | --- | --- |
| A | k,x | l,z | g | y |
| B | k,y | l,z | x | g |

These assumptions follow from the first-round braids i:g,D:k,E:l,j:y and
j:g,D:k,E:l,i:x. They impose no maximizing condition on the final assignments.
D is always EF1 in the paths below: the other double bundle either contains
two of l,x,y,z, each no better than k, or contains g and one such good; delete
g in the latter case. Comparisons with singleton bundles are automatic.

### Lending l when i values it at least x

Choose t to be the less valuable of x,z **to E**, and let r be the other.
Start by exchanging x,z between D,E if necessary, reaching

`D={k,t}, E={l,r}, i={g}, j={y}`.

Now exchange g,l, then g,y:

| | D | E | i | j |
| --- | --- | --- | --- | --- |
| after g,l | k,t | g,r | l | y |
| after g,y | k,t | y,r | l | g |

E's own value is at least its value of r, which is at least its value of t;
deleting k from D therefore establishes EF1 for E at both steps. Agent i
holds l, which it values at least x,y,z, so it is safe against both double
bundles, even when E contains g: delete g. Agent j first holds its favorite
tail good y, then g, and is safe too.

Next choose t' to be the less valuable of y,z to E. Put t' with D and the
other two tail goods with E. This takes at most one exchange from the current
tail assignment. It is fair: E has x and the larger of y,z, whose value alone
is at least t'; both singleton holders are still safe. E now contains x.
Exchange x,l to give i its target x, then rearrange D,E's tails to y,z.
E retains l in the last step, and i values x at least both tails. All states
are EF1. There are at most six exchanges.

If instead j values l at least y, apply exactly this construction backwards
from B, interchanging i,j and x,y. That also retains k.

### When neither singleton wants l

The only remaining case has `u_i(x)>u_i(l)` and `u_j(y)>u_j(l)`.
Use four exchanges:

`A -> (k,z; l,x; g; y) -> (k,z; l,g; x; y)`

`  -> (k,z; l,y; x; g) -> B`.

Semicolons separate D,E,i,j. In the central state each singleton values its
own good above l, so deleting g from E is sufficient. E retains l and can
delete k from D. The other states are fair by the favorite-tail inequalities.
The three cases exhaust all weak comparisons, including ties.

## 2. The twelve-state residual lemma

Fix one good k with double recipient D and one good g with singleton i.
Each fixed good need only dominate the **four variable goods** for its own
holder. It need not dominate the other fixed good. There remain a double
recipient E, a singleton j and one variable slot for D.

**Lemma.** Every EF1 allocation of these four variable goods connects to every
other while keeping the fixed goods in place, in at most eight exchanges.

D and i are always safe. Write b for j's good, t for D's variable good, and
{f,e} for E's pair. For a given observer, write its value without a subscript
when that observer is clear. The only constraints left are

`u_j(b) >= min(u_j(f),u_j(e))`,

`u_j(b) >= min(u_j(k),u_j(t))`,

`u_E(f)+u_E(e) >= min(u_E(k),u_E(t))`.

For fixed b, the three placements of the other goods in D's slot form a
triangle of single exchanges. At most one placement violates E's constraint:
failure requires that slot's good to be worth more than the sum of the other
two to E. Two different goods cannot each exceed the sum of the other two
when values are nonnegative.

### Upgrade j to a top-two variable good

If b has at most one strictly better variable good, skip this paragraph.
Otherwise the first inequality says E's pair contains at most one better
good; hence exactly two variable goods are better than b: t and one member
f of E's pair. Its other member e is no better than b. The second inequality
forces `u_j(k)<=u_j(b)`.

First try exchanging b,f. The new singleton is top-two and above k, so only
E can be unfair. If E is unfair, then

`u_E(b)+u_E(e) < min(u_E(k),u_E(t)) <= u_E(f)+u_E(e)`,

where the last inequality is the original state's fairness. Thus E values
f strictly above b. Instead exchange b,t from the original state. E keeps
{f,e}, whose value is at least b and hence at least min(k,b) in E's valuation.
The new singleton t is top-two and above k in j's valuation. This alternative
is therefore fair. One of the two direct upgrades always works; they cannot
both fail from an initially fair state.

### Upgrade top-two to a chosen maximum

Choose once and for all a maximizing variable good h for j, with a fixed
label rule for ties. If j already holds h, skip this paragraph. Of the two
variable goods other than b,h, put the one less valuable to E in D's slot,
and put h and the other with E. This takes at most one exchange from the
current state. Both of those two goods are no better than b to j, because b
was top-two and h is a maximum. Thus j is safe; E is safe because its pair
contains the larger of the two in E's valuation. Exchange b,h. E remains
safe for the same reason, while j now holds its chosen maximum.

Finally put E's least-valued remaining variable good in D's slot. This is
one exchange at most and leaves E fair; j's maximum makes j safe regardless.
The resulting allocation is a single canonical state. Each endpoint reaches
it in at most four exchanges, proving the lemma. This is a proof for arbitrary
nonnegative real values, not a classification by bounded integer samples.

## 3. Connectivity when a double recipient picks first

Fix D's first good k, a maximum for D among all six goods. Consider any
greedy-first-round/free-final outcome starting with that pick.

If a singleton is next, it holds a favorite among the five remaining goods.
If E is next, write f for E's first good, b for the earliest singleton J's
good, c for the other singleton's good, t for D's tail and e for E's tail.
J values b at least c,t,e. The later singleton values c at least t,e.

If b is a favorite among the five goods after k, nothing needs changing.
Otherwise f is such a favorite for J. Exchange f,b. The only possibly failed
comparison is E against D: all remaining double bundles contain a tail good
no better than each singleton's own good. If E fails, then

`u_E(t)>u_E(b)+u_E(e)`.

Instead exchange e,t first while E still holds f, then exchange f,b. The
first state is safe because f is E's original maximizing pick, both t,e are
no better than either singleton's chosen good, and D retains k. The second
state is safe because E now holds b,t and t is worth more than e to E.
Thus in at most two exchanges a singleton holds a favorite of the five goods
after k, while D still holds k. This need not be another greedy outcome.

For every singleton i and every favorite g of its five-good pool, let C(i,g)
contain **all fair states** fixing D:k and i:g. Section 2 makes each C(i,g)
connected. Every outcome of the D-first class reaches one of these sets by
the preceding upgrade.

All these sets connect to one another. For different singleton agents with
distinct favorites, perform both favorite picks then finish a greedy round;
this gives a common state. For a shared favorite g, put E's favorite l of
the remaining four goods next and choose x,y as the two singletons' favorites
of the last three goods. Section 1 joins the resulting free-final states
while retaining D:k. For two tied favorites of the same singleton, pass
through any favorite class of the other singleton. Hence the entire D-first
class is connected. The argument applies equally when E picks first.

## 4. Joining the first-pick classes

If a singleton i picks first, fix its favorite g and remove it and that good.
The remaining system has three agents, five goods and exactly one absent
final recipient. The near-complete theorem in [FRONTIER.md](FRONTIER.md)
connects its greedy-first-round/free-final outcomes. Adding back i:g preserves
EF1: i has a global favorite and every other agent can delete its singleton
bundle entirely. This proves each fixed singleton-first class connected.
This step uses that theorem's enlarged free-final family, not merely its
greedy endpoint statement.

Section 3 proves the corresponding assertion for each double-first class.
Now take two distinct first agents. If their favorite goods differ, the two
picks commute and give a common free-final outcome. If the favorite is shared
and both agents are singletons, use Section 1, letting D,E make their common
first picks in between the carriers.

If at least one carrier is a double recipient, use the usual shared-favorite
coupling: give g first to one carrier in each run, let the two other agents
choose identically from the common pool, and let the opposite carriers choose
last in the first round. If these last goods coincide, one exchange closes
the runs. Otherwise the two final pools are {x,z} and {y,z}; assign x and y
respectively to a carrier who is a double recipient and assign z to the other
double recipient. The resulting allocations differ by one exchange involving
g. These are allowed free-final assignments and are EF1. This also works
when both carriers are double recipients.

Different tied favorites of the same first agent connect through any other
first agent's favorite class. This exhausts first picks and proves the theorem.

The proof does **not** say that the whole six-good EF1 graph is connected,
that every intermediate state is greedy, or that all partial first-round
prefixes have connected fibers. In fact, fixing both double anchors can
disconnect the local braid. Section 3 deliberately fixes only the first one.

## Run and check

From the repository root, Python 3.10+ with the standard library:

```sh
python3 projects/fair-round-swaps/two_final_extension.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_two_final_extension.py -v
```

The first command prints the following owner vectors (zero-based D,E,i,j):

```text
201031 -> 201130 -> 102130 -> 302110 -> 301210 -> 301201
```

Both singleton agents value the common final good at 1 and their respective
favorite tail at 60; the old guard fails. All five exchanges are checked by
the exact EF1 predicate. `bridge` implements Section 1, `residual_path`
implements Section 2, and `path` validates two fully greedy witnesses before
searching the entire fixed-size EF1 graph, including non-greedy vertices.
It returns a shortest path for this fixed six-good problem.

The tests use a separate all-deletions EF1 predicate, test all three bridge
branches with exact rational utilities and zero ties, preserve a case where
the first direct residual upgrade fails and the second works, check every fair residual endpoint pair
in fresh cardinal profiles, and check greedy endpoints with a full graph
search. They support the implementation; Sections 1–4 supply the universal
argument. An exploratory installed symbolic solver helped locate the local
lemmas; neither the proof nor the delivered code depends on it.

The next unresolved case remains four agents with longer complete-round
prefixes (and the wider arbitrary-agent problem). The fixed-first-round
lifting lemma does not on its own lift this proof's changes to an earlier
anchor. Do not count this six-good result as the general project milestone.
