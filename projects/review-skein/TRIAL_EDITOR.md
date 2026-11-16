# The independent try for the Skein comment editor

This companion tests editing for Milestone 2. Read [TRIAL.md](TRIAL.md) for the
packet-view method and its separate milestone criterion. This file is a method,
not evidence; an editor result alone does not close the milestone. Disclose
source reading, authorship and preparation help before claiming independence.
Try the page before its implementation or other people's results when possible.

## Prepare a disposable complete packet

You need Python, Git and either the house page viewer or a browser. Use one
writer for the packet. Keep its original files until the try ends. The committed
HTML samples omit their bundles and cannot replace a complete packet here.

```sh
python3 projects/review-skein/example.py /tmp/skein-editor-practice
python3 projects/review-skein/comment_editor.py compose \
  /tmp/skein-editor-practice/common scratch/skein-editor.html
```

Choose fresh output paths and create the `scratch` directory inside your room
first. The generator refuses existing outputs; wait for success and `example.json`.
Record the source revision, packet base/head IDs and a hash of `comments.json`.
Use the **compose** page: the alternative `page` command only edits existing
comments and cannot test adding one. Keep `review.html` available for comparison.

For the viewer, HTML and steps paths must be inside your own room, non-hidden
and non-symlink. The packet itself can stay at your chosen private temporary
path; the generated HTML contains its comment text, so keep it private too.

## House viewer limits

The rebuilt viewer sends real clicks and keys and measures phone and desktop
layouts even when the page has its own content policy. It speaks nothing and
cannot perform browser zoom or return a saved browser download. Speech, 200 %
zoom, clipboard transfer and a saved-file download witness stay `NOT RUN` unless
actually observed through a separate capable tool.

Edited-state attempts once timed out on this editor (16 November, before the
viewer repair): a `fill` that armed the editor's unsaved-changes question made
the view fail instead of returning the edited page, and a minimal dirty-flag
page reproduced the same failure, so the cause was the question, not this
editor. The viewer has since been repaired (house need
`skein-viewer-unsaved-dialog`, granted 16 November): it answers a page's
questions as a visitor would and reports `asked_before_leaving`. In the first
editor try after the repair, every edited-state look — composing, editing
bodies, resolving, and showing the edits JSON — returned with
`asked_before_leaving: true` and the typed values present in `fields`; the
`dialogs` lists were empty for the unsaved-changes question, so read that
signal from `asked_before_leaving`. Keep the editor's protection; do not remove
it to obtain a successful trial. In that same try, setting a resolution worked
by `fill`, while arrow keys alone did not change the native resolution menu in
two attempts; treat arrow-key operation of that menu as still to be observed,
not assumed from a changed value.

Use a new request ID per look:

```sh
.house-client view scratch/skein-editor.html --as YOUR-ID --request NEW-ID \
  --steps scratch/editor-steps.json
```

A steps file is a list of up to 30 actions, for example:

```json
[
  {"fill": ["#new-id", "trial-editor-note"]},
  {"fill": ["#new-body", "First trial note."]},
  {"press": "Tab"},
  {"press": "Space"}
]
```

This example uses the initially selected anchor. Read its actual path, side,
line number, commit and context before accepting that choice. `fill` prepares
text; the Tab and Space are actual key actions, not evidence that the entire
workflow was performed without pointer/focus assistance. A `focus` step likewise
sets a starting position; it does not establish keyboard reachability.

Each request and each device starts from the original page. Replay all needed
actions to reach a later state; do not infer persistence between requests or
combine desktop and phone edits as one session. A timeout is a failed attempt;
keep it and report a smaller later attempt separately. Split checks into short,
self-contained sequences where possible, retaining their independent baselines.

Read per-device `step_log`, `focused_after_steps`, `layout`, overflow facts,
errors and screenshots after the steps. `fields` and `text` describe desktop
state; compare `phone_text` when `phone_text_differs` is true. A different focused
state or text requires explanation, not an automatic content-loss verdict.
`keyboard_walk` is a bounded Tab walk on a fresh desktop load **without** steps.
The markup `tab_order` snapshot can include hidden controls, so use actual walks
and steps for reachability. Neither transcript is screen-reader speech.

Open screenshots at both widths and retain earlier images privately before
another look at the same path reuses their names. `files`, `pictured_to` and
`page_height` bound visual coverage: at most three screenfuls per device. A
control below that coverage has not been visually inspected, even when its
value is present in `fields`. Do not infer a visible focus outline there.

## The steps

Write one expectation before starting. Give each step/sub-check `PASS` only
when executed and observed; use `FAIL` for a mismatch and `NOT RUN` or `BLOCKED`
for unavailable evidence, with a reason. A trial reviewer reports defects before
repairing them. Use actual IDs, bodies and selected anchors in the record.

1. **Open the compose page.** Expect “Edit Skein comments”, **Add an anchored
   comment**, a rendered-line selector, labelled existing comments and controls,
   and the explanation that the packet is unchanged until command-line apply.
   The loading message should disappear and the count should match the packet.
   Inspect `text`, `headings`, `fields`, screenshots and `script_errors` at both
   widths. Blank content, missing controls, an unexpected script/content-policy
   error or observed overflow is `FAIL`. Record the viewer's network-refused
   surface without claiming an independent request trace you did not inspect.

2. **Navigate with real keys.** Start with Tab, then Enter on **Skip to comments**;
   test Tab/Shift+Tab through download/export, composer, comment links and body/
   resolution controls. Use `keyboard_walk` for the initial desktop sequence,
   explicit `press` steps and per-device `step_log` for later states and phone.
   Expect named reachable controls and no trap. Inspect visible focus where
   screenshots cover it. The return contains no `href` or location fragment:
   Enter dispatch or body focus alone does not prove a skip destination. Use
   subsequent focus position or a directly observed target; otherwise record
   that sub-check `NOT RUN`. Do not call assisted `focus` a keyboard-only path.

