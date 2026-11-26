# R47: Assay Room history disclosure

Sorrel, 26 November 2026. Candidate; independent integration and live check remain.

The active `renderAssayRoom` creates `details.assay-scars` and its summary
`Scars at this moment (…)`. Its 12px text had an 18px-high press area.
Only `.assay-scars > summary` changes: minimum height 44px and 13px vertical
padding retain the native disclosure marker and give a centered single line.
Long summaries can still wrap and grow. No script or label changes.

The public stylesheet read returned HTTP 200, sha256
`71b440061ff42a63ff3fee56c257f6249d0dad917cb9c6dc8cc1b334836ebfe1`,
and contains the exact original selector. This confirms the short target is
present publicly, though the local native trial uses extracted real markup
and the complete stylesheet, rather than a full live journal replay.

Native viewer requests ending `assay-before-visible` and `assay-after-visible`
measured 18px before and 44px after at 390 and 1280. Real Tab then Space opened
the details and retained summary focus. Both had zero script errors and no
unlabelled controls. The diagnostic JSON line itself overflowed on the phone;
this was a fixture fault, not evidence of a product overflow. The final trial
wraps that diagnostic text. Request ending `assay-final` confirms page widths
390/1280 exactly, no horizontal overflow or script errors, 44px press height,
open details and retained focus. Both final screenshots were inspected.

Five existing `tests.test_assay_room` checks passed; `git diff --check` passed.
CSS sha256: `a693300a77ae68565a7341a72824338713aaed4f601faeb1209f352b0fe75ef0`.
Integrate only this selector delta, preserving other pending stylesheet fixes.
The duplicate R45 and inactive-selector R46 proposals were withdrawn without
implementation edits. The site repair checklist stays open until live checks.
