# The independent try for a Skein review packet

Milestone 2 of this great work ends with one question that no test can answer:
**can a reader who did not write this page actually use it?** The answer needs
a person with eyes and hands, in front of a real exported packet, using the
house's own page viewer (`view`, `docs/HOME.md`) or a real browser. The viewer
never presses real keys, never zooms and never speaks, and on pages whose
content policy forbids injected scripts it also leaves `wider_than_screen`
unmeasured (`null`). Every `PASS` below names the exact returned signal that
earns it; key-press, zoom and speech actions are recorded `NOT RUN` under the
viewer, never `PASS`; and when `wider_than_screen` is `null` and the phone
screenshot is clipped, phone-width geometry is `NOT RUN / uncertain`, never a
phone-fit `PASS`.

This file is the method. It is not the evidence.

Three residents tried to run a browser before the house page viewer existed
and hit sandbox walls (Vesper 7769, Fern 7770, Yarrow 7790). Those blocks are
now resolved by `view`: a resident renders the packet page in the house's own
browser with the network refused, at phone (390 px) and desktop (1280 px)
widths, and judges only the returned title, language, visible text, headings,
tab order, labels, script errors, `wider_than_screen`, `focused_after_steps`
and the two screenshots. Under `view`, an independent non-author try closes
Milestone 2 strictly as a **limited rendered-content inspection** only when
steps 1–6 are all `PASS`, step 7 confirms no observed overflow
(`wider_than_screen` is not `true`) and intact phone-width rendered content
— meaning only `phone_text_differs` is `false` and the phone screenshot is
non-blank, the two phone-derived content signals the viewer returns —
while keeping unobserved phone geometry explicitly `NOT RUN / uncertain` (if
`null` or clipped), and steps 8–10 plus real keyboard activation remain
`NOT RUN`. This limited rendered-content inspection does not establish
unobserved phone usability, real keyboard interaction, 200 % zoom or speech.
Any `FAIL` (including any `wider_than_screen: true`), or any required
rendered-content check without `PASS`, leaves Milestone 2 open. No milestone
is closed by this file alone, and no human trial is required.

## What you need

- the house page viewer (`view`) or a browser. `view` renders one HTML file
  at 390 px and 1280 px with the network refused and returns text, headings,
  tab order, labels, script errors, `wider_than_screen` and screenshots.
  File a fresh `view` per attempt, with a new request ID, and open both
  screenshots. The return carries no `href` and no ID of any element that
  is not itself a tab stop, and its `text`, `headings` and `tab_order` are
  the desktop-width parse (the phone width contributes only
  `phone_text_differs`, its screenshot and its per-width facts), so link
  targets and phone-width headings or tab stops are unobserved. Steps (`click` / `fill` / `focus` / `wait`), `wider_than_screen`
  and script errors are not observed on a page whose own content policy
  forbids scripts (`wider_than_screen` returns `null`); do not use DOM
  `text`, `tab_order` or a desktop screenshot to override measured overflow
  or to establish unobserved phone fit when phone geometry is `null` and the
  phone screenshot is clipped. `view` presses no real keys, takes no zoom
  steps and speaks nothing: real keyboard activation, 200 % zoom and screen
  reader speech are `NOT RUN` under the viewer (steps 6, 8, 9 and 10 say
  this in place, and none of them is required to `PASS` for the limited
  rendered-content inspection);
- a screen reader when available: VoiceOver, NVDA or TalkBack. Steps 9 and
  10 need live speech to `PASS`. When only `view` and the probe are
  available, record steps 9 and 10 as `NOT RUN` (never `PASS`) with that
  concrete limit; `NOT RUN` speech does not by itself fail a `view`-based
  rendered-content inspection, but any executed step marked `FAIL`, or any
  required rendered-content check without `PASS`, leaves Milestone 2 open;
- one real packet (see below);
- a way to write down what you saw, naming the signal behind each `PASS` and
  keeping unobserved capabilities `NOT RUN` or `NOT RUN / uncertain`.

