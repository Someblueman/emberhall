# Shadow Theatre first-build review

Keeper extracted the six immutable finish5388 artifacts into a temporary directory. Only the exact three browser files were served on an ephemeral loopback port; the Python model with solutions, tests and private journal were not served. An existing unrelated server occupied8768 and was left untouched; the actual experiment used60367.

## Actual browser failure, 15 November06:08 UTC

1. Open the submitted page: Single Gate, interval[30,70], one prop and target[25,75]. Export JSON to observe the current complete challenge.
2. Import the physically valid but incomplete challenge recorded in build-5388.json: light/screen/empty props, missing required challenge fields.
3. The title/description disappear, the selector switches to Sandbox, but the old prop drawing, old interval and old target remain. Browser console records TypeError reading target.length at app.js180, from the import catch render at373.
4. Export JSON again: it contains the incomplete imported object, proving previous scene state was replaced despite the failed render. No visible import diagnostic appears.

[Observed broken view](import-failure.jpg). The error and exact asset hashes are in [the receipt](build-5388.json). This is a witnessed product defect, not a hypothetical concern or a blind-player result. Keeper has read the source/answers and must not be the independent prediction witness.

The ten submitted tests import shadow_model.py. The browser executes a second implementation in app.js; the tests do not exercise its import validation, error rendering or state replacement. The two implementations already differ: Python validates the challenge envelope; JavaScript validates only its physical scene.

Repair before acceptance: validate the complete imported challenge before committing state, preserve the previous scene on rejection, show a durable visible error, and test the actual browser JavaScript projection and JSON round-trip boundary. Prefer one implementation used by the browser and tests instead of maintaining an unused Python mirror. Retain original artifacts and provenance. No project closure, source integration or broad playability claim is made here.
