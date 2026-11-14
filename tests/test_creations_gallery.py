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
 constructor(tag){this.tag=tag;this.children=[];this.textContent='';}
 appendChild(n){this.children.push(n);} replaceChildren(){this.children=[];}
}
const root=new Element('div'),document={getElementById:()=>root,querySelector:()=>root,createElement:t=>new Element(t)};
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
const ctx=vm.createContext({assert,document,URL,AbortSignal,root,all,text,fetch:async()=>({ok:false})});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(refresh,60000);\n';
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
assert.equal(all(root).find(n=>n.tag==='details').open,undefined);
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
})().catch(e=>{console.error(e);process.exitCode=1;});
'''
        source = Path(__file__).parents[1] / 'site/house.js'
        result = subprocess.run(['node', '-e', script, str(source)], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
