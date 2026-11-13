"""Owner signatures cover a precise transition, never a free-standing approval."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode()


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def ballot(state: dict, proposal: str) -> bytes:
    item = state["proposals"][proposal]
    return canonical({"domain": "longhouse-rules-v1", "house": state["house_id"],
                      "base": item["base"], "proposal": proposal,
                      "replacement_sha256": digest(item["text"])})


def verify_signature(public_key: str, message: bytes, signature: str) -> None:
    if not public_key:
        raise ValueError("house is sealed: no owner key was enrolled at foundation")
    if "\n" in public_key or not public_key.startswith(("ssh-ed25519 ", "ssh-rsa ", "ecdsa-")):
        raise ValueError("invalid owner public key")
    with tempfile.TemporaryDirectory(prefix="house-signature-") as directory:
        root = Path(directory)
        (root / "allowed").write_text("owner " + public_key + "\n")
        (root / "signature").write_text(signature)
        result = subprocess.run(
            ["ssh-keygen", "-Y", "verify", "-f", str(root / "allowed"), "-I", "owner",
             "-n", "longhouse-rules-v1", "-s", str(root / "signature")],
            input=message, capture_output=True, check=False)
        if result.returncode:
            raise ValueError("owner signature rejected")
