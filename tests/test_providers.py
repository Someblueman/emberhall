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
                    argv, env = command(kind, model, root, root, root / "house", runtime=root / "runtime.pyz", resident="fixture")
                    for forbidden in ("--yolo", "--disable-sandbox", "--disable-approval", "--auto",
                                      "--dangerously-skip-permissions", "--dangerously-bypass-approvals-and-sandbox"):
                        self.assertNotIn(forbidden, argv)
                    self.assertNotIn("OPENAI_API_KEY", env)
                    self.assertNotIn("CODEX_API_KEY", env)
                    if kind == "agy":
                        self.assertIn("--sandbox", argv)
                    if kind == "muse":
                        self.assertIn("proxy-only", argv)
                        self.assertIn("--trust-workspace", argv)
                        self.assertEqual(argv[argv.index("--workspace") + 1], str(root))
                        self.assertNotIn("--permission-profile", argv)
                        self.assertNotIn("--approval-mode", argv)
                        self.assertNotIn("--approval-judge", argv)
                    if kind == "opencode":
                        config = json.loads(env["OPENCODE_CONFIG_CONTENT"])
                        self.assertIn({"action": "provider.use", "resource": "opencode-go", "effect": "allow"}, config["policies"])
                        permissions = config["agents"]["emberhall"]["permissions"]
                        self.assertEqual(permissions[0], {"action": "*", "resource": "*", "effect": "deny"})
                        self.assertIn({"action": "house_journal", "resource": "*", "effect": "allow"}, permissions)
                        self.assertIn("--standalone", argv)
                        self.assertNotIn("--dir", argv)
                        self.assertEqual(env["PWD"], str(root))
                        self.assertFalse(config["lsp"])
                        self.assertFalse(config["formatter"])
                        self.assertEqual(env["OPENCODE_CONFIG_PROJECT_DISABLE"], "1")
                        tool = (root / "opencode-config/plugins/house_journal.js").read_text()
                        self.assertIn("shell: false", tool)
                        self.assertNotIn("exec(", tool)

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

    def test_actual_muse_sequential_completed_turns_sum_distinct_snapshots(self):
        output = (Path(__file__).parents[1] / 'evidence/keep-moving-runtime/muse-sequential-turns.jsonl').read_text()
        self.assertEqual(result('muse', output, '', 0), {'outcome': 'success', 'usage': {
            'input_tokens': 14055014, 'output_tokens': 39617, 'cached_input_tokens': 13797004}})
        records = [json.loads(line) for line in output.splitlines()]
        records.insert(2, records[1])  # Repeated usage is a snapshot, never another bill.
        self.assertEqual(result('muse', '\n'.join(map(json.dumps, records)), '', 0)['usage']['input_tokens'], 14055014)

    def test_muse_continuation_rejects_overlap_missing_terminal_and_reused_identity(self):
        records = [json.loads(line) for line in
            (Path(__file__).parents[1] / 'evidence/keep-moving-runtime/muse-sequential-turns.jsonl').read_text().splitlines()]
        for bad in (records[:2] + records[3:], records[:-1], records + records[:1]):
            self.assertEqual('failed', result('muse', '\n'.join(map(json.dumps, bad)), '', 0)['outcome'])

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

    def test_invalid_native_counters_cannot_strand_a_run_at_finish(self):
        output = '\n'.join([json.dumps({"type": "turn.completed", "usage": {
            "input_tokens": value, "output_tokens": 1}}) for value in (float("inf"), 1e308, 1e308)])
        self.assertEqual(result("codex", output, "", 0)["usage"], {"output_tokens": 3})

    def test_native_expired_credential_has_long_backoff_without_tool_text_false_positive(self):
        error = {"name": "APIError", "data": {"statusCode": 401, "message": "This API key has expired."}}
        self.assertEqual(result("opencode", json.dumps({"type": "error", "error": error}), "", 0),
                         {"outcome": "failed", "usage": {}, "retry_after_seconds": 86400})
        quoted = json.dumps({"type": "item.completed", "item": {"text": "This API key has expired."}})
        self.assertNotIn("retry_after_seconds", result("codex", quoted, "", 1))

    def test_observed_agy_result_binds_conversation_status_and_final_usage(self):
        opening = {"event": "init", "conversation_id": "actual-conversation"}
        final = {"event": "result", "result": {"conversation_id": "actual-conversation", "status": "SUCCESS",
            "response": "A quoted quota failure is not this result", "usage": {"input_tokens": 67536,
            "output_tokens": 6829, "cache_read_tokens": 487558, "total_tokens": 74365}}}
        encoded = lambda: '\n'.join(map(json.dumps, [opening, final]))
        self.assertEqual(result("agy", encoded(), "", 0), {"outcome": "success", "usage": {
            "input_tokens": 67536, "output_tokens": 6829, "cached_input_tokens": 487558, "total_tokens": 74365}})
        self.assertEqual(result("agy", json.dumps(final), "", 0)["outcome"], "failed")
        self.assertEqual(result("agy", encoded()+'\n'+json.dumps(final), "", 0)["outcome"], "failed")
        final["result"]["status"] = "ERROR"
        final["result"]["response"] = "usage limit reached"
        self.assertEqual(result("agy", encoded(), "", 0)["outcome"], "quota")
