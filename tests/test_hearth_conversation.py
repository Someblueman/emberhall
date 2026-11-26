"""Run the public Hearth's renderer, handlers and historical boundary in Node."""
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
  querySelector:()=>root,getElementById:id=>all(root).find(n=>n.id===id)||null};
const ctx=vm.createContext({assert,document,console,Intl,Date,Math,root,all,text});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
const get=id=>document.getElementById(id);
const articles=()=>all(root).filter(n=>n.tag==='article');
const show=()=>{root.replaceChildren();renderHearth(root);};
const search=value=>{get('hearth-search').value=value;get('hearth-search').listeners.input();};
const voice=n=>({seq:n,at:1000+n,resident:'r'+n,name:'Resident '+n,text:'Message '+n});
const voices=Array.from({length:13},(_,i)=>voice(i+1));
data={timezone:'UTC',frames:voices.map((v,i)=>({seq:v.seq,at:v.at,hearth:voices.slice(Math.max(0,i-2),i+1)}))};
frame=data.frames.at(-1);index=12;current=true;
observationTime=()=>frame.at;
`,ctx);
'''


@unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
class HearthConversationTests(unittest.TestCase):
    def run_renderer(self, script):
        result = subprocess.run(
            ["node", "-e", HARNESS + "\nvm.runInContext(" + repr(script) + ",ctx);", str(ROOT / "site/house.js")],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_reunites_public_messages_without_duplicates_and_pages_with_focus(self):
        self.run_renderer(r'''
const before=JSON.stringify(data);show();
assert.equal(articles().length,4);assert.match(text(articles()[0]),/Message 13/);
assert.match(text(get('hearth-results')),/13 of 13 public messages · 1–4/);
assert(get('hearth-newer').disabled);
get('hearth-older').listeners.click();assert.match(text(articles()[0]),/Message 9/);
assert.equal(document.activeElement,get('hearth-messages'));assert(get('hearth-messages').scrolled);
get('hearth-older').listeners.click();get('hearth-older').listeners.click();
assert.equal(articles().length,1);assert.match(text(articles()[0]),/Message 1/);
assert(get('hearth-older').disabled);get('hearth-newer').listeners.click();
assert.equal(articles().length,4);assert.equal(JSON.stringify(data),before);
''')

    def test_search_names_words_clear_and_literal_text(self):
        self.run_renderer(r'''
voices[0].name='<img src=x>';voices[0].text='<script>alert(1)</script>\nGolden thread';show();
const input=get('hearth-search');input.focus();
for(const query of [' GOLDEN   THREAD ','<IMG SRC=X>']) {
  search(query);assert.equal(articles().length,1);assert.match(text(root),/<script>alert\(1\)<\/script>/);
  assert.equal(get('hearth-search'),input);assert.equal(document.activeElement,input);
}
assert(!all(root).some(n=>['script','img'].includes(n.tag)));
search('absent');assert.equal(articles().length,0);assert.match(text(root),/No messages match/);
get('hearth-clear').listeners.click();assert.equal(input.value,'');assert(get('hearth-clear').disabled);
assert.equal(articles().length,4);assert.equal(document.activeElement,input);
assert.equal(get('hearth-results').attrs.role,'status');
assert.equal(get('hearth-search').attrs['aria-describedby'],'hearth-results');
assert(all(root).some(n=>n.tag==='label'&&n.htmlFor==='hearth-search'));
assert.equal(get('hearth-older').attrs['aria-controls'],'hearth-messages');
''')

    def test_historical_boundary_missing_receipt_and_event_visit(self):
        self.run_renderer(r'''
frame=data.frames[4];index=4;current=false;
frame.hearth.push(voice(99));show();
assert.match(text(root),/through event 5 · later messages hidden/);
assert.match(text(get('hearth-results')),/5 of 5/);assert.doesNotMatch(text(root),/Message 99|Message 13/);
search('Message 1');assert.equal(articles().length,1);
render=()=>{frame=data.frames[index];show();};
get('hearth-visit-1').listeners.click();
assert.equal(index,0);assert.equal(current,false);assert.equal(frame.seq,1);
assert.equal(document.activeElement,get('hearth-message-1'));assert(get('hearth-message-1').scrolled);
data.frames=[{seq:5,at:1005,hearth:[voice(1)]}];frame=data.frames[0];hearthState.query='';show();
assert.equal(articles().length,1);assert(!get('hearth-visit-1'));
assert.match(text(root),/moment is not available/);
''')

    def test_refresh_preserves_search_selection_page_focus_and_new_public_words(self):
        self.run_renderer(r'''
show();get('hearth-older').listeners.click();
roomPanel=show;lighting=accounts=drawHouse=renderViewContext=renderCollection=renderRecentGrowth=renderLately=()=>{};
get('hearth-messages').focus();refreshView();
assert.equal(hearthState.page,1);assert.equal(document.activeElement,get('hearth-messages'));
search('Message 1');get('hearth-search').focus();get('hearth-search').setSelectionRange(1,4,'backward');
refreshView();assert.equal(document.activeElement,get('hearth-search'));
assert.equal(get('hearth-search').value,'Message 1');assert.equal(get('hearth-search').selectionStart,1);
assert.equal(get('hearth-search').selectionEnd,4);assert.equal(get('hearth-search').selectionDirection,'backward');
frame={seq:14,at:1014,hearth:[voice(14)]};data.frames.push(frame);refreshView();
assert.match(text(get('hearth-results')),/6 of 14/);
get('hearth-clear').listeners.click();hearthState.page=99;frame=data.frames[0];current=false;show();
assert.equal(hearthState.page,0);assert.equal(articles().length,1);
''')

    def test_legacy_private_and_empty_snapshots_do_not_invent_words(self):
        self.run_renderer(r'''
frame={seq:0};current=false;show();assert.match(text(root),/not what they said/);
assert.equal(articles().length,0);assert(!get('hearth-search'));
data.frames=[];frame.hearth=[];show();assert.match(text(root),/private journal/);
assert.equal(articles().length,0);
frame.hearth=[{name:'No receipt',text:'Kept words',at:1}];show();
assert.equal(articles().length,1);assert.match(text(root),/Kept words/);
assert(!all(root).some(n=>(n.id||'').startsWith('hearth-visit-')));
''')

    def test_speaker_identity_combines_with_search_and_distinguishes_names(self):
        self.run_renderer(r'''
voices.forEach((v,i)=>{v.resident=i%2?'aster':'fern';v.name=i%2?'Aster':'Fern';v.text='A warm ember '+v.seq;});
voices[1].name='Earlier name';voices[0].name='Aster'; // Another person shares the name.
show();
const picker=get('hearth-speaker'),options=()=>all(picker).filter(n=>n.tag==='option');
const select=value=>{picker.focus();picker.value=value;picker.listeners.change();};
assert.equal(options().length,3);assert.equal(options()[0].textContent,'All speakers');
assert.match(options().find(n=>n.value==='resident:aster').textContent,/Aster.*Earlier name/);
assert.match(options().find(n=>n.value==='resident:fern').textContent,/Fern/);
assert(all(root).some(n=>n.tag==='label'&&n.htmlFor==='hearth-speaker'));
assert.equal(picker.attrs['aria-controls'],'hearth-messages');
get('hearth-older').listeners.click();select('resident:aster');
assert.equal(hearthState.page,0);assert.equal(document.activeElement,picker);
assert.match(text(get('hearth-results')),/6 of 13/);
assert(articles().every(n=>!text(n).includes('Fern')));
search('ember 2');assert.equal(articles().length,1);assert.match(text(root),/Earlier name/);
get('hearth-clear').listeners.click();assert.equal(hearthState.speaker,'resident:aster');
assert.match(text(get('hearth-results')),/6 of 13/);
select('');assert.match(text(get('hearth-results')),/13 of 13/);
// Matching names still identify different people; legacy words remain a separate, honest group.
voices.forEach(v=>v.name='<img src=x>');delete voices[0].resident;show();
const named=all(get('hearth-speaker')).filter(n=>n.tag==='option').slice(1);
assert.equal(named.length,3);assert.equal(new Set(named.map(n=>n.textContent)).size,3);
assert(!all(root).some(n=>n.tag==='img'));
get('hearth-speaker').value='name:<img src=x>';get('hearth-speaker').listeners.change();
assert.equal(articles().length,1);assert.match(text(articles()[0]),/ember 1/);
''')

    def test_speaker_survives_refresh_detour_and_absence_without_future_names(self):
        self.run_renderer(r'''
show();get('hearth-speaker').value='resident:r12';get('hearth-speaker').listeners.change();
roomPanel=show;lighting=accounts=drawHouse=renderViewContext=renderCollection=renderRecentGrowth=renderLately=()=>{};
get('hearth-speaker').focus();refreshView();
assert.equal(document.activeElement,get('hearth-speaker'));assert.equal(get('hearth-speaker').value,'resident:r12');
render=()=>{frame=data.frames[index];show();};choose=()=>{};
get('hearth-visit-12').listeners.click();assert.equal(hearthTrail.state.speaker,'resident:r12');
get('hearth-speaker').value='resident:r1';get('hearth-speaker').listeners.change();
get('hearth-return').listeners.click();assert.equal(frame.seq,13);
assert.equal(hearthState.speaker,'resident:r12');assert.equal(get('hearth-speaker').value,'resident:r12');
// Earlier moments retain the filter but neither expose later names nor silently widen it.
frame=data.frames[4];index=4;current=false;show();
assert.equal(articles().length,0);assert.equal(get('hearth-speaker').value,'resident:r12');
assert.match(text(root),/Selected speaker has no messages at this moment/);
assert.doesNotMatch(text(root),/Resident 12|Resident 13/);
assert.equal(all(get('hearth-speaker')).filter(n=>n.tag==='option').length,7);
get('hearth-speaker').value='';get('hearth-speaker').listeners.change();
assert.match(text(get('hearth-results')),/5 of 5/);assert.equal(articles().length,4);
frame=data.frames[12];index=12;current=true;show();
assert.equal(get('hearth-speaker').value,'');
''')

    def test_return_restores_original_conversation_after_nested_visits_and_refresh(self):
        self.run_renderer(r'''
const before=JSON.stringify(data);let chosen=null;
choose=room=>{chosen=room;};render=()=>{frame=data.frames[index];show();};
show();get('hearth-visit-13').listeners.click();assert(!get('hearth-return'));
search('Message');get('hearth-older').listeners.click();
get('hearth-visit-8').listeners.click();
assert.equal(frame.seq,8);assert.equal(hearthState.page,0);
assert.doesNotMatch(text(root),/Message 9|Message 13/);
assert.match(text(get('hearth-return')),/Back to conversation/);
get('hearth-visit-6').listeners.click();assert.equal(frame.seq,6);
assert.equal(hearthTrail.sequence,13);assert.equal(hearthTrail.state.page,1);
search('Message 1'); // Edits made during the detour do not replace the saved search.
get('hearth-return').focus();refreshView(true);
assert.equal(document.activeElement,get('hearth-return'));
get('hearth-return').listeners.click();
assert.equal(frame.seq,13);assert.equal(index,12);assert.equal(current,true);
assert.equal(chosen,'hearth');assert.equal(hearthState.page,1);assert.equal(hearthState.query,'Message');
assert.equal(document.activeElement,get('hearth-visit-8'));assert(get('hearth-visit-8').scrolled);
assert(!get('hearth-return'));assert.equal(hearthTrail,null);assert.equal(JSON.stringify(data),before);
// A later publication must not silently move the original latest conversation forward.
get('hearth-visit-8').listeners.click();data.frames.push({seq:99,at:1099,hearth:[voice(99)]});
show();get('hearth-return').listeners.click();assert.equal(frame.seq,13);assert.equal(current,false);
assert.doesNotMatch(text(root),/Message 99/);
// A historical origin stays historical even if it is the last frame in a replacement publication.
get('hearth-visit-8').listeners.click();data.frames.pop();show();get('hearth-return').listeners.click();
assert.equal(current,false);assert.equal(hearthState.page,1);
''')

    def test_return_handles_missing_origin_and_legacy_destination(self):
        self.run_renderer(r'''
render=()=>{frame=data.frames[index];show();};choose=()=>{};
show();get('hearth-visit-12').listeners.click();
// The return remains available when an older destination has no public words.
delete frame.hearth;data.frames=data.frames.slice(11);show();
assert(get('hearth-return'));assert.match(text(root),/not what they said/);
get('hearth-return').listeners.click();assert.equal(frame.seq,13);
assert.equal(document.activeElement,get('hearth-visit-12'));
get('hearth-visit-12').listeners.click();data.frames=data.frames.filter(f=>f.seq!==13);show();
assert(!get('hearth-return'));assert.match(text(root),/original moment is absent/);
assert.equal(frame.seq,12);assert.equal(current,false);
''')
