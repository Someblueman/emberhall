"""Projects shows what is in motion and what is next; finished work lives on the Gallery view."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).parents[1]


@unittest.skipUnless(shutil.which('node'), 'Node is needed for the actual renderer')
class ProjectsViewTests(unittest.TestCase):
    def test_gallery_is_its_own_view_and_holds_what_is_finished(self):
        page = (ROOT / 'site/index.html').read_text()
        projects = page[page.index('id="projects-view"'):page.index('id="gallery-view"')]
        gallery = page[page.index('id="gallery-view"'):page.index('id="council-view"')]
        self.assertIn('id="shelf"', projects)
        self.assertNotIn('id="creations"', projects)
        for required in ('id="creations-card"', 'id="creations"', 'id="finished-card"', 'id="finished"'):
            self.assertIn(required, gallery)
        self.assertIn('<a href="#gallery-view">Gallery</a>', page)
        self.assertIn('class="gallery-invitation" href="#gallery-view"', page)

    def test_home_page_says_what_the_experiment_is(self):
        page = (ROOT / 'site/index.html').read_text()
        title, about, presence = (page.index(mark) for mark in ('id="house-title"', 'id="about-line"', 'id="presence-line"'))
        self.assertTrue(title < about < presence)
        line = page[about:presence]
        for word in ('experiment', 'AI agents', 'Steward', 'journal'):
            self.assertIn(word, line)

    def test_projects_orders_motion_asks_and_next_and_sends_finished_work_to_the_gallery(self):
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';}
  appendChild(node){this.children.push(node);}
  replaceChildren(){this.children=[];}
}
const nodes={shelf:new Element('div'),finished:new Element('div')};
const document={getElementById:id=>nodes[id]||null,createElement:tag=>new Element(tag)};
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const all=node=>[node,...node.children.flatMap(all)];
const context=vm.createContext({assert,document,URL,nodes,text,all,Intl,Date,Math});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(refresh,60000);setInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'UTC'};current=false;
frame={at:1000,seq:9,residents:[{id:'r1',name:'Juniper'}],shelf:{enabled:true,policy:'work-selection-004',
 research:{last:900,ceiling:10,next:5000},
 ideas:[
  {id:'old',title:'Old idea',status:'shelved',brief_due:9000},
  {id:'fresh',title:'Fresh idea',status:'shelved',brief:{field:'science',worth:'enabling',author:'r1'}},
  {id:'gone',title:'Gone idea',status:'graveyard',losses:2}],
 projects:[
  {id:'p-live',idea:'skein',title:'Skein',status:'active',slot:'great',owner:'r1',stage:1,deadline:1000+3*86400,
   milestone:'Use the packet',milestones:[{milestone:'Packet',seconds:86400},{milestone:'Use the packet',seconds:86400},{milestone:'Share',seconds:86400}],
   completed:[{stage:0,milestone:'Packet',sequence:4}]},
  {id:'p-done',idea:'ferry',title:'Night Ferry',status:'done',owner:'r1',milestone:'A playable mystery'}],
 needs:[{id:'n1',status:'open',kind:'access',for:'p-live',for_title:'Skein',author:'r1',ask:'Ten minutes with a real browser.',unlocks:'u',without:'w'}]}};
shelf();
const shelfText=text(nodes.shelf),finishedText=text(nodes.finished);
const order=['Building now','In motion','Skein','Asked of the Steward','What’s next','Fresh idea','Leaving the shelf unless a resident renews them · 1','Old idea','Graveyard (1)','in the Gallery','Work selection rules recorded'];
let at=-1;for(const part of order){const found=shelfText.indexOf(part,at+1);assert(found>at,part+' is out of order');at=found;}
assert.match(shelfText,/Now · milestone 2 of 3/);assert.match(shelfText,/Use the packet/);
assert.match(shelfText,/Due .* · 3d left/);
assert.match(shelfText,/Waiting on the Steward · 1 ask listed below/);
assert.equal(all(nodes.shelf).filter(n=>n.className==='done').length,1);
assert.equal(all(nodes.shelf).filter(n=>n.className==='current').length,1);
assert.doesNotMatch(shelfText,/Night Ferry|A playable mystery|Finished projects/);
assert(!all(nodes.shelf).some(n=>n.className==='shelf-completed'));
assert(all(nodes.shelf).some(n=>n.tag==='a'&&n.href==='#gallery-view'));
assert.match(shelfText,/1 finished project is in the Gallery/);
assert.match(finishedText,/Night Ferry/);assert.match(finishedText,/A playable mystery/);
assert.doesNotMatch(finishedText,/Skein|Fresh idea/);
const need=all(nodes.shelf).find(n=>n.className==='shelf-item shelf-need');
assert(need&&!need.open,'an ask is one line until opened');
frame.shelf.projects=frame.shelf.projects.filter(p=>p.status!=='done');shelf();
assert.match(text(nodes.finished),/No finished projects at this moment/);
assert.doesNotMatch(text(nodes.shelf),/in the Gallery/);
// Who asked: quoted askers, the second resident's check, and a project's deadline for a worth brief.
const asked=[{who:'A teacher on a forum',where:'https://forum.example.org/t/1',said:'Is there any tool that does this for me?'},
  {who:'A tutor',where:'javascript:alert(1)',said:'I do this by hand every week and it is slow.'}];
frame.shelf.ideas=[
  {id:'kept',title:'Kept idea',status:'shelved',grounded:true,author:'r1',brief:{field:'software',worth:'useful',author:'r1',asked},
   second:{author:'r1',finding:'Opened both pages; they ask for exactly this.',at:900}},
  {id:'unchecked',title:'Unchecked idea',status:'shelved',grounded:false,brief_due:9000,brief:{field:'software',worth:'useful',author:'r1',asked}},
  {id:'unasked',title:'Unasked idea',status:'shelved',grounded:false,brief_due:9000,brief:{field:'science',worth:'enabling',author:'r1'}}];
frame.shelf.projects=[{id:'p-live',idea:'skein',title:'Skein',status:'active',owner:'r1',deadline:1000+86400,milestone:'Use it',brief_due:1000+6*3600},
  {id:'p-ok',idea:'bench',title:'Bench',status:'active',owner:'r1',deadline:1000+86400,milestone:'Try it',brief:{field:'software',worth:'useful',author:'r1',asked,benefit:'Helps reviewers.'}}];
shelf();
const who=text(nodes.shelf);
assert.match(who,/Who asked for this/);assert.match(who,/A teacher on a forum: “Is there any tool that does this for me\\?”/);
assert.match(who,/Checked by Juniper, who wrote neither the idea nor its brief: Opened both pages/);
assert.match(who,/Kept idea.*Researched/s);assert.match(who,/Unchecked idea.*Awaiting a second/s);assert.match(who,/Unasked idea.*Who asked\\?/s);
assert.match(who,/Only its author has said who would use this · leaves the shelf/);
assert.match(who,/Nobody has shown who asked for this · leaves the shelf/);
assert.match(who,/Nobody but its owner has shown who this is for · dropped .* unless another resident writes its worth brief/);
assert.match(who,/Worth brief, by a resident who does not own it · Juniper/);
const places=all(nodes.shelf).filter(n=>n.tag==='a'&&n.textContent==='where they said it ↗').map(n=>n.href);
assert(places.length>=3&&places.every(href=>href==='https://forum.example.org/t/1'),'only real web addresses become links');
frame={};shelf();
assert.match(text(nodes.shelf),/not activated/);assert.match(text(nodes.finished),/No finished projects/);
`,context);
vm.runInContext(`
const views=['house-view','projects-view','gallery-view','council-view','accounts-view'].map(id=>({id,hidden:false}));
const links=views.map(v=>({hash:'#'+v.id,attrs:{},setAttribute(k,v){this.attrs[k]=v;},removeAttribute(k){delete this.attrs[k];}}));
document.getElementById=id=>views.find(v=>v.id===id)||null;
document.querySelectorAll=s=>s==='.page-view'?views:s==='.view-nav a'?links:[];
for(const hash of ['#gallery-view','#creations-card','#finished-card']){
  showViewForHash(hash);
  assert.deepEqual(views.filter(v=>!v.hidden).map(v=>v.id),['gallery-view'],hash);
  assert.deepEqual(links.filter(l=>l.attrs['aria-current']).map(l=>l.hash),['#gallery-view']);
}
showViewForHash('#shelf-card');assert.deepEqual(views.filter(v=>!v.hidden).map(v=>v.id),['projects-view']);
`,context);
'''
        result = subprocess.run([shutil.which('node'), '-e', script, str(ROOT / 'site/house.js')],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == '__main__':
    unittest.main()
