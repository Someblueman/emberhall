"""Focused filesystem, input and real Git/CLI tests; no house runtime needed."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import check_handoff as checker

CLI = Path(checker.__file__).resolve()


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / 'workspace'
        self.workspace.mkdir()
        self.claim_file = self.root / 'claims.json'
        (self.workspace / 'note.txt').write_bytes(b'ember\n')

    def claims(self, *entries):
        return checker.validate_claims({'version': 1, 'artifacts': list(entries)})

    def cli(self, *entries, env=None):
        self.claim_file.write_text(json.dumps({'version': 1, 'artifacts': list(entries)}))
        result = subprocess.run([sys.executable, '-B', str(CLI), str(self.workspace),
                                 str(self.claim_file)], capture_output=True, text=True,
                                timeout=10, env=env)
        return result, json.loads(result.stdout or result.stderr)

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.workspace), *args], check=True,
                              capture_output=True).stdout

    def init_git(self):
        if not shutil.which('git'):
            self.skipTest('Git not installed')
        self.git('init', '-q')
        self.git('add', '--', 'note.txt')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null',
                 'commit', '-qm', 'fixture')

    def test_exact_bytes_and_hash_without_git(self):
        result, report = self.cli({'path': 'note.txt', 'bytes': 6,
                                  'sha256': hashlib.sha256(b'ember\n').hexdigest()})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(report['ok'])
        self.assertFalse(report['git_available'])
        self.assertEqual(report['artifacts'][0]['git'], 'unavailable')
        self.assertIn('Git', report['artifacts'][0]['git_reason'])

    def test_mismatches_and_missing_file_are_exit_one(self):
        result, report = self.cli({'path': 'note.txt', 'bytes': 3, 'sha256': '0' * 64},
                                  {'path': 'missing'})
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(report['artifacts'][0]['errors']), 2)
        self.assertIn('file unavailable', report['artifacts'][1]['errors'][0])

    def test_unavailable_git_cannot_satisfy_either_state(self):
        for state in ('clean', 'dirty'):
            with self.subTest(state=state):
                result, report = self.cli({'path': 'note.txt', 'git': state})
                self.assertEqual(result.returncode, 1)
                self.assertIn('observed unavailable', report['artifacts'][0]['errors'][0])

    def test_git_executable_missing_is_honest(self):
        env = dict(os.environ, PATH='')
        result, report = self.cli({'path': 'note.txt', 'git': 'clean'}, env=env)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(report['git_available'])

    def test_malformed_claims(self):
        invalid = [None, {}, {'version': True, 'artifacts': [{'path': 'note.txt'}]},
                   {'version': 1, 'artifacts': []},
                   {'version': 1, 'artifacts': [{'path': 'note.txt'}], 'typo': 1}]
        entries = [{'path': 'note.txt', 'bytes': v} for v in (-1, True, 1.5, '6', None)]
        entries += [{'path': 'note.txt', 'sha256': v} for v in ('x', 'A' * 64, 9, None)]
        entries += [{'path': 'note.txt', 'git': v} for v in ('staged', None, [], {})]
        entries += [{'bytes': 6}, {'path': 'note.txt', 'size': 6}, 'note.txt']
        invalid += [{'version': 1, 'artifacts': [entry]} for entry in entries]
        invalid.append({'version': 1, 'artifacts': [{'path': 'a'}, {'path': 'a'}]})
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(checker.ClaimError):
                checker.validate_claims(value)

    def test_bad_paths_are_rejected_before_checks(self):
        for path in ('', '/note.txt', '../note.txt', 'a/../b', './note.txt', 'a//b',
                     'a/', 'C:/x', 'a\\b', 'a\0b', 'a\nb', '.git/config', '.GIT/index',
                     'nested/.git/config'):
            with self.subTest(path=path), self.assertRaises(checker.ClaimError):
                self.claims({'path': path})

    def test_bad_json_duplicate_keys_and_encoding_exit_two(self):
        for raw in (b'{', b'\xff', b'{"version":1,"version":1,"artifacts":[{"path":"note.txt"}]}',
                    b'{"version":1,"artifacts":[{"path":"note.txt","path":"other"}]}'):
            self.claim_file.write_bytes(raw)
            result = subprocess.run([sys.executable, '-B', str(CLI), str(self.workspace),
                                     str(self.claim_file)], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('error', json.loads(result.stderr))
            self.assertFalse(result.stdout)

    def test_symlinks_and_nonregular_artifacts_fail_without_hanging(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (outside / 'secret').write_bytes(b'private')
        (self.workspace / 'link').symlink_to(outside / 'secret')
        (self.workspace / 'parent').symlink_to(outside, target_is_directory=True)
        (self.workspace / 'directory').mkdir()
        os.mkfifo(self.workspace / 'pipe')
        for path in ('link', 'parent/secret', 'directory', 'pipe', 'note.txt/child'):
            with self.subTest(path=path):
                result, report = self.cli({'path': path})
                self.assertEqual(result.returncode, 1)
                self.assertNotIn('sha256', report['artifacts'][0])

    def test_nonregular_claim_input_is_rejected_without_hanging(self):
        for kind in ('symlink', 'fifo', 'directory'):
            path = self.root / kind
            if kind == 'symlink':
                path.symlink_to(self.workspace / 'note.txt')
            elif kind == 'fifo':
                os.mkfifo(path)
            else:
                path.mkdir()
            result = subprocess.run([sys.executable, '-B', str(CLI), str(self.workspace),
                                     str(path)], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 2, result.stderr)

    def test_file_changed_while_hashing_is_rejected(self):
        original_read = os.read
        def change_after_read(fd, size):
            chunk = original_read(fd, size)
            if chunk:
                (self.workspace / 'note.txt').write_bytes(b'changed')
            return chunk
        with patch.object(checker.os, 'read', side_effect=change_after_read):
            report = checker.check(self.workspace, self.claims({'path': 'note.txt'}))
        self.assertFalse(report['ok'])
        self.assertIn('changed', report['artifacts'][0]['errors'][0])

    def test_clean_staged_unstaged_untracked_ignored_and_renamed(self):
        self.init_git()
        self.assertEqual(self.cli({'path': 'note.txt', 'git': 'clean'})[0].returncode, 0)
        (self.workspace / 'note.txt').write_bytes(b'changed')
        self.assertEqual(self.cli({'path': 'note.txt', 'git': 'dirty'})[0].returncode, 0)
        self.assertEqual(self.cli({'path': 'note.txt', 'git': 'clean'})[0].returncode, 1)
        self.git('add', '--', 'note.txt')
        self.assertEqual(self.cli({'path': 'note.txt', 'git': 'dirty'})[0].returncode, 0)
        (self.workspace / '.gitignore').write_text('ignored\n')
        for name in ('new', 'ignored'):
            (self.workspace / name).write_bytes(b'x')
            self.assertEqual(self.cli({'path': name, 'git': 'dirty'})[0].returncode, 0)
            self.assertEqual(self.cli({'path': name, 'git': 'clean'})[0].returncode, 1)
        self.git('mv', 'note.txt', 'renamed.txt')
        result, report = self.cli({'path': 'renamed.txt', 'git': 'dirty'},
                                  {'path': 'note.txt', 'git': 'dirty'})
        self.assertEqual(result.returncode, 1)
        self.assertTrue(report['artifacts'][0]['ok'])
        self.assertFalse(report['artifacts'][1]['ok'])

    def test_literal_path_boundaries_do_not_include_neighbor_changes(self):
        self.init_git()
        names = ('star*.txt', 'bracket[1].txt', '-leading', 'space and ü.txt')
        for name in names:
            (self.workspace / name).write_bytes(b'own')
        self.git('--literal-pathspecs', 'add', '--', *names)
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null',
                 'commit', '-qm', 'literal paths')
        for name in ('star-other.txt', 'bracket1.txt', 'unrelated'):
            (self.workspace / name).write_bytes(b'dirty')
        result, report = self.cli(*({'path': name, 'git': 'clean'} for name in names))
        self.assertEqual(result.returncode, 0, report)

    def test_cli_preserves_index_refs_worktree_and_claims(self):
        self.init_git()
        (self.workspace / 'note.txt').write_bytes(b'dirty')
        self.claim_file.write_text(json.dumps({'version': 1, 'artifacts': [
            {'path': 'note.txt', 'git': 'dirty'}]}))
        def snapshot():
            return {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mtime_ns)
                    for p in self.root.rglob('*') if p.is_file()}
        before = snapshot()
        result = subprocess.run([sys.executable, '-B', str(CLI), str(self.workspace),
                                 str(self.claim_file)], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(), before)

    def test_subdirectory_is_not_silently_treated_as_git_root(self):
        self.init_git()
        folder = self.workspace / 'nested'
        folder.mkdir()
        (folder / 'x').write_bytes(b'x')
        report = checker.check(folder, self.claims({'path': 'x', 'git': 'dirty'}))
        self.assertFalse(report['ok'])
        self.assertIn('Git top-level', report['artifacts'][0]['git_reason'])

    def test_inherited_git_overrides_are_ignored(self):
        self.init_git()
        env = dict(os.environ, GIT_DIR=str(self.root / 'absent'),
                   GIT_WORK_TREE=str(self.root), GIT_INDEX_FILE=str(self.root / 'bad-index'))
        result, report = self.cli({'path': 'note.txt', 'git': 'clean'}, env=env)
        self.assertEqual(result.returncode, 0, report)
        self.assertFalse((self.root / 'bad-index').exists())


if __name__ == '__main__':
    unittest.main()
