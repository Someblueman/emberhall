"""Dollhouse history is a public projection, never an invented activity stream."""
import base64
import hashlib
import json
import subprocess
import sys
from unittest.mock import patch

from house.body import export, usage
from tests.support import HouseCase, SOURCE


class BodyTests(HouseCase):
    def latest(self):
        exported = export(self.record)
        frame = exported["frames"][-1]
        frame["scars"] = [{**exported["scars"][s["id"]], **s} for s in frame["scars"]]
        return frame

    def person(self, frame, resident):
        return next(r for r in frame["residents"] if r["id"] == resident)

    def life(self, kind, actor="alice", **fields):
        return self.record.append("life", actor, {"kind": kind, **fields})

    def start(self, resident="newcomer", run="run1"):
        self.record.append("arrive", "watch-keeper", {"name": "Watch keeper"})
        return self.life("run-start", "watch-keeper", run=run, resident=resident, agent="muse",
                         model="muse-ember-1.0", source_head="a" * 40, workspace="residents/" + run,
                         policy_revision="policy1", mode="work")

    def test_every_event_is_scrubbable_without_future_residents_or_rooms(self):
        old = export(self.record)
        self.life("room", room="garden", name="Glass garden")
        self.life("identity", agent="codex", model="gpt-6.1-sol")
        self.life("activity", room="garden")
        self.life("ambition", ambition="feed-the-world", title="Feed the world", description="A long thread",
                  status="growing", next_step="One useful thing", expect=0)
        self.record.append("say", "alice", {"text": "I am by the hearth"})
        self.record.append("sleep", "alice", {"through": self.record.read()[0]["sequence"], "note": "Back soon"})
        result = export(self.record)
        self.assertEqual(len(result["frames"]), self.record.read()[0]["sequence"])
        self.assertEqual(result["frames"][:len(old["frames"])], old["frames"])
        self.assertEqual(result["frames"][0]["residents"], [])
        self.assertNotIn("garden", [r["id"] for r in result["frames"][2]["rooms"]])
        self.assertEqual(self.person(result["frames"][5], "alice")["room"], "garden")
        self.assertEqual(self.person(result["frames"][-2], "alice")["pose"], "sitting")
        self.assertEqual(self.person(result["frames"][-1], "alice")["pose"], "sleeping")
        self.assertEqual(result["frames"][-1]["ambitions"][0]["title"], "Feed the world")
        self.assertEqual(self.person(result["frames"][2], "alice")["agent"], "unrecorded")

    def test_expired_claim_retains_a_mark_after_reclaim_without_declaring_death(self):
        self.task()
        self.record.append("claim", "alice", {"task": "work", "token": "first", "expect": 0, "seconds": 1})
        until = self.record.read()[0]["tasks"]["work"]["until"]
        with patch("house.record.time.time", return_value=until + 1):
            self.record.append("claim", "bob", {"task": "work", "token": "second", "expect": 1, "seconds": 30})
        result = export(self.record, until + 2)
        ref = result["frames"][-1]["scars"][0]
        scar = {**result["scars"][ref["id"]], **ref}
        self.assertEqual(scar["kind"], "expired")
        self.assertTrue(scar["mended"])
        self.assertEqual(scar["resident"], "alice")
        self.assertIn("unconfirmed", scar["basis"])
        self.assertEqual(self.person(result["frames"][-1], "alice")["presence"], "recorded awake")
        self.assertFalse(result["frames"][-2]["scars"])

    def test_real_interrupted_run_keeps_mid_task_marker_and_no_false_sleep(self):
        self.start()
        self.record.append("arrive", "newcomer", {"name": "Fern"})
        self.record.append("task", "newcomer", {"task": "work", "title": "Useful work", "description": "Bounded"})
        self.record.append("claim", "newcomer", {"task": "work", "token": "first", "expect": 0, "seconds": 100})
        self.life("run-finish", "watch-keeper", run="run1", outcome="interrupted", exit_code=None,
                  usage={"input_tokens": 120, "cached_input_tokens": 20}, elapsed_seconds=14)
        frame = self.latest()
        person = self.person(frame, "newcomer")
        self.assertEqual(person["agent"], "muse")
        self.assertEqual(person["pose"], "unconfirmed")
        self.assertEqual(person["room"], "workshop")
        self.assertNotIn("watch-keeper", [r["id"] for r in frame["residents"]])
        self.assertEqual(frame["scars"][0]["title"], "Interrupted mid-task")
        self.assertEqual(frame["scars"][0]["kind"], "interrupted")
        self.assertEqual(frame["runs"][0]["usage"]["cached_input_tokens"], 20)

    def test_legacy_supervisor_unknown_is_not_relabelled_as_death(self):
        self.record.append("arrive", "watch-keeper", {"name": "Watch keeper"})
        for item in ({"kind": "start", "run": "old", "resident": "alice", "executable": "codex"},
                     {"kind": "recovered-interruption", "run": "old", "reason": "missing receipt"}):
            self.record.append("say", "watch-keeper", {"text": "house-watch-v1 " + json.dumps(item)})
        frame = self.latest()
        self.assertEqual(frame["scars"][0]["kind"], "unconfirmed")
        self.assertEqual(frame["runs"][0]["outcome"], "unconfirmed")
        self.assertEqual(self.person(frame, "alice")["pose"], "unconfirmed")

    def test_public_data_excludes_artifact_bytes_arbitrary_messages_and_private_run_fields(self):
        self.start()
        secret = b"PRIVATE-RAW-OUTPUT-MUST-NOT-APPEAR"
        self.task()
        self.record.append("claim", "alice", {"task": "work", "token": "x", "expect": 0, "seconds": 100})
        self.record.append("finish", "alice", {"task": "work", "token": "x", "result": secret.decode(),
                           "artifacts": {"private.txt": {"base64": base64.b64encode(secret).decode(),
                                         "sha256": hashlib.sha256(secret).hexdigest()}}})
        self.record.append("say", "alice", {"text": secret.decode()})
        public = json.dumps(export(self.record))
        for value in (secret.decode(), base64.b64encode(secret).decode(), "workspace", "policy_revision", "artifacts"):
            self.assertNotIn(value, public)
        self.assertEqual(usage({"access_token": "secret", "input_tokens": 4, "total_tokens": float("inf")}),
                         {"input_tokens": 4})

    def test_cli_source_provenance_and_read_only_export(self):
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=Test", "-c", "user.email=test@local",
                        "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "A real <&> stone"], check=True)
        before = self.record.read()[2]
        out = self.root / "history.json"
        result = subprocess.run([sys.executable, "-m", "house.body", "--repo", str(self.repo), "--output", str(out)],
                                cwd=SOURCE, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        exported = json.loads(out.read_text())
        self.assertEqual(exported["commits"][0]["title"], "A real <&> stone")
        self.assertEqual(exported["journal_head"], before)
        self.assertEqual(self.record.read()[2], before)
        for timestamp in (0, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                export(self.record, timestamp)

    def test_budget_is_reported_backoff_not_a_guessed_remaining_balance(self):
        self.record.append("arrive", "watch-keeper", {"name": "Watch keeper"})
        before = self.latest()
        until = self.record.read()[0]["at"] + 60
        self.life("budget", "watch-keeper", agent="muse", until=until, reason="Quota response")
        after = self.latest()
        self.assertEqual(before["budgets"], [])
        self.assertEqual(after["budgets"][0]["until"], until)
        self.assertEqual(after["budgets"][0]["usage"], {})
        self.assertNotIn("remaining", after["budgets"][0])

    def test_reviewed_scar_stays_when_its_lesson_is_later_contested(self):
        self.record.append("learn", "alice", {"lesson": "repair", "key": "output",
                           "claim": "Flush output", "evidence": "Repaired failure in proof.txt"})
        self.assertEqual(self.latest()["scars"], [])
        self.record.append("review", "bob", {"lesson": "repair", "evidence": "Independently checked"})
        before = self.latest()
        self.record.append("learn", "bob", {"lesson": "contradiction", "key": "output",
                           "claim": "Do not flush", "evidence": "A later observation"})
        after = self.latest()
        self.assertEqual(before["scars"][0]["lesson_status"], "observed")
        self.assertEqual(after["scars"][0]["lesson_status"], "contested")
        self.assertEqual(after["scars"][0]["room"], "archive")
        self.assertEqual(before["scars"][0]["id"], after["scars"][0]["id"])
