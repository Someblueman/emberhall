import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch

from house import craft_outcomes
from house.home_work import git
from house.publish import BRANCH, publish
from tests.support import HouseCase

SOURCE = Path(__file__).resolve().parents[1]


class CraftPublication(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo / "site").mkdir()
        for name in ("house.js", "house.css", "index.html"):
            shutil.copyfile(SOURCE / "site" / name, self.repo / "site" / name)
        (self.repo / "site/projects.json").write_text('{"version":1,"projects":[]}')
        git(self.repo, "add", "site")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", "Public test site")

    def record_work(self):
        run = "private-run-identity"
        resident = "resident-private-name"
        self.record.append("arrive", "watch-keeper", {"name": "Clock"})
        self.record.append("life", "watch-keeper", {"kind": "run-start", "run": run,
                           "resident": resident, "agent": "codex", "model": "gpt-6.1-sol",
                           "source_head": "a" * 40, "workspace": "residents/" + run,
                           "policy_revision": "baseline", "mode": "work"})
        self.record.append("arrive", resident, {"name": "First builder"})
        self.task()
        self.record.append("claim", resident, {"task": "work", "token": "private-lease",
                                                "expect": 0, "seconds": 300})
        (self.repo / "private-artifact.txt").write_text("private contents")
        self.cli("finish", "work", "--as", resident, "--token", "private-lease",
                 "--result", "private result", "--artifact", "private-artifact.txt")
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": run,
                           "outcome": "success", "exit_code": 0, "usage": {}, "elapsed_seconds": 1})
        receipt = {"run": run, "actor": "bob", "base": "a" * 40, "contribution": "b" * 40,
                   "status": "integrated", "test_exit": 0, "test_commands": [["private-path"]]}
        self.record.append("say", "bob", {"text": "house-integration-v1 " + json.dumps(receipt)})

    def report(self):
        publish(self.record)
        head = json.loads(self.record.git("show", BRANCH + ":head.json"))
        raw = self.record.git("show", BRANCH + ":craft.json")
        self.assertNotIn(b"private", raw)
        report = json.loads(raw)
        self.assertEqual((report["through"], report["journal_head"], report["source_head"]),
                         (head["seq"], head["journal_head"], head["source_head"]))
        return report

    def test_real_publication_and_bounded_window(self):
        self.assertEqual(self.report()["rows"], [])
        self.record_work()
        report = self.report()
        row, = report["rows"]
        self.assertEqual((row["eligible_finishes"], row["eligible_claims"], row["first_pass"],
                          row["reviewed_runs"]), (1, 1, 1, 1))
        self.assertEqual(row["examples"], {"claim": 8, "finish": 9, "first_review": 11})
        self.record.append("say", "alice", {"text": "Another moment"})
        with patch.object(craft_outcomes, "PUBLIC_WINDOW", 4):
            bounded = self.report()
        self.assertEqual((bounded["first"], bounded["through"]), (9, 12))
        self.assertEqual((bounded["rows"], bounded["unmatched_finishes"], bounded["unmatched_reviews"]),
                         ([], 1, 1))


class CraftDispatchCounts(unittest.TestCase):
    def test_assignment_stays_with_its_run_when_another_resident_takes_it(self):
        def start(run, resident, family):
            return ("life", "watch-keeper", {"kind": "run-start", "run": run, "resident": resident,
                    "agent": family, "mode": "work", "task": "work", "task_generation": 0})

        def stop(run, outcome):
            return ("life", "watch-keeper", {"kind": "run-finish", "run": run, "outcome": outcome})

        events = [{"op": op, "actor": actor, "data": data} for op, actor, data in [
            ("task", "one", {"task": "work", "project": "math"}),
            start("first", "one", "agy"), start("second", "two", "codex"),
            ("claim", "two", {"task": "work", "expect": 0}), ("release", "two", {"task": "work"}),
            ("claim", "one", {"task": "work", "expect": 2}), ("release", "one", {"task": "work"}),
            ("claim", "two", {"task": "work", "expect": 4}), ("finish", "two", {"task": "work"}),
            stop("first", "success"), stop("second", "quota")]]
        result = craft_outcomes.public_window(events, len(events), "journal", "source")
        first, second = result["rows"]
        self.assertEqual((first["dispatches"], first["taken_dispatches"], first["eligible_dispatches"],
                          first["eligible_taken_dispatches"], first["claims"]), (1, 0, 1, 0, 1))
        self.assertEqual((second["dispatches"], second["taken_dispatches"], second["eligible_dispatches"],
                          second["eligible_taken_dispatches"], second["claims"]), (1, 1, 0, 0, 2))
        self.assertEqual((first["examples"]["dispatch"], second["examples"]["dispatch"]), (2, 3))

class CraftBrowserBoundary(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node executes the actual reader")
    def test_matches_only_current_counts_and_suppresses_later_results(self):
        js = """
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[1],'utf8').split('\\nrefresh();\\nsetInterval')[0];
const ctx=vm.createContext({assert});
vm.runInContext(source,ctx);
vm.runInContext(`
  data={source_head:"source",journal_head:"head",frames:[{seq:12}]};
  const valid={source_head:"source",journal_head:"head",through:12,first:1,rows:[],
               unmatched_finishes:0,unmatched_reviews:0};
  assert(craftMatches(valid,data));
  for(const change of [{journal_head:"other"},{source_head:"stale"},{through:11},{first:0},{rows:[null]}])
    assert.equal(craftMatches({...valid,...change},data),false);
  current=false; frame={seq:8}; data.craft=valid;
  renderCraftOutcomes(null); // the historical view must not even create a panel
`,ctx);
"""
        subprocess.run(["node", "-e", js, str(SOURCE / "site/house.js")], check=True)
