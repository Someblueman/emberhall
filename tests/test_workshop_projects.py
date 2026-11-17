"""Follow project work without leaking facts from later house moments."""
import shutil
import unittest

from tests.test_workshop_ui import RendererMixin


@unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
class WorkshopProjectTests(RendererMixin, unittest.TestCase):
    def test_project_options_include_house_work_and_missing_names(self):
        self.run_renderer(r'''
draw([
 {id:'house',title:'Repair the door',status:'open'},
 {id:'ferry',title:'Sail',status:'open',project:'ferry'},
 {id:'unknown',title:'Unknown name',status:'open',project:'lost'},
 {id:'blank',title:'No project',status:'open',project:'  '},
 {id:'all',title:'A project called all',status:'open',project:'all'}
]);
frame.shelf={projects:[{id:'ferry',title:'Night Ferry'},{id:'unused',title:'No threads yet'}]};roomPanel();
const options=()=>all($('workshop-project')).filter(n=>n.tag==='option');
assert.equal(options().map(n=>n.value).join('|'),'all|house|project:all|project:lost|project:ferry');
assert.match(text($('workshop-project')),/Project: Night Ferry/);
assert(all(panel()).some(n=>n.tag==='label'&&n.attrs.for==='workshop-project'));
assert.doesNotMatch(text($('workshop-project')),/No threads yet/);
$('workshop-project').change('project:ferry');assert.equal(cards().length,1);
assert.match(text(cards()[0]),/Sail/);assert.equal(document.activeElement.id,'workshop-project');
$('workshop-project').change('house');assert.equal(cards().length,2);
$('workshop-project').change('project:lost');assert.match(text(cards()[0]),/Unknown name/);
$('workshop-project').change('project:all');assert.equal(cards().length,1);
assert.match(text(cards()[0]),/A project called all/);
''')

    def test_combined_filters_paging_search_and_find_selected_card(self):
        self.run_renderer(r'''
draw([
 ...Array.from({length:9},(_,i)=>({id:'p'+i,title:'Build '+i,status:'open',ready:true,project:'p'})),
 {id:'other',title:'Other work',status:'open',project:'q'}
]);
$('workshop-unassigned-Next').click();assert.match(text(panel()),/5–8 of 10/);
$('workshop-project').change('project:p');assert.match(text(panel()),/1–4 of 9/);
assert.match(text($('workshop-results')),/9 of 10 tasks/);
$('workshop-readiness').change('ready');$('workshop-filter').change('unassigned');
$('workshop-search').value='Build 8';$('workshop-search').listeners.input();
assert.equal(cards().length,1);assert.match(text(cards()[0]),/Build 8/);
$('workshop-clear').click();assert.match(text(panel()),/1–4 of 9/);
assert.equal($('workshop-project').value,'project:p');
$('workshop-unassigned-Next').click();const chosen=cards()[0].id;cards()[0].click();
$('workshop-project').change('project:q');assert.equal(cards().length,0);
assert.match(text($('workshop-detail')),/Build/);
button('Find task card').click();assert.equal(document.activeElement.id,chosen);
assert.equal($('workshop-project').value,'all');assert.equal($('workshop-readiness').value,'all');
''')

    def test_finished_history_keeps_project_and_rewind_hides_future_names(self):
        self.run_renderer(r'''
const base={at:1000,rooms:[{id:'workshop',name:'Workshop'}],residents:[],runs:[],scars:[]};
data.frames=[
 {...base,seq:1,tasks:[{id:'old',title:'Old work',project:'p',status:'open'}],event:{op:'task'}},
 {...base,seq:2,tasks:[],event:{op:'finish',title:'old'}},
 {...base,seq:3,tasks:[{id:'future',title:'Future work',project:'q',status:'open'}],event:{op:'task'},
  shelf:{projects:[{id:'p',title:'Later name'},{id:'q',title:'Future project'}]}}
];
index=2;frame=data.frames[index];roomPanel();
$('workshop-project').change('project:p');assert.equal(cards().length,1);
assert.match(text(cards()[0]),/Old work/);assert.match(text(cards()[0]),/Finished/);
assert.match(text($('workshop-project')),/Later name/);
$('workshop-project').change('project:q');cards()[0].click();
index=0;frame=data.frames[0];roomPanel();
assert.equal(cards().length,0);assert.equal($('workshop-project').value,'project:q');
assert.match(text($('workshop-project')),/Selected project not recorded at this moment/);
assert.match(text($('workshop-project')),/Project: p/);
assert.doesNotMatch(text(panel()),/Later name|Future project|Future work/);
index=2;frame=data.frames[2];roomPanel();assert.equal(cards().length,1);
assert.equal(cards()[0].id,'workshop-task-future');
''')

    def test_refresh_retains_project_and_safe_labels(self):
        self.run_renderer(r'''
draw([{id:'one',title:'One',status:'open',project:'<img src=x>'}]);
frame.shelf={projects:[{id:'<img src=x>',title:'<script>alert(1)</script>'}]};roomPanel();
assert.equal(all(panel()).filter(n=>n.tag==='img'||n.tag==='script').length,0);
$('workshop-project').change('project:<img src=x>');
lighting=accounts=drawHouse=renderViewContext=renderCollection=renderRecentGrowth=()=>{};
refreshView();assert.equal($('workshop-project').value,'project:<img src=x>');
assert.equal(document.activeElement.id,'workshop-project');assert.equal(cards().length,1);
assert.match(text(cards()[0]),/<script>alert\(1\)<\/script>/);
''')


if __name__ == "__main__":
    unittest.main()
