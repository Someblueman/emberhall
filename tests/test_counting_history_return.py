"""Counting event trips restore the visitor's ledger instead of losing its page."""
import unittest
import shutil
import json
from pathlib import Path
from tests import test_counting_work_trail as ledger


def write_deferred_fixture(destination):
    """Native-browser reproduction with a delayed, complete retained history."""
    from tests.test_site_refresh_scheduling import write_missing_snapshot_fixture
    root = Path(__file__).resolve().parents[1]
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    write_missing_snapshot_fixture(destination, failures=0)
    history = json.loads((root / "site/history.json").read_text())
    for moment in history["frames"]:
        moment["rooms"].append(dict(id="counting", name="Counting Room", status="open"))
    history["frames"][-1]["runs"] = [dict(
        id="fixture-run", resident="fixture-reader", agent="codex", sequence=6,
        start=history["frames"][5]["at"], status="ended", outcome="success", finished_tasks=[])]
    payload = json.dumps(history).replace("<", "\\u003c")
    page = destination.read_text().replace(
        "Controlled missing snapshot fixture", "Controlled deferred run-ledger fixture")
    page = page.replace("window.fetch=async url=>{", "const historyFixture=" + payload +
                        ";fixtureSnapshot.frames[0]=structuredClone(historyFixture.frames.at(-1));"
                        "window.fetch=async url=>{")
    page = page.replace("if(path==='head.json')", "if(path==='history.json'){"
                        "await new Promise(resolve=>setTimeout(resolve,250));"
                        "return {ok:true,json:async()=>structuredClone(historyFixture)};}"
                        "if(path==='head.json')")
    destination.write_text(page)


