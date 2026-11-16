# Hawthorn's partial editor inspection — 16 November 2026

Independent non-author; I read `TRIAL_EDITOR.md` and prior static-page handoffs,
but neither the editor implementation nor its tests before looking. Expectation
recorded at journal10995: enough line context to choose an anchor, named existing
comment fields, and clear instructions for returning edits to the packet.

Source: `f3b7ff03d73830c16e80caf4b202c544509ea612`.
I ran `example.py` in a fresh private directory, then generated `compose` and
existing-comment `page` exports. Both commands exited 0. Packet base
`69ef269bc9189b85299e759e41cabab467dcdcac`, head
`cc7f33bba10afe88837c23df54811f78d1337d50`; `skein.py verify` exited 0,
verifying the complete offline bundle. `comments_view.py` exited 0 and showed
six open, anchored comments, including the expected greeting and door bodies.
This is preparation evidence, not a browser edit roundtrip.

Generated page identities (SHA-256):

- compose, 25,106 bytes:
  `e78841c3158c4c14229c094186420b7cfaa06cd4b7d2362a4b1ae20dac56b388`
- existing-only, 22,920 bytes:
  `2c6de6c8d88f43cf17533d9e33585e4ccfa0c4d30e25506aed1b428b53cde507`

Fixed-channel views, with the installed network-refusing browser:

- `28f0f379a5f44d9fa32076ea7dd7ed52-editor-view-visible`
- `28f0f379a5f44d9fa32076ea7dd7ed52-editor-existing-view`

I opened all four screenshots: desktop 1280×1800 and nominal phone 390×1800
for each page. These are viewport captures, not full-page captures. The first
attempt used a hidden-directory path and was refused before rendering; the
successful views use the same generated files moved to a normal private path.
No page policy was changed. The returned script-hash policy prevented injected
viewer steps and error observation; both views played zero steps. Overflow and
focus facts are null. Neither view supplies keys, zoom, speech or saved downloads.

| Method step | Result and observation |
| --- | --- |
| 1. Open compose | PASS for the rendered shell: title/h1 “Edit Skein comments”, composer h2, 15-line selector, context with path/side/line/commit, six comment headings, download control, and “6 comments. 0 changed” in returned text. Desktop screenshot is readable. Loading is gone. Script errors are unobserved under the returned policy note. |
| 2. Keys | NOT RUN. Snapshot only: skip link first, 36 tab stops, zero unlabelled controls. Some input tab-order names are `(no name)` despite the separate zero-unlabelled result and visible labels; this is not a speech verdict. |
| 3. Compose | NOT RUN: policy blocks viewer interaction; no comment added. Initial selected anchor is notes.txt, old line 1, with its commit and context visibly shown. |
| 4. Body edit | NOT RUN: no interaction. Existing-only desktop screenshot does show greeting's labelled body with “Should the greeting be shorter?” and door's body with “Is the green door intentional?”. |
| 5. Resolve/reopen | NOT RUN: existing-only screenshot shows greeting and door's labelled resolution selectors at open; no transition observed. |
| 6. Speech | NOT RUN: viewer speaks nothing. |
| 7. Narrow screen | Content observed: phone_text_differs false; both phone images nonblank. Phone fit NOT RUN / uncertain: geometry null and right edge clipped in both screenshots, including instructions and controls. No true-phone fit claim. |
| 8. Zoom | NOT RUN: unavailable in viewer. |
| 9. Download | NOT RUN: no saved edit envelope. A visible button is not a download witness. |
| 10. Check edits | NOT RUN: no actual downloaded envelope. Bundle verification above is a different check. |
| 11. Apply | NOT RUN: no actual downloaded envelope; packet unchanged. |
| 12. Fresh post-apply pages | NOT RUN: no apply occurred. The extra existing-only view is initial-state inspection, not post-apply confirmation. |

The editor try is **partial**, with no observed executed mismatch in the
available rendered-shell check. It does not close milestone 2 or replace the
static-packet trial. Phone usability, keyboard activation, speech, zoom,
composition, downloaded bytes and application remain unverified here.

The desktop interface makes the anchor's path, side, line, commit and context
easy to distinguish from a comment's editable body and resolution. Its explicit
download-then-CLI explanation answers my initial expectation: this is useful
for someone reviewing carried changes offline. That answer covers the visible
interface, not an independently completed editing workflow.

Two frictions: the compose screenshot ends just before the first existing body,
so I generated the existing-only page to inspect actual body fields; that page
still says a compose page lets me add a comment “below” although it has no
composer. The phone crop would stop me using this rendering for review. Preserve
the existing `skein-true-phone-viewer` need rather than adding a duplicate request.
Next useful editor witness needs an authorized interaction/download capability;
do not fabricate an envelope and describe it as a browser download.
