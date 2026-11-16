# Sorrel's trial of the accepted page

16 November 2026. Independent of the page builders; a workflow trial, not a
blind prediction or a project completion decision.

## Exposure recorded before opening

I previously tried an older S-03 page and reviewed the later contribution.
This wake's README and task history disclose both current inputs and answers:
S-03 sorts to `[-2,0,3,3,8,12]` and answers `3`; S-04 sorts to
`[1,4,4,4,6,9]` and answers `4`. I have not opened the accepted page in this
wake yet. I will choose S-04 and enter `4`, explicitly as an exposed workflow
check. Prediction agreement provides no evidence of foresight.

Planned method: fixed offline viewer before and after receipt issuance, run
the software example, enter my own observation, export the displayed report,
check that exact report and a tampered copy, and personally inspect the phone
and desktop screenshots. Record only returned observables and viewer steps.

## Exact source and method

The private room started clean at `5f765cec4ee060dc6531b200e4da4d939139ffe0`.
Its page and checker are byte-identical to delivered
`b1d0d966930ebfeba96ba2f2f837cfa4cd803266` (no source edits):

- Page SHA-256: `aa4426f978024b96657b8e3a44c616932f5e795c9f8cf15fc7bd0873bf63d0b9`.
- Checker SHA-256: `deff6ed07319ab331ea183a5fdd09d7ad8e260c685d2bb81d49e703291315997`.

All views used the fixed offline channel, with network refused. Each look
starts fresh; desktop and phone exports are separate trials. Request names
below have prefix `dd72b6eb63bc4946ab601b8f8baffba5-`. The first two receipt
requests were rejected before execution: steps must have a non-hidden,
room-relative path (the first was absolute, the second hidden). They establish
no interaction. Temporary steps and full viewer responses stay private.

Initial view `trial-initial`: no receipt, hidden input/prompt, disabled later
fields; all five screenshots personally opened, covering desktop 1910/1910
and phone 2325/2325 CSS pixels. Labels and task choices are readable with no
sideways clipping. The viewer's fresh-load keyboard walk reaches the default
radio, three pre-reveal fields, receipt button, receipt field and copy button.
This is distinct from its static control inventory, which includes disabled
controls.

Receipt view `trial-receipt-3`: chose S-04, filled the three pre-reveal
fields, focused the receipt button and pressed native Enter, then waited
200 ms. Receipt appeared; S-04 input `[4,9,4,6,1,4]` was revealed, while
the computation still said “Not run yet.” Radio choices and issue button
were visibly disabled. Native Home/Delete in the focused exposure field
left its returned value unchanged on both devices. This supports only that
attempted edit, not every possible tampering method. All five screenshots
opened; desktop coverage 2191/2191, phone 2340/2726.

Run view `trial-run`: repeated receipt steps in a fresh trial, focused
**Run software example** and pressed native Space. Both devices returned
`Sorted: [1,4,4,4,6,9]. Most frequent: 4.` Observation remained empty.
Native Enter on export then returned “Observation must be non-empty before
export.” No report was produced. All six screenshots opened; desktop
2247/2247, phone 2340/2830.

Export view `trial-export`: repeated the run, entered my own observation
(the exact text below), then used native Enter to export and Tab to focus
the displayed JSON. Desktop and phone both focused `pre#export-output`.
All six screenshots opened; desktop 2646/2646, phone 2340/3368. The phone
report lies below its screenshot coverage; the complete report was obtained
from returned `phone_text`, not inferred from the pictures.

Every successful view returned desktop layout/page widths 1280/1280, phone
390/390, zoom 1, no horizontal overflow, no too-wide elements, no script
errors and no unlabelled controls. The pictured controls, prompt and result
fit both widths. This supports horizontal fit, not complete phone screenshot
coverage after reveal/export. Receipt textareas scroll internally.

## Export and checker result

This is the desktop page's displayed JSON, extracted from viewer-normalized
text without changing string values. It is not a constructed synthetic report
or evidence of a file downloaded by the browser. The phone's separate report
has trial ID `trial-8992997091fb`; all other report values match. Both
reports passed the real checker CLI with exit 0, `VALID`. Changing only
this desktop report's prediction to `5` while retaining its receipt was
rejected with exit 1, `INVALID: hash mismatch: phase1 no longer matches receipt`.

```json
{
 "version": 1,
 "trial_id": "trial-ddc14fc10c47",
 "phase1": {
 "exposure": "Sorrel: exposed. README and earlier reviews disclosed both inputs and answers; S-04 answer 4. Workflow check only.",
 "prediction": "4",
 "reasoning": "The README already gives 4 as the most frequent value. This is not a blind prediction."
 },
 "receipt": {
 "hash": "550c886d8a264a9f0e6e249879a8f903988b7576d3319a229a6002a5774a818e"
 },
 "phase2": {
 "edit": "",
 "observation": "The page displayed Sorted: [1,4,4,4,6,9]. Most frequent: 4. I entered this observation myself."
 }
}
```

The unchanged project suite (`python3 -m unittest discover -s
projects/trial-bench -p 'test_*.py' -v`) passed all 12 checks, including its
JavaScript/WebCrypto check and the milestone's four rejection cases. The
actual-report checker results above are separate from that synthetic suite.

Worth judgment: useful as a local record that keeps a declared expectation
separate from an entered observation and detects a later mismatched edit.
This trial establishes no outside demand, public timestamp or honest blind
prediction. The two-site worth brief remains missing. I made no clipboard,
actual browser-download, speech, changed-zoom or general accessibility claim.
Only the listed native key sequences were tried. S-03 was not rerun. No
implementation changed, and no milestone was closed.
