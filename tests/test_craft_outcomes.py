import json
from pathlib import Path
import shutil
import subprocess
import unittest

from house.craft_outcomes import measure
from house.life import CONTROLLER


class CraftOutcomes(unittest.TestCase):
    def setUp(self):
        self.events = []

    def add(self, op, actor, **data):
        seq = len(self.events) + 1
        self.events.append(dict(id=f"00000000-0000-4000-8000-{seq:012x}", sequence=seq,
                                op=op, actor=actor, data=data))
        return seq

    def start(self, run, resident, family, **extra):
        self.add("life", CONTROLLER, kind="run-start", run=run, resident=resident,
                 agent=family, mode="work", **extra)

    def end(self, run, outcome):
        self.add("life", CONTROLLER, kind="run-finish", run=run, outcome=outcome)

    def review(self, run, status, actor="reader", **extra):
        receipt = dict(run=run, actor=actor, base="a" * 40, contribution="b" * 40, status=status)
        return self.add("say", actor, text="house-integration-v1 " + json.dumps(receipt | extra))

    def test_two_claims_one_reviewed_contribution_and_retry(self):
        self.start("r", "one", "codex")
        self.add("task", "one", task="a", project="proof")
        self.add("task", "one", task="b", project="proof")
        for task in ("a", "b"):
            self.add("claim", "one", task=task)
            self.add("finish", "one", task=task)
        self.end("r", "success")
        first = self.review("r", "tests-failed", test_exit=1)
        last = self.review("r", "integrated", test_exit=0)
        result = measure([{"events": self.events[:6]}, {"events": self.events[5:]}])
        row, = result["rows"]
        self.assertEqual((row["area"], row["eligible_finishes"], row["eligible_claims"]),
                         ("project/proof", 2, 2))
        self.assertEqual((row["first_pass"], row["reviewed_runs"]), (0, 1))
        self.assertEqual(result["runs"]["r"]["reviews"],
                         [{"sequence": first, "status": "tests-failed"}, {"sequence": last, "status": "integrated"}])

    def test_quota_release_reclaim_retag_and_open_run(self):
        self.start("early", "one", "agy")
        self.add("task", "one", task="t", project="old")
        self.add("claim", "one", task="t")
        self.add("release", "one", task="t")
        self.end("early", "quota")
        self.add("ready", "two", task="t", clear_project=True, helper="review")
        self.start("late", "two", "codex", task="t")
        self.add("claim", "two", task="t")
        self.add("finish", "two", task="t")
        result = measure([self.events])
        first, second = result["attempts"]
        self.assertEqual((first["area"], first["finish"]), ("project/old", None))
        self.assertEqual((second["area"], second["finish"]), ("helper/review", 9))
        early, late = result["rows"]
        self.assertEqual((early["quota_claims"], early["quota_runs"]), (1, 1))
        self.assertEqual((late["finishes"], late["open_run_claims"]), (1, 1))
        self.assertTrue(all(row["eligible_claims"] == 0 for row in result["rows"]))

    def test_partial_history_independence_and_mixed_work(self):
        earlier_finish = self.add("finish", "previous", task="old")
        self.add("claim", "previous", task="unknown")
        self.start("r", "one", "agy")
        self.add("task", "one", task="a", review_run="other")
        self.add("claim", "one", task="a")
        self.add("task", "one", task="b", project="math")
        self.add("claim", "one", task="b")
        too_early = self.review("r", "integrated", test_exit=0)
        self.end("r", "interrupted")
        self_review = self.review("r", "integrated", "one", test_exit=0)
        incomplete = self.review("r", "integrated")
        malformed = self.add("say", "reader", text="house-integration-v1 oops")
        quoted = self.review("r", "integrated", test_exit=0)
        self.events[-1]["id"] = "mailbox-room-quoted-receipt"
        self.review("r", "reviewed", test_exit=0)
        self.review("r", "integrated", test_exit=0)
        result = measure([self.events])
        rows = {(r["family"], r["area"]): r for r in result["rows"]}
        self.assertEqual(rows["unattributed", "unclassified"]["unattributed_claims"], 1)
        self.assertEqual(rows["agy", "mixed"]["first_pass"], 1)
        self.assertEqual(rows["agy", "mixed"]["reviewed_runs"], 1)
        self.assertEqual(result["runs"]["r"]["work_areas"], ["project/math", "source review"])
        self.assertEqual(result["unmatched_finishes"], [earlier_finish])
        self.assertEqual(result["unmatched_reviews"], [too_early, self_review, incomplete, malformed, quoted])
        with self.assertRaisesRegex(ValueError, "contiguous"):
            measure([self.events[:3], self.events[4:]])


