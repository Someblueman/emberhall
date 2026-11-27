"""Public-byte and output boundaries for a local rendering copy."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import public_site_fixture as fixture


class PublicSiteFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.output = self.root / "output"
        self.snapshot = {"version": 1, "source_head": "a" * 40,
                         "journal_head": "b" * 40, "frames": [{"seq": 42}]}
        self.prepare()

    def prepare(self, snapshot=None, companion=None):
        self.compressed = gzip.compress(json.dumps(snapshot or self.snapshot).encode())
        digest = hashlib.sha256(self.compressed).hexdigest()
        self.companion = companion or "current/" + digest[:16] + ".json.gz"
        listing = dict(self.snapshot, gzip=self.companion,
                       history={"current_only": True, "last_sequence": 42, "total_frames": 42})
        listing.pop("frames")
        text = json.dumps(listing)
        self.listing = self.root / "listing.json"
        self.delivery = self.root / "delivery.json"
        self.listing.write_text(json.dumps(dict(status=200, url=fixture.PUBLIC_URL + "current.json",
            text=text, sha256=fixture.sha(text.encode()), truncated=False, text_truncated=False)))
        self.delivery.write_text(json.dumps(dict(status=200, url=fixture.PUBLIC_URL + self.companion,
            sha256=digest, bytes_read=len(self.compressed), truncated=False)))

    def git(self, repository, *args):
        self.assertEqual(repository, self.root)
        if args == ("rev-parse", "--verify", fixture.PUBLIC_REF + "^{commit}"):
            return ("c" * 40 + "\n").encode()
        self.assertEqual(args[0], "show")
        if args[1] == "c" * 40 + ":" + self.companion:
            return self.compressed
        if args[1] == "c" * 40 + ":balance.json":
            return b'{"note":"separate public balance"}'
        if args[1] == "a" * 40 + ":site/projects.json":
            return b'{"projects":[{"files":["projects/example/gallery-preview.svg"]}]}'
        if args[1] == "a" * 40 + ":projects/example/gallery-preview.svg":
            return b'<svg xmlns="http://www.w3.org/2000/svg"/>'
        self.assertIn(args[1], ["a" * 40 + ":site/" + name for name in fixture.ASSETS])
        return args[1].encode()

    def build(self):
        with patch.object(fixture, "git", side_effect=self.git):
            return fixture.build(self.root, self.output, self.listing, self.delivery)

    def test_exact_source_and_witnessed_compressed_bytes_are_copied(self):
        report = self.build()
        self.assertEqual(report["sequence"], 42)
        self.assertEqual((self.output / self.companion).read_bytes(), self.compressed)
        self.assertEqual((self.output / "house.js").read_bytes(), ("a" * 40 + ":site/house.js").encode())
        self.assertEqual(json.loads((self.output / "head.json").read_text()),
                         {key: self.snapshot[key] for key in ("journal_head", "source_head")})
        self.assertTrue((self.output / "fixture-provenance.json").is_file())
        self.assertTrue((self.output / "projects/example/gallery-preview.svg").is_file())

    def test_changed_companion_is_rejected_before_output(self):
        receipt = json.loads(self.delivery.read_text())
        receipt["sha256"] = "0" * 64
        self.delivery.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, "witnessed public bytes"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_unsafe_companion_never_reaches_git(self):
        self.prepare(companion="../private.json.gz")
        with patch.object(fixture, "git") as git:
            with self.assertRaisesRegex(ValueError, "safe compressed"):
                fixture.build(self.root, self.output, self.listing, self.delivery)
            git.assert_not_called()

    def test_changed_listing_text_is_rejected(self):
        receipt = json.loads(self.listing.read_text())
        receipt["text"] += " "
        self.listing.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, "receipt hash"):
            self.build()

    def test_different_snapshot_identity_is_rejected(self):
        self.prepare(snapshot={**self.snapshot, "journal_head": "d" * 40})
        with self.assertRaisesRegex(ValueError, "identity"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_existing_output_and_dangling_symlink_are_preserved(self):
        self.output.mkdir()
        marker = self.output / "kept"
        marker.write_text("unchanged")
        with self.assertRaisesRegex(ValueError, "new directory"):
            self.build()
        self.assertEqual(marker.read_text(), "unchanged")
        marker.unlink()
        self.output.rmdir()
        self.output.symlink_to(self.root / "missing")
        with self.assertRaisesRegex(ValueError, "new directory"):
            self.build()
        self.assertTrue(self.output.is_symlink())

    def test_decoded_size_limit_leaves_no_output(self):
        with patch.object(fixture, "MAX_DECODED", 8):
            with self.assertRaisesRegex(ValueError, "size limit"):
                self.build()
        self.assertFalse(self.output.exists())

    def test_truncated_delivery_is_not_evidence(self):
        receipt = json.loads(self.delivery.read_text())
        receipt["truncated"] = True
        self.delivery.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, "complete successful"):
            self.build()

    def test_unsafe_catalogue_preview_leaves_no_output(self):
        ordinary = self.git
        def unsafe(repository, *args):
            if args == ("show", "a" * 40 + ":site/projects.json"):
                return b'{"projects":[{"files":["../../outside/gallery-preview.svg"]}]}'
            return ordinary(repository, *args)
        with patch.object(fixture, "git", side_effect=unsafe):
            with self.assertRaisesRegex(ValueError, "Unsafe.*preview"):
                fixture.build(self.root, self.output, self.listing, self.delivery)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
