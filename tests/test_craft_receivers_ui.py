import json
from pathlib import Path
import shutil
import subprocess
import unittest

from house.craft_outcomes import public_window
from tests import test_craft_public_receivers as projection_tests

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node executes the actual page renderer")
class ReceivingUI(unittest.TestCase):
    def test_counts_examples_malformed_payload_and_historical_isolation(self):
        fixture = projection_tests.PublicReceivers()
        fixture.setUp()
        work = fixture.work
        offered = work.start("one", "receiver")
        work.finish(work.claim("one"))
        work.close("one")
        review = fixture.review("one", "tests-failed")
        fixture.review("one", "integrated")
        report = public_window(work.events, len(work.events), "head", "source")
        js = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const report=JSON.parse(fs.readFileSync(0,'utf8'));
const source=fs.readFileSync(process.argv[1],'utf8').split('\nrefresh();\nsetInterval')[0];
function node(tag) {return {tagName:tag,children:[],style:{},dataset:{},listeners:{},textContent:'',
 appendChild(n){n.parent=this;this.children.push(n);return n},replaceChildren(){this.children=[]},
 setAttribute(){},addEventListener(k,f){this.listeners[k]=f},focus(){this.focused=true},
 closest(tag){return this.parent?.tagName===tag?this.parent:this.parent?.closest(tag)}}}
const latest={focus(){this.focused=true}};
const document={createElement:node,getElementById(){return latest}};
const ctx=vm.createContext({document,assert,report});
vm.runInContext(source,ctx);
vm.runInContext(`
  data={source_head:'source',journal_head:'head',frames:[{seq:report.through}],craft:report};
  frame={seq:report.through,at:0,shelf:{projects:[{id:'math',title:'<img src=x onerror=alert(1)>'}]}};
  current=true;
  const panel=document.createElement('section');
  fillCraftOutcomes(panel);
  function walk(n){return [n,...n.children.flatMap(walk)]}
  const texts=walk(panel).map(n=>n.textContent).join(' | ');
  assert(texts.includes('1 of 1 eligible offers finished by the receiver'));
  assert(texts.includes('0 of 1 finished offered tasks with a review passed their first check'));
  assert(texts.includes('Receiver finishes without a matched review: 0'));
  assert(texts.includes('<img src=x onerror=alert(1)>'));
  assert.equal(walk(panel).some(n=>n.tagName==='img'),false);
  assert(texts.includes('Claims residents took on'));
  assert(craftMatches(report,data));
  const copy=()=>JSON.parse(JSON.stringify(report));
  for(const key of ['eligible_offers','offers','quota','receiver_finished','reviewed_receiver_runs']) {
    const bad=copy();bad.receiving.rows[0][key]=-1;assert.equal(craftMatches(bad,data),false);
  }
  for(const change of [
    r=>r.receiving.rows[0].first_pass=2,
    r=>r.receiving.rows[0].finished_without_review=1,
    r=>r.receiving.rows[0].examples[0].offer=report.through+1,
    r=>r.receiving.rows[0].examples[0].disposition='<script>',
    r=>r.receiving.rows[0].examples[0].claim='3',
    r=>r.receiving.rows[0].claimed_elsewhere=1,
    r=>r.receiving.distinct_eligible_tasks=-1]) {
    const bad=copy();change(bad);assert.equal(craftMatches(bad,data),false);
  }
  const old=copy();delete old.receiving;assert(craftMatches(old,data));
  const missing=document.createElement('section');renderCraftReceiving(missing,undefined,{});
  assert(walk(missing).some(n=>n.textContent.includes('older publication')));
  let jumped=null;
  jumpToSequence=(seq,afterJump)=>{jumped=seq;current=false;afterJump?.()};
  const expected=report.receiving.rows[0].examples[0];
  document.querySelector=selector=>walk(panel).find(n=>n.dataset?.craftReturn&&
    selector.includes('"'+n.dataset.craftReturn+'"'));

  for(const [label,seq] of [['Offered',expected.offer],['Claimed',expected.claim],
                           ['Finished',expected.finish],['First review',expected.first_review]]) {
    current=true;
    walk(panel).find(n=>n.tagName==='button'&&n.textContent===label+' · event '+seq).listeners.click();
    assert.equal(jumped,seq);assert(document.getElementById('view-latest').focused);
    restoreCraftFocus();
    const origin=walk(panel).find(n=>n.dataset?.craftReturn===expected.offer+'-'+
      ({Offered:'offer',Claimed:'claim',Finished:'finish','First review':'first_review'})[label]);
    assert(origin.focused);assert(origin.closest('details').open);assert.equal(craftReturn,null);
  }
  craftReturn={source:'old-source',head:'head',control:expected.offer+'-offer'};
  assert.doesNotThrow(()=>restoreCraftFocus());assert.equal(craftReturn,null);
  craftReturn={source:'source',head:'head',control:'missing'};
  assert.doesNotThrow(()=>restoreCraftFocus());assert.equal(craftReturn,null);
  const past=document.createElement('section');
  current=false;renderCraftOutcomes(past);assert.equal(past.children.length,0);
  current=true;frame.seq--;fillCraftOutcomes(past);
  assert(!walk(past).some(n=>n.textContent==='Tasks offered to a resident'));
`,ctx);
'''
        subprocess.run(["node", "-e", js, str(ROOT / "site/house.js")],
                       input=json.dumps(report), text=True, check=True)
        self.assertEqual(report["receiving"]["rows"][0]["examples"][0]["offer"], offered)
        self.assertEqual(report["receiving"]["rows"][0]["examples"][0]["first_review"], review)


if __name__ == "__main__":
    unittest.main()
