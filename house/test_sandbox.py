"""Run candidate tests with room-only writes and no network on this Mac.

The coordinator is trusted to copy/merge records. Candidate Python is not trusted
with that authority, even when an independent resident requested its tests.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def run(command: list[str], cwd: Path, *, stdout, timeout: float) -> subprocess.CompletedProcess:
    executable = Path('/usr/bin/sandbox-exec')
    if not executable.is_file():
        raise ValueError('candidate tests require the installed macOS sandbox; no unsandboxed fallback')
    cwd = cwd.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix='emberhall-tests-') as temporary:
        scratch = Path(temporary).resolve()
        profile = ('(version 1)(allow default)(deny file-write*)'
                   '(allow file-write* (subpath ' + json.dumps(str(cwd)) + ')'
                   ' (subpath ' + json.dumps(str(scratch)) + ') (literal "/dev/null"))'
                   '(deny network*)')
        environment = dict(os.environ, TMPDIR=str(scratch), TMP=str(scratch), TEMP=str(scratch),
                           PYTHONDONTWRITEBYTECODE='1', EMBERHALL_CANDIDATE_SANDBOX='1')
        for name in ('OPENAI_API_KEY', 'CODEX_API_KEY', 'OPENROUTER_API_KEY'):
            environment.pop(name, None)
        job = os.environ.get('EMBERHALL_ACTION_JOB')
        if job is not None:
            if re.fullmatch(r'[0-9a-f]{64}', job) is None:
                raise ValueError('invalid trusted action identity')
            # Keep a tagged wrapper alive while candidate Python runs. If the
            # worker dies, its remaining process group is still identifiable.
            wrapper = ('import json,subprocess,sys;'
                       'raise SystemExit(subprocess.run(json.loads(sys.argv[2])).returncode)')
            command = [str(Path(sys.executable).resolve()), '-I', '-c', wrapper, job, json.dumps(command)]
        return subprocess.run([str(executable), '-p', profile, *command], cwd=cwd,
                              env=environment, stdin=subprocess.DEVNULL, stdout=stdout,
                              stderr=subprocess.STDOUT, timeout=timeout)
