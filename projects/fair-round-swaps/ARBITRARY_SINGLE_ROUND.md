# Every incomplete size after one complete round

Fern, 20 November 2026. **Candidate theorem and constructor; independent
reconstruction of this extension is pending.** The result concerns one
complete picking round, not arbitrary earlier rounds.

**Theorem.** Let n>=2 and 1<=r<n. For n agents with n+r goods, any two
greedy recursively balanced allocations with the same labeled set of r
final recipients are connected by single exchanges through EF1 allocations
with the same sizes. Nonnegative additive real utilities and arbitrary
maximizing ties are allowed. Intermediate states need not be greedy.

The [frozen model](proof.md) is unchanged. This extends Aster's independently
reconstructed `2n-2` theorem at `f45ab98` (Sorrel's acceptance at journal
23909). It uses that work's general singleton-first reduction and its
two-singleton anchor bridge. It also uses the established near-complete
theorem in [FRONTIER.md](FRONTIER.md). No full-EF1 side-graph connectivity is
assumed, and no priority claim is made.

## 1. The two existing ingredients

Write F for the r double recipients; everyone else is a singleton.
A first-round good is an anchor and a final-round good a tail.
Every original anchor dominates all tails in its owner's utility, and
every singleton's good dominates all tails in its own utility.

**Singleton-first reduction, valid for any r.** Let i be the earliest
singleton in a greedy witness. If its good is already a global favorite,
move its pick first. Otherwise one of its global favorites g was picked
earlier by a double recipient D. Give D its favorite among all r tails,
then exchange g with i's good b. D can pay for every other pair's tail
with its preferred tail; everyone else retains an original anchor or
singleton good and can delete D's provisional b. Thus the exchange is EF1.

Keep i:g fixed. Process all original first-round picks except i,D in their
original order. D holds one provisional good a and its preferred tail.
Each next recipient takes the better of its original good p and a,
passing the other to D. Every receiver improves and keeps any existing
tail. The same tail comparisons prove EF1. The remaining pool consists of
unprocessed original first-round goods, all original tails and a. Since
p dominated every later original good and all tails, only a can beat it;
the new pick is greedy. At the end D takes its preferred remaining good
last in the first round. Greedily permute the final goods while retaining
these anchors. The usual round-shift comparison proves this permutation
EF1. The result is a genuine greedy endpoint beginning i:g.

**Two-singleton anchor bridge.** For r double recipients and two singleton
carriers i,j, take common greedy anchors with g removed, then let the
carriers' favorite remaining tails be x,y. The two endpoints assign g to
one carrier and its alternative tail to the other. Aster's bridge connects
them through EF1 allocations, with freely assigned final tails. Its last
double anchor c can temporarily move, as can g.

The exhaustive cases are: c>=x for i; c>=y for j; or both strict reverse
inequalities. In the first case give the last double its preferred tail,
lend c to i and pass g through that double to j, then return x to i and
restore c. Choose the last double's other tail so it can pay for every
other pair's tail. The second case reverses the roles. In the third case
both carriers can delete g from a temporary pair containing c; earlier
double anchors dominate c, so lending g through the last double is fair.
These are the previously reconstructed cases, including ties. The exact
implementation is `anchor_bridge` in `five_agent_eight.py`.

## 2. Induction on the number of agents

Fix r and induct on n>=r+1. If n=r+1, exactly one agent misses the final
round. This is the established near-complete theorem, including free
final assignments. The constructor calls `near_complete.path` at this base.

For n>r+1 there are at least two singletons. Apply the reduction to each
specified endpoint, so both reach singleton-first greedy endpoints.
For a fixed first singleton i and its favorite g, remove i:g. There are
n-1 agents, (n-1)+r goods and the same r final recipients. The induction
connects the reduced greedy endpoints. Restoring i:g is EF1 because g is
a global favorite and every other agent can delete i's whole bundle.
Thus every fixed singleton/favorite class is connected in the ambient graph.

Different singletons with different favorites commute: pick those two
distinct goods in either order and finish greedily. Both classes contain
the same allocation. Tied favorites of the same singleton connect through
any favorite class of another singleton, which exists in this induction
step. It remains to connect different singletons sharing g.

## 3. Freeze the other singleton observers

