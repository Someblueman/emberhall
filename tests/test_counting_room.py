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
    appendChild(child) { this.children.push(child); child.parentElement = this; return child; },
    replaceChildren(...nodes) { this.children = [...nodes]; },
    addEventListener(ev, fn) { this.listeners[ev] = fn; },
    focus() { document.activeElement = this; },
    scrollIntoView() {},
    setSelectionRange() {},
    closest(tag) { let n = this; while (n && n.tagName !== tag.toUpperCase()) n = n.parentElement; return n || null; },
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

const trimmed = code.replace(/refresh\(\);\s*setInterval\(watch,10000\);\s*$/, "");
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
const handoffButtons = allContentNodes.filter(n => n.id.startsWith("counting-finish-"))
  .map(n => ({id:n.id, label:n.attributes["aria-label"]}));
const families = allContentNodes
  .filter(n => n.attributes && n.attributes["data-family"])
  .map(n => ({
    family: n.attributes["data-family"],
    texts: walk(n).filter(c => c.textContent && c.children.length === 0).map(c => c.textContent)
  }));

const pageStates = [];
for (const action of input.actions || []) {
  if (Number.isInteger(action.index)) {
    vm.runInContext(`index=${action.index};frame=data.frames[index];current=false;roomPanel();`, context);
  } else {
    const control = findById(getEl("room-content"), action.id);
    if (action.value !== undefined) { control.value = action.value; control.listeners.change(); }
    else if (!control.disabled) control.listeners.click();
  }
  const nodes = walk(getEl("room-content"));
  pageStates.push({
    results: findById(getEl("room-content"), "counting-results").textContent,
    runs: nodes.filter(n => n.className === "counting-run-info").map(n => n.children[0].textContent),
    previousDisabled: findById(getEl("room-content"), "counting-previous").disabled,
    nextDisabled: findById(getEl("room-content"), "counting-next").disabled,
    pagesHidden: nodes.find(n => n.attributes["aria-label"] === "Recorded run pages").hidden,
    focus: document.activeElement?.id,
  });
}

let filteredResults = null;
let focusPreserved = null;
let refreshedResults = null;
let refreshedHandoffOpen = null;

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
    const handoffs = target.closest("details");
    if (handoffs) { handoffs.open = true; handoffs.listeners.toggle(); }
    target.focus();
    vm.runInContext("lighting = () => {}; accounts = () => {}; drawHouse = () => {}; renderViewContext = () => {}; renderCollection = () => {}; renderRecentGrowth = () => {}; renderLately = () => {}; refreshView(false);", context);
    focusPreserved = document.activeElement ? document.activeElement.id : null;
    refreshedResults = findById(getEl("room-content"), "counting-results").textContent;
    refreshedHandoffOpen = document.activeElement?.closest("details")?.open;
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

