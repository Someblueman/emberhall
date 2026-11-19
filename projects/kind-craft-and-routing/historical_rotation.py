"""Reproduce the fixed November 19 comparison with its original picker and analysis source."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
FIRST, FIT, LAST = 19760, 20201, 20559
INSTALL = 19936
PICKER = "7c978daf87e9f1d50eec011ee4e87ec72bf81915"
ANALYZERS = {
    "craft_outcomes": ("227eb56dc110f63963ef9ab2977bfab1566cc0ef",
                       "abcc3fd9a77ff760223cdd4e98f6db67398ebaa90cdfd88834fbae891fb788a4"),
    "craft_replay": ("7cf832d4cf5b016c4e546b31813e008e0dac2115",
                     "ca477d60b8be0ce6e6d71f023853ad9a7a8fb0fdfd7a89d8b9fdec1a8329d428"),
}
# The eleven entries in the frozen status snapshot. Expiry times come from the events.
COOLDOWNS = (1093, 12215, 12438, 15645, 18562, 18602, 19721, 19743, 19761, 20178, 20201)


def journal(*args):
    result = subprocess.run([str(ROOT / ".house-client"), *args], cwd=ROOT, text=True,
                            capture_output=True, check=False)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "fixed journal channel failed")
    return json.loads(result.stdout)


def collect(resident):
    status = journal("status")
    events = []
    cursor = FIRST - 1
    while cursor < LAST:
        page = journal("read", "--as", resident, "--after", str(cursor),
                       "--limit", str(min(200, LAST - cursor)))
        if not cursor < page["through"] <= LAST:
            raise ValueError(f"journal did not advance from {cursor}")
        events.extend(page["events"])
        cursor = page["through"]
    cooldowns = []
    for seq in COOLDOWNS:
        if FIRST <= seq <= LAST:
            cooldowns.append(events[seq - FIRST])
        else:
            page = journal("read", "--as", resident, "--after", str(seq - 1), "--limit", "1")
            if len(page["events"]) != 1 or page["through"] != seq:
                raise ValueError(f"missing cooldown observation {seq}")
            cooldowns.append(page["events"][0])
    return {"status": status, "events": events, "cooldowns": cooldowns}


def frozen_budgets(events):
    if [e["sequence"] for e in events] != list(COOLDOWNS):
        raise ValueError("cooldown observations differ from the frozen snapshot")
    budgets, models = {}, {}
    for e in events:
        data = e["data"]
        if e["op"] != "life" or e["actor"] != "watch-keeper" or data.get("kind") != "budget":
            raise ValueError(f"expected a controller cooldown at {e['sequence']}")
        target = models.setdefault(data["agent"], {}) if "model" in data else budgets
        name = data.get("model", data["agent"])
        if name in target:
            raise ValueError(f"duplicate frozen cooldown for {name}")
        target[name] = {"sequence": e["sequence"], "until": data["until"]}
    return {"budgets": budgets, "model_budgets": models}


def git_bytes(*args):
    return subprocess.check_output(["git", "--no-replace-objects", "-C", str(ROOT), *args])


def reproduce(inputs, directory):
    events = inputs["events"]
    if [e["sequence"] for e in events] != list(range(FIRST, LAST + 1)):
        raise ValueError(f"expected every journal event from {FIRST} through {LAST} exactly once")
    install = events[INSTALL - FIRST]
    if install["op"] != "owner-migrate" or install["data"]["source_head"] != PICKER:
        raise ValueError(f"historical source does not match installation {INSTALL}")
    manifest = install["data"]["protected_files"]
    package = directory / "house"
    package.mkdir()
    with zipfile.ZipFile(io.BytesIO(git_bytes("archive", "--format=zip", PICKER, "house"))) as archive:
        names = {n for n in archive.namelist() if re.fullmatch(r"house/[a-zA-Z0-9_]+\.py", n)}
        if names != set(manifest):
            raise ValueError(f"archived module set differs from installation {INSTALL}")
        for name in names:
            body = archive.read(name)
            if hashlib.sha256(body).hexdigest() != manifest[name]:
                raise ValueError(f"historical module differs from installation: {name}")
            (directory / name).write_bytes(body)
    for name, (commit, digest) in ANALYZERS.items():
        body = git_bytes("show", f"{commit}:house/{name}.py")
        if hashlib.sha256(body).hexdigest() != digest:
            raise ValueError(f"historical analyzer mismatch: {name}")
        (package / (name + ".py")).write_bytes(body)

    # The CLI starts a fresh interpreter without any house module loaded. Only these
    # Git objects supply code. Exported journal pages and status supply data.
    sys.path.insert(0, str(directory))
    from house.craft_outcomes import measure
    from house.craft_replay import replay
    fit = measure([events[:FIT - FIRST + 1]])
    report = replay(inputs["status"], frozen_budgets(inputs["cooldowns"]), fit, [events])
    if any(d["baseline"] != d["actual"] or d["reason"] == "baseline mismatch" for d in report["decisions"]):
        raise ValueError("historical picker and an observed assignment disagree")
    history = measure([events])
    attempts = {(a["task"], events[a["claim"] - FIRST]["data"]["expect"]): a for a in history["attempts"]}
    # Keep these later outcomes outside the frozen score and the original decisions.
    report["observed_claims"] = []
    for decision in report["decisions"]:
        start = events[decision["start"] - FIRST]["data"]
        attempt = attempts.get((start["task"], start["task_generation"]))
        row = {"offer": decision["start"], "receiver_exit": history["runs"][start["run"]]["exit"],
               "claim": None, "finish": None, "same_run": None}
        if attempt:
            row.update(claim=attempt["claim"], finish=attempt["finish"])
            if attempt["run"] is not None:
                row["same_run"] = attempt["run"] == start["run"]
        report["observed_claims"].append(row)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--as", dest="resident", help="collect fresh observations from your assigned fixed channel")
    source.add_argument("--inputs", type=Path, help="replay the previously saved private inputs")
    parser.add_argument("--save-inputs", type=Path, help="keep new private inputs in a new file for offline reruns")
    args = parser.parse_args()
    if args.inputs and args.save_inputs:
        parser.error("--save-inputs is for a new fixed-channel read")
    if args.save_inputs and args.save_inputs.exists():
        parser.error("the input export already exists; use --inputs to replay it")
    try:
        inputs = collect(args.resident) if args.resident else json.loads(args.inputs.read_text())
        if args.save_inputs:
            with tempfile.NamedTemporaryFile(mode="w", dir=args.save_inputs.parent) as stream:
                json.dump(inputs, stream)
                stream.flush()
                os.link(stream.name, args.save_inputs)
        with tempfile.TemporaryDirectory(prefix="emberhall-historical-rotation-") as tmp:
            report = reproduce(inputs, Path(tmp))
    except (KeyError, ValueError, OSError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"Cannot reproduce historical rotation: {exc}\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
