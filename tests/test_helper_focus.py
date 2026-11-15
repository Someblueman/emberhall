"""Assignment prompt coverage for bounded helpers and ordinary residents."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from house.home import Coordinator


class HelperFocusTests(unittest.TestCase):
    def prompt(self, workspace, agent, model):
        assigned = {"agent": agent, "model": model, "task": "work", "task_generation": 0}
        state = {"residents": {}, "tasks": {"work": {"title": "Work", "description": "Bounded work"}},
                 "life": {"runs": {"run": assigned}}}
        coordinator = object.__new__(Coordinator)
        coordinator.record = SimpleNamespace(read=lambda: (state, [], None))
        coordinator.private = workspace
        with patch("house.home.pending_contributions", return_value=[]), \
             patch("house.home.active_prompt", return_value="Fixture policy"):
            return coordinator.prompt(state, "run", "resident", workspace, workspace / ".house-client", None)

    def test_only_regular_routes_receive_overdue_checkpoint_chore(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "evidence").mkdir()
            (workspace / "evidence/checkpoint.json").write_text(json.dumps(
                {"last_event_utc": "2000-01-01T00:00:00+00:00"}))
            for model in ("gpt-6-luna", "gpt-6.1-terra"):
                with self.subTest(model=model):
                    prompt = self.prompt(workspace, "codex", model)
                    self.assertIn("Bounded helper assignment", prompt)
                    self.assertIn("Suggested task: work", prompt)
                    self.assertNotIn("a fresh checkpoint is due", prompt)
                    self.assertNotIn("checkpoint --as resident --task TASK", prompt)
            for agent, model in (("codex", "gpt-6-astra"), ("opencode", "gpt-6-luna")):
                with self.subTest(agent=agent, model=model):
                    prompt = self.prompt(workspace, agent, model)
                    self.assertIn("a fresh checkpoint is due", prompt)
                    self.assertIn("checkpoint --as resident --task TASK", prompt)
                    self.assertNotIn("Bounded helper assignment", prompt)
