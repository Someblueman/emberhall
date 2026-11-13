"""Watch receipts remain distinct from resident presence in the visible house."""
import json
import xml.etree.ElementTree as ET

from house.illustration import render
from house.watch import ACTOR, message
from tests.support import HouseCase

NS = "{http://www.w3.org/2000/svg}"


class WatchIllustrationTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.record.append("arrive", ACTOR, {"name": "Watch keeper"})

    def emit(self, kind, run="one", **fields):
        return self.record.append("say", ACTOR, message(kind, run, **fields))

    def picture(self):
        before = self.record.read()[2]
        picture = ET.fromstring(render(self.record))
        self.assertEqual(before, self.record.read()[2])
        return picture

    def watches(self):
        return {node.get("data-watch"): node for node in self.picture().iter()
                if "data-watch" in node.attrib}

    def test_sleep_and_saved_success_do_not_imply_terminal_cleanup(self):
        self.emit("start", resident="alice")
        self.record.append("sleep", "alice", {"through": self.record.read()[0]["sequence"],
                                              "note": "Work completed"})
        self.assertIn("No terminal receipt yet", "".join(self.watches()["one"].itertext()))
        self.emit("execution-result", outcome="success", exit_code=0)
        pending = self.watches()["one"]
        self.assertEqual(pending.get("data-state"), "pending")
        self.assertIn("Result saved · cleanup pending", "".join(pending.itertext()))
        receipt = self.emit("finish", outcome="success", exit_code=0)
        finished = self.watches()["one"]
        self.assertEqual(finished.get("data-state"), "terminal")
        self.assertIn("Finished · success", "".join(finished.itertext()))
        self.assertIn(f'Event {receipt["sequence"]}', "".join(finished.itertext()))

    def test_interruption_and_failed_exit_remain_visible_after_rescue(self):
        self.emit("start", resident="alice")
        self.emit("recovered-interruption", reason="supervisor-ended-without-finish")
        self.emit("rescue", digest="recorded-rescue")
        self.assertIn("Interrupted · outcome unknown", "".join(self.watches()["one"].itertext()))
        self.emit("start", "two", resident="bob")
        self.emit("finish", "two", outcome="failed", exit_code=7)
        self.assertIn("Finished · failed", "".join(self.watches()["two"].itertext()))

    def test_latest_three_starts_only_and_non_machine_prose_is_ignored(self):
        self.assertFalse(self.watches())
        self.record.append("say", "alice", message("start", "pretend", resident="alice"))
        self.assertFalse(self.watches())
        for run in ("one", "two", "three", "four"):
            self.emit("start", run, resident="alice")
        self.assertEqual(list(self.watches()), ["four", "three", "two"])
        metadata = json.loads(self.picture().find(NS + "metadata").text)
        self.assertEqual(metadata["watch_runs"], ["two", "three", "four"])

    def test_unarrived_identity_and_xml_text_are_safe(self):
        self.emit("start", 'run<&"', resident='guest<&"')
        self.emit("execution-result", 'run<&"', outcome='<script>oops</script>', exit_code=2)
        picture = self.picture()
        self.assertFalse(list(picture.iter(NS + "script")))
        watch = self.watches()['run<&"']
        self.assertIn('guest<&"', "".join(watch.itertext()))
