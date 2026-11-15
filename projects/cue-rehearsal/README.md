# Cue Rehearsal

An offline browser workbench for an authored print-and-make workshop. Compare a
read-only baseline with one cloned rehearsal: edit a duration, release minute,
prerequisite list or resource, and read why each earliest time follows. Resource
availability belongs to each plan, so changing the scenario keeps the baseline.

Open `projects/cue-rehearsal/index.html` in a modern browser. No build, install,
server, internet connection or account is required. The page uses only local
scripts and CSS; its CSP disables network connections. There is no journal
connection. The working copy lives in memory. Export before closing or reloading;
a reload starts the example again. Exporting to text does not save a file until
you copy it somewhere; the separate download button requests a JSON file.

## Try it

1. Read the baseline and its explanations. Room preparation and paper preparation
   run in parallel; welcoming the group waits for both.
2. Choose a step, edit its fields, and click **Apply to scenario**. Blank
   prerequisites mean an independent start; otherwise use comma-separated IDs.
   Uncheck a scenario resource to explore an unavailable resource. A resource ID
   absent from the resource list is reported as unknown and blocks its step.
3. Compare both plans and the per-ID start/finish changes. Cycles, missing IDs,
   blocked steps and resource overlaps appear beside the affected plan.
4. **Export JSON to text** includes both plans. **Import JSON from text** replaces
   both only after validating the entire document. A rejected import leaves the
   working project and displayed explanations intact; its diagnostic persists
   through ordinary edits until another transfer action. Text in the transfer
   box is a draft, independent of the displayed project.
5. **Reset scenario from baseline** deliberately replaces the scenario with a
   fresh clone. Export first if you want to retain an earlier rehearsal.

The baseline is read-only through the editing controls. Import can replace the
entire document, including the baseline. The editor modifies existing steps;
adding/removing steps, changing their labels/tracks or changing resource names
uses JSON import. No implicit saving, undo stack, extra scenarios or resource
optimizer is present.

## Time and resource semantics

Times are integer minutes relative to a named origin, not dates. Negative release
minutes mean preparation before minute zero. Duration is a strictly positive
integer. For every unblocked step:

```
start = max(release, finish of each prerequisite)
finish = start + duration
```

This is a pure precedence calculation. The graph is traversed by ID, independent
of input array order. A strongly connected component of two or more steps, or a
self-prerequisite, is a cycle. Its members get no interval. A missing prerequisite,
unknown resource or explicitly unavailable resource also gives no interval.
Blocking propagates through prerequisites; unrelated tracks continue. Cyclic
members report their cycle and direct missing/resource faults; downstream steps
name their blocked prerequisites. Overall finish is unresolved if any step is
blocked. The formula shown for each unblocked step includes every prerequisite
finish and the release, so ties and slack are visible.

Each step needs exactly one resource ID. A resource represents one exclusive
person, team, place or piece of equipment; it has a name and a boolean availability
flag. Intervals are **half-open `[start, finish)`**. Two unblocked steps assigned
to the same resource conflict if their intervals overlap by a positive number of
minutes. Touching endpoints are allowed. Each conflicting pair and the exact
intersection are reported, even within the same track. Resources do not delay,
serialize or reorder steps. A conflicting plan still shows its precedence-only
finish, which is not a feasible resource-constrained completion promise.

## JSON v1

`example.json` is the exact initial project. The complete document has exactly
`version` (1), `title`, `origin`, `baseline`, `scenario`. Each plan has exactly
`name`, `resources`, `steps`:

```json
{
  "name": "Small example",
  "resources": [{"id": "crew", "name": "Room crew", "available": true}],
  "steps": [{
    "id": "unlock", "label": "Unlock the room", "track": "Room",
    "release": 0, "duration": 5, "prerequisites": [], "resource": "crew"
  }]
}
```

IDs start with a lowercase ASCII letter, followed by lowercase letters, digits or
hyphens, up to 40 characters. Step IDs and resource IDs are unique within their
own plan. Prerequisites are unique IDs; references to missing steps and unknown
resources are structurally valid so the model can explain them. Labels, names,
title and origin are nonblank strings of at most 120 characters, with no ASCII
control characters; tracks have at most 40. Bounds per plan: 1–80 steps, 1–30
resources, 0–80 prerequisites per step, release −1000000…1000000, duration
1…1000000. Booleans, strings, fractions and infinite numbers are not integer
minutes. Unknown fields, duplicate IDs, invalid fields, unsupported versions,
invalid JSON, and sparse arrays at the JavaScript boundary are rejected.

Input and formatted export are each limited to 200000 JavaScript characters.
Validation enforces the formatted bound before accepting a compact import, so
an accepted document can always be exported. JSON is parsed as data, never
executed; user text reaches the DOM through `textContent`, never HTML. The
transfer text and browser download are not authenticated backups. No filesystem
writes happen from the calculation.

## Checks and evidence limits

From the repository root:

```sh
node --test projects/cue-rehearsal/model.test.js
python3 -m unittest discover -s projects/cue-rehearsal -v
node --check projects/cue-rehearsal/model.js
node --check projects/cue-rehearsal/app.js
node --check projects/cue-rehearsal/model.test.js
python3 -c 'import ast; ast.parse(open("projects/cue-rehearsal/test_project.py").read())'
python3 -m json.tool projects/cue-rehearsal/example.json > /dev/null
git diff --check -- projects/cue-rehearsal
```

`model.js` is the sole calculation and import/edit implementation. The browser
loads it before `app.js`; the Node tests require those same source bytes. The
small Python unittest launcher invokes the Node suite so the house's existing
project gate actually runs it. Missing Node is an explicit skip. Static wiring
checks do not establish DOM behavior.

The builder executed the commands above successfully (exit 0): 11 Node cases,
2 Python cases (the Node suite is rerun by one of them), JavaScript/Python/JSON
syntax and whitespace checks. The hand-derived baseline is unlock 0–5,
tables 5–15, projector 5–13, room-ready 15–19; print 0–6, pack 6–13;
welcome 19–22. Tests also check a delayed branch, slack, release control,
independent-track stability, cycle/downstream distinction, missing references,
resource blocks, endpoint/containment/identical/partial conflicts, order
invariance, maximum admitted chain, clone retention and atomic malformed import.
These are numerical and data-boundary observations.

**No actual browser interaction or visual-quality check was available to this
builder.** Computer Use inventory reported “The browser access host is
unavailable”; requesting native Chrome returned “Computer Use was not approved
to use Google Chrome”. No replacement browser automation or permission bypass
was used. Download behavior, DOM import preservation, keyboard use and the
rendered layout still need an actual browser witness. Unit tests and static
inspection do not substitute for that observation.

## Independent trial still required

An eligible non-author must record a prediction of a changed case **before**
applying it or revealing the result, then actually use the accepted browser page
to edit, export, reimport and check its explanation and retention of both plans.
The public baseline UI and this README are allowed entry material. Choose a new
specific duration or resource change; do not use a changed case whose results
you have read in source tests/review. The builder and source/test reviewers who
saw those answers cannot provide the blind trial. Record initial exposure and
keep the pre-reveal prediction separate from numerical correctness checks.
The separately queued trial task remains blocked until independent source
acceptance and a loadable exact page; the owner assesses eventual closure.

No claim of scheduling efficacy, actual-event readiness, resource optimization
or broad usability follows from this build. There is no live clock, time zone,
show control, notification, multi-user sync, network access or external action.
