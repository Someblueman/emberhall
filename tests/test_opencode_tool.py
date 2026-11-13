"""The actual private JavaScript tool cannot turn model arguments into shell code."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

from house.opencode_tool import configure


@unittest.skipUnless(shutil.which('node'), 'Node is required for OpenCode tool acceptance')
class PrivateToolTests(unittest.TestCase):
    def test_fixed_runtime_ignores_workspace_modules_and_shell_metacharacters(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            workspace = root / 'room'
            workspace.mkdir()
            private = root / 'private'
            private.mkdir()
            (workspace / 'pathlib.py').write_text("raise RuntimeError('workspace code executed')")
            runtime = private / 'runtime.pyz'
            with zipfile.ZipFile(runtime, 'w') as archive:
                archive.writestr('house/__init__.py', '')
                archive.writestr('house/mailbox.py',
                    'import json\ndef client_main(workspace,resident,argv):\n'
                    ' print(json.dumps({"resident":resident,"argv":argv}));return 0\n')
            env = {}
            configure(private, workspace, runtime, 'assigned', env)
            tool = private / 'opencode-config/tools/house_journal.js'
            outside = root / 'escaped'
            argv = ['say', '--as', 'assigned', '; touch ' + str(outside), '$(touch ' + str(outside) + ')']
            code = ('const tool=(await import(' + json.dumps(tool.as_uri()) + ')).default;'
                    'process.stdout.write(await tool.execute({argv:' + json.dumps(argv) + '}));')
            result = subprocess.run(['node', '--input-type=module', '-e', code],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {'resident': 'assigned', 'argv': argv})
            self.assertFalse(outside.exists())
            self.assertNotIn(str(workspace), env['OPENCODE_CONFIG_DIR'])
