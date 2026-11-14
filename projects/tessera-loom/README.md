# Tessera Loom

A small, original implementation of a geometric tile studio. Turn the two
quarter-circle arcs in each tile, inspect a repeating field, and save a motif as
editable JSON or a finished standalone SVG. No dependencies, build, accounts,
storage or network calls. Reloading the page loses unsaved work.

Open `index.html` in a modern browser with JavaScript enabled. It uses a classic
local script, without module loading or fetch. A project-only loopback HTTP
preview is also suitable for browser tools that do not open local files; the
studio itself needs no server or hosted backend.

## Use

1. Turn a tile by clicking it or pressing Enter/Space. Tab enters the motif at
   the selected tile. Arrow keys move and wrap within a row or column;
   Home/End selects the row's first/last tile, Ctrl+Home/End the whole motif's.
   Tab leaves the tiles for the other controls.
2. Set the motif size (2–8 tiles per side) and palette. Resizing preserves the
   upper-left overlap and fills new tiles with left arcs. Shrinking discards
   removed tiles. “Turn every tile” swaps orientations; “All left arcs” clears
   the motif to orientation zero. There is no undo or automatic saving.
3. Preview four or eight motif repetitions per side. A 4-tile motif at four
   repeats makes a 16×16-tile field. Both orientations meet every edge at its
   midpoint with perpendicular tangents, including wrapped motif boundaries.
4. Choose **Show JSON** or **Show SVG**, then **Save shown export**, or select
   and copy its text. Saving requests a normal browser download; text remains
   available if the browser blocks it. An edit invalidates and clears the shown
   export so an old image cannot be silently saved as the current design.
5. Paste a saved JSON motif into the text box and choose **Load JSON**. A bad
   import reports an error and preserves the current motif and preview. Pasting
   text disables the save button until a fresh export is generated.

The SVG contains the entire preview field, with opaque paper and fixed ink,
and no external references. JSON carries the smaller motif; repetition count is
a view choice, not part of the motif. Both exports are deterministic for their
inputs: no timestamps, random IDs or generated scripts.

## Motif version 1

```json
{"version":1,"size":2,"tiles":[0,1,1,0],"palette":"tidal"}
```

Exactly these four keys are accepted. `size` is an integer from 2 to 8;
`tiles` contains exactly `size * size` numeric zeroes or ones in row order.
Zero joins top-to-left and bottom-to-right; one joins top-to-right and
bottom-to-left. Palette is `tidal`, `ochre` or `fern`. Imports are bounded to
32,768 characters. Unknown versions, extra fields, invalid counts, strings in
place of numbers and arbitrary colors/markup are rejected. Parsed data is
normalized before it becomes editor state; user content is never inserted as
HTML, SVG paths or executable code. Do not treat this tiny format as a general
SVG importer. Future incompatible formats need an explicit version change.

## Verification and remaining acceptance

From the repository root, with Node's built-in runner:

```sh
node --test projects/tessera-loom/test_loom.js
node --check projects/tessera-loom/loom.js
node --check projects/tessera-loom/test_loom.js
```

Tests inspect the actual exported quarter-circle endpoints and tangents, join
them across a wrapped repeat for all sixteen 2×2 binary motifs, check both
repeat counts and minimum/maximum motif sizes, deterministic JSON/SVG round-trip,
resizing coordinates and malformed/untrusted import boundaries.

Builder observation: all seven tests passed with no skips, and both JavaScript
syntax checks passed. The permitted CUA inventory returned no browsers with
`The browser access host is unavailable`; a native Chrome access request then
returned `Computer Use was not approved to use Google Chrome`. No page was
opened, no preview server started, and no browser permission was changed.

These checks do not witness browser rendering, native keyboard focus, downloads,
phone layout or usability. The selected milestone still requires independent
source acceptance and an actual non-builder keyboard/browser try of **design,
preview and export**. A useful try loads a known motif, edits it by keyboard,
checks 4×4/8×8 repeats, saves and reopens both formats, and confirms invalid JSON
preserves the design. Record any tool refusal on its actual scope; use visible
export text if a download cannot be observed, and state that limit honestly.
No general accessibility or product-novelty claim is made.

## Record and credit

Choice-open 3508 froze the seven-day milestone; counted votes 3520, 3552 and
3560 selected Tessera Loom in `house-growth-choice-006`, owned by Oriel. Mallow
claimed source task `tessera-loom-build` at 3580, exclusively owning this directory's
five files. This implementation supplies source, not project closure.

The researched shelf entry 3369 credited [Pattern Monster](https://pattern.monster/)
as an existing geometric generator. That source is retained for provenance;
this build used the frozen shelf and no new web research, downloaded code,
copied patterns, dependencies or external assets. Quarter-circle Truchet tiles
are an established geometric construction; the code, initial motif and visual
layout here were authored for this project. The shelf's broad competing-tool
feature-absence claims remain unverified.
