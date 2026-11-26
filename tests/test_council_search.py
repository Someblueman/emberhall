"""Run the actual voting renderer with a working Council Find filter."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site/house.js"
HARNESS = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
class Element {
  constructor(tag,id=''){this.tag=tag;this.id=id;this.children=[];this.textContent='';this.className='';this.value='';this.attrs={};this.listeners={};this.dataset={};this.style={};this.classList={toggle(){},add(){},remove(){}};}
  appendChild(node){this.children.push(node);return node;}
  replaceChildren(){if(all(this).includes(document.activeElement))document.activeElement=document.body;this.children=[];}
  setAttribute(k,v){this.attrs[k]=String(v);if(k==='id')this.id=v;}
  addEventListener(name,fn){(this.listeners[name]??=[]).push(fn);}
  dispatch(name){for(const fn of (this.listeners[name]||[])) fn();}
  focus(){document.activeElement=this;}
  setSelectionRange(start,end,direction){this.selectionStart=start;this.selectionEnd=end;this.selectionDirection=direction;}
  querySelectorAll(selector){return this.children.flatMap(n=>[n,...n.querySelectorAll(selector)]).filter(n=>n.tag==='details'&&(selector!=='details[open]'||n.open));}
}
const root=new Element('section','voting');
const nodes={voting:root};
const document={
  body:new Element('body'),
  activeElement:null,
  getElementById(id){
    const found=all(root).find(n=>n.id===id);
    if(found)return found;
    if(id.startsWith('voting-'))return null;
    return nodes[id]||(nodes[id]=new Element('div',id));
  },
  createElement:tag=>new Element(tag),
  createElementNS:(_ns,tag)=>new Element(tag)
};
const byId=id=>all(root).find(n=>n.id===id);
const context=vm.createContext({assert,document,URL,root,text,all,byId});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
"""


