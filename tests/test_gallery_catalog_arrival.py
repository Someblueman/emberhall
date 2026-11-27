"""Direct Gallery arrival and a shared retry must produce live cards and focus."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

def write_fixture(destination, failures=0, shared_retry=False, source_script="../site/house.js"):
    """Native page with one completed creation and a delayed collection reply."""
    import json
    from tests.test_site_refresh_scheduling import write_missing_snapshot_fixture
    write_missing_snapshot_fixture(destination, failures=0, source_script=source_script)
    path = Path(destination)
    entry = json.loads((ROOT / 'site/projects.json').read_text())['projects'][0]
    setup = ('fixtureSnapshot.frames[0].rooms.push({id:"gallery",name:"The Gallery",status:"open"});'
             'fixtureSnapshot.frames[0].shelf={ideas:[],choices:[],needs:[],projects:'
             '[{id:"fixture-tessera",idea:"tessera-loom",title:"Tessera Loom",status:"done",milestones:[],completed:0}]};'
             f'let collectionFailures={int(failures)};const fixtureCatalog='
             + json.dumps({'version': 1, 'projects': [entry]}) + ';')
    page = path.read_text().replace('window.fetch=async url=>{', setup + 'window.fetch=async url=>{')
    page = page.replace("const path=String(url).split('?')[0];", """
const path=String(url).split('?')[0];
if(path==='projects.json'){
 await new Promise(resolve=>setTimeout(resolve,500));
 return collectionFailures-->0?{ok:false,status:503}:{ok:true,json:async()=>structuredClone(fixtureCatalog)};
}
""")
    startup = '<script>location.hash="room/gallery";'
    if shared_retry:
        startup += 'document.addEventListener("click",e=>{if(e.target.id==="gallery-room-catalog-retry")refresh();},true);'
    page = page.replace('<body>', '<body>' + startup + '</script>')
    path.write_text(page)
    preview = Path('projects/tessera-loom/gallery-preview.svg')
    target = path.parent / preview
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / preview, target)


@unittest.skipUnless(shutil.which('node'), 'Node executes the actual renderer')
class GalleryCatalogArrivalTests(unittest.TestCase):
    def test_direct_arrival_and_shared_retry_focus(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.listeners={};this.attrs={};this.textContent='';this.hidden=false;}
 appendChild(n){this.children.push(n);return n;} replaceChildren(){if(this.children.some(n=>all(n).includes(document.activeElement)))document.activeElement=document.body;this.children=[];}
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
 active='house-view';get('room-content').id='room-content';
 document.body=new Element('body');
 run(`data={source_head:'one'};frame={shelf:{projects:[{idea:'garden',status:'done'}]},rooms:[{id:'gallery',status:'open'}]};current=true;selected='gallery';
 reconcileCreationPicture=()=>{};
 roomPanel=()=>{const parent=document.getElementById('room-content');parent.replaceChildren();renderGalleryRoom(parent);};
 renderAuxiliaryViews=()=>{};roomPanel();`);
 const start=source.indexOf('    if(catalogSource!==data.source_head) {');
 const end=source.indexOf('    const recovered=',start);
 assert(start>=0&&end>start);
 const arrival=()=>run('(async()=>{'+source.slice(start,end)+'})()');
 let loading=arrival();requests.shift()(response());await loading;
 assert(document.getElementById('gallery-room-display'),'Direct Gallery room must show cards when its catalog arrives');
 // A retry shares the initial refresh request. Disabling it moves native focus to body.
 run(`catalog=null;catalogSource=null;roomPanel();`);
 let retry=document.getElementById('gallery-room-catalog-retry');
 Object.defineProperty(retry,'disabled',{get(){return this._disabled},set(value){this._disabled=value;if(value&&document.activeElement===this)document.activeElement=document.body;}});
 loading=arrival();document.activeElement=retry;
 let clicked=retry.listeners.click();assert.equal(requests.length,1);
 // refreshView preserves focus by moving it onto a replacement retry with the same id.
 run(`roomPanel();`);document.activeElement=document.getElementById('gallery-room-catalog-retry');
 requests.shift()(response());await Promise.all([loading,clicked]);
 assert.equal(document.activeElement,document.getElementById('gallery-room-display'),'Shared arrival must leave focus on the live recovered display');
 // The retry can also become the first waiter before refresh joins it.
 run(`catalog=null;catalogSource=null;roomPanel();`);
 retry=document.getElementById('gallery-room-catalog-retry');document.activeElement=retry;
 run(`roomPanel();`);document.activeElement=document.getElementById('gallery-room-catalog-retry');
 clicked=retry.listeners.click();loading=arrival();
 run(`roomPanel();`);document.activeElement=document.getElementById('gallery-room-catalog-retry');
 requests.shift()(response());await Promise.all([clicked,loading]);
 assert.equal(document.activeElement,document.getElementById('gallery-room-display'),'Refresh joining retry must not detach its recovered focus');
 // Leaving the room while a reply is pending must not redraw it or steal focus.
 run(`catalog=null;catalogSource=null;roomPanel();`);
 retry=document.getElementById('gallery-room-catalog-retry');document.activeElement=retry;
 loading=arrival();clicked=retry.listeners.click();
 run(`selected='workshop';`);get('room-content').replaceChildren();
 const elsewhere=new Element('button');document.activeElement=elsewhere;
 requests.shift()(response());await Promise.all([loading,clicked]);
 assert.equal(get('room-content').children.length,0);assert.equal(document.activeElement,elsewhere);
 // An obsolete retry must not redraw a replacement snapshot, even for the same source.
 run(`catalog=null;catalogSource=null;selected='gallery';roomPanel();`);
 retry=document.getElementById('gallery-room-catalog-retry');document.activeElement=retry;
 clicked=retry.listeners.click();run(`data={source_head:'one'};`);
 requests.shift()(response());await clicked;
 assert.equal(document.getElementById('gallery-room-catalog-retry'),retry);
 assert.equal(document.activeElement,retry);
 console.log('automatic arrival, shared request/native blur, live focus and navigation-away pass');
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
        result = subprocess.run(['node', '-e', script, str(ROOT / 'site/house.js')], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
