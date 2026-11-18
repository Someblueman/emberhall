"""Older Assay receipts remain reachable at the selected historical moment."""
import shutil
import unittest

from tests import test_assay_room as assay


@unittest.skipUnless(shutil.which("node"), "Node runs the shipped renderer")
class AssayScarBrowsingTests(unittest.TestCase):
    run_harness = assay.AssayRoomTests.run_harness

    def fixture(self):
        scars = []
        for n in range(1, 16):
            scars.append({
                "id": f"scar-{n}", "title": f"Receipt [{n}]", "sequence": n,
                "room": "workshop", "kind": "failure", "mended": n % 4 == 0,
                "detail": "finished-task" if n == 9 else
                "No unfinished claim at this receipt" if n % 4 == 1 else
                "unrecorded-task" if n % 4 == 2 else "unfinished-task",
            })
        base = {"rooms": [{"id": "assay", "name": "The Assay Room", "status": "open"}],
                "tasks": [{"id": "unfinished-task", "status": "unclaimed", "generation": 0},
                          {"id": "finished-task", "status": "done", "generation": 1}],
                "residents": [], "runs": [], "ambitions": [], "budgets": [],
                "event": {"op": "say", "actor": "r"}}
        frames = [{**base, "seq": n, "at": 1000 + n,
                   "scars": [{"id": s["id"]} for s in scars[:n]]}
                  for n in range(1, 16)]
        return {"data": {"timezone": "UTC", "observed_at": 1015, "commits": [],
                         "scars": {s["id"]: s for s in scars}, "frames": frames},
                "index": 12, "current": False, "selected": "assay"}

    def test_all_receipts_have_bounded_pages_without_future_leakage(self):
        initial = self.run_harness(self.fixture())["panelText"]
        for n in range(1, 16):
            if 8 <= n <= 13:
                self.assertIn(f"Receipt [{n}]", initial)
            else:
                self.assertNotIn(f"Receipt [{n}]", initial)
        result = self.run_harness({**self.fixture(), "steps": [
            {"id": "assay-scars-next", "action": "click"},
            {"id": "assay-scars-next", "action": "click"},
            {"id": "assay-scars-previous", "action": "click"},
        ]})
        pages = [result["interactions"][i]["text"] for i in range(3)]
        for n in range(2, 8):
            self.assertIn(f"Receipt [{n}]", pages[0])
        self.assertNotIn("Receipt [8]", pages[0])
        self.assertEqual([pages[0].index(f"Receipt [{n}]") for n in range(7, 1, -1)],
                         sorted(pages[0].index(f"Receipt [{n}]") for n in range(7, 1, -1)))
        self.assertEqual(pages[0], pages[2])
        self.assertIn("Receipt [1]", pages[1])
        self.assertNotIn("Receipt [2]", pages[1])
        self.assertIn("assay-scars-next", result["interactions"][1]["disabled"])
        self.assertEqual(result["interactions"][0]["focus"], "assay-scars")
        for page in pages:
            self.assertNotIn("Receipt [14]", page)
            self.assertNotIn("Receipt [15]", page)
        self.assertFalse(result["dataMutated"])

    def test_attention_filter_resets_page_and_keeps_uncertain_receipts(self):
        result = self.run_harness({**self.fixture(), "steps": [
            {"id": "assay-scars-next", "action": "click"},
            {"id": "assay-scar-filter", "action": "change", "value": "attention"},
            {"id": "assay-scars-next", "action": "click"},
            {"id": "assay-scar-filter", "action": "change", "value": "history"},
            {"id": "assay-scar-filter", "action": "refresh", "selection": [0, 0, "none"]},
        ]})
        attention = result["interactions"][1]["text"]
        self.assertIn("Not confirmed finished", attention)
        self.assertIn("Still unfinished", attention)
        self.assertIn("showing 1–6", attention)
        for n in (1, 4, 5, 8, 9, 12, 13):
            self.assertNotIn(f"Receipt [{n}]", attention)
        history = result["interactions"][3]["text"]
        self.assertIn("showing 1–6", history)
        for n in (2, 3, 6, 7, 10, 11):
            self.assertNotIn(f"Receipt [{n}]", history)
        self.assertNotIn("Not confirmed finished", history)
        self.assertIn("Finished later", history)
        self.assertEqual(result["interactions"][4]["focus"], "assay-scar-filter")

    def test_rewind_clamps_pages_and_empty_filter_explains_absence(self):
        result = self.run_harness({**self.fixture(), "steps": [
            {"id": "assay-scars-next", "action": "click"},
            {"id": "assay-scars-next", "action": "click"},
            {"frame": 0},
            {"id": "assay-scar-filter", "action": "change", "value": "attention"},
        ]})
        rewound, empty = result["interactions"][2:]
        self.assertIn("showing 1–1", rewound["text"])
        self.assertIn("Receipt [1]", rewound["text"])
        self.assertNotIn("Receipt [2]", rewound["text"])
        self.assertIn("No scars match", empty["text"])
        self.assertIn("assay-scars-next", empty["disabled"])
        self.assertIn("assay-scars-previous", empty["disabled"])


if __name__ == "__main__":
    unittest.main()
