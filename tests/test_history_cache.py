"""The publisher replays only new events, yet publishes exactly the full history."""
import json
import marshal
from unittest.mock import patch

from house import publish
from house.body import export
from house.public_history import decode
from tests.support import HouseCase


class HistoryCacheTests(HouseCase):
    def setUp(self):
        super().setUp()
        self.private = self.record.common / "house-home"
        self.private.mkdir(exist_ok=True)

    def history(self, at=1e10):
        body, summary, parts = publish.history(self.record, self.private, observed_at=at)
        return decode(json.loads(body), parts), summary

    def grow(self):
        if "garden" not in self.record.read()[0].get("life", {}).get("rooms", {}):
            self.record.append("life", "alice", {"kind": "room", "room": "garden", "name": "Glass garden"})
        else:
            self.record.append("say", "alice", {"text": "In the garden"})
        self.record.append("say", "alice", {"text": "I am by the hearth"})

    def test_resumed_history_equals_a_full_rebuild(self):
        first, summary = self.history()
        self.assertEqual(first, export(self.record, 1e10))
        self.grow()
        with patch("house.publish.replay", wraps=publish.replay) as replay:
            resumed, later = self.history()
        context = replay.call_args.args[1]
        self.assertEqual(summary["seq"], len(first["frames"]))
        self.assertEqual(later["seq"], summary["seq"] + 2)
        self.assertEqual(resumed, export(self.record, 1e10))
        self.assertEqual(later["seq"], context["replayed"])

    def test_changed_code_or_rewritten_journal_rebuilds_from_the_start(self):
        self.history()
        path = self.private / publish.HISTORY_CACHE
        for change in ({"code": "0" * 64}, {"head": "0" * 40}, {"format": 0}):
            cache = marshal.loads(path.read_bytes())
            cache.update(change)
            path.write_bytes(marshal.dumps(cache))
            self.grow()
            with patch("house.publish.replay_context", wraps=publish.replay_context) as fresh:
                rebuilt, _ = self.history()
            fresh.assert_called_once()
            self.assertEqual(rebuilt, export(self.record, 1e10))
        path.write_bytes(b"not marshal")
        self.assertEqual(self.history()[0], export(self.record, 1e10))

    def test_chunked_history_resumes_to_the_bytes_of_a_full_rebuild_and_old_caches_are_dropped(self):
        with patch("house.public_history.CHUNK", 4):
            for _ in range(3):
                self.grow()
            first, _, _ = publish.history(self.record, self.private, observed_at=1e10)
            self.assertEqual(json.loads(first)["version"], 4)
            self.assertTrue(any(len(node) == 1 and isinstance(node[0], list)
                                for node in json.loads(first)["nodes"] if isinstance(node, list)))
            for _ in range(3):
                self.grow()
            resumed, summary, parts = publish.history(self.record, self.private, observed_at=1e10)
            self.assertEqual(summary["history_version"], 4)
            self.assertEqual(decode(json.loads(resumed), parts), export(self.record, 1e10))
            (self.private / publish.HISTORY_CACHE).unlink()
            self.assertEqual(publish.history(self.record, self.private, observed_at=1e10)[0], resumed)
            # A cache written before chunking (format 1) holds unchunked nodes and is rebuilt.
            path = self.private / publish.HISTORY_CACHE
            cache = marshal.loads(path.read_bytes())
            path.write_bytes(marshal.dumps({**cache, "format": 1}))
            with patch("house.publish.replay_context", wraps=publish.replay_context) as fresh:
                self.assertEqual(publish.history(self.record, self.private, observed_at=1e10)[0], resumed)
            fresh.assert_called_once()

    def test_a_rebuild_stopped_midway_resumes_from_its_checkpoint_to_the_same_bytes(self):
        # 18 November: a full rebuild outran the publisher's time limit, was killed and began again from
        # nothing each time. It now saves its place, so the next attempt carries on.
        for _ in range(4):
            self.grow()
        whole = publish.history(self.record, self.private, observed_at=1e10)[0]
        total = len(self.record.read()[1])
        path = self.private / publish.HISTORY_CACHE
        path.unlink()
        real, calls = publish.replay, []

        def stopped(events, context):
            calls.append(len(events))
            if len(calls) == 3:
                raise KeyboardInterrupt   # the publisher is killed here
            return real(events, context)

        with patch("house.publish.REPLAY_BATCH", 2), patch("house.publish.CHECKPOINT_SECONDS", 0):
            with patch("house.publish.replay", stopped), self.assertRaises(KeyboardInterrupt):
                publish.history(self.record, self.private, observed_at=1e10)
            self.assertEqual([2, 4, 6], calls, "two events at a time")
            kept = marshal.loads(path.read_bytes())
            self.assertEqual(4, kept["context"]["replayed"])
            self.assertLess(4, total)
            with patch("house.publish.replay_context", wraps=publish.replay_context) as fresh, \
                    patch("house.publish.replay", wraps=real) as resumed:
                again = publish.history(self.record, self.private, observed_at=1e10)[0]
            fresh.assert_not_called()
            self.assertEqual(6, len(resumed.call_args_list[0].args[0]), "it carried on from event 4")
        self.assertEqual(again, whole)
        self.assertEqual(total, marshal.loads(path.read_bytes())["context"]["replayed"])

