"""Record actual daughter CLI calls; run from the source checkout."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SESSION = json.loads((HERE / "session.json").read_text())


def run(argv, expected=0, timeout=20):
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(argv, cwd=SESSION["source"], capture_output=True,
                            text=True, timeout=timeout)
    record = {"argv": argv, "cwd": SESSION["source"], "started": started,
              "returncode": result.returncode, "stdout": result.stdout,
              "stderr": result.stderr}
    with (HERE / "transcript.jsonl").open("a") as stream:
        stream.write(json.dumps(record) + "\n")
    if result.returncode != expected:
        raise RuntimeError(record)
    return result.stdout


def house(*args):
    return run([sys.executable, "-m", "house", "--repo", SESSION["repo"], *args])


if __name__ == "__main__":
    print(house(*sys.argv[1:]))
