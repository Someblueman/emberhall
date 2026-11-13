"""Bounded JSON client for an operator-configured SSH forced-command custodian."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import sys
import time
from typing import TextIO
import uuid

MAX_REQUEST = 8_000_000
MAX_RESPONSE = 16_000_000
MAX_DIAGNOSTICS = 65_536
ACTIONS = ("verify", "status", "rules", "read", "receipt", "ballot", "append")


def strict_json(raw: bytes) -> object:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("JSON contains duplicate object keys")
            result[key] = value
        return result

    def finite(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("JSON contains a nonfinite number")
        return number

    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_float=finite, parse_constant=finite)


def read_data(path: Path | None, text: str | None) -> dict:
    if path is None:
        raw = (text if text is not None else "{}").encode("utf-8")
    else:
        # Do not let a FIFO or a raced symlink block a local request before its deadline.
        descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError("data file must be a regular file")
            raw = stream.read(MAX_REQUEST + 1)
    if len(raw) > MAX_REQUEST:
        raise ValueError("request data exceeds 8,000,000 bytes")
    data = strict_json(raw)
    if not isinstance(data, dict):
        raise ValueError("request data must be a JSON object")
    return data


def request_bytes(house: str, resident: str, request: str, action: str, data: dict) -> bytes:
    for value in (house, resident, request):
        if not isinstance(value, str) or not 1 <= len(value) <= 200:
            raise ValueError("house, resident and request IDs must have 1..200 characters")
    if action not in ACTIONS or not isinstance(data, dict):
        raise ValueError("unsupported action or invalid data")
    raw = json.dumps({"version": 1, "house": house, "resident": resident,
                      "request": request, "action": action, "data": data},
                     ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_REQUEST:
        raise ValueError("complete request exceeds 8,000,000 bytes")
    return raw


def ssh_arguments(host: str, config: Path | None = None) -> list[str]:
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,252}", host) is None:
        raise ValueError("host must be an SSH alias using letters, digits, dot, underscore or dash")
    command = ["ssh"] if config is None else ["ssh", "-F", str(config)]
    return [*command, "-T", "-a", "-x", "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=yes", "-o", "ClearAllForwardings=yes",
            "-o", "RemoteCommand=none", "-o", "PermitLocalCommand=no",
            "-o", "ControlMaster=no", "-o", "ControlPath=none", "--", host]


def exchange(host: str, payload: bytes, timeout: float,
             config: Path | None = None) -> tuple[int, bytes]:
    """Run SSH once, bounding pipe memory and elapsed time even for a broken peer."""
    if not math.isfinite(timeout) or not 0 < timeout <= 300:
        raise ValueError("timeout must be greater than zero and at most 300 seconds")
    if len(payload) > MAX_REQUEST:
        raise ValueError("complete request exceeds 8,000,000 bytes")
    deadline = time.monotonic() + timeout
    output = bytearray()
    diagnostics = 0
    position = 0
    process = subprocess.Popen(ssh_arguments(host, config), stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True)
    try:
        with selectors.DefaultSelector() as selector:
            for stream, event in ((process.stdin, selectors.EVENT_WRITE),
                                  (process.stdout, selectors.EVENT_READ),
                                  (process.stderr, selectors.EVENT_READ)):
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, event)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ValueError("SSH request timed out")
                for key, _ in selector.select(min(remaining, 0.2)):
                    stream = key.fileobj
                    if stream is process.stdin:
                        try:
                            position += os.write(stream.fileno(), payload[position:position + 65536])
                        except BrokenPipeError:
                            position = len(payload)
                        if position == len(payload):
                            selector.unregister(stream)
                            stream.close()
                        continue
                    chunk = os.read(stream.fileno(), 65536)
                    if not chunk:
                        selector.unregister(stream)
                        stream.close()
                    elif stream is process.stdout:
                        if len(output) + len(chunk) > MAX_RESPONSE:
                            raise ValueError("SSH response exceeds 16,000,000 bytes")
                        output.extend(chunk)
                    else:
                        diagnostics += len(chunk)
                        if diagnostics > MAX_DIAGNOSTICS:
                            raise ValueError("SSH diagnostics exceed 65,536 bytes")
            try:
                code = process.wait(timeout=max(0, deadline - time.monotonic()))
            except subprocess.TimeoutExpired as exc:
                raise ValueError("SSH request timed out") from exc
        return code, bytes(output)
    finally:
        # Also stop children holding pipes if the leader exited during an error.
        if process.poll() is None or sys.exc_info()[0] is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.wait()
        for stream in (process.stdin, process.stdout, process.stderr):
            stream.close()


def response(raw: bytes, code: int, house: str, resident: str, request: str) -> dict:
    if code not in (0, 2):
        raise ValueError(f"SSH transport exited with status {code}; diagnostics withheld")
    if len(raw) > MAX_RESPONSE:
        raise ValueError("SSH response exceeds 16,000,000 bytes")
    value = strict_json(raw)
    if not isinstance(value, dict) or type(value.get("version")) is not int or value["version"] != 1:
        raise ValueError("invalid custodian response version or envelope")
    if (code == 2 and set(value) == {"version", "ok", "error"}
            and value["ok"] is False and isinstance(value["error"], str)):
        raise ValueError("custodian rejected request: " + value["error"])
    if (code != 0 or set(value) != {"version", "ok", "house", "resident", "request", "result"}
            or value["ok"] is not True or value["house"] != house
            or value["resident"] != resident or value["request"] != request):
        raise ValueError("custodian response does not match the request envelope")
    return value


def emit(value: dict, stream: TextIO) -> bool:
    try:
        stream.write(json.dumps(value, ensure_ascii=True, allow_nan=False) + "\n")
        stream.flush()
    except OSError:
        # Prevent CPython's final flush from turning a handled closed pipe into exit 120.
        sink = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(sink, stream.fileno())
        finally:
            os.close(sink)
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, help="trusted, preconfigured SSH host alias")
    parser.add_argument("--ssh-config", type=Path, help="operator-owned SSH config file (-F)")
    parser.add_argument("--house", required=True)
    parser.add_argument("--resident", required=True)
    parser.add_argument("--request", help="stable receipt ID; mandatory for append")
    parser.add_argument("--timeout", type=float, default=30, help="whole SSH exchange seconds (max 300)")
    parser.add_argument("action", choices=ACTIONS)
    data = parser.add_mutually_exclusive_group()
    data.add_argument("--data", help="JSON object (prefer --data-file for private or large content)")
    data.add_argument("--data-file", type=Path)
    args = parser.parse_args(argv)
    request = args.request if args.request is not None else str(uuid.uuid4())
    try:
        if args.action == "append" and args.request is None:
            raise ValueError("append requires an explicit stable --request ID")
        payload = request_bytes(args.house, args.resident, request, args.action,
                                read_data(args.data_file, args.data))
        code, raw = exchange(args.host, payload, args.timeout, args.ssh_config)
        result = response(raw, code, args.house, args.resident, request)
        return 0 if emit(result, sys.stdout) else 2
    except (ValueError, OSError, UnicodeError, RecursionError) as exc:
        error = {"error": str(exc), "request": request}
        if args.action == "append":
            error["recovery"] = ("No automatic retry. An append may already be accepted. Inspect its "
                                 "receipt; retry only the same ID with exactly the same content.")
        emit(error, sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
