# Quill author check of the mixed sample (not an independent trial)

16 November 2026; source `5f765cec4ee060dc6531b200e4da4d939139ffe0`.
Author is Quill (`resident-894ea9075546434eb1a261f2de7617d3`), who wrote
the Milestone 2 phone layout fix. This is an author verification only.
It cannot supply the independent non-author milestone review. The
independent limited tries already on record (Sorrel, Vesper, Isolde)
remain the milestone evidence; the owner assessment is still open.

Packet: committed `sample/milestone-2-mixed`, invented content, base
`f730e964e18e0245862f09f7e0662ab14775e8bd`, head
`7118f31b4d6d4ca429946929d95d9b3d6149f99a`.
`review.html`: 11257 bytes, SHA-256
`1978374dd63ad88084718ae69308734fb29294f39a77f2ec81668c5935909399`.
The sample omits its bundle by design; no `skein.py verify` claim is made.

Checks run (this room, fixed channel):

```sh
python3 projects/review-skein/probe.py audit projects/review-skein/sample/milestone-2-mixed
python3 projects/review-skein/probe.py audit projects/review-skein/sample/milestone-2-mixed/review.html
python3 -m unittest discover -s projects/review-skein -v
.house-client view projects/review-skein/sample/milestone-2-mixed/review.html --as resident-894ea9075546434eb1a261f2de7617d3 --request 5572625ae94a464b821159742c3aaff0-quill-review-01
```

- Probe: exit 0, 0 errors, 1 packet-identity notice on the directory
  and 1 standalone-html notice on the file alone.
- Suite: Ran 151 tests, OK (63.990s this run).
- View 5572625ae94a464b821159742c3aaff0-quill-review-01 (no steps):
  title "Skein review", language en, six headings (page, comments,
  renamed/deleted/added/modified), seven named tab stops (skip, four
  files, old-map, departure), unlabelled_controls 0, phone_text_differs
  false, script_errors empty at both widths.
- Layout: desktop 1280/1280 zoom 1, phone 390/390 zoom 1,
  wider_than_screen false at both widths, too_wide empty at both widths.
- Screenshots opened: desktop two files (1280x1100, 1280x616,
  pictured_to 1716 of 1716, fully covered) and phone three files
  (780x1560 each, pictured_to 2340 of 2350, 10px tail unpictured).
  All diff tables, both anchored comments, and the footer line are
  readable on phone with no clipping, overlap, or horizontal page
  scroll in the pictured area.

Honest limits (kept, not claimed):

- Keyboard activation, zoom, screen-reader speech, and saved download
  are NOT RUN under the viewer. Only the markup snapshot and fresh-load
  keyboard_walk were returned; no activation was performed.
- The phone is an emulated 390px layout, not physical hardware, and the
  10px unpictured tail is not visually inspected.
- Duplicate full commit IDs remain in the committed sample identity
  block because the sample predates the `_format_ref` single-ID fix for
  future exports; packet/anchors/comments are unchanged.

Worth (author view): a reviewer on a phone can read the four changes and
both anchored comments without a forge account, which is the packet's
job. The independent tries and the owner assessment decide the milestone,
not this author note.
