import json
import unittest

from house.craft_outcomes import public_window
from tests import test_craft_offers as offers_tests


class PublicReceivers(unittest.TestCase):
    def setUp(self):
        self.work = offers_tests.CraftOffers()
        self.work.setUp()

    def report(self, events=None):
        events = self.work.events if events is None else events
        return public_window(events, len(events), "head", "source")["receiving"]

    def review(self, run, status):
        work = self.work
        seq = work.add("say", "reviewer", text="house-integration-v1 " + json.dumps({
            "run": run, "actor": "reviewer", "base": "a" * 40,
            "contribution": "b" * 40, "status": status,
            "test_exit": 0 if status == "integrated" else 1,
            "test_commands": [["private-command"]]}))
        work.events[-1]["id"] = f"00000000-0000-4000-8000-{seq:012x}"
        return seq

    def test_other_claimant_does_not_finish_the_receivers_offer(self):
        work = self.work
        work.start("other-private", "other-person", "agy", offer=False)
        offered = work.start("receiver-private", "receiver-person")
        claim = work.claim("other-private")
        work.finish(claim)
        work.close("other-private")
        work.close("receiver-private")
        result = self.report()
        row, = result["rows"]
        self.assertEqual((row["eligible_offers"], row["claimed_elsewhere"],
                          row["receiver_finished"], row["reviewed_receiver_runs"]), (1, 1, 0, 0))
        self.assertEqual(row["examples"][0], {
            "offer": offered, "assignment": offered + 2, "claim": claim["claim"],
            "finish": claim["finish"], "first_review": None, "disposition": "claimed elsewhere"})
        raw = json.dumps(result)
        for private in ("receiver-private", "receiver-person", "other-person", "token0", "private-command"):
            self.assertNotIn(private, raw)

    def test_quota_open_missing_launch_and_repeated_offers(self):
        work = self.work
        work.start("quota", "q")
        work.close("quota", "quota")
        work.start("no-launch", "n")
        work.events[-2]["data"]["kind"] = "other"
        work.close("no-launch", "failed")
        first = work.start("first", "one")
        work.close("first", "failed")
        last = work.start("last", "two")
        work.finish(work.claim("last"))
        work.close("last")
        work.start("open", "three", generation=1)
        row, = self.report()["rows"]
        self.assertEqual((row["offers"], row["quota"], row["open"], row["closed_without_launch"]), (5, 1, 1, 1))
        self.assertEqual((row["eligible_offers"], row["unique_eligible_tasks"], row["receiver_finished"],
                          row["claimed_elsewhere"], row["finished_without_review"]), (2, 1, 1, 1, 1))
        self.assertEqual([x["offer"] for x in row["examples"]], [first, last])
        self.assertEqual(self.report()["distinct_eligible_tasks"], 1)

    def test_first_rejection_remains_and_examples_are_bounded(self):
        work = self.work
        for generation in range(4):
            work.start(f"r{generation}", f"person{generation}", generation=generation)
            work.finish(work.claim(f"r{generation}", generation), generation)
            work.close(f"r{generation}")
            first = self.review(f"r{generation}", "tests-failed")
            self.review(f"r{generation}", "integrated")
        row, = self.report()["rows"]
        self.assertEqual((row["first_pass"], row["reviewed_receiver_runs"], row["finished_without_review"]), (0, 4, 0))
        self.assertEqual(len(row["examples"]), 3)
        self.assertEqual(row["examples"][-1]["first_review"], first)

    def test_missing_context_and_reserved_route_are_not_failures(self):
        work = self.work
        work.start("unknown", "one")
        work.close("unknown")
        start = work.start("helper", "two")
        work.events[start - 1]["data"]["model"] = "gpt-6.1-terra"
        work.close("helper")
        result = self.report(work.events[1:])
        self.assertEqual((result["rows"], result["unconfirmed"], result["excluded_reserved"]), ([], 1, 1))


if __name__ == "__main__":
    unittest.main()
