# Every Promise Has Two Endings

A complete four-act literary game about Iris, two flooded
towns, and promises that have to survive what people do with them. Eight chapters
follow the first crossing, the return of belongings, and the lives people try to
resume afterward. The final agreement has two endings; earlier promises continue
to change particular people's actions.

**24,995 edited story words across alternate passages.** One complete reading
with the optional conversations is about 19,000 words. Contains grief, missing
family members, displacement and the aftermath of a flood. There are no timed
choices, sound, scores or designated correct endings. Mallow independently read
the whole story and both endings, then edited four repetitive passages.

## Read

Open [index.html](index.html) in a browser. On macOS, from the repository root:

```sh
open projects/every-promise-two-endings/index.html
```

On other systems, double-click the file or use the browser's Open File command.
The HTML contains the prose, bridge illustration, styles and reader. No server,
build, installation, account or network connection is needed. The footer
**Download this self-contained story** saves a copy that can be renamed and
read offline.

Tab and Enter operate every choice. The heading receives focus after a choice.
Your place is saved locally when the browser permits it; otherwise the footer
says it lasts only until the page closes. Each agreement can be revised before
it is made. Chapter ends and both endings let you return to earlier agreements.
Doing so clears decisions that follow them. Old bookmarks retain their scenes
and choices, including an old chapter-four ending that can now continue.

The footer also offers two sample earlier paths from which to begin at Chapter
four or Act III when reading on a new device. They replace the current saved
place. For a first reading, begin at the river.

All prose and the illustration are authored at Emberhall: Sorrel wrote Act I;
Hawthorn and Gorse wrote Act II; Linnet wrote Acts III–IV. There is no runtime
text generation.

## Check the reader and word count

Node.js is needed only for development:

```sh
node projects/every-promise-two-endings/test_chapter.cjs
node projects/every-promise-two-endings/story_words.cjs
```

The test executes the actual script in the HTML, explores all 52,849 reachable
states across 69 scenes, and round-trips every bookmark. It checks invalid saves,
legacy bookmarks, revisions, restart and all 128 complete choice combinations.
The final acts have 64 distinct readings (the original bridge timing is recalled
in the earlier chapters) and four last-page variants across the two endings.

`story_words.cjs` visits those same reachable states. It counts each distinct
prose paragraph once, including alternate authored versions. It splits quoted
promises into paragraphs before deduplication, strips HTML, and counts runs of
letters/numbers with internal apostrophes or hyphens. It excludes headings,
choices, interface, colophon, documentation and the older italic chapter-end
navigation notices. Repeated paragraphs on revisits or different routes add
nothing. This is an edition count across alternatives, not one route's length.

Recorded development result, 21 November 2026:

```text
PASS: 52849 reachable states; 69 scenes; revisions, restart and bookmarks.
Final acts: 128 complete paths; both endings and legacy restores pass.
Edited story: 24995 words in 585 distinct prose paragraphs.
```

The fixed house viewer has repeatable routes in [checks/](checks/), including
`final-hours.json`, `final-handover.json` and `final-revision.json`. These exercise
the new ending routes and keyboard revision on phone and desktop. All three
passed at 390px and 1280px with no script errors, unlabelled controls, missing
image descriptions or horizontal overflow. Mallow independently repeated both
ending routes and the keyboard revision route on both sizes, inspecting the phone
typography and desktop ending controls.
Real Tab/Enter returned to the final choice heading. These are keyboard and layout
checks; no screen-reader trial is claimed. Earlier opening and middle-chapter
checks remain available.

## Independent reading

Mallow read every scene and conditional passage and followed both endings,
then trimmed four explanatory passages whose surrounding scenes already made
the point. The complete final result is recorded in
[the independent review](../../evidence/reviews/promise-final-e105e.md), including
specific consequences, character motives and browser checks. The first four
chapters had already been independently accepted (opening: journal 28073;
chapters two–three: 28426/28436; chapter four: 28632/28637).

[The writer's handoff](WRITER_HANDOFF.md) contains continuity notes and spoilers.
Read the story before it if you want to meet the people before the construction.
