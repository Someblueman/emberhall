"""Synthetic credentials only; native import never contacts a model."""
from contextlib import closing
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import zipfile
import tempfile
import traceback
import unittest
from unittest.mock import patch

from house.opencode_auth import bootstrap, source_database, _read_source


class OpenCodeAuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.reader = patch('house.opencode_auth._source_payload', side_effect=_read_source)
        self.reader.start(); self.addCleanup(self.reader.stop)
        self.root = Path(self.temp.name).resolve()
        self.private = self.root / 'private'; self.private.mkdir()
        self.source = self.root / 'source.db'
        self.db = sqlite3.connect(self.source)
        self.addCleanup(self.db.close)
        self.db.executescript('''CREATE TABLE credential(id TEXT PRIMARY KEY, integration_id TEXT,
            label TEXT, value TEXT, active INTEGER, time_created INTEGER, time_updated INTEGER);
            CREATE TABLE session(id TEXT, content TEXT);
            INSERT INTO session VALUES('unrelated','history must not transfer');''')
        self.env = dict(os.environ)
        for key in list(self.env):
            if key.startswith('OPENCODE_'):
                self.env.pop(key)
        for key in ('XDG_DATA_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME', 'XDG_CONFIG_HOME'):
            self.env[key] = str(self.private / key.lower())
        self.env.update(OPENCODE_DB=str(self.private / 'opencode.db'),
            OPENCODE_TEST_HOME=str(self.private / 'test-home'),
            OPENCODE_CONFIG_DIR=str(self.private / 'config'), OPENCODE_CONFIG_PROJECT_DISABLE='1',
            OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1', OPENCODE_DISABLE_MODELS_FETCH='1',
            OPENCODE_CONFIG_CONTENT=json.dumps({'warming': False, 'policies': [
                {'action': 'plugin.use', 'resource': '*', 'effect': 'deny'}]}))

    def row(self, identifier, active=None, created=1, integration='opencode-go', value=None):
        self.db.execute('INSERT INTO credential VALUES(?,?,?,?,?,?,?)',
            (identifier, integration, 'private source label', json.dumps(value or
             {'type': 'key', 'key': 'synthetic-' + identifier}), active, created, created))
        self.db.commit()

    def capture(self, *args, **kwargs):
        self.assertEqual(args[0], ['/fake/opencode', 'auth', 'import', '--standalone'])
        self.assertEqual(kwargs['stdout'], subprocess.DEVNULL)
        self.assertEqual(kwargs['stderr'], subprocess.DEVNULL)
        self.assertEqual(kwargs['timeout'], 60)
        self.payload = json.loads(kwargs['input'])
        Path(self.env['OPENCODE_DB']).touch()

    def test_source_resolution_matches_stable_v2(self):
        self.assertEqual(source_database({'HOME': '/home/example'}), Path('/home/example/.local/share/opencode/opencode.db'))
        self.assertEqual(source_database({'XDG_DATA_HOME': '/data', 'OPENCODE_DB': 'other.db'}), Path('/data/opencode/other.db'))
        self.assertEqual(source_database({'OPENCODE_DB': '/absolute/database'}), Path('/absolute/database'))
        with self.assertRaises(ValueError): source_database({'OPENCODE_DB': ':memory:'})

    def test_wal_native_selection_excludes_other_accounts_and_history(self):
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA wal_autocheckpoint=0')
        self.row('newer-inactive', 0, 20)
        self.row('selected', 1, 2)
        self.row('unrelated-secret', 1, 99, 'another-provider')
        with patch('house.opencode_auth.subprocess.run', side_effect=self.capture):
            bootstrap('/fake/opencode', self.source, self.private, self.env)
        self.assertEqual(len(self.payload), 1)
        self.assertEqual(self.payload[0]['id'], 'selected')
        self.assertEqual(self.payload[0]['value']['key'], 'synthetic-selected')
        self.assertTrue(self.payload[0]['active'])
        self.assertNotIn('private source label', json.dumps(self.payload))
        self.assertEqual(self.db.execute('SELECT count(*) FROM session').fetchone()[0], 1)

    def test_null_active_uses_native_time_then_id_order(self):
        self.row('a', created=5); self.row('z', created=5); self.row('newest', created=6)
        with patch('house.opencode_auth.subprocess.run', side_effect=self.capture):
            bootstrap('/fake/opencode', self.source, self.private, self.env)
        self.assertEqual(self.payload[0]['id'], 'newest')

    def test_existing_or_symlink_destination_and_nonempty_data_fail_before_import(self):
        self.row('selected', 1)
        target = Path(self.env['OPENCODE_DB'])
        for kind in ('file', 'symlink', 'legacy'):
            with self.subTest(kind=kind), patch('house.opencode_auth.subprocess.run') as run:
                if kind == 'file': target.touch()
                elif kind == 'symlink': target.symlink_to(self.source)
                else:
                    data = Path(self.env['XDG_DATA_HOME']); data.mkdir(exist_ok=True)
                    (data / 'auth.json').write_text('synthetic stale data')
                with self.assertRaisesRegex(ValueError, 'no model started'):
                    bootstrap('/fake/opencode', self.source, self.private, self.env)
                run.assert_not_called()
                if kind != 'legacy': target.unlink()

    def test_missing_malformed_unsupported_and_native_errors_are_sanitized(self):
        cases = [None, 'malformed synthetic-secret', json.dumps({'type': 'oauth', 'access': 'synthetic-secret'}),
                 json.dumps({'type': 'external', 'methodID': 'synthetic-secret'})]
        for value in cases:
            self.db.execute('DELETE FROM credential')
            if value is not None:
                self.db.execute('INSERT INTO credential VALUES(?,?,?,?,?,?,?)', ('c', 'opencode-go', '', value, 1, 1, 1))
            self.db.commit()
            with patch('house.opencode_auth.subprocess.run') as run:
                with self.assertRaises(ValueError) as raised:
                    bootstrap('/fake/opencode', self.source, self.private, self.env)
                self.assertIsNone(raised.exception.__context__)
                self.assertNotIn('synthetic-secret', ''.join(traceback.format_exception(raised.exception)))
                run.assert_not_called()
        self.db.execute('DELETE FROM credential'); self.db.commit(); self.row('selected', 1)
        with patch('house.opencode_auth.subprocess.run', side_effect=subprocess.TimeoutExpired('synthetic-secret', 60)):
            with self.assertRaises(ValueError) as raised:
                bootstrap('/fake/opencode', self.source, self.private, self.env)
            self.assertIsNone(raised.exception.__context__)

    def test_missing_source_or_wrong_schema_never_calls_native_import(self):
        for source in (self.root / 'missing.db', self.root / 'wrong.db'):
            if source.name == 'wrong.db':
                with closing(sqlite3.connect(source)) as db:
                    db.execute('CREATE TABLE credential(unexpected TEXT)')
            with self.subTest(source=source.name), patch('house.opencode_auth.subprocess.run') as run:
                with self.assertRaises(ValueError) as raised:
                    bootstrap('/fake/opencode', source, self.private, self.env)
                self.assertIsNone(raised.exception.__context__)
                run.assert_not_called()

    @unittest.skipUnless(os.environ.get('EMBERHALL_NATIVE_OPENCODE') == '1'
                         and not os.environ.get('EMBERHALL_CANDIDATE_SANDBOX'), 'opt-in installed no-model import')
    def test_native_import_contains_only_selected_synthetic_key(self):
        self.reader.stop()
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA wal_autocheckpoint=0')
        self.row('cred_selected', 1)
        self.row('cred_unrelated', 1, 99, 'another-provider')
        before = self.source.read_bytes()
        supplied_runtime = os.environ.get('EMBERHALL_OPENCODE_PINNED_RUNTIME')
        runtime = Path(supplied_runtime) if supplied_runtime else self.root / 'pinned.pyz'
        if not supplied_runtime:
            with zipfile.ZipFile(runtime, 'w') as archive:
                for module in (Path(__file__).resolve().parents[1] / 'house').glob('*.py'):
                    archive.writestr('house/' + module.name, module.read_bytes())
        self.assertTrue(runtime.is_file())
        room = self.root / 'room'; room.mkdir()
        (self.private / 'prompt.txt').write_text('Never submitted')
        code = ('import sys,os;sys.path.insert(0,sys.argv[1]);from pathlib import Path;'
                'from house.providers import command,DEFAULTS;from house.opencode_auth import bootstrap;'
                'runtime,source,private,room=map(Path,sys.argv[1:]);'
                'argv,env=command("opencode",DEFAULTS["opencode"],room,private,room/".house-client",'
                'runtime=runtime,resident="synthetic-import");'
                'env["OPENCODE_DISABLE_MODELS_FETCH"]="1";os.environ.clear();os.environ.update(env);'
                'bootstrap(argv[0],source,private,env)')
        outcome = subprocess.run([sys.executable, '-I', '-c', code, str(runtime), str(self.source),
            str(self.private), str(room)], capture_output=True, text=True, timeout=80)
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        with closing(sqlite3.connect(self.env['OPENCODE_DB'])) as destination:
            rows = destination.execute('SELECT id,integration_id,active,value FROM credential').fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][:3], ('cred_selected', 'opencode-go', 1))
            self.assertEqual(json.loads(rows[0][3])['key'], 'synthetic-cred_selected')
            tables = destination.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%session%'").fetchall()
            for (name,) in tables:
                quoted = '"' + name.replace('"', '""') + '"'
                self.assertEqual(destination.execute('SELECT count(*) FROM ' + quoted).fetchone()[0], 0, name)
        self.assertEqual(self.source.read_bytes(), before)

    @unittest.skipUnless(os.environ.get('EMBERHALL_NATIVE_OPENCODE') == '1'
                         and not os.environ.get('EMBERHALL_CANDIDATE_SANDBOX'), 'host sandbox boundary')
    def test_os_reader_reads_live_wal_but_never_creates_cold_sidecars(self):
        self.reader.stop()
        # Import after stopping the patch, so this is the actual sandbox child.
        from house.opencode_auth import _source_payload
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA wal_autocheckpoint=0')
        self.row('wal_selected', 1)
        selected = json.loads(_source_payload(self.source))
        self.assertEqual(selected[0]['id'], 'wal_selected')
        self.db.close()
        before = sorted(p.name for p in self.root.iterdir())
        with self.assertRaises(ValueError):
            bootstrap('/unused', self.source, self.private, self.env)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), before)
        self.assertFalse(Path(str(self.source) + '-wal').exists())
        self.assertFalse(Path(str(self.source) + '-shm').exists())

    @unittest.skipUnless(os.environ.get('EMBERHALL_NATIVE_OPENCODE') == '1'
                         and not os.environ.get('EMBERHALL_CANDIDATE_SANDBOX'), 'host sandbox contention witness')
    def test_exclusive_live_wal_failure_keeps_destination_empty(self):
        self.reader.stop()
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA locking_mode=EXCLUSIVE')
        self.row('cred_locked_synthetic', 1)
        native_run = subprocess.run
        with patch('house.opencode_auth.subprocess.run', wraps=native_run) as calls:
            with self.assertRaisesRegex(ValueError, '^OpenCode account bootstrap failed; no model started$'):
                bootstrap('/unused-native-importer', self.source, self.private, self.env)
        self.assertEqual(calls.call_count, 1)
        self.assertEqual(calls.call_args.args[0][0], '/usr/bin/sandbox-exec')
        self.assertFalse(Path(self.env['OPENCODE_DB']).exists())
        self.assertFalse(any(Path(self.env['XDG_DATA_HOME']).iterdir()))
