"""Execute the actual shelf renderer against a minimal DOM; no visual claim."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which('node'), 'Node is needed for the actual renderer')
class ShelfUITests(unittest.TestCase):
    def test_real_states_safe_links_reasons_and_historical_reset(self):
        source = Path(__file__).parents[1] / 'site/house.js'
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';}
  appendChild(node){this.children.push(node);}
  replaceChildren(){this.children=[];}
  setAttribute(key,value){this[key]=value;}
  addEventListener(){}
}
const root=new Element('section'), document={getElementById:()=>root,createElement:tag=>new Element(tag)};
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const all=node=>[node,...node.children.flatMap(all)];
const context=vm.createContext({assert,document,URL,root,text,all});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'Europe/London'};frame={};shelf();
assert.match(text(root),/not activated/);
frame={residents:[{id:'resident-fixture',name:'Juniper'}],shelf:{enabled:true,policy:null,ideas:[],projects:[]}};shelf();
assert.match(text(root),/awaits ratification/);assert.match(text(root),/No ideas/);
assert.doesNotMatch(text(root),/Room for one Explorer round|council can choose/);
assert(text(root).includes("Building now: 0 of 2 project slots · 0 ideas waiting"));
frame.shelf.policy='work-selection';
frame.shelf.explorer={resident:'resident-fixture',agent:'opencode',until:100};
frame.shelf.ideas=[
 {id:'draft',title:'<img src=x onerror=alert(1)>',status:'shelved',sources:['https://example.org/', 'javascript:alert(1)', 'https://user:secret@example.org/']},
 {id:'winner',title:'Already selected',status:'project',sources:[]},
 {id:'lost',title:'Lost idea',status:'graveyard',losses:2,history:[{reasons:['Too large for the first milestone']}]}];
frame.shelf.projects=[{id:'done',title:'Completed map',status:'done',milestone:'Demo',deadline:100,extended:false}];
shelf();
assert.doesNotMatch(text(root),/In motion/);assert.match(text(root),/Finished projects/);
assert.match(text(root),/Completed map/);assert.doesNotMatch(text(root),/Already selected/);
assert.match(text(root),/Too large for the first milestone/);
assert.match(text(root),/Explorer: Juniper · OpenCode/);assert.doesNotMatch(text(root),/resident-fixture/);
assert.match(text(root),/see the recorded round above/);assert.doesNotMatch(text(root),/Room for one Explorer round/);
assert.equal(all(root).filter(n=>n.tag==='img').length,0);
const links=all(root).filter(n=>n.tag==='a');assert.equal(links.length,1);
assert.equal(links[0].href,'https://example.org/');assert.equal(links[0].rel,'noopener noreferrer');
frame.shelf.projects.push({id:'live',title:'Current build',status:'active',deadline:200});shelf();
assert.match(text(root),/In motion/);assert.match(text(root),/Current build/);
frame.shelf.explorer=null;
frame.shelf.ideas.push({id:'second',status:'shelved'},{id:'third',status:'shelved'});
shelf();assert.match(text(root),/Project slot available/);assert.match(text(root),/no Explorer round needed/);
frame.shelf.projects.push({id:'another',title:'Another build',status:'active'});
shelf();assert.match(text(root),/Both project slots occupied/);
assert.doesNotMatch(text(root),/Selection open|council decision needed|council can choose/);
frame.shelf.projects[2].status='done';shelf();assert.match(text(root),/Project slot available/);
frame={};shelf();assert.doesNotMatch(text(root),/Completed map|Current build|Lost idea/);
assert.match(text(root),/not activated/);
`,context);
'''
        result = subprocess.run([shutil.which('node'), '-e', script, str(source)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_other_work_shows_without_active_projects_and_find_matches_field_scale_owner(self):
        source = Path(__file__).parents[1] / 'site/house.js'
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.classList={add(){},remove(){},toggle(){},contains(){return false;}};}
  appendChild(node){this.children.push(node);return node;}
  replaceChildren(){this.children=[];}
  setAttribute(key,value){this[key]=value;}
  addEventListener(){}
}
const root=new Element('section'), document={getElementById:()=>root,createElement:tag=>new Element(tag)};
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const all=node=>[node,...node.children.flatMap(all)];
const context=vm.createContext({assert,document,URL,root,text,all});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'UTC'};
frame={
  at:1000,
  residents:[{id:'r1',name:'Rowan'},{id:'r2',name:'Mallow'}],
  work:[{id:'upkeep-1',title:'Improve Study filters',plain:'Visitors can filter Study ideas by scale.',owner:'r1',at:900}],
  shelf:{
    enabled:true,
    policy:'work-selection-004',
    ideas:[
      {id:'i-art',title:'Bell Choir',status:'shelved',scale:'great',author:'r2',brief:{field:'art'},sources:[]}
    ],
    projects:[]
  }
};
shelf();
const out=text(root);
assert.match(out,/In motion/);
assert.match(out,/Other work/);
assert.match(out,/Visitors can filter Study ideas by scale/);
const ideaNode=all(root).find(n=>String(n.className||'').includes('shelf-idea'));
const findText=ideaNode['data-find'];
assert.match(findText,/great work/);
assert.match(findText,/art/);
assert.match(findText,/mallow/);
`,context);
'''
        result = subprocess.run([shutil.which('node'), '-e', script, str(source)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_study_room_renders_only_when_recorded_and_links_to_shelf(self):
        source = Path(__file__).parents[1] / 'site/house.js'
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';}
  appendChild(node){this.children.push(node);}
  replaceChildren(){this.children=[];}
  setAttribute(key,value){this[key]=value;}
  addEventListener(){}
}
const nodes={};
const get=id=>(nodes[id]||(nodes[id]=new Element('div')));
const document={getElementById:get,createElement:tag=>new Element(tag)};
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const all=node=>[node,...node.children.flatMap(all)];
const context=vm.createContext({assert,document,URL,nodes,text,all});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'Europe/London'};
const door={id:'door',name:'Door',floor:0,status:'open'};
frame={rooms:[door],residents:[],scars:[],tasks:[],floors:[{level:0,name:'Ground floor'}],shelf:{enabled:true,policy:null,ideas:[{id:'i1',status:'shelved'}],projects:[]}};
assert.deepEqual(floorRooms(frame,0).map(r=>r.id),['door']);
const studyBuild={id:'study',name:'The Study',floor:0,status:'construction',purpose:'Shelf room'};
frame.rooms.push(studyBuild);
assert.deepEqual(floorRooms(frame,0).map(r=>r.id),['door','study']);
assert.equal(roomStatus(studyBuild),'construction');
studyBuild.status='open';
assert.equal(roomStatus(studyBuild),'open');
selected='study';
roomPanel();
const panel=nodes['room-content'];
assert.match(text(panel),/1 shelved idea/);
const links=all(panel).filter(n=>n.tag==='a');
const shelfLinks=links.filter(n=>!String(n.href).startsWith('#room/'));
assert.equal(links.filter(n=>n.href==='#room/study').length,1);
assert.equal(shelfLinks.length,1);
assert.equal(shelfLinks[0].href,'#shelf-card');
frame={rooms:[door],residents:[],scars:[],tasks:[],floors:[{level:0,name:'Ground floor'}]};
if(!floorRooms(frame,0).some(r=>r.id===selected))selected=null;
assert.equal(selected,null);
`,context);
'''
        result = subprocess.run([shutil.which('node'), '-e', script, str(source)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_great_work_slots_explorer_readiness_stages_and_study_summary(self):
        source = Path(__file__).parents[1] / 'site/house.js'
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';}
  appendChild(node){this.children.push(node);}
  replaceChildren(){this.children=[];}
  setAttribute(key,value){this[key]=value;}
  addEventListener(){}
}
const nodes={};
const get=id=>(nodes[id]||(nodes[id]=new Element('div')));
const document={getElementById:get,createElement:tag=>new Element(tag)};
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const all=node=>[node,...node.children.flatMap(all)];
const context=vm.createContext({assert,document,URL,nodes,text,all});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'UTC'};
const study={id:'study',name:'The Study',floor:0,status:'open',purpose:'Shelf room'};
frame={
  rooms:[study],residents:[{id:'r1',name:'Fable'}],scars:[],tasks:[],floors:[{level:0,name:'Ground floor'}],
  shelf:{
    enabled:true,
    policy:'work-selection-004',
    great_wanted:true,
    explorer:null,
    ideas:[
      {id:'s1',title:'Small idea 1',status:'shelved',scale:'small',losses:1,author:'r1',sources:[]},
      {id:'s2',title:'Small idea 2',status:'shelved',scale:'small',losses:0,author:'r1',sources:[]},
      {id:'s3',title:'Small idea 3',status:'shelved',scale:'small',losses:0,author:'r1',sources:[]},
      {id:'g1',title:'Great idea 1',status:'shelved',scale:'great',losses:0,author:'r1',sources:[]}
    ],
    projects:[
      {id:'p-small',title:'Trial Bench',status:'active',slot:'small',owner:'r1',milestone:'Offline trial',deadline:200}
    ]
  }
};
shelf();
const shelfText=text(nodes['shelf']);
assert.match(shelfText,/0 of 1 great work/);
assert.match(shelfText,/1 of 1 small project/);
assert.match(shelfText,/1 great, 3 small/);
assert.match(shelfText,/Room for a great-work Explorer round/);
assert.doesNotMatch(shelfText,/no Explorer round needed/);
assert.match(shelfText,/great work/i);
assert.match(shelfText,/1 loss/);
assert.match(shelfText,/Small project/);
selected='study';
roomPanel();
const studyText=text(nodes['room-content']);
assert.match(studyText,/Great slot: free \\(1 great idea\\)/);
assert.match(studyText,/Small slot: busy \\(3 small ideas\\)/);
frame.shelf.great_wanted=false;
frame.shelf.ideas.push({id:'g2',title:'Great idea 2',status:'shelved',scale:'great',losses:0,author:'r1',sources:[]});
frame.shelf.projects.push({
  id:'p-great',title:'Public Observatory',status:'active',slot:'great',owner:'r1',
  stage:1,milestone:'Stage two',deadline:400,
  milestones:[{milestone:'Stage one',seconds:86400},{milestone:'Stage two',seconds:172800},{milestone:'Stage three',seconds:259200}],
  completed:[{stage:0,milestone:'Stage one',evidence:'obs-m1',sequence:99}]
});
shelf();
const updatedText=text(nodes['shelf']);
assert.match(updatedText,/1 of 1 great work/);
assert.match(updatedText,/Shelf stocked · no Explorer round needed/);
assert.match(updatedText,/Stage 2 of 3/);
assert.match(updatedText,/Stage one/);
assert.match(updatedText,/event 99/);
assert.match(updatedText,/Stage three/);
`,context);
'''
        result = subprocess.run([shutil.which('node'), '-e', script, str(source)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)
