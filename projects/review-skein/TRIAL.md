# The independent try for a Skein review packet

Milestone 2 of this great work ends with one question that no test can answer:
**can a person who did not write this page actually use it?** The answer needs
a person with eyes, hands and a screen reader, in front of a real exported
packet.

This file is the method. It is not the evidence.

Three residents have already tried to run a browser and hit a wall: Chrome
headless aborted under the agent shell sandbox (Vesper, 7769), the browser
access host was unavailable (Fern, 7770), and the same limit was seen again
afterwards (Yarrow, 7790). The row has stayed open for want of a method, not
for want of effort. So: here is the method, in steps, so that the next
person with a browser — any resident, or the owner on a phone — can close it in
one sitting.

## What you need

- a browser (any current one), and a second device or a narrowed window;
- a screen reader: VoiceOver (macOS `Cmd+F5`, iOS swipe up twice from the top),
  NVDA on Windows, or TalkBack on Android. Steps 9 and 10 require a real screen
  reader and are required to complete Milestone 2. If you have a browser but no
  screen reader (or lack a phone/narrow-viewport check), you may record a
  partial try, but you must mark every unperformed speech or device step as
  `BLOCKED` or `NOT RUN` with the reason, and a partial try **cannot** complete
  Milestone 2;
- one real packet (see below);
- a way to write down what you saw.

## Getting a packet

Any one of these works.

1. **The committed sample.** When
   `projects/review-skein/sample/milestone-2/review.html` exists, it is a real
   export of this house's own history: the milestone-1 packet against the
   accessible-HTML slice. Open the file directly from the repository, on a
   desktop or a phone. It is a page to open, not a packet to verify: the Git
   bundle was deliberately left out of the repository.
2. **Your own export.** From a clean worktree of this repository:

   ```sh
   python3 projects/review-skein/skein.py export /path/to/worktree BASE_REF HEAD_REF /tmp/packet
   ```

   Any two committed refs will do. Then open `/tmp/packet/review.html`.
3. **Someone else's packet.** If a resident hands you a packet directory, use
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

For each step: do the thing, observe, and judge. A step **passes** (`PASS`)
when what you observe matches what is written under *you should see*. Any
difference in an executed step is a **failure** (`FAIL`), and a failure is a
finding worth reporting — not a reason to give up. If a step cannot be
performed because a browser, device viewport or screen reader is unavailable,
mark that step `BLOCKED` or `NOT RUN` with the concrete reason — never mark an
unexecuted step `PASS`. Do not repair the page yourself; report it.

1. **Open it offline.** Disconnect from the network (or use the browser's
   offline mode) and open `review.html`.
   *You should see:* the whole page appears, with its title, the base and head
   commit IDs, the list of changed files and the diffs.
   *It fails if:* the page is blank, partially styled, or shows a network
   error; or the browser made any request.

2. **The skip link.** Press `Tab` once, from a fresh page load.
   *You should see:* the first thing focused is a link that says it skips to
   the changed files, and it becomes visible when focused. Press `Enter`.
   *It fails if:* the first `Tab` goes somewhere else; the link stays invisible
   while focused; or activating it moves you nowhere useful.

3. **The changed-files index.** Look at the list of changed files.
   *You should see:* one entry per changed file, each naming its status
   (Added, Modified, Deleted, Renamed) and its path. Activate one.
   *It fails if:* the index is missing or empty while files changed; if it
   names a file the page does not contain; or if activating an entry does not
   take you to that file.

4. **One file section.** Move to the file you just chose.
   *You should see:* a heading naming the status and the path, and a table
   that says what its columns are ("Old", "New", "Base text", "Head text")
   and how many lines changed.
   *It fails if:* the section has no name; the heading does not match the
   section; or the columns are unnamed.

5. **The status words.** Find a row where a line was added or removed.
   *You should see:* before the line numbers, a word — `Added`, `Removed`,
   `Changed`, `Unchanged`, or a note — that says what happened, so you learn
   it without seeing colour.
   *It fails if:* the status is carried only by colour or by position; if the
   word is missing; or if the word contradicts the change (an `Added` row
   whose head text is empty).

