"""Exercise the Beds directory with the shipped renderer and public fields."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.attrs={};this.style={};this.textContent='';}
 appendChild(n){this.children.push(n);return n;} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=v;} addEventListener(k,fn){this.listeners[k]=fn;}
 focus(){document.activeElement=this;} setSelectionRange(a,b,d){this.selectionStart=a;this.selectionEnd=b;this.selectionDirection=d;}
}
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
const root=new Element('div'),nodes={};
const document={createElement:t=>new Element(t),activeElement:null,
 getElementById:id=>all(root).find(n=>n.id===id)||nodes[id]||null};
const ctx=vm.createContext({assert,document,root,all,text,nodes,Element,Intl});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
const people=Array.from({length:14},(_,i)=>({id:'r'+i,name:'Resident '+String(i).padStart(2,'0'),
 agent:'codex',pose:i===0?'unconfirmed':'sleeping',presence:i===0?'interrupted; no sleep event':'asleep',room:i===0?'workshop':'bedroom'}));
people[0].name='Fern';people[0].name_history=[{from:'Willow',to:'Fern',sequence:20}];
const runs=Array.from({length:5},(_,i)=>({id:'run'+i,resident:'r0',sequence:10+i,last_sequence:20+i,agent:i%2?'opencode':'codex',model:'model-'+i,end:2000+i,start:1000+i,status:'ended',outcome:'success'}));
const moment=(seq,residents)=>({seq,residents,runs:runs.filter(r=>r.last_sequence<=seq),rooms:[{id:'bedroom',name:'The Beds',status:'open'},{id:'workshop',name:'The Workshop'}],tasks:[],scars:[]});
data={timezone:'UTC',frames:[moment(20,people.slice(0,7)),moment(22,people.slice(0,7)),moment(24,people)]};frame=data.frames[2];index=2;current=true;
const get=id=>document.getElementById(id),show=()=>{root.replaceChildren();renderBedsDirectory(root);};
const search=value=>{get('beds-search').value=value;get('beds-search').listeners.input();};
const vmRoomPanel=roomPanel;
render=()=>{frame=data.frames[index];show();};roomPanel=show;
lighting=()=>{};accounts=()=>{};drawHouse=()=>{};renderViewContext=()=>{};renderCollection=()=>{};renderRecentGrowth=()=>{};renderLately=()=>{};
`,ctx);
'''


@unittest.skipUnless(shutil.which('node'), 'Node executes the renderer')
class BedsDirectoryTests(unittest.TestCase):
    def run_renderer(self, checks):
        result = subprocess.run(
            ['node', '-e', HARNESS + '\nvm.runInContext(' + repr(checks) + ',ctx);',
             str(ROOT / 'site/house.js')], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_search_alias_reset_paging_and_unchanged_bunks(self):
        self.run_renderer(r'''
const before=JSON.stringify(frame),bunks=JSON.stringify(dormView(frame,1));show();
assert.equal(all(root).filter(n=>n.className==='beds-person').length,6);
assert.match(text(get('beds-results')),/14 of 14.*page 1 of 3/);assert(get('beds-previous').disabled);
get('beds-next').listeners.click();assert.equal(document.activeElement,get('beds-list'));
get('beds-next').listeners.click();assert(get('beds-next').disabled);
assert.equal(all(root).filter(n=>n.className==='beds-person').length,2);
search('  WiLLoW  ');assert.match(text(get('beds-results')),/1 of 14/);
assert.match(text(root),/Fern.*Earlier names: Willow/s);assert.match(text(root),/stopped without sleep/);
search('unknown');assert.match(text(root),/No name matches/);assert(get('beds-next').disabled);
get('beds-reset').listeners.click();assert.equal(document.activeElement,get('beds-search'));
assert.equal(get('beds-search').value,'');assert.equal(bedsState.page,0);
assert.equal(JSON.stringify(frame),before);assert.equal(JSON.stringify(dormView(frame,1)),bunks);
''')

    def test_historical_run_bounds_event_jump_and_safe_names(self):
        self.run_renderer(r'''
show();search('fern');assert.equal(all(root).filter(n=>n.className==='beds-run').length,5);
assert.equal(all(root).filter(n=>n.tag==='button'&&n.id?.startsWith('beds-event-')).length,3);
assert.match(text(root),/Codex · model-0 run0/);
assert.match(text(root),/Codex · model-4 run4/);
assert.match(text(root),/OpenCode · model-3 run3/);
assert.match(text(root),/Started.*event 10/s);assert.match(text(root),/end receipt.*event 24/s);
assert.match(text(root),/r0/);assert.match(text(root),/Willow → Fern.*event 20/);
// Receipt 23 is absent from this bounded fixture, so it has no fabricated jump.
get('beds-event-end-run2').listeners.click();assert.equal(frame.seq,22);assert.equal(current,false);
assert.equal(document.activeElement,get('beds-name-r0'));assert.match(text(get('beds-results')),/1 of 7/);
assert.equal(get('beds-event-end-run4'),null);assert.equal(get('beds-event-end-run3'),null);
frame.residents=[{...people[0],name:'<img src=x>',name_history:[]}];bedsState.query='';show();
assert.match(text(root),/<img src=x>/);assert(!all(root).some(n=>n.tag==='img'));
frame.residents=[];show();assert.match(text(get('beds-results')),/0 of 0.*page 1 of 1/);
assert(get('beds-next').disabled);assert(get('beds-previous').disabled);
''')

    def test_start_result_and_unfinished_receipts(self):
        self.run_renderer(r'''
// Add a visitable start and retain a result receipt while the run is still open.
data.frames.unshift({...data.frames[0],seq:10});
frame.runs[4]={...frame.runs[4],status:'running',outcome:'failed'};
frame.runs[3]={...frame.runs[3],status:'running',outcome:'unconfirmed',end:null};
show();search('fern');assert.match(text(root),/result receipt.*event 24/s);
assert(get('beds-event-result-run4'));assert.equal(get('beds-event-end-run4'),null);
assert.equal(get('beds-event-result-run3'),null);assert.match(text(root),/no end receipt/);
get('beds-event-start-run0').listeners.click();assert.equal(frame.seq,10);
assert.equal(document.activeElement,get('beds-name-r0'));
frame.runs=[];show();assert.match(text(root),/No supervised run receipts/);
assert.equal(all(root).filter(n=>n.className==='beds-run').length,0);
''')

    def test_room_gate_and_both_refresh_paths_keep_navigation(self):
        self.run_renderer(r'''
for(const id of ['room-content','room-kicker','room-title','room-description','room-context']){
 nodes[id]=new Element('div');nodes[id].id=id;
}
const actualPanel=vmRoomPanel;
selected='bedroom';actualPanel();assert.match(text(nodes['room-content']),/Find a resident/);
for(const status of ['closed','construction']){
 frame.rooms[0].status=status;actualPanel();assert.doesNotMatch(text(nodes['room-content']),/Find a resident/);
}
frame.rooms[0].status='open';show();search('fern');
const card=get('beds-person-r0');card.open=true;card.listeners.toggle();
get('beds-event-end-run0').focus();refreshView();
assert.equal(document.activeElement,get('beds-event-end-run0'));
refreshView(true);assert.equal(document.activeElement,get('beds-event-end-run0'));
''')

    def test_refresh_preserves_neighboring_room_focus_and_search_selection(self):
        self.run_renderer(r'''
for(const changed of [false,true]) {
 for(const id of ['hearth-search','chronicle-next','gallery-search']) {
  nodes[id]=new Element('input');nodes[id].id=id;nodes[id].focus();
  nodes[id].setSelectionRange(1,4,'backward');
  const redraw=()=>{nodes[id]=new Element('input');nodes[id].id=id;};
  roomPanel=render=redraw;refreshView(changed);
  assert.equal(document.activeElement,nodes[id],id);
  if(id.endsWith('-search')) {
   assert.equal(nodes[id].selectionStart,1,id);assert.equal(nodes[id].selectionEnd,4,id);
   assert.equal(nodes[id].selectionDirection,'backward',id);
  }
 }
}
''')

    def test_refresh_retains_query_selection_and_open_resident(self):
        self.run_renderer(r'''
show();search('fern');const card=get('beds-person-r0');card.open=true;card.listeners.toggle();
const input=get('beds-search');input.focus();input.setSelectionRange(1,3,'backward');
refreshView();assert.equal(document.activeElement,get('beds-search'));
assert.equal(get('beds-search').value,'fern');assert.equal(get('beds-search').selectionStart,1);
assert.equal(get('beds-search').selectionEnd,3);assert.equal(get('beds-search').selectionDirection,'backward');
assert(get('beds-person-r0').open);
refreshView(true);assert.equal(get('beds-search').value,'fern');assert(get('beds-person-r0').open);
''')


if __name__ == '__main__':
    unittest.main()