@unittest.skipUnless(shutil.which("node"), "Node is needed for the actual renderer")
class CouncilSearchTests(unittest.TestCase):
    def run_renderer(self, code):
        script = HARNESS + "\nvm.runInContext(" + json.dumps(code) + ",context);"
        result = subprocess.run(
            [shutil.which("node"), "-e", script, str(SOURCE)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_find_filters_choices_and_proposals(self):
        self.run_renderer(r"""
data={timezone:'UTC'};
const mara={name:'Mara',agent:'codex',id:'resident-mara'};
const juniper={name:'Juniper',agent:'opencode',id:'resident-juniper'};
frame={voting:{inbox_checked_at:100,
  choices:[
    {id:'choice-alpha',status:'open',owner:juniper,opened_sequence:7,selection_version:2,
     candidates:[{id:'idea-alpha',title:'Lantern garden',author:mara,milestone:'Try it',seconds:86400}],
     votes:[{resident:juniper,idea:'idea-alpha',counted:true,reason:'Warm and useful',sequence:8,at:100}]},
    {id:'choice-beta',status:'closed',owner:mara,opened_sequence:9,selection_version:2,winner:'idea-beta',
     candidates:[{id:'idea-beta',title:'Observatory lens',author:juniper,milestone:'Build it',seconds:172800}],
     votes:[{resident:mara,idea:'idea-beta',counted:true,reason:'Seen years ahead',sequence:10,at:110}]}
  ],
  proposals:[
    {id:'rule-waking',title:'Better waking',mode:'wake-prompt',author:juniper,status:'pending',stale:false,
     reason:'Lived experience',text:'Exact wording',trial:null,endorsements:[],notice:null},
    {id:'rule-bell',title:'Bell at dusk',mode:'rule',author:mara,status:'pending',stale:false,
     reason:'Quiet hours',text:'Soft wording',trial:null,endorsements:[],notice:null}
  ]}};
votingState.query='';
voting();
let rendered=text(root);
assert.match(rendered,/2 of 2 choices/);
assert.match(rendered,/2 of 2 proposals/);
assert.match(rendered,/Find a choice or proposal/);
assert.match(rendered,/Lantern garden/);assert.match(rendered,/Observatory lens/);
assert.match(rendered,/Better waking/);assert.match(rendered,/Bell at dusk/);
assert(byId('voting-search'));assert(byId('voting-clear'));
assert.equal(byId('voting-clear').disabled,true);
// open one card, then search: open state survives filtering and Clear search
byId('vote-choice-choice-alpha').open=true;
const input=byId('voting-search');
input.value='observatory';
input.dispatch('input');
rendered=text(root);
assert.match(rendered,/1 of 2 choices/);
assert.match(rendered,/0 of 2 proposals/);
assert.match(rendered,/Observatory lens/);
assert.doesNotMatch(rendered,/Lantern garden/);
assert.match(rendered,/No proposals match this search/);
assert.equal(byId('voting-clear').disabled,false);
// clear restores all and preserves choice-alpha open state
byId('voting-clear').dispatch('click');
rendered=text(root);
assert.match(rendered,/2 of 2 choices/);
assert.match(rendered,/2 of 2 proposals/);
assert.match(rendered,/Lantern garden/);assert.match(rendered,/Bell at dusk/);
assert.equal(byId('vote-choice-choice-alpha').open,true);
// closing a pre-opened card stays closed across filtering
byId('vote-choice-choice-beta').open=true;
voting();
assert.equal(byId('vote-choice-choice-beta').open,true);
byId('vote-choice-choice-beta').open=false;
byId('voting-search').value='observatory';
byId('voting-search').dispatch('input');
assert.equal(byId('vote-choice-choice-beta').open,false);
byId('voting-clear').dispatch('click');
assert.equal(byId('vote-choice-choice-beta').open,false);
assert.equal(byId('vote-choice-choice-alpha').open,true);
// author name narrows proposals only
byId('voting-search').value='MARA';
byId('voting-search').dispatch('input');
rendered=text(root);
assert.match(rendered,/Bell at dusk/);
assert.doesNotMatch(rendered,/Better waking/);
// nothing matches: honest note, never a bare empty heading
byId('voting-search').value='zzz-no-such-house';
byId('voting-search').dispatch('input');
rendered=text(root);
assert.match(rendered,/0 of 2 choices/);
assert.match(rendered,/0 of 2 proposals/);
assert.match(rendered,/No choices match this search/);
assert.match(rendered,/No proposals match this search/);
// votingState reset for later renders
votingState.query='';
voting();
assert.match(text(root),/2 of 2 choices/);
""")

    def test_find_by_record_id_and_case_insensitive(self):
        self.run_renderer(r"""
data={timezone:'UTC'};
const person={name:'Fable',agent:'opencode',id:'resident-fable'};
frame={voting:{inbox_checked_at:100,choices:[],proposals:[{id:'wake-brief-build-004',title:'Renew wake brief',mode:'wake-prompt',author:person,status:'pending',stale:false,reason:'Current charter',text:'Wording',trial:null,endorsements:[],notice:null}]}};
votingState.query='';
voting();
const input=byId('voting-search');
input.value='  WAKE-BRIEF-BUILD-004 ';
input.dispatch('input');
const rendered=text(root);
assert.match(rendered,/1 of 1 proposals/);
assert.match(rendered,/Renew wake brief/);
assert.match(rendered,/0 of 0 choices/);
assert.match(rendered,/No project ballots recorded/);
votingState.query='';
""")

    def test_refresh_view_preserves_voting_focus_and_selection(self):
        self.run_renderer(r"""
const mara={name:'Mara',agent:'codex',id:'resident-mara'};
frame={seq:1,at:100,event:{actor:mara.id,op:'vote'},residents:[mara],rooms:[],tasks:[],ambitions:[],runs:[],scars:[],
  voting:{inbox_checked_at:100,
    choices:[{id:'choice-beta',status:'closed',owner:mara,opened_sequence:9,selection_version:2,winner:'idea-beta',
      candidates:[{id:'idea-beta',title:'Observatory lens',author:mara,milestone:'Build it',seconds:172800}],
      votes:[{resident:mara,idea:'idea-beta',counted:true,reason:'Seen years ahead',sequence:10,at:110}]}],
    proposals:[]}};
data={timezone:'UTC',frames:[frame],commits:[],observed_at:100,journal_head:'abcdef1234567890',source_head:'1234567890abcdef'};
index=0;
floorControls=renderViewContext=drawHouse=roomPanel=dormControls=accounts=shelf=renderCollection=renderResidentPulse=renderRecentGrowth=renderLately=lighting=()=>{};
votingState.query='';
voting();
const input=byId('voting-search');
input.focus();
input.value='observatory';
input.dispatch('input');
input.setSelectionRange(2,5,'backward');
refreshView(true);
const replacement=byId('voting-search');
assert.notEqual(replacement,input);
assert.equal(document.activeElement,replacement);
assert.equal(replacement.value,'observatory');
assert.equal(replacement.selectionStart,2);
assert.equal(replacement.selectionEnd,5);
assert.equal(replacement.selectionDirection,'backward');
const clearBtn=byId('voting-clear');
clearBtn.focus();
refreshView(true);
const nextClear=byId('voting-clear');
assert.notEqual(nextClear,clearBtn);
assert.equal(document.activeElement,nextClear);
votingState.query='';
""")

    def test_open_state_survives_full_rerender_while_filtered(self):
        self.run_renderer(r"""
data={timezone:'UTC'};
const mara={name:'Mara',agent:'codex',id:'resident-mara'};
const juniper={name:'Juniper',agent:'opencode',id:'resident-juniper'};
frame={voting:{inbox_checked_at:100,
  choices:[
    {id:'choice-alpha',status:'open',owner:juniper,opened_sequence:7,selection_version:2,
     candidates:[{id:'idea-alpha',title:'Lantern garden',author:mara,milestone:'Try it',seconds:86400}],
     votes:[{resident:juniper,idea:'idea-alpha',counted:true,reason:'Warm and useful',sequence:8,at:100}]},
    {id:'choice-beta',status:'closed',owner:mara,opened_sequence:9,selection_version:2,winner:'idea-beta',
     candidates:[{id:'idea-beta',title:'Observatory lens',author:juniper,milestone:'Build it',seconds:172800}],
     votes:[{resident:mara,idea:'idea-beta',counted:true,reason:'Seen years ahead',sequence:10,at:110}]}
  ],
  proposals:[]}};
votingState.query='';
voting();
// open alpha, filter it out, then a full re-render (minute refresh), then clear
byId('vote-choice-choice-alpha').open=true;
byId('voting-search').value='observatory';
byId('voting-search').dispatch('input');
voting();
byId('voting-clear').dispatch('click');
assert.equal(byId('vote-choice-choice-alpha').open,true);
assert.equal(byId('vote-choice-choice-beta').open,false);
votingState.query='';
""")


if __name__ == "__main__":
    unittest.main()
