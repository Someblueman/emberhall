# Greedy endpoints can require a temporary loss

Fern, 20 November 2026. **Candidate theorem; independent reconstruction pending.**

Extra automatically fair pairs do not make value-preserving attachment possible.
For every number of double recipients `r >= 3`, there are positive, strictly
ordered utility rows and two actual greedy picking outcomes such that:

- A, B and the active singleton J each strictly prefer the target; I is unchanged.
- Every exchange path to that target temporarily lowers at least one of
  A, B, I or J below its initial value, even if unfair intermediate states
  are permitted and the initially protected good is allowed to move.
- There is an EF1 path attaining the exact least possible maximum loss.

The automatically fair recipients may lose value, including at the target.
Thus this is a statement about preserving the two exceptional recipients and
the singleton recipients, not a Pareto improvement for every agent.

This rules out a monotone strengthening of the project's desired theorem.
It does **not** refute EF1 connectivity: a five-exchange fair path is given.
The [frozen model](proof.md) is unchanged. No literature priority is claimed.
The earlier six-good monotone warning at Fern/Rook `13b55dd` motivated this
investigation; the greedy endpoints, arbitrary-size extension and exact loss
bound below are the new obligations.

## The greedy-endpoint family

There are r pairs, agents A=0 and B=1 unrestricted, automatic recipients
2,...,r-1, and singleton agents I=r and J=r+1. Set m=2r+2. The initial
allocation is

```
I:0   B:1,5   J:2   A:3,4   C:6,7   D:8,9   ...
```

The following table gives base values. Unlisted goods have base value zero
for A, B, I and J.

| Observer | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 0 | 10 | 19 | 20 | 10 | 0 | 12 | 0 |
| B | 0 | 10 | 0 | 20 | 0 | 10 | 0 | 0 |
| I, J | 30 | 20 | 10 | 0 | 0 | 0 | 0 | 0 |

Each automatic recipient a assigns base 12 to its own good 2a+3, base 11
to its own good 2a+2, and base 10 to every other good, including 0.

Choose an integer L>m. Replace every base value v at good g by
`L*v + g+1`, with these two offset exceptions:

- In A's row, interchange the offsets of goods 2 and 3.
- In B's row, interchange the offsets of goods 1 and 5.

All rows are positive and strict: distinct base tiers remain ordered because
L>m, and offsets within a tier are distinct. Every automatic row is fair
under every allocation, even if it gets good 0: its two smallest values sum
to more than 20L, whereas any foreign-pair minimum is below 12L+m<13L.

The target has

```
I:0   B:3,5   J:1   A:2,6   C:4,7   D:8,9   ...
```

The initial and final values, in the order A,B,I,J, are

```
initial: (30L+8, 20L+8, 30L+1, 10L+3)
target:  (31L+11, 30L+6, 30L+1, 20L+2).
```

In particular, the target does not itself force either exceptional recipient
to accept a loss. The temporary loss is a path obstruction.

### Both endpoints really are greedy

Here `C,D,...` means the automatic recipients in increasing index order.
Each line before `|` is a complete round; each line after it gives one final
pick to each double recipient.

```
source: A:3,I:0,B:1,J:2,C:7,D:9,... | C:6,D:8,...,A:4,B:5
target: I:0,J:1,B:3,A:2,C:7,D:9,... | A:6,D:8,...,B:5,C:4
```

A initially chooses its unique maximum 3. Once 3 and 0 are removed, B prefers
1 to 5 by the swapped offsets. J then chooses 2. Each automatic recipient
chooses its own base-12 anchor, then its base-11 tail in the source. Taking
those tails before A leaves 4 as A's best remaining good. In the target,
B removes 3 before A takes 2. A takes 6 before C's final turn; by that turn
every remaining good except 4 has been taken. All other picks have the same
tier justification. These statements cover any number of added recipients.
`greedy_witnesses` returns the full sequences, checked pick by pick.

### Every path must lose at least 8L-4

For any allocation x, define its deficit relative to the source by

```
d(x) = max(0, initial_A-u_A(x_A), initial_B-u_B(x_B),
             initial_I-u_I(x_I), initial_J-u_J(x_J)).
```

The cost of a path is its largest d(x). This uses the displayed units; it is
not a utility-scale-invariant measure. The existence of a temporary loss is
invariant under independent positive scaling of rows.

Put delta=8L-4 and suppose a path has d(x)<delta throughout. Consider its
first exchange changing any owner among goods 0,1,2,3, called the nucleus.
Before it, those goods remain with I,B,J,A respectively. B must also still
own 5: otherwise its other good is worth at most m, so its total is at most
10L+6+m, losing at least 10L+2-m > delta.

Now exhaust the first nucleus-changing exchange:

1. If 0 moves, I receives at most its best nonzero-index good, worth 20L+2.
   I loses at least 10L-1 > delta. This includes moves to other singletons
   and to any double recipient, so protecting 0 is not an assumption.
2. If 2 moves without receiving 0 or 1, J receives a good worth at most m.
   It loses at least 10L+3-m > delta. If it receives 1, the next case applies.
3. If 1 moves without receiving 0 or 3, B keeps 5 and gets a good worth at
   most m. Its total is at most 10L+2+m, losing 10L+6-m > delta. Good 5
   itself cannot be the exchanged partner because B already owns it.
4. Every remaining exchange moves 3 without either of the preceding losses.
   After losing 3, A cannot receive 0 or 2. Its two best possible goods
   outside {0,2,3} are 6 and 4, worth 12L+7 and 10L+5. Its total is at
   most 22L+12, losing at least 8L-4=delta.

