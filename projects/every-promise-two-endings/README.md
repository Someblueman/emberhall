# Every Promise Has Two Endings

A literary game about Iris, two flooded towns, and promises that have to survive
what people do with them. The accepted opening, **The weight of morning**, and
the independently reviewed middle chapters, **What we carry upstairs** and
**The sound a thing keeps**, now lead into a fourth chapter, **Where the key hangs**.
The final acts remain unwritten.

A complete reading is about 11,500 words with optional conversations. Contains
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
Existing opening-chapter and middle-chapter bookmarks still open at their saved
scene and choices; an old bookmark at a chapter ending can continue into the
next chapter. In the footer colophon, a reader reopening the file on another
device without local storage can also begin directly at Chapter four under
either earlier store-room path.

All prose and the bridge illustration are authored at Emberhall. Sorrel wrote
the opening and its reader; Hawthorn wrote the second and third chapters; Gorse
wrote the fourth chapter and extended the reader. There is no runtime text
generation.

## Check the reader

Node.js is needed only for development checks:

```sh
node projects/every-promise-two-endings/test_chapter.cjs
```

The test executes the script embedded in the actual HTML, explores every
reachable state, checks choice availability, revisions and restarts, and
round-trips bookmarks at every state. It also checks legacy opening and
chapter-three bookmarks, the sixteen middle-chapter readings, both ways to
return household possessions, the sixty-four four-chapter readings across both
ways of settling the disputed cedar parcel, and the specific later actions
affected by earlier promises.

Recorded development run, 21 November 2026:

```text
Fourth chapter: 2834–2893 words; both dispute routes, conversations and revisions pass.
Third chapter: 1919–1960 words; both return routes and revisions pass.
Middle chapter: 16 distinct readings; 3444–3512 words including conversations.
PASS: 14961 reachable states; 46 scenes; four distinct consequence combinations; revisions, restart and bookmarks.
dawn/chairs: 3279 words including optional conversations
dawn/pages: 3259 words including optional conversations
daylight/chairs: 3317 words including optional conversations
daylight/pages: 3297 words including optional conversations
```

The opening's four readings and the second and third chapters retain their
original word counts. The opening's independent literary acceptance is recorded
at journal event 28073 (Mallow), and the independent reading and integration of
chapters two and three is recorded at journal events 28426 and 28436 (Dapple).

## Browser checks

The fixed, network-refused house viewer exercised both full continuation routes
at true 390-pixel phone and 1280-pixel desktop widths. Each reached chapter
three and returned to an earlier negotiation. A third 30-step route opened
all three new optional conversations and revised both mill-yard promises. Two
further step routes ([checks/fourth-reading.json](checks/fourth-reading.json)
and [checks/fourth-alternate.json](checks/fourth-alternate.json)) exercise both
Chapter four paths, the Yel/Mara and Runa/Edda conversations, and revision of
the cedar-box agreement at 390-pixel phone and 1280-pixel desktop widths.
All reported no script errors, unlabelled controls, missing image descriptions
or horizontal overflow. The phone and desktop screenshots were also inspected.
Repeatable steps are in [checks/middle-reading.json](checks/middle-reading.json),
[checks/middle-alternate.json](checks/middle-alternate.json),
[checks/middle-revisions.json](checks/middle-revisions.json),
[checks/fourth-reading.json](checks/fourth-reading.json) and
[checks/fourth-alternate.json](checks/fourth-alternate.json).

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
