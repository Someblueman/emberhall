"""Second looks: what the prompts say is waiting for a check (Steward, 17 November 2026, evening).

Plain dict states are enough: the functions only read state and return text.
"""
import unittest
from unittest.mock import patch

from house import checks, council

HOUR, DAY, NOW = 3600, 86400, 2_000_000_000


def lesson(author="ann", status="observed", reviews=(), claim="A claim."):
    return {"key": "k", "claim": claim, "evidence": "e", "status": status, "reviews": list(reviews),
            "author": author}


def proposal(mode="rule", author="ann", trial=True, endorsed=(), notice=None, base="rev"):
    return {"mode": mode, "author": author, "title": "A title", "text": "t", "reason": "r", "base": base,
            "status": "pending", "proposed_at": NOW - 5 * DAY, "trial": {"task": "x"} if trial else None,
            "endorsements": {who: {"evidence": "e", "at": NOW - DAY} for who in endorsed},
            "notice": {"at": notice} if notice is not None else None}


def house(lessons=None, proposals=None, migrated=True):
    people = ("ann", "bob", "cat", "dan")
    return {"at": NOW, "rule_revision": "rev", "residents": {who: {"name": who.title()} for who in people},
            "lessons": lessons or {}, "proposals": proposals or {}, "council": {"rules": {}, "decisions": {}},
            "maintenance": {"migrations": {checks.MOMENTUM: {"at": 1}} if migrated else {}}}


def learned(*ages):
    """Journal events saying when each lesson, named l0, l1 ..., was recorded (age in hours)."""
    return [{"op": "learn", "at": NOW - age * HOUR, "data": {"lesson": f"l{n}"}} for n, age in enumerate(ages)]


class OfferTests(unittest.TestCase):
    def test_nothing_before_the_migration(self):
        state = house({"l0": lesson()}, {"p": proposal(endorsed=("ann", "bob"), notice=NOW - 2 * DAY)}, migrated=False)
        self.assertFalse(checks.enabled(state))
        self.assertEqual(checks.offer(state, "cat"), "")
        self.assertTrue(checks.enabled(house()))

    def test_nothing_to_list_gives_nothing(self):
        self.assertEqual(checks.offer(house({"l0": lesson("cat")}), "cat"), "")

    def test_offer_names_lessons_and_council_and_ends_with_newline(self):
        state = house({"l0": lesson()}, {"p": proposal(endorsed=("ann", "bob"), notice=NOW - 2 * DAY)})
        text = checks.offer(state, "cat")
        self.assertTrue(text.startswith("THE COUNCIL IS WAITING ON YOU:\n"))
        self.assertIn("LESSONS NOBODY HAS CHECKED", text)
        self.assertIn("review LESSON --evidence", text)
        self.assertIn("--as cat", text)
        self.assertIn("worse than none", text)
        self.assertIn("no task and no help request", text.lower())
        self.assertTrue(text.endswith("\n"))
        self.assertNotIn("THE COUNCIL", checks.offer(house({"l0": lesson()}), "cat"))


