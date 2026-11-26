"""Tests for Council room panel, Council status/kind filters, and renovation formatting."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOUSE_JS = ROOT / "site" / "house.js"
HOUSE_CSS = ROOT / "site" / "house.css"
INDEX_HTML = ROOT / "site" / "index.html"

HARNESS = r"""
const fs = require("node:fs"), vm = require("node:vm"), assert = require("node:assert/strict");
const all = n => [n, ...n.children.flatMap(all)];
const text = n => [n.textContent, ...n.children.map(text)].filter(Boolean).join(" ");
const visible = n => n.tag === "details" && !n.open
  ? [n.textContent, ...(n.children[0] ? [visible(n.children[0])] : [])].filter(Boolean).join(" ")
  : [n.textContent, ...n.children.map(visible)].filter(Boolean).join(" ");
class Element {
  constructor(tag, id = "") {
    this.tag = tag; this.id = id; this.children = []; this.textContent = "";
    this.className = ""; this.value = ""; this.attrs = {}; this.listeners = {};
    this.dataset = {}; this.style = {}; this.href = "";
    this.classList = { toggle() {}, add() {}, remove() {} };
  }
  appendChild(node) { this.children.push(node); return node; }
  replaceChildren() {
    if (all(this).includes(document.activeElement)) document.activeElement = document.body;
    this.children = [];
  }
  set innerHTML(_v) { throw new Error("Use safe DOM text, never innerHTML"); }
  setAttribute(k, v) { this.attrs[k] = String(v); if (k === "id") this.id = String(v); }
  removeAttribute(k) { delete this.attrs[k]; }
  addEventListener(name, fn) { (this.listeners[name] ??= []).push(fn); }
  dispatch(name) { for (const fn of (this.listeners[name] || [])) fn(); }
  focus() { if (!this.disabled) document.activeElement = this; }
  setSelectionRange(start, end, direction) {
    this.selectionStart = start; this.selectionEnd = end; this.selectionDirection = direction;
  }
  querySelectorAll(selector) {
    return this.children.flatMap(n => [n, ...n.querySelectorAll(selector)])
      .filter(n => n.tag === "details" && (selector !== "details[open]" || n.open));
  }
}
const nodes = {
  voting: new Element("section", "voting"),
  "room-content": new Element("div", "room-content"),
  "room-kicker": new Element("div", "room-kicker"),
  "room-title": new Element("h2", "room-title"),
  "room-description": new Element("p", "room-description"),
  "room-context": new Element("p", "room-context"),
};
const document = {
  body: new Element("body"),
  activeElement: null,
  getElementById(id) {
    for (const root of Object.values(nodes)) {
      const found = all(root).find(n => n.id === id);
      if (found) return found;
    }
    if (id.startsWith("voting-")) return null;
    return nodes[id] || (nodes[id] = new Element("div", id));
  },
  createElement: tag => new Element(tag),
  createElementNS: (_ns, tag) => new Element(tag),
  querySelectorAll: () => [],
};
const byId = (root, id) => all(root).find(n => n.id === id);
const context = vm.createContext({ assert, document, URL, Intl, Date, nodes, text, visible, all, byId });
const source = fs.readFileSync(process.argv[1], "utf8");
const tail = "refresh();\nsetInterval(watch,10000);\n";
assert(source.endsWith(tail));
vm.runInContext(source.slice(0, -tail.length), context);
"""


@unittest.skipUnless(shutil.which("node"), "Node is needed for the actual renderer")
class CouncilRoomAndFiltersTests(unittest.TestCase):
    def run_renderer(self, code: str) -> None:
        script = HARNESS + "\nvm.runInContext(" + json.dumps(code) + ", context);"
        result = subprocess.run(
            [shutil.which("node"), "-e", script, str(HOUSE_JS)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_council_room_panel_renders_live_decisions_without_raw_ids(self):
        self.run_renderer(r"""
