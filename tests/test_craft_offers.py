import json
import unittest

from house.craft_offers import audit
from house.life import CONTROLLER
from house.work_metrics import ASSIGNMENT_PREFIX


class CraftOffers(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.runs = {}
        self.attempts = []
        self.add("task", "writer", task="proof", project="math")

    def add(self, op, actor, **data):
        seq = len(self.events) + 1
        self.events.append(dict(op=op, actor=actor, id=str(seq), data=data, sequence=seq))
        return seq

    def start(self, run, resident, family="codex", offer=True, generation=0, **extra):
        task = dict(task="proof", task_generation=generation, backlog=True) if offer else {}
        seq = self.add("life", CONTROLLER, kind="run-start", run=run, resident=resident,
                       agent=family, model="ordinary", mode="work", **task, **extra)
        self.runs[run] = dict(start=seq, family=family, resident=resident, exit=None, outcome=None, reviews=[])
        self.add("life", CONTROLLER, kind="run-launched", run=run)
        observation = dict(run=run, reason="balanced", lane="work", helper=False)
        self.add("say", CONTROLLER, text=ASSIGNMENT_PREFIX + json.dumps(observation))
        self.events[-1]["id"] = f"home-{run}-assignment"
        return seq

    def claim(self, run, generation=0):
        actor = self.runs[run]["resident"]
        seq = self.add("claim", actor, task="proof", expect=generation, token=f"token{generation}")
        attempt = dict(task="proof", run=run, claim=seq, finish=None)
        self.attempts.append(attempt)
        return attempt

    def finish(self, attempt, generation=0):
        attempt["finish"] = self.add("finish", self.runs[attempt["run"]]["resident"],
                                     task="proof", token=f"token{generation}")

    def close(self, run, outcome="success"):
        seq = self.add("life", CONTROLLER, kind="run-finish", run=run, outcome=outcome)
        self.runs[run].update(exit=seq, outcome=outcome)

    def report(self):
        outcome = dict(first=1, through=len(self.events), attempts=self.attempts, runs=self.runs)
        return audit([self.events], outcome, 1)

    def test_other_resident_delivers_same_task_without_credit_to_recipient(self):
        other = self.start("a", "alice", "agy", offer=False)
        self.start("b", "ben")
        claim = self.claim("a")
        self.close("b")
        self.finish(claim)
        self.close("a")
        self.runs["b"]["reviews"] = [{"sequence": len(self.events), "status": "integrated"}]
        report = self.report()
        row, = report["offers"]
        self.assertEqual((row["claimant_start"], row["claim_finish"], row["claimant_family"]),
                         (other, claim["finish"], "agy"))
        self.assertEqual(row["disposition"], "claimed elsewhere")
        self.assertEqual(row["task_finisher_start"], other)
        totals, = report["rows"]
        self.assertEqual((totals["eligible_offers"], totals["claimed_elsewhere"],
                          totals["receiver_finished"], totals["reviewed_receiver_runs"]), (1, 1, 0, 0))

    def test_same_person_returns_and_repeated_offers_remain_separate(self):
        self.start("early", "alice")
        self.close("early", "quota")
        self.start("later", "alice")
        self.finish(self.claim("later"))
        self.close("later")
        first = self.add("say", "reviewer", text="first decision")
        second = self.add("say", "reviewer", text="later decision")
        self.runs["later"]["reviews"] = [{"sequence": first, "status": "conflict"},
                                         {"sequence": second, "status": "integrated"}]
        report = self.report()
        early, later = report["offers"]
        self.assertEqual(early["disposition"], "claimed elsewhere")
        self.assertEqual(later["receiver_first_review"]["sequence"], first)
        totals, = report["rows"]
        self.assertEqual((totals["offers"], totals["quota"], totals["eligible_offers"],
                          totals["receiver_finished"], totals["first_pass"]), (2, 1, 1, 1, 0))
        self.assertEqual(report["distinct_eligible_tasks"], 1)

    def test_new_generation_cannot_complete_old_offer(self):
        self.start("a", "alice")
        self.add("ready", "writer", task="proof", expect=0, project="language")
        self.start("b", "ben", generation=1)
        self.finish(self.claim("b", generation=1), generation=1)
        self.close("a")
        self.close("b")
        old, new = self.report()["offers"]
        self.assertEqual((old["disposition"], old["claim_finish"]), ("readiness changed", None))
        self.assertEqual(old["task_finish"], new["claim_finish"])
        self.assertEqual(new["area"], "project/language")
        self.assertEqual(self.report()["rows"][0]["finished_without_review"], 1)

    def test_open_offer_wrong_finish_and_unconfirmed_receipt(self):
        self.start("a", "alice")
        report = self.report()
        self.assertEqual(report["rows"][0]["open"], 1)
        self.assertEqual(report["rows"][0]["eligible_offers"], 0)
        self.events[-1]["actor"] = "alice"
        self.assertEqual(self.report()["excluded_bound_starts"], {"ordinary dispatch unconfirmed": 1})
        self.events[-1]["actor"] = CONTROLLER
        self.finish(self.claim("a"), generation=1)
        with self.assertRaisesRegex(ValueError, "does not belong"):
            self.report()

    def test_missing_launch_and_older_task_declaration_stay_visible(self):
        self.start("a", "alice")
        self.events[2]["data"]["kind"] = "other"
        self.close("a", "failed")
        totals, = self.report()["rows"]
        self.assertEqual((totals["offers"], totals["closed_without_launch"], totals["eligible_offers"]), (1, 1, 0))
        self.events[0].update(op="ready", data={"task": "proof", "project": "math", "expect": 0})
        self.assertEqual(self.report()["excluded_bound_starts"], {"project association unavailable": 1})

    def test_release_and_later_finish_do_not_credit_first_lease(self):
        self.start("a", "alice")
        first = self.claim("a")
        self.add("release", "alice", task="proof", token="token0")
        other = self.start("b", "ben", "agy", offer=False)
        self.finish(self.claim("b", generation=1), generation=1)
        self.close("b")
        self.close("a")
        row, = self.report()["offers"]
        self.assertEqual((row["disposition"], row["claim"], row["claim_finish"]),
                         ("receiver claimed", first["claim"], None))
        self.assertEqual((row["task_finisher_start"], row["task_finisher_family"]), (other, "agy"))

    def test_prospective_receipt_must_name_same_offer(self):
        self.start("a", "alice")
        receipt = self.events[-1]
        payload = json.loads(receipt["data"]["text"][len(ASSIGNMENT_PREFIX):])
        payload.update(task="proof", task_generation=0, tied_families=["codex", "agy"])
        receipt["data"]["text"] = ASSIGNMENT_PREFIX + json.dumps(payload)
        self.assertEqual(len(self.report()["offers"]), 1)
        payload["task_generation"] = 1
        receipt["data"]["text"] = ASSIGNMENT_PREFIX + json.dumps(payload)
        self.assertEqual(self.report()["excluded_bound_starts"], {"assignment names a different task or generation": 1})
