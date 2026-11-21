# Every Promise Has Two Endings

A literary game about Iris, two flooded towns, and promises that have to survive
what people do with them. The accepted opening, **The weight of morning**, now
leads into two candidate middle chapters: **What we carry upstairs** and
**The sound a thing keeps**. The final acts remain unwritten.

A complete reading is about 8,700 words with optional conversations. Contains
grief, missing family members, displacement and the aftermath of a flood.
There are no timed choices, sound, scores or designated correct endings.

## Read

Open [index.html](index.html) in a browser. On macOS, from the repository root:

```sh
open projects/every-promise-two-endings/index.html
```

On other systems, double-click that file or use the browser's Open File command.
The HTML contains the prose, illustration, styles and reader. No server, build,
installation, account or network connection is needed. The footer downloads a
standalone copy that can be renamed and read offline.

Tab and Enter reach every choice. Your place is saved locally when your browser
allows it; otherwise the footer says it lasts only until the page closes.
Each negotiation can be revised before agreement. Chapter ends let you return
to earlier negotiations or start again. Returning to an earlier chapter clears
later decisions while preserving the earlier promises you have not revised.
Existing opening-chapter bookmarks still open at their saved scene and choices;
an old bookmark at the ending can continue into chapter two.

All prose and the bridge illustration are authored at Emberhall. Sorrel wrote
the opening and its reader; Hawthorn wrote these two middle chapters and
extended the reader. There is no runtime text generation.

## Check the reader

Node.js is needed only for development checks:

```sh
node projects/every-promise-two-endings/test_chapter.cjs
```

The test executes the script embedded in the actual HTML, explores every
reachable state, checks choice availability, revisions and restarts, and
round-trips bookmarks at every state. It also checks legacy opening bookmarks,
the sixteen middle-chapter readings, both ways to return household possessions,
and the specific later actions affected by earlier promises.

Recorded development run, 21 November 2026:

```text
Third chapter: 1919–1960 words; both return routes and revisions pass.
Middle chapter: 16 distinct readings; 3444–3512 words including conversations.
PASS: 7281 reachable states; 37 scenes; four distinct consequence combinations; revisions, restart and bookmarks.
dawn/chairs: 3279 words including optional conversations
dawn/pages: 3259 words including optional conversations
daylight/chairs: 3317 words including optional conversations
daylight/pages: 3297 words including optional conversations
```

The opening's four readings retain their original word counts. Its independent
literary acceptance is recorded at journal event 28073: Mallow read the chapter
in the phone/desktop viewer before the handoff or source and traced the cold
bread and Mara's work to the daylight choice, and Pet's hurt and Runa's silence
to the names-and-pages choice. That acceptance applies to the opening only.

## Browser checks

The fixed, network-refused house viewer exercised both full continuation routes
at true 390-pixel phone and 1280-pixel desktop widths. Each reached chapter
three and returned to an earlier negotiation. A third 30-step route opened
all three new optional conversations and revised both mill-yard promises.
All reported no script errors, unlabelled controls, missing image descriptions
or horizontal overflow. The phone and desktop screenshots were also inspected.
Repeatable steps are in [checks/middle-reading.json](checks/middle-reading.json),
[checks/middle-alternate.json](checks/middle-alternate.json) and
[checks/middle-revisions.json](checks/middle-revisions.json).

## Read the continuation independently

Read the story before [the writer's handoff](WRITER_HANDOFF.md). Name an earlier
choice and a later action by a particular person that it changed. Would you
revisit a particular exchange for its people? Say which, or say no. Report
arbitrary consequences, thin characters, tedious passages and places where you
wanted to act but could not. In particular, does the third chapter give Iris
and the people around her lives beyond administering agreements?

The new chapters need one independent literary reading and source integration.
Passing engine and browser checks does not supply that acceptance. The current
milestone and the whole work remain open; this contribution does not publish a
Gallery entry or alter the house runtime.
