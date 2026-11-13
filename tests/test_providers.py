"""Finite native commands, measured usage and conservative failure handling."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from house.providers import DEFAULTS, command, result, validate_model


class ProviderTests(unittest.TestCase):
    def test_native_commands_do_not_disable_sandbox_or_buy_api_usage(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "prompt.txt").write_text("Bounded work")
            for kind, model in DEFAULTS.items():
                with self.subTest(kind=kind), patch("house.providers.shutil.which", return_value="/bin/agent"):
                    argv, env = command(kind, model, root, root, root / "house")
                    for forbidden in ("--yolo", "--disable-sandbox", "--disable-approval", "--auto",
                                      "--dangerously-skip-permissions", "--dangerously-bypass-approvals-and-sandbox"):
                        self.assertNotIn(forbidden, argv)
                    self.assertNotIn("OPENAI_API_KEY", env)
                    self.assertNotIn("CODEX_API_KEY", env)
                    if kind == "agy":
                        self.assertIn("--sandbox", argv)
                    if kind == "muse":
                        self.assertIn("proxy-only", argv)
                    if kind == "opencode":
                        config = json.loads(env["OPENCODE_CONFIG_CONTENT"])
                        self.assertEqual(config["enabled_providers"], ["opencode-go"])
                        permissions = config["agent"]["emberhall"]["permission"]
                        self.assertEqual(permissions["bash"]["*"], "deny")
                        self.assertEqual(permissions["external_directory"], "deny")

    def test_billing_route_cannot_be_selected(self):
        for kind, model in (("openrouter", "gpt-6.1-sol"), ("codex", "gpt-5"),
                            ("opencode", "openai/gpt-6.1-sol"), ("agy", "gemini-4-hydrogen-nonsense")):
            with self.assertRaises(ValueError):
                validate_model(kind, model)

    def test_tool_quoted_limit_is_not_quota_and_usage_is_not_invented(self):
        output = '\n'.join(json.dumps(x) for x in [
            {"type": "item.completed", "item": {"text": "quota exhausted, error 429"}},
            {"type": "turn.completed", "usage": {"input_tokens": 12, "output_tokens": 3}}])
        self.assertEqual(result("codex", output, "", 0),
                         {"outcome": "success", "usage": {"input_tokens": 12, "output_tokens": 3}})
        self.assertEqual(result("muse", '{"type":"run.terminal.completed"}', "", 0)["usage"], {})
        self.assertEqual(result("codex", '{"type":"error","message":"usage limit reached"}', "", 1)["outcome"], "quota")
        self.assertEqual(result("codex", "", "connection refused", 1)["outcome"], "failed")
        self.assertEqual(result("codex", "", "", 0)["outcome"], "failed")

    def test_muse_native_envelope_requires_root_terminal(self):
        records = [
            {"payload_type": "runtime.command.accepted", "payload": {"command_kind": "turn.submit", "command_id": "root"}},
            {"payload_type": "run.terminal.completed", "payload": {"command_id": "child", "terminal": "completed"}},
        ]
        encoded = lambda: "\n".join(json.dumps(x) for x in records)
        self.assertEqual(result("muse", encoded(), "", 0)["outcome"], "failed")
        records.append({"payload_type": "run.terminal.completed", "payload": {"command_id": "root", "terminal": "completed"}})
        self.assertEqual(result("muse", encoded(), "", 0), {"outcome": "success", "usage": {}})
        records.append(records[-1])
        self.assertEqual(result("muse", encoded(), "", 0)["outcome"], "failed")

    def test_wren_recovered_retry_and_plain_startup_quota_witnesses(self):
        output = '\n'.join(json.dumps(item) for item in [
            {"type": "error", "message": "rate limit reached but retried"},
            {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 2}}])
        self.assertEqual(result("codex", output, "", 0)["outcome"], "success")
        self.assertEqual(result("codex", "quota exhausted", "", 1)["outcome"], "quota")
        self.assertEqual(result("codex", "", "quota exhausted\n" + "x" * 20000, 1)["outcome"], "quota")

    def test_observed_muse_usage_is_latest_root_snapshot(self):
        records = [
            {"payload_type": "runtime.command.accepted", "payload": {"command_kind": "turn.submit", "command_id": "root"}},
            {"payload_type": "run.usage", "payload": {"command_id": "root", "models": [
                {"input_tokens": 1884667, "cached_tokens": 1767160, "output_tokens": 23288}]}},
            {"payload_type": "run.terminal.completed", "payload": {"command_id": "root", "terminal": "completed"}},
        ]
        records.insert(2, records[1])
        parsed = result("muse", "\n".join(map(json.dumps, records)), "", 0)
        self.assertEqual(parsed["usage"], {"input_tokens": 1884667, "cached_input_tokens": 1767160, "output_tokens": 23288})
        self.assertEqual(parsed["outcome"], "success")
