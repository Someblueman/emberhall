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
  {agent:'codex',elapsed_seconds:60,usage:{input_tokens:169087031,cached_input_tokens:165094912,output_tokens:414580}},
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
vm.runInContext('frame={budgets:[],runs:[]};accounts();',ctx);
assert.equal(box.children.length,4); // history navigation clears later counters
assert(rows().every(row=>row.includes('Cached input: unreported')));
assert(!rows().flat().some(s=>s.startsWith('Native input')));
'''
        result = subprocess.run([shutil.which("node"), "-e", script, str(source)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
