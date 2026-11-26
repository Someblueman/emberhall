"""Exercise the real collection renderer, link boundary and dated availability."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which('node'), 'Node executes the renderer')
class CreationsGalleryTests(unittest.TestCase):
    def test_safe_actions_historical_filter_and_missing_manifest(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.listeners={};}
 appendChild(n){this.children.push(n);} replaceChildren(){this.children=[];}
 setAttribute(k,v){this[k]=v;} addEventListener(k,fn){this.listeners[k]=fn;}
}
const root=new Element('div'),document={getElementById:()=>root,querySelector:()=>root,createElement:t=>new Element(t)};
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
const manifest=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const ctx=vm.createContext({assert,document,URL,AbortSignal,root,all,text,manifest,fetch:async()=>({ok:false})});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
const creation={id:'garden',title:'<img src=x>',summary:'Send a picture',category:'creation',action:'Play',href:'projects/garden/'};
const tool={id:'lens',title:'Lens',summary:'Read records',category:'house-tool',action:'Read guide',href:'https://github.com/Someblueman/emberhall/blob/main/projects/lens/README.md'};
for(const href of ['javascript:alert(1)','//evil.test/','projects/../secret/','projects/a/%2e%2e/','projects/a/\\\\secret/','https://evil.test/'])
 assert.equal(collectionUrl({...creation,href}),null);
assert.equal(collectionUrl({...tool,href:'https://github.com@evil.test/README.md'}),null);
catalog=[creation,tool];frame={shelf:{projects:[{idea:'garden',status:'done'},{idea:'lens',status:'done'}]}};current=true;
renderCollection();assert.match(text(root),/Play <img src=x>/);assert.match(text(root),/Read guide Lens/);
assert.equal(all(root).filter(n=>n.tag==='img').length,0);
assert.equal(all(root).find(n=>n.tag==='details').open,false);
assert.equal(all(root).find(n=>n.tag==='a').href,'projects/garden/');
current=false;frame={shelf:{projects:[{idea:'garden',status:'active'}]}};renderCollection();
assert.equal(all(root).filter(n=>n.tag==='a').length,0);assert.match(text(root),/No published creations/);
assert.match(text(root),/current published versions/);
`,ctx);
(async()=>{
 await ctx.loadCatalog('new-source');
 vm.runInContext(`renderCollection();assert.match(text(root),/Collection links are unavailable/);`,ctx);
 ctx.fetch=async()=>({ok:true,json:async()=>({version:1,projects:[{id:'garden',title:'Garden',summary:'Play',category:'creation',action:'Play',href:'projects/garden/'},{id:'bad',title:'Bad',summary:'X',category:'creation',href:'javascript:alert(1)'}]})});
 await ctx.loadCatalog('new-source');
 vm.runInContext(`assert.equal(catalog.length,1);assert.equal(catalogSource,'new-source');`,ctx);
 ctx.fetch=async()=>({ok:true,json:async()=>manifest});
 await ctx.loadCatalog('actual-manifest');
 vm.runInContext(`
 assert.equal(catalog.length,manifest.projects.length,'Every committed project must survive the URL filter');
 current=true;frame={shelf:{projects:manifest.projects.map(p=>({idea:p.id,status:'done'}))}};
 renderCollection();
 assert.equal(all(root).find(n=>n.tag==='h3').textContent,'Tessera Loom','Show the real drawing first');
 const preview=all(root).find(n=>n.tag==='img');
 assert.equal(preview.src,'projects/tessera-loom/gallery-preview.svg');
 assert.match(preview.alt,/Blue quarter-circle arcs/);
 assert.equal(preview.width,preview.height);
 assert.equal(manifest.projects.find(p=>p.id==='tessera-loom').files.includes(preview.src),true);
 const shown=all(root).filter(n=>n.tag==='img');
 assert.equal(shown.map(n=>n.src).join('|'),
  'projects/tessera-loom/gallery-preview.svg|projects/lantern-loop/gallery-preview.svg|projects/night-ferry/gallery-preview.svg|projects/signal-garden/gallery-preview.svg|projects/specimen-cards/gallery-preview.svg|projects/shadow-theatre/gallery-preview.svg|projects/cue-rehearsal/gallery-preview.svg|projects/rain-ledger/gallery-preview.svg|projects/review-skein/gallery-preview.svg|projects/five-marks/gallery-preview.svg|projects/left-glove-post/gallery-preview.svg|projects/bench-for-two/gallery-preview.svg|projects/last-dance-school/gallery-preview.svg|projects/terminal-in-brainfuck/gallery-preview.svg|projects/rail-replacement-geese/gallery-preview.svg|projects/you-were-supposed-to-drop-it/gallery-preview.svg',
  'Every listed real-output browser creation preview shows in the present view');
 for(const image of shown){
  assert.equal(image.loading,'lazy');
  assert.match(image.alt,/.{40,}/,'Previews carry real alternative text');
  assert.ok(image.width>0&&image.height>0,'Previews declare their dimensions');
  const owner=manifest.projects.find(p=>p.files.includes(image.src));
  assert.ok(owner,'Every shown preview is listed in the public manifest');
 }
 const geese=manifest.projects.find(p=>p.id==='rail-replacement-geese');
 assert.equal(all(root).find(n=>n.tag==='a'&&n.href===geese.href).textContent,'Play Rail Replacement Geese →');
 frame.shelf.projects.find(p=>p.idea===geese.id).status='active';
 renderCollection();
 assert.ok(!all(root).some(n=>n.href===geese.href||n.src==='projects/rail-replacement-geese/gallery-preview.svg'));
 const rain=manifest.projects.find(p=>p.id==='rain-ledger');
 assert.ok(rain,'rain-ledger must be registered in site/projects.json');
 assert.equal(all(root).find(n=>n.tag==='a'&&n.href===rain.href).textContent,'Open Rain Ledger →');
 catalog=[{...creation,id:'tessera-loom',files:['https://evil.test/gallery-preview.svg']}];
 frame={shelf:{projects:[{idea:'tessera-loom',status:'done'}]}};renderCollection();
 assert.equal(all(root).filter(n=>n.tag==='img').length,0,'Never request an unlisted preview');
 catalog=manifest.projects;current=false;
 frame={shelf:{projects:manifest.projects.filter(p=>p.id!=='tessera-loom').map(p=>({idea:p.id,status:'done'}))}};
 renderCollection();assert.equal(all(root).filter(n=>n.tag==='img').length,0,'No future output in historical views');
 frame={shelf:{projects:manifest.projects.map(p=>({idea:p.id,status:'done'}))}};
 renderCollection();assert.equal(all(root).filter(n=>n.tag==='img').length,0,'Even completed creations show no present-day preview in a historical view');
 current=true;
 frame={shelf:{projects:manifest.projects.map(p=>({idea:p.id,status:'done'}))}};renderCollection();
 const sow=manifest.projects.find(p=>p.id==='sow-ledger');
 assert.equal(all(root).find(n=>n.tag==='a'&&n.href===sow.href).textContent,'Read guide Sow Ledger →');
 for(const href of ['https://evil.test/README.md','https://github.com/Other/repo/blob/main/projects/sow-ledger/README.md','https://github.com/Someblueman/emberhall/blob/main/projects/../README.md'])
  assert.equal(collectionUrl({...sow,href}),null);
 assert.equal(collectionUrl({...sow,action:'Play'}),null);
 `,ctx);

})().catch(e=>{console.error(e);process.exitCode=1;});
'''
        source = Path(__file__).parents[1] / 'site/house.js'
        result = subprocess.run(['node', '-e', script, str(source), str(source.with_name('projects.json'))], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_preview_is_the_studios_real_default_export(self):
        root = Path(__file__).parents[1]
        result = subprocess.run(
            ['node', '-e', 'const m=require("./projects/tessera-loom/loom.js"); process.stdout.write(m.svg(m.initial(),4));'],
            cwd=root, capture_output=True, timeout=15, check=True)
        self.assertEqual((root / 'projects/tessera-loom/gallery-preview.svg').read_bytes(), result.stdout)

    def test_shadow_and_signal_previews_are_model_generated(self):
        root = Path(__file__).parents[1]
        for project in ('shadow-theatre', 'signal-garden', 'specimen-cards', 'rain-ledger', 'five-marks'):
            with self.subTest(project=project):
                result = subprocess.run(
                    ['node', '-e', f'process.stdout.write(require("./projects/{project}/make-gallery-preview.js").svg());'],
                    cwd=root, capture_output=True, timeout=15, check=True)
                self.assertEqual((root / f'projects/{project}/gallery-preview.svg').read_bytes(), result.stdout)
        for project in ('night-ferry', 'cue-rehearsal'):
            with self.subTest(project=project):
                result = subprocess.run(
                    ['node', f'./projects/{project}/make-gallery-preview.js'],
                    cwd=root, capture_output=True, timeout=15, check=True)
                self.assertEqual((root / f'projects/{project}/gallery-preview.svg').read_bytes(), result.stdout)

    def test_gallery_room_links_to_gallery_and_labels_are_bound(self):
        root = Path(__file__).parents[1]
        html = (root / 'site/index.html').read_text()
        self.assertIn('<label class="notes-toggle" for="presence-notes">', html)
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.style={};this.dataset={};this.textContent='';this.listeners={};this.classList={toggle(){}};}
 appendChild(n){this.children.push(n);return n;} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=String(v);} addEventListener(k,fn){this.listeners[k]=fn;}
}
const nodes={};
const get=id=>(nodes[id]||(nodes[id]=new Element('div')));
const document={getElementById:get,querySelector:()=>null,createElement:t=>new Element(t)};
const all=n=>[n,...n.children.flatMap(all)];
const ctx=vm.createContext({assert,document,all,URL,Intl,Date,Math,Number,String,Set,Object,Array});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
data={timezone:'UTC',observed_at:1000,name:'Emberhall',journal_head:'abc',commits:[],frames:[{seq:1,at:1000,event:{op:'wake',actor:'r1'},
  rooms:[{id:'gallery',name:'Gallery',status:'open',floor:0}],
  residents:[{id:'r1',name:'Yarrow',pose:'standing',room:'gallery'}],
  tasks:[{id:'t1',title:'T1',status:'open',generation:0}],
  ambitions:[],runs:[],budgets:[],scars:[],shelf:{projects:[]}}]};
index=0;frame=data.frames[0];current=true;selected='gallery';
roomPanel();
const galleryLinks=all(document.getElementById('room-content')).filter(n=>n.tag==='a');
assert(galleryLinks.some(n=>n.href==='#gallery-view'),'Gallery room must link to #gallery-view');
assert(!galleryLinks.some(n=>n.href==='#projects-view'),'Gallery room must not link to #projects-view');
document.getElementById('history').max=1;document.getElementById('floor-picker').value='0';
drawHouse=dormControls=accounts=shelf=voting=renderCollection=renderResidentPulse=renderRecentGrowth=renderLately=lighting=()=>{};
render();
assert.match(document.getElementById('presence-line').textContent,/1 unfinished thread\\./);
assert.doesNotMatch(document.getElementById('presence-line').textContent,/1 unfinished threads/);
frame.tasks.push({id:'t2',title:'T2',status:'open',generation:0});
render();
assert.match(document.getElementById('presence-line').textContent,/2 unfinished threads\\./);
const wsBox=document.createElement('div');
renderWorkshopTasks(wsBox);
const searchLabel=all(wsBox).find(n=>n.tag==='label'&&n.textContent==='Find work');
assert.equal(searchLabel.attrs.for,'workshop-search');
`,ctx);
'''
        result = subprocess.run(['node', '-e', script, str(root / 'site/house.js')], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