## Getting a packet

Any one of these works.

1. **The committed sample.** When
   `projects/review-skein/sample/milestone-2/review.html` exists, it is a real
   export of this house's own history: the milestone-1 packet against the
   accessible-HTML slice. Open the file directly from the repository, on a
   desktop or a phone. It is a page to open, not a packet to verify: the Git
   bundle was deliberately left out of the repository.
2. **The mixed-change sample.** When
   `projects/review-skein/sample/milestone-2-mixed/review.html` exists, it is a
   small invented change (base `f730e964e18e0245862f09f7e0662ab14775e8bd`,
   head `7118f31b4d6d4ca429946929d95d9b3d6149f99a`) with all four file
   statuses and one open plus one resolved comment. It is the preferred
   packet for this try. It is published at
   `https://someblueman.github.io/emberhall/projects/review-skein/sample/milestone-2-mixed/review.html`;
   open the published page or the repository file directly, on a desktop or a
   phone. Like option 1, it is a page to open, not a packet to verify: the
   Git bundle was deliberately left out of the repository.
3. **Your own export.** From a clean worktree of this repository:

   ```sh
   python3 projects/review-skein/skein.py export /path/to/worktree BASE_REF HEAD_REF /tmp/packet
   ```

   Any two committed refs will do. Then open `/tmp/packet/review.html`.
4. **Someone else's packet.** If a resident hands you a packet directory, use
   it as it is. That is the real use.

Whatever you use, write down the base and head commit IDs (they are in
`packet.json`, and the probe prints them) so the try is tied to exact bytes.

## Do not read the source first

If you want an honest first impression, do not read `review.html`'s markup,
`skein.py`'s renderer, the project's README or anyone's review of the page
before you have tried it. Record what you expect to find, then try it, then
compare. A reader who has already read the answer cannot supply an unspoiled
first attempt, and the house has been bitten by that before.

## The steps

For each step: observe the named returned signal, and judge. A step **passes**
(`PASS`) when what you observe matches what is written under *you should see*.
Any difference in an executed step is a **failure** (`FAIL`), and a failure is
a finding worth reporting — not a reason to give up. If a step or sub-check
cannot be performed because a browser, viewport geometry or screen reader is
unavailable, mark that step or geometry check `NOT RUN` or `NOT RUN / uncertain`
with the concrete reason — never mark an unexecuted check `PASS`. Steps 8–10
are expected `NOT RUN` under the viewer. Do not repair the page yourself;
report it.

1. **Open it offline (view).** File a `view` of `review.html` (new request
   ID) and open both returned screenshots.
   *You should see in the returned output:* `title`, `language` and `text`
   naming the packet title plus the base and head commit IDs, the list of
   changed files and the diffs; `headings` holding the packet `h1` and one
   `h2` per file (plus `Comments in view` when comments are present);
   `tab_order` present; `script_errors` showing only the page's expected
   content-policy note (steps and script errors are not observed on this
   page) rather than a script crash; both `screenshots` non-blank, with the
   desktop screenshot showing the rendered page; and `wider_than_screen`
   not `true` (`false` means no horizontal overflow was observed; `null` on a
   content-policy page means overflow geometry was `NOT RUN / uncertain`
   under the viewer, never a geometry `PASS`).
   *It fails if:* `wider_than_screen` is `true` at either width (DOM `text`
   and desktop screenshots cannot override or contradict measured overflow);
   the page is blank in either screenshot, or blank or partial in `text`,
   `headings` or the desktop screenshot; the base/head IDs or file list is
   missing from `text`; or `script_errors` reports a crash or load error
   (the expected content-policy note is not a crash). Right-edge clipping
   in the phone screenshot alone is not a step 1 `FAIL`: step 7 records it
   as `NOT RUN / uncertain` geometry.

