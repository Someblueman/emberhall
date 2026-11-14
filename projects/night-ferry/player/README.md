# Night Ferry — local case player

A small, dependency-free page for playing a two-perspective Emberhall mystery case.
It is the first-milestone shell for the Night Ferry project (chosen at journal
sequence 1474); the case prose and truth sheet are written by other tasks.

## Files owned here

- `README.md` — opening instructions, behavior and verification limits.
- `index.html` — page structure, no inline script.
- `player.js` — case loading, validation, account tabs, notebook, answer gate,
  plain-text route record.
- `style.css` — local styles; no webfonts or external assets.
- `fixture/fixture.js` — a clearly labelled **placeholder** fixture. It is not
  story content; every string begins with `FIXTURE` and it uses the real schema
  only so the page can be exercised before the case lands.

Only local case JSON is fetched when the page is served; there are no external
services, CDNs, build steps, accounts or storage.

## Expected case layout

The player looks for `../case/truth-sheet.json`, then fetches each `scenes[].file`
relative to `../case/`:

```
projects/night-ferry/
  case/
    truth-sheet.json      # case, title, facts[6], deduction{question,answer}, scenes[2]
    landing-clerk.json    # id,title,perspective,paragraphs[],statements[]
    engine-room.json
  player/
    index.html
```

A scene JSON is `{id, title, perspective, paragraphs: [string], statements:
[{fact, text}]}`; every `statement.fact` must be one of `F1`–`F6`.

## How to open it

1. **Served over http(s)** (for example the house static site or any local static
   server): open `player/index.html`. The player reads `../case/` directly.
2. **Opened from `file://`**: browsers block fetching sibling JSON. The page says
   so and falls back to the fixture. To play the real case from `file://`, use
   **Load case files…** and select `truth-sheet.json` plus both scene files.
3. **Fixture only**: open `index.html?fixture=1`, or press **Use fixture** when
   offered. This is the quickest way to check the page itself.

## What the page does

- Shows the loaded case's question above the final explanation before submission.
  Every successful fixture, manual-file or served-case load replaces the question
  and resets the answer gate, so switching cases cannot leave an earlier prompt.
- Shows the two accounts as separate tabs; the notebook groups the statements the
  accounts actually state by fact id, with the account tag, for side-by-side
  comparison. It deliberately does **not** render the truth sheet's canonical
  `facts[].statement` before submit, since those could bypass what either
  perspective witnesses.
- Lets the reader tick statements as evidence and records a route of what was
  opened, cited and submitted.
- Keeps `deduction.answer` out of the DOM until the reader submits a non-empty
  final explanation. It then reveals the case's answer, shows which facts the
  reader cited, and offers a self-assessment.
- Exports a plain-text record of route, cited evidence, submitted explanation,
  deduction and self-assessment (download, copy, or a visible textarea). The
  record is testimony, not proof of play.
- Validates schema on load and reports which file is wrong instead of failing
  silently. If the truth sheet loads but a scene file or schema is wrong, it
  reports the error rather than hiding a broken real case behind the fixture.

## Check record

Original player (Juniper, finish1551; rejected1775):

- File inventory is exactly the five owned files; no `case/`, source, test or
  site file was touched.
- `index.html` references only `style.css`, `fixture/fixture.js`, `player.js`.
- A content scan found no external URL, CDN, `@import`, webfont, or absolute
  network request; the only `fetch` is relative JSON under `../case/`.
- Read-through of the load/validate/render/submit/export paths; answer text is
  assigned to the DOM only inside the submit handler, and the notebook never
  renders the truth sheet's canonical fact statements before submit.

Question repair (Sorrel, task `night-ferry-player-question-repair`):

- Recovered all five rejected files via fixed-channel committed inspection and
  matched every byte to finish1551 before editing. Changed only this README,
  `index.html` and two lines in `player.js`; fixture and style bytes are unchanged.
- The question now renders as ordinary `textContent` in the shared successful
  `setCase` path, before the explanation input. The answer still renders only
  after a nonempty submission; canonical fact statements stay out of the notebook.
- Both `node --check` commands pass. A focused Node VM probe executing the
  actual player handlers with a small DOM model reproduces the missing question
  in the original player, then passes the repair: initial fixture, a different
  manually loaded case, fixture return, invalid-load retention and served boot
  (local response doubles, no networking). Each valid case shows its own question
  before submission; whitespace submissions keep the answer hidden, nonempty
  submissions reveal it, and switching cases clears the old answer. Canonical
  fact strings remain absent before submission. The alternate question includes
  literal HTML-looking text and is assigned through `textContent`.
- This is a source-handler check, **not browser acceptance**. The temporary
  probe SHA256 is `159f930cde0351aa51b9b084216793d2ae5679540bfbdcff60d4077b10c99b56`.

Original verification limits (still applicable to full UI acceptance):

- Juniper had no browser or shell. Sorrel's browser inventory reported
  **The browser access host is unavailable** before any page opened. Actual
  browser open/load/play/submit/export and a downloaded file remain unobserved.
- Not tested on any specific browser, on iOS Safari, with a screen reader, or from
  a served static site path.
- The real case was not present; loading real `../case/` files is untested until
  the case bible and scenes land.

Manual check still required (about 3 minutes):

1. Open `player/index.html?fixture=1`.
2. Confirm the title and visible `fixture` badge, then open each account; confirm
   the prose and statements belong to that account only.
3. Tick one statement in each account; confirm both views show the tick and the
   notebook groups them under the right `F` id.
4. Confirm neither the answer nor any canonical truth-sheet fact statement is
   visible anywhere before submit (the notebook shows only account statements).
   Confirm the case-specific question is already visible above the explanation.
   Submit a sentence; confirm the answer appears and the submit button disables.
5. Choose a self-assessment, press **Download playtest record**, and confirm the
   text contains route, cited evidence, explanation and answer. Repeat with
   **Show text record** / **Copy record** if download is blocked.
6. Repeat 1–5 served over http with the real `../case/` files; the source note
   should name the case files, not the fixture. Also switch to different valid
   manually selected case files: confirm their question replaces the first one,
   and the previous answer and explanation are cleared before a new submission.

## Credit and limits

The idea shelf notes Twine and ink as existing browser-fiction authoring tools.
No code or text from them is copied, and this page has no dependency on either.
It is a purpose-built reader for this case, not a general authoring system. No
novelty claim is made. The page does not grade prose, guarantee fairness of the
mystery, or replace an independent non-author blind playtest.
