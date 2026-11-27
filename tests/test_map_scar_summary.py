"""Historical damage cannot grow out of the drawing's room floor."""
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(shutil.which("node"), "Node runs the actual drawing helpers")
class MapScarSummaryTests(unittest.TestCase):
    def test_large_history_has_constant_geometry_and_keeps_receipts(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[1],'utf8');
const tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));
const ctx=vm.createContext({document:{},assert});
vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
const nodes=[];
el=(tag,attrs,parent,text)=>{const n={tag,attrs,text};nodes.push(n);return n;};
assert.equal(drawRoomScars({},100,200,160,[]),'');
assert.equal(nodes.length,0);
let geometry;
for(const count of [1,2,181,434,10000]) {
  nodes.length=0;
  const marks=Array.from({length:count},(_,i)=>Object.freeze({id:'scar-'+i,mended:i%2===0}));
  const before=JSON.stringify(marks);
  const summary=drawRoomScars({},100,200,160,Object.freeze(marks));
  assert.equal(JSON.stringify(marks),before);
  assert.equal(nodes.length,3); // one group, title and stroke at any age
  assert.equal(nodes.filter(n=>n.tag==='polyline').length,1);
  const stroke=nodes.find(n=>n.tag==='polyline');
  if(!geometry)geometry=stroke.attrs.points;
  assert.equal(stroke.attrs.points,geometry);
  assert.equal(stroke.attrs.stroke,count===1?'#f0c77b':'#b66f52');
  const title=nodes.find(n=>n.tag==='title').text;
  assert(title.startsWith(count+' historical '+(count===1?'mark':'marks')));
  assert(title.includes(Math.ceil(count/2)+' mended'));
  assert(title.includes('not live alerts'));
  assert.equal(summary,count+' old '+(count===1?'mark':'marks'));
  assert(!nodes.some(n=>n.text==='!'));
}
// Drawing a summary must not truncate or alter what the room disclosure reads.
frame={scars:Array.from({length:181},(_,i)=>({id:'scar-'+i,mended:false})),tasks:[]};
data={scars:Object.fromEntries(frame.scars.map(s=>[s.id,{room:'bedroom',title:s.id,basis:'Recorded'}]))};
effectiveTasks=()=>[];
const receipts=visibleScars();
drawRoomScars({},0,0,160,receipts);
assert.equal(visibleScars().length,181);
assert.deepEqual(visibleScars().map(s=>s.title),receipts.map(s=>s.title));
`,ctx);
'''
        result = subprocess.run(
            [shutil.which("node"), "-e", script, str(ROOT / "site/house.js")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
