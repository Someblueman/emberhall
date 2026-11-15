"""Run the shipped Shadow Theatre JavaScript, not just the Python mirror.

The exhibit's browser code lives in projects/shadow-theatre/. This module runs
that exact code under node:

* ``node --check`` on both shipped scripts, so a syntax error in the DOM glue
  cannot hide behind the model tests;
* a small DOM-free harness that requires ``scene-core.js`` and exercises the
  projection, interval union, full challenge validation, the atomic import
  boundary and the export boundary;
* a static wiring check that the page loads ``scene-core.js`` before
  ``app.js`` and that the UI uses the tested import/export functions instead of
  assigning a parsed object straight into state.

The harness is written to a temporary directory at run time so the repository
keeps only the two shipped scripts plus this test.

Run:
    python3 -m unittest tests/test_shadow_theatre_js.py -v

If ``node`` is not installed the tests skip with an explicit reason rather than
silently passing.
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "projects" / "shadow-theatre"
CORE = PROJECT / "scene-core.js"
APP = PROJECT / "app.js"
PAGE = PROJECT / "index.html"
NODE_TIMEOUT = 180


HARNESS = r'''
"use strict";

const core = require(process.argv[2]);

let checks = 0;
let failures = 0;

function pass(name) {
  checks += 1;
  console.log("ok " + checks + " - " + name);
}

function fail(name, detail) {
  checks += 1;
  failures += 1;
  console.log("not ok " + checks + " - " + name + (detail ? " :: " + detail : ""));
}

function ok(name, condition, detail) {
  if (condition) pass(name);
  else fail(name, detail);
}

function same(name, actual, expected) {
  ok(name, core.deepEqual(actual, expected),
    "actual=" + JSON.stringify(actual) + " expected=" + JSON.stringify(expected));
}

function expectThrow(name, fn, fragment) {
  let message = null;
  try {
    fn();
  } catch (err) {
    message = String(err && err.message ? err.message : err);
  }
  if (message === null) return fail(name, "expected a throw");
  if (fragment && message.indexOf(fragment) === -1) {
    return fail(name, "message " + JSON.stringify(message) + " lacks " + JSON.stringify(fragment));
  }
  pass(name);
}

function expectReject(name, text, fragment) {
  const result = core.applyImport(text);
  if (result.ok) return fail(name, "import was accepted");
  if (result.scene !== null) return fail(name, "a rejected import returned a scene");
  if (fragment && String(result.error).indexOf(fragment) === -1) {
    return fail(name, "error " + JSON.stringify(result.error) + " lacks " + JSON.stringify(fragment));
  }
  pass(name);
}

function challenge() {
  return JSON.parse(JSON.stringify(core.CHALLENGES[0]));
}

function screen() {
  return { x: 100, yMin: 0, yMax: 100 };
}

/* ---------- shipped projection model ---------- */

const eq1 = core.computeShadows({ x: 0, y: 50 }, [{ x: 50, yLow: 40, yHigh: 60 }], screen());
same("analytic endpoint projection", eq1.intervals, [[30, 70]]);
ok("analytic total length 40", eq1.totalLength === 40, "got " + eq1.totalLength);

const overlap = core.computeShadows({ x: 0, y: 50 }, [
  { x: 50, yLow: 35, yHigh: 55 },
  { x: 50, yLow: 45, yHigh: 65 }
], screen());
same("overlapping intervals merge", overlap.intervals, [[20, 80]]);
ok("overlap total length 60", overlap.totalLength === 60, "got " + overlap.totalLength);

const touch = core.computeShadows({ x: 0, y: 50 }, [
  { x: 50, yLow: 35, yHigh: 50 },
  { x: 50, yLow: 50, yHigh: 65 }
], screen());
same("touching intervals merge", touch.intervals, [[20, 80]]);
ok("touching total length 60", touch.totalLength === 60, "got " + touch.totalLength);

const disjoint = core.computeShadows({ x: 0, y: 50 }, [
  { x: 50, yLow: 60, yHigh: 70 },
  { x: 50, yLow: 30, yHigh: 40 }
], screen());
same("disjoint intervals stay separate and sorted", disjoint.intervals, [[10, 30], [70, 90]]);
ok("disjoint total length 40", disjoint.totalLength === 40, "got " + disjoint.totalLength);

const clipped = core.computeShadows({ x: 0, y: 50 }, [
  { x: 50, yLow: 15, yHigh: 35 },
  { x: 50, yLow: 65, yHigh: 90 },
  { x: 50, yLow: 80, yHigh: 95 }
], screen());
same("clipping keeps the visible part and drops the offscreen prop", clipped.intervals, [[0, 20], [80, 100]]);
ok("clipped total length 40", clipped.totalLength === 40, "got " + clipped.totalLength);

const repA = core.computeShadows(
  { x: 10, y: 45 },
  [{ x: 40, yLow: 30, yHigh: 50 }, { x: 70, yLow: 55, yHigh: 75 }],
  screen()
);
const repB = core.computeShadows(
  { x: 10, y: 45 },
  [{ x: 40, yLow: 30, yHigh: 50 }, { x: 70, yLow: 55, yHigh: 75 }],
  screen()
);
same("repeated computation is deterministic", repA, repB);

/* ---------- valid import and lossless export ---------- */

ok("exactly three built-in challenges", core.CHALLENGES.length === 3, "got " + core.CHALLENGES.length);

for (const ch of core.CHALLENGES) {
  const text = core.exportChallenge(ch);
  const imported = core.parseChallenge(text);
  same("lossless import of " + ch.id, imported, ch);
  ok("export of " + ch.id + " round-trips byte for byte",
    core.exportChallenge(imported) === text, "export changed after import");
  ok("imported " + ch.id + " displays cleanly", core.describeScene(imported).ok === true);
}

const withExtra = challenge();
withExtra.solution = { light: { x: 0, y: 50 }, props: [{ x: 40, yLow: 40, yHigh: 60 }] };
const extraImported = core.parseChallenge(core.exportChallenge(withExtra));
same("unknown challenge fields survive a round trip", extraImported, withExtra);

const sandbox = core.parseChallenge(JSON.stringify(core.SANDBOX_DEFAULT));
same("sandbox exports without a target", sandbox.target, []);
ok("sandbox with an empty target is accepted", core.describeScene(sandbox).ok === true);

/* ---------- the recorded defect ---------- */

const current = JSON.parse(JSON.stringify(core.CHALLENGES[1]));
const currentExport = core.exportChallenge(current);
const currentView = core.describeScene(current);
const currentBytes = JSON.stringify(current);

/* Exactly the shape Keeper imported at finish 5436: valid light/screen/props,
 * but the challenge envelope has no id, title, description or target. */
const incomplete = {
  screen: { x: 100, yMin: 0, yMax: 100 },
  light: { x: 0, y: 50 },
  props: []
};
const defect = core.applyImport(JSON.stringify(incomplete));
ok("recorded incomplete-challenge import is rejected", defect.ok === false, "import was accepted");
ok("rejected import returns no scene to assign", defect.scene === null,
  "a rejected import handed back a scene");
ok("rejected import reports the missing field", String(defect.error).indexOf("Missing challenge field") !== -1,
  "error=" + JSON.stringify(defect.error));
ok("rejected import leaves the scene object unchanged", JSON.stringify(current) === currentBytes,
  "scene bytes changed");
ok("rejected import leaves the export unchanged", core.exportChallenge(current) === currentExport,
  "export changed");
same("rejected import leaves the displayed view unchanged", core.describeScene(current), currentView);
ok("rejected import did not blank the title", core.describeScene(current).title === currentView.title);
ok("rejected import leaves the target unchanged",
  JSON.stringify(core.describeScene(current).targetText) === JSON.stringify(currentView.targetText));

/* ---------- import boundary: malformed JSON ---------- */

expectReject("malformed JSON is rejected", "{not valid json", "Invalid challenge JSON");
expectReject("empty import text is rejected", "   ", "requires JSON text");
expectReject("JSON null is rejected", "null", "Challenge must be a JSON object");
expectReject("JSON array is rejected", "[]", "Challenge must be a JSON object");

/* ---------- import boundary: missing fields ---------- */

for (const key of ["id", "title", "description", "screen", "light", "props", "target"]) {
  const broken = challenge();
  delete broken[key];
  expectReject("missing field is rejected: " + key, JSON.stringify(broken), "Missing challenge field: " + key);
}

/* ---------- import boundary: wrong types ---------- */

function rejectType(name, mutate, fragment) {
  const broken = challenge();
  mutate(broken);
  expectReject(name, JSON.stringify(broken), fragment);
}

rejectType("string coordinate is rejected", function (c) { c.light.x = "0"; }, "must be a finite number");
rejectType("null coordinate is rejected", function (c) { c.light.y = null; }, "must be a finite number");
rejectType("numeric title is rejected", function (c) { c.title = 42; }, "title must be a non-empty string");
rejectType("blank title is rejected", function (c) { c.title = "   "; }, "title must be a non-empty string");
rejectType("numeric id is rejected", function (c) { c.id = 7; }, "id must be a non-empty string");
rejectType("numeric description is rejected", function (c) { c.description = 1; }, "description must be a string");
rejectType("screen as array is rejected", function (c) { c.screen = [100, 0, 100]; }, "screen must be an object");
rejectType("light as string is rejected", function (c) { c.light = "0,50"; }, "light must be an object");
rejectType("props as object is rejected", function (c) { c.props = {}; }, "props must be an array");
rejectType("prop as number is rejected", function (c) { c.props = [5]; }, "props[0] must be an object");
rejectType("target as object is rejected", function (c) { c.target = {}; }, "target must be an array");
rejectType("target pair of wrong length is rejected", function (c) { c.target = [[10, 20, 30]]; }, "must be a [start, end] pair");
rejectType("target pair of strings is rejected", function (c) { c.target = [["10", "20"]]; }, "must be a finite number");
rejectType("string tolerance is rejected", function (c) { c.tolerance = "0.5"; }, "tolerance must be a finite number");
rejectType("negative tolerance is rejected", function (c) { c.tolerance = -1; }, "tolerance must be zero or greater");

/* ---------- import boundary: NaN / Infinity ---------- */

expectThrow("JSON overflow to Infinity is rejected", function () {
  core.parseChallenge('{"id":"x","title":"T","description":"d","screen":{"x":100,"yMin":0,"yMax":100},"light":{"x":0,"y":1e999},"props":[],"target":[]}');
}, "finite number");

expectThrow("NaN in an object is rejected", function () {
  const broken = challenge();
  broken.light.x = NaN;
  core.validateChallenge(broken);
}, "finite number");

expectThrow("Infinity in an object is rejected", function () {
  const broken = challenge();
  broken.props[0].yHigh = Infinity;
  core.validateChallenge(broken);
}, "finite number");

expectThrow("non-JSON extras are rejected instead of being silently dropped", function () {
  const broken = challenge();
  broken.solution = { x: undefined };
  core.validateChallenge(broken);
}, "JSON-representable");

/* ---------- import boundary: bounded structure ---------- */

const fourProps = challenge();
fourProps.props = [
  { x: 20, yLow: 40, yHigh: 60 },
  { x: 40, yLow: 40, yHigh: 60 },
  { x: 60, yLow: 40, yHigh: 60 },
  { x: 80, yLow: 40, yHigh: 60 }
];
expectReject("four props are rejected", JSON.stringify(fourProps), "at most 3 props");

const fourTargets = challenge();
fourTargets.target = [[10, 20], [30, 40], [50, 60], [70, 80]];
expectReject("four target intervals are rejected", JSON.stringify(fourTargets), "at most 3 target intervals");

/* ---------- import boundary: out-of-domain coordinates ---------- */

rejectType("light at the screen is rejected", function (c) { c.light.x = 100; }, "Forbidden source position");
rejectType("light beyond the screen is rejected", function (c) { c.light.x = 120; }, "Forbidden source position");
rejectType("prop at the light is rejected", function (c) { c.props[0].x = 0; }, "Forbidden prop position");
rejectType("prop behind the light is rejected", function (c) { c.props[0].x = -20; }, "Forbidden prop position");
rejectType("prop at the screen is rejected", function (c) { c.props[0].x = 100; }, "Forbidden prop position");
rejectType("prop beyond the screen is rejected", function (c) { c.props[0].x = 110; }, "Forbidden prop position");
rejectType("degenerate screen is rejected", function (c) { c.screen.yMin = 50; c.screen.yMax = 50; }, "Degenerate screen");
rejectType("inverted screen is rejected", function (c) { c.screen.yMin = 80; c.screen.yMax = 20; }, "Degenerate screen");
rejectType("zero-length prop is rejected", function (c) { c.props[0].yHigh = c.props[0].yLow; }, "Degenerate segment");
rejectType("inverted prop is rejected", function (c) { c.props[0].yLow = 60; c.props[0].yHigh = 40; }, "Degenerate segment");
rejectType("target above the screen is rejected", function (c) { c.target = [[-30, 20]]; }, "within the screen bounds");
rejectType("target below the screen is rejected", function (c) { c.target = [[70, 130]]; }, "within the screen bounds");
rejectType("target with start >= end is rejected", function (c) { c.target = [[50, 50]]; }, "start < end");
rejectType("unsorted target is rejected", function (c) { c.target = [[60, 70], [10, 20]]; }, "strictly increasing");
rejectType("overlapping target is rejected", function (c) { c.target = [[10, 50], [40, 60]]; }, "strictly increasing");

/* ---------- failed import then export ---------- */

const baseline = JSON.parse(JSON.stringify(core.CHALLENGES[2]));
const beforeExport = core.exportChallenge(baseline);
const beforeView = core.describeScene(baseline);

const bad = core.applyImport(JSON.stringify({ title: "Broken", light: baseline.light, screen: baseline.screen, props: baseline.props }));
ok("import without a target is rejected", bad.ok === false, "import was accepted");
ok("failed import then export is identical", core.exportChallenge(baseline) === beforeExport, "export changed");
same("failed import then displayed view is identical", core.describeScene(baseline), beforeView);
ok("failed-import export still parses", core.deepEqual(JSON.parse(core.exportChallenge(baseline)), baseline));

/* ---------- repeated identical imports ---------- */

const once = core.applyImport(beforeExport);
const twice = core.applyImport(beforeExport);
ok("first repeatable import succeeds", once.ok === true, "rejected");
ok("second repeatable import succeeds", twice.ok === true, "rejected");
same("repeated identical imports agree", once.scene, twice.scene);
ok("repeated identical imports export identically",
  core.exportChallenge(once.scene) === core.exportChallenge(twice.scene), "exports differ");
same("repeated identical imports display identically",
  core.describeScene(once.scene), core.describeScene(twice.scene));

/* ---------- export refuses invalid displayed state ---------- */

const invalidDisplay = challenge();
invalidDisplay.props[0].yHigh = 10;
expectThrow("export refuses an invalid displayed scene", function () {
  core.exportChallenge(invalidDisplay);
}, "Degenerate segment");
ok("invalid displayed scene is reported, not rendered",
  core.describeScene(invalidDisplay).ok === false &&
  core.describeScene(invalidDisplay).intervalText === "Intervals: (invalid scene)");

/* ---------- target matching tolerance ---------- */

ok("target match allows the stated tolerance",
  core.matchesTarget([[25.4, 74.6]], [[25, 75]], 0.5) === true);
ok("target match rejects beyond the stated tolerance",
  core.matchesTarget([[26, 74]], [[25, 75]], 0.5) === false);
ok("target match refuses an empty target",
  core.matchesTarget([[25, 75]], [], 0.5) === false);

console.log("checks=" + checks + " failures=" + failures);
if (failures > 0) {
  console.log("JS-CHECKS-FAIL");
  process.exit(1);
}
console.log("JS-CHECKS-PASS");
'''


def _require_node(testcase):
    node = shutil.which("node")
    if node is None:
        testcase.skipTest(
            "node is not installed; shipped Shadow Theatre JavaScript cannot be executed here"
        )
    return node


def _run(testcase, argv):
    proc = subprocess.run(
        argv,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=NODE_TIMEOUT,
    )
    # Retain the observation in the test output rather than only asserting.
    if proc.stdout:
        print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n", flush=True)
    if proc.stderr:
        print(proc.stderr, end="" if proc.stderr.endswith("\n") else "\n", flush=True)
    return proc


class ShadowTheatreJavaScriptTests(unittest.TestCase):
    def test_shipped_javascript_parses(self):
        node = _require_node(self)
        for path in (CORE, APP):
            with self.subTest(script=path.name):
                proc = _run(self, [node, "--check", str(path)])
                self.assertEqual(
                    proc.returncode,
                    0,
                    msg=f"node --check {path} failed with {proc.returncode}",
                )

    def test_projection_validation_and_import_boundary(self):
        node = _require_node(self)
        for path in (CORE, APP):
            self.assertTrue(path.is_file(), msg=f"missing shipped script {path}")
        with tempfile.TemporaryDirectory() as tmp:
            harness = Path(tmp) / "shadow_theatre_harness.js"
            harness.write_text(HARNESS, encoding="utf-8")
            proc = _run(self, [node, str(harness), str(CORE)])
        self.assertEqual(
            proc.returncode,
            0,
            msg=(
                "shipped JavaScript harness failed with exit "
                f"{proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
            ),
        )
        self.assertIn("JS-CHECKS-PASS", proc.stdout)
        self.assertNotIn("JS-CHECKS-FAIL", proc.stdout)

    def test_page_wires_the_tested_model_before_the_ui(self):
        page = PAGE.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")

        core_tag = '<script src="scene-core.js"></script>'
        app_tag = '<script src="app.js"></script>'
        self.assertIn(core_tag, page)
        self.assertIn(app_tag, page)
        self.assertLess(page.index(core_tag), page.index(app_tag), msg="core must load before the UI glue")

        self.assertIn("window.ShadowCore", app)
        self.assertIn("core.applyImport(", app)
        self.assertIn("core.exportChallenge(", app)
        self.assertIn("core.describeScene(", app)
        # The original defect: a parsed object assigned into state before the
        # envelope was validated.
        self.assertNotIn("state.scene = parsed", app)
        self.assertIn('id="io-message"', page)


if __name__ == "__main__":
    unittest.main()
