"""Public snapshots use an independent index and preserve the source checkout."""
import json

from house.home_work import git
from house.publish import BRANCH, publish
from house.public_history import decode
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
        public = decode(json.loads(git(self.repo, "show", BRANCH + ":history.json")))
        self.assertEqual(public["journal_head"], self.record.read()[2])

    def test_rejected_local_chain_is_preserved_and_remote_history_fast_forwards(self):
        from unittest.mock import patch
        import subprocess
        from house.public_history import decode

        (self.repo / 'site').mkdir()
        for name in ('index.html', 'house.js', 'house.css'):
            (self.repo / 'site' / name).write_text('public ' + name)
        git(self.repo, 'add', '.')
        git(self.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test',
            '-c', 'user.email=test@local', 'commit', '-m', 'Fixture')
        remote = self.repo.parent / (self.repo.name + '-pages-remote')
        subprocess.run(['git', 'init', '--bare', str(remote)], capture_output=True, check=True)
        git(self.repo, 'remote', 'add', 'origin', str(remote))
        first = publish(self.record, push=True)['commit']
        ref = 'refs/heads/' + BRANCH
        # Existing v1 snapshot and oversized ancestor, followed by a small tip.
        # Recovery must inspect all unpublished blobs, not only the latest tree.
        projection = decode(json.loads(git(self.repo, 'show', ref + ':history.json')))
        blob = self.record.git('hash-object', '-w', '--stdin', data=json.dumps(projection).encode()).decode().strip()
        huge = self.record.git('hash-object', '-w', '--stdin', data=b'x' * 120000).decode().strip()
        tree = self.record.git('mktree', data=f'100644 blob {blob}\thistory.json\n100644 blob {huge}\toversized\n'.encode()).decode().strip()
        bad = self.record.git('commit-tree', tree, '-p', first, data=b'rejected snapshot').decode().strip()
        small_tree = self.record.git('mktree', data=f'100644 blob {blob}\thistory.json\n'.encode()).decode().strip()
        tip = self.record.git('commit-tree', small_tree, '-p', bad, data=b'later unpublished snapshot').decode().strip()
        self.record.git('update-ref', ref, tip, first)
        before_index = (self.record.gitdir / 'index').read_bytes()
        before_source = git(self.repo, 'rev-parse', 'HEAD')
        before_ledger = self.record.read()[2]
        with patch('house.publish.MAX_PUBLIC_BLOB', 100000):
            fixed = publish(self.record, push=True)
        self.assertEqual(git(self.repo, 'rev-parse', fixed['commit'] + '^'), first)
        self.assertEqual(git(self.repo, 'rev-parse', 'refs/house-publication-recovery/' + tip), tip)
        self.assertEqual(git(remote, 'rev-parse', ref), fixed['commit'])
        self.assertEqual(decode(json.loads(git(self.repo, 'show', ref + ':history.json')))['frames'], projection['frames'])
        self.assertEqual(before_index, (self.record.gitdir / 'index').read_bytes())
        self.assertEqual(before_source, git(self.repo, 'rev-parse', 'HEAD'))
        self.assertEqual(before_ledger, self.record.read()[2])
        self.assertFalse(publish(self.record, push=True)['changed'])
        # A rejected upload preserves the candidate and retries that exact commit.
        self.record.append('say', 'alice', {'text': 'A later public event'})
        hook = remote / 'hooks/pre-receive'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o700)
        with self.assertRaises(subprocess.CalledProcessError):
            publish(self.record, push=True)
        retry_head = git(self.repo, 'rev-parse', ref)
        self.assertNotEqual(retry_head, fixed['commit'])
        self.assertEqual(git(remote, 'rev-parse', ref), fixed['commit'])
        hook.unlink()
        fixed = publish(self.record, push=True)
        self.assertFalse(fixed['changed'])
        self.assertEqual(fixed['commit'], retry_head)
        self.assertEqual(git(remote, 'rev-parse', ref), retry_head)
        # Oversized output fails before any publication ref can change.
        with patch('house.publish.MAX_PUBLIC_BLOB', 1), self.assertRaises(ValueError):
            publish(self.record, push=True)
        self.assertEqual(git(self.repo, 'rev-parse', ref), fixed['commit'])
        # Divergence is refused; no remote overwrite or automatic reconciliation.
        other = self.record.git('commit-tree', small_tree, data=b'unrelated').decode().strip()
        self.record.git('update-ref', ref, other, fixed['commit'])
        with self.assertRaises(ValueError):
            publish(self.record, push=True)
        self.assertEqual(git(remote, 'rev-parse', ref), fixed['commit'])
