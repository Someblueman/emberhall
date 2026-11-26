"""Exercise the Chronicle reader against the real page script."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node executes the page renderer")
class ChronicleRoomReaderTests(unittest.TestCase):
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
const root=new Element('div'),nodes={};
const get=id=>all(root).find(n=>n.id===id)||nodes[id]||null;
const card=new Element('section');
const document={activeElement:null,createElement:t=>new Element(t),getElementById:get,
 querySelector:s=>s==='.room-card'?card:null};
const ctx=vm.createContext({assert,document,root,all,text,get,card,nodes,Element});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
const event=(sequence,kind='room-open')=>({sequence,kind,at:1000+sequence,name:'Room '+sequence,actor:'r',purpose:'A place for reading',reason:'Build a place to read' });
const rooms=[{id:'chronicle',name:'Chronicle',status:'open'},
 {id:'study',name:'Study',history:[event(2,'room-plan'),event(3),event(5,'room-close'),event(6,'room-repurpose'),event(7),event(8),event(9)]},
 {id:'archive',name:'Archive',history:[event(4)]},{id:'door',name:'Door'}];
frame={seq:8,rooms,residents:[{id:'r',name:'Rowan'}],scars:[],tasks:[],runs:[]};
data={timezone:'UTC',frames:[{seq:2},{seq:3},{seq:8}],commits:[]};
const before=JSON.stringify(frame);
const change=(id,value)=>{get(id).value=value;get(id).listeners.change();};
const draw=()=>{root.replaceChildren();renderChronicleRoom(root);};
let visitedRoom=null,visitedSequence=null;
choose=id=>{visitedRoom=id;};jumpToSequence=(seq,afterJump)=>{visitedSequence=seq;afterJump?.();};
`,ctx);
        vm.runInContext(process.argv[2],ctx);
'''
        result = subprocess.run(
            [shutil.which("node"), "-e", script, str(Path(__file__).parents[1] / "site/house.js"), checks],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_filters_order_paging_and_event_visits(self):
        self.run_js(r'''
draw();assert.match(text(root),/7 of 7 recorded changes.*1–5 shown.*latest change first/);
assert.equal(all(root).filter(n=>n.tag==='article').length,5);
assert.equal(all(root).find(n=>n.tag==='h4').textContent,'Room opened · Room 8');
assert.doesNotMatch(text(root),/Room 2|Room 9/);
assert.match(text(root),/no visitable frame/);
get('chronicle-next').listeners.click();assert.equal(document.activeElement.id,'chronicle-entries');
assert.match(text(root),/6–7 shown/);assert.equal(get('chronicle-next').disabled,true);
change('chronicle-order','oldest');assert.match(text(root),/1–5 shown.*first change first/);
assert.equal(all(root).find(n=>n.tag==='h4').textContent,'Building began · Room 2');
get('chronicle-visit-study-2').listeners.click();
assert.equal(visitedRoom,'study');assert.equal(visitedSequence,2);assert.equal(document.activeElement,card);
change('chronicle-room','archive');assert.match(text(root),/1 of 7 recorded changes/);
assert.equal(get('chronicle-next').disabled,true);assert.equal(all(root).filter(n=>n.tag==='article').length,1);
assert.doesNotMatch(text(root),/Room 2|Room 8/);assert.equal(JSON.stringify(frame),before);
change('chronicle-room','door');assert.match(text(root),/No room changes.*No opening date is guessed/);
''')

    def test_earlier_frames_missing_dates_and_literal_text(self):
        self.run_js(r'''
rooms[1].history.push(event(0),event(-1),event(2.5),event(3,'unknown'));
rooms[1].history[0].name='<img src=x onerror=alert(1)>';
rooms[1].history[0].purpose='<script>not executable</script>';rooms[1].history[0].at=null;
frame.seq=2;draw();assert.match(text(root),/1 of 1 recorded changes/);
assert.match(text(root),/date unrecorded/);assert.match(text(root),/<img src=x/);
assert.match(text(root),/<script>not executable/);assert(!all(root).some(n=>['img','script'].includes(n.tag)));
assert.doesNotMatch(text(root),/Room opened|Room 9/);
change('chronicle-room','study');frame.rooms=[rooms[0],rooms[3]];draw();
assert.equal(get('chronicle-room').value,'all');assert.match(text(root),/0 of 0 recorded changes/);
assert.doesNotMatch(text(root),/Room 9|not executable/);
''')

    def test_building_trail_uses_viewed_tasks_and_returns_to_exact_story(self):
        self.run_js(r'''
rooms.push({id:'workshop',name:'Workshop',status:'open',floor:1});
rooms[1].history[0].task='build-study';rooms[1].history[1].task='absent';
frame.tasks=[{id:'build-study',plain:'Make a place to read.',title:'internal',status:'done'}];
data.frames=[frame,{seq:99,rooms,tasks:[{id:'absent',title:'FUTURE SECRET',status:'done'}]}];
index=0;current=false;const beforeTrail=JSON.stringify(data);draw();
change('chronicle-room','study');change('chronicle-order','oldest');
assert.match(text(root),/Building work: Make a place to read.*Finished/);
assert.doesNotMatch(text(root),/acceptance and delivery unknown/);
assert.match(text(root),/State at this viewed moment/);assert.match(text(root),/details are absent/);
assert.match(text(root),/No building task was recorded/);assert.doesNotMatch(text(root),/FUTURE SECRET/);
const reason=all(root).find(n=>n.tag==='details');reason.open=true;reason.listeners.toggle();
const follow=get('chronicle-work-study-2');follow.listeners.click();
assert.equal(visitedRoom,'workshop');assert.equal(selectedFloor,1);
assert.equal(workshopState.selectedId,'build-study');assert.equal(frame.seq,8);assert.equal(current,false);
assert.equal(chronicleWorkTrail.target,follow.id);
root.replaceChildren();renderChronicleReturn(root);assert(get('workshop-room-story'));
// Following an earlier task handoff must not lose the original story, filter or page.
frame={seq:1,rooms:[]};chronicleState.room='all';chronicleState.page=0;chronicleState.opened.clear();
chronicleWorkTrail.current=true; // A newer publication must not turn the old story into Latest.
render=draw;get('workshop-room-story').listeners.click();
assert.equal(frame.seq,8);assert.equal(index,0);assert.equal(current,false);
assert.equal(visitedRoom,'chronicle');assert.equal(selectedFloor,0);
assert.equal(chronicleState.room,'study');assert.equal(chronicleState.order,'oldest');
assert.equal(document.activeElement.id,follow.id);assert.equal(JSON.stringify(data),beforeTrail);
assert.equal(all(root).find(n=>n.tag==='details').open,true);
rooms[1].history[5].task='build-study';draw();change('chronicle-room','all');
change('chronicle-order','oldest');get('chronicle-next').listeners.click();
get('chronicle-work-study-8').listeners.click();root.replaceChildren();renderChronicleReturn(root);
get('workshop-room-story').listeners.click();assert.equal(chronicleState.page,1);
assert.equal(document.activeElement.id,'chronicle-work-study-8');
workshopState.selectedId='different';root.replaceChildren();renderChronicleReturn(root);
assert(!get('workshop-room-story'));
workshopState.selectedId='build-study';data.frames=[];renderChronicleReturn(root);
assert.match(text(root),/original moment is absent/);assert(!get('workshop-room-story'));
// Missing/closed Workshop and hostile titles never create links or executable markup.
data.frames=[frame];chronicleState.page=0;rooms.at(-1).status='closed';frame.tasks[0].plain='<script>literal</script>';draw();
assert.match(text(root),/Workshop is not open/);assert(!get('chronicle-work-study-2'));
assert.match(text(root),/<script>literal<\/script>/);assert(!all(root).some(n=>n.tag==='script'));
''')

    def test_room_gate_and_refresh_preserve_filters_page_and_focus(self):
        self.run_js(r'''
for(const id of ['room-content','room-kicker','room-title','room-description','room-context']){
 nodes[id]=new Element('div');nodes[id].id=id;
}
// Use the real room gate, then capture the reader root for the refresh test.
selected='chronicle';roomPanel();assert.match(text(nodes['room-content']),/How the house grew/);
for(const status of ['closed','construction']){
 rooms[0].status=status;roomPanel();assert.doesNotMatch(text(nodes['room-content']),/How the house grew/);
}
rooms[0].status='open';draw();get('chronicle-next').listeners.click();get('chronicle-order').focus();
render=draw;refreshView(true);
assert.equal(document.activeElement,get('chronicle-order'));assert.match(text(root),/6–7 shown/);
change('chronicle-room','study');change('chronicle-order','oldest');get('chronicle-room').focus();
const reason=all(root).find(n=>n.tag==='details');reason.open=true;reason.listeners.toggle();
get('chronicle-reason-study-2').focus();refreshView(true);
assert.equal(document.activeElement,get('chronicle-reason-study-2'));
assert.equal(all(root).find(n=>n.tag==='details').open,true);
get('chronicle-room').focus();refreshView(true);assert.equal(document.activeElement,get('chronicle-room'));
assert.equal(get('chronicle-room').value,'study');assert.equal(get('chronicle-order').value,'oldest');
assert.match(text(root),/6 of 7 recorded changes/);
''')


if __name__ == "__main__":
    unittest.main()
