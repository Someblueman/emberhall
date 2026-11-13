"""Copy-only recovery drill. Usage: python3 drill.py SOURCE NEW_OUTPUT_DIRECTORY."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

source = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=False)
records = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, expected=0, timeout=30):
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(args, cwd=source, capture_output=True, text=True,
                            timeout=timeout)
    records.append({"argv": args, "cwd": str(source), "started": started,
                    "returncode": result.returncode, "stdout": result.stdout,
                    "stderr": result.stderr})
    (out / "commands.json").write_text(json.dumps(records, indent=2) + "\n")
    if result.returncode != expected:
        raise RuntimeError(records[-1])
    return result.stdout


paths = ["evidence/house-custodian.bundle", "evidence/custodian/SUMMARY.md",
         "evidence/custodian/recovery.json", "evidence/seed-trial/daughter.bundle",
         "evidence/seed-trial/provenance.json"]
publication = json.loads((source / "evidence/custodian/publication.json").read_text())
published_commit = publication["source_commit"]
before = {path: digest(source / path) for path in paths}
for path in paths:
    # Git blob identities establish these are the bytes in the recorded publication.
    published_blob = run(["git", "rev-parse", published_commit + ":" + path]).strip()
    working_blob = run(["git", "hash-object", str(source / path)]).strip()
    assert published_blob == working_blob, path
    destination = out / "reference" / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / path, destination)
shutil.copytree(out / "reference", out / "backup")
cli = [sys.executable, str(source / "projects/blackout/blackout.py")]
manifest = str(out / "inventory.json")
run([*cli, "create", str(out / "reference"), manifest])
initial = json.loads(run([*cli, "verify", str(out / "backup"), manifest]))
assert initial == {"ok": True, "missing": [], "changed": [], "extra": [], "matched": 5}
target = "evidence/house-custodian.bundle"
damaged = out / "backup" / target
data = bytearray(damaged.read_bytes())
offset = len(data) // 2
original_byte = data[offset]
data[offset] ^= 1
damaged.write_bytes(data)
corrupt_hash = digest(damaged)
detected = json.loads(run([*cli, "verify", str(out / "backup"), manifest], expected=1))
assert detected == {"ok": False, "missing": [], "changed": [target], "extra": [], "matched": 4}
assert digest(damaged) == corrupt_hash  # Verification did not repair the fault.
shutil.copyfile(out / "reference" / target, damaged)
recovered = json.loads(run([*cli, "verify", str(out / "backup"), manifest]))
assert recovered == initial
after = {path: digest(source / path) for path in paths}
assert before == after
assert {path: digest(out / "backup" / path) for path in paths} == before
restored = out / "restored-house"
run(["git", "init", str(restored)])
house = [sys.executable, "-m", "house", "--repo", str(restored)]
anchor = "74339de5dda84c799fe43650ba273a84de31ba8a"
run([*house, "restore", str(damaged), "--expect-anchor", anchor])
verification = json.loads(run([*house, "verify"]))
published_recovery = json.loads((source / "evidence/custodian/recovery.json").read_text())
assert before[target] == published_recovery["bundle_sha256"]
assert verification["head"] == published_recovery["restored"]["head"]
assert verification["events"] == published_recovery["restored"]["events"]
assert anchor == published_recovery["restored"]["anchor"]
(out / "published-recovery.json").write_text(json.dumps(published_recovery, indent=2) + "\n")
review = (source / "docs/BLACKOUT_REVIEW.md").read_text()
probe = review.split("python3 - <<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
(out / "inherited-probe.py").write_text(probe + "\n")
probe_output = run([sys.executable, str(out / "inherited-probe.py")])
assert "TIMEOUT" not in probe_output
assert "FIFO manifest: 2" in probe_output
assert "symlink-component 2" in probe_output
assert "missing-component 2" in probe_output
run([sys.executable, "-m", "unittest", "discover", "-s", "projects/blackout", "-p", "test_*.py", "-v"])
summary = {"published_source_commit": published_commit, "source_hashes_before": before,
           "source_hashes_after": after, "source_unchanged": before == after,
           "inventory_sha256": digest(out / "inventory.json"),
           "blackout_sha256": digest(source / "projects/blackout/blackout.py"),
           "tests_sha256": digest(source / "projects/blackout/test_blackout.py"),
           "initial": initial, "corrupted": detected, "recovered": recovered,
           "corruption": {"path": target, "offset": offset, "xor": 1,
                          "original_byte": original_byte, "corrupt_sha256": corrupt_hash,
                          "original_and_recovered_sha256": before[target]},
           "restored_verification": verification,
           "inherited_probe_output": probe_output,
           "limits": "Same-day quiescent copies; intentional one-byte fault. Byte checks do not authenticate manifests, preserve metadata, prove live-writer isolation, or restore automatically. Published checkpoint is not the latest live journal."}
(out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
