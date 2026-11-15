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
'''


class LivingHouseTests(unittest.TestCase):
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
