"""Exercise the Projects find box against the shipped renderer; browser checks are separate."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node executes the Projects renderer")
class ProjectsFindTests(unittest.TestCase):
    def run_js(self, checks):
        root = Path(__file__).parents[1]
        harness = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){
  this.tag=tag;this.children=[];this.parent=null;this.listeners={};this.attrs={};
  this.textContent='';this.id='';this.className='';this.value='';this.hidden=false;this.open=false;
  const self=this;
  this.classList={
   add:(c)=>{const p=self.className?self.className.split(' '):[];if(!p.includes(c))p.push(c);self.className=p.join(' ');},
   remove:(c)=>{self.className=self.className?self.className.split(' ').filter(x=>x&&x!==c).join(' '):'';},
   contains:(c)=>self.className?self.className.split(' ').includes(c):false,
   toggle:(c,force)=>{
    const on=force===undefined?!self.classList.contains(c):Boolean(force);
    if(on)self.classList.add(c);else self.classList.remove(c);return on;
   }};
 }
 appendChild(n){n.parent=this;this.children.push(n);return n;}
 replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=String(v);if(k==='id')this.id=String(v);}
 getAttribute(k){return k in this.attrs?this.attrs[k]:null;}
 addEventListener(k,fn){this.listeners[k]=fn;}
 focus(){document.activeElement=this;}
 setSelectionRange(start,end,direction){Object.assign(this,{selectionStart:start,selectionEnd:end,selectionDirection:direction});}
 querySelectorAll(selector){
  const matchSimple=(node,simple)=>{
   const parts=simple.split('.'),tag=parts[0];
   if(tag&&node.tag!==tag)return false;
   const wanted=parts.slice(1).filter(Boolean);
   return wanted.every(c=>(node.className||'').split(' ').includes(c));
  };
  const matches=(node,parts,ancestors)=>{
   if(!matchSimple(node,parts[parts.length-1]))return false;
   let chain=ancestors;
   for(let i=parts.length-2;i>=0;i--){
    const at=chain.findIndex(n=>matchSimple(n,parts[i]));
    if(at<0)return false;chain=chain.slice(at+1);
   }
   return true;
  };
  const out=[],walk=(node,ancestors)=>{
   for(const part of selector.split(',').map(s=>s.trim().split(/\s+/))){
    if(matches(node,part,ancestors)&&!out.includes(node))out.push(node);
   }
   for(const child of node.children)walk(child,[...ancestors,node]);
  };
  walk(this,[]);
  // Restore document order across comma parts.
  const order=[],collect=(node)=>{order.push(node);for(const child of node.children)collect(child);};
  collect(this);
  return out.sort((a,b)=>order.indexOf(a)-order.indexOf(b));
 }
}
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
const root=new Element('div');
const document={activeElement:null,createElement:t=>new Element(t),
 getElementById:id=>id==='shelf'?root:(all(root).find(n=>n.id===id)||null)};
const find=id=>document.getElementById(id),query=value=>{
 find('projects-find-search').value=value;find('projects-find-search').listeners.input();
};
const visibleItems=()=>all(root).filter(
 n=>typeof n.getAttribute('data-find')==='string'&&!n.classList.contains('projects-find-hidden'));
const ctx=vm.createContext({assert,document,root,all,text,find,query,visibleItems,URL,AbortSignal});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
data={timezone:'Europe/London',observed_at:1800000000,frames:[],journal_head:'head',source_head:'src'};
const resident={id:'r1',name:'Ember'};
frame={at:1800000000,seq:1,residents:[resident],work:[],shelf:{enabled:true,policy:null,ideas:[],projects:[]}};
projectsFindState.query='';
shelf();
`,ctx);
vm.runInContext(process.argv[2],ctx);
'''
        result = subprocess.run(
            ["node", "-e", harness, str(root / "site/house.js"), checks],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_find_filters_projects_and_ideas_by_title_and_plain(self):
        self.run_js(r'''
frame.shelf.projects=[
 {id:'p1',title:'Night Lantern',plain:'a lamp that only lights after dark',status:'active',owner:'r1'},
 {id:'p2',title:'Seed Ledger',plain:'plain text germination records',status:'active',owner:'r1'}
];
frame.shelf.ideas=[
 {id:'i1',title:'Glass Orchestra',plain:'music the hands can almost hear',what:'a song for quiet rooms',status:'shelved'},
 {id:'i2',title:'Paper Harbor',plain:'origami boats on a river',what:'folding study',status:'shelved'}
];
shelf();
assert.equal(visibleItems().length,4);
assert.equal(find('projects-find-search').value,'');
assert.match(find('projects-find-status').textContent,/Showing all 4/);
assert.equal(find('projects-find-status').attrs.role,'status');
assert.equal(find('projects-find-search').attrs['aria-describedby'],'projects-find-status');
query('  NIGHT  ');
assert.equal(visibleItems().length,1);
assert.match(text(visibleItems()[0]),/Night Lantern/);
assert.match(find('projects-find-status').textContent,/1 of 4/);
assert.equal(document.activeElement,null);
find('projects-find-search').focus();
assert.equal(document.activeElement,find('projects-find-search'));
query('origami boats');
assert.equal(visibleItems().length,1);
assert.match(text(visibleItems()[0]),/Paper Harbor/);
query('quiet rooms');
assert.equal(visibleItems().length,1);
assert.match(text(visibleItems()[0]),/Glass Orchestra/);
''')

    def test_find_empty_state_and_show_everything(self):
        self.run_js(r'''
frame.shelf.projects=[{id:'p1',title:'Night Lantern',plain:'a lamp',status:'active',owner:'r1'}];
frame.shelf.ideas=[{id:'i1',title:'Glass Orchestra',plain:'music',status:'shelved'}];
shelf();
const empty=all(root).find(n=>(n.className||'').split(' ').includes('empty-note'));
assert(empty);
assert(empty.classList.contains('projects-find-hidden'));
query('zzz-no-such-word');
assert.equal(visibleItems().length,0);
assert.match(find('projects-find-status').textContent,/0 of 2/);
assert(!empty.classList.contains('projects-find-hidden'));
assert.match(text(empty),/Nothing matches/);
find('projects-find-search').focus();
find('projects-find-reset').listeners.click();
assert.equal(find('projects-find-search').value,'');
assert.equal(visibleItems().length,2);
assert.match(find('projects-find-status').textContent,/Showing all 2/);
assert(empty.classList.contains('projects-find-hidden'));
assert.equal(document.activeElement,find('projects-find-search'));
''')

    def test_find_preserves_links_and_includes_a_retired_only_shelf(self):
        self.run_js(r'''
frame.shelf.projects=[{id:'p1',title:'Night Lantern',plain:'a lamp',status:'active',owner:'r1'}];
frame.shelf.ideas=[{id:'i1',title:'Glass Orchestra',plain:'music',status:'shelved',
 sources:['https://example.org/poem']}];
shelf();
query('lantern');
assert.equal(visibleItems().length,1);
const links=all(root).filter(n=>n.tag==='a'&&n.href);
assert(links.length>=1);
assert.equal(links[0].href,'https://example.org/poem');
assert.equal(links[0].rel,'noopener noreferrer');
projectsFindState.query='';
frame={at:1800000000,seq:1,residents:[{id:'r1',name:'Ember'}],work:[],
 shelf:{enabled:true,policy:null,ideas:[{id:'lost',title:'Lost idea',status:'graveyard',losses:1}],projects:[]}};
shelf();
assert.equal(visibleItems().length,1);
assert(!all(root).find(n=>(n.className||'').split(' ').includes('projects-find-controls')).classList.contains('projects-find-hidden'));
query('Lost idea');
assert(find('projects-retired').open);
assert.match(text(visibleItems()[0]),/Lost idea/);
frame.shelf.ideas=[];shelf();
assert(!all(root).some(n=>(n.className||'').split(' ').includes('projects-find-controls')));
''')

    def test_find_opens_stopped_records_by_reason_and_respects_viewed_history(self):
        self.run_js(r'''
frame.shelf.projects=[
 {id:'p1',title:'Lethe',plain:'a language experiment',status:'dropped',lesson:'No extra advantage under the same assumptions.'},
 {id:'p2',title:'Still building',status:'active',owner:'r1'}
];
frame.shelf.ideas=[{id:'retired',title:'<img src=x> Earlier idea',what:'a finite folding puzzle',status:'graveyard',
 history:[{lesson:'The complete counterexample ended the search.'}]}];
const before=JSON.stringify(frame);shelf();
assert.equal(visibleItems().length,3);assert(!find('projects-retired').open);
query('same assumptions');
assert.equal(visibleItems().length,1);assert.match(text(visibleItems()[0]),/Lethe/);
assert(find('projects-retired').open);
query('folding puzzle');
assert.equal(visibleItems().length,1);assert.match(text(visibleItems()[0]),/<img src=x> Earlier idea/);
assert(!all(root).some(n=>n.tag==='img'));
query('counterexample');assert.equal(visibleItems().length,1);
query('Still building');
assert.equal(visibleItems().length,1);assert(find('projects-retired').classList.contains('projects-find-hidden'));
find('projects-find-reset').listeners.click();
assert.equal(visibleItems().length,3);assert(!find('projects-retired').classList.contains('projects-find-hidden'));
assert.equal(document.activeElement,find('projects-find-search'));
assert.equal(JSON.stringify(frame),before);
// A prior publication's shelf cannot borrow stopped work from today's frame.
data.frames=[frame];frame={...frame,seq:0,shelf:{enabled:true,ideas:[],projects:[]}};
projectsFindState.query='Lethe';shelf();
assert(!text(root).includes('Lethe'));assert.equal(visibleItems().length,0);
''')

    def test_refresh_preserves_query_focus_and_selection(self):
        self.run_js(r'''
frame.shelf.projects=[{id:'p1',title:'Night Lantern',plain:'a lamp',status:'active',owner:'r1'}];
frame.shelf.ideas=[{id:'i1',title:'Glass Orchestra',plain:'music',status:'shelved'}];
shelf();
query('lantern');
find('projects-find-search').focus();
find('projects-find-search').setSelectionRange(1,4,'backward');
lighting=accounts=roomPanel=drawHouse=renderViewContext=renderRecentGrowth=renderLately=()=>{};
refreshView();
assert.equal(document.activeElement,find('projects-find-search'));
assert.equal(find('projects-find-search').selectionStart,1);
assert.equal(find('projects-find-search').selectionEnd,4);
assert.equal(find('projects-find-search').selectionDirection,'backward');
shelf();
assert.equal(find('projects-find-search').value,'lantern');
assert.equal(visibleItems().length,1);
assert.match(text(visibleItems()[0]),/Night Lantern/);
assert.match(find('projects-find-status').textContent,/1 of 2/);
''')


if __name__ == '__main__':
    unittest.main()
