# The independent try for a Skein review packet

Milestone 2 asks whether a reader who did not build the changed page can use it.
Try a real exported page with the house page viewer (`view`, [HOME.md](../../docs/HOME.md))
or a browser, then record what happened. This is the method, not evidence of a try.
Disclose prior source reading, authorship and preparation help; an author's check
cannot supply the independent non-author milestone review.

The rebuilt viewer uses the browser's real keys and clicks, measures a true
390 px phone layout and a 1280 px desktop layout, and works with the page's own
content policy. The old injected-script and cropped-phone limits are historical.
It **speaks nothing** and takes no zoom steps. Screen-reader speech and 200 %
zoom remain `NOT RUN` under the viewer. A successful view-based try is a
**limited rendered-content and interaction inspection**, not full accessibility.

## Prepare a packet

Use the committed mixed-change sample:
`projects/review-skein/sample/milestone-2-mixed/review.html`. Its base is
`f730e964e18e0245862f09f7e0662ab14775e8bd`, head is
`7118f31b4d6d4ca429946929d95d9b3d6149f99a`; it has renamed, deleted, added
and modified files, one open comment and one resolved comment. The bundle is
omitted, so this sample is a page to read, not a complete packet to verify.
For a complete disposable packet, follow [EXAMPLE.md](EXAMPLE.md).

Read this method before the page markup, renderer, tests or others' reviews if
an unspoiled first impression is still possible. Write down what you expect,
the source revision and packet base/head IDs. Keep private packets private.

```sh
.house-client view projects/review-skein/sample/milestone-2-mixed/review.html \
  --as YOUR-ID --request NEW-ID
```

Use your assigned fixed channel and a new request ID for each look. Input HTML
and steps files must be inside your room on non-hidden, non-symlink paths.
Generated HTML is disposable output, not an artifact to commit.

## Read the viewer result honestly

Open every returned screenshot you rely on, at both widths. `screenshots`
contains a `files` list per device; `pictured_to` and `page_height` say how much
of a long page was pictured. At most three screenfuls per device are returned.
Anything below that coverage is not visually inspected. Screenshot names can
be reused by another look at the same path: copy them into a private attempt
folder before the next request if you need the earlier images.

- `text`, `headings`, `fields` and `tab_order` describe the desktop page after
  your steps. `tab_order` is a markup snapshot and may include hidden controls;
  it does not establish actual reachability or speech.
- `keyboard_walk` is a bounded real Tab walk on a **fresh desktop load without
  your steps**. It is not the focus order of your edited state or a phone walk.
- `step_log`, `focused_after_steps`, `layout`, `wider_than_screen`, `too_wide`,
  `script_errors` and screenshots are per-device observations of the requested
  steps. Use `press` steps to test a later state on each device.
- `phone_text_differs` compares post-step rendered text. A difference requires
  inspection of `phone_text`; it is not automatically lost content. An equal
  transcript does not establish equal focus, layout or a shared session.

Each request and device starts fresh. Replay the whole action sequence needed
for a later state; never assume an earlier request's edits survive. Steps are
limited to 30 and each device has a time bound. A timeout is a failed attempt,
not a successful page trial; retain it and report any narrower later attempt
separately. No runtime workaround or weakened content policy is needed.

## The steps

Record `PASS` only for an executed check with its named evidence. An observed
mismatch is `FAIL`; an unavailable or unperformed check is `NOT RUN` with a
reason. Continue independent checks, but do not repair the page during an
independent try.

1. **Open it offline.** Check `title`, `language`, `text` and `headings` for the
   page title, exact base/head IDs, file list and diffs. Open the screenshots;
   inspect `script_errors` at both widths. Expect readable content and no
   unexpected errors, including no content-policy failure excused as normal.
   Blank or missing content, a crash, or `wider_than_screen: true` is `FAIL`.
   Desktop text cannot override phone overflow. Missing layout measurement is
   `NOT RUN / uncertain`, not proof of fit. The viewer refuses network access;
   do not invent a separate network trace you did not inspect.

2. **Reach and activate the skip link.** On a fresh load, use real `Tab` and
   `Enter` steps. Expect `step_log` to name **Skip to changed files** as the
   first Tab stop. A separate one-Tab look can show its focused appearance in
   the screenshot. Then Tab after Enter: expect the first changed-file link,
   rather than unrelated earlier controls. Record the actual focus sequence.
   The return contains no `href` or location fragment; a log saying Enter was
   pressed, or `focused_after_steps: null` for the page body, alone proves no
   destination. If the target or focused appearance cannot be established,
   mark that sub-check `NOT RUN`, never infer it from the link's name.

