"""Reuse one existing OpenCode Go key in a fresh, private V2 database.

Only the already-gated resident process calls this; it never runs in the
coordinator or against the source through OpenCode's mutable native services.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys


def source_database(env: dict) -> Path:
    """Resolve the standard installed V2 release database before env isolation."""
    home = Path(env.get('HOME') or Path.home())
    data = Path(env.get('XDG_DATA_HOME') or home / '.local/share') / 'opencode'
    filename = env.get('OPENCODE_DB', 'opencode.db')
    if not isinstance(filename, str) or not filename or filename == ':memory:':
        raise ValueError('OpenCode source must be a persistent database')
    return Path(os.path.abspath(data / filename))


def bootstrap(executable: str, source: Path, private: Path, env: dict) -> None:
    """Import one selected key using stdin; every failure is secret-free.

    No exception from SQLite/JSON/native execution escapes or becomes the
    sanitized exception's cause/context. Never print or persist the payload.
    """
    failed = False
    try:
        _bootstrap(executable, source, private, env)
    except Exception:
        failed = True
    if failed:
        raise ValueError('OpenCode account bootstrap failed; no model started')


def _bootstrap(executable: str, source: Path, private: Path, env: dict) -> None:
    private = private.resolve(strict=True)
    target = private / 'opencode.db'
    if env.get('OPENCODE_DB') != str(target):
        raise ValueError('destination')
    for suffix in ('', '-wal', '-shm', '-journal'):
        candidate = Path(str(target) + suffix)
        if candidate.exists() or candidate.is_symlink():
            raise ValueError('destination exists')
    data = Path(env['XDG_DATA_HOME'])
    if not data.is_absolute() or not data.is_relative_to(private) or data == private:
        raise ValueError('data root')
    # Reject symlink parents too: an empty directory outside the task is unsafe.
    for component in (data, *data.parents):
        if component == private:
            break
        if component.is_symlink():
            raise ValueError('data symlink')
    data.mkdir(parents=True, exist_ok=True)
    if any(data.iterdir()):
        raise ValueError('data not empty')
    source = source.resolve(strict=True)
    if source == target or not source.is_file():
        raise ValueError('source')
    payload = _source_payload(source)
    # Keep the import in the already-gated resident's process group. Its private
    # standalone child is leased by stdin; no background global service is used.
    subprocess.run([executable, 'auth', 'import', '--standalone'], input=payload,
        env=env, cwd=private, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        timeout=60, check=True)
    if not target.is_file() or target.is_symlink():
        raise ValueError('missing imported database')


def _source_payload(source: Path) -> bytes:
    # SQLite mode=ro can create WAL/SHM files. The source query therefore also
    # has an OS-enforced no-write/no-network boundary, with no fallback.
    package_root = str(Path(__file__).parent.parent)
    code = ('import sys;sys.dont_write_bytecode=True;sys.path.insert(0,' + repr(package_root) + ');'
            'from pathlib import Path;from house.opencode_auth import _read_source;'
            'sys.stdout.buffer.write(_read_source(Path(sys.argv[1])))')
    result = subprocess.run(['/usr/bin/sandbox-exec', '-p',
        '(version 1)(allow default)(deny file-write*)(deny network*)',
        str(Path(sys.executable).resolve()), '-I', '-c', code, str(source)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=10, check=True)
    if not result.stdout or len(result.stdout) > 2_000_000:
        raise ValueError('source payload')
    return result.stdout


def _read_source(source: Path) -> bytes:
    """Trusted child only: the parent captures this result, never logs it."""
    # A read-only connection observes live WAL commits; immutable=1 would not.
    connection = sqlite3.connect(source.as_uri() + '?mode=ro', uri=True, timeout=5)
    try:
        connection.execute('PRAGMA query_only=ON')
        row = connection.execute('''SELECT id,
            CASE WHEN length(value) <= 262144 THEN value ELSE NULL END
            FROM credential WHERE integration_id = 'opencode-go'
            ORDER BY active DESC, time_created DESC, id DESC LIMIT 1''').fetchone()
    finally:
        connection.close()
    if not row or not isinstance(row[0], str) or not 1 <= len(row[0]) <= 256 or not isinstance(row[1], str):
        raise ValueError('selected credential')
    value = json.loads(row[1])
    if (not isinstance(value, dict) or value.get('type') != 'key'
            or set(value) - {'type', 'key', 'metadata', 'configuration'}
            or not isinstance(value.get('key'), str) or not 1 <= len(value['key']) <= 65536):
        raise ValueError('unsupported credential')
    for name in ('metadata', 'configuration'):
        if name in value and not isinstance(value[name], dict):
            raise ValueError('credential metadata')
    return json.dumps([{'id': row[0], 'integrationID': 'opencode-go',
        'label': 'Emberhall existing OpenCode Go account', 'active': True, 'value': value}],
        allow_nan=False).encode()