const aster = { name: "Aster", agent: "codex", id: "resident-aster" };
const yarrow = { name: "Yarrow", agent: "agy", id: "resident-yarrow" };
const vesper = { name: "Vesper", agent: "muse", id: "resident-vesper" };
data = { timezone: "UTC", frames: [] };
current = true;
selectedFloor = 0;
selected = "council";
frame = {
  seq: 9900,
  at: 10000,
  residents: [aster, yarrow, vesper].map(r => ({ ...r, room: "council", pose: "standing", presence: "recorded awake" })),
  rooms: [{ id: "council", name: "The Council", status: "open", floor: 0, purpose: "Decide together." }],
  tasks: [],
  scars: [],
  runs: [],
  council: { pending: 3, enacted: 2 },
  voting: {
    inbox_checked_at: 9950,
    choices: [
      {
        id: "choice-secret-open",
        status: "open",
        slot: "great",
        owner: aster,
        opened_sequence: 9000,
        selection_version: 3,
        candidates: [
          { id: "idea-1", title: "Review Skein", author: yarrow, milestone: "M1", seconds: 86400 },
          { id: "idea-2", title: "Signal Garden", author: vesper, milestone: "M1", seconds: 86400 },
        ],
        votes: [
          { resident: aster, idea: "idea-1", counted: true, reason: "Useful", sequence: 9001, at: 9100 },
        ],
      },
    ],
    proposals: [
      {
        id: "prop-stale-hidden-id",
        title: "Old stale proposal",
        mode: "rule",
        author: aster,
        status: "pending",
        stale: true,
        reason: "Superseded base",
        text: "Old rule",
        trial: null,
        endorsements: [],
        notice: null,
      },
      {
        id: "prop-reno-pending-id",
        title: "Combined checkpoint and 404 renovation",
        mode: "renovation",
        author: vesper,
        status: "pending",
        stale: false,
        reason: "Unblock checkpoints",
        text: JSON.stringify({
          source_commit: "408c6d4268cc51fd404fd2f979e1767f452b9450",
          files: {
            "house/checkpoint.py": "c763702cd07c32cccdb50326c0a1dc4bdaa549bd69437169a15011f701c46b38",
            "house/publish.py": "191155992fb9d03f879532d721a87bd7df66ac85a1c36973d252ae783dfdf247",
          },
          summary: "Install checkpoint bound and 404 publisher together",
        }),
        trial: { task: "t-trial", evidence: "Tests passed" },
        endorsements: [
          { resident: aster, reason: "Verified", at: 2000 },
          { resident: yarrow, reason: "Verified", at: 2500 },
        ],
        notice: { url: "https://github.com/Someblueman/emberhall/issues/1", at: 3000, until: 6600 },
      },
      {
        id: "prop-reno-approved-id",
        title: "Body great-work projection",
        mode: "renovation",
        author: aster,
        status: "enacted",
        rule_status: "approved",
        stale: false,
        reason: "Expose great work fields",
        text: JSON.stringify({
          source_commit: "a6837d9fabe5b5cc08555ed096c6f3291920dabe",
          files: { "house/body.py": "6925cf624e90b455f73b3de7a075ac2e95dbaa40ffe9b3b9e51e3d7df4e0f0b0" },
          summary: "Expose great work fields",
        }),
        trial: { task: "t-body", evidence: "Tests passed" },
        endorsements: [
          { resident: yarrow, reason: "OK", at: 1000 },
          { resident: vesper, reason: "OK", at: 1100 },
        ],
        notice: { url: "https://github.com/Someblueman/emberhall/issues/1", at: 1200, until: 4800 },
      },
      {
        id: "prop-rule-active-id",
        title: "Work selection 004",
        mode: "rule",
        author: aster,
        status: "enacted",
        rule_status: "active",
        stale: false,
        reason: "Great work slot",
        text: "Rule text",
        trial: { task: "t-rule", evidence: "Passed" },
        endorsements: [
          { resident: yarrow, reason: "OK", at: 500 },
          { resident: vesper, reason: "OK", at: 600 },
        ],
        notice: null,
      },
    ],
  },
};
roomPanel();
const panel = nodes["room-content"];
const vis = visible(panel);
assert(byId(panel, "council-room-panel"), "Expected .council-room-panel inside Council room");
assert.match(vis, /Great work choice/i);
assert.match(vis, /1\/3 counted votes/);
assert.match(vis, /Review Skein/);
assert.match(vis, /Combined checkpoint and 404 renovation/);
assert.match(vis, /2\/2 endorsements/);
assert.match(vis, /Ready to enact/);
assert.doesNotMatch(vis, /window elapsed/i);
// Each proposal says what it waits for; the one that can be enacted says so and comes first.
assert.match(vis, /Ready: any resident can enact it/);
assert(vis.indexOf("Ready: any resident can enact it") < vis.indexOf("Enacted: waiting to be installed"));
assert.match(vis, /Overtaken by a later decision · 1/);
const folded = all(panel).find(n => n.tag === "details" && /Overtaken by a later decision/.test(n.children[0]?.textContent || ""));
assert(folded && !folded.open, "Overtaken proposals are folded away");
assert.match(text(folded), /Old stale proposal/);
assert.match(folded.children.find(n => n.className?.includes("council-room-list")).children[0].className, /council-quiet/);
assert.match(vis, /Body great-work projection/);
assert.match(vis, /Awaiting install/i);
assert.match(vis, /1 active rule/i);
assert.doesNotMatch(vis, /Old stale proposal/, "Stale proposals should not clutter the live Council room summary");
assert.doesNotMatch(vis, /choice-secret-open|prop-stale-hidden-id|prop-reno-pending-id|prop-reno-approved-id|prop-rule-active-id/,
  "Raw record IDs must not appear in uncollapsed Council room text");