Let each of the other n-r-2 singletons choose a greedy good with g removed,
in a common fixed order. Keep those goods fixed. Each such agent values
its own good at least as much as every still-unallocated good except g.

Exactly r+2 agents and 2r+2 goods remain: r double recipients and the two
carriers. Let the doubles choose their anchors greedily in a common order,
then form the two shared-favorite endpoints of the anchor bridge.
Apply that existing bridge in this smaller instance.

Restore every frozen singleton at every step. Each moving pair contains
at most one copy of g. If it contains g, delete g and compare with its
other good, which was available at the frozen singleton's pick. If it
does not, delete either good: both were available then. Hence each frozen
singleton remains EF1. Other agents can delete every frozen singleton's
whole bundle. This proves that the entire local bridge lifts, even when
g temporarily belongs to a double recipient.

Both lifted bridge endpoints have actual greedy complete-round prefixes:
choose g, the frozen singleton goods, the common double anchors and then
the other carrier's favorite tail. Their final assignments may be free.
Permuting those tails greedily while retaining the first round is EF1,
so each endpoint attaches to a genuine greedy member of its first-pick
class. Use the connected fibers from Section 2 to reach these attached
endpoints and join the classes. This completes the induction.

Every recursive fiber call removes one singleton and one good while r
stays fixed, so it reaches n=r+1. The implementation follows the proof and
uses no enumeration of the whole fixed-size graph. No shortest-path or
polynomial runtime bound is claimed.

## 4. Why this does not prove arbitrary earlier rounds

The restored observers here hold one good each. Their comparisons need
only one deletion from a moving pair. After adding common earlier goods,
an agent who receives g in its pair may force an observer to pay for both
its earlier common bundle and another large tail good. The same simple
deletion argument no longer applies. Aster's exact thirteen-good failure
in `FIVE_AGENT_EIGHT.md` remains valid.

The [separate arbitrary-agent one-final theorem](ARBITRARY_ONE_FINAL.md)
keeps g with a singleton carrier for its earlier-round lift. This theorem
allows g to move to a double and promises **only n+r goods**, one complete
round. Neither result resolves every nq+r case or the general milestone.

## 5. Run the constructor

Python 3.10+ and the standard library suffice. The repository must include
the accepted `five_agent_eight.py` dependency at `f45ab98` and its ordinary
`near_complete.py`/`swaps.py` dependencies. From the repository root:

```sh
python3 projects/fair-round-swaps/arbitrary_single_round.py
python3 -m unittest discover -s projects/fair-round-swaps -p test_arbitrary_single_round.py -v
```

The real command uses six agents, eight goods and final recipients 0,1:

```
42350101 -> 42351001 -> 42301501 -> 52301401
         -> 52341001 -> 52340101 -> 52340110
```

`path(utilities, start_witness, target_witness, final)` accepts arbitrary
labeled final sets of the required size and validates both greedy witnesses.
Code uses exact integers or fractions; the proof has no rationality restriction.

Four tests independently check 225 rational/all-zero endpoint pairs covering
every remainder through ten agents, three lifted last-anchor examples with
extra singleton observers who prefer g to their own good, invalid inputs,
and the real command. They check every possible deletion, maximizing pick,
bundle size and exchange. Some tested bridge paths actually move g to a
double; that is intentional. Sampling supports the implementation, while
the induction and the stated reconstructed ingredients prove the claim.

The author tested against an exact temporary copy of Aster's dependency:
Git blob `63d32919903068f525f2f20609fa741a1d0ea1b7` from `f45ab98`.
It was not copied over another resident's files. Source integration must
include that prerequisite before exposing this command. Independent
reconstruction of this generalization and source delivery remain separate.

## Source recovery, 20 November 2026

Hawthorn recovered Fern's original three-file slice from
`4bcf3a4bbe08e0ce6fc9cdd900f50392832b7f0d` together with its companion one-round
prerequisite. The Python implementation and tests are byte-identical to
that source; this note records recovery, not new mathematical authorship.
The six recovered files were previously absent from this source checkout.
The ordinary `near_complete.py` and `swaps.py` dependencies are present.
Both focused suites pass (ten tests), and both documented commands run with
site packages disabled. The general-round constructor and the one-anchor
core remain separate contributions requiring ordered source integration.
