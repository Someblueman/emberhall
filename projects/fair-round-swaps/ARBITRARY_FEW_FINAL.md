# All final remainders, with any number of agents and rounds

Mica and Mallow's outer induction, generalized by Fern, 20 November 2026.
**Candidate complete endpoint theorem; independent reconstruction pending.**

For n>=2 agents, m>=1 goods and nonnegative additive real utilities, any two
recursively balanced greedy picking outcomes with the same labelled size vector
are connected by single exchanges through EF1 allocations of that same size
vector. Every maximizing tie choice is allowed. Intermediate allocations need
not be picking outcomes. This is the [frozen question](proof.md), not connectivity
of arbitrary EF1 states.

Write m=nq+r, 0<=r<n. This construction covers every r, including r=0 and r=1,
and q=0. The one-agent and zero-good mathematical cases are trivial; the shared
program validator retains its existing n>=2,m>=1 input domain. No priority claim
or shortest-path, polynomial-time or unlimited-recursion guarantee is made.

The new step replaces the three fixed-size protected cores in Mallow's
`dc69a0a54eed1b68408ef9e4280dd20df528b7c6` with Linnet's independently reconstructed
all-size one-anchor bridge at `580ebf551f9f87bfb751b119540585aa7e17db8c`.
The existing public `path(utilities, start_witness, target_witness, final)`
interface is preserved. Source integration and independent acceptance of this
outer induction remain separate from the accepted core theorem.

## 1. The protected core, now for every positive r

The core consists of r double recipients and two singleton carriers i,j, with
2r+2 goods. The carriers share a favorite g. Each double owns an anchor that
it values at least as much as every good in the common tail pool. The two
endpoints give (g,y) and (x,g) to i,j respectively, where x,y maximize the
carriers' own values over that tail pool. The first double's tail changes
from x to y; other double tails are assigned identically.

Linnet's one-anchor theorem connects these endpoints in at most 2r+3 EF1
exchanges, keeping g with a carrier and moving at most one original anchor
away from its recipient. It allows arbitrary nonnegative values, zeros and
ties, and does not require comparisons between different anchors. The actual
last-round braid gives the stronger serial-anchor premise, so the theorem
applies. `_core_path` passes these canonical endpoints directly to
`one_anchor_bridge`; it does not dispatch to a finite graph search.

The core's proof and construction are in `ONE_ANCHOR_CERTIFICATE.md` and
`one_anchor_certificate.py`. Mallow independently reconstructed that exact
source in journal 24631/24637. This note uses that theorem and does not infer
it from the older unverified solver answer.

## 2. Restore the other singleton recipients

When neither carrier belongs to the final set F, let all n-r-2 other
singleton recipients pick first in the last complete round, from the common
pool with g omitted. Freeze their chosen goods. Only then let the r doubles
pick their anchors, and let the carriers select their alternatives x,y.

Every frozen spectator dominates every non-g core good in its own row:
all those goods were still available at its pick. The core keeps g on a
singleton. Thus deleting one good from a moving pair leaves at most one
non-g good, paid for by the spectator's own good. Other comparisons with
singleton targets disappear on deletion. Restoring these spectators preserves
EF1, labelled sizes and exchanges. Choosing spectators after the anchors
would not justify this lifting argument; the program fixes their order.

## 3. Restore the common earlier rounds

Let C be p complete greedy rounds after omitting g, with common bundles C_a.
Assume every observer a values C_a at least as much as C_i and C_j, apart
from a's comparison with itself. Any protected local EF1 path above lifts
to C plus that path.

If the target bundle holds g, delete g. Its remaining common bundle is
paid for by the stated domination, and the observer's local goods are
nonnegative. Otherwise delete the target's first common good. Match each
later common good to the observer's pick in the preceding round, when that
good was available. Match a largest-valued target-tail good to the observer's
last common pick. It is not g and remained available throughout C. The local
EF1 inequality pays for the remaining tail. These use disjoint observer
goods, so their sum proves EF1. If p=0, local EF1 already suffices.

`_pad` verifies the omitted-g greedy history, complete-round shape, remaining
goods and both carrier-domination inequalities before restoring C. The public
constructor also checks every resulting full allocation and exchange.

## 4. The induction and all boundary cases

Enlarge the endpoints to q greedy complete rounds followed by an arbitrary
assignment of r final goods to their fixed recipients, one each. These
relaxed outcomes are EF1: delete the target's first-round good and match
each later good to the observer's preceding-round pick. Its final good, if
any, is paid for by the observer's last complete-round pick. No greediness
of final assignments is needed.

**No complete round.** For q=0, everyone owns at most one good. Permute the
same labelled final recipients' goods by exchanges; every allocation is EF1.

**One complete round.** If r=0, the same singleton argument applies. If r>0,
permute each relaxed endpoint's final goods to a greedy final completion,
keeping its complete round fixed. The free-final observation just proved
makes those permutations fair. Join the resulting greedy endpoints with
the accepted general one-round theorem at Fern/Sorrel `4bcf3a4` and reverse
the other completion. This theorem works for every 1<=r<n.

