"""The actual private JavaScript tool cannot turn model arguments into shell code."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

from house.opencode_tool import configure, validate_workspace


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
            tool = private / 'opencode-config/plugins/house_journal.js'
            outside = root / 'escaped'
            argv = ['say', '--as', 'assigned', '; touch ' + str(outside), '$(touch ' + str(outside) + ')']
            code = ('const plugin=(await import(' + json.dumps(tool.as_uri()) + ')).default;'
                    'let tool;let checked=false;await plugin.setup({tool:{transform:async f=>f({list:()=>[],add:t=>tool=t})},'
                    'permission:{assert:async r=>{if(r.action!=="house_journal")throw Error("wrong permission");checked=true}}});'
                    'const result=await tool.execute({argv:' + json.dumps(argv) + '},{sessionID:"s",agent:"emberhall",messageID:"m",id:"i"});'
                    'if(!checked)throw Error("permission skipped");process.stdout.write(result.content);')
            result = subprocess.run(['node', '--input-type=module', '-e', code],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {'resident': 'assigned', 'argv': argv})
            self.assertFalse(outside.exists())
            self.assertNotIn(str(workspace), env['OPENCODE_CONFIG_DIR'])


class OpenCodeRoomBoundaryTests(unittest.TestCase):
    def test_outside_file_directory_and_git_alias_links_refuse_admission(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            room, outside = root / 'room', root / 'private'
            room.mkdir(); outside.mkdir()
            (room / '.git').mkdir()
            (outside / 'proof.txt').write_text('private sentinel')
            (room / 'ordinary.txt').write_text('resident source')
            validate_workspace(room)
            for target in (outside / 'proof.txt', outside, room / '.git'):
                alias = room / 'innocent'
                alias.symlink_to(target)
                with self.assertRaisesRegex(ValueError, 'links'):
                    validate_workspace(room)
                alias.unlink()
            self.assertEqual((outside / 'proof.txt').read_text(), 'private sentinel')

    def test_hard_link_and_special_file_refuse_admission(self):
        import os
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            room = root / 'room'; room.mkdir()
            source = root / 'outside'; source.write_text('private')
            target = room / 'innocent'; os.link(source, target)
            with self.assertRaisesRegex(ValueError, 'hard-linked'):
                validate_workspace(room)
            target.unlink(); os.mkfifo(target)
            with self.assertRaisesRegex(ValueError, 'special files'):
                validate_workspace(room)
            target.unlink()
            alias = root / 'room-alias'; alias.symlink_to(room)
            with self.assertRaisesRegex(ValueError, 'canonical path'):
                validate_workspace(alias)
