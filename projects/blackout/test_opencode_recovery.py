"""Real CLI recovery boundary proposed by Briar (Codex, not OpenCode)."""

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).with_name("blackout.py")


class RecoveryBoundaryTests(unittest.TestCase):
    def test_fifo_after_valid_candidate_rejects_entire_plan_and_allows_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary).resolve()
            root = home / "archive"
            root.mkdir()
            target = root / "needed.txt"
            target.write_bytes(b"irreplaceable bytes\n")
            manifest = home / "manifest.json"

            def run_cli(command):
                return subprocess.run(
                    [sys.executable, str(CLI), command, str(root), str(manifest)],
                    capture_output=True, text=True, timeout=5)

            created = run_cli("create")
            self.assertEqual(created.returncode, 0, created.stderr)
            candidate = root / "a-rescue.txt"
            target.rename(candidate)
            baseline = run_cli("plan")
            self.assertEqual(baseline.returncode, 1, baseline.stderr)
            self.assertEqual(baseline.stderr, "")
            plan = json.loads(baseline.stdout)
            self.assertEqual(plan["restores"], [{
                "ambiguous": False, "candidates": ["a-rescue.txt"],
                "recoverable": True, "status": "missing", "target": "needed.txt",
            }])

            # Sorted scanning reads a-rescue.txt before encountering the FIFO.
            # A viable candidate must never turn an incomplete scan into a plan.
            fifo = root / "z-blocked.fifo"
            os.mkfifo(fifo)

            def snapshot(nodes):
                result = {}
                for node in nodes:
                    info = node.lstat()
                    content = node.read_bytes() if stat.S_ISREG(info.st_mode) else None
                    result[node.name] = (
                        info.st_dev, info.st_ino, info.st_mode, info.st_size,
                        info.st_mtime_ns, info.st_ctime_ns, content)
                return result

            nodes = (root, candidate, fifo, manifest)
            before = snapshot(nodes)
            failed = run_cli("plan")
            self.assertEqual(failed.returncode, 2, failed.stdout + failed.stderr)
            self.assertEqual(failed.stdout, "")
            error = json.loads(failed.stderr)
            self.assertEqual(set(error), {"error"})
            self.assertIn("z-blocked.fifo", error["error"])
            self.assertNotIn("Traceback", failed.stderr)
            self.assertEqual(snapshot(nodes), before)
            self.assertEqual(sorted(node.name for node in root.iterdir()),
                             ["a-rescue.txt", "z-blocked.fifo"])
            self.assertFalse(target.exists())

            # The operator removes only the fixture FIFO, then retries unchanged
            # inputs. Planning itself must neither restore nor consume a source.
            fifo.unlink()
            retried = run_cli("plan")
            self.assertEqual(retried.returncode, 1, retried.stderr)
            self.assertEqual(retried.stderr, "")
            self.assertEqual(retried.stdout, baseline.stdout)
            self.assertEqual(snapshot((candidate, manifest)), {
                node.name: before[node.name] for node in (candidate, manifest)
            })
            self.assertFalse(target.exists())
            self.assertEqual(list(root.iterdir()), [candidate])


if __name__ == "__main__":
    unittest.main()
