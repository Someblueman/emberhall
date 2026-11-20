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
