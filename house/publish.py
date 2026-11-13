"""Publish only the record-generated public house to its dedicated Pages branch."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import tempfile

from .body import export
from .record import Record

BRANCH = "codex/house-pages"


def publish(record: Record, *, push=False) -> dict:
    private = record.common / "house-home"
    private.mkdir(mode=0o700, exist_ok=True)
    with (private / "publisher.lock").open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        projection = export(record)
        contents = {name: record.git("show", "HEAD:site/" + name)
                    for name in ("index.html", "house.css", "house.js")}
        contents["history.json"] = json.dumps(projection, separators=(",", ":")).encode()
        contents[".nojekyll"] = b""
        ref = "refs/heads/" + BRANCH
        previous = record.ref(ref)
        if push:
            remote = record.git("ls-remote", "origin", ref).decode().split()
            if remote and (not previous or remote[0] != previous):
                if not previous or record.git("merge-base", previous, remote[0]).decode().strip() != remote[0]:
                    raise ValueError("Pages branch diverged remotely; reconcile before publication")
        if previous:
            old = json.loads(record.git("show", previous + ":history.json"))
            if (old["journal_head"], old["source_head"]) == (projection["journal_head"], projection["source_head"]):
                if push:
                    record.git("push", "origin", ref + ":" + ref)
                    if record.git("ls-remote", "origin", ref).decode().split()[0] != previous:
                        raise ValueError("remote Pages commit not verified")
                return {"changed": False, "commit": previous, "pushed": push}
        with tempfile.TemporaryDirectory(prefix="house-public-index-") as temp:
            env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / "index"),
                       GIT_AUTHOR_NAME="Emberhall", GIT_AUTHOR_EMAIL="house@local",
                       GIT_COMMITTER_NAME="Emberhall", GIT_COMMITTER_EMAIL="house@local")
            def git(*args, data=None):
                return subprocess.run(["git", "-C", str(record.root), *args], env=env,
                                      input=data, capture_output=True, check=True).stdout.decode().strip()
            git("read-tree", "--empty")
            for name, body in contents.items():
                blob = git("hash-object", "-w", "--stdin", data=body)
                git("update-index", "--add", "--cacheinfo", "100644", blob, name)
            tree = git("write-tree")
            if previous and git("rev-parse", previous + "^{tree}") == tree:
                return {"changed": False, "commit": previous}
            args = ["commit-tree", tree]
            if previous:
                args.extend(["-p", previous])
            commit = git(*args, data=f"Emberhall journal view through {projection['frames'][-1]['seq']}\n".encode())
            git("update-ref", ref, commit, previous or "0" * 40)
            if push:
                git("push", "origin", ref + ":" + ref)
                remote = git("ls-remote", "origin", ref).split()
                if not remote or remote[0] != commit:
                    raise ValueError("remote Pages commit not verified")
        return {"changed": True, "commit": commit, "pushed": push,
                "url": "https://someblueman.github.io/longhouse/"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(publish(Record(args.repo), push=args.push), indent=2))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"published": False, "error": type(error).__name__}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
