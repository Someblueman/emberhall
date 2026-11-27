"""Secondary views render on entry and release hidden record rows."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(id='',tag='DIV'){this.id=id;this.tagName=tag;this.children=[];this.attrs={};this.hidden=true;}
 appendChild(node){this.children.push(node);return node;}
 replaceChildren(){this.children=[];}
 querySelectorAll(tag){return this.children.filter(n=>n.tagName===tag.toUpperCase());}
 setAttribute(k,v){this.attrs[k]=v;}
 removeAttribute(k){delete this.attrs[k];}
 focus(){document.activeElement=this;}
 scrollIntoView(){this.scrolled=true;}
}
const ids=['house-view','projects-view','gallery-view','council-view','accounts-view'];
const nodes={},get=id=>nodes[id]??(nodes[id]=new Element(id));
ids.forEach(get);get('house-view').hidden=false;
const document={getElementById:get,activeElement:null,
 querySelector:s=>s==='.page-view:not([hidden])'?ids.map(get).find(n=>!n.hidden):null,
 querySelectorAll:s=>s==='.page-view'?ids.map(get):[]};
const context=vm.createContext({document,Date,Intl,Math,URL});
const source=fs.readFileSync(process.argv[1],'utf8'),startup=source.lastIndexOf('\nrefresh();');
assert(startup>0);vm.runInContext(source.slice(0,startup),context);
const run=s=>vm.runInContext(s,context);
context.calls={accounts:0,shelf:0,voting:0,collection:0,house:0};
run(`data={journal_head:'head1'};frame={seq:1};catalogSource='catalog1';
 const write=(id)=>{const target=document.getElementById(id);target.replaceChildren();target.appendChild({tagName:'P',textContent:frame.seq+':'+catalogSource});};
 accounts=()=>{calls.accounts++;write('budgets');};
 shelf=()=>{calls.shelf++;write('shelf');write('finished');};
 voting=()=>{calls.voting++;write('voting');};
 renderCollection=()=>{calls.collection++;write('creations');};
 render=()=>{calls.house++;renderAuxiliaryViews();};
`);
for(const id of ['budgets','shelf','finished','voting','creations'])get(id).appendChild({tagName:'P',oldFrame:true});
run(`renderAuxiliaryViews();`);
assert.deepEqual(context.calls,{accounts:0,shelf:0,voting:0,collection:0,house:0});
for(const id of ['budgets','shelf','finished','voting','creations'])assert.equal(get(id).children.length,0);
run(`showViewForHash('#voting-card',true);`);
assert.equal(context.calls.voting,1);assert.equal(get('council-view').hidden,false);
assert.equal(document.activeElement.id,'voting-card');
const detail=new Element('vote-a','DETAILS');detail.open=true;get('voting').appendChild(detail);
run(`showViewForHash('#accounts-view');`);
assert.equal(context.calls.accounts,1);assert.equal(get('voting').children.length,0);
assert.equal(run(`votingOpened.has('vote-a')`),true);
run(`frame={seq:2};data={journal_head:'head2'};catalogSource='catalog2';showViewForHash('#projects-view');`);
assert.equal(context.calls.shelf,1);assert.equal(get('shelf').children[0].textContent,'2:catalog2');
assert.equal(get('budgets').children.length,0);
run(`showViewForHash('#finished-card',true);`);
assert.equal(get('gallery-view').hidden,false);assert.equal(context.calls.collection,1);
assert.equal(get('finished').children[0].textContent,'2:catalog2');
assert.equal(get('creations').children[0].textContent,'2:catalog2');
const iframe=get('gallery-signal-trial');iframe.tagName='IFRAME';iframe.setAttribute('src','old-gallery');
run(`showViewForHash('#house-view');`);
assert.equal(context.calls.house,1);assert.equal(get('creations').children.length,0);
assert.equal(get('shelf').children.length,0);assert.equal(iframe.attrs.src,undefined);assert.equal(iframe.hidden,true);
// Returning to a view after a frame/catalog change rebuilds it, never shows old rows.
run(`frame={seq:3};catalogSource='catalog3';showViewForHash('#gallery-view');`);
assert.equal(get('creations').children[0].textContent,'3:catalog3');
assert.equal(get('finished').children[0].textContent,'3:catalog3');
// An unchanged-publication local redraw updates only the active auxiliary view.
run(`lighting=roomPanel=drawHouse=renderViewContext=renderRecentGrowth=renderLately=()=>{};
 refreshView(false);`);
assert.equal(get('creations').children[0].textContent,'3:catalog3');
assert.equal(context.calls.accounts,1);assert.equal(context.calls.voting,1);
run(`showViewForHash('#room/hearth');`);
assert.equal(get('house-view').hidden,false);assert.equal(get('creations').children.length,0);
// A minimal embedded host without page views retains the established eager renderer.
context.document.querySelector=()=>null;
run(`renderAuxiliaryViews();`);
assert.equal(get('budgets').children[0].textContent,'3:catalog3');
console.log('initial hidden panels skipped; route aliases, refresh, frame/catalog changes and old DOM release pass');
'''


@unittest.skipUnless(shutil.which('node'),'Node executes the real routing and dispatcher')
class DeferredViewChecks(unittest.TestCase):
    def test_secondary_views_are_current_on_entry_and_hidden_rows_are_released(self):
        result=subprocess.run(['node','-e',SCRIPT,str(ROOT/'site/house.js')],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('initial hidden panels skipped',result.stdout)


    def test_late_catalog_load_does_not_build_hidden_gallery(self):
        from tests.test_site_refresh_scheduling import SiteRefreshSchedulingTests
        SiteRefreshSchedulingTests().run_page(r'''
await start();
let activeView='house-view';
document.querySelector=()=>({id:activeView});
for(const id of ['budgets','shelf','finished','voting','creations']) {
 get(id).replaceChildren=()=>{};get(id).querySelectorAll=()=>[];
}
run(`let galleryDraws=0,projectDraws=0;
 renderCollection=()=>galleryDraws++;shelf=()=>projectDraws++;
 loadCatalog=async()=>{catalog={};catalogSource=data.source_head;};
 catalogSource=null;`);
await run('refresh()');
assert.equal(run('galleryDraws'),0);assert.equal(run('projectDraws'),0);
activeView='gallery-view';run('catalogSource=null');
await run('refresh()');
assert.equal(run('galleryDraws'),1);assert.equal(run('projectDraws'),1);
''')


if __name__=='__main__':unittest.main()
