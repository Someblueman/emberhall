"""Candidate tests can write their room, not the coordinator's authority store."""
import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from house import test_sandbox, watch


@unittest.skipUnless(Path('/usr/bin/sandbox-exec').exists(), 'macOS sandbox required')
@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                     "host-only sandbox boundary fixture cannot nest macOS sandboxes")
class CandidateSandboxTests(unittest.TestCase):
    def test_writes_and_network_are_fenced_even_through_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            room = root / 'room'
            room.mkdir()
            outside = root / 'authority'
            outside.write_text('unchanged')
            (room / 'escape').symlink_to(outside)
            code = '''
import pathlib, socket, tempfile
pathlib.Path('inside').write_text('allowed')
with tempfile.NamedTemporaryFile() as output: output.write(b'allowed')
for target in ['escape', %r]:
    try: pathlib.Path(target).write_text('forbidden')
    except PermissionError: pass
    else: raise AssertionError('escaped room')
try:
    socket.socket().bind(('127.0.0.1', 0))
except PermissionError: pass
else: raise AssertionError('network unexpectedly allowed')
''' % str(outside)
            with tempfile.TemporaryFile() as output:
                result = test_sandbox.run([sys.executable, '-c', code], room, stdout=output, timeout=10)
                output.seek(0)
                self.assertEqual(result.returncode, 0, output.read().decode())
            self.assertEqual(outside.read_text(), 'unchanged')
            self.assertEqual((room / 'inside').read_text(), 'allowed')

    def test_timeout_stops_child_and_grandchild_before_removing_scratch(self):
        with tempfile.TemporaryDirectory() as temporary:
            room = Path(temporary).resolve()
            grandchild = ("import json,os,signal,time;from pathlib import Path;"
                          "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                          "Path('started.json').write_text(json.dumps("
                          "{'group':os.getpgrp(),'scratch':os.environ['TMPDIR']}));"
                          "time.sleep(30)")
            code = ("import subprocess,sys,time;"
                    f"subprocess.Popen([sys.executable,'-c',{grandchild!r}]);"
                    "time.sleep(30)")
            with tempfile.TemporaryFile() as output:
                with self.assertRaises(subprocess.TimeoutExpired):
                    test_sandbox.run([sys.executable, '-c', code], room,
                                     stdout=output, timeout=2)
            seen = json.loads((room / 'started.json').read_text())
            self.assertEqual(watch.group_members(seen['group']), [])
            self.assertFalse(Path(seen['scratch']).exists())

    # Steward, 18 November, night: the house's terminal runs a real shell and its tests need a real
    # pseudo-terminal and /bin/ps. One listed project's test run gets those; nothing else changes.
    TERMINAL = '''
import os, pathlib, pty, socket, subprocess, sys
def refused(action):
    try: action()
    except OSError: return True
    return False
def shell():
    pid, master = pty.fork()
    if pid == 0:
        os.execv('/bin/sh', ['/bin/sh', '-c', 'echo from-a-real-terminal'])
    seen = b''
    while b'from-a-real-terminal' not in seen:
        seen += os.read(master, 1024)
    os.waitpid(pid, 0)
def listing():
    out = subprocess.run(['ps', '-o', 'pid=,stat=', '-p', str(os.getpid())], capture_output=True, text=True)
    assert out.returncode == 0 and str(os.getpid()) in out.stdout, out
allowed = sys.argv[1] == 'yes'
assert refused(shell) != allowed, 'pseudo-terminal'
assert refused(listing) != allowed, 'ps'
assert refused(lambda: pathlib.Path(sys.argv[2]).write_text('forbidden')), 'escaped room'
assert refused(lambda: socket.socket().bind(('127.0.0.1', 0))), 'network unexpectedly allowed'
assert refused(lambda: open('/dev/console', 'w').close()), 'other devices stay closed'
pathlib.Path('inside').write_text('allowed')
'''

    def test_a_listed_projects_tests_may_open_a_real_terminal_and_nothing_else_changes(self):
        for allowed in (False, True):
            with self.subTest(terminals=allowed), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                room, outside = root / 'room', root / 'authority'
                room.mkdir()
                outside.write_text('unchanged')
                with tempfile.TemporaryFile() as output:
                    result = test_sandbox.run([sys.executable, '-c', self.TERMINAL, 'yes' if allowed else 'no',
                                               str(outside)], room, stdout=output, timeout=20, terminals=allowed)
                    output.seek(0)
                    self.assertEqual(result.returncode, 0, output.read().decode())
                self.assertEqual(outside.read_text(), 'unchanged')
                self.assertEqual((room / 'inside').read_text(), 'allowed')


class TerminalScopeTests(unittest.TestCase):
    def test_only_the_listed_projects_own_test_run_gets_terminals(self):
        runner = [sys.executable, '-c', 'import sys,unittest']
        self.assertEqual(frozenset({'projects/terminal-in-brainfuck'}), test_sandbox.TERMINAL_PROJECTS)
        scope = 'projects:projects/bench-for-two,projects/terminal-in-brainfuck'
        self.assertTrue(test_sandbox.terminals(scope, runner + ['projects/terminal-in-brainfuck']))
        self.assertFalse(test_sandbox.terminals(scope, runner + ['projects/bench-for-two']))
        self.assertFalse(test_sandbox.terminals(scope, ['node', '--check', 'projects/terminal-in-brainfuck/vm.js']))
        self.assertFalse(test_sandbox.terminals('foundation', runner + ['projects/terminal-in-brainfuck']))
        self.assertFalse(test_sandbox.terminals('prose', []))
        from house import renovation
        self.assertIn('house/test_sandbox.py', renovation.STEWARD_ONLY, 'only the Steward widens this list')
        import inspect
        self.assertEqual(False, inspect.signature(test_sandbox.run).parameters['terminals'].default)