const link = all(panel).find(n => n.tag === "a" && n.href === "#voting-card");
assert(link, "Expected link to #voting-card in Council room");

// Fallback when frame.voting is absent in very early snapshots
frame.voting = null;
roomPanel();
assert.doesNotMatch(text(nodes["room-content"]), /undefined|NaN/);
assert(all(nodes["room-content"]).some(n => n.tag === "a" && n.href === "#voting-card"));
""")

    def test_pending_proposal_says_what_it_waits_for(self):
        self.run_renderer(r"""
data = { timezone: "UTC", frames: [] };
const person = { name: "Aster", agent: "codex", id: "resident-aster" };
const endorse = n => Array.from({ length: n }, (_, i) => ({ resident: person, reason: "ok", at: i }));
const trial = { task: "t", evidence: "ran it" };
const waitLine = (proposal, now = 1000) => proposalWaitingLine({ status: "pending", stale: false, mode: "rule", ...proposal }, now);
assert.equal(waitLine({ trial: null, endorsements: [] }).text, "Needs a trial");
assert.equal(waitLine({ trial, endorsements: [] }).text, "Needs 2 more endorsements from residents who did not write it");
assert.equal(waitLine({ trial, endorsements: endorse(1) }).text, "Needs 1 more endorsement from residents who did not write it");
assert.equal(waitLine({ trial, endorsements: endorse(2), notice: null }).text, "Needs its public notice");
assert.match(waitLine({ trial, endorsements: endorse(2), notice: { at: 0, until: 5000 } }).text, /^Notice window open until /);
const ready = waitLine({ trial, endorsements: endorse(2), notice: { at: 0, until: 500 } });
assert.equal(ready.text, "Ready: any resident can enact it");assert.equal(ready.key, "ready");
assert.equal(waitLine({ stale: true, closure: { how: "replaced", by: "x" } }).text, "Overtaken by a later decision");
assert.equal(waitLine({ status: "enacted", rule_status: "approved" }).text, "Enacted: waiting to be installed");
assert.equal(waitLine({ status: "enacted", rule_status: "active" }), null);
// The same wording leads each proposal's heading in the voting card, which lists overtaken ones last.
frame = { seq: 5, at: 1000, residents: [], rooms: [], tasks: [], ambitions: [], runs: [], scars: [],
  voting: { choices: [], proposals: [
    { id: "p-old", title: "Old", mode: "rule", author: person, status: "pending", stale: true, closure: { how: "lapsed", by: null }, trial: null, endorsements: [], notice: null, text: "t", reason: "r" },
    { id: "p-new", title: "New", mode: "rule", author: person, status: "pending", stale: false, trial: null, endorsements: [], notice: null, text: "t", reason: "r" },
  ] } };
current = false;
voting();
const titles = all(nodes.voting).filter(n => n.className === "vote-summary-title").map(n => n.textContent);
assert.equal(titles.join("|"), "New · Needs a trial|Old · Closed · the rules changed before it was enacted");
assert(all(nodes.voting).some(n => n.tag === "details" && n.id === "vote-rule-p-old" && /council-quiet/.test(n.className)));
""")

    def test_council_view_status_and_kind_filters_clear_and_focus(self):
        self.run_renderer(r"""
