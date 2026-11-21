# Every Promise Has Two Endings

**The weight of morning** is the complete opening chapter of an unfinished
literary game. Iris helps two flooded towns agree how to open their rebuilt
bridge. You can question the people at the table, revise two promises, then
spend the next day with the people who carry them out.

About fifteen minutes, or longer if you linger. Contains grief, a missing
family member and the aftermath of a flood. No timed choices or sound.

## Read

Open [index.html](index.html) in a browser. On macOS, from the repository root:

```sh
open projects/every-promise-two-endings/index.html
```

On other systems, double-click that file or use the browser's Open File command.
The one HTML file contains the prose, illustration, styling and reader. It
needs no server, build, installation, account or network connection. The
footer also downloads a standalone copy that can be renamed and read offline.

Tab and Enter reach every choice. Your place is saved locally when your browser
allows it; otherwise the footer says it lasts only until the page closes. The
two promises can be revised before signing. At the end you can return to that
passage, or start again. There is no score and no designated correct ending.

This is the real first chapter, not a description of the proposed game. The
remaining acts have not been written. All prose and the SVG illustration were
authored for this chapter by Sorrel at Emberhall; there is no runtime model.

## Check the reader

Node.js is needed only for development checks:

```sh
node projects/every-promise-two-endings/test_chapter.cjs
```

The check executes the actual script embedded in the HTML. It explores all
625 reachable states, including different question orders and revisions;
checks all four consequence combinations, round-trip bookmarks, invalid
bookmarks, unavailable choices and restart; and counts the words on complete
readings. It does not judge the writing or simulate a person caring about it.

Recorded development run, 21 November 2026:

```text
PASS: 625 reachable states; 15 scenes; four distinct consequence combinations; revisions, restart and bookmarks.
dawn/chairs: 3279 words including optional conversations
dawn/pages: 3259 words including optional conversations
daylight/chairs: 3317 words including optional conversations
daylight/pages: 3297 words including optional conversations
```

The house's network-refused Chrome viewer opened the final page at true 390-pixel
phone and 1280-pixel desktop widths. Both reported zero script errors, unlabelled
controls, missing image descriptions and horizontal overflow. A 24-step reading
opened all four conversations, revised both promises, signed and reached the end
on both devices. Real Tab/Enter presses began the reading; every scene change
focused its heading. The repeatable interaction steps are in
[checks/reading.json](checks/reading.json).

A second, 20-step route reached the alternate morning and meal, clicked the
download control without script errors, dismissed restart with Escape and with
"Keep my place", then confirmed a restart and used Tab/Enter to begin the fresh
reading. Both devices returned to "What the river leaves" with no errors or
overflow. These steps are in [checks/ending.json](checks/ending.json). The viewer
does not expose the downloaded file, so this observes the download control, not
a separate reopening of the saved copy.

A passing script or headless browser check does not complete the project
milestone. The independent literary reading is still pending.

## Independent first reading

Read the chapter before [the writer's handoff](WRITER_HANDOFF.md), without a
mechanics explanation. Record which person you cared about, if any, and a later
action you could trace to words you chose. Would you revisit a specific exchange
for its people? Say which one, or say no. Report arbitrary consequences,
caricatures, dull passages and points where you wanted to act but could not.
The milestone stops if this is merely a contract checker with dialogue attached.
Do not commission the middle acts until this first reading passes.
