"""Candidate tests can write their room, not the coordinator's authority store."""
import os
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from house import test_sandbox


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
