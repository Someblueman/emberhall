"""Project completion receipts remain visible while the next stage is active."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.textContent='';}
 appendChild(n){this.children.push(n);return n;} replaceChildren(){this.children=[];}
 setAttribute(k,v){this[k]=v;} addEventListener(k,fn){this.listeners[k]=fn;}
 focus(){document.activeElement=this;} scrollIntoView(){}
}
const all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' ');
const root=new Element('div'),growth=new Element('div');
const document={createElement:t=>new Element(t),activeElement:null,
 getElementById:id=>id==='recent-growth'?growth:[...all(root),...all(growth)].find(n=>n.id===id)||null};
const ctx=vm.createContext({assert,document,root,growth,all,text,Intl});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),ctx);
vm.runInContext(`
const get=id=>document.getElementById(id);
const plan=[{milestone:'Find a direction.'},{milestone:'Prove the result.'},{milestone:'Publish the argument.'}];
const project={id:'five',title:'Five Marks',status:'active',stage:0,milestones:plan,completed:[]};
const first={stage:0,milestone:plan[0].milestone,sequence:12};
const second={stage:1,milestone:plan[1].milestone,sequence:14};
const final={stage:2,milestone:plan[2].milestone,sequence:16};
const moment=(seq,p)=>({seq,at:50000+seq,rooms:[],tasks:[],event:{op:'shelf'},shelf:{projects:p?[p]:[]}});
const frames=[moment(10,null),moment(11,project),moment(12,{...project,stage:1,completed:[first]}),
 moment(13,{...project,stage:1,completed:[first],extended:true,deadline:90000}),
 moment(14,{...project,stage:2,completed:[first,second]}),
 moment(15,{...project,stage:2,completed:[first,second],title:'Revised title'}),
 moment(16,{...project,status:'done',stage:2,completed:[first,second,final]})];
data={frames,observed_at:50016,timezone:'UTC'};index=6;frame=frames[index];current=true;
const show=()=>{root.replaceChildren();renderCatchupPanel(root);};
`,ctx);
'''


@unittest.skipUnless(shutil.which('node'), 'Node executes the renderer')
class ProjectMilestoneChangesTests(unittest.TestCase):
    def run_renderer(self, checks):
        result = subprocess.run(
            ['node', '-e', HARNESS + '\nvm.runInContext(' + repr(checks) + ',ctx);',
             str(ROOT / 'site/house.js')], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_stages_final_receipt_unchanged_frames_and_legacy(self):
        self.run_renderer(r'''
const before=JSON.stringify(frames),digest=buildCatchupDigest(frames,6,10);
assert.deepEqual(digest.projects.map(p=>p.seq),[11,12,14,16]);
assert.match(digest.projects[1].verb,/Stage 1 of 3 completed/);
assert.equal(digest.projects[2].milestone,'Prove the result.');
assert.match(digest.projects[3].verb,/Final stage 3 of 3 completed/);
const changes=recentGrowth(frames,6,50016).filter(c=>c.kind==='project');
assert.deepEqual(changes.map(c=>c.seq),[16,14,12,11]);
assert.equal(changes.filter(c=>c.seq===16).length,1);
const legacy={id:'old',title:'Old project',status:'active'};
assert.equal(projectProgressChanges(null,legacy,1)[0].verb,'Project started');
assert.equal(projectProgressChanges(legacy,{...legacy,status:'done'},2)[0].verb,'Milestone completed');
assert.equal(projectProgressChanges(legacy,{...legacy,status:'dropped'},2)[0].verb,'Project dropped');
assert.equal(JSON.stringify(frames),before);
''')

    def test_ranges_time_boundaries_and_receipts_not_stage_guesses(self):
        self.run_renderer(r'''
assert.deepEqual(buildCatchupDigest(frames,3,12).projects.map(p=>p.seq),[12]);
assert.deepEqual(buildCatchupDigest(frames,4,13).projects.map(p=>p.seq),[14]);
assert.equal(buildCatchupDigest(frames,3,13).projects.length,0);
assert.deepEqual(recentGrowth(frames,3,50013).map(p=>p.seq),[12,11]);
assert.equal(recentGrowth(frames,6,50016+43201).length,0);
assert.deepEqual(recentGrowth(frames,6,50016+43200).map(p=>p.seq),[16]);
// A changed stage number alone, renamed text or a deadline is no completion receipt.
assert.equal(projectProgressChanges(project,{...project,stage:1,deadline:99999},12).length,0);
const stale={...project,completed:[first]};
assert.equal(projectProgressChanges(project,stale,13).length,0);
assert.equal(projectProgressChanges(stale,stale,12).length,0);
const malformed={...project,completed:[{...first,sequence:12,stage:99},{...first,stage:-1},{...first,stage:'0'}]};
assert.equal(projectProgressChanges(project,malformed,12).length,0);
''')

    def test_rendered_progress_exact_jump_history_and_literal_text(self):
        self.run_renderer(r'''
catchupStartSeq=12;show();assert.match(text(root),/Project progress/);
assert.match(text(root),/Stage 2 of 3 completed: Five Marks/);
assert.match(text(root),/Prove the result/);
render=()=>{frame=data.frames[index];show();renderRecentGrowth();};
get('catchup-jump-2-14-1').listeners.click();
assert.equal(frame.seq,14);assert.equal(current,false);
assert.equal(document.activeElement,get('catchup-list-2'));
assert.match(text(root),/Stage 2 of 3 completed/);assert.doesNotMatch(text(root),/Final stage|Publish the argument/);
renderRecentGrowth();assert.match(text(growth),/Stage 2 of 3 completed: Five Marks/);
const growthButton=all(growth).find(n=>n.tag==='button');growthButton.listeners.click();assert.equal(frame.seq,14);
assert.equal(document.activeElement,get(growthButton.id));assert.notEqual(document.activeElement,growthButton);
frames[4].shelf.projects[0]={...frames[4].shelf.projects[0],title:'<img src=x>',
 completed:[first,{...second,milestone:'<script>literal</script>'}]};
show();assert.match(text(root),/<script>literal/);assert.match(text(root),/<img src=x>/);
assert(!all(root).some(n=>n.tag==='script'||n.tag==='img'));
''')


if __name__ == '__main__':
    unittest.main()
