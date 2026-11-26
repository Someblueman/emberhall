"""Exercise the shipped SVG furnishings with historical, bounded record data."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node executes the actual SVG renderer")
class RoomInteriorTests(unittest.TestCase):
    def render_check(self, assertions):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.textContent='';}
 appendChild(node){this.children.push(node);} setAttribute(k,v){this.attrs[k]=String(v);}
}
const document={createElementNS:(_,tag)=>new Element(tag)};
const all=node=>[node,...node.children.flatMap(all)];
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const context=vm.createContext({document,assert,Element,all,text});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
function render(room){const root=new Element('g');furnishings(root,room,0,0,false,[]);return root;}
function marked(root,key){return all(root).filter(node=>node.attrs[key]!==undefined);}
`+process.argv[2],context);
'''
        source = Path(__file__).resolve().parents[1] / "site" / "house.js"
        result = subprocess.run(["node", "-e", script, str(source), assertions],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_gallery_exhibits_only_selected_frame_completions_and_stays_bounded(self):
        self.render_check(r'''
const done=Array.from({length:9},(_,i)=>({id:'project-'+i,title:'Creation '+i,status:'done',milestone:'Witness '+i}));
frame={seq:30,rooms:[],shelf:{projects:[...done,{id:'active',title:'Unfinished',status:'active'}]}};
const before=JSON.stringify(frame),gallery=render('gallery');
assert.equal(marked(gallery,'data-interior')[0].attrs['data-interior'],'gallery');
assert.equal(marked(gallery,'data-exhibit').map(n=>n.attrs['data-exhibit']).join(','),'project-6,project-7,project-8');
assert.match(text(gallery),/9 completed/);assert.match(text(gallery),/Creation 8.*Witness 8/);
assert(!text(gallery).includes('Unfinished'));assert.equal(JSON.stringify(frame),before);
// The latest catalog/data cannot leak into an earlier frame, even when loaded.
data={frames:[frame]};catalog=[{id:'future',title:'Future creation'}];
frame={seq:1,rooms:[],shelf:{projects:[{id:'project-8',title:'Creation 8',status:'active'}]}};
const earlier=render('gallery');assert.equal(marked(earlier,'data-exhibit').length,0);
assert.match(text(earlier),/0 completed/);assert(!text(earlier).includes('Creation 8'));
frame={seq:1,rooms:[]};assert.equal(marked(render('gallery'),'data-exhibit').length,0);
frame={seq:2,rooms:[],shelf:{projects:[{id:'safe',title:'<script>not markup</script>',status:'done'}]}};
const untrusted=render('gallery');assert(text(untrusted).includes('<script>not markup</script>'));
assert(!all(untrusted).some(n=>n.tag==='script'));
''')

    def test_chronicle_uses_ordered_room_history_without_future_or_invented_entries(self):
        self.render_check(r'''
const history=Array.from({length:9},(_,i)=>({kind:i%2?'room-open':'room-plan',sequence:i+1})).reverse();
frame={seq:8,rooms:[{id:'chronicle',name:'Chronicle',history},{id:'legacy',name:'Legacy'}]};
const before=JSON.stringify(frame),chronicle=render('chronicle');
assert.equal(marked(chronicle,'data-interior')[0].attrs['data-interior'],'chronicle');
assert.equal(marked(chronicle,'data-history-sequence').map(n=>n.attrs['data-history-sequence']).join(','),'3,4,5,6,7,8');
assert.match(text(chronicle),/8 room entries/);assert(!text(chronicle).includes('event 9'));
assert.equal(JSON.stringify(frame),before);assert(!JSON.stringify(chronicle).includes('NaN'));
data={frames:[frame]};frame={seq:1,rooms:[{id:'chronicle',name:'Chronicle'}]};
const earlier=render('chronicle');assert.equal(marked(earlier,'data-history-sequence').length,0);
assert.match(text(earlier),/0 room entries/);assert(!text(earlier).includes('event 8'));
// Furniture remains recognizable without claiming historical activity.
assert(all(earlier).filter(n=>n.tag==='polygon').length>3);
assert.notEqual(JSON.stringify(earlier),JSON.stringify(render('gallery')));
''')
