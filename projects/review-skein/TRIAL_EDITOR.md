# The independent try for the Skein comment editor

This is a companion to [TRIAL.md](TRIAL.md), for the editing part of milestone 2.
It does not replace or change that file's milestone-2 criterion
(limited rendered-content inspection through the house viewer: steps 1–6
`PASS` on returned names and text only, step 7 with `wider_than_screen`
not `true` and phone-width rendered content intact — `phone_text_differs`
`false`, phone screenshot non-blank — while recording unobserved phone
geometry `NOT RUN / uncertain` when `null`/clipped, and steps 8–10, real
keyboard activation and the skip link's unreturned target `NOT RUN`).
Try both surfaces in the same sitting when possible, and record their results
separately. A completed editor try alone cannot close the milestone.

This file is the method, not evidence of a try. Authoring it, generating HTML,
passing Node tests or running the static editor probe does not execute these
steps or establish browser usability, downloads or accessibility.

## What you need

- A browser with JavaScript enabled and permission to save a local download;
  no server, account or network connection is needed.
- A desktop with a window you can narrow to about 360 CSS pixels, or a phone
  that can open the generated file; browser zoom to 200 percent on desktop.
  The house viewer (`view`) cannot zoom: with the viewer, actual zoom is
  `NOT RUN` (step 8) and is not required for a view-based editor check.
- A **real screen reader** and someone who can operate it, for step 6:
  VoiceOver, NVDA or TalkBack, for example. Mark missing speech evidence
  `BLOCKED` or `NOT RUN`; DOM inspection and a predicted transcript cannot
  supply it. The viewer speaks nothing, so speech under the viewer is
  always `NOT RUN`.

## House viewer limits (if you use `view`)

`view` renders the generated editor at phone (390 px) and desktop (1280 px)
widths with the network refused and returns text, headings, tab order,
labels, script errors, `wider_than_screen` and screenshots. The return
carries no `href` and no ID of any element that is not itself a tab stop,
so a skip link's target is unobserved under the viewer. It presses no
real keys, takes no zoom steps, speaks nothing and saves no download, and on
pages whose content policy restricts scripts it also leaves `wider_than_screen`
unmeasured (`null`). Steps requiring real interaction — keyboard navigation
and composition (steps 2–5), speech (step 6), zoom (step 8) and the
saved-download witness (step 9) — are `NOT RUN` under the viewer and never
`PASS`. Phone-width fit in step 7 is `NOT RUN / uncertain` whenever
`wider_than_screen` is `null` and the phone screenshot is clipped; only a real
browser or unclipped measured view can earn phone-fit `PASS`. The
`view`-checkable parts are the static-shell / rendered-content inspection in
steps 1, 7 (rendered DOM content and desktop screenshot) and 12: each `PASS`
names the returned signal (`text`, `headings`, `tab_order`,
`unlabelled_controls`, `wider_than_screen` when non-null) plus the named
screenshot. The CLI stages (steps 10–11) are shell-observable and unaffected.
A view-based editor check is a partial limited rendered-content inspection
by definition and is never "full" (see Recording the result); only a real
browser with keys, zoom, speech and downloads can be full. The CLI prepare
stages are unchanged.
- Python 3.10+, Git and this checkout for the CLI stages, or a preparer who
  can run those stages with you while you judge the browser experience.
- A disposable, complete packet with at least one rendered text line, using
  version-2 comments, and one writer for the duration of the try. Applying the
  download will change this copy's `comments.json`.
- A short place to record observations and exact screen-reader words.

## Prepare the actual files

Run commands from the source checkout root. These are the current commands in
[EDITOR.md](EDITOR.md). Replace `/path/to/packet` with your disposable packet,
and each output path with a fresh filename; editor generators refuse existing
outputs. Keep the page and download private if the packet is private.

If you need a complete invented packet rather than real work, follow
[EXAMPLE.md](EXAMPLE.md):

```sh
python3 projects/review-skein/example.py /tmp/skein-editor-practice
```

Choose a new workspace path if that one exists. Wait for successful completion
and `example.json`; use `/tmp/skein-editor-practice/common` as the packet below.
It has rendered lines, comments and a bundle. The committed milestone-2 sample
omits the bundle, so it is not a complete packet for this end-to-end method.
An empty version-2 comments file in another complete packet is also fine.

Generate the **compose** page, which supports both adding and editing comments:

```sh
python3 projects/review-skein/comment_editor.py compose \
  /path/to/packet /path/to/new-editor.html
```

Also have the packet's `review.html` available in another tab to read the diff.
Write down the source revision used to generate the editor and the base/head
commit IDs from `packet.json`. Retain the starting packet copy until the try
ends. Do not change its files through another tool while the editor is open.

The alternative below only edits existing comments; it cannot perform the
composition step, so do not substitute it for the initial compose page:

```sh
python3 projects/review-skein/comment_editor.py page \
  /path/to/packet/comments.json /path/to/new-existing-editor.html
```

## Do not read the implementation first

An independent reader should read this method, then try the generated page
before reading its markup, the editor source, tests or other people's results.
Write one sentence about what you expect the editor to do. If you already know
the implementation, disclose that: your observations still help, but they are
not an unspoiled first attempt. A preparer can generate files without coaching
you through the controls; record any help you need.

## The steps

For every step, record `PASS` only when you performed it and the observations
match *you should see*. An executed mismatch is `FAIL`; report it without
repairing the page. Use `BLOCKED` for a concrete unavailable capability or
prerequisite, and `NOT RUN` for a step you did not attempt, with the reason.
Continue independent steps where possible. Missing speech, viewport or CLI
steps leave this companion try partial; never infer a pass from generated HTML.

1. **Open the compose page (view or browser).** File a fresh `view` (new
   request ID) or open the file offline; open both screenshots.
   *You should see in the returned output (view) or on the page (browser):*
   “Edit Skein comments” in `text` / `headings`, a download control in
   `tab_order`, an “Add an anchored comment” section with a rendered-line
   selector, and existing comments in `text` if the packet has any; the
   loading message gone, a comment count present, `script_errors` without
   an unexpected runtime crash (on script-hash CSP pages, `view` reports
   its own content-policy note), `wider_than_screen` not `true` (`null`
   means overflow geometry was `NOT RUN / uncertain`, not `PASS`), and the
   explanation that the packet stays unchanged until CLI apply. Record how
   network refusal was checked (`view` refuses every address except its own
   page); if you could not inspect requests, record that limit rather than
   invent a check.
   *It fails if:* `wider_than_screen` is `true` at either width (DOM `text`
   and desktop screenshots cannot override measured overflow); `text` is
   blank, the title or controls are missing from `text` / `tab_order`, the
   screenshots show a blank page, or the page needs a network resource per
   the returned output.

2. **Navigate with the keyboard (real browser only; NOT RUN under view).**
   Put the mouse down. From a fresh load use `Tab`, `Shift+Tab`, `Enter`,
   `Space` and arrow keys. Activate **Skip to comments**, then navigate
   back to the composer. If there are no comments yet, the skip target
   may be empty; repeat the skip after step 3 adds one.
   *You should see (real browser):* the first page control is the skip
   link; its target is the comment editor. The download button, composer,
   comment index and existing body/resolution fields are reachable, with
   visible focus and no trap. Under the viewer this step stays
   `NOT RUN`: note only the snapshot for the step 1 inspection —
   `tab_order` entry 1's returned name is the skip link and
   `unlabelled_controls` is 0. The viewer returns no `href`, so the
   link's target is unobserved, and real key presses are `NOT RUN` —
   never claim either from the snapshot, and never record this step
   `PASS` under the viewer.
   *It fails if (real browser):* a control is unreachable, focus
   disappears, the skip leads nowhere once a comment exists, or you must
   use the mouse. Under the viewer there is no step 2 verdict; a
   snapshot contradiction (entry 1 not the named skip link, or
   `unlabelled_controls` above 0) is a `FAIL` finding against the
   step 1 rendered-content inspection, not a keyboard result.

3. **Compose a comment with the keyboard (real browser only; NOT RUN under view).**
   Select a rendered line. Read its path, side, line number, commit and
   context; compare it with `review.html`.
   Enter a new unique ID such as `trial-editor-note` and body `First trial note.`;
   record the actual ID and anchor. Choose **Add comment to download**.
   *You should see:* the comment appears in the index and editor with that
   anchor, body and `open` resolution. The draft ID/body clear, and the status
   reports a changed comment and changes not downloaded. Nothing has been
   applied to the packet. Leave any filters at their initial all/empty settings.
   *It fails if:* you cannot identify or select a line, the wrong anchor is
   used, the comment disappears, or you need to type a Git ID to add it.

4. **Edit the body with the keyboard (real browser only; NOT RUN under view).**
   Reach **Body for YOUR-ID**, replace the text with `Edited trial note.`,
   then tab out.
   *You should see:* the new text remains in that comment and the status still
   warns that changes have not been downloaded. Its anchor stays fixed.
   *It fails if:* typing loses focus, changes a different comment, loses the
   text on blur, or moves the anchor.

5. **Resolve and reopen with the keyboard (real browser only; NOT RUN under view).**
   Reach **Resolution for YOUR-ID**, choose `resolved`, then choose `open`
   again. Keep it open for the download.
   *You should see:* each selected value takes effect, with no lost body text
   or changed anchor. “Anchor state” remains separate from resolution: resolving
   a comment does not reattach an orphan or move a line.
   *It fails if:* you cannot make either transition, changes affect another
   comment, or resolution is confused with anchor state.

6. **Hear labels and status changes — requires a real screen reader.** Record
   its name/version and mode. With it running, navigate to the new comment's
   body and resolution controls. Append ` Heard in the trial.` to the body,
   tab out, resolve and reopen once more, pausing after each action for polite
   announcements. Keep the final body and resolution for the later preview.
   *You should see/hear:* the controls have labels identifying this comment;
   the selected resolution is understandable; the status region announces the
   comment/changed counts and that edits need downloading and CLI application.
   Record the **exact words heard**, in action order, including missing,
   repeated, interrupted or delayed speech. If nothing is announced, navigate
   to the status text to diagnose it, recording that separately from an automatic
   announcement. Counts describe comments changed, not the number of keystrokes.
   *It fails if:* controls are unnamed, their values cannot be understood, or
   status changes are silent or misleading. Reading a DOM transcript aloud
   yourself is not this step. Without a real screen reader, mark it `BLOCKED`
   or `NOT RUN`; keep the actual final body from step 4 for later steps.

7. **A narrow screen (view or phone).** Narrow the window to about 360 CSS
   pixels, open the same generated file on a phone, or file a `view`
   (phone 390 px, desktop 1280 px). Record the width/device used. A second
   device starts from the original data: repeat steps 3–5 there if needed
   and keep its download separate from the desktop one.
   *Phone-fit geometry (`PASS`):* phone-width fit earns `PASS` only when
   `wider_than_screen` is observed `false` at both widths **and** the phone
   screenshot (`390 px`) visibly shows labels, line context, body fields,
   resolution selectors and buttons unclipped and readable without overlap
   or whole-page horizontal scrolling.
   *Unobserved geometry (`NOT RUN / uncertain`):* when `wider_than_screen`
   at phone width is `null` (CSP blocks measurement) and the phone
   screenshot is clipped, phone-width layout fit and overflow geometry are
   explicitly **`NOT RUN / uncertain`** — **never a phone-fit `PASS`**.
   Intact DOM `text`, `tab_order` or a readable desktop screenshot cannot
   establish phone fit or phone usability. Under that limit, record only
   the phone-derived content observables actually returned
   (`wider_than_screen` not `true`, `phone_text_differs` `false` — the
   phone-width DOM text equals the returned desktop-width `text`; no
   phone-width `tab_order` is returned — and a non-blank phone
   screenshot), plus any visible right-edge clipping as uncertain.
   *It fails if:* `wider_than_screen` is `true` at either width (DOM `text`
   and desktop screenshots cannot override or contradict measured overflow);
   the phone screenshot is blank or the page fails to render; or content
   overlaps within the phone screenshot's visible, unclipped area. Words
   cut off at the right edge under `null` geometry are
   `NOT RUN / uncertain`, not by themselves a `FAIL`.
   Record whether this was `view`, an actual phone, or a narrow desktop
   window; one does not establish the other.

8. **Zoom (NOT RUN under view).** On desktop set browser zoom to 200 percent
   and navigate the composer, edited body, resolution and download control
   again. Do not reload the page, which would discard these undownloaded
   edits. The viewer takes no zoom steps, so under the viewer record
   `NOT RUN` with that limit and never `PASS`.
   *You should see:* readable, reachable controls without overlapping or cut-off
   content or whole-page horizontal scrolling.
   *It fails if:* zoom hides a control, obscures focus, clips text or breaks
   the layout. Record the viewport and zoom; a phone pinch gesture alone is
   not this desktop browser-zoom check.

9. **Download the edit envelope (real browser only; NOT RUN under view).**
   Ensure the draft ID/body are empty and the new comment has the intended
   final body and `open` resolution. Choose **Download edits** with the
   keyboard, then inspect the browser's saved file. The viewer saves no
   download, so under the viewer record `NOT RUN` and never `PASS`.
   *You should see:* a saved, nonempty `skein-comment-edits.json` (or the
   browser's renamed copy), and a status saying the download was requested
   and the packet is still unchanged. Record the actual saved filename/path.
   With a real screen reader still running, also record its exact announcement;
   otherwise mark this speech observation `BLOCKED` or `NOT RUN` separately.
   *It fails if:* no file is saved, a valid comment is blocked, or the page
   claims it has written the packet. A “Download requested” message alone is
   not a saved-file witness. Do not reload until the download is confirmed.

10. **Preview before writing.** Substitute the actual downloaded file path:

    ```sh
    python3 projects/review-skein/comment_editor.py check \
      /path/to/packet /path/to/skein-comment-edits.json
    ```

    *You should see:* exit 0 and a preview naming your added ID, exact anchor,
    final body and `open` resolution, plus only other changes you intended.
    The packet remains untouched: `check` is read-only.
    *It fails if:* a fresh valid download is rejected, preview data differs
    from your edits, or packet files change. Do not apply unexpected changes.
    A stale-file error is a finding to record; get a fresh editor and repeat
    the edits if another writer changed the packet. Do not force the old file.

11. **Apply the checked file.** Use the same packet and saved download:

    ```sh
    python3 projects/review-skein/comment_editor.py apply \
      /path/to/packet /path/to/skein-comment-edits.json
    python3 projects/review-skein/comments_view.py /path/to/packet/comments.json
    ```

    *You should see:* successful application and the saved new comment with
    the intended body, `open` resolution and original anchor. Only
    `comments.json` is replaced; no editor directly saves into the packet.
    *It fails if:* validation accepted the preview but the unchanged inputs
    cannot apply, unrelated comments change, or the saved values differ.
    Stop on an error; do not reapply a successful download, whose baseline
    is now stale. Record CLI exits and any concrete error.

12. **Open a fresh packet view and editor.** Generate the annotated packet
    view using [REVIEW_VIEW.md](REVIEW_VIEW.md), to a fresh output path:

    ```sh
    python3 projects/review-skein/review_view.py /path/to/packet --format html \
      > /path/to/new-review-with-comments.html
    python3 projects/review-skein/comment_editor.py compose \
      /path/to/packet /path/to/new-editor-after-apply.html
    ```

    Open both new files offline. Use the comment index to locate your ID.
    *You should see:* the annotated view puts the new comment at the selected
    line, with its final body and `open` resolution. The fresh editor has the
    same saved values and no new changes to download. Check with keyboard
    navigation and, when available, the real screen reader; record what it says.
    *It fails if:* the comment is missing, attached elsewhere, incorrectly
    unplaced, or has lost its body/resolution. The original static `review.html`
    and the old editor are snapshots: merely reopening them cannot confirm
    applied comments. Neither is regenerated by `apply`.

## Recording the result

Keep one short note, beside the disposable packet if convenient:

```text
Reader/date; independent and unspoiled? Preparation or navigation help:
Device/viewport; browser/version; zoom; screen reader/version/mode:
Skein source revision; packet source; base/head IDs; editor filename:
Chosen comment ID and anchor; final body/resolution; actual saved download:
1–12: PASS / FAIL / BLOCKED / NOT RUN — one observation or concrete reason each.
6: action -> exact words heard (or missing speech / BLOCKED / NOT RUN).
9: saved file observed? Exact speech separately, or BLOCKED / NOT RUN.
10–12: CLI exits, preview/apply outcome, fresh view/editor observations.
Most confusing moment; anything that made me want to give up:
Editor try: full / failed / partial. TRIAL.md ten-step result: separate reference.
```

Call this companion full only if every step, including the required real
screen-reader observations and the saved-file witness, was performed and
passed. A view-based try is a partial limited rendered-content inspection by
definition (steps 2–6, 8 and 9 are `NOT RUN` under the viewer, and step 7
phone geometry is `NOT RUN / uncertain` when `wider_than_screen` is `null`
and the phone screenshot is clipped) and is never "full". Any executed mismatch
is a failed try; any unperformed required part leaves it partial. Keep failures
and unavailable capabilities visible even when later steps work. Share a short
summary through the journal's `say` channel if you are a resident, without
private packet text or local paths; do not add a large evidence bundle.

One person's try establishes observations for that setup, not general
accessibility or completion of TRIAL.md. Someone who wrote the editor cannot
supply its independent non-author try. Report the experience before proposing
repairs.
