"""Real Git/mailbox/checkpoint operations across a recorded location migration."""
import copy
import json
import os
from pathlib import Path
import subprocess
import time
import unittest
import zipfile

from house import maintenance, mailbox
from house.files import workspace_path
from house.home_work import client, git, room, contribution, preserve
from house.resident_actions import execute
from tests import test_runtime
from tests.support import SOURCE


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        fixture = test_runtime.RuntimeTests(); fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.record, self.repo, self.root = fixture.record, fixture.repo, fixture.root
        (self.repo / '.gitignore').write_text('.house-residents/\n')
        git(self.repo, 'add', '.gitignore')
        git(self.repo, '-c', 'commit.gpgsign=false', '-c', 'user.name=Test', '-c',
            'user.email=test@local', 'commit', '-m', 'Ignore private source rooms')
        self.base = git(self.repo, 'rev-parse', 'HEAD')
        self.private = self.record.common / 'house-home'; self.private.mkdir()
        self.record.append('arrive', 'watch-keeper', {'name': 'Clock'})
        self.migrate(scope=maintenance.RETRY_SCOPE)

    def migration(self, scope=maintenance.WORKSPACE_SCOPE):
        state = self.record.read()[0]; old = maintenance.protected_manifest(state)
        names = set(old) | maintenance.OWNER_MODULES
        from house.wake_policy import source_snapshot
        files = source_snapshot(self.repo)['files']
        return {
            'scope': scope, 'approval_sha256': maintenance.SOURCES[scope],
            'house': state['house_id'], 'owner_id': maintenance.council.OWNER_ID,
            'source_head': self.base, 'source_sha256': 'a'*64,
            'protected_files': {name: files[name] for name in names},
            'previous_manifest_sha256': maintenance.fingerprint(old),
            'previous_runtime_sha256': 'b'*64, 'runtime_sha256': 'c'*64,
            'test_output_sha256': 'd'*64, 'test_count': 1}

    def migrate(self, scope=maintenance.WORKSPACE_SCOPE):
        return self.record.append('owner-migrate', 'alice', self.migration(scope))

    def start(self, run):
        self.record.append('life', 'watch-keeper', {'kind':'run-start', 'run':run,
            'resident':'resident-'+run, 'agent':'muse', 'model':'muse-ember-1.0',
            'source_head':self.base, 'workspace':'residents/'+run, 'policy_revision':'fixture', 'mode':'work'})

    def test_new_room_supports_fixed_mailbox_checkpoint_and_preserved_contribution(self):
        before = copy.deepcopy(self.record.read()[0]); receipt = self.migrate()
        after = self.record.read()[0]
        self.assertEqual(after['maintenance']['workspace_layout_sequence'], receipt['sequence'])
        for key, value in before.items():
            if key not in {'maintenance','sequence','at','receipts'}: self.assertEqual(after[key], value)
        self.start('new'); workspace = room(self.record,self.private,'new',self.base)
        self.assertEqual(workspace,self.record.root/'.house-residents/new')
        self.assertNotIn('.git',workspace.parts)
        self.assertEqual(workspace.parent.stat().st_mode & 0o777,0o700)
        self.record.append('life','watch-keeper',{'kind':'run-launched','run':'new','pgid':os.getpid()})
        runtime=self.private/'fixture.pyz'
        with zipfile.ZipFile(runtime,'w') as archive:
            for file in (SOURCE/'house').glob('*.py'): archive.write(file,'house/'+file.name)
        endpoint=client(self.record,workspace,'resident-new',runtime)
        (self.private/'new').mkdir()
        def call(*args):
            process=subprocess.Popen([str(endpoint),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            self.addCleanup(lambda: process.kill() if process.poll() is None else None)
            deadline=time.monotonic()+12
            while process.poll() is None and time.monotonic()<deadline:
                mailbox.service(self.record,self.private,'new');time.sleep(.02)
            out,err=process.communicate(timeout=2)
            self.assertEqual(process.returncode,0,err);return json.loads(out)
        call('arrive','--as','resident-new','--name','Fixture')
        call('task','work','--as','resident-new','--title','Work','--description','Synthetic work')
        call('claim','work','--as','resident-new','--expect','0','--token','token','--seconds','600')
        checkpoint=execute(self.record,workspace,'resident-new','new',
            ['checkpoint','--as','resident-new','--task','work','--token','token'],'checkpoint')
        self.assertTrue((workspace/checkpoint['bundle']).is_file())
        (workspace/'result.txt').write_text('preserved\n')
        call('finish','work','--as','resident-new','--token','token','--result','Done','--artifact','result.txt')
        self.assertIsNotNone(preserve(self.private,'new',workspace)['rescue'])
        candidate=contribution(workspace,self.base,self.private/'candidate.json',journal_artifacts={})
        self.assertIn('result.txt',candidate['paths'])
        self.assertEqual(git(self.repo,'status','--porcelain'),'')
        self.assertFalse((self.repo/'result.txt').exists())

    def test_old_room_stays_bound_and_new_paths_do_not_fall_back_or_follow_symlinks(self):
        self.start('old');old=room(self.record,self.private,'old',self.base)
        (old/'kept.txt').write_text('old work')
        self.record.append('life','watch-keeper',{'kind':'run-finish','run':'old','outcome':'success',
            'exit_code':0,'usage':{},'elapsed_seconds':1})
        self.migrate();self.assertEqual(workspace_path(self.record,'old'),old)
        self.assertEqual((old/'kept.txt').read_text(),'old work')
        self.start('new')
        (self.private/'residents/new').mkdir()
        self.assertEqual(workspace_path(self.record,'new'),self.record.root/'.house-residents/new')
        outside=self.root/'outside';outside.mkdir()
        (self.repo/'.house-residents').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(OSError):room(self.record,self.private,'new',self.base)
        self.assertEqual(list(outside.iterdir()),[])
        for value in ('../new','/tmp/new','bad/name',''):
            with self.assertRaises(ValueError):workspace_path(self.record,value)
        with self.assertRaisesRegex(ValueError,'recorded run'):workspace_path(self.record,'unknown')

    def test_new_resolver_is_pinned_and_cannot_change_other_enforcement(self):
        state=self.record.read()[0]
        self.assertIn('house/files.py',maintenance.protected_manifest(state))
        for path in ('house/council.py','house/providers.py','house/owner_upgrade.py'):
            bad=self.migration();bad['protected_files'][path]='0'*64
            with self.assertRaisesRegex(ValueError,'outside.*scope'):
                self.record.append('owner-migrate','alice',bad)
        self.migrate();state=self.record.read()[0]
        self.assertIn('house/files.py',maintenance.protected_manifest(state))
        self.assertNotIn('house/council.py',maintenance.ALLOWED_CHANGES[maintenance.WORKSPACE_SCOPE])
        with self.assertRaisesRegex(ValueError,'already used'):self.migrate()

    def test_replaced_parent_or_room_is_rejected_before_actions_and_integration(self):
        from house.integrate import integrate
        self.migrate();self.start('new')
        workspace=room(self.record,self.private,'new',self.base)
        self.record.append('life','watch-keeper',{'kind':'run-launched','run':'new','pgid':os.getpid()})
        self.record.append('arrive','resident-new',{'name':'Fixture'})
        saved=workspace.with_name('saved');workspace.rename(saved)
        workspace.symlink_to(saved,target_is_directory=True)
        with self.assertRaises(OSError):workspace_path(self.record,'new')
        workspace.unlink();saved.rename(workspace)
        parent=workspace.parent;original=parent.with_name('.saved-rooms');parent.rename(original)
        parent.symlink_to(original,target_is_directory=True)
        with self.assertRaises(OSError):
            execute(self.record,workspace,'resident-new','new',
                    ['council','--as','resident-new','status'],'symlink-action')
        from house.home import Coordinator
        (self.private/'new').mkdir()
        runtime=self.private/'unused-runtime.pyz';runtime.write_bytes(b'not executed')
        coordinator=Coordinator(self.record,runtime)
        coordinator.finish('new',{'outcome':'success','exit_code':0,'usage':{},'elapsed_seconds':1})
        self.assertEqual(self.record.read()[0]['life']['runs']['new']['status'],'completed')
        error=json.loads((self.private/'new/preservation-error.json').read_text())
        self.assertTrue(error['workspace_retained'])
        with self.assertRaises(OSError):integrate(self.record,'new','alice')
        self.assertTrue((original/'new/.git').is_dir())
