"""CLI artifact recovery and advice-only transfer to a separate house."""
import json
import os

from house.record import Record
from tests.support import HouseCase


class ArtifactAndSeedTests(HouseCase):
    def test_finish_extract_recovers_original_bytes_after_worktree_changes(self):
        self.task()
        self.cli("claim", "work", "--as", "alice", "--token", "artifact-token", "--expect", "0")
        source = self.repo / "nested/result.txt"
        source.parent.mkdir()
        source.write_bytes(b"Original bytes\x00\xff")
        self.cli("finish", "work", "--as", "alice", "--token", "artifact-token",
                 "--result", "Done", "--artifact", "nested/result.txt")
        source.write_bytes(b"Later accidental damage")
        target = self.root / "extracted"
        self.cli("extract", "work", str(target))
        self.assertEqual((target / "nested/result.txt").read_bytes(), b"Original bytes\x00\xff")
        self.cli("extract", "work", str(target), success=False)
        self.assertEqual((target / "nested/result.txt").read_bytes(), b"Original bytes\x00\xff")

    def test_finish_rejects_path_escape_symlinks_and_fifo_without_blocking(self):
        self.task()
        self.cli("claim", "work", "--as", "alice", "--token", "artifact-token", "--expect", "0")
        (self.root / "secret").write_text("Must not copy")
        (self.repo / "link").symlink_to(self.root / "secret")
        (self.repo / "dirlink").symlink_to(self.root, target_is_directory=True)
        os.mkfifo(self.repo / "pipe")
        before = self.record.read()[2]
        for path in ("../secret", str(self.root / "secret"), "link", "dirlink/secret", "pipe"):
            with self.subTest(path=path):
                self.cli("finish", "work", "--as", "alice", "--token", "artifact-token",
                         "--result", "Attack", "--artifact", path, success=False)
        self.assertEqual(self.record.read()[2], before)

    def lesson(self, lesson, key):
        self.record.append("learn", "alice", {"lesson": lesson, "key": key, "claim": lesson,
                           "evidence": "Independent reproducible test"})

    def test_seed_adoption_keeps_provenance_but_not_authority_or_reviews(self):
        self.lesson("reviewed", "good")
        self.lesson("unreviewed", "unreviewed")
        self.lesson("conflict1", "contested")
        self.record.append("review", "bob", {"lesson": "conflict1", "evidence": "Checked"})
        self.lesson("conflict2", "contested")
        self.record.append("review", "bob", {"lesson": "reviewed", "evidence": "Checked"})
        seed = self.root / "wisdom.json"
        self.cli("seed", str(seed))
        exported = json.loads(seed.read_text())
        self.assertEqual([v["source_lesson"] for v in exported["lessons"]], ["reviewed"])
        target = Record(self.new_repo("daughter"))
        target.found("Daughter", "Daughter rules")
        target.append("arrive", "newcomer", {"name": "Newcomer"})
        self.cli("adopt", str(seed), "--as", "newcomer", repo=target.root)
        head = target.read()[2]
        self.cli("adopt", str(seed), "--as", "newcomer", repo=target.root)
        state = target.read()[0]
        self.assertEqual(target.read()[2], head)
        self.assertEqual(state["rules"], "Daughter rules")
        self.assertEqual(state["owner_key"], "")
        self.assertEqual(set(state["residents"]), {"newcomer"})
        self.assertEqual(state["tasks"], {})
        self.assertNotEqual(state["house_id"], exported["source_house"])
        lesson = next(iter(state["lessons"].values()))
        self.assertEqual(lesson["status"], "observed")
        self.assertEqual(lesson["reviews"], [])
        self.assertIn(exported["source_house"], lesson["evidence"])
        self.assertIn(exported["source_head"], lesson["evidence"])

    def test_invalid_later_seed_lesson_does_not_partially_import(self):
        seed = self.root / "bad-seed.json"
        seed.write_text(json.dumps({"format": "longhouse-wisdom-v1", "source_house": "elsewhere",
            "source_head": "a" * 40, "lessons": [
                {"key": "one", "claim": "Valid", "evidence": "Evidence", "source_lesson": "one"},
                {"key": "two", "claim": "Invalid", "evidence": "", "source_lesson": "two"}]}))
        before = self.record.read()[2]
        self.cli("adopt", str(seed), "--as", "alice", success=False)
        self.assertEqual(self.record.read()[2], before)
