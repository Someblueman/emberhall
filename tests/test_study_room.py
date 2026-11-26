"""Exercise the Study's actual renderer; browser use is recorded separately."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node is required for the renderer")
class StudyRoomTests(unittest.TestCase):
    def run_js(self, checks):
        source = Path(__file__).parents[1] / "site/house.js"
        harness = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes={};
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.listeners={};this.style={};}
  set id(value){this._id=value;nodes[value]=this;} get id(){return this._id;}
  appendChild(node){this.children.push(node);return node;}
  replaceChildren(){this.children=[];}
  setAttribute(key,value){this[key]=value;}
  addEventListener(key,fn){this.listeners[key]=fn;}
  focus(){document.activeElement=this;}
  setSelectionRange(start,end,direction){Object.assign(this,{selectionStart:start,selectionEnd:end,selectionDirection:direction});}
}
const document={createElement:tag=>new Element(tag),getElementById:id=>nodes[id]||null};
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const all=node=>[node,...node.children.flatMap(all)];
const root=new Element('div');
const ctx=vm.createContext({assert,document,URL,root,nodes,text,all,Element});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
data={timezone:'UTC'};frame={residents:[{id:'r',name:'Rowan'}]};
const brief={worth:'useful',author:'r',asked:[{who:'Outside reader',said:'Please make a way to do this without a server.',where:'https://example.org/ask'}]};
const ideas=[
 {id:'checked',title:'Checked idea',grounded:true,brief,what:'A portable map'},
 {id:'second',title:'Second reader idea',grounded:false,brief},
 {id:'research',title:'Research idea',grounded:false,brief:{worth:'useful',author:'r'}},
 {id:'legacy',title:'Earlier idea',brief:{benefit:'A historical brief'}},
 {id:'empty',title:'Empty idea'},
 {id:'renew',title:'Renew idea',brief:{benefit:'Old brief'},brief_due:100},
 {id:'selected',title:'Selected project',status:'project'},
 {id:'retired',title:'Retired idea',status:'graveyard'}
].map(i=>({status:'shelved',author:'r',sources:[],...i}));
const shelfData={enabled:true,policy:'work-selection-004',ideas,projects:[]};
const find=id=>all(root).find(n=>n.id===id);
const change=(id,value,event)=>{const n=find(id);n.value=value;n.listeners[event]();};
`,ctx);
vm.runInContext(process.argv[2],ctx);
'''
        result = subprocess.run([shutil.which("node"), "-e", harness, str(source), checks],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_search_status_and_paging(self):
        self.run_js(r'''
renderStudyDesk(root,shelfData);
assert.match(text(root),/6 of 6 ideas match.*page 1 of 2/);
assert.equal(all(root).filter(n=>n.className==='study-idea').length,4);
assert.doesNotMatch(text(root),/Selected project|Retired idea|Empty idea/);
find('study-next').listeners.click();
assert.match(text(root),/page 2 of 2/);assert.match(text(root),/Empty idea/);
assert.equal(document.activeElement.id,'study-filter');
change('study-filter','checked','change');
assert.match(text(root),/1 of 6 ideas match/);assert.match(text(root),/Checked idea/);
assert.doesNotMatch(text(root),/Second reader idea/);
change('study-filter','second','change');assert.match(text(root),/Second reader idea/);
change('study-filter','research','change');assert.match(text(root),/3 of 6 ideas match/);
change('study-filter','unknown','change');assert.match(text(root),/Earlier idea/);
change('study-search','nobody','input');assert.match(text(root),/No ideas match/);
change('study-filter','all','change');change('study-search','  portable   MAP ','input');
assert.match(text(root),/1 of 6 ideas match/);assert.match(text(root),/Checked idea/);
change('study-search','Rowan','input');assert.match(text(root),/6 of 6 ideas match/);
''')

    def test_historical_isolation_safe_sources_and_empty_state(self):
        self.run_js(r'''
ideas[0].title='<img src=x onerror=alert(1)>';
ideas[0].sources=['javascript:alert(1)','https://user:secret@example.org/','https://example.org/read'];
renderStudyDesk(root,shelfData);
assert.equal(all(root).filter(n=>n.tag==='img').length,0);
const links=all(root).filter(n=>n.tag==='a');assert.equal(links.length,3);
assert(links.every(n=>n.href.startsWith('https://example.org/')&&n.rel==='noopener noreferrer'));
root.replaceChildren();renderStudyDesk(root,{...shelfData,ideas:[ideas[4]]});
assert.match(text(root),/1 of 1 ideas match/);assert.match(text(root),/Empty idea/);
assert.doesNotMatch(text(root),/Second reader idea|Outside reader|portable map/);
root.replaceChildren();renderStudyDesk(root,{...shelfData,ideas:[]});
assert.match(text(root),/No ideas are waiting/);assert(!find('study-search'));
root.replaceChildren();renderStudyDesk(root,{...shelfData,ideas:[{...ideas[3],grounded:false}]});
assert.match(text(root),/Who asked\?/);assert.doesNotMatch(text(root),/Researched/);
''')

    def test_refresh_keeps_search_focus_and_selection(self):
        self.run_js(r'''
renderStudyDesk(root,shelfData);
const first=all(root).find(n=>n.className==='shelf-item shelf-idea');
first.open=true;first.listeners.toggle();
change('study-search','portable','input');find('study-search').focus();
document.activeElement.setSelectionRange(2,5,'backward');
render=()=>{root.replaceChildren();renderStudyDesk(root,shelfData);};
refreshView(true);
assert.equal(document.activeElement,find('study-search'));
assert.equal(find('study-search').value,'portable');
assert.equal(find('study-search').selectionStart,2);assert.equal(find('study-search').selectionEnd,5);
assert.equal(find('study-search').selectionDirection,'backward');
assert.match(text(root),/1 of 6 ideas match/);
assert(all(root).find(n=>n.className==='shelf-item shelf-idea').open);
''')

    def test_desk_requires_an_open_recorded_study(self):
        self.run_js(r'''
for(const id of ['room-content','room-kicker','room-title','room-description','room-context']){
 const node=new Element('div');node.id=id;
}
const study={id:'study',name:'The Study',status:'open'};
frame={...frame,rooms:[study],shelf:shelfData,scars:[],tasks:[],runs:[]};selected='study';
roomPanel();assert.match(text(nodes['room-content']),/Read the ideas/);
for(const status of ['construction','closed']){
 study.status=status;roomPanel();assert.doesNotMatch(text(nodes['room-content']),/Read the ideas|Checked idea/);
}
study.status='open';frame.shelf={enabled:false};roomPanel();
assert.match(text(nodes['room-content']),/not activated/);
frame.rooms=[];roomPanel();assert.doesNotMatch(text(nodes['room-content']),/Read the ideas/);
''')

    def test_vote_and_asks_lines_use_this_moment_only(self):
        self.run_js(r'''
for(const id of ['room-content','room-kicker','room-title','room-description','room-context']){
 const node=new Element('div');node.id=id;
}
const study={id:'study',name:'The Study',status:'open'};
frame={...frame,rooms:[study],shelf:shelfData,scars:[],tasks:[],runs:[],
 voting:{choices:[{id:'c1',status:'open',slot:'house',
  candidates:[{id:'a',title:'A'},{id:'b',title:'B'},{id:'c',title:'C'}],
  votes:[{counted:true},{counted:false}]}]}};
selected='study';roomPanel();
assert.match(text(nodes['room-content']),/Vote open · House work choice · 3 candidates · 1 of 3 votes recorded/);
assert.match(text(nodes['room-content']),/Asked of the Steward · nothing waiting/);
frame.shelf={...shelfData,needs:[{id:'n1',status:'open'},{id:'n2',status:'granted'}]};
roomPanel();
assert.match(text(nodes['room-content']),/Asked of the Steward · 1 ask waits for an answer/);
frame.voting={choices:[{id:'c1',status:'closed',slot:'house',candidates:[{id:'a',title:'A'}],votes:[]}]};
frame.shelf={...shelfData,needs:[]};
roomPanel();
assert.match(text(nodes['room-content']),/No vote open at this moment/);
assert.doesNotMatch(text(nodes['room-content']),/Vote open/);
assert.match(text(nodes['room-content']),/Asked of the Steward · nothing waiting/);
''')

    def test_search_plain_field_scale_filter_and_reset(self):
        self.run_js(r'''
ideas[0].plain='Compose two magic tricks that share one card deal.';
ideas[0].scale='great';
ideas[0].brief={...brief,field:'language',for:'play'};
ideas[1].scale='small';
ideas[1].brief={...brief,field:'art',for:'play'};
renderStudyDesk(root,shelfData);
assert.equal(find('study-scale').value,'all');
assert(find('study-reset').disabled);
change('study-scale','great','change');
assert.match(text(root),/1 of 6 ideas match/);
assert.match(text(root),/Checked idea/);
assert.doesNotMatch(text(root),/Second reader idea/);
assert(!find('study-reset').disabled);
change('study-scale','small','change');
assert.match(text(root),/5 of 6 ideas match/);
assert.doesNotMatch(text(root),/Checked idea/);
change('study-scale','all','change');
change('study-search','magic tricks','input');
assert.match(text(root),/1 of 6 ideas match/);
assert.match(text(root),/Checked idea/);
change('study-search','language','input');
assert.match(text(root),/1 of 6 ideas match/);
change('study-search','great work','input');
assert.match(text(root),/1 of 6 ideas match/);
find('study-reset').listeners.click();
assert.equal(find('study-scale').value,'all');
assert.equal(find('study-filter').value,'all');
assert.equal(find('study-search').value,'');
assert(find('study-reset').disabled);
assert.equal(document.activeElement.id,'study-search');
assert.match(text(root),/6 of 6 ideas match/);
''')

    def test_search_finds_audience_and_ignores_earlier_snapshot(self):
        self.run_js(r'''
ideas[0].brief={...brief,audience:'Amateur astronomers'};
ideas[1].brief={...brief,audience:'Children aged six'};
renderStudyDesk(root,shelfData);
change('study-search','astronomers','input');
assert.match(text(root),/1 of 6 ideas match/);
assert.match(text(root),/Checked idea/);
assert.doesNotMatch(text(root),/Second reader idea/);
change('study-search','children aged six','input');
assert.match(text(root),/1 of 6 ideas match/);
assert.match(text(root),/Second reader idea/);
assert.doesNotMatch(text(root),/Checked idea/);
root.replaceChildren();renderStudyDesk(root,{...shelfData,ideas:[ideas[3]]});
change('study-search','astronomers','input');
assert.match(text(root),/No ideas match/);
''')
