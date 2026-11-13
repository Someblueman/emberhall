"""The Steward's finite provider allowlist and native headless boundaries.

No credentials are created or copied. Raw provider output stays private. Usage
here is measured tokens, never an invented currency bill or remaining allowance.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import shutil

MODELS = {
    "codex": ("gpt-6.1-sol", "gpt-6-astra"),
    "opencode": ("opencode-go/kimi-k3.1-pro", "opencode-go/minimax-m3.1-flash",
                 "opencode-go/deepseek-v4.1-flash"),
    "muse": ("muse-ember-1.0", "muse-wonder-full-1.0"),
    "agy": tuple(f"gemini-4-{family}-{effort}" for family in ("hydrogen", "argon")
                 for effort in ("low", "medium", "high", "xhigh", "max")),
}
DEFAULTS = {kind: models[0] for kind, models in MODELS.items()}
DEFAULTS["opencode"] = "opencode-go/deepseek-v4.1-flash"


def validate_model(kind, model):
    if kind not in MODELS or model not in MODELS[kind]:
        raise ValueError("provider/model is outside the Steward's allowance")


def command(kind: str, model: str, workspace: Path, private: Path,
            house_command: Path, *, runtime: Path | None = None, resident: str | None = None) -> tuple[list[str], dict]:
    validate_model(kind, model)
    executable = shutil.which(kind)
    if not executable:
        raise ValueError(f"{kind} is not installed")
    env = dict(os.environ)
    # Subscription-managed authentication only; no accidental API-key override.
    for key in ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENROUTER_API_KEY"):
        env.pop(key, None)
    if kind == "codex":
        argv = [executable, "exec", "-m", model, "--approve-for-me", "--json",
                "-c", 'model_provider="openai"', "-c", 'forced_login_method="chatgpt"',
                "-C", str(workspace), "-o", str(private / "final.txt"), "-"]
    elif kind == "muse":
        argv = [executable, "exec", "--provider", "meta", "--model", model,
                "--json", "--workspace", str(workspace), "--worktree", "off",
                "--sandbox-network", "proxy-only", "--disable-web-tools",
                "--disable-reminders", "--no-session-log", "--prompt-file", str(private / "prompt.txt")]
    elif kind == "agy":
        argv = [executable, "--model", model, "--sandbox", "--mode", "auto",
                "--output-format", "stream-json", "--log-file", str(private / "agy.log"),
                "-p", (private / "prompt.txt").read_text()]
    else:
        # A shell prefix still permits redirections. Deny shell entirely and
        # expose only a private fixed tool that invokes the pinned mailbox code.
        if runtime is None or resident is None:
            raise ValueError("OpenCode requires a pinned runtime and assigned resident")
        from .opencode_tool import configure
        configure(private, workspace, runtime, resident, env)
        permission = {"*": "deny", "read": {"*": "allow", "*.env*": "deny"},
                      "glob": "allow", "grep": "allow",
                      "edit": {"*": "allow", ".house-client": "deny", "*/.house-client": "deny"},
                      "external_directory": "deny",
                      "bash": "deny", "house_journal": "allow"}
        config = {"model": model, "small_model": model, "formatter": False, "lsp": False,
                  "enabled_providers": ["opencode-go"],
                  "agent": {"emberhall": {"mode": "primary", "permission": permission}}}
        env["OPENCODE_CONFIG_CONTENT"] = json.dumps(config)
        env["OPENCODE_DB"] = str(private / "opencode.db")
        env["OPENCODE_GOAL_STATE_PATH"] = str(private / "opencode-goal.json")
        argv = [executable, "run", "-m", model, "--agent", "emberhall", "--format", "json",
                "--dir", str(workspace), "--title", "Emberhall " + private.name,
                (private / "prompt.txt").read_text()]
    return argv, env


def result(kind: str, output: str, errors: str, exit_code: int | None) -> dict:
    """Parse only native terminal usage/errors, never tool text quoting a quota.

    stderr may report startup quota errors without a terminal JSON event. Such a
    report only triggers a conservative cooldown after nonzero process exit.
    """
    usage, terminal, error_text, plain_output = {}, False, [], []
    muse_root, muse_terminals = None, 0
    agy_root, agy_terminals = None, 0
    for line in output.splitlines():
        try:
            item = json.loads(line)
        except (ValueError, TypeError):
            plain_output.append(line)
            continue
        if not isinstance(item, dict):
            continue
        tag = item.get("type", item.get("event", item.get("payload_type", "")))
        if kind == "agy" and "event" in item:
            if tag == "init":
                root = item.get("conversation_id")
                if not isinstance(root, str) or not root or agy_root is not None:
                    return {"outcome": "failed", "usage": {}}
                agy_root = root
                continue
            if tag == "result":
                payload = item.get("result", {})
                if not isinstance(payload, dict) or agy_root is None or payload.get("conversation_id") != agy_root:
                    return {"outcome": "failed", "usage": {}}
                agy_terminals += 1
                if agy_terminals > 1:
                    return {"outcome": "failed", "usage": {}}
                terminal = payload.get("status") == "SUCCESS"
                if terminal:
                    error_text.clear()
                else:
                    error_text.append(str(payload.get("error", payload.get("response", payload.get("message", "")))))
                measured = payload.get("usage", {})
                if isinstance(measured, dict):
                    for source, target in (("input_tokens", "input_tokens"), ("output_tokens", "output_tokens"),
                                           ("cache_read_tokens", "cached_input_tokens"), ("total_tokens", "total_tokens")):
                        value = measured.get(source)
                        if type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 2**63 - 1:
                            usage[target] = value
                continue
        if kind == "muse" and "payload_type" in item:
            payload = item.get("payload", {})
            if not isinstance(payload, dict):
                continue
            if tag == "runtime.command.accepted" and payload.get("command_kind") == "turn.submit":
                root = payload.get("command_id")
                if muse_root is not None and muse_root != root:
                    return {"outcome": "failed", "usage": {}}
                muse_root = root
            if tag.startswith("run.terminal."):
                if muse_root is None or payload.get("command_id") != muse_root:
                    continue
                muse_terminals += 1
                if muse_terminals > 1:
                    return {"outcome": "failed", "usage": {}}
                terminal = tag == "run.terminal.completed" and payload.get("terminal") == "completed"
                if not terminal:
                    error_text.append(str(payload.get("reason", "")))
                else:
                    error_text.clear()
            if tag == "run.usage" and muse_root is not None and payload.get("command_id") == muse_root:
                measured = {}
                for model in payload.get("models", []):
                    for source, target in (("input_tokens", "input_tokens"), ("output_tokens", "output_tokens"),
                                           ("cached_tokens", "cached_input_tokens")):
                        value = model.get(source)
                        if type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 2**63 - 1:
                            measured[target] = measured.get(target, 0) + value
                usage = measured  # A run-usage event is a snapshot, not an increment.
            continue
        if tag in {"turn.completed", "run.terminal.completed", "result", "step_finish"}:
            terminal = tag != "step_finish" or item.get("part", {}).get("reason") == "stop"
            if tag in {"turn.completed", "result"}:
                error_text.clear()  # Native retry recovered before successful completion.
            if item.get("is_error"):
                terminal = False
                error_text.append(str(item.get("error", item.get("result", "provider failed"))))
            native = item.get("usage", {})
            if tag == "step_finish":
                native = item.get("part", {}).get("tokens", {})
                native = {"input_tokens": native.get("input"), "output_tokens": native.get("output"),
                          "cached_input_tokens": native.get("cache", {}).get("read")}
            if isinstance(native, dict):
                for key in ("input_tokens", "output_tokens", "cached_input_tokens", "total_tokens"):
                    value = native.get(key)
                    if type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 2**63 - 1:
                        usage[key] = usage.get(key, 0) + value
        if tag in {"error", "turn.failed", "run.terminal.failed"}:
            error_text.append(json.dumps(item.get("error", item.get("message", ""))))
    if exit_code not in (None, 0):
        error_text.append(errors)
        if not terminal:
            error_text.extend(plain_output)
    failure = " ".join(error_text)
    credentials = bool(re.search(r'API key.{0,30}expired|invalid.api.key|authentication.failed|'
                                 r'"statusCode"\s*:\s*401|HTTP\s+401', failure, re.I))
    if credentials:
        return {"outcome": "failed", "usage": usage, "retry_after_seconds": 86400}
    quota = bool(re.search(r"quota|usage.limit|rate.limit|too many requests|\b429\b|allowance.exhaust",
                           failure, re.I))
    outcome = "quota" if quota else "success" if exit_code == 0 and terminal and not error_text else "failed"
    return {"outcome": outcome, "usage": usage}
