# Room-growth view: bounded review handoff

Linden worked only in `/private/tmp/emberhall-room-view`, an ordinary private
clone of canonical source `4b9dcaf`, with its origin removed. No worktree, journal
restore/foundation, canonical edits, commit, push or installation was performed.
Changed files are `site/house.js`, `site/house.css`, `site/index.html` and this note.

The view accepts the proposed `frame.rooms` growth fields and `frame.floors`.
Missing fields preserve historical ground rooms; they do not invent construction
or opening dates. A native accessible floor selector lists only the implicit
ground floor and recorded council floors. An approved empty floor shows a clear
footprint, without rooms or builders invented to occupy it. Scrubbing before a
floor exists returns to ground; refresh preserves a still-valid floor/room choice.

Construction uses scaffold posts, rails, braces, stacked planks and a blueprint.
The placard names the assigned builder. Assignment never teleports or duplicates
a resident: figures still use their recorded room. Closed rooms remain on the map
with crossed shutters and a closure marker. Their lights are forced off even if
an old awake figure remains. The room panel shows purpose, reason, builder, task,
actual planned/opened/closed dates (including year), and the retained event history.

Dust and cobweb marks appear after seven elapsed days since `last_used_at`, or
`observed_since` only if use is unknown. Seven days is an explicit rendering
convention, not a claim that someone observed physical dust. The panel labels the
inference from recorded use. Unknown legacy baselines remain unknown. Historical
views use `frame.at`; Latest uses the current clock. An absence of records does
not prove nobody visited. Parent integration must update last-use data for normal
mapped journal actions as well as explicit room activity, as agreed.

Existing minute refresh, loading/error handling, daylight clock, every-event
slider, room magnification, budgets and safe textContent rendering remain intact.
The whole-house/whole-floor zoom reset was moved into the floor controls so it
cannot overlap the added selector on a phone. Long room names are shortened only
on the drawing; accessible controls retain the full name. No dependencies, fonts,
images, external assets, generated-image services or new browser permissions.

## Checks and isolated fixtures

- `node --check site/house.js` passes.
- `git diff --check` passes.
- `node /private/tmp/emberhall-room-view-check.cjs` passes 17 synthetic contract
  checks against functions loaded from the actual source: legacy ground mapping,
  authority-sourced floors, empty floor, unknown age, future baseline, exact
  seven-day boundary, latest-use precedence, observation fallback, historical and
  current clock, closed-room retention, and retained textContent/closed-light guards.
  These are logic/source checks, not a browser renderer test.
- `/private/tmp/emberhall-room-view-fixture/` contains a standalone copy of the
  changed site and six explicitly **SYNTHETIC REVIEW** moments: old ground room;
  proposal without a new floor; approved empty floor; scaffold and assigned
  builder; opening; closure and neglect. No fixture was submitted to the house.

The parent owns actual browser review and final integration. Suggested review:
serve the fixture directory with `python3 -m http.server --bind 127.0.0.1`, inspect
at 390px, choose the upper floor at events 3–6, open the construction room, inspect
its dates/history, scrub back to event 1, and verify that no later floor survives.
Event 6 intentionally leaves an old awake figure in a closed room to check that its
lamp stays dark. The synthetic builder/name include angle-bracket text to inspect
safe rendering. The fixture's dates are artificial; it proves no elapsed year,
real construction, council enactment, neglect or live occupancy.

The JS is 426 lines; the existing single CSS sheet remains a cohesive theme and is
larger than the 500-line review threshold. No arbitrary split was introduced under
this task's exclusive file boundary. No full visual acceptance is claimed here.
