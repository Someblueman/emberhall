"""Render native counters without treating missing cache reports as zero."""
from pathlib import Path
import shutil
import subprocess
import unittest


@unittest.skipUnless(shutil.which("node"), "Node executes the actual account renderer")
class AccountViewTests(unittest.TestCase):
    def test_native_counters_keep_cache_missingness_and_reporting_coverage(self):
        source = Path(__file__).resolve().parents[1] / "site/house.js"
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(){this.children=[];this.textContent='';}
  appendChild(node){this.children.push(node);}
  replaceChildren(){this.children=[];}
}
const box=new Element(),document={getElementById:()=>box,createElement:()=>new Element()};
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(refresh,60000);\n';
assert(source.endsWith(tail));
const ctx=vm.createContext({document,assert});
vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
frame={budgets:[],runs:[
  {agent:'codex',sequence:10,outcome:'failed',elapsed_seconds:60,
   assignment:{lane:'work',reason:'requested-provider',requested_agent:'codex',help_request:'build-a'},
   finished_tasks:[{task:'artifact-a',sequence:11}],
   waiting:{mailbox_seconds:40,voluntary_seconds:30,measured_requests:2,unmeasured_requests:1},
   usage:{input_tokens:169087031,cached_input_tokens:165094912,output_tokens:414580}},
  {agent:'codex',usage:{}},
  {agent:'codex',elapsed_seconds:30,usage:{input_tokens:100,cached_input_tokens:0}},
  {agent:'opencode',elapsed_seconds:60,usage:{input_tokens:1705670,cached_input_tokens:34465408}},
  {agent:'muse',usage:{input_tokens:100}},
  {agent:'agy',usage:{input_tokens:2367488,cached_input_tokens:24971031,output_tokens:216420,total_tokens:2583908}}
]};
accounts();
`,ctx);
const rows=()=>box.children.map(row=>row.children.map(child=>child.textContent));
const text=(label,n,count)=>`${label}: ${n.toLocaleString()} · ${count} reporting runs`;
let rendered=rows();
assert(rendered[0].includes(text('Native input',169087131,2)));
assert(rendered[0].includes(text('Cached input',165094912,2))); // zero is a report
assert(rendered[0].includes(text('Native output',414580,1)));
assert(!rendered[0].some(s=>s.startsWith('Native total'))); // never synthesize totals
assert(rendered[1].includes(text('Cached input',34465408,1))); // may exceed native input
assert(rendered[2].includes('Cached input: unreported'));
assert(rendered[3].includes(text('Native total',2583908,1))); // retain provider's total
assert(rendered.every(row=>row.includes('Remaining unknown')));
assert(rendered[0].includes('0 successful exits · 1 failed · 0 interrupted · 0 quota'));
assert(rendered[0].includes('1 finished task receipts · 1 runs with a finish'));
assert(rendered[0].includes('1 work assignments · 0 review assignments · 0 explore assignments · 2 unrecorded'));
assert(rendered[0].includes('1 measured mailbox min (1 explicit wait min included) · 1 runs'));
assert(rendered[0].includes('2 runs without measured waiting · 1 observed requests without timing'));
const all=n=>[n.textContent,...n.children.flatMap(all)];
assert(all(box).some(s=>s.includes('Explicit provider request (Codex)')));
assert(all(box).includes('Request: build-a'));
assert(all(box).includes('Finished artifact-a · event 11'));
assert(rendered[2].includes('Mailbox waiting: unreported'));
vm.runInContext('frame={budgets:[],runs:[]};accounts();',ctx);
assert.equal(box.children.length,4); // history navigation clears later counters
assert(rows().every(row=>row.includes('Cached input: unreported')));
assert(!rows().flat().some(s=>s.startsWith('Native input')));
'''
        result = subprocess.run([shutil.which("node"), "-e", script, str(source)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
