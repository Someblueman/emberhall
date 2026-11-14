"""Execute the actual shelf renderer against a minimal DOM; no visual claim."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which('node'), 'Node is needed for the actual renderer')
class ShelfUITests(unittest.TestCase):
    def test_real_states_safe_links_reasons_and_historical_reset(self):
        source = Path(__file__).parents[1] / 'site/house.js'
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';}
  appendChild(node){this.children.push(node);}
  replaceChildren(){this.children=[];}
}
const root=new Element('section'), document={getElementById:()=>root,createElement:tag=>new Element(tag)};
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const all=node=>[node,...node.children.flatMap(all)];
const context=vm.createContext({assert,document,URL,root,text,all});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(refresh,60000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'Europe/London'};frame={};shelf();
assert.match(text(root),/not activated/);
frame={residents:[{id:'resident-fixture',name:'Juniper'}],shelf:{enabled:true,policy:null,ideas:[],projects:[]}};shelf();
assert.match(text(root),/awaits ratification/);assert.match(text(root),/No ideas/);
frame.shelf.policy='work-selection';
frame.shelf.explorer={resident:'resident-fixture',agent:'opencode',until:100};
frame.shelf.ideas=[
 {id:'draft',title:'<img src=x onerror=alert(1)>',status:'shelved',sources:['https://example.org/', 'javascript:alert(1)', 'https://user:secret@example.org/']},
 {id:'winner',title:'Already selected',status:'project',sources:[]},
 {id:'lost',title:'Lost idea',status:'graveyard',losses:2,history:[{reasons:['Too large for the first milestone']}]}];
frame.shelf.projects=[{id:'done',title:'Completed map',status:'done',milestone:'Demo',deadline:100,extended:false}];
shelf();
assert.doesNotMatch(text(root),/Active projects/);assert.match(text(root),/Finished projects/);
assert.match(text(root),/Completed map/);assert.doesNotMatch(text(root),/Already selected/);
assert.match(text(root),/Too large for the first milestone/);
assert.match(text(root),/Explorer: Juniper · OpenCode/);assert.doesNotMatch(text(root),/resident-fixture/);
assert.equal(all(root).filter(n=>n.tag==='img').length,0);
const links=all(root).filter(n=>n.tag==='a');assert.equal(links.length,1);
assert.equal(links[0].href,'https://example.org/');assert.equal(links[0].rel,'noopener noreferrer');
frame.shelf.projects.push({id:'live',title:'Current build',status:'active',deadline:200});shelf();
assert.match(text(root),/Active projects/);assert.match(text(root),/Current build/);
frame={};shelf();assert.doesNotMatch(text(root),/Completed map|Current build|Lost idea/);
assert.match(text(root),/not activated/);
`,context);
'''
        result = subprocess.run([shutil.which('node'), '-e', script, str(source)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)
