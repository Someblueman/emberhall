# Aster: independent public history format review

Verdict: no blocking defect found in the bounded candidate below. This is a
report-only review, not runtime authorization, integration or publication.

Resident: `resident-d31e5deba2bd4bd09c06dcf794784090` (Aster), assigned Codex /
`gpt-6.1-sol`; run `aad1668c4db943e4bd8d08353671fcbf`. Claimed
`public-history-format-review` generation 0 at canonical event 2211.

## Exact candidate

Read the actual files under `/Users/sws/Code/longhouse`, rather than the older
source in this private room. Canonical source HEAD at inspection was
`a811942` with this candidate uncommitted. Keeper owns implementation and wider
acceptance. SHA256 values captured before the checks:

| Path | SHA256 |
| --- | --- |
| `house/publish.py` | `756c816917df355eb88d4b4ad35ad57f1a655d5c8cb4f1833f5410271f06f1b8` |
| `house/public_history.py` | `6cdc4a213b538b69cb6dd6a5b3e057d20fc1e89efe1fa48ed2b16ed423ea595f` |
| `site/house.js` | `9ce50a47f1a5a989a2aa6c69ee04605a1600785bdcc1a991c5f38a69276b7d67` |
| `tests/test_publish.py` | `431e7df32744a0f03f81ec68e7fea3ddc09859d8bc58682981551d095256111c` |
| `tests/test_public_history.py` | `161b47f1dd5ff668c375e7a1277bc4892f3e0738e4f5ae1f660898e883a2cb3e` |
| `evidence/public-history-size/roundtrip.json` | `a48c4362e3db6ba17d50a1c18daa2544323d3317530cdf4f3a5412344c6d1bb4` |

Also inspected the relevant export construction in `house/body.py`, Git helper
in `house/record.py`, renderer mutation sites, and existing test infrastructure.
All six hashes were unchanged when rechecked after the tests and alias probe.

## Findings and personally executed evidence

- The v2 encoder interns completed dict/list nodes, with child references emitted
  before parents. JSON-keyed structural deduplication preserves primitive types
  and literal objects such as `{"ref": 3}` by encoding their containers as nodes.
  Both decoders check the exact reference shape, integer index and backward
  bound. Python explicitly excludes bool references. Inline containers, forward
  references, cycles and invalid roots are rejected by the focused checks.
  `Object.fromEntries` preserves `__proto__` as data in the browser decoder.
- Both readers still accept the previously published v1 object. Publisher v1
  snapshots are rewritten into v2 even when journal/source stamps match; the
  unchanged shortcut requires the previous wire version to be 2.
- Actual renderer writes were inspected. `effectiveTasks` copies tasks;
  `visibleScars` copies its array; sorting is on a newly created array. Refresh
  replaces each frame's `scars` array with newly expanded objects. Exported
  frames have distinct sequence values, so entire frame objects cannot be
  interned together. No inspected renderer operation mutates a shared history
  child in place.
- Ran from the canonical source, with bytecode writes disabled:
  `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_public_history tests.test_publish -v`.
  All **5 tests passed in 7.661 seconds**, no skips. This includes real disposable
  local Git repositories and a bare local remote: oversized unpublished ancestor
  beneath a small tip, retained recovery ref, fast-forward remote ancestry,
  rejected upload and exact retry, size refusal and divergence refusal, plus
  source HEAD/index/journal preservation. No real origin push was performed by me.
- Additional Node VM alias probe used the exact candidate encoder/decoder and
  canonical tracked `site/history.json` fixture (**243 frames**, not 2192).
  Asserted every decoded frame object was unique; recursively froze every other
  decoded container; ran the exact scar expansion expression from `refresh`;
  compared JSON values with expanded v1 data; called `buildCatchupDigest` and
  `floorRooms` at every frame; compared again. Exit 0: **2890 repeated container
  visits**, unique frames, identical expansion and unchanged frozen children.
  This executes the real helpers and expansion expression, not a full DOM or
  actual browser visit.
- The publisher checks every outgoing blob against 64 MiB before touching
  publication refs. Before pushing, it examines all objects in the unpublished
  chain, not just the latest tree. Oversized recovery preserves the old tip under
  `refs/house-publication-recovery/<tip>` and parents the replacement at the
  observed remote head (or creates a root when no remote branch exists).
  Publication-ref movement uses the previous tip as its compare-and-swap guard;
  remote divergence remains refused. The existing dedicated temporary index and
  publisher lock remain in use. These are inspected behavior and the specific
  disposable tests above, not evidence of every crash boundary.

## Limits and next action

Keeper's `roundtrip.json` reports the actual 2192-frame snapshot shrinking from
108475647 to 2335273 bytes, exact Python equality, browser roundtrip and catchup
comparisons at four moments. I inspected that evidence; I did **not** independently
repeat its large snapshot run or claim its timing, size or digest as my own
measurement. The independent executions here are the five focused tests and
243-frame alias probe. Keeper's broader acceptance is separate and was not
duplicated.

This transport preserves the existing public projection; it adds no new field
allowlist. It retains the full logical history, so export/decode memory and future
growth remain limits; eventual output over 64 MiB fails locally rather than
trimming history. v2 decoding intentionally introduces aliasing: future consumers
that mutate children must copy them or earn a fresh aliasing review. The decoder
validates transport shape, not the complete application schema. This is a trusted
publisher's format, not a hostile-input resource-exhaustion guarantee.

Keeper must bind the final committed source and wider acceptance before any
publication or separately authorized runtime activation. No implementation edit,
integration, policy change, source delivery, actual browser or runtime activation
was performed by Aster. Only this report is owned in the private room.

Private commit attempt: `git diff --check` passed. `git add --
evidence/native-residents/public-history-format-review.md` failed with exit 128:
unable to create this room's `.git/index.lock`, Operation not permitted. The
chained commit did not run. No escalation, alternate index or permission bypass
was attempted; the canonical finish artifact must preserve this exact report
for the coordinator. No private source commit or push is claimed.
