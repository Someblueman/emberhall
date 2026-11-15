"""Focused tests for the resident runtime-test subprocess deadline."""

from unittest.mock import patch

from house import wake_policy as policy
from tests.test_wake_policy import RuntimeProcessTests


class RuntimeTestWindowTests(RuntimeProcessTests):
    def test_runtime_test_uses_900_second_subprocess_deadline(self):
        real_run = policy.test_sandbox.run
        timeouts = []

        def capture_run(*args, **kwargs):
            timeouts.append(kwargs.get("timeout"))
            return real_run(*args, **kwargs)

        with patch.object(policy.test_sandbox, "run", side_effect=capture_run):
            result = self.run_tests()

        self.assertTrue(result["tested"])
        self.assertEqual(timeouts, [900])

    def test_failed_runtime_test_with_900_second_deadline_still_rejects_refresh(self):
        (self.source / "tests/test_example.py").write_text(
            "import unittest\nclass Example(unittest.TestCase):\n"
            "    def test_bad(self): self.fail('window fixture failure')\n"
        )
        self.git("add", ".")
        self.git("-c", "commit.gpgsign=false", "commit", "-m", "failing fixture")

        real_run = policy.test_sandbox.run
        timeouts = []

        def capture_run(*args, **kwargs):
            timeouts.append(kwargs.get("timeout"))
            return real_run(*args, **kwargs)

        with patch.object(policy.test_sandbox, "run", side_effect=capture_run):
            result = self.run_tests()

        self.assertFalse(result["tested"])
        self.assertEqual(timeouts, [900])
        with self.assertRaisesRegex(ValueError, "did not pass"):
            policy.refresh_gate(self.record, "eve", "runtime-check", "later", self.source)