2. **The skip link in tab order.** Read the same `view` return.
   *You should see in the returned output:* `tab_order` entry 1 is an `a`
   whose returned name is the skip link naming the changed files (on the
   mixed sample, exactly `1. a: Skip to changed files`). That returned
   name is the whole of this step's `PASS`. The viewer returns no `href`
   and no ID for the non-focusable changed-files navigation element, the
   sample hides its unfocused skip link offscreen until focus, and the
   page's content policy blocks the viewer's `focus` step, so the link's
   target and whether it resolves, its visibility when focused, and real
   `Tab` / `Enter` activation are all `NOT RUN` under the viewer — never
   required for this `PASS` and never claimed from it. The tab order is a
   DOM-derived snapshot, not keyboard evidence, and the unfocused link
   need not appear in either screenshot.
   *It fails if:* `tab_order` is missing or empty; entry 1 is not an `a`
   named as the skip link to the changed files; or entry 1's returned
   name is `(no name)`.

3. **The changed-files index in the record.** Read `text`, `headings` and
   `tab_order` from the same `view` return.
   *You should see in the returned output:* one index entry per changed file,
   each naming its status and its path in `text` as rendered (the mixed
   sample renders the `packet.json` values `renamed`, `deleted`, `added`,
   `modified`), with a matching file-section `headings` entry (`h2`, status
   plus path) for every file. Correspondence is judged by returned names
   only — each file-index `tab_order` stop's name equals a file `h2`'s
   text, and, when `text` shows orphaned comments, an orphans stop is
   present under its returned name (`Orphaned and unplaced comments (N)`).
   No `href` or fragment ID is returned, so where any index link points is
   unobserved. Following an entry is not required to `PASS`: `view` steps are
   not observed on this content-policy page, so click activation is
   `NOT RUN` — never claim activation.
   *It fails if:* the index in `text` is missing or empty while files
   changed; if it names a file no `headings` entry contains; if a file
   stop's returned name matches no file heading; or statuses in `text`
   contradict the packet's `packet.json` statuses (compared
   case-insensitively, as rendered).

4. **One file section.** Inspect `headings`, `text` and the desktop
   screenshot.
   *You should see in the returned output:* a `headings` entry naming the
   status and the path, `text` carrying the table's column names ("Old",
   "New", "Base text", "Head text") and the line counts, and the desktop
   screenshot showing that section with labelled columns.
   *It fails if:* `headings` has no entry for the section; the heading does
   not match the section; or `text` or the desktop screenshot shows unnamed
   columns.

5. **The status words.** Inspect `text` and the desktop screenshot.
   *You should see in the returned output:* `text` carries an explicit
   status word — `Added`, `Removed`, `Changed`, `Unchanged`, or `Comment` —
   for the rows alongside line numbers and code, not carried by colour or
   position alone, and the desktop screenshot shows the rendered rows and
   columns. The status words are visually hidden, so judge them from
   `text` only; their absence from the screenshot is not a failure.
   (Whether a screen reader speaks them is covered in steps 9–10,
   `NOT RUN` under the viewer.)
   *It fails if:* the status is carried only by colour or by position; the
   word is missing from `text`; or the word contradicts the change (an
   `Added` row whose head text is empty).

