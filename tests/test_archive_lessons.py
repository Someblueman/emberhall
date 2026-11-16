"""Exercise the Archive's real renderer and handlers with a small DOM boundary."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.attrs={};this.textContent='';}
  appendChild(node){this.children.push(node);return node;}
  replaceChildren(...nodes){this.children=[...nodes];}
  setAttribute(k,v){this.attrs[k]=v;}
  addEventListener(k,fn){this.listeners[k]=fn;}
  focus(){document.activeElement=this;}
  setSelectionRange(start,end,direction){Object.assign(this,{selectionStart:start,selectionEnd:end,selectionDirection:direction});}
  scrollIntoView(){this.scrolled=true;}
}
const all=n=>[n,...n.children.flatMap(all)];
const text=n=>[n.textContent,...n.children.map(text)].filter(Boolean).join(' ');
const root=new Element('div');
const document={activeElement:null,createElement:tag=>new Element(tag),
  getElementById:id=>all(root).find(n=>n.id===id)||null};
const ctx=vm.createContext({assert,document,console,Intl,Date,Math,root,all,text});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(refresh,60000);setInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
const get=id=>document.getElementById(id);
const articles=()=>all(root).filter(n=>n.tag==='article');
const show=()=>{root.replaceChildren();renderLessons(root);};
const search=value=>{get('archive-search').value=value;get('archive-search').listeners.input();};
const filter=value=>{get('archive-status').value=value;get('archive-status').listeners.change();};
const lesson=(key,status='observed',reviews=0,author='Fern',claim='Keep the record.')=>({key,status,reviews,author,claim});
frame={seq:90,archive:Array.from({length:12},(_,i)=>lesson('lesson-'+i))};
current=true;
`,ctx);
'''


@unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
class ArchiveLessonsTests(unittest.TestCase):
    def run_renderer(self, script):
        result = subprocess.run(
            ["node", "-e", HARNESS + "\nvm.runInContext(" + repr(script) + ",ctx);", str(ROOT / "site/house.js")],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bounded_pages_newest_first_and_page_focus(self):
        self.run_renderer(r'''
const before=JSON.stringify(frame);show();
assert.equal(articles().length,5);
assert.match(text(articles()[0]),/lesson 11/);
assert(get('archive-previous').disabled);
get('archive-next').listeners.click();
assert.match(text(articles()[0]),/lesson 6/);
assert.equal(document.activeElement,get('archive-lessons'));
assert(get('archive-lessons').scrolled);
assert.match(text(get('archive-results')),/showing 6–10/);
get('archive-next').listeners.click();
assert.equal(articles().length,2);assert(get('archive-next').disabled);
get('archive-previous').listeners.click();
assert.equal(articles().length,5);
assert.equal(JSON.stringify(frame),before);
''')

    def test_search_displayed_title_claim_author_and_clear_without_replacing_input(self):
        self.run_renderer(r'''
frame.archive.push(lesson('check-twice','observed',2,'Bay','Use the golden thread.'));show();
const input=get('archive-search');input.focus();
for(const query of [' CHECK   TWICE ','check-twice','GOLDEN',' bay ']) {
  search(query);assert.equal(articles().length,1);assert.match(text(articles()[0]),/check twice/);
  assert.equal(get('archive-search'),input);assert.equal(document.activeElement,input);
}
search('absent');assert.equal(articles().length,0);assert.match(text(root),/No lessons match/);
get('archive-clear').listeners.click();
assert.equal(get('archive-search'),input);assert.equal(input.value,'');
assert(get('archive-clear').disabled);assert.equal(articles().length,5);
assert.equal(archiveState.page,0);assert.equal(document.activeElement,input);
''')

    def test_states_keep_contested_reviews_and_superseded_lessons_distinct(self):
        self.run_renderer(r'''
frame.archive=[lesson('checked','observed',2),lesson('fresh'),
  lesson('disputed','contested',1),lesson('replaced','superseded',3)];show();
assert.match(text(root),/Contested · checked by 1 other resident/);
assert.match(text(root),/replaced by a later lesson/);
for(const [state,key] of [['reviewed','checked'],['unchecked','fresh'],['contested','disputed'],['superseded','replaced']]) {
  filter(state);assert.equal(articles().length,1);assert.match(text(articles()[0]),new RegExp(key));
  assert.match(text(get('archive-results')),/1 of 4/);
}
filter('all');search('missing');filter('reviewed');assert.equal(articles().length,0);
get('archive-clear').listeners.click();assert.equal(articles().length,1);
''')

    def test_history_refresh_clamps_pages_and_preserves_search_selection(self):
        self.run_renderer(r'''
show();get('archive-next').listeners.click();get('archive-next').listeners.click();
current=false;frame={seq:3,archive:[lesson('earlier','observed',0)]};show();
assert.equal(archiveState.page,0);assert.match(text(root),/event 3 · later lessons and reviews hidden/);
assert.match(text(root),/not yet checked/);assert.doesNotMatch(text(root),/lesson 11/);
roomPanel=show;lighting=accounts=drawHouse=renderViewContext=renderCollection=renderRecentGrowth=renderLately=()=>{};
search('ear');get('archive-search').focus();get('archive-search').setSelectionRange(1,2,'backward');
refreshView();assert.equal(document.activeElement,get('archive-search'));
assert.equal(get('archive-search').value,'ear');assert.equal(get('archive-search').selectionStart,1);
assert.equal(get('archive-search').selectionEnd,2);assert.equal(get('archive-search').selectionDirection,'backward');
get('archive-status').focus();refreshView();assert.equal(document.activeElement,get('archive-status'));
frame={seq:1};show();assert.equal(articles().length,0);assert.match(text(root),/not their text/);
frame.archive=[];show();assert.match(text(root),/No lesson has been written/);
''')

    def test_untrusted_text_stays_text(self):
        self.run_renderer(r'''
frame.archive=[lesson('<script>alert(1)</script>','contested',0,'<img src=x>','<svg onload=evil()>')];show();
assert.match(text(root),/<script>alert\(1\)<\/script>/);
assert.match(text(root),/<svg onload=evil\(\)>/);
assert(!all(root).some(n=>['script','img','svg'].includes(n.tag)));
assert.equal(get('archive-search').attrs['aria-describedby'],'archive-results');
assert.equal(get('archive-results').attrs.role,'status');
assert.equal(get('archive-next').attrs['aria-controls'],'archive-lessons');
''')
