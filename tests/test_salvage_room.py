"""The real room renderer rehearses the retained Blackout Kit fixture."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
DRILL = ROOT / "projects/blackout/examples/recovery-drill"


@unittest.skipUnless(shutil.which("node"), "Node runs the shipped renderer")
class SalvageRoomTests(unittest.TestCase):
    def run_js(self, checks):
        harness = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.listeners={};this.style={};this.attrs={};}
 appendChild(n){this.children.push(n);return n;} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=String(v);} addEventListener(k,fn){this.listeners[k]=fn;}
 focus(){document.activeElement=this;}
}
const root=new Element('div'),nodes={};
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
const document={createElement:t=>new Element(t),activeElement:null,
 createElementNS:(_,t)=>new Element(t),
 getElementById:id=>all(root).find(n=>n.id===id)||(nodes[id]??=new Element('div'))};
const ctx=vm.createContext({assert,document,root,nodes,all,text,JSON});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
const find=id=>all(root).find(n=>n.id===id),click=id=>find(id).listeners.click();
`,ctx);
vm.runInContext(process.argv[2],ctx);
'''
        proc = subprocess.run(["node", "-e", harness, str(ROOT / "site/house.js"), checks],
                              capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_practice_matches_actual_fixture_bytes_and_plan(self):
        plan = json.loads((DRILL / "expected-plan.json").read_text())
        manifest = json.loads((DRILL / "manifest.json").read_text())
        hashes = {f["path"]: f["sha256"][:12] for f in manifest["files"]}
        surviving = {p.relative_to(DRILL / "surviving").as_posix():
                     hashlib.sha256(p.read_bytes()).hexdigest()[:12]
                     for p in (DRILL / "surviving").rglob("*") if p.is_file()}
        self.run_js(f'''
const expected={json.dumps(plan['restores'])},hashes={json.dumps(hashes)},surviving={json.dumps(surviving)};
assert.equal(salvageCases.length,expected.length);
for(const item of salvageCases){{
 const real=expected.find(r=>r.target===item.target);assert(real);
 assert.deepEqual(item.candidates,real.candidates);assert.equal(item.status,real.status);
 assert.equal(item.hash,hashes[item.target]);
 for(const path of item.candidates)assert.equal(surviving[path],item.hash);
 assert.equal(item.decoyHash,surviving[item.decoy]);assert.notEqual(item.decoyHash,item.hash);
}}
''')

    def test_choices_ambiguity_loss_completion_reset_and_refresh(self):
        self.run_js(r'''
renderSalvageRoom(root);
// Before the visitor acts the line invites them; it must not read as unchecked resident work.
assert.match(text(root),/Your turn: 6 practice files are waiting for your decision/);
assert.doesNotMatch(text(root),/0 of 6/);
assert.doesNotMatch(text(root),/decisions checked/);
assert.match(text(root),/your own exercise, not work done by the residents/);
click('salvage-choice-1');assert.match(find('salvage-result').textContent,/Look again/);
assert.match(text(root),/Your practice: 0 of 6 decisions right · 1 to look at again/);
click('salvage-choice-0');assert.match(find('salvage-result').textContent,/survived a rename/);
assert.equal(document.activeElement.id,'salvage-choice-0');
assert.match(text(root),/Your practice: 1 of 6 decisions right/);
assert.equal(find('salvage-file-0').attrs['aria-label'],'family/winter.txt, practice file 1, you chose correctly');
assert.equal(find('salvage-file-1').attrs['aria-label'],'records/invoice.txt, practice file 2');
for(let i=1;i<6;i++){
 click('salvage-file-'+i);
 const entry=salvageCases[i];
 if(i===2){
  click('salvage-choice-0');assert.match(find('salvage-result').textContent,/origin is right/);
  click('salvage-choice-1');assert.match(find('salvage-result').textContent,/Preserve both/);
 }else click('salvage-choice-'+(entry.candidates.length?0:1));
}
assert.match(text(root),/Your practice: 6 of 6 decisions right/);
assert.match(find('salvage-result').textContent,/7 of 9 files.*2 remain missing/);
root.replaceChildren();renderSalvageRoom(root);assert.match(text(root),/6 of 6/);
click('salvage-next');assert.equal(document.activeElement.id,'salvage-file-0');
click('salvage-reset');assert.match(text(root),/Your turn: 6 practice files are waiting/);assert.doesNotMatch(text(root),/0 of 6/);
assert.equal(document.activeElement.id,'salvage-reset');
assert.equal(find('salvage-choice-0').attrs['aria-pressed'],'false');
// Text remains text, even if a future fixture contains markup-like names.
salvageCases[0].target='<img src=x onerror=alert(1)>';
root.replaceChildren();renderSalvageRoom(root);
assert.match(text(root),/<img src=x/);assert(!all(root).some(n=>n.tag==='img'));
''')

    def test_panel_requires_recorded_open_room_and_does_not_mutate_history(self):
        self.run_js(r'''
nodes['room-content']=root;
roomFact=()=>'';roomRecord=()=>{};visibleScars=()=>[];
data={timezone:'UTC'};selected='salvage';current=false;
frame={rooms:[{id:'salvage',name:'The Salvage Room',status:'construction'}],residents:[],tasks:[]};
roomPanel();assert(!find('salvage-reset'));
frame.rooms[0].status='closed';roomPanel();assert(!find('salvage-reset'));
frame.rooms[0].status='open';const before=JSON.stringify(frame);
roomPanel();assert(find('salvage-reset'));click('salvage-choice-0');
const picture=document.createElement('g');furnishings(picture,'salvage',0,0,false,[]);
assert(all(picture).some(n=>n.attrs['data-interior']==='salvage'));
assert.match(text(picture),/invented archive/);
assert.equal(JSON.stringify(frame),before);
assert.match(text(root),/invented files/);
frame.rooms=[];roomPanel();assert(!find('salvage-reset'));
''')
