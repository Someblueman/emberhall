"""Search the published Workshop renderer without consulting future frames."""
import json
import shutil
import unittest

from house.body import export
from house.public_history import decode
from tests.support import HouseCase
from tests.test_workshop_ui import ROOT, RendererMixin


SEARCH = r'''
const searchFor=value=>{
 const input=$('workshop-search');input.focus();input.value=value;
 input.listeners.input({target:input});return input;
};
'''


@unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
class WorkshopSearchTests(RendererMixin, unittest.TestCase):
    def test_title_matching_counts_and_combined_filters(self):
        self.run_renderer(SEARCH + r'''
draw([
 {id:'one',title:'Repair   the Hearth',status:'open',ready:true},
 {id:'two',title:'Repair the Door',status:'open',ready:false},
 {id:'three',title:'Repair the Roof',status:'claimed',owner:'a',until:3000,ready:true},
 {id:'four',title:'Other',status:'done'}
]);
assert.equal($('workshop-search').type,'search');
assert.equal($('workshop-search').attrs['aria-describedby'],'workshop-results');
assert.match(text(panel()),/Find work/);searchFor('  REPAIR   THE  ');
assert.equal(cards().length,3);assert.match(text($('workshop-results')),/3 of 4 tasks/);
$('workshop-readiness').change('ready');assert.equal(cards().length,2);
$('workshop-filter').change('unassigned');assert.equal(cards().length,1);
assert.match(text(cards()[0]),/Hearth/);searchFor('absent');assert.equal(cards().length,0);
assert.match(text(panel()),/Clear search or change Work and Queue/);
assert.match(text($('workshop-results')),/0 of 4 tasks/);
$('workshop-clear').click();assert.equal(cards().length,1);
assert.equal($('workshop-filter').value,'unassigned');
assert.equal($('workshop-readiness').value,'ready');
''')

    def test_paging_resets_on_query_and_clear(self):
        self.run_renderer(SEARCH + r'''
draw(Array.from({length:13},(_,i)=>({id:'t'+i,title:'Thread '+i,status:'open'})));
$('workshop-unassigned-Next').click();assert.match(text(panel()),/5–8 of 13/);
searchFor('thread');assert.match(text(panel()),/1–4 of 13/);
$('workshop-unassigned-Next').click();searchFor('Thread 12');
assert.equal(cards().length,1);assert.match(text(cards()[0]),/Thread 12/);
assert.match(text($('workshop-results')),/1 of 13 tasks/);
$('workshop-clear').click();assert.equal($('workshop-search').value,'');
assert.match(text(panel()),/1–4 of 13/);assert.equal($('workshop-clear').disabled,true);
assert.equal(document.activeElement,$('workshop-search'));
''')

    def test_typing_keeps_input_and_caret_and_refresh_restores_selection(self):
        self.run_renderer(SEARCH + r'''
draw([{id:'one',title:'Hearth repair',status:'open'}]);
const input=searchFor('Hearth');input.selectionStart=2;input.selectionEnd=4;input.selectionDirection='backward';
input.listeners.input({target:input});assert.equal($('workshop-search'),input);
assert.equal(document.activeElement,input);assert.equal(input.selectionStart,2);assert.equal(input.selectionEnd,4);
Object.getPrototypeOf(input).setSelectionRange=function(start,end,direction){
 this.selectionStart=start;this.selectionEnd=end;this.selectionDirection=direction;
};
lighting=accounts=drawHouse=renderViewContext=renderCollection=renderRecentGrowth=()=>{};
refreshView();const replacement=$('workshop-search');assert.notEqual(replacement,input);
assert.equal(document.activeElement,replacement);assert.equal(replacement.value,'Hearth');
assert.equal(replacement.selectionStart,2);assert.equal(replacement.selectionEnd,4);
assert.equal(replacement.selectionDirection,'backward');
''')

    def test_partial_snapshot_owner_names_and_safe_query(self):
        self.run_renderer(SEARCH + r'''
draw([{id:'x',title:'<img src=x>',status:'claimed',owner:'a',until:3000}]);
frame.residents=[{id:'a',name:'Tern'}];roomPanel();searchFor(' tErN ');
assert.equal(cards().length,1);searchFor('<img');assert.equal(cards().length,1);
assert.equal(all(panel()).filter(n=>n.tag==='img').length,0);
searchFor('unrecorded');assert.equal(cards().length,0);
''')

    def test_find_a_finished_task_in_real_retained_history(self):
        fixture = decode(json.loads((ROOT / "site/history.json").read_text()))
        self.run_renderer(SEARCH + r'''
data=fixture;index=data.frames.length-1;frame=data.frames[index];current=true;roomPanel();
$('workshop-filter').change('done');searchFor('founding boundary');
assert.equal(cards().length,1);assert.equal(cards()[0].id,'workshop-task-witness-review');
cards()[0].click();assert.equal(events().length,3);
assert.match(text($('workshop-detail')),/Finished/);
assert.doesNotMatch(text($('workshop-detail')),/acceptance and delivery unknown/);
''', fixture)


@unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
class WorkshopSearchHistoryTests(RendererMixin, HouseCase):
    def test_participants_selection_rewind_return_and_future_isolation(self):
        self.task()
        self.record.append("claim", "bob", {"task": "work", "expect": 0, "token": "x", "seconds": 300})
        self.record.append("release", "bob", {"task": "work", "token": "x", "note": "Private"})
        prefix = export(self.record)
        self.record.append("arrive", "future", {"name": "Future Person"})
        self.record.append("task", "future", {"task": "future-work", "title": "Later Title", "description": "Private"})
        self.record.append("claim", "future", {"task": "work", "expect": 1, "token": "y", "seconds": 300})
        fixture = export(self.record)
        fixture["prefix_seq"] = prefix["frames"][-1]["seq"]
        # A later resident name in a later public frame must also stay out of the prefix search.
        fixture["frames"][-1]["residents"] = [dict(r, name="Later Name") if r["id"] == "bob" else r
                                             for r in fixture["frames"][-1]["residents"]]
        self.run_renderer(SEARCH + r'''
data=fixture;index=data.frames.length-1;frame=data.frames[index];current=true;roomPanel();
searchFor('Later Name');assert.equal(cards().length,1);
searchFor('Alice');assert.equal(cards().length,1);cards()[0].click();
searchFor('no match');assert.equal(cards().length,0);
assert.match(text($('workshop-detail')),/Work/);button('Find task card').click();
assert.equal($('workshop-search').value,'');assert.equal(document.activeElement.id,'workshop-task-work');
searchFor('Bob');assert.equal(cards().length,1);events()[0].click();
assert.equal(frame.seq,4);assert.equal(cards().length,0);assert.equal(events().length,1);
assert.equal(document.activeElement.id,'workshop-detail');
$('workshop-present').click();assert.equal(current,true);assert.equal(cards().length,1);
$('workshop-filter').change('all');jumpToSequence(data.prefix_seq);searchFor('Bob');assert.equal(cards().length,1);
searchFor('Future Person');assert.equal(cards().length,0);
searchFor('Later Title');assert.equal(cards().length,0);searchFor('Later Name');assert.equal(cards().length,0);
assert.match(text($('workshop-results')),/0 of 1 tasks/);
assert.doesNotMatch(text(panel()),/Future Person|Later Title|Later Name|Private/);
''', fixture)


if __name__ == "__main__":
    unittest.main()
