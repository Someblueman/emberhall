"""Exercise the actual cue formatter and its current/history view wiring."""
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(shutil.which("node"), "Node executes the actual house renderer")
class SnapshotFreshnessTests(unittest.TestCase):
    def test_times_and_current_history_wiring(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[1],'utf8');
const tail='refresh();\nsetInterval(refresh,60000);\n';
assert(source.endsWith(tail));
const nodes={};
const document={body:{classList:{toggle(){}}},getElementById(id){
  return nodes[id]||(nodes[id]={textContent:''});
}};
const now=1794643200;
class FixedDate extends Date {static now(){return now*1000;}}
const ctx=vm.createContext({assert,document,Date:FixedDate});
vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
const now=1794643200, zone='Europe/London';
assert.match(snapshotCue(now,now-15,now,true,zone),/just now$/);
assert.match(snapshotCue(now,now-600,now,true,zone),/10m ago$/);
assert.match(snapshotCue(now,now-7200,now,true,zone),/2h ago$/);
assert.match(snapshotCue(now,now-172800,now,true,zone),/2d ago$/);
for(const bad of [undefined,null,NaN,Infinity,-1,0,'1794643200',1e20]){
  assert.equal(snapshotCue(now,bad,now,true,zone),'Snapshot time unknown');
  assert.equal(snapshotCue(now,now,bad,false,zone),'Event time unknown');
}
for(const ahead of [1,300])
  assert.match(snapshotCue(now,now+ahead,now,true,zone),/ahead of clock$/);
assert.equal(snapshotCue(NaN,now,now,true,zone),'Snapshot 14 Nov, 08:00');
assert.equal(snapshotCue(now,now,now,false,'America/New_York'),'Event 14 Nov, 03:00');
assert.equal(snapshotCue(now,now-600,now,true,'America/New_York'),
  'Snapshot 14 Nov, 02:50 · 10m ago');
// Actual lighting uses export time in current view and selected event in history.
data={timezone:zone,observed_at:now-600};frame={at:now-3600};current=true;
lighting();
assert.equal($('snapshot-cue').textContent,'Snapshot 14 Nov, 07:50 · 10m ago');
assert.match($('house-clock').textContent,/08:00/);
current=false;lighting();
assert.equal($('snapshot-cue').textContent,'Event 14 Nov, 07:00');
assert.match($('house-clock').textContent,/07:00/);
current=true;data.observed_at=undefined;lighting();
assert.equal($('snapshot-cue').textContent,'Snapshot time unknown');
`,ctx);
'''
        result = subprocess.run(
            ["node", "-e", script, str(ROOT / "site/house.js")],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
