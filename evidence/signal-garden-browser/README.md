# Signal Garden: an actual keyboard walkthrough

On 14 November 2026, Keeper played the delivered **Bent lantern** challenge in
the CUA in-app browser, through a temporary loopback-only server scoped to this
project. The earlier browser-host failure remains historical evidence; a browser
was available for this test. No Night Ferry target or denied file URL was used.

Keeper did not author the model, page or challenge. The project README and
`unseen.json` were read first; prediction **3075** was recorded before opening
the page or answer key. Prior Hamming/interleaving knowledge was disclosed: this
is an independent expert walkthrough, not evidence that a novice learned the
concept or a general accessibility assessment.

## Observed route

1. Starting from the page, Tab reached the first tile. Tab and Space entered
   `1001 / 0100 / 0110 / 0010`; five Right presses set burst start to 6. Length
   remained 4. The visible values were checked before proceeding.
2. Tab reached the prediction selector; Space, Home, Down and Return chose
   **Only interleaved**. Tab and Return began the four-step, initially paused
   walkthrough. Each subsequent Return advanced exactly one step; no timed
   advance was observed during inspection.
3. The channel view placed consecutive errors in rows A/A/B/B, and interleaved
   errors in B/C/D/A. At decode, consecutive recovered `1010/1100/0110/0010`
   with **3 changed pixels**; interleaved recovered the original with **0**.
   The page said the prediction matched.
4. Tab and Space opened the plain-text trace. It reported error counts
   `[2,2,0,0]` versus `[1,1,1,1]`, and syndromes `[1,3,0,0]` versus `[3,2,2,2]`.
   The separate answer key was opened only after this observed result and
   agreed with the prediction, decoded rows, counts and explanation.
5. Wide (1280×720) and phone (390×844) views showed readable controls, channel
   chips, recovered picture and trace, with no page-level horizontal overflow.
   At phone width, Shift+Tab and Return activated New prediction: the old
   walkthrough became hidden, prediction cleared, Follow the signal disabled,
   and focus returned to the prediction selector. The viewport was restored.

## What the witness learned and what it does not establish

The boundary-straddling burst gives two errors to each of two consecutive row
blocks. The decoder still attempts syndrome flips and changes three payload
pixels. Interleaving distributes the same four channel errors one per block,
so all rows recover without extra transmitted bits. The trace makes the failed
correction visible; a zero/nonzero syndrome alone cannot certify the original
picture. This result does not extend the guarantee beyond one burst of four.

No blocking usability defect was observed on this route. The phone stacks the
two layouts, requiring vertical scrolling to compare them; the trace is long.
Those are usability limits, not hidden failures. No screen-reader, touch-input,
other-browser or novice-learning claim is made. Existing arithmetic tests were
not rerun as a substitute for this browser evidence.

The project owner must still assess this evidence and record project closure
under the active shelf rule. This report is not itself a project-close event.

- [Actual rendered text and phone dimensions](observed-dom.json)
- [Source identities and prediction receipt](source.json)
- [Wide result and keyboard-opened trace](wide-trace.jpg)
- [Phone recovered-picture view](phone-result.jpg)
