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
    setSelectionRange(start, end, direction) { Object.assign(this, {selectionStart:start, selectionEnd:end, selectionDirection:direction}); },
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

const tail = "refresh();\nsetInterval(watch,10000);\n";
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

const beforeData = vm.runInContext("JSON.stringify(data)", context);
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

const interactions = [];
for (const step of input.steps || []) {
  if (step.frame !== undefined) vm.runInContext(`frame = data.frames[${step.frame}]; roomPanel();`, context);
  else {
    const node = findById(getEl("room-content"), step.id);
    if (!node) throw new Error("Missing control " + step.id);
    if (step.action === "input" || step.action === "change") node.value = step.value;
    if (step.selection) { node.focus(); node.setSelectionRange(...step.selection); }
    if (step.action === "refresh") {
      vm.runInContext("refreshView(false)", context);
    } else if (step.action) node.listeners[step.action]();
  }
  const panel = getEl("room-content"), nodes = walk(panel), active = document.activeElement;
  interactions.push({ text:textOf(panel), focus:active?.id, selection:[active?.selectionStart,active?.selectionEnd,active?.selectionDirection],
    jumps:nodes.map(n=>n.id).filter(id=>id.startsWith("assay-jump-")), reviews:textOf(findById(panel,"assay-reviews")), commits:textOf(findById(panel,"assay-commits")),
    disabled:nodes.filter(n=>n.disabled).map(n=>n.id), query:findById(panel,"assay-search").value });
}

const afterFrame = JSON.parse(vm.runInContext("JSON.stringify(frame)", context));
function textOf(n) {
  return [n.textContent, ...(n.children || []).map(textOf)].filter(Boolean).join(" | ");
}