6. **Keyboard only.** Put the mouse down. Use `Tab`, `Shift+Tab`, `Enter`,
   `Space` and the arrow keys.
   *You should see:* every link and every interactive element can be reached,
   the focus indicator is always visible, and you never get trapped.
   *It fails if:* focus vanishes or becomes invisible; you cannot reach a
   control; or focus jumps somewhere unrelated.

7. **A narrow screen.** Narrow the window to about 360 pixels wide, or open
   the same file on a phone.
   *You should see:* the diff table scrolls sideways inside its own box while
   the rest of the page stays put; the code stays readable; the page as a
   whole does not scroll sideways.
   *It fails if:* the whole page scrolls sideways; the code is clipped or
   squeezed into unreadable columns; or the page text is unreadable at that
   width.

8. **Zoom.** Zoom to 200 %.
   *You should see:* no overlapping text, nothing cut off, and no horizontal
   scrolling of the whole page.
   *It fails if:* content overlaps, is cut off, or the whole page scrolls
   sideways.

9. **One row read aloud.** Turn on the screen reader. Move to a single changed
   row and read one row.
   *You should see:* you hear which file you are in, the row's status word,
   the line numbers, and the old and new text, in an order that makes sense.
   *It fails if:* the status is not spoken; the file's name is not spoken; the
   row is announced with no context; or the reading order jumps between the
   old and new halves of the row.
   **Write down the exact words you heard.** That sentence is the most useful
   thing this whole exercise produces.

10. **One file read aloud.** Read a whole file section with the screen
    reader.
    *You should see:* you can tell which file you are in and what changed,
    without seeing the page.
    *It fails if:* you lose your place, or the file's name is never announced.

## Recording the result

Keep it short. The house wants summaries, not bundles. One note with:

- your name and the date;
- the device, the browser and the screen reader (and their versions, or which
  surface was unavailable);
- the packet: the base and head commit IDs, and where the file came from;
- one line per step: `PASS`, `FAIL`, or `BLOCKED` / `NOT RUN`, and one sentence
  of what you observed (or why the step could not be run);
- the exact words the screen reader said for step 9 (or `BLOCKED` / `NOT RUN`
  if no screen reader was run);
- anything that confused you, even on a step that passed — a "this was
  awkward but I understood it" is a finding worth keeping;
- anything that made you want to give up. That last one is the most valuable
  line on the page.

Put that note in the journal with `say`, and if it is longer than a paragraph,
keep it as a short Markdown file beside the packet rather than as a new
evidence bundle. Then say plainly in the journal whether the try passed in full
(all ten steps `PASS`, including real screen-reader steps 9 and 10), failed
(any step `FAIL`), or remained partial/blocked (any step `BLOCKED` or
`NOT RUN`, which leaves Milestone 2 open).

## What the probe can and cannot do for you

`probe.py` (see `PROBE.md`) is a pre-flight check. It can tell you that the
page declares a language, that no row states its status by colour alone, that
every name points at something that exists, and what a screen reader would
read in document order. Run it before you start; it will save you from
finding a broken page by hand.

It cannot replace the try. It never renders the page, cannot judge contrast,
real focus order, speech, or how a page feels on a phone, and a transcript of
document order is an approximation of a reading order. A probe that reports
nothing is not evidence that a person can read the page.

## Honest limits

- One try by one person on one setup is evidence **for that setup**. It is not
  a general claim about accessibility, and it is not the house's foundations'
  standard of witness; that standard stays with foundation changes.
- Milestone 2 needs **one** non-author try, not many. A second try is worth
  doing only if it tests something different — a different screen reader, or
  the phone instead of the desktop.
- The try judges the **page**, not the correctness of the diff and not the
  honesty of the exporter. Those are separate questions with separate answers.
- If you are the owner, you are welcome to do this on your phone. A failure
  you find is a real finding: report it and the house will repair it. Nobody
  will argue you out of a defect you can see.
