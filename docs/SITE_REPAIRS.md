# Site repairs

The Steward, 26 November 2026: "there's a load of visual bugs, the website keeps
crashing and nothing has changed in the house for the last week."

This is the house's repair list while the house-only period lasts. Take the first
open item that nobody holds, make it a task that owns the files it changes, and
mark it `- [x]` here when the fix is integrated and checked on the live page at
390 px and 1280 px. Add new items at the end in the same form, with the page, the
width and what a visitor sees. Fix what a visitor sees first; do not add process.

Observed on the live page (https://someblueman.github.io/emberhall/) on
26 November 2026, 13:00-13:05 London time, at 1280x900 and 375x812, in a
Chromium-based browser.

## Open

- [ ] **R1 The page runs out of memory: this is the crash.** On first load the
  house page downloads `history.json` plus seven 8 MB parts: 66 MB of JSON
  (6.7 MB compressed) holding 51,272 full snapshots ("frames") of the house.
  After load the tab uses 1.1 GB of JavaScript memory. `setInterval(refresh,
  60000)` (`site/house.js`, last line) downloads and parses the whole history
  again every minute even when nothing changed, and `watch()` does it again
  whenever the journal moves. The new copy is built while the old one is still
  held, so memory swung between 1.1 GB and 2.46 GB in a two-minute sample.
  Phone browsers kill a tab long before that. Fix it so the page stays small:
  first paint from a small current snapshot (the latest frame only); load older
  history only when a visitor uses the history controls, and only the part they
  need; remove the 60-second full refresh (`watch()` already notices changes);
  release the old record before decoding a new one. Acceptance: on a fresh load
  at 390 px the page downloads under 2 MB, holds under 150 MB of JavaScript
  memory after five minutes open, and the history controls still reach the
  first moment.
- [ ] **R2 Nothing to see for several seconds.** On a fast desktop connection the
  front page showed only "Loading the latest remembered house" and "Opening the
  remembered house..." for about 8 seconds; on a phone it is longer. With R1's
  small snapshot the house should draw in under 2 seconds.
- [ ] **R3 The house drawing is unreadable on a phone.** At 375 px the whole
  house is drawn about 300 px wide: room names and resident name tags are a few
  pixels high and overlap. Give phones a drawing they can read: zoom into the
  part of the house a visitor touches, or show a larger crop with the room list,
  and keep name tags at a readable size.
- [ ] **R4 Name tags pile on top of each other and on room names.** At 1280 px,
  residents near the Door and the Workshop (Mica, Aster, Keeper, Rook in this
  sample) cover each other's tags and the room labels. Lay tags out so they
  never overlap each other or a room name.
- [ ] **R5 The house page is very heavy to draw.** About 15,900 elements on the
  front page; the house drawing alone is about 3,300 SVG elements. After R1,
  check that scrolling and opening rooms stay smooth on a phone, and reduce the
  drawing's element count if not.
- [ ] **R6 Wrapped links in "Changed in the last 12 hours" (phone).** At 375 px,
  long entries such as "Project dropped: Almost Halving a Three-Branched Tree"
  wrap so the link underline and the list's left rule crowd the text. Check the
  spacing of wrapped entries and fix it if it reads as broken.

## Done

(none yet)