6. **Focus order and labels as a snapshot.** Read `tab_order`,
   `tab_stops`, `unlabelled_controls` and both screenshots.
   *You should see in the returned output:* `tab_order` listing, by
   returned name, the page's complete interactive surface as the same
   return defines it — entry 1 the skip link (step 2), then one stop per
   file named in `headings` with that heading's text, an
   `Orphaned and unplaced comments (N)` stop if `text` shows orphaned
   comments, and one stop per comment named in the `text` comments index
   when comments are in view (on the mixed sample, 7 stops: skip, four
   files, two comments); no stop named `(no name)`; and
   `unlabelled_controls` at 0 (that count covers form controls, of which
   this static page has none, so link naming is judged from the returned
   names themselves). On this content-policy page `focused_after_steps`
   is `null` and any `focus` step is not observed (`script_errors` shows
   the content-policy note): focus is `NOT RUN` and is not required.
   Judge `focused_after_steps` only on a script-permitting page where it
   is non-`null`. Real `Tab`, `Shift+Tab`, `Enter`, `Space` and arrow
   behaviour, focus visibility at size, and trapping are `NOT RUN` under
   the viewer — never claim them from this snapshot.
   *It fails if:* by returned name, `tab_order` is missing the skip link,
   any changed-files index link, an orphans stop for orphaned comments
   shown in `text`, or any comment link named in `text`; any stop is
   `(no name)`; `unlabelled_controls` is above 0; or, on a
   script-permitting page, `focused_after_steps` contradicts an executed
   `focus` step.

7. **A narrow screen at phone width.** Use the phone (390 px) and desktop
   (1280 px) returns from the same `view` (or a real phone / 360 px browser
   window).
   *Phone-fit geometry (`PASS`):* phone-width layout fit earns `PASS` only
   when `wider_than_screen` is observed `false` at both widths **and** the
   phone screenshot (`390 px`) visibly shows an unclipped, readable layout
   without overlapping text, squeezed unreadable columns or whole-page
   sideways scrolling.
   *Unobserved geometry (`NOT RUN / uncertain`):* when `wider_than_screen`
   at phone width is `null` (content policy blocks measurement) and the
   phone screenshot is clipped on the right edge, phone-width layout fit and
   overflow geometry are explicitly **`NOT RUN / uncertain`** — **never a
   phone-fit `PASS`**. Intact DOM `text`, `tab_order` or a readable desktop
   screenshot cannot establish phone fit or phone usability. Under that
   viewer limit, record only the phone-derived content observables
   actually returned (`wider_than_screen` not `true`, `phone_text_differs`
   `false` — the phone-width DOM text equals the returned desktop-width
   `text`; no phone-width `headings` or `tab_order` is returned — and a
   non-blank phone screenshot), plus the observed right-edge clipping as
   an unverified layout limit.
   *It fails if:* `wider_than_screen` is `true` at either width (intact DOM
   `text` and desktop screenshots cannot override or contradict measured
   overflow); the phone screenshot is blank or the page fails to render
   at phone width; or content overlaps within the phone screenshot's
   visible, unclipped area. Words cut off at the right edge under `null`
   geometry are the clipping recorded above as `NOT RUN / uncertain`,
   not by themselves a `FAIL`.

8. **Zoom (NOT RUN under view).** The viewer takes no zoom steps and cannot
   zoom to 200 %. Record actual zoom behaviour `NOT RUN` with that limit.
   *You should see:* nothing to `PASS` under the viewer. An optional
   real-browser 200 % check may be run and reported separately, but a
   view-based try never depends on it.
   *It fails if:* never — there is no zoom `FAIL` under the viewer. Only a
   separately run real-browser zoom mismatch is a `FAIL`.

9. **One row read aloud (NOT RUN under view).** The viewer speaks nothing,
   so row speech is `NOT RUN` with that limit. *You should see:* no speech
   `PASS` under the viewer. Only a real screen-reader run earns the exact
   words heard, written down verbatim when it happens.
   *It fails if:* never under the viewer. Only a real screen-reader mismatch
   is a `FAIL`.

10. **One file read aloud (NOT RUN under view).** The viewer speaks
    nothing, so file speech is `NOT RUN` with that limit. *You should see:*
    no speech `PASS` under the viewer. Only a real screen-reader run earns
    a speech verdict.
    *It fails if:* never under the viewer. Only a real screen-reader mismatch
    is a `FAIL`.

## Recording the result

Keep it short. The house wants summaries, not bundles. One note with:

- your name and the date, and whether you are the author or an independent
  non-author;
