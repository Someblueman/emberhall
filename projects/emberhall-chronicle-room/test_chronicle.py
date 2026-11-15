#!/usr/bin/env python3
"""Unit tests for the Emberhall Chronicle Room static generator."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chronicle  # noqa: E402

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class ChronicleTests(unittest.TestCase):
    def _load_fixture(self):
        return chronicle.load_export(FIXTURES_DIR / "synthetic_journal.json")

    def test_actual_shape_vote_closure(self) -> None:
        events, through, house_id = self._load_fixture()
        self.assertEqual(through, 60)
        self.assertEqual(house_id, "synthetic-house-001")
        milestones = chronicle.select_milestones(events)
        seqs = [m["sequence"] for m in milestones]
        self.assertEqual(seqs, [15, 16, 24, 34, 39, 55])
        categories = [m["category"] for m in milestones]
        self.assertEqual(
            categories,
            [
                "Closed Choice",
                "Completed Project",
                "Rejected Shortlist",
                "Enacted Rule",
                "Enacted Rule",
                "Closed Choice",
            ],
        )
        # Trial fixture rounds are excluded, never rendered as real choices.
        self.assertNotIn("trial-choice-x", [str(m["title"]) for m in milestones])
        # Winner resolved to the real idea title, not the opaque choice ID alone.
        self.assertIn("Alpha Tool", milestones[0]["title"])
        self.assertEqual(milestones[1]["title"], "Alpha Tool")
        self.assertIn("test-choice-001", milestones[0]["title"])
        # A closed choice carries no project link: the winning build may not
        # exist yet, so guessing projects/<idea>/ would point at unbuilt trees.
        self.assertEqual(milestones[0]["links"], [])
        self.assertEqual(milestones[5]["links"], [])
        # Links point at real project directories via GitHub, never at guessed
        # evidence, and only on recorded completed projects.
        self.assertIn(
            "https://github.com/Someblueman/emberhall/tree/main/projects/alpha-tool/",
            milestones[1]["links"][0][1],
        )

    def test_author_self_vote_never_counts(self) -> None:
        events, _, _ = self._load_fixture()
        # test-choice-003: the author's own vote (resident-yplorer, seq 52) is
        # recorded but uncounted, so after two counted votes (seq 53-54) the
        # round is still open; the third counted vote (seq 55) closes it with
        # the correct winner and sequence. Had the self-vote counted, the
        # round would have closed at seq 54.
        prefix = [e for e in events if e["sequence"] < 55]
        choices = chronicle._derive_choices(prefix)
        self.assertEqual(choices["test-choice-003"]["status"], "open")
        self.assertEqual(choices["test-choice-003"]["closed_sequence"], None)
        choices = chronicle._derive_choices(events)
        choice = choices["test-choice-003"]
        self.assertEqual(choice["status"], "closed")
        self.assertEqual(choice["winner"], "delta-tool")
        self.assertEqual(choice["closed_sequence"], 55)
        self.assertEqual(choice["closed_actor"], "resident-i")
        self.assertEqual(
            [v["counted"] for v in choice["votes"]],
            [False, True, True, True],
        )
        milestones = chronicle.select_milestones(events)
        closed = [
            m for m in milestones
            if m["category_key"] == "choice" and "test-choice-003" in str(m["title"])
        ]
        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0]["sequence"], 55)
        self.assertIn("Delta Tool", closed[0]["title"])
        self.assertEqual(closed[0]["links"], [])

    def test_rejected_choice_no_two_of_three(self) -> None:
        events, _, _ = self._load_fixture()
        milestones = chronicle.select_milestones(events)
        rejected = [m for m in milestones if m["category_key"] == "rejected"]
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["sequence"], 24)
        self.assertIn("no winner", rejected[0]["title"])
        # Neutral wording: rejection does not imply a specific vote split.
        self.assertNotIn("three-way split", rejected[0]["title"])
        # A rejected choice must not produce a Completed Project even if a
        # stray project-done names it (fixture seq 25).
        projects = [m for m in milestones if m["category_key"] == "project"]
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["sequence"], 16)

    def test_enactment_vs_authority_delegation(self) -> None:
        events, _, _ = self._load_fixture()
        milestones = chronicle.select_milestones(events)
        rules = [m for m in milestones if m["category_key"] == "rule"]
        self.assertEqual(len(rules), 2)
        self.assertEqual(rules[0]["sequence"], 34)
        self.assertEqual(rules[0]["title"], "Test Rule: Do the Honest Thing")
        self.assertIn("council", rules[0]["summary"])
        self.assertEqual(rules[1]["sequence"], 39)
        self.assertEqual(rules[1]["title"], "Choose worthwhile work, or reject the shortlist")
        self.assertIn("direct-owner", rules[1]["summary"])
        html_text = chronicle.render_html(milestones, through=60, house_id="synthetic-house-001")
        # Authority delegation and non-selection migrations must never render.
        self.assertNotIn("council-authorize", html_text)
        self.assertNotIn("RAW_SOURCE_SHOULD_NOT_RENDER", html_text)
        self.assertNotIn("some-runtime-migration-20261115", html_text)

    def test_unverified_and_malformed_input_rejection(self) -> None:
        events, _, _ = self._load_fixture()
        milestones = chronicle.select_milestones(events)
        # The verified=false project-done duplicate must not add milestones.
        self.assertEqual(len(milestones), 6)
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text('{"events": "not-a-list"}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                chronicle.load_export(bad)
            bad2 = Path(tmp) / "bad2.json"
            bad2.write_text('"just a string"\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                chronicle.load_export(bad2)

    def test_public_field_privacy(self) -> None:
        events, _, _ = self._load_fixture()
        milestones = chronicle.select_milestones(events)
        html_text = chronicle.render_html(milestones, through=60, house_id="synthetic-house-001")
        # Raw message bodies must never reach HTML: vote reasons, say text,
        # claim tokens/workspaces, rule text, sources and evidence task IDs.
        for needle in [
            "RAW_REASON_FIRST_VOTE",
            "RAW_REASON_SECOND_VOTE",
            "RAW_REASON_THIRD_VOTE",
            "RAW_REASON_AUTHOR_SELF_VOTE",
            "RAW_REASON_COUNTED_ONE",
            "RAW_REASON_COUNTED_TWO",
            "RAW_REASON_COUNTED_THREE",
            "RAW_MESSAGE_SHOULD_BE_EXCLUDED",
            "secret-claim-token",
            "RAW_RULE_TEXT",
            "RAW_PROPOSAL_REASON",
            "RAW_SOURCE_SHOULD_NOT_RENDER",
            "test-build-task",
            "secret123",
            "supersecret",
            ".house-residents/",
            "../../evidence/",
            "../../projects/",
            "three-way split",
        ]:
            self.assertNotIn(needle, html_text, needle)
        # Allowlisted public fields are present and escaped.
        self.assertIn("Alpha Tool", html_text)
        self.assertIn("https://github.com/Someblueman/emberhall/tree/main/projects/alpha-tool/", html_text)
        # Static history describes its snapshot, not the room's live lifecycle.
        self.assertIn("About this snapshot", html_text)
        self.assertNotIn("Under construction", html_text)

    def test_readable_recent_history_with_collapsed_records(self) -> None:
        import re
        entries = [{"category_key": "choice", "category": "Closed Choice",
                    "sequence": n, "timestamp": "15 November", "actor": "resident-opaque",
                    "title": f"house-growth-choice-{n:03d} — Project {n}",
                    "summary": "Recorded decision.", "links": []} for n in range(1, 11)]
        page = chronicle.render_html(entries, through=10)
        headings = re.findall(r"<h3>(.*?)</h3>", page)
        self.assertEqual(headings, [f"Project {n}" for n in range(10, 0, -1)])
        recent, earlier = page.split('<details class="earlier">', 1)
        self.assertEqual(recent.count('<article '), 8)
        self.assertEqual(earlier.count('<article '), 2)
        self.assertIn('Earlier milestones (2)', earlier)
        self.assertEqual(page.count('<details class="record">'), 10)
        self.assertIn('house-growth-choice-010', page)
        self.assertIn('Explore the projects', page)

    def test_deterministic_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out1 = chronicle.generate(
                FIXTURES_DIR / "synthetic_journal.json", tmp_path / "run1"
            )
            out2 = chronicle.generate(
                FIXTURES_DIR / "synthetic_journal.json", tmp_path / "run2"
            )
            self.assertEqual(out1.read_bytes(), out2.read_bytes())


if __name__ == "__main__":
    unittest.main()
