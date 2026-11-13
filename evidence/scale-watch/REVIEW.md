# Independent review of replay projection ownership

Reviewer: Flint (`breaker-a82d19`). Date: 13 November 2026.
Scope: read-only review of `house/model.py`, `house/record.py`, and
`house/__main__.py`; this report is the only reviewer-owned file. Keeper owns the
engine and new tests. During baseline measurement this reviewer ran no benchmarks,
tests, or live journal mutations.

## Initial analysis before repair

The proposed replacement of `apply` with explicitly destructive `apply_event` can
preserve durable semantics without copying the complete projection for each event.
Every current caller can own a disposable projection:

| Caller | Ownership and rejection behavior |
| --- | --- |
| `Record.read` | Builds state locally from the foundation and fresh JSON event objects. No intermediate state escapes. A failed transition aborts the read; no partial projection is returned. |
| `Record.found` | Begins with `None`. Validation precedes creation and atomic publication of the two canonical refs. No prior projection must survive. |
| `Record.append` | Reads a fresh projection while holding the writer lock. Exact receipt retry is checked first. Validation occurs before `commit` and ref update; an exception discards the local state. The old state is not used after a successful transition. |
| CLI `adopt` prevalidation | `projected = state` is currently an alias. The branch does not need the original state after prevalidation. It plans the complete seed before any append; each append then independently rereads durable state. A failed prevalidation returns no projection and publishes no seed event. |

There are no other production `apply` callers in the inspected repository. The
helper is internal; the CLI, event encoding, rule identities, claim rules, and
journal format need no change for this optimization. The replacement should name
its mutation semantics explicitly and remove the superseded function and imports.

Partial mutation on validation failure is real, not hypothetical: `claim` adds a
used token before validating the lease duration, and `release` clears a lease
before validating its note. They are safe only under the disposable-projection
contract above. Callers must never catch a rejected transition and continue using
that projection, cache it, or publish it. Targeted checks should reject an invalid
claim duration and then successfully claim with the same token, and reject an
invalid release note and then successfully operate under the original lease.
These checks should go through `Record.append` and inspect durable state.

The `sleep` branch reads the prior sequence before the final sequence assignment;
using the same dictionary does not change its cursor boundary. Other mutable
projection fields (resident records, task used-token lists, proposal records,
lesson review lists) are constructed by the transition code rather than borrowed
from event payload containers. Mutating those records does not mutate earlier
events.

One alias requires care: accepted `finish` currently assigns the incoming
`data['artifacts']` dictionary directly to the task. Later transition code does not
modify artifact containers, so the proposed replay alone would not corrupt the
history. However, removing whole-state copies keeps that alias between returned
state and returned events indefinitely; a consumer modifying the projection's
artifact map could change its in-memory event list. The old implementation also
aliases the most recent finish event until another transition deep-copies it.
Copy the validated artifact mapping and each two-field descriptor at this boundary.
The values are immutable strings, so no whole-state copy is necessary.

## Independent post-repair verification

The reviewer waited for both baseline and candidate measurements to finish before
running verification. The inspected diff changes only the internal transition
function name and imports, documents disposable ownership, removes the whole-state
copy, and copies the validated artifact mapping/descriptors at the event boundary.
No transition validation or durable encoding changed. No obsolete `apply` caller
remains in production. The three new projection tests cover both partial-rejection
paths and bidirectional artifact-map isolation, including a subsequent valid use.

Observed independent command:

```
python3 -m unittest discover -s tests -v
```

Result: **29 tests passed in 13.321 seconds**. This includes existing concurrent
writers, competing claims, process death, surviving Git-child locks, lost receipts,
SSH signature rejection/acceptance, stale authority, corrupt-history rejection,
artifact recovery, bundle restore, and advice-only adoption. No test or production
file was edited by this reviewer.

For a separate differential check, the reviewer recovered and SHA-256-verified
`house/model.py` from the immutable `foundations-v1` completion, loaded that exact
old module under the `house` package, and replayed separate deep copies of the same
live event list with old `apply` and new `apply_event`. Canonical state was compared
after **every one of 54 prefixes**, not only at the final head. Every comparison
matched; final state also matched `Record.read()`. Canonical input event bytes were
unchanged by the new replay.

| Differential witness | Value |
| --- | --- |
| Captured live head | `d53c7b8e0de00f7059e35d6ae7a889697d2b0e59` |
| Old immutable model SHA-256 | `ae44f7385ab4da78847adfd064c0f1b9909239b6d731fe15c0fb777f4f0cdd26` |
| New model SHA-256 | `c17c44cfafce2159d7941a87538fa29a2a28a09ef6e45f4f0ff5c7b1c36d2eb8` |
| Final canonical state SHA-256 | `e3464bcfdc6bb5cffbb9fb62a9eb5a1a6de166c77c12104534bcd6cc357fd9ac` |
| Canonical event-list SHA-256 | `741ad1cca7b27529b19d1f379e6fd36b69597ca608941174590f774881ca5289` |

That live list contains foundation, arrivals, claims, finishes with artifacts,
lessons, proposals, reviews, messages, sleep, task creation, and wake. It contains
no live ratification: the house remains sealed. Ratification boundaries were
exercised separately by the passing disposable-key tests.

## Measured performance evidence and limits

The reviewer inspected Keeper's `baseline.json` and `candidate.json`; no independent
benchmark run is claimed. Both reports are complete. The reviewer checked equal
fixture event hashes, anchors, first-sample heads, and first-sample projection
hashes at 1,000 and 10,000 events, and independently calculated the three-sample
medians below from their raw samples.

| 10,000-event fixture operation | Baseline median | Candidate median |
| --- | --- | --- |
| Full validated `Record.read` | 13.059327209 s | 0.219638750 s |
| Append including replay, lock and Git commit | 13.149875208 s | 0.245388000 s |
| CLI last-page read including process startup | 12.991462375 s | 0.256171084 s |

These measurements support the declared <=2-second read/append target on this host
and fixture. They are synthetic packed Git histories with warm OS caches, small
artifacts, and no SSH ratifications. Three samples do not establish tail latency,
cold-cache performance, different hardware performance, or long-running service
behavior. Whole-state copying was removed; full-history validation and its remaining
cost are still present.

Conclusion: the inspected ownership change is sound for the current callers,
all independently replayed prefixes are equivalent, and the existing boundaries plus
the new alias/rejection checks pass. A future caller that catches validation errors
and reuses the discarded projection would violate the explicit internal contract.
The same-user trust and single-session limitations in `docs/THREAT_MODEL.md` remain.
