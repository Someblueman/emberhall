"""Compound scenery paths preserve projected strokes and room interaction targets."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]

SCRIPT=r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.listeners={};this.style={};this.classList={toggle(){}};}
 appendChild(node){this.children.push(node);return node;}
 replaceChildren(){this.children=[];}
 setAttribute(key,value){this.attrs[key]=String(value);}
 addEventListener(key,value){this.listeners[key]=value;}
}
const source=fs.readFileSync(process.argv[1],'utf8');
const nodes={},document={getElementById:id=>nodes[id]??(nodes[id]=new Element('div')),
 createElementNS:(ns,tag)=>new Element(tag),querySelector:()=>null};
const context=vm.createContext({document,Date,Intl,Math,URL});
// The public startup owns network/timers; drawing tests execute only its declarations.
const startup=source.lastIndexOf('\nrefresh();');assert(startup>0);
vm.runInContext(source.slice(0,startup),context);
const run=s=>vm.runInContext(s,context);
const flatten=n=>[n,...n.children.flatMap(flatten)];
function normalized(node){
 const attrs={...node.attrs};
 if(attrs['data-scenery-lines']==='true'){
  const segments=attrs.d.trim().split(/\s+(?=M)/);
  return segments.map(segment=>{
   const xy=segment.replace(/[ML]/g,' ').trim().split(/\s+/).map(Number);
   assert(xy.every(Number.isFinite));assert.equal(xy.length,4);
   return {tag:'polyline',attrs:{points:`${xy[0]},${xy[1]} ${xy[2]},${xy[3]}`,
    fill:'none',stroke:attrs.stroke,'stroke-width':attrs['stroke-width']},text:undefined,children:[]};
  });
 }
 return [{tag:node.tag,attrs,text:node.textContent,children:node.children.flatMap(normalized)}];
}
run(`data={name:'Emberhall',frames:[],scars:[]};current=false;
 frame={seq:1,at:1000,rooms:['door','hearth','workshop','archive','council','bedroom',
 'counting','assay','study','parlor','gallery','chronicle','salvage'].map(id=>({id,name:id})),
 residents:[],runs:[],scars:[],tasks:[],council:{pending:0},lessons:0};data.frames=[frame];`);
// Cover larger occupied rooms, uneven floorboard counts and both awake/sleep paint.
for(const occupancy of [0,7,19]){
 run(`frame.residents=Array.from({length:${occupancy}},(_,i)=>({id:'r'+i,name:'Guest '+i,
 room:'door',pose:'standing',agent:'codex',presence:'awake'}));drawHouse();`);
 const batched=normalized(nodes.house),batchedCount=flatten(nodes.house).length;
 const controls=flatten(nodes.house).filter(n=>n.attrs.role==='button');
 assert.equal(controls.length,13);
 for(const node of controls){assert.equal(node.attrs.tabindex,'0');assert(node.listeners.click);assert(node.listeners.keydown);}
 const saved=run('sceneryLines');context.oldScenery=saved;
 run(`sceneryLines=(g,segments,color,width=1)=>{for(const segment of segments)line(g,segment,color,width);};drawHouse();`);
 const unbatched=normalized(nodes.house),unbatchedCount=flatten(nodes.house).length;
 assert.deepEqual(batched,unbatched);
 assert(unbatchedCount-batchedCount>=324);
 if(occupancy===0){assert.equal(batchedCount,844);assert.equal(unbatchedCount,1168);}
 run('sceneryLines=oldScenery');
}
// Each stroke remains an independent subpath; no unwanted joins across the fence gate.
run(`const fixture=new Object();fixture.group=document.createElementNS('', 'g');
 sceneryLines(fixture.group,[[[-64,-72,0],[-64,-72,12]],[[64,-72,0],[64,-72,12]]],'#b9a67c',2);
 assertFixture=fixture;`);
const fixture=run('assertFixture.group');
assert.equal(fixture.children.length,1);
assert.equal((fixture.children[0].attrs.d.match(/M/g)||[]).length,2);
assert.equal(run(`sceneryLines(document.createElementNS('','g'),[],'#fff')`),null);
console.log('13-room geometry and controls identical; empty scene 1168 -> 844 SVG nodes');
'''


@unittest.skipUnless(shutil.which('node'),'Node executes the actual renderer')
class SceneryPathChecks(unittest.TestCase):
    def test_geometry_paint_order_and_controls_with_fewer_nodes(self):
        result=subprocess.run(['node','-e',SCRIPT,str(ROOT/'site/house.js')],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('1168 -> 844',result.stdout)


if __name__=='__main__':unittest.main()