3. **Compose an anchored comment.** Select a rendered line and compare its path,
   side, line, commit and context with `review.html`. Enter a fresh ID and body;
   activate **Add comment to download** with Enter/Space or a click, stating which.
   Expect the new ID in the index and editor with that anchor/body and `open`
   resolution, cleared draft ID/body, and an increased changed count. Confirm
   `fields`, rendered text and the action log; the packet file must stay unchanged.
   A wrong anchor, lost body, duplicate insertion or changed packet is `FAIL`.

4. **Edit the new body.** Reach **Body for YOUR-ID**, replace its text and Tab out.
   Expect the exact edited body to remain under that ID, with its original anchor
   and unsaved-change status. Inspect the matching `fields` entry and text, not
   just a log saying fill succeeded. Wrong-comment edits or loss on blur is `FAIL`.

5. **Resolve and reopen.** Reach **Resolution for YOUR-ID**, select `resolved`,
   then `open` again with arrow keys. Observe both transitions in separate
   self-contained attempts if needed, replaying composition each time. Check
   exact values and unchanged body/anchor; resolution must not reattach an orphan.
   Ending open does not by itself prove the intermediate resolved transition.

6. **Hear labels and status changes — real screen reader required.** Record tool,
   version and mode, then edit, resolve and reopen while recording the exact
   words heard in action order. Expect labels identifying the comment, selected
   resolution and useful status/count announcements. Missing or misleading speech
   is `FAIL`. Under the viewer record `NOT RUN`; DOM text, an accessible-name
   snapshot or reading the transcript yourself cannot pass this step.

7. **Inspect phone fit.** Require phone `layout_width` and `screen_width` 390 at
   `zoom` 1, desktop 1280, and `wider_than_screen: false` at both widths. Inspect
   `too_wide` and phone screenshots for unclipped labels, anchor context, body
   fields, resolution controls and buttons without overlap. Overflow or visibly
   clipped/unreadable content is `FAIL`; desktop text cannot override it. Missing
   measurements are `NOT RUN / uncertain`, never a phone-fit `PASS`. Record
   unpictured controls and device-specific state differences rather than making
   a whole-editor visual claim from partial coverage. An emulated phone is not
   a physical-device trial.

8. **Zoom (NOT RUN under view).** In a capable browser, set desktop zoom to
   200 % and repeat navigation without reloading away the draft. Record the
   viewport and zoom; clipping, unreachable controls or hidden focus is `FAIL`.
   Under the viewer record `NOT RUN`; narrowing a viewport does not test zoom.

9. **Export the actual edit envelope.** In a capable browser, activate **Download
   edits** and inspect the saved nonempty file. A download-request message alone
   is not a saved-file witness. Under the viewer that check is `NOT RUN`.
   To continue the command-line roundtrip with the viewer, activate **Show edits
   JSON**, inspect the rendered envelope and transcribe its exact returned JSON
   into a private file. Record this as **transcribed returned JSON**, not a
   download or clipboard test. Check format, baseline, IDs, anchor and final
   body/resolution against your actual actions; never substitute a hand-invented
   envelope. If returned text is truncated or incomplete, stop this route.
   Keep desktop and phone results separate and explain any difference.

10. **Preview before writing.** Use the actual saved or transcribed file:

    ```sh
    python3 projects/review-skein/comment_editor.py check /path/to/packet /path/to/edits.json
    ```

    Expect exit 0 and only the intended IDs, anchors, bodies and resolutions.
    Compare packet hashes: `check` is read-only. Rejection or an unexpected edit
    is `FAIL`; do not force stale or unexpected data through apply.

11. **Apply the checked envelope once.** With unchanged inputs:

    ```sh
    python3 projects/review-skein/comment_editor.py apply /path/to/packet /path/to/edits.json
    python3 projects/review-skein/comments_view.py /path/to/packet/comments.json
    ```

    Expect success and exactly the checked changes in `comments.json`; other
    packet files stay unchanged. Do not reapply a successful envelope: its
    baseline is now stale. Keep a failed receipt and the original packet copy.

12. **Inspect fresh views.** Generate new outputs, rather than reopen snapshots:

    ```sh
    python3 projects/review-skein/review_view.py /path/to/packet --format html > scratch/after-review.html
    python3 projects/review-skein/comment_editor.py compose /path/to/packet scratch/after-editor.html
    ```

    Open both, find the added/edited comment and verify its exact anchor, body
    and resolution; the new editor should start with no changed comments.
    Missing, moved, orphaned or stale data is `FAIL`. Record actual keyboard,
    visual and speech observations separately, including coverage limits.

## Record the outcome

Keep a short note with reader/date, independence and preparation disclosures,
source revision, packet IDs, baseline hashes, request IDs/actions, inspected
screenshots and their coverage, new ID/anchor, exact final body/resolution and
export-transfer method. Give a result for each step and each device actually
tested. Retain failed/time-limited attempts, actual command exits and confusing
moments. No large evidence bundle is needed.

Call this companion **full** only if all steps and sub-checks, including real
speech, zoom and saved-download evidence, passed. A viewer-based editor try is
never "full"; report the observed interaction and command-line roundtrip while
keeping unavailable checks `NOT RUN` and unmeasured geometry
`NOT RUN / uncertain`. Any executed mismatch is a failed try; missing required
observations make it partial. Neither outcome supplies another person's
independent review or closes [TRIAL.md](TRIAL.md) by itself.
