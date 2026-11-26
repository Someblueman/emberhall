"""Check named house views and readable record labels in the live renderer."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Views(HTMLParser):
    def __init__(self):
        super().__init__()
        self.views = {}
        self.details = []
        self.links = []
        self.stack = []
        self.ancestors = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ancestors[attrs["id"]] = [item[1] for item in self.stack]
        if tag == "section" and attrs.get("id", "").endswith("-view"):
            self.views[attrs["id"]] = "hidden" not in attrs
        if tag == "details":
            self.details.append("open" in attrs)
        if tag == "a" and attrs.get("href", "").startswith("#"):
            self.links.append((attrs.get("href"), attrs.get("aria-current")))
        if tag not in {"meta", "link", "br", "input"}:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


class HouseNavigationTests(unittest.TestCase):
    def test_short_default_and_named_collapsed_views(self):
        parser = Views()
        parser.feed((ROOT / "site/index.html").read_text())
        self.assertEqual(parser.views, {
            "house-view": True, "projects-view": False, "gallery-view": False,
            "council-view": False, "accounts-view": False,
        })
        labels = [href for href, _ in parser.links]
        self.assertTrue(all(f"#{view}" in labels for view in parser.views))
        source = (ROOT / "site/index.html").read_text()
        for required in ("Who is home", 'id="room-nav"', 'id="house"',
                         'id="shelf-card"', 'id="voting-card"', 'id="view-context"'):
            self.assertIn(required, source)
        self.assertEqual((ROOT / "site/index.html").read_text().count("?v=choice-progress-1"), 2)
        self.assertTrue(parser.details)
        self.assertFalse(any(parser.details))

    def test_explorer_contains_controls_but_not_the_introduction(self):
        # DOM ownership, not a claim that CSS fits an actual screen.
        source = (ROOT / "site/index.html").read_text()
        parser = Views()
        parser.feed(source)
        for target in ("floor-picker", "room-context", "house", "room-nav", "history"):
            self.assertIn("house-explorer", [node.get("id") for node in parser.ancestors[target]])
        self.assertNotIn("house-explorer", [node.get("id") for node in parser.ancestors["house-title"]])
        self.assertNotIn("house-explorer", [node.get("id") for node in parser.ancestors["presence-line"]])
        self.assertIn('id="back-to-rooms"', source)
        self.assertIn("Back to rooms", source)

    @unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
    def test_room_context_updates_and_back_to_rooms_returns_focus(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
 constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.listeners={};this.dataset={};this.style={};this.textContent='';this.className='';this.id='';this.classList={toggle(){},add(){},remove(){}};}
 appendChild(n){this.children.push(n);return n;}
 replaceChildren(){this.children=[];}
 set innerHTML(v){throw Error('Use safe text');}
 setAttribute(k,v){this.attrs[k]=String(v);if(k==='id')this.id=v;}
 removeAttribute(k){delete this.attrs[k];}
 addEventListener(k,fn){this.listeners[k]=fn;}
 focus(opts){if(!this.disabled)document.activeElement=this;this.focusOpts=opts;}
 scrollIntoView(opts){this.scrolled=true;this.scrollOpts=opts;}
 querySelectorAll(sel){const out=[];const walk=n=>{for(const c of n.children){if(sel==='button'&&c.tag==='button')out.push(c);if(sel==='#room-nav button'&&c.tag==='button')out.push(c);walk(c);}};walk(this);return out;}
}
const nodes={},all=n=>[n,...n.children.flatMap(all)];
const document={body:new Element('body'),activeElement:null,
 getElementById(id){const found=Object.values(nodes).flatMap(all).find(n=>n.id===id);if(found)return found;const node=new Element('div');node.id=id;return nodes[id]=node;},
 createElement:t=>new Element(t),createElementNS:(ns,t)=>new Element(t),querySelectorAll:()=>[]};
const context=vm.createContext({assert,document,Date,URL});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'UTC',frames:[]};current=false;selectedFloor=0;
frame={seq:10,at:1000,rooms:[{id:'hearth',name:'Hearth'},{id:'workshop',name:'Workshop'}],residents:[],runs:[],scars:[],tasks:[]};
selected=null;roomPanel();
assert.match(document.getElementById('room-context').textContent,/Ground floor · whole house/);
selected='hearth';roomPanel();
assert.match(document.getElementById('room-context').textContent,/Ground floor · Hearth/);
assert.equal(document.getElementById('room-title').textContent,'Hearth');
const nav=document.getElementById('room-nav');
const other=document.createElement('button');other.dataset.room='door';nav.appendChild(other);
const btn=document.createElement('button');btn.dataset.room='hearth';btn.textContent='Hearth';nav.appendChild(btn);
backToRooms();
assert.equal(document.activeElement,btn);
assert.equal(btn.focusOpts.preventScroll,true);
assert.equal(nav.scrolled,true);
assert.equal(nav.scrollOpts.block,'nearest');
assert.equal(nav.scrollOpts.behavior,'instant');
selected='workshop';roomPanel();
assert.match(document.getElementById('room-context').textContent,/Ground floor · Workshop/);
selected=null;roomPanel();
assert.match(document.getElementById('room-context').textContent,/Ground floor · whole house/);
`,context);
'''
        result = subprocess.run([shutil.which("node"), "-e", script, str(ROOT / "site/house.js")],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
    def test_navigation_keyboard_targets_and_record_labels(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag,id=''){this.tag=tag;this.id=id;this.children=[];this.attrs={};this.hidden=false;this.calls=[];this.listeners={};}
 appendChild(n){this.children.push(n);} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=String(v);} removeAttribute(k){delete this.attrs[k];}
 addEventListener(k,fn){this.listeners[k]=fn;} focus(){this.calls.push('focus');} scrollIntoView(){this.calls.push('scroll');}
 querySelectorAll(selector){return selector==='button'?this.children:[];}
}
const ids=['house-view','projects-view','council-view','accounts-view','shelf-card','voting-card',
 'floor-picker','history','present','previous','next','overview','back-to-rooms','room-nav','room-card'];
const nodes=Object.fromEntries(ids.map(id=>[id,new Element('section',id)]));
const links=['house-view','projects-view','council-view','accounts-view'].map(id=>{const a=new Element('a');a.hash='#'+id;return a;});
const views=ids.slice(0,4).map(id=>nodes[id]);
const document={getElementById:id=>nodes[id]||null,querySelectorAll:s=>s==='.page-view'?views:s==='.view-nav a'?links:[]};
const listeners={};const window={location:{hash:'#shelf-card'},addEventListener:(k,fn)=>listeners[k]=fn};
const context=vm.createContext({assert,document,window,links,listeners,Element});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
bindControls();
assert.equal($('projects-view').hidden,false);assert.equal($('house-view').hidden,true);
assert.equal(links[1].attrs['aria-current'],'page');
window.location.hash='#voting-card';listeners.hashchange();
assert.equal($('council-view').hidden,false);assert.equal($('projects-view').hidden,true);
assert.equal($('voting-card').calls.join(','),'focus,scroll');
assert.equal(links[2].attrs['aria-current'],'page');
showViewForHash('#accounts-view');assert.equal($('accounts-view').hidden,false);
const roomButton=new Element('button');$('room-nav').appendChild(roomButton);
$('back-to-rooms').listeners.click();
assert.equal(roomButton.calls.join(','),'focus');assert.equal($('room-nav').calls.join(','),'scroll');
let prevented=0;
const escape={key:'Escape',target:$('room-card'),preventDefault(){prevented++;}};
$('room-card').listeners.keydown(escape);
assert.equal(prevented,1);assert.equal(roomButton.calls.length,2);
for(const event of [{...escape,target:new Element('input')},{...escape,defaultPrevented:true},
 {...escape,key:'Enter'}])$('room-card').listeners.keydown(event);
assert.equal(prevented,1,'Escape inside controls and handled keys retain native behavior');
`,context);
'''
        result = subprocess.run([shutil.which("node"), "-e", script, str(ROOT / "site/house.js")],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
    def test_shelf_votes_presence_use_titles_and_exact_models(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){
  this.tag=tag;this.children=[];this.textContent='';this.attrs={};this.style={};this.className='';
  this.classList={toggle:(name,force)=>{
   const classes=new Set(this.className.split(/\s+/).filter(Boolean));
   const present=force===undefined?!classes.has(name):Boolean(force);
   if(present)classes.add(name);else classes.delete(name);
   this.className=[...classes].join(' ');return present;
  }};
 }
 appendChild(n){this.children.push(n);} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=String(v);} querySelectorAll(s){return all(this).filter(n=>n.tag==='details'&&(s!=='details[open]'||n.open));}
}
const nodes={},get=id=>(nodes[id]||(nodes[id]=new Element('div')));
const document={getElementById:get,createElement:t=>new Element(t)};
const all=n=>[n,...n.children.flatMap(all)];
const visible=n=>n.tag==='details'&&!n.open?[n.textContent,...(n.children[0]?[visible(n.children[0])]:[])].join(' '):[n.textContent,...n.children.map(visible)].join(' ');
const context=vm.createContext({assert,document,URL,nodes,all,visible});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'UTC'};const person={name:'Fern',agent:'codex',id:'resident-x'};
frame={residents:[person],shelf:{enabled:true,policy:'work-selection',ideas:[
 {id:'idea-private-1',title:'A useful garden',status:'shelved',what:'Long explanation'},
 {id:'idea-private-2',status:'shelved'}],projects:[
 {id:'project-private-1',title:'Active project',status:'active',owner:person.id,milestone:'First step'},
 {id:'project-private-2',status:'done',milestone:'Finished step'}]},
 voting:{inbox_checked_at:100,choices:[{id:'house-growth-choice-006',status:'closed',winner:'candidate-x',owner:person,
 opened_sequence:1,selection_version:2,candidates:[{id:'candidate-x',title:'Human choice title',author:person,milestone:'Try it',seconds:86400}],
 votes:[{resident:person,idea:'candidate-x',counted:true,reason:'Clear reason',sequence:2,at:100}]}],
 proposals:[{id:'proposal-private-3',title:'Readable proposal',mode:'wake-prompt',author:person,status:'pending',stale:false,
 reason:'A reason',text:'Exact proposed wording',trial:null,endorsements:[],notice:null}]},
 runs:[{id:'run-luna',resident:person.id,agent:'codex',model:'gpt-6-luna',start:100,sequence:1,status:'started'},
 {id:'run-missing',resident:person.id,agent:'codex',start:100,sequence:2,status:'started'}],tasks:[],scars:[],at:100,seq:2};current=true;
frame.voting.choices.push({...frame.voting.choices[0],id:'unreadable-open-id',status:'open',
 votes:[frame.voting.choices[0].votes[0],{...frame.voting.choices[0].votes[0],counted:false}]});
shelf();voting();data.frames=[frame];data.observed_at=100;renderResidentPulse();
assert.match(text($('shelf')),/Council choosing: 1 of 3 counted votes/);
assert(!text($('shelf')).includes('Project slot available · council can choose'));
assert(all($('shelf')).some(node=>node.href==='#voting-card'));
const shelfText=visible($('shelf')),voteText=visible($('voting'));
assert.match(shelfText,/Active project/);assert.doesNotMatch(shelfText,/Finished step|Long explanation|idea-private|project-private/);
assert.match(voteText,/Human choice title/);assert.match(voteText,/Readable proposal/);
assert.doesNotMatch(voteText,/house-growth-choice-006|candidate-x|proposal-private-3/);
assert.match(text($('finished')),/Finished step/);assert.match(text($('shelf')),/Long explanation/);
assert(all($('shelf')).some(n=>n.tag==='a'&&n.href==='#gallery-view'));
assert.match(text($('voting')),/house-growth-choice-006/);assert.match(text($('voting')),/candidate-x/);
assert.match(text($('voting')),/proposal-private-3/);
assert.match(text($('resident-pulse')),/Codex · gpt-6-luna/);assert.match(text($('resident-pulse')),/Codex · Model unrecorded/);
function text(n){return [n.textContent,...n.children.map(text)].join(' ');}
`,context);
'''
        result = subprocess.run([shutil.which("node"), "-e", script, str(ROOT / "site/house.js")],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
