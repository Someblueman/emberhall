"""A temporary collection failure must not strand the Gallery on a stable head."""
from pathlib import Path
import json
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


def write_fixture(destination, failures=1):
    """Real page/renderer, a completed real guide, and a recoverable manifest request."""
    from tests.test_site_refresh_scheduling import write_missing_snapshot_fixture
    write_missing_snapshot_fixture(destination, failures=0)
    path = Path(destination)
    entry = next(p for p in json.loads((ROOT / 'site/projects.json').read_text())['projects']
                 if p['id'] == 'wake-digest')
    setup = ('fixtureSnapshot.frames[0].shelf={ideas:[],choices:[],needs:[],projects:'
             '[{id:"fixture-wake-digest",idea:"wake-digest",title:"Wake Digest",'
             'status:"done",milestones:[],completed:0}]};'
             f'let collectionFailures={int(failures)};const fixtureCatalog='
             + json.dumps({'version': 1, 'projects': [entry]}) + ';')
    page = path.read_text().replace('window.fetch=async url=>{', setup + 'window.fetch=async url=>{')
    page = page.replace("const path=String(url).split('?')[0];", """const path=String(url).split('?')[0];
if(path==='projects.json')return collectionFailures-->0?{ok:false,status:503}:{ok:true,json:async()=>structuredClone(fixtureCatalog)};""")
    page = page.replace('<body>', '<body><script>location.hash="gallery-view";</script>')
    path.write_text(page)


@unittest.skipUnless(shutil.which('node'), 'Node executes the actual collection renderer')
class GalleryCatalogRecoveryTests(unittest.TestCase):
    def test_retry_failure_success_hidden_navigation_and_publication_race(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.listeners={};this.attrs={};this.textContent='';this.hidden=false;}
 appendChild(n){this.children.push(n);return n;} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=v;} removeAttribute(k){delete this.attrs[k];}
 addEventListener(k,fn){this.listeners[k]=fn;} focus(){document.activeElement=this;}
}
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
const nodes={},get=id=>nodes[id]??(nodes[id]=new Element('div'));
for(const id of ['house-view','gallery-view','creations','creations-card'])get(id).id=id;
let active='gallery-view';
const document={activeElement:null,createElement:t=>new Element(t),
 getElementById:id=>Object.values(nodes).flatMap(all).find(n=>n.id===id)||null,
 querySelector:s=>s==='.page-view:not([hidden])'?get(active):s==='#creations-card'?get('creations-card'):null};
const requests=[];
const ctx=vm.createContext({document,URL,AbortSignal,fetch:()=>new Promise(resolve=>requests.push(resolve))});
const source=fs.readFileSync(process.argv[1],'utf8'),end=source.lastIndexOf('\nrefresh();');
vm.runInContext(source.slice(0,end),ctx);const run=s=>vm.runInContext(s,ctx);
const entry={id:'garden',title:'Garden',summary:'Try the garden',category:'creation',action:'Play',href:'projects/garden/'};
const response=()=>({ok:true,json:async()=>({version:1,projects:[entry]})});
const fail=()=>({ok:false,status:503});
(async()=>{
 run(`data={source_head:'one'};frame={shelf:{projects:[{idea:'garden',status:'done'}]}};current=true;
 shelf=()=>{};reconcileCreationPicture=()=>{};`);
 let loading=ctx.loadCatalog('one');requests.shift()(fail());await loading;
 ctx.renderCollection();let retry=document.getElementById('gallery-catalog-retry');
 assert(retry,'Unavailable Gallery must offer recovery without a whole-page reload');
 document.activeElement=retry;let clicked=retry.listeners.click();
 assert(retry.disabled);assert.match(text(get('creations')),/Loading/);
 const duplicate=ctx.loadCatalog('one');assert.equal(requests.length,1,'Coalesce the same collection request');
 requests.shift()(fail());await Promise.all([clicked,duplicate]);
 assert.equal(retry.disabled,false);assert.match(text(get('creations')),/Try again/);
 clicked=retry.listeners.click();requests.shift()(response());await clicked;
 assert(all(get('creations')).some(n=>n.tagName==='A'&&n.href==='projects/garden/'));
 assert.equal(document.activeElement.id,'gallery-search','Move focus from the removed retry into the recovered Gallery');
 // A success after leaving the view must not reconstruct hidden collection rows or steal focus.
 run(`catalog=null;catalogSource=null;renderCollection();`);
 retry=document.getElementById('gallery-catalog-retry');document.activeElement=retry;
 clicked=retry.listeners.click();active='house-view';get('creations').replaceChildren();
 const elsewhere=new Element('button');document.activeElement=elsewhere;
 requests.shift()(response());await clicked;
 assert.equal(get('creations').children.length,0);assert.equal(document.activeElement,elsewhere);
 // A late failure/success for an older publication cannot replace a newer collection.
 run(`catalog=null;catalogSource=null;data.source_head='old';`);
 const old=ctx.loadCatalog('old');run(`data.source_head='new';`);
 const fresh=ctx.loadCatalog('new');const finishOld=requests.shift(),finishNew=requests.shift();
 finishNew(response());await fresh;finishOld(fail());await old;
 assert.equal(run('catalogSource'),'new');assert.equal(run('catalog.length'),1);
 run(`catalogSource=null;data.source_head='old2';`);
 const old2=ctx.loadCatalog('old2');run(`data.source_head='new2';`);
 const fresh2=ctx.loadCatalog('new2');const doneOld=requests.shift(),doneNew=requests.shift();
 doneNew(response());await fresh2;doneOld(response());await old2;
 assert.equal(run('catalogSource'),'new2');
 // The room offers the same recovery, using the real room cards after success.
 active='house-view';get('room-content').id='room-content';
 run(`catalog=null;catalogSource=null;selected='gallery';
 frame.rooms=[{id:'gallery',status:'open'}];
 roomPanel=()=>{const parent=document.getElementById('room-content');parent.replaceChildren();renderGalleryRoom(parent);};
 roomPanel();`);
 retry=document.getElementById('gallery-room-catalog-retry');assert(retry);
 document.activeElement=retry;clicked=retry.listeners.click();requests.shift()(response());await clicked;
 assert(all(get('room-content')).some(n=>n.tagName==='A'&&n.href==='projects/garden/'));
 assert.equal(document.activeElement.id,'gallery-room-display');
 console.log('failure, retry, coalescing, focus, hidden-view and publication-race controls pass');
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
        result = subprocess.run(['node', '-e', script, str(ROOT / 'site/house.js')],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
