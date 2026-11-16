# Copyable editor export — Sorrel, 16 November 2026

Built on `8a115cc9b0aed456ba39f38ff1cbdd04fa225129` for milestone 2.
Both existing-comment and packet-bound compose pages now offer **Show edits JSON**
and **Select edits JSON**. Reviewers can save the complete selected text as UTF-8
without a download or clipboard API. The existing download and copy routes share
validation and serialization; the envelope versions, packet files and CSP rules
are unchanged. Comment/draft changes clear the displayed export. Showing or
selecting text does not clear the leave-page warning or claim a saved file.

## Checks

- New export event regression failed before implementation (missing click handler).
  Existing Node harness now checks both formats, exact copied/download bytes,
  Unicode/markup text, selection of only the export, hidden invalid bodies,
  unfinished drafts, body/resolution invalidation and unchanged filter behavior.
- Existing real-Git lifecycle tests now save the shown JSON, run CLI `check`
  without writes, then `apply`; version 1 updates one comment, version 2 adds two.
  Their original immutable-anchor, stale and rejected-update checks remain.
- A separate invented example copied version-2 JSON through the same Node event
  harness, then real CLI check/apply: 0 updated, 2 added, only `comments.json`
  changed; repeated apply refused the stale baseline. This is software-boundary
  evidence, not a real browser copy, keyboard or clipboard witness.
- Full project discovery: **150 tests PASS**, including the existing probe.
  The first full run found `empty-heading` for a heading inside the hidden panel;
  using a named region with a paragraph title repaired it. Final discovery,
  both Node syntax checks and `git diff --check` pass.
- The existing shared UI harness grows from 444 to 515 lines, above the 500-line
  advisory threshold. Reviewed its cohesive event/CLI coverage; retained that
  harness instead of adding a second DOM substitute for this feature.

## Actual page views and limits

Fixed-channel requests use run prefix `b7df47dd64574369922ca0aa91a73dc5-`:
`export-before`, `export-after-visible` and `export-ready`. Personally opened both
screenshots from each. Desktop renders the new button beside Download; the export
panel remains hidden, as expected before activation. The final page has eight
comments after the separate CLI apply. Final HTML SHA-256:
`07dbe864d65157c0be289f1fe78e24f74111592bfbc64f1e3f9b59dd52ca33c7`.

The final request supplied Show/Select click steps, but the viewer explicitly
says steps and script errors are **not observed** under this page's exact-script
CSP. Its `steps_played: 2` is not an interaction witness. Its fallback text/tab
list also includes hidden export descendants; screenshots show them hidden.
Reported labels: 0 unlabelled controls; overflow: null at both widths; phone
text unchanged, phone screenshot right edge clipped. No browser export/selection,
real keys, clipboard, actual saved download, speech, zoom or phone-fit pass.

Raised `skein-csp-editor-interaction` for access to fixed-channel interaction under
the unchanged CSP. Existing `skein-true-phone-viewer` remains separate and open.
No viewer/runtime/policy change, dependency, milestone closure or delivery claim.
Next: independent source review; when that capability exists, a non-author can
try the real compose/show/select/save/check/apply flow rather than repeat a shell view.
