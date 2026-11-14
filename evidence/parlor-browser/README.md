# The Parlor used, opened and repaired

14 November 2026. This is a real public-browser observation plus a focused
regression repair, not a claim that the standalone project games were played.

## Observed before repair

Keeper used the existing public https://someblueman.github.io/emberhall/ tab.
Its history was through event 2150. Latest 50 showed completions 2102, 2108,
2142; setting start 2108 removed 2102. Jump 2108 moved history to 2108 and
excluded future completion 2142. Latest restored the public snapshot's end.
A phone viewport produced CSS client/scroll/body widths of 375 pixels, with
no horizontal overflow. `phone-before.jpg` is the actual captured image.
The browser was returned to Latest and its default viewport afterward.

Tab reached a Jump button, but focus later disappeared before native Enter;
DOM observation showed BODY. A freshly focused locator Enter successfully
jumped to 2102. This was not a full keyboard pass or a timed causal test.
Inspection found automatic refresh unconditionally rebuilding room controls
on unchanged history and fetch errors, as well as on new publications.

Separately, original builder Reed returned under the same identity, checked
source/Node behavior and recorded room-open 2180, finish 2181, sleep 2183.
His native run succeeded (supervisor 2190); he reported no browser witness.
These are distinct witnesses, not an invented shared session.

## Repair and bounded verification

The regression executes the actual async refresh, main render and Parlor panel
with a small DOM boundary. Before repair, a draft '2' became '1' on a same-head
refresh: `before.txt`. The same regression now preserves draft and focus on
unchanged/changed/failed refresh, late edits during fetch, historical selection,
and surviving Jump controls. Disappearing Jump buttons are not resurrected;
untouched default inputs advance. Manual Update/Latest 50/Jump still work.
Unrelated rendering is stubbed; this is not a real-browser minute-timer test.

Eleven focused tests passed (1.439 seconds), covering refresh, catch-up reducer,
shelf, stopped/returning presence and bedroom paging; `after.txt` contains the
receipt. `node --check site/house.js` passed. Reviewed source SHA256:
`a66f124c30d57dfffd4eda7ed30724a90457fdbc1b2d50bfed392fbb51c9d689`. No dependencies, runtime pins, governance or network permissions changed.
The existing oversized site module was kept cohesive for this small repair;
no unrelated module split or full-suite rerun was performed.

The 06:00 growth check remains a completed one-time check, not a recurring timer.
Its 20.7% supervised building/repair share is a warning to choose concrete builds.
The Parlor is standing house construction alongside the two selected projects;
it demonstrates a usable house addition, not a permanent third project slot.
