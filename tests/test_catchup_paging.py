"""Run the real catch-up JavaScript with a small DOM; browser checks are separate."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node runs the catch-up renderer")
class CatchupPagingTests(unittest.TestCase):
    def run_js(self, checks):
        source = Path(__file__).parents[1] / "site/house.js"
        harness = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.listeners={};this.style={};}
  appendChild(node){this.children.push(node);return node;}
  replaceChildren(){this.children=[];}
  setAttribute(key,value){this[key]=value;}
  addEventListener(key,fn){this.listeners[key]=fn;}
  focus(){document.activeElement=this;}
  scrollIntoView(){}
}
const all=node=>[node,...node.children.flatMap(all)];
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const root=new Element('div'),document={activeElement:null,createElement:tag=>new Element(tag),
  getElementById:id=>all(root).find(node=>node.id===id)||null};
const find=id=>document.getElementById(id),click=id=>find(id).listeners.click();
const ctx=vm.createContext({assert,document,root,all,text,find,click,URL});
const code=fs.readFileSync(process.argv[1],'utf8');
vm.runInContext(code.slice(0,code.indexOf('function roomPanel()')),ctx);
vm.runInContext(`
data={frames:[]};
for(let i=1;i<=18;i++){
 const task={id:'task-'+i,title:'Task '+i,plain:i===18?'<img src=x onerror=alert(1)>':'Finished work '+i};
 const room={id:'parlor',name:'Parlor '+i,status:i%2?'open':'closed'};
 const project={id:'project-'+i,title:'Project '+i,status:'done'};
 data.frames.push({seq:i*2-1,at:i*2-1,event:{op:'task'},tasks:[task],rooms:[room],shelf:{projects:[]}});
 data.frames.push({seq:i*2,at:i*2,event:{op:'finish',title:task.id},tasks:[],rooms:[room],shelf:{projects:[project]}});
}
index=data.frames.length-1;current=true;catchupStartSeq=1;
roomPanel=()=>{root.replaceChildren();renderCatchupPanel(root);};
render=()=>{frame=data.frames[index];roomPanel();};
roomPanel();
`,ctx);
vm.runInContext(process.argv[2],ctx);
'''
        result = subprocess.run([shutil.which("node"), "-e", harness, str(source), checks],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_every_group_reaches_every_item_and_pages_independently(self):
        self.run_js(r'''
for(const section of [0,1,2]){
 const list=()=>find('catchup-list-'+section);
 assert.equal(list().children.length,8);
 assert(find('catchup-previous-'+section).disabled);
 assert.match(find('catchup-range-'+section).textContent,/1–8 of 18/);
 click('catchup-next-'+section);assert.equal(list().children.length,8);
 assert.equal(document.activeElement,list());
 assert.match(find('catchup-range-'+section).textContent,/9–16 of 18/);
 click('catchup-next-'+section);assert.equal(list().children.length,2);
 assert(find('catchup-next-'+section).disabled);
 assert.match(find('catchup-range-'+section).textContent,/17–18 of 18/);
 click('catchup-previous-'+section);
 assert.match(find('catchup-range-'+section).textContent,/9–16 of 18/);
}
assert.equal(all(root).filter(n=>n.tag==='img').length,0);
click('catchup-next-0');assert.match(text(find('catchup-list-0')),/<img src=x/);
assert.match(find('catchup-range-1').textContent,/9–16 of 18/);
roomPanel();assert.match(find('catchup-range-0').textContent,/17–18 of 18/);
assert.equal(find('catchup-next-0')['aria-controls'],'catchup-list-0');
assert.equal(find('catchup-list-0')['aria-label'],'Completed tasks');
// Two rooms at the initial event must have distinct focus-restoration IDs.
data.frames[0].rooms.push({id:'another',name:'Another room',status:'open'});
catchupPages[1]=0;roomPanel();
const roomJumps=all(find('catchup-list-1')).filter(n=>n.tag==='button');
assert.equal(new Set(roomJumps.map(n=>n.id)).size,roomJumps.length);
assert.equal(roomJumps[0].id,'catchup-jump-1-1-0');
assert.equal(roomJumps[1].id,'catchup-jump-1-1-1');
''')

    def test_range_changes_and_historical_bounds(self):
        self.run_js(r'''
click('catchup-next-0');click('catchup-next-1');click('catchup-next-2');
find('catchup-seq').value='31';click('catchup-apply');
for(const section of [0,1,2]){
 assert.match(find('catchup-range-'+section).textContent,/1–3 of 3/);
 assert(find('catchup-pages-'+section).hidden);
 assert.equal(find('catchup-pages-'+section).style,'display:none');
}
click('catchup-reset');assert.match(find('catchup-range-0').textContent,/1–8 of 18/);
click('catchup-next-0');click('catchup-next-0');
index=3;current=false;roomPanel();
assert.match(find('catchup-range-0').textContent,/1–2 of 2/);
assert.doesNotMatch(text(root),/Finished work 3|Project 3|Parlor 3/);
assert.equal(find('catchup-list-0').children.length,2);
''')

    def test_jump_from_later_page_keeps_historical_selection(self):
        self.run_js(r'''
selected='parlor';click('catchup-next-0');click('catchup-jump-0-18');
assert.equal(index,17);assert.equal(current,false);assert.equal(selected,'parlor');
assert.equal(frame.seq,18);
assert.equal(document.activeElement.id,'catchup-list-0');
assert.doesNotMatch(text(root),/Finished work 10|Project 10/);
assert.match(find('catchup-range-0').textContent,/9–9 of 9/);
click('catchup-previous-0');assert.equal(find('catchup-list-0').children.length,8);
''')
