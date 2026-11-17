"""The Chronicle distinguishes passing a project stage from finishing the work."""
import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from house import chronicle_page, publish, shelf

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/emberhall-chronicle-room"


def staged_events():
    def event(sequence, kind, **data):
        return {"sequence": sequence, "at": 1000 + sequence, "op": "shelf",
                "actor": f"resident-{sequence}", "id": f"event-{sequence}",
                "data": {"kind": kind, **data}}

    stages = [{"milestone": f"PRIVATE_STAGE_{n}", "seconds": 1000} for n in range(3)]
    return [
        event(1, "explore-publish", ideas=[{"idea": "night-ferry", "title": "Long crossing"}]),
        event(2, "choice-open", choice="long-work", slot="great",
              milestones={"night-ferry": {"milestones": stages}}),
        *[event(n, "choice-vote", choice="long-work", idea="night-ferry") for n in range(3, 6)],
        *[event(n, "project-done", project="long-work", evidence=f"PRIVATE_TASK_{n}")
          for n in range(6, 9)],
    ]


class ChronicleStageTests(unittest.TestCase):
    def test_each_prefix_agrees_with_the_project_reducer(self):
        events = staged_events()
        plan = events[1]["data"]["milestones"]["night-ferry"]["milestones"]
        project = {"status": "active", "slot": "great", "milestones": plan,
                   "stage": 0, "completed": [], "owner": "builder", "deadline": 0,
                   "milestone": plan[0]["milestone"]}
        state = {"shelf": {"projects": {"long-work": project}}, "tasks": {
            f"PRIVATE_TASK_{n}": {"status": "done", "artifacts": {"proof.txt": "hash"}}
            for n in range(6, 9)}}
        self.assertEqual(len(chronicle_page.select_milestones(events[:5])), 1)
        for end in range(6, 9):
            with self.subTest(through=end):
                ev = events[end - 1]
                shelf.project_action(state, ev["data"], "builder", ev["at"], end)
                entries = chronicle_page.select_milestones(events[:end])
                finished = [m for m in entries if m["category_key"] == "project"]
                passed = [m for m in entries if m["category_key"] == "stage"]
                self.assertEqual(bool(finished), project["status"] == "done")
                self.assertEqual([m["sequence"] for m in passed], list(range(6, min(end + 1, 8))))
                if finished:
                    self.assertEqual(finished[0]["sequence"], 8)
                self.assertEqual([m["sequence"] for m in entries], sorted(m["sequence"] for m in entries))
                for stage in passed:
                    self.assertEqual(stage["links"], [])

    def test_rendered_stages_filters_privacy_and_final_launch(self):
        events = staged_events()
        catalog = json.loads((ROOT / "site/projects.json").read_text())
        before = copy.deepcopy(events)
        for end in (6, 7, 8):
            entries = chronicle_page.select_milestones(events[:end])
            page = chronicle_page.render_html(entries, through=end, catalog=catalog)
            self.assertIn(f"Finished creations ({int(end == 8)})", page)
            self.assertIn(f"Passed stages ({min(end - 5, 2)})", page)
            self.assertIn("Long crossing — stage 1 of 3", page)
            self.assertIn('id="chronicle-stage" value="stage"', page)
            self.assertIn('main:has(#chronicle-stage:checked) .entry:not(.entry-stage)', page)
            self.assertEqual('class="launch"' in page, end == 8)
            self.assertNotIn("PRIVATE_", page)
            self.assertNotIn("<script", page)
        self.assertEqual(events, before)

    def test_single_stage_drop_and_preclosure_boundaries(self):
        events = staged_events()
        small = copy.deepcopy(events)
        small[1]["data"]["milestones"]["night-ferry"] = {"milestone": "PRIVATE", "seconds": 1000}
        entries = chronicle_page.select_milestones(small)
        self.assertEqual([m["sequence"] for m in entries if m["category_key"] == "project"], [6])
        self.assertFalse(any(m["category_key"] == "stage" for m in entries))
        dropped = copy.deepcopy(events)
        dropped[6]["data"] = {"kind": "project-drop", "project": "long-work", "lesson": "PRIVATE_DROP"}
        entries = chronicle_page.select_milestones(dropped)
        self.assertFalse(any(m["category_key"] == "project" for m in entries))
        self.assertEqual([m["sequence"] for m in entries if m["category_key"] == "stage"], [6])
        early = copy.deepcopy(events[5]); early["sequence"] = 2
        entries = chronicle_page.select_milestones(events[:5] + [early])
        self.assertEqual([m["category_key"] for m in entries], ["choice"])

    def test_standalone_and_real_publisher_match_each_prefix(self):
        spec = importlib.util.spec_from_file_location("standalone_stages", PROJECT / "chronicle.py")
        standalone = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(standalone)
        for end in range(5, 9):
            events = staged_events()[:end]
            entries = chronicle_page.select_milestones(events)
            self.assertEqual(standalone.select_milestones(events), entries)
            expected = standalone.render_html(entries, through=end, house_id="Example house")
            record = SimpleNamespace(read=lambda: ({"house_id": "Example house"}, events, "head"))
            self.assertEqual(publish.chronicle_body(record, {}).decode(), expected)

    def test_malformed_stage_plan_never_becomes_a_single_stage_completion(self):
        for stages in (None, "three", {}, [], [{}], [{}] * 9):
            with self.subTest(stages=stages):
                events = staged_events()
                events[1]["data"]["milestones"]["night-ferry"]["milestones"] = stages
                entries = chronicle_page.select_milestones(events)
                self.assertEqual([m["category_key"] for m in entries], ["choice"])


if __name__ == "__main__":
    unittest.main()