let finishJumpState = null;
if (Number.isInteger(input.finishJumpSeq)) {
  const btn = findById(getEl("room-content"), `counting-finish-${input.finishJumpSeq}`);
  btn.focus();btn.listeners.click();
  finishJumpState = {
    seq: vm.runInContext("frame.seq", context),
    focus: document.activeElement?.id,
    open: document.activeElement?.closest("details")?.open,
    texts: walk(getEl("room-content")).map(n => n.textContent).join(" | ")
  };
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
  handoffButtons,
  finishJumpState,
  families,
  pageStates,
  filteredResults,
  focusPreserved,
  refreshedResults,
  refreshedHandoffOpen,
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
        self.assertEqual(res["initialResults"], "2 of 2 recorded runs match filters at this moment · showing 1–2, newest first")
        self.assertEqual(res["filteredResults"], "1 of 2 recorded runs match filters at this moment · showing 1–1, newest first")
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
                "results": "1 of 1 recorded runs match filters at this moment · showing 1–1, newest first",
            },
        )

    def handoff_data(self) -> dict:
        data = self.sample_data()
        last = data["frames"][-1]
        before = json.loads(json.dumps(last))
        before["seq"] = 18
        before["tasks"] = [{"id": "counting-room", "title": "Technical title",
                            "plain": "See what each visit finished <literally>.", "status": "claimed"}]
        before["runs"] = json.loads(json.dumps(last["runs"][:2]))
        before["runs"][1]["finished_tasks"] = []
        finished = json.loads(json.dumps(before))
        finished["seq"] = 19
        finished["tasks"] = []  # Production removes tasks on finish.
        finished["event"] = {"op": "finish", "actor": "resident-curlew", "title": "counting-room"}
        finished["runs"][1]["finished_tasks"] = [{"task": "counting-room", "sequence": 19}]
        data["frames"][1:1] = [before, finished]
        return data

    def test_handoffs_recover_plain_names_and_jump_with_open_keyboard_focus(self) -> None:
        res = self.run_harness({"data": self.handoff_data(), "index": 3, "current": True,
                                "selected": "counting", "finishJumpSeq": 19})
        self.assertEqual(res["handoffButtons"], [{"id": "counting-finish-19",
            "label": "Open handoff: See what each visit finished <literally>. · event 19"}])
        self.assertIn("Handed on: See what each visit finished <literally>.", " ".join(res["runTexts"]))
        self.assertNotIn("Technical title", " ".join(res["runTexts"]))
        jump = res["finishJumpState"]
        self.assertEqual((jump["seq"], jump["focus"], jump["open"]), (19, "counting-finish-19", True))
        self.assertIn("source acceptance and delivery are separate", jump["texts"])

    def test_handoffs_hide_future_and_invalid_receipts_and_names(self) -> None:
        data = self.handoff_data()
        data["frames"][-1]["tasks"] = [{"id": "counting-room", "plain": "FUTURE NAME"}]
        run = data["frames"][2]["runs"][1]
        run["finished_tasks"] += [{"task": "future-task", "sequence": 20},
                                  {"task": "bad", "sequence": "19"}, {"task": "bad", "sequence": 0}]
        res = self.run_harness({"data": data, "index": 2, "current": False, "selected": "counting"})
        texts = " ".join(res["runTexts"])
        self.assertNotIn("FUTURE NAME", texts)
        self.assertNotIn("future-task", texts)
        self.assertEqual(len(res["handoffButtons"]), 1)
        agy = next(f for f in res["families"] if f["family"] == "agy")
        self.assertIn("1 task finish", " ".join(agy["texts"]))

    def test_unretained_handoff_has_a_label_but_no_dead_control(self) -> None:
        data = self.handoff_data()
        del data["frames"][2]  # Completion event missing from this partial history.
        data["frames"][-1]["runs"][1]["finished_tasks"].append({"task": "unknown", "sequence": 17})
        res = self.run_harness({"data": data, "index": 2, "current": True, "selected": "counting"})
        self.assertEqual(res["handoffButtons"], [])
        texts = " ".join(res["runTexts"])
        self.assertIn("See what each visit finished <literally>.", texts)
        self.assertIn("Event 19 · outside retained history", texts)
        self.assertIn("Task name not retained", texts)
        self.assertIn("1 more", texts)

    def test_handoff_disclosure_and_focus_survive_refresh_but_not_future_history(self) -> None:
        data = self.handoff_data()
        res = self.run_harness({"data": data, "index": 3, "current": True, "selected": "counting",
                               "testFocusId": "counting-finish-19"})
        self.assertEqual(res["focusPreserved"], "counting-finish-19")
        self.assertTrue(res["refreshedHandoffOpen"])
        earlier = self.run_harness({"data": data, "index": 1, "current": False, "selected": "counting"})
        self.assertEqual(earlier["handoffButtons"], [])
        self.assertNotIn("Handed on:", " ".join(earlier["runTexts"]))

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

    def paging_data(self) -> dict:
        data = self.sample_data(budgets=[])
        data["frames"][1]["seq"] = 50
        data["frames"][1]["runs"] = [
            {"id": f"run-{n}", "resident": "resident-moss", "agent": "codex" if n % 2 else "agy",
             "model": f"fixture-{n}", "sequence": n, "start": 1700000100 + n,
             "end": 1700000110 + n, "last_sequence": n + 20, "usage": {}, "finished_tasks": [],
             "status": "completed", "outcome": "success", "assignment": {"lane": "work"}}
            for n in range(1, 18)
        ]
        return data

    def test_pages_reach_every_run_once_and_keep_filters(self) -> None:
        res = self.run_harness({
            "data": self.paging_data(), "index": 1, "current": False, "selected": "counting",
            "testFocusId": "counting-runs",
            "actions": [{"id": "counting-next"}, {"id": "counting-next"},
                        {"id": "counting-previous"}, {"id": "counting-agent", "value": "codex"},
                        {"id": "counting-next"}],
        })
        self.assertEqual([row.split(" | ")[0].rsplit(" · ", 1)[-1] for row in res["runTexts"]],
                         [f"fixture-{n}" for n in range(17, 9, -1)])
        second, last, back, filtered, filtered_last = res["pageStates"]
        self.assertEqual([row.rsplit(" · ", 1)[-1] for row in second["runs"]],
                         [f"fixture-{n}" for n in range(9, 1, -1)])
        self.assertEqual(len(last["runs"]), 1)
        self.assertTrue(last["runs"][0].endswith("fixture-1"))
        self.assertTrue(last["nextDisabled"])
        self.assertEqual(second["runs"], back["runs"])
        self.assertEqual(second["focus"], "counting-runs")
        self.assertIn("showing 1–8", filtered["results"])
        self.assertTrue(filtered["previousDisabled"])
        self.assertEqual(filtered["focus"], "counting-agent")
        self.assertIn("9 of 17", filtered_last["results"])
        self.assertEqual(len(filtered_last["runs"]), 1)
        self.assertEqual(res["refreshedResults"], filtered_last["results"])
        self.assertEqual(res["focusPreserved"], "counting-runs")
        self.assertTrue(res["frameUnchanged"])

    def test_empty_filter_and_earlier_history_clamp_the_page(self) -> None:
        res = self.run_harness({
            "data": self.paging_data(), "index": 1, "current": False, "selected": "counting",
            "actions": [{"id": "counting-next"}, {"id": "counting-next"}, {"index": 0},
                        {"id": "counting-lane", "value": "explore"}],
        })
        earlier, empty = res["pageStates"][-2:]
        self.assertIn("1 of 1", earlier["results"])
        self.assertTrue(earlier["previousDisabled"] and earlier["nextDisabled"])
        self.assertTrue(earlier["pagesHidden"])
        self.assertEqual(empty["runs"], [])
        self.assertIn("showing 0", empty["results"])
        self.assertTrue(empty["previousDisabled"] and empty["nextDisabled"])
        self.assertTrue(empty["pagesHidden"])


if __name__ == "__main__":
    unittest.main()
