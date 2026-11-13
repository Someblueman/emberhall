"""Real process races and process death, never attacks on the live house."""
import json
import signal
import subprocess
import time

from tests.support import HouseCase


class ConcurrentJournalTests(HouseCase):
    def test_parallel_appends_are_exactly_once_and_do_not_touch_source_index(self):
        (self.repo / "source.txt").write_text("uncommitted source\n")
        self.record.git("add", "source.txt")
        index = (self.repo / ".git/index").read_bytes()
        writers = [self.process("say", "--as", "alice", "--request", f"parallel-{i}",
                                f"Message {i}") for i in range(12)]
        receipts = []
        for process in writers:
            out, err = process.communicate(timeout=30)
            self.assertEqual(process.returncode, 0, err)
            receipts.append(json.loads(out))
        state, events, _ = self.record.read()
        self.assertEqual(state["sequence"], 15)
        self.assertEqual({r["sequence"] for r in receipts}, set(range(4, 16)))
        self.assertEqual({e["id"] for e in events[3:]}, {f"parallel-{i}" for i in range(12)})
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)
        self.assertEqual((self.repo / "source.txt").read_text(), "uncommitted source\n")

    def test_claim_race_has_one_owner(self):
        self.task()
        processes = [self.process("claim", "work", "--as", actor, "--expect", "0",
                                  "--token", actor + "-token", "--seconds", "60")
                     for actor in ("alice", "bob")]
        results = [(p, p.communicate(timeout=20)) for p in processes]
        self.assertEqual(sorted(p.returncode for p, _ in results), [0, 2])
        winner = next(i for i, (p, _) in enumerate(results) if p.returncode == 0)
        task = self.record.read()[0]["tasks"]["work"]
        self.assertEqual(task["owner"], ("alice", "bob")[winner])
        self.assertEqual(task["generation"], 1)

    def test_duplicate_requests_race_to_one_event(self):
        processes = [self.process("say", "--as", "alice", "--request", "same", "Hello")
                     for _ in range(6)]
        receipts = []
        for process in processes:
            out, err = process.communicate(timeout=20)
            self.assertEqual(process.returncode, 0, err)
            receipts.append(json.loads(out))
        self.assertEqual(sum(not item["replayed"] for item in receipts), 1)
        self.assertEqual({item["sequence"] for item in receipts}, {4})
        self.assertEqual(self.record.read()[0]["sequence"], 4)
        with self.assertRaisesRegex(ValueError, "different content"):
            self.record.append("say", "alice", {"text": "Changed"}, "same")

    def test_killed_writer_releases_kernel_lock_and_recovers_reserved_git_lock(self):
        before = self.record.read()[2]
        child = self.script('''
import sys, time
from house.record import Record, REF
r = Record(sys.argv[1])
with r.locked():
    lock = r.common / (REF + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text("interrupted update")
    print("locked", flush=True)
    time.sleep(60)
''')
        self.addCleanup(lambda: child.poll() is None and child.kill())
        self.assertEqual(child.stdout.readline().strip(), "locked")
        child.send_signal(signal.SIGKILL)
        child.communicate(timeout=5)
        self.assertEqual(self.record.read()[2], before)
        unrelated = self.repo / ".git/index.lock"
        unrelated.write_text("not owned by house")
        self.cli("say", "--as", "bob", "Writer recovered")
        self.assertTrue(unrelated.exists())
        self.assertFalse((self.repo / ".git/refs/heads/house-ledger.lock").exists())

    def test_publication_survives_lost_process_receipt(self):
        child = self.script('''
import os, sys
from house.record import Record
Record(sys.argv[1]).append("say", "alice", {"text": "Durable"}, "lost-receipt")
os._exit(27)
''')
        child.communicate(timeout=20)
        self.assertEqual(child.returncode, 27)
        receipt = self.cli("receipt", "lost-receipt")
        self.assertEqual(receipt["event"]["data"], {"text": "Durable"})
        retry = self.cli("say", "--as", "alice", "--request", "lost-receipt", "Durable")
        self.assertTrue(retry["replayed"])
        self.assertEqual(self.record.read()[0]["sequence"], 4)

    def test_git_child_retains_writer_lock_after_parent_is_killed(self):
        marker = self.repo / "git-child-ready"
        release = self.repo / "release-git-child"
        child = self.script("""
import sys
from house.record import Record
r = Record(sys.argv[1])
with r.locked():
    r.git("-c", "alias.hold=!touch git-child-ready; while test ! -f release-git-child; do sleep 0.02; done", "hold")
""")
        writer = None
        try:
            deadline = time.monotonic() + 5
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(marker.exists(), "Git child did not reach the lock-holding point")
            child.kill()
            child.wait(timeout=5)
            writer = self.process("say", "--as", "bob", "After orphaned Git")
            with self.assertRaises(subprocess.TimeoutExpired):
                writer.communicate(timeout=0.2)
            release.touch()
            out, err = writer.communicate(timeout=10)
            self.assertEqual(writer.returncode, 0, (out, err))
        finally:
            release.touch()
            if child.poll() is None:
                child.kill()
            child.communicate(timeout=5)
            if writer is not None and writer.poll() is None:
                writer.kill()
                writer.communicate(timeout=5)
        self.assertEqual(self.record.read()[0]["sequence"], 4)
