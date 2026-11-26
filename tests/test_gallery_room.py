"""Exercise the Gallery room's actual cards, browsing, and dated availability."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.attrs={};this.textContent='';}
 appendChild(n){this.children.push(n);return n;} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=v;} addEventListener(k,fn){this.listeners[k]=fn;}
 focus(){document.activeElement=this;} scrollIntoView(){this.scrolled=true;}
}
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
const root=new Element('div'),nodes={};
const document={createElement:t=>new Element(t),activeElement:null,querySelector:()=>root,
 getElementById:id=>all(root).find(n=>n.id===id)||nodes[id]||null};
const manifest=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const ctx=vm.createContext({assert,document,URL,AbortSignal,root,all,text,nodes,Element,manifest});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
catalog=manifest.projects;current=true;
frame={seq:90,rooms:[{id:'gallery',name:'The Gallery',status:'open'}],residents:[],tasks:[],scars:[],
 shelf:{projects:manifest.projects.map(p=>({idea:p.id,status:'done'}))}};
const get=id=>document.getElementById(id),show=()=>{root.replaceChildren();renderGalleryRoom(root);};
const images=()=>all(root).filter(n=>n.tag==='img');
`,ctx);
'''


@unittest.skipUnless(shutil.which('node'), 'Node executes the renderer')
class GalleryRoomTests(unittest.TestCase):
    def run_renderer(self, checks):
        result = subprocess.run(
            ['node', '-e', HARNESS + '\nvm.runInContext(' + repr(checks) + ',ctx);',
             str(ROOT / 'site/house.js'), str(ROOT / 'site/projects.json')],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_real_preview_direct_action_and_bounded_browsing(self):
        self.run_renderer(r'''
const before=JSON.stringify(frame);show();
assert.equal(all(root).filter(n=>n.tag==='article').length,1);
assert.equal(images().length,1);assert.match(images()[0].src,/tessera-loom/);
assert.match(images()[0].alt,/Blue quarter-circle arcs/);
assert.equal(all(root).find(n=>n.className==='creation-action').href,'projects/tessera-loom/index.html');
assert(get('gallery-room-previous').disabled);
const titles=[];
while(true){
 titles.push(text(get('gallery-room-position')));
 if(get('gallery-room-next').disabled)break;
 get('gallery-room-next').listeners.click();
 assert.equal(document.activeElement,get('gallery-room-display'));
 assert(get('gallery-room-display').scrolled);
}
assert(titles.length>=7);assert(titles.some(t=>/Night Ferry/.test(t)));
assert(!titles.some(t=>/Sow Ledger|Assay|Blackout/.test(t)));
assert.equal(new Set(titles).size,titles.length);
get('gallery-room-previous').listeners.click();assert(!get('gallery-room-next').disabled);
assert.equal(get('gallery-room-next').attrs['aria-controls'],'gallery-room-display');
assert.equal(get('gallery-room-position').attrs.role,'status');
assert.equal(JSON.stringify(frame),before);
''')

    def test_history_limits_entries_and_hides_present_output(self):
        self.run_renderer(r'''
show();get('gallery-room-next').listeners.click();
const chosen=galleryRoomChoice;show();assert.equal(galleryRoomChoice,chosen);
current=false;frame.shelf.projects=[{idea:'tessera-loom',status:'done'},{idea:'night-ferry',status:'active'}];show();
assert.equal(galleryRoomChoice,'tessera-loom');assert.equal(images().length,0);
assert.match(text(root),/Pictures are hidden; links open current published versions/);
assert(!all(root).some(n=>n.className==='creation-action'&&/Night Ferry/.test(n.textContent)));
assert(get('gallery-room-next').disabled);
frame.shelf.projects=[];show();assert.match(text(root),/No browser creations were completed/);
assert.equal(all(root).filter(n=>n.className==='creation-action').length,0);
''')

    def test_unavailable_manifest_refresh_and_safe_output(self):
        self.run_renderer(r'''
catalog=null;show();assert.match(text(root),/Creation links are unavailable/);
assert.equal(all(root).find(n=>n.tag==='a').href,'#gallery-view');
catalog=manifest.projects;show();assert.equal(images().length,1);
catalog=[{...catalog[0],title:'<img src=x>',summary:'<script>evil()</script>',files:[]}];show();
assert.match(text(root),/<img src=x>/);assert.match(text(root),/<script>evil/);
assert.equal(images().length,0);assert(!all(root).some(n=>n.tag==='script'));
catalog[0].href='javascript:evil()';show();
assert.equal(all(root).filter(n=>n.className==='creation-action').length,0);
''')

    def test_refresh_retains_the_selected_creation_and_keyboard_focus(self):
        self.run_renderer(r'''
show();get('gallery-room-next').listeners.click();
const chosen=galleryRoomChoice;get('gallery-room-next').focus();
roomPanel=show;lighting=accounts=drawHouse=renderViewContext=renderCollection=renderRecentGrowth=renderLately=()=>{};
refreshView();assert.equal(galleryRoomChoice,chosen);
assert.equal(document.activeElement,get('gallery-room-next'));
get('gallery-room-previous').listeners.click();
refreshView();assert.equal(document.activeElement,get('gallery-room-display'));
''')

    def test_room_content_only_appears_when_open(self):
        self.run_renderer(r'''
for(const id of ['room-content','room-kicker','room-title','room-description','room-context'])nodes[id]=new Element('div');
selected='gallery';roomPanel();assert.match(text(nodes['room-content']),/Take something off the shelf/);
for(const status of ['construction','closed']){
 frame.rooms[0].status=status;roomPanel();
 assert.doesNotMatch(text(nodes['room-content']),/Take something off the shelf|Play Night Ferry/);
}
''')
