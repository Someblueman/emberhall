"""The house drawing carries what the record knows: room facts, name tags and recent events."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(refresh,60000);setInterval(watch,10000);\n';
assert(source.endsWith(tail));
const context=vm.createContext({document:{getElementById:()=>null,querySelector:()=>null},Intl,Date,Math,Number,String,Set,Object,Array});
vm.runInContext(source.slice(0,-tail.length),context);
const run=code=>vm.runInContext(code,context);
run(`
const people=[{id:'a',name:'Ash',pose:'standing',room:'workshop'},{id:'b',name:'Bay',pose:'sleeping',room:'bedroom'}];
const task={id:'mend-roof',title:'Mend the roof',owner:'a',status:'claimed',until:9e9,generation:1};
const base={rooms:[],residents:people,tasks:[task],lessons:3,council:{pending:2},voting:{choices:[{status:'open'}]},
  shelf:{ideas:[{},{}],projects:[{status:'active'},{status:'done'}]}};
const moment=(seq,op,actor,title='')=>({...base,seq,at:1000+seq,event:{op,actor,title}});
data={frames:[moment(1,'wake','a'),moment(2,'claim','a','mend-roof'),moment(3,'life','watch-keeper'),
  moment(4,'say','b'),moment(5,'say','b'),moment(6,'finish','a','mend-roof')]};
index=5;frame=data.frames[5];current=false;
`);
assert.deepEqual(run(`['workshop','bedroom','council','gallery','study','archive','door'].map(roomFact)`),
  ['1 thread open','1 asleep','1 vote open','1 project being built','2 ideas on the shelf','3 lessons kept','']);
assert.equal(run(`heldWork('a')`),'Mend the roof');
assert.equal(run(`heldWork('b')`),null);
// Bookkeeping is skipped and repeated speech is folded into one line.
assert.deepEqual(run(`latelyEvents(6).map(latelySentence)`),
  ['Ash finished “Mend the roof”','Bay spoke 2 times','Ash took up “Mend the roof”','Ash woke up']);
assert.equal(run(`clip('abcdefghij',6)`),'abcde…');
// The Archive lists lessons newest first and says who checked them.
const made=[];
context.document.createElement=tag=>{const node={tag,children:[],appendChild(child){this.children.push(child);}};made.push(node);return node;};
run(`frame.archive=[{key:'old-lesson',claim:'Old.',author:'Ash',status:'superseded',reviews:0},
  {key:'check-twice',claim:'Check twice.',author:'Bay',status:'observed',reviews:2}];[...frame.archive].reverse().forEach(lesson=>lessonEntry(lesson,{appendChild(){}}));`);
const text=made.map(node=>node.textContent).filter(Boolean);
assert.deepEqual(text.slice(0,3),['check twice','Check twice.','Bay · checked by 2 other residents']);
assert(text.includes('Ash · replaced by a later lesson'));
// Public conversation deduplicates repeated snapshot messages, newest first.
assert.deepEqual(run(`hearthConversation([{seq:5,hearth:[{seq:1,text:'First.'},{seq:5,text:'Second.'}]}],
  {seq:5,hearth:[{seq:5,text:'Second.'}]}).map(v=>v.text)`),['Second.','First.']);
// The quieter rooms say what they hold, from the same record their panels show.
// A snapshot without kept words gets no invented message count.
assert.equal(run(`roomFact('hearth')`),'');
assert.equal(run(`frame.hearth=[{seq:4,text:'First.'},{seq:6,text:'Second.'}];roomFact('hearth')`),'2 public messages kept');
assert.equal(run(`frame.rooms=[{id:'door',history:[{sequence:1},{sequence:2}]},{id:'study',history:[{sequence:3}]},{id:'assay'}];roomFact('chronicle')`),'3 room entries');
// The Parlor lead counts exactly the changes its catch-up sections list.
assert.equal(run(`(()=>{const d=buildCatchupDigest(data.frames,index,catchupStartSeq);const n=d.tasks.length+d.rooms.length+d.projects.length;return roomFact('parlor')===n+' changes to catch up on';})()`),true);
// Rooms with no honest record count stay blank instead of guessing.
assert.deepEqual(run(`[roomFact('door'),roomFact('salvage')]`),['','']);
// Every open room has a fallback description for moments without a recorded purpose.
assert.deepEqual(run(`['door','hearth','workshop','archive','council','bedroom','study','parlor','gallery','chronicle','counting','assay','salvage'].map(id=>typeof descriptions[id])`),
  ['string','string','string','string','string','string','string','string','string','string','string','string','string']);
'''


class LivingHouseTests(unittest.TestCase):
    def test_house_focus_names_stale_tasks_and_stalled_projects(self):
        from house.home import HOME_FOCUS, focus_prompt
        state = {"tasks": {"old": {"status": "open", "ready": False, "generation": 2, "title": "Old chore"},
                           "next": {"status": "open", "ready": True, "generation": 0, "title": "Next", "project": "busy"},
                           "done": {"status": "done", "generation": 1, "title": "Done"}},
                 "shelf": {"projects": {"busy": {"status": "active"}, "idle": {"status": "active"},
                                        "over": {"status": "done"}}},
                 "life": {"rooms": {"door": {"name": "The Door", "status": "open"}}}}
        tend = focus_prompt(state, "tend")
        self.assertIn("old (generation 2): Old chore", tend)
        self.assertIn("no ready task: idle.", tend)
        self.assertNotIn("Done", tend)
        self.assertIn("The Door (open)", focus_prompt(state, "room"))
        self.assertIn("docs/RENOVATION.md", focus_prompt(state, "improve"))
        self.assertEqual(("improve", "room", "tend", "research"), HOME_FOCUS)

    def test_builders_spread_across_projects(self):
        from unittest.mock import patch
        from house import project_work
        state = {"tasks": {"a1": {"project": "a", "generation": 0}, "b1": {"project": "b", "generation": 0},
                           "a0": {"project": "a", "generation": 0}},
                 "life": {"runs": {}, "requests": {}}}
        project = {"a": {"deadline": 10}, "b": {"deadline": 20}}
        with patch.object(project_work, "enabled", return_value=True), \
                patch.object(project_work, "available", return_value=True), \
                patch.object(project_work, "active_project", side_effect=lambda state, key, at: project[key]):
            self.assertEqual("a1", project_work.first(state, 0, ["a1", "b1"], [])["task"])
            state["life"]["runs"]["r"] = {"status": "active", "task": "a0"}
            self.assertEqual("b1", project_work.first(state, 0, ["a1", "b1"], [])["task"])

    def test_hearth_words_are_private_until_the_steward_opens_it(self):
        from house import body
        self.assertEqual("upgrade-20261115-public-hearth", body.PUBLIC_HEARTH)
        self.assertEqual([], body.replay_context()["hearth"])

    def test_speech_is_published_without_local_paths_or_addresses(self):
        from house.body import spoken
        self.assertEqual(spoken("Saved  to /Users/someone/Code/x.py, mail a.b@example.org (see /tmp/out)."),
                         "Saved to [path], mail [address] (see [path]).")
        self.assertEqual(len(spoken("word " * 400)), 600)
        self.assertTrue(spoken("word " * 400).endswith("…"))
        from house.body import voiced
        self.assertTrue(voiced("resident-ab12", "Fern finished the review."))
        self.assertFalse(voiced("resident-ab12", 'house-integration-v1 {"actor": "resident-ab12"}'))
        self.assertFalse(voiced("resident-ab12", ' {"raw": 1}'))
        self.assertFalse(voiced("keeper-01", "STEWARD DIRECTIVE"))
        self.assertFalse(voiced("watch-keeper", "note"))
        self.assertFalse(voiced("resident-ab12", None))

    @unittest.skipUnless(shutil.which("node"), "node is required")
    def test_room_facts_name_tags_and_recent_events_come_from_the_record(self):
        result = subprocess.run([shutil.which("node"), "-e", SCRIPT, str(ROOT / "site/house.js")],
                                capture_output=True, text=True, timeout=15, stdin=subprocess.DEVNULL)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_page_has_the_strip_and_keeps_reading_notes_optional(self):
        page = (ROOT / "site/index.html").read_text()
        self.assertIn('<ol id="lately" class="lately"></ol>', page)
        self.assertIn('id="presence-notes"', page)
        styles = (ROOT / "site/house.css").read_text()
        self.assertIn(".house-layout:not(.room-open)", styles)
        self.assertIn("prefers-reduced-motion", styles[styles.index("The living house"):])


if __name__ == "__main__":
    unittest.main()