@unittest.skipUnless(shutil.which("node"), "Node executes the page renderer")
class CountingHistoryReturnTests(unittest.TestCase):
    run_js = ledger.CountingWorkTrailTests.run_js
    # Reuse the existing small DOM with the shipped renderer and real event jump.
    def run_trip(self, checks):
        self.run_js(r'''
const origin=frame;
runs[0].sequence=1;runs[1].sequence=3;
const append=Element.prototype.appendChild;
Element.prototype.appendChild=function(n){n.parent=this;return append.call(this,n);};
Element.prototype.closest=function(tag){let n=this;while(n&&n.tag!==tag)n=n.parent;return n;};
const earlier={...base,seq:3,at:1003,runs:[runs[0]],event:{op:'wake'}};
finished.runs=[runs[0]];
data.frames.splice(2,0,earlier);index=3;
render=()=>{frame=data.frames[index];root.replaceChildren();
 if(visitedRoom==='workshop')renderWorkshopTasks(root);else draw();};
const openHandoff=()=>{const d=get('counting-handoffs-run%200');d.open=true;d.listeners.toggle();};
countingState={agent:'codex',lane:'work',page:1};draw();openHandoff();
''' + checks)

    def test_run_visit_returns_to_page_filters_disclosures_and_focus(self):
        self.run_trip(r'''
const before=JSON.stringify(data),saved=JSON.stringify(countingState);
get('counting-jump-3').listeners.click();assert.equal(frame.seq,3);
assert.equal(countingState.page,0);assert(get('counting-history-return'));
assert.doesNotMatch(text(root),/fixture-9/);
get('counting-history-return').listeners.click();
assert.equal(frame.seq,20);assert.equal(current,true);
assert.equal(JSON.stringify(countingState),saved);
assert(get('counting-handoffs-run%200').open);
assert.equal(document.activeElement,get('counting-jump-3'));
assert.equal(countingHistoryTrail,null);assert.equal(JSON.stringify(data),before);
''')

    def test_deferred_history_focuses_the_mounted_destination(self):
        self.run_trip(r'''
const historyFrames=[...data.frames];
data.frames=[origin];data.history={current_only:true,last_sequence:20,total_frames:4};index=0;
let complete;
ensureHistory=()=>new Promise(resolve=>{complete=()=>{
 data.frames=historyFrames;delete data.history;resolve(true);
};});
const replace=Element.prototype.replaceChildren;
Element.prototype.replaceChildren=function(){
 if(all(this).includes(document.activeElement))document.activeElement=null;
 replace.call(this);
};
let scrolled=null;
Element.prototype.scrollIntoView=function(){scrolled=this;};
draw();get('counting-jump-3').listeners.click();assert.equal(frame.seq,20);
complete();Promise.resolve().then(()=>{
 assert.equal(frame.seq,3);
 assert(document.activeElement===get('counting-runs'),'focus the new ledger after loading');
 assert(scrolled===document.activeElement,'bring the mounted destination into view');
 assert(all(root).includes(document.activeElement),'never focus a detached control');
 get('counting-history-return').listeners.click();assert.equal(frame.seq,20);
 assert(document.activeElement===get('counting-jump-3'),'restore the original run button');
});
''')

    def test_deferred_trip_cannot_steal_focus_from_newer_navigation(self):
        self.run_trip(r'''
const historyFrames=[...data.frames];
data.frames=[origin];data.history={current_only:true,last_sequence:20,total_frames:4};index=0;
let complete;
ensureHistory=()=>new Promise(resolve=>{complete=()=>{
 data.frames=historyFrames;delete data.history;resolve(true);
};});
draw();get('counting-jump-3').listeners.click();
const newer=new Element('button');document.activeElement=newer;
historyNavigation++;complete();Promise.resolve().then(()=>{
 assert.equal(frame.seq,20);assert(document.activeElement===newer,'a cancelled trip must not move focus');
});
''')

    def test_trip_before_the_ledger_existed_focuses_the_room_record(self):
        self.run_trip(r'''
nodes['room-card']=new Element('section');
render=()=>{frame=data.frames[index];root.replaceChildren();};
get('counting-jump-3').listeners.click();
assert.equal(frame.seq,3);
assert(document.activeElement===nodes['room-card'],'show the room record when the ledger is absent');
''')

    def test_handoff_visit_returns_to_historical_origin_after_new_publication(self):
        self.run_trip(r'''
current=false;get('counting-finish-2').listeners.click();
assert.equal(frame.seq,2);assert.equal(document.activeElement,get('counting-finish-2'));
assert(get('counting-handoffs-run%200').open);
data.frames.push({...origin,seq:30,at:1030});render();
get('counting-history-return').listeners.click();
assert.equal(frame.seq,20);assert.equal(current,false);assert.equal(countingState.page,1);
assert.equal(document.activeElement,get('counting-finish-2'));
assert(get('counting-handoffs-run%200').open);
''')

    def test_nested_visits_keep_origin_and_lost_origin_allows_fresh_trip(self):
        self.run_trip(r'''
get('counting-jump-3').listeners.click();get('counting-finish-2').listeners.click();
assert.equal(countingHistoryTrail.sequence,20);
get('counting-history-return').listeners.click();assert.equal(frame.seq,20);
get('counting-jump-3').listeners.click();
data.frames=data.frames.filter(f=>f.seq!==20);index=data.frames.indexOf(frame);render();
assert(!get('counting-history-return'));assert.match(text(root),/original moment is absent/);
get('counting-finish-2').listeners.click();assert.equal(countingHistoryTrail.sequence,3);
get('counting-history-return').listeners.click();assert.equal(frame.seq,3);
assert.equal(document.activeElement,get('counting-finish-2'));
''')

    def test_missing_destination_and_same_moment_do_not_create_trip(self):
        self.run_trip(r'''
const stale=get('counting-jump-3');data.frames=data.frames.filter(f=>f.seq!==3);
stale.listeners.click();assert.equal(countingHistoryTrail,null);assert.equal(frame.seq,20);
index=data.frames.indexOf(finished);current=false;render();
get('counting-finish-2').listeners.click();assert.equal(countingHistoryTrail,null);
assert.equal(frame.seq,2);assert.equal(document.activeElement,get('counting-finish-2'));
''')

    def test_workshop_round_trip_keeps_the_history_return(self):
        self.run_trip(r'''
get('counting-jump-3').listeners.click();get(followId).listeners.click();render();
assert(get('workshop-run-ledger'));get('workshop-run-ledger').listeners.click();
assert.equal(frame.seq,3);assert(get('counting-history-return'));
get('counting-history-return').listeners.click();assert.equal(frame.seq,20);
assert.equal(document.activeElement,get('counting-jump-3'));
''')

    def test_return_resolves_the_source_again_when_the_publication_changes(self):
        self.run_trip(r'''
get('counting-jump-3').listeners.click();
data.frames.unshift({...base,seq:0,at:1000});
data.frames.push({...origin,seq:30,at:1030});
get('counting-history-return').listeners.click();
assert.equal(frame.seq,20);assert.equal(current,false);
assert.equal(document.activeElement,get('counting-jump-3'));
get('counting-jump-3').listeners.click();const back=get('counting-history-return');
data.frames=data.frames.filter(f=>f.seq!==20);index=data.frames.indexOf(frame);
back.listeners.click();assert.equal(frame.seq,3);assert(!get('counting-history-return'));
assert.match(text(root),/original moment is absent/);
get('counting-finish-2').listeners.click();assert.equal(countingHistoryTrail.sequence,3);
''')
