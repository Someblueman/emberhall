"""The Door offers real room visits without losing the selected history."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node runs the shipped renderer")
class DoorGuideTests(unittest.TestCase):
    def test_recorded_rooms_status_text_safety_and_navigation(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag,id=''){this.tag=tag;this.id=id;this.children=[];this.attrs={};this.listeners={};this.dataset={};this.style={};this.textContent='';this.classList={toggle(){}};}
 appendChild(n){this.children.push(n);return n;} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=String(v);} removeAttribute(k){delete this.attrs[k];}
 addEventListener(k,fn){this.listeners[k]=fn;}
 focus(){document.activeElement=this;} scrollIntoView(){}
}
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' '),nodes={};
const get=id=>Object.values(nodes).flatMap(all).find(n=>n.id===id)||nodes[id]||(nodes[id]=new Element('div',id));
const card=new Element('section');
const document={activeElement:null,body:new Element('body'),getElementById:get,
 createElement:t=>new Element(t),createElementNS:(_,t)=>new Element(t),
 querySelector:s=>s==='.room-card'?card:null,querySelectorAll:()=>[]};
const listeners={},addresses=['#room/door'];let cursor=0;
const window={innerHeight:900,location:{hash:addresses[0]},addEventListener:(k,fn)=>listeners[k]=fn,
 history:{pushState(a,b,hash){addresses.splice(++cursor);addresses.push(hash);window.location.hash=hash;}}};
const ctx=vm.createContext({assert,document,window,Date,URL,Intl});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
const run=s=>vm.runInContext(s,ctx),links=()=>all(get('room-content')).filter(n=>n.tag==='a');
run(`
drawHouse=()=>{};dormControls=()=>{};accounts=()=>{};shelf=()=>{};voting=()=>{};
renderCollection=()=>{};renderResidentPulse=()=>{};renderRecentGrowth=()=>{};renderLately=()=>{};lighting=()=>{};
const base={at:1000,event:{op:'say',actor:'r'},floors:[{level:0,name:'Ground floor'},{level:1,name:'Upstairs'}],residents:[],tasks:[],scars:[],ambitions:[],runs:[]};
const door={id:'door',name:'The Door',status:'open'},hearth={id:'hearth',name:'The Hearth',status:'open'};
data={timezone:'UTC',observed_at:1000,journal_head:'head',commits:[],frames:[
 {...base,seq:1,rooms:[door,hearth]},
 {...base,seq:2,rooms:[door,hearth,{id:'gallery',name:'The Gallery',status:'open'},
 {id:'sun room',name:'Sun room',floor:1,status:'open',purpose:'Look at the sky'},
 {id:'assay',name:'The Assay Room',status:'construction'},
 {id:'salvage',name:'The Salvage Room',status:'closed'},
 {id:'__proto__',name:'<script>untrusted</script>',status:'open',purpose:'<img src=x>'}]}]};
index=1;current=true;bindControls();render();
`);
assert.match(text(get('room-content')),/Where would you like to go/);
assert.match(text(get('room-content')),/latest published/);
assert(links().find(n=>n.href==='#room/gallery').textContent.includes('Try something made here'));
assert(links().find(n=>n.href==='#room/assay').textContent.includes('See the construction'));
assert(links().find(n=>n.href==='#room/salvage').textContent.includes('Read its kept history'));
assert.doesNotMatch(text(get('room-content')),/Practise choosing/); // closed room offers no activity
assert.match(text(get('room-content')),/<script>untrusted<\/script>/);
assert(!all(get('room-content')).some(n=>['script','img'].includes(n.tag)));
assert(links().some(n=>n.href==='#room/sun%20room'));
const before=run('JSON.stringify(frame)');run('roomPanel()');assert.equal(run('JSON.stringify(frame)'),before);
// Follow the actual room address through the shipped hash handler, then browser Back.
const target=links().find(n=>n.href==='#room/sun%20room').href;
window.history.pushState(null,'',target);listeners.hashchange();
assert.equal(run('selected'),'sun room');assert.equal(run('selectedFloor'),1);
assert.equal(document.activeElement,card);
window.location.hash=addresses[--cursor];listeners.hashchange();
assert.equal(run('selected'),'door');assert.equal(run('selectedFloor'),0);
run("$('previous').listeners.click()");
assert.equal(run('current'),false);assert.equal(run('frame.seq'),1);
assert.match(text(get('room-content')),/Visiting one keeps you at this point in history/);
assert(!links().some(n=>n.href==='#room/gallery'));
window.location.hash='#room/hearth';listeners.hashchange();
assert.equal(run('frame.seq'),1);assert.equal(run('current'),false);
// A closed Door does not offer an open directory, and an empty one explains the absence.
run("selected='door';frame={...frame,rooms:[{...door,status:'closed'}]};roomPanel()");
assert.doesNotMatch(text(get('room-content')),/Where would you like to go/);
run("frame={...frame,rooms:[door]};roomPanel()");
assert.match(text(get('room-content')),/No other rooms are recorded/);
// Wish links use only the selected shelf, never future data or guessed completion.
run(`
const art={id:'art',title:'<img src=x> A moth',status:'project',brief:{field:'art',for:'play'}};
const math={id:'math',title:'Five marks',status:'project',brief:{field:'mathematics',for:'field'}};
const language={id:'lang',title:'Forget me',status:'shelved',brief:{field:'language',for:'people'}};
const future={...language,id:'future',title:'Future secret'};
const terminal={id:'terminal',title:'Tape terminal',status:'project',brief:{field:'software',for:'play'}};
const nowShelf={enabled:true,ideas:[art,math,language,terminal],projects:[
 {id:'terminal-work',idea:'terminal',title:terminal.title,status:'active'},
 {id:'art-work',idea:'art',title:art.title,status:'done',plain:'One moth circles the lamp.',milestone:'Draw the whole flight.'},
 {id:'math-work',idea:'math',title:math.title,status:'active',stage:2,milestones:[{},{},{}],completed:[{},{}]},
 ...Array.from({length:4},(_,n)=>({id:'stopped-'+n,title:'Stopped '+n,status:'dropped',brief:{field:'art'}})),
 {id:'dropped',title:'Dropped work',status:'dropped',brief:{field:'art'},lesson:'<img src=x> The gate found no advantage.'},
 {id:'language-stop',title:'Earlier language',status:'dropped',brief:{field:'language'}},
 ...Array.from({length:4},(_,n)=>({id:'old-'+n,title:'Old '+n,status:'done',brief:{field:'art'}}))]};
frame={...frame,seq:5,shelf:nowShelf};current=true;roomPanel();
`);
let body=text(get('room-content'));
assert.match(body,/not wishes declared fulfilled/);
assert.match(body,/In progress · stage 3 of 3 ·.*Five marks/);
assert.match(body,/Proposed ·.*Forget me/);
assert.match(body,/Finished ·.*<img src=x> A moth/);
assert.match(body,/Show 2 more attempts/);
const playful=all(get('room-content')).find(n=>n.children.some(c=>c.id==='door-wish-5'));
assert.match(text(playful),/Be audacious or playful · 2 related attempts/);
assert.match(text(playful),/Tape terminal/);
const uncataloged=all(playful).find(n=>n.children.some(c=>c.id==='door-record-5-art-work'));
assert.match(text(uncataloged),/One moth circles the lamp/);
assert.match(text(uncataloged),/Draw the whole flight/);
assert(!links().some(n=>n.id==='door-attempt-5-art-work'));
assert.match(body,/5 stopped attempts · read why/);
assert.match(body,/Stopped · Dropped work/);
assert.match(body,/<img src=x> The gate found no advantage/);
assert.match(body,/No reason for stopping is recorded/);
assert.doesNotMatch(body,/Stopped · Stopped 0|Future secret/);
assert.equal(links().filter(n=>n.id.startsWith('door-stopped-0-')).length,3);
assert(!all(get('room-content')).some(n=>n.tag==='img'));
assert(links().some(n=>n.href.endsWith('/docs/WISHES.md')));
assert(links().some(n=>n.href==='#room/workshop'));
run(`catalog=[{id:'art',title:'Moth picture',category:'creation',href:'projects/art/'}];galleryState={query:'old filter',activity:'Read',toolsOpen:false};roomPanel()`);
const doneLink=links().find(n=>n.id==='door-attempt-0-art-work');
assert.equal(doneLink.href,'#gallery-view');doneLink.listeners.click();
assert.equal(run('galleryState.query'),'Moth picture');
assert.equal(run('galleryState.activity'),'all');assert(run('galleryState.toolsOpen'));
const artSection=all(get('room-content')).find(n=>n.tag==='summary'&&n.id==='door-wish-0');
const artDetails=all(get('room-content')).find(n=>n.children.includes(artSection));
artDetails.open=true;artDetails.listeners.toggle();run('roomPanel()');
assert(all(get('room-content')).find(n=>n.tag==='details'&&n.children.some(c=>c.id==='door-wish-0')).open);
const stoppedSummary=all(get('room-content')).find(n=>n.id==='door-stopped-0');
const stoppedDetails=all(get('room-content')).find(n=>n.children.includes(stoppedSummary));
stoppedDetails.open=true;stoppedDetails.listeners.toggle();run('roomPanel()');
assert(all(get('room-content')).find(n=>n.children.some(c=>c.id==='door-stopped-0')).open);
let stoppedLink=links().find(n=>n.id==='door-stopped-0-dropped');
stoppedLink.focus();run('refreshView(false)');
assert.equal(document.activeElement.id,stoppedLink.id);assert.notEqual(document.activeElement,stoppedLink);
stoppedLink=links().find(n=>n.id==='door-stopped-0-dropped');
assert.equal(stoppedLink.href,'#projects-view');stoppedLink.listeners.click();
assert.equal(run('projectsFindState.query'),'Dropped work');
const mathLink=links().find(n=>n.id==='door-attempt-1-math-work');
mathLink.focus();run('refreshView(false)');
assert.equal(document.activeElement.id,mathLink.id);assert.notEqual(document.activeElement,mathLink);
assert.equal(mathLink.href,'#projects-view');mathLink.listeners.click();
assert.equal(run('projectsFindState.query'),'Five marks');
window.location.hash=mathLink.href;listeners.hashchange();
assert.equal(document.activeElement,get('projects-view'));
assert.equal(run('frame.seq'),5); // following the work does not move the history cursor
run(`current=false;frame={...frame,shelf:{enabled:true,ideas:[],projects:[]}};selected='door';roomPanel()`);
body=text(get('room-content'));assert.doesNotMatch(body,/Tape terminal|A moth|Five marks|Forget me|Dropped work|gate found no advantage/);
assert.match(body,/belongs to this recorded moment/);
assert.match(body,/No related attempt/);
run(`frame={...frame,shelf:{enabled:true,ideas:[future],projects:[]}};roomPanel()`);
assert.match(text(get('room-content')),/Future secret/);
run(`frame={...frame,shelf:null};roomPanel()`);
assert.match(text(get('room-content')),/No project shelf is recorded/);
'''
        result = subprocess.run(
            ["node", "-e", script, str(Path(__file__).parents[1] / "site/house.js")],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
