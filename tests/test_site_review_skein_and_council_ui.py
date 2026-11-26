"""Tests for Review Skein active sample integration, Council UI polish, and desktop layout."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOUSE_JS = ROOT / "site" / "house.js"
HOUSE_CSS = ROOT / "site" / "house.css"
INDEX_HTML = ROOT / "site" / "index.html"
PROJECTS_JSON = ROOT / "site" / "projects.json"


class SiteReviewSkeinAndCouncilUITests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node executes the actual house renderer")
    def test_review_skein_sample_registered_and_active_project_links_safely(self):
        manifest = json.loads(PROJECTS_JSON.read_text())
        skein = next((p for p in manifest["projects"] if p["id"] == "review-skein"), None)
        self.assertIsNotNone(skein, "Expected review-skein entry in site/projects.json")
        self.assertEqual(skein["category"], "creation")
        self.assertEqual(skein["action"], "Open")
        self.assertEqual(skein["href"], "projects/review-skein/sample/milestone-2-mixed/review.html")
        self.assertIn("projects/review-skein/sample/milestone-2/review.html", skein["files"])
        for rel in skein["files"]:
            self.assertTrue((ROOT / rel).is_file(), f"Missing published sample file: {rel}")

        script = r'''
const fs = require("node:fs"), vm = require("node:vm"), assert = require("node:assert/strict");
class Element {
  constructor(tag = "div") {
    this.tag = tag; this.children = []; this.attrs = {}; this.style = {};
    this.className = ""; this.textContent = ""; this.id = ""; this.href = "";
  }
  appendChild(node) { this.children.push(node); return node; }
  replaceChildren() { this.children = []; }
  setAttribute(k, v) { this.attrs[k] = String(v); if (k === "id") this.id = String(v); }
  addEventListener() {}
}
const nodes = {};
const document = {
  getElementById: id => (nodes[id] || (nodes[id] = new Element("div"))),
  querySelector: sel => (sel === "#creations-card" ? nodes["creations-card"] || (nodes["creations-card"] = new Element("section")) : null),
  createElement: tag => new Element(tag),
};
const all = n => [n, ...n.children.flatMap(all)];
const text = n => [n.textContent, ...n.children.map(text)].filter(Boolean).join(" ");
const manifest = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const ctx = vm.createContext({ assert, document, URL, Intl, Date, AbortSignal, fetch: async () => ({ ok: true, json: async () => manifest }) });
const source = fs.readFileSync(process.argv[1], "utf8");
const tail = "refresh();\nsetInterval(watch,10000);\n";
assert(source.endsWith(tail));
vm.runInContext(source.slice(0, -tail.length), ctx);
(async () => {
  await ctx.loadCatalog("head-1");
  const skein = manifest.projects.find(p => p.id === "review-skein");
  assert.equal(ctx.collectionUrl(skein), "projects/review-skein/sample/milestone-2-mixed/review.html");
  for (const bad of [
    "projects/review-skein/sample/../secret.html",
    "projects/review-skein/sample/review.html?x=1",
    "projects/review-skein/sample/review.html#top",
    "projects/review-skein/sample/review.js",
    "projects/review-skein/%2e%2e/review.html",
    "https://evil.test/projects/review-skein/review.html",
  ]) {
    assert.equal(ctx.collectionUrl({ ...skein, href: bad }), null, `Unsafe href must be rejected: ${bad}`);
  }
  vm.runInContext(`
    data = { timezone: "UTC" };
    current = true;
    frame = {
      at: 1000000,
      residents: [{ id: "r1", name: "Yarrow" }],
      rooms: [],
      shelf: {
        enabled: true,
        policy: "work-selection-004",
        projects: [
          { id: "great-work-choice-001", idea: "review-skein", title: "Review Skein",
            status: "active", slot: "great", owner: "r1", stage: 1,
            milestones: [
              { milestone: "Packet and anchors", seconds: 604800 },
              { milestone: "Use the packet", seconds: 864000 }
            ],
            completed: [{ stage: 0, sequence: 8577, evidence: "m1" }],
            deadline: 1000000 + 86400 }
        ],
        ideas: []
      }
    };
    renderCollection();
    shelf();
  `, ctx);
  const creations = nodes.creations;
  assert.equal(all(creations).filter(n => n.tag === "a" && n.href === "projects/review-skein/sample/milestone-2-mixed/review.html").length, 0,
    "Active projects must not appear as Completed in Made here");
  const toolsGrid = all(creations).find(n => n.className && n.className.includes("house-tools-grid"));
  assert(!toolsGrid, "No tools rendered when none are completed");

  const shelfBox = nodes.shelf;
  const links = all(shelfBox).filter(n => n.tag === "a");
  assert(links.some(a => a.href === "projects/review-skein/sample/milestone-2-mixed/review.html" && /Open Review Skein sample/i.test(a.textContent)),
    "Expected active Review Skein card to surface sample packet link when current");
  assert(links.some(a => a.href === "https://github.com/Someblueman/emberhall/blob/main/projects/review-skein/README.md" && /Read guide/i.test(a.textContent)),
    "Expected active Review Skein card to surface guide link when current");

  // Historical frames must not show current sample links on active projects
  vm.runInContext(`current = false; shelf();`, ctx);
  const histLinks = all(nodes.shelf).filter(n => n.tag === "a");
  assert.equal(histLinks.length, 0, "Historical frame must not emit current sample links on active project");

  // Completed house-tools wrap cards in responsive grid inside collapsed details
  vm.runInContext(`
    current = true;
    frame.shelf.projects.push({ id: "t1", idea: "wake-digest", title: "Wake Digest", status: "done", owner: "r1" });
    renderCollection();
  `, ctx);
  const toolDetails = all(nodes.creations).find(n => n.tag === "details" && n.className === "house-tools");
  assert(toolDetails && !toolDetails.open);
  assert(all(toolDetails).some(n => n.className && n.className.includes("house-tools-grid")),
    "House-tool cards should sit inside .house-tools-grid");
})().catch(err => { console.error(err); process.exitCode = 1; });
'''
        result = subprocess.run(
            ["node", "-e", script, str(HOUSE_JS), str(PROJECTS_JSON)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node executes the actual house renderer")
    def test_council_view_renovation_copy_tags_and_active_banner(self):
        script = r'''
const fs = require("node:fs"), vm = require("node:vm"), assert = require("node:assert/strict");
class Element {
  constructor(tag = "div") {
    this.tag = tag; this.children = []; this.attrs = {}; this.style = {};
    this.className = ""; this.textContent = ""; this.id = ""; this.value = "";
  }
  appendChild(node) { this.children.push(node); return node; }
  replaceChildren() { this.children = []; }
  setAttribute(k, v) { this.attrs[k] = String(v); if (k === "id") this.id = String(v); }
  querySelectorAll(sel) {
    return this.children.flatMap(n => [n, ...n.querySelectorAll(sel)]).filter(n => n.tag === "details" && (sel !== "details[open]" || n.open));
  }
}
const root = new Element("section");
const document = { getElementById: () => root, createElement: tag => new Element(tag) };
const all = n => [n, ...n.children.flatMap(all)];
const text = n => [n.textContent, ...n.children.map(text)].filter(Boolean).join(" ");
const visible = n => n.tag === "details" && !n.open
  ? [n.textContent, ...(n.children[0] ? [visible(n.children[0])] : [])].join(" ")
  : [n.textContent, ...n.children.map(visible)].join(" ");
const ctx = vm.createContext({ assert, document, URL, Intl, Date });
const source = fs.readFileSync(process.argv[1], "utf8");
const tail = "refresh();\nsetInterval(watch,10000);\n";
assert(source.endsWith(tail));
vm.runInContext(source.slice(0, -tail.length), ctx);
vm.runInContext(`
  data = { timezone: "UTC" };
  current = false;
  const aster = { name: "Aster", agent: "codex", id: "resident-aster" };
  const yarrow = { name: "Yarrow", agent: "agy", id: "resident-yarrow" };
  frame = {
    at: 10000,
    voting: {
      inbox_checked_at: 9900,
      choices: [
        { id: "choice-open-secret", status: "open", owner: aster, opened_sequence: 10, selection_version: 3,
          candidates: [{ id: "idea-1", title: "Idea One", author: yarrow, milestone: "M1", seconds: 86400 }],
          votes: [] }
      ],
      proposals: [
        { id: "prop-stale-secret", title: "Old rule", mode: "rule", author: aster, status: "pending", stale: true,
          reason: "Old", text: "Text", trial: null, endorsements: [], notice: null },
        { id: "prop-reno-secret", title: "Restore checkpoints", mode: "renovation", author: aster, status: "pending", stale: false,
          reason: "Bundle bound", text: "JSON", trial: { task: "t1", evidence: "ok" },
          endorsements: [{ resident: yarrow, reason: "Checked", at: 200 }],
          notice: { url: "https://github.com/Someblueman/emberhall/issues/1", at: 5000, until: 8600 } },
        { id: "prop-wake-secret", title: "Wake brief", mode: "wake-prompt", author: yarrow, status: "pending", stale: false,
          reason: "Wake", text: "Prompt", trial: { task: "t2", evidence: "ok" },
          endorsements: [], notice: { url: "https://github.com/Someblueman/emberhall/issues/1", at: 9000, until: 95400 } }
      ]
    }
  };
  voting();
`, ctx);
const full = text(root);
assert.match(full, /1 hour/i, "Bell explanation should reflect 1-hour renovation window");
assert.match(full, /24-hour/i, "Bell explanation should keep 24-hour rule/wake-prompt window");
const banner = all(root).find(n => n.className && n.className.includes("vote-summary-banner"));
assert(banner, "Expected .vote-summary-banner when active choice or pending proposals exist");
assert.match(text(banner), /1 open project choice/);
assert.match(text(banner), /2 pending proposals/);
assert.match(text(banner), /1 with the notice period over/);
assert.doesNotMatch(text(banner), /elapsed/i);
const vis = visible(root);
assert.doesNotMatch(vis, /choice-open-secret|prop-stale-secret|prop-reno-secret|prop-wake-secret/,
  "Raw record IDs must never leak outside closed details");
const renoSummary = all(root).find(n => n.id === "vote-rule-prop-reno-secret").children[0];
assert(all(renoSummary).some(n => n.className && n.className.includes("vote-tags")),
  "Proposal summary should carry .vote-tags pills");
assert.match(text(renoSummary), /Renovation/);
assert.match(text(renoSummary), /Ready to enact/);
assert.doesNotMatch(text(renoSummary), /window elapsed/i);
const wakeSummary = all(root).find(n => n.id === "vote-rule-prop-wake-secret").children[0];
assert.match(text(wakeSummary), /Wake prompt/);
assert.match(text(wakeSummary), /Notice active/);
const staleSummary = all(root).find(n => n.id === "vote-rule-prop-stale-secret").children[0];
assert.match(text(staleSummary), /Closed/);
'''
        result = subprocess.run(
            ["node", "-e", script, str(HOUSE_JS)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_desktop_layout_styles_and_asset_cache_params(self):
        css = HOUSE_CSS.read_text()
        self.assertIn(".house-layout.room-open .room-card", css)
        self.assertIn("#budgets", css)
        self.assertIn(".vote-tags", css)
        self.assertIn(".vote-summary-banner", css)
        self.assertIn(".shelf-project-actions", css)
        index = INDEX_HTML.read_text()
        self.assertEqual(index.count("?v=choice-progress-1"), 2)
        self.assertIn("skein=2", index)
