"""Real CLI round-trips and focused publication failure boundaries."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from sow_ledger import main, write_report


ROOT = Path(__file__).resolve().parent
CLI = ROOT / 'sow_ledger.py'


class CliTests(unittest.TestCase):
    def setUp(self):
        self.room = tempfile.TemporaryDirectory()
        self.addCleanup(self.room.cleanup)
        self.root = Path(self.room.name)
        self.source = self.root / 'seeds.md'
        self.source.write_bytes((ROOT / 'example.md').read_bytes())
        self.output = self.root / 'report.json'

    def run_cli(self, *extra):
        return subprocess.run([sys.executable, '-B', str(CLI), str(self.source),
                               '--as-of', '2026-11-15', '--output', str(self.output), *extra],
                              capture_output=True, timeout=10)

    def test_worked_example_repeat_bytes_and_atomic_replacement(self):
        self.output.write_bytes(b'old report')
        first = self.run_cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, b'')
        raw = self.output.read_bytes()
        parsed = json.loads(raw)
        self.assertEqual(parsed['as_of'], '2026-11-15')
        self.assertEqual([r['variety'] for r in parsed['entries']],
                         ['Garden pea', 'Lettuce mix', 'Mystery marigold', 'Red onion'])
        self.assertEqual(parsed['entries'][1]['sow_by'], '2027-12-31')
        self.assertEqual(parsed['entries'][2]['germination'], None)
        self.assertEqual(self.run_cli().returncode, 0)
        self.assertEqual(self.output.read_bytes(), raw)
        self.assertEqual(list(self.root.glob('.sow-ledger-*')), [])

    def test_bad_input_and_dates_preserve_output(self):
        original = self.source.read_bytes()
        for bad in [b'invalid', b'\xff', original + b'| bad |\n', b'x' * 1_000_001]:
            with self.subTest(bad=bad[:20]):
                self.source.write_bytes(bad)
                self.output.write_bytes(b'keep me')
                run = self.run_cli()
                self.assertEqual(run.returncode, 2, run.stderr)
                self.assertEqual(self.output.read_bytes(), b'keep me')
                self.assertEqual(list(self.root.glob('.sow-ledger-*')), [])
        self.source.write_bytes(original)
        for invalid_date in ['2026-02-29', '20261115']:
            self.assertEqual(self.run_cli('--as-of', invalid_date).returncode, 2)
            self.assertEqual(self.output.read_bytes(), b'keep me')

    def test_requires_explicit_date_and_output(self):
        for args in [[], ['--as-of', '2026-11-15'], ['--output', str(self.output)]]:
            run = subprocess.run([sys.executable, '-B', str(CLI), str(self.source), *args],
                                 capture_output=True, timeout=10)
            self.assertEqual(run.returncode, 2)
        self.assertFalse(self.output.exists())

    def test_cannot_overwrite_input_or_its_hardlink(self):
        original = self.source.read_bytes()
        self.output = self.source
        self.assertEqual(self.run_cli().returncode, 2)
        self.output = self.root / 'alias.md'
        os.link(self.source, self.output)
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertEqual(self.source.read_bytes(), original)

    def test_output_symlink_directory_and_missing_parent_fail(self):
        self.output.symlink_to(self.source)
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertTrue(self.output.is_symlink())
        self.output.unlink()
        self.output.mkdir()
        self.assertEqual(self.run_cli().returncode, 2)
        self.output = self.root / 'missing' / 'report.json'
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertFalse(self.output.parent.exists())

    @unittest.skipUnless(os.name == 'posix', 'POSIX special-file probe')
    def test_fifo_and_symlink_input_rejected_without_blocking(self):
        self.source.unlink()
        os.mkfifo(self.source)
        self.assertEqual(self.run_cli().returncode, 2)
        self.source.unlink()
        self.source.symlink_to(ROOT / 'example.md')
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertFalse(self.output.exists())

    def test_atomic_write_failures_preserve_old_file_and_clean_temp(self):
        for boundary in ['sow_ledger.os.fsync', 'sow_ledger.os.replace']:
            with self.subTest(boundary=boundary):
                self.output.write_bytes(b'keep me')
                with patch(boundary, side_effect=OSError('injected write failure')):
                    with self.assertRaises(OSError):
                        write_report(self.output, b'new report')
                self.assertEqual(self.output.read_bytes(), b'keep me')
                self.assertEqual(list(self.root.glob('.sow-ledger-*')), [])

    def test_cli_reports_replace_failure(self):
        self.output.write_bytes(b'keep me')
        with patch('sow_ledger.os.replace', side_effect=OSError('injected replace failure')):
            self.assertEqual(main([str(self.source), '--as-of', '2026-11-15',
                                   '--output', str(self.output)]), 2)
        self.assertEqual(self.output.read_bytes(), b'keep me')


if __name__ == '__main__':
    unittest.main()
