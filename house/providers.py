"""The Steward's finite provider allowlist and native headless boundaries.

No credentials are created. OpenCode reuses only the existing selected Go login
in its private database. Raw output stays private. Usage is measured tokens,
never an invented currency bill or remaining allowance.
"""
from __future__ import annotations

import datetime
import json
import math
import os
from pathlib import Path
import re
import shutil
import time

MODELS = {
    "codex": ("gpt-6.1-sol", "gpt-6-astra", "gpt-6-luna", "gpt-6.1-terra", "gpt-6.2-astra"),
    "opencode": ("opencode-go/kimi-k3.1-pro", "opencode-go/minimax-m3.1-flash",
                 "opencode-go/deepseek-v4.1-flash"),
    "muse": ("muse-ember-1.0", "muse-wonder-full-1.0"),
    "agy": tuple(f"gemini-4-{family}-{effort}" for family in ("hydrogen", "argon")
                 for effort in ("low", "medium", "high", "xhigh", "max")),
}
DEFAULTS = {kind: models[0] for kind, models in MODELS.items()}
DEFAULTS["opencode"] = "opencode-go/deepseek-v4.1-flash"
# Steward course correction (15 November): ordinary runs rotate across these
# routes instead of always taking the default. No route defaults to the lowest
# effort. Helpers keep their own Codex routes in staffing.HELPER_MODELS.
ROTATION = {
    "codex": ("gpt-6.1-sol", "gpt-6.2-astra"),
    "opencode": ("opencode-go/kimi-k3.1-pro", "opencode-go/minimax-m3.1-flash",
                 "opencode-go/deepseek-v4.1-flash"),
    "muse": ("muse-ember-1.0", "muse-wonder-full-1.0"),
    "agy": ("gemini-4-hydrogen-high", "gemini-4-argon-high"),
}
# Explorers and great-work builders may use each agent's stronger route. Codex
# stays on Sol: the Steward found Astra far too defensive for house work.
STRONG = {"codex": "gpt-6.1-sol", "opencode": "opencode-go/kimi-k3.1-pro",
          "muse": "muse-wonder-full-1.0", "agy": "gemini-4-argon-high"}
# Steward, 18 November: the scout's seat of the evening before is gone. With one resident doing nearly
# all the research its taste became the shelf's (8 of its 14 ideas were art). Research rotates across
# the kinds again, and Astra 6.2 is an ordinary Codex route so its resident works the house like
# everyone else. Explorers and great works on Codex stay on Sol (STRONG).
ROTATION_WINDOW = 24
# Steward, 18 November, night: "let's fall back to more codex with 2/3 running sol and the last one
# running Astra". The two Codex routes took turns, and Explorers and great works went to Sol on top, so
# every ordinary Codex wake went to the two or three Astra residents: one of them was woken 26 times in a
# day against 15 to 18 for each Sol resident. A route's weight is its share of its family's recent runs
# (course.route): of every three Codex runs, two are Sol and one is Astra 6.2, counting the Sol runs
# that Explorers and great works take. A route with no entry weighs 1. Since the Steward's next sentence
# ("just rotate across all the codex residents", course.TURNS) a sleeping Codex resident is chosen
# before a route, so these weights choose the route only for a newcomer.
WEIGHTS = {"gpt-6.1-sol": 2, "gpt-6.2-astra": 1}
# Steward, 19 November, midday, with Codex out of quota too: "I think we need to drop Astra as part of
# this as it's the one using a lot of tokens". Since the owner migration life.RETIRED no run starts on a
# route listed here, and a resident who lived on it returns on the route it maps to. Astra 6.2 stays in
# MODELS and ROTATION only so that the journal before the migration replays; Sol is the one ordinary
# Codex route from then on.
RETIRED = {"codex": {"gpt-6.2-astra": "gpt-6.1-sol"}}


def validate_model(kind, model):
    if kind not in MODELS or model not in MODELS[kind]:
        raise ValueError("provider/model is outside the Steward's allowance")


def command(kind: str, model: str, workspace: Path, private: Path,
            house_command: Path, *, runtime: Path | None = None, resident: str | None = None,
            web: bool = False) -> tuple[list[str], dict]:
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
        if web:
            argv.insert(1, "--search")
    elif kind == "muse":
        argv = [executable, "exec", "--provider", "meta", "--model", model,
                "--json", "--workspace", str(workspace), "--worktree", "off",
                "--trust-workspace",
                "--sandbox-network", "proxy-only", "--disable-web-tools",
                "--disable-reminders", "--no-session-log", "--prompt-file", str(private / "prompt.txt")]
        if web:
            argv.remove("--disable-web-tools")
    elif kind == "agy":
        argv = [executable, "--model", model, "--sandbox", "--mode", "auto",
                "--output-format", "stream-json", "--log-file", str(private / "agy.log"),
                "-p", (private / "prompt.txt").read_text()]
    else:
        # A shell prefix still permits redirections. Deny shell entirely and
        # expose only a private fixed tool that invokes the pinned mailbox code.
        if runtime is None or resident is None:
            raise ValueError("OpenCode requires a pinned runtime and assigned resident")
        from .opencode_auth import source_database
        from .opencode_tool import configure
        source = source_database(env)
        config = configure(private, workspace, runtime, resident, env, web=web)
        config.update(model=model, default_agent="emberhall", formatter=False, lsp=False,
                      warming=False, share="disabled", update="disable")
        config["agents"]["title"] = {"model": model}
        env["OPENCODE_CONFIG_CONTENT"] = json.dumps(config)
        env["OPENCODE_DB"] = str(private / "opencode.db")
        env["EMBERHALL_OPENCODE_SOURCE_DB"] = str(source)
        # V2 run prefers PWD over process.cwd(); the coordinator also sets cwd.
        env["PWD"] = str(workspace)
        argv = [executable, "run", "--standalone", "-m", model, "--agent", "emberhall",
                "--format", "json", "--title", "Emberhall " + private.name,
                (private / "prompt.txt").read_text()]
    return argv, env


