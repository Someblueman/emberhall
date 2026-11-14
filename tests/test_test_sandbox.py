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
