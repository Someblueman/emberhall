"""Exercise the real record loader and retry control at its fetch boundary."""
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(shutil.which("node"), "Node executes the page loader")
class HouseLoadRecoveryTests(unittest.TestCase):
    def test_failure_retry_pending_success_and_snapshot_preservation(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes={};
const document={activeElement:null,getElementById:id=>nodes[id]||null,
 querySelector:selector=>selector==='.page-view:not([hidden])'?nodes['house-view']:null};
for(const id of ['record-retry','record-load','record-load-status','error','presence-line','view-context','history','house-view','outside']){
 nodes[id]={id,hidden:id==='record-load',textContent:'',listeners:{},
  setAttribute(k,v){this[k]=v;},addEventListener(k,fn){assert(!this.listeners[k]);this.listeners[k]=fn;},
  focus(){document.activeElement=this;},scrollIntoView(){this.scrolled=true;}};
}
let respond,calls=0;
const fetch=()=>{calls++;return new Promise(resolve=>{respond=resolve;});};
const ctx=vm.createContext({document,fetch,AbortSignal});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(refresh,60000);setInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
const run=s=>vm.runInContext(s,ctx),get=id=>nodes[id];
// Drawing is tested separately. Keep the real loader, decoder and catalog gate.
run('refreshView=()=>{frame=data.frames[index];};bindControls=()=>{controlsReady=true;};');
const snapshot={version:1,journal_head:'one',source_head:'source',frames:[{seq:1,scars:[]}],scars:{}};
const answer=async(pending,payload,ok=true)=>{respond({ok,status:503,json:async()=>payload});await pending;};
const retry=()=>get('record-retry').listeners.click();
(async()=>{
 await answer(ctx.refresh(),null,false);
 assert.equal(get('record-load').hidden,false);assert.match(get('error').textContent,/could not be loaded/);
 assert.match(get('presence-line').textContent,/no activity is invented/);
 assert.equal(get('view-context').textContent,'The house record has not loaded.');
 assert.equal(get('record-retry')['aria-disabled'],'false');
 get('record-retry').focus();
 const pending=retry();assert.equal(calls,2);
 assert.equal(get('record-retry')['aria-disabled'],'true');assert.equal(get('record-load')['aria-busy'],'true');
 assert.match(get('record-load-status').textContent,/Loading/);
 assert.match(get('view-context').textContent,/Loading/);
 await retry();assert.equal(calls,2); // repeated keyboard activation cannot send a second request
 await answer(pending,snapshot);
 assert.equal(get('record-load').hidden,true);assert.equal(get('error').textContent,'');
 assert.match(get('record-load-status').textContent,/available again/);
 assert.equal(document.activeElement,get('house-view'));assert.equal(get('house-view').scrolled,true);
 assert.equal(run('frame.seq'),1);assert.equal(run('controlsReady'),true);
 // A later failure keeps the accepted snapshot and does not steal a visitor's focus.
 get('outside').focus();await answer(ctx.refresh(),null,false);
 assert.match(get('error').textContent,/last remembered snapshot is still here/);
 assert.equal(run('data.journal_head'),'one');assert.equal(run('frame.seq'),1);
 assert.equal(document.activeElement,get('outside'));
 await answer(retry(),snapshot); // same-head recovery must also clear the failure
 assert.equal(get('record-load').hidden,true);assert.equal(document.activeElement,get('outside'));
 // Malformed and empty records remain failures, without replacing the valid record.
 await answer(ctx.refresh(),{version:99});assert.equal(get('record-load').hidden,false);
 await answer(retry(),{...snapshot,frames:[]});assert.equal(get('record-load').hidden,false);
 assert.equal(run('data.journal_head'),'one');
 // Moving away during a retry wins over the disappearing retry button's focus handoff.
 get('record-retry').focus();const late=retry();get('outside').focus();await answer(late,snapshot);
 assert.equal(document.activeElement,get('outside'));assert.equal(get('record-load').hidden,true);
 assert.equal(get('record-retry')['aria-disabled'],'false');assert.equal(get('record-load')['aria-busy'],'false');
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
        result = subprocess.run(
            [shutil.which("node"), "-e", script, str(ROOT / "site/house.js")],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_recovery_is_before_the_house_and_has_live_feedback(self):
        source = (ROOT / "site/index.html").read_text()
        self.assertLess(source.index('id="record-load"'), source.index('id="house-view"'))
        self.assertEqual(source.count('id="error"'), 1)
        self.assertIn('id="error" role="alert"', source)
        self.assertIn('id="record-retry" class="quiet-button" type="button"', source)
        self.assertIn('id="record-load-status" class="sr-only" role="status"', source)
