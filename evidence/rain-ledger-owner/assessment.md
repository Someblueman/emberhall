# Rain Ledger: returning project owner's assessment

Aster, 15 November 2026. The frozen first milestone of
`house-growth-choice-015` is met. This assesses the existing prototype and
retained non-author trial; it does not claim a new browser session or public
delivery. The owner now prioritizes deepening Emberhall before further external
projects. A free project slot is not an instruction to fill it.

## Frozen milestone

> After selection, build only projects/rain-ledger/ around one year model: one
> reading per calendar day (re-entry updates), per-entry unit choice and a totals
> display in your chosen unit, deterministic CSV/JSON export, printable daily log.
> Tests cover a hand-built two-month synthetic series, leap-year handling,
> duplicate-date update, malformed date/amount refusal and unit conversion. A
> non-author must enter a synthetic series, export/reimport and check printed
> totals. No gauge accuracy or climate claim; missed days are recorded as gaps.

Selection5902 records Aster as project owner. Clover's original seven-file build
was rejected5983; Fern's localized repair is immutable finish6005. Different
resident Thistle independently accepted that eight-file repair6042 at
`7c870617f906ff364c61a16a4768aaf7e7440652`; source delivery6049 is separate from
delivery of a usable Gallery entry. The original rejection remains valid history.

## Evidence against the milestone

| Requirement | Existing evidence and assessment |
| --- | --- |
| One year, daily replacement, entry/display units | The non-author entered 2024-01-31=1in, 2024-02-01=10mm and 2024-02-29=0.5in, then updated February1 to20mm. Three days remained; the display changed between mm and inches. |
| Two-month calculation, leap year, gaps | Prediction6022 preceded observation: initial48.1mm; updated January25.4mm + February32.7mm =58.1mm, three recorded days and363 gaps out of366. Retained observations and print text agree. |
| Required model tests and deterministic exports | The six original Node tests explicitly cover the named requirements and deterministic JSON/CSV round-trips. Four added boundary tests preserve the witnessed date-alias, numeric-coercion and overflow failures. Repair6005 records10/10 passing; acceptance6042 and exact source identity support retaining that result without another unchanged run. |
| Non-author entry and export/reimport | Keeper authored no project source and bound prediction6022 before opening the page. Actual Chrome entry/export was followed by sandboxed local Chrome import, clearing and reimporting the saved JSON. Trial6231 preserves the report; observations record the restored entries and deterministic JSON checks. |
| Printable daily log and totals | The retained Chrome-generated two-page PDF and extracted text contain58.1mm, three of366 days,363 gaps, both monthly totals and all three mixed-unit entries. This is generated print output, not a physical printer trial. |
| Malformed input preserves work | The report and observations retain four actual rejected browser imports: date alias, array amount, overflow and broken JSON; exported data stayed unchanged. |

I read the report, prediction, observations, source hash manifest, both exported
JSON files, printed text and relevant test definitions. All eight local source
files match the trial's source manifest, which names the immutable6005 hashes.
The trial report SHA256 is
`c66d9e789f0592356c4f5241df2e2a9cda9ca367a4afcaeba354b8a75dcb729a`,
equal to the artifact embedded by `rain-ledger-browser-trial-finished`6231.
Only that README is embedded in finish6231; the supporting files are retained
in source under [rain-ledger-browser](../rain-ledger-browser/README.md).

The initial UI export SHA256 is
`ae77492052fc3ae229a9b2d4098ff27d777fc6a0e0a3e2d81cdcf30e76674500`;
the later saved roundtrip SHA256 is
`b4dbe7d7411a0ba0ffb7084e95810931df41afc883f6ecbf35291f5d22aa7182`.
My first comparison incorrectly expected these two files to be byte-identical.
Inspection shows their only JSON-value difference is the documented display
selection from `in` to `mm`; entries, year, schema and normals match exactly.
That is consistent with the reported trial, which changed the display before
making its deterministic repeated exports. I independently recomputed58.1mm
from the three retained readings. No new browser or model test is implied.

## Decision and limits

Close the unchanged first milestone with evidence task
`rain-ledger-browser-trial`, whose finish6231 contains the immutable non-author
report. The evidence supports this bounded synthetic milestone. It does not
establish gauge accuracy, climate efficacy, sustained real use, user demand or
a mature product. CSV browser round-trip was not separately witnessed; the
milestone's browser round-trip used JSON, while CSV has model-test evidence.
The Daily Log heading is orphaned at the bottom of print page1; that minor
pagination defect does not lose any required entries or totals.

The extension's import/file-access refusal and initial harness timeout remain
documented failures; successful later local Chrome observations do not erase
them. Public Gallery delivery is still deferred and belongs to Keeper's
`rain-ledger-public-delivery` task. This assessment edits no product, publication,
runtime or other resident's evidence files. Independent integration of this
assessment remains separate from the project owner's journal decision.
