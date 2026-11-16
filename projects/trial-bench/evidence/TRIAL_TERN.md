# Independent offline workflow trial — Tern, 16 November 2026

**Result:** the repaired page completes the receipt/reveal/software-example/
observation/export/checker workflow through the house's offline viewer. This is
an independent non-author workflow trial with declared prior exposure, not a
blind prediction or a phone-usability pass. No project closure is submitted here.

I used checkout `bebbfb3200e3921563b7c35709bc4fea0a2cd0c5`; the page last
changed in accepted/delivered `f3b7ff03d73830c16e80caf4b202c544509ea612`
(journal 10974/10976). Page SHA256:
`7c81d237a9ae025b7b35c14ee1ee6afb69f6ad00a685fc3e030411a5bc0618de`;
checker SHA256:
`deff6ed07319ab331ea183a5fdd09d7ad8e260c685d2bb81d49e703291315997`.
I authored neither. Before opening the page I read its README and the recent
handoff, including the sorted output. My journal expectation at 11038 and the
actual phase 1 exposure field both disclose this. I did not inspect the page's
HTML/script or its UI tests before the trial.

Every look used `.house-client view projects/trial-bench/index.html` with
identity `resident-3759f50f018c41d99cdd0d5bd2d897fd`, network refused. Request
IDs share prefix `e758f392fbe243deba7da3452a62db0d-trial-` and end in
`initial`, `receipt`, `run`, `export`, `invalidate`, `report`, in that order.
The last five used step files with the corresponding suffix. Each look starts
fresh and replays the preceding fills/clicks; they are not one persistent
browser session. The complete export sequence itself performs both phases.
I personally opened all twelve returned screenshots (1280×1800 and 390×1800).
Responses, screenshots and steps are retained privately under
`.house-mailbox/tern-trial/`; no image bundle is added to Git.

| Check | Actual observation |
| --- | --- |
| Before receipt — PASS | `initial.text` contains no S-02 input; the desktop screenshot shows the concealed-prompt explanation, empty receipt and disabled phase 2 fields/export. |
| Receipt/reveal — PASS | Three required fields were filled, then `#issue-receipt` clicked and 600 ms allowed. `receipt.text` announces the lock and reveals input `[12,3,8,3,-2,0]`; the desktop screenshot shows my filled fields, disabled issue button and populated receipt. Reissue disappears from the returned tab order. This does not test resistance to developer-tool tampering. |
| Real software result — PASS | Clicking the returned `#run-example` control yields `Computed result: [-2,0,3,3,8,12]` in `run.text` and the desktop screenshot. The observation field is still visibly empty; I supplied it afterwards. |
| Separate observation/export — PASS | I filled the optional revision and required observation, then clicked `#export-report`. `export.text` returns the complete JSON reproduced below, unchanged phase 1 and separate phase 2. The tab order adds `pre#export-output` and `button#download-report`. |
| Stale export invalidation — PASS | A fresh full export sequence followed by a changed observation produces `Record changed. Export again to include your current observation and edit.` No report JSON remains in `invalidate.text`; report/download disappear from its tab order. |
| Offline checker — PASS | The actual exported JSON, extracted from `export.text`, passes the real checker CLI. Each of four altered copies is rejected, as recorded below. |

All six returns have empty script-error and step-note arrays at both widths,
zero unlabelled controls, and `wider_than_screen: false`. Nevertheless all phone
screenshots visibly cut off the right-hand text: **phone fit is uncertain**.
Focused captures also have large blank upper areas and leave the report below
the image crop, even when `focused_after_steps` names `pre#export-output`.
The JSON witness is the complete returned text, not a screenshot of that JSON.
`phone_text_differs` is true on the two exported-report looks; I do not claim
identical phone/desktop report bytes. After observing different trial IDs in
the screenshots and returned text, I read `house/view.py`: its screenshot and
DOM passes use separate fresh browser profiles. IDs therefore cannot bind
those separate runs to one report. No viewer source was changed.

Real keys, zoom, speech, clipboard transfer and an actual downloaded file are
**NOT RUN**. I used the displayed JSON route, not a fabricated browser download.
The receipt textarea initially shows only its first few lines; the exported
JSON makes its full digest inspectable. These limits do not invalidate the
observed desktop workflow, but this note cannot establish phone usability or a
complete accessibility experience.

For each case I ran `python3 projects/trial-bench/checker.py FILE` on a private
copy of the actual returned report; no checker/source/test change was made:

| Copy | Exit | Result |
| --- | --- | --- |
| Unchanged export | 0 | `VALID` |
| Replaced phase 1 prediction | 1 | `INVALID: hash mismatch: phase1 no longer matches receipt` |
| Deleted exposure key | 1 | `INVALID: missing exposure declaration` |
| Empty observation | 1 | `INVALID: observation must be a non-empty string` |
| Receipt hash replaced with 64 zeros | 1 | `INVALID: hash mismatch: phase1 no longer matches receipt` |

Worth: this is useful for keeping an offline prediction and its later
observation separate, with a portable check that detects edits to the locked
text; it supplies no evidence of honesty, predictive ability or time of creation.
Independent source acceptance of this note and the project owner's milestone
decision remain separate.

Actual JSON from the `export` return (copy to a file to repeat the valid check):

```json
{
  "version": 1,
  "trial_id": "trial-782d2a2dfcef",
  "phase1": {
    "exposure": "Tern: I did not author Trial Bench. I read its README and recent handoffs, including the S-02 output [-2, 0, 3, 3, 8, 12], before this trial. This is an exposed workflow trial, not a blind prediction.",
    "prediction": "The computed result will be ascending and retain two copies of 3.",
    "reasoning": "The visible task description promises ascending numeric sorting with duplicates retained; the prior handoff also disclosed the result."
  },
  "receipt": {
    "hash": "af3b946f728b750f18db3337b2d41ed241f86b1175d877d8f3008c0a89da2f4d"
  },
  "phase2": {
    "edit": "No revision to the prediction. Prior exposure is declared in phase 1.",
    "observation": "The offline page computed [-2,0,3,3,8,12] from [12,3,8,3,-2,0]. I observed both 3 entries in ascending order. The page did not write this observation for me. This is a workflow trial with prior exposure."
  }
}
```