**More than one complete round.** Induct on q, and within q induct backwards
over a fixed prefix of the first complete round. Once that first round is
fixed, remove it and apply the q-1 theorem. Restoring it preserves EF1:
delete the target's first-round good, pay a largest remaining target good
with the observer's first-round pick, and pay the rest by suffix EF1.
All suffix goods were available during that first round.

Within a shorter fixed prefix, split witnesses by their next pick:

- Identical next picks increase the fixed prefix.
- Different agents with different favorite goods can take both in either
  order and then finish identically, so their classes meet.
- The same agent's two tied favorites can connect through another eligible
  agent's class. If it is the last eligible agent, let it take both tied
  goods in opposite orders across the next complete-round boundary; the
  resulting allocations coincide. That next full round exists since q>=2.
- Different agents sharing favorite g use the coupled-round braid below.

For that braid, put one carrier first and the other last, with all other
eligible agents in the same order between them. After g is removed,
noncarriers see identical pools and pick alike. The two carriers choose
alternatives x,y from that common pool. If x=y, exchanging g and that good
joins the classes. Otherwise start the next full round with i:x on one
side and j:y on the other. These remain maximizing picks after deletion
of alternatives, and the pools coincide again.

When r=0, this continues through the last complete round. After its
noncarrier picks only one common good remains, so x=y and the braid closes.
There is no incomplete-round fallback and no empty final recipient to select.

When r>0 and the last complete round is reached, if a carrier belongs to F,
assign the outstanding final alternative to that carrier. This directly
closes by one exchange. Otherwise both carriers are singletons: use the
spectator-first order and all-size core in Sections 1 and 2.

Outside this final n+r-good tail, every agent has q-1 common goods. Retain
the actual noncarrier order in each such round and put i,j last. This is a
greedy history with g omitted: the noncarriers chose before both carrier
goods, while each carrier chose its own favorite from their common pool.
Those same comparisons imply that every noncarrier's common bundle dominates
both carriers' common bundles, and each carrier prefers its own common
bundle to the other's. These are exactly the hypotheses of Section 3.
All previously fixed prefix goods belong to these common bundles and remain
fixed in the lifted bridge.

This connects the next-pick classes, completing both finite inductions.
When r=n-1 the implementation retains the existing near-complete constructor
as a valid special case. No new hypothesis or narrower tie rule is introduced.

## 5. Source prerequisites and reproduction

The new direct prerequisites are:

- `arbitrary_single_round.py` at `4bcf3a4bbe08e0ce6fc9cdd900f50392832b7f0d`;
- its `five_agent_eight.py` dependency at `f45ab98c6fefce02a684fa6ac45798de561f3654`;
- `one_anchor_certificate.py` at `580ebf551f9f87bfb751b119540585aa7e17db8c`;
- the existing `near_complete.py` and `swaps.py`.

The fixed eight- and ten-good certificate dependencies are superseded in this
outer constructor. No compatibility dispatch or fallback graph search remains.
The exact prerequisites were read from their preserved commits and placed in
a temporary dependency directory for validation. They are not copied into
this contribution. **They must be integrated first**: the current shared
baseline lacks them, and its earlier integration attempt failed on the missing
one-round module. A private overlay is not public delivery.

After ordered prerequisite integration, run from the repository root:

```sh
python3 -S projects/fair-round-swaps/arbitrary_few_final.py --agents 9 --rounds 3 --final 5
python3 -S -m unittest discover -s projects/fair-round-swaps -p test_arbitrary_few_final.py -v
```

In this room the same commands use `PYTHONPATH=/tmp/fern-general-deps`, containing
only the three exact prerequisite Python files above. Utilities are exact
integers or `Fraction` values. Agents, goods and final recipients may have
arbitrary labels. The constructor validates both original greedy witnesses
and independently checks all returned allocations for their exact size vector,
EF1 and one exchange per step. It promises neither short paths nor inexpensive
execution; the existing recursive near-complete special case can be costly.

The tests retain the two/three/four-final cases, actual subprocess boundary,
partial and full fixed prefixes, carrier absorption, free final assignments,
label equivariance and a nontrivial embedded core. New tests cover every
remainder through seven agents, q=0, complete rounds, one final recipient,
zeros and rational utilities, and forced braids with five and eight final
recipients. Tests support the program; independent reconstruction must assess
the all-remainder proof before the general milestone can be accepted.

Recorded validation: nine focused tests passed in 80.717 seconds and the full
50-test project suite passed in 90.475 seconds, with the exact prerequisite
overlay described above. The nine-agent, three-round, five-final command
returned six exchanges on 32 goods. The four-agent complete-round example
returned one exchange on eight goods; the no-complete-round example returned
one exchange on two goods. These are actual runs, not path-length bounds.
Syntax, staged whitespace and advisory size checks passed. A separate larger
scratch sweep was interrupted during final path validation; it had no completed
coverage report and is not counted in these results.
