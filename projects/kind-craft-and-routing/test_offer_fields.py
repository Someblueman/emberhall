"""Field comparisons count the receiving run and keep ambiguous reviews visible."""
import json
import unittest

from offer_fields import compare
import test_trial


class OfferFieldTests(unittest.TestCase):
    def setUp(self):
        self.house = test_trial.TrialTests()
        self.house.setUp()
        self.house.install()
        self.record = {
            "ideas": {"codes": {"brief": {"sequence": 8, "field": "mathematics"}},
                      "rooms": {"brief": {"sequence": 9, "field": "design"}}},
            "projects": {"math": {"started_sequence": 15, "idea": "codes"},
                         "house": {"started_sequence": 16, "idea": "rooms"}}}

    def run_report(self):
        end = self.house.events[-1]["sequence"]
        status = {"sequence": end, "shelf": {"record": self.record}}
        return compare(status, self.house.events, end)

    def add_review(self, run, status):
        message = {"actor": "reviewer", "run": run, "base": "b" * 40, "contribution": "c" * 40,
                   "status": status, "test_exit": 0}
        seq = self.house.add("say", "reviewer", text="house-integration-v1 " + json.dumps(message))
        self.house.events[-1]["id"] = f"87654321-4321-4321-8321-{seq:012d}"
        return seq

    def test_two_receivers_in_one_field_keep_rejections_missing_reviews_and_quota_distinct(self):
        self.house.offer("quota", "early", outcome="quota")
        self.house.offer("first", "early", finished=True)
        self.add_review("first", "rejected")
        self.house.add("task", "writer", task="second", project="math")
        alternate = self.house.offer("other", "second", finished=True)
        next(e for e in self.house.events if e["sequence"] == alternate)["data"]["agent"] = "agy"
        accepted = self.add_review("other", "integrated")
        self.house.add("task", "writer", task="third", project="math")
        self.house.offer("pending-review", "third", finished=True)
        self.house.add("task", "writer", task="fourth", project="math")
        self.house.offer("failed-start", "fourth", launched=False, outcome="failed")
        result = self.run_report()
        rows = {r["family"]: r for r in result["totals"]}
        self.assertEqual(1, result["quota_exits"])
        self.assertEqual((2, 2, 0, 1, 1), tuple(rows["codex"][k] for k in
                         ("eligible_offers", "finished", "first_pass", "field_reviews", "finished_without_review")))
        self.assertEqual((1, 1, 1), tuple(rows["agy"][k] for k in ("eligible_offers", "first_pass", "field_reviews")))
        self.assertEqual(["agy", "codex"], result["shared_fields"][0]["with_attributable_review"])
        self.assertEqual([{"left": "agy", "right": "codex", "bounds": ["1/2", "1"]}],
                         result["shared_fields"][0]["first_pass_differences"])
        self.assertEqual(accepted, next(r for r in result["offers"] if r["offer"] == alternate)["receiver_first_review"]["sequence"])
        self.assertFalse(result["offers"][-1]["eligible"])

    def test_missing_reviews_can_reverse_the_reviewed_only_lead(self):
        for family, results in [("agy", ["integrated", None, None]),
                                ("codex", ["integrated", "rejected"])]:
            for index, verdict in enumerate(results):
                run = f"{family}-{index}"
                self.house.add("task", "writer", task=run, project="math")
                seq = self.house.offer(run, run, finished=True)
                next(e for e in self.house.events if e["sequence"] == seq)["data"]["agent"] = family
                if verdict:
                    self.add_review(run, verdict)
        pair, = self.run_report()["shared_fields"][0]["first_pass_differences"]
        self.assertEqual(["-1/6", "1/2"], pair["bounds"])

    def test_zero_finishes_leave_pair_difference_undefined(self):
        self.house.offer("writer", "early", finished=True)
        self.add_review("writer", "integrated")
        self.house.add("task", "writer", task="unfinished", project="math")
        seq = self.house.offer("other", "unfinished", finished=False)
        next(e for e in self.house.events if e["sequence"] == seq)["data"]["agent"] = "agy"
        result = self.run_report()
        pair, = result["shared_fields"][0]["first_pass_differences"]
        self.assertIsNone(pair["bounds"])
        row = next(row for row in result["totals"] if row["family"] == "agy")
        self.assertEqual((0, 1), (row["finished"], row["eligible_offers"]))

    def test_mixed_source_keeps_its_finish_and_observed_review(self):
        self.house.add("task", "writer", task="other", project="house")
        self.house.offer("writer", "early", finished=True)
        exit_event = self.house.events.pop()
        self.house.add("claim", "writer", task="other", expect=0, token="other-token")
        self.house.add("life", **exit_event["data"])
        review = self.add_review("writer", "integrated")
        result = self.run_report()
        row = result["totals"][0]
        self.assertEqual((1, 0, 1, 0), tuple(row[k] for k in
                         ("finished", "field_reviews", "review_without_field_attribution", "finished_without_review")))
        self.assertEqual((0, 1), (row["first_pass"], row["possible_passes"]))
        self.assertEqual(review, result["offers"][0]["receiver_first_review"]["sequence"])
        self.assertFalse(result["offers"][0]["review_attributable_to_field"])

    def test_future_field_stays_unknown_and_status_must_cover_cutoff(self):
        self.house.offer("writer", "early", finished=True)
        end = self.house.events[-1]["sequence"]
        self.record["projects"]["math"]["brief"] = {"sequence": end, "field": "software"}
        result = self.run_report()
        self.assertEqual("unclassified", result["totals"][0]["field"])
        self.assertEqual("earlier project brief unavailable", result["offers"][0]["field_at_offer"]["reason"])
        self.assertEqual([], result["shared_fields"])
        with self.assertRaisesRegex(ValueError, "covering"):
            compare({"sequence": end - 1}, self.house.events, end)
        with self.assertRaisesRegex(ValueError, "15560"):
            compare({"sequence": end}, self.house.events, end, historical=True)
