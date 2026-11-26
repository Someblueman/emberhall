"""The graveyard is a list to scan: one line per entry, newest first, reasons folded until opened."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).parents[1]

SCRIPT = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';this.attrs={};this.open=false;}
  appendChild(node){this.children.push(node);}
  replaceChildren(){this.children=[];}
  setAttribute(name,value){this.attrs[name]=String(value);}
}
const nodes={shelf:new Element('div'),finished:new Element('div')};
const document={getElementById:id=>nodes[id]||null,createElement:tag=>new Element(tag)};
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const all=node=>[node,...node.children.flatMap(all)];
const context=vm.createContext({assert,document,URL,nodes,text,all,Intl,Date,Math});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'UTC'};current=false;
const longReason='A reason that runs on for a paragraph. '.repeat(12);
frame={at:1000,seq:90,residents:[{id:'r1',name:'Juniper'}],shelf:{enabled:true,policy:'work-selection-004',house_work:true,
 ideas:[
  {id:'lost',title:'Lost twice',status:'graveyard',losses:2,scale:'great',plain:'A plain line about it.',what:'Long what text.',
   history:[{choice:'c1',won:false,sequence:10,reasons:[longReason,'Second voter.']},{choice:'c2',won:false,sequence:20,reasons:['Third voter.']}]},
  {id:'second',title:'Second look',status:'graveyard',losses:0,scale:'house',what:'Only a what.',
   history:[{seconded_out:true,by:'r1',sequence:80,lesson:'The pages did not say that.'}]},
  {id:'expired',title:'Never kept',status:'graveyard',losses:0,history:[{expired:true,sequence:50,lesson:'Nobody kept it.'}]},
  {id:'voted',title:'Voted down',status:'graveyard',losses:1,history:[{choice:'c3',won:false,rejected:true,sequence:60,lesson:'None of these.',reasons:['No.']}]},
  {id:'bare',title:'Bare',status:'graveyard',losses:0,history:[]},
  {id:'gone',title:'Gone with its project',status:'graveyard',losses:0,history:[{dropped_project:true,sequence:70,lesson:'x'}]}],
 projects:[{id:'p-drop',idea:'gone',title:'Dropped thing',status:'dropped',slot:'great',owner:'r1',lesson:'It did not earn its days.',plain:'What it was.'}]}};
shelf();
const yard=all(nodes.shelf).find(n=>n.id==='projects-retired');
assert(yard&&yard.tag==='details'&&!yard.open);
assert.equal(yard.children[0].textContent,'Graveyard (6)');
const rows=yard.children.filter(n=>n.className==='shelf-item shelf-dead');
assert.equal(rows.length,6);
// Every entry is a closed fold whose one visible line is its title and how it ended.
for(const row of rows){
  assert.equal(row.tag,'details');assert(!row.open);
  const head=row.children[0];assert.equal(head.tag,'summary');
  assert.equal(head.children.length,2);assert.equal(head.children[0].tag,'strong');
  assert(text(head).length<120,'the visible line stays short: '+text(head));
}
const headLine=row=>row.children[0].children.map(n=>n.textContent).join(' | ');
assert.equal(rows.map(headLine).join(' / '),[
  'Dropped thing | Great work · Project dropped',
  'Second look | House work · Declined on a second look',
  'Voted down | Small project · Voted down',
  'Never kept | Small project · Nobody kept it in time',
  'Lost twice | Great work · Lost 2 votes',
  'Bare | Small project · Retired before a vote'].join(' / '));
// The reasons are inside the fold; what the voters said is folded once more.
const lost=rows[4],body=lost.children.slice(1);
assert.equal(body[0].textContent,'A plain line about it.');
const votes=body.find(n=>n.className==='shelf-dead-votes');
assert(votes&&votes.tag==='details'&&!votes.open);
assert.equal(votes.children[0].textContent,'What the 3 voters said');
assert.equal(votes.children.length,4);
assert.equal(rows[1].children[1].textContent,'Only a what.');
assert.equal(rows[1].children[2].textContent,'The pages did not say that.');
assert.equal(rows[0].children[2].textContent,'It did not earn its days.');
assert.equal(rows[5].children[1].textContent,'No reason was recorded.');
// The idea whose project was dropped is listed once, as the project.
assert.doesNotMatch(text(yard),/Gone with its project/);
// Search still reaches the folded words.
assert(rows[4].attrs['data-find'].includes('second voter'));
assert(rows[1].attrs['data-find'].includes('declined on a second look'));
`,context);
'''


@unittest.skipUnless(shutil.which('node'), 'Node is needed for the actual renderer')
class GraveyardListTests(unittest.TestCase):
    def test_each_entry_is_one_line_until_opened_newest_first(self):
        result = subprocess.run(['node', '-e', SCRIPT, str(ROOT / 'site/house.js')], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr[-3000:])

    def test_the_fold_is_styled_as_a_list(self):
        css = (ROOT / 'site/house.css').read_text()
        for rule in ('.shelf-dead > summary', '.shelf-dead-how', '.shelf-dead-votes'):
            self.assertIn(rule, css)


if __name__ == '__main__':
    unittest.main()
