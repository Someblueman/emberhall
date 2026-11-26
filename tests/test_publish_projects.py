"""The Pages tree contains only manifest-listed committed project files."""
import json
from pathlib import Path

from house.home_work import git
from house.publish import BRANCH, publish
from tests.support import HouseCase

SOURCE = Path(__file__).resolve().parents[1]


class ProjectPublicationTests(HouseCase):
    def setUp(self):
        super().setUp()
        (self.repo / 'site').mkdir()
        for name in ('index.html', 'house.js', 'house.css'):
            (self.repo / 'site' / name).write_text(name)
        self.manifest = json.loads((SOURCE / 'site/projects.json').read_text())
        for project in self.manifest['projects']:
            for name in project['files']:
                target = self.repo / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((SOURCE / name).read_bytes())
        self.write_manifest()
        private = self.repo / 'projects/night-ferry/PLAYTEST-RECORD.md'
        private.write_text('private playtest')
        self.commit()

    def write_manifest(self):
        (self.repo / 'site/projects.json').write_text(json.dumps(self.manifest))

    def commit(self):
        git(self.repo, 'add', '.')
        git(self.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test',
            '-c', 'user.email=test@local', 'commit', '-m', 'Project fixture')

    def test_real_manifest_tree_and_committed_bytes(self):
        target = 'projects/night-ferry/player/player.js'
        committed = (self.repo / target).read_bytes()
        (self.repo / target).write_text('dirty')
        git(self.repo, 'add', target)
        before_index = (self.record.gitdir / 'index').read_bytes()
        head = git(self.repo, 'rev-parse', 'HEAD')
        publish(self.record)
        self.assertEqual(before_index, (self.record.gitdir / 'index').read_bytes())
        self.assertEqual(head, git(self.repo, 'rev-parse', 'HEAD'))
        self.assertEqual(self.record.git('show', BRANCH + ':' + target), committed)
        names = set(git(self.repo, 'ls-tree', '-r', '--name-only', BRANCH).splitlines())
        files = {name for project in self.manifest['projects'] for name in project['files']}
        self.assertEqual(names, files | {'projects.json', 'index.html', 'house.js', 'house.css',
                                        'history.json', 'current.json', 'balance.json', 'head.json', '.nojekyll'})
        self.assertNotIn('projects/night-ferry/PLAYTEST-RECORD.md', names)

    def test_rejects_unsafe_missing_untracked_and_symlink(self):
        paths = ['/projects/x', 'projects/../secret', 'projects/x/.hidden',
                 'projects/x//file', 'projects/x\\file', 'projects/x/missing',
                 'projects/x/untracked', 'projects/x/link']
        directory = self.repo / 'projects/x'
        directory.mkdir(parents=True)
        (directory / 'link').symlink_to('../night-ferry/player/player.js')
        git(self.repo, 'add', 'projects/x/link')
        git(self.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test',
            '-c', 'user.email=test@local', 'commit', '-m', 'Symlink fixture')
        (directory / 'untracked').write_text('not committed')
        for path in paths:
            with self.subTest(path=path):
                self.manifest['projects'][0]['files'] = [path]
                self.write_manifest()
                git(self.repo, 'add', 'site/projects.json')
                git(self.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test',
                    '-c', 'user.email=test@local', 'commit', '-m', 'Invalid manifest')
                with self.assertRaises(ValueError):
                    publish(self.record)
                self.assertIsNone(self.record.ref('refs/heads/' + BRANCH))

    def test_chronicle_is_rebuilt_from_the_journal_and_never_publishes_its_input(self):
        folder = self.repo / 'site/chronicle'
        folder.mkdir()
        page = folder / 'index.html'
        page.write_text('accepted static chronicle')
        publish(self.record)
        self.assertNotIn('chronicle/index.html',
                         git(self.repo, 'ls-tree', '-r', '--name-only', BRANCH).splitlines())
        (folder / 'export.json').write_text('private journal input')
        self.commit()
        page.write_text('dirty page must not publish')
        publish(self.record)
        from house import chronicle_page
        published = self.record.git('show', BRANCH + ':chronicle/index.html')
        events = self.record.read()[1]
        self.assertEqual(published, chronicle_page.render_html(chronicle_page.select_milestones(
            [event | {'sequence': n} for n, event in enumerate(events, 1)]), through=len(events),
            house_id=self.record.read()[0].get('house_id')).encode())
        self.assertIn(b'Emberhall Chronicle Room', published)
        self.assertNotIn(b'dirty page', published)
        # The house's copy is the project's generator, apart from its opening note.
        strip = lambda text: text[text.index('from __future__') if 'from __future__' in text else text.index('import argparse'):]
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(strip((root / 'house/chronicle_page.py').read_text()),
                         strip((root / 'projects/emberhall-chronicle-room/chronicle.py').read_text()))
        self.assertNotIn('chronicle/export.json',
                         git(self.repo, 'ls-tree', '-r', '--name-only', BRANCH).splitlines())

    def test_chronicle_rejects_committed_symlink(self):
        folder = self.repo / 'site/chronicle'
        folder.mkdir()
        (folder / 'index.html').symlink_to('../index.html')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'not a regular blob'):
            publish(self.record)
        self.assertIsNone(self.record.ref('refs/heads/' + BRANCH))