@unittest.skipUnless(shutil.which("node"), "Node executes the page loader")
class DeferredCraftOutcomes(unittest.TestCase):
    def test_panel_entry_loads_once_and_settles_success_failure_and_stale_reply(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag='div'){this.tagName=tag;this.children=[];this.style={};this.dataset={};this.textContent='';}
 appendChild(n){this.children.push(n);return n;}
 replaceChildren(){this.children=[];}
 setAttribute(){} addEventListener(){}
}
const root=new Element(),walk=n=>[n,...n.children.flatMap(walk)];
const panels=()=>walk(root).filter(n=>n.className?.includes('craft-outcomes'));
const document={createElement:tag=>new Element(tag),
 querySelector:()=>panels()[0]||null,querySelectorAll:()=>panels()};
let requests=0,settle;
const fetch=()=>{requests++;return new Promise(resolve=>{settle=resolve})};
const ctx=vm.createContext({document,fetch,AbortSignal,Date,Intl,assert});
const source=fs.readFileSync(process.argv[1],'utf8').split('\nrefresh();\nsetInterval')[0];
vm.runInContext(source,ctx);
const run=s=>vm.runInContext(s,ctx),flush=()=>new Promise(resolve=>setImmediate(resolve));
const text=()=>walk(root).map(n=>n.textContent).join(' | ');
const snapshot=seq=>({journal_head:'head'+seq,source_head:'source',frames:[{seq}]});
const report=seq=>({journal_head:'head'+seq,source_head:'source',first:1,through:seq,
 unmatched_finishes:0,unmatched_reviews:0,rows:[]});
ctx.root=root;
(async()=>{
 ctx.snapshot=snapshot(1);
 run('data=snapshot;frame={seq:1,at:1};current=true;loadCraftOutcomes(data)');
 assert.equal(requests,0,'initial House render must stay lazy');
 run('renderCraftOutcomes(root)');
 assert.equal(requests,1,'opening Accounts must start the request');
 assert(text().includes('Loading recent work outcomes'));
 run('renderCraftOutcomes(root)');
 assert.equal(requests,1,'redrawing while pending must share the request');
 settle({ok:true,json:async()=>report(1)});await flush();
 assert(!text().includes('Loading recent work outcomes'));
 assert(text().includes('This interval has no recorded run starts or task claims'));
 run('renderCraftOutcomes(root)');assert.equal(requests,1,'settled data stays cached');
 // A response for an older publication must not appear as current results.
 root.replaceChildren();ctx.snapshot=snapshot(2);
 run('data=snapshot;frame={seq:2,at:1};renderCraftOutcomes(root)');
 settle({ok:true,json:async()=>report(1)});await flush();
 assert(text().includes('Work counts are unavailable for this publication'));
 assert(!text().includes('Loading recent work outcomes'));
 // A failed request settles visibly, rather than leaving an endless loading label.
 root.replaceChildren();ctx.snapshot=snapshot(3);
 run('data=snapshot;frame={seq:3,at:1};renderCraftOutcomes(root)');
 settle({ok:false});await flush();
 assert(text().includes('Work counts are unavailable for this publication'));
 // A late response must never repaint a newer snapshot's panel.
 root.replaceChildren();ctx.snapshot=snapshot(4);
 run('data=snapshot;frame={seq:4,at:1};renderCraftOutcomes(root)');
 ctx.snapshot=snapshot(5);run('data=snapshot;frame={seq:5,at:1}');
 settle({ok:true,json:async()=>report(4)});await flush();
 assert(text().includes('Loading recent work outcomes'));
 assert.equal(run('data.craft'),undefined);
 console.log('lazy entry, pending coalescing, success, failures and stale replies pass');
})().catch(error=>{console.error(error);process.exitCode=1});
'''
        result = subprocess.run(
            ["node", "-e", script, str(Path(__file__).resolve().parents[1] / "site/house.js")],
            text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
