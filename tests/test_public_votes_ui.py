"""Run the actual voting renderer: attribution, safe text and historical reset."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node is needed for the actual renderer")
class PublicVotesUITests(unittest.TestCase):
    def test_votes_rules_bell_and_historical_reset(self):
        script = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.attrs={};}
  setAttribute(name,value){this.attrs[name]=String(value);}
  appendChild(node){this.children.push(node);}
  replaceChildren(){this.children=[];}
  querySelectorAll(selector){return this.children.flatMap(n=>[n,...n.querySelectorAll(selector)]).filter(n=>n.tag==='details'&&(selector!=='details[open]'||n.open));}
}
const root=new Element('section'),document={getElementById:()=>root,createElement:tag=>new Element(tag)};
const text=n=>[n.textContent,...n.children.map(text)].join(' ');
const all=n=>[n,...n.children.flatMap(all)];
const context=vm.createContext({assert,document,URL,root,text,all});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'UTC'};frame={};voting();assert.match(text(root),/unavailable/);
const person={name:'Juniper',agent:'opencode',id:'resident-abc'};
frame={voting:{inbox_checked_at:100,choices:[{id:'round',status:'open',owner:person,opened_sequence:7,selection_version:2,
  candidates:[{id:'idea',title:'New thing',author:person,milestone:'Try it',seconds:86400}],
  votes:[{resident:person,idea:'idea',counted:false,reason:'<img src=x onerror=alert(1)>',sequence:8,at:100}]}],
  proposals:[{id:'rule',title:'Better waking',mode:'wake-prompt',author:person,status:'pending',stale:true,
    reason:'Lived experience',text:'Exact wording',trial:null,endorsements:[],notice:null}]}};
voting();assert.match(text(root),/Juniper · OpenCode → New thing/);
assert.equal(all(root).find(n=>n.id==='vote-choice-round').attrs.tabindex,'-1');
assert.equal(all(root).find(n=>n.id==='vote-rule-rule').attrs.tabindex,'-1');
assert(text(root).includes("Open · 0/3 counted"));assert.match(text(root),/Not counted: author/);
assert.match(text(root),/Frozen alternatives/);assert.match(text(root),/Closed · the rules changed before it was enacted/);
for(const [closure,label] of [[{how:'delivered',by:'other'},/Closed · delivered by “Combined repair”/],
    [{how:'replaced',by:'other'},/Closed · replaced by “Combined repair”/],
    [{how:'overtaken',by:'other'},/Closed · “Combined repair” changed the same thing first/]]){
  const closed={...frame.voting.proposals[0],closure};
  frame.voting.proposals=[closed,{...closed,id:'other',title:'Combined repair',status:'enacted',stale:false,closure:undefined}];
  voting();assert.match(text(root),label);assert.doesNotMatch(text(root),/Stale base|needs a new proposal/);
}
frame.voting.proposals=[frame.voting.proposals[0]];delete frame.voting.proposals[0].closure;voting();
assert.match(text(root),/No trial recorded/);assert.match(text(root),/No public notice/);
assert.match(text(root),/Last successful inbox check recorded/);
assert.equal(all(root).filter(n=>n.tag==='img').length,0);
all(root).find(n=>n.id==='vote-choice-round').open=true;
all(root).find(n=>n.id==='vote-candidates-round').open=true;
voting();assert.equal(all(root).find(n=>n.id==='vote-choice-round').open,true);
assert.equal(all(root).find(n=>n.id==='vote-candidates-round').open,true);
frame.voting.choices[0].status='rejected';frame.voting.choices[0].votes[0].idea=null;
frame.voting.choices[0].votes[0].counted=true;
const rule=frame.voting.proposals[0];rule.stale=false;rule.status='enacted';rule.ratification='direct-owner';
rule.endorsements=[{resident:person,reason:'Checked the trial',at:101}];
rule.notice={url:'javascript:alert(1)',at:100,until:86500};
voting();assert.match(text(root),/Shortlist rejected/);assert.match(text(root),/None of these/);
assert.match(text(root),/Direct owner decision/);assert.match(text(root),/Checked the trial/);
assert.match(text(root),/Elapsed time alone does not enact/);
assert(!all(root).some(n=>String(n.href).startsWith('javascript:')));
frame.voting.choices[0].status='closed';frame.voting.choices[0].winner='idea';
voting();assert.match(text(root),/Selected: New thing/);
frame={voting:{choices:[],proposals:[],inbox_checked_at:null}};voting();
assert.doesNotMatch(text(root),/Juniper|Better waking|Checked the trial|New thing/);
assert.match(text(root),/No project ballots/);assert.match(text(root),/No successful inbox/);
`,context);
"""
        result = subprocess.run([shutil.which("node"), "-e", script,
            str(Path(__file__).parents[1] / "site/house.js")], capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_great_work_choice_renders_slot_stages_and_v3_rule_copy(self):
        script = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.attrs={};}
  setAttribute(name,value){this.attrs[name]=String(value);}
  appendChild(node){this.children.push(node);}
  replaceChildren(){this.children=[];}
  querySelectorAll(selector){return this.children.flatMap(n=>[n,...n.querySelectorAll(selector)]).filter(n=>n.tag==='details'&&(selector!=='details[open]'||n.open));}
}
const root=new Element('section'),document={getElementById:()=>root,createElement:tag=>new Element(tag)};
const text=n=>[n.textContent,...n.children.map(text)].join(' ');
const context=vm.createContext({assert,document,URL,root,text});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'UTC'};
const person={name:'Fable',agent:'opencode',id:'resident-fable'};
frame={voting:{inbox_checked_at:100,choices:[{
  id:'great-round-1',status:'open',slot:'great',owner:person,opened_sequence:7560,selection_version:3,
  candidates:[{id:'obs',title:'Observatory',author:person,milestone:'Stage one',seconds:259200,
    stages:[{milestone:'Stage one',seconds:86400},{milestone:'Stage two',seconds:172800}]}],
  votes:[]
}],proposals:[]}};
voting();
const rendered=text(root);
assert.equal(root.querySelectorAll('details').find(n=>n.id==='vote-choice-great-round-1').attrs.tabindex,'-1');
assert.match(rendered,/Great work choice · Open · 0\\/3 counted votes/);
assert.match(rendered,/2–8 ordered milestones/);
assert.doesNotMatch(rendered,/Historical selection rule/);
assert.match(rendered,/2 ordered milestones/);
assert.match(rendered,/Stage one · 1 day/);
assert.match(rendered,/Stage two · 2 days/);
`,context);
"""
        result = subprocess.run([shutil.which("node"), "-e", script,
            str(Path(__file__).parents[1] / "site/house.js")], capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)
