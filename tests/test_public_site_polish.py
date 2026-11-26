"""Tests for Accounts balance legend/target, Shelf summary tags, Chronicle link, and daylight CSS."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PublicSitePolishTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node executes the actual house renderer")
    def test_load_balance_renders_summary_legend_and_target_marker(self):
        source = ROOT / "site/house.js"
        script = r'''
const fs = require("node:fs"), vm = require("node:vm"), assert = require("node:assert/strict");
class Element {
  constructor(tag = "div") {
    this.tag = tag;
    this.children = [];
    this.attrs = {};
    this.style = {};
    this.className = "";
    this.textContent = "";
  }
  appendChild(node) { this.children.push(node); return node; }
  replaceChildren() { this.children = []; }
  setAttribute(k, v) { this.attrs[k] = String(v); }
}
const box = new Element("div");
const document = {
  getElementById: id => (id === "balance" ? box : null),
  querySelector: sel => (sel === "#balance" ? box : null),
  createElement: tag => new Element(tag),
};
const all = n => [n, ...n.children.flatMap(all)];
const text = n => [n.textContent, ...n.children.map(text)].filter(Boolean).join(" ");
const payload = {
  version: 1,
  source_head: "abc123",
  target_building_share: 0.5,
  days: [
    { day: "2026-11-10", building: 100, record: 300, foundations: 0, other: 0, binary_files: 0 },
    { day: "2026-11-14", building: 600, record: 200, foundations: 150, other: 50, binary_files: 2 },
    { day: "2026-11-16", building: 0, record: 0, foundations: 0, other: 0, binary_files: 0 },
  ],
};
const ctx = vm.createContext({
  assert,
  document,
  AbortSignal,
  fetch: async () => ({ ok: true, json: async () => payload }),
});
const source = fs.readFileSync(process.argv[1], "utf8");
const tail = "refresh();\nsetInterval(watch,10000);\n";
assert(source.endsWith(tail));
vm.runInContext(source.slice(0, -tail.length), ctx);
(async () => {
  await ctx.loadBalance("abc123");
  const full = text(box);
  assert.match(full, /Recorded UTC commit dates \(3\): 2026-11-10 to 2026-11-16 · 50% building \(700 of 1,400 lines\) · Steward target: 50%/);
  assert.doesNotMatch(full, /Last 3 days/);
  const legend = all(box).find(n => n.className === "balance-legend");
  assert(legend, "Expected a .balance-legend element");
  for (const [cls, label] of [
    ["seg-building", "Building"],
    ["seg-record", "Record"],
    ["seg-foundations", "Foundations"],
    ["seg-other", "Other"],
  ]) {
    assert(all(legend).some(n => n.className.split(/\s+/).includes(cls)), `Missing legend swatch ${cls}`);
    assert(text(legend).includes(label), `Missing legend label ${label}`);
  }
  const days = all(box).filter(n => n.className === "balance-day");
  assert.equal(days.length, 3);
  assert.match(text(days[0]), /2026-11-16 · 0% building · no text changes/);
  assert.match(text(days[1]), /2026-11-14 · 60% building · meets 50% target/);
  assert.match(text(days[2]), /2026-11-10 · 25% building · below 50% target/);
  const targets = all(box).filter(n => n.className === "balance-target");
  assert.equal(targets.length, 3);
  assert(targets.every(t => t.style.left === "50%"));
  payload.days = [payload.days[0]];
  await ctx.loadBalance("single-date");
  assert.match(text(box), /Recorded UTC commit dates \(1\): 2026-11-10 · 25% building/);
  assert.doesNotMatch(text(box), /Last 1 day|2026-11-16/);
  payload.days = [{ day: "2026-11-10", binary_files: 1 }];
  await ctx.loadBalance("binary-only");
  assert.match(text(box), /Recorded UTC commit dates \(1\): 2026-11-10 · no text line changes/);
  payload.days = [];
  await ctx.loadBalance("empty");
  assert.match(text(box), /No recent committed changes in this window/);
  assert.equal(all(box).filter(n => n.className === "balance-day").length, 0);
})().catch(err => { console.error(err); process.exitCode = 1; });
'''
        result = subprocess.run(
            ["node", "-e", script, str(source)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node executes the actual house renderer")
    def test_shelf_summaries_expose_scale_field_worth_and_brief_status(self):
        source = ROOT / "site/house.js"
        script = r'''
const fs = require("node:fs"), vm = require("node:vm"), assert = require("node:assert/strict");
class Element {
  constructor(tag = "div") {
    this.tag = tag;
    this.children = [];
    this.className = "";
    this.textContent = "";
    this.attrs = {};
  }
  appendChild(node) { this.children.push(node); return node; }
  replaceChildren() { this.children = []; }
  setAttribute(k, v) { this.attrs[k] = String(v); }
}
const root = new Element("div");
const document = { getElementById: () => root, createElement: tag => new Element(tag) };
const all = n => [n, ...n.children.flatMap(all)];
const text = n => [n.textContent, ...n.children.map(text)].filter(Boolean).join(" ");
const ctx = vm.createContext({ assert, document, URL, Intl, Date });
const source = fs.readFileSync(process.argv[1], "utf8");
const tail = "refresh();\nsetInterval(watch,10000);\n";
assert(source.endsWith(tail));
vm.runInContext(source.slice(0, -tail.length), ctx);
vm.runInContext(`
data = { timezone: "UTC" };
current = false;
frame = {
  at: 1000000,
  residents: [{ id: "r1", name: "Yarrow" }],
  shelf: {
    enabled: true,
    policy: "work-selection-004",
    great_wanted: false,
    explorer: null,
    projects: [
      { id: "p1", title: "Review Skein", status: "active", slot: "great", owner: "r1",
        milestone: "Browser try", deadline: 1000000 + 3 * 86400, extended: false },
      { id: "p2", title: "Late Build", status: "active", slot: "small", owner: "r1",
        milestone: "Check", deadline: 1000000 - 3600, extended: false }
    ],
    ideas: [
      { id: "g1", title: "Chorus", status: "shelved", scale: "great", losses: 1, author: "r1", sources: [],
        brief: { field: "software", worth: "enabling", benefit: "B", interest: "I", exists: "E", first_version: "F", check: "C", author: "r1" } },
      { id: "s1", title: "Fieldbook", status: "shelved", scale: "small", losses: 0, author: "r1", brief_due: 1200000,
        brief: { audience: "A", exists: "E", first_version: "F", risks: "R", author: "r1" } },
      { id: "s2", title: "Interval Ear", status: "shelved", losses: 0, author: "r1", brief_due: 1200000 }
    ]
  }
};
shelf();
`, ctx);
const summaries = all(root).filter(n => n.tag === "summary" && all(n).some(c => c.className === "shelf-idea-tags"));
assert.equal(summaries.length, 3, "Every shelved idea summary must include .shelf-idea-tags");
assert.equal(summaries.flatMap(all).filter(n => n.tag === "a").length, 0);
assert.match(text(summaries[0]), /Chorus.*Great work.*Software.*Enabling.*Researched/);
assert.match(text(summaries[1]), /Fieldbook.*Small project.*Renew brief/);
assert.match(text(summaries[2]), /Interval Ear.*Small project.*Needs brief/);
const shelfText = text(root);
assert.match(shelfText, /3d left/);
assert.match(shelfText, /past deadline/);
'''
        result = subprocess.run(
            ["node", "-e", script, str(source)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node executes the actual house renderer")
    def test_chronicle_is_registered_and_allowed_by_collection_url(self):
        manifest = json.loads((ROOT / "site/projects.json").read_text())
        chronicle = next((p for p in manifest["projects"] if p["id"] == "emberhall-chronicle-room"), None)
        self.assertIsNotNone(chronicle)
        self.assertEqual(chronicle["category"], "house-tool")
        self.assertEqual(chronicle["action"], "Open")
        self.assertEqual(chronicle["href"], "chronicle/index.html")
        self.assertEqual(chronicle["files"], [])
        source = ROOT / "site/house.js"
        script = r'''
const fs = require("node:fs"), vm = require("node:vm"), assert = require("node:assert/strict");
const document = { getElementById: () => null, querySelector: () => null };
const ctx = vm.createContext({ assert, document });
const source = fs.readFileSync(process.argv[1], "utf8");
const tail = "refresh();\nsetInterval(watch,10000);\n";
assert(source.endsWith(tail));
vm.runInContext(source.slice(0, -tail.length), ctx);
const entry = JSON.parse(process.argv[2]);
assert.equal(ctx.collectionUrl(entry), "chronicle/index.html");
assert.equal(ctx.collectionUrl({ ...entry, href: "chronicle/../index.html" }), null);
assert.equal(ctx.collectionUrl({ ...entry, category: "creation" }), null);
'''
        result = subprocess.run(
            ["node", "-e", script, str(source), json.dumps(chronicle)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_css_uses_theme_variables_and_defines_balance_and_shelf_styles(self):
        css = (ROOT / "site/house.css").read_text()
        for selector in (".shelf-item", ".shelf-brief", ".catchup-panel", ".catchup-controls input", ".vote-round"):
            match = re.search(re.escape(selector) + r"\s*\{[^}]*\}", css)
            self.assertIsNotNone(match, f"Missing CSS rule for {selector}")
            block = match.group(0)
            self.assertNotRegex(block, r"rgba\(\s*255\s*,\s*255\s*,\s*255", f"Dark-only rgba white in {selector}")
            self.assertNotRegex(block, r"rgba\(\s*0\s*,\s*0\s*,\s*0", f"Dark-only rgba black in {selector}")
        for required in (".balance-summary", ".balance-legend", ".balance-bar-wrap", ".balance-target", ".shelf-idea-tags", ".shelf-tag"):
            self.assertIn(required, css)


if __name__ == "__main__":
    unittest.main()
