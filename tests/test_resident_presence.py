"""Resident presence logic runs in the actual house renderer with a small DOM."""
from pathlib import Path
import shutil
import subprocess
import unittest


SOURCE = Path(__file__).parents[1] / "site/house.js"
HARNESS = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.className='';this.style={};}
  appendChild(node){this.children.push(node);}
  replaceChildren(){this.children=[];}
  set innerHTML(value){throw new Error('Render text safely');}
  setAttribute(){}
  addEventListener(){}
}
const flags={missing:false},nodes={};
const get=id=>flags.missing&&id==='resident-pulse'?null:
  (nodes[id]||(nodes[id]=Object.assign(new Element('div'),{id})));
const document={getElementById:get,createElement:tag=>new Element(tag),
  createElementNS:(ns,tag)=>new Element(tag),querySelectorAll:()=>[]};
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const all=node=>[node,...node.children.flatMap(all)];
class FixedDate extends Date {static now(){return 2000000;}}
const context=vm.createContext({assert,document,nodes,flags,text,all,Date:FixedDate});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
const pulse=()=>nodes['resident-pulse'];
const pulseText=()=>text(pulse());
const pulseNodes=()=>all(pulse());
`,context);
'''


@unittest.skipUnless(shutil.which("node"), "Node executes the actual house renderer")
class ResidentPresenceTests(unittest.TestCase):
    def run_renderer(self, setup, assertions):
        script = HARNESS + "\nvm.runInContext(" + repr(setup + assertions) + ",context);"
        result = subprocess.run(
            [shutil.which("node"), "-e", script, str(SOURCE)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_preparing_open_runs_manual_keeper_and_claims(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',observed_at:4000,frames:[{seq:1,at:1000}]};current=true;
frame={seq:40,at:4000,rooms:[],scars:[],residents:[
 {id:'r1',name:'Fern',agent:'codex',model:'gpt-6.1-sol',room:'workshop',pose:'standing'},
 {id:'r2',name:'Oriel',agent:'opencode',model:'deepseek-v4.1-flash',room:'hearth',pose:'sitting'},
 {id:'keeper-01',name:'Keeper',agent:'unrecorded',room:'hearth',pose:'standing'}],
 tasks:[{id:'t1',title:'Build presence pulse',owner:'r2',status:'claimed',until:5000,generation:1}],
 runs:[
  {id:'run-prep',resident:'r1',agent:'codex',model:'gpt-6.1-sol',start:3900,sequence:2,status:'started'},
  {id:'run-open',resident:'r2',agent:'opencode',model:'deepseek-v4.1-flash',start:3800,sequence:3,status:'launched'}]};
renderResidentPulse();
const body=pulseText();
''', r'''
assert.match(body,/2 resident runs open/);
assert.match(body,/0 recent run endings/);
assert.match(body,/1 recorded awake outside a house run/);
assert.match(body,/Preparing/);
assert.match(body,/Run open/);
assert.match(body,/dated record, not a live process check/);
assert.match(body,/Keeper/);
assert.match(body,/Recorded awake outside a house run:/);
assert.match(body,/Claimed: Build presence pulse/);
assert.match(body,/No task claimed/);
assert.match(body,/Open and preparing runs are clipped to/);
assert.match(body,/0 residents 46m 40s/);
assert.match(body,/1 resident 1m 40s/);
assert.match(body,/2 residents 1m 40s/);
assert.doesNotMatch(body,/is idle|is waiting/);
''')

    def test_sleep_before_run_closure_is_not_shown_working(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',observed_at:4000,frames:[{seq:1,at:1000}]};current=true;
frame={seq:20,at:4000,rooms:[],scars:[],residents:[
 {id:'r2',name:'Oriel',agent:'opencode',room:'bedroom',pose:'sleeping'}],
 tasks:[],
 runs:[{id:'run-open',resident:'r2',agent:'opencode',start:3900,sequence:3,status:'launched'}]};
renderResidentPulse();
const body=pulseText();
''', r'''
assert.match(body,/Last posture: asleep; launch timing uncertain/);
assert.doesNotMatch(body,/Run open ·|Run open at this moment/);
assert.doesNotMatch(body,/actively working|working now/i);
''')

    def test_recorded_end_is_collapsed_and_expired_claim_stays_honest(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',observed_at:4000,frames:[{seq:1,at:1000}]};current=true;
frame={seq:30,at:4000,rooms:[],scars:[],residents:[
 {id:'r2',name:'Oriel',agent:'opencode',room:'hearth',pose:'standing'}],
 tasks:[{id:'t-old',title:'Old repair',owner:'r2',status:'claimed',until:3500,generation:2}],
 runs:[{id:'run-end',resident:'r2',agent:'opencode',start:3700,sequence:2,
   status:'ended',end:3800,outcome:'success',last_sequence:4}]};
renderResidentPulse();
const body=pulseText();
const details=pulseNodes().filter(n=>n.tag==='details');
''', r'''
assert.equal(details.length,1);
assert.equal(details[0].open,undefined);
assert.match(body,/0 resident runs open/);
assert.match(body,/1 recent run ending/);
assert.match(body,/Run ended .*success/);
assert.match(body,/Last claim expired; fate unconfirmed/);
assert.doesNotMatch(body,/Claimed: Old repair/);
''')

    def test_awake_after_ended_run_is_listed_outside_the_run(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',observed_at:4000,frames:[{seq:1,at:1000}]};current=true;
frame={seq:31,at:4000,rooms:[],scars:[],residents:[
 {id:'r',name:'Oriel',agent:'opencode',room:'hearth',pose:'standing'}],
 tasks:[],
 runs:[{id:'run-end',resident:'r',agent:'opencode',start:3700,sequence:2,
   status:'ended',end:3800,outcome:'success',last_sequence:4}]};
renderResidentPulse();
const body=pulseText();
''', r'''
assert.match(body,/0 resident runs open/);
assert.match(body,/1 recent run ending/);
assert.match(body,/1 recorded awake outside a house run/);
assert.match(body,/Recorded awake outside a house run:/);
assert.match(body,/Run ended .*success/);
assert.match(body,/No task claimed/);
''')

    def test_overlap_bar_preserves_concurrency_counts_and_gaps(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',observed_at:4000,frames:[{seq:1,at:100}]};current=true;
frame={seq:60,at:4000,rooms:[],scars:[],residents:[],tasks:[],runs:[
 {id:'a',resident:'x',agent:'codex',start:300,sequence:1,status:'ended',end:900,outcome:'success'},
 {id:'b',resident:'y',agent:'muse',start:800,sequence:2,status:'ended',end:1400,outcome:'success'},
 {id:'c',resident:'z',agent:'agy',start:1300,sequence:3,status:'ended',end:2000,outcome:'success'},
 {id:'d',resident:'w',agent:'opencode',start:2500,sequence:4,status:'ended',end:2600,outcome:'success'}]};
renderResidentPulse();
const body=pulseText();
const segments=pulseNodes().filter(n=>n.className==='occupancy-segment');
''', r'''
assert.equal(segments.length,8);
assert.equal(segments[0].style.flexGrow,'400');
assert.equal(segments[1].style.flexGrow,'100');
assert.equal(segments[5].style.flexGrow,'500');
assert.equal(segments[5].style.opacity,'0');
assert.equal(segments[7].style.flexGrow,'1400');
assert.equal(segments[7].style.opacity,'0');
assert.ok(segments.every(s=>s.style.marginLeft===undefined));
assert.ok(segments.every(s=>s.style.flexBasis==='0'));
assert.match(body,/0 residents 31m 40s/);
assert.match(body,/1 resident 25m/);
assert.match(body,/2 residents 3m 20s/);
assert.match(body,/3\+ residents 0s/);
assert.match(body,/3 start and 4 end receipts in this window/);
assert.match(body,/recorded run overlap, not active working time/);
''')

    def test_historical_frame_never_uses_future_endings_or_names(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',observed_at:5000,frames:[{seq:1,at:500}]};current=false;
frame={seq:40,at:1000,rooms:[],scars:[],residents:[
 {id:'a',name:'Past Resident',agent:'codex',pose:'standing'},
 {id:'b',name:'Future Resident',agent:'muse',pose:'standing'}],
 tasks:[],runs:[
 {id:'past',resident:'a',agent:'codex',start:800,sequence:20,status:'ended',end:900,outcome:'success'},
 {id:'future-end',resident:'b',agent:'muse',start:950,sequence:25,status:'ended',end:2000,outcome:'success'},
 {id:'future-start',resident:'z',agent:'agy',start:999,sequence:80,status:'launched'}]};
renderResidentPulse();
const body=pulseText();
''', r'''
assert.match(body,/remembered moment/);
assert.match(body,/Run open at this moment/);
assert.match(body,/Open and preparing runs are clipped to this frame/);
assert.doesNotMatch(body,/Future Only|future-start/);
assert.match(body,/0 residents 5m 50s/);
assert.match(body,/1 resident 2m 30s/);
''')

    def test_unsafe_names_and_claim_titles_stay_text(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',observed_at:4000,frames:[{seq:1,at:1000}]};current=true;
frame={seq:10,at:4000,rooms:[],scars:[],residents:[
 {id:'r',name:'<img src=x onerror=alert(1)>',agent:'codex',pose:'standing'}],
 tasks:[{id:'t',title:'<b>claim</b>',owner:'r',status:'claimed',until:5000,generation:0}],
 runs:[{id:'run',resident:'r',agent:'codex',start:3900,sequence:2,status:'launched'}]};
renderResidentPulse();
const body=pulseText();
const injected=pulseNodes().filter(n=>n.tag==='img'||n.tag==='b');
''', r'''
assert.match(body,/<img src=x onerror=alert\(1\)>/);
assert.match(body,/<b>claim<\/b>/);
assert.equal(injected.length,0);
''')

    def test_missing_container_and_empty_history_are_safe(self):
        self.run_renderer(r'''
flags.missing=true;
data={timezone:'Europe/London',observed_at:4000,frames:[{seq:1,at:1000}]};current=true;
frame={seq:1,at:4000,rooms:[],scars:[],residents:[],tasks:[],runs:[]};
renderResidentPulse();
assert.equal(flags.missing,true);
assert.equal(nodes['resident-pulse'],undefined);
flags.missing=false;
data={timezone:'Europe/London',observed_at:4000,frames:[]};current=true;
frame={seq:1,at:4000,rooms:[],scars:[],residents:[],tasks:[]};
renderResidentPulse();
const body=pulseText();
''', r'''
assert.match(body,/0 resident runs open/);
assert.match(body,/0 residents 0s/);
assert.match(body,/No recorded run interval overlaps this hour/);
assert.match(body,/not proof that the house was empty/);
''')

    def test_missing_export_time_falls_back_to_frame_time(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',frames:[{seq:1,at:1000}]};current=true;
frame={seq:1,at:4000,rooms:[],scars:[],residents:[],tasks:[],runs:[]};
renderResidentPulse();
const body=pulseText();
''', r'''
assert.match(body,/public snapshot at/);
assert.match(body,/0 resident runs open/);
assert.match(body,/No recorded run interval overlaps this hour/);
''')

    def test_open_receipt_is_clipped_to_snapshot_observation(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',observed_at:1000,frames:[{seq:1,at:500}]};current=true;
frame={seq:12,at:1000,rooms:[],scars:[],residents:[
 {id:'r',name:'Oriel',agent:'opencode',pose:'standing'}],tasks:[],
 runs:[{id:'open',resident:'r',agent:'opencode',start:900,sequence:2,status:'launched'}]};
renderResidentPulse();
const body=pulseText();
''', r'''
assert.match(body,/Run open/);
assert.match(body,/0 residents 6m 40s/);
assert.match(body,/1 resident 1m 40s/);
assert.match(body,/clipped to the snapshot export time/);
assert.match(body,/their full span is not confirmed/);
''')

    def test_empty_runs_do_not_imply_an_empty_house(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',observed_at:4000,frames:[{seq:1,at:1000}]};current=true;
frame={seq:9,at:4000,rooms:[],scars:[],residents:[
 {id:'keeper-01',name:'Keeper',agent:'unrecorded',room:'hearth',pose:'standing'}],
 tasks:[]};
renderResidentPulse();
const body=pulseText();
''', r'''
assert.match(body,/0 resident runs open/);
assert.match(body,/1 recorded awake outside a house run/);
assert.match(body,/0 residents 50m/);
assert.match(body,/No recorded run interval overlaps this hour/);
assert.match(body,/not proof that the house was empty/);
''')

    def test_missing_container_is_safe_before_layout_lands(self):
        self.run_renderer(r'''
flags.missing=true;
data={timezone:'Europe/London',observed_at:4000,frames:[{seq:1,at:1000}]};current=true;
frame={seq:1,at:4000,rooms:[],scars:[],residents:[],tasks:[],runs:[]};
renderResidentPulse();
''', r'''
assert.equal(flags.missing,true);
assert.equal(nodes['resident-pulse'],undefined);
''')

    def test_alerting_labels_are_rendered_as_text(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',observed_at:4000,frames:[{seq:1,at:1000}]};current=true;
frame={seq:11,at:4000,rooms:[],scars:[],residents:[
 {id:'r',name:'<script>alert(1)</script>',agent:'codex',pose:'standing'}],
 tasks:[{id:'t',title:'<img src=x>',owner:'r',status:'claimed',until:5000,generation:0}],
 runs:[{id:'run',resident:'r',agent:'codex',start:3900,sequence:2,status:'launched'}]};
renderResidentPulse();
const body=pulseText();
const injected=pulseNodes().filter(n=>['img','script','b','i'].includes(n.tag));
''', r'''
assert.match(body,/<script>alert\(1\)<\/script>/);
assert.match(body,/<img src=x>/);
assert.equal(injected.length,0);
''')

    def test_exact_model_labels_cover_helpers_fallback_and_hostile_text(self):
        self.run_renderer(r'''
data={timezone:'Europe/London',observed_at:4000,frames:[{seq:1,at:1000}]};current=true;
frame={seq:40,at:4000,rooms:[],scars:[],residents:[
 {id:'r-luna',name:'Luna',agent:'codex',room:'workshop',pose:'standing'},
 {id:'r-terra',name:'Terra',agent:'codex',room:'workshop',pose:'standing'},
 {id:'r-sol',name:'Sol',agent:'codex',room:'hearth',pose:'standing'},
 {id:'r-muse',name:'Muse Guest',agent:'muse',room:'hearth',pose:'standing'},
 {id:'r-agy',name:'Agy Guest',agent:'agy',room:'workshop',pose:'standing'},
 {id:'r-oc',name:'Oc Guest',agent:'opencode',room:'hearth',pose:'standing'}],
 tasks:[],
 runs:[
  {id:'run-luna',resident:'r-luna',agent:'codex',model:'gpt-6-luna',start:3900,sequence:2,status:'launched'},
  {id:'run-terra',resident:'r-terra',agent:'codex',model:'gpt-6.1-terra',start:3800,sequence:3,status:'launched'},
  {id:'run-sol',resident:'r-sol',agent:'codex',model:'gpt-6.1-sol',start:3850,sequence:4,status:'started'},
  {id:'run-ended-known',resident:'r-sol',agent:'codex',model:'gpt-6.1-sol',start:3700,sequence:5,status:'ended',end:3800,outcome:'success'},
  {id:'run-ended-missing',resident:'r-muse',agent:'muse',start:3600,sequence:6,status:'ended',end:3700,outcome:'success'},
  {id:'run-ended-blank',resident:'r-agy',agent:'agy',model:'   ',start:3500,sequence:7,status:'ended',end:3600,outcome:'success'},
  {id:'run-ended-hostile',resident:'r-oc',agent:'opencode',model:'<img src=x onerror=alert(1)>',start:3400,sequence:8,status:'ended',end:3500,outcome:'success'}]};
renderResidentPulse();
const body=pulseText();
const injected=pulseNodes().filter(n=>['img','script','b','i','a'].includes(n.tag));
''', r'''
assert.match(body,/3 resident runs open/);
assert.match(body,/4 recent run endings/);
assert.match(body,/3 recorded awake outside a house run/);
assert.match(body,/gpt-6-luna/);
assert.match(body,/gpt-6\.1-terra/);
assert.match(body,/gpt-6\.1-sol/);
assert.match(body,/Model unrecorded/);
assert.equal((body.match(/Model unrecorded/g)||[]).length,2);
assert.match(body,/<img src=x onerror=alert\(1\)>/);
assert.equal(injected.length,0);
assert.match(body,/Last hour:/);
assert.match(body,/dated record, not a live process check/);
''')


if __name__ == "__main__":
    unittest.main()
