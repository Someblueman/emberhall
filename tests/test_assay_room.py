"""Tests for The Assay Room interior, fact, interactive ledger, and standalone tool."""
from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOUSE_JS = ROOT / "site" / "house.js"


@unittest.skipUnless(shutil.which("node"), "node is required for JS unit tests")
class AssayRoomTests(unittest.TestCase):
    def run_harness(self, payload: dict) -> dict:
        script = r"""
const fs = require("fs");
const vm = require("vm");

const input = JSON.parse(fs.readFileSync(0, "utf8"));
const code = fs.readFileSync(input.houseJsPath, "utf8");

function makeNode(tag, ns = null) {
  return {
    tagName: String(tag).toUpperCase(),
    namespaceURI: ns,
    id: "",
    className: "",
    textContent: "",
    value: "",
    defaultValue: "",
    type: "",
    min: "",
    max: "",
    placeholder: "",
    hidden: false,
    disabled: false,
    open: false,
    tabIndex: 0,
    href: "",
    target: "",
    rel: "",
    dataset: {},
    style: {},
    attributes: {},
    children: [],
    listeners: {},
    classList: {
      _set: new Set(),
      add(...names) { names.forEach(n => this._set.add(n)); },
      remove(...names) { names.forEach(n => this._set.delete(n)); },
      toggle(name, force) {
        const on = force === undefined ? !this._set.has(name) : Boolean(force);
        if (on) this._set.add(name);
        else this._set.delete(name);
        return on;
      },
      contains(name) { return this._set.has(name); }
    },
    setAttribute(k, v) { this.attributes[k] = String(v); },
    getAttribute(k) { return this.attributes[k]; },
    removeAttribute(k) { delete this.attributes[k]; },
    appendChild(child) { this.children.push(child); return child; },
    replaceChildren(...nodes) { this.children = [...nodes]; },
    addEventListener(ev, fn) { this.listeners[ev] = fn; },
    focus() { document.activeElement = this; },
    scrollIntoView() {},
    setSelectionRange() {},
    closest() { return null; },
    contains() { return false; },
    querySelector() { return null; },
    querySelectorAll() { return []; }
  };
}

const elements = new Map();
function getEl(id) {
  if (!elements.has(id)) {
    const n = makeNode("div");
    n.id = id;
    elements.set(id, n);
  }
  return elements.get(id);
}

function walk(node, out = []) {
  out.push(node);
  for (const child of node.children || []) walk(child, out);
  return out;
}

function findById(root, id) {
  return walk(root).find(n => n.id === id) || null;
}

function findByIdInAll(id) {
  if (elements.has(id)) return elements.get(id);
  for (const root of elements.values()) {
    const hit = findById(root, id);
    if (hit) return hit;
  }
  return null;
}

const document = {
  activeElement: null,
  body: makeNode("body"),
  documentElement: makeNode("html"),
  getElementById: (id) => findByIdInAll(id) || getEl(id),
  createElement: (tag) => makeNode(tag),
  createElementNS: (ns, tag) => makeNode(tag, ns),
  querySelector: () => null,
  querySelectorAll: () => []
};

const tail = "refresh();\nsetInterval(refresh,60000);setInterval(watch,10000);\n";
if (!code.endsWith(tail)) throw new Error("Expected standard trailing tail in site/house.js");

const context = {
  document,
  window: { innerHeight: 900, location: { hash: "" }, addEventListener() {} },
  fetch: async () => ({ ok: false, status: 503 }),
  AbortSignal: { timeout: () => null },
  Intl,
  Date,
  Math,
  Number,
  String,
  Boolean,
  Array,
  Object,
  Map,
  Set,
  RegExp,
  Error,
  URL,
  console,
  setInterval: () => 0
};

vm.createContext(context);
vm.runInContext(code.slice(0, -tail.length), context);

const snapshot = JSON.stringify(input.data);
vm.runInContext(`
  data = ${snapshot};
  index = ${input.index};
  current = ${input.current ? "true" : "false"};
  frame = data.frames[index];
  selectedFloor = 0;
  selected = ${JSON.stringify(input.selected)};
  frame.scars = (frame.scars || []).map(s => ({...(data.scars?.[s.id] || {}), ...s}));
`, context);

const beforeFrame = JSON.parse(vm.runInContext("JSON.stringify(frame)", context));
const fact = vm.runInContext("roomFact('assay')", context);

const svgRoot = makeNode("g", "http://www.w3.org/2000/svg");
context.__svgRoot = svgRoot;
vm.runInContext("furnishings(__svgRoot, 'assay', 0, 0, true, [])", context);
const svgNodes = walk(svgRoot);

vm.runInContext("roomPanel();", context);
const roomContent = getEl("room-content");

let afterSearch = null;
if (input.searchQuery !== undefined) {
  const searchEl = findById(roomContent, "assay-search");
  if (searchEl) {
    searchEl.value = input.searchQuery;
    searchEl.listeners.input();
    afterSearch = textOf(getEl("room-content"));
  }
}

let afterFamilyFilter = null;
if (input.filterFamily) {
  const sel = findById(roomContent, "assay-family");
  if (sel) {
    sel.value = input.filterFamily;
    sel.listeners.change();
    afterFamilyFilter = {
      text: textOf(getEl("room-content")),
      activeId: document.activeElement ? document.activeElement.id : null
    };
  }
}

// Verify refreshView preserves focus on assay-family
let refreshFocusId = null;
const familySel = findById(getEl("room-content"), "assay-family");
if (familySel) {
  familySel.focus();
  vm.runInContext("refreshView(false);", context);
  refreshFocusId = document.activeElement ? document.activeElement.id : null;
}

const afterFrame = JSON.parse(vm.runInContext("JSON.stringify(frame)", context));
function textOf(n) {
  return [n.textContent, ...(n.children || []).map(textOf)].filter(Boolean).join(" | ");
}

process.stdout.write(JSON.stringify({
  fact,
  mutated: JSON.stringify(beforeFrame) !== JSON.stringify(afterFrame),
  svgMarkers: svgNodes.map(n => n.attributes).filter(a => a["data-interior"] || a["data-assay-review"]),
  svgText: svgNodes.map(n => n.textContent).filter(Boolean),
  panelText: textOf(getEl("room-content")),
  panelIds: walk(getEl("room-content")).map(n => n.id).filter(Boolean),
  hasScriptTag: walk(getEl("room-content")).some(n => n.tagName === "SCRIPT"),
  afterSearch,
  afterFamilyFilter,
  refreshFocusId
}));
"""
        proc = subprocess.run(
            ["node", "-e", script],
            input=json.dumps({"houseJsPath": str(HOUSE_JS), **payload}),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    def test_assay_room_renders_bounded_reviews_commits_scars_and_filters(self):
        data = {
            "timezone": "UTC",
            "commits": [
                {"id": "1111aaaa2222bbbb", "at": 1005, "title": "Add Parlor digest"},
                {"id": "3333cccc4444dddd", "at": 1045, "title": "Polish Counting Room"},
                {"id": "5555eeee6666ffff", "at": 2000, "title": "Future commit should hide"},
            ],
            "scars": {
                "run:w1": {
                    "id": "run:w1", "room": "workshop", "kind": "failure",
                    "title": "Earlier build failed", "detail": "missing test", "sequence": 2, "at": 1010,
                },
                "repair:l1": {
                    "id": "repair:l1", "room": "archive", "kind": "repair",
                    "title": "lesson one", "detail": "Check twice", "sequence": 4, "at": 1030,
                },
            },
            "frames": [
                {
                    "seq": 2, "at": 1010, "floors": [{"level": 0, "name": "Ground floor"}],
                    "event": {"op": "life", "actor": "r-yarrow", "title": ""},
                    "rooms": [{"id": "assay", "name": "The Assay Room", "status": "construction", "purpose": "Inspect reviews"}],
                    "residents": [], "tasks": [], "runs": [], "budgets": [], "lessons": 0,
                    "council": {"pending": 0, "enacted": 0}, "hearth": [], "archive": [],
                    "scars": [{"id": "run:w1", "mended": False}],
                },
                {
                    "seq": 5, "at": 1035, "floors": [{"level": 0, "name": "Ground floor"}],
                    "event": {"op": "life", "actor": "r-mallow", "title": ""},
                    "rooms": [{"id": "assay", "name": "The Assay Room", "status": "construction", "purpose": "Inspect reviews"}],
                    "residents": [], "tasks": [], "runs": [], "budgets": [], "lessons": 0,
                    "council": {"pending": 0, "enacted": 0}, "hearth": [], "archive": [],
                    "scars": [],
                },
                {
                    "seq": 6, "at": 1050, "floors": [{"level": 0, "name": "Ground floor"}],
                    "event": {"op": "life", "actor": "r-yarrow", "title": ""},
                    "rooms": [{"id": "assay", "name": "The Assay Room", "status": "open", "purpose": "Inspect reviews"}],
                    "budgets": [], "lessons": 0, "council": {"pending": 0, "enacted": 0}, "hearth": [], "archive": [],
                    "residents": [
                        {"id": "r-yarrow", "name": "Yarrow", "agent": "agy", "room": "assay", "pose": "standing", "presence": "recorded awake", "tasks": []},
                        {"id": "r-mallow", "name": "Mallow", "agent": "codex", "room": "workshop", "pose": "standing", "presence": "recorded awake", "tasks": []},
                    ],
                    "tasks": [],
                    "runs": [
                        {
                            "id": "work-10", "resident": "r-yarrow", "agent": "agy", "model": "gemini-4",
                            "start": 1015, "sequence": 3, "outcome": "success", "usage": {},
                            "assignment": {"lane": "work", "reason": "balanced"},
                            "finished_tasks": [{"task": "counting-room", "sequence": 3}],
                        },
                        {
                            "id": "rev-11", "resident": "r-mallow", "agent": "codex", "model": "gpt-6.1-sol",
                            "start": 1035, "sequence": 5, "outcome": "success", "usage": {},
                            "assignment": {"lane": "review", "reason": "balanced", "help_request": "source-review-work-10"},
                            "finished_tasks": [],
                        },
                        {
                            "id": "rev-future", "resident": "r-mallow", "agent": "codex", "model": "gpt-6.1-sol",
                            "start": 1995, "sequence": 99, "outcome": "success", "usage": {},
                            "assignment": {"lane": "review", "reason": "balanced", "help_request": "source-review-future"},
                            "finished_tasks": [],
                        },
                    ],
                    "scars": [
                        {"id": "run:w1", "mended": False},
                        {"id": "repair:l1", "mended": True},
                    ],
                },
            ],
        }
        out = self.run_harness({
            "data": data, "index": 2, "current": False, "selected": "assay",
            "filterFamily": "codex", "searchQuery": "Counting",
        })
        self.assertFalse(out["mutated"])
        self.assertFalse(out["hasScriptTag"])
        self.assertEqual(out["fact"], "1 review")
        self.assertTrue(any(m.get("data-interior") == "assay" for m in out["svgMarkers"]))
        review_markers = [m.get("data-assay-review") for m in out["svgMarkers"] if m.get("data-assay-review")]
        self.assertEqual(review_markers, ["rev-11"])
        self.assertNotIn("Future commit should hide", out["panelText"])
        # These are ordinary exported source-history entries; this fixture has
        # no integration receipts that could establish source acceptance.
        self.assertIn("2 source commits", out["panelText"])
        self.assertNotIn("integrated commit", out["panelText"])
        self.assertTrue(any("2 source commits" in text for text in out["svgText"]))
        self.assertIn("Polish Counting Room", out["panelText"])
        self.assertIn("Mallow", out["panelText"])
        self.assertIn("Yarrow", out["panelText"])
        self.assertIn("counting-room", out["panelText"])
        self.assertIn("assay-jump-5", out["panelIds"])
        self.assertIn("assay-family", out["panelIds"])
        self.assertIn("assay-outcome", out["panelIds"])
        self.assertEqual(out["refreshFocusId"], "assay-family")
        self.assertIn("Polish Counting Room", out["afterSearch"])
        self.assertNotIn("Add Parlor digest", out["afterSearch"])

        # Under construction: panel does not render interactive open ledger
        under_construction = self.run_harness({"data": data, "index": 0, "current": False, "selected": "assay"})
        self.assertEqual(under_construction["fact"], "")
        self.assertNotIn("assay-family", under_construction["panelIds"])

        # Untrusted text stays plain text without injecting script elements
        hostile_data = json.loads(json.dumps(data))
        hostile_data["commits"][1]["title"] = "<script>alert(1)</script> Counting"
        hostile_data["frames"][2]["residents"][0]["name"] = "<script>evil</script>"
        hostile_out = self.run_harness({"data": hostile_data, "index": 2, "current": False, "selected": "assay"})
        self.assertFalse(hostile_out["hasScriptTag"])
        self.assertIn("<script>alert(1)</script>", hostile_out["panelText"])
        self.assertIn("<script>evil</script>", hostile_out["panelText"])

    def test_assay_room_docs_and_cli_smoke(self):
        doc = ROOT / "docs" / "ASSAY_ROOM.md"
        readme = ROOT / "projects" / "assay-room" / "README.md"
        self.assertTrue(doc.is_file())
        self.assertTrue(readme.is_file())
        self.assertIn("The Assay Room", doc.read_text())


if __name__ == "__main__":
    unittest.main()
