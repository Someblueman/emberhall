"""Keep the keyboard shortcut on the visitor's current page and moment."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in ("a", "button", "input", "select"):
            self.links.append((tag, dict(attrs)))


class SkipNavigationTests(unittest.TestCase):
    def test_first_control_has_a_native_focusable_destination(self):
        parser = Links()
        page = (ROOT / "site/index.html").read_text()
        parser.feed(page)
        tag, attrs = parser.links[0]
        self.assertEqual(tag, "a")
        self.assertEqual(attrs["id"], "skip-content")
        self.assertEqual(attrs["href"], "#house-view")
        self.assertRegex(page, r'id="house-view"[^>]*tabindex="-1"')

    @unittest.skipUnless(shutil.which("node"), "Node executes the real navigation")
    def test_shortcut_preserves_routes_and_historical_state(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes={};
function node(id) {
 return nodes[id] ||= {id, listeners:{}, hidden:false,
  addEventListener(k,fn){this.listeners[k]=fn;},
  focus(){document.activeElement=this;},
  scrollIntoView(){this.scrolled=true;}};
}
const views=['house-view','projects-view','gallery-view','council-view','accounts-view'].map(node);
const card=node('room-card');
const document={activeElement:null,getElementById:node,
 querySelector:s=>s==='.room-card'?card:views.find(v=>!v.hidden),
 querySelectorAll:s=>s==='.page-view'?views:[]};
const window={location:{hash:''},addEventListener(){}};
const ctx=vm.createContext({assert,document,window,views,card});
const source=fs.readFileSync(process.argv[1],'utf8');
const tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
bindControls();
assert.equal($('skip-content').listeners.click,skipToContent);
const original={seq:17};frame=original;index=16;current=false;selected='hearth';
let prevented=0;
for(const hash of ['', '#house-view', '#projects-view', '#gallery-view',
 '#creations-card', '#finished-card', '#shelf-card', '#council-view', '#voting-card',
 '#accounts-view', '#room/hearth', '#room/future', '#room/%E0%A4%A']) {
 window.location.hash=hash;
 // Route switching is exercised without redrawing the house in this focused DOM.
 const saved=frame;frame=null;showViewForHash(hash);frame=saved;
 const view=views.find(v=>!v.hidden);
 const expected=hash.startsWith('#room/')?card:view;
 $('skip-content').listeners.click({preventDefault(){prevented++;}});
 assert.equal(document.activeElement,expected,hash);
 assert.equal(expected.scrolled,true);
 assert.equal(window.location.hash,hash,'No bookmark or history mutation');
 assert.equal(frame,original);assert.equal(index,16);assert.equal(current,false);
 assert.equal(selected,'hearth','Skipping does not select or clear a room');
}
assert.equal(prevented,13);
views.forEach(v=>v.hidden=true);
skipToContent({preventDefault(){assert.fail('Keep native fallback without a view');}});
`,ctx);
'''
        result = subprocess.run(
            ["node", "-e", script, str(ROOT / "site/house.js")],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
