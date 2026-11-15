"""Run the house's unittest suite in parallel processes.

``python -m unittest discover -s tests -v`` runs every test one after another
and takes about fifteen minutes. This runner discovers the same tests, splits
them into batches (one test class each, large classes in smaller pieces), runs
the batches in separate processes and prints each batch's verbose output
followed by a standard unittest summary, so callers that parse
``Ran N tests`` and ``OK`` keep working. Exit status is 0 only if every batch
passed. Set EMBERHALL_TEST_JOBS to change the number of parallel workers.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import unittest

BATCH = 6


def _ids(suite) -> list[str]:
    found = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            found.extend(_ids(item))
        else:
            found.append(item.id())
    return found


def batches(root: Path) -> list[list[str]]:
    loader = unittest.TestLoader()
    suite = loader.discover(str(root / "tests"), top_level_dir=str(root))
    if loader.errors:
        raise SystemExit("test discovery failed:\n" + "\n".join(loader.errors))
    classes: dict[str, list[str]] = {}
    for test_id in _ids(suite):
        classes.setdefault(test_id.rsplit(".", 1)[0], []).append(test_id)
    work = []
    for ids in classes.values():
        if len(ids) <= BATCH:
            work.append([ids[0].rsplit(".", 1)[0]])
        else:
            work.extend(ids[index:index + BATCH] for index in range(0, len(ids), BATCH))
    # Bigger batches first so the slowest work does not start last.
    return sorted(work, key=lambda batch: -sum(len(classes.get(name, [name])) for name in batch))


def run_batch(root: Path, batch: list[str]) -> tuple[list[str], int, bytes]:
    process = subprocess.run([sys.executable, "-m", "unittest", "-v", *batch], cwd=root,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return batch, process.returncode, process.stdout


def main() -> int:
    root = Path.cwd()
    if not (root / "tests" / "__init__.py").is_file():
        # Not a package: test ids cannot be addressed separately, so run them in one process.
        return subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                              cwd=root).returncode
    started = time.time()
    work = batches(root)
    jobs = int(os.environ.get("EMBERHALL_TEST_JOBS") or min(8, os.cpu_count() or 2))
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        results = list(pool.map(lambda batch: run_batch(root, batch), work))
    total = skipped = failures = errors = 0
    broken = []
    out = sys.stdout.buffer
    for batch, code, output in sorted(results, key=lambda item: item[0]):
        out.write(output)
        ran = re.findall(rb"\nRan ([0-9]+) tests? in ", output)
        if not ran:
            broken.append(batch)
            continue
        total += int(ran[-1])
        tail = output[output.rfind(b"\nRan "):]
        counts = {key.decode(): int(value) for key, value in re.findall(rb"(skipped|failures|errors)=([0-9]+)", tail)}
        skipped += counts.get("skipped", 0)
        failures += counts.get("failures", 0)
        errors += counts.get("errors", 0)
        if code != 0 and not counts.get("failures") and not counts.get("errors"):
            broken.append(batch)
    for batch in broken:
        out.write(b"\nERROR: batch did not complete: " + " ".join(batch).encode() + b"\n")
    errors += len(broken)
    out.write(b"\n" + b"-" * 70 + b"\n")
    out.write(f"Ran {total} tests in {time.time() - started:.3f}s\n\n".encode())
    if failures or errors:
        parts = [f"failures={failures}"] * bool(failures) + [f"errors={errors}"] * bool(errors)
        parts += [f"skipped={skipped}"] * bool(skipped)
        out.write(f"FAILED ({', '.join(parts)})\n".encode())
        return 1
    out.write((f"OK (skipped={skipped})\n" if skipped else "OK\n").encode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
