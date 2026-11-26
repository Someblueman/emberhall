"""Exercise Gallery controls against the shipped renderer; browser checks are separate."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node executes the Gallery renderer")
class GallerySearchTests(unittest.TestCase):
    def run_js(self, checks):
        root = Path(__file__).parents[1]
        harness = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.attrs={};this.textContent='';}
 appendChild(n){this.children.push(n);return n;} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=v;} addEventListener(k,fn){this.listeners[k]=fn;}
 focus(){document.activeElement=this;}
 setSelectionRange(start,end,direction){Object.assign(this,{selectionStart:start,selectionEnd:end,selectionDirection:direction});}
}
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
const root=new Element('div'),document={activeElement:null,createElement:t=>new Element(t),
 getElementById:id=>id==='creations'?root:all(root).find(n=>n.id===id)||null};
const find=id=>document.getElementById(id),query=value=>{
 find('gallery-search').value=value;find('gallery-search').listeners.input();
},activity=value=>{find('gallery-activity').value=value;find('gallery-activity').listeners.change();};
const ctx=vm.createContext({assert,document,root,all,text,find,query,activity,URL,AbortSignal});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
catalog=[
 {id:'game',title:'Night Ferry',summary:'Solve a ferry mystery',category:'creation',action:'Play',href:'projects/night-ferry/'},
 {id:'studio',title:'Pattern Studio',summary:'Make geometric tiles',category:'creation',action:'Open',href:'projects/tessera-loom/'},
 {id:'lens',title:'Hearth Lens',summary:'Inspect the house record',category:'house-tool',action:'Read guide',href:'https://github.com/Someblueman/emberhall/blob/main/projects/hearth-lens/README.md'},
 {id:'chronicle',title:'Chronicle',summary:'Explore house history',category:'house-tool',action:'Open',href:'chronicle/index.html'}
];
frame={shelf:{projects:catalog.map(p=>({idea:p.id,status:'done'}))}};current=true;
const cards=()=>all(root).filter(n=>n.className==='creation-card');
renderCollection();
`,ctx);
vm.runInContext(process.argv[2],ctx);
'''
        result = subprocess.run(
            ["node", "-e", harness, str(root / "site/house.js"), checks],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_search_activity_reset_and_matching_house_tools(self):
        self.run_js(r'''
assert.equal(cards().length,4);assert.equal(all(root).find(n=>n.tag==='details').open,false);
const search=find('gallery-search');search.focus();query('  FERRY  ');
assert.equal(cards().length,1);assert.match(text(cards()[0]),/Night Ferry/);
assert.equal(document.activeElement,search);assert.match(find('gallery-status').textContent,/1 of 4/);
activity('Open');assert.equal(cards().length,0);assert.match(text(root),/Nothing matches/);
find('gallery-reset').listeners.click();assert.equal(cards().length,4);
assert.equal(document.activeElement,search);assert.equal(find('gallery-activity').value,'all');
activity('Read guide');assert.equal(cards().length,1);assert.match(text(cards()[0]),/Read guide Hearth Lens/);
assert.equal(all(root).find(n=>n.tag==='details').open,true);
activity('Open');assert.equal(cards().length,2);
assert.match(text(root),/Open Chronicle/);assert.doesNotMatch(text(root),/Read guide Chronicle/);
delete catalog[1].action;renderCollection();assert.equal(cards().length,2);
assert.match(text(root),/Open Pattern Studio/);
query('geometric');assert.equal(cards().length,1);assert.match(text(root),/Pattern Studio/);
assert.equal(find('gallery-search').attrs['aria-controls'],'gallery-results');
assert.equal(find('gallery-status').attrs.role,'status');
''')

    def test_historical_completion_catalog_changes_and_safe_text(self):
        self.run_js(r'''
const before=JSON.stringify(frame);query('history');assert.equal(cards().length,1);
assert.equal(JSON.stringify(frame),before);
current=false;frame.shelf.projects[3].status='active';renderCollection();
assert.equal(cards().length,0);assert.match(text(root),/current published versions/);
galleryState.query='';galleryState.activity='all';
catalog[0].title='<img src=x>';catalog[0].summary='<script>evil()</script>';
catalog[1].href='javascript:evil()';renderCollection();
assert.equal(cards().length,2);assert.match(text(root),/<img src=x>/);
assert.equal(all(root).filter(n=>n.tag==='img'||n.tag==='script').length,0);
catalog=null;renderCollection();assert.match(text(root),/Collection links are unavailable/);
catalog=[];renderCollection();assert.match(text(root),/No published creations/);
assert.equal(find('gallery-search'),null);
''')

    def test_refresh_preserves_query_filter_focus_and_selection(self):
        self.run_js(r'''
query('ferry');activity('Play');find('gallery-search').focus();
find('gallery-search').setSelectionRange(1,4,'backward');
lighting=accounts=roomPanel=drawHouse=renderViewContext=renderRecentGrowth=renderLately=()=>{};
refreshView();assert.equal(find('gallery-search').value,'ferry');
assert.equal(find('gallery-activity').value,'Play');assert.equal(cards().length,1);
assert.equal(document.activeElement,find('gallery-search'));
assert.equal(find('gallery-search').selectionStart,1);assert.equal(find('gallery-search').selectionEnd,4);
assert.equal(find('gallery-search').selectionDirection,'backward');
find('gallery-reset').listeners.click();
const details=all(root).find(n=>n.tag==='details');details.open=true;details.listeners.toggle();
find('gallery-tools').focus();refreshView();
assert.equal(all(root).find(n=>n.tag==='details').open,true);
assert.equal(document.activeElement,find('gallery-tools'));
''')

    def test_guide_only_creation_is_a_searchable_archive_link(self):
        self.run_js(r'''
const guide={id:'sow-ledger',title:'Sow Ledger',summary:'Earlier seed inventory experiment',
 category:'creation',action:'Read guide',href:'https://github.com/Someblueman/emberhall/blob/main/projects/sow-ledger/README.md'};
catalog.push(guide);frame.shelf.projects.push({idea:guide.id,status:'done'});renderCollection();
const archive=()=>all(root).find(n=>n.className==='gallery-archive');
assert.equal(cards().length,4,'Guide-only work leaves the featured cards');
assert.equal(all(archive()).filter(n=>n.tag==='li').length,1);
assert.match(text(archive()),/Archive.*do not open a working demonstration/);
assert.equal(find('gallery-archive-sow-ledger').href,guide.href);
assert.match(find('gallery-status').textContent,/5 of 5/);
query('SEED');assert.equal(cards().length,0);assert.match(text(archive()),/Sow Ledger/);
assert.match(find('gallery-status').textContent,/1 of 5/);
activity('Play');assert.equal(archive(),undefined);assert.match(text(root),/Nothing matches/);
find('gallery-reset').listeners.click();activity('Read guide');
assert.equal(cards().length,1,'The house guide remains in its own section');
assert.match(text(archive()),/Sow Ledger/);
find('gallery-archive-sow-ledger').focus();
lighting=accounts=roomPanel=drawHouse=renderViewContext=renderRecentGrowth=renderLately=()=>{};
refreshView();assert.equal(document.activeElement,find('gallery-archive-sow-ledger'));
current=false;frame.shelf.projects.find(p=>p.idea===guide.id).status='active';renderCollection();
assert.equal(archive(),undefined,'An unfinished historical project is never archived early');
frame.shelf.projects.find(p=>p.idea===guide.id).status='done';renderCollection();
assert.match(text(archive()),/Sow Ledger/);assert.match(text(root),/current published versions/);
guide.title='<script>ledger</script>';guide.summary='<img src=x>';renderCollection();
assert.match(text(archive()),/<script>ledger<\/script>/);
assert.equal(all(archive()).filter(n=>n.tag==='script'||n.tag==='img').length,0);
guide.href='javascript:evil()';renderCollection();assert.equal(archive(),undefined);
''')
