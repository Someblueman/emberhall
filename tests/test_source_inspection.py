"""Real committed-source inspection, refusal, and proportionate project acceptance."""
import fcntl
import json
import os
import unittest

from house.home_work import contribution, git
from house.integrate import check_plan, inspect_contribution, integrate, INSPECTION_LIMIT
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