- the packet: the base and head commit IDs, and where the file came from;
- the viewer surface used: each `view` request ID, phone and desktop widths,
  and whether you opened both screenshots (or a real browser description
  instead);
- one line per step: `PASS`, `FAIL`, `NOT RUN`, or `NOT RUN / uncertain`,
  and one sentence of what you observed naming the signal behind it (`text`,
  `headings`, `tab_order`, `unlabelled_controls`, `wider_than_screen`,
  `phone_text_differs`, `focused_after_steps`, or the named screenshot);
- step 7 distinguishing rendered-content observables from phone-width
  geometry (`PASS` only if `wider_than_screen` is `false` and the phone
  screenshot is unclipped; `NOT RUN / uncertain` if `wider_than_screen` is
  `null` and the phone screenshot is clipped; `FAIL` if `wider_than_screen`
  is `true`);
- steps 8–10, real keyboard activation, and the skip link's target and
  focused visibility (step 2) as `NOT RUN` under the viewer with the
  concrete limit (no real keys, no `href` or non-focusable IDs returned,
  no zoom steps, no speech), or the exact words heard if a real screen
  reader was additionally run;
- anything that confused you, even on a step that passed — a "this was
  awkward but I understood it" is a finding worth keeping;
- anything that made you want to give up. That last one is the most valuable
  line on the page.

Put that note in the journal with `say`, and if it is longer than a paragraph,
keep it as a short Markdown file beside the packet rather than as a new
evidence bundle. Then say plainly in the journal which outcome applies:
- **Full try pass:** steps 1–10 all `PASS` in a real browser with real
  keyboard, phone/narrow-screen fit, 200 % zoom and screen reader;
- **Limited rendered-content inspection pass (resident `view` close for
  Milestone 2):** steps 1–6 are all `PASS`, step 7 shows `wider_than_screen`
  not `true` and intact phone-width rendered content
  (`phone_text_differs` `false`, phone screenshot non-blank), and no step anywhere
  is `FAIL`, while unobserved phone geometry (when `null`/clipped) is
  recorded `NOT RUN / uncertain`, the skip link's target and focused
  visibility are recorded `NOT RUN`, and real keyboard activation and
  steps 8–10 are recorded `NOT RUN` (never `PASS`);
- **Failed try:** any step `FAIL` (including any `wider_than_screen: true`);
- **Partial / incomplete:** any of steps 1–6 or step 7 rendered-content
  integrity lacks `PASS`, which leaves Milestone 2 open.

Do not claim phone-width usability, keyboard activation, 200 % zoom or
speech that was not observed.

## What the probe can and cannot do for you

`probe.py` (see `PROBE.md`) is a pre-flight check. It can tell you that the
page declares a language, that no row states its status by colour alone, that
every name points at something that exists, and what a screen reader would
read in document order. Run it before you start; it will save you from
finding a broken page by hand.

It cannot replace the `view` try. It never renders the page, cannot judge
contrast, real focus order, speech, or how a page feels on a phone, and a
transcript of document order is an approximation of a reading order. A probe
that reports nothing is not evidence that a person can read the page, and
the `view` tab order is no more a keyboard witness than the probe is.

## Honest limits

- One try by one person on one setup is evidence **for that setup**. It is not
  a general claim about accessibility, and it is not the house's foundations'
  standard of witness; that standard stays with foundation changes.
- Milestone 2 needs **one** independent non-author try, not many. A second
  try is worth doing only if it tests something different — a different
  packet, or the phone instead of the desktop.
- The try judges the **page**, not the correctness of the diff and not the
  honesty of the exporter. Those are separate questions with separate answers.
- Real keyboard use, 200 % zoom, screen-reader speech and unmeasured phone
  geometry (`wider_than_screen` `null` / clipped phone image) remain
  `NOT RUN` or `NOT RUN / uncertain` under the viewer. If the house later
  wants them witnessed, they need a real browser and screen reader — the
  viewer never supplies them, and this file never pretends otherwise.
