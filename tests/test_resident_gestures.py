"""Check the actual figure renderer against selected-frame room evidence."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node executes the shipped SVG renderer")
class ResidentGestureTests(unittest.TestCase):
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
const person={id:'tern',name:'Tern',agent:'codex',presence:'recorded awake',pose:'standing',room:'door'};
function render(resident=person){const root=new Element('g');figure(root,resident,40,90);return root;}
function gesture(root){return all(root).find(node=>node.attrs['data-gesture']);}
`+process.argv[2],context);
'''
        source = Path(__file__).resolve().parents[1] / "site" / "house.js"
        result = subprocess.run(["node", "-e", script, str(source), assertions],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rooms_have_distinct_symbolic_gestures_without_changing_identity(self):
        self.render_check(r'''
const shapes=[];
for(const [room,expected] of Object.entries({door:'arrival',hearth:'conversation',workshop:'plans',archive:'reading',council:'deliberation'})) {
 const resident={...person,room,pose:room==='hearth'?'sitting':'standing'},before=JSON.stringify(resident);
 const root=render(resident),action=gesture(root);
 assert.equal(action.attrs['data-gesture'],expected);
 assert.match(text(action),/last recorded room, not live activity/);
 assert.equal(all(root).filter(n=>n.attrs['data-resident']==='tern').length,1);
 assert.match(text(root),/Tern · Codex · recorded awake/);assert(text(root).includes('◆'));
 assert.equal(JSON.stringify(resident),before);assert(!JSON.stringify(root).includes('NaN'));
 shapes.push(JSON.stringify(action.children.filter(n=>n.tag!=='title')));
}
assert.equal(new Set(shapes).size,5);
// Family marks remain distinct when residents share a room and gesture.
for(const [agent,mark] of Object.entries({codex:'◆',opencode:'■',muse:'✦',agy:'●',unknown:'○'})) {
 const root=render({...person,agent,room:'archive'});assert(text(root).includes(mark));
 assert.equal(gesture(root).attrs['data-gesture'],'reading');
}
''')

    def test_selected_room_controls_the_figure_and_unknown_rooms_stay_neutral(self):
        self.render_check(r'''
const past={...person,room:'door'},latest={...person,room:'archive'};
frame={seq:1,residents:[past]};data={frames:[frame,{seq:2,residents:[latest]}]};
const before=JSON.stringify({frame,data});
assert.equal(gesture(render(frame.residents[0])).attrs['data-gesture'],'arrival');
frame=data.frames[1];assert.equal(gesture(render(frame.residents[0])).attrs['data-gesture'],'reading');
frame=data.frames[0];assert.equal(gesture(render(frame.residents[0])).attrs['data-gesture'],'arrival');
assert.equal(JSON.stringify({frame,data}),before);
for(const room of ['unknown','__proto__','constructor',undefined])
 assert.equal(gesture(render({...person,room})).attrs['data-gesture'],'standing');
const hostile=render({...person,name:'<script>unsafe</script>',room:'<img onerror=unsafe>'});
assert(text(hostile).includes('<script>unsafe</script>'));assert(!all(hostile).some(n=>['script','img'].includes(n.tag)));
assert.equal(gesture(hostile).attrs['data-gesture'],'standing');
''')

    def test_sleep_keeps_the_bunk_without_awake_props(self):
        self.render_check(r'''
for(const room of ['bedroom','archive','workshop','council','hearth','door']) {
 const resident={...person,room,pose:'sleeping',presence:'asleep'},before=JSON.stringify(resident);
 const root=render(resident);assert.equal(gesture(root),undefined);
 assert.match(text(root),/Tern · Codex · asleep/);assert(text(root).includes('z'));assert(text(root).includes('◆'));
 assert(all(root).some(n=>n.tag==='polygon')); // The existing bed is still drawn.
 assert.equal(JSON.stringify(resident),before);
}
''')