RESET_CEILING_SECONDS = 8 * 86400


def reset_after(failure: str, now: float | None = None) -> float | None:
    """Seconds until a quota returns, when the provider's own terminal error says so.

    OpenCode Go reports ``"retryAfterMs": 535655000`` beside "resets in 6d 4h"; Antigravity says
    "Resets in 143h1m4s"; Muse names the moment, "Your usage window resets at 2026-11-23T00:00:00Z"
    (read only with its time zone); Codex gives a time on the local clock, "try again at 11:11 PM".
    Anything else, or a wait longer than eight days, is treated as not said.
    """
    found = re.search(r'retryAfterMs\\*"?\s*:\s*(\d{1,12})', failure)
    seconds = int(found.group(1)) / 1000 if found else None
    if seconds is None:
        spoken = re.search(r"resets?\s+in\s+((?:\d{1,4}\s*[dhms]\s*){1,4})", failure, re.I)
        if spoken:
            units = {"d": 86400, "h": 3600, "m": 60, "s": 1}
            seconds = sum(int(number) * units[unit.lower()]
                          for number, unit in re.findall(r"(\d{1,4})\s*([dhms])", spoken.group(1), re.I))
    if seconds is None:
        moment = re.search(r"resets?\s+at\s+(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?)(?:\.\d{1,9})?(Z|[+-]\d\d:\d\d)",
                           failure, re.I)
        if moment:
            try:
                stated = datetime.datetime.fromisoformat(
                    moment.group(1) + ("+00:00" if moment.group(2).upper() == "Z" else moment.group(2)))
                seconds = stated.timestamp() - (time.time() if now is None else now)
            except (ValueError, OverflowError):
                seconds = None
    if seconds is None:
        # Codex gives a time on this Mac's own clock and no date: "try again at 11:11 PM". It is the
        # next time the clock shows that, so always less than a day away.
        clock = re.search(r"try again at (\d{1,2}):(\d\d)\s*([AP])\.?M\b", failure, re.I)
        if clock and 1 <= int(clock.group(1)) <= 12 and int(clock.group(2)) < 60:
            current = datetime.datetime.fromtimestamp(time.time() if now is None else now)
            hour = int(clock.group(1)) % 12 + (12 if clock.group(3).upper() == "P" else 0)
            stated = current.replace(hour=hour, minute=int(clock.group(2)), second=0, microsecond=0)
            seconds = (stated - current).total_seconds()
            if seconds < -300:
                seconds += 86400    # that time has passed today: it means tomorrow
            elif seconds <= 0:
                seconds = 60.0      # named a minute that has just gone: try again shortly, not in a day
    if seconds is None or not 0 < seconds <= RESET_CEILING_SECONDS:
        return None
    return max(60.0, float(seconds))


def result(kind: str, output: str, errors: str, exit_code: int | None) -> dict:
    """Parse only native terminal usage/errors, never tool text quoting a quota.

    stderr may report startup quota errors without a terminal JSON event. Such a
    report only triggers a conservative cooldown after nonzero process exit.
    """
    usage, terminal, error_text, plain_output = {}, False, [], []
    muse_root, muse_terminals = None, 0
    muse_seen, muse_completed_usage = set(), {}
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
                # Muse can continue after a background terminal result with a
                # second root turn in this same native process. Only accept a
                # new turn after the previous root has completed exactly once.
                if (not isinstance(root, str) or not root or root in muse_seen or
                        (muse_root is not None and (not terminal or muse_terminals != 1))):
                    return {"outcome": "failed", "usage": {}}
                if muse_root is not None:
                    for key, value in usage.items():
                        muse_completed_usage[key] = muse_completed_usage.get(key, 0) + value
                muse_seen.add(root)
                muse_root = root
                muse_terminals, terminal, usage = 0, False, {}
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
    if kind == "muse":
        usage = {key: muse_completed_usage.get(key, 0) + usage.get(key, 0)
                 for key in muse_completed_usage.keys() | usage.keys()}
    credentials = bool(re.search(r'API key.{0,30}expired|invalid.api.key|authentication.failed|'
                                 r'"statusCode"\s*:\s*401|HTTP\s+401', failure, re.I))
    if credentials:
        return {"outcome": "failed", "usage": usage, "retry_after_seconds": 86400}
    quota = bool(re.search(r"quota|usage.limit|rate.limit|too many requests|\b429\b|allowance.exhaust",
                           failure, re.I))
    outcome = "quota" if quota else "success" if exit_code == 0 and terminal and not error_text else "failed"
    wait = reset_after(failure) if quota else None
    return {"outcome": outcome, "usage": usage, **({"retry_after_seconds": wait} if wait else {})}
