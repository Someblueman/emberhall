"""Exercise room addresses against the real renderer and its DOM boundary."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
class RoomBookmarkTests(unittest.TestCase):
    def test_addresses_history_floors_and_earlier_frames(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag,id=''){this.tag=tag;this.id=id;this.children=[];this.attrs={};this.listeners={};this.dataset={};this.style={};this.textContent='';this.classList={toggle(){}};}
 appendChild(n){this.children.push(n);return n;} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=String(v);} removeAttribute(k){delete this.attrs[k];}
 addEventListener(k,fn){this.listeners[k]=fn;}
 focus(){document.activeElement=this;} scrollIntoView(){this.scrolled=true;}
 querySelectorAll(s){return all(this).filter(n=>s==='button'?n.tag==='button':n.tag==='details'&&(s!=='details[open]'||n.open));}
}
const all=n=>[n,...n.children.flatMap(all)],nodes={};
const get=id=>Object.values(nodes).flatMap(all).find(n=>n.id===id)||(nodes[id]=new Element('div',id));
const card=nodes['room-card']=new Element('section','room-card');
const views=['house-view','projects-view','gallery-view','council-view','accounts-view'].map(get);
const links=views.map(v=>Object.assign(new Element('a'),{hash:'#'+v.id}));
const document={body:new Element('body'),activeElement:null,getElementById:get,
 createElement:t=>new Element(t),querySelector:s=>s==='.room-card'?card:null,
 querySelectorAll:s=>s==='.page-view'?views:s==='.view-nav a'?links:[]};
const listeners={},addresses=['#room/sun%20room'];let cursor=0;
const window={location:{hash:addresses[0]},addEventListener:(k,fn)=>listeners[k]=fn,
 history:{pushState(a,b,hash){addresses.splice(++cursor);addresses.push(hash);window.location.hash=hash;}}};
const ctx=vm.createContext({assert,document,window,Date,URL,card,links});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
const run=s=>vm.runInContext(s,ctx),text=n=>[n.textContent,...n.children.map(text)].join(' ');
run(`
drawHouse=()=>{};dormControls=()=>{};accounts=()=>{};shelf=()=>{};voting=()=>{};
renderCollection=()=>{};renderResidentPulse=()=>{};renderRecentGrowth=()=>{};renderLately=()=>{};lighting=()=>{};
const moment=(seq,rooms)=>({seq,at:1000+seq,event:{op:'say',actor:'a'},rooms,
 floors:[{level:1,name:'Upper floor',purpose:'Reading'}],residents:[],tasks:[],scars:[],ambitions:[]});
const ground={id:'hearth',name:'Hearth'},upper={id:'sun room',name:'Sun room',floor:1};
data={timezone:'UTC',observed_at:1020,journal_head:'head',commits:[],
 frames:[moment(1,[ground]),moment(2,[ground,upper])]};
index=1;bindControls();render();
assert.equal(selected,'sun room');assert.equal(selectedFloor,1);
assert.equal($('room-title').textContent,'Sun room');
assert.equal($('house-view').hidden,false);assert.equal(links[0].attrs['aria-current'],'page');
`);
assert(all(get('room-content')).some(n=>n.tag==='a'&&n.href==='#room/sun%20room'));
run(`choose('hearth');choose('hearth');`);
assert.equal(document.activeElement,card,'Opening a room moves focus out of the replaced drawing');
assert.equal(card.scrolled,true,'The room contents are brought into view');
assert.deepEqual(addresses,['#room/sun%20room','#room/hearth']); // no duplicate visit
run(`
const trialDoorway=$('room-link-hearth');trialDoorway.focus();refreshView(true);
assert.notEqual($('room-link-hearth'),trialDoorway,'A new publication replaces the doorway');
assert.equal(document.activeElement,$('room-link-hearth'),'Refresh restores the same doorway');
choose('hearth');refreshView();assert.equal(document.activeElement,card);
const first=$('room-link-hearth');const other=document.createElement('button');
other.dataset.room='other';$('room-nav').children.unshift(other);
backToRooms();assert.equal(document.activeElement,first,'Return finds the selected room, not the first button');
assert.equal(window.location.hash,'#room/hearth','Returning focus keeps the room bookmark');
`);
window.location.hash=addresses[--cursor];listeners.hashchange();
assert.equal(run('selected'),'sun room');assert.equal(document.activeElement,card);
window.location.hash=addresses[++cursor];listeners.hashchange();
assert.equal(run('selected'),'hearth');assert.equal(run('selectedFloor'),0);
// A new publication or a timeline redraw must keep the room address meaningful.
run('render();');assert.equal(run('selected'),'hearth');
window.location.hash='#room/sun%20room';listeners.hashchange();
run("$('previous').listeners.click();");
assert.equal(run('selected'),null);
assert.match(text(get('room-content')),/not recorded at this moment/);
assert.doesNotMatch(text(get('room-content')),/Link to Sun room/);
run("$('present').listeners.click();");assert.equal(run('selected'),'sun room');
window.location.hash='#room/future';listeners.hashchange();
assert.equal(run('selected'),null);assert.match(text(get('room-content')),/not recorded/);
window.location.hash='#room/%E0%A4%A';listeners.hashchange(); // malformed escape
assert.equal(run('selected'),null);assert.match(text(get('room-content')),/not recorded/);
// Existing view fragments keep their destinations and the last room selection.
window.location.hash='#room/hearth';listeners.hashchange();
window.location.hash='#shelf-card';listeners.hashchange();
assert.equal(get('projects-view').hidden,false);assert.equal(run('selected'),'hearth');
window.location.hash='#house-view';listeners.hashchange();assert.equal(run('selected'),null);
assert.doesNotMatch(text(get('room-content')),/not recorded/);
// Switching floors leaves the room address, so render cannot pull the visitor back.
window.location.hash='#room/sun%20room';listeners.hashchange();
run("$('floor-picker').listeners.change({target:{value:'0'}});");
assert.equal(window.location.hash,'#house-view');assert.equal(run('selectedFloor'),0);
assert.equal(run('selected'),null);
window.location.hash='';listeners.hashchange();
run("choose('hearth');");
assert.equal(window.location.hash,'#room/hearth');
run("choose(null);");
assert.equal(window.location.hash,'#house-view');assert.equal(run('selected'),null);
run("choose('hearth');");
window.location.hash='';listeners.hashchange(); // Back to the original unfragmented page
assert.equal(run('selected'),null);assert.equal(get('house-view').hidden,false);
'''
        result = subprocess.run(
            ["node", "-e", script, str(Path(__file__).parents[1] / "site/house.js")],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
