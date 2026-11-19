"""Compare a work-outcomes proposal with an installation receipt and committed source."""
from __future__ import annotations

import argparse
from functools import cache
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from historical_rotation import ROOT, git_bytes

sys.path.insert(0, str(ROOT))
from house.renovation import descriptor


@cache
def digest(object_id: str) -> str:
    return hashlib.sha256(git_bytes("cat-file", "blob", object_id)).hexdigest()


def modules(commit: str) -> dict[str, str]:
    result = {}
    for entry in git_bytes("ls-tree", "-rz", commit, "--", "house").split(b"\0"):
        if not entry:
            continue
        header, path = entry.decode().split("\t", 1)
        if not path.endswith(".py"):
            continue
        mode, kind, object_id = header.split()
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError(f"expected regular source at {path}")
        result[path] = digest(object_id)
    return result


def differences(left: dict, right: dict) -> list[str]:
    added_or_removed = left.keys() ^ right.keys()
    changed = {path for path in left.keys() & right.keys() if left[path] != right[path]}
    return sorted(added_or_removed | changed)


def check(page: dict, proposal: dict, revision: str) -> None:
    events = page["events"]
    if len(events) != 1 or events[0]["sequence"] != page["through"]:
        raise ValueError("supply a verified read page containing one installation")
    receipt = events[0]
    if receipt["op"] not in {"owner-migrate", "renovation-install"}:
        raise ValueError(f"event {page['through']} is not an installation")
    installed = receipt["data"]["protected_files"]
    base = receipt["data"]["source_head"]
    if not isinstance(installed, dict) or not re.fullmatch(r"[0-9a-f]{40}", base):
        raise ValueError("invalid installation source or manifest")
    mismatches = differences(modules(base), installed)
    if mismatches:
        raise ValueError("installation differs from its source at " + ", ".join(mismatches))

    declared = proposal["files"]
    pinned = modules(proposal["source_commit"])
    wrong = sorted(path for path, value in declared.items() if pinned.get(path) != value)
    if wrong:
        raise ValueError("proposal differs from its own source at " + ", ".join(wrong))
    head = git_bytes("rev-parse", "--verify", "--end-of-options", revision + "^{commit}").decode().strip()
    current = modules(head)
    target = installed | declared
    mismatches = differences(target, current)
    print(f"Installation {page['through']} at {base[:7]} | {len(installed)} modules")
    print(f"Source {head[:7]} | {len(current)} modules | {len(declared)} proposed files")
    if mismatches:
        raise ValueError("proposed installation differs from checked source at " + ", ".join(mismatches))
    changed = differences(installed, current)
    if changed:
        print(f"Proposal covers all {len(changed)} source changes.")
        for path in changed:
            print(path)
    else:
        print("The recorded installation already contains this source.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("installation", type=Path, help="one-event page from the fixed journal reader")
    parser.add_argument("proposal", type=Path, help="council renovation descriptor")
    parser.add_argument("--source", default="HEAD", help="local committed source to compare (default HEAD)")
    args = parser.parse_args()
    try:
        check(json.loads(args.installation.read_text()), descriptor(args.proposal.read_text()), args.source)
    except (KeyError, TypeError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"Cannot confirm proposal coverage: {exc}\n")


if __name__ == "__main__":
    main()
