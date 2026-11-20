"""Light runs (Steward, 20 November): three Codex sessions at once and a lighter prompt."""
from __future__ import annotations

import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from house import home, staffing


def state_with(active: dict[str, str], light: bool) -> dict:
    runs = {f"r{n}": {"agent": agent, "model": model, "status": "active", "resident": f"p{n}",
                      "started_sequence": n}
            for n, (agent, model) in enumerate(active.items() if isinstance(active, dict) else active)}
    return {"maintenance": {"migrations": {staffing.LIGHT: {"at": 0}} if light else {}},
            "life": {"runs": runs, "requests": {}, "rooms": {}}, "tasks": {}, "residents": {}, "at": 0}


class LightRunTests(unittest.TestCase):
    def test_three_codex_sessions_fill_the_codex_room_only_after_the_migration(self):
        three = [("codex", "gpt-6.1-sol"), ("codex", "gpt-6.1-sol"), ("codex", "gpt-6-luna")]
        self.assertTrue(staffing.codex_room(state_with(three, light=False)))
        self.assertFalse(staffing.codex_room(state_with(three, light=True)))
        self.assertTrue(staffing.codex_room(state_with(three[:2] + [("muse", "muse-ember-1.0")], light=True)))

    def test_no_codex_start_is_chosen_while_three_run(self):
        three = [("codex", "gpt-6.1-sol")] * 3
        with patch("house.home.provider_available", lambda state, kind, now: kind in {"codex", "muse"}), \
                patch("house.home.work_metrics.counts", lambda state, mode, kinds: {k: 0 for k in kinds}), \
                patch("house.home.provider_shares", lambda state, now: {k: 1 for k in home.KINDS}):
            self.assertEqual("muse", home.choose_provider(state_with(three, light=True), 0, "codex"))
            self.assertEqual("codex", home.choose_provider(state_with(three, light=False), 0, "codex"))
        with patch("house.home.provider_available", lambda state, kind, now: kind == "codex"):
            self.assertIsNone(home.choose_provider(state_with(three, light=True), 0, "codex"))

    def test_a_helper_is_not_started_past_the_cap(self):
        three = [("codex", "gpt-6.1-sol")] * 3
        state = state_with(three, light=True)
        with patch("house.staffing.enabled", lambda state: True), \
                patch("house.life.provider_available", lambda state, kind, at: True):
            self.assertIsNone(staffing.select(state, 0, {"pending_help": [], "ready_tasks": [],
                                                         "uncovered_tasks": 0}))

    def test_every_prompt_asks_for_a_light_run(self):
        for light in (False, True):
            state = state_with([], light)
            state["life"]["runs"]["run1"] = {"agent": "codex", "model": "gpt-6.1-sol", "status": "active",
                                             "resident": "newbie"}
            state["wake_policy"] = None
            stub = types.SimpleNamespace(record=types.SimpleNamespace(read=lambda: (state, [], 0)), focus=None,
                                         running={}, private=Path(tempfile.mkdtemp()))
            with tempfile.TemporaryDirectory() as folder, patch("house.home.active_prompt", lambda state: ""):
                prompt = home.Coordinator.prompt(stub, state, "run1", "newbie", Path(folder),
                                                 Path(folder) / "client", None)
            if not light:
                self.assertNotIn("KEEP THE RUN LIGHT", prompt)
                continue
            for words in ("KEEP THE RUN LIGHT", "ran out of a weeks worth of tokens",
                          "do not read docs/STEWARD_ORDERS.md, README.md or docs/RESUME.md in full",
                          "scripts/status_brief.py", "longer than about 150 lines",
                          "Do not re-check what the record already shows accepted"):
                self.assertIn(words, prompt)


if __name__ == "__main__":
    unittest.main()


class MixAndHouseTests(unittest.TestCase):
    def test_research_rounds_start_in_each_field_in_turn(self):
        state = {"maintenance": {"migrations": {}}, "shelf": {"rounds": {}}}
        self.assertEqual("", home.field_turn(state))
        state["maintenance"]["migrations"][home.MIX] = {"at": 0}
        seen = []
        for n in range(len(home.FIELD_TURNS) + 1):
            line = home.field_turn(state)
            self.assertIn("THIS ROUND STARTS IN", line)
            self.assertIn("should be a mix of them", line)
            seen.append(line)
            state["shelf"]["rounds"][f"r{n}"] = {"started_at": 5}
        state["shelf"]["rounds"]["before"] = {"started_at": -1}
        self.assertEqual(len(home.FIELD_TURNS), len(set(seen)), "every field gets a round")
        self.assertEqual(seen[0], seen[-1], "and then the turns begin again")
        self.assertEqual(seen[1], home.field_turn(state), "rounds before the migration do not count")
        self.assertIn("library someone would import", seen[0], "software goes first")

    def test_one_session_at_a_time_always_looks_after_the_house(self):
        import time
        from house import course, shelf
        state = {"maintenance": {"migrations": {}}, "shelf": shelf.empty()}
        just_ended = lambda count: types.SimpleNamespace(
            running={}, focus_record=lambda: {"run": "gone", "at": time.time() - 60, "count": count})
        still_running = types.SimpleNamespace(
            running={"r": 1}, focus_record=lambda: {"run": "r", "at": time.time() - 7200, "count": 0})
        with patch.object(course, "enabled", lambda state: True):
            self.assertIsNone(home.Coordinator.home_focus(just_ended(0), state), "before: half an hour apart")
            state["maintenance"]["migrations"][home.MIX] = {"at": 0}
            self.assertEqual("improve", home.Coordinator.home_focus(just_ended(0), state))
            self.assertIsNone(home.Coordinator.home_focus(still_running, state), "one at a time")
            turns = [home.Coordinator.home_focus(just_ended(count), state) for count in range(6)]
        self.assertEqual("improve", turns[0])
        self.assertGreaterEqual(turns.count("improve"), 3, "at least every other house turn improves the house")

    def test_voters_are_asked_for_a_mix(self):
        ideas = {f"i{n}": {"brief": {"for": "field", "field": "mathematics"}} for n in range(3)}
        choices = {f"c{n}": {"status": "closed", "winner": f"i{n}", "closed_sequence": n} for n in range(3)}
        state = {"maintenance": {"migrations": {home.MIX: {"at": 0}, staffing.LIGHT: {"at": 0}}},
                 "shelf": {"ideas": ideas, "choices": choices}}
        with patch("house.shelf.higher_since", lambda state: 1.0):
            text = home.chosen_mix(state)
        self.assertIn("mathematics 3", text)
        self.assertIn("choose the one from a field the house has chosen least lately", text)