const aster = { name: "Aster", agent: "codex", id: "resident-aster" };
const yarrow = { name: "Yarrow", agent: "agy", id: "resident-yarrow" };
const frameData = {
  seq: 12,
  at: 10000,
  event: { actor: aster.id, op: "council-propose" },
  residents: [aster, yarrow],
  rooms: [],
  tasks: [],
  ambitions: [],
  runs: [],
  scars: [],
  voting: {
    inbox_checked_at: 9900,
    choices: [
      {
        id: "choice-open", status: "open", owner: aster, opened_sequence: 10, selection_version: 3,
        candidates: [{ id: "idea-1", title: "Open Candidate", author: yarrow, milestone: "M1", seconds: 86400 }],
        votes: [],
      },
      {
        id: "choice-closed", status: "closed", winner: "idea-2", owner: yarrow, opened_sequence: 5, selection_version: 2,
        candidates: [{ id: "idea-2", title: "Closed Winner", author: aster, milestone: "M1", seconds: 86400 }],
        votes: [],
      },
    ],
    proposals: [
      {
        id: "prop-reno-pending", title: "Pending Renovation", mode: "renovation", author: aster,
        status: "pending", stale: false, reason: "Fix checkpoint", text: "JSON",
        trial: { task: "t1", evidence: "ok" }, endorsements: [], notice: null,
      },
      {
        id: "prop-reno-installed", title: "Installed Renovation", mode: "renovation", author: yarrow,
        status: "enacted", rule_status: "installed", stale: false, reason: "Already live", text: "JSON",
        trial: { task: "t2", evidence: "ok" }, endorsements: [], notice: null,
      },
      {
        id: "prop-rule-active", title: "Active Rule", mode: "rule", author: aster,
        status: "enacted", rule_status: "active", stale: false, reason: "Governance", text: "Rule wording",
        trial: { task: "t3", evidence: "ok" }, endorsements: [], notice: null,
      },
      {
        id: "prop-wake-stale", title: "Stale Wake", mode: "wake-prompt", author: yarrow,
        status: "pending", stale: true, reason: "Old base", text: "Wake wording",
        trial: null, endorsements: [], notice: null,
      },
    ],
  },
};
data = { timezone: "UTC", frames: [frameData], commits: [], observed_at: 10000, journal_head: "abcdef123456", source_head: "123456abcdef" };
frame = frameData;
index = 0;
current = true;
votingState.query = "";
votingState.status = "all";
votingState.kind = "all";
floorControls = renderViewContext = drawHouse = roomPanel = dormControls = accounts = shelf = renderCollection = renderResidentPulse = renderRecentGrowth = renderLately = lighting = () => {};
voting();

const root = nodes.voting;
const statusSel = byId(root, "voting-status");
const kindSel = byId(root, "voting-kind");
const clearBtn = byId(root, "voting-clear");
assert(statusSel && kindSel && clearBtn);
assert.equal(clearBtn.disabled, true);

// Filter by Needs action (open / pending non-stale)
byId(root, "vote-rule-prop-reno-pending").open = true;
statusSel.value = "action";
statusSel.dispatch("change");
let rendered = text(root);
assert.match(rendered, /1 of 2 choices/);
assert.match(rendered, /1 of 4 proposals/);
assert.match(rendered, /Open Candidate/);
assert.match(rendered, /Pending Renovation/);
assert.doesNotMatch(rendered, /Installed Renovation|Active Rule|Stale Wake|Closed Winner/);
assert.equal(clearBtn.disabled, false);
assert.equal(byId(root, "vote-rule-prop-reno-pending").open, true, "Open card state should survive status filtering");

// Filter by Active & installed
statusSel.value = "enacted";
statusSel.dispatch("change");
rendered = text(root);
assert.match(rendered, /Installed Renovation/);
assert.match(rendered, /Active Rule/);
assert.doesNotMatch(rendered, /Pending Renovation|Stale Wake/);

// Filter by Stale, superseded or closed
statusSel.value = "historical";
statusSel.dispatch("change");
rendered = text(root);
assert.match(rendered, /Closed Winner/);
assert.match(rendered, /Stale Wake/);
assert.doesNotMatch(rendered, /Pending Renovation|Installed Renovation|Active Rule/);

// Filter by kind = renovation with status = all
statusSel.value = "all";
statusSel.dispatch("change");
kindSel.value = "renovation";
kindSel.dispatch("change");
rendered = text(root);
assert.match(rendered, /0 of 2 choices/);
assert.match(rendered, /2 of 4 proposals/);
assert.match(rendered, /Pending Renovation/);
assert.match(rendered, /Installed Renovation/);
assert.doesNotMatch(rendered, /Active Rule|Stale Wake/);

// Focus preservation across refreshView(true)
kindSel.focus();
refreshView(true);
const nextKindSel = byId(root, "voting-kind");
assert.notEqual(nextKindSel, kindSel);
assert.equal(document.activeElement, nextKindSel);
assert.equal(nextKindSel.value, "renovation");

