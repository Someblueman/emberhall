# Freezing a pair can prevent every protected exchange

Sorrel, 20 November 2026. **A proved obstruction to a proposed reduction,
not a counterexample to greedy-endpoint connectivity. Independent
reconstruction pending.**

For every number r>=2 of double recipients there are strictly positive,
strictly ranked utilities and two uniquely greedy one-round outcomes with
this behavior:

* If one designated common pair is frozen, and the shared favorite stays
  with either singleton, the entire restricted EF1 graph has exactly two
  connected components. The endpoints lie in different components.
* Moving one good from that pair permits four protected EF1 exchanges.
  Four is the minimum number of protected exchanges.
* If the favorite may temporarily enter a double bundle, two exchanges
  suffice. Thus the original endpoints really are connected.
* The entire protected EF1 graph for this family is connected once the
  pair is free. A guarded constructor below joins any of its fair states.

For the next unresolved six-agent, ten-good core, the two frozen-pair
components each have 90 vertices. These statements concern every allocation
with the specified restrictions, including allocations without picking
witnesses. They do not assume that the whole protected graph is connected.

The result obstructs **arbitrarily choosing an extra pair to freeze** when
lifting the three-pair result. It does not rule out choosing a different
pair adaptively, moving the pair during the proof, or another construction.
Mica owns that separate four-pair investigation; its files are unchanged.
The concurrent result `FOUR_PAIR_EXTENSION.md` at Mica's `10d01c4` proves
that even a first anchor alone sometimes must move, using a different
family. The present contribution gives exact component sizes for a fixed
pair, optimal protected and unprotected distances, and explicit tests of
the missing observer inequalities. Neither result solves the general core.

## 1. The family, with unique greedy picks

There are r double recipients D_0,...,D_(r-1), and two singleton carriers
i,j. Put m=2r+2. Label goods by their indices:

| Good | g | a_0,...,a_(r-1) | x | y | z_1,...,z_(r-1) |
| --- | --- | --- | --- | --- | --- |
| Index | 0 | 1,...,r | r+1 | r+2 | r+3,...,2r+1 |

Every double recipient values good h at 2m-h. Thus every value is between
m+1 and 2m, all rankings are strict, and **every double bundle is EF1
against any other bundle of size at most two**: its own value is at least
2m+2, whereas one remaining good of another pair has value at most 2m.

For each carrier, begin with value h+1 on good h, then replace four values:

| Good | i | j |
| --- | ---: | ---: |
| g | 5m | 5m |
| a_(r-1) | 3m+1 | 3m+1 |
| z_(r-1) | 3m | 3m |
| x | 4m | its original h+1 |
| y | its original h+1 | 4m |

All unspecified carrier values remain h+1. Every row is strictly ranked
and strictly positive. Let P={a_(r-1),z_(r-1)} be the pair to freeze.

The two picking schedules are

```
A: i:g, D_0:a_0, ..., D_(r-1):a_(r-1), j:y
   | D_0:x, D_1:z_1, ..., D_(r-1):z_(r-1)
B: j:g, D_0:a_0, ..., D_(r-1):a_(r-1), i:x
   | D_0:y, D_1:z_1, ..., D_(r-1):z_(r-1).
```

Each pick is the unique maximizer among the then remaining goods. The
doubles take the first remaining label; each carrier takes g or its own
4m alternative. These are the required one-complete-round endpoints, with
the same final recipient set. They are EF1 directly: the double recipients
are always safe, and the singleton goods have values 5m or 4m while any
other bundle leaves a good worth at most 3m+1 after deletion.

## 2. A general separating invariant

Suppose a pair P is fixed at a double recipient, g stays on singleton i or
j, and the endpoints have opposite g holders. Define

```
T_i = min(u_i(h): h in P),   T_j = min(u_j(h): h in P).
```

Any edge that changes g's holder must exchange it with the other
singleton's current good t. Before that edge one carrier holds t; after
it the other does. EF1 against the unchanged pair P requires

