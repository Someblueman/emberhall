"""Exercise the published house renderer, including its keyboard focus contract."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site/house.js"
HARNESS = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.listeners={};this.dataset={};
  this.style={};this.textContent='';this.className='';this.id='';this.classList={toggle(){},add(){},remove(){}};}
 appendChild(n){this.children.push(n);return n;}
 replaceChildren(){if(all(this).includes(document.activeElement))document.activeElement=document.body;this.children=[];}
 set innerHTML(v){throw Error('Use safe text');}
 setAttribute(k,v){this.attrs[k]=String(v);if(k==='id')this.id=v;}
 removeAttribute(k){delete this.attrs[k];}
 addEventListener(k,fn){this.listeners[k]=fn;}
 focus(){if(!this.disabled)document.activeElement=this;}
 scrollIntoView(){this.scrolled=true;}
 click(){this.focus();this.listeners.click?.({target:this});}
 change(value){this.value=value;this.focus();this.listeners.change({target:this});}
 querySelectorAll(){return [];}
}
const nodes={},document={body:new Element('body'),activeElement:null,
 getElementById(id){const found=Object.values(nodes).flatMap(all).find(n=>n.id===id);
  if(found)return found;if(id.startsWith('workshop-'))return null;
  const node=new Element('div');node.id=id;return nodes[id]=node;},
 createElement:t=>new Element(t),createElementNS:(ns,t)=>new Element(t),querySelectorAll:()=>[]};
const context=vm.createContext({assert,document,nodes,text,all,Date,URL});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
const fixture=JSON.parse(fs.readFileSync(0,'utf8')||'null');context.fixture=fixture;
vm.runInContext(`
data={timezone:'UTC',frames:[]};selected='workshop';current=false;
const panel=()=>$('room-content'),cards=()=>all(panel()).filter(n=>n.className.startsWith('workshop-task'));
const events=()=>all(panel()).filter(n=>n.className==='workshop-event');
const button=label=>all(panel()).find(n=>n.tag==='button'&&n.textContent===label);
const draw=tasks=>{frame={seq:10,at:1000,rooms:[{id:'workshop',name:'Workshop'}],residents:[],runs:[],scars:[],tasks};roomPanel();};
`,context);
'''


class RendererMixin:
    def run_renderer(self, code, fixture=None):
        script = HARNESS + "\nvm.runInContext(" + json.dumps(code) + ",context);"
        result = subprocess.run(
            [shutil.which("node"), "-e", script, str(SOURCE)],
            input=json.dumps(fixture), capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


@unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
class WorkshopUITests(RendererMixin, unittest.TestCase):
    def test_queue_project_and_owner_unknowns_are_not_invented(self):
        self.run_renderer(r'''
frame={};data.frames=[];
draw([
 {id:'ready',title:'Build ferry',status:'open',ready:true,project:'ferry'},
 {id:'blocked',title:'Repair',status:'open',ready:false},
 {id:'unknown',title:'Ordinary',status:'open',ready:null},
 {id:'claimed',title:'Claimed work',status:'claimed',owner:'mallow',until:3000}
]);
frame.residents=[{id:'mallow',name:'Mallow',room:'hearth',pose:'standing'}];
frame.shelf={projects:[{id:'ferry',title:'Night Ferry'}]};roomPanel();
assert.equal(cards().length,4);
assert.match(text(panel()),/4 unfinished · 0 finished/);
assert.match(text(panel()),/Recorded claim · Mallow/);
assert.match(text(panel()),/Declared ready/);assert.match(text(panel()),/Not queued/);
assert.match(text(panel()),/Readiness unknown \(unrecorded\)/);
assert.match(text(panel()),/Project: Night Ferry/);
$('workshop-readiness').change('ready');assert.equal(cards().length,1);
assert.equal(document.activeElement.id,'workshop-readiness');
assert.match(text(cards()[0]),/Build ferry/);
$('workshop-readiness').change('not-queued');assert.equal(cards().length,1);
$('workshop-filter').change('claimed');assert.equal(cards().length,0);
assert.match(text(panel()),/No work matches/);
''')

    def test_compact_groups_pagination_and_nearby_selection_keep_focus(self):
        self.run_renderer(r'''
draw(Array.from({length:13},(_,i)=>({id:'work-'+i,title:'Work '+i,status:'open',ready:true})));
assert.equal(cards().length,4);assert.match(text(panel()),/Unassigned · 13/);
$('workshop-unassigned-Next').click();assert.equal(cards().length,4);
assert.equal(document.activeElement.id,'workshop-pages-unassigned');
assert.match(text(panel()),/5–8 of 13/);
const card=cards()[0];card.click();
assert.equal(document.activeElement.id,'workshop-detail');assert($('workshop-detail').scrolled);
const children=all(panel());assert(children.indexOf($('workshop-detail'))<children.indexOf(cards()[0]));
assert.match(text($('workshop-detail')),/Individual handoffs are not exposed/);
button('Find task card').click();assert.equal(document.activeElement.id,card.id);
$('workshop-filter').change('done');assert.equal(cards().length,0);
button('Find task card').click();assert.equal(document.activeElement.id,card.id);
''')

    def test_old_empty_and_hostile_snapshots_render_only_safe_text(self):
        self.run_renderer(r'''
draw([]);assert.match(text(panel()),/No tasks are exposed/);assert.equal(cards().length,0);
draw([{id:'xss',title:'<img src=x onerror=alert(1)>',status:'open',description:'private-desc',token:'private-token'}]);
assert.equal(cards().length,1);cards()[0].click();
assert.equal(all(panel()).filter(n=>n.tag==='img').length,0);
assert.match(text(panel()),/Readiness unknown/);
assert.doesNotMatch(text(panel()),/private-desc|private-token/);
draw([]);assert.match(text(panel()),/No work matches/);
assert.match(text(panel()),/Selected task not yet recorded/);
assert.doesNotMatch(text(panel()),/onerror/);
''')

    def test_refresh_preserves_workshop_selection_and_keyboard_focus(self):
        self.run_renderer(r'''
draw([{id:'one',title:'One',status:'open'}]);cards()[0].click();
const before=workshopState.selectedId;
// Refresh's other house panels are outside this focused DOM boundary.
lighting=accounts=drawHouse=renderViewContext=renderCollection=renderRecentGrowth=()=>{};
$('workshop-readiness').focus();refreshView();
assert.equal(workshopState.selectedId,before);
assert.equal(document.activeElement.id,'workshop-readiness');
''')


if __name__ == "__main__":
    unittest.main()