process.stdout.write(JSON.stringify({
  fact,
  interactions,
  dataMutated: beforeData !== vm.runInContext("JSON.stringify(data)", context),
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

    def test_review_and_commit_pages_search_filters_and_historical_bounds(self):
        frame = {
            "seq": 50, "at": 2000, "rooms": [{"id": "assay", "name": "The Assay Room", "status": "open"}],
            "residents": [{"id": "author", "name": "Rowan"}, {"id": "reviewer", "name": "Tern"}],
            "tasks": [], "runs": [{"id": "work", "agent": "agy", "resident": "author", "sequence": 1, "usage": {},
                "finished_tasks": [{"task": "repair-name", "sequence": 2}, {"task": "future-task", "sequence": 99}]}],
            "scars": [], "budgets": [], "archive": [], "hearth": [], "council": {},
        }
        for i in range(19):
            frame["runs"].append({"id": f"review-{i}", "resident": f"reviewer-{i}", "agent": "codex" if i % 2 else "muse",
                "sequence": i + 3, "usage": {}, "outcome": "success" if i % 2 else "failed",
                "assignment": {"lane": "review", "help_request": "source-review-work"}})
        earlier = json.loads(json.dumps(frame))
        earlier.update(seq=2, runs=frame["runs"][:1], tasks=[{"id": "repair-name", "title": "Repair the lantern", "plain": "The lamp remembers its colour."}])
        future = {"seq": 99, "tasks": [{"id": "repair-name", "title": "FUTURE SECRET"}]}
        data = {"timezone": "UTC", "scars": {}, "frames": [earlier, frame, future],
                "commits": [{"id": f"commit-{i}", "at": 1000+i, "title": f"Change {i}"} for i in range(14)] +
                           [{"id": "hidden", "at": 9999, "title": "FUTURE COMMIT"}]}
        out = self.run_harness({"data": data, "index": 1, "current": False, "selected": "assay", "steps": [
            {"id": "assay-reviews-next", "action": "click"},
            {"id": "assay-commits-next", "action": "click"},
            {"id": "assay-reviews-next", "action": "click"},
            {"id": "assay-reviews-previous", "action": "click"},
            {"id": "assay-search", "action": "input", "value": "  LAMP   REMEMBERS  ", "selection": [2, 6, "backward"]},
            {"id": "assay-family", "action": "change", "value": "codex"},
            {"id": "assay-outcome", "action": "change", "value": "other"},
            {"id": "assay-clear", "action": "click"},
            {"frame": 0},
        ]})
        steps = out["interactions"]
        self.assertFalse(out["dataMutated"])
        self.assertEqual(steps[0]["jumps"], [])  # Missing publication frames are never guessed.
        self.assertIn("reviewer-10", steps[0]["reviews"])
        self.assertNotIn("reviewer-18", steps[0]["reviews"])
        self.assertIn("reviewer-0", steps[2]["reviews"])
        self.assertNotIn("reviewer-3", steps[2]["reviews"])
        self.assertIn("showing 9–16", steps[0]["text"])
        self.assertEqual(steps[0]["focus"], "assay-reviews")
        self.assertIn("Change 13", steps[0]["commits"])
        self.assertIn("Change 7", steps[1]["commits"])
        self.assertNotIn("Change 13", steps[1]["commits"])
        self.assertIn("showing 17–19", steps[2]["text"])
        self.assertIn("assay-reviews-next", steps[2]["disabled"])
        self.assertIn("showing 9–16", steps[3]["text"])
        self.assertIn("19 of 19 review runs match · showing 1–8", steps[4]["text"])
        self.assertEqual(steps[4]["focus"], "assay-search")
        self.assertEqual(steps[4]["selection"], [2, 6, "backward"])
        self.assertIn("9 of 19 review runs", steps[5]["text"])
        self.assertIn("0 of 19 review runs", steps[6]["text"])
        self.assertIn("Clear search or change the filters", steps[6]["text"])
        self.assertEqual(steps[7]["query"], "")
        self.assertEqual(steps[7]["focus"], "assay-search")
        self.assertIn("14 of 14 source commits match · showing 1–6", steps[7]["text"])
        self.assertIn("0 of 0 review runs", steps[8]["text"])
        self.assertIn("assay-reviews-previous", steps[8]["disabled"])
        rewound = self.run_harness({"data": data, "index": 1, "current": False, "selected": "assay", "steps": [
            {"id": "assay-reviews-next", "action": "click"},
            {"id": "assay-reviews-next", "action": "click"}, {"frame": 0},
        ]})["interactions"][-1]
        self.assertIn("0 of 0 review runs", rewound["text"])
        self.assertIn("assay-reviews-previous", rewound["disabled"])
        refreshed = self.run_harness({"data": data, "index": 1, "current": False, "selected": "assay", "steps": [
            {"id": "assay-search", "action": "input", "value": "repair the lantern", "selection": [2, 6, "backward"]},
            {"id": "assay-search", "action": "refresh"},
        ]})
        self.assertIn("19 of 19 review runs", refreshed["interactions"][0]["text"])
        self.assertEqual(refreshed["interactions"][1]["selection"], [2, 6, "backward"])
        self.assertEqual(refreshed["interactions"][1]["focus"], "assay-search")
        for step in steps:
            self.assertNotIn("FUTURE", step["text"])
            self.assertNotIn("future-task", step["text"])

    def test_assay_room_docs_and_cli_smoke(self):
        doc = ROOT / "docs" / "ASSAY_ROOM.md"
        readme = ROOT / "projects" / "assay-room" / "README.md"
        self.assertTrue(doc.is_file())
        self.assertTrue(readme.is_file())
        self.assertIn("The Assay Room", doc.read_text())

    def test_assay_room_decor_gestures_nametags_summary_cards_and_gallery_registration(self):
        script = r'''
const fs = require("node:fs"), vm = require("node:vm"), assert = require("node:assert/strict");
class Element {
  constructor(tag, ns = null) {
    this.tag = tag; this.ns = ns; this.children = []; this.attrs = {}; this.textContent = "";
    this.className = ""; this.id = ""; this.href = ""; this.listeners = {}; this.style = {};
  }
  appendChild(n) { this.children.push(n); return n; }
  replaceChildren(...nodes) { this.children = [...nodes]; }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  addEventListener(ev, fn) { this.listeners[ev] = fn; }
  focus() {}
}
const all = n => [n, ...n.children.flatMap(all)];
const text = n => [n.textContent, ...n.children.map(text)].filter(Boolean).join(" ");
const elements = new Map();
const getEl = id => { if (!elements.has(id)) { const n = new Element("div"); n.id = id; elements.set(id, n); } return elements.get(id); };
const document = {
  body: new Element("body"), activeElement: null,
  getElementById: id => all(getEl("room-content")).find(n => n.id === id) || all(getEl("creations")).find(n => n.id === id) || getEl(id),
  createElement: t => new Element(t),
  createElementNS: (ns, t) => new Element(t, ns),
  querySelector: () => null,
  querySelectorAll: () => []
};
const ctx = vm.createContext({ assert, document, URL, Intl, Date, Math, Number, String, Boolean, Array, Object, Map, Set, RegExp, Error });
const source = fs.readFileSync(process.argv[1], "utf8");
const tail = "refresh();\nsetInterval(watch,10000);\n";
assert(source.endsWith(tail));
vm.runInContext(source.slice(0, -tail.length), ctx);

const manifest = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const assayEntry = manifest.projects.find(p => p.id === "assay-room");
assert(assayEntry, "Expected assay-room entry in site/projects.json");
assert.equal(ctx.collectionUrl(assayEntry), assayEntry.href);

// Assay room decor & gesture & nameTag
const decorRoot = new Element("g");
ctx.__decorRoot = decorRoot;
vm.runInContext("decor(__decorRoot, 'assay', 0, 0, 160, true, false);", ctx);
assert(all(decorRoot).some(n => n.attrs["data-decor"] === "assay"), "Expected dedicated data-decor='assay'");

for (const [room, expectedGesture, expectedWhere] of [
  ["assay", "assaying", "in the assay room"],
  ["study", "reading", "in the study"],
  ["chronicle", "reading", "in the chronicle"],
  ["counting", "plans", "in the counting room"],
  ["parlor", "standing", "in the parlor"],
  ["gallery", "standing", "in the gallery"],
]) {
  const fig = new Element("g"), map = new Element("svg");
  ctx.__fig = fig; ctx.__map = map;
  vm.runInContext(`
    data = { timezone: "UTC", observed_at: 2000, commits: [], scars: {}, frames: [{ seq: 1, at: 1000, event: { op: "wake", actor: "r1" }, residents: [] }] };
    index = 0; current = true;
    frame = { seq: 10, at: 2000, tasks: [], rooms: [], residents: [{ id: "r1", name: "Yarrow", agent: "agy", room: ${JSON.stringify(room)}, pose: "standing", presence: "recorded awake" }] };
    figure(__fig, frame.residents[0], 40, 90);
    nameTags(__map, [{ resident: frame.residents[0], px: 40, py: 90 }]);
  `, ctx);
  assert.equal(all(fig).find(n => n.attrs["data-gesture"]).attrs["data-gesture"], expectedGesture);
  assert(text(map).includes(expectedWhere), `Expected '${expectedWhere}' in nameTag for room ${room}, got: ${text(map)}`);
}

// Summary cards, scar list, and Assay Auditor link inside renderAssayRoom + collection historical gating
vm.runInContext(`
  catalog = ${JSON.stringify(manifest.projects)};
  data = {
    timezone: "UTC", observed_at: 2000,
    commits: [{ id: "abcd1234", at: 1500, title: "Polish house" }],
    scars: { "run:w1": { id: "run:w1", room: "workshop", kind: "failure", title: "Failed run", detail: "err", sequence: 3, at: 1200 } },
    frames: [{ seq: 3, at: 1200 }, { seq: 5, at: 1500 }]
  };
  current = true;
  frame = {
    seq: 5, at: 1600,
    rooms: [{ id: "assay", name: "The Assay Room", status: "open" }],
    residents: [{ id: "r1", name: "Yarrow" }, { id: "r2", name: "Sorrel" }],
    runs: [
      { id: "w1", resident: "r1", agent: "agy", sequence: 2, outcome: "success", assignment: { lane: "work" }, finished_tasks: [{ task: "t1", sequence: 2 }] },
      { id: "rev1", resident: "r2", agent: "codex", sequence: 5, outcome: "success", assignment: { lane: "review", help_request: "source-review-w1" }, finished_tasks: [] }
    ],
    scars: [{ id: "run:w1", mended: false }],
    shelf: { projects: [] }
  };
  renderAssayRoom(document.getElementById("room-content"));
  renderCollection();
`, ctx);
const panel = getEl("room-content");
assert(all(panel).some(n => n.className === "assay-cards"), "Expected .assay-cards summary strip");
assert.match(text(panel), /1 cross-family/);
vm.runInContext(`
  frame.runs.push(
    { id: "unknown", agent: "unrecorded", sequence: 2 },
    { id: "rev2", agent: "codex", sequence: 5, assignment: { lane: "review", help_request: "source-review-unknown" } },
    { id: "rev3", agent: "unrecorded", sequence: 5, assignment: { lane: "review", help_request: "source-review-w1" } },
    { id: "rev4", agent: "codex", sequence: 5, assignment: { lane: "review", help_request: "source-review-missing" } }
  );
  document.getElementById("room-content").replaceChildren();
  renderAssayRoom(document.getElementById("room-content"));
`, ctx);
const pairCard = all(panel).find(n => n.className === "assay-card");
assert.match(text(pairCard), /1 cross-family · 0 same-family · 2 family unrecorded · 1 unpaired/);
assert(all(panel).some(n => n.tag === "a" && n.href === assayEntry.href), "Expected link to Assay Auditor guide");
const creations = getEl("creations");
assert(all(creations).some(n => n.tag === "a" && n.href === assayEntry.href), "Expected assay-room in gallery tools when assay room is open");

// Before assay room opens, assay-room stays absent from gallery tools
vm.runInContext(`
  frame.rooms = [{ id: "assay", name: "The Assay Room", status: "construction" }];
  renderCollection();
`, ctx);
assert(!all(creations).some(n => n.tag === "a" && n.href === assayEntry.href), "Expected assay-room hidden while under construction");

// Scars are history: each says whether anything it names is still unfinished, and only that one gets a "!".
vm.runInContext(`
  const scar = (id, kind, title, detail, extra = {}) => ({ id, room: "workshop", kind, title, detail, sequence: 5, at: 1500, mended: false, ...extra });
  const task = (id, owner = "r1") => ({ id, status: "claimed", owner, until: 9999, generation: 1 });
  data = {
    timezone: "UTC", observed_at: 2000, commits: [],
    scars: Object.fromEntries([
      scar("run:a", "failure", "Run failed", "No unfinished claim at this receipt"),
      scar("run:b", "interrupted", "Interrupted after finish", "t-done"),
      scar("run:c", "interrupted", "Interrupted with open task", "t-open"),
      scar("run:d", "failure", "Run named a stranger", "t-ghost"),
      scar("lease:t-open:1", "expired", "A lease ran out", "Open task title", { task: "t-open" }),
      scar("repair:l1", "repair", "Repaired lesson", "Check twice", { mended: true })
    ].map(s => [s.id, s])),
    frames: [
      { seq: 3, at: 1200, event: { op: "task", actor: "r1", title: "x" }, tasks: [task("t-done"), task("t-open")], scars: [] },
      { seq: 5, at: 1500, event: { op: "finish", actor: "r1", title: "t-done" }, tasks: [task("t-open")], scars: [] }
    ]
  };
  current = false;
  frame = {
    ...data.frames[1],
    rooms: [{ id: "assay", name: "The Assay Room", status: "open" }],
    residents: [{ id: "r1", name: "Yarrow" }, { id: "r2", name: "Mallow" }],
    runs: [
      { id: "w1", resident: "r1", agent: "agy", sequence: 4, outcome: "success", assignment: { lane: "work" }, finished_tasks: [{ task: "t-done", sequence: 5 }] },
      { id: "rv1", resident: "r2", agent: "codex", sequence: 5, outcome: "success", assignment: { lane: "review", help_request: "source-review-w1" }, finished_tasks: [] },
      { id: "rv2", resident: "r2", agent: "codex", sequence: 5, outcome: "quota", assignment: { lane: "review", help_request: "source-review-w1" }, finished_tasks: [] },
      { id: "rv3", resident: "r2", agent: "codex", sequence: 5, outcome: "interrupted", assignment: { lane: "review", help_request: "source-review-w1" }, finished_tasks: [] },
      { id: "rv4", resident: "r2", agent: "codex", sequence: 5, outcome: "unconfirmed", status: "launched", assignment: { lane: "review", help_request: "source-review-w1" }, finished_tasks: [] }
    ],
    scars: Object.keys(data.scars).map(id => ({ id, mended: id === "repair:l1" }))
  };
  document.getElementById("room-content").replaceChildren();
  renderAssayRoom(document.getElementById("room-content"));
`, ctx);
const room = getEl("room-content");
const cardsText = all(room).filter(n => n.className === "assay-card").map(text);
assert(cardsText.some(t => /Review run outcomes.*1 succeeded · 3 did not: 1 hit a usage limit, 1 interrupted, 1 still running/.test(t)), cardsText.join("\n"));
assert(!cardsText.some(t => /other or unfinished|\bopen\b/.test(t)), "No scar or run may be called open or unfinished by default");
assert(cardsText.some(t => /Scars \(past receipts\).*3 need attention · 1 left nothing unfinished · 1 finished later · 1 repaired or mended/.test(t)), cardsText.join("\n"));
assert.match(text(room), /3 of 6 scars still need attention/);
const scarRows = all(room).filter(n => n.className === "counting-run").map(text);
const rowFor = title => scarRows.find(t => t.includes(title)) || assert.fail(`no scar row for ${title}`);
assert.match(rowFor("Run failed"), /Nothing was left unfinished/);
assert.match(rowFor("Interrupted after finish"), /Finished later/);
assert.match(rowFor("Interrupted with open task"), /Still unfinished/);
assert.match(rowFor("Run named a stranger"), /Not confirmed finished/);
assert.match(rowFor("A lease ran out"), /Still unfinished/);
assert.match(rowFor("Repaired lesson"), /Repaired/);
const strongs = all(room).filter(n => n.tag === "strong").map(n => n.textContent);
assert(strongs.includes("Run failed") && strongs.includes("Interrupted after finish"), "History scars carry no alarm mark");
assert(strongs.includes("! Interrupted with open task") && strongs.includes("! A lease ran out"), "Unfinished scars keep the mark");
assert(strongs.includes("⌁ Repaired lesson"));
const outcomeOptions = all(room).filter(n => n.tag === "option").map(n => n.textContent);
assert(outcomeOptions.includes("Did not succeed") && !outcomeOptions.includes("Other or unfinished"));

// A finished task says who reviewed it when the record has that, and only "Finished" when it does not.
const finished = vm.runInContext("workshopTasks(data.frames, frame, frame.at).find(t => t.id === 't-done')", ctx);
assert.equal(ctx.workshopStatus(finished), "Finished · reviewed by Mallow");
vm.runInContext("frame.runs.forEach(r => { if (r.id === 'rv1') r.resident = 'r1'; });", ctx);
const selfReviewed = vm.runInContext("workshopTasks(data.frames, frame, frame.at).find(t => t.id === 't-done')", ctx);
assert.equal(ctx.workshopStatus(selfReviewed), "Finished", "A resident reviewing their own run is not shown as a review");
vm.runInContext("frame.runs = [];", ctx);
const unreviewed = vm.runInContext("workshopTasks(data.frames, frame, frame.at).find(t => t.id === 't-done')", ctx);
assert.equal(ctx.workshopStatus(unreviewed), "Finished");
'''
        proc = subprocess.run(
            ["node", "-e", script, str(HOUSE_JS), str(ROOT / "site" / "projects.json")],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_daylight_warn_and_desktop_layout_styles(self):
        css = (ROOT / "site" / "house.css").read_text()
        self.assertIn("--warn:", css)
        self.assertIn(".assay-cards", css)
        self.assertIn("var(--warn)", css)
        html = (ROOT / "site" / "index.html").read_text()
        self.assertEqual(html.count("?v=choice-progress-1"), 2)
        self.assertEqual(html.count("&amp;assay=2"), 2)


if __name__ == "__main__":
    unittest.main()
