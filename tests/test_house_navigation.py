"""Check named house views and readable record labels in the live renderer."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Views(HTMLParser):
    def __init__(self):
        super().__init__()
        self.views = {}
        self.details = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section" and attrs.get("id", "").endswith("-view"):
            self.views[attrs["id"]] = "hidden" not in attrs
        if tag == "details":
            self.details.append("open" in attrs)
        if tag == "a" and attrs.get("href", "").startswith("#"):
            self.links.append((attrs.get("href"), attrs.get("aria-current")))


class HouseNavigationTests(unittest.TestCase):
    def test_short_default_and_named_collapsed_views(self):
        parser = Views()
        parser.feed((ROOT / "site/index.html").read_text())
        self.assertEqual(parser.views, {
            "house-view": True, "projects-view": False,
            "council-view": False, "accounts-view": False,
        })
        labels = [href for href, _ in parser.links]
        self.assertTrue(all(f"#{view}" in labels for view in parser.views))
        source = (ROOT / "site/index.html").read_text()
        for required in ("Who is home", 'id="room-nav"', 'id="house"',
                         'id="shelf-card"', 'id="voting-card"', 'id="view-context"'):
            self.assertIn(required, source)
        self.assertEqual((ROOT / "site/index.html").read_text().count("?v=growth-1"), 2)
        self.assertTrue(parser.details)
        self.assertFalse(any(parser.details))

    @unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
    def test_navigation_keyboard_targets_and_record_labels(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag,id=''){this.tag=tag;this.id=id;this.children=[];this.attrs={};this.hidden=false;this.calls=[];this.listeners={};}
 appendChild(n){this.children.push(n);} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=String(v);} removeAttribute(k){delete this.attrs[k];}
 addEventListener(k,fn){this.listeners[k]=fn;} focus(){this.calls.push('focus');} scrollIntoView(){this.calls.push('scroll');}
 querySelectorAll(selector){return selector==='details[open]'?[]:[];}
}
const ids=['house-view','projects-view','council-view','accounts-view','shelf-card','voting-card',
 'floor-picker','history','present','previous','next','overview'];
const nodes=Object.fromEntries(ids.map(id=>[id,new Element('section',id)]));
const links=['house-view','projects-view','council-view','accounts-view'].map(id=>{const a=new Element('a');a.hash='#'+id;return a;});
const views=ids.slice(0,4).map(id=>nodes[id]);
const document={getElementById:id=>nodes[id]||null,querySelectorAll:s=>s==='.page-view'?views:s==='.view-nav a'?links:[]};
const listeners={};const window={location:{hash:'#shelf-card'},addEventListener:(k,fn)=>listeners[k]=fn};
const context=vm.createContext({assert,document,window,links,listeners});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(refresh,60000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
bindControls();
assert.equal($('projects-view').hidden,false);assert.equal($('house-view').hidden,true);
assert.equal(links[1].attrs['aria-current'],'page');
window.location.hash='#voting-card';listeners.hashchange();
assert.equal($('council-view').hidden,false);assert.equal($('projects-view').hidden,true);
assert.equal($('voting-card').calls.join(','),'focus,scroll');
assert.equal(links[2].attrs['aria-current'],'page');
showViewForHash('#accounts-view');assert.equal($('accounts-view').hidden,false);
`,context);
'''
        result = subprocess.run([shutil.which("node"), "-e", script, str(ROOT / "site/house.js")],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
    def test_shelf_votes_presence_use_titles_and_exact_models(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.attrs={};this.style={};}
 appendChild(n){this.children.push(n);} replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attrs[k]=String(v);} querySelectorAll(s){return all(this).filter(n=>n.tag==='details'&&(s!=='details[open]'||n.open));}
}
const nodes={},get=id=>(nodes[id]||(nodes[id]=new Element('div')));
const document={getElementById:get,createElement:t=>new Element(t)};
const all=n=>[n,...n.children.flatMap(all)];
const visible=n=>n.tag==='details'&&!n.open?[n.textContent,...(n.children[0]?[visible(n.children[0])]:[])].join(' '):[n.textContent,...n.children.map(visible)].join(' ');
const context=vm.createContext({assert,document,URL,nodes,all,visible});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(refresh,60000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'UTC'};const person={name:'Fern',agent:'codex',id:'resident-x'};
frame={residents:[person],shelf:{enabled:true,policy:'work-selection',ideas:[
 {id:'idea-private-1',title:'A useful garden',status:'shelved',what:'Long explanation'},
 {id:'idea-private-2',status:'shelved'}],projects:[
 {id:'project-private-1',title:'Active project',status:'active',owner:person.id,milestone:'First step'},
 {id:'project-private-2',status:'done',milestone:'Finished step'}]},
 voting:{inbox_checked_at:100,choices:[{id:'house-growth-choice-006',status:'closed',winner:'candidate-x',owner:person,
 opened_sequence:1,selection_version:2,candidates:[{id:'candidate-x',title:'Human choice title',author:person,milestone:'Try it',seconds:86400}],
 votes:[{resident:person,idea:'candidate-x',counted:true,reason:'Clear reason',sequence:2,at:100}]}],
 proposals:[{id:'proposal-private-3',title:'Readable proposal',mode:'wake-prompt',author:person,status:'pending',stale:false,
 reason:'A reason',text:'Exact proposed wording',trial:null,endorsements:[],notice:null}]},
 runs:[{id:'run-luna',resident:person.id,agent:'codex',model:'gpt-6-luna',start:100,sequence:1,status:'started'},
 {id:'run-missing',resident:person.id,agent:'codex',start:100,sequence:2,status:'started'}],tasks:[],scars:[],at:100,seq:2};current=true;
shelf();voting();data.frames=[frame];data.observed_at=100;renderResidentPulse();
const shelfText=visible($('shelf')),voteText=visible($('voting'));
assert.match(shelfText,/Active project/);assert.doesNotMatch(shelfText,/Finished step|Long explanation|idea-private|project-private/);
assert.match(voteText,/Human choice title/);assert.match(voteText,/Readable proposal/);
assert.doesNotMatch(voteText,/house-growth-choice-006|candidate-x|proposal-private-3/);
assert.match(text($('shelf')),/Finished step/);assert.match(text($('shelf')),/Long explanation/);
assert(all($('shelf')).some(n=>n.tag==='details'&&n.className==='shelf-completed'&&!n.open));
assert.match(text($('voting')),/house-growth-choice-006/);assert.match(text($('voting')),/candidate-x/);
assert.match(text($('voting')),/proposal-private-3/);
assert.match(text($('resident-pulse')),/Codex · gpt-6-luna/);assert.match(text($('resident-pulse')),/Codex · Model unrecorded/);
function text(n){return [n.textContent,...n.children.map(text)].join(' ');}
`,context);
'''
        result = subprocess.run([shutil.which("node"), "-e", script, str(ROOT / "site/house.js")],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