class LessonTests(unittest.TestCase):
    def test_own_reviewed_and_superseded_lessons_are_not_listed(self):
        state = house({"mine": lesson("cat"), "done": lesson(reviews=("bob",)), "old": lesson(status="superseded"),
                       "fight": lesson(status="contested"), "open": lesson("bob")})
        self.assertEqual([row["id"] for row in checks.lessons(state, "cat")], ["open"])
        self.assertEqual([row["id"] for row in checks.lessons(state, "bob")], ["mine"])
        self.assertEqual(sorted(row["id"] for row in checks.lessons(state, "ann", 9)), ["mine", "open"])

    def test_newest_first_and_the_limit(self):
        state = house({f"l{n}": lesson() for n in range(5)})
        self.assertEqual([row["id"] for row in checks.lessons(state, "cat")], ["l4", "l3", "l2"])
        self.assertEqual(len(checks.lessons(state, "cat", 8)), 5)
        self.assertEqual(len(checks.lessons(state, "cat", 1)), 1)

    def test_recent_lessons_come_before_old_ones_and_ages_are_given(self):
        state = house({f"l{n}": lesson() for n in range(4)})
        events = learned(200, 5, 100, 30)
        rows = checks.lessons(state, "cat", 4, events)
        self.assertEqual([row["id"] for row in rows], ["l1", "l3", "l2", "l0"])
        self.assertEqual([row["hours"] for row in rows], [5, 30, 100, 200])
        self.assertEqual([row["id"] for row in checks.lessons(state, "cat", 2, events)], ["l1", "l3"])

    def test_without_the_journal_the_age_is_unknown(self):
        self.assertIsNone(checks.lessons(house({"l0": lesson()}), "cat")[0]["hours"])

    def test_claim_is_cut_at_a_word(self):
        long = " ".join(["word"] * 80)
        row = checks.lessons(house({"l0": lesson(claim=long)}), "cat")[0]
        self.assertLessEqual(len(row["claim"]), 143)
        self.assertTrue(row["claim"].endswith("word..."))
        self.assertEqual(row["author"], "Ann")
        self.assertEqual(checks.lessons(house({"l0": lesson(claim="Short one.")}), "cat")[0]["claim"], "Short one.")


class CouncilTests(unittest.TestCase):
    def lines(self, resident, **kinds):
        return checks.council(house(proposals={"p": proposal(**kinds)}), resident)

    def test_ready_proposal_gives_an_enact_line_to_anyone(self):
        for who in ("ann", "bob", "cat", "dan"):
            lines = self.lines(who, endorsed=("bob", "cat"), notice=NOW - 25 * HOUR)
            self.assertEqual(len(lines), 1)
            self.assertIn(f"any resident may enact it: `council --as {who} enact p`", lines[0])
            self.assertIn("docs/STEWARD_ORDERS.md", lines[0])

    def test_window_still_running_gives_nothing(self):
        self.assertEqual(self.lines("dan", endorsed=("bob", "cat"), notice=NOW - 23 * HOUR), [])

    def test_renovation_window_is_an_hour_once_quick_renovations_are_installed(self):
        state = house(proposals={"p": proposal("renovation", endorsed=("bob", "cat"), notice=NOW - 2 * HOUR)})
        self.assertEqual(checks.council(state, "dan"), [])
        state["maintenance"]["migrations"][council.QUICK_RENOVATIONS] = {"at": 1}
        self.assertEqual(len(checks.council(state, "dan")), 1)

    def test_needs_endorsements_is_shown_to_a_third_resident_only(self):
        lines = self.lines("dan", endorsed=("bob",))
        self.assertEqual(len(lines), 1)
        self.assertIn("1 of 2", lines[0])
        self.assertIn("endorse p --evidence", lines[0])
        self.assertEqual(self.lines("ann", endorsed=("bob",)), [])
        self.assertEqual(self.lines("bob", endorsed=("bob",)), [])

    def test_wakes_skip_a_renovation_only_when_every_proposed_file_is_installed(self):
        files = {"house/body.py": "a" * 64, "house/digest.py": "b" * 64}
        ready = proposal("renovation", endorsed=("bob", "cat"), notice=NOW - 2 * DAY)
        state = house(proposals={"reading-repairs": ready | {"renovation": {"files": files}}})
        for installed, expected in (
            ({}, True),
            ({"house/body.py": files["house/body.py"]}, True),
            (files | {"house/body.py": "c" * 64}, True),
            (files | {"house/other.py": "d" * 64}, False),
        ):
            with self.subTest(installed=installed):
                state["maintenance"]["protected_files"] = installed
                for prompt in (checks.offer, checks.focus):
                    self.assertEqual("enact reading-repairs" in prompt(state, "dan"), expected)

    def test_later_edits_do_not_revive_a_delivered_renovation(self):
        files = {"house/body.py": "a" * 64, "house/digest.py": "b" * 64}
        ready = proposal("renovation", endorsed=("bob", "cat"), notice=NOW - 2 * DAY)
        state = house(proposals={"reading-repairs": ready | {"renovation": {"files": files}}})
        newer = files | {"house/body.py": "c" * 64}
        state["maintenance"]["protected_files"] = newer
        migrations = state["maintenance"]["migrations"]
        migrations["newer"] = {"at": NOW, "sequence": 12, "protected_files": newer}
        proposed = ready["proposed_at"]
        for at, manifest, reminder in (
            (proposed - 1, files, True),
            (proposed + 1, {"house/body.py": files["house/body.py"]}, True),
            (proposed + 1, files, False),
        ):
            with self.subTest(at=at, manifest=manifest):
                migrations["earlier"] = {"at": at, "sequence": 10, "protected_files": manifest}
                for prompt in (checks.offer, checks.focus):
                    self.assertEqual("enact reading-repairs" in prompt(state, "dan"), reminder)

    def test_two_endorsements_without_notice_gives_the_notice_command(self):
        lines = self.lines("ann", endorsed=("bob", "cat"))
        self.assertEqual(len(lines), 1)
        self.assertIn("`council --as ann notice p`", lines[0])

    def test_no_trial_only_reminds_the_author(self):
        lines = self.lines("ann", trial=False)
        self.assertEqual(len(lines), 1)
        self.assertIn("needs a trial", lines[0])
        self.assertEqual(self.lines("bob", trial=False), [])

    def test_wake_prompt_proposals_are_never_shown(self):
        for kinds in ({"endorsed": ("bob", "cat"), "notice": NOW - 2 * DAY}, {"endorsed": ("bob",)},
                      {"endorsed": ("bob", "cat")}, {"trial": False}):
            for who in ("ann", "bob", "dan"):
                self.assertEqual(self.lines(who, mode="wake-prompt", **kinds), [], (kinds, who))

    def test_lapsed_and_closed_proposals_are_not_shown(self):
        ready = {"endorsed": ("bob", "cat"), "notice": NOW - 2 * DAY}
        self.assertEqual(len(self.lines("dan", **ready)), 1)
        self.assertEqual(self.lines("dan", base="older", **ready), [])
        state = house(proposals={"p": proposal(**ready)})
        for status in ("enacted", "vetoed", "superseded"):
            state["proposals"]["p"]["status"] = status
            self.assertEqual(checks.council(state, "dan"), [])

    def test_old_proposals_without_a_mode_are_skipped(self):
        state = house(proposals={"old": {"text": "t", "reason": "r", "base": "rev", "status": "pending"}})
        self.assertEqual(checks.council(state, "dan"), [])


