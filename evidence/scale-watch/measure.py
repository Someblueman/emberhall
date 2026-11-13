"""Bounded synthetic-history probe; not evidence of elapsed days or live residency."""
from __future__ import annotations

import argparse
import base64
import cProfile
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import pstats
import subprocess
import sys
import tempfile
import time

SOURCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SOURCE))
from house.governance import canonical
from house.record import ANCHOR, REF, Record


def fixture(repo: Path, count: int) -> dict:
    """Fast-import valid event commits; every measured operation validates full replay."""
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    chunks = []
    event_hash = hashlib.sha256()
    artifact = b"An independently checkable test contribution.\n" * 12
    payload = {"sha256": hashlib.sha256(artifact).hexdigest(),
               "base64": base64.b64encode(artifact).decode()}
    for seq in range(1, count + 1):
        actor = f"resident-{seq % 20}"
        if seq == 1:
            op, actor = "found", "founder"
            data = {"house_id": "scale-probe-v1", "name": "Disposable scale probe",
                    "rules": "Synthetic fixture; no authority or real residents.", "owner_key": ""}
        elif seq <= 21:
            op, actor = "arrive", f"resident-{seq - 2}"
            data = {"name": actor}
        else:
            block, position = divmod(seq, 100)
            task, lesson = f"task-{block}", f"lesson-{block}"
            if position == 0:
                op, actor = "task", "resident-0"
                data = {"task": task, "title": "Bounded synthetic work",
                        "description": "Publish a small artifact, then review the lesson."}
            elif position == 1 and block:
                op, actor = "claim", "resident-0"
                data = {"task": task, "expect": 0, "token": f"token-{block}", "seconds": 300}
            elif position == 2 and block:
                op, actor = "finish", "resident-0"
                data = {"task": task, "token": f"token-{block}", "result": "Fixture work",
                        "artifacts": {"result.txt": payload}}
            elif position == 3 and block:
                op, actor = "learn", "resident-0"
                data = {"lesson": lesson, "key": lesson, "claim": "A scoped fixture lesson",
                        "evidence": f"Synthetic task {task}; not a real observation."}
            elif position == 4 and block:
                op, actor = "review", "resident-1"
                data = {"lesson": lesson, "evidence": "Synthetic fixture review"}
            elif position == 5 and block:
                op, actor = "sleep", "resident-1"
                data = {"through": seq - 1, "note": "A synthetic sleep, not elapsed days."}
            elif position == 6 and block:
                op, actor = "wake", "resident-1"
                data = {}
            else:
                op, data = "say", {"text": f"Observation {seq}: bounded work and a durable receipt."}
        event = {"id": f"scale-{seq}", "op": op, "actor": actor,
                 "at": 1700000000 + seq, "data": data}
        raw = canonical(event)
        event_hash.update(raw + b"\n")
        message = f"scale fixture event {seq}\n".encode()
        chunks.append(f"commit {REF}\nmark :{seq}\n"
                      f"committer Scale probe <probe@local> {1700000000 + seq} +0000\n"
                      f"data {len(message)}\n".encode() + message +
                      f"M 100644 inline event.json\ndata {len(raw)}\n".encode() + raw + b"\n\n")
    marks = repo / "marks"
    subprocess.run(["git", "-C", str(repo), "-c", "gc.auto=0", "fast-import", "--quiet",
                    f"--export-marks={marks}", "--done"],
                   input=b"".join(chunks) + b"done\n", check=True, capture_output=True)
    anchor = marks.read_text().splitlines()[0].split()[1]
    subprocess.run(["git", "-C", str(repo), "update-ref", ANCHOR, anchor], check=True)
    return {"events": count, "events_sha256": event_hash.hexdigest(), "anchor": anchor}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sizes", type=int, nargs="+", default=[1000, 10000])
    parser.add_argument("--samples", type=int, default=3)
    args = parser.parse_args()
    if any(n < 100 or n > 10000 for n in args.sizes) or not 1 <= args.samples <= 5:
        parser.error("sizes must be 100..10000; samples must be 1..5")
    result = {"format": "house-scale-probe-v1", "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "python": platform.python_version(), "os": platform.system(), "machine": platform.machine(),
              "cpu_count": os.cpu_count(), "git": subprocess.check_output(["git", "--version"], text=True).strip(),
              "load_average_start": os.getloadavg(),
              "source_sha256": {str(p.relative_to(SOURCE)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted((SOURCE / "house").glob("*.py"))},
              "fixture": "20 residents; per 100 events one task/claim/finish/lesson/review/sleep/wake; otherwise messages",
              "boundary": "Record.read full validation; CLI last-page read including startup; append including full validation/lock/Git commit",
              "limits": "Synthetic packed Git history; warm OS caches; small artifacts; no live SSH ratifications; no elapsed-day or tail-latency claim",
              "target": "At 10000 events, median full read and append each <= 2 seconds on this host",
              "runs": []}
    def save():
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    save()
    for count in args.sizes:
        with tempfile.TemporaryDirectory(prefix="emberhall-scale-") as directory:
            repo = Path(directory)
            run = {"fixture": fixture(repo, count), "samples": []}
            result["runs"].append(run)
            record = Record(repo)
            for sample in range(args.samples):
                row = {"starting_events": count + sample}
                start = time.perf_counter()
                state, events, head = record.read()
                row["read_seconds"] = time.perf_counter() - start
                assert state["sequence"] == count + sample and len(events) == count + sample
                row["state_sha256"] = hashlib.sha256(canonical(state)).hexdigest()
                row["head"] = head
                start = time.perf_counter()
                cli = subprocess.run([sys.executable, "-m", "house", "--repo", str(repo), "read",
                                      "--as", "resident-0", "--after", str(count + sample - 10),
                                      "--limit", "10"], cwd=SOURCE, capture_output=True, check=True)
                row["cli_page_seconds"] = time.perf_counter() - start
                page = json.loads(cli.stdout)
                assert page["through"] == count + sample and len(page["events"]) == 10
                start = time.perf_counter()
                receipt = record.append("say", "resident-0", {"text": "Measured append"}, f"probe-{sample}")
                row["append_seconds"] = time.perf_counter() - start
                assert receipt["sequence"] == count + sample + 1
                run["samples"].append(row)
                save()
                print(json.dumps({"events": count, "sample": sample, **row}), flush=True)
            if count == min(args.sizes):
                profile = cProfile.Profile()
                profile.runcall(record.read)
                output = io.StringIO()
                pstats.Stats(profile, stream=output).sort_stats("cumulative").print_stats(18)
                run["profile"] = output.getvalue()
                save()
    result["load_average_end"] = os.getloadavg()
    result["complete"] = True
    save()


if __name__ == "__main__":
    main()
