"""Run the Door's publication-clock trial on a preserved Emberhall archive."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

from house import body
from house.public_history import Encoder

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "evidence/house-checkpoint-3972-4bdfe7b29470eae71633221367a73b55bb9608ffe6e94acf38a6f450cf6ab621.json"
PARLOR_OPEN = 2180
SALVAGE_PLAN = 550
RECORDED_CHANGES = [2180, 2024, 1946, 1928, 1614, 1474, 1247, 1244, 563, 550]


def historical_prefix():
    manifest = json.loads(CHECKPOINT.read_bytes())
    bundle = ROOT / manifest["bundle"]
    if hashlib.sha256(bundle.read_bytes()).hexdigest() != manifest["bundle_sha256"]:
        raise ValueError("Historical checkpoint differs from its recorded digest")
    with tempfile.TemporaryDirectory() as folder:
        git = ["git", "-C", folder]
        subprocess.run([*git, "init", "-q", "--bare"], check=True)
        # Unpack objects for inspection. No Emberhall refs are created here.
        subprocess.check_output([*git, "bundle", "unbundle", str(bundle)])
        commits = subprocess.check_output(
            [*git, "rev-list", "--first-parent", "--reverse", manifest["head"]], text=True
        ).splitlines()[:PARLOR_OPEN]
        queries = "".join(f"{commit}:event.json\n" for commit in commits)
        # Canonical event blobs are single-line JSON. Git emits a header before each blob.
        rows = subprocess.check_output([*git, "cat-file", "--batch"], input=queries, text=True).splitlines()
    return commits[-1], [json.loads(row) for row in rows[1::2]]


ARCHIVE_READER = r"""
const fs = require('node:fs'), vm = require('node:vm');
const source = fs.readFileSync(process.argv[1], 'utf8');
const startup = 'refresh();\nsetInterval(watch,10000);\n';
if (!source.endsWith(startup)) throw Error('Check how the archive reader starts');
const context = vm.createContext({document: {}, ...JSON.parse(fs.readFileSync(0, 'utf8'))});
vm.runInContext(source.slice(0, -startup.length), context);
const rows = vm.runInContext(`
  const frames = decodePublicHistory(wire).frames;
  clocks.map(at => recentGrowth(frames, frames.length - 1, at));
`, context);
process.stdout.write(JSON.stringify(rows));
"""


def run_trial(source):
    spec = importlib.util.spec_from_file_location("house.door_summary", source / "house/door_summary.py")
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    head, events = historical_prefix()
    encoder = Encoder(chunked=True)
    context, references = body.replay_context(), []
    for start in range(0, len(events), 100):
        batch = body.replay(events[:start + 100], context)
        references.extend(encoder.value(frame) for frame in batch)
    root = encoder.intern({"version": 1, "frames": encoder.sequence(references)})
    wire = {"version": 4, "nodes": encoder.nodes, "root": root}

    opening = events[-1]["at"]
    salvage_expires = events[SALVAGE_PLAN - 1]["at"] + 43200
    clocks = [opening, salvage_expires, salvage_expires + 1,
              opening + 43200, opening + 43201]
    expected = [RECORDED_CHANGES, RECORDED_CHANGES, RECORDED_CHANGES[:-1], [PARLOR_OPEN], []]
    archive = json.loads(subprocess.check_output(
        ["node", "-e", ARCHIVE_READER, str(source / "site/house.js")],
        input=json.dumps({"wire": wire, "clocks": clocks}), text=True,
    ))
    for at, sequences, rows in zip(clocks, expected, archive, strict=True):
        changes = json.loads(producer.now_bytes(
            final=context["state"], head=head, source_head=None, observed_at=at,
            commits=[], frames=references, nodes=encoder.nodes,
        ))["changes"]
        if [row["seq"] for row in rows] != sequences:
            raise AssertionError(f"Archive at {at} disagrees with the recorded transitions: {rows}")
        if (changes["since"], changes["until"], changes["count"], changes["items"]) != (
            at - 43200, at, len(rows), rows
        ):
            raise AssertionError(f"Door differs from archive at {at}\nDoor: {changes}\nArchive: {rows}")
        print(f"{at:.6f}  {len(rows):2} changes  {sequences}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT,
                        help="local reviewed source containing the Door publisher and page reader")
    source = parser.parse_args().source
    if not (source / "house/door_summary.py").is_file():
        parser.error("Supply --source with a reviewed checkout containing house/door_summary.py")
    run_trial(source)
