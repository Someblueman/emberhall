/*
 * Shadow Theatre shared model.
 *
 * This file holds every rule the exhibit depends on: the finite-screen
 * projection, the interval union, target matching, challenge validation and
 * the import/export boundary. It is plain JavaScript with no DOM access, so
 * the same bytes run in the browser page (as a classic script that assigns
 * globalThis.ShadowCore) and under `node` (as a CommonJS module).
 *
 * app.js is only the DOM glue; tests/test_shadow_theatre_js.py runs this file.
 */
(function (root, factory) {
  "use strict";
  var api = factory();
  if (typeof module === "object" && module !== null && module.exports) {
    module.exports = api;
  }
  root.ShadowCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  var MAX_PROPS = 3;
  var DEFAULT_TOLERANCE = 0.5;

  var CHALLENGES = [
    {
      id: "single-gate",
      title: "1. Single Gate",
      description: "Position the single prop so its shadow spans [25, 75] on the screen.",
      screen: { x: 100, yMin: 0, yMax: 100 },
      light: { x: 0, y: 50 },
      props: [{ x: 50, yLow: 40, yHigh: 60 }],
      target: [[25, 75]],
      tolerance: 0.5
    },
    {
      id: "twin-pillars",
      title: "2. Twin Pillars, One Shadow",
      description: "Align two props so their shadows touch or overlap into one continuous interval [20, 80].",
      screen: { x: 100, yMin: 0, yMax: 100 },
      light: { x: 0, y: 50 },
      props: [
        { x: 50, yLow: 35, yHigh: 50 },
        { x: 50, yLow: 55, yHigh: 70 }
      ],
      target: [[20, 80]],
      tolerance: 0.5
    },
    {
      id: "clipped-horizon",
      title: "3. Clipped Horizon",
      description: "Use three props\u2014with at least one clipped by the screen edge\u2014to cast [[10, 40], [70, 100]].",
      screen: { x: 100, yMin: 0, yMax: 100 },
      light: { x: 0, y: 50 },
      props: [
        { x: 50, yLow: 30, yHigh: 45 },
        { x: 50, yLow: 60, yHigh: 75 },
        { x: 50, yLow: 75, yHigh: 90 }
      ],
      target: [[10, 40], [70, 100]],
      tolerance: 0.5
    }
  ];

  var SANDBOX_DEFAULT = {
    id: "sandbox",
    title: "Editable Sandbox",
    description: "Freely edit light, up to 3 vertical props, and screen bounds. No target required.",
    screen: { x: 100, yMin: 0, yMax: 100 },
    light: { x: 10, y: 50 },
    props: [{ x: 50, yLow: 35, yHigh: 65 }],
    target: [],
    tolerance: 0.5
  };

  var REQUIRED_FIELDS = ["id", "title", "description", "screen", "light", "props", "target"];

  function isPlainObject(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function hasOwn(obj, key) {
    return Object.prototype.hasOwnProperty.call(obj, key);
  }

  function requireFinite(value, name) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
      throw new Error(name + " must be a finite number");
    }
    return value;
  }

  function cloneJson(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function deepEqual(a, b) {
    if (a === b) return true;
    if (typeof a !== typeof b) return false;
    if (a === null || b === null) return false;
    if (typeof a !== "object") return false;
    if (Array.isArray(a) !== Array.isArray(b)) return false;
    if (Array.isArray(a)) {
      if (a.length !== b.length) return false;
      for (var i = 0; i < a.length; i += 1) {
        if (!deepEqual(a[i], b[i])) return false;
      }
      return true;
    }
    var ka = Object.keys(a);
    var kb = Object.keys(b);
    if (ka.length !== kb.length) return false;
    for (var j = 0; j < ka.length; j += 1) {
      if (!hasOwn(b, ka[j])) return false;
      if (!deepEqual(a[ka[j]], b[ka[j]])) return false;
    }
    return true;
  }

  function validateScene(light, props, screen) {
    if (!isPlainObject(light)) throw new Error("light must be an object");
    if (!isPlainObject(screen)) throw new Error("screen must be an object");
    if (!Array.isArray(props)) throw new Error("props must be an array");

    var sx = requireFinite(screen.x, "screen.x");
    var syMin = requireFinite(screen.yMin, "screen.yMin");
    var syMax = requireFinite(screen.yMax, "screen.yMax");
    if (syMin >= syMax) {
      throw new Error("Degenerate screen: screen.yMin must be strictly less than screen.yMax");
    }

    var lx = requireFinite(light.x, "light.x");
    var ly = requireFinite(light.y, "light.y");
    if (lx >= sx) {
      throw new Error("Forbidden source position: light.x must be strictly less than screen.x");
    }

    if (props.length > MAX_PROPS) {
      throw new Error("Out of domain: at most " + MAX_PROPS + " props are allowed");
    }

    var cleanProps = [];
    for (var i = 0; i < props.length; i += 1) {
      var p = props[i];
      if (!isPlainObject(p)) throw new Error("props[" + i + "] must be an object");
      var px = requireFinite(p.x, "props[" + i + "].x");
      var yLow = requireFinite(p.yLow, "props[" + i + "].yLow");
      var yHigh = requireFinite(p.yHigh, "props[" + i + "].yHigh");
      if (px <= lx || px >= sx) {
        throw new Error("Forbidden prop position: props[" + i + "].x must be strictly between light.x and screen.x");
      }
      if (yLow >= yHigh) {
        throw new Error("Degenerate segment: props[" + i + "].yLow must be strictly less than props[" + i + "].yHigh");
      }
      cleanProps.push({ x: px, yLow: yLow, yHigh: yHigh });
    }

    return {
      light: { x: lx, y: ly },
      props: cleanProps,
      screen: { x: sx, yMin: syMin, yMax: syMax }
    };
  }

  function validateTarget(target, screen) {
    if (!Array.isArray(target)) {
      throw new Error("Challenge target must be an array of [start, end] pairs");
    }
    if (target.length > MAX_PROPS) {
      throw new Error("Out of domain: at most " + MAX_PROPS + " target intervals are allowed");
    }
    var previousEnd = -Infinity;
    for (var i = 0; i < target.length; i += 1) {
      var iv = target[i];
      if (!Array.isArray(iv) || iv.length !== 2) {
        throw new Error("target[" + i + "] must be a [start, end] pair");
      }
      var a = requireFinite(iv[0], "target[" + i + "][0]");
      var b = requireFinite(iv[1], "target[" + i + "][1]");
      if (a >= b) {
        throw new Error("target[" + i + "] must have start < end");
      }
      if (a < screen.yMin || b > screen.yMax) {
        throw new Error("target[" + i + "] must lie within the screen bounds [yMin, yMax]");
      }
      if (i > 0 && a <= previousEnd) {
        throw new Error("target intervals must be strictly increasing and non-overlapping");
      }
      previousEnd = b;
    }
  }

  /*
   * Validate a complete challenge envelope and return a normalized copy.
   * Throws on anything that could not be displayed and exported losslessly:
   * missing fields, wrong types, non-JSON values (NaN/Infinity/undefined),
   * too many segments, out-of-domain coordinates, inconsistent intervals.
   */
  function validateChallenge(input) {
    if (!isPlainObject(input)) {
      throw new Error("Challenge must be a JSON object");
    }
    for (var i = 0; i < REQUIRED_FIELDS.length; i += 1) {
      var key = REQUIRED_FIELDS[i];
      if (!hasOwn(input, key)) {
        throw new Error("Missing challenge field: " + key);
      }
    }

    if (typeof input.id !== "string" || input.id.trim() === "") {
      throw new Error("Challenge field id must be a non-empty string");
    }
    if (typeof input.title !== "string" || input.title.trim() === "") {
      throw new Error("Challenge field title must be a non-empty string");
    }
    if (typeof input.description !== "string") {
      throw new Error("Challenge field description must be a string");
    }

    var scene = validateScene(input.light, input.props, input.screen);
    validateTarget(input.target, scene.screen);

    var tolerance = null;
    if (hasOwn(input, "tolerance")) {
      tolerance = requireFinite(input.tolerance, "tolerance");
      if (tolerance < 0) throw new Error("tolerance must be zero or greater");
    }

    // Only JSON data may be imported or exported: nothing may be silently
    // dropped, coerced or turned into null on the way back out.
    var copy = cloneJson(input);
    if (!deepEqual(copy, input)) {
      throw new Error("Challenge must contain only JSON-representable values");
    }

    if (tolerance !== null) copy.tolerance = tolerance;

    copy.id = input.id;
    copy.title = input.title;
    copy.description = input.description;
    copy.screen = scene.screen;
    copy.light = scene.light;
    copy.props = scene.props;
    copy.target = input.target.map(function (iv) {
      return [iv[0], iv[1]];
    });
    return copy;
  }

  function computeShadows(light, props, screen) {
    var clean = validateScene(light, props, screen);
    var lx = clean.light.x;
    var ly = clean.light.y;
    var sx = clean.screen.x;
    var syMin = clean.screen.yMin;
    var syMax = clean.screen.yMax;

    var rays = [];
    var clipped = [];
    for (var i = 0; i < clean.props.length; i += 1) {
      var p = clean.props[i];
      var mag = (sx - lx) / (p.x - lx);
      var ya = ly + mag * (p.yLow - ly);
      var yb = ly + mag * (p.yHigh - ly);
      rays.push({ p: p, ya: ya, yb: yb });
      var ca = Math.max(ya, syMin);
      var cb = Math.min(yb, syMax);
      if (ca < cb) {
        clipped.push([ca, cb]);
      }
    }

    clipped.sort(function (a, b) {
      return (a[0] - b[0]) || (a[1] - b[1]);
    });

    var merged = [];
    for (var j = 0; j < clipped.length; j += 1) {
      var start = clipped[j][0];
      var end = clipped[j][1];
      if (merged.length === 0 || start > merged[merged.length - 1][1]) {
        merged.push([start, end]);
      } else if (end > merged[merged.length - 1][1]) {
        merged[merged.length - 1][1] = end;
      }
    }

    var totalLength = 0;
    for (var k = 0; k < merged.length; k += 1) {
      totalLength += merged[k][1] - merged[k][0];
    }

    return { rays: rays, intervals: merged, totalLength: totalLength };
  }

  function toleranceOf(scene) {
    if (isPlainObject(scene) && hasOwn(scene, "tolerance") && typeof scene.tolerance === "number") {
      return scene.tolerance;
    }
    return DEFAULT_TOLERANCE;
  }

  function matchesTarget(intervals, target, tolerance) {
    var tol = typeof tolerance === "number" ? tolerance : DEFAULT_TOLERANCE;
    if (!Array.isArray(target) || target.length === 0) return false;
    if (!Array.isArray(intervals) || intervals.length !== target.length) return false;
    for (var i = 0; i < intervals.length; i += 1) {
      if (Math.abs(intervals[i][0] - target[i][0]) > tol) return false;
      if (Math.abs(intervals[i][1] - target[i][1]) > tol) return false;
    }
    return true;
  }

  function fmt(n) {
    return Number(n.toFixed(2));
  }

  function formatIntervals(intervals) {
    if (!Array.isArray(intervals) || intervals.length === 0) return "(none)";
    var parts = [];
    for (var i = 0; i < intervals.length; i += 1) {
      parts.push("[" + fmt(intervals[i][0]) + ", " + fmt(intervals[i][1]) + "]");
    }
    return parts.join(", ");
  }

  /*
   * Everything the page displays, derived only from a scene. Pure and
   * non-throwing, so a failed command can be compared against the last good
   * view byte for byte.
   */
  function describeScene(scene) {
    var view = {
      title: "",
      description: "",
      targetText: "Target: (none \u2014 sandbox)",
      ok: false,
      errorText: "",
      intervals: [],
      rays: [],
      totalLength: 0,
      intervalText: "",
      statusText: "",
      statusClass: "status"
    };
    if (!isPlainObject(scene)) {
      view.errorText = "Scene must be an object";
      view.intervalText = "Intervals: (invalid scene)";
      view.statusText = "Out-of-domain / Degenerate";
      return view;
    }
    if (typeof scene.title === "string") view.title = scene.title;
    if (typeof scene.description === "string") view.description = scene.description;

    var target = Array.isArray(scene.target) ? scene.target : [];
    if (target.length) {
      try {
        view.targetText = "Target: " + JSON.stringify(target);
      } catch (err) {
        view.targetText = "Target: (unreadable)";
      }
    }

    var result = null;
    try {
      result = computeShadows(scene.light, scene.props, scene.screen);
    } catch (err) {
      view.errorText = err && err.message ? err.message : String(err);
    }

    if (!result) {
      view.intervalText = "Intervals: (invalid scene)";
      view.statusText = "Out-of-domain / Degenerate";
      return view;
    }

    view.ok = true;
    view.intervals = result.intervals;
    view.rays = result.rays;
    view.totalLength = result.totalLength;
    view.intervalText =
      "Intervals: " + formatIntervals(result.intervals) +
      "\nTotal shadow length: " + fmt(result.totalLength) +
      "\nLight: (" + fmt(scene.light.x) + ", " + fmt(scene.light.y) + ")";

    if (target.length) {
      var solved = matchesTarget(result.intervals, target, toleranceOf(scene));
      view.statusText = solved ? "SOLVED" : "Not yet matched";
      view.statusClass = solved ? "status solved" : "status";
    } else {
      view.statusText = "Sandbox active";
      view.statusClass = "status";
    }
    return view;
  }

  /*
   * Parse and validate a challenge JSON document. The returned scene is a
   * fresh object; the caller's input is never mutated.
   */
  function parseChallenge(rawText) {
    if (typeof rawText !== "string") {
      throw new Error("Import requires JSON text");
    }
    if (rawText.trim() === "") {
      throw new Error("Import requires JSON text");
    }
    var parsed;
    try {
      parsed = JSON.parse(rawText);
    } catch (err) {
      throw new Error("Invalid challenge JSON: " + (err && err.message ? err.message : String(err)));
    }
    return validateChallenge(parsed);
  }

  /* Serialize a validated challenge. Throws instead of emitting invalid state. */
  function exportChallenge(scene) {
    var clean = validateChallenge(scene);
    return JSON.stringify(clean, null, 2);
  }

  /*
   * The import boundary the page uses. It either returns a complete new scene
   * or an error; it never returns a partially applied scene, so a rejected
   * import cannot replace the displayed state.
   */
  function applyImport(rawText) {
    try {
      return { ok: true, scene: parseChallenge(rawText), error: "" };
    } catch (err) {
      return { ok: false, scene: null, error: err && err.message ? err.message : String(err) };
    }
  }

  return {
    MAX_PROPS: MAX_PROPS,
    DEFAULT_TOLERANCE: DEFAULT_TOLERANCE,
    CHALLENGES: CHALLENGES,
    SANDBOX_DEFAULT: SANDBOX_DEFAULT,
    validateScene: validateScene,
    validateChallenge: validateChallenge,
    computeShadows: computeShadows,
    matchesTarget: matchesTarget,
    describeScene: describeScene,
    parseChallenge: parseChallenge,
    exportChallenge: exportChallenge,
    applyImport: applyImport,
    formatIntervals: formatIntervals,
    deepEqual: deepEqual
  };
});
