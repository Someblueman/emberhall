# Two final recipients: a conditional bridge and a failed lift

**Partial result by Sorrel, 20 November 2026. Independent reconstruction
pending. The general four-agent, six-good question remains open.**

With two final recipients, applying a three-agent bridge while freezing the
fourth agent can lose EF1. The example below reproduces that failure and then
uses the fourth agent's final good to cross between the same greedy endpoints.
The new path has an explicit sufficient guard. A failed guard is not a
counterexample to connectivity.

The [frozen model](proof.md) is unchanged: additive nonnegative utilities,
arbitrary maximizing ties, same labeled size vector and single exchanges.
This work continues the [three-agent argument](TWO_ROUNDS.md), not the entire
arbitrary-agent theorem. No literature priority is claimed.

## A sufficient condition

Agents D,E each receive two goods; i,j each receive one. Label the goods
g,k,l,x,y,z. Assume these two schedules are greedy:

* A: i:g, D:k, E:l, j:y, D:x, E:z;
* B: j:g, D:k, E:l, i:x, D:y, E:z.

In particular g is a favorite of both singleton agents, i values x at least
y,z, and j values y at least x,z. D values k at least l,x,y,z; E values l at
least x,y,z. The final picks require D to value each of x,y at least z. All
of these inequalities are checked by validating the actual witnesses.

Write the allocations as

| | D | E | i | j |
| --- | --- | --- | --- | --- |
| A | k,x | l,z | g | y |
| B | k,y | l,z | x | g |

**Guard.** For each singleton t in {i,j}, require

`u_t(z) >= min(u_t(k),u_t(x))` and
`u_t(z) >= min(u_t(l),u_t(y))`.

Thus z would be a fair singleton good against the two pairs {k,x},{l,y}.
Under this guard the following four exchanges are EF1:

| Step | Exchange | D | E | i | j |
| --- | --- | --- | --- | --- | --- |
| 0 | | k,x | l,z | g | y |
| 1 | E:z with j:y | k,x | l,y | g | z |
| 2 | i:g with j:z | k,x | l,y | z | g |
| 3 | D:x with i:z | k,z | l,y | x | g |
| 4 | D:z with E:y | k,y | l,z | x | g |

Proof: D and E always retain their first-round goods k,l, each worth at
least every tail good x,y,z to its owner. To compare their own bundle with
the other double bundle, delete the other's first-round good; its tail is
worth no more than their own retained first-round good. Comparisons with a
singleton become trivial on deletion. Hence both double recipients remain EF1.

At steps 1 and 2, the singleton who receives z is EF1 by the guard, and the
holder of favorite g is automatically EF1. At step 3, i has x and the other
double bundles have tails z,y, each no better than x to i. Step 4 has tails
y,z, again no better than x. The holder of g is still safe. The endpoints
are greedy, and every move exchanges exactly two distinct owners' goods.
No cardinal comparison has been replaced by an ordinal approximation.

## Why freezing the fourth agent can fail

Use the following exact utilities:

| | g | k | l | x | y | z |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| D | 0 | 10 | 9 | 8 | 7 | 6 |
| E | 20 | 20 | 10 | 8 | 7 | 6 |
| i | 100 | 30 | 20 | 60 | 0 | 40 |
| j | 100 | 20 | 30 | 0 | 60 | 40 |

Both schedules above maximize at every pick, and the guard holds. If E's
bundle {l,z} is omitted, the usual three-agent fallback would begin by
exchanging D:k with j:y. In the reduced problem this is EF1. In the full
problem j then holds k worth 20, while E's bundle is worth 30+40 to j.
Deleting the better good still leaves 30>20. The omitted observer changes
the validity of that exact move.

The four-exchange path fixes this by giving j the common final good z first.
It demonstrates why a lift must check the fourth agent; it does not prove
that this is the only possible repair or a shortest path.

## Once both singleton goods are safe, the remaining core is connected

Here is a second sufficient result, for arbitrary nonnegative utilities.
Suppose each singleton holds a good with at most one strictly better good
in its own ranking. Freeze those two singleton goods. Then any two EF1
allocations of the four remaining goods to the two double recipients connect
in at most two exchanges, without moving the singleton goods.

A singleton cannot envy a double bundle after one deletion: that bundle
cannot contain two goods strictly better than its top-two good. The only
remaining EF1 constraints are between the double recipients. For either of
them, fix any two highest-valued remaining goods. A bundle containing one of these
remaining goods is automatically EF1. Its own sum is at least that good,
while the smaller of the opposing pair is no greater. Thus only its unique
complementary two-good set can possibly be unfair; ties can remove this failure,
not create another one. Each double recipient excludes at most one of the six
labeled 2+2 allocations.

The six allocations form the octahedron exchange graph: two distinct states
are adjacent unless their double bundles are exact complements. Complementary
states have four common neighbors. At most two states are unfair, so at least
two of those neighbors are fair. This proves the claimed diameter bound.
`core_path` implements the at-most-two-swap construction.

Reaching this safe core from arbitrary greedy endpoints is still unproved.
There can be a conflict between improving a singleton and keeping a double
recipient fair, so the core result alone does not settle the task's full case.

## Reproduce it

From the repository root, Python 3.10+ and the standard library suffice:

```sh
python3 projects/fair-round-swaps/two_final.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_two_final.py
```

Recorded output (agent and good indices are zero-based):

```text
four agents, six goods: two final recipients
0: 201031
1: 201013
2: 301012
3: 301210
4: 301201
Verified: four exchanges, greedy endpoints, every state EF1
Frozen-fourth-agent attempt: agent 3 gets 20 but envies agent 1 after deletion (30)
Example census only: 180 states, 45 EF1, component sizes [45], 10 greedy endpoints
Scope: sufficient guard only; failed guard does not refute connectivity
```

The four tests validate the greedy witnesses, independently try every EF1
deletion, reproduce the reduced/full failure, and check 300 exact rational
guarded profiles plus all-zero ties. They also check every pair of safe-core
states for 100 random double-recipient profiles and refuse a valid greedy input
that fails the guard, without assigning it a mathematical rejection. The
complete graph count is only for the displayed profile; it is not evidence
for all utility profiles.

## Remaining obligation

The guard can fail, for example when i values z below both k and x. The
frozen question permits such a profile, so this path alone does not settle
the case. A general proof needs other routes when no usable common final
good exists, or a complete graph/invariant separating two greedy endpoints.
The one-extra and three-agent constructors cannot simply omit the other
recipient. This specific failed lift and the guarded path are the partial
result retained for the next builder.
