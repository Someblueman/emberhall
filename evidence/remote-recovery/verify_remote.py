"""Reproduce a real HTTPS checkpoint recovery; writes one public JSON receipt."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from house.governance import canonical
from house.model import apply_event
from house.record import ANCHOR, Record

REMOTE = "https://github.com/Someblueman/longhouse.git"
PINNED = ROOT / ".git/house-watch/runtime-350c76cec338620c85de930ad8c7fdca9bbaaf29.pyz"
PYTHON = "/Users/sws/.local/share/mise/installs/python/3.13.2/bin/python3"
RECEIPT = Path(__file__).with_name("receipt.json")


def sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def main() -> None:
    if RECEIPT.exists():
        raise SystemExit("Preserve the existing receipt; run a copied script for a new observation.")
    transcript = []

    def run(argv: list[str], expected: int = 0) -> str:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=120)
        transcript.append({"argv": argv, "exit_code": result.returncode,
                           "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode != expected:
            raise RuntimeError(f"Unexpected exit {result.returncode}: {argv}")
        return result.stdout

    receipt = {"observed_at": datetime.now(timezone.utc).isoformat(),
               "remote": REMOTE, "commands": transcript, "passed": False}
    try:
        local = Record(ROOT)
        _, live_events, live_head = local.read()
        anchor = local.ref(ANCHOR)
        with tempfile.TemporaryDirectory(prefix="emberhall-remote-", dir="/private/tmp") as tmp:
            work = Path(tmp)
            clone = work / "source"
            run(["git", "clone", "--single-branch", "--branch", "main", "--depth", "1",
                 REMOTE, str(clone)])
            source_head = run(["git", "-C", str(clone), "rev-parse", "HEAD"]).strip()
            checkpoint = json.loads((clone / "evidence/checkpoint.json").read_text())
            bundle = clone / checkpoint["bundle"]
            assert bundle.resolve().is_relative_to(clone.resolve())
            original = bundle.read_bytes()
            assert sha(original) == checkpoint["bundle_sha256"]
            assert checkpoint["anchor"] == anchor
            assert (clone / "projects/blackout/blackout.py").read_bytes() == (
                ROOT / "projects/blackout/blackout.py").read_bytes()

            # Byte verification is separate from journal recovery; corrupt only a disposable copy.
            backup = work / "backup"
            backup.mkdir()
            copied = backup / "checkpoint.bundle"
            shutil.copyfile(bundle, copied)
            manifest = work / "manifest.json"
            blackout = [PYTHON, str(ROOT / "projects/blackout/blackout.py")]
            run([*blackout, "create", str(backup), str(manifest)])
            clean = json.loads(run([*blackout, "verify", str(backup), str(manifest)]))
            offset = len(original) // 2
            damaged = bytearray(original)
            damaged[offset] ^= 1
            copied.write_bytes(damaged)
            mismatch = json.loads(run([*blackout, "verify", str(backup), str(manifest)], 1))
            assert mismatch == {"ok": False, "changed": ["checkpoint.bundle"],
                                "extra": [], "missing": [], "matched": 0}
            assert copied.read_bytes() == damaged  # Checking never repairs the bytes.
            shutil.copyfile(bundle, copied)
            repaired = json.loads(run([*blackout, "verify", str(backup), str(manifest)]))
            assert clean == repaired == {"ok": True, "changed": [], "extra": [],
                                        "missing": [], "matched": 1}

            restored = work / "restored"
            run(["git", "init", "-q", str(restored)])
            cli = [PYTHON, str(PINNED), "house", "--repo", str(restored)]
            restoration = json.loads(run([*cli, "restore", str(copied), "--expect-anchor", anchor]))
            verification = json.loads(run([*cli, "verify"]))
            state, events, head = Record(restored).read()
            assert head == checkpoint["head"] == restoration["head"] == verification["head"]
            assert len(events) == checkpoint["events"] == verification["events"]
            assert state["house_id"] == checkpoint["house_id"]
            assert sha(canonical(state)) == checkpoint["state_sha256"]
            assert events == live_events[:len(events)]
            prefix_state = None
            for event in live_events[:len(events)]:
                prefix_state = apply_event(prefix_state, event)
            assert state == prefix_state
            assert bundle.read_bytes() == original
            receipt.update({"passed": True, "remote_source_head": source_head,
                            "checkpoint": checkpoint, "restoration": restoration,
                            "verification": verification, "local_observed_head": live_head,
                            "local_observed_events": len(live_events),
                            "unbacked_local_tail_events": len(live_events) - len(events),
                            "restored_exact_local_prefix_events_and_state": True,
                            "events_sha256": sha(canonical(events)),
                            "corruption": {"offset": offset, "xor": 1,
                                           "damaged_sha256": sha(damaged), "detected": mismatch},
                            "blackout_sha256": sha((ROOT / "projects/blackout/blackout.py").read_bytes()),
                            "pinned_runtime_sha256": sha(PINNED.read_bytes()),
                            "script_sha256": sha(Path(__file__).read_bytes()),
                            "limits": "HTTPS retrieval and exact point-in-time restore, not an independent archive service, future availability, metadata backup, or continuous multi-day life. Manifest generated locally from fetched bytes; authenticity relies on the local trusted anchor and prefix comparison."})
    except BaseException as exc:
        receipt["failure"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k not in ("commands", "checkpoint")}, indent=2))


if __name__ == "__main__":
    main()
