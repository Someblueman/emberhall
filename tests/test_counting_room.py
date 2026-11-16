import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOUSE_JS = ROOT / "site" / "house.js"
HOUSE_CSS = ROOT / "site" / "house.css"


@unittest.skipUnless(shutil.which("node"), "node is required for JS unit tests")
class CountingRoomTests(unittest.TestCase):
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
      contains(name) {
        return this._set.has(name);
      }
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

const trimmed = code.replace(/refresh\(\);\s*setInterval\(refresh,60000\);setInterval\(watch,10000\);\s*$/, "");
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
vm.runInContext(trimmed, context);

const snapshot = JSON.stringify(input.data);
vm.runInContext(`
  data = ${snapshot};
  index = ${input.index};
  current = ${input.current ? "true" : "false"};
  frame = data.frames[index];
  selectedFloor = 0;
  selected = ${JSON.stringify(input.selected)};
`, context);

const beforeFrame = JSON.parse(vm.runInContext("JSON.stringify(frame)", context));
const floorIds = JSON.parse(vm.runInContext("JSON.stringify(floorRooms(frame, 0).map(r => r.id))", context));
const fact = vm.runInContext("roomFact('counting')", context);

const svgRoot = makeNode("g", "http://www.w3.org/2000/svg");
context.__svgRoot = svgRoot;
vm.runInContext("furnishings(__svgRoot, 'counting', 0, 0, true, [])", context);
const svgNodes = walk(svgRoot);
const interior = svgNodes.find(n => n.attributes && n.attributes["data-interior"] === "counting");
const tallies = svgNodes
  .filter(n => n.attributes && n.attributes["data-kind-tally"])
  .map(n => ({
    agent: n.attributes["data-kind-tally"],
    count: Number(n.attributes["data-run-count"])
  }));
const captions = svgNodes
  .filter(n => n.tagName === "TEXT" && n.attributes && String(n.attributes.class || "").split(" ").includes("resident-label"))
  .map(n => n.textContent);

vm.runInContext("roomPanel()", context);
const roomContent = getEl("room-content");
const allContentNodes = walk(roomContent);
const links = allContentNodes.filter(n => n.tagName === "A").map(n => ({ text: n.textContent, href: n.href }));
const resultsNode = findById(roomContent, "counting-results");
const initialResults = resultsNode ? resultsNode.textContent : null;
const jumpButtons = allContentNodes
  .filter(n => n.tagName === "BUTTON" && typeof n.id === "string" && n.id.startsWith("counting-jump-"))
  .map(n => n.id);
const runTexts = allContentNodes
  .filter(n => n.className === "counting-run")
  .map(n => walk(n).filter(c => c.textContent && c.children.length === 0).map(c => c.textContent).join(" | "));
const families = allContentNodes
  .filter(n => n.attributes && n.attributes["data-family"])
  .map(n => ({
    family: n.attributes["data-family"],
    texts: walk(n).filter(c => c.textContent && c.children.length === 0).map(c => c.textContent)
  }));

let filteredResults = null;
let focusPreserved = null;

if (input.filterAgent) {
  const agentSelect = findById(roomContent, "counting-agent");
  if (agentSelect && agentSelect.listeners.change) {
    agentSelect.value = input.filterAgent;
    agentSelect.listeners.change();
    const updatedResults = findById(getEl("room-content"), "counting-results");
    filteredResults = updatedResults ? updatedResults.textContent : null;
  }
}

if (input.filterLane) {
  const laneSelect = findById(getEl("room-content"), "counting-lane");
  if (laneSelect && laneSelect.listeners.change) {
    laneSelect.value = input.filterLane;
    laneSelect.listeners.change();
    const updatedResults = findById(getEl("room-content"), "counting-results");
    filteredResults = updatedResults ? updatedResults.textContent : null;
  }
}

if (input.testFocusId) {
  const target = findById(getEl("room-content"), input.testFocusId);
  if (target) {
    target.focus();
    vm.runInContext("lighting = () => {}; accounts = () => {}; drawHouse = () => {}; renderViewContext = () => {}; renderCollection = () => {}; renderRecentGrowth = () => {}; renderLately = () => {}; refreshView(false);", context);
    focusPreserved = document.activeElement ? document.activeElement.id : null;
  }
}

let missingJumpState = null;
if (Number.isInteger(input.missingJumpSeq)) {
  const beforeMissing = JSON.parse(vm.runInContext("JSON.stringify({index, current, frameSeq: frame.seq})", context));
  vm.runInContext(`jumpToSequence(${input.missingJumpSeq})`, context);
  const afterMissing = JSON.parse(vm.runInContext("JSON.stringify({index, current, frameSeq: frame.seq})", context));
  missingJumpState = { before: beforeMissing, after: afterMissing };
}

