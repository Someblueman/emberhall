"""Tests for room resident run-history and stopped-resident disclosure touch targets (R54)."""
from pathlib import Path
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


def rule_declarations(css: str, selector: str) -> str:
    pattern = re.compile(
        r"(?:^|\n)\s*" + re.escape(selector) + r"\s*\{([^}]*)\}",
        re.MULTILINE,
    )
    matches = pattern.findall(css)
    return "\n".join(matches)


class ResidentHistoryTargetTests(unittest.TestCase):
    def test_resident_history_and_remembered_summaries_have_44px_touch_targets(self):
        css = (ROOT / "site/house.css").read_text(encoding="utf-8")
        body = rule_declarations(css, ".resident-history summary, .remembered-residents summary")
        self.assertTrue(body, "Expected .resident-history summary, .remembered-residents summary rule in site/house.css")
        self.assertRegex(body, r"min-height\s*:\s*44px\b")
        self.assertRegex(body, r"padding\s*:\s*14px\s+0\b")
        self.assertRegex(body, r"cursor\s*:\s*pointer\b")
        self.assertRegex(body, r"color\s*:\s*var\(--gold\)")
        self.assertNotRegex(
            body,
            r"display\s*:\s*(?:flex|inline-flex|grid|block)\b",
            "Summary should preserve native list-item disclosure marker",
        )

    def test_resident_history_and_remembered_summaries_have_gold_focus_outline(self):
        css = (ROOT / "site/house.css").read_text(encoding="utf-8")
        focus_body = rule_declarations(
            css,
            ".resident-history summary:focus-visible, .remembered-residents summary:focus-visible",
        )
        self.assertTrue(
            focus_body,
            "Expected focus-visible rule for .resident-history summary and .remembered-residents summary",
        )
        self.assertRegex(focus_body, r"outline\s*:\s*2px\s+solid\s+var\(--gold\)")
        self.assertRegex(focus_body, r"outline-offset\s*:\s*3px\b")

    @unittest.skipUnless(shutil.which("node"), "node is required")
    def test_room_panel_renders_resident_history_and_remembered_disclosures(self):
        script = r"""
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
class Element {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this.attrs = {};
    this.style = {};
    this.dataset = {};
    this.textContent = "";
    this.className = "";
    this.listeners = {};
    this.classList = { toggle() {}, add() {}, remove() {} };
  }
  appendChild(n) { this.children.push(n); return n; }
  replaceChildren(...nodes) { this.children = [...nodes]; }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  removeAttribute(k) { delete this.attrs[k]; }
  addEventListener(k, fn) { this.listeners[k] = fn; }
}
const nodes = {};
const get = id => (nodes[id] || (nodes[id] = new Element("div")));
const document = {
  getElementById: get,
  querySelector: () => null,
  createElement: t => new Element(t),
  createElementNS: (_, t) => new Element(t),
};
const all = n => [n, ...n.children.flatMap(all)];
const ctx = vm.createContext({ assert, document, all, URL, Intl, Date, Math, Number, String, Set, Map, Object, Array });
const source = fs.readFileSync(process.argv[1], "utf8");
const tail = "refresh();\nsetInterval(watch,10000);\n";
assert(source.endsWith(tail));
vm.runInContext(source.slice(0, -tail.length), ctx);
vm.runInContext(`
data = {
  timezone: "UTC",
  observed_at: 1000,
  name: "Emberhall",
  journal_head: "abc",
  commits: [],
  frames: [{
    seq: 10,
    at: 1000,
    event: { op: "wake", actor: "r1" },
    rooms: [{ id: "archive", name: "The Archive", status: "open", floor: 0 }],
    residents: [
      { id: "r1", name: "Gorse", agent: "agy", model: "gemini-4-argon-high", presence: "recorded awake", pose: "standing", room: "archive" },
      { id: "r2", name: "Mica", agent: "codex", presence: "unconfirmed", pose: "unconfirmed", room: "archive" }
    ],
    tasks: [],
    lessons: 2,
    council: { pending: 0 },
    ambitions: [],
    runs: [
      { id: "run-11112222", resident: "r1", agent: "agy", start: 900, end: 980, sequence: 5, last_sequence: 9, status: "ended", outcome: "success" }
    ],
    budgets: [],
    scars: [],
    shelf: { enabled: false, projects: [], ideas: [] }
  }]
};
index = 0;
frame = data.frames[0];
current = true;
selected = "archive";
roomPanel();
const content = document.getElementById("room-content");
const details = all(content).filter(n => n.tag === "details");
const histories = details.filter(n => n.className === "resident-history");
const remembered = details.filter(n => n.className === "remembered-residents");
assert.equal(histories.length, 2, "Expected resident-history details for both awake and remembered residents");
assert.equal(remembered.length, 1, "Expected remembered-residents disclosure when stopped residents exist");
assert.equal(histories[0].children[0].tag, "summary");
assert.equal(histories[0].children[0].textContent, "1 recorded run");
assert.equal(remembered[0].children[0].tag, "summary");
assert.equal(remembered[0].children[0].textContent, "Remembered here · 1 stopped resident");
`, ctx);
"""
        result = subprocess.run(
            [shutil.which("node"), "-e", script, str(ROOT / "site/house.js")],
            capture_output=True,
            text=True,
            timeout=15,
            stdin=subprocess.DEVNULL,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
