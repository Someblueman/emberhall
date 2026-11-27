"""Crowded drawing controls and a reproducible native-browser fixture."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parent.parent


def write_fixture(destination, residents=15):
    """Build a labelled local drawing fixture, never a public house record."""
    snapshot = json.loads((ROOT / 'site/history.json').read_text())
    moment = snapshot['frames'][-1]
    moment['seq'] = 1
    moment['residents'] = [dict(id=f'fixture-{i}', name=f'Tag visitor {i+1}',
                                agent='codex', model='', room='workshop',
                                pose='working', presence='awake', tasks=[])
                           for i in range(residents)]
    moment['tasks'] = []
    snapshot.update(name='Emberhall · controlled crowded fixture', frames=[moment],
                    journal_head='tag-fixture', source_head='tag-fixture', commits=[])
    payload = json.dumps(snapshot, separators=(',', ':')).replace('<', '\\u003c')
    intercept = '<script>const tagFixture=' + payload + r''';
window.fetch=async url=>{
 const path=String(url).split('?')[0];
 if(path.endsWith('history.json'))return {ok:true,json:async()=>structuredClone(tagFixture)};
 if(path.endsWith('head.json'))return {ok:true,json:async()=>({journal_head:'tag-fixture',source_head:'tag-fixture'})};
 return {ok:false,status:404,json:async()=>({})};
};</script>'''
    metrics = r'''<p id="fixture-check" role="status" style="padding:16px;max-width:65ch">Controlled crowded fixture; checking tags…</p>
<script>
function checkTags(){
 const svg=document.getElementById('house'),rects=[...svg.querySelectorAll('.life-tag rect')];
 if(!rects.length){setTimeout(checkTags,100);return;}
 const boxes=rects.map(n=>n.getBBox()),names=[...svg.querySelectorAll('.room-label,.room-fact')].map(n=>n.getBBox());
 const intersects=(a,b)=>a.x<b.x+b.width&&a.x+a.width>b.x&&a.y<b.y+b.height&&a.y+a.height>b.y;
 let overlaps=0,roomOverlaps=0,clipped=0,textOutside=0;
 const v=svg.viewBox.baseVal;
 boxes.forEach((a,i)=>{
  overlaps+=boxes.slice(0,i).filter(b=>intersects(a,b)).length;
  roomOverlaps+=names.filter(b=>intersects(a,b)).length;
  if(a.x<v.x||a.y<v.y||a.x+a.width>v.x+v.width||a.y+a.height>v.y+v.height)clipped++;
  for(const text of rects[i].parentNode.querySelectorAll('text')){
   const t=text.getBBox();if(t.x<a.x||t.x+t.width>a.x+a.width)textOutside++;
  }
 });
 const drawing=svg.getBoundingClientRect();
 document.getElementById('fixture-check').textContent=`Controlled crowded fixture: ${boxes.length} tags; ${overlaps} tag intersections; ${roomOverlaps} room-name intersections; ${clipped} clipped tags; ${textOutside} overflowing text lines; drawing ${Math.round(drawing.width)} by ${Math.round(drawing.height)}.`;
}
setTimeout(checkTags,200);
document.addEventListener('click',()=>setTimeout(checkTags,100));
</script>'''
    html = (ROOT / 'site/index.html').read_text()
    html = html.replace('href="house.css', 'href="../site/house.css')
    html = html.replace('<script src="house.js', intercept + '<script src="../site/house.js')
    html = html.replace('</body>', metrics + '</body>')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html)


@unittest.skipUnless(shutil.which('node'), 'Node executes actual drawing code')
class NameTagLayoutTests(unittest.TestCase):
    def test_crowded_boxes_room_labels_text_width_and_bounds(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));const ctx=vm.createContext({document:{},assert});
vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
const collides=(a,b)=>a.x<b.x+b.width&&a.x+a.width>b.x&&a.top<b.top+b.height&&a.top+a.height>b.top;
function check(boxes,labels){
 for(let i=0;i<boxes.length;i++){
  const a=boxes[i];assert(Number.isFinite(a.top)&&Number.isFinite(a.x));
  for(const b of boxes.slice(0,i))assert(!collides(a,b));
  for(const l of labels)assert(!collides(a,{x:l.x-l.width/2,top:l.y-20,width:l.width,height:l.fact?44:28}));
 }
 const [x,y,w,h]=includeTagBounds('0 0 900 700',boxes).split(' ').map(Number);
 boxes.forEach(a=>assert(a.x>=x&&a.top>=y&&a.x+a.width<=x+w&&a.top+a.height<=y+h));
}
// More than twelve identical anchors proves the old retry limit cannot return.
const labels=[{x:400,y:80,width:250,fact:'busy'},{x:650,y:-40,width:350,fact:''}];
for(const n of [0,1,6,15,30,120]){
 const tags=Array.from({length:n},(_,i)=>({cx:400,top:100,width:120+(i%4)*35,id:i}));
 const before=JSON.stringify(tags),boxes=layoutNameTags(tags,labels);
 check(boxes,labels);assert.equal(JSON.stringify(tags),before);
 assert.deepEqual(boxes,layoutNameTags(tags,labels));
 assert.deepEqual(boxes.map(b=>b.id),tags.map(t=>t.id));
}
// Reproducible mixed widths, positions and room-title obstacles.
let state=971;const random=()=>((state=(Math.imul(state,1664525)+1013904223)>>>0)/4294967296);
for(let trial=0;trial<8;trial++){
 const obstacles=Array.from({length:20},()=>({x:random()*1200,y:random()*600-100,width:40+random()*300,fact:'occupied'}));
 const tags=Array.from({length:80},()=>({cx:random()*1200,top:random()*600,width:50+random()*350}));
 check(layoutNameTags(tags,obstacles),obstacles);
}
// Replay nameTags with the real three-column resident coordinates.
let removed=0;const nodes=[];
el=(tag,attrs,parent,text)=>{const n={tag,attrs,text,getComputedTextLength(){return text.length*(attrs.class==='life-name'?13:11);},remove(){removed++;}};nodes.push(n);return n;};
heldWork=()=>null;latelyEvents=()=>[];
const placed=Array.from({length:30},(_,i)=>({resident:{id:'r'+i,name:'WWWWWW '+i,pose:'working',agent:'codex',room:'workshop'},px:36+(i%3)*53,py:97+Math.floor(i/3)*40}));
const boxes=nameTags({ownerDocument:{createElementNS(){}}},placed,labels);check(boxes,labels);
assert.equal(removed,60);assert.equal(boxes.length,30);
boxes.forEach(b=>assert(b.width>=b.resident.name.length*13+30));
const stems=nodes.filter(n=>n.tag==='line'&&n.attrs.class==='life-stem');
stems.forEach((line,i)=>assert.equal(line.attrs.x2,p(placed[i].px,placed[i].py,0)[0]));
assert.equal(nameTags({},[{...placed[0],resident:{...placed[0].resident,pose:'sleeping'}}],[]).length,0);
assert.equal(includeTagBounds('0 0 900 700',[]),'0 0 900 700');
`,ctx);
'''
        result = subprocess.run([shutil.which('node'), '-e', script, str(ROOT / 'site/house.js')],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
