"""Use genuine exported frames, lifecycle transitions and publisher output."""
import base64
import hashlib
import json
from html.parser import HTMLParser
import shutil
import unittest
from urllib.parse import urlsplit

from house.body import export
from house.home_work import git
from house.public_history import decode
from house.publish import BRANCH, publish
from tests.support import HouseCase
from tests.test_workshop_ui import ROOT, RendererMixin


@unittest.skipUnless(shutil.which("node"), "Node executes the actual renderer")
class WorkshopHistoryTests(RendererMixin, HouseCase):
    def test_real_243_event_history_creation_finish_and_keyboard_navigation(self):
        fixture = decode(json.loads((ROOT / "site/history.json").read_text()))
        self.run_renderer(r'''
data=fixture;data.frames.forEach(f=>{f.scars=f.scars.map(s=>({...data.scars[s.id],...s}));});
index=data.frames.length-1;frame=data.frames[index];current=true;roomPanel();
const model=workshopTasks(data.frames,frame,frame.at);
const witness=model.find(t=>t.id==='witness-review');
assert.equal(witness.title,'Keep the founding boundary and verify Blackout repairs');
assert.deepEqual(witness.events.map(e=>e.seq),[6,8,17]);
assert.deepEqual(witness.events.map(e=>e.label),['Created','Claimed','Finished']);
assert.equal(witness.state,'done');
// Default view is bounded, and every unfinished task remains in the first groups.
assert(cards().length<=4*4);assert.match(text(panel()),/Recent finishes/);
workshopState.selectedId='witness-review';roomPanel();
assert.equal(events().length,3);
assert.match(text(events()[0]),/Created · Witness · 13 Nov/);
assert.doesNotMatch(text(events()[0]),/179452/);
assert.doesNotMatch(text(panel()),/unreviewed/);
// Use the real renderer and its existing house/history controls on each jump.
events()[1].click();assert.equal(frame.seq,8);assert.equal(index,7);assert.equal(current,false);
assert.equal($('history').value,8);assert.equal(workshopState.selectedId,'witness-review');
assert.equal(events().length,2);assert.doesNotMatch(text($('workshop-detail')),/Finished/);
assert.equal(document.activeElement.id,'workshop-detail');
$('workshop-present').click();assert.equal(frame.seq,data.frames[data.frames.length-1].seq);assert.equal(index,data.frames.length-1);assert.equal(current,true);
assert.equal(events().length,3);assert.equal(document.activeElement.id,'workshop-detail');
jumpToSequence(5);assert.match(text($('workshop-detail')),/Selected task not yet recorded/);
assert.doesNotMatch(text($('workshop-detail')),/Blackout|Witness|event 17/);
''', fixture)

    def test_real_journal_renew_release_and_readiness_annotation(self):
        self.record.append("task", "alice", {
            "task": "work", "title": "Readable title, not an ID",
            "description": "PRIVATE-DESCRIPTION", "ready": True,
        })
        self.record.append("claim", "alice", {
            "task": "work", "expect": 0, "token": "PRIVATE-TOKEN", "seconds": 120,
        })
        self.record.append("renew", "alice", {
            "task": "work", "token": "PRIVATE-TOKEN", "seconds": 300,
        })
        self.record.append("release", "alice", {
            "task": "work", "token": "PRIVATE-TOKEN", "note": "Not a public handoff body",
        })
        self.record.append("ready", "bob", {"task": "work", "expect": 1, "ready": False})
        fixture = export(self.record)
        self.run_renderer(r'''
data=fixture;index=data.frames.length-1;frame=data.frames[index];current=false;roomPanel();
assert(!data.frames.some(f=>'task' in f.event));
cards()[0].click();assert.equal(events().length,5);
assert.equal(events().map(e=>e.textContent.split(' · ')[0]).join('|'),'Created|Claimed|Lease renewed|Released|Queue updated');
assert.match(text(events()[4]),/Not queued · Bob/);
assert.match(text($('workshop-detail')),/Readable title, not an ID/);
assert.doesNotMatch(text(panel()),/PRIVATE|Not a public handoff body/);
const before=workshopTasks(data.frames,data.frames[5],data.frames[5].at).find(t=>t.id==='work');
assert.equal(before.events.length,3);assert.equal(before.ready,true);
''', fixture)

    def test_finished_task_and_earlier_prefix_keep_their_recorded_scope(self):
        # A prefix exported by the real reducer: compare with the same prefix in a later export.
        self.task()
        prefix = export(self.record)
        self.record.append("claim", "alice", {"task": "work", "expect": 0, "token": "x", "seconds": 120})
        body = b"Immutable fixture"
        self.record.append("finish", "alice", {"task": "work", "token": "x", "result": "PRIVATE-RESULT",
            "artifacts": {"a.txt": {"sha256": hashlib.sha256(body).hexdigest(),
                                     "base64": base64.b64encode(body).decode()}}})
        fixture = export(self.record)
        fixture["earlier_frames"] = prefix["frames"]
        self.run_renderer(r'''
const end=fixture.earlier_frames.at(-1);
assert.deepEqual(workshopTasks(fixture.frames,end,end.at),workshopTasks(fixture.earlier_frames,end,end.at));
data=fixture;frame=fixture.frames.at(-1);index=fixture.frames.length-1;current=false;roomPanel();
assert.match(text(panel()),/0 unfinished · 1 finished/);cards()[0].click();
assert.match(text($('workshop-detail')),/acceptance and delivery unknown/);
assert.doesNotMatch(text(panel()),/PRIVATE-RESULT|a.txt|Immutable fixture/);
''', fixture)

    def test_actual_publisher_delivers_every_local_page_asset(self):
        (self.repo / "site").mkdir()
        for name in ("index.html", "house.js", "house.css"):
            shutil.copyfile(ROOT / "site" / name, self.repo / "site" / name)
        git(self.repo, "add", "site")
        git(self.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
            "-c", "user.email=test@local", "commit", "-m", "UI publication fixture")
        publish(self.record)
        page = git(self.repo, "show", BRANCH + ":index.html")
        self.assertEqual(page, (ROOT / "site/index.html").read_text().rstrip())

        class Assets(HTMLParser):
            paths = []

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                # Inline scripts travel in the page, not as separate assets.
                if ((tag == "script" and "src" in attrs)
                        or (tag == "link" and attrs.get("rel") == "stylesheet")):
                    self.paths.append(urlsplit(attrs.get("src", attrs.get("href", ""))).path)

        parser = Assets()
        parser.feed(page)
        self.assertEqual(set(parser.paths), {"house.js", "house.css"})
        for path in parser.paths:
            self.assertEqual(git(self.repo, "show", BRANCH + ":" + path), (ROOT / "site" / path).read_text().rstrip())
        self.assertNotIn("renderWorkshopExplorer", (ROOT / "site/house.js").read_text())
        self.assertNotIn("workshop.js", page)


if __name__ == "__main__":
    unittest.main()
