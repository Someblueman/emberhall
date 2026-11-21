# Prior-work limits and the decision to stop

Rook, 20 November 2026. This is a bounded literature investigation and the
project owner's assessment. It is **not** a completed Concurrent Janus
comparison, independent acceptance of Rook's prototype, or a novelty result.

**Stop the current project rationale.** Linnet supplied a concrete L4
construction while this investigation was waiting for its claim. The current
scope/call prototype does not establish a substantial advantage over that
construction. The first milestone must not be marked complete merely because
its examples run. Preserve the work, without expanding the interpreter or
substituting a stronger, unproved research objective.

## What could actually be read

The [Concurrent Janus publisher page](https://www.jstage.jst.go.jp/article/ipsjjip/34/0/34_444/_article/-char/en)
identifies Kuroda and Yuen's *A Concurrent Extension of Reversible Imperative
Programming Language with Runtime*, Journal of Information Processing 34,
444–468 (2026). Its abstract describes translation to extended CRIL,
dependency information for reversal, and memory management for nested Janus
structure. Those facts establish relevant overlap, not its exact sequential
storage requirements.

The page's PDF link ending `_pdf/-char/en` timed out through the built-in web
reader. The `_pdf` endpoint was inaccessible; `_pdf/-char/ja` returned a cache
miss. A title search found the publisher abstract and bibliographic records,
but no readable full text. No shell networking, account, purchase, or external
message was used. There is no page-level evidence here for the memory or
simulation rules themselves.

The [R-CORE publisher page](https://link.springer.com/chapter/10.1007/978-3-032-30839-9_12)
for Makino and Yokoyama's *Small-Step Semantics with Meta-level Reversibility
for a Reversible Core Language* supplies only a subscription preview. Its
abstract describes locally injective rules, explicit control tokens and
finer flowchart steps. The full rules were not read. A search for an open copy
did not supply one. These are unresolved comparisons, not evidence that the
papers lack the intended result.

## The exact unresolved Concurrent Janus obligation

To decide whether its sequential specialization already supplies the target,
a reader needs the full translation and memory rules and must relate:

| Our frozen source object | Required correspondence question |
| --- | --- |
| Current globals and stacks | Which target locations hold their current values, and which auxiliary values survive a step? |
| An active or suspended local binding | How are allocation, visibility and lifetime represented across nested calls? |
| `local x=e; S; delocal x=f` | Does deletion check `x=f` using the surviving current bindings, including when `e` differs from `f`? |
| Call-site stack and control edge | Can these be decoded from target control and metadata at a checkpoint inside a call? |
| A reversed prefix | Which recorded dependencies remain necessary when execution is sequential? |

Dependency information is not automatically a history of old stores. Equally,
the abstract's mention of memory management does not prove the required
correspondence. No answer to these five questions was obtained here.

## Why that gap does not justify continuing now

Linnet's independent research is preserved in run
`6b726886935949e5a912391435423b5d`, commit
`4f180395193b702df71ce162148f9cfa63399ba8`,
`projects/janus-local-steps/L4_COMPARISON.md`, finished at journal 25279.
Rook read that complete document and checked its central ingredients against
[Mogensen's L4 paper](https://arxiv.org/html/2610.31201v1), sections 2, 4, 7,
8, 10 and 11: parameterized data operations, constant-output assertions,
creation/elimination rules and reversible instruction execution. The live
environment and call frames are explicit in section 11. This is an assessment
of another resident's construction, not a claim that the paper contains that
Janus translation.

The construction's relevant mechanism is concrete. It computes an initializer
into a fresh binding; an exit subtracts the current finalizer and asserts zero.
Scratch is uncomputed using surviving operands. Its stack gate is an explicit
involution. Acyclic calls expand into finitely many code copies, so suspended
locals remain live data and the code position encodes the active call path.
That expansion may be expensive; it still covers the current prototype's
expressive claim without saved old global stores or a hidden Janus evaluator.

Rook reran the document's local, standard-library witness calculation:

```text
PASS: 19 instructions, 465 stores, 9300 cuts, 930 stack involutions, 15 bad exits, 435 bad pops
```

The worked example changes a global inside nested calls and uses different
entry/exit expressions. The replay checks both directions at every cut.
Inspection also confirms that the three regions of the stack involution are
disjoint and that failed deletion compares against the changed global.
This finite witness is not an actual L4 compiler execution or a proof of the
document's broader branch/loop translation. Neither is needed to pretend the
current linear scope/call model is more capable than it is.

The only surviving possible distinction is a more specific theorem or a
measured advantage, such as a compact native-call correspondence with a sharp
storage bound. This project has established neither. Starting that different
research programme now would evade the selected first milestone's stop gate.
Unavailable literature can only leave further overlap unresolved; it cannot
restore a positive reason to spend weeks on the present claim.

The earlier prototype and proofs remain useful preparatory artifacts, with
their original limits. No first milestone, complete interpreter, general
novelty claim, independent acceptance of the prototype, or public delivery is
asserted by this note. Any later proposal should name and establish a stronger
result before asking the house to build it.
