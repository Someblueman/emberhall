"""Real journal state must survive the journey into the illustrated house."""
import base64
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

from house.illustration import render
from tests.support import HouseCase, SOURCE

NS = "{http://www.w3.org/2000/svg}"


class IllustrationTests(HouseCase):
    def picture(self, at=None):
        return ET.fromstring(render(self.record, at))

    def groups(self, picture, attribute):
        return {node.attrib[attribute]: node for node in picture.iter()
                if attribute in node.attrib}

    def test_awake_sleep_and_expired_lease_are_separate_states(self):
        self.task()
        self.record.append("claim", "alice", {"task": "work", "token": "one",
                           "expect": 0, "seconds": 30})
        state, _, head = self.record.read()
        before = self.picture(state["at"])
        self.assertEqual(self.groups(before, "data-task")["work"].get("data-state"), "claimed")
        after = self.picture(state["tasks"]["work"]["until"])
        self.assertEqual(self.groups(after, "data-task")["work"].get("data-state"), "expired")
        self.assertEqual(self.groups(after, "data-resident")["alice"].get("data-state"), "awake")
        metadata = json.loads(after.find(NS + "metadata").text)
        self.assertEqual(metadata["journal_head"], head)
        self.assertEqual(metadata["expired_claims"], ["work"])
        self.record.append("sleep", "bob", {"through": state["sequence"], "note": "Back tomorrow"})
        picture = self.picture()
        bob = self.groups(picture, "data-resident")["bob"]
        self.assertEqual(bob.get("data-state"), "asleep")
        self.assertIn("Back tomorrow", bob.find(NS + "title").text)
        self.assertEqual(set(self.groups(picture, "data-resident")), {"alice", "bob"})
        self.record.append("wake", "bob", {})
        self.assertEqual(self.groups(self.picture(), "data-resident")["bob"].get("data-state"), "awake")

    def test_finished_work_leaves_bench_and_only_reviewed_repairs_leave_seams(self):
        self.task()
        self.record.append("claim", "alice", {"task": "work", "token": "one",
                           "expect": 0, "seconds": 30})
        self.record.append("finish", "alice", {"task": "work", "token": "one", "result": "Repaired",
                           "artifacts": {"proof.txt": {"sha256": hashlib.sha256(b"proof").hexdigest(),
                           "base64": base64.b64encode(b"proof").decode()}}})
        self.record.append("learn", "alice", {"lesson": "seam", "key": "output-repair",
                           "claim": "Flush output", "evidence": "Failure and repair in proof.txt"})
        self.assertFalse(self.groups(self.picture(), "data-task"))
        self.assertFalse(self.groups(self.picture(), "data-lesson"))
        self.record.append("review", "bob", {"lesson": "seam", "evidence": "Independently reran proof"})
        seam = self.groups(self.picture(), "data-lesson")["seam"]
        self.assertIn("proof.txt", seam.find(NS + "title").text)
        self.record.append("learn", "bob", {"lesson": "conflict", "key": "output-repair",
                           "claim": "Do not flush", "evidence": "Conflicting repair"})
        self.assertFalse(self.groups(self.picture(), "data-lesson"))

    def test_labels_cannot_inject_svg_and_controls_stay_parseable(self):
        actor = 'guest<&"'
        name = '<script>alert("x")</script> & \x00'
        self.record.append("arrive", actor, {"name": name})
        self.record.append("task", actor, {"task": 'task"<>&', "title": name,
                           "description": '<image href="https://example.invalid"/>'})
        picture = self.picture()
        self.assertFalse(list(picture.iter(NS + "script")))
        self.assertFalse(list(picture.iter(NS + "image")))
        resident = self.groups(picture, "data-resident")[actor]
        self.assertIn(name.replace("\x00", "\ufffd"), resident.find(NS + "title").text)
        self.assertIn('task"<>&', self.groups(picture, "data-task"))

    def test_cli_reads_real_git_history_and_does_not_mutate_record(self):
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=Test",
                        "-c", "user.email=test@local", "-c", "commit.gpgsign=false",
                        "commit", "--allow-empty", "-qm", "A real foundation <&>"], check=True)
        before = self.record.read()[2]
        source = self.record.git("rev-parse", "HEAD").decode().strip()
        output = self.root / "portrait.svg"
        result = subprocess.run([sys.executable, "-m", "house.illustration", "--repo", str(self.repo),
                                 "--output", str(output)], cwd=SOURCE, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        picture = ET.parse(output).getroot()
        self.assertEqual(self.record.read()[2], before)
        self.assertEqual(set(self.groups(picture, "data-commit")), {source})
        metadata = json.loads(picture.find(NS + "metadata").text)
        self.assertEqual(metadata["source_head"], source)
        self.assertEqual(metadata["journal_head"], before)
        self.assertEqual(picture.get("viewBox").split()[2], "440")
        self.assertTrue(picture.find(NS + "desc").text)

    def test_machine_watch_is_a_clock_not_an_independent_resident(self):
        self.record.append("arrive", "watch-keeper", {"name": "Watch keeper"})
        picture = self.picture()
        self.assertNotIn("watch-keeper", self.groups(picture, "data-resident"))
        self.assertIn("watch-keeper", self.groups(picture, "data-machine"))
        self.assertIn("2 residents recorded awake", picture.find(NS + "desc").text)

    def test_observation_cannot_predate_snapshot_or_be_nonfinite(self):
        for at in (0, float("nan"), float("inf")):
            with self.subTest(at=at), self.assertRaisesRegex(ValueError, "observation"):
                render(self.record, at)
        at = self.record.read()[0]["at"]
        self.assertEqual(render(self.record, at), render(self.record, at))
