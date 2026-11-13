"""Returning identities and finite drawings of complete, historical rosters."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch

from house.body import export
from tests.support import HouseCase


class BodyReturnTests(HouseCase):
    def person(self, frame, resident):
        return next(person for person in frame["residents"] if person["id"] == resident)

    def watch(self, kind, run, **fields):
        self.record.append("say", "watch-keeper", {
            "text": "house-watch-v1 " + json.dumps({"kind": kind, "run": run, **fields})})

    def test_explicit_wake_after_ended_run_wins_by_sequence_and_keeps_scar(self):
        self.record.append("arrive", "watch-keeper", {"name": "Watch keeper"})
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": "first", "resident": "fern",
            "agent": "muse", "model": "muse-ember-1.0", "source_head": "a" * 40,
            "workspace": "residents/first", "policy_revision": "fixture", "mode": "work"})
        self.record.append("arrive", "fern", {"name": "Fern"})
        now = self.record.read()[0]["at"]
        with patch("house.record.time.time", return_value=now):
            self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": "first",
                "outcome": "interrupted", "exit_code": None, "usage": {}, "elapsed_seconds": 3})
            before = export(self.record, now)
            self.assertEqual(self.person(before["frames"][-1], "fern")["pose"], "unconfirmed")
            self.record.append("wake", "fern", {})
            after = export(self.record, now)
        self.assertEqual(after["frames"][:len(before["frames"])], before["frames"])
        self.assertEqual(self.person(after["frames"][-1], "fern")["presence"], "recorded awake")
        self.assertEqual(self.person(after["frames"][-1], "fern")["room"], "door")
        self.assertEqual(after["scars"], before["scars"])
        self.assertEqual(after["frames"][-1]["scars"], before["frames"][-1]["scars"])
        self.assertEqual(after["frames"][-1]["runs"], before["frames"][-1]["runs"])

    def test_two_recorded_runs_share_one_identity_and_keep_distinct_receipts(self):
        # The historical watch envelope already accepts repeat identities; this
        # tests the view independently of the new supervisor's reuse policy.
        self.record.append("arrive", "watch-keeper", {"name": "Watch keeper"})
        self.watch("start", "first", resident="alice", executable="codex", model="gpt-6.1-sol")
        self.watch("finish", "first", outcome="success")
        self.record.append("sleep", "alice", {"through": self.record.read()[0]["sequence"], "note": "Back later"})
        before = export(self.record)
        self.watch("start", "second", resident="alice", executable="codex", model="gpt-6.1-sol")
        self.record.append("wake", "alice", {})
        awake = export(self.record)
        self.watch("finish", "second", outcome="interrupted")
        after = export(self.record)
        self.assertEqual(after["frames"][:len(before["frames"])], before["frames"])
        self.assertEqual(after["frames"][:len(awake["frames"])], awake["frames"])
        self.assertEqual([p["id"] for p in after["frames"][-1]["residents"]], ["alice", "bob"])
        self.assertEqual(self.person(awake["frames"][-1], "alice")["pose"], "standing")
        self.assertEqual(self.person(after["frames"][-1], "alice")["pose"], "unconfirmed")
        runs = after["frames"][-1]["runs"]
        self.assertEqual([r["id"] for r in runs], ["first", "second"])
        self.assertEqual([r["resident"] for r in runs], ["alice", "alice"])
        self.assertEqual([r["outcome"] for r in runs], ["success", "interrupted"])
        self.assertLess(runs[0]["last_sequence"], runs[1]["sequence"])
        self.assertEqual(len(before["frames"][-1]["runs"]), 1)
        self.assertNotIn("run:second", before["scars"])

    def test_equal_names_remain_separate_and_sleep_does_not_remove_people(self):
        self.record.append("arrive", "other-alice", {"name": "Alice"})
        for resident in ("alice", "other-alice"):
            self.record.append("sleep", resident, {"through": self.record.read()[0]["sequence"], "note": "Rest"})
        frame = export(self.record)["frames"][-1]
        twins = [p for p in frame["residents"] if p["name"] == "Alice"]
        self.assertEqual([p["id"] for p in twins], ["alice", "other-alice"])
        self.assertTrue(all(p["pose"] == "sleeping" for p in twins))
        self.assertEqual(len(frame["residents"]), 3)


@unittest.skipUnless(shutil.which("node"), "Node is needed for the actual view's pure functions")
class DormViewTests(unittest.TestCase):
    def test_one_hundred_sleepers_are_paged_without_growth_or_lost_identities(self):
        source = Path(__file__).resolve().parents[1] / "site" / "house.js"
        script = r'''
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const source=fs.readFileSync(process.argv[1],"utf8"),tail="refresh();\nsetInterval(refresh,60000);\n";
assert(source.endsWith(tail));
const context=vm.createContext({assert});
vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
const hundred={residents:Array.from({length:100},(_,i)=>({id:'person-'+i,name:'Same name',room:'bedroom',pose:'sleeping'}))};
const original=JSON.stringify(hundred),seen=[];
for(let page=0;page<17;page++){
  const view=dormView(hundred,page);
  assert.equal(view.pages,17);assert.equal(view.asleep,100);
  assert(view.visible.length<=6);assert.equal(roomDepth({id:'bedroom'},view.members.length),160);
  seen.push(...view.visible.map(r=>r.id));
}
assert.equal(seen.length,100);assert.equal(new Set(seen).size,100);
assert.equal(dormSummary(dormView(hundred,0)),'100 recorded asleep / 6 shown');
assert.equal(dormSummary(dormView(hundred,16)),'100 recorded asleep / 4 shown');
assert.equal(dormView(hundred,100).page,16);assert.equal(dormView(hundred,-1).page,0);
const earlier={residents:hundred.residents.slice(0,1)};
assert.equal(dormView(earlier,16).page,0);assert.equal(dormView(earlier,0).visible.length,1);
assert.equal(dormSummary(dormView({residents:[]},0)),'0 recorded asleep / 0 shown');
const mixed={residents:[{id:'awake',room:'bedroom',pose:'standing'},...hundred.residents.slice(0,6)]};
assert.equal(dormSummary(dormView(mixed,0)),'6 recorded asleep / 5 shown');
const ids=['resident-alpha-deadbeef','resident-beta-deadbeef'];
assert.notEqual(shortId(ids[0],ids),shortId(ids[1],ids));
assert.equal(JSON.stringify(hundred),original);
`,context);
'''
        result = subprocess.run([shutil.which("node"), "-e", script, str(source)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