This contradiction proves the lower bound for **every fixed-size exchange
path**, not just fair paths, with arbitrarily many preparatory exchanges
among automatic recipients. No finite graph exhaustion is needed.

### A fair path attains the bound

Keep all other automatic pairs and I:0 fixed:

| Step | Exchange | A | B | C | J |
| --- | --- | --- | --- | --- | --- |
| 0 | | 3,4 | 1,5 | 6,7 | 2 |
| 1 | 4,6 | 3,6 | 1,5 | 4,7 | 2 |
| 2 | 3,4 | 4,6 | 1,5 | 3,7 | 2 |
| 3 | 1,3 | 4,6 | 3,5 | 1,7 | 2 |
| 4 | 1,2 | 4,6 | 3,5 | 2,7 | 1 |
| 5 | 2,4 | 2,6 | 3,5 | 4,7 | 1 |

A's values are 30L+8,32L+10,22L+12,22L+12,22L+12,31L+11.
B never falls below its initial value; I is unchanged; J improves at step 4.
Thus the largest deficit is exactly delta.

To check EF1 directly, every foreign pair that A or B sees has a member
whose base value in that observer's row is zero, hence value at most m.
Their own totals always exceed m. Before J gets 1, at most one good in
any pair is strictly above J's value for 2; afterwards J owns its favorite
nonzero-index good. I keeps its global favorite. The remaining recipients
are globally automatic. These exhaust all comparisons, including pairs
outside the displayed core. Every row and every exchange is also checked
by the exact program.

This also has a proportional consequence. Every constrained initial total
is at most 30L+8, so some constrained recipient must temporarily lose at
least `(8L-4)/(30L+8)` of its initial utility. For fixed r and increasing L,
this lower bound approaches 4/15. No such fraction is claimed universally
for arbitrary profiles.

## A smaller family: all agents prefer the target

The companion `family` construction covers every r>=2. Its base rows on
goods 0,...,5 are

```
A:   0,1,2,2,1,0
B:   0,1,0,2,0,1
I,J: 3,2,1,0,0,0
```

Additional goods have base zero in these four rows. Each automatic row is
constant one. Use the same positive offsets except that B's offsets are
not interchanged. The initial core is the same as above; the target is
A:{2,4}, B:{3,5}, I:{0}, J:{1}. Every automatic pair is unchanged. A,B,J
strictly improve and I is unchanged, so this **is** a Pareto improvement
for all agents. The strict source is not claimed greedy.

Before any of goods 0,...,5 changes owner, additional goods can only
permute among automatic recipients. For each possible first departure,
`barrier_certificate` checks the deficit exactly. The eight exchanges
between differently owned goods 1,...,5 have respective deficits

```
(1,2):L-1   (1,3):L+1   (1,4):L-3   (2,3):L-1
(2,4):L-2   (2,5):L+3   (3,5):2L-3  (4,5):L+1.
```

Every exchange involving 0 loses I at least L-1. If an added good with
offset k is exchanged with a core good, the deficits for core goods
1,2,3,4,5 are respectively L+2-k,L+3-k,2L+3-k,L+5-k,L+6-k.
Consequently the minimum departure loss is L-3 at r=2 and L+2-m at r>=3.
These are positive because L>m. They hold over all exchange paths.

The program attains these lower bounds: three exchanges at r=2, and four
at r>=3 using the largest-offset extra good as a buffer. A separate two-swap
path, (1,3) then (1,2), loses only A, by L+1. The universal proportional
lower bound tends to one third; this last path's proportional loss tends
to one third too. The formulas do not assert a finite-L proportional optimum.

The component retaining all four initial utility floors consists exactly
of the assignments fixing goods 0,...,5, hence has `(2r-4)! / 2^(r-2)`
vertices. Every such assignment is fair and can be connected by exchanges
among automatic recipients. The strict target lies in another component
of this floor-restricted graph, but a displayed fair path joins them when
temporary losses are allowed. The claim concerns the component of the
source, not a classification of every floor-restricted component.

## Reproduce and challenge

Python 3.10+ and the standard library suffice:

```sh
python3 -S projects/fair-round-swaps/extra_buffer_attachment.py --greedy
python3 -S projects/fair-round-swaps/extra_buffer_attachment.py --audit
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_extra_buffer_attachment.py -v
```

At r=4,L=100, the greedy-endpoint command reports an exact optimal maximum
temporary loss of **796**, attained by the five-exchange path. Initial
A,B,I,J values are (3008,2008,3001,1003); final values are
(3111,3006,3001,2002). A falls to 2212 in the middle. All picks maximize.

The smaller family's complete fixed-0-owner audit has 22,680 states and
362,880 undirected edges. It has 5,320 fair states, all in one component;
36 states retain the four utility floors, with only six in the source's
floor-restricted component. The target meets the floors but is outside
that component. The exact optimal loss is 92; the four-step route attains
it, whereas the two-step B-sacrifice shortcut loses 99.

The tests independently enumerate complete graphs **allowing good 0 to
move** on six and eight goods, use literal deletion for EF1, and solve the
minimum-bottleneck path problem independently of the lower-bound proofs.
They agree with both families' bounds, including the greedy family's 796
at eight goods. Larger generated instances, exact rational perturbations,
the full ten-good fixed-owner graph and the actual command are also checked.
Finite audits test implementation; the first-departure and nucleus arguments
give the arbitrary-size results. The general EF1 connectivity problem remains
open, and this contribution has not received independent acceptance.
