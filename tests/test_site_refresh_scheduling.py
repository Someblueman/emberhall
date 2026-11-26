"""Exercise snapshot-first loading, navigation, and replacement with the real page scripts."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node executes the page loader")
class SiteRefreshSchedulingTests(unittest.TestCase):
    def run_page(self, checks):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const {gzipSync}=require('node:zlib');
const source=fs.readFileSync(process.argv[1]+'/site/house.js','utf8');
const page=fs.readFileSync(process.argv[1]+'/site/index.html','utf8');
const calls=[],timers=[],nodes={},loaded=[];
const get=id=>nodes[id]??={
 id,hidden:id==='record-load',listeners:{},textContent:'',value:'',
 addEventListener(k,fn){this.listeners[k]=fn;},
 setAttribute(k,v){this[k]=v;},removeAttribute(k){delete this[k];},focus(){}
};
const document={getElementById:get,querySelector:()=>null,activeElement:null,
 addEventListener(k,fn){assert.equal(k,'DOMContentLoaded');loaded.push(fn);}};
let now=0,head='one',size=3,decodeFailure=false,compressed=false,currentMissing=false,pauseHistory;
const gzipPath='current/0123456789abcdef.json.gz';
const frames=()=>Array.from({length:size},(_,i)=>({seq:i+1,scars:[]}));
const history=()=>({version:1,journal_head:head,source_head:'source',frames:frames(),scars:{}});
const current=()=>({...history(),frames:frames().slice(-1),
 history:{current_only:true,total_frames:size,last_sequence:size}});
let beforeParse=()=>{};
const fetch=async url=>{
 calls.push(url.split('?')[0]);
 if(url.startsWith('head.json'))return {ok:true,json:async()=>({journal_head:head,source_head:'source'})};
 if(url==='current.json'&&currentMissing)return {ok:false,status:404};
 if(url==='current.json')return {ok:true,json:async()=>{
   const snapshot=current();
   if(compressed)return {...snapshot,frames:undefined,gzip:gzipPath};
   return snapshot;
 }};
 if(url===gzipPath)return new Response(gzipSync(JSON.stringify(current())));
 assert.equal(url,'history.json');
 if(pauseHistory)await pauseHistory;
 return {ok:true,json:async()=>{
   beforeParse();
   if(decodeFailure)throw new Error('Bad JSON');
   return history();
 }};
};
const ctx=vm.createContext({document,fetch,AbortSignal,DecompressionStream,Response,
 Date:{now:()=>now},window:{location:{hash:''},addEventListener(){}},
 setInterval:(fn,ms)=>timers.push({fn,ms})});
const run=s=>vm.runInContext(s,ctx);
const start=()=>{
 const bootstrap=source.lastIndexOf('\nrefresh();\n');
 assert(bootstrap>=0);
 run(source.slice(0,bootstrap));
 run(`let draws=0,ticks=0;
 render=()=>{frame=data.frames[index];draws++;};
 refreshView=changed=>{if(changed)render();else ticks++;};
 showViewForHash=()=>{};
 renderViewContext=()=>{};`);
 run(source.slice(bootstrap));
 run(page.match(/<script id="event-navigation-script">([\s\S]*?)<\/script>/)[1]);
 loaded[0]();
 return run('refreshPending');
};
const click=id=>get(id).listeners.click();
const move=value=>get('history').listeners.input({target:{value}});
const submit=value=>{
 get('event-number').value=value;
 return get('event-navigation').listeners.submit({preventDefault(){}});
};
const check=(async()=>{
''' + checks + r'''
})();
check.catch(error=>{console.error(error);process.exitCode=1;});
'''
        result = subprocess.run(
            [shutil.which("node"), "-e", script, str(ROOT)],
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_bootstrap_and_thirty_unchanged_head_polls(self):
        self.run_page(r'''
await start();
assert.deepEqual(timers.map(({fn,ms})=>[fn.name,ms]),[['watch',10000]]);
assert.deepEqual(calls.splice(0),['current.json']);
assert.equal(run('frame.seq'),3);assert.equal(run('data.frames.length'),1);
assert.equal(run('historyLength()'),3);assert.equal(run('draws'),1);
for(let i=0;i<30;i++){
 now+=10000;await timers[0].fn();
}
assert.deepEqual(calls.splice(0),Array(30).fill('head.json'));
assert.equal(run('draws'),1);assert.equal(run('ticks'),5);
head='two';size=4;compressed=true;await timers[0].fn();
assert.deepEqual(calls.splice(0),['head.json','current.json',gzipPath]);
assert.equal(run('frame.seq'),4);assert.equal(run('data.frames.length'),1);
await timers[0].fn();assert.deepEqual(calls,['head.json']);
''')

    def test_first_history_control_loads_on_demand_and_shares_one_request(self):
        for initial_control in ("move(1)", "click('previous')", "submit('1')"):
            with self.subTest(control=initial_control):
                self.run_page(r'''
await start();
assert.deepEqual(calls.splice(0),['current.json']);
const initial=''' + initial_control + r''';
await initial;
assert.deepEqual(calls.splice(0),['history.json']);
assert.equal(run('frame.seq'),''' + ("2" if initial_control == "click('previous')" else "1") + r''');
assert.equal(run('current'),false);
move(1);click('next');assert.equal(run('frame.seq'),2);
click('previous');assert.equal(run('frame.seq'),1);
await submit('2');assert.equal(run('frame.seq'),2);
assert.match(get('event-number-result').textContent,/Opened event 2/);
click('present');assert.equal(run('frame.seq'),3);
await move(2);assert.equal(run('frame.seq'),2);
assert.deepEqual(calls,[]);
''')
        self.run_page(r'''
await start();calls.length=0;
let release;pauseHistory=new Promise(resolve=>{release=resolve;});
const first=move(2),last=move(1);
assert.deepEqual(calls,['history.json']);
assert.equal(run('frame.seq'),3);
release();await Promise.all([first,last]);
assert.equal(run('frame.seq'),1);assert.deepEqual(calls,['history.json']);
''')

    def test_replacement_releases_the_old_graph_before_parse_and_keeps_selection(self):
        self.run_page(r'''
await start();await move(2);calls.length=0;
head='two';size=4;
// A visitor in the past keeps the history they opened; a journal change does not reload it.
await ctx.watch();
assert.deepEqual(calls.splice(0),['head.json']);
assert.equal(run('frame.seq'),2);assert.equal(run('data.frames.length'),3);
const old=run('data');
beforeParse=()=>{
 assert.equal(old.frames.length,1);
 assert.equal(run('data.frames.length'),1);
 assert.equal(run('frame.seq'),2);assert.equal(run('historyLength()'),3);
};
decodeFailure=true;
await run('refresh(true)');
assert.deepEqual(calls.splice(0),['history.json']);
assert.match(get('error').textContent,/last remembered snapshot/);
assert.equal(run('frame.seq'),2);assert.equal(run('current'),false);
decodeFailure=false;size=2;await click('record-retry');
assert.match(get('error').textContent,/last remembered snapshot/);
size=4;await click('record-retry');
assert.equal(get('record-load').hidden,true);
assert.equal(run('data.frames.length'),4);assert.equal(run('frame.seq'),2);
assert.equal(run('data.journal_head'),'two');
calls.length=0;await ctx.watch();assert.deepEqual(calls,['head.json']);
''')

    def test_latest_visitor_returns_to_the_snapshot_after_history(self):
        self.run_page(r'''
await start();await move(1);
click('present');assert.equal(run('frame.seq'),3);assert.equal(run('current'),true);
calls.length=0;head='two';size=4;
await ctx.watch();
assert.deepEqual(calls.splice(0),['head.json','current.json']);
assert.equal(run('data.frames.length'),1);assert.equal(run('frame.seq'),4);
assert.equal(run('historyOpened'),false);
await ctx.watch();assert.deepEqual(calls,['head.json']);
''')

    def test_publication_without_a_snapshot_reads_the_full_history(self):
        self.run_page(r'''
currentMissing=true;
await start();
assert.deepEqual(calls.splice(0),['current.json','history.json']);
assert.equal(run('frame.seq'),3);assert.equal(run('data.frames.length'),3);
assert.equal(get('record-load').hidden,true);
currentMissing=false;head='two';size=4;
await ctx.watch();
assert.deepEqual(calls.splice(0),['head.json','current.json']);
assert.equal(run('data.frames.length'),1);assert.equal(run('frame.seq'),4);
''')
