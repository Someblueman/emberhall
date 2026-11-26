"""Exercise the page's event form against the real history navigation."""
from pathlib import Path
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).parents[1]


@unittest.skipUnless(shutil.which("node"), "Node executes the page scripts")
class EventNavigationTests(unittest.TestCase):
    def run_js(self, checks):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const page=fs.readFileSync(process.argv[1]+'/site/index.html','utf8');
const inline=page.match(/<script id="event-navigation-script">([\s\S]*?)<\/script>/)[1];
class Element {
 constructor(id){this.id=id;this.value='';this.textContent='';this.attrs={};this.listeners={};}
 addEventListener(k,fn){this.listeners[k]=fn;} setAttribute(k,v){this.attrs[k]=v;}
 removeAttribute(k){delete this.attrs[k];} focus(){document.activeElement=this;}
}
const nodes={},get=id=>nodes[id]||(nodes[id]=new Element(id)),loaded=[];
const document={getElementById:get,activeElement:null,addEventListener:(k,fn)=>{
 assert.equal(k,'DOMContentLoaded');loaded.push(fn);
}};
const ctx=vm.createContext({assert,document,get,nodes});
const source=fs.readFileSync(process.argv[1]+'/site/house.js','utf8');
const tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(inline,ctx);assert.equal(loaded.length,1);loaded[0]();
vm.runInContext(`
let renders=0;
render=()=>{renders++;frame=data.frames[index];};
lighting=accounts=roomPanel=drawHouse=renderViewContext=renderCollection=renderRecentGrowth=renderLately=()=>{};
const input=get('event-number'),result=get('event-number-result');
const submit=value=>{
 input.value=value;let prevented=false;
 get('event-navigation').listeners.submit({preventDefault(){prevented=true;}});
 assert(prevented);
};
const seed=()=>{data={frames:[{seq:10},{seq:20},{seq:50}]};index=2;current=true;
 frame=data.frames[index];selected='hearth';};
`,ctx);
vm.runInContext(process.argv[2],ctx);
'''
        result = subprocess.run(
            [shutil.which("node"), "-e", script, str(ROOT), checks],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exact_visits_latest_and_selected_room(self):
        self.run_js(r'''
seed();input.focus();submit(' 020 ');
assert.equal(frame.seq,20);assert.equal(index,1);assert.equal(current,false);
assert.equal(selected,'hearth');assert.equal(renders,1);assert.equal(document.activeElement,input);
assert.match(result.textContent,/Opened event 20/);assert(!input.attrs['aria-invalid']);
submit('50');assert.equal(frame.seq,50);assert.equal(current,true);
assert.match(result.textContent,/latest published moment/);
// A subsequent publication must be read at submission, never cached at binding.
data.frames.push({seq:80});submit('80');assert.equal(frame.seq,80);assert.equal(current,true);
''')

    def test_rejects_invalid_and_missing_without_moving(self):
        self.run_js(r'''
seed();
for(const value of ['', ' ', '0', '-1', '1.5', '2e1', '+20', 'Infinity', 'NaN',
 '9007199254740993', '２０', '<script>alert(1)</script>']) {
 submit(value);assert.match(result.textContent,/whole event number/);
 assert.equal(input.attrs['aria-invalid'],'true');assert.equal(document.activeElement,input);
 assert.equal(frame.seq,50);assert.equal(renders,0);assert.equal(current,true);
}
for(const value of ['1','15','51']) {
 submit(value);assert.match(result.textContent,/not in this published snapshot \(events 10–50\)/);
 assert.equal(frame.seq,50);assert.equal(renders,0);assert.equal(selected,'hearth');
}
submit('20');assert(!input.attrs['aria-invalid']);assert.equal(frame.seq,20);
''')

    def test_unloaded_history_and_draft_survives_redraw(self):
        self.run_js(r'''
for(const unavailable of [undefined, null, {}, {frames:[]}]) {
 data=unavailable;submit('20');assert.match(result.textContent,/has not loaded yet/);
 assert(!input.attrs['aria-invalid']);assert.equal(renders,0);
}
seed();submit('15');input.value='2';input.listeners.input();
assert.equal(result.textContent,'');assert(!input.attrs['aria-invalid']);input.focus();
refreshView(true);refreshView(false);
assert.equal(input.value,'2');assert.equal(document.activeElement,input);
submit('20');assert.equal(frame.seq,20);
''')

    def test_static_page_labels_and_publisher_delivery(self):
        page = (ROOT / "site/index.html").read_text()
        self.assertIn('for="event-number"', page)
        self.assertIn('id="event-open" class="quiet-button" type="submit" disabled', page)
        self.assertIn('aria-describedby="event-number-hint event-number-result"', page)
        self.assertIn('id="event-number-result" role="status"', page)
        self.assertIn('inputmode="numeric"', page)
        # All new assets travel in the already-published page, with no runtime change.
        self.assertEqual(len(re.findall('id="event-navigation-script"', page)), 1)
        self.assertNotIn('src="event-navigation', page)
        self.assertIn('.event-navigation :focus-visible', page)


if __name__ == "__main__":
    unittest.main()
