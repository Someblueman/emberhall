"""The homepage shows actual outcome transitions within its selected time window."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('node'), 'Node executes the actual renderer')
class RecentGrowthTests(unittest.TestCase):
    def test_window_history_and_visible_actions(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.listeners={};}
 appendChild(n){this.children.push(n);} replaceChildren(){this.children=[];}
 addEventListener(k,fn){this.listeners[k]=fn;}
 setAttribute(k,v){this[k]=v;} focus(){document.activeElement=this;}
}
const nodes={'recent-growth':new Element('div')};
const text=n=>[n.textContent,...n.children.map(text)].join(' ');
const all=n=>[n,...n.children.flatMap(all)];
const document={getElementById:id=>nodes[id]||all(nodes['recent-growth']).find(n=>n.id===id)||null,
 createElement:tag=>new Element(tag)};
const context=vm.createContext({document,assert,nodes,text,all});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
const legacy={id:'hearth',name:'Hearth'};
const plannedRoom={id:'gallery',name:'Gallery',status:'construction',planned_at:50000};
const project={id:'internal-choice-013',title:'Shadow Theatre',status:'active'};
const frames=[
 {seq:1,at:1,rooms:[legacy],shelf:{projects:[]}},
 {seq:2,at:50000,rooms:[legacy,plannedRoom],shelf:{projects:[project]}},
 {seq:3,at:50001,rooms:[legacy,{...plannedRoom,status:'open'}],shelf:{projects:[project]}},
 {seq:4,at:50002,event:{op:'finish'},rooms:[legacy,{...plannedRoom,status:'open'}],shelf:{projects:[project]}},
 {seq:5,at:100000,rooms:[legacy,{...plannedRoom,status:'open'}],shelf:{projects:[{...project,status:'done'}]}},
];
assert.equal(recentGrowth(frames,0,1).length,0); // legacy rooms are not construction
let changes=recentGrowth(frames,3,50002);
assert.equal(changes.length,3); // task finish is not project acceptance
assert.equal(changes[0].verb,'Room opened');
assert(!changes.some(change=>change.verb==='Milestone completed')); // future hidden
assert.equal(recentGrowth(frames,4,100000).length,1); // old transitions fall out
assert.equal(recentGrowth(frames,4,200000).length,0); // stale publication cannot invent today
assert.equal(recentGrowth(frames,4,100000)[0].verb,'Milestone completed');
data={frames,observed_at:50002,timezone:'UTC'};index=3;frame=frames[3];current=true;
renderRecentGrowth();
assert(text(nodes['recent-growth']).includes('Building now: Shadow Theatre'));
assert(!text(nodes['recent-growth']).includes('internal-choice-013'));
assert(all(nodes['recent-growth']).some(node=>node.href==='#shelf-card'));
assert(all(nodes['recent-growth']).some(node=>node.href==='#projects-view'));
let jumped=null;jumpToSequence=seq=>jumped=seq;
all(nodes['recent-growth']).find(node=>node.tag==='button').listeners.click();
assert.equal(jumped,3);
index=0;frame=frames[0];current=false;renderRecentGrowth();
assert(text(nodes['recent-growth']).includes('No selected project is active'));
assert(text(nodes['recent-growth']).includes('No room or project milestone changed'));
assert(!text(nodes['recent-growth']).includes('Shadow Theatre'));
// An open choice explains empty build slots, using only the selected frame.
frame={...frames[0],voting:{choices:[{id:'internal-round',status:'open',candidates:[1,2,3,4,5],
 votes:[{counted:true},{counted:false},{counted:true}]}]}};
renderRecentGrowth();
assert(text(nodes['recent-growth']).includes('Council choosing: 2 of 3 counted votes · 5 candidates'));
assert(!text(nodes['recent-growth']).includes('No selected project is active'));
assert(!text(nodes['recent-growth']).includes('internal-round'));
assert(all(nodes['recent-growth']).some(node=>node.href==='#voting-card'));
frame.voting.choices[0].status='closed';renderRecentGrowth();
assert(!text(nodes['recent-growth']).includes('Council choosing'));
frame=frames[0];renderRecentGrowth(); // older snapshot with no voting projection
assert(!text(nodes['recent-growth']).includes('Council choosing'));
// The compact card stays bounded even after a busy day.
data.frames=Array.from({length:10},(_,i)=>({seq:i+1,at:50000+i,rooms:[],shelf:{projects:
 Array.from({length:i},(_,j)=>({id:String(j),title:'Project '+j,status:'active'}))}}));
index=9;frame=data.frames[9];data.observed_at=50010;current=true;renderRecentGrowth();
const events=()=>all(nodes['recent-growth']).filter(n=>n.className==='growth-event');
assert.equal(events().length,5);
assert.match(text(nodes['recent-growth']),/Changes 1–5 of 9/);
assert($('growth-newer').disabled);
$('growth-earlier').listeners.click();
assert.match(text(nodes['recent-growth']),/Changes 6–9 of 9/);
assert.equal(events().length,4);assert($('growth-earlier').disabled);
assert.equal(document.activeElement,$('growth-list'));
events().at(-1).focus();const focusedId=document.activeElement.id;
renderRecentGrowth();
assert.equal(document.activeElement,$(focusedId));
events().at(-1).listeners.click();assert.equal(jumped,2);
$('growth-newer').listeners.click();
assert.match(text(nodes['recent-growth']),/Changes 1–5 of 9/);
$('growth-earlier').listeners.click();
current=false;index=4;frame=data.frames[index];renderRecentGrowth();
assert.equal(events().length,4);assert.equal($('growth-earlier'),null);
current=true;index=9;frame=data.frames[index];renderRecentGrowth();
assert.match(text(nodes['recent-growth']),/Changes 1–5 of 9/);
$('growth-earlier').listeners.click();
data.observed_at+=43201;renderRecentGrowth();assert.equal(events().length,0);
data.observed_at=50010;renderRecentGrowth();assert.match(text(nodes['recent-growth']),/Changes 1–5 of 9/);
`,context);
'''
        result = subprocess.run(['node', '-e', script, str(ROOT/'site/house.js')],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