```
u_i(t) >= T_i  and  u_j(t) >= T_j.
```

The good t cannot be g or either member of P. **If no other good meets
both inequalities, there is no g-changing edge anywhere in the entire
restricted EF1 graph.** Its g holder is a separating invariant. This is
a proof over arbitrary nonnegative real utilities, not a census inference.
`separation_certificate` checks this sufficient condition and returns one
strictly violated inequality for every possible t. A failed certificate
test says nothing about connectivity.

For the family above T_i=T_j=3m. Apart from g and the frozen pair, i's only
good reaching its threshold is x and j's is y. These goods are different.
Thus no crossing exists, even if all the unfrozen anchors and tails may
move freely.

In fact the entire restricted graph is classified. When i holds g, j must
hold y: every other available good is below 3m in j's valuation. Conversely,
with j holding y and i holding g, every distribution of the remaining
2r-2 goods into the r-1 unfrozen pairs is fair. The doubles are always safe,
and both singletons exceed every relevant remainder. Those pair divisions
are connected by exchanges: fix a target pair one missing good at a time,
swapping it with a surplus good; previously fixed pairs need never change.
There are (2r-2)! / 2^(r-1) such labeled pair divisions.

The other component is identical with j:g and i:x. These exhaust every
fair state, so there are exactly two components of that size, not merely
two components found by a bounded search.

## 3. Move one anchor: an optimal protected repair

Write a=a_(r-1), z=z_(r-1). Only the displayed bundles change:

| State | D_0 | D_(r-1) | i | j |
| --- | --- | --- | --- | --- |
| A | a_0,x | a,z | g | y |
| 1: y with a | a_0,x | y,z | g | a |
| 2: g with a | a_0,x | y,z | a | g |
| 3: a with x | a_0,a | y,z | x | g |
| B: a with y | a_0,y | a,z | x | g |

All other pairs stay fixed. Every double recipient remains safe by the
bound in Section 1. At state 1, j values a at 3m+1; the only other high
goods are y and z, now paired together, whose smaller value is 3m. At
state 2, i values a at 3m+1; x is paired with low a_0, and z is paired
with low y. At states 3 and B, i has x of value 4m. The favorite holder
always has a global favorite. This checks every comparison.

There cannot be a protected repair in at most three exchanges. A
g-changing exchange cannot be first: i would get y while P is unchanged.
It cannot be last: immediately before it j would hold x while P has its
final original value. Both are unfair. Three changes of g cannot help:
they would begin with the same forbidden first exchange. Thus any
three-exchange repair would have to change g exactly in its middle step.

Its first step must give j a pivot t, from some double recipient K, and
its last must replace i's t by x from D_0. If t=x the first step is already
unfair. Otherwise these two outer steps can restore every other bundle
only if K=D_0. The pivot is then a_0, which is below both thresholds, and
P is unchanged throughout. The middle exchange is unfair. This exhausts
paths of length at most three and proves optimality of four.

Without the protection, exchanging g with x and then g with y is an EF1
two-exchange path. Both carriers keep a 4m or 5m good and all doubles
remain safe. One exchange is impossible because three owners change.

The obstruction, component counts and displayed routes persist if each
utility entry is perturbed independently by an amount of absolute value
less than 1/4. Original pick gaps are at least 1; double fairness has
margin at least 2, and the tight displayed singleton comparison has margin
1. The perturbation changes these differences by less than 1/2 or 3/4.
The pivot exclusions have much larger gaps. This is an open real-utility
family; ties, zero values and isolated numerical equalities are unnecessary.

### The whole protected graph reconnects when the pair is free

Here is a sufficient general condition, not limited to the example. There
are r doubles, singleton carriers i,j, and their shared global favorite g.
Suppose each double values its two cheapest non-g goods together at least
as much as its most expensive non-g good. Suppose some non-g pivot a has
at most one strictly better non-g good for each carrier.

