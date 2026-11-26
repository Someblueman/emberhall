"""Open research (Steward decision, 15 November): rounds with a full shelf, briefs, expiry."""
import copy
from pathlib import Path
import shutil
import subprocess
import unittest

from house import body, life, shelf, shelf_gate
from house.home import BRIEF_GUIDE, HOME_FOCUS, focus_prompt
from tests import test_explorer_dispatch, test_shelf

HOUR = 3600
PART = "Plain researched prose that says something specific about this idea. " * 2
BRIEF = {name: PART for name in shelf.BRIEF_FIELDS}


def briefed(key):
    return test_shelf.idea(key) | {"brief": dict(BRIEF)}


def worthy(key, field="design", worth="beautiful"):
    return test_shelf.idea(key) | {"brief": {"field": field, "worth": worth,
                                             **{name: PART for name in shelf.WORTH_FIELDS}}}


class OpenResearchTests(unittest.TestCase):
    def setUp(self):
        self.f = test_shelf.ShelfTests(); self.f.setUp()

    def open(self, at=1000):
        self.f.state["maintenance"] = {"migrations": {shelf.OPEN_RESEARCH: {"at": at}}}

    def publish(self, keys, round_id, at=None, actor="author", ideas=None):
        f = self.f
        generation = f.state.get("shelf", {}).get("generation", 0)
        f.send("explore-start", actor=actor, at=at, round=round_id, expect=generation, token=round_id, seconds=100)
        f.send("explore-publish", actor=actor, round=round_id, token=round_id,
               ideas=ideas or [briefed(k) for k in keys])

    def test_before_the_decision_nothing_changes(self):
        f = self.f
        f.publish()
        f.reject("shelf is full; build instead", "explore-start", actor="other", round="r2", expect=1,
                 token="r2", seconds=100)
        f.reject("unknown shelf action", "idea-brief", idea="a", brief=dict(BRIEF))
        before = copy.deepcopy(f.state["shelf"])
        shelf.advance(f.state, f.state["at"] + 30 * shelf.DAY, 99)
        self.assertEqual(before, f.state["shelf"])
        self.assertNotIn("research_at", before)
        self.assertNotIn("shelved_at", before["ideas"]["a"])
        self.assertNotIn("started_at", before["rounds"]["r1"])
        f.state["shelf"]["ideas"].clear()
        f.send("explore-start", actor="other", round="r3", expect=1, token="r3", seconds=100)
        f.reject("invalid idea fields", "explore-publish", actor="other", round="r3", token="r3",
                 ideas=[briefed("x"), briefed("y")])

    def test_research_continues_with_a_full_shelf_every_four_hours_up_to_the_ceiling(self):
        f = self.f
        self.open()
        self.publish("abc", "r1")
        started = f.state["shelf"]["research_at"]
        self.assertEqual(started, f.state["shelf"]["rounds"]["r1"]["started_at"])
        f.reject("started recently", "explore-start", actor="other", round="r2", expect=1, token="r2", seconds=100)
        self.assertFalse(shelf.research_open(f.state, f.state["shelf"], started + 4 * HOUR - 1, 1))
        self.assertTrue(shelf.research_open(f.state, f.state["shelf"], started + 4 * HOUR, 1))
        self.publish("defg", "r2", at=started + 4 * HOUR, actor="other")
        self.assertEqual(7, len(shelf.shelf_ids(f.state["shelf"])))
        self.publish("hij", "r3", at=started + 8 * HOUR, actor="v1")
        self.assertEqual(shelf.SHELF_CEILING, len(shelf.shelf_ids(f.state["shelf"])))
        f.reject("started recently", "explore-start", actor="v2", at=started + 20 * HOUR, round="r4", expect=3,
                 token="r4", seconds=100)

    def test_ideas_need_a_real_brief(self):
        f = self.f
        self.open()
        f.send("explore-start", round="r1", expect=0, token="r1", seconds=100)
        f.reject("needs a research brief", "explore-publish", round="r1", token="r1",
                 ideas=[test_shelf.idea("a"), test_shelf.idea("b")])
        thin = briefed("a"); thin["brief"]["risks"] = "It might not work."
        f.reject("at least 120 characters", "explore-publish", round="r1", token="r1", ideas=[thin, briefed("b")])
        partial = briefed("a"); del partial["brief"]["exists"]
        f.reject("audience, exists, first_version and risks", "explore-publish", round="r1", token="r1",
                 ideas=[partial, briefed("b")])
        f.send("explore-publish", round="r1", token="r1", ideas=[briefed("a"), briefed("b")])
        stored = f.state["shelf"]["ideas"]["a"]
        self.assertEqual({*shelf.BRIEF_FIELDS, "author", "sequence"}, set(stored["brief"]))
        self.assertEqual("author", stored["brief"]["author"])
        f.reject("not on the shelf", "idea-brief", idea="missing", brief=dict(BRIEF))
        f.send("idea-brief", actor="other", idea="a", brief={name: PART + name for name in shelf.BRIEF_FIELDS})
        self.assertEqual("other", f.state["shelf"]["ideas"]["a"]["brief"]["author"])
        self.assertIn("idea-brief", shelf_gate.ACTIONS)
        self.assertNotIn("idea-brief", shelf_gate.RESEARCH)

    def test_thin_ideas_expire_two_days_after_the_decision_unless_briefed_or_in_a_choice(self):
        f = self.f
        f.publish(("old1", "old2", "old3"))
        self.open(at=5000)
        self.assertEqual(5000 + shelf.BRIEF_SECONDS, shelf.brief_due(f.state, f.state["shelf"]["ideas"]["old1"]))
        f.send("idea-brief", actor="other", at=5100, idea="old1", brief=dict(BRIEF))
        self.assertIsNone(shelf.brief_due(f.state, f.state["shelf"]["ideas"]["old1"]))
        f.send("choice-open", actor="other", at=5200, choice="c1", milestones={
            k: {"milestone": "One usable example"} for k in ("old1", "old2", "old3")})
        late = 5000 + shelf.BRIEF_SECONDS
        f.send("choice-vote", actor="v1", at=late, choice="c1", idea="old1", reason="Researched")
        self.assertEqual("shelved", f.state["shelf"]["ideas"]["old2"]["status"])
        f.send("choice-vote", actor="v2", choice="c1", idea="old1", reason="Researched")
        f.send("choice-vote", actor="v3", choice="c1", idea="old1", reason="Researched")
        self.assertEqual("project", f.state["shelf"]["ideas"]["old1"]["status"])
        self.assertEqual("shelved", f.state["shelf"]["ideas"]["old2"]["status"])
        f.reject("not on the shelf", "idea-brief", actor="v1", idea="old3", brief=dict(BRIEF))
        f.send("idea-return", actor="v1", idea="old3", changed="A resident will research it")
        ideas = f.state["shelf"]["ideas"]
        self.assertEqual("graveyard", ideas["old2"]["status"])
        self.assertEqual({"expired": True, "lesson": shelf.EXPIRED, "sequence": f.state["sequence"]},
                         ideas["old2"]["history"][-1])
        self.assertEqual("shelved", ideas["old3"]["status"])
        f.send("idea-return", actor="v2", idea="old2", changed="Someone will research it now")
        returned = f.state["shelf"]["ideas"]["old2"]
        self.assertEqual(f.state["at"] + shelf.BRIEF_SECONDS, shelf.brief_due(f.state, returned))
        shelf.advance(f.state, f.state["at"] + shelf.BRIEF_SECONDS, 500)
        self.assertEqual("graveyard", returned["status"])

    def test_dispatch_demand_asks_the_same_question_as_the_reducer(self):
        d = test_explorer_dispatch.ExplorerDispatchTests(); d.setUp(); d.enable()
        d.h.event("life", {"kind": "identity", "agent": "codex", "model": "gpt-6.1-sol"})
        d.h.event("shelf", {"kind": "explore-start", "round": "r", "expect": 0, "token": "r", "seconds": 60})
        d.h.event("shelf", {"kind": "explore-publish", "round": "r", "token": "r",
                            "ideas": [test_shelf.idea(k) for k in "abc"]})
        state, now = copy.deepcopy(d.h.state), d.h.now
        self.assertIsNone(life.explorer_demand(state, now))
        state["maintenance"]["migrations"][shelf.OPEN_RESEARCH] = {"at": now}
        self.assertEqual(1, life.explorer_demand(state, now))
        state["shelf"]["research_at"] = now
        self.assertIsNone(life.explorer_demand(state, now + 4 * HOUR - 1))
        self.assertEqual(1, life.explorer_demand(state, now + 4 * HOUR))

    def test_public_view_shows_briefs_expiry_and_the_next_round(self):
        f = self.f
        f.publish(("thin1", "thin2"))
        self.assertNotIn("research", body.shelf_view(f.state))
        self.assertNotIn("brief_due", body.shelf_view(f.state)["ideas"][0])
        self.open(at=5000)
        self.publish("xy", "r2", at=6000, actor="other")
        view = body.shelf_view(f.state)
        ideas = {idea["id"]: idea for idea in view["ideas"]}
        self.assertEqual(5000 + shelf.BRIEF_SECONDS, ideas["thin1"]["brief_due"])
        self.assertNotIn("brief", ideas["thin1"])
        self.assertEqual({*shelf.BRIEF_FIELDS, "author"}, set(ideas["x"]["brief"]))
        self.assertEqual(" ".join(PART.split()), ideas["x"]["brief"]["audience"])
        self.assertNotIn("brief_due", ideas["x"])
        self.assertEqual({"last": 6000, "next": 6000 + 4 * HOUR, "ceiling": 10}, view["research"])
        self.assertNotIn("token", str(view))

    def test_research_focus_lists_ideas_without_a_brief(self):
        f = self.f
        f.publish(("thin1", "thin2"))
        self.open(at=f.state["at"])
        prompt = focus_prompt(f.state | {"life": {}}, "research")
        self.assertIn("thin1: thin1 (expires in 48 h)", prompt)
        self.assertIn('"kind":"idea-brief"', prompt)
        for name in shelf.BRIEF_FIELDS:
            self.assertIn(name, BRIEF_GUIDE)
        self.assertEqual(("improve", "room", "tend", "research"), HOME_FOCUS)

    def worth(self, at):
        self.f.state["maintenance"]["migrations"][shelf.WORTH_BUILDING] = {"at": at}

    def test_worth_test_binds_ideas_to_software_design_or_science(self):
        f = self.f
        self.open()
        self.publish("ab", "r1")
        old_brief = copy.deepcopy(f.state["shelf"]["ideas"]["a"]["brief"])
        self.worth(at=f.state["at"])
        f.send("explore-start", actor="other", at=f.state["at"] + 4 * HOUR, round="r2", expect=1, token="r2",
               seconds=100)
        f.reject("field, worth, benefit, interest, exists, first_version and check", "explore-publish",
                 actor="other", round="r2", token="r2", ideas=[briefed("c"), briefed("d")])
        physical = worthy("c"); physical["brief"]["field"] = "craft"
        f.reject("software, design or science", "explore-publish", actor="other", round="r2", token="r2",
                 ideas=[physical, worthy("d")])
        popular = worthy("c"); popular["brief"]["worth"] = "popular"
        f.reject("useful, beautiful or enabling", "explore-publish", actor="other", round="r2", token="r2",
                 ideas=[popular, worthy("d")])
        vague = worthy("c"); vague["brief"]["interest"] = "People might like it."
        f.reject("at least 120 characters", "explore-publish", actor="other", round="r2", token="r2",
                 ideas=[vague, worthy("d")])
        f.send("explore-publish", actor="other", round="r2", token="r2",
               ideas=[worthy("c"), worthy("d", field="science", worth="enabling")])
        ideas = f.state["shelf"]["ideas"]
        self.assertEqual({*shelf.WORTH_FIELDS, "field", "worth", "author", "sequence"}, set(ideas["d"]["brief"]))
        self.assertEqual(("science", "enabling"), (ideas["d"]["brief"]["field"], ideas["d"]["brief"]["worth"]))
        self.assertEqual(old_brief, ideas["a"]["brief"])
        self.assertIsNone(shelf.brief_due(f.state, ideas["c"]))

    def test_earlier_briefs_have_two_days_to_meet_the_worth_test(self):
        f = self.f
        f.publish(("thin", "thin2"))
        self.open(at=5000)
        self.publish("ab", "r2", at=6000, actor="other")
        ideas = f.state["shelf"]["ideas"]
        self.assertIsNone(shelf.brief_due(f.state, ideas["a"]))
        self.worth(at=9000)
        self.assertEqual(5000 + shelf.BRIEF_SECONDS, shelf.brief_due(f.state, ideas["thin"]))
        self.assertEqual(9000 + shelf.BRIEF_SECONDS, shelf.brief_due(f.state, ideas["a"]))
        f.reject("field, worth, benefit", "idea-brief", at=9100, idea="a", brief=dict(BRIEF))
        f.send("idea-brief", actor="v1", at=9100, idea="a", brief=worthy("a")["brief"])
        self.assertIsNone(shelf.brief_due(f.state, f.state["shelf"]["ideas"]["a"]))
        view = {idea["id"]: idea for idea in body.shelf_view(f.state)["ideas"]}
        self.assertEqual("design", view["a"]["brief"]["field"])
        self.assertEqual("beautiful", view["a"]["brief"]["worth"])
        self.assertNotIn("sequence", view["a"]["brief"])
        self.assertEqual(9000 + shelf.BRIEF_SECONDS, view["b"]["brief_due"])
        self.assertIn("audience", view["b"]["brief"])
        shelf.advance(f.state, 9000 + shelf.BRIEF_SECONDS, 700)
        ideas = f.state["shelf"]["ideas"]
        self.assertEqual(("shelved", "graveyard", "graveyard"),
                         tuple(ideas[k]["status"] for k in ("a", "b", "thin")))
        self.assertEqual(shelf.OUTDATED, ideas["b"]["history"][-1]["lesson"])
        self.assertEqual(shelf.EXPIRED, ideas["thin"]["history"][-1]["lesson"])

    def test_prompts_carry_the_worth_test_only_once_it_is_installed(self):
        from house.home import WORTH_GUIDE, brief_guide, course_prompt
        f = self.f
        f.publish(("thin", "thin2"))
        self.open(at=f.state["at"])
        state = f.state | {"life": {}}
        self.assertEqual(BRIEF_GUIDE, brief_guide(state)[1])
        self.assertNotIn("WORTH TEST", course_prompt(state, {}))
        self.worth(at=f.state["at"])
        shape, guide = brief_guide(state)
        self.assertEqual(WORTH_GUIDE, guide)
        for name in ("field", "worth", *shelf.WORTH_FIELDS):
            self.assertIn(f'"{name}"', shape)
        for words in ("software, design or science", "people or other agents", "art or technical",
                      "is it useful, is it beautiful", "could not yesterday", "Traction is not the test",
                      "printed, assembled"):
            self.assertIn(words, guide)
        self.assertIn(shape, focus_prompt(state, "research"))
        vote = course_prompt(state, {})
        self.assertIn("THE WORTH TEST", vote)
        self.assertIn("none of these", vote)
        wishes = (Path(__file__).parents[1] / "docs/WISHES.md").read_text()
        self.assertIn("## Open", wishes)
        self.assertIn("docs/WISHES.md", (Path(__file__).parents[1] / "house/home.py").read_text())

    def test_a_need_is_grounded_and_only_the_steward_answers(self):
        f = self.f
        self.open()
        self.publish("ab", "r1")
        need = {"need": "n1", "need_kind": "server", "for": "a", "ask": "A small always-on server",
                "cost": "about 5 dollars a month", "unlocks": PART, "without": PART}
        f.reject("unknown shelf action", "need-raise", **need)
        self.worth(at=f.state["at"])
        f.state["council"] = {"authorized_by": "v3"}
        f.reject("names the idea or project", "need-raise", **(need | {"for": "nothing"}))
        f.reject("need_kind must be", "need-raise", **(need | {"need_kind": "favour"}))
        f.reject("at least 120 characters", "need-raise", **(need | {"unlocks": "It would be nice."}))
        f.reject("unexpected shelf fields", "need-raise", **{k: v for k, v in need.items() if k != "without"})
        f.send("need-raise", **need)
        f.reject("already used", "need-raise", **need)
        f.reject("only the Steward", "need-answer", actor="other", need="n1", answer="granted", note="Yes")
        f.reject("granted or declined", "need-answer", actor="v3", need="n1", answer="maybe", note="Hm")
        f.reject("only its author", "need-withdraw", actor="other", need="n1", reason="Not mine")
        for n in range(2, 6):
            f.send("need-raise", actor="other", **(need | {"need": f"n{n}"}))
        f.reject("five needs are already open", "need-raise", **(need | {"need": "n6"}))
        f.send("need-answer", actor="v3", need="n1", answer="granted", note="I will set it up this week.")
        f.send("need-withdraw", actor="other", need="n2", reason="Found a way without it")
        f.reject("need is not open", "need-answer", actor="v3", need="n1", answer="declined", note="No")
        needs = f.state["shelf"]["needs"]
        self.assertEqual(["granted", "withdrawn", "open", "open", "open"], [n["status"] for n in needs.values()])
        view = body.shelf_view(f.state)["needs"]
        self.assertEqual(["n3", "n4", "n5", "n1", "n2"], [n["id"] for n in view])
        self.assertEqual("a", view[0]["for_title"])
        self.assertEqual("I will set it up this week.", view[3]["note"])
        self.assertEqual({"need-raise", "need-withdraw", "need-answer"},
                         {kind for kind in shelf_gate.ACTIONS if kind.startswith("need-")})
        from house.home import course_prompt
        self.assertIn("you still never spend money", course_prompt(f.state | {"life": {}}, {}))

    @unittest.skipUnless(shutil.which("node"), "Node is needed for the actual renderer")
    def test_page_shows_a_brief_or_when_a_thin_idea_leaves(self):
        source = Path(__file__).parents[1] / "site/house.js"
        script = r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.textContent='';}
  appendChild(node){this.children.push(node);}
  replaceChildren(){this.children=[];}
}
const root=new Element('section'), document={getElementById:()=>root,createElement:tag=>new Element(tag)};
const text=node=>[node.textContent,...node.children.map(text)].join(' ');
const context=vm.createContext({assert,document,URL,root,text});
const source=fs.readFileSync(process.argv[1],'utf8'),tail='refresh();\nsetInterval(watch,10000);\n';
assert(source.endsWith(tail));vm.runInContext(source.slice(0,-tail.length),context);
vm.runInContext(`
data={timezone:'UTC'};current=false;
frame={at:1000,residents:[{id:'r1',name:'Juniper'}],shelf:{enabled:true,policy:'work-selection-004',great_wanted:false,
 explorer:null,projects:[],research:{last:900,next:900+14400,ceiling:10},ideas:[
 {id:'deep',title:'Deep idea',status:'shelved',sources:[],author:'r1',
  brief:{audience:'Choir leaders',exists:'Two tools, both stop at export',first_version:'One page',risks:'Nobody sings',author:'r1'}},
 {id:'thin',title:'Thin idea',status:'shelved',sources:[],author:'r1',brief_due:90000},
 {id:'third',title:'Third idea',status:'shelved',sources:[],author:'r1',brief_due:90000}]}};
shelf();
const shown=text(root);
assert.match(shown,/Research brief · Juniper/);assert.match(shown,/Who it is for: Choir leaders/);
assert.match(shown,/What already exists: Two tools/);assert.match(shown,/What could sink it: Nobody sings/);
assert.match(shown,/researched/);assert.match(shown,/no research brief yet/);
assert.match(shown,/No research brief yet · leaves the shelf 2 Jan/);
assert.match(shown,/next round after 1 Jan/);assert.doesNotMatch(shown,/no Explorer round needed/);
frame.at=20000;shelf();assert.match(text(root),/a round may start now/);
frame.shelf.ideas=Array.from({length:10},(_,i)=>({id:'i'+i,title:'Idea '+i,status:'shelved',sources:[]}));shelf();
assert.match(text(root),/Research pauses while 10 or more ideas wait/);
frame.shelf.ideas=[
 {id:'new',title:'New idea',status:'shelved',sources:[],author:'r1',brief:{field:'science',worth:'enabling',
  benefit:'Lets a reader check a claim',interest:'Three threads ask for it',exists:'One paper',first_version:'A page',
  check:'A resident answers one question',author:'r1'}},
 {id:'old',title:'Old idea',status:'shelved',sources:[],author:'r1',brief_due:90000,
  brief:{audience:'Choir leaders',exists:'Two tools',first_version:'One page',risks:'Nobody sings',author:'r1'}},
 {id:'third',title:'Third',status:'shelved',sources:[],author:'r1'}];
shelf();
const worth=text(root);
assert.match(worth,/Science · shelved · researched/);
assert.match(worth,/Judged by one question: Does it let someone do or answer something they could not yesterday\?/);
assert.match(worth,/Why it matters outside Emberhall: Lets a reader check a claim/);
assert.match(worth,/What research shows about interest: Three threads ask for it/);
assert.match(worth,/How the house will judge it: A resident answers one question/);
assert.match(worth,/brief needs renewing/);assert.match(worth,/This brief predates the worth test/);
assert.doesNotMatch(worth,/Asked of the Steward/);
frame.shelf.needs=[{id:'n1',status:'open',kind:'server',for:'new',for_title:'New idea',ask:'A small server',cost:'5 a month',
  unlocks:'A live demo',without:'Pages cannot run it',author:'r1',raised_at:1000},
 {id:'n0',status:'declined',kind:'funds',for:'old',ask:'A grant',author:'r1',raised_at:900,note:'Not this year'}];
shelf();
const asked=text(root);
assert.match(asked,/Asked of the Steward · 1 waiting for an answer/);assert.match(asked,/A small server/);
assert.match(asked,/Server · waiting · likely cost: 5 a month · Juniper/);assert.match(asked,/For: New idea/);
assert.match(asked,/What it would unlock: A live demo/);assert.match(asked,/Answered or withdrawn \\(1\\)/);
assert.match(asked,/The Steward's answer: Not this year/);assert.equal(openNeeds().length,1);
`,context);
'''
        result = subprocess.run([shutil.which("node"), "-e", script, str(source)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
