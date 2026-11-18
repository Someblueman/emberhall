"""The terminal's public entry must include the page it actually runs."""
import json
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit

from house.home_work import git
from house.publish import BRANCH, publish
from tests.support import HouseCase

SOURCE = Path(__file__).resolve().parents[1]


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value and name in {"href", "src"}:
                self.targets.append(value)


class TerminalPublicPlayerTests(HouseCase):
    def test_readme_destination_and_page_dependencies_survive_publication(self):
        manifest = json.loads((SOURCE / 'site/projects.json').read_text())
        terminal = next(p for p in manifest['projects'] if p['id'] == 'terminal-in-brainfuck')
        destination = 'https://someblueman.github.io/emberhall/' + terminal['href']
        readme = (SOURCE / 'README.md').read_text().split('## What is happening now', 1)[1]
        readme = readme.split('\n## ', 1)[0]
        self.assertIn('](' + destination + ')', readme)
        self.assertEqual(terminal['action'], 'Play')

        (self.repo / 'site').mkdir()
        for name in ('index.html', 'house.js', 'house.css', 'projects.json'):
            (self.repo / 'site' / name).write_bytes((SOURCE / 'site' / name).read_bytes())
        for project in manifest['projects']:
            for name in project['files']:
                target = self.repo / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((SOURCE / name).read_bytes())
        git(self.repo, 'add', '.')
        git(self.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test',
            '-c', 'user.email=test@local', 'commit', '-m', 'Public player fixture')
        publish(self.record)

        def published(path):
            return self.record.git('show', BRANCH + ':' + path)

        self.assertEqual(json.loads(published('projects.json')), manifest)
        for path in terminal['files']:
            self.assertEqual(published(path), (SOURCE / path).read_bytes(), path)

        # Check the actual HTML, so adding a script without publishing it fails.
        page = PageLinks()
        page.feed(published(terminal['href']).decode())
        folder = PurePosixPath(terminal['href']).parent
        for target in page.targets:
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            path = str(folder / parsed.path)
            self.assertIn(path, terminal['files'], target)
            self.assertTrue(published(path), target)

        # The linked generator also needs its local imports to be usable.
        for name in ('build_terminal.py', 'controls.py'):
            source = published(str(folder / name)).decode()
            for module in re.findall(r'^from (\w+) import', source, re.MULTILINE):
                local = folder / (module + '.py')
                if (SOURCE / local).is_file():
                    self.assertIn(str(local), terminal['files'])
