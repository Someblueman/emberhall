import json
from pathlib import Path
import tempfile
import unittest

import collect_trial
import test_trial
import trial


class CollectionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.directory = Path(tmp.name) / "sample"
        self.fixture = test_trial.TrialTests()
        self.fixture.setUp()
        self.after = self.fixture.events[0]["sequence"] - 1
        self.fixture.install()
        self.fixture.offer("receiver", "early", finished=True)
        while len(self.fixture.events) < 215:
            self.fixture.add("say", text="other work")
        self.horizon = self.fixture.events[-1]["sequence"]
        self.calls = []

    def read(self, *args):
        self.calls.append(args)
        if args == ("status",):
            return {"house_id": "test-house", "sequence": self.horizon}
        command, flag, resident, after_flag, cursor, limit_flag, limit = args
        self.assertEqual(("read", "--as", "reader", "--after", "--limit"),
                         (command, flag, resident, after_flag, limit_flag))
        start = int(cursor) - self.after
        events = self.fixture.events[start:start + int(limit)]
        through = events[-1]["sequence"]
        return {"events": events, "through": through, "latest": self.horizon + 12, "has_more": True}

    def collect(self, reader):
        return collect_trial.collect(self.directory, "reader", trial.REVIEWED, self.after, reader)

    def test_interrupted_collection_reuses_status_and_pages_after_live_head_advances(self):
        def interrupted(*args):
            page = self.read(*args)
            if args[0] == "read" and int(args[4]) > self.after:
                page["events"].pop()
            return page

        with self.assertRaisesRegex(ValueError, "gap|invalid journal event"):
            self.collect(interrupted)
        self.assertEqual(1, len(list(self.directory.glob("page-*.json"))))
        self.calls.clear()
        for _ in range(24):
            self.fixture.add("say", text="arrived later")
        result = self.collect(self.read)
        self.assertEqual(1, len(self.calls))
        self.assertEqual(("read", "--as", "reader", "--after", str(self.after + 200), "--limit", "15"),
                         self.calls[0])
        self.assertEqual((self.horizon, "receiver finished"),
                         (result["through"], result["enrolled"][0]["disposition"]))
        self.assertEqual(0, self.directory.stat().st_mode & 0o077)
        self.assertTrue(all(p.stat().st_mode & 0o077 == 0 for p in self.directory.iterdir()))
        self.assertEqual(result, self.collect(lambda *args: self.fail("completed sample contacted the house")))
        events, end = trial.baseline_pages(sorted(self.directory.glob("page-*.json")), trial.REVIEWED)
        self.assertEqual(result, trial.assess(events, end))

    def test_refuses_other_selection_moving_status_and_wrong_saved_cursor(self):
        self.collect(self.read)
        with self.assertRaisesRegex(ValueError, "saved baseline"):
            collect_trial.collect(self.directory, "reader", trial.ONE_FAMILY, self.after, self.read)
        status = self.directory / "status.json"
        original = status.read_text()
        status.write_text(json.dumps({"house_id": "test-house", "sequence": self.horizon + 5}))
        with self.assertRaisesRegex(ValueError, "frozen collection"):
            self.collect(self.read)
        status.write_text(original)
        page = sorted(self.directory.glob("page-*.json"))[-1]
        data = json.loads(page.read_text())
        data["events"] = data["events"][1:]
        page.write_text(json.dumps(data))
        self.calls.clear()
        with self.assertRaisesRegex(ValueError, "gap"):
            self.collect(self.read)
        self.assertEqual([], self.calls)