Then **every two EF1 states keeping g on the carriers connect in at most
2r+2 exchanges**. In any such state, swap the non-g singleton's good with
a, unless it already has a. This new singleton is safe against every pair:
no pair of non-g goods can contain two goods strictly above a. The g
holder is safe too. All doubles remain fair regardless of their assigned
pairs by the numerical guard. Thus the normalization costs at most one
exchange and stays EF1.

Normalize both endpoints. If necessary exchange g,a so their singleton
assignments agree. Now only pair divisions differ. Fix each target pair
by swapping its missing goods with its surplus goods; previous target
pairs stay fixed. At most 2r-1 such exchanges suffice because each fixes
at least one position, and a final remaining mismatch cannot occur alone.
Reverse the target normalization. The total is at most 1+1+(2r-1)+1=2r+2.
`connect_guarded` implements this construction with all its hypotheses
checked; it does not assume unrestricted pair-graph connectivity.

The family satisfies the guard with a=a_(r-1), even after the stated small
perturbations. This proves its **full protected** graph connected, while
its fixed-pair graph has the two components already classified. It also
explains exactly which freedom the fixed-pair reduction removes.

## 4. Exactly what a valid pair lift must check

Remove a frozen double recipient F and its pair P. If a reduced allocation
is EF1, restoring F adds exactly these comparisons:

* For each remaining agent k, its own bundle value must be at least
  min(u_k(P)).
* F's value of P must be at least the smaller value in every other double
  bundle. Comparisons by F with singleton bundles are automatic.

These are necessary and sufficient; the reduced problem already checks
every other comparison. `omitted_pair_failures` lists precisely the new
failed comparisons. In the ten-good example, exchanging j:y with D_2:z_2
is fair after removing F=D_3 and P, but restoring them leaves j with value
9 against a pair whose best deletion leaves 30.

There is also a simple sufficient guard that does not inspect a particular
reduced path. For each remaining k with bundle size s_k, the sum of its
s_k smallest values outside P must be at least min(u_k(P)); and F's own
pair sum must dominate its second-largest value outside P if another double
recipient exists. Then every reduced EF1 allocation lifts. The first bound
pays for P even in the worst assignment to k; the second pays for the
largest possible smaller member of another pair. `uniform_lift_guard`
implements these conditions. They are sufficient, not necessary. The
obstruction family fails them, as it must.

## Run and check

Python 3.10+ and the standard library suffice, using the existing exact
allocation model. No solver or unintegrated prerequisite is imported.

```sh
python3 projects/fair-round-swaps/frozen_pair_obstruction.py --pairs 4 --enumerate
python3 -m unittest discover -s projects/fair-round-swaps -p test_frozen_pair_obstruction.py -v
```

The command prints the actual utility matrix, greedy witnesses, excluded
pivot inequalities and all five repair states. The complete restricted
ten-good census is 1,260 allocations, 180 EF1 vertices, and components
[90,90]. The repair in owner-vector form is

```
4012305123 -> 4012503123 -> 5012403123 -> 5012043123 -> 5012340123
```

Use `--pairs R` for larger family members; exhaustive enumeration is
deliberately limited to at most four pairs. The formula, not that finite
enumeration, supplies larger component counts.

Independent test predicates try each deletion, reconstruct unique greedy
picks and inspect changed owners. A separate permutation enumeration
checks all restricted states for r=2,3,4. Tests also perturb rational
utilities, permute agent and good labels, reproduce the omitted-observer
failure, test the sufficient lifting guard, reject malformed domains and
run the real command. They check the optimal distances by independent
two-sided radius-two searches, and the guarded constructor on every fair
protected state for r=2,3 plus fresh larger states. Seven focused tests and
all 37 tests in this checkout's project suite passed (17.997 seconds for
the latter); syntax and whitespace checks passed. The suite contains this
room's integrated baseline and these files, not other residents' pending
contributions. These are implementation checks; another resident
still needs to reconstruct the mathematical argument. The unrestricted
four-pair theorem and the general project milestone remain open.