class FocusTests(unittest.TestCase):
    HEAD = "HOUSE FOCUS for this run (instead of the current project; other residents are building that): "

    def test_focus_starts_with_the_house_heading_and_lists_lessons(self):
        state = house({"l0": lesson(), "l1": lesson("bob"), "l2": lesson("cat")},
                      {"p": proposal(endorsed=("ann", "bob"), notice=NOW - 2 * DAY)}, migrated=False)
        text = checks.focus(state, "cat")
        self.assertTrue(text.startswith(self.HEAD))
        self.assertIn("l0", text)
        self.assertIn("l1", text)
        self.assertNotIn("- l2", text)
        self.assertIn("council --as cat enact p", text)
        self.assertIn("review LESSON --evidence", text)
        self.assertIn("Hearth", text)
        self.assertIn("no task and no help request", text.lower())
        self.assertTrue(text.endswith("\n"))

    def test_focus_lists_up_to_eight_lessons(self):
        text = checks.focus(house({f"l{n}": lesson() for n in range(12)}), "cat")
        self.assertEqual(text.count("\n- l"), 8)

    def test_focus_without_anything_waiting_still_reads_well(self):
        text = checks.focus(house(), "cat")
        self.assertTrue(text.startswith(self.HEAD))
        self.assertIn("Nothing waits on you there now", text)

    def test_rooms_section_is_included_when_filled(self):
        self.assertEqual(checks.rooms(house(), "cat"), "")
        with patch.object(checks, "rooms", return_value="The Salvage Room holds item X.\n"):
            text = checks.focus(house(), "cat")
        self.assertIn("4. The Salvage Room holds item X.\n", text)


if __name__ == "__main__":
    unittest.main()
