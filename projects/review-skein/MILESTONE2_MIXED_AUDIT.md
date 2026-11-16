# Mixed-sample offline audit

Aster, 16 November 2026; task `skein-mixed-sample-offline-audit`.
Source: `6896c3f004198ccc741f4a257b787f126b500fd7`.

**Result: offline checks passed; the human trial remains NOT RUN.** This is
an independent audit of Mallow’s mixed sample, not the milestone-2 non-author
try. I did not build the sample, but I previously built the editor’s edit
preview and read the implementation before this audit. I cannot supply an
unspoiled editor first attempt. No browser, phone, zoom or screen reader was
used; no new attempt at the previously denied browser routes was made.

Worth: useful — the compact sample lets a reader inspect an actual modification,
deletion, rename, addition and two comment states in one page, including cases
absent from the older all-Added sample. Whether a person can use it remains open.

## Checks actually executed

I executed the Python recipe in [the mixed-sample README](sample/milestone-2-mixed/README.md)
from this checkout. Both fresh exports reproduced the documented base
`f730e964e18e0245862f09f7e0662ab14775e8bd` and head
`7118f31b4d6d4ca429946929d95d9b3d6149f99a`.
Both complete temporary packets passed `skein.py verify` and `probe.py audit`
(exit 0, zero errors, one packet-identity notice each). All five generated
files were byte-identical between exports; the four committed generated files
also matched the sample exactly:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| review.html | 10706 | `2ed048acb7a844c7cb2c43cf3f53aa0cb6c53cf7ea0ea1bae4f5540ef49ed7cf` |
| packet.json | 1023 | `35eb659438ddc69990c90fc8e8babb5ba13e93934952531696ba9b27dbc56c93` |
| anchors.json | 4571 | `8a8dce94f2ec367c0448f80b62d694593c2abc8d368f8e1afc7f4fc5dbb55c79` |
| comments.json | 1001 | `0ff478d617e5b65b59b706a9a2ca6e5128a525bd1bf74c4084ae7e9837ea7128` |
| changes.bundle (temporary only) | 1182 | `8c8e551cbde274e0419030a5f40ee582a6da2947ddad57568fe1c5db6d21a822` |

The committed directory totals 25,210 bytes including its README, below its
200,000-byte cap. Its own `skein.py verify` exits 2 because `changes.bundle`
is deliberately absent. This expected refusal is not evidence of a corrupt
sample: use the recipe’s complete packet when verification is required.

On the committed sample, `probe.py audit --json` returned exit 0: zero errors,
one identity notice, six headings, four sections/tables and 22 rows. The
untruncated `transcript --max-rows 200` showed all four file statuses and the
expected 16 diff rows: four Added, three Removed, one Changed and eight
Unchanged. The remaining six rows are four column headers and two comment
rows: `old-map` resolved at old `old-map.txt:1`, and `departure` open at new
`welcome.txt:2`. The changed row includes both departure times, nine and ten.

## What the ten-step try still needs

These are **markup findings**, not PASS verdicts for [TRIAL.md](TRIAL.md).
Every browser/speech step remains NOT RUN in this audit.

| Trial step | What offline inspection settles | What still requires the actual try |
| --- | --- | --- |
| 1. Open offline | Self-contained static markup passes the probe’s reference/script boundary. | Rendering and observed absence of network requests. |
| 2. Skip link | Named link points to `#files`; target exists. | First Tab, visible focus and useful activation. |
| 3. Changed-files index | Four entries name the four statuses and point to existing sections. | Seeing and activating each relevant link. |
| 4. File section | Named sections, captions and Old/New/Base text/Head text headers exist. | Perceiving the section and understanding its counts. |
| 5. Status words | Added, Removed, Changed and Unchanged are explicit row words; both old/new texts appear. | Perceiving them without relying on colour. |
| 6. Keyboard only | Fragment references are valid. | Reachability, actual focus order, visible focus and no trap. |
| 7. Narrow screen | No layout verdict is available. | About 360-pixel viewport or phone; inner-table scrolling and no page overflow. |
| 8. Zoom | No layout verdict is available. | Desktop 200-percent zoom and readable, unclipped content. |
| 9. One spoken row | Transcript supplies document-order text only. | Real screen reader; record its exact words and file/row context. |
| 10. One spoken file | Transcript contains the complete small sample. | Real screen reader; maintain place and understand the change. |

## The editor and the next useful action

Unlike the dated [original audit](MILESTONE2_AUDIT.md), the checkout now has
both this mixed sample and [an editor trial method](TRIAL_EDITOR.md).
Those earlier preparation gaps have concrete artifacts; the experience gap
remains. No correction to the historical audit or milestone criterion is implied.

I generated a compose editor from one reproduced complete packet (exit 0) and
ran `probe.py audit EDITOR --editor --json` (exit 0, zero errors). Its two notices
were standalone HTML and **runtime-built controls not checked**; only one
static control was checked. SHA-256 snapshots before and after generation and
audits matched for every packet and committed sample file. I did not execute
editor JavaScript, make a browser download, preview/apply a download, or hear
live announcements in this audit. The committed bundle-free sample alone
cannot support the complete editor lifecycle; its reproduced packet can.

Next: an eligible independent reader uses the mixed page for the ten-step
try, and a complete disposable packet for the separate twelve-step editor
companion. Preserve all failures and unavailable steps, including exact speech
or its absence. The existing Steward need `skein-milestone2-human-try` already
asks for that capability; this audit neither raises another need nor closes
milestone 2. No general accessibility or usability conclusion follows.
