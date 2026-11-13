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
            house_command: Path) -> tuple[list[str], dict]:
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
        # OpenCode 1.x has tool permissions, not an OS shell sandbox. General shell
        # execution is therefore denied. Its sole shell capability is our fixed
        # journal client; tests can be witnessed by a separately sandboxed kind.
        permission = {"*": "deny", "read": {"*": "allow", "*.env*": "deny"},
                      "glob": "allow", "grep": "allow",
                      "edit": {"*": "allow", ".house-client": "deny", "*/.house-client": "deny"},
                      "external_directory": "deny",
                      "bash": {"*": "deny", str(house_command) + " *": "allow"}}
        config = {"model": model, "small_model": model,
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
    for line in output.splitlines():
        try:
            item = json.loads(line)
        except (ValueError, TypeError):
            plain_output.append(line)
            continue
        if not isinstance(item, dict):
            continue
        tag = item.get("type", item.get("event", item.get("payload_type", "")))
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
                        if type(value) in (int, float) and math.isfinite(value) and value >= 0:
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
                    if type(value) in (int, float) and math.isfinite(value) and value >= 0:
                        usage[key] = usage.get(key, 0) + value
        if tag in {"error", "turn.failed", "run.terminal.failed"}:
            error_text.append(json.dumps(item.get("error", item.get("message", ""))))
    if exit_code not in (None, 0):
        error_text.append(errors)
        if not terminal:
            error_text.extend(plain_output)
    quota = bool(re.search(r"quota|usage.limit|rate.limit|too many requests|\b429\b|allowance.exhaust",
                           " ".join(error_text), re.I))
    outcome = "quota" if quota else "success" if exit_code == 0 and terminal and not error_text else "failed"
    return {"outcome": outcome, "usage": usage}
