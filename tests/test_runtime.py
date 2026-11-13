"""Real immutable zipapp bootstrap, corruption rejection and interrupted switch."""
from pathlib import Path
from unittest.mock import patch

from house import council, runtime, wake_policy
from house.home_work import git
from tests.support import HouseCase, SOURCE
from tests.test_council import approval


class RuntimeTests(HouseCase):
    def setUp(self):
        super().setUp()
        identity = self.record.read()[0]["house_id"]
        patched = patch.object(council, "APPROVED_HOUSE", identity)
        patched.start()
        self.addCleanup(patched.stop)
        (self.repo / "house").mkdir()
        (self.repo / "tests").mkdir()
        (self.repo / "docs").mkdir()
        for path in (SOURCE / "house").glob("*.py"):
            (self.repo / "house" / path.name).write_bytes(path.read_bytes())
        (self.repo / "tests/test_small.py").write_text("# fixture test path\n")
        (self.repo / "docs/WATCH_PROMPT.md").write_text("Historical watch prompt\n")
        git(self.repo, "add", ".")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c", "user.email=test@local",
            "commit", "-m", "Runtime fixture")
        self.record.append("council-authorize", "alice", approval())
        self.record.append("council-wake-authorize", "alice", wake_policy.approval(
            "Synthetic runtime fixture", wake_policy.source_snapshot(self.repo)))

    def test_bootstrap_pins_actual_bytes_and_no_unwitnessed_second_activation(self):
        selected = runtime.activate(self.record, "alice")
        self.assertEqual(runtime.selected(self.record), selected)
        with self.assertRaisesRegex(ValueError, "tested later"):
            runtime.activate(self.record, "alice")
        with Path(selected["entry"]).open("ab") as output:
            output.write(b"changed bytes")
        with self.assertRaisesRegex(ValueError, "bytes changed"):
            runtime.selected(self.record)

    def test_interruption_before_pointer_leaves_verified_archive_and_retries(self):
        with patch("house.runtime.os.replace", side_effect=OSError("power loss")):
            with self.assertRaisesRegex(OSError, "power loss"):
                runtime.activate(self.record, "alice")
        self.assertFalse((self.record.common / "house-home/active-runtime.json").exists())
        selected = runtime.activate(self.record, "alice")
        self.assertEqual(runtime.selected(self.record)["runtime_sha256"], selected["runtime_sha256"])

    def test_bootstrap_refuses_committed_enforcement_change_after_authorization(self):
        (self.repo / "house/providers.py").write_text("# changed boundary\n")
        git(self.repo, "add", ".")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c", "user.email=test@local",
            "commit", "-m", "Unexpected alteration")
        with self.assertRaisesRegex(ValueError, "protected enforcement"):
            runtime.activate(self.record, "alice")
