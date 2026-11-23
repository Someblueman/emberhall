"""Paged shelf and graveyard reads: traversal, filters and limit rejection."""
import copy
import json
import unittest

from house.shelf_status import shelf_page
from tests.support import HouseCase


def record(status, scale=None, brief=True):
    entry = {"author": "alice", "status": status, "title": "Title", "losses": 0,
             "shelved_sequence": 5, "history": []}
    if scale:
        entry["scale"] = scale
    if brief:
        entry["brief"] = {"sequence": 9, "author": "alice",
                          "asked": [{"who": "w", "where": "x", "said": "secret quote"}]}
    return entry


class ShelfPageTests(unittest.TestCase):
    def setUp(self):
        self.state = {"house_id": "fixture", "name": "Fixture", "sequence": 30,
                      "shelf": {"ideas": {
                          "apple": record("shelved", "small"),
                          "birch": record("graveyard", "small"),
                          "cedar": record("shelved", "great"),
                          "dune": record("project", "small"),
                          "elm": record("graveyard", "great", brief=False),
                          "fern": record("shelved"),
                          "gale": record("graveyard", "small"),
                      }}}

    def traverse(self, **filters):
        seen, after = [], None
        while True:
            page = shelf_page(self.state, "head", limit=2, after=after, **filters)
            seen.extend(page["ideas"])
            if not page["page"]["has_more"]:
                return seen, page
            after = page["page"]["next_after"]
            self.assertIsNotNone(after)

    def test_traversal_is_complete_sorted_and_nonduplicated(self):
        before = copy.deepcopy(self.state)
        seen, last = self.traverse()
        self.assertEqual(seen, sorted(self.state["shelf"]["ideas"]))
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(last["counts"]["matching"], 7)
        self.assertEqual(last["counts"]["by_standing"],
                         {"shelved": 3, "graveyard": 3, "project": 1})
        self.assertEqual(self.state, before)

    def test_entries_are_compact_without_brief_bodies(self):
        page = shelf_page(self.state, "head", limit=50)
        self.assertNotIn("secret quote", json.dumps(page))
        self.assertEqual(page["ideas"]["apple"]["brief_revision"], 9)
        self.assertIsNone(page["ideas"]["elm"]["brief_revision"])
        self.assertEqual(page["ideas"]["fern"]["scale"], "small")

    def test_scale_and_standing_filters(self):
        self.assertEqual(self.traverse(standing="graveyard")[0],
                         ["birch", "elm", "gale"])
        self.assertEqual(self.traverse(scale="great")[0], ["cedar", "elm"])
        self.assertEqual(self.traverse(scale="great", standing="shelved")[0],
                         ["cedar"])

    def test_cursor_past_the_end_is_an_empty_page(self):
        page = shelf_page(self.state, "head", after="zzz")
        self.assertEqual(page["ideas"], {})
        self.assertFalse(page["page"]["has_more"])
        self.assertIsNone(page["page"]["next_after"])

    def test_invalid_limits_and_filters_are_rejected(self):
        for bad in (0, -1, 51):
            with self.assertRaisesRegex(ValueError, "1..50"):
                shelf_page(self.state, "head", limit=bad)
        with self.assertRaisesRegex(ValueError, "standing"):
            shelf_page(self.state, "head", standing="lost")
        with self.assertRaisesRegex(ValueError, "scale"):
            shelf_page(self.state, "head", scale="enormous")


class ShelfPageCliTests(HouseCase):
    def test_empty_shelf_pages_and_bad_limit_fails_through_cli(self):
        page = self.cli("status", "--shelf", "--limit", "5")
        self.assertEqual(page["ideas"], {})
        self.assertEqual(page["counts"]["matching"], 0)
        err = self.cli("status", "--shelf", "--limit", "0", success=False)
        self.assertIn("1..50", err)
        err = self.cli("status", "--shelf", "--tasks", success=False)
        self.assertIn("--shelf", err)
