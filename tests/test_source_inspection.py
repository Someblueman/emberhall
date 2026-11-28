"""Real committed-source inspection, refusal, and proportionate project acceptance."""
import fcntl
import json
import os
import shutil
import hashlib
import base64
import subprocess
import unittest

from house.home_work import contribution, git
from house.integrate import check_plan, inspect_contribution, export_contribution, integrate, INSPECTION_LIMIT
from house.home import pending_contributions
from house.resident_actions import parse
from tests import test_integrate


class SourceInspectionTests(unittest.TestCase):
    def setUp(self):
        self.f = test_integrate.IntegrationTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def amend(self, room):
        contribution(room, self.f.base, self.f.private / 'one/contribution.json', journal_artifacts={})

    def test_deleted_room_retains_exact_inspection_and_export_without_writes(self):
        f = self.f
        room = f.candidate('one', 'first\n')
        original = inspect_contribution(f.record, 'one', 'alice', bundle=True)
        shutil.rmtree(room)
        archive = f.private / 'one' / ('source-' + original['contribution'] + '.git')
        def snapshot(path):
            return {str(p.relative_to(path)): p.read_bytes() for p in path.rglob('*') if p.is_file()}
        before = snapshot(archive), f.record.read()[2], git(f.repo, 'rev-parse', 'HEAD')
        exact = inspect_contribution(f.record, 'one', 'alice', path='document.txt')
        self.assertEqual(exact['content'], 'first\n')
        actual = inspect_contribution(f.record, 'one', 'alice', bundle=True, preview=True)
        self.assertEqual(actual['patch_base64'], original['patch_base64'])
        self.assertEqual(actual['preview']['status'], 'clean')
        exported = export_contribution(f.record, 'one', 'alice', f.repo)
        patch = (f.repo / exported['path']).read_bytes()
        self.assertEqual(patch, base64.b64decode(original['patch_base64']))
        self.assertEqual(hashlib.sha256(patch).hexdigest(), original['patch_sha256'])
        self.assertEqual(before, (snapshot(archive), f.record.read()[2], git(f.repo, 'rev-parse', 'HEAD')))
        self.assertFalse((f.private / 'one/integration.json').exists())
        with self.assertRaisesRegex(ValueError, 'different, awake'):
            inspect_contribution(f.record, 'one', 'author-one', bundle=True)
        # Inspection fallback does not authorize execution/publication from a bare archive.
        with self.assertRaises(subprocess.CalledProcessError):
            integrate(f.record, 'one', 'alice', publish=True)

    def test_missing_or_changed_retained_source_fails_closed(self):
        f = self.f
        room = f.candidate('one', 'first\n')
        report_path = f.private / 'one/contribution.json'
        report = json.loads(report_path.read_text())
        archive = report_path.parent / ('source-' + report['commit'] + '.git')
        shutil.rmtree(room)
        legacy = dict(report); legacy.pop('retained_source')
        report_path.write_text(json.dumps(legacy))
        with self.assertRaisesRegex(ValueError, 'no retained source'):
            inspect_contribution(f.record, 'one', 'alice', bundle=True)
        report_path.write_text(json.dumps(report))
        git(archive, 'update-ref', 'HEAD', f.base)
        with self.assertRaisesRegex(ValueError, 'identity changed'):
            inspect_contribution(f.record, 'one', 'alice', bundle=True)
        (archive / 'objects/info/alternates').write_text(str(room / '.git/objects') + '\n')
        with self.assertRaisesRegex(ValueError, 'object dependency changed'):
            inspect_contribution(f.record, 'one', 'alice', bundle=True)
        shutil.rmtree(archive)
        with self.assertRaisesRegex(ValueError, 'retained source is unavailable'):
            export_contribution(f.record, 'one', 'alice', f.repo)

    def test_changed_live_room_does_not_fall_back_to_retained_source(self):
        f = self.f
        room = f.candidate('one', 'first\n')
        git(room, 'update-ref', 'HEAD', f.base)
        with self.assertRaisesRegex(ValueError, 'identity changed'):
            inspect_contribution(f.record, 'one', 'alice', bundle=True)

    def test_inspection_reads_exact_committed_diff_without_receipt_or_lock_mutation(self):
        f = self.f
        room = f.candidate('one', 'first\n')
        receipt = f.private / 'one/integration.json'
        receipt.write_bytes(b'{incomplete')
        (room / 'document.txt').write_text('uncommitted decoy\n')
        before = f.record.read()[2], git(f.repo, 'rev-parse', 'HEAD')
        with (f.private / 'integration.lock').open('a+b') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = inspect_contribution(f.record, 'one', 'alice', 'document.txt')
        self.assertEqual(result['content'], 'first\n')
        self.assertIn('+first', result['diff'])
        self.assertEqual(result['paths'], ['document.txt'])
        self.assertFalse(result['truncated'])
        self.assertEqual(receipt.read_bytes(), b'{incomplete')
        self.assertEqual((f.record.read()[2], git(f.repo, 'rev-parse', 'HEAD')), before)
        self.assertEqual((room / 'document.txt').read_text(), 'uncommitted decoy\n')
        for path in ('../document.txt', '/etc/passwd', ':(glob)*', 'tests/test_document.py'):
            with self.assertRaisesRegex(ValueError, 'exact changed'):
                inspect_contribution(f.record, 'one', 'alice', path)
        with self.assertRaisesRegex(ValueError, 'different, awake'):
            inspect_contribution(f.record, 'one', 'author-one')

    def test_large_binary_symlink_and_deleted_content_are_explicit(self):
        f = self.f
        room = f.candidate('one', 'first\n')
        (room / 'large.txt').write_text('x' * (INSPECTION_LIMIT + 1))
        (room / 'binary.bin').write_bytes(b'\x00\xff')
        (room / 'link').symlink_to('/etc/passwd')
        (room / 'document.txt').unlink()
        # Deliberately malformed legacy candidate: ordinary capture already refuses symlinks.
        git(room, 'add', '--all')
        git(room, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test', '-c', 'user.email=test@local',
            'commit', '-m', 'Boundary fixture')
        report = f.private / 'one/contribution.json'
        data = json.loads(report.read_text()); data['commit'] = git(room, 'rev-parse', 'HEAD')
        report.write_text(json.dumps(data))
        for path, status in (('large.txt', 'too-large'), ('binary.bin', 'binary'),
                             ('link', 'not-regular-file'), ('document.txt', 'deleted')):
            result = inspect_contribution(f.record, 'one', 'alice', path)
            self.assertEqual(result['content_status'], status)
            self.assertNotIn('content', result)
        self.assertTrue(inspect_contribution(f.record, 'one', 'alice')['truncated'])
        self.assertFalse((f.private / 'one/integration.json').exists())

    def test_rejection_is_terminal_preserves_source_and_skips_queue(self):
        f = self.f
        room = f.candidate('one', 'first\n')
        head = git(f.repo, 'rev-parse', 'HEAD')
        (f.repo / 'document.txt').write_text('unrelated dirty work\n')
        result = integrate(f.record, 'one', 'alice', reject='Cursor drops unseen events; repair first.')
        self.assertEqual(result['status'], 'rejected')
        self.assertEqual(pending_contributions(f.private), [])
        journal = f.record.read()[2]
        self.assertEqual(integrate(f.record, 'one', 'bob', publish=True), result)
        self.assertEqual(f.record.read()[2], journal)
        self.assertEqual(git(f.repo, 'rev-parse', 'HEAD'), head)
        self.assertEqual((room / 'document.txt').read_text(), 'first\n')
        self.assertEqual((f.repo / 'document.txt').read_text(), 'unrelated dirty work\n')
        with self.assertRaisesRegex(ValueError, 'bounded reason'):
            integrate(f.record, 'one', 'alice', reject=' ')

    def project(self):
        f = self.f
        room = f.candidate('one', 'base\n')
        project = room / 'projects/example'
        project.mkdir(parents=True)
        (project / 'data.json').write_text('{"value": 2}\n')
        (project / 'test_data.py').write_text(
            'import json,pathlib,unittest\nclass Data(unittest.TestCase):\n'
            ' def test_value(self): self.assertEqual(json.loads(pathlib.Path(__file__).with_name("data.json").read_text())["value"], 2)\n')
        self.amend(room)
        return room

    def test_actual_git_paths_select_checks_even_if_report_lies(self):
        f = self.f
        room = self.project()
        head = git(room, 'rev-parse', 'HEAD')
        scope, commands = check_plan(room, f.base, head)
        self.assertEqual(scope, 'projects:projects/example')
        self.assertIn('projects/example', commands[0])
        (room / 'document.txt').write_text('first\n')
        self.amend(room)
        path = f.private / 'one/contribution.json'
        report = json.loads(path.read_text()); report['paths'] = ['projects/example/data.json']
        path.write_text(json.dumps(report))
        scope, commands = check_plan(room, f.base, git(room, 'rev-parse', 'HEAD'))
        self.assertEqual(scope, 'foundation')
        self.assertIn('tests', commands[0])
        self.assertIn('document.txt', inspect_contribution(f.record, 'one', 'alice')['paths'])

    @unittest.skipIf(os.environ.get('EMBERHALL_CANDIDATE_SANDBOX') == '1', 'cannot nest macOS sandboxes')
    def test_project_tests_gate_real_merge_and_rejection_cannot_erase_acceptance(self):
        f = self.f
        self.project()
        result = integrate(f.record, 'one', 'alice', publish=True)
        self.assertEqual(result['status'], 'integrated')
        self.assertEqual(result['test_scope'], 'projects:projects/example')
        self.assertEqual(result['test_exit'], 0)
        self.assertEqual(integrate(f.record, 'one', 'bob', reject='late opinion'), result)

    @unittest.skipIf(os.environ.get('EMBERHALL_CANDIDATE_SANDBOX') == '1', 'cannot nest macOS sandboxes')
    def test_project_failure_does_not_publish(self):
        f = self.f
        room = self.project()
        (room / 'projects/example/data.json').write_text('{"value": 3}\n')
        self.amend(room)
        result = integrate(f.record, 'one', 'alice', publish=True)
        self.assertEqual(result['status'], 'tests-failed')
        self.assertEqual(git(f.repo, 'rev-parse', 'HEAD'), f.base)

    @unittest.skipIf(os.environ.get('EMBERHALL_CANDIDATE_SANDBOX') == '1', 'cannot nest macOS sandboxes')
    def test_prose_and_json_project_without_tests_reports_zero_and_still_checks_syntax(self):
        f = self.f
        room = f.candidate('one', 'base\n')
        project = room / 'projects/case'
        project.mkdir(parents=True)
        (project / 'README.md').write_text('Six facts, no executable code.\n')
        (project / 'facts.json').write_text('{"facts": [1, 2, 3]}\n')
        self.amend(room)
        result = integrate(f.record, 'one', 'alice')
        self.assertEqual(result['status'], 'reviewed')
        log = (f.private / (result['candidate'] + '.tests.log')).read_text()
        self.assertIn('Ran 0 tests', log)
        self.assertIn('json.load', log)
        # Zero unit tests must not hide a subsequent JSON syntax error.
        (project / 'facts.json').write_text('{broken')
        self.amend(room)
        result = integrate(f.record, 'one', 'alice', publish=True)
        self.assertEqual(result['status'], 'tests-failed')
        self.assertEqual(git(f.repo, 'rev-parse', 'HEAD'), f.base)

    def test_native_fixed_parser_keeps_modes_exclusive(self):
        args = parse(['integrate', 'one', '--inspect', '--path', 'document.txt', '--as', 'alice'], 'alice')
        self.assertTrue(args.inspect)
        self.assertEqual(args.path, 'document.txt')
        with self.assertRaises(ValueError):
            parse(['integrate', 'one', '--inspect', '--as', 'bob'], 'alice')

    def test_bundle_pages_salvage_exact_unicode_binary_and_deleted_patch(self):
        import base64
        import hashlib
        import subprocess
        from scripts.salvage_conflict import salvage
        f = self.f
        room = f.candidate('one', '😀' * 40_000 + '\n')
        (room / 'binary.bin').write_bytes(bytes(range(256)) * 40)
        (room / 'gone.txt').write_text('new\n')
        self.amend(room)
        selected = ['document.txt', 'binary.bin', 'gone.txt']
        expected = subprocess.run(['git', '--literal-pathspecs', 'diff', '--no-ext-diff',
            '--no-textconv', '--no-renames', '--binary', '--full-index', '--no-color',
            f.base, git(room, 'rev-parse', 'HEAD'), '--', *selected], cwd=room,
            capture_output=True, check=True).stdout
        pages = []; chunks = []; offset = 0
        while True:
            page = inspect_contribution(f.record, 'one', 'alice', bundle=True,
                                        paths=selected, offset=offset)
            data = base64.b64decode(page['patch_base64'])
            self.assertLessEqual(len(data), INSPECTION_LIMIT)
            self.assertLessEqual(len(json.dumps(page, indent=2).encode()), INSPECTION_LIMIT)
            chunks.append(data)
            filename = f.repo / ('page-' + str(offset) + '.json')
            filename.write_text(json.dumps(page)); pages.append(filename)
            if not page['has_more']:
                break
            self.assertGreater(page['through'], offset); offset = page['through']
        self.assertGreater(len(pages), 1)
        self.assertEqual(b''.join(chunks), expected)
        patch = f.repo / 'saved.patch'
        result = salvage(pages, patch)
        self.assertEqual(patch.read_bytes(), expected)
        self.assertEqual(result['sha256'], hashlib.sha256(expected).hexdigest())
        recovery = f.repo / 'private-recovery'
        subprocess.run(['git', 'clone', '--quiet', '--shared', '--no-checkout', str(room),
                        str(recovery)], check=True, capture_output=True)
        git(recovery, 'checkout', '--detach', f.base)
        git(recovery, 'apply', '--check', str(patch))
        git(recovery, 'apply', str(patch))
        for name in selected:
            self.assertEqual((recovery / name).read_bytes(), (room / name).read_bytes())
        self.assertEqual((f.repo / 'document.txt').read_text(), 'base\n')
        self.assertEqual(git(f.repo, 'rev-parse', 'HEAD'), f.base)
        with self.assertRaises(FileExistsError):
            salvage(pages, patch)
        with self.assertRaises(ValueError):
            salvage(pages[1:], f.repo / 'bad.patch')
        self.assertFalse((f.repo / 'bad.patch').exists())
        corrupted = json.loads(pages[0].read_text()); corrupted['patch_sha256'] = '0' * 64
        pages[0].write_text(json.dumps(corrupted))
        with self.assertRaises(ValueError):
            salvage(pages, f.repo / 'bad.patch')
        self.assertFalse((f.repo / 'bad.patch').exists())

    def test_preview_conflict_and_clean_are_read_only_and_bound_to_heads(self):
        f = self.f
        room = f.candidate('one', 'candidate\n')
        clean = inspect_contribution(f.record, 'one', 'alice', preview=True)['preview']
        self.assertEqual(clean['status'], 'clean')
        (f.repo / 'document.txt').write_text('shared\n')
        git(f.repo, 'add', 'document.txt')
        git(f.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test',
            '-c', 'user.email=test@local', 'commit', '-m', 'Shared change')
        (f.repo / 'dirty.txt').write_text('keep me\n')
        def snapshot(repo):
            gitdir = repo / '.git'
            if gitdir.is_file():
                gitdir = __import__('pathlib').Path(git(repo, 'rev-parse', '--absolute-git-dir'))
            return {str(p.relative_to(gitdir)): p.read_bytes()
                    for p in gitdir.rglob('*') if p.is_file()}
        before = snapshot(f.repo), snapshot(room), f.record.read()[2]
        preview = inspect_contribution(f.record, 'one', 'alice', preview=True)['preview']
        self.assertEqual(preview['status'], 'conflict')
        self.assertEqual(preview['base'], f.base)
        self.assertEqual(preview['current'], git(f.repo, 'rev-parse', 'HEAD'))
        self.assertEqual(preview['contribution'], git(room, 'rev-parse', 'HEAD'))
        self.assertEqual(before, (snapshot(f.repo), snapshot(room), f.record.read()[2]))
        self.assertEqual((f.repo / 'dirty.txt').read_text(), 'keep me\n')
        self.assertFalse((f.private / 'one/integration.json').exists())

    def test_bundle_options_and_utf8_byte_boundary_are_explicit(self):
        import base64
        f = self.f
        room = f.candidate('one', '😀tail\n')
        first = inspect_contribution(f.record, 'one', 'alice', bundle=True)
        patch = base64.b64decode(first['patch_base64'])
        # Byte pages may begin inside a code point: base64 preserves it exactly.
        offset = patch.index('😀'.encode()) + 1
        page = inspect_contribution(f.record, 'one', 'alice', bundle=True, offset=offset)
        self.assertEqual(base64.b64decode(page['patch_base64']), patch[offset:])
        for options in ({'paths': ['document.txt']}, {'bundle': True, 'paths': []},
                        {'bundle': True, 'paths': ['../document.txt']},
                        {'bundle': True, 'offset': -1}, {'bundle': True, 'offset': len(patch)+1},
                        {'bundle': True, 'path': 'document.txt'}):
            with self.assertRaises(ValueError):
                inspect_contribution(f.record, 'one', 'alice', **options)
        args = parse(['integrate', 'one', '--inspect', '--bundle', '--paths',
                      'document.txt', '--offset', '0', '--preview', '--as', 'alice'], 'alice')
        self.assertTrue(args.bundle and args.preview)
        self.assertEqual(args.paths, ['document.txt'])


    def test_bundle_patch_preserves_deletion_and_executable_mode(self):
        import base64
        import subprocess
        f = self.f
        (f.repo / 'remove.txt').write_bytes(b'remove this\n')
        git(f.repo, 'add', 'remove.txt')
        git(f.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test',
            '-c', 'user.email=test@local', 'commit', '-m', 'Deletion base')
        f.base = git(f.repo, 'rev-parse', 'HEAD')
        room = f.candidate('one', 'first\n')
        (room / 'remove.txt').unlink()
        (room / 'document.txt').chmod(0o755)
        self.amend(room)
        page = inspect_contribution(f.record, 'one', 'alice', bundle=True)
        patch = base64.b64decode(page['patch_base64'])
        self.assertIn(b'deleted file mode 100644', patch)
        self.assertIn(b'new mode 100755', patch)
        self.assertIn(b'--- a/remove.txt', patch)
        self.assertIn(b'+++ /dev/null', patch)
        self.assertTrue((f.repo / 'remove.txt').exists())
        self.assertEqual((f.repo / 'document.txt').stat().st_mode & 0o111, 0)

    def test_fixed_channel_patch_export_is_private_retryable_and_never_applies(self):
        import hashlib
        from house.home_work import room as make_room
        from house.resident_actions import execute
        f = self.f
        candidate = f.candidate('one', 'candidate 😀\n')
        f.record.append('life', 'watch-keeper', {'kind': 'run-start', 'run': 'requester',
            'resident': 'request-reader', 'agent': 'codex', 'model': 'gpt-6.1-sol',
            'source_head': f.base, 'workspace': 'residents/requester',
            'policy_revision': 'fixture', 'mode': 'work'})
        f.record.append('arrive', 'request-reader', {'name': 'Reader'})
        f.record.append('life', 'watch-keeper', {'kind': 'run-launched', 'run': 'requester',
                                               'pgid': os.getpid()})
        requester = make_room(f.record, f.private, 'requester', f.base)
        argv = ['integrate', 'one', '--export-patch', '--paths', 'document.txt', '--as', 'request-reader']
        from house.mailbox_jobs import lane
        item = {'argv': argv, 'run': 'requester', 'resident': 'request-reader'}
        self.assertEqual(lane(f.record, item), 'worker')
        item['argv'] = ['integrate', 'one', '--inspect', '--bundle', '--preview',
                        '--as', 'request-reader']
        self.assertEqual(lane(f.record, item), 'inspection')
        before = f.record.read()[2], git(f.repo, 'rev-parse', 'HEAD')
        result = execute(f.record, requester, 'request-reader', 'requester', argv, 'export-one')
        patch = requester / result['path']
        self.assertEqual(hashlib.sha256(patch.read_bytes()).hexdigest(), result['patch_sha256'])
        self.assertEqual(execute(f.record, requester, 'request-reader', 'requester', argv, 'export-one'), result)
        self.assertEqual((requester / 'document.txt').read_text(), 'base\n')
        self.assertEqual((f.repo / 'document.txt').read_text(), 'base\n')
        self.assertEqual((candidate / 'document.txt').read_text(), 'candidate 😀\n')
        self.assertEqual(before, (f.record.read()[2], git(f.repo, 'rev-parse', 'HEAD')))
        with self.assertRaises(ValueError):
            execute(f.record, candidate, 'request-reader', 'requester', argv, 'wrong-room')
        patch.write_bytes(b'preserve existing altered patch')
        with self.assertRaises(ValueError):
            execute(f.record, requester, 'request-reader', 'requester', argv, 'changed-output')
        self.assertEqual(patch.read_bytes(), b'preserve existing altered patch')
        patch.unlink(); patch.symlink_to(requester / 'document.txt')
        with self.assertRaises(OSError):
            execute(f.record, requester, 'request-reader', 'requester', argv, 'symlink-output')
        self.assertEqual((requester / 'document.txt').read_text(), 'base\n')

    def test_preview_does_not_execute_candidate_merge_driver_and_fails_closed(self):
        import subprocess
        from unittest.mock import patch
        f = self.f
        (f.repo / '.gitattributes').write_text('document.txt merge=untrusted\n')
        git(f.repo, 'add', '.gitattributes')
        git(f.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test',
            '-c', 'user.email=test@local', 'commit', '-m', 'Merge attributes')
        f.base = git(f.repo, 'rev-parse', 'HEAD')
        candidate = f.candidate('one', 'candidate\n')
        marker = candidate / 'driver-was-executed'
        git(candidate, 'config', 'merge.untrusted.driver', 'touch ' + str(marker))
        (f.repo / 'document.txt').write_text('shared\n')
        git(f.repo, 'add', 'document.txt')
        git(f.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test',
            '-c', 'user.email=test@local', 'commit', '-m', 'Conflict')
        result = inspect_contribution(f.record, 'one', 'alice', preview=True)
        self.assertEqual(result['preview']['status'], 'conflict')
        self.assertIn('document.txt', result['preview']['output'])
        self.assertFalse(marker.exists())
        real_run = subprocess.run
        def unavailable(command, **kwargs):
            if 'merge-tree' in command:
                return subprocess.CompletedProcess(command, 129)
            return real_run(command, **kwargs)
        with patch('house.integrate.subprocess.run', side_effect=unavailable):
            with self.assertRaisesRegex(ValueError, 'preview unavailable'):
                inspect_contribution(f.record, 'one', 'alice', preview=True)
