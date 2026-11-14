"""Run candidate tests with room-only writes and no network on this Mac.

The coordinator is trusted to copy/merge records. Candidate Python is not trusted
with that authority, even when an independent resident requested its tests.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time


def _stop_group(pgid: int, *, keep: int | None = None, guardian: int | None = None) -> None:
    """Stop the owned candidate group before removing its scratch directory.

    In a trusted action, keep the worker (and its durable job tag) alive while
    stopping every other group member. Standalone callers own a separate group.
    """
    deadline = time.monotonic() + 5
    while True:
        with subprocess.Popen(['ps', '-axo', 'pid=,pgid=,stat='],
                              stdout=subprocess.PIPE, text=True) as inspector:
            listing, _ = inspector.communicate(timeout=5)
            if inspector.returncode:
                raise RuntimeError('cannot inspect candidate process group; scratch preserved')
            members = [int(pid) for pid, group, status in
                       (line.split() for line in listing.splitlines())
                       if int(group) == pgid and int(pid) not in {keep, inspector.pid}
                       and not status.startswith('Z')]
        if not members:
            return
        # The guardian stays tagged until every candidate descendant stops.
        targets = [pid for pid in members if pid != guardian] or members
        for pid in targets:
            try:
                # The owning worker/group remains alive during inspection. Do
                # not signal a PID that exited and was reused in another group.
                if os.getpgid(pid) == pgid:
                    os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if time.monotonic() >= deadline:
            raise RuntimeError('candidate descendants did not stop; scratch preserved')
        time.sleep(0.02)


def run(command: list[str], cwd: Path, *, stdout, timeout: float) -> subprocess.CompletedProcess:
    executable = Path('/usr/bin/sandbox-exec')
    if not executable.is_file():
        raise ValueError('candidate tests require the installed macOS sandbox; no unsandboxed fallback')
    cwd = cwd.resolve(strict=True)
    job = os.environ.get('EMBERHALL_ACTION_JOB')
    if job is not None:
        if re.fullmatch(r'[0-9a-f]{64}', job) is None:
            raise ValueError('invalid trusted action identity')
        if os.getpgrp() != os.getpid():
            raise ValueError('trusted action must own its process group')
    scratch = Path(tempfile.mkdtemp(prefix='emberhall-tests-')).resolve()
    child = None
    read_fd = write_fd = None
    try:
        profile = ('(version 1)(allow default)(deny file-write*)'
                   '(allow file-write* (subpath ' + json.dumps(str(cwd)) + ')'
                   ' (subpath ' + json.dumps(str(scratch)) + ') (literal "/dev/null"))'
                   '(deny network*)')
        environment = dict(os.environ, TMPDIR=str(scratch), TMP=str(scratch), TEMP=str(scratch),
                           PYTHONDONTWRITEBYTECODE='1', EMBERHALL_CANDIDATE_SANDBOX='1')
        for name in ('OPENAI_API_KEY', 'CODEX_API_KEY', 'OPENROUTER_API_KEY'):
            environment.pop(name, None)
        if job is not None:
            # The tag survives abrupt worker death so the coordinator can
            # identify and stop the complete existing action group.
            read_fd, write_fd = os.pipe()
            wrapper = ("import json,os,subprocess,sys,time\n"
                       "code = subprocess.run(json.loads(sys.argv[2])).returncode\n"
                       "try: os.write(int(sys.argv[3]), str(code).encode())\n"
                       "except BrokenPipeError: pass\n"
                       "os.close(int(sys.argv[3]))\n"
                       "while True: time.sleep(3600)\n")
            command = [str(Path(sys.executable).resolve()), '-I', '-c', wrapper,
                       job, json.dumps(command), str(write_fd)]
        argv = [str(executable), '-p', profile, *command]
        child = subprocess.Popen(argv, cwd=cwd, env=environment,
                                 stdin=subprocess.DEVNULL, stdout=stdout,
                                 stderr=subprocess.STDOUT, start_new_session=job is None,
                                 pass_fds=() if write_fd is None else (write_fd,))
        if write_fd is not None:
            os.close(write_fd)
            write_fd = None
            if not select.select([read_fd], [], [], timeout)[0]:
                raise subprocess.TimeoutExpired(argv, timeout)
            result = os.read(read_fd, 32)
            if not result:
                raise RuntimeError('candidate guardian exited without a result')
            code = int(result)
        else:
            code = child.wait(timeout=timeout)
        return subprocess.CompletedProcess(argv, code)
    finally:
        for descriptor in (read_fd, write_fd):
            if descriptor is not None:
                os.close(descriptor)
        if child is not None:
            # Unlike subprocess.run(timeout=...), do not kill/reap only the
            # tagged wrapper and strand its untagged children. No new process
            # group is created inside a durable action. Unknown groups remain
            # protected by the coordinator's unchanged identity check.
            _stop_group(os.getpgrp() if job else child.pid,
                        keep=os.getpid() if job else None,
                        guardian=child.pid if job else None)
            child.wait(timeout=5)
        # If group inspection/termination failed, leave scratch intact. A
        # failing timeout must not race live descendants during rmtree.
        shutil.rmtree(scratch)
