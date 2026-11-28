"""Keep keyboard navigation continuous when recent-event cards are replaced."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('node'), 'Node executes the renderer')
class LatelyFocusTests(unittest.TestCase):
    def test_redraw_navigation_and_missing_events(self):
        script = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
class Element {
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.listeners={};this.id='';}
 appendChild(child){this.children.push(child);child.parentNode=this;return child;}
 contains(node){return node===this||this.children.some(child=>child.contains(node));}
 replaceChildren(){if(this.contains(document.activeElement))document.activeElement=document.body;this.children=[];}
 setAttribute(key,value){this[key]=String(value);}
 addEventListener(key,fn){this.listeners[key]=fn;}
 focus(options){document.activeElement=this;this.focusOptions=options;}
 querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
 querySelectorAll(selector){return this.children.flatMap(child=>[
 ...((selector==='button'&&child.tagName==='BUTTON')||(selector.startsWith('#')&&child.id===selector.slice(1))?[child]:[]),
 ...child.querySelectorAll(selector)]);}
}
const host=new Element('ol'),outside=new Element('input');host.id='lately';
const document={body:new Element('body'),activeElement:null,createElement:tag=>new Element(tag),
 getElementById:id=>id==='lately'?host:host.querySelector('#'+id),querySelector:()=>null};
document.activeElement=document.body;
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));
const ctx=vm.createContext({document,assert,host,outside});vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
let entries=[{seq:30,at:100},{seq:20,at:90},{seq:10,at:80}];
latelyEvents=()=>entries;latelySentence=item=>'Event '+item.seq;ago=()=>'';
data={frames:[{seq:10},{seq:20},{seq:30}]};index=2;current=true;
render=()=>renderLately();renderLately();
const buttons=()=>host.querySelectorAll('button');
buttons()[1].focus();buttons()[1].listeners.click();
assert.equal(index,1);assert.equal(document.activeElement,buttons()[1]);
assert.equal(document.activeElement.focusOptions.preventScroll,true);
// A new card changes position but must not change the selected event.
entries.unshift({seq:40,at:110});renderLately();
assert.equal(document.activeElement,buttons()[2]);
// An event absent from the new history leaves a visible fallback.
entries=entries.filter(item=>item.seq!==20);renderLately();
assert.equal(document.activeElement,buttons()[0]);
// A refresh cannot steal focus from an unrelated field.
outside.focus();renderLately();assert.equal(document.activeElement,outside);
buttons()[0].focus();entries=[];renderLately();
assert.equal(document.activeElement,host);assert.equal(String(host.tabindex??host.tabIndex),'-1');
`,ctx);
'''
        result = subprocess.run([shutil.which('node'), '-e', script, str(ROOT / 'site/house.js')],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
