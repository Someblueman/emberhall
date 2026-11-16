"""Missing-page navigation follows the same committed-file boundary as the house."""
from pathlib import Path

from house.home_work import git
from house.publish import BRANCH, publish
from tests.support import HouseCase


class MissingPagePublicationTests(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo / "site").mkdir()
        for name in ("index.html", "house.js", "house.css"):
            (self.repo / "site" / name).write_text(name)
        self.page = self.repo / "site/404.html"
        self.commit()

    def commit(self):
        git(self.repo, "add", "site")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", "Public fixture")

    def names(self):
        return git(self.repo, "ls-tree", "-r", "--name-only", BRANCH).splitlines()

    def test_optional_page_uses_committed_bytes_and_preserves_dirty_source(self):
        publish(self.record)
        self.assertNotIn("404.html", self.names())
        self.page.write_text("private untracked draft")
        self.assertFalse(publish(self.record)["changed"])
        self.assertNotIn("404.html", self.names())

        source = Path(__file__).resolve().parents[1] / "site/404.html"
        accepted = source.read_bytes()
        self.page.write_bytes(accepted)
        self.commit()
        self.page.write_text("private staged draft")
        git(self.repo, "add", "site/404.html")
        self.page.write_text("private unstaged draft")
        index = (self.record.gitdir / "index").read_bytes()
        head = git(self.repo, "rev-parse", "HEAD")
        ledger = self.record.read()[2]

        self.assertTrue(publish(self.record)["changed"])
        self.assertEqual(self.record.git("show", BRANCH + ":404.html"), accepted)
        self.assertFalse(publish(self.record)["changed"])
        self.assertEqual((self.record.gitdir / "index").read_bytes(), index)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), head)
        self.assertEqual(self.record.read()[2], ledger)
        self.assertEqual(self.page.read_text(), "private unstaged draft")

        self.page.unlink()
        self.commit()
        publish(self.record)
        self.assertNotIn("404.html", self.names())

    def test_symlink_is_refused_without_changing_the_published_snapshot(self):
        publish(self.record)
        previous = self.record.ref("refs/heads/" + BRANCH)
        self.page.symlink_to("index.html")
        self.commit()
        with self.assertRaisesRegex(ValueError, "not a regular blob: site/404.html"):
            publish(self.record)
        self.assertEqual(self.record.ref("refs/heads/" + BRANCH), previous)
