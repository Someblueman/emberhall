"""Council labels a stranger can read, proposals the Steward's upgrade already installed, and the house slot.

The projection side (house/body.py) is checked on small hand-made states; the page side (site/house.js)
runs the real renderer under node against hand-made projections, as the reducer for house work is not here.
"""
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest

from house import body
from tests.test_council_room_and_filters import HARNESS

ROOT = Path(__file__).resolve().parents[1]
HOUSE_JS = ROOT / "site" / "house.js"
INDEX_HTML = ROOT / "site" / "index.html"
UPGRADE_AT = 1795009272.885789          # 18 Nov 2026, 13:41 UTC


def proposal(files, **extra):
    return {"title": "Install it", "mode": "renovation", "author": "alice", "status": "pending",
            "reason": "r", "text": "t", "proposed_at": 1000.0, "base": "rev-1",
            "renovation": {"files": files}, **extra}


def upgrade(sequence, at, files):
    return {"scope": f"upgrade-{sequence}", "sequence": sequence, "at": at, "protected_files": files}


def make_state(proposals, migrations):
    return {"proposals": proposals, "rule_revision": "rev-1", "residents": {"alice": {"name": "Alice"}},
            "council": {"rules": {}}, "shelf": {"ideas": {}, "projects": {}, "choices": {}},
            "maintenance": {"migrations": migrations}}


def view(state):
    return {item["id"]: item for item in body.voting_view(state, {}, {})["proposals"]}


class InstalledByUpgradeTests(unittest.TestCase):
    FILES = {"house/a.py": "a" * 64, "house/b.py": "b" * 64}

    def test_every_file_in_the_latest_upgrade_closes_it_as_delivered(self):
        state = make_state({"p": proposal(self.FILES)}, {
            "old": upgrade(5, 500.0, {"house/a.py": "0" * 64}),
            "new": upgrade(9, 2000.0, {**self.FILES, "house/c.py": "c" * 64}),
            "bare": {"at": 9000.0}})      # an entry with no manifest is skipped
        shown = view(state)["p"]
        self.assertTrue(shown["stale"])
        self.assertEqual({"how": "delivered", "by": "upgrade-9", "via": "upgrade", "at": 2000.0}, shown["closure"])
        self.assertEqual("pending", state["proposals"]["p"]["status"], "the record is not changed")

    def test_anything_short_of_a_full_match_leaves_it_pending(self):
        cases = {
            "one hash differs": ({"house/a.py": "a" * 64, "house/b.py": "x" * 64}, 2000.0, 9),
            "one file missing": ({"house/a.py": "a" * 64}, 2000.0, 9),
            "upgrade came before the proposal": (self.FILES, 900.0, 9),
        }
        for name, (installed, at, sequence) in cases.items():
            with self.subTest(name):
                shown = view(make_state({"p": proposal(self.FILES)}, {"u": upgrade(sequence, at, installed)}))["p"]
                self.assertFalse(shown["stale"])
                self.assertNotIn("closure", shown)

    def test_a_later_upgrade_that_changes_the_files_again_does_not_reopen_it(self):
        # 18 November: two proposals were installed by the 13:41 upgrade, then the 14:57 upgrade changed
        # one of their files again. Looking only at the newest upgrade, the page called them waiting.
        state = make_state({"p": proposal(self.FILES)}, {
            "later": upgrade(12, 3000.0, {"house/a.py": "9" * 64}),
            "first": upgrade(9, 2000.0, self.FILES),
            "again": upgrade(15, 4000.0, self.FILES)})
        shown = view(state)["p"]
        self.assertTrue(shown["stale"])
        self.assertEqual({"how": "delivered", "by": "upgrade-9", "via": "upgrade", "at": 2000.0}, shown["closure"],
                         "the first upgrade that installed them is named")

    def test_other_proposals_and_closures_are_untouched(self):
        lapsed = proposal(self.FILES, base="rev-0")       # closed by the old rule, whatever the upgrade did
        rule = {"title": "A rule", "mode": "rule", "author": "alice", "status": "pending", "reason": "r",
                "text": "t", "proposed_at": 1000.0, "base": "rev-1"}
        enacted = proposal(self.FILES, status="enacted")
        state = make_state({"lapsed": lapsed, "rule": rule, "enacted": enacted, "empty": proposal({})},
                           {"u": upgrade(9, 2000.0, self.FILES)})
        shown = view(state)
        self.assertEqual({"how": "lapsed", "by": None}, shown["lapsed"]["closure"])
        for name in ("rule", "enacted", "empty"):
            self.assertFalse(shown[name]["stale"], name)

    def test_odd_manifest_entries_do_not_break_the_view(self):
        state = make_state({"p": proposal(self.FILES)}, {
            "a": "not a dict", "b": {"protected_files": ["x"], "sequence": 3, "at": 5.0},
            "c": {"protected_files": dict(self.FILES), "at": 2000.0},          # no sequence
            "d": {"protected_files": dict(self.FILES), "sequence": 4},         # no time
            "e": {"protected_files": {"house/a.py": 5}, "sequence": 2, "at": 2000.0}})
        self.assertFalse(view(state)["p"]["stale"])


