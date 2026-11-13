"""Public snapshots use an independent index and preserve the source checkout."""
import json

from house.home_work import git
from house.publish import BRANCH, publish
from tests.support import HouseCase


class PublishTests(HouseCase):
    def test_publication_preserves_dirty_source_and_does_not_repeat_unchanged_views(self):
        (self.repo / "site").mkdir()
        for name in ("index.html", "house.js", "house.css"):
            (self.repo / "site" / name).write_text("committed " + name)
        git(self.repo, "add", ".")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test", "-c", "user.email=test@local",
            "commit", "-m", "Public fixture")
        (self.repo / "site/index.html").write_text("unfinished private edit")
        git(self.repo, "add", "site/index.html")
        before_index = (self.record.gitdir / "index").read_bytes()
        before_source = git(self.repo, "rev-parse", "HEAD")
        first = publish(self.record)
        second = publish(self.record)
        self.assertTrue(first["changed"])
        self.assertFalse(second["changed"])
        self.assertEqual(before_index, (self.record.gitdir / "index").read_bytes())
        self.assertEqual(before_source, git(self.repo, "rev-parse", "HEAD"))
        self.assertEqual(git(self.repo, "show", BRANCH + ":index.html"), "committed index.html")
        public = json.loads(git(self.repo, "show", BRANCH + ":history.json"))
        self.assertEqual(public["journal_head"], self.record.read()[2])
