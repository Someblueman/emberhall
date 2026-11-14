import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOUSE_JS = ROOT / "site" / "house.js"
HISTORY_JSON = ROOT / "site" / "history.json"


def run_node(script: str) -> dict:
    proc = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


class CatchupRoomTests(unittest.TestCase):
    def test_build_catchup_digest_respects_scrubbed_moment_and_start_seq(self) -> None:
        script = f"""
const fs = require("fs");
const vm = require("vm");
const code = fs.readFileSync({json.dumps(str(HOUSE_JS))}, "utf8");
const marker = "function roomPanel()";
const slice = code.slice(0, code.indexOf(marker));
const ctx = vm.createContext({{
  console, Math, Number, Set, Map, Array, Object, String, Boolean, JSON,
  document: {{ getElementById: () => null }},
  window: {{}},
}});
vm.runInContext(slice, ctx);

const frames = [
  {{ seq: 1, at: 100, event: {{ op: "task", actor: "a", title: "t1" }}, tasks: [{{ id: "t1", title: "First <script> thing", owner: "a", status: "claimed", until: 200, generation: 1 }}], rooms: [{{ id: "parlor", name: "The Parlor", status: "construction" }}], shelf: {{ projects: [] }} }},
  {{ seq: 2, at: 110, event: {{ op: "finish", actor: "a", title: "t1" }}, tasks: [], rooms: [{{ id: "parlor", name: "The Parlor", status: "construction" }}], shelf: {{ projects: [{{ id: "p1", title: "Wake Digest", status: "active" }}] }} }},
  {{ seq: 3, at: 120, event: {{ op: "task", actor: "b", title: "t2" }}, tasks: [{{ id: "t2", title: "Future Task", owner: "b", status: "claimed", until: 200, generation: 1 }}], rooms: [{{ id: "parlor", name: "The Parlor", status: "open" }}], shelf: {{ projects: [{{ id: "p1", title: "Wake Digest", status: "done" }}] }} }},
  {{ seq: 4, at: 130, event: {{ op: "finish", actor: "b", title: "t2" }}, tasks: [], rooms: [{{ id: "parlor", name: "The Parlor", status: "open" }}], shelf: {{ projects: [{{ id: "p1", title: "Wake Digest", status: "done" }}] }} }},
];

const early = ctx.buildCatchupDigest(frames, 1, null);
const custom = ctx.buildCatchupDigest(frames, 3, 4);
console.log(JSON.stringify({{ early, custom }}));
"""
        out = run_node(script)
        early = out["early"]
        self.assertEqual(early["endSeq"], 2)
        self.assertEqual(len(early["tasks"]), 1)
        self.assertEqual(early["tasks"][0]["title"], "First <script> thing")
        self.assertEqual(early["tasks"][0]["seq"], 2)
        self.assertEqual(len(early["projects"]), 1)
        self.assertTrue(early["isDefault"])

        custom = out["custom"]
        self.assertEqual(custom["startSeq"], 4)
        self.assertEqual(custom["endSeq"], 4)
        self.assertFalse(custom["isDefault"])
        self.assertEqual(len(custom["tasks"]), 1)
        self.assertEqual(custom["tasks"][0]["title"], "Future Task")
        self.assertEqual(custom["tasks"][0]["seq"], 4)

    def test_tracked_history_finish_events_are_recovered(self) -> None:
        history = json.loads(HISTORY_JSON.read_text(encoding="utf-8"))
        frames = history["frames"]
        self.assertEqual(len(frames), 243)
        finish_count = sum(1 for f in frames if f["event"]["op"] == "finish")
        self.assertEqual(finish_count, 29)
        self.assertFalse(any(t.get("status") == "done" for f in frames for t in f.get("tasks", [])))
        script = f"""
const fs = require("fs");
const vm = require("vm");
const code = fs.readFileSync({json.dumps(str(HOUSE_JS))}, "utf8");
const slice = code.slice(0, code.indexOf("function roomPanel()"));
const ctx = vm.createContext({{console, Math, Number, Set, Map, Array, Object, String, Boolean, JSON, document: {{ getElementById: () => null }}, window: {{}}}});
vm.runInContext(slice, ctx);
const frames = JSON.parse(fs.readFileSync({json.dumps(str(HISTORY_JSON))}, "utf8")).frames;
const full = ctx.buildCatchupDigest(frames, frames.length - 1, 1);
const scoped = ctx.buildCatchupDigest(frames, 13, 1);
const edge = ctx.buildCatchupDigest(frames, frames.length - 1, 14);
const latest = ctx.buildCatchupDigest(frames, frames.length - 1, null);
console.log(JSON.stringify({{ full, scoped, edge, latest }}));
"""
        out = run_node(script)
        full = out["full"]
        self.assertEqual(full["startSeq"], 1)
        self.assertEqual(full["endSeq"], 243)
        self.assertFalse(full["isDefault"])
        self.assertEqual(len(full["tasks"]), 29)
        self.assertEqual(full["tasks"][0], {"title": "Publish Blackout Kit after independent review", "seq": 14})
        self.assertEqual(full["tasks"][-1]["seq"], 237)
        scoped = out["scoped"]
        self.assertEqual(len(scoped["tasks"]), 1)
        self.assertEqual(scoped["tasks"][0]["seq"], 14)
        edge = out["edge"]
        self.assertEqual(edge["startSeq"], 14)
        self.assertEqual(edge["tasks"][0]["seq"], 14)
        self.assertEqual(len(edge["tasks"]), 29)
        latest = out["latest"]
        self.assertTrue(latest["isDefault"])
        self.assertEqual(latest["count"], 50)
        self.assertEqual(latest["startSeq"], 194)
        self.assertEqual(len(latest["tasks"]), 6)

    def test_render_catchup_panel_and_jump(self) -> None:
        script = f"""
const fs = require("fs");
const vm = require("vm");
const code = fs.readFileSync({json.dumps(str(HOUSE_JS))}, "utf8");
const marker = "function roomPanel()";
const slice = code.slice(0, code.indexOf(marker));

function makeEl(tag) {{
  const el = {{
    tagName: tag.toUpperCase(),
    className: "",
    textContent: "",
    children: [],
    listeners: {{}},
    appendChild(c) {{ this.children.push(c); return c; }},
    addEventListener(ev, fn) {{ this.listeners[ev] = fn; }},
    setAttribute(k, v) {{ this[k] = v; }},
    replaceChildren() {{ this.children = []; }},
  }};
  return el;
}}

let rendered = false;
const ctx = vm.createContext({{
  console, Math, Number, Set, Map, Array, Object, String, Boolean, JSON,
  document: {{
    createElement: makeEl,
    getElementById: () => null,
  }},
  window: {{}},
  render() {{ rendered = true; }},
  roomPanel() {{}},
}});
vm.runInContext(slice, ctx);
vm.runInContext(`
  data = {{
    frames: [
      {{ seq: 10, at: 100, event: {{ op: "task", actor: "a", title: "t1" }}, tasks: [{{ id: "t1", title: "Build Parlor", owner: "a", status: "claimed", until: 200, generation: 1 }}], rooms: [{{ id: "parlor", name: "The Parlor", status: "construction" }}], shelf: {{ projects: [] }} }},
      {{ seq: 11, at: 110, event: {{ op: "finish", actor: "a", title: "t1" }}, tasks: [], rooms: [{{ id: "parlor", name: "The Parlor", status: "construction" }}], shelf: {{ projects: [] }} }},
    ]
  }};
  index = 1;
  current = true;
`, ctx);

const root = makeEl("div");
ctx.renderCatchupPanel(root);
const panel = root.children[0];
const note = panel.children[0].textContent;
const list = panel.children.find(c => c.className === "catchup-list");
const jumpBtn = list.children[0].children[1];
jumpBtn.listeners.click();
console.log(JSON.stringify({{ note, rendered }}));
"""
        out = run_node(script)
        self.assertIn("Not a remembered visitor cursor", out["note"])
        self.assertTrue(out["rendered"])


if __name__ == "__main__":
    unittest.main()