3. **Use the changed-files index.** Compare index names in `text` and
   `tab_order` with each file's `headings` entry and `packet.json` status.
   Follow a file link using keys or a click and record the observed result.
   A dispatched input alone is not evidence of the destination: use subsequent
   focus position or a directly visible target; otherwise that activation
   sub-check is `NOT RUN`. Missing/mismatched files or a wrong observed target
   are `FAIL`. Record orphan navigation when the packet has orphan comments.

4. **Read one file section.** Inspect its `headings`, `text` and screenshots.
   Expect labelled Old/New line columns, Base text/Head text, correct line
   counts and enough context to understand the change. Unnamed or unreadable
   columns, or a missing section, are `FAIL`. Keep screenshot coverage limits
   explicit; the desktop transcript is not a picture of a later phone section.

5. **Distinguish status without colour.** In `text`, identify Added, Removed,
   Changed, Unchanged and Comment rows when present; compare their line numbers
   and code with the rendered table. Missing or contradictory status words are
   `FAIL`. These text observations are not screen-reader speech evidence.

6. **Walk the interactive surface.** Compare the markup `tab_order` snapshot
   with `keyboard_walk`: the skip link, each changed-files index link, every
   comment link, and **Orphaned and unplaced comments** when present must be
   named. The mixed sample has seven links. Check `unlabelled_controls`, then
   use explicit `press` steps for Tab/Shift+Tab and activation at both sizes.
   Expect sensible forward/backward focus, no trap, and visibly focused links
   in screenshots where pictured. Use `step_log` and `focused_after_steps` for
   the state you actually tested; do not infer a phone walk from desktop data.
   A broken observed order, unnamed reachable control or trap is `FAIL`.
   Unobserved parts remain `NOT RUN`, not a keyboard-wide `PASS`.

7. **Inspect the phone layout.** Check per-device `layout`: the phone must have
   `screen_width` and `layout_width` 390 at `zoom` 1, desktop 1280. Require
   `wider_than_screen: false` at both widths, inspect `too_wide`, and personally
   inspect the phone screenshots for unclipped readable columns, code and
   comments, with no overlap or whole-page horizontal scroll. Overflow or
   visible unreadable/clipped content is `FAIL`; intact text cannot override
   it. Missing measurements are `NOT RUN / uncertain`, never a phone-fit `PASS`.
   Inspect `phone_text` when it differs and explain every meaningful difference.
   Record unpictured sections separately; no blanket whole-page visual pass
   follows from three screenshots. An emulated phone is not physical hardware.

8. **Zoom (NOT RUN under view).** The viewer cannot zoom to 200 %. Record
   `NOT RUN`. In a separate real-browser check, set desktop zoom to 200 % and
   repeat navigation; record viewport, zoom and any clipped/overlapping content.
   A small viewport is not a browser-zoom test.

9. **One row read aloud (NOT RUN under view).** With a real screen reader,
   record its name/version, mode, row and exact words heard for status, old/new
   line numbers and code. Missing or misleading speech is `FAIL`. Without that
   tool, record `NOT RUN`; reading a transcript yourself supplies no speech test.

10. **One file read aloud (NOT RUN under view).** With the same screen reader,
    navigate from the file heading through its table, naming any confusing
    order, repeated headers or missing context and the exact words heard.
    Record `NOT RUN` when unavailable. No viewer screenshot or automated probe
    can pass this step.

## Record and decide

Keep a short note with reader/date, authorship and preparation disclosures,
source and packet IDs, request IDs, steps played, screenshots actually opened
and their coverage. Give one result per step and per separately tested device,
naming the returned signal or observation. Keep failed attempts, unknown target
checks, missing focus pictures and differences between device results visible.
Say what confused you and what made you want to give up.

A **full try pass** requires all ten steps, including real zoom and speech.
For a **limited rendered-content and interaction inspection**, steps 1–7 must
have their required checks observed and pass; steps 8–10 are `NOT RUN` under the
viewer. Any executed mismatch is a failed try. Any missing required observation
leaves it partial, rather than closing Milestone 2. Complete the editor companion
[TRIAL_EDITOR.md](TRIAL_EDITOR.md) separately and report its scope honestly.
The project owner assesses the milestone from the independent result; this
method, an author's check and passing markup tests close nothing on their own.

`probe.py` is a useful markup/identity preflight, not a browser or screen reader.
Its predicted reading order and the viewer's markup snapshot cannot substitute
for actual focus, visual quality, usability or speech. One try supports claims
for that reader and setup, not general accessibility or usefulness to everyone.
