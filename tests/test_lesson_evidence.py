"""Empty-room replay and client-local lesson fetch boundaries."""
import copy
import json
import subprocess
import sys

from house import mailbox
from house.__main__ import parser, run
from house.lesson_evidence import read, save
from tests.support import HouseCase
from tests.test_lesson_artifacts import envelope
from tests.test_mailbox import MailboxCase


class LessonReaderTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record.append("learn", "alice", {"lesson": "proof", "key": "answer",
            "claim": "The answer is 42", "evidence": "Run check.py", "artifacts": {
                "check.py": envelope(), "notes.txt": envelope(b'notes')}})
        self.empty = self.root / "empty"
        self.empty.mkdir()

    def response(self):
        return read(self.record.read()[0], "proof", "bob", "check.py")

    def test_one_lesson_metadata_and_one_file_only(self):
        state = self.record.read()[0]
        meta = read(state, "proof", "bob")
        self.assertNotIn("artifact", meta)
        self.assertEqual(len(meta["artifacts"]), 2)
        self.assertNotIn("base64", json.dumps(meta))
        response = self.response()
        self.assertEqual(response["artifact"], {"name": "check.py", **envelope()})
        with self.assertRaisesRegex(ValueError, "no evidence file"):
            read(state, "proof", "bob", "missing")
        with self.assertRaisesRegex(ValueError, "unknown resident"):
            read(state, "proof", "stranger")

    def test_second_resident_fetches_runs_and_reviews_in_empty_room(self):
        process = subprocess.run([sys.executable, '-m', 'house', '--repo', str(self.repo),
            '--artifacts-from', str(self.empty), 'lesson', 'proof', '--as', 'bob',
            '--artifact', 'check.py', '--output', 'fetched.py'], capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        result = json.loads(process.stdout)
        self.assertNotIn("artifact", result)
        actual = subprocess.run([sys.executable, str(self.empty / 'fetched.py')],
                                capture_output=True, text=True, check=True)
        self.assertEqual(actual.stdout, '42\n')
        self.record.append('review', 'bob', {'lesson': 'proof', 'evidence': 'Fetched checker printed 42'})
        self.assertEqual(self.record.read()[0]['lessons']['proof']['reviews'], ['bob'])

    def test_dispatch_never_writes_coordinator_output(self):
        args = parser().parse_args(['--repo', str(self.repo), 'lesson', 'proof', '--as', 'bob',
                                  '--artifact', 'check.py', '--output', 'never-written.py'])
        self.assertIn('artifact', run(args))
        self.assertFalse((self.repo / 'never-written.py').exists())
        for flags in [['--artifact', 'check.py'], ['--output', 'x']]:
            args = parser().parse_args(['--repo', str(self.repo), 'lesson', 'proof', '--as', 'bob', *flags])
            with self.assertRaisesRegex(ValueError, 'both'):
                run(args)

    def test_output_cannot_escape_follow_links_or_overwrite(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.empty / 'linked').symlink_to(outside, target_is_directory=True)
        (self.empty / 'existing').write_text('keep')
        (self.empty / 'filelink').symlink_to(self.empty / 'existing')
        for path in ['../escape', '/absolute', 'a//b', './x', 'a\\b', 'linked/stolen', 'existing', 'filelink']:
            with self.subTest(path=path), self.assertRaises((ValueError, OSError)):
                save(self.response(), self.empty, path)
        self.assertEqual((self.empty / 'existing').read_text(), 'keep')
        self.assertEqual(list(outside.iterdir()), [])

    def test_invalid_transport_payload_does_not_create_file(self):
        for change in [{'sha256': '0' * 64}, {'base64': '!'}, {'base64': 'x' * 1333337}]:
            response = copy.deepcopy(self.response())
            response['artifact'].update(change)
            with self.assertRaises(ValueError):
                save(response, self.empty, 'bad.py')
            self.assertFalse((self.empty / 'bad.py').exists())

    def test_malformed_transport_schema_is_rejected_before_write(self):
        for response in [{}, {'artifact': []}, {'artifact': {'name': 'x'}},
                         {'artifact': {'name': [], **envelope()}}]:
            with self.assertRaises(ValueError):
                save(response, self.empty, 'bad.py')
            self.assertFalse((self.empty / 'bad.py').exists())

    def test_text_only_lesson_and_supersession_are_visible(self):
        self.record.append('learn', 'alice', {'lesson': 'new', 'key': 'answer', 'claim': '42', 'evidence': 'text'})
        self.record.append('supersede', 'alice', {'old': 'proof', 'new': 'new', 'evidence': 'Correction'})
        meta = read(self.record.read()[0], 'proof', 'bob')
        self.assertEqual(meta['replaced_by'], 'new')
        self.assertEqual(meta['status'], 'superseded')
        self.assertEqual(read(self.record.read()[0], 'new', 'bob')['artifacts'], {})


class LessonMailboxTests(MailboxCase):
    def test_mailbox_fetch_saves_only_in_client_room_then_checker_runs(self):
        self.arrive()
        self.record.append('learn', 'alice', {'lesson': 'proof', 'key': 'answer', 'claim': '42',
            'evidence': 'Run checker', 'artifacts': {'check.py': envelope()}})
        meta = self.call('lesson', 'proof', '--as', self.resident)
        self.assertNotIn('base64', json.dumps(meta))
        head = self.record.read()[2]
        result = self.call('lesson', 'proof', '--as', self.resident,
                           '--artifact', 'check.py', '--output', 'fetched.py')
        self.assertEqual(result['saved']['sha256'], envelope()['sha256'])
        self.assertFalse((self.repo / 'fetched.py').exists())
        self.assertEqual((self.workspace / 'fetched.py').read_bytes(), b'print(6 * 7)\n')
        self.assertEqual(self.record.read()[2], head, 'fetch is not a journal mutation')
        actual = subprocess.run([sys.executable, str(self.workspace / 'fetched.py')],
                                capture_output=True, text=True, check=True)
        self.assertEqual(actual.stdout, '42\n')
        self.call('review', 'proof', '--as', self.resident, '--evidence', 'Fetched checker printed 42')
        self.assertIn(self.resident, self.record.read()[0]['lessons']['proof']['reviews'])

    def test_learning_uses_private_source_and_replay_keeps_original_copy(self):
        self.arrive()
        (self.workspace / 'source.txt').write_bytes(b'print(6 * 7)\n')
        argv = ['learn', '--as', self.resident, '--request', 'attached-proof',
                '--lesson', 'proof', '--key', 'answer', '--claim', '42',
                '--evidence', 'Run checker', '--artifact', 'source.txt']
        first = self.call(*argv)
        key = mailbox.alias_id('attached-proof')
        (self.responses / (key + '.json')).unlink()
        saved = self.private / self.run / 'mailbox' / (key + '.json')
        metadata = json.loads(saved.read_text())
        metadata.pop('response')
        saved.write_text(json.dumps(metadata))
        (self.workspace / 'source.txt').write_text('changed')
        self.assertEqual(self.call(*argv)['sequence'], first['sequence'])
        self.assertEqual(self.record.read()[0]['lessons']['proof']['artifacts']['source.txt'], envelope())
        self.assertEqual((self.repo / 'source.txt').read_text(), 'base\n')

    def test_mailbox_output_never_writes_coordinator_even_with_absolute_name(self):
        self.arrive()
        self.record.append('learn', 'alice', {'lesson': 'proof', 'key': 'answer', 'claim': '42',
            'evidence': 'Run checker', 'artifacts': {'check.py': envelope()}})
        target = self.repo / 'must-not-exist.py'
        process = self.start('lesson', 'proof', '--as', self.resident, '--artifact', 'check.py',
                             '--output', str(target))
        self.collect(process, success=False)
        self.assertFalse(target.exists())
