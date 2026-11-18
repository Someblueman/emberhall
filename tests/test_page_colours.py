"""The page colour preference works independently of the house record and storage."""
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).parents[1]


@unittest.skipUnless(shutil.which("node"), "Node executes the shipped page script")
class PageColourTests(unittest.TestCase):
    def test_saved_choices_changes_and_unavailable_storage(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const page=fs.readFileSync(process.argv[1]+'/site/index.html','utf8');
const source=page.match(/<script id="page-colours-script">([\s\S]*?)<\/script>/)[1];
assert.match(page,/<label for="page-colours">Page colours<\/label>/);
assert.match(page,/<div class="page-colours" id="page-colours-control" hidden>/);
const options=[...page.match(/<select id="page-colours">([\s\S]*?)<\/select>/)[1]
 .matchAll(/<option value="([^"]+)">([^<]+)<\/option>/g)].map(m=>[m[1],m[2]]);
assert.deepEqual(options,[['auto','Follow the house'],['light','Light'],['dark','Dark']]);
function boot(saved,blocked=false){
 const picker={value:'auto',addEventListener(k,fn){assert.equal(k,'change');this.change=fn;}};
 const control={hidden:true},body={dataset:{},className:'day'},store=new Map();
 if(saved!==null)store.set('emberhall-page-colours',saved);
 const document={body,getElementById:id=>id==='page-colours'?picker:control};
 const localStorage={
  getItem(k){if(blocked)throw Error('unavailable');return store.get(k)??null;},
  setItem(k,v){if(blocked)throw Error('unavailable');store.set(k,v);},
  removeItem(k){if(blocked)throw Error('unavailable');store.delete(k);}
 };
 vm.runInNewContext(source,{document,localStorage});
 return {picker,control,body,store};
}
for(const saved of [null,'light','dark','auto','invalid','<img src=x>']){
 const {picker,control,body,store}=boot(saved);
 const expected=saved==='light'||saved==='dark'?saved:'auto';
 assert.equal(picker.value,expected);assert.equal(body.dataset.pageColours,expected);
 assert.equal(control.hidden,false);assert.equal(body.className,'day');
 for(const choice of ['dark','light','auto']){
  picker.value=choice;picker.change();
  assert.equal(body.dataset.pageColours,choice);
  assert.equal(store.get('emberhall-page-colours'),choice==='auto'?undefined:choice);
  // The renderer can still update its day class without changing the preference.
  body.className=body.className?'':'day';
  assert.equal(body.dataset.pageColours,choice);
 }
 assert.equal(boot(store.get('emberhall-page-colours')??null).picker.value,'auto');
}
const denied=boot('dark',true);
assert.equal(denied.picker.value,'auto');assert.equal(denied.control.hidden,false);
for(const choice of ['light','dark','auto']){
 denied.picker.value=choice;denied.picker.change();
 assert.equal(denied.body.dataset.pageColours,choice);
}
// Browsers can deny access to the storage property itself, before getItem runs.
const doc={body:{dataset:{}},getElementById:id=>id==='page-colours'?
 {addEventListener(){},value:'auto'}:{hidden:true}};
const ctx={document:doc};Object.defineProperty(ctx,'localStorage',{get(){throw Error('denied');}});
vm.runInNewContext(source,ctx);assert.equal(doc.body.dataset.pageColours,'auto');
'''
        result = subprocess.run(
            [shutil.which("node"), "-e", script, str(ROOT)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
