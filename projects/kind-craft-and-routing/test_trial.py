"""Exercise the combined trial from installation through late independent review."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import trial


class TrialTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.descriptor = json.loads(trial.DESCRIPTOR.read_text())
        self.manifest = {f"house/{module}.py": "f" * 64 for module in trial.CHOICE_MODULES}
        self.manifest.update(self.descriptor["files"])
        self.add("task", "writer", task="early", project="math")
        self.add("council-propose", "writer", proposal=trial.PROPOSAL, mode="renovation",
                 text=trial.DESCRIPTOR.read_text())

    def add(self, op, actor="watch-keeper", **data):
        seq = self.events[-1]["sequence"] + 1 if self.events else trial.PROPOSED_AT - 1
        self.events.append({"sequence": seq, "id": str(seq), "actor": actor, "op": op, "data": data})
        return seq

    def install(self, *, op="renovation-install", **changes):
        data = {"protected_files": self.manifest, "source_head": "a" * 40}
        if op == "renovation-install":
            data["proposal"] = trial.PROPOSAL
        return self.add(op, "keeper-01" if op == "owner-migrate" else "watch-keeper", **(data | changes))

    def offer(self, run, task, *, launched=True, finished=False, outcome="success", help_request=None):
        binding = {"help_request": help_request} if help_request else {"backlog": True, "task": task, "task_generation": 0}
        start = self.add("life", kind="run-start", run=run, resident=run, agent="codex", model="ordinary",
                         mode="work", **binding)
        receipt = {"run": run, "reason": "balanced", "lane": "work", "helper": False, "help_request": help_request,
                   "task": task, "task_generation": 0, "tied_families": ["codex", "agy"]}
        self.add("say", text="house-assignment-v1 " + json.dumps(receipt))
        self.events[-1]["id"] = f"home-{run}-assignment"
        if launched:
            self.add("life", kind="run-launched", run=run)
        if finished:
            self.add("claim", run, task=task, expect=0, token="private-claim-token")
            self.add("finish", run, task=task, token="private-claim-token")
        self.add("life", kind="run-finish", run=run, outcome=outcome)
        return start

    def report(self):
        return trial.assess(self.events, self.events[-1]["sequence"])

    def test_an_enactment_a_failed_install_and_a_partial_upgrade_do_not_start_trial(self):
        self.add("council-enact", proposal=trial.PROPOSAL)
        self.add("renovation-failed", proposal=trial.PROPOSAL)
        self.install(op="owner-migrate", protected_files={"house/home.py": self.descriptor["files"]["house/home.py"]})
        self.offer("unobserved", "early", finished=True)
        self.assertIsNone(self.report()["installed_at"])
        installed = self.install(op="owner-migrate")
        self.assertEqual(installed, self.report()["installed_at"])
        self.assertEqual([], self.report()["enrolled"])

    def test_first_twenty_keep_quota_out_missing_launch_visible_and_late_review_joined(self):
        self.install()
        self.offer("quota", "early", outcome="quota")
        first = self.offer("receiver", "early", finished=True)
        for i in range(1, 21):
            self.offer(f"run-{i}", f"task-{i}", launched=i != 1, outcome="failed")
        self.offer("retry", "task-2")
        changed = self.install(proposal="new", protected_files=self.manifest | {"house/home.py": "0" * 64})
        self.offer("following", "another")
        review = {"run": "receiver", "actor": "reviewer", "base": "b" * 40, "contribution": "c" * 40,
                  "status": "integrated", "test_exit": 0}
        seq = self.add("say", "reviewer", text="house-integration-v1 " + json.dumps(review))
        self.events[-1]["id"] = "87654321-4321-4321-8321-123456789abc"
        report = self.report()
        self.assertEqual(("twenty baseline offers observed", changed, 1, 20),
                         (report["state"], report["runtime_changed_at"], report["quota_exits"], len(report["enrolled"])))
        row = report["enrolled"][0]
        self.assertEqual((first, "project/math", seq), (row["offer"], row["area"], row["receiver_first_review"]["sequence"]))
        self.assertEqual(report["twentieth_start"], report["enrolled"][-1]["offer"])
        self.assertEqual(19, sum(r["eligible_offers"] for r in report["outcomes"]))
        opportunities = {r["family"]: (r["chosen_in_tie"], r["in_tie"]) for r in report["opportunities"]}
        self.assertEqual({"codex": (20, 20), "agy": (0, 20), "opencode": (0, 0), "muse": (0, 0)}, opportunities)
        self.assertNotIn("private-claim-token", json.dumps(report))

    def test_changed_runtime_stops_enrollment_without_restarting_the_count(self):
        self.install()
        self.install(proposal="unrelated", protected_files=self.manifest | {"house/body.py": "e" * 64})
        self.offer("one", "early")
        self.install(proposal="new", protected_files=self.manifest | {"house/home.py": "0" * 64})
        self.install()
        self.offer("later", "different")
        result = self.report()
        self.assertEqual("choice code changed before twenty offers qualified", result["state"])
        self.assertEqual(1, len(result["enrolled"]))

    def test_later_install_missing_one_choice_module_closes_enrollment(self):
        self.install()
        first = self.offer("one", "early", finished=True)
        partial = self.manifest.copy()
        del partial["house/course.py"]
        stop = self.install(op="owner-migrate", protected_files=partial)
        self.install()
        self.offer("later", "different")
        result = self.report()
        self.assertEqual(stop, result["runtime_unverified_at"])
        self.assertIsNone(result["runtime_changed_at"])
        self.assertEqual("choice code unverified before twenty offers qualified", result["state"])
        self.assertEqual([first], [row["offer"] for row in result["enrolled"]])

    def test_reviewed_files_without_initial_choice_manifest_cannot_enroll(self):
        installed = self.install(protected_files=self.descriptor["files"])
        self.offer("one", "early")
        result = self.report()
        self.assertEqual((installed, installed, []),
                         (result["installed_at"], result["runtime_unverified_at"], result["enrolled"]))

    def test_earlier_help_request_resolves_an_offer_without_changing_the_trial_start(self):
        installed = self.install()
        offer = self.offer("helper-request-recipient", "early", help_request="carry")
        missing = self.report()
        self.assertEqual(([], offer, [offer]), (missing["enrolled"], missing["first_unresolved"],
                                                missing["unmatched_roster_starts"]))
        self.events.insert(0, {"sequence": trial.PROPOSED_AT - 2, "op": "life", "actor": "requester",
                               "id": "carry-request", "data": {"kind": "help", "request": "carry", "task": "early"}})
        complete = self.report()
        self.assertEqual((installed, None, [offer]), (complete["installed_at"], complete["first_unresolved"],
                         [row["offer"] for row in complete["enrolled"]]))

    def test_command_refuses_lost_proposal_and_conflicting_installation(self):
        self.install(protected_files={})
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page.json"
            end = self.events[-1]["sequence"]
            for events, reason in ((self.events, "different files"), (self.events[-1:], "include proposal")):
                page.write_text(json.dumps({"events": events, "through": end, "latest": end, "has_more": False}))
                run = subprocess.run([sys.executable, str(trial.ROOT / "projects/kind-craft-and-routing/trial.py"),
                                      str(page)], cwd=tmp, capture_output=True, text=True)
                self.assertEqual(2, run.returncode)
                self.assertIn(reason, run.stderr)
                self.assertEqual("", run.stdout)

    def test_new_baseline_requires_delivery_declaration_and_matching_installation(self):
        frozen = json.loads(trial.ONE_FAMILY_MANIFEST.read_text())
        source = frozen["source_commit"]
        self.assertEqual(set(self.descriptor["files"]) | {"house/review_completion.py", "house/shelf.py"}
                         | {f"house/{name}.py" for name in trial.CHOICE_MODULES}, set(frozen["files"]))
        while self.events[-1]["sequence"] < trial.DELIVERED_AT - 1:
            self.add("say", text="other business")
        delivery = {"commit": source, "remote_main": source, "repository": "Someblueman/emberhall"}
        self.add("say", text="house-source-delivery-v1 " + json.dumps(delivery))
        entry = self.events[-1]
        entry["id"] = "source-delivered-" + source
        self.install(op="owner-migrate", protected_files=frozen["files"])
        while self.events[-1]["sequence"] < trial.DECLARED_AT - 1:
            self.add("say", text="other business")
        self.add("task", "mica", task="craft-one-family-baseline", project="house-after-rooms-20261119")
        self.add("council-enact", proposal="shelf-change")
        self.install(op="owner-migrate", scope="another-upgrade", protected_files=frozen["files"])
        self.install(proposal="code-only", protected_files=frozen["files"])
        partial = dict(frozen["files"])
        del partial["house/shelf.py"]
        self.install(op="owner-migrate", scope=trial.SHELF_UPGRADE, protected_files=partial)
        self.offer("before", "early")

        def selected():
            return trial.assess(self.events, self.events[-1]["sequence"], trial.ONE_FAMILY)

        self.assertIsNone(selected()["installed_at"])
        installed = self.install(op="owner-migrate", protected_files=frozen["files"])
        self.offer("quota", "late", outcome="quota")
        admitted = self.offer("after", "late", finished=True)
        stop = self.install(proposal="shelf-change", protected_files=partial)
        self.offer("later", "another")
        result = selected()
        self.assertEqual((installed, 1, [admitted], stop, 0),
                         (result["installed_at"], result["quota_exits"], [r["offer"] for r in result["enrolled"]],
                          result["runtime_unverified_at"], result["routing_weight"]))
        self.assertIsNone(self.report()["installed_at"])
        declaration = self.events[trial.DECLARED_AT - self.events[0]["sequence"]]
        declaration["data"]["project"] = "other"
        with self.assertRaisesRegex(ValueError, "trial declaration"):
            selected()
        declaration["data"]["project"] = "house-after-rooms-20261119"
        entry["actor"] = "another resident"
        with self.assertRaisesRegex(ValueError, "delivery"):
            selected()