// Clear resets query, status, and kind
byId(root, "voting-clear").dispatch("click");
rendered = text(root);
assert.equal(votingState.status, "all");
assert.equal(votingState.kind, "all");
assert.equal(votingState.query, "");
assert.equal(byId(root, "voting-clear").disabled, true);
assert.match(rendered, /2 of 2 choices/);
assert.match(rendered, /4 of 4 proposals/);
assert.equal(byId(root, "vote-rule-prop-reno-pending").open, true);
""")

    def test_renovation_and_floor_descriptors_render_human_details_and_install_tags(self):
        self.run_renderer(r"""
const aster = { name: "Aster", agent: "codex", id: "resident-aster" };
data = { timezone: "UTC" };
current = false;
votingState.query = "";
votingState.status = "all";
votingState.kind = "all";
frame = {
  at: 10000,
  voting: {
    inbox_checked_at: 9900,
    choices: [],
    proposals: [
      {
        id: "combined-checkpoint-publish-001",
        title: "Install checkpoint bound and 404 publisher",
        mode: "renovation",
        author: aster,
        status: "enacted",
        rule_status: "approved",
        stale: false,
        reason: "Fix both together",
        text: JSON.stringify({
          source_commit: "408c6d4268cc51fd404fd2f979e1767f452b9450",
          files: {
            "house/checkpoint.py": "c763702cd07c32cccdb50326c0a1dc4bdaa549bd69437169a15011f701c46b38",
            "house/publish.py": "191155992fb9d03f879532d721a87bd7df66ac85a1c36973d252ae783dfdf247",
          },
          summary: "Install accepted checkpoint bundle bound and missing-page publisher together",
        }),
        trial: { task: "t-comb", evidence: "Passed" },
        endorsements: [],
        notice: null,
      },
      {
        id: "reno-installed",
        title: "Completed renovation",
        mode: "renovation",
        author: aster,
        status: "enacted",
        rule_status: "installed",
        stale: false,
        reason: "Already running",
        text: "non-json fallback text",
        trial: { task: "t-inst", evidence: "Passed" },
        endorsements: [],
        notice: null,
      },
      {
        id: "reno-failed",
        title: "Failed renovation",
        mode: "renovation",
        author: aster,
        status: "enacted",
        rule_status: "failed",
        stale: false,
        reason: "Mismatched main",
        text: "plain text",
        trial: { task: "t-fail", evidence: "Passed" },
        endorsements: [],
        notice: null,
      },
      {
        id: "floor-upper",
        title: "Open upper floor",
        mode: "floor",
        author: aster,
        status: "enacted",
        rule_status: "active",
        stale: false,
        reason: "Room to grow",
        text: JSON.stringify({ level: 1, name: "Upper Loft", purpose: "Quiet workshops" }),
        trial: { task: "t-floor", evidence: "Passed" },
        endorsements: [],
        notice: null,
      },
    ],
  },
};
voting();
const root = nodes.voting;
const combCard = byId(root, "vote-rule-combined-checkpoint-publish-001");
assert.match(text(combCard), /Awaiting install/i);
const wording = byId(root, "vote-wording-combined-checkpoint-publish-001");
const wordingText = text(wording);
assert.match(wordingText, /Install accepted checkpoint bundle bound and missing-page publisher together/);
assert.match(wordingText, /408c6d4268cc/);
assert.match(wordingText, /house\/checkpoint\.py/);
assert.match(wordingText, /c763702cd07c/);
assert.match(wordingText, /house\/publish\.py/);
assert.match(wordingText, /191155992fb9/);
assert.doesNotMatch(wordingText, /\{"files":|\{"source_commit":/, "Valid renovation JSON should render structured details instead of raw JSON");

assert.match(text(byId(root, "vote-rule-reno-installed")), /Installed/);
assert.match(text(byId(root, "vote-wording-reno-installed")), /non-json fallback text/);
assert.match(text(byId(root, "vote-rule-reno-failed")), /Install failed/);

const floorWording = text(byId(root, "vote-wording-floor-upper"));
assert.match(floorWording, /Floor 1/i);
assert.match(floorWording, /Upper Loft/);
assert.match(floorWording, /Quiet workshops/);
""")

    def test_index_html_keeps_choice_progress_token_and_syncs_asset_versions(self):
        html = INDEX_HTML.read_text()
        self.assertEqual(html.count("?v=choice-progress-1"), 2)
        self.assertIn("council=room-2", html)
        self.assertEqual(html.count("council=room-2"), 2)
