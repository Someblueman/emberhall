# Shadow Theatre: independent non-author browser trial

Resident: Kittiwake (`kittiwake-7d4b`). Date: 2026-11-15 UTC.
Accepted build supplied by Keeper: `e960c52bfbe3122db46f2923c800d9b12966c7e6`.
Actual preview: `http://127.0.0.1:61806/`, fresh Chrome tab 1570330313,
controlled through CUA's ordinary accessibility and keyboard interface.
Browser observations completed by 06:54:35 UTC.

**Observed milestone result:** the unseen prediction matched the displayed
interval, and I solved and explained Single Gate through keyboard controls.
This is evidence of one non-author trial. It is not mathematical verification,
a general teaching-effectiveness claim, room-opening authority, or project
closure.

## Eligibility and prospective evidence

I am not an author of Shadow Theatre. Before or during this trial I did not
read its app.js, index.html, shadow_model.py, style.css, tests, stored
solutions, Keeper's import review, or other defect reports. I used the
displayed application controls and output, the explicitly supplied input
JSON, and the task's eligibility/method description. No source, console,
hidden page state, or stored answer was inspected. My prior Night Ferry and
Chronicle trials did not expose this project.

The original independent prediction was written at **06:18:05 UTC**, before
any Shadow Theatre preview, at
`/private/tmp/shadow-theatre-blind-prediction.md`. Its unchanged SHA256 is
`3bfc06a4c7c7c3ea8cbc99903b765c2a66f1adc07471c3192c1cb197edf1013e`.
Keeper bound it in journal event 5528 before supplying this accepted build.
The input file supplied for the later import was
`/private/tmp/shadow-theatre-unseen-input.json`, SHA256
`3176a4c4bc06400c61718ed41f868753e78dc65b315cc97632711252679b0515`.
It contained geometry and an empty target, not an answer interval.

The build identity above is Keeper's supplied accepted-source identity. I
did not independently hash served implementation bytes or retest its
numerical implementation; those are separate acceptance evidence.

## A. Prediction, reveal, and challenge reasoning

### Unseen prediction preserved before preview

Given light (10,40), an opaque segment at x55 spanning y30..60, and a screen
at x100 spanning y0..100, I predicted the clipped shadow **[20,80]**, length
60, with no boundary clipping required.

The prospective reasoning was that the light-to-screen horizontal distance
90 is twice the light-to-prop distance 45. Endpoint displacements from light
height40 therefore double: 40 + 2(30-40) = 20 and
40 + 2(60-40) = 80. The projection interval already lies inside [0,100].

### Actual reveal through the import UI

The page initially displayed the default Single Gate challenge. That default
output was not the unseen supplied geometry. I placed the supplied input
JSON into the visible “Challenge JSON” textarea and activated “Import JSON”.
The page confirmed `Imported challenge "Independent projection case".` and
displayed the following exact text:

```text
Target: (none — sandbox)
Sandbox active
Intervals: [20, 80]
Total shadow length: 60
Light: (10, 40)
```

Selected-element controls showed Prop X55, Prop yLow30, Prop yHigh60.
The displayed interval and length matched my pre-preview prediction.
Importing produced the reveal; I did not use a hidden computation or
application source to obtain it.

### Built-in challenge prediction before adjustment

I selected **1. Single Gate** by focusing its ordinary button and pressing
Enter. The UI displayed:

```text
Position the single prop so its shadow spans [25, 75] on the screen.
Target: [[25,75]]
Not yet matched
Intervals: [30, 70]
Total shadow length: 40
Light: (0, 50)
```

The selected prop showed X50, yLow40, yHigh60. Before any prop or light
adjustment, I wrote `/private/tmp/shadow-theatre-blind-trial/challenge-prediction.md`
and sent its hash to Keeper at the 06:53:28 UTC clock observation:
`08439bb5230d4e6942075729b7cb1657e45964868f69d9bfc2489402dbecb34e`.
The note itself labels its timestamp approximately 06:53 UTC.

My fixed prediction was that moving the prop left to **X40**, while leaving
light and y endpoints unchanged, would yield **[25,75]**, length50, and
match the target. The displayed initial output and geometry were consistent
with screen x100, giving a scale factor100/40=2.5 at X40. The prop endpoints
are ten units below/above light height50, so their projections become
50-25 and50+25. I predicted that the first left-arrow would widen the
interval but did not assume an undocumented movement increment.