class HouseWorkFlagTests(unittest.TestCase):
    def shelf(self, migrations):
        state = make_state({}, migrations)
        state["residents"] = {}
        return body.shelf_view(state)

    def test_flag_follows_the_migration_and_is_absent_before_it(self):
        self.assertNotIn("house_work", self.shelf({}))
        self.assertNotIn("house_work", self.shelf({"upgrade-20261118-research-rotation": {}}))
        self.assertIs(True, self.shelf({"upgrade-20261118-house-work": {}})["house_work"])

    def test_scale_and_slot_pass_through_as_recorded(self):
        state = make_state({}, {})
        state["residents"] = {"alice": {"name": "Alice"}}
        idea = {"title": "A room", "what": "w", "why": "y", "first_step": "f", "author": "alice",
                "status": "shelved", "scale": "house", "sources": [], "losses": 0, "history": []}
        state["shelf"] = {"ideas": {"i": idea}, "choices": {}, "projects": {"p": {
            "idea": "i", "owner": "alice", "status": "active", "slot": "house", "milestone": "m",
            "deadline": 5, "extended": False}}}
        shown = body.shelf_view(state)
        self.assertEqual("house", shown["ideas"][0]["scale"])
        self.assertEqual("house", shown["projects"][0]["slot"])


@unittest.skipUnless(shutil.which("node"), "Node executes the actual house renderer")
class PageTests(unittest.TestCase):
    def run_renderer(self, code: str) -> None:
        script = HARNESS + "\nvm.runInContext(" + json.dumps(code) + ", context);"
        result = subprocess.run([shutil.which("node"), "-e", script, str(HOUSE_JS)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    # 1. Council labels

    def test_notice_over_tag_says_what_it_means(self):
        self.run_renderer(r"""
data = { timezone: "UTC", frames: [] };
const person = { name: "Aster", agent: "codex", id: "resident-aster" };
const two = [1, 2].map(i => ({ resident: person, reason: "ok", at: i }));
const base = { status: "pending", stale: false, mode: "rule", trial: { task: "t", evidence: "e" }, endorsements: two };
const tags = (extra, now) => proposalSummaryTags({ ...base, ...extra }, now).map(t => t.text);
const over = { notice: { at: 0, until: 500 } };
assert(tags(over, 1000).includes("Ready to enact"));
assert(tags({ notice: { at: 0, until: 5000 } }, 1000).includes("Notice active"));
// A wake prompt is left to the Steward: its tag must not say a resident can enact it.
const wake = tags({ ...over, mode: "wake-prompt" }, 1000);
assert(wake.includes("Left for the Steward"), wake.join("|"));
assert(!wake.some(t => /enact/i.test(t)), wake.join("|"));
assert.match(proposalWaitingLine({ ...base, ...over, mode: "wake-prompt" }, 1000).text, /left for the Steward/);
assert.equal(proposalWaitingLine({ ...base, ...over }, 1000).key, "ready");
for (const mode of ["rule", "wake-prompt", "renovation", "floor"])
  assert(!tags({ ...over, mode }, 1000).some(t => /window/i.test(t)));
""")

    def test_the_old_wording_is_gone_from_page_and_docs(self):
        pattern = re.compile(r"window elapsed|notice elapsed", re.I)
        self.assertIsNone(pattern.search(HOUSE_JS.read_text()))
        self.assertIsNone(pattern.search((ROOT / "docs" / "BODY.md").read_text()))
        # The council doc may quote the old words only to say they were replaced.
        for line in (ROOT / "docs" / "COUNCIL.md").read_text().splitlines():
            if pattern.search(line):
                self.assertRegex(line, r"used to|now says|replaced")

    # 2. Already installed by the Steward's upgrade

    def test_upgrade_closure_names_the_upgrade_not_a_rule(self):
        self.run_renderer(r"""
data = { timezone: "UTC", frames: [] };
frame = { voting: { proposals: [{ id: "council-rule-1", title: "Rule One" }] } };
const upgraded = proposalClosure({ stale: true, closure: { how: "delivered", by: "upgrade-20261118-research-rotation", via: "upgrade", at: 1795009272.885789 } });
assert.equal(upgraded.label, "Already installed by the Steward’s upgrade of 18 Nov, 13:41");
assert.equal(upgraded.tag, "Already installed");
const byRule = proposalClosure({ stale: true, closure: { how: "delivered", by: "council-rule-1" } });
assert.equal(byRule.label, "Closed · delivered by “Rule One”");
assert.notEqual(byRule.tag, upgraded.tag);
// No time recorded: still plain, no "undefined".
const bare = proposalClosure({ stale: true, closure: { how: "delivered", by: "x", via: "upgrade" } });
assert.equal(bare.label, "Already installed by the Steward’s upgrade");
assert.equal(proposalStatusLabel({ stale: true, closure: { how: "delivered", by: "x", via: "upgrade", at: 1795009272 } }),
  "Already installed by the Steward’s upgrade of 18 Nov, 13:41");
const waiting = proposalWaitingLine({ stale: true, status: "pending", closure: { how: "delivered", via: "upgrade", by: "x" } }, 1);
assert.equal(waiting.key, "overtaken");
assert.doesNotMatch(waiting.text, /later decision/);
""")

    def test_council_room_folds_the_installed_proposal_and_keeps_it_out_of_the_count(self):
        self.run_renderer(r"""
const aster = { name: "Aster", agent: "codex", id: "resident-aster" };
data = { timezone: "UTC", frames: [] };
current = true; selectedFloor = 0; selected = "council";
frame = { seq: 9, at: 1795010000, residents: [aster], scars: [], runs: [], tasks: [], council: { pending: 2 },
  rooms: [{ id: "council", name: "The Council", status: "open", floor: 0, purpose: "Decide." }],
  voting: { choices: [], proposals: [
    { id: "installed-secret", title: "Readable work", mode: "renovation", author: aster, status: "pending", stale: true,
      closure: { how: "delivered", by: "upgrade-20261118-research-rotation", via: "upgrade", at: 1795009272.885789 },
      reason: "r", text: "t", trial: null, endorsements: [], notice: null },
    { id: "live-secret", title: "Still open", mode: "rule", author: aster, status: "pending", stale: false,
      reason: "r", text: "t", trial: null, endorsements: [], notice: null } ] } };
roomPanel();
const panel = nodes["room-content"];
const vis = visible(panel);
assert.match(vis, /1 active proposal\b/);
assert.match(vis, /Closed, overtaken or already installed · 1/);
const folded = all(panel).find(n => n.tag === "details" && /already installed/.test(n.children[0]?.textContent || ""));
assert(folded && !folded.open);
assert.match(text(folded), /Readable work/);
assert.match(text(folded), /Already installed by the Steward’s upgrade of 18 Nov, 13:41/);
assert.doesNotMatch(text(folded), /Overtaken by a later decision/);
""")

    # 3. The house slot

    SETUP = r"""
const r1 = { id: "r1", name: "Fable" };
data = { timezone: "UTC", frames: [] };
current = true;
const study = { id: "study", name: "The Study", floor: 0, status: "open", purpose: "Shelf room" };
const council = { id: "council", name: "The Council", floor: 0, status: "open", purpose: "Decide." };
const idea = (id, scale, extra = {}) => ({ id, title: id + " idea", status: "shelved", scale, losses: 0, author: "r1", sources: [], ...extra });
const make = (shelfExtra, choices = []) => {
  frame = { seq: 5, at: 1000, rooms: [study, council], residents: [r1], scars: [], tasks: [], runs: [], floors: [{ level: 0, name: "Ground floor" }],
    shelf: { enabled: true, policy: "work-selection-004", great_wanted: false, explorer: null,
      ideas: [idea("s1", "small"), idea("s2", "small"), idea("g1", "great")], projects: [], ...shelfExtra },
    voting: { choices, proposals: [] } };
};
const shelfText = () => { shelf(); return text(nodes["shelf"]); };
const studyText = () => { selected = "study"; roomPanel(); return text(nodes["room-content"]); };
"""

    def test_before_the_migration_the_page_is_unchanged(self):
        self.run_renderer(self.SETUP + r"""
make({});
const before = shelfText(), studyBefore = studyText();
assert.doesNotMatch(before, /house work|house slot|One change to the house/i);
assert.doesNotMatch(studyBefore, /house work|house slot|House idea/i);
assert.match(before, /Building now: 0 of 1 great work, 0 of 1 small project · 3 ideas waiting \(1 great, 2 small\)/);
assert.match(studyBefore, /Great slot: free \(1 great idea\) · Small slot: free \(2 small ideas\) · 0 finished/);
const options = all(all(nodes["room-content"]).find(n => n.id === "study-scale")).filter(n => n.tag === "option").map(n => n.textContent);
assert.equal(options.join("|"), "All scales|Great work|Small project");
make({ house_work: false });
assert.equal(shelfText(), before);
// A recorded house item is never hidden, even if the flag were missing.
make({ ideas: [idea("h1", "house")] });
assert.match(shelfText(), /House work/);
""")

    def test_empty_house_slot_says_what_it_is_for(self):
        self.run_renderer(self.SETUP + r"""
make({ house_work: true });
const out = shelfText();
assert.match(out, /In motion/);
assert.match(out, /House work Slot open One change to the house itself at a time: a new room, a rethought front page, a new ability for residents\. Nothing chosen yet\./);
assert.match(out, /Building now: 0 of 1 great work, 0 of 1 small project, 0 of 1 house work · 3 ideas waiting \(1 great, 2 small, 0 house\)/);
// Open council choice for the slot, and one that finished before.
make({ house_work: true }, [{ id: "c1", status: "open", slot: "house", owner: r1, opened_sequence: 1, selection_version: 3,
  candidates: [{ id: "h1", title: "A new room", author: r1, milestone: "M", seconds: 1 }], votes: [] }]);
assert.match(shelfText(), /The council is choosing one now\./);
make({ house_work: true, projects: [{ id: "old", title: "Old house work", status: "done", slot: "house", owner: "r1" }] });
assert.match(shelfText(), /Nothing is being built in this slot now\./);
// Nothing at all on the shelf: the slot still shows.
make({ house_work: true, ideas: [] });
assert.match(shelfText(), /One change to the house itself/);
""")

    def test_all_three_slots_occupied(self):
        self.run_renderer(self.SETUP + r"""
const ideas = [idea("s1", "small"), idea("g1", "great"), idea("h1", "house", { plain: "A rethought front page." }), idea("h2", "house")];
const projects = [
  { id: "ps", title: "Small build", status: "active", slot: "small", owner: "r1", milestone: "M", deadline: 9 },
  { id: "pg", title: "Great build", status: "active", slot: "great", owner: "r1", milestone: "M2", deadline: 9, stage: 0,
    milestones: [{ milestone: "M2", seconds: 1 }, { milestone: "M3", seconds: 1 }], completed: [] },
  { id: "ph", title: "House build", status: "active", slot: "house", owner: "r1", milestone: "New door", deadline: 9 }];
const choices = [
  { id: "c-house", status: "open", slot: "house", owner: r1, opened_sequence: 1, selection_version: 3,
    candidates: [{ id: "h1", title: "A new room", author: r1, milestone: "M", seconds: 1 }], votes: [] },
  { id: "c-small", status: "open", slot: "small", owner: r1, opened_sequence: 2, selection_version: 3,
    candidates: [{ id: "s1", title: "Small one", author: r1, milestone: "M", seconds: 1 }], votes: [] },
  { id: "c-done", status: "closed", slot: "house", winner: "h1", owner: r1, opened_sequence: 3, selection_version: 3,
    candidates: [{ id: "h1", title: "A new room", author: r1, milestone: "M", seconds: 1 }], votes: [] }];
make({ house_work: true, ideas, projects }, choices);
const out = shelfText();
assert.match(out, /Building now: 1 of 1 great work, 1 of 1 small project, 1 of 1 house work · 4 ideas waiting \(1 great, 1 small, 2 house\)/);
assert.match(out, /All three project slots occupied/);
assert.doesNotMatch(out, /Both project slots/);
assert.match(out, /House work · Active · Fable/);
assert.match(out, /Small project · Active · Fable/);
assert.match(out, /Great work · Active · Fable/);
assert.doesNotMatch(out, /One change to the house itself/, "the slot is not empty");
// A house idea is labelled house, never small.
const card = all(nodes["shelf"]).find(n => n.tag === "details" && /h1 idea/.test(text(n)));
assert(card);
assert.match(text(card), /House work/);
assert.doesNotMatch(text(card), /Small project|Great work/);
// The study: counts, filter option, filtering.
const study_ = studyText();
assert.match(study_, /Great slot: busy \(1 great idea\)/);
assert.match(study_, /Small slot: busy \(1 small idea\) · House slot: busy \(2 house ideas\)/);
const select = all(nodes["room-content"]).find(n => n.id === "study-scale");
const options = all(select).filter(n => n.tag === "option").map(n => [n.value, n.textContent]);
assert.equal(JSON.stringify(options), JSON.stringify([["all", "All scales"], ["great", "Great work"], ["small", "Small project"], ["house", "House work"]]));
studyState.scale = "house"; studyState.filter = "all"; studyState.query = "";
roomPanel();
const filtered = text(nodes["room-content"]);
assert.match(filtered, /2 of 4 ideas match/);
assert.match(filtered, /h1 idea/); assert.doesNotMatch(filtered, /s1 idea|g1 idea/);
studyState.scale = "small"; roomPanel();
assert.match(text(nodes["room-content"]), /1 of 4 ideas match/);
studyState.scale = "all"; studyState.query = "house work"; roomPanel();
assert.match(text(nodes["room-content"]), /2 of 4 ideas match/);
studyState.query = "";
// The Council room and the voting card name the slot.
selected = "council"; roomPanel();
const councilText = text(nodes["room-content"]);
assert.match(councilText, /House work choice · 0\/3 counted votes/);
assert.match(councilText, /Small project choice · 0\/3 counted votes/);
assert.match(councilText, /2 open project choices/);
voting();
const votes = text(nodes.voting);
assert.match(votes, /House work choice · Open/);
assert.match(votes, /House work choice · Selected: A new room/);
assert.match(votes, /A house work is one change to the house itself, with one milestone and one deadline\./);
assert.doesNotMatch(votes, /Great works carry/);
""")

    def test_cache_numbers_are_bumped_and_the_token_kept(self):
        html = INDEX_HTML.read_text()
        self.assertEqual(2, html.count("living=25"))
        self.assertEqual(0, html.count("living=24"))
        self.assertEqual(2, html.count("?v=choice-progress-1"))


if __name__ == "__main__":
    unittest.main()
