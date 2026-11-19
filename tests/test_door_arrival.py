"""The entrance loads independently; requesting the archive keeps its real loader."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(shutil.which("node"), "Node exercises browser JavaScript")
class DoorArrivalTests(unittest.TestCase):
    def test_arrival_archive_and_failure_boundaries(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=process.argv[1], nodes={},listeners={},classes=new Set(["entrance"]);
function node(id='') {return {id,hidden:false,textContent:'',children:[],listeners:{},
 setAttribute(k,v){this[k]=v;},getAttribute(k){return this[k];},
 replaceChildren(){this.children=[];},appendChild(n){this.children.push(n);},
 addEventListener(k,f){this.listeners[k]=f;},focus(){document.activeElement=this;},scrollIntoView(){this.scrolled=true;}};}
for(const match of fs.readFileSync(root+'/site/index.html','utf8').matchAll(/id="([^"]+)"/g))nodes[match[1]]=node(match[1]);
nodes['record-load'].hidden=true;
const document={getElementById:id=>nodes[id]||null,createElement:()=>node(),activeElement:null,
 body:{classList:{add:k=>classes.add(k),contains:k=>classes.has(k),remove:k=>classes.delete(k)}},
 addEventListener:(k,f)=>listeners[k]=f,
 querySelector:s=>s==='.room-card'?nodes['room-card']:s==='.page-view:not([hidden])'?nodes['house-view']:null};
const window={setInterval(){},location:{hash:''},history:{pushState:(a,b,hash)=>window.location.hash=hash},addEventListener(){}};
const at=1795029000;
const scene={version:1,seq:19215,observed_at:at,scene:{status:'occupied',
 resident:{name:'Mallow',agent:'codex'},room:{id:'workshop',name:'Workshop'},
 activity:'working',work:{id:'ten-second-door-arrival',title:'Make the first screen a working room',plain:'An actual house drawing.',
 project:{id:'house-door-choice',title:'The Ten-Second Door'}},destination:{href:'#room/workshop'}},
 changes:{since:at-43200,until:at,count:1,items:[{seq:1,at,title:'Workshop',verb:'Room opened'}]}};
const history={version:1,journal_head:'one',source_head:'source',frames:[{seq:1,scars:[]}],scars:{}};
let summary=scene,archiveAvailable=false;const calls=[];
const fetch=async path=>{calls.push(path);
 if(path==='now.json')return{ok:true,json:async()=>summary};
 if(path==='history.json')return{ok:archiveAvailable,status:503,json:async()=>history};
 return{ok:false,status:404,json:async()=>null};};
const ctx=vm.createContext({document,window,fetch,AbortSignal,Intl,Date});
let source=fs.readFileSync(root+'/site/house.js','utf8');
const tail='refresh();\nsetInterval(refresh,60000);setInterval(watch,10000);\n';assert(source.endsWith(tail));
vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext('refreshView=()=>{frame=data.frames[index];};bindControls=()=>{controlsReady=true;};showViewForHash=()=>{};',ctx);
source=fs.readFileSync(root+'/site/index.html','utf8').match(/<script id="arrival-script">([\s\S]*?)<\/script>/)[1];
vm.runInContext(source.replace('document.addEventListener("DOMContentLoaded",loadArrival);',''),ctx);
(async()=>{
 await ctx.refresh();assert.deepEqual(calls,[],'old renderer must wait for an archive request');
 await ctx.loadArrival();assert.deepEqual(calls,['now.json'],'the first room must not fetch the archive');
 assert.match(nodes['arrival-who'].textContent,/Mallow/);
 assert.equal(nodes['arrival-drawing'].visibility,'visible');
 assert.equal(nodes['arrival-resident'].visibility,'visible');
 assert.equal(nodes['arrival-enter'].href,'#room/workshop');
 assert.equal(nodes['arrival-changes'].children.length,1);
 // The Door handles skipping before archive controls exist, without fetching history.
 function skip(expected) {
   const before=calls.length,hash=window.location.hash;
   nodes[expected].scrolled=false;
   const event={defaultPrevented:false,preventDefault(){this.defaultPrevented=true;}};
   nodes['skip-content'].listeners.click(event);
   ctx.skipToContent(event); // the listener remains after the archive has been opened
   assert.equal(document.activeElement,nodes[expected]);assert(nodes[expected].scrolled);
   assert.equal(calls.length,before);assert.equal(window.location.hash,hash);
 }
 skip('arrival-title');
 // Enter the dated room with the archive still unavailable. Only its history link fetches history.
 const click=nodes["arrival-enter"];
 listeners.click({target:{closest:()=>click},button:0,preventDefault(){}});
 assert.equal(nodes["arrival-visit"].hidden,false);
 assert.equal(nodes["arrival-visit-name"].textContent,"Workshop");
 assert.match(nodes["arrival-visit-work"].textContent,/Mallow.*Make the first screen/);
 assert.equal(nodes["arrival-visit-history"].href,"#room/workshop");
 assert.deepEqual(calls,["now.json"]);
 skip('arrival-visit-name');
 ctx.leaveDatedRoom();
 assert.equal(nodes["arrival-visit"].hidden,true);
 skip('arrival-title');
 const blackout={...scene,scene:{...scene.scene,work:{id:"blackout-output-repair",
   title:"Keep Blackout output failures within its documented exit contract"}}};
 ctx.drawArrival(blackout);
 assert.equal(nodes["arrival-blackout"].visibility,"visible");
 assert.equal(nodes["arrival-page-detail"].textContent,blackout.scene.work.title);
 ctx.drawArrival(scene);
 // A stale publication cannot replace the accepted dated picture or start the archive.
 summary={...scene,observed_at:at-60,changes:{...scene.changes,since:at-43260,until:at-60}};
 await ctx.refreshArrival();assert.equal(calls.length,2);
 assert.match(nodes['arrival-status'].textContent,/dated picture is still here/);summary=scene;

 // The same drawing can honestly show a quiet record, without retaining a person or prop.
 ctx.drawArrival({...scene,scene:{status:'quiet'},changes:{...scene.changes,count:0,items:[]}});
 assert.equal(nodes['arrival-resident'].visibility,'hidden');
 assert.equal(nodes['arrival-drawing'].visibility,'hidden');assert.equal(nodes['arrival-quiet'].visibility,'visible');
 assert.equal(nodes['arrival-name'].textContent,'');
 assert.equal(nodes["arrival-page-detail"].hidden,true);
 const quiet={...scene,scene:{status:"quiet",activity:"quiet",resident:null,work:null,
   room:{id:"door",name:"The door"},destination:{href:"#room/door"}}};
 assert.equal(ctx.enterDatedRoom(quiet),true);
 assert.equal(nodes["arrival-visit-work"].textContent,"No resident was recorded awake.");
 assert.equal(nodes["arrival-visit-name"].textContent,"The door");ctx.leaveDatedRoom();
 ctx.drawArrival({...scene,scene:{...scene.scene,work:{...scene.scene.work,project:{id:'terminal-in-brainfuck',title:'A terminal in Brainfuck'}}}});
 assert.equal(nodes['arrival-terminal'].visibility,'visible');assert.equal(nodes['arrival-drawing'].visibility,'hidden');
 ctx.drawArrival({...scene,scene:{...scene.scene,work:{...scene.scene.work,project:{id:'you-were-supposed-to-drop-it',title:'You Were Supposed to Drop It'}}}});
 assert.equal(nodes['arrival-theatre'].visibility,'visible');assert.equal(nodes['arrival-terminal'].visibility,'hidden');
 // Record text is written literally, never interpreted as markup or an external destination.
 const hostile={...scene,scene:{...scene.scene,work:{...scene.scene.work,title:'<img src=x onerror=alert(1)>'},destination:{href:'https://outside.example'}}};
 ctx.drawArrival(hostile);assert.equal(nodes['arrival-page-detail'].textContent,hostile.scene.work.title);
 assert.equal(nodes['arrival-enter'].href,'#room/door');
 assert.equal(ctx.arrivalLink('javascript:alert(1)'),null);
 assert.equal(ctx.arrivalLink('projects/../private/index.html'),null);
 assert.equal(ctx.arrivalLink('projects/lantern-loop/index.html'),'projects/lantern-loop/index.html');
 assert.throws(()=>ctx.validateArrival({...scene,changes:{...scene.changes,since:at-48}}),/twelve elapsed hours/);
 assert.throws(()=>ctx.validateArrival({...scene,scene:{status:'occupied'}}),/Incomplete/);
 // A requested but absent archive keeps the existing recovery notice; it never changes the summary.
 assert.equal(await ctx.openArrivalArchive('#room/archive'),false);
 assert.equal(calls.at(-1),'history.json');assert.equal(nodes['record-load'].hidden,false);
 assert.equal(nodes.arrival.hidden,false);assert(!classes.has('archive-open'));
 skip('arrival-title');
 assert.match(nodes.error.textContent,/could not be loaded/);
 // Returning to the Door cancels the background retry. A pending room visit can recover.
 window.location.hash="#arrival";const beforeRetry=calls.length;
 await ctx.refresh();assert.equal(calls.length,beforeRetry);
 window.location.hash="#room/archive";archiveAvailable=true;await ctx.refresh();
 assert.equal(nodes['record-load'].hidden,true);assert.equal(vm.runInContext('frame.seq',ctx),1);
 // A direct old-room URL opens the archive, bypassing the arrival fetch.
 calls.length=0;await ctx.loadArrival();assert.equal(calls[0],'history.json');assert(!calls.includes('now.json'));
})().catch(e=>{console.error(e);process.exitCode=1;});
'''
        result = subprocess.run([shutil.which("node"), "-e", script, str(ROOT)],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_inline_entrance_waits_for_the_existing_renderer(self):
        source = (ROOT / "site/index.html").read_text()
        self.assertLess(source.index('<script src="house.js?'), source.index('<script id="arrival-script">'))
        self.assertIn('document.addEventListener("DOMContentLoaded",loadArrival)', source)
        self.assertIn('#arrival, #record-load', source)  # no-script page retains its own entrance
        self.assertIn('aria-labelledby="arrival-picture-title arrival-picture-desc"', source)
        self.assertIn('id="arrival-title" tabindex="-1"', source)
