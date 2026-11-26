"""Follow a real public task history from a run and return to its ledger place."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node executes the page renderer")
class CountingWorkTrailTests(unittest.TestCase):
    def run_js(self, checks):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.style={};this.textContent='';}
 appendChild(n){this.children.push(n);return n;} replaceChildren(){this.children=[];}
 setAttribute(k,v){this[k]=v;} addEventListener(k,fn){this.listeners[k]=fn;}
 focus(){document.activeElement=this;} scrollIntoView(){}
}
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
const root=new Element('div'),nodes={},get=id=>all(root).find(n=>n.id===id)||nodes[id]||null;
const document={activeElement:null,createElement:t=>new Element(t),getElementById:get};
const ctx=vm.createContext({assert,document,root,all,text,get,nodes,Element});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
const rooms=[{id:'counting',name:'Counting',status:'open',floor:0},
 {id:'workshop',name:'Workshop',status:'open',floor:1}];
const base={rooms,residents:[{id:'r',name:'Rowan'}],scars:[],budgets:[],ambitions:[],runs:[],tasks:[]};
const created={...base,seq:1,at:1001,event:{op:'task',title:'Internal title'},
 tasks:[{id:'build',plain:'Make a place to read <literally>.',status:'open'}]};
const finished={...base,seq:2,at:1002,event:{op:'finish',actor:'r',title:'build'}};
const runs=Array.from({length:10},(_,i)=>({id:'run '+i,resident:'r',agent:'codex',model:'fixture-'+i,
 sequence:i+3,assignment:{lane:'work'},outcome:'success',finished_tasks:i===0?[{task:'build',sequence:2}]:[]}));
frame={...base,seq:20,at:1020,event:{op:'say'},runs};
data={timezone:'UTC',frames:[created,finished,frame],commits:[]};index=2;current=true;
observationTime=()=>frame.at;
const change=(id,value)=>{get(id).value=value;get(id).listeners.change();};
const draw=()=>{root.replaceChildren();renderCountingRoom(root);};roomPanel=draw;
let visitedRoom=null;
choose=id=>{visitedRoom=id;};
render=()=>{root.replaceChildren();if(visitedRoom==='workshop')renderWorkshopTasks(root);else draw();};
const followId='counting-work-run%200-2';
const follow=()=>{draw();get('counting-next').listeners.click();get(followId).listeners.click();};
`,ctx);
vm.runInContext(process.argv[2],ctx);
'''
        result = subprocess.run(
            ["node", "-e", script, str(Path(__file__).parents[1] / "site/house.js"), checks],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_round_trip_restores_page_filters_disclosures_and_exact_moment(self):
        self.run_js(r'''
countingState={agent:'codex',lane:'work',page:0};const before=JSON.stringify(data);
chronicleWorkTrail={task:'build'};follow();
assert.equal(visitedRoom,'workshop');assert.equal(selectedFloor,1);
assert.equal(workshopState.selectedId,'build');assert.equal(frame.seq,20);assert.equal(current,true);
assert.equal(chronicleWorkTrail,null);assert(countingWorkTrail.opened.has('run 0'));
render();assert(get('workshop-run-ledger'));assert.match(text(root),/Make a place to read <literally>/);
assert.match(text(root),/Created.*Finished/);assert(!all(root).some(n=>n.tag==='literally'));
// An event visit and a later publication must not turn the origin into Latest.
frame=created;index=0;current=false;countingState={agent:'all',lane:'all',page:0};countingHandoffsOpen.clear();
data.frames.push({...base,seq:30,at:1030});render();get('workshop-run-ledger').listeners.click();
assert.equal(frame.seq,20);assert.equal(index,2);assert.equal(current,false);
assert.equal(visitedRoom,'counting');assert.equal(selectedFloor,0);
assert.equal(countingState.agent,'codex');assert.equal(countingState.lane,'work');assert.equal(countingState.page,1);
assert(countingHandoffsOpen.has('run 0'));assert.equal(document.activeElement.id,followId);
assert(all(root).find(n=>n.tag==='details').open);data.frames.pop();assert.equal(JSON.stringify(data),before);
// A normal redraw keeps the return link and original trail; an unrelated task hides it.
visitedRoom='workshop';root.replaceChildren();renderCountingReturn(root);assert(get('workshop-run-ledger'));
workshopState.selectedId='other';root.replaceChildren();renderCountingReturn(root);assert(!get('workshop-run-ledger'));
''')

    def test_missing_or_closed_rooms_and_unretained_tasks_offer_no_dead_trip(self):
        self.run_js(r'''
for(const status of ['closed','construction']){
 rooms[1].status=status;draw();get('counting-next').listeners.click();
 assert(!get(followId));assert.match(text(root),/Workshop is not open/);
}
rooms.pop();draw();get('counting-next').listeners.click();assert(!get(followId));
rooms.push({id:'workshop',status:'open'});
// A receipt alone cannot fabricate the task history. Future data cannot fill the gap.
created.tasks=[];data.frames.push({...base,seq:30,tasks:[{id:'build',plain:'FUTURE SECRET'}]});
draw();get('counting-next').listeners.click();assert(!get(followId));
assert.match(text(root),/task's history is absent/);assert.doesNotMatch(text(root),/FUTURE SECRET/);
''')

    def test_return_needs_the_original_room_and_preserves_historical_mode(self):
        self.run_js(r'''
current=false;follow();root.replaceChildren();renderCountingReturn(root);
get('workshop-run-ledger').listeners.click();assert.equal(current,false);
root.replaceChildren();renderCountingReturn(root);rooms[0].status='closed';
root.replaceChildren();renderCountingReturn(root);assert(!get('workshop-run-ledger'));
assert.match(text(root),/original moment is absent/);rooms[0].status='open';
data.frames=[];root.replaceChildren();renderCountingReturn(root);assert(!get('workshop-run-ledger'));
assert.match(text(root),/original moment is absent/);
''')

    def test_refresh_keeps_the_return_control_and_ledger_target_focused(self):
        self.run_js(r'''
document.querySelectorAll=()=>[];follow();render();get('workshop-run-ledger').focus();
refreshView(true);assert.equal(document.activeElement.id,'workshop-run-ledger');
assert.equal(document.activeElement,get('workshop-run-ledger'));
get('workshop-run-ledger').listeners.click();refreshView(true);
assert.equal(document.activeElement.id,followId);assert.equal(document.activeElement,get(followId));
assert.equal(countingState.page,1);assert(countingHandoffsOpen.has('run 0'));
''')


if __name__ == "__main__":
    unittest.main()