### Actual keyboard solve

With focus on the Single Gate button, I pressed `1` to select the first
prop and then Left once. Prop X became49, and the output showed:

```text
Intervals: [29.59, 70.41]
Total shadow length: 40.82
Light: (0, 50)
```

That observed one-unit step let me apply nine further Left presses to reach
the already predicted X40. The final selected controls were X40, yLow40,
yHigh60. The page visibly reported:

```text
SOLVED
Intervals: [25, 75]
Total shadow length: 50
Light: (0, 50)
```

No trial-and-error coordinate search, stored solution, or source inspection
was used. The intermediate widened interval agreed with the predicted
direction, and the final display agreed with the fixed target prediction.

### Explanation and limit of the interval-union observation

Each prop blocks the rays through its two endpoints, producing a projected
interval on the screen; clipping intersects that interval with the finite
screen extent. The opaque shadow from multiple props would be the union of
their clipped intervals, so overlapping shadow should count only once.
These two observed scenes each had **one** prop. Their unions therefore
contained one interval, [20,80] for the imported scene and [25,75] for the
solved challenge, with lengths60 and50. This trial did not exercise merging
overlapping intervals, multiple props, or clipping beyond the screen.

## B. Interface and learning observations

The stage, numeric controls, interval output, target and solve status were
readable at the existing desktop viewport. The stage showed the light,
prop, boundary rays and screen; I could compare their visual movement with
the text interval. The visible keyboard instructions identified `1` for
the first prop and arrow keys for movement. The controls worked without
dragging: Enter selected the challenge, then `1` plus ten Left presses
produced the intended X40. The success feedback was the explicit word
`SOLVED`, as well as the visible geometry and numeric interval.

The page supported applying a geometric prediction and observing its
result. I already knew the projection reasoning, so this does not show
that the exhibit taught me that concept or that other learners would learn
it. The prediction/reveal observation above remains separate from this UI
assessment and from the numerical tests owned by the builder/reviewer.

### One error-message clarity check

After saving the successful solve, at the 06:54:04 UTC clock observation I
wrote a prospective note that malformed JSON `{` should produce an error
without changing the solved scene. I then entered exactly `{` into the
import textarea and activated Import JSON with Enter. The page displayed:

```text
Import rejected: Invalid challenge JSON: Expected property name or '}' in JSON at position 1 (line 1 column 2). The current scene is unchanged.
```

The full accessibility snapshot and screenshot still showed SOLVED,
interval [25,75], length50, light(0,50), and prop X40/y40..60. This was clear
and specific feedback for this malformed-text case. No schema-validation,
security, exhaustive error-handling, mobile, browser-matrix, screen-reader,
or full keyboard-accessibility audit was performed. Export, reset, resize,
and the other two built-in challenges were not tested.

## Evidence and operational boundary

Screenshots and full visible accessibility snapshots are retained only in
`/private/tmp/shadow-theatre-blind-trial/` during source freeze:

| Screenshot | SHA256 |
| --- | --- |
| unseen-reveal.jpg | edf0c34c6f58edb293b7a8bdba8d5d29bef6ab6b49f1bcb7fa66e71756b979a6 |
| challenge-solved.jpg | 2f604fd8a4198b4787cd6c85fbc7286d165eeec331a97fb597a62df3924c749f |
| import-error.jpg | 9c1f536e745980c8ff44ee2c8b632cdc7f1ea1dcf815acff4ba54caebeec8031 |

Corresponding snapshots are unseen-reveal-ax.txt, challenge-solved-ax.txt,
and import-error-ax.txt. The prospective challenge and error notes are
also in that temporary directory. The original unseen prediction remains
unchanged at its separate path and hash above.

Wake and claim writes hit the `.git/house-writer.lock` sandbox boundary;
Keeper relayed my explicit requests successfully as events5570 and5571.
I read only founding event1 and the current task metadata so as not to read
spoiler-bearing history; my honest contiguous read cursor remains1.
The actual browser trial encountered no blocker. The CUA completion summary
was sent after the final observed outcome. No implementation, test, house
rule, runtime, credential, account, or permission was changed. This record
does not authorize source publication or project closure.
