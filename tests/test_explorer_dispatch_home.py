"""Real disposable journal races and inert native dispatch; no model calls."""
import copy
import json
import os
import time
import unittest
import uuid
from unittest.mock import patch

from house import council, home, life
from house.record import Record
from tests import test_council, test_explorer_dispatch, test_home
from tests.support import HouseCase


def configure(case, fixture_type=test_explorer_dispatch.ExplorerDispatchTests):
    events = []
    original = test_council.CouncilTests.event

    def capture(h, op, data, actor="alice"):
        original(h, op, data, actor)
        events.append((h.now, op, copy.deepcopy(data), actor))

    with patch.object(test_council.CouncilTests, "event", capture):
        fixture = fixture_type()
        fixture.setUp(); fixture.enable()
    case.repo = case.new_repo("automatic-explorer")
    case.record = Record(case.repo)
    with patch("house.record.uuid.uuid4", side_effect=[uuid.uuid4(), uuid.UUID(council.APPROVED_HOUSE)]):
        with patch("house.record.time.time", return_value=1700000000):
            case.record.found("Test", "Founding charter")
    for at, op, data, actor in events:
        with patch("house.record.time.time", return_value=at):
            case.record.append(op, actor, data)
    return fixture


class ExplorerRaceTests(HouseCase):
    def test_competing_admissions_lost_receipt_and_recovery(self):
        fixture = configure(self)
        data = {key: fixture.start_data(key, explore_generation=0) for key in ("left", "right")}
        children = [(key, self.process("life", "--as", "watch-keeper", "--request", key,
                                      "--data", json.dumps(value))) for key, value in data.items()]
        for _, child in children:
            child.communicate(timeout=30)
        self.assertEqual([0, 2], sorted(child.returncode for _, child in children))
        winner = next(key for key, child in children if child.returncode == 0)
        head = self.record.read()[2]
        receipt = self.cli("life", "--as", "watch-keeper", "--request", winner, "--data", json.dumps(data[winner]))
        self.assertTrue(receipt["replayed"])
        self.assertEqual(head, self.record.read()[2])
        self.record.append("life", "watch-keeper", {"kind": "run-finish", "run": winner,
            "outcome": "interrupted", "exit_code": None, "elapsed_seconds": 1, "usage": {}})
        demand = life.workload(self.record.read()[0], time.time())
        self.assertEqual(0, demand["explore_generation"])
        self.assertEqual(self.record.read()[0], Record(self.repo).read()[0])


@unittest.skipIf(os.environ.get("EMBERHALL_CANDIDATE_SANDBOX") == "1",
                 "native process fixture requires host process observation")
class AutomaticExplorerHomeTests(unittest.TestCase):
    def test_empty_shelf_dispatches_without_task_or_help_and_recovers(self):
        fixture = test_home.HomeTests()
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        configure(fixture)
        (fixture.repo / "source.txt").write_text("inert fixture\n")
        test_home.git(fixture.repo, "add", "source.txt")
        test_home.git(fixture.repo, "-c", "commit.gpgsign=false", "-c", "user.name=Test",
                      "-c", "user.email=test@local", "commit", "-m", "Fixture")
        coordinator = home.Coordinator(fixture.record, fixture.runtime)
        self.addCleanup(coordinator.close)
        fixture.delay = 0.1
        started = coordinator.tick(poll=False)["started"]
        self.assertEqual(1, len(started))
        run = fixture.record.read()[0]["life"]["runs"][started[0]]
        self.assertEqual(0, run["explore_generation"])
        self.assertNotIn("help_request", run)
        self.assertNotIn("backlog", run)
        prompt = (coordinator.private / started[0] / "prompt.txt").read_text()
        self.assertIn("Automatic Explorer assignment", prompt)
        self.assertIn("this is not a research lease", prompt)
        fixture.drain(coordinator)
        again = coordinator.tick(poll=False)["started"]
        self.assertEqual(1, len(again))
        self.assertNotEqual(started, again)
        fixture.drain(coordinator)