let jumpState = null;
if (Number.isInteger(input.jumpSeq)) {
  // Re-render roomPanel with reset filter state or inspect current roomContent button.
  const btn = findById(getEl("room-content"), `counting-jump-${input.jumpSeq}`);
  if (btn && btn.listeners.click) {
    btn.listeners.click();
    const postResultsNode = findById(getEl("room-content"), "counting-results");
    jumpState = {
      index: vm.runInContext("index", context),
      current: vm.runInContext("current", context),
      frameSeq: vm.runInContext("frame.seq", context),
      results: postResultsNode ? postResultsNode.textContent : null
    };
  }
}

const afterFrame = JSON.parse(vm.runInContext("JSON.stringify(frame)", context));

process.stdout.write(JSON.stringify({
  floorIds,
  fact,
  hasInterior: Boolean(interior),
  tallies,
  captions,
  links,
  initialResults,
  jumpButtons,
  runTexts,
  families,
  filteredResults,
  focusPreserved,
  missingJumpState,
  jumpState,
  frameUnchanged: JSON.stringify(beforeFrame) === JSON.stringify(afterFrame)
}));
"""
        proc = subprocess.run(
            ["node", "-e", script],
            input=json.dumps({**payload, "houseJsPath": str(HOUSE_JS)}),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(proc.stdout)

    def sample_data(self, room_status: str = "open", include_room: bool = True, budgets: list | None = None) -> dict:
        rooms = [
            {"id": "door", "name": "The Door", "floor": 0, "status": "open"},
            {"id": "workshop", "name": "The Workshop", "floor": 0, "status": "open"},
        ]
        if include_room:
            rooms.append({
                "id": "counting",
                "name": "The Counting Room",
                "floor": 0,
                "status": room_status,
                "purpose": "Inspect how the four agent families share work, review and exploration runs.",
                "reason": "Household stewardship under Accounts had no room on the map.",
                "builder": "resident-curlew",
                "task": "counting-room",
                "planned_at": 1700000100,
                "opened_at": 1700000200 if room_status == "open" else None,
                "history": [
                    {"kind": "room-plan", "at": 1700000100, "sequence": 10, "actor": "resident-curlew", "generation": 1}
                ],
            })
        runs = [
            {
                "id": "run-codex-1",
                "resident": "resident-moss",
                "agent": "codex",
                "model": "gpt-5.4",
                "sequence": 12,
                "start": 1700000110,
                "end": 1700000150,
                "status": "completed",
                "outcome": "success",
                "assignment": {"lane": "review", "reason": "balanced"},
                "finished_tasks": [],
                "usage": {},
            },
            {
                "id": "run-agy-1",
                "resident": "resident-curlew",
                "agent": "agy",
                "model": "gemini-4-argon-high",
                "sequence": 18,
                "start": 1700000160,
                "end": 1700000220,
                "status": "completed",
                "outcome": "success",
                "assignment": {"lane": "work", "reason": "balanced"},
                "finished_tasks": [{"task": "counting-room", "sequence": 19}],
                "usage": {},
            },
            {
                "id": "run-opencode-future",
                "resident": "resident-vesper",
                "agent": "opencode",
                "model": "glm-5.1",
                "sequence": 28,
                "start": 1700000300,
                "end": 1700000360,
                "status": "completed",
                "outcome": "success",
                "assignment": {"lane": "explore", "reason": "balanced"},
                "finished_tasks": [],
                "usage": {},
            },
        ]
        active_budgets = (
            [{"agent": "muse", "until": 1700000900, "reason": "rate limit backoff"}]
            if budgets is None
            else budgets
        )
        return {
            "version": 1,
            "name": "Emberhall",
            "timezone": "Europe/London",
            "observed_at": 1700000400,
            "journal_head": "a" * 40,
            "source_head": "b" * 40,
            "scars": {},
            "commits": [],
            "frames": [
                {
                    "seq": 12,
                    "at": 1700000120,
                    "event": {"op": "wake", "actor": "resident-moss"},
                    "residents": [
                        {"id": "resident-curlew", "name": "Curlew", "agent": "agy", "room": "counting", "pose": "standing", "presence": "awake"},
                        {"id": "resident-moss", "name": "Moss", "agent": "codex", "room": "workshop", "pose": "standing", "presence": "awake"},
                    ],
                    "rooms": rooms,
                    "tasks": [],
                    "lessons": 0,
                    "council": {"pending": 0},
                    "ambitions": [],
                    "runs": runs[:1],
                    "budgets": [],
                    "scars": [],
                },
                {
                    "seq": 20,
                    "at": 1700000250,
                    "event": {"op": "life", "actor": "resident-curlew"},
                    "residents": [
                        {"id": "resident-curlew", "name": "Curlew", "agent": "agy", "room": "counting", "pose": "standing", "presence": "awake"},
                        {"id": "resident-moss", "name": "Moss", "agent": "codex", "room": "workshop", "pose": "standing", "presence": "awake"},
                    ],
                    "rooms": rooms,
                    "tasks": [],
                    "lessons": 0,
                    "council": {"pending": 0},
                    "ambitions": [],
                    "runs": runs,
                    "budgets": active_budgets,
                    "scars": [],
                },
            ],
        }

    def test_counting_room_not_synthesized_when_absent(self) -> None:
        res = self.run_harness({
            "data": self.sample_data(include_room=False),
            "index": 1,
            "current": True,
            "selected": None,
        })
        self.assertNotIn("counting", res["floorIds"])

    def test_counting_room_furnishings_and_fact_respect_frame_seq(self) -> None:
        res = self.run_harness({
            "data": self.sample_data(room_status="open"),
            "index": 1,
            "current": False,
            "selected": "counting",
        })
        self.assertIn("counting", res["floorIds"])
        self.assertTrue(res["hasInterior"])
        self.assertEqual(res["fact"], "2 runs recorded")
        self.assertIn("2 runs tallied", res["captions"])
        self.assertEqual(
            res["tallies"],
            [
                {"agent": "codex", "count": 1},
                {"agent": "opencode", "count": 0},
                {"agent": "muse", "count": 0},
                {"agent": "agy", "count": 1},
            ],
        )
        self.assertTrue(res["frameUnchanged"])

    def test_open_counting_room_renders_ledger_filters_focus_and_accounts_link(self) -> None:
        res = self.run_harness({
            "data": self.sample_data(room_status="open"),
            "index": 1,
            "current": False,
            "selected": "counting",
            "filterAgent": "agy",
            "testFocusId": "counting-agent",
        })
        self.assertIn({"text": "Open Household Accounts →", "href": "#accounts-view"}, res["links"])
        self.assertEqual(res["initialResults"], "2 of 2 recorded runs match filters at this moment")
        self.assertEqual(res["filteredResults"], "1 of 2 recorded runs match filters at this moment")
        self.assertEqual(res["focusPreserved"], "counting-agent")
        muse_family = next(f for f in res["families"] if f["family"] == "muse")
        self.assertTrue(any("Resting until" in t for t in muse_family["texts"]))

    def test_absent_and_expired_backoffs_report_unknown_availability_never_ready(self) -> None:
        res_empty = self.run_harness({
            "data": self.sample_data(room_status="open", budgets=[]),
            "index": 1,
            "current": False,
            "selected": "counting",
        })
        for family in res_empty["families"]:
            joined = " ".join(family["texts"])
            self.assertNotIn("Ready", joined)
            self.assertIn("Availability unknown · no backoff recorded", family["texts"])

        res_mixed = self.run_harness({
            "data": self.sample_data(
                room_status="open",
                budgets=[
                    {"agent": "codex", "until": 1700000240, "reason": "rate limit backoff"},
                    {"agent": "agy", "until": 1700000900, "reason": "401 key expired"},
                ],
            ),
            "index": 1,
            "current": False,
            "selected": "counting",
        })
        by_family = {f["family"]: f["texts"] for f in res_mixed["families"]}
        for texts in by_family.values():
            self.assertNotIn("Ready", " ".join(texts))
        self.assertIn("Availability unknown · prior backoff ended", by_family["codex"])
        self.assertIn("Credential unavailable", by_family["agy"])
        self.assertIn("Availability unknown · no backoff recorded", by_family["opencode"])
        self.assertIn("Availability unknown · no backoff recorded", by_family["muse"])

    def test_sequence_jump_renders_only_existing_frames_and_uses_real_jump_to_sequence(self) -> None:
        res = self.run_harness({
            "data": self.sample_data(room_status="open"),
            "index": 1,
            "current": True,
            "selected": "counting",
            "missingJumpSeq": 18,
            "jumpSeq": 12,
        })
        # Run 12 exists in data.frames, run 18 is sampled out (no dead button), run 28 is future.
        self.assertEqual(res["jumpButtons"], ["counting-jump-12"])
        self.assertTrue(any("event 18" in row for row in res["runTexts"]))
        self.assertFalse(any("event 28" in row for row in res["runTexts"]))
        # Calling real jumpToSequence(18) must leave index/current/frame.seq unchanged.
        self.assertEqual(
            res["missingJumpState"]["before"],
            res["missingJumpState"]["after"],
        )
        # Clicking real #counting-jump-12 calls real jumpToSequence(12) and renders frame 0.
        self.assertEqual(
            res["jumpState"],
            {
                "index": 0,
                "current": False,
                "frameSeq": 12,
                "results": "1 of 1 recorded runs match filters at this moment",
            },
        )

    def test_construction_and_closed_counting_room_hide_open_controls(self) -> None:
        for status in ("construction", "closed"):
            res = self.run_harness({
                "data": self.sample_data(room_status=status),
                "index": 1,
                "current": True,
                "selected": "counting",
            })
            self.assertEqual(
                [link for link in res["links"] if not link["href"].startswith("#room/")],
                [],
            )
            self.assertEqual(
                [link["href"] for link in res["links"] if link["href"].startswith("#room/")],
                ["#room/counting"],
            )
            self.assertIsNone(res["initialResults"])

    def test_counting_room_css_classes_defined(self) -> None:
        css = HOUSE_CSS.read_text(encoding="utf-8")
        for selector in (".counting-panel", ".counting-families", ".counting-controls", ".counting-runs"):
            self.assertIn(selector, css)


if __name__ == "__main__":
    unittest.main()
