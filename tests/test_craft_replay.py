import copy
import json
import unittest

from house import craft_replay as replay
from house.life import CONTROLLER
from house.work_metrics import ASSIGNMENT_PREFIX


class CraftReplay(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.status = {"sequence": 1000, "life": {"runs": {}}, "shelf": {"record": {
            "projects": {p: {"idea": p, "started_sequence": 0} for p in ("old", "new")},
            "ideas": {p: {"brief": {"field": "mathematics", "sequence": 0}}
                      for p in ("old", "new")}}}}

    def add(self, op, actor=CONTROLLER, **data):
        seq = len(self.events) + 1
        self.events.append(dict(id=f"00000000-0000-4000-8000-{seq:012x}", sequence=seq,
                                op=op, actor=actor, data=data))
        return seq

    def start(self, run, family, **extra):
        data = dict(kind="run-start", run=run, resident=run, agent=family,
                    model="ordinary", mode="work") | extra
        seq = self.add("life", **data)
        self.status["life"]["runs"][run] = dict(data, started_sequence=seq)
        return seq

    def contribution(self, run, family, *, outcome="success", review=True):
        self.add("task", task=run, project="old")
        self.start(run, family)
        self.add("claim", run, task=run)
        self.add("finish", run, task=run)
        self.add("life", kind="run-finish", run=run, outcome=outcome)
        if review:
            self.review(run)

    def review(self, run, status="reviewed", actor="reader"):
        return self.add("say", actor, text="house-integration-v1 " + json.dumps(dict(
            run=run, actor=actor, base="a" * 40, contribution="b" * 40,
            status=status, test_exit=0)))

    def dispatch(self, run="next", family="agy", **extra):
        self.add("task", task=run, project="new")
        seq = self.start(run, family, task=run, backlog=True, **extra)
        self.add("say", text=ASSIGNMENT_PREFIX + json.dumps(dict(
            run=run, lane="work", reason="balanced", helper=False,
            requested_agent=None, help_request=extra.get("help_request"))))
        self.events[-1]["id"] = f"home-{run}-assignment"
        return seq

    def report(self, first):
        return replay.replay(self.status, [self.events], first, len(self.events))

    def test_two_families_across_projects_keep_recorded_baseline(self):
        self.contribution("a", "codex")
        self.contribution("b", "muse")
        seq = self.dispatch()
        report = self.report(seq)
        decision, = report["decisions"]
        self.assertEqual(report["covered"], 1)
        self.assertEqual(decision["baseline"], "agy")
        self.assertIsNone(decision["recorded_shortlist"])
        self.assertFalse(report["alternative_outcomes_estimated"])
        self.assertEqual(set(decision["supported_families"]), {"codex", "muse"})

    def test_later_review_cannot_justify_earlier_choice(self):
        self.contribution("a", "codex")
        self.contribution("b", "muse", review=False)
        seq = self.dispatch()
        late = self.review("b")
        first = self.report(seq)["decisions"][0]
        self.assertFalse(first["covered"])
        self.assertEqual(first["earlier"]["muse"]["first_reviews"], [])
        later = self.dispatch("later")
        second = self.report(later)["decisions"][0]
        self.assertTrue(second["covered"])
        self.assertEqual(second["earlier"]["muse"]["first_reviews"][0]["sequence"], late)

    def test_later_exit_and_quota_are_not_earlier_evidence(self):
        self.contribution("a", "codex", outcome="quota")
        self.contribution("b", "muse", review=False)
        finish = self.events.pop()
        seq = self.dispatch()
        self.assertFalse(self.report(seq)["decisions"][0]["supported_families"])
        finish["sequence"] = len(self.events) + 1
        self.events.append(finish)
        self.assertFalse(self.report(seq)["decisions"][0]["supported_families"])

    def test_one_first_review_per_run_even_with_several_tasks_and_retries(self):
        self.contribution("a", "codex", review=False)
        self.events.pop()  # second claim in the same still-active run
        self.add("task", task="second", project="new")
        self.add("claim", "a", task="second")
        self.add("finish", "a", task="second")
        self.add("life", kind="run-finish", run="a", outcome="success")
        first = self.review("a", "rejected")
        self.review("a")
        seq = self.dispatch()
        row = self.report(seq)["decisions"][0]["earlier"]["codex"]
        self.assertEqual(len(row["claims"]), 2)
        self.assertEqual(row["first_reviews"], [{"run_start": 2, "sequence": first, "status": "rejected"}])

    def test_field_versions_and_conflicts_are_not_backfilled(self):
        record = self.status["shelf"]["record"]
        record["ideas"]["new"]["brief"]["sequence"] = 99
        self.assertIsNone(replay.field_at(self.status, [], "new", 5)["field"])
        self.add("shelf", kind="idea-brief", idea="new", brief={"field": "art"})
        self.assertEqual(replay.field_at(self.status, self.events, "new", 5)["field"], "art")
        record["ideas"]["new"]["brief"] = {"sequence": 1, "field": "design"}
        self.assertEqual(replay.field_at(self.status, self.events, "new", 5)["reason"],
                         "conflicting brief field")
        record["projects"]["new"]["started_sequence"] = 9
        self.assertIsNone(replay.field_at(self.status, self.events, "new", 5)["field"])

    def test_unknown_mixed_and_missing_reviews_remain_visible(self):
        self.contribution("a", "codex", review=False)
        self.events.pop()
        self.add("task", task="other", project="unknown")
        self.add("claim", "a", task="other")
        self.add("life", kind="run-finish", run="a", outcome="failed")
        self.review("a")
        self.contribution("b", "muse", review=False)
        seq = self.dispatch()
        decision = self.report(seq)["decisions"][0]
        self.assertFalse(decision["covered"])
        self.assertEqual(decision["earlier"]["muse"]["without_field_review"], [10])
        self.assertEqual(decision["missing_earlier"]["project missing from status"], 1)
        self.assertEqual(decision["missing_earlier"]["mixed or unclassified reviewed contribution"], 1)
        self.assertEqual(decision["earlier"]["codex"]["claims"][0]["outcome"], "failed")

    def test_new_project_brief_needs_its_earlier_version(self):
        record = self.status["shelf"]["record"]
        record["projects"]["new"]["brief"] = {"sequence": 99, "field": "software"}
        self.assertIsNone(replay.field_at(self.status, [], "new", 5)["field"])
        self.add("shelf", kind="project-brief", project="new", brief={"field": "art"})
        self.assertEqual(replay.field_at(self.status, self.events, "new", 5)["field"], "art")

    def test_special_routes_and_quota_dispatch_are_excluded(self):
        cases = [({"model": "gpt-6-luna"}, "helper"),
                 ({"explore_generation": 2}, "Explorer"), ({"ballot_open": "choice"}, "ballot"),
                 ({"mode": "review"}, "review")]
        for extra, reason in cases:
            self.setUp()
            seq = self.dispatch(family="codex", **extra)
            self.assertEqual(self.report(seq)["excluded"], {reason: 1})
        self.setUp()
        seq = self.dispatch()
        self.add("life", kind="run-finish", run="next", outcome="quota")
        report = self.report(seq)
        self.assertEqual((report["ordinary_balanced_starts"], report["quota_excluded"]), (1, 1))
        self.assertEqual(report["task_bound_project_starts"], 0)

    def test_untargeted_help_and_missing_or_retagged_tasks(self):
        self.add("life", kind="help", request="h", task="next")
        seq = self.dispatch(help_request="h")
        self.assertEqual(self.report(seq)["task_bound_project_starts"], 1)
        self.events[0]["data"]["target_resident"] = "next"
        self.assertEqual(self.report(seq)["excluded"], {"explicit request": 1})
        self.events[0]["data"].pop("target_resident")
        self.events[1]["data"].pop("project")
        self.add("ready", task="next", project="new")
        self.assertEqual(self.report(seq)["task_bound_project_starts"], 0)

    def test_bad_status_gaps_and_receipt_spoofs_fail_closed(self):
        seq = self.dispatch()
        saved = copy.deepcopy(self.status)
        self.status["life"]["runs"]["next"]["agent"] = "muse"
        with self.assertRaisesRegex(ValueError, "disagree"):
            self.report(seq)
        self.status = saved
        with self.assertRaisesRegex(ValueError, "contiguous"):
            replay.replay(self.status, [self.events[::2]], seq, len(self.events))
        self.events[-1]["actor"] = "next"
        self.assertEqual(self.report(seq)["excluded"], {"ordinary assignment unconfirmed": 1})


if __name__ == "__main__":
    unittest.main()
